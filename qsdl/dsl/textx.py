# Copyright (C) 2020 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Core generation"""

from pathlib import Path
from typing import List

import textx.model
from textx import metamodel_from_file
from textx.export import PlantUmlRenderer, metamodel_export
from textx.metamodel import TextXMetaModel

from qsdl import __folder__, logger
from qsdl.dsl.models import *
from qsdl.dsl.processors.model_processor import model_processor
from qsdl.dsl.processors.obj_processors import obj_processors

log = logger.getLogger(__name__)


def draw_metamodel(metamodel: TextXMetaModel):
    """Exports a PlantUml diagram of the metamodel.

    Args:
        metamodel (TextXMetaModel): The metamodel to draw.
    """
    out_path = Path(__folder__) / "dsl" / "definition" / "entity.md"

    metamodel_export(metamodel, out_path, renderer=PlantUmlRenderer())

    with open(out_path, "r+") as file:
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
        "Int": Scalar(name="Int"),
        "Long": Scalar(name="Long"),
        "Float": Scalar(name="Float"),
        "Double": Scalar(name="Double"),
        "String": Scalar(name="String"),
        "Boolean": Scalar(name="Boolean"),
        "Date": Scalar(name="Date"),
        "Object": Scalar(name="Object"),
        "Void": Scalar(name="Void"),
    }

    # parse the grammar file
    metamodel = metamodel_from_file(grammar_path, classes=all_dsl_models(), builtins=type_builtins)

    # register pre-processors
    # these allow us to hook into the model and object creation
    metamodel.register_model_processor(model_processor)
    metamodel.register_obj_processors(obj_processors)

    # export model with plantuml
    if print_uml:
        draw_metamodel(metamodel)

    return metamodel


def parse_schema(raw_schema: str) -> Schema:
    """Builds and returns the DSL model as python object graph.

    Args:
        schema (str): The schema definition.

    Returns:
        schema (Schema): The parsed schema definition.
    """
    # export model with plantuml
    log.info("loading metamodel...")
    metamodel = get_metamodel()

    # build a model from schema definition file
    log.info("generating schema...")
    schema = metamodel.model_from_str(raw_schema)

    return schema


def get_children_of_api(schema: Schema) -> List[Api]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Api", schema)


def get_children_of_argument(schema: Schema) -> List[Argument]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Argument", schema)


def get_children_of_base(schema: Schema) -> List[Base]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Base", schema)


def get_children_of_directive(schema: Schema) -> List[Directive]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Directive", schema)


def get_children_of_enum(schema: Schema) -> List[Enum]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Enum", schema)


def get_children_of_field(schema: Schema) -> List[Field]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Field", schema)


def get_children_of_object(schema: Schema) -> List[Object]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Object", schema)


def get_children_of_operation(schema: Schema) -> List[Operation]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Operation", schema)



def get_children_of_scalar(schema: Schema) -> List[Scalar]:
    """Proxy method for typing support"""
    return textx.model.get_children_of_type("Scalar", schema)
