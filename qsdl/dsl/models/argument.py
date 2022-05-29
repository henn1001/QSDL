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

"""Argument class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from qsdl.dsl.models import Base, Enum, Object, Operation, Scalar


@dataclass
class Argument:
    """textX Argument class"""

    # defined in entity.tx
    # LHS
    name: str = None
    # RHS
    is_array: bool = False
    value: Union[Scalar, Base, Object, Enum] = None
    is_required: bool = False

    # required by textX
    parent: Operation = None
    _tx_fqn: str = "entity.Argument"

    # addons
    is_path: bool = False
    is_query: bool = False
    is_body: bool = False
