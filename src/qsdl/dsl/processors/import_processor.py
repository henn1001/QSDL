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

from textx import get_location, get_model
from textx.exceptions import TextXSemanticError
from textx.metamodel import MetaAttr
from textx.model import ObjCrossRef
from textx.scoping.providers import PlainNameImportURI

from qsdl import dsl
from qsdl.dsl.diagnostics import reporter_for


class ImportStatement(Protocol):
    """Attributes added to QSDL import statements by TextX."""

    importURI: str
    _tx_loaded_models: list[dsl.Schema]
    _tx_position: int
    _tx_position_end: int


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


class ImportLoadError(TextXSemanticError):
    """An import that prevents textX from constructing a linked model."""


class AmbiguousReferenceError(TextXSemanticError):
    """A reference for which textX found more than one candidate in a file."""


def _import_location(source: Path, statement: ImportStatement, encoding: str) -> dict[str, str | int]:
    # textX has recorded the token offsets, but exposes its parser only after loading imports.
    try:
        prefix = source.read_text(encoding=encoding)[: statement._tx_position]
    except (OSError, UnicodeDecodeError):
        return {"filename": str(source)}
    return {
        "filename": str(source),
        "line": prefix.count("\n") + 1,
        "col": len(prefix) - prefix.rfind("\n"),
        "nchar": statement._tx_position_end - statement._tx_position,
    }


class CanonicalImportURI(PlainNameImportURI):
    """Load QSDL imports by canonical path without provider-level state."""

    def __call__(self, obj: object, attr: MetaAttr, obj_ref: ObjCrossRef) -> object | None:
        try:
            return super().__call__(obj, attr, obj_ref)
        except TextXSemanticError as exc:
            if not reporter_for(obj).collecting or exc.message != f"name {obj_ref.obj_name} is not unique.":
                raise
            # During import lookup, textX can report the searched file instead of the reference's file.
            model = get_model(obj)
            line, col = model._tx_parser.pos_to_linecol(obj_ref.position)
            raise AmbiguousReferenceError(
                exc.message, line=line, col=col, nchar=len(obj_ref.obj_name), filename=model._tx_filename
            ) from exc

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
            collecting = reporter_for(model).collecting
            if "\0" in import_uri:
                raise ImportLoadError(
                    f"Imported schema path {import_uri!r} contains an embedded NUL.",
                    **_import_location(source_path, import_statement, encoding),
                )
            if Path(import_uri).suffix != ".qsdl":
                message = f"Imported schema {import_statement.importURI!r} must use the .qsdl extension."
                if collecting:
                    raise ImportLoadError(message, **_import_location(source_path, import_statement, encoding))
                raise TextXSemanticError(message, filename=str(source_path))

            try:
                imported_path = canonical_path(source_path.parent / import_uri)
                import_statement._tx_loaded_models = model._tx_model_repository.load_models_using_filepattern(
                    str(imported_path),
                    model=model,
                    glob_args=self.glob_args,
                    encoding=encoding,
                    add_to_local_models=True,
                    # Share the directive specifications and reporting policy with imports.
                    model_params=model._tx_model_params,
                )
            except (OSError, UnicodeDecodeError) as exc:
                if not collecting:
                    raise
                raise ImportLoadError(
                    f"Cannot load imported schema {import_statement.importURI!r}: {exc}",
                    **_import_location(source_path, import_statement, encoding),
                ) from exc


def collect_imported_schemas(schema: dsl.Schema) -> list[dsl.Schema]:
    """Return each imported schema once in dependency-first order.

    TextX safely loads circular graphs and caches imported models. QSDL applies
    its stricter no-cycles rule while traversing the resulting import graph.
    """
    reporter = reporter_for(schema)
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
                get_location(imported_by) if imported_by is not None else {"filename": current_schema._tx_filename}
            )
            reporter.error("LOG-403", f"Circular import detected: {' -> '.join(chain)}", **location)
            reporter.namespace_complete = False
            return
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
