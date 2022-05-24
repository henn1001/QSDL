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

"""Spring Generator Api class"""

from __future__ import annotations

from ast import Str
from dataclasses import dataclass

from .. import Config


@dataclass
class Package:
    """Parsed spring package paths"""

    _config: Config

    namespace: str = None
    slashed: bool = False

    def __prepare(self, string: Str) -> str:
        ret = self.base
        ret += "."
        # ret += self.__namespace()
        ret += string

        # format
        ret = ret.replace(".", "/") if self.slashed else ret.replace("/", ".")

        return ret

    # def __namespace(self) -> str:
    #     ret = ""

    #     if self._config.include_namespace and self.namespace:
    #         ret = self.namespace.lower() + "."

    #     elif self._config.include_namespace and not self.namespace:
    #         ret = "shared."

    #     return ret

    @property
    def base(self) -> str:
        """property helper method"""
        ret = self._config.group_id
        return ret.replace(".", "/") if self.slashed else ret.replace("/", ".")

    @property
    def api(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.api_path)

    @property
    def controller(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.controller_path)

    @property
    def domain(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.domain_path)

    @property
    def enum(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.enum_path)

    @property
    def repository(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.repository_path)

    @property
    def service(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.service_path)

    @property
    def model(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.model_path)

    @property
    def config(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.config_path)

    @property
    def exception(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.exception_path)

    @property
    def util(self) -> str:
        """property helper method"""
        return self.__prepare(self._config.util_path)
