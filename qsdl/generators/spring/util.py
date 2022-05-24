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

"""Spring Generator Utility functions"""

from __future__ import annotations

from typing import List, Union

import qsdl.dsl.models as dsl
import qsdl.dsl.textx as xtx
from qsdl.generators.spring.models import ApiClass, ModelField

from .config import Config
from .models import HibernateFieldInfo, HibernateModelInfo, HibernateParentInfo, ModelClass, Parent, Package


class Store:
    """Parsed data storage class"""

    schema: dsl.Schema = None
    config: Config = None
    models: List[ModelClass] = []
    package: Package = None


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
    is_aggregated: bool = False,
    has_relation: bool = False,
    has_query: bool = False,
    has_enum: bool = False,
) -> bool:
    """Checks if the Base or Object has various attributes.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.
        has_type (List, optional): [description]. Defaults to None.
        has_list (bool, optional): [description]. Defaults to False.
        has_model (bool, optional): [description]. Defaults to False.
        has_required (bool, optional): [description]. Defaults to False.
        is_aggregated (bool, optional): [description]. Defaults to False.
        has_relation (bool, optional): [description]. Defaults to False.
        has_enum (bool, optional): [description]. Defaults to False.

    Returns:
        bool:  Returns True on detection.
    """
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        # for the aggregation check - we want to search the parent fields
        fields = entity.fields if not is_aggregated else get_parent_fields(entity.name)

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
            if is_aggregated and field.is_aggregation:
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

            # checks if there is a query attribute
            if has_enum and field.value._tx_fqn in ["entity.Enum"]:
                ret = True
                break

    return ret


def controller_has(
    entity: dsl.Api,
    has_objectnode: bool = False,
    has_enum: bool = False,
    has_gen_patch: bool = False,
) -> bool:
    """Checks if the Operations of a Api has various attributes.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.
        has_objectnode (bool, optional): [description]. Defaults to False.
        has_enum (bool, optional): [description]. Defaults to False.
        has_gen_patch (bool, optional): [description]. Defaults to False.

    Returns:
        bool:  Returns True on detection.
    """
    if entity._tx_fqn in ["entity.Api"]:

        for opr in entity.operations:

            # for the api imports, we only care about the operation return value
            # and if the body has exactly one parameter
            args = [opr.value] if opr.value else []

            if len(opr.body_parameters) == 1 and opr.body_parameters[0].value:
                args.append(opr.body_parameters[0].value)
            elif has_objectnode and len(opr.body_parameters) > 1:
                return True

            for arg in args:

                # checks for enum parameters
                if has_enum and arg and arg._tx_fqn == "entity.Enum":
                    return True

                # checks for objectnode parameters
                if has_objectnode and arg and arg.name == "Object":
                    return True

            # checks for generated patch endpoints
            if has_gen_patch and opr.method == "PATCH" and opr.is_generated:
                return True

    return False


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


def is_used(entity: Union[dsl.Base, dsl.Object], field_only: bool = False) -> bool:
    """Checks if the provided Base or Object is used anywhere.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.
        field_only (bool, optional): Checks only fields. Defaults to False.

    Returns:
        bool: [description]
    """
    entity_list = []
    entity_list += xtx.get_children_of_field(Store.schema)

    if not field_only:
        entity_list += xtx.get_children_of_operation(Store.schema)
        entity_list += xtx.get_children_of_argument(Store.schema)

    for itr in entity_list:
        if itr.value == entity:
            return True

    return False


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


def sort_api_controller(api_list: list[ApiClass]) -> list[ApiClass]:
    """Reorganize api controllers and merge operations if needed"""
    api_store = {}

    # we work with case insensitive names here to simplify things
    for api in api_list:
        api_name = api.name.lower()

        # make sure we merge custom apis into domain apis
        if api_name not in api_store:
            api_store[api_name] = api
        elif api_name in api_store and api.has_generated:
            api.operations.extend(api_store[api_name].operations)
            api_store[api_name] = api
        else:
            api_store[api_name].operations.extend(api.operations)

    return list(api_store.values())


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


def get_field_for(model: ModelClass, target: ModelClass) -> ModelField:
    """Returns the ModelField with the type of target for the given ModelClass.

    Args:
        model (ModelClass): The ModelClass where to search.
        target (ModelClass): The ModelClass type to search for.

    Returns:
        ModelField: The matching ModelField
    """
    ret = None

    for model_field in model.fields:
        if model_field.type == target.name:
            ret = model_field

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


def get_api_imports(api: dsl.Api) -> List[str]:
    """Helper for dynamic controller imports"""
    imports = []

    if controller_has(api, has_enum=True):
        imprt = f"import {Store.package.enum}.*;"
        imports.append(imprt)

    imprt = f"import {Store.package.domain}.*;"
    imports.append(imprt)

    imprt = f"import {Store.package.model}.*;"
    imports.append(imprt)

    # remove duplicates and sort
    imports = list(dict.fromkeys(imports))
    imports.sort()

    return imports


def get_controller_imports(api: dsl.Api, api_name: str) -> List[str]:
    """Helper for dynamic controller imports"""
    imports = []

    if controller_has(api, has_enum=True):
        imprt = f"import {Store.package.enum}.*;"
        imports.append(imprt)

    imprt = f"import {Store.package.api}.{api_name}Api;"
    imports.append(imprt)

    imprt = f"import {Store.package.domain}.*;"
    imports.append(imprt)

    imprt = f"import {Store.package.model}.*;"
    imports.append(imprt)

    if api.has_generated:
        imprt = f"import {Store.package.service}.{api_name}Service;"
        imports.append(imprt)

    if controller_has(api, has_gen_patch=True):
        imprt = f"import {Store.package.util}.Validator;"
        imports.append(imprt)

    # remove duplicates and sort
    imports = list(dict.fromkeys(imports))
    imports.sort()

    return imports


def get_service_imports(api: dsl.Api) -> List[str]:
    """Helper for dynamic service imports"""
    imports = []

    if controller_has(api, has_enum=True):
        imprt = f"import {Store.package.enum}.*;"
        imports.append(imprt)

    imprt = f"import {Store.package.domain}.*;"
    imports.append(imprt)

    imprt = f"import {Store.package.model}.*;"
    imports.append(imprt)

    imprt = f"import {Store.package.exception}.AppException;"
    imports.append(imprt)

    if Store.config.database == "hibernate":
        imprt = f"import {Store.package.repository}.*;"
        imports.append(imprt)

        imprt = f"import {Store.package.util}.PredicateBuilder;"
        imports.append(imprt)

    # remove duplicates and sort
    imports = list(dict.fromkeys(imports))
    imports.sort()

    return imports


def get_model_imports(entity: Union[dsl.Enum, dsl.Base, dsl.Object]) -> List[str]:
    """Helper for dynamic model imports"""
    imports = []

    if has(entity, has_enum=True):
        imprt = f"import {Store.package.enum}.*;"
        imports.append(imprt)

    imprt = f"import {Store.package.model}.*;"
    imports.append(imprt)

    imprt = f"import {Store.package.util}.Json;"
    imports.append(imprt)

    # remove duplicates and sort
    imports = list(dict.fromkeys(imports))
    imports.sort()

    return imports
