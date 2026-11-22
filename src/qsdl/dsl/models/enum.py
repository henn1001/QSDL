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

"""Enum class"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from qsdl import dsl
from qsdl.dsl.models.directive import DirectiveOwnerModel, Directives

if TYPE_CHECKING:
    from qsdl.dsl.directives import EnumDirectiveView


@dataclass
class Enum(DirectiveOwnerModel):
    """textX Enum class"""

    # required by textX
    parent: dsl.Schema

    # defined in entity.tx
    name: str

    # defined in entity.tx (with defaults)
    description: list[str] = field(default_factory=list)
    # Source and synthetic directives, bound after parsing
    directives: Directives = None
    values: list[str] = field(default_factory=list)

    # required by textX
    _tx_fqn: str = "entity.Enum"

    @property
    def directive(self) -> EnumDirectiveView:
        """Return typed access to this owner's core directives."""
        from qsdl.dsl.directives import EnumDirectiveView

        return EnumDirectiveView(self.directives)
