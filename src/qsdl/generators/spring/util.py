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

from __future__ import annotations

from pathlib import Path

import pathspec
import stringcase

import qsdl.dsl.textx as xtx
import qsdl.dsl.util as qutil
import qsdl.filter as qfilter
from qsdl import dsl

from . import models as spring
from .config import Config, Directive


class Store:
    """Parsed data storage class"""

    schema: dsl.Schema = None
    config: Config = None
    models: list[spring.ModelClass] = []
    apis: list[spring.ApiClass] = []
    enums: list[spring.EnumClass] = []
    package: spring.Package = None
    packages: list[spring.Package] = []
    is_id_long: bool = True


custom_types = {
    "Int": "Integer",
    "Long": "Long",
    "Float": "Float",
    "Double": "Double",
    "String": "String",
    "Boolean": "Boolean",
    "ID": "Long",
    "Date": "LocalDate",
    "Datetime": "OffsetDateTime",
    "Object": "ObjectNode",
    "Void": "Void",
}


def custom_type(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, custom_types, entity.name, Directive.TYPE, ["entity", "pattern"], "type")


def custom_type_entity(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, {}, None, Directive.TYPE, ["entity", "pattern"], "entity")


def custom_type_pattern(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str | None:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, {}, None, Directive.TYPE, ["entity", "pattern"], "pattern")


def remove_ignored_files(output_path: Path, api_files: list, model_files: list, supporting_files: list) -> None:
    """Removes all generated files mentioned in .qsdl-ignore.

    Utilizes the pathspec python package.
    https://github.com/cpburnz/python-path-specification

    Args:
        output_path (Path): [description]
        domain_files (list): [description]
        model_files (list): [description]
        supporting_files (list): [description]
    """
    ignorefile_path = output_path / ".qsdl-ignore"

    if ignorefile_path.is_file():
        supporting_files.remove((".qsdl-ignore.j2", ".qsdl-ignore"))

        # read the spec
        with open(ignorefile_path, encoding="utf-8") as infile:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", infile)

        # loop over each all files and remove matches
        # note the copy() - we dont want to modify the list directly
        for src, dest, _ in api_files.copy():
            if spec.match_file(dest):
                api_files.remove((src, dest, _))

        for src, dest, _ in model_files.copy():
            if spec.match_file(dest):
                model_files.remove((src, dest, _))

        for src, dest in supporting_files.copy():
            if spec.match_file(dest):
                supporting_files.remove((src, dest))


def has(
    entity: dsl.Base | dsl.Object,
    has_type: list = None,
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
        has_type (list, optional): [description]. Defaults to None.
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

    if isinstance(entity, dsl.Base | dsl.Object):
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
            if has_model and isinstance(field.value, dsl.Base | dsl.Object):
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
            if has_enum and isinstance(field.value, dsl.Enum):
                ret = True
                break

    return ret


def is_supertype(entity: dsl.Base | dsl.Object) -> bool:
    """Checks if the Base or Object is used somewhere as a supertype.

    Args:
        entity (Union[Base, Object]): Either entity.Base or entity.Object.

    Returns:
        bool: Returns True on detection.
    """
    base_list = xtx.get_children_of_base(Store.schema)
    object_list = xtx.get_children_of_object(Store.schema)

    for itr in base_list + object_list:
        supertypes = itr.supertypes
        if supertypes and entity in supertypes:
            return True
    return False


def add_parents_to_model(models: list[spring.ModelClass]) -> None:
    """Add all Models who are a domain parent to a Model.

    Args:
        models (list[spring.ModelClass]): The list of all available models.
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

            result = [spring.Parent().build(x, model) for x in result]

            parents.extend(result)

        model.parents = parents


def add_hibernate_info(models: list[spring.ModelClass]) -> None:
    """Add hibernate related info to model and fields"""
    if Store.config.database != "HIBERNATE":
        return

    for model in models:
        if not model.is_object:
            continue

        model_info = spring.HibernateModelInfo(model)
        model.hibernate = model_info

        for field in model.fields:
            field_info = spring.HibernateFieldInfo(field)
            field.hibernate = field_info

        for parent in model.parents:
            parent_info = spring.HibernateParentInfo(model, parent.model)
            parent.hibernate = parent_info


def sort_api_controller(api_list: list[spring.ApiClass]) -> list[spring.ApiClass]:
    """Reorganize api controllers and merge operations if needed"""
    api_store: dict[str, spring.ApiClass] = {}

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


def get_model_for(obj_name: dsl.Object.name) -> spring.ModelClass:
    """Returns the spring.ModelClass for a given Object name.

    Args:
        obj_name (dsl.Object.name): Name of dsl.Object

    Returns:
        spring.ModelClass: The matching spring.ModelClass
    """
    ret = None

    for model in Store.models:
        if obj_name == model.name:
            ret = model
            break

    return ret


def get_parent_for(obj_name: dsl.Object.name, parent_name: dsl.Object.name) -> spring.Parent:
    """Returns the spring.Parent object for the given child - parent Object names.

    Args:
        obj_name (dsl.Object.name): Name of dsl.Object

    Returns:
        spring.ModelClass: The matching spring.ModelClass
    """
    ret = None

    for model in Store.models:
        if obj_name == model.name:
            for parent in model.parents:
                if parent_name == parent.model.name:
                    ret = parent
    return ret


def get_field_for(model: spring.ModelClass, target: spring.ModelClass) -> spring.ModelField:
    """Returns the spring.ModelField with the type of target for the given spring.ModelClass.

    Args:
        model (spring.ModelClass): The spring.ModelClass where to search.
        target (spring.ModelClass): The spring.ModelClass type to search for.

    Returns:
        spring.ModelField: The matching spring.ModelField
    """
    ret = None

    for model_field in model.fields:
        if model_field.type == target.name:
            ret = model_field

    return ret


def get_parent_fields(obj_name: str, filter_relations: bool = True) -> list[dsl.Field]:
    """Returns all Objects whos Field value is this Object.

    Args:
        obj_name (str): The Object which value the fields should have.
        filter_relations (bool, optional): Include only relation fields. Defaults to True.

    Returns:
        list[dsl.Field]: The list of Fields.
    """
    fields = []

    fields = xtx.get_children_of_field(Store.schema)

    fields = [x for x in fields if isinstance(x.parent, dsl.Object) and x.value.name == obj_name]

    fields = [x for x in fields if x.is_relation] if filter_relations else fields

    return fields


def extract_embedded_columns(
    ref: dsl.Base | dsl.Object, prefix: str = "", dto_path: str = "", fields: list[dsl.Field] | None = None
) -> list[spring.ModelField]:
    """Recursively flattens Base type fields into columns with prefixes.

    Args:
        ref: The Base or Object reference to process
        prefix: Snake_case prefix for entity column names (e.g., "a_field_")
        dto_path: Nested DTO path for mapping (e.g., "aField.")
        fields: Optional pre-filtered list of fields to process

    Note: This function is only called for Base types WITHOUT @opaque directive.
    Base types with @opaque are stored as JSONB and don't reach this function.
    """
    model_fields = []

    # Use provided fields if available, otherwise use ref.fields
    dsl_fields = fields if fields is not None else ref.fields

    for dsl_field in dsl_fields:
        if isinstance(dsl_field.value, dsl.Base) and not (dsl_field.is_array or dsl_field.is_opaque):
            # Flatten Base types - recursively process nested Base fields
            embedded_prefix = prefix + qfilter.snakecase(dsl_field.name).lower() + "_"
            embedded_dto_path = dto_path + stringcase.camelcase(dsl_field.name) + "."
            embedded_fields = extract_embedded_columns(dsl_field.value, embedded_prefix, embedded_dto_path)
            model_fields.extend(embedded_fields)
        else:
            # Handle regular fields (non-Base types or Base types that are arrays/opaque)
            new_field = spring.ModelField().build(dsl_field)

            # Apply prefix to names if we're in a nested context
            if prefix:
                prefixed_snake = prefix + qfilter.snakecase(dsl_field.name).lower()
                new_field.name = stringcase.camelcase(prefixed_snake)
                new_field.json_key = prefixed_snake
                # Set the nested DTO path (remove trailing dot)
                new_field.dto_nested_path = dto_path + stringcase.camelcase(dsl_field.name)

            model_fields.append(new_field)

    return model_fields


def extract_fields_for_mapper(ref: dsl.Base | dsl.Object) -> list[dsl.Field]:
    """Extracts all fields (including nested ones) that are either a Object or a opaqued Base"""
    nested_objects = []

    for field in ref.fields:
        if isinstance(field.value, dsl.Base):
            if field.is_opaque:
                # Opaque base types need mappers for Request/Response conversion
                nested_objects.append(field)
            else:
                # Non-opaque base types are flattened, recurse into them
                extracted = extract_fields_for_mapper(field.value)
                nested_objects.extend(extracted)
        if isinstance(field.value, dsl.Object) and not field.is_relation:
            nested_objects.append(field)

    return nested_objects


def build_filter_models() -> list[spring.ModelClass]:
    """Build filter models from operations with query parameters.

    Creates a dsl.Base for each operation that has query arguments,
    then converts it to a ModelClass.

    Returns:
        list[spring.ModelClass]: The parsed filter models.
    """
    filter_models = []

    operations = xtx.get_children_of_operation(Store.schema)

    for operation in operations:
        # Skip operations without query parameters
        if not operation.query_parameters:
            continue

        new_name = stringcase.capitalcase(operation.name) + "Filter"

        # Create a dsl.Base for this filter
        filter_base = dsl.Base(
            parent=Store.schema,
            name=new_name,
            namespace=operation.parent.namespace if hasattr(operation.parent, "namespace") else None,
        )

        # Convert query arguments to fields
        for argument in operation.query_parameters:
            field = dsl.Field(
                parent=filter_base,
                name=argument.name,
                value=argument.value,
                is_array=argument.is_array,
                is_required=argument.is_required,
                is_query=True,
            )
            filter_base.fields.append(field)

        # Build ModelClass from the filter base
        filter_model = spring.ModelClass().build(filter_base)
        filter_model.has_request = False  # we do not want a request class
        filter_models.append(filter_model)

    return filter_models
