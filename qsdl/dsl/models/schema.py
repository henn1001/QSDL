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

"""Schema class"""

from dataclasses import dataclass, field
from typing import List, Union

from .base import Base
from .enum import Enum
from .object import Object
from .operation import Operation
from .scalar import Scalar


@dataclass
class Schema:
    """Our Schema class"""

    # defined in entity.tx
    title: str = None
    version: str = None
    description: str = None
    servers: List[str] = field(default_factory=list)
    types: List[Union[Scalar, Enum, Base, Operation, Object]] = field(default_factory=list)
