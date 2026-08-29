# Copyright 2026 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""QSDL import loading and graph processing."""

from pathlib import Path
from typing import Protocol, cast

from textx import get_location
from textx.exceptions import TextXSemanticError
from textx.scoping.providers import PlainNameImportURI

from qsdl import dsl


class ImportStatement(Protocol):
    """Attributes added to QSDL import statements by TextX."""

    importURI: str
    _tx_loaded_models: list[dsl.Schema]


type ModelKey = Path | int


def canonical_path(filename: str | Path | None) -> Path | None:
    """Return a canonical absolute path for a model filename."""
    if filename is None:
        return None
    return Path(filename).expanduser().resolve()


def _source_path(schema: dsl.Schema) -> Path | None:
    """Return the canonical source path for a TextX model root."""
    parser = getattr(schema, "_tx_parser", None)
    parser_filename = getattr(parser, "file_name", None) if parser is not None else None
    return canonical_path(schema._tx_filename or parser_filename)


def _model_key(schema: dsl.Schema) -> ModelKey:
    """Identify file models by canonical path and anonymous models by identity."""
    return _source_path(schema) or id(schema)


def _model_label(schema: dsl.Schema) -> str:
    """Return a readable model identifier for diagnostics."""
    source_path = _source_path(schema)
    return str(source_path) if source_path is not None else f"<anonymous:{id(schema)}>"


class CanonicalImportURI(PlainNameImportURI):
    """Load QSDL imports by canonical path without provider-level state."""

    def _load_referenced_models(self, model: dsl.Schema, encoding: str) -> None:
        """Validate and load imports relative to the importing schema."""
        imports = cast(list[ImportStatement], model.imports)
        source_path = _source_path(model)
        if source_path is None:
            if imports:
                raise TextXSemanticError("Imports require a schema loaded from a file.")
            return

        for import_statement in imports:
            import_uri = self.importURI_converter(import_statement.importURI)
            if Path(import_uri).suffix != ".qsdl":
                raise TextXSemanticError(
                    f"Imported schema {import_statement.importURI!r} must use the .qsdl extension.",
                    filename=str(source_path),
                )

            imported_path = canonical_path(source_path.parent / import_uri)
            import_statement._tx_loaded_models = model._tx_model_repository.load_models_using_filepattern(
                str(imported_path),
                model=model,
                glob_args=self.glob_args,
                encoding=encoding,
                add_to_local_models=True,
                model_params=model._tx_model_params,
            )


def collect_imported_schemas(schema: dsl.Schema) -> list[dsl.Schema]:
    """Return each imported schema once in dependency-first order.

    TextX safely loads circular graphs and caches imported models. QSDL applies
    its stricter no-cycles rule while traversing the resulting import graph.
    """
    imported_schemas: list[dsl.Schema] = []
    active: list[ModelKey] = []
    active_labels: list[str] = []
    visited: set[ModelKey] = set()

    def visit(current_schema: dsl.Schema, imported_by: ImportStatement | None = None) -> None:
        key = _model_key(current_schema)
        if key in active:
            cycle_start = active.index(key)
            chain = active_labels[cycle_start:] + [_model_label(current_schema)]
            location = (
                get_location(imported_by)
                if imported_by is not None
                else {"filename": current_schema._tx_filename}
            )
            raise TextXSemanticError(f"Circular import detected: {' -> '.join(chain)}", **location)
        if key in visited:
            return

        active.append(key)
        active_labels.append(_model_label(current_schema))
        try:
            for import_statement in cast(list[ImportStatement], current_schema.imports):
                for loaded_schema in import_statement._tx_loaded_models:
                    visit(loaded_schema, import_statement)
        finally:
            active.pop()
            active_labels.pop()

        visited.add(key)
        if current_schema is not schema:
            imported_schemas.append(current_schema)

    visit(schema)
    return imported_schemas


def merge_imported_types(schema: dsl.Schema) -> None:
    """Merge types from each imported physical file into the root schema."""
    for imported_schema in collect_imported_schemas(schema):
        schema.types.extend(imported_schema.types)
