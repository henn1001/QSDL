# Copyright (C) 2022 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Field class"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from qsdl.dsl.models import Scalar, Base, Directive, Object, Api, Enum


@dataclass
class Field:
    """textX Field class"""

    # defined in entity.tx
    description: str = None
    # LHS
    name: str = None
    # RHS
    is_array: bool = False
    value: Union[Scalar, Base, Object, Enum] = None
    is_required: bool = False
    # Special directives
    is_query: bool = False
    is_read_only: bool = False
    is_write_only: bool = False
    is_composition: bool = False
    is_aggregation: bool = False
    min_size: int = None
    max_size: int = None
    # Custom directives
    directives: List[Directive] = field(default_factory=list)

    # required by textX
    parent: Union[Base, Object] = None

    # addons
    is_relation: bool = False
