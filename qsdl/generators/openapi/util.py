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

"""OpenAPI Generator Utility functions"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

import qsdl.dsl.textx as xtx

if TYPE_CHECKING:
    from qsdl.dsl.models import Base, Enum, Field, Object, Schema


# the parsed schema definition.
schema: Schema = None

# used to flag paths as used in order to prevent path duplicates in
# OpenAPI
used_paths: List[str] = []

custom_types = {
    "Int": "integer",
    "Long": "integer",
    "Float": "number",
    "Double": "number",
    "String": "string",
    "Boolean": "boolean",
    "ID": "integer",
    "Date": "string",
    "Object": "object",
}

custom_type_formats = {
    "Int": "int32",
    "Long": "int64",
    "Float": "float",
    "Double": "double",
    "String": None,
    "Boolean": None,
    "ID": "int64",
    "Date": "date-time",
    "Object": None,
}


def custom_type(input_type: str) -> str:
    """Converter map for custom types.

    Args:
        input_type (str): The type to map.

    Returns:
        str: The mapped type name or the input_type if it does not exist.
    """
    return custom_types.get(input_type, input_type)


def custom_type_format(input_type_format: str) -> str:
    """Converter map for custom formats.

    Args:
        input_type_format (str): The type_format to map.

    Returns:
        str: The mapped type_format name or input_type_format if it does not exist.
    """
    return custom_type_formats.get(input_type_format, None)


def is_supertype(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object is used somewhere as a supertype.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    base_list = xtx.get_children_of_base(schema)
    object_list = xtx.get_children_of_object(schema)

    for itr in base_list + object_list:
        if entity == itr.supertype:
            return True

    return False


def is_nested(entity: Union[Base, Object]) -> bool:
    """Checks if the provided Base or Object is nested into another Base or Object.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: [description]
    """
    base_list = xtx.get_children_of_base(schema)
    object_list = xtx.get_children_of_object(schema)

    for itr in base_list + object_list:
        for field in itr.fields:
            if field.value == entity and not field.is_relation:
                return True

    return False


def get_enum_values(entity: Enum) -> List[Enum]:
    """Returns all enum values.

    Args:
        entity (Enum): entity.Enum

    Returns:
        List[Enum]: All enum values.
    """
    values = []

    if entity._tx_fqn in ["entity.Enum"]:

        for value in entity.values:
            values.append(value)

    return values


def is_path_unique(operation_path: str) -> bool:
    """Checks if the operation path has already been used.

    Args:
        operation_path (str): The operation path.

    Returns:
        bool: True if the path has not been used yet.
    """
    ret = False

    if operation_path not in used_paths:
        used_paths.append(operation_path)
        ret = True

    return ret


def get_namespaces() -> list:
    """Return all NameSpaces.

    Returns:
        list[str]: All NameSpaces
    """
    namespaces = []

    for api in xtx.get_children_of_api(schema):
        if api.namespace and api.namespace not in namespaces:
            namespaces.append(api.namespace)

    return namespaces
