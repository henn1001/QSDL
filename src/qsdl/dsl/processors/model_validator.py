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

"""Model validation"""

import re

import textx.metamodel
from textx import get_location
from textx.exceptions import TextXSemanticError

import qsdl.dsl.textx as xtx
import qsdl.dsl.util as qutil
from qsdl import dsl

from . import CrudGeneratorEnum as CrudEnum

_PASCAL_CASE_NAME = re.compile(r"[A-Z][A-Za-z0-9]*")
_ENUM_VALUE_NAME = re.compile(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*")
_MEMBER_NAME = re.compile(r"(?:[a-z][a-z0-9]*(?:_[a-z0-9]+)+|[a-z][A-Za-z0-9]*)")
_DIRECTIVE_NAME = re.compile(r"(?:[a-z][a-z0-9]*(?:_[a-z0-9]+)+|[a-z][a-z0-9]*(?:-[a-z0-9]+)+|[a-z][A-Za-z0-9]*)")
_NAMESPACE_NAME = re.compile(r"[A-Z][a-zA-Z]*")


def _validate_name(entity: object, name: str, convention: str, pattern: re.Pattern[str]) -> None:
    """Validate a model name and report the location of its containing element."""
    if pattern.fullmatch(name) is None:
        entity_type = entity.__class__.__name__
        context = ""
        if isinstance(entity, dsl.Field):
            context = f" in {entity.parent.__class__.__name__} {entity.parent.name!r}"
        elif isinstance(entity, dsl.Argument):
            context = f" in Operation {entity.parent.name!r}"
        msg = f"The {entity_type} name {name!r}{context} must use {convention}."
        raise TextXSemanticError(msg, **get_location(entity))


def _get_location(entity: object, schema: dsl.Schema) -> dict[str, object]:
    """Return a source location, falling back for generated model elements."""
    if getattr(entity, "is_generated", False):
        return {"filename": schema._tx_filename}
    return get_location(entity)


def validate(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Check for logical input errors and provide better error messages.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    validate_server_url(schema, metamodel)
    validate_type_names(schema, metamodel)
    validate_member_names(schema)
    validate_directives(schema)
    validate_enum_values(schema)
    validate_reserved_words(schema)
    validate_arguments(schema, metamodel)
    validate_custom_operations_path(schema, metamodel)
    validate_crud_generator_directive(schema, metamodel)
    validate_field_directives(schema, metamodel)
    validate_no_circular_supertypes(schema, metamodel)


def validate_server_url(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Validate the naming convention for servers.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    for server in schema.servers:
        if not server.startswith("/"):
            msg = f"The server {server} must start with /"
            raise TextXSemanticError(msg, filename=schema._tx_filename)

        if server.endswith("/"):
            msg = f"The server {server} must not end with /"
            raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_type_names(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Validate type and enum-value naming conventions."""
    _ = metamodel

    names: set[str] = set()
    entities = [
        *xtx.get_children_of_scalar(schema),
        *xtx.get_children_of_enum(schema),
        *xtx.get_children_of_base(schema),
        *xtx.get_children_of_object(schema),
    ]

    for entity in entities:
        _validate_name(entity, entity.name, "PascalCase", _PASCAL_CASE_NAME)
        if entity.name in names:
            msg = "Names for scalars, enums, bases and objects must be unique."
            raise TextXSemanticError(msg, **get_location(entity))
        names.add(entity.name)

        if isinstance(entity, dsl.Object) and entity.namespace and _NAMESPACE_NAME.fullmatch(entity.namespace) is None:
            msg = f"The namespace of {entity._tx_fqn} {entity.name} must use PascalCase."
            raise TextXSemanticError(msg, **get_location(entity))

        if isinstance(entity, dsl.Enum):
            for value in entity.values:
                if _ENUM_VALUE_NAME.fullmatch(value) is None:
                    msg = (
                        f"The Enum value {value!r} in Enum {entity.name!r} must use "
                        "ALL_CAPS with optional underscore-separated words."
                    )
                    raise TextXSemanticError(msg, **get_location(entity))


def validate_member_names(schema: dsl.Schema) -> None:
    """Validate names of fields, operations, arguments, and custom directives."""
    for field in xtx.get_children_of_field(schema):
        _validate_name(field, field.name, "camelCase or snake_case", _MEMBER_NAME)

    for operation in xtx.get_children_of_operation(schema):
        _validate_name(operation, operation.name, "camelCase or snake_case", _MEMBER_NAME)

    for argument in xtx.get_children_of_argument(schema):
        _validate_name(argument, argument.name, "camelCase or snake_case", _MEMBER_NAME)

    for directive in xtx.get_children_of_directive(schema):
        _validate_name(directive, directive.name, "camelCase, snake_case, or kebab-case", _DIRECTIVE_NAME)


def _present_special_directive_names(entity: object) -> set[str]:
    """Return special directives represented by populated model attributes."""
    names: set[str] = set()

    if isinstance(entity, dsl.Enum | dsl.Base | dsl.Object | dsl.Api) and entity.namespace is not None:
        names.add("namespace")

    if isinstance(entity, dsl.Base | dsl.Object | dsl.Api) and entity.is_deprecated:
        names.add("deprecated")

    if isinstance(entity, dsl.Api) and entity.generate:
        names.add("generate")

    if isinstance(entity, dsl.Field):
        for attribute, directive_name in (
            ("is_query_list", "queryList"),
            ("is_query", "query"),
            ("is_read_only", "readOnly"),
            ("is_write_only", "writeOnly"),
            ("is_composition", "composition"),
            ("is_aggregation", "aggregation"),
            ("is_opaque", "opaque"),
            ("is_unique", "unique"),
            ("is_hidden", "hidden"),
            ("is_transient", "transient"),
            ("is_ignored", "ignore"),
            ("is_override", "override"),
        ):
            if getattr(entity, attribute):
                names.add(directive_name)

        for attribute, directive_name in (
            ("min_size", "minSize"),
            ("max_size", "maxSize"),
            ("default", "default"),
        ):
            if getattr(entity, attribute) is not None:
                names.add(directive_name)

    if isinstance(entity, dsl.Operation):
        if entity.is_pageable:
            names.add("pagination")

        for attribute, directive_name in (
            ("path", "path"),
            ("method", "method"),
            ("consumes", "consumes"),
            ("produces", "produces"),
        ):
            if getattr(entity, attribute) is not None:
                names.add(directive_name)

    return names


def _directive_entity_label(entity: object) -> str:
    """Return a useful label for duplicate-directive errors."""
    if isinstance(entity, dsl.Field):
        return f"Field {entity.name} of {entity.parent.name}"

    if isinstance(entity, dsl.Operation):
        return f"Operation {entity.name}"

    if isinstance(entity, dsl.Api):
        if isinstance(entity.parent, dsl.Object):
            return f"Api of Object {entity.parent.name}"
        return "Api"

    return f"{entity.__class__.__name__} {entity.name}"


def validate_directives(schema: dsl.Schema) -> None:
    """Reject repeated directive names on the same entity."""
    entities = [
        *xtx.get_children_of_scalar(schema),
        *xtx.get_children_of_enum(schema),
        *xtx.get_children_of_base(schema),
        *xtx.get_children_of_object(schema),
        *xtx.get_children_of_field(schema),
        *xtx.get_children_of_api(schema),
        *xtx.get_children_of_operation(schema),
    ]

    for entity in entities:
        seen_names = _present_special_directive_names(entity)
        custom_names: set[str] = set()

        for directive in entity.directives:
            if directive.name in seen_names or directive.name in custom_names:
                msg = f"The {_directive_entity_label(entity)} specifies @{directive.name} more than once."
                raise TextXSemanticError(msg, **get_location(directive))
            custom_names.add(directive.name)


def validate_enum_values(schema: dsl.Schema) -> None:
    """Validate that enum values are unique within each enum.

    Args:
        schema (Schema): The parsed schema definition.

    Raises:
        TextXSemanticError: Exception for duplicate enum values.
    """
    for enum in xtx.get_children_of_enum(schema):
        seen: set[str] = set()
        for value in enum.values:
            if value in seen:
                msg = f"The Enum {enum.name} contains the duplicate value {value}."
                raise TextXSemanticError(msg, filename=schema._tx_filename)
            seen.add(value)


def validate_reserved_words(schema: dsl.Schema) -> None:
    errors = []
    first_entity = None

    for entity in xtx.get_children_of_object(schema):
        fields = qutil.get_all_fields_as_list(entity)
        match = [x for x in fields if x.name.lower() in ["id", "uid", "iv"]]

        if match:
            msg = f"The Object {entity.name} uses a reserved word {', '.join([f'"{x.name}"' for x in match])}."
            errors.append(msg)
            first_entity = first_entity or entity

    if errors:
        location = get_location(first_entity) if first_entity else {"filename": schema._tx_filename}
        raise TextXSemanticError("\n".join(errors), **location)


def validate_arguments(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Check that reference a maximum of one Object or Base.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # loop for custom operations
    operations = xtx.get_children_of_operation(schema)

    for operation in operations:
        count = 0
        is_ref = False

        for argument in operation.arguments:
            if argument.is_query and argument.is_header:
                msg = f"The Argument {argument.name} of Operation {operation.name} cannot be both query and header."
                raise TextXSemanticError(msg, **get_location(argument))

            # we only wanty limit the request body to one value
            if not argument.is_query and not argument.is_header:
                count = count + 1

            if isinstance(argument.value, dsl.Object | dsl.Base):
                is_ref = True

            # validate that Base types used as query parameters only contain scalar fields
            if (argument.is_query or not operation.method) and isinstance(argument.value, dsl.Base):
                for field in qutil.get_all_fields_as_list(argument.value):
                    if isinstance(field.value, dsl.Object | dsl.Base):
                        msg = (
                            f"The Base type {argument.value.name} used as query parameter in operation {operation.name} "
                            f"contains a nested type field '{field.name}'. Query parameters with Base types must only contain scalar/enum fields."
                        )
                        raise TextXSemanticError(msg, **get_location(field))

        if is_ref and count > 1:
            msg = (
                f"The Operation {operation.name} references more than one Object "
                "or tries to mix them. Currently not supported"
            )
            raise TextXSemanticError(msg, **get_location(operation))

        if operation.method == "DELETE" and count:
            msg = f"The DELETE Operation {operation.name} specifies a body. This is not supported."
            raise TextXSemanticError(msg, **get_location(operation))


def validate_custom_operations_path(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Check that custom operations specify a path.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # loop for custom operations
    operations = xtx.get_children_of_operation(schema)

    for operation in operations:
        if not operation.path:
            msg = f"The custom Operation {operation.name} needs to specify a path."
            raise TextXSemanticError(msg, **get_location(operation))


def validate_field_directives(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Checks various rules that apply to field directives.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    bases = xtx.get_children_of_base(schema)
    objects = xtx.get_children_of_object(schema)

    for entity in bases + objects:
        duplicate_relation = []
        for field in entity.fields:
            # verify that read-only and write-only are not combined
            if field.is_read_only and field.is_write_only:
                msg = f"The Field {field.name} for {field.parent.name} cannot be both read-only and write-only."
                raise TextXSemanticError(msg, filename=schema._tx_filename)

            # verify that queries are only used on scalars
            if (field.is_query or field.is_query_list) and not isinstance(field.value, dsl.Scalar | dsl.Enum):
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as query."
                raise TextXSemanticError(msg, **get_location(field))

            # verify that composition and aggregation are mutually exclusive
            if field.is_composition and field.is_aggregation:
                msg = f"The Field {field.name} for {field.parent.name} cannot be both composition and aggregation."
                raise TextXSemanticError(msg, **get_location(field))

            # verify that composition is used only on Objects
            if field.is_composition and not isinstance(field.value, dsl.Object):
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as composition."
                raise TextXSemanticError(msg, **get_location(field))

            # verify that aggregation is used only on Objects and array
            if field.is_aggregation and not isinstance(field.value, dsl.Object):
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as aggregation."
                raise TextXSemanticError(msg, **get_location(field))

            if (field.is_composition or field.is_aggregation) and not field.is_array:
                msg = f"The Field {field.name} for {field.parent.name} declares a non-array as composition/aggregation."
                raise TextXSemanticError(msg, **get_location(field))

            if (field.is_composition or field.is_aggregation) and not field.is_required:
                msg = (
                    f"The Field {field.name} for {field.parent.name} declares a non-required array as "
                    "composition/aggregation."
                )
                raise TextXSemanticError(msg, **get_location(field))

            # verify that we prevent duplicate relations
            if field.is_aggregation or field.is_composition:
                flag = (field.value, field.is_aggregation, field.is_composition)

                if flag not in duplicate_relation:
                    duplicate_relation.append(flag)
                else:
                    msg = f"The Field {field.name} for {field.parent.name} creates a duplicate relation."
                    raise TextXSemanticError(msg, **get_location(field))

            # verify that composition/aggregation is used only in Objects
            if (field.is_composition or field.is_aggregation) and not isinstance(entity, dsl.Object):
                msg = f"The Field {field.name} for {field.parent.name} declares a relation inside a Base."
                raise TextXSemanticError(msg, **get_location(field))

            # verify that the relation is not self referencing
            if field.value == entity:
                msg = f"The Field {field.name} for {field.parent.name} references itself."
                raise TextXSemanticError(msg, **get_location(field))

            # verify that opaque is used only for Bases
            if field.is_opaque and not isinstance(field.value, dsl.Base):
                msg = f"The Field {field.name} for {field.parent.name} declares opaque on a non Base value."
                raise TextXSemanticError(msg, **get_location(field))


def validate_crud_generator_directive(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Check if the requested crud operations are valid

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    apis = xtx.get_children_of_api(schema)

    apis = [x for x in apis if x.generate]

    for api in apis:
        match = [x for x in api.generate if not CrudEnum.has_member_key(x)]

        if match:
            msg = f"The Api of Object {api.parent.name} @generate directive specifies a invalid value. Needs to be one or multiples of {[e.value for e in CrudEnum]}"
            raise TextXSemanticError(msg, **get_location(api))


def validate_operations(schema: dsl.Schema) -> None:
    """Check for duplicate operation names and method/path routes.

    Args:
        schema (Schema): The parsed schema definition.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    names = []
    routes = []

    operations = xtx.get_children_of_operation(schema)

    for operation in operations:
        names.append(operation.name)
        routes.append((operation.method, operation.path))

    if len(names) != len(set(names)):
        msg = "Duplicate operation names found."
        raise TextXSemanticError(msg, **_get_location(operations[0], schema))

    if len(routes) != len(set(routes)):
        msg = "Duplicate operation routes found."
        raise TextXSemanticError(msg, **_get_location(operations[0], schema))

    # validate that path arguments do not clash with query/body arguments
    for operation in operations:
        arg_names = [x.name for x in operation.arguments]

        if len(arg_names) != len(set(arg_names)):
            msg = f"The Operation {operation.name} contains duplicated argument names."
            raise TextXSemanticError(msg, **_get_location(operation, schema))

    # validate that pagination is only used for object and base responses
    for operation in operations:
        if (operation.is_pageable and not operation.value) or (
            operation.is_pageable and not isinstance(operation.value, dsl.Object | dsl.Base)
        ):
            msg = f"The Operation {operation.name} needs to return a 'type' or 'base' when @pagination is used."
            raise TextXSemanticError(msg, **_get_location(operation, schema))


def validate_no_circular_supertypes(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Detects and prevents circular inheritance in supertypes for Base entities."""
    _ = metamodel

    def dfs(entity: dsl.Base | dsl.Object, path: list[dsl.Base | dsl.Object]) -> None:
        if entity in path:
            cycle = " -> ".join([b.name for b in path + [entity]])
            msg = f"Circular inheritance detected in Base supertypes: {cycle}"
            raise TextXSemanticError(msg, **get_location(entity))
        for supertype in entity.supertypes:
            dfs(supertype, path + [entity])

    bases = xtx.get_children_of_base(schema)
    objects = xtx.get_children_of_object(schema)

    for entity in bases + objects:
        dfs(entity, [])
