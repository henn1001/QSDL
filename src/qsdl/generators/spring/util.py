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


def is_direct_query_filter(operation: dsl.Operation) -> bool:
    if len(operation.query_parameters) != 1:
        return False

    argument = operation.query_parameters[0]
    if argument.is_array:
        return False

    return isinstance(argument.value, (dsl.Base, dsl.Object))


def resolve_query_filter(operation: dsl.Operation) -> tuple[bool, str | None]:
    if not operation.query_parameters:
        return False, None

    if is_direct_query_filter(operation):
        argument = operation.query_parameters[0]
        return True, custom_type(argument.value)

    return True, stringcase.capitalcase(operation.name) + "Filter"


def _is_inline_body_operation(operation: dsl.Operation) -> bool:
    """Returns True if the operation has inline body parameters that require a request DTO.

    Qualifies when:
    - body_parameters is not empty
    - method is not GET or DELETE
    - NOT a single body param whose value is already a Base or Object reference
    """
    if not operation.body_parameters:
        return False
    if operation.method and operation.method.upper() in ("GET", "DELETE"):
        return False

    return not (
        len(operation.body_parameters) == 1 and isinstance(operation.body_parameters[0].value, (dsl.Base, dsl.Object))
    )


def resolve_request_body_dto(operation: dsl.Operation) -> tuple[bool, str | None]:
    """Returns (uses_dto, dto_name) for an operation's inline body parameters.

    Mirrors resolve_query_filter for write operations.
    """
    if not _is_inline_body_operation(operation):
        return False, None
    return True, stringcase.capitalcase(operation.name) + "Request"


def custom_type(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, custom_types, entity.name, Directive.TYPE, ["entity", "pattern"], "type")


def custom_type_entity(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, {}, None, Directive.TYPE, ["entity", "pattern"], "entity")


def custom_type_pattern(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str | None:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, {}, None, Directive.TYPE, ["entity", "pattern"], "pattern")


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
            if has_query and (field.is_query or field.is_query_list):
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


def add_request_info(models: list[spring.ModelClass]) -> None:
    """Post-processing step to set  has_request and nested_type_has_request flag"""
    for model in models:
        for model_field in model.fields:
            if model_field.is_base or model_field.is_object:
                nested_model = get_model_for(model_field.type)
                if nested_model:
                    model_field.nested_type_has_request = nested_model.has_request


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
        # Skip transient fields entirely - they are not part of the DB/entity model
        if dsl_field.is_transient:
            continue

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
        # Skip transient fields entirely - they are not part of the DB/entity model
        if field.is_transient:
            continue

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

        if is_direct_query_filter(operation):
            continue

        new_name = stringcase.capitalcase(operation.name) + "Filter"

        # For CRUD operations, use domain_object's namespace/package; for custom ops, use parent API's
        namespace_source = operation.domain_object if operation.domain_object else operation.parent
        filter_namespace = getattr(namespace_source, "namespace", None)

        # Create a dsl.Base for this filter
        filter_base = dsl.Base(
            parent=Store.schema,
            name=new_name,
            namespace=filter_namespace,
        )

        # Copy @spring-package directive from source if present (takes priority over namespace)
        spring_package_directive = qutil.get_directive_of_name(Directive.PACKAGE, namespace_source)
        if spring_package_directive:
            filter_base.directives = [spring_package_directive]

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
        # The namespace was already set on filter_base and will be picked up by build()
        filter_model = spring.ModelClass().build(filter_base)
        filter_model.has_request = False
        filter_models.append(filter_model)

    return filter_models


def build_request_body_models() -> list[spring.ModelClass]:
    """Build request-body DTOs for write operations with inline scalar parameters.

    For each qualifying operation a synthetic dsl.Base named ``{Op}Request`` is created
    and converted to a ModelClass (has_request=False, has_response=True so that
    Response.j2 generates ``{Op}Request.java`` — the suffix is baked into the name).

    Mirrors build_filter_models() for GET query-filter DTOs.
    """
    request_models = []

    operations = xtx.get_children_of_operation(Store.schema)

    for operation in operations:
        if not _is_inline_body_operation(operation):
            continue

        new_name = stringcase.capitalcase(operation.name) + "Request"

        # Derive namespace and package from the same source as filter models
        namespace_source = operation.domain_object if operation.domain_object else operation.parent
        request_namespace = getattr(namespace_source, "namespace", None)

        request_base = dsl.Base(
            parent=Store.schema,
            name=new_name,
            namespace=request_namespace,
        )

        # Copy @spring-package directive if present (same logic as filter models)
        spring_package_directive = qutil.get_directive_of_name(Directive.PACKAGE, namespace_source)
        if spring_package_directive:
            request_base.directives = [spring_package_directive]

        # Convert body arguments to fields on the synthetic base
        for argument in operation.body_parameters:
            request_field = dsl.Field(
                parent=request_base,
                name=argument.name,
                value=argument.value,
                is_array=argument.is_array,
                is_required=argument.is_required,
            )
            request_base.fields.append(request_field)

        request_model = spring.ModelClass().build(request_base)
        # has_request=False: avoids generating "{Name}Request.java" via Request.j2
        # (the "Request" suffix is already in model.name; Response.j2 produces the right file)
        request_model.has_request = False
        request_models.append(request_model)

    return request_models


def needs_separate_request_response(ref: dsl.Base | dsl.Object) -> bool:
    """
    Determine if Request and Response DTOs would differ.
    Returns True if:
    1. Any non-relation, non-hidden field has @readOnly or @writeOnly
    2. Any nested Base/Object field requires a split (transitive requirement)
    """
    return qutil.traverse_fields(
        ref,
        predicate=lambda f: f.is_read_only or f.is_write_only or isinstance(f.value, dsl.Object),
        include_nested=True,
        skip_relations=True,
        skip_hidden=True,
    )


def resolve_request_dto_usage() -> None:
    """
    Post-processing step to determine which models actually need Request/Response DTOs.

    A model needs a Request DTO if:
    1. It has its OWN @readOnly/@writeOnly fields (always generate), OR
    2. It has transitive split (nested types with @readOnly/@writeOnly) AND
       is actually used in request parameters

    A model needs a Response DTO if:
    1. It has its OWN @readOnly/@writeOnly fields (always generate), OR
    2. It has transitive split (nested types with @readOnly/@writeOnly) AND
       is actually used in response types

    This prevents generating unnecessary DTOs for types that:
    - Only have transitive splits (no own @readOnly/@writeOnly)
    - Are only used in one direction (request or response)

    Must be called after APIs are parsed.
    """
    dsl_types = {
        type_def.name: type_def for type_def in Store.schema.types if isinstance(type_def, (dsl.Base, dsl.Object))
    }
    needs_split = {name: needs_separate_request_response(ref) for name, ref in dsl_types.items()}

    # Collect all types used in request parameters and response types
    types_used_in_requests: set[str] = set()
    types_used_in_responses: set[str] = set()

    for operation in xtx.get_children_of_operation(Store.schema):
        # Collect request usage
        if operation.arguments:
            parameters = operation.arguments
        else:
            parameters = (
                operation.path_parameters
                + operation.query_parameters
                + operation.header_parameters
                + operation.body_parameters
            )

        for param in parameters:
            if not (param.is_body or param.is_path or param.is_query or param.is_header):
                continue
            if isinstance(param.value, (dsl.Base, dsl.Object)):
                types_used_in_requests.add(param.value.name)
                collect_nested_request_types(param.value, types_used_in_requests, needs_split)

        # Collect response usage
        if operation.value and isinstance(operation.value, (dsl.Base, dsl.Object)):
            types_used_in_responses.add(operation.value.name)
            collect_nested_response_types(operation.value, types_used_in_responses, needs_split)

    # Update has_request and has_response flags for models
    for model in Store.models:
        # Object types always generate both Request and Response DTOs
        # (they have auto-generated @readOnly ID fields)
        if model.is_object:
            model.has_request = True
            model.has_response = True
            continue

        # Base types: conditional generation based on usage
        if model.name not in needs_split:
            continue

        if not needs_split[model.name]:
            # No split needed - always use response DTO, never request
            model.has_request = False
            model.has_response = True
            continue

        # For Base types that need split (own or transitive), check actual schema-wide usage
        # Even if a type has its own @readOnly/@writeOnly, we only generate the DTOs
        # that are actually used across the entire schema
        model.has_request = model.name in types_used_in_requests
        model.has_response = model.name in types_used_in_responses

    add_request_info(Store.models)


def collect_nested_request_types(
    entity: dsl.Base | dsl.Object,
    type_set: set[str],
    needs_split: dict[str, bool],
) -> None:
    """
    Recursively collect nested Base/Object types that would need Request DTOs.
    Only adds types that have fields requiring the type to be used in requests.
    """
    for field in entity.fields:
        if field.is_relation or field.is_hidden or field.is_read_only:
            continue

        if isinstance(field.value, (dsl.Base, dsl.Object)) and needs_split.get(field.value.name, False):
            type_set.add(field.value.name)
            collect_nested_request_types(field.value, type_set, needs_split)


def collect_nested_response_types(
    entity: dsl.Base | dsl.Object,
    type_set: set[str],
    needs_split: dict[str, bool],
) -> None:
    """
    Recursively collect nested Base/Object types that would need Response DTOs.
    Only adds types that have fields requiring the type to be used in responses.
    """
    for field in entity.fields:
        if field.is_relation or field.is_hidden or field.is_write_only:
            continue

        if isinstance(field.value, (dsl.Base, dsl.Object)) and needs_split.get(field.value.name, False):
            type_set.add(field.value.name)
            collect_nested_response_types(field.value, type_set, needs_split)
