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

"""Bind captured directives and resolve response header types."""

import ast
from collections.abc import Sequence
from typing import Any, cast, get_args, overload

from textx import get_location, get_model
from textx.exceptions import TextXSemanticError

from qsdl import dsl
from qsdl.dsl.directives import CORE_SPECS, DIRECTIVE_NAME, HEADERS, ResponseHeader, _HeaderDeclaration
from qsdl.dsl.models.directive import DirectiveOwner, DirectiveSpec, RawDirective


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


def validate_directive_specs(specs: Sequence[DirectiveSpec[Any]]) -> dict[str, DirectiveSpec[Any]]:
    """Validate external definitions and index them by exact name."""
    if not isinstance(specs, Sequence):
        raise TypeError("directive_specs must be a sequence of DirectiveSpec instances")
    supported_owners = get_args(DirectiveOwner.__value__)
    by_name = {}
    for spec in specs:
        if not isinstance(spec, DirectiveSpec):
            raise TypeError("directive_specs must contain only DirectiveSpec instances")
        if not isinstance(spec.name, str) or DIRECTIVE_NAME.fullmatch(spec.name) is None:
            raise TypeError(f"invalid directive name: {spec.name!r}")
        if spec.name in CORE_SPECS:
            raise TypeError(f"directive @{spec.name} conflicts with a core directive")
        if spec.name in by_name:
            raise TypeError(f"duplicate directive spec @{spec.name}")
        if (
            not isinstance(spec.owners, tuple)
            or not spec.owners
            or any(owner not in supported_owners for owner in spec.owners)
        ):
            raise TypeError(f"directive @{spec.name} must declare supported QSDL owner classes")
        if not callable(spec.decode) or (spec.validate_value is not None and not callable(spec.validate_value)):
            raise TypeError(f"directive @{spec.name} must declare callable decoders and validators")
        by_name[spec.name] = spec
    return by_name


def bind_directives(owner: DirectiveOwner) -> None:
    """Decode and attach the complete directive list of a textX owner."""
    active_specs = get_model(owner)._tx_model_params.get("directive_specs", {})
    nodes = []
    seen = set()
    for capture in owner.directives:
        location = get_location(capture)
        name = capture.name
        if name in seen:
            msg = f"The {_directive_owner_label(owner)} specifies @{name} more than once."
            raise TextXSemanticError(msg, **location)
        seen.add(name)
        if DIRECTIVE_NAME.fullmatch(name) is None:
            msg = f"Directive name {name!r} must use camelCase, snake_case, or kebab-case."
            raise TextXSemanticError(msg, **location)

        raw = RawDirective(name, capture.has_parens, (capture.value or "") if capture.has_parens else None, location)
        spec = CORE_SPECS.get(name)
        if spec is not None and not isinstance(owner, spec.owners):
            spec = None
        if spec is None and name in active_specs:
            spec = active_specs[name]
            if not isinstance(owner, spec.owners):
                msg = f"@{name} is not supported on {_directive_owner_label(owner)}."
                raise TextXSemanticError(msg, **location)

        if spec is None:
            value = normalize_directive_value(raw.raw_value)
        else:
            try:
                value = spec.decode(raw)
                if spec is not HEADERS and spec.validate_value is not None:
                    spec.validate_value(value)
            except ValueError as exc:
                msg = f"Invalid @{name} on {_directive_owner_label(owner)}: {exc}."
                raise TextXSemanticError(msg, **location) from exc

        nodes.append(
            dsl.Directive(
                owner,
                name,
                value,
                spec,
                location=location,
                _raw=raw if spec is None else None,
                _tx_position=capture._tx_position,
                _tx_position_end=capture._tx_position_end,
            )
        )

    owner.directives = dsl.Directives(owner, nodes)


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


def complete_response_headers(schema: dsl.Schema, operation: dsl.Operation) -> None:
    """Resolve typed declarations after imported types have been merged."""
    directive = operation.directives.get(HEADERS)
    if directive is None:
        return

    value_types = _value_types(schema)
    response_headers = []
    for declaration in cast(tuple[_HeaderDeclaration, ...], directive.value):
        value_type = value_types.get(declaration.type_name)
        if value_type is None:
            msg = (
                f"The response header {declaration.name!r} of Operation {operation.name} "
                f"references unknown type {declaration.type_name!r}."
            )
            raise TextXSemanticError(msg, **directive.location)
        response_headers.append(ResponseHeader(declaration.name, value_type, declaration.is_array))
    operation.directives._complete_source(HEADERS, tuple(response_headers))
