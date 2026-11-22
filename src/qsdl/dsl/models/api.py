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

"""Api class"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from qsdl import dsl
from qsdl.dsl.models.directive import DirectiveOwnerModel, Directives

if TYPE_CHECKING:
    from qsdl.dsl.directives import ApiDirectiveView


@dataclass
class Api(DirectiveOwnerModel):
    """textX Api class"""

    # required by textX
    parent: dsl.Schema | dsl.Object

    # defined in entity.tx
    description: list[str] = field(default_factory=list)
    directives: Directives = None
    operations: list[dsl.Operation] = field(default_factory=list)

    # addons
    has_generated: bool = False

    # required by textX
    _tx_fqn: str = "entity.Api"

    @property
    def directive(self) -> ApiDirectiveView:
        """Return typed access to this owner's core directives."""
        from qsdl.dsl.directives import ApiDirectiveView

        return ApiDirectiveView(self.directives)
