# Copyright 2025 henn1001
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

"""Scalar class"""

from __future__ import annotations

from dataclasses import dataclass, field

import qsdl.dsl.models as dsl


@dataclass
class Scalar:
    """textX Scalar class"""

    # defined in entity.tx
    name: str = None
    # Custom directives
    directives: list[dsl.Directive] = field(default_factory=list)

    # required by textX
    parent: dsl.Schema = None
    _tx_fqn: str = "entity.Scalar"
