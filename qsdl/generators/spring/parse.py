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

"""Spring Generator parser"""

from pathlib import Path

import pathspec
import stringcase
from textx import model as xtx

from qsdl.dsl.models import Field, Object, Scalar
from qsdl.util import get_operations

from . import util
from .models import Api, Model


def add_paging_list(entity, model):

    # represents the model
    new_object = Object()
    new_object.name = model.name + "List"
    new_object._tx_fqn = "entity.Object"

    # contains the item list of the entity
    item_field = Field()
    item_field.name = "items"
    item_field.array = True
    item_field.non_nullable = True
    item_field.nested = True
    item_field.value = entity
    item_field._tx_fqn = "entity.Field"
    new_object.fields.append(item_field)

    # next cursor
    cursor_field = Field(name="next_cursor")
    string_scalar = Scalar(name="String")
    string_scalar._tx_fqn = "entity.Scalar"
    cursor_field.value = string_scalar
    cursor_field._tx_fqn = "entity.Field"
    new_object.fields.append(cursor_field)

    # total count
    count_field = Field(name="total_count")
    long_scalar = Scalar(name="Long")
    long_scalar._tx_fqn = "entity.Scalar"
    count_field.value = long_scalar
    count_field._tx_fqn = "entity.Field"
    new_object.fields.append(count_field)

    # init the new model class
    model = Model(new_object)

    return model


def parse_apis(schema: dict):

    apis = []
    api2operations = {}

    for operation in get_operations():

        # filter path and prune empty
        f = filter(None, operation.path.split("/"))
        tmp = list(f)

        api_name = tmp[-2] if (tmp[-1] in ["add", "remove"]) or ("{" in tmp[-1]) else tmp[-1]
        api_name = stringcase.lowercase(api_name)

        tag = operation.tag if operation.tag else "_default"
        tag = stringcase.lowercase(tag)
        if (tag, api_name) not in api2operations:
            api2operations[(tag, api_name)] = [operation]
        else:
            api2operations[(tag, api_name)].append(operation)

    for tmp in api2operations.items():

        api = Api(tmp)

        apis.append(api)

    return apis


def parse_models(schema: dict):
    """Parse OpenAPI Data Models.

    A Data Model is converted into a class with a flat representation of its attributes.

    Model
        Domain object to represent a class.
    Vars
        Domain object to represent class attributes.

    There are three things to consider:

        * Models defined in the schema section
        * Models defined via operation parameter/requestBody/responses
        * Models defined as inline model via the above two

    Args:
        schema (dict): The OpenApi 3 schema definition.

    Returns:
        list<Model>: The parsed models.
    """
    models = []

    enum_list = xtx.get_children_of_type("Enum", schema)
    base_list = xtx.get_children_of_type("Base", schema)
    object_list = xtx.get_children_of_type("Object", schema)

    # loop over schema dict
    for entity in enum_list + base_list:
        # init the new model class
        model = Model(entity)
        models.append(model)

    # loop over schema dict
    for entity in object_list:
        # init the new model class
        model = Model(entity)
        models.append(model)

        # add paging response for all objects with default CRUD endpoints
        if not entity.operation:
            model = add_paging_list(entity, model)
            models.append(model)

    return models


def parse_ignored_files(
    output_path: Path, api_files: list, model_files: list, supporting_files: list
):
    """Removes all generated files mentioned in .qsdl-ignore.

    Utilizes the pathspec python package.
    https://github.com/cpburnz/python-path-specification

    Args:
        api_files (list): [description]
        model_files (list): [description]
        supporting_files (list): [description]
    """
    ignorefile_path = output_path / ".qsdl-ignore"

    if ignorefile_path.is_file():
        supporting_files.remove((".qsdl-ignore.j2", ".qsdl-ignore"))

        # read the spec
        with open(ignorefile_path, "r") as infile:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", infile)

        # loop over each all files and remove matches
        # note the copy() - we dont want to modify the list directly
        for src, dest, _ in api_files.copy():
            if spec.match_file(output_path / dest):
                api_files.remove((src, dest, _))

        for src, dest, _ in model_files.copy():
            if spec.match_file(output_path / dest):
                model_files.remove((src, dest, _))

        for src, dest in supporting_files.copy():
            if spec.match_file(output_path / dest):
                supporting_files.remove((src, dest))
