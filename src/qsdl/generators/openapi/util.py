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

"""Generator Utility functions"""

from __future__ import annotations

import qsdl.dsl.models as dsl
import qsdl.dsl.textx as xtx
import qsdl.dsl.util as qutil

from .config import Directive

# the parsed schema definition.
schema: dsl.Schema = None

# used to flag paths as used in order to prevent path duplicates in
# OpenAPI
used_paths: list[str] = []

custom_types = {
    "Int": "integer",
    "Long": "integer",
    "Float": "number",
    "Double": "number",
    "String": "string",
    "Boolean": "boolean",
    "ID": "integer",
    "Date": "string",
    "Datetime": "string",
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
    "Date": "date",
    "Datetime": "date-time",
    "Object": None,
}


def custom_type(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, custom_types, entity.name, Directive.TYPE, ["format", "pattern"], "type")


def custom_type_format(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str | None:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, custom_type_formats, None, Directive.TYPE, ["format", "pattern"], "format")


def custom_type_pattern(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str | None:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, {}, None, Directive.TYPE, ["format", "pattern"], "pattern")


def is_supertype(entity: dsl.Base | dsl.Object) -> bool:
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


def is_nested(entity: dsl.Base | dsl.Object) -> bool:
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


def get_enum_values(entity: dsl.Enum) -> list[dsl.Enum]:
    """Returns all enum values.

    Args:
        entity (Enum): entity.Enum

    Returns:
        list[Enum]: All enum values.
    """
    values = []

    if entity._tx_fqn in ["entity.Enum"]:

        for value in entity.values:

            if value.upper() in ["YES", "NO", "TRUE", "FALSE", "ON", "OFF"]:
                value = f"'{value}'"

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
