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

"""QSDL post-processing"""

from enum import Enum


class CrudGeneratorEnum(str, Enum):
    GET_ALL = "GET_ALL"
    CREATE = "CREATE"
    GET = "GET"
    REPLACE = "REPLACE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ADD = "ADD"
    REMOVE = "REMOVE"

    @classmethod
    def has_member_key(cls, key):
        return key in cls.__members__
