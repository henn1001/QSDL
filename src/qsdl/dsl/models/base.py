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

"""Base class"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from qsdl import dsl
from qsdl.dsl.models.directive import DirectiveOwnerModel, Directives

if TYPE_CHECKING:
    from qsdl.dsl.directives import BaseDirectiveView


@dataclass
class Base(DirectiveOwnerModel):
    """textX Base class"""

    # required by textX
    parent: dsl.Schema

    # defined in entity.tx
    name: str

    # defined in entity.tx (with defaults)
    description: list[str] = field(default_factory=list)
    supertypes: list[dsl.Base] = field(default_factory=list)
    # Source and synthetic directives, bound after parsing
    directives: Directives = None
    fields: list[dsl.Field] = field(default_factory=list)

    # addons
    _resolved_fields: tuple[dsl.Field, ...] | None = field(default=None, init=False, repr=False, compare=False)

    # required by textX
    _tx_fqn: str = "entity.Base"

    @property
    def effective_fields(self) -> tuple[dsl.Field, ...]:
        """Return ordered inherited and local fields, including any generated ID."""
        return tuple(self.fields) if self._resolved_fields is None else self._resolved_fields

    @property
    def generation_fields(self) -> tuple[dsl.Field, ...]:
        """Return effective fields that are not marked @ignore."""
        return tuple(member for member in self.effective_fields if not member.directive.is_ignored)

    @property
    def directive(self) -> BaseDirectiveView:
        """Return typed access to this owner's core directives."""
        from qsdl.dsl.directives import BaseDirectiveView

        return BaseDirectiveView(self.directives)
