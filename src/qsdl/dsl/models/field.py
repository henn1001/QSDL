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

"""Field class"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from qsdl import dsl
from qsdl.dsl.models.directive import DirectiveOwnerModel, Directives

if TYPE_CHECKING:
    from qsdl.dsl.directives import FieldDirectiveView


@dataclass
class Field(DirectiveOwnerModel):
    """textX Field class"""

    # required by textX
    parent: dsl.Base | dsl.Object

    # defined in entity.tx
    # LHS
    name: str
    # RHS
    value: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object

    # defined in entity.tx (with defaults)
    description: list[str] = field(default_factory=list)
    is_array: bool = False
    is_required: bool = False
    # Source and synthetic directives, bound after parsing
    directives: Directives = None

    # required by textX
    _tx_fqn: str = "entity.Field"

    @property
    def directive(self) -> FieldDirectiveView:
        """Return typed access to this owner's core directives."""
        from qsdl.dsl.directives import FieldDirectiveView

        return FieldDirectiveView(self.directives)
