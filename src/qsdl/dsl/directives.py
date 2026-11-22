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


"""Core directive definitions and typed owner views."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, overload

from qsdl import dsl
from qsdl.dsl.models.directive import Directive, DirectiveOwner, Directives, DirectiveSpec, RawDirective
from qsdl.dsl.processors import CrudGeneratorEnum

DIRECTIVE_NAME = re.compile(r"(?:[a-z][a-z0-9]*(?:_[a-z0-9]+)+|[a-z][a-z0-9]*(?:-[a-z0-9]+)+|[a-z][A-Za-z0-9]*)")
_QUOTED_STRING = re.compile(r""""(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' """, re.VERBOSE | re.DOTALL)
_INTEGER = re.compile(r"[-+]?[0-9]+")
_HTTP_HEADER_NAME = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
_TYPE_NAME = re.compile(r"[^\d\W][\w-]*")
_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")


def _payload(raw: RawDirective) -> str:
    if not raw.has_parens:
        raise ValueError("expected a parenthesized payload")
    return (raw.raw_value or "").strip()


def _unquote(quoted: str) -> str:
    # Match textX's STRING conversion, not Python string-literal semantics.
    return quoted[1:-1].replace(r"\"", '"').replace(r"\'", "'")


def decode_string(raw: RawDirective) -> str:
    """Decode a single quoted string using textX STRING semantics."""
    value = _payload(raw)
    if _QUOTED_STRING.fullmatch(value) is None:
        raise ValueError("expected a single quoted string")
    return _unquote(value)


def _validate_string(value: str) -> None:
    if not isinstance(value, str):
        raise TypeError("expected a string value")


def _validate_int(value: int) -> None:
    if type(value) is not int:
        raise ValueError("expected an integer value")


def _decode_int(raw: RawDirective) -> int:
    value = _payload(raw)
    if _INTEGER.fullmatch(value) is None:
        raise ValueError("expected a signed or unsigned integer")
    return int(value)


def _validate_flag(value: bool) -> None:
    if value is not True:
        raise ValueError("expected True for a present flag")


def _decode_flag(raw: RawDirective) -> bool:
    if raw.has_parens:
        raise ValueError("expected a bare flag without parentheses")
    return True


def _flag(name: str, owner: type[DirectiveOwner]) -> DirectiveSpec[bool]:
    return DirectiveSpec(name, (owner,), _decode_flag, _validate_flag)


def _presence_flag(raw: RawDirective) -> bool:
    # Historically @force-generate was interpreted by presence only.
    return True


def _validate_method(value: str) -> None:
    if value not in _METHODS:
        raise ValueError(f"expected one of {', '.join(_METHODS)} (unquoted)")


def _decode_method(raw: RawDirective) -> str:
    return _payload(raw)


def _validate_generate(value: tuple[str, ...]) -> None:
    if not isinstance(value, tuple) or any(not CrudGeneratorEnum.has_member_key(token) for token in value):
        raise ValueError(f"invalid value; expected zero or more of {[member.value for member in CrudGeneratorEnum]}")


def _decode_generate(raw: RawDirective) -> tuple[str, ...]:
    value = _payload(raw)
    items = []
    while value:
        match = _QUOTED_STRING.match(value)
        if match is None:
            raise ValueError("expected a comma-separated list of quoted CRUD tokens")
        items.append(_unquote(match[0]))
        value = value[match.end() :].lstrip()
        if not value:
            break
        if not value.startswith(",") or not (value := value[1:].lstrip()):
            raise ValueError("expected another quoted CRUD token after a comma")
    return tuple(items)


@dataclass(frozen=True, slots=True)
class _HeaderDeclaration:
    """An unresolved response header declared by @headers."""

    name: str
    type_name: str
    is_array: bool


def _validate_headers(value: tuple[_HeaderDeclaration, ...]) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("expected at least one response header")
    for header in value:
        if not isinstance(header, _HeaderDeclaration) or type(header.is_array) is not bool:
            raise ValueError("expected a header declaration")
        if not _HTTP_HEADER_NAME.fullmatch(header.name):
            raise ValueError(f"response header name {header.name!r} is invalid")
        if not _TYPE_NAME.fullmatch(header.type_name):
            raise ValueError(f"invalid type name {header.type_name!r} for response header {header.name!r}")


def _decode_headers(raw: RawDirective) -> tuple[_HeaderDeclaration, ...]:
    value = _payload(raw)
    if _QUOTED_STRING.fullmatch(value):
        value = _unquote(value)
    if not value:
        raise ValueError("expected at least one response header")
    items = []
    for declaration in value.split(","):
        declaration = declaration.strip()
        if _QUOTED_STRING.fullmatch(declaration):
            declaration = _unquote(declaration)
        name, separator, type_name = declaration.partition(":")
        if not separator:
            raise ValueError(f"response header declaration {declaration!r} must use 'name: Type' syntax")
        type_name = type_name.strip()
        is_array = type_name.startswith("[") and type_name.endswith("]")
        if is_array:
            type_name = type_name[1:-1].strip()
        items.append(_HeaderDeclaration(name.strip(), type_name, is_array))
    declarations = tuple(items)
    _validate_headers(declarations)
    return declarations


NAMESPACE = DirectiveSpec("namespace", (dsl.Enum, dsl.Base, dsl.Object, dsl.Api), decode_string, _validate_string)
FORCE_GENERATE = DirectiveSpec("force-generate", (dsl.Base, dsl.Enum), _presence_flag, _validate_flag)
GENERATE = DirectiveSpec("generate", (dsl.Api,), _decode_generate, _validate_generate)
QUERY_LIST = _flag("queryList", dsl.Field)
QUERY = _flag("query", dsl.Field)
READ_ONLY = _flag("readOnly", dsl.Field)
WRITE_ONLY = _flag("writeOnly", dsl.Field)
COMPOSITION = _flag("composition", dsl.Field)
AGGREGATION = _flag("aggregation", dsl.Field)
OPAQUE = _flag("opaque", dsl.Field)
UNIQUE = _flag("unique", dsl.Field)
HIDDEN = _flag("hidden", dsl.Field)
TRANSIENT = _flag("transient", dsl.Field)
IGNORE = _flag("ignore", dsl.Field)
OVERRIDE = _flag("override", dsl.Field)
MIN_SIZE = DirectiveSpec("minSize", (dsl.Field,), _decode_int, _validate_int)
MAX_SIZE = DirectiveSpec("maxSize", (dsl.Field,), _decode_int, _validate_int)
DEFAULT = DirectiveSpec("default", (dsl.Field,), decode_string, _validate_string)
PATH = DirectiveSpec("path", (dsl.Operation,), decode_string, _validate_string)
METHOD = DirectiveSpec("method", (dsl.Operation,), _decode_method, _validate_method)
PAGINATION = _flag("pagination", dsl.Operation)
CONSUMES = DirectiveSpec("consumes", (dsl.Operation,), decode_string, _validate_string)
PRODUCES = DirectiveSpec("produces", (dsl.Operation,), decode_string, _validate_string)


@dataclass(frozen=True, slots=True)
class ResponseHeader:
    """A response header with a resolved schema type."""

    name: str
    value: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object
    is_array: bool


def _validate_resolved_headers(value: tuple[ResponseHeader, ...]) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("expected at least one resolved response header")
    for header in value:
        if (
            not isinstance(header, ResponseHeader)
            or not isinstance(header.value, dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object)
            or type(header.is_array) is not bool
            or not _HTTP_HEADER_NAME.fullmatch(header.name)
        ):
            raise ValueError("expected a resolved response header")


# Only the core binder sees the provisional declarations. The public spec and
# its synthetic value validator describe the completed tuple.
HEADERS = DirectiveSpec[tuple[ResponseHeader, ...], tuple[_HeaderDeclaration, ...]](
    "headers",
    (dsl.Operation,),
    _decode_headers,
    _validate_resolved_headers,
)

CORE_SPECS: dict[str, DirectiveSpec[Any]] = {
    spec.name: spec
    for spec in (
        NAMESPACE,
        FORCE_GENERATE,
        GENERATE,
        QUERY_LIST,
        QUERY,
        READ_ONLY,
        WRITE_ONLY,
        COMPOSITION,
        AGGREGATION,
        OPAQUE,
        UNIQUE,
        HIDDEN,
        TRANSIENT,
        IGNORE,
        OVERRIDE,
        MIN_SIZE,
        MAX_SIZE,
        DEFAULT,
        PATH,
        METHOD,
        PAGINATION,
        CONSUMES,
        PRODUCES,
        HEADERS,
    )
}


class _DirectiveAccessor[T]:
    def __init__(self, spec: DirectiveSpec[T, Any]) -> None:
        self._spec = spec

    @overload
    def __get__(self, instance: None, owner: type) -> _DirectiveAccessor[T]: ...

    @overload
    def __get__(self, instance: _DirectiveView, owner: type) -> Directive[T] | None: ...

    def __get__(self, instance: _DirectiveView | None, owner: type) -> _DirectiveAccessor[T] | Directive[T] | None:
        return self if instance is None else instance._directives.get(self._spec)


class _FlagAccessor:
    """Read a flag directive as a bool: present is True, absent is False."""

    def __init__(self, spec: DirectiveSpec[bool]) -> None:
        self._spec = spec

    @overload
    def __get__(self, instance: None, owner: type) -> _FlagAccessor: ...

    @overload
    def __get__(self, instance: _DirectiveView, owner: type) -> bool: ...

    def __get__(self, instance: _DirectiveView | None, owner: type) -> _FlagAccessor | bool:
        return self if instance is None else instance._directives.get(self._spec) is not None


class _DirectiveView:
    def __init__(self, directives: Directives) -> None:
        self._directives = directives


class ScalarDirectiveView(_DirectiveView):
    """Scalars have no built-in directive accessors."""


class _NamespaceView(_DirectiveView):
    namespace = _DirectiveAccessor(NAMESPACE)


class EnumDirectiveView(_NamespaceView):
    """Typed access to enum directives."""

    is_force_generate = _FlagAccessor(FORCE_GENERATE)


class BaseDirectiveView(_NamespaceView):
    """Typed access to base directives."""

    is_force_generate = _FlagAccessor(FORCE_GENERATE)


class ObjectDirectiveView(_NamespaceView):
    """Typed access to object directives."""


class ApiDirectiveView(_NamespaceView):
    """Typed access to API directives."""

    generate = _DirectiveAccessor(GENERATE)


class FieldDirectiveView(_DirectiveView):
    """Typed access to field directives."""

    is_query_list = _FlagAccessor(QUERY_LIST)
    is_query = _FlagAccessor(QUERY)
    is_read_only = _FlagAccessor(READ_ONLY)
    is_write_only = _FlagAccessor(WRITE_ONLY)
    is_composition = _FlagAccessor(COMPOSITION)
    is_aggregation = _FlagAccessor(AGGREGATION)
    is_opaque = _FlagAccessor(OPAQUE)
    is_unique = _FlagAccessor(UNIQUE)
    is_hidden = _FlagAccessor(HIDDEN)
    is_transient = _FlagAccessor(TRANSIENT)
    is_ignored = _FlagAccessor(IGNORE)
    is_override = _FlagAccessor(OVERRIDE)
    min_size = _DirectiveAccessor(MIN_SIZE)
    max_size = _DirectiveAccessor(MAX_SIZE)
    default = _DirectiveAccessor(DEFAULT)


class OperationDirectiveView(_DirectiveView):
    """Typed access to operation directives."""

    path = _DirectiveAccessor(PATH)
    method = _DirectiveAccessor(METHOD)
    is_pageable = _FlagAccessor(PAGINATION)
    consumes = _DirectiveAccessor(CONSUMES)
    produces = _DirectiveAccessor(PRODUCES)
    headers = _DirectiveAccessor(HEADERS)
