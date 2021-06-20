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

"""Spring Generator Utility functions"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from textx import model as xtx

if TYPE_CHECKING:
    from qsdl.dsl.models import Base, Enum, Object, Schema


# the parsed schema definition.
schema: Schema = None


custom_types = {
    "Int": "Integer",
    "Long": "Long",
    "Float": "Float",
    "Double": "Double",
    "String": "String",
    "Boolean": "Boolean",
    "ID": "Long",
    "Date": "OffsetDateTime",
    "Object": "Object",
    "Void": "Void",
}


def custom_type(input_type: str) -> str:
    """Converter map for custom types.

    Args:
        input_type (str): The type to map.

    Returns:
        str: The mapped type name or the input_type if it does not exist.
    """
    return custom_types.get(input_type, input_type)


def has_id(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has an ID.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        if entity.supertype:
            ret = has_id(entity.supertype)

            if ret:
                return True

        for field in entity.fields:

            if field.value.name == "ID":
                return True

    return ret


def has_list(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has an array.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.array:
                ret = True
                break

    return ret


def has_float(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has a float.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.value.name in ["Float", "Double"]:
                ret = True
                break

    return ret


def has_date(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has a date.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.value.name in ["Date"]:
                ret = True
                break

    return ret


def has_enum(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has an enum.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.value._tx_fqn in ["Enum"]:
                ret = True
                break

    return ret


def has_model(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has a base or object.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.value._tx_fqn in ["entity.Base", "entity.Object"]:
                ret = True
                break

    return ret


def has_required(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has an required attribute.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.is_required:
                ret = True
                break

    return ret


def has_relation(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has a relation.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.is_composition or field.is_aggregation:
                ret = True
                break

    return ret


def has_relation_not_nested(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object has a relation that is not nested.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if (field.is_composition or field.is_aggregation) and not field.is_nested:
                ret = True
                break

    return ret


def is_supertype(entity: Union[Base, Object]) -> bool:
    """Checks if the Base or Object is used somewhere as a supertype.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    base_list = xtx.get_children_of_type("Base", schema)
    object_list = xtx.get_children_of_type("Object", schema)

    for itr in base_list + object_list:
        if entity == itr.supertype:
            return True

    return False


def is_nested(entity: object) -> bool:
    """Checks if the provided object or base is nested.

    Args:
        entity (object): entity.Object or entity.Base

    Returns:
        bool: [description]
    """
    base_list = xtx.get_children_of_type("Base", schema)
    object_list = xtx.get_children_of_type("Object", schema)

    for itr in base_list + object_list:
        for field in itr.fields:
            if field.value == entity and field.is_nested:
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


def get_model_imports(entity):
    """Returns all imports for this model."""
    imports = []

    if entity._tx_fqn not in ["entity.Enum", "entity.Base", "entity.Object"]:
        raise ValueError

    # note: the order is already sorted
    if has_date(entity):
        _import = ["java.time.OffsetDateTime"]
        imports.extend(_import)

    if has_list(entity) or entity._tx_fqn != "entity.Enum":
        _import = ["java.util.*"]
        imports.extend(_import)

    # TODO: if use db
    _import = ["javax.persistence.*"]
    imports.extend(_import)

    if has_list(entity) or has_model(entity):
        _import = ["javax.validation.*"]
        imports.extend(_import)

    if has_required(entity):
        _import = ["javax.validation.constraints.*"]
        imports.extend(_import)

    _import = ["com.fasterxml.jackson.annotation.*"]
    imports.extend(_import)

    if has_date(entity):
        _import = ["org.springframework.format.annotation.DateTimeFormat"]
        imports.extend(_import)

    return imports
