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

"""Directive class"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from typing import Any, Literal, TypedDict, overload

from qsdl import dsl

type DirectiveOwner = dsl.Scalar | dsl.Base | dsl.Api | dsl.Object | dsl.Field | dsl.Operation | dsl.Enum


class SourceLocation(TypedDict):
    """Location fields accepted by textX diagnostics."""

    filename: str | None
    line: int
    col: int
    nchar: int


@dataclass(frozen=True, slots=True)
class RawDirective:
    """Captured directive payload before interpretation."""

    name: str
    has_parens: bool
    raw_value: str | None
    location: SourceLocation


@dataclass(frozen=True, slots=True)
class DirectiveSpec[T, SourceT = T]:
    """Definition of a directive payload and its supported owners."""

    name: str
    owners: tuple[type[DirectiveOwner], ...]
    decode: Callable[[RawDirective], SourceT]
    validate_value: Callable[[T], None] | None = None


@dataclass(frozen=True)
class Directive[T = str | None]:
    """Directive attached to its declaring model element."""

    parent: DirectiveOwner
    name: str
    value: T = None
    spec: DirectiveSpec[T, Any] | None = None
    origin: Literal["source", "synthetic"] = "source"
    location: SourceLocation | None = None

    # Opaque source captures can be inspected by bundled artifact renderers.
    _raw: RawDirective | None = field(default=None, repr=False, compare=False, kw_only=True)
    _tx_position: int = field(default=0, repr=False, compare=False, kw_only=True)
    _tx_position_end: int = field(default=0, repr=False, compare=False, kw_only=True)


class Directives(Sequence[Directive[Any]]):
    """Ordered attachment collection; all lookups return the stored nodes."""

    def __init__(
        self, owner: DirectiveOwner, nodes: Sequence[Directive[Any]] = (), *, invalid: frozenset[str] = frozenset()
    ) -> None:
        self._owner = owner
        self._nodes = [node for node in nodes if node.name not in invalid]
        self._invalid = set(invalid)

    def is_invalid(self, *specs: DirectiveSpec[Any]) -> bool:
        """Whether any requested directive was rejected, or any directive if none are given."""
        return any(spec.name in self._invalid for spec in specs) if specs else bool(self._invalid)

    def _invalidate(self, spec: DirectiveSpec[Any]) -> None:
        """Mark a directive whose value failed validation after binding."""
        self._invalid.add(spec.name)
        self._nodes = [node for node in self._nodes if node.name != spec.name]

    def __len__(self) -> int:
        return len(self._nodes)

    @overload
    def __getitem__(self, index: int) -> Directive[Any]: ...

    @overload
    def __getitem__(self, index: slice) -> list[Directive[Any]]: ...

    def __getitem__(self, index: int | slice) -> Directive[Any] | list[Directive[Any]]:
        return self._nodes[index]

    def by_name(self, name: str) -> Directive[Any] | None:
        return next((node for node in self._nodes if node.name == name), None)

    def get[T](self, spec: DirectiveSpec[T, Any]) -> Directive[T] | None:
        node = self.by_name(spec.name)
        return node if node is not None and node.spec is spec else None

    def _complete_source[T](self, spec: DirectiveSpec[T, Any], value: T) -> None:
        """Replace a provisional source node in place before publishing the schema."""
        for index, node in enumerate(self._nodes):
            if node.spec is spec and node.origin == "source":
                self._nodes[index] = replace(node, value=value)
                return
        raise ValueError(f"No source @{spec.name} to complete.")

    def attach_synthetic[T](self, spec: DirectiveSpec[T, Any], value: T) -> Directive[T]:
        """Validate and append a new node owned by this collection's recipient."""
        if not isinstance(self._owner, spec.owners):
            raise TypeError(f"@{spec.name} is not supported on {type(self._owner).__name__}.")
        if self.by_name(spec.name) is not None:
            raise ValueError(f"@{spec.name} is already attached.")
        if spec.validate_value is not None:
            spec.validate_value(value)
        node = Directive(self._owner, spec.name, value, spec, origin="synthetic")
        self._nodes.append(node)
        return node


class DirectiveOwnerModel:
    """Initialize the collection for programmatic owners; textX passes raw captures."""

    def __post_init__(self) -> None:
        if self.directives is None:
            self.directives = Directives(self)
