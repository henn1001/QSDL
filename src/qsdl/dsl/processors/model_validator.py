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
from urllib.parse import urlsplit, urlunsplit

import textx.metamodel
from textx import get_location

import qsdl.dsl.textx as xtx
from qsdl import dsl
from qsdl.dsl.diagnostics import Reporter, reporter_for
from qsdl.dsl.directives import AGGREGATION, COMPOSITION, METHOD, NAMESPACE, PATH

_PASCAL_CASE_NAME = re.compile(r"[A-Z][A-Za-z0-9]*")
_ENUM_VALUE_NAME = re.compile(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*")
_MEMBER_NAME = re.compile(r"(?:[a-z][a-z0-9]*(?:_[a-z0-9]+)+|[a-z][A-Za-z0-9]*)")
_NAMESPACE_NAME = re.compile(r"[A-Za-z][A-Za-z0-9]*")


def _validate_name(entity: object, name: str, convention: str, pattern: re.Pattern[str], code: str) -> None:
    """Validate a model name and report the location of its containing element."""
    if pattern.fullmatch(name) is None:
        entity_type = entity.__class__.__name__
        context = ""
        if isinstance(entity, dsl.Field):
            context = f" in {entity.parent.__class__.__name__} {entity.parent.name!r}"
        elif isinstance(entity, dsl.Argument):
            context = f" in Operation {entity.parent.name!r}"
        msg = f"The {entity_type} name {name!r}{context} must use {convention}."
        reporter_for(entity).error(code, msg, **get_location(entity), invalid=entity)


def _operation_location(operation: dsl.Operation, schema: dsl.Schema, reporter: Reporter) -> dict[str, object]:
    if not operation.is_generated:
        return get_location(operation)
    if reporter.collecting and operation.domain_object is not None:
        return get_location(operation.domain_object)
    return {"filename": schema._tx_filename}


def validate_declarations(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Check for logical input errors and provide better error messages.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    validate_server_url(schema, metamodel)
    validate_type_names(schema, metamodel)
    validate_namespaces(schema)
    validate_member_names(schema)
    validate_enum_values(schema)
    validate_custom_operations_path(schema, metamodel)
    validate_field_directives(schema, metamodel)


def validate_server_url(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Validate and normalize relative or absolute HTTP(S) server URLs.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    normalized_servers: list[str] = []
    for server in schema.servers:
        normalized_server = _normalize_server_url(server)
        if normalized_server is None:
            msg = (
                f"The server {server!r} must be a relative path beginning with '/' "
                "or an absolute http:// or https:// URL."
            )
            reporter_for(schema).error("LOG-302", msg, filename=schema._tx_filename)
            continue
        normalized_servers.append(normalized_server)

    schema.servers = normalized_servers


def _normalize_server_url(server: str) -> str | None:
    """Return a normalized server URL, or ``None`` when it is not supported."""
    if not server or any(
        character.isspace() or ord(character) < 0x20 or ord(character) == 0x7F for character in server
    ):
        return None

    try:
        parsed = urlsplit(server)
        if parsed.scheme:
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.hostname is None:
                return None
            # Accessing port makes urlsplit report malformed numeric ports.
            _ = parsed.port
        elif parsed.netloc or not parsed.path.startswith("/"):
            return None

        normalized_path = parsed.path.rstrip("/")
        if parsed.path.startswith("/") and not normalized_path:
            normalized_path = "/"

        return urlunsplit(parsed._replace(path=normalized_path))
    except ValueError:
        return None


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

    reporter = reporter_for(schema)
    type_codes = {dsl.Scalar: "SYN-001", dsl.Enum: "SYN-002", dsl.Base: "SYN-003", dsl.Object: "SYN-004"}
    for entity in entities:
        _validate_name(entity, entity.name, "PascalCase", _PASCAL_CASE_NAME, type_codes[type(entity)])
        if entity.name in names:
            msg = "Names for scalars, enums, bases and objects must be unique."
            reporter.error("SEM-101", msg, **get_location(entity))
            reporter.ambiguous_types.add(entity.name)
        names.add(entity.name)

        if isinstance(entity, dsl.Enum):
            for value in entity.values:
                if _ENUM_VALUE_NAME.fullmatch(value) is None:
                    msg = (
                        f"The Enum value {value!r} in Enum {entity.name!r} must use "
                        "ALL_CAPS with optional underscore-separated words."
                    )
                    reporter.error("SYN-005", msg, **get_location(entity), invalid=entity)


def validate_namespaces(schema: dsl.Schema) -> None:
    """Validate that namespaces are single alphanumeric identifiers beginning with a letter."""
    entities = [
        *xtx.get_children_of_enum(schema),
        *xtx.get_children_of_base(schema),
        *xtx.get_children_of_object(schema),
        *xtx.get_children_of_api(schema),
    ]

    for entity in entities:
        node = entity.directive.namespace
        namespace = node.value if node else None
        if not namespace or _NAMESPACE_NAME.fullmatch(namespace) is not None:
            continue

        name = getattr(entity, "name", None)
        label = f"{entity.__class__.__name__} {name!r}" if name is not None else entity.__class__.__name__
        msg = f"The namespace of {label} must be a single alphanumeric identifier beginning with a letter."
        reporter = reporter_for(schema)
        reporter.error("SYN-010", msg, **(node.location if reporter.collecting else get_location(entity)))
        entity.directives._invalidate(NAMESPACE)


def validate_member_names(schema: dsl.Schema) -> None:
    """Validate names of fields, operations, and arguments."""
    for field in xtx.get_children_of_field(schema):
        _validate_name(field, field.name, "camelCase or snake_case", _MEMBER_NAME, "SYN-006")

    for operation in xtx.get_children_of_operation(schema):
        _validate_name(operation, operation.name, "camelCase or snake_case", _MEMBER_NAME, "SYN-007")

    for argument in xtx.get_children_of_argument(schema):
        _validate_name(argument, argument.name, "camelCase or snake_case", _MEMBER_NAME, "SYN-008")


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
                reporter = reporter_for(schema)
                location = get_location(enum) if reporter.collecting else {"filename": schema._tx_filename}
                reporter.error("SEM-103", msg, **location, invalid=enum)
            seen.add(value)


def validate_reserved_words(schema: dsl.Schema) -> None:
    reporter = reporter_for(schema)
    errors = []
    first_entity = None

    for entity in xtx.get_children_of_object(schema):
        fields = entity.fields if id(entity) in reporter.unavailable_fields else entity.effective_fields
        match = [field for field in fields if field.name.lower() in {"id", "uid", "iv"}]

        if match:
            msg = f"The Object {entity.name} uses a reserved word {', '.join([f'"{x.name}"' for x in match])}."
            if reporter.collecting:
                reporter.error("SEM-609", msg, **get_location(entity), invalid=entity)
            errors.append(msg)
            first_entity = first_entity or entity

    if errors and not reporter.collecting:
        location = get_location(first_entity)
        reporter.error("SEM-609", "\n".join(errors), **location)


def validate_arguments(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Check that reference a maximum of one Object or Base.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    reporter = reporter_for(schema)

    for operation in xtx.get_children_of_operation(schema):
        method = operation.directive.method
        method_available = not operation.directives.is_invalid(METHOD)
        count = 0
        is_ref = False

        for argument in operation.arguments:
            if argument.is_query and argument.is_header:
                msg = f"The Argument {argument.name} of Operation {operation.name} cannot be both query and header."
                reporter.error("SEM-903", msg, **get_location(argument), invalid=operation)
                continue

            if not argument.is_query and not argument.is_header:
                count += 1

            if reporter.reference_available(argument.value.name) and isinstance(argument.value, dsl.Object | dsl.Base):
                is_ref = True

            if (
                (argument.is_query or (method_available and method is None))
                and isinstance(argument.value, dsl.Base)
                and reporter.type_available(argument.value)
            ):
                for field in argument.value.effective_fields:
                    if not reporter.reference_available(field.value.name):
                        reporter.invalid_nodes.add(id(operation))
                        continue
                    if isinstance(field.value, dsl.Object | dsl.Base):
                        msg = (
                            f"The Base type {argument.value.name} used as query parameter in operation {operation.name} "
                            f"contains a nested type field '{field.name}'. Query parameters with Base types must only contain scalar/enum fields."
                        )
                        reporter.error("SEM-906", msg, **get_location(field), invalid=operation)

        if is_ref and count > 1:
            msg = (
                f"The Operation {operation.name} references more than one Object "
                "or tries to mix them. Currently not supported"
            )
            reporter.error("SEM-907", msg, **get_location(operation), invalid=operation)

        if method is not None and method.value == "DELETE" and count:
            msg = f"The DELETE Operation {operation.name} specifies a body. This is not supported."
            reporter.error("SEM-908", msg, **get_location(operation), invalid=operation)


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
        if operation.directives.is_invalid(PATH):
            continue
        if not operation.directive.path or not operation.directive.path.value:
            msg = f"The custom Operation {operation.name} needs to specify a path."
            reporter_for(schema).error("SEM-803", msg, **get_location(operation), invalid=operation)


def validate_field_directives(schema: dsl.Schema, metamodel: textx.metamodel.TextXMetaModel) -> None:
    """Checks various rules that apply to field directives.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (textx.metamodel.TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    reporter = reporter_for(schema)
    bases = xtx.get_children_of_base(schema)
    objects = xtx.get_children_of_object(schema)

    for entity in bases + objects:
        duplicate_relation = []
        for field in entity.fields:
            reference_available = reporter.reference_available(field.value.name)
            is_relation = field.directive.is_composition or field.directive.is_aggregation
            # verify that read-only and write-only are not combined
            if field.directive.is_read_only and field.directive.is_write_only:
                msg = f"The Field {field.name} for {field.parent.name} cannot be both read-only and write-only."
                location = get_location(field) if reporter.collecting else {"filename": schema._tx_filename}
                reporter.error("SEM-606", msg, **location, invalid=field)

            # verify that queries are only used on scalars
            if (
                reference_available
                and (field.directive.is_query or field.directive.is_query_list)
                and not isinstance(field.value, dsl.Scalar | dsl.Enum)
            ):
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as query."
                reporter.error("SEM-610", msg, **get_location(field), invalid=field)

            # verify that composition and aggregation are mutually exclusive
            if field.directive.is_composition and field.directive.is_aggregation:
                msg = f"The Field {field.name} for {field.parent.name} cannot be both composition and aggregation."
                reporter.error("SEM-703", msg, **get_location(field), invalid=field)

            # verify that composition is used only on Objects
            if reference_available and field.directive.is_composition and not isinstance(field.value, dsl.Object):
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as composition."
                reporter.error("SEM-704", msg, **get_location(field), invalid=field)

            # verify that aggregation is used only on Objects and array
            if reference_available and field.directive.is_aggregation and not isinstance(field.value, dsl.Object):
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as aggregation."
                reporter.error("SEM-704", msg, **get_location(field), invalid=field)

            if is_relation and not field.is_array:
                msg = f"The Field {field.name} for {field.parent.name} declares a non-array as composition/aggregation."
                reporter.error("SEM-701", msg, **get_location(field), invalid=field)

            elif is_relation and not field.is_required:
                msg = (
                    f"The Field {field.name} for {field.parent.name} declares a non-required array as "
                    "composition/aggregation."
                )
                reporter.error("SEM-701", msg, **get_location(field), invalid=field)

            # verify that we prevent duplicate relations
            valid_relation = (
                reference_available
                and isinstance(field.value, dsl.Object)
                and isinstance(entity, dsl.Object)
                and field.value is not entity
                and field.is_array
                and field.is_required
                and not field.directives.is_invalid(COMPOSITION, AGGREGATION)
                and field.directive.is_composition != field.directive.is_aggregation
            )
            if is_relation and (not reporter.collecting or valid_relation):
                flag = (field.value, field.directive.is_aggregation, field.directive.is_composition)

                if flag not in duplicate_relation:
                    duplicate_relation.append(flag)
                else:
                    msg = f"The Field {field.name} for {field.parent.name} creates a duplicate relation."
                    reporter.error("SEM-707", msg, **get_location(field), invalid=field)

            # verify that composition/aggregation is used only in Objects
            if is_relation and not isinstance(entity, dsl.Object):
                msg = f"The Field {field.name} for {field.parent.name} declares a relation inside a Base."
                reporter.error("SEM-706", msg, **get_location(field), invalid=field)

            # verify that the relation is not self referencing
            if reference_available and field.value is entity:
                msg = f"The Field {field.name} for {field.parent.name} references itself."
                reporter.error("SEM-705", msg, **get_location(field), invalid=field)

            # verify that opaque is used only for Bases
            if reference_available and field.directive.is_opaque and not isinstance(field.value, dsl.Base):
                msg = f"The Field {field.name} for {field.parent.name} declares opaque on a non Base value."
                reporter.error("SEM-611", msg, **get_location(field), invalid=field)


def validate_operations(schema: dsl.Schema, completed: set[int]) -> None:
    """Check names across all operations and compare routes of completed operations."""
    reporter = reporter_for(schema)
    operations = xtx.get_children_of_operation(schema)
    if reporter.collecting:
        for operation in operations:
            _validate_operation_details(schema, operation, reporter)

    names: dict[str, dsl.Operation] = {}
    routes: dict[tuple[str, str], dsl.Operation] = {}
    duplicate_routes: list[tuple[dsl.Operation, dsl.Operation, tuple[str, str]]] = []

    for operation in operations:
        if (first := names.get(operation.name)) is not None:
            _report_collision(
                schema,
                reporter,
                operations[0],
                first,
                operation,
                "SEM-104",
                "Duplicate operation names found.",
                operation.name,
            )
        else:
            names[operation.name] = operation
        if reporter.collecting and (
            (not operation.is_generated and id(operation) not in completed) or id(operation) in reporter.invalid_nodes
        ):
            continue
        route = (operation.directive.method.value, operation.directive.path.value)
        if (first := routes.get(route)) is not None:
            duplicate_routes.append((first, operation, route))
        else:
            routes[route] = operation

    for first, operation, (method, path) in duplicate_routes:
        _report_collision(
            schema,
            reporter,
            operations[0],
            first,
            operation,
            "SEM-105",
            "Duplicate operation routes found.",
            f"{method} {path}",
        )

    # Preserve strict error precedence: collisions before operation details.
    if not reporter.collecting:
        for operation in operations:
            _validate_duplicate_arguments(schema, operation, reporter)
        for operation in operations:
            _validate_pagination(schema, operation, reporter)


def _report_collision(
    schema: dsl.Schema,
    reporter: Reporter,
    first_in_schema: dsl.Operation,
    first: dsl.Operation,
    duplicate: dsl.Operation,
    code: str,
    message: str,
    key: str,
) -> None:
    if reporter.collecting:
        message += f" {key!r} is used by {first.name!r} and {duplicate.name!r}."
        origin = first if duplicate.is_generated and not first.is_generated else duplicate
    else:
        origin = first_in_schema
    reporter.error(code, message, **_operation_location(origin, schema, reporter))


def _validate_operation_details(schema: dsl.Schema, operation: dsl.Operation, reporter: Reporter) -> None:
    _validate_duplicate_arguments(schema, operation, reporter)
    _validate_pagination(schema, operation, reporter)


def _validate_duplicate_arguments(schema: dsl.Schema, operation: dsl.Operation, reporter: Reporter) -> None:
    names = [argument.name for argument in operation.arguments]
    if len(names) != len(set(names)):
        msg = f"The Operation {operation.name} contains duplicated argument names."
        reporter.error("duplicate-argument", msg, **_operation_location(operation, schema, reporter), invalid=operation)


def _validate_pagination(schema: dsl.Schema, operation: dsl.Operation, reporter: Reporter) -> None:
    value = operation.value
    if value is not None and not reporter.reference_available(value.name):
        return
    if operation.directive.is_pageable and not isinstance(value, dsl.Object | dsl.Base):
        msg = f"The Operation {operation.name} needs to return a 'type' or 'base' when @pagination is used."
        reporter.error("SEM-805", msg, **_operation_location(operation, schema, reporter), invalid=operation)
