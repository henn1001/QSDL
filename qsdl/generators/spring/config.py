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

"""Spring Generator Configuration"""

from dataclasses import dataclass
from enum import Enum

from qsdl.generators.base_config import BaseConfig


class Database(str, Enum):
    """Available Options for database"""

    HIBERNATE = "HIBERNATE"
    NO = "NO"


class IDTYPE(str, Enum):
    """Available Options for id_type"""

    LONG = "LONG"
    STRING = "STRING"


@dataclass
class Config(BaseConfig):
    """A configuration class that holds relevant data for the generator"""

    title: str = "SpringBootApp"
    group_id: str = "app"
    base_package: str = "app.server"
    artifact_id: str = "app"
    database: Database = Database.HIBERNATE
    encapsulation: bool = False

    # used to change the OpenAPI type for ID between "String" and "Long"
    id_type: IDTYPE = IDTYPE.LONG

    # used for changing the folder layout
    # include_namespace: bool = False

    api_path: str = f"{base_package}.api"
    config_path: str = f"{base_package}.config"
    controller_path: str = f"{base_package}.controller"
    domain_path: str = f"{base_package}.domain"
    enum_path: str = f"{base_package}.constant"
    exception_path: str = f"{base_package}.exception"
    model_path: str = f"{base_package}.model"
    repository_path: str = f"{base_package}.repository"
    service_path: str = f"{base_package}.service"
    util_path: str = f"{base_package}.util"

    # used for dactite enum casting
    _dactive_casts = [Database, IDTYPE]
