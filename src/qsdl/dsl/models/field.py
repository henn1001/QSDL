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

from qsdl import dsl


@dataclass
class Field:
    """textX Field class"""

    # required by textX
    parent: dsl.Base | dsl.Object

    # defined in entity.tx
    # LHS
    name: str
    # RHS
    value: dsl.Scalar | dsl.Object | dsl.Enum

    # defined in entity.tx (with defaults)
    description: list[str] = field(default_factory=list)
    is_array: bool = False
    is_required: bool = False
    # Special directives
    is_query: bool = False
    is_read_only: bool = False
    is_write_only: bool = False
    is_composition: bool = False
    is_aggregation: bool = False
    is_opaque: bool = False
    is_unique: bool = False
    is_hidden: bool = False
    is_transient: bool = False
    is_ignored: bool = False
    is_override: bool = False
    min_size: int | None = None
    max_size: int | None = None
    default: str | None = None
    # Custom directives
    directives: list[dsl.Directive] = field(default_factory=list)

    # addons
    is_relation: bool = False

    # required by textX
    _tx_fqn: str = "entity.Field"
