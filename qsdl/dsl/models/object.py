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

"""Object class"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from . import Base, Directive, Field, Operation, Schema


@dataclass
class Object:
    """Our Object class"""

    # defined in entity.tx
    description: str = None
    name: str = None
    supertype: Base = None
    # Special directives
    deprecated: bool = False
    namespace: str = None
    # Custom directives
    directives: List[Directive] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)
    operation: Operation = None

    # required by textX
    parent: Schema = None

    # addons
    is_crud: bool = False
