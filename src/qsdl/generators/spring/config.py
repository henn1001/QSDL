# Copyright 2026 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generator Configuration"""

from dataclasses import dataclass
from enum import StrEnum

from qsdl.generators.base_config import BaseConfig


class Database(StrEnum):
    """Available Options for database"""

    HIBERNATE = "HIBERNATE"
    NO = "NO"


class IDTYPE(StrEnum):
    """Available Options for id_type"""

    LONG = "LONG"
    STRING = "STRING"


class Directive(StrEnum):
    """Available directives"""

    TYPE = "spring"
    PACKAGE = "spring-package"
    CONTROLLER = "spring-controller"
    VOID_INPUT = "spring-void-input"


@dataclass
class Config(BaseConfig):
    """A configuration class that holds relevant data for the generator"""

    title: str = "SpringBootApp"
    group_id: str = "app"
    base_package: str = "app.server"
    artifact_id: str = "app"
    database: Database = Database.HIBERNATE
    use_auditing: bool = False
    table_prefix: str = "t_"

    # used to change the OpenAPI type for ID between "String" and "Long"
    id_type: IDTYPE = IDTYPE.LONG

    # used for changing the folder layout
    api_path: str = "%placeholder%.api"
    controller_path: str = "%placeholder%.api"
    config_path: str = "%placeholder%.config"
    domain_path: str = "%placeholder%.domain"
    entity_path: str = "%placeholder%.domain.entity"
    mapper_path: str = "%placeholder%.domain.mapper"
    enum_path: str = "%placeholder%.constant"
    exception_path: str = "%placeholder%.exception"
    model_path: str = "%placeholder%.model"
    repository_path: str = "%placeholder%.repository"
    service_path: str = "%placeholder%.service"
    util_path: str = "%placeholder%.util"

    package_placeholder_fallback: str = "global"

    # used for dactite enum casting
    _dactive_casts = [Database, IDTYPE]

    def __post_init__(self) -> None:
        # update all fields ending with _path
        for key, value in [x for x in vars(self).items() if x[0].endswith("_path")]:
            # value was probably not provided by the user - replace with placeholder
            if "%placeholder%" in value:
                self.__setattr__(key, value.replace("%placeholder%", self.base_package))

            # prefix with base package if it was not provided
            elif not str(value).startswith(self.base_package):
                self.__setattr__(key, self.base_package + "." + value)
