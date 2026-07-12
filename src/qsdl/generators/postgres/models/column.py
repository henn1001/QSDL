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

import qsdl.filter as qfilter
from qsdl import dsl

from .. import util


def T_PREFIX() -> str:
    return util.Store.config.table_prefix.lower()


class Column:
    """The column of a table"""

    def __init__(self) -> None:
        self._ref: dsl.Field

        self.name: str
        self.type: str
        self.enum: str

        self.is_id: bool = False
        self.is_array: bool = False
        self.is_required: bool = False
        self.is_unique: bool = False

    @staticmethod
    def from_ref(_ref: dsl.Field, prefix: str = "") -> Self:
        """Rebuilds the column from a new reference"""
        column = Column()
        column._ref = _ref

        column.name = prefix + qfilter.snakecase(_ref.name).lower()
        column.type = util.custom_type(_ref.value)

        column.enum = ""

        column.is_id = _ref.value.name == "ID"
        column.is_array = _ref.is_array
        column.is_required = _ref.is_required
        column.is_unique = _ref.is_unique

        # relations (only for Objects, not Bases - Bases are handled separately)
        if isinstance(_ref.value, dsl.Object):
            column.name += f"_{_ref.value.name.lower()}_id"
            column.type = "BIGINT"

        # Enum handling
        if isinstance(_ref.value, dsl.Enum):
            column.type = "TEXT"
            values = (", ").join([f"'{x}'" for x in _ref.value.values])

            if column.is_array:
                column.enum = f" check ({column.name} is null or array_length({column.name}, 1) = 0 or {column.name} <@ ARRAY[{values}])"
            else:
                column.enum = f" check ({column.name} in ({values}))"

        # Special handling for Object scalar type arrays: JSONB can natively store arrays
        if _ref.value.name == "Object" and column.is_array:
            # Don't add [] suffix - JSONB natively handles arrays
            column.is_array = False

        return column
