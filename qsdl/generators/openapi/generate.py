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

"""OpenAPI Generator"""

from pathlib import Path
from typing import List

from textx import model as xtx

from qsdl.dsl.models import Field, Object, Scalar, Schema
from qsdl.render import render

from . import util
from .config import Config
from .models import Api, Model


def parse_apis(schema: Schema) -> List[Api]:
    """Parse QSDL schema into custom API model.

    Args:
        schema (Schema): The QSDL schema model.

    Returns:
        List[Api]: A list of custom API models.
    """
    apis = []

    entities = xtx.get_children_of_type("Api", schema)

    for entity in entities:
        new_api = Api(entity)
        apis.append(new_api)

    return apis


def parse_models(schema: Schema) -> List[Model]:
    """Parse QSDL schema into custom models.

    Args:
        schema (Schema): The QSDL schema model.
    Returns:
        List[Model]: The parsed models.
    """
    models = []

    enum_list = xtx.get_children_of_type("Enum", schema)
    base_list = xtx.get_children_of_type("Base", schema)
    object_list = xtx.get_children_of_type("Object", schema)

    for obj in enum_list + base_list:
        model = Model(obj)
        models.append(model)

    for obj in object_list:
        model = Model(obj)
        models.append(model)

        # add paging response for all objects with default CRUD endpoints
        if obj.is_crud:
            model = get_paginated_object(obj, model)
            model.is_crud = False
            models.insert(-1, model)

    return models


def get_paginated_object(obj: Object, model: Model) -> Model:
    """Returns a pagable custom model that is used to return a given model.

    Args:
        obj (Object): The QSDL Object.
        model (Model): The OpenApi Model.

    Returns:
        Model: The pagable custom model.
    """

    # represents the model
    new_object = Object()
    new_object.name = model.name + "List"
    new_object._tx_fqn = "entity.Object"

    # contains the item list of the entity
    item_field = Field()
    item_field.name = "items"
    item_field.is_array = True
    item_field.is_required = True
    item_field.value = obj
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


def generate(schema: Schema, output_path: Path, config: Config):
    """Generator func for OpenAPI"""

    if config.id_type not in ["integer", "string"]:
        raise ValueError("id_type must be `integer` or `string`")

    if config.id_type == "integer":
        config.id_type_format = "int64"
    else:
        config.id_type_format = None

    # sets the id type and schema
    util.custom_types["ID"] = config.id_type
    util.schema = schema
    util.used_paths = []

    output_file = output_path / "openapi.yaml"
    template_path = Path(__file__).parent / "template" / "openapi.j2"

    # parse schema into OpenApi custom models
    apis = parse_apis(schema)
    models = parse_models(schema)

    # build the render arguments
    context = {
        "schema": schema,
        "apis": apis,
        "models": models,
        "util": util,
        "config": config,
    }

    render(output_file, context, template_path)
