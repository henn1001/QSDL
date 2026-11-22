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
from typing import ClassVar

from qsdl import dsl
from qsdl.generators.base_config import BaseConfig
from qsdl.generators.directive_payloads import decode_nonempty_string, decode_scalar_options, validate_nonempty_string


class Database(StrEnum):
    """Available Options for database"""

    HIBERNATE = "HIBERNATE"
    NO = "NO"


class IDTYPE(StrEnum):
    """Available Options for id_type"""

    LONG = "LONG"
    STRING = "STRING"


@dataclass(frozen=True, slots=True)
class SpringScalarMapping:
    """The mapped type and optional target-specific overrides."""

    type: str
    entity: str | None = None
    pattern: str | None = None


def _decode_mapping(raw: dsl.RawDirective) -> SpringScalarMapping:
    type_name, options = decode_scalar_options(raw, ("entity", "pattern"))
    return SpringScalarMapping(type_name, **options)


SPRING_SCALAR = dsl.DirectiveSpec("spring", (dsl.Scalar,), _decode_mapping)
SPRING_PACKAGE = dsl.DirectiveSpec(
    "spring-package", (dsl.Base, dsl.Object, dsl.Enum, dsl.Api), decode_nonempty_string, validate_nonempty_string
)
SPRING_CONTROLLER = dsl.DirectiveSpec("spring-controller", (dsl.Api,), decode_nonempty_string, validate_nonempty_string)


@dataclass
class SpringConfig(BaseConfig):
    """A configuration class that holds relevant data for the generator"""

    title: str = "SpringBootApp"
    group_id: str = "app"
    base_package: str = "app"
    artifact_id: str = "app"
    database: Database = Database.HIBERNATE
    use_auditing: bool = False
    table_prefix: str = "t_"

    # used to change the OpenAPI type for ID between "String" and "Long"
    id_type: IDTYPE = IDTYPE.LONG

    # used for changing the folder layout
    api_path: str = "api.{package}.web"
    controller_path: str = "api.{package}.web"
    config_path: str = "shared.config"
    domain_path: str = "api.{package}.contract"
    entity_path: str = "api.{package}.persistence"
    mapper_path: str = "api.{package}.mapping"
    enum_path: str = "shared.constants"
    exception_path: str = "shared.exception"
    model_path: str = "shared.model"
    repository_path: str = "api.{package}.persistence"
    service_path: str = "api.{package}"
    util_path: str = "shared.util"
    shared_controller_path: str = "shared.web"
    shared_repository_path: str = "shared.persistence"

    package_placeholder_fallback: str = "general"

    # used for dactite enum casting
    _dactive_casts: ClassVar[list[type[StrEnum]]] = [Database, IDTYPE]

    def __post_init__(self) -> None:
        # update all fields ending with _path
        for key, value in [x for x in vars(self).items() if x[0].endswith("_path")]:
            # prefix with base package if it was not provided
            if not str(value).startswith(self.base_package):
                self.__setattr__(key, self.base_package + "." + value)
