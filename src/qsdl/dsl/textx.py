# Copyright 2025 henn1001
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

from pathlib import Path

import textx.model
import textx.scoping.providers as scoping_providers
from textx import metamodel_from_file
from textx.export import PlantUmlRenderer, metamodel_export
from textx.metamodel import TextXMetaModel

import qsdl.dsl.models as dsl
from qsdl import __folder__, logger
from qsdl.dsl.processors.model_processor import model_merger, model_post_processor, model_processor
from qsdl.dsl.processors.obj_processors import obj_processors

log = logger.getLogger(__name__)


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

    # parse the grammar file
    metamodel = metamodel_from_file(grammar_path, classes=dsl.all_dsl_models(), builtins=type_builtins)

    # register pre-processors
    # these allow us to hook into the model and object creation
    metamodel.register_model_processor(model_processor)
    metamodel.register_obj_processors(obj_processors)

    # register scope provider to allow multi-schema-files
    metamodel.register_scope_providers({"*.*": scoping_providers.PlainNameImportURI()})

    # export model with plantuml
    if print_uml:
        draw_metamodel(metamodel)

    return metamodel


def parse_schema(input_path: Path = None, raw_schema: str = None) -> dsl.Schema:
    """Builds and returns the DSL model as python object graph.

    Expects either input_path or raw_schema.

    Args:
        input_path (Path, optional): Path to the schema file.
        raw_schema (str, optional): The schema definition as string.

    Returns:
        schema (Schema): The parsed schema definition.
    """

    if not input_path and not raw_schema:
        raise Exception("please provide either raw_schema or input_path")

    # export model with plantuml
    log.info("loading metamodel...")
    metamodel = get_metamodel()

    log.info("generating schema...")
    if input_path:
        schema: dsl.Schema = metamodel.model_from_file(input_path)
    elif 'import "' in raw_schema:
        raise Exception("import statements in raw_schema are not supported")
    else:
        # model_from_str does not seem to support the scope provider system
        # no support for multi-schema-files
        schema: dsl.Schema = metamodel.model_from_str(raw_schema)

    # merge schema for multi-schema-files
    model_merger(schema)

    # run post processing
    model_post_processor(schema, metamodel)

    log.info("schema successfully loaded")

    return schema


def get_children_of_api(schema: dsl.Schema) -> list[dsl.Api]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Api", schema)


def get_children_of_argument(schema: dsl.Schema) -> list[dsl.Argument]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Argument", schema)


def get_children_of_base(schema: dsl.Schema) -> list[dsl.Base]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Base", schema)


def get_children_of_directive(schema: dsl.Schema) -> list[dsl.Directive]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Directive", schema)


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
