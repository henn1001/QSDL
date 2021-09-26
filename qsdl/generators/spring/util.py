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

from typing import List, Union

import qsdl.dsl.models as dsl
import qsdl.dsl.textx as xtx

from .config import Config
from .models import ModelClass

# the parsed schema definition.
schema: dsl.Schema = None
config: Config = None


custom_types = {
    "Int": "Integer",
    "Long": "Long",
    "Float": "Float",
    "Double": "Double",
    "String": "String",
    "Boolean": "Boolean",
    "ID": "Long",
    "Date": "OffsetDateTime",
    "Object": "ObjectNode",
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


def has(
    entity: Union[dsl.Base, dsl.Object],
    has_type: List = None,
    has_list: bool = False,
    has_model: bool = False,
    has_required: bool = False,
    has_required_ignore_id: bool = False,
    has_aggregation: bool = False,
    has_relation: bool = False,
    has_query: bool = False,
) -> bool:
    """Checks if the Base or Object has various attributes.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.
        has_type (List, optional): [description]. Defaults to None.
        has_list (bool, optional): [description]. Defaults to False.
        has_model (bool, optional): [description]. Defaults to False.
        has_required (bool, optional): [description]. Defaults to False.
        has_aggregation (bool, optional): [description]. Defaults to False.
        has_relation (bool, optional): [description]. Defaults to False.

    Returns:
        bool:  Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        # for the aggregation check - we want to search the parent fields
        fields = entity.fields if not has_aggregation else get_parent_fields(entity)

        for field in fields:

            # checks for scalar types
            if has_type and field.value.name in has_type:
                ret = True
                break

            # check for lists
            if has_list and field.is_array:
                ret = True
                break

            # check for base and object references
            if has_model and field.value._tx_fqn in ["entity.Base", "entity.Object"]:
                ret = True
                break

            # checks if there is a required attribute
            if has_required and field.is_required:
                ret = True
                break

            if has_required_ignore_id and field.name != "id" and field.is_required:
                ret = True
                break

            # checks if the Object is aggregated somewhere
            if has_aggregation and field.is_aggregation:
                ret = True
                break

            # checks if the Object has a relation
            if has_relation and (field.is_composition or field.is_aggregation):
                ret = True
                break

            # checks if there is a query attribute
            if has_query and field.is_query:
                ret = True
                break

    return ret


def is_supertype(entity: Union[dsl.Base, dsl.Object]) -> bool:
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


def is_nested(entity: Union[dsl.Base, dsl.Object]) -> bool:
    """Checks if the provide dBase or Object is nested into another Base or Object.

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


def is_aggregation(entity: dsl.Object, parent: dsl.Object) -> bool:
    """Checks if the first Object is aggregated in the second Object.

    Args:
        entity (Object): entity.Object.
        parent (Object): entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Object"] and parent._tx_fqn in ["entity.Object"]:

        for field in parent.fields:

            if field.is_aggregation and field.value == entity:
                ret = True
                break

    return ret


def get_model_imports(entity):
    """Returns all imports for this model."""
    imports = []

    if entity._tx_fqn not in ["entity.Enum", "entity.Base", "entity.Object"]:
        raise ValueError

    # note: the order is already sorted
    if has(entity, has_type=["Date"]):
        _import = ["java.time.OffsetDateTime"]
        imports.extend(_import)

    if has(entity, has_list=True) or entity._tx_fqn != "entity.Enum":
        _import = ["java.util.*"]
        imports.extend(_import)

    _import = ["javax.persistence.*"]
    imports.extend(_import)

    if has(entity, has_list=True) or has(entity, has_model=True):
        _import = ["javax.validation.*"]
        imports.extend(_import)

    if has(entity, has_required=True):
        _import = ["javax.validation.constraints.*"]
        imports.extend(_import)

    _import = ["com.fasterxml.jackson.annotation.*"]
    imports.extend(_import)

    if has(entity, has_type=["Object"]):
        _import = ["com.fasterxml.jackson.databind.node.ObjectNode"]
        imports.extend(_import)

    if has(entity, has_type=["Date"]):
        _import = ["org.springframework.format.annotation.DateTimeFormat"]
        imports.extend(_import)

    return imports


def get_parent_fields(obj: dsl.Object) -> List[dsl.Field]:
    """Returns all Objects whos Field value is this Object.

    Args:
        schema (Schema): The QSDL schema model.
        obj (Object): entity.Object

    Returns:
        List[Field]: [entity.Field]
    """
    fields = []

    fields = xtx.get_children_of_field(schema)

    fields = [x for x in fields if x.is_composition or x.is_aggregation]

    fields = [x for x in fields if x.value == obj and x.parent._tx_fqn == "entity.Object"]

    return fields


def get_filtered_fields_as_list(entity: dsl.Object) -> List[dsl.Field]:
    """Returns all fields ob a object including its supertype as list.

    Exclude composition or aggregations.

    Args:
        entity (object): entity.Object

    Returns:
        list: [entity.Field]
    """
    fields = []

    for field in entity.fields:
        if not field.is_composition and not field.is_aggregation:
            fields.append(field)

    return fields


def get_id_for_repo(entity: dsl.Object) -> str:
    """Returns the ID name of a API Object.

    If no ID is found, we return ID regardless because that is
    the default internal id.

    Args:
        entity (Object): entity.Object.

    Returns:
        str: Returns ID name for the query
    """
    ret = None
    tmp = entity

    while True:
        for field in tmp.fields:

            if field.value.name == "ID":
                ret = field.name
                break

        if not tmp.supertype:
            break

        tmp = tmp.supertype

    if not ret:
        ret = "ID"

    return ret.capitalize()


def get_parent_id_for_repo(entity: dsl.Object) -> str:
    """Returns the ID name of a API Object.

    If no ID is found, we return ID regardless because that is
    the default internal id.

    Args:
        entity (Object): entity.Object.

    Returns:
        str: Returns ID name for the query
    """
    ret = None
    tmp = entity

    while True:
        for field in tmp.fields:

            if field.value.name == "ID":
                ret = field.name
                break

        if not tmp.supertype:
            break

        tmp = tmp.supertype

    ret = entity.name.lower() + ret.capitalize()

    return ret
