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

"""Operation class"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Operation:
    """Our Operation class"""

    name: str = None
    ref: str = None
    order: int = None
    tag: str = None
    summary: str = None
    description: str = None
    path: str = None
    method: str = None
    parameters: List[dict] = field(default_factory=list)
    request: dict = None
    response: dict = None
    parent: object = None
    childs: List[dict] = field(default_factory=list)
    is_crud: bool = False
