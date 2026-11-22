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

"""PostgreSQL column models."""

from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import ClassVar

import qsdl.casing as qfilter
from qsdl import dsl

from .. import util


@dataclass
class Column:
    """A SQL column backed by a DSL field."""

    source: dsl.Field
    prefix: InitVar[str] = ""
    name: str = field(init=False)
    type: str = field(init=False)

    def __post_init__(self, prefix: str) -> None:
        value = self.source.value
        self.name = prefix + qfilter.snakecase(self.source.name).lower()
        if isinstance(value, dsl.Object):
            self.name += f"_{value.name.lower()}_id"
            self.type = "BIGINT"
        elif isinstance(value, dsl.Enum):
            self.type = "TEXT"
        elif isinstance(value, dsl.Base):
            self.type = "JSONB"
        else:
            self.type = util.custom_type(value)

    @property
    def is_id(self) -> bool:
        value = self.source.value
        return not isinstance(value, dsl.Base) and value.name == "ID"

    @property
    def is_array(self) -> bool:
        # JSONB stores arrays natively.
        return (
            self.source.is_array and not isinstance(self.source.value, dsl.Base) and self.source.value.name != "Object"
        )

    @property
    def is_required(self) -> bool:
        return self.source.is_required

    @property
    def is_unique(self) -> bool:
        return self.source.directive.is_unique

    @property
    def enum(self) -> str:
        value = self.source.value
        if not isinstance(value, dsl.Enum):
            return ""

        values = ", ".join(f"'{x}'" for x in value.values)
        if self.source.is_array:
            return f" check ({self.name} is null or array_length({self.name}, 1) = 0 or {self.name} <@ ARRAY[{values}])"
        return f" check ({self.name} in ({values}))"


@dataclass
class ForeignKeyColumn:
    """A synthetic column for a join table or a reverse composition reference."""

    name: str
    is_required: bool = False
    type: ClassVar[str] = "BIGINT"
    is_id: ClassVar[bool] = False
    is_array: ClassVar[bool] = False
    is_unique: ClassVar[bool] = False
    enum: ClassVar[str] = ""
