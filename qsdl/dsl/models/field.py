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

from dataclasses import dataclass


@dataclass
class Field:
    """Our Field class"""

    # required by textX
    parent: object

    # defined in entity.tx
    description: str
    # LHS
    name: str
    function: bool
    arguments: list
    # RHS
    array: bool
    value: object
    non_nullable_array: bool
    non_nullable: bool
    # Special directives
    query: bool
    nested: bool
    readonly: bool
    writeonly: bool
    composition: bool
    aggregation: bool
    path: str
    method: str
    # Custom directives
    directives: list
