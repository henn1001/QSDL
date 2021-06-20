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

"""Spring Generator Configuration"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """A configuration class that holds relevant data for the generator"""

    title: str = "SpringBootApp"
    group_id: str = "com.test"
    artifact_id: str = "app"
    interface_pattern: bool = False
    database: List[str] = field(default_factory=lambda: ["no", "hibernate"])

    # used to change the OpenAPI type for ID between "String" and "Long"
    id_type: str = "Long"
