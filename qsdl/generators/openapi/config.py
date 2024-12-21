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

"""Generator specific parameters"""

from dataclasses import dataclass
from enum import Enum

from qsdl.generators.base_config import BaseConfig


class IDTYPE(str, Enum):
    """Available Options for id_type"""

    LONG = "LONG"
    STRING = "STRING"

class Directive(str, Enum):
    """Available directives"""

    TYPE = "openapi"

@dataclass
class Config(BaseConfig):
    """A configuration class that holds relevant data for the generator"""

    # used to change the OpenAPI type for ID between "string" and "integer"
    id_type: IDTYPE = IDTYPE.LONG

    # used for dactite enum casting
    _dactive_casts = [IDTYPE]
