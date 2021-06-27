# Copyright (C) 2020 henn1001

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
    from qsdl.dsl.models import Argument, Base, Directive, Object, Api


@dataclass
class Operation:
    """textX Field class"""

    # defined in entity.tx
    description: str = None
    # LHS
    name: str = None
    arguments: List[Argument] = field(default_factory=list)
    # RHS
    is_array: bool = False
    value: object = None
    is_required: bool = False
    # Special directives
    path: str = None
    method: str = None
    # Custom directives
    directives: List[Directive] = field(default_factory=list)

    # custom
    summary: str = None
    is_pageable: bool = False
    path_parameters: List[Argument] = field(default_factory=list)
    query_parameters: List[Argument] = field(default_factory=list)
    body_parameters: List[Argument] = field(default_factory=list)

    domain_object: Object = None
    domain_parent: Object = None

    # required by textX
    parent: Union[Base, Object, Api] = None
