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

"""QSDL Utility functions"""

from collections.abc import Callable, Iterable, Iterator

import qsdl.dsl.textx as xtx
from qsdl import dsl


def description_wrapper(raw_string: str) -> list[str]:
    """Formats a multiline string if needed"""
    strings = []

    if raw_string:
        # first we split by new lines
        splits = raw_string.split("\n")

        # our ident is defined by the first line that starts with non whitespace
        first_line_detected = False
        count = 0

        for string in splits:
            # we skip the beginning and end of the comment if it is empty
            # we also strip the string if the first_line_detected logic does not apply
            if string.startswith('"""') or string.endswith('"""'):
                # dont strip when we detected a first_line and we rather want to remove padding
                if string.endswith('"""') and count == 0:
                    string = string.strip()

                string = string.replace('"""', "")

                if string.isspace() or not string:
                    continue
            else:
                # remove all quotes
                if string.startswith('"') or string.endswith('"'):
                    string = string.replace('"', "")

                # our first valid line starts after the tripple quote
                # it should be a non space character
                # we count the spaces via lstrip
                if string and not string.isspace() and not first_line_detected:
                    count = len(string) - len(string.lstrip(" "))
                    first_line_detected = True

            # after we identified the ident - calc padding and remove it
            padding = " " * count
            string = string.replace(padding, "", 1) if padding else string

            # finally add string to the list
            strings.append(string)

    return strings


def iter_object_fields(schema: dsl.Schema, *, include_ignored: bool = False) -> Iterator[dsl.Field]:
    """Yield each Object's fields in order, using the generation view unless requested otherwise."""
    for obj in xtx.get_children_of_object(schema):
        yield from obj.effective_fields if include_ignored else obj.generation_fields


def get_compositions(schema: dsl.Schema, obj: dsl.Object, *, include_ignored: bool = False) -> list[dsl.Field]:
    """Return composition fields referencing the given Object."""
    return [
        field
        for field in iter_object_fields(schema, include_ignored=include_ignored)
        if field.value is obj and field.directive.is_composition
    ]


def get_aggregation(schema: dsl.Schema, obj: dsl.Object, *, include_ignored: bool = False) -> list[dsl.Field]:
    """Return aggregation fields referencing the given Object."""
    return [
        field
        for field in iter_object_fields(schema, include_ignored=include_ignored)
        if field.value is obj and field.directive.is_aggregation
    ]


def get_query_fields(fields: Iterable[dsl.Field]) -> list[dsl.Field]:
    """Return fields marked @query or @queryList from the caller's field view."""
    return [x for x in fields if x.directive.is_query or x.directive.is_query_list]


def get_composition_fields(schema: dsl.Schema, obj_name: str) -> list[dsl.Field]:
    """Return visible Object array fields referencing the named Object, except aggregations."""
    return [
        x
        for x in iter_object_fields(schema)
        if x.value.name == obj_name and x.is_array and not x.directive.is_aggregation
    ]


def traverse_fields(
    entity: dsl.Object | dsl.Base,
    predicate: Callable[[dsl.Field], bool],
    include_nested: bool = True,
    skip_relations: bool = True,
    skip_hidden: bool = True,
    skip_transient: bool = True,
    skip_ignored: bool = True,
) -> bool:
    """Recursively traverse fields of an Object or Base and check if any field matches a predicate.

    This utility function provides a generic way to traverse all fields (including nested Base/Object fields)
    and evaluate a condition on each field.

    Args:
        entity: The Object or Base to traverse
        predicate: A callable that takes a dsl.Field and returns True/False
        include_nested: Whether to recursively check nested Base/Object fields (default: True)
        skip_relations: Whether to skip relation fields (default: True)
        skip_hidden: Whether to skip fields that are excluded from api layer (default: True)
        skip_transient: Whether to skip fields that are excluded from database layer (default: True)
        skip_ignored: Whether to skip fields that are excluded from both layers (default: True)

    Returns:
        bool: True if any field (including nested) matches the predicate, False otherwise

    Example:
        # Check if any field has @readOnly
        has_readonly = traverse_fields(
            entity,
            lambda f: f.directive.is_read_only,
            include_nested=True
        )

        # Check if any non-relation field has @writeOnly
        has_writeonly = traverse_fields(
            entity,
            lambda f: f.directive.is_write_only,
            skip_relations=True
        )
    """
    fields = entity.generation_fields if skip_ignored else entity.effective_fields
    for dsl_field in fields:
        if skip_relations and is_relation(dsl_field):
            continue
        if skip_hidden and dsl_field.directive.is_hidden:
            continue
        if skip_transient and dsl_field.directive.is_transient:
            continue
        if predicate(dsl_field):
            return True

        if (
            include_nested
            and isinstance(dsl_field.value, dsl.Base)
            and traverse_fields(dsl_field.value, predicate, include_nested, skip_relations, skip_hidden)
        ):
            return True

    return False


def is_relation(field: dsl.Field) -> bool:
    """Return whether the field declares composition or aggregation."""
    return field.directive.is_composition or field.directive.is_aggregation


def render_namespace(owner: dsl.Base | dsl.Enum | dsl.Object | dsl.Api) -> str | None:
    """Keep the historical namespace fallback for rendering an empty API annotation."""
    namespace = owner.directive.namespace
    if (
        isinstance(owner, dsl.Api)
        and isinstance(owner.parent, dsl.Object)
        and (namespace is None or not namespace.value)
    ):
        namespace = owner.parent.directive.namespace
    return namespace.value if namespace else None


def has_inline_request_body(operation: dsl.Operation) -> bool:
    """Whether a write operation needs an inline schema rather than a direct model reference."""
    body = operation.body_parameters
    method = operation.directive.method
    if not body or (method is not None and method.value in ("GET", "DELETE")):
        return False
    return not (len(body) == 1 and isinstance(body[0].value, dsl.Base | dsl.Object))


def operation_media_types(operation: dsl.Operation) -> tuple[str | None, str | None]:
    """Return the rendered request and response media types, respectively."""
    directive = operation.directive
    return (
        _render_media_type(directive.consumes, applicable=bool(operation.body_parameters)),
        _render_media_type(directive.produces, applicable=operation.value is not None),
    )


def _render_media_type(node: dsl.Directive[str] | None, *, applicable: bool) -> str | None:
    """Use JSON for an explicit empty media type where a body is present."""
    if node is None:
        return None
    return node.value or ("application/json" if applicable else None)
