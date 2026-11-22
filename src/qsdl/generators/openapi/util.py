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

"""Generator Utility functions"""

import qsdl.dsl.textx as xtx
import qsdl.dsl.util as qutil
from qsdl import dsl
from qsdl.generators.directive_payloads import scalar_mapping

from .config import OPENAPI_SCALAR

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
    mapping = scalar_mapping(entity, OPENAPI_SCALAR)
    return mapping.type if mapping else custom_types.get(entity.name, entity.name)


def custom_type_format(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str | None:
    """Converts builtin types to generator specific types."""
    mapping = scalar_mapping(entity, OPENAPI_SCALAR)
    return mapping.format if mapping and mapping.format is not None else custom_type_formats.get(entity.name)


def custom_type_pattern(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str | None:
    """Converts builtin types to generator specific types."""
    mapping = scalar_mapping(entity, OPENAPI_SCALAR)
    return mapping.pattern if mapping else None


def get_enum_values(entity: dsl.Enum) -> list[dsl.Enum]:
    """Returns all enum values.

    Args:
        entity (Enum): entity.Enum

    Returns:
        list[Enum]: All enum values.
    """
    values = []

    if isinstance(entity, dsl.Enum):
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


def get_namespaces(schema: dsl.Schema) -> list[str]:
    """Return distinct OpenAPI tags in API declaration order."""
    return list(
        dict.fromkeys(
            namespace for api in xtx.get_children_of_api(schema) if (namespace := qutil.render_namespace(api))
        )
    )
