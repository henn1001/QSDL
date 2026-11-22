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

from typing import ClassVar

import qsdl.casing as qfilter
import qsdl.dsl.textx as xtx
import qsdl.dsl.util as qutil
from qsdl import dsl
from qsdl.dsl.directives import NAMESPACE, QUERY

from . import models as spring
from .config import SPRING_PACKAGE, SPRING_SCALAR, SpringConfig, SpringScalarMapping


def package_namespace(source: dsl.Base | dsl.Object | dsl.Enum) -> str:
    """Resolve the package placeholder for a domain type."""
    if directive := source.directives.get(SPRING_PACKAGE):
        return directive.value
    return qfilter.lowercase(qutil.render_namespace(source) or "")


class Store:
    """Parsed data storage class"""

    schema: dsl.Schema = None
    config: SpringConfig = None
    models: ClassVar[list[spring.ModelClass]] = []
    apis: ClassVar[list[spring.ApiClass]] = []
    enums: ClassVar[list[spring.EnumClass]] = []
    package: spring.Package = None
    packages: ClassVar[list[spring.Package]] = []


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


# Java keywords and reserved literals cannot be used for generated fields.
# Keep the mapping local to the Spring generator; the original QSDL name remains
# available on each field's schema source for JSON and database mappings.
JAVA_RESERVED_IDENTIFIERS = frozenset(
    {
        "abstract",
        "assert",
        "boolean",
        "break",
        "byte",
        "case",
        "catch",
        "char",
        "class",
        "const",
        "continue",
        "default",
        "do",
        "double",
        "else",
        "enum",
        "extends",
        "final",
        "finally",
        "float",
        "for",
        "goto",
        "if",
        "implements",
        "import",
        "instanceof",
        "int",
        "interface",
        "long",
        "native",
        "new",
        "package",
        "private",
        "protected",
        "public",
        "return",
        "short",
        "static",
        "strictfp",
        "super",
        "switch",
        "synchronized",
        "this",
        "throw",
        "throws",
        "transient",
        "try",
        "void",
        "volatile",
        "while",
        "true",
        "false",
        "null",
        "_",
    }
)


def java_identifier(name: str) -> str:
    """Return a legal Java identifier for a QSDL member name."""
    identifier = qfilter.camelcase(name)
    return f"{identifier}_" if identifier in JAVA_RESERVED_IDENTIFIERS else identifier


def is_direct_query_filter(operation: dsl.Operation) -> bool:
    if len(operation.query_parameters) != 1:
        return False

    argument = operation.query_parameters[0]
    if argument.is_array:
        return False

    return isinstance(argument.value, (dsl.Base, dsl.Object))


def resolve_query_filter(operation: dsl.Operation) -> str | None:
    if not operation.query_parameters:
        return None

    if is_direct_query_filter(operation):
        return custom_type(operation.query_parameters[0].value)

    return qfilter.capitalcase(operation.name) + "Filter"


def _is_inline_body_operation(operation: dsl.Operation) -> bool:
    """Returns True if the operation has inline body parameters that require a request DTO.

    Qualifies when:
    - body_parameters is not empty
    - method is not GET or DELETE
    - NOT a single body param whose value is already a Base or Object reference
    """
    if not operation.body_parameters:
        return False
    if operation.directive.method and operation.directive.method.value in ("GET", "DELETE"):
        return False

    return not (
        len(operation.body_parameters) == 1 and isinstance(operation.body_parameters[0].value, (dsl.Base, dsl.Object))
    )


def resolve_request_body_dto(operation: dsl.Operation) -> str | None:
    """Return the generated DTO name for inline request body parameters, if any."""
    if not _is_inline_body_operation(operation):
        return None
    return qfilter.capitalcase(operation.name) + "Request"


def argument_type(argument: dsl.Argument) -> str:
    """Resolve a Java argument type, including request-specific DTO naming."""
    value = argument.value
    name = custom_type(value)
    if argument.is_body and isinstance(value, dsl.Base | dsl.Object) and needs_separate_request_response(value):
        return f"{name}Request"
    return name


def _scalar_mapping(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> SpringScalarMapping | None:
    directive = entity.directives.get(SPRING_SCALAR) if isinstance(entity, dsl.Scalar) else None
    return directive.value if directive is not None else None


def custom_type(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str:
    """Converts builtin types to generator specific types."""
    mapping = _scalar_mapping(entity)
    return mapping.type if mapping else custom_types.get(entity.name, entity.name)


def custom_type_entity(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str | None:
    """Return the scalar's explicit Java persistence type, if specified."""
    mapping = _scalar_mapping(entity)
    return mapping.entity if mapping else None


def custom_type_pattern(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str | None:
    """Converts builtin types to generator specific types."""
    mapping = _scalar_mapping(entity)
    return mapping.pattern if mapping else None


def add_parents_to_model(models: list[spring.ModelClass]) -> None:
    """Link parent models after all models have been constructed."""
    for model in models:
        if not model.is_object:
            continue

        parent_names = set()
        for field in get_parent_fields(model.name):
            name = field.parent.name
            if name in parent_names:
                continue
            parent_names.add(name)
            model.parents.extend(spring.Parent(parent, model) for parent in models if parent.name == name)


def add_request_info(models: list[spring.ModelClass]) -> None:
    """Post-processing step to set  has_request and nested_type_has_request flag"""
    for model in models:
        for model_field in model.fields:
            if model_field.is_base or model_field.is_object:
                nested_model = get_model_for(model_field.type)
                if nested_model:
                    model_field.nested_type_has_request = nested_model.has_request


def _apis_can_merge(first: spring.ApiClass, second: spring.ApiClass) -> bool:
    """Return whether two API declarations should produce one controller.

    APIs with the same name in different packages are separate top-level
    controllers. Generated APIs and APIs using ``@spring-controller`` are
    exceptions: both explicitly identify a controller that custom operations
    should be merged into.
    """
    if first.name.lower() != second.name.lower():
        return False

    # Compare rendered package paths rather than only the namespace. A
    # configuration may deliberately keep one layer in a shared package, and
    # those declarations must not produce two files at the same destination.
    if any(getattr(first.package, path) == getattr(second.package, path) for path in ("api", "controller", "service")):
        return True

    return (
        first.source.has_generated
        or second.source.has_generated
        or first.controller_target is not None
        or second.controller_target is not None
    )


def _prefer_api(first: spring.ApiClass, second: spring.ApiClass) -> spring.ApiClass:
    """Select the package/controller metadata to retain when APIs merge."""
    # A generated API owns the controller for its Object. This keeps
    # @spring-controller customizations in the Object's package.
    if first.source.has_generated != second.source.has_generated:
        return first if first.source.has_generated else second

    # @spring-controller targets an existing Object controller, even when that
    # Object has no generated CRUD operations.
    if first.model is not second.model:
        if first.model and second.controller_target:
            return first
        if second.model and first.controller_target:
            return second

    # For standalone APIs, explicit @spring-package outranks @namespace,
    # which outranks the configured fallback package.
    if first.package_priority != second.package_priority:
        return first if first.package_priority > second.package_priority else second

    return first


def sort_api_controller(api_list: list[spring.ApiClass]) -> list[spring.ApiClass]:
    """Reorganize API controllers and merge operations when appropriate."""
    api_store: list[spring.ApiClass] = []
    operation_order = {id(op): (i, j) for i, api in enumerate(api_list) for j, op in enumerate(api.operations)}

    for api in api_list:
        matching = [existing for existing in api_store if _apis_can_merge(existing, api)]
        if not matching:
            api_store.append(api)
            continue

        # Merge all matching declarations into the selected controller. A
        # generated/targeted Object API remains the package owner when present.
        for existing in matching:
            api_store.remove(existing)
            preferred = _prefer_api(existing, api)
            if preferred is existing:
                existing.operations.extend(api.operations)
                api = existing
            else:
                api.operations.extend(existing.operations)

        api_store.append(api)

    # Controller ownership should not change the order of its API declarations.
    for api in api_store:
        api.operations.sort(key=lambda op: operation_order[id(op)])

    return api_store


def get_model_for(obj_name: str) -> spring.ModelClass | None:
    """Return the generated model for a schema type name."""
    return next((model for model in Store.models if model.name == obj_name), None)


def request_type_name(ref: dsl.Base | dsl.Object | str) -> str:
    """Return the generated Java type used for a model in request payloads."""
    name = ref if isinstance(ref, str) else ref.name
    model = get_model_for(name)
    return f"{name}Request" if model and model.has_request else name


def get_parent_for(obj_name: str, parent_name: str) -> spring.Parent | None:
    """Find a parent's relation metadata for a child model."""
    if model := get_model_for(obj_name):
        return next((parent for parent in model.parents if parent.model.name == parent_name), None)
    return None


def get_field_for(model: spring.ModelClass, target: spring.ModelClass) -> spring.ModelField:
    """Return the last matching relation field, as used by repository lookups."""
    return next(field for field in reversed(model.fields) if field.type == target.name)


def get_parent_fields(obj_name: str) -> list[dsl.Field]:
    """Find relation fields on objects that reference the named object."""
    return [
        field
        for field in xtx.get_children_of_field(Store.schema)
        if isinstance(field.parent, dsl.Object) and field.value.name == obj_name and qutil.is_relation(field)
    ]


def extract_embedded_columns(fields: list[dsl.Field], prefix: str = "", dto_path: str = "") -> list[spring.ModelField]:
    """Flatten non-opaque base fields into Java entity fields."""
    model_fields = []

    for field in fields:
        if field.directive.is_transient:
            continue

        if isinstance(field.value, dsl.Base) and not (field.is_array or field.directive.is_opaque):
            embedded_prefix = prefix + qfilter.snakecase(field.name).lower() + "_"
            embedded_dto_path = dto_path + java_identifier(field.name) + "."
            model_fields.extend(extract_embedded_columns(field.value.fields, embedded_prefix, embedded_dto_path))
        elif prefix:
            name = qfilter.camelcase(prefix + qfilter.snakecase(field.name).lower())
            path = dto_path + java_identifier(field.name)
            model_fields.append(spring.ModelField(field, java_name=name, dto_nested_path=path))
        else:
            model_fields.append(spring.ModelField(field))

    return model_fields


def extract_fields_for_mapper(ref: dsl.Base | dsl.Object) -> list[dsl.Field]:
    """Extracts all fields (including nested ones) that are either a Object or a opaqued Base"""
    nested_objects = []

    for field in ref.fields:
        # Skip transient fields entirely - they are not part of the DB/entity model
        if field.directive.is_transient:
            continue

        if isinstance(field.value, dsl.Base):
            if field.directive.is_opaque:
                # Opaque base types need mappers for Request/Response conversion
                nested_objects.append(field)
            else:
                # Non-opaque base types are flattened, recurse into them
                extracted = extract_fields_for_mapper(field.value)
                nested_objects.extend(extracted)
        if isinstance(field.value, dsl.Object) and not qutil.is_relation(field):
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

        new_name = qfilter.capitalcase(operation.name) + "Filter"

        # For CRUD operations, use domain_object's namespace/package; for custom ops, use parent API's
        namespace_source = operation.domain_object if operation.domain_object else operation.parent
        filter_namespace = qutil.render_namespace(namespace_source)

        # Create a dsl.Base for this filter
        filter_base = dsl.Base(
            parent=Store.schema,
            name=new_name,
        )

        if filter_namespace is not None:
            filter_base.directives.attach_synthetic(NAMESPACE, filter_namespace)

        # Copy @spring-package directive from source if present (takes priority over namespace)
        package_directive = namespace_source.directives.get(SPRING_PACKAGE)
        if package_directive is not None:
            filter_base.directives.attach_synthetic(SPRING_PACKAGE, package_directive.value)

        # Convert query arguments to fields
        for argument in operation.query_parameters:
            field = dsl.Field(
                parent=filter_base,
                name=argument.name,
                value=argument.value,
                is_array=argument.is_array,
                is_required=argument.is_required,
            )
            field.directives.attach_synthetic(QUERY, True)
            filter_base.fields.append(field)

        # Build ModelClass from the filter base
        filter_models.append(spring.ModelClass(filter_base, is_query_filter=True, has_request=False))

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

        new_name = qfilter.capitalcase(operation.name) + "Request"

        # Derive namespace and package from the same source as filter models
        namespace_source = operation.domain_object if operation.domain_object else operation.parent
        request_namespace = qutil.render_namespace(namespace_source)

        request_base = dsl.Base(
            parent=Store.schema,
            name=new_name,
        )

        if request_namespace is not None:
            request_base.directives.attach_synthetic(NAMESPACE, request_namespace)

        # Copy @spring-package directive if present (same logic as filter models)
        package_directive = namespace_source.directives.get(SPRING_PACKAGE)
        if package_directive is not None:
            request_base.directives.attach_synthetic(SPRING_PACKAGE, package_directive.value)

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

        # Response.j2 produces the file because the model name already ends in "Request".
        request_models.append(spring.ModelClass(request_base, has_request=False))

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
        predicate=lambda f: f.directive.is_read_only or f.directive.is_write_only or isinstance(f.value, dsl.Object),
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
        if qutil.is_relation(field) or field.directive.is_hidden or field.directive.is_read_only:
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
        if qutil.is_relation(field) or field.directive.is_hidden or field.directive.is_write_only:
            continue

        if isinstance(field.value, (dsl.Base, dsl.Object)) and needs_split.get(field.value.name, False):
            type_set.add(field.value.name)
            collect_nested_response_types(field.value, type_set, needs_split)
