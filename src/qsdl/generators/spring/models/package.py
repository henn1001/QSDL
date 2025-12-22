# Copyright 2025 henn1001
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

"""Spring Generator Package class"""

from __future__ import annotations

from dataclasses import dataclass

from .. import Config


@dataclass
class Package:
    """Parsed spring package paths"""

    _config: Config

    _namespace: str = ""
    slashed: bool = False

    def __post_init__(self) -> None:
        self._namespace = self._config.package_placeholder_fallback

    def __prepare(self, string: str) -> str:
        ret = string

        # format
        ret = ret.replace("{package}", self._namespace)
        ret = ret.replace(".", "/") if self.slashed else ret.replace("/", ".")

        return ret

    def set_namespace(self, namespace: str) -> None:
        """Sets the namespace for this package"""
        self._namespace = namespace if namespace else self._namespace

    @property
    def base(self) -> str:
        """Property helper method"""
        ret = self._config.base_package
        return ret.replace(".", "/") if self.slashed else ret.replace("/", ".")

    @property
    def api(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.api_path)

    @property
    def controller(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.controller_path)

    @property
    def domain(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.domain_path)

    @property
    def entity(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.entity_path)

    @property
    def mapper(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.mapper_path)

    @property
    def enum(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.enum_path)

    @property
    def repository(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.repository_path)

    @property
    def service(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.service_path)

    @property
    def model(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.model_path)

    @property
    def config(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.config_path)

    @property
    def exception(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.exception_path)

    @property
    def util(self) -> str:
        """Property helper method"""
        return self.__prepare(self._config.util_path)
