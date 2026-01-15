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

"""Generator class"""

from __future__ import annotations

from typing import Self

from qsdl import dsl

from .. import models as spring
from .. import util


class EnumClass:
    """The Java Model for the Domain Class Object"""

    def __init__(self) -> None:
        self._ref: dsl.Enum

        self.name: str
        self.constants: list[str] = []

        self.package: spring.Package = spring.Package(util.Store.config)

    @staticmethod
    def from_ref(_ref: dsl.Enum) -> Self:
        """Rebuilds the enum class from a new reference"""
        enum = EnumClass()
        enum._ref = _ref
        enum.name = _ref.name
        enum.constants.extend(_ref.values)

        return enum
