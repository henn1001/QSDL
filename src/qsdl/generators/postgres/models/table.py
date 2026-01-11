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

"""Generator class"""

from __future__ import annotations

import qsdl.filter as qfilter
from qsdl import dsl

from .. import util
from . import Column


class Table:
    """The table of a Database Entity"""

    def __init__(self) -> None:
        self._ref: dsl.Object | dsl.Base

        self.name: str
        self.is_jointable: bool = False

        self.columns: list[Column] = []
        self.constraints: list[str] = []

    @staticmethod
    def from_ref(_ref: dsl.Object | dsl.Base) -> Table:
        """Rebuilds the table from a new reference"""
        table = Table()
        table._ref = _ref
        table.name = util.T_PREFIX() + qfilter.snakecase(_ref.name).upper()

        dsl_fields = [x for x in table._ref.fields]

        for dsl_field in dsl_fields:
            # Handle arrays of Object types - either composition or aggregation
            if isinstance(dsl_field.value, dsl.Object) and dsl_field.is_array:
                # handled later
                continue

            # Handle arrays of Base types - ALWAYS JSONB (value objects)
            if isinstance(dsl_field.value, dsl.Base) and dsl_field.is_array:
                new_column = Column()
                new_column.name = qfilter.snakecase(dsl_field.name).lower()
                new_column.type = "JSONB"
                new_column.is_required = dsl_field.is_required
                new_column.is_unique = dsl_field.is_unique
                table.columns.append(new_column)
                continue  # Skip join table creation

            # Handle Base types with new semantics
            if isinstance(dsl_field.value, dsl.Base):
                if dsl_field.is_opaque:
                    # @opaque = JSONB storage (FIXED SEMANTICS!)
                    new_column = Column()
                    new_column.name = qfilter.snakecase(dsl_field.name).lower()
                    new_column.type = "JSONB"
                    new_column.is_required = dsl_field.is_required
                    new_column.is_unique = dsl_field.is_unique
                    table.columns.append(new_column)
                else:
                    # DEFAULT = Flatten columns (NEW DEFAULT!)
                    embedded_prefix = qfilter.snakecase(dsl_field.name).lower() + "_"
                    table.columns.extend(util.extract_embedded_columns(dsl_field.value, embedded_prefix))
                continue  # Skip rest of logic for Base types

            # Normal column creation for non-Base types
            new_column = Column.from_ref(dsl_field)
            table.columns.append(new_column)

            # one to one object relation (only for Objects now)
            if isinstance(dsl_field.value, dsl.Object):
                ref_table_name = util.T_PREFIX() + qfilter.snakecase(dsl_field.value.name).upper()
                field_name = qfilter.snakecase(dsl_field.name).upper()

                table.constraints.extend(
                    [
                        util.build_fk_constraint(table.name, field_name, new_column.name, ref_table_name),
                    ]
                )

                # Ensure the foreign key column is unique
                new_column.is_unique = True

        return table
