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

"""Directive normalization, parsing, and structural validation."""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import overload

from textx import get_location
from textx.exceptions import TextXSemanticError

from qsdl import dsl

_HTTP_HEADER_NAME = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\Z")

DirectiveOwner = dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object | dsl.Field | dsl.Api | dsl.Operation


class _Presence(Enum):
    """How a grammar-native directive is represented on its owner."""

    TRUTHY = "truthy"
    NOT_NONE = "not_none"


@dataclass(frozen=True)
class _GrammarDirective:
    """Transitional definition for a directive parsed into a model attribute.

    Once every directive is captured by ``entity.directives`` in the grammar,
    this compatibility registry and its special-presence checks can be removed.
    """

    name: str
    attribute: str
    presence: _Presence = _Presence.TRUTHY

    def is_present(self, owner: DirectiveOwner) -> bool:
        value = getattr(owner, self.attribute)
        return value is not None if self.presence is _Presence.NOT_NONE else bool(value)


_GRAMMAR_DIRECTIVES: dict[type[object], tuple[_GrammarDirective, ...]] = {
    dsl.Enum: (_GrammarDirective("namespace", "namespace", _Presence.NOT_NONE),),
    dsl.Base: (_GrammarDirective("namespace", "namespace", _Presence.NOT_NONE),),
    dsl.Object: (_GrammarDirective("namespace", "namespace", _Presence.NOT_NONE),),
    dsl.Api: (
        _GrammarDirective("namespace", "namespace", _Presence.NOT_NONE),
        _GrammarDirective("generate", "generate"),
    ),
    dsl.Field: (
        _GrammarDirective("queryList", "is_query_list"),
        _GrammarDirective("query", "is_query"),
        _GrammarDirective("readOnly", "is_read_only"),
        _GrammarDirective("writeOnly", "is_write_only"),
        _GrammarDirective("composition", "is_composition"),
        _GrammarDirective("aggregation", "is_aggregation"),
        _GrammarDirective("opaque", "is_opaque"),
        _GrammarDirective("unique", "is_unique"),
        _GrammarDirective("hidden", "is_hidden"),
        _GrammarDirective("transient", "is_transient"),
        _GrammarDirective("ignore", "is_ignored"),
        _GrammarDirective("override", "is_override"),
        _GrammarDirective("minSize", "min_size", _Presence.NOT_NONE),
        _GrammarDirective("maxSize", "max_size", _Presence.NOT_NONE),
        _GrammarDirective("default", "default", _Presence.NOT_NONE),
    ),
    dsl.Operation: (
        _GrammarDirective("path", "path", _Presence.NOT_NONE),
        _GrammarDirective("method", "method", _Presence.NOT_NONE),
        _GrammarDirective("pagination", "is_pageable"),
        _GrammarDirective("consumes", "consumes", _Presence.NOT_NONE),
        _GrammarDirective("produces", "produces", _Presence.NOT_NONE),
    ),
}


def _split_directive_value(value: str) -> list[str]:
    """Split a directive payload on top-level commas."""
    values = []
    current = []
    quote = False
    escaped = False
    depth = 0

    for char in value:
        if quote:
            current.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = False
            continue

        if char == '"':
            quote = True
            current.append(char)
        elif char in "[{(":
            depth += 1
            current.append(char)
        elif char in "]})":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            values.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if quote or depth != 0:
        raise ValueError("unterminated quoted value or grouped directive value")

    values.append("".join(current).strip())
    return values


@overload
def normalize_directive_value(value: str) -> str: ...


@overload
def normalize_directive_value(value: None) -> None: ...


def normalize_directive_value(value: str | None) -> str | None:
    """Decode one quoted directive argument while preserving opaque values."""
    if value is None:
        return None

    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        try:
            decoded = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value
        if isinstance(decoded, str):
            return decoded
    return value


def _present_grammar_directive_names(owner: DirectiveOwner) -> set[str]:
    """Return directives currently represented by grammar-populated attributes."""
    return {definition.name for definition in _GRAMMAR_DIRECTIVES.get(type(owner), ()) if definition.is_present(owner)}


def _directive_owner_label(owner: DirectiveOwner) -> str:
    """Return a useful owner label for directive errors."""
    if isinstance(owner, dsl.Field):
        return f"Field {owner.name} of {owner.parent.name}"

    if isinstance(owner, dsl.Operation):
        return f"Operation {owner.name}"

    if isinstance(owner, dsl.Api):
        if isinstance(owner.parent, dsl.Object):
            return f"Api of Object {owner.parent.name}"
        return "Api"

    return f"{owner.__class__.__name__} {owner.name}"


def _directive_owners(schema: dsl.Schema) -> list[DirectiveOwner]:
    """Return every model element that can own directives."""
    # Import lazily to avoid the textx -> model_processor -> model_parser
    # -> directive_parser import cycle during module initialization.
    import qsdl.dsl.textx as xtx

    return [
        *xtx.get_children_of_scalar(schema),
        *xtx.get_children_of_enum(schema),
        *xtx.get_children_of_base(schema),
        *xtx.get_children_of_object(schema),
        *xtx.get_children_of_field(schema),
        *xtx.get_children_of_api(schema),
        *xtx.get_children_of_operation(schema),
    ]


def validate_directives(schema: dsl.Schema) -> None:
    """Reject repeated directive names on the same model element."""
    for owner in _directive_owners(schema):
        seen_names = _present_grammar_directive_names(owner)

        for directive in owner.directives:
            if directive.name in seen_names:
                msg = f"The {_directive_owner_label(owner)} specifies @{directive.name} more than once."
                raise TextXSemanticError(msg, **get_location(directive))
            seen_names.add(directive.name)


def _value_types(schema: dsl.Schema) -> dict[str, dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object]:
    """Return schema and built-in value types by name."""
    # Import lazily to avoid the textx -> model_processor -> model_parser
    # -> directive_parser import cycle during module initialization.
    import qsdl.dsl.textx as xtx

    types = {
        entity.name: entity
        for entity in [
            *xtx.get_children_of_scalar(schema),
            *xtx.get_children_of_enum(schema),
            *xtx.get_children_of_base(schema),
            *xtx.get_children_of_object(schema),
        ]
    }
    types.update({name: entity for name, entity in xtx.type_builtins.items() if name not in types})
    return types


def parse_response_headers(schema: dsl.Schema, operation: dsl.Operation) -> list[dsl.Argument]:
    """Parse the opaque ``@headers(...)`` directive for an operation.

    Header declarations remain raw directive text in the grammar. This
    function resolves them into the argument-shaped objects consumed by the
    generators.
    """
    directives = [directive for directive in operation.directives if directive.name == "headers"]
    if not directives:
        return []

    # Duplicate directive names are rejected centrally before operation parsing.
    directive = directives[0]
    if not directive.value:
        msg = f"The Operation {operation.name} must specify at least one response header in @headers(...)."
        raise TextXSemanticError(msg, **get_location(operation))

    try:
        declarations = _split_directive_value(directive.value)
    except ValueError as exc:
        msg = f"The response headers of Operation {operation.name} are malformed: {exc}."
        raise TextXSemanticError(msg, **get_location(operation)) from exc

    value_types = _value_types(schema)
    response_headers = []

    for declaration in declarations:
        if not declaration:
            msg = f"The response headers of Operation {operation.name} contain an empty declaration."
            raise TextXSemanticError(msg, **get_location(operation))

        declaration = normalize_directive_value(declaration)
        name, separator, value = declaration.partition(":")
        name = name.strip()
        value = value.strip()

        if not separator or not name or not value:
            msg = (
                f"The response header declaration {declaration!r} of Operation {operation.name} must use "
                "'name: Type' syntax."
            )
            raise TextXSemanticError(msg, **get_location(operation))

        if _HTTP_HEADER_NAME.fullmatch(name) is None:
            msg = f"The response header name {name!r} of Operation {operation.name} is invalid."
            raise TextXSemanticError(msg, **get_location(operation))

        is_array = value.startswith("[") or value.endswith("]")
        if is_array:
            if not (value.startswith("[") and value.endswith("]")):
                msg = f"The response header declaration {declaration!r} of Operation {operation.name} is malformed."
                raise TextXSemanticError(msg, **get_location(operation))
            value = value[1:-1].strip()

        value_type = value_types.get(value)
        if value_type is None:
            msg = f"The response header {name!r} of Operation {operation.name} references unknown type {value!r}."
            raise TextXSemanticError(msg, **get_location(operation))

        response_headers.append(dsl.Argument(operation, name, value_type, is_array=is_array))

    return response_headers
