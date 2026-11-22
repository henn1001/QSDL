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


"""Shared payload handling for built-in generators."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, cast

from qsdl.dsl import Base, DirectiveSpec, Enum, Object, RawDirective, Scalar, Schema
from qsdl.dsl.directives import decode_string
from qsdl.dsl.processors.directive_parser import normalize_directive_value
from qsdl.dsl.textx import get_children_of_scalar

_EMBEDDED_MAPPINGS: ContextVar[tuple[DirectiveSpec[Any], dict[int, Any]] | None] = ContextVar(
    "embedded_scalar_mappings", default=None
)


def validate_nonempty_string(value: str) -> None:
    """Require a string with non-whitespace content."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("expected a non-empty string")


def decode_nonempty_string(raw: RawDirective) -> str:
    """Require a quoted string and retain legacy generator escape handling."""
    value = decode_string(raw)
    # Generator overrides previously consumed the normalized opaque payload.
    # Keep its double-quoted escape handling, including regex backslashes.
    quoted = raw.raw_value.strip()
    normalized = normalize_directive_value(quoted)
    if normalized != quoted:
        value = normalized
    validate_nonempty_string(value)
    return value


def decode_scalar_options(raw: RawDirective, allowed: tuple[str, ...]) -> tuple[str, dict[str, str]]:
    """Decode a scalar type followed by named options separated by comma-space."""
    first, *segments = decode_nonempty_string(raw).split(", ")
    type_name = first.strip()
    if not type_name or ":" in type_name:
        raise ValueError("expected a mapped type before any options")
    options = {}
    for segment in segments:
        key, separator, value = segment.strip().partition(":")
        value = value.strip()
        if not separator or not value:
            raise ValueError(f"expected a non-empty key: value option, got {segment!r}")
        if key not in allowed:
            raise ValueError(f"unknown scalar mapping option {key!r}")
        if key in options:
            raise ValueError(f"duplicate scalar mapping option {key!r}")
        options[key] = value
    return type_name, options


@contextmanager
def embedded_scalar_mappings[T](schema: Schema, spec: DirectiveSpec[T]) -> Iterator[None]:
    """Supply valid mappings to a bundled artifact without binding on the source schema."""
    mappings = {}
    for scalar in get_children_of_scalar(schema):
        node = scalar.directives.by_name(spec.name)
        if node is None or node.spec is not None or node._raw is None:
            continue
        try:
            value = spec.decode(node._raw)
            if spec.validate_value is not None:
                spec.validate_value(value)
        except ValueError:
            # An embedded target does not validate a name on behalf of Spring.
            continue
        mappings[id(scalar)] = value

    token = _EMBEDDED_MAPPINGS.set((spec, mappings))
    try:
        yield
    finally:
        _EMBEDDED_MAPPINGS.reset(token)


def scalar_mapping[T](entity: Scalar | Enum | Base | Object, spec: DirectiveSpec[T]) -> T | None:
    """Read a scalar's bound mapping, with an explicit embedded-render fallback."""
    if not isinstance(entity, Scalar):
        return None
    node = entity.directives.get(spec)
    if node is not None:
        return node.value
    embedded = _EMBEDDED_MAPPINGS.get()
    return cast("T | None", embedded[1].get(id(entity))) if embedded and embedded[0] is spec else None
