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
    from qsdl.dsl.directives import OperationDirectiveView


@dataclass
class Operation(DirectiveOwnerModel):
    """textX Field class"""

    # required by textX
    parent: dsl.Api

    # defined in entity.tx
    # LHS
    name: str

    # defined in entity.tx (with defaults)
    description: list[str] = field(default_factory=list)
    arguments: list[dsl.Argument] = field(default_factory=list)
    # RHS
    is_array: bool = False
    value: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object | None = None
    is_required: bool = False
    # Source and synthetic directives, bound after parsing
    directives: Directives = None

    # addons
    is_generated: bool = False
    summary: str | None = None
    is_aggregated: bool = False
    path_parameters: list[dsl.Argument] = field(default_factory=list)
    query_parameters: list[dsl.Argument] = field(default_factory=list)
    header_parameters: list[dsl.Argument] = field(default_factory=list)
    body_parameters: list[dsl.Argument] = field(default_factory=list)

    domain_object: dsl.Object | None = None
    domain_parent: dsl.Object | None = None

    # required by textX
    _tx_fqn: str = "entity.Operation"

    @property
    def directive(self) -> OperationDirectiveView:
        """Return typed access to this owner's core directives."""
        from qsdl.dsl.directives import OperationDirectiveView

        return OperationDirectiveView(self.directives)
