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
from .models import HibernateFieldInfo, HibernateModelInfo, HibernateParentInfo, ModelClass, Parent


class Store:
    """Parsed data storage class"""

    schema: dsl.Schema = None
    config: Config = None
    models: List[ModelClass] = []


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
        fields = entity.fields if not has_aggregation else get_parent_fields(entity.name)

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


def is_supertype(entity: dsl.Base) -> bool:
    """Checks if the provided Base is used somewhere as a supertype.

    Args:
        entity (Base): entity.Base.

    Returns:
        bool: Returns True on detection.
    """
    base_list = xtx.get_children_of_base(Store.schema)
    object_list = xtx.get_children_of_object(Store.schema)

    for itr in base_list + object_list:
        if entity == itr.supertype:
            return True

    return False


def is_used(entity: Union[dsl.Base, dsl.Object]) -> bool:
    """Checks if the provided Base or Object is used anywhere.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: [description]
    """
    field_list = xtx.get_children_of_field(Store.schema)
    opr_list = xtx.get_children_of_operation(Store.schema)
    arg_list = xtx.get_children_of_argument(Store.schema)

    for itr in field_list + opr_list + arg_list:
        if itr.value == entity:
            return True

    return False


def is_aggregated(entity: dsl.Object, parent: dsl.Object) -> bool:
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


def get_model_imports(entity: Union[dsl.Enum, dsl.Base, dsl.Object]):
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

    return imports


def add_parents_to_model(models: List[ModelClass]):
    """Add all Models who are a domain parent to a Model.

    Args:
        models (List[ModelClass]): The list of all available models.
    """
    for model in models:

        if not model.is_object:
            continue

        parents = []
        parent_names = []

        parent_fields = get_parent_fields(model.name)
        parent_objects = [x.parent for x in parent_fields]

        for obj in parent_objects:
            # search in provided models list for a match to the current obj and filter duplicates
            result = [x for x in models if x.name == obj.name and x.name not in parent_names]
            _ = [parent_names.append(x.name) for x in result]

            result = [Parent().build(x, model) for x in result]

            parents.extend(result)

        model.parents = parents


def add_hibernate_info(models: List[ModelClass]):
    """Add hibernate related info to model and fields"""
    if not Store.config.database == "hibernate":
        return

    for model in models:

        if not model.is_object:
            continue

        model_info = HibernateModelInfo(model)
        model.hibernate = model_info

        for field in model.fields:
            field_info = HibernateFieldInfo(field)
            field.hibernate = field_info

        for parent in model.parents:
            parent_info = HibernateParentInfo(model, parent.model)
            parent.hibernate = parent_info


def get_model_for(obj_name: dsl.Object.name) -> ModelClass:
    """Returns the ModelClass for a given Object name.

    Args:
        obj_name (dsl.Object.name): Name of dsl.Object

    Returns:
        ModelClass: The matching ModelClass
    """
    ret = None

    for model in Store.models:
        if obj_name == model.name:
            ret = model

    return ret


def get_parent_for(obj_name: dsl.Object.name, parent_name: dsl.Object.name) -> Parent:
    """Returns the Parent object for the given child - parent Object names.

    Args:
        obj_name (dsl.Object.name): Name of dsl.Object

    Returns:
        ModelClass: The matching ModelClass
    """
    ret = None

    for model in Store.models:
        if obj_name == model.name:

            for parent in model.parents:
                if parent_name == parent.model.name:
                    ret = parent
    return ret


def get_parent_fields(obj_name: dsl.Object.name, filter_relations=True) -> List[dsl.Field]:
    """Returns all Objects whos Field value is this Object.

    Args:
        obj_name (dsl.Object.name): The Object which value the fields should have.
        filter_relations (bool, optional): Include only relation fields. Defaults to True.

    Returns:
        List[dsl.Field]: The list of Fields.
    """
    fields = []

    fields = xtx.get_children_of_field(Store.schema)

    fields = [x for x in fields if x.parent._tx_fqn == "entity.Object" and x.value.name == obj_name]

    fields = [x for x in fields if x.is_relation] if filter_relations else fields

    return fields
