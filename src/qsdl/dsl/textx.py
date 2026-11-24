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

"""Core generation"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import textx.model
from textx import metamodel_from_file
from textx.const import UNKNOWN_OBJ_ERROR
from textx.exceptions import TextXSemanticError, TextXSyntaxError
from textx.export import PlantUmlRenderer, metamodel_export
from textx.metamodel import TextXMetaModel

from qsdl import __folder__, dsl, logger
from qsdl.dsl.diagnostics import Diagnostic, Reporter, SchemaValidationError
from qsdl.dsl.processors.directive_parser import _directive_owners, validate_directive_specs
from qsdl.dsl.processors.import_processor import (
    AmbiguousReferenceError,
    CanonicalImportURI,
    ImportLoadError,
    merge_imported_types,
)
from qsdl.dsl.processors.model_parser import retain_used_types
from qsdl.dsl.processors.model_processor import model_post_processor, model_processor
from qsdl.dsl.processors.obj_processors import obj_processors
from qsdl.exceptions import QsdlException

log = logger.getLogger(__name__)


type_builtins = {
    "Int": dsl.Scalar(name="Int"),
    "Long": dsl.Scalar(name="Long"),
    "Float": dsl.Scalar(name="Float"),
    "Double": dsl.Scalar(name="Double"),
    "String": dsl.Scalar(name="String"),
    "Boolean": dsl.Scalar(name="Boolean"),
    "Date": dsl.Scalar(name="Date"),
    "Datetime": dsl.Scalar(name="Datetime"),
    "Object": dsl.Scalar(name="Object"),
    "Void": dsl.Scalar(name="Void"),
}


def draw_metamodel(metamodel: TextXMetaModel) -> None:
    """Exports a PlantUml diagram of the metamodel.

    Args:
        metamodel (TextXMetaModel): The metamodel to draw.
    """
    out_path = Path(__folder__) / "dsl" / "definition" / "entity.md"

    metamodel_export(metamodel, out_path, renderer=PlantUmlRenderer())

    with open(out_path, "r+", encoding="utf-8") as file:
        tmp = file.readlines()
        file.seek(0)
        tmp.insert(0, "```plantuml\n")
        tmp.append("```")
        file.writelines(tmp)
        file.truncate()


def get_metamodel(print_uml: bool = False) -> TextXMetaModel:
    """Builds and returns a meta-model for our meta language.

    Args:
        print_uml (bool, optional): Draw a PlantUml diagram of the model.
            Defaults to False.

    Returns:
        TextXMetaModel: The metamodel.
    """

    metamodel = None
    grammar_path = __folder__ / "dsl/definition/entity.tx"

    # parse the grammar file
    metamodel = metamodel_from_file(grammar_path, classes=dsl.all_dsl_models(), builtins=type_builtins)

    # register pre-processors
    # these allow us to hook into the model and object creation
    metamodel.register_model_processor(model_processor)
    metamodel.register_obj_processors(obj_processors)
    metamodel.model_param_defs.add("directive_specs", "Active generator directive specifications by name")
    metamodel.model_param_defs.add("reporter", "Rule error policy shared with imported schemas")

    # register scope provider to allow multi-schema-files
    metamodel.register_scope_providers({"*.*": CanonicalImportURI()})

    # export model with plantuml
    if print_uml:
        draw_metamodel(metamodel)

    return metamodel


def parse_schema(
    input_path: Path | None = None,
    raw_schema: str | None = None,
    *,
    directive_specs: Sequence[dsl.DirectiveSpec[Any]] = (),
    collect_errors: bool = False,
) -> dsl.Schema:
    """Builds and returns the DSL model as python object graph.

    Expects either input_path or raw_schema.

    Args:
        input_path (Path, optional): Path to the schema file.
        raw_schema (str, optional): The schema definition as string.
        directive_specs: Optional generator definitions active for this parse and its imports.
        collect_errors: Raise SchemaValidationError with all independent diagnostics instead of failing fast.

    Returns:
        schema (Schema): The parsed schema definition.
    """

    if not input_path and not raw_schema:
        raise QsdlException("please provide either raw_schema or input_path")

    active_specs = validate_directive_specs(directive_specs)
    reporter = Reporter(collecting=collect_errors)
    schema = _process_schema(input_path, raw_schema, active_specs, reporter)
    if reporter.diagnostics:
        raise SchemaValidationError(tuple(reporter.diagnostics))

    assert schema is not None
    retain_used_types(schema)
    return schema


def analyze_schema(input_path: Path) -> tuple[Diagnostic, ...]:
    """Analyze a file and its imports with core rules, returning diagnostics only."""
    reporter = Reporter(collecting=True)
    _process_schema(input_path, None, {}, reporter)
    return tuple(reporter.diagnostics)


def _process_schema(
    input_path: Path | None,
    raw_schema: str | None,
    active_specs: dict[str, dsl.DirectiveSpec[Any]],
    reporter: Reporter,
) -> dsl.Schema | None:
    log.info("loading metamodel...")
    metamodel = get_metamodel()
    try:
        schema = _load_schema(metamodel, input_path, raw_schema, active_specs, reporter)
    except (TextXSyntaxError, TextXSemanticError) as exc:
        if not reporter.collecting:
            raise
        if isinstance(exc, TextXSyntaxError):
            code = "syntax"
        elif isinstance(exc, ImportLoadError):
            code = "import-load"
        elif (
            isinstance(exc, AmbiguousReferenceError)
            or exc.err_type == UNKNOWN_OBJ_ERROR
            or exc.message.startswith("Unresolvable cross references:")
        ):
            code = "unresolved-reference"
        else:
            raise
        reporter.diagnostics.clear()
        reporter.error(
            code, exc.message, filename=exc.filename or input_path, line=exc.line, col=exc.col, nchar=exc.nchar
        )
    except (OSError, UnicodeDecodeError) as exc:
        if not reporter.collecting:
            raise
        reporter.diagnostics.clear()
        reporter.error("input-load", str(exc), filename=getattr(exc, "filename", None) or input_path)
    else:
        merge_imported_types(schema)
        model_post_processor(schema, metamodel)
        if not reporter.diagnostics:
            log.info("schema validation passed")
        return schema
    return None


def _load_schema(
    metamodel: TextXMetaModel,
    input_path: Path | None,
    raw_schema: str | None,
    active_specs: dict[str, dsl.DirectiveSpec[Any]],
    reporter: Reporter,
) -> dsl.Schema:
    log.info("loading schema...")
    if input_path:
        return metamodel.model_from_file(input_path, directive_specs=active_specs, reporter=reporter)
    if raw_schema and 'import "' in raw_schema:
        raise QsdlException("import statements in raw_schema are not supported")
    # model_from_str does not support loading additional files through the provider.
    return metamodel.model_from_str(raw_schema, directive_specs=active_specs, reporter=reporter)


def get_children_of_api(schema: dsl.Schema) -> list[dsl.Api]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Api", schema)


def get_children_of_argument(schema: dsl.Schema) -> list[dsl.Argument]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Argument", schema)


def get_children_of_base(schema: dsl.Schema) -> list[dsl.Base]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Base", schema)


def get_children_of_directive(schema: dsl.Schema) -> list[dsl.Directive[Any]]:
    """Return attached directives across every owner in the schema."""
    return [node for owner in _directive_owners(schema) for node in owner.directives]


def get_children_of_enum(schema: dsl.Schema) -> list[dsl.Enum]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Enum", schema)


def get_children_of_field(schema: dsl.Schema) -> list[dsl.Field]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Field", schema)


def get_children_of_object(schema: dsl.Schema) -> list[dsl.Object]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Object", schema)


def get_children_of_operation(schema: dsl.Schema) -> list[dsl.Operation]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Operation", schema)


def get_children_of_scalar(schema: dsl.Schema) -> list[dsl.Scalar]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Scalar", schema)
