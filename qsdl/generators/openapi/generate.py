# Copyright (C) 2022 henn1001

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

import stringcase

import qsdl.dsl.textx as xtx
from qsdl.dsl.models import Field, Object, Scalar, Schema
from qsdl.render import render

from . import util
from .config import IDTYPE, Config
from .models import ApiObject, ModelObject


def parse_apis(schema: Schema) -> List[ApiObject]:
    """Parse QSDL schema into custom API model.

    Args:
        schema (Schema): The QSDL schema model.

    Returns:
        List[Api]: A list of custom API models.
    """
    apis = []

    api_list = xtx.get_children_of_api(schema)

    for api in api_list:

        # we can skip empty apis
        if not api.operations:
            continue

        api_class = ApiObject().build(api)
        apis.append(api_class)

    return apis


def parse_models(schema: Schema) -> List[ModelObject]:
    """Parse QSDL schema into custom models.

    Args:
        schema (Schema): The QSDL schema model.
    Returns:
        List[Model]: The parsed models.
    """
    models = []

    enum_list = xtx.get_children_of_enum(schema)
    base_list = xtx.get_children_of_base(schema)
    object_list = xtx.get_children_of_object(schema)
    operations_list = xtx.get_children_of_operation(schema)

    for obj in enum_list + base_list + object_list:
        model = ModelObject().build(obj)
        models.append(model)

    # scan for paginated responses
    # use a dict for efficiency to prevent duplicates
    pageables = {}
    operations = [x for x in operations_list if x.is_pageable]

    for operation in operations:
        # in theory we should only allow base or object here but this is already validated in model_validator.py
        pageables[operation.value.name] = operation.value

    for entity in pageables.values():
        model = get_paginated_object(entity, stringcase.pascalcase(entity.name))

        # find index and insert one before the object
        index = [i for i, x in enumerate(models) if x.name == entity.name][0]
        models.insert(index, model)

    return models


def get_paginated_object(obj: Object, model_name: str) -> ModelObject:
    """Returns a pagable custom model that is used to return a given model.

    Args:
        obj (Object): The QSDL Object.
        model_name (str): The OpenApi Model-Name.

    Returns:
        Model: The pagable custom model.
    """

    # represents the model
    new_object = Object()
    new_object.name = model_name + "List"
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
    model = ModelObject().build(new_object)

    return model


def generate(schema: Schema, output_path: Path, config: Config):
    """Generator func for OpenAPI"""

    if not config.id_type in IDTYPE.__members__:
        raise ValueError("id_type must be `LONG` or `STRING`")

    if config.id_type == IDTYPE.LONG:
        id_type = "integer"
        id_type_format = "int64"
    else:
        id_type = "string"
        id_type_format = None

    # sets the id type and schema
    util.custom_types["ID"] = id_type
    util.custom_type_formats["ID"] = id_type_format
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
