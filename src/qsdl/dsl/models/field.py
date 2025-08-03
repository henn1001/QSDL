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

"""Field class"""

from __future__ import annotations

from dataclasses import dataclass, field

import qsdl.dsl.models as dsl


@dataclass
class Field:
    """textX Field class"""

    # defined in entity.tx
    description: list[str] = field(default_factory=list)
    # LHS
    name: str = None
    # RHS
    is_array: bool = False
    value: dsl.Scalar | dsl.Object | dsl.Enum = None
    is_required: bool = False
    # Special directives
    is_query: bool = False
    is_read_only: bool = False
    is_write_only: bool = False
    is_composition: bool = False
    is_aggregation: bool = False
    is_unique: bool = False
    is_hidden: bool = False
    min_size: int = None
    max_size: int = None
    default: str = None
    # Custom directives
    directives: list[dsl.Directive] = field(default_factory=list)

    # required by textX
    parent: dsl.Base | dsl.Object = None
    _tx_fqn: str = "entity.Field"

    # addons
    is_relation: bool = False
