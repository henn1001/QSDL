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

"""Generator Model class"""

from __future__ import annotations

import qsdl.filter as qfilter
from qsdl import dsl

from .. import util


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
    def from_ref(_ref: dsl.Field, prefix: str = "") -> Column:
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
        if _ref.value._tx_fqn == "entity.Object":
            column.name += f"_{_ref.value.name.lower()}_id"
            column.type = "BIGINT"

        column._extend_type_field(_ref)

        return column

    def _extend_type_field(self, _ref: dsl.Field) -> None:
        # Special handling for Object scalar type arrays: JSONB can natively store arrays
        if _ref.value.name == "Object" and self.is_array:
            # Don't add [] suffix - JSONB natively handles arrays
            self.is_array = False

        if isinstance(_ref.value, dsl.Enum):
            self.type = "TEXT"
            values = (", ").join([f"'{x}'" for x in _ref.value.values])

            if self.is_array:
                self.enum = f" check ({self.name} is null or array_length({self.name}, 1) = 0 or {self.name} <@ ARRAY[{values}])"
            else:
                self.enum = f" check ({self.name} in ({values}))"


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
        table.name = qfilter.snakecase(_ref.name).upper()

        table._build_columns()
        return table

    def _build_columns(self) -> None:
        """Creates all visible attributes"""

        dsl_fields = [x for x in self._ref.fields]

        for dsl_field in dsl_fields:
            # Handle arrays of Base types - ALWAYS JSONB (value objects)
            if isinstance(dsl_field.value, dsl.Base) and dsl_field.is_array:
                new_column = Column()
                new_column.name = qfilter.snakecase(dsl_field.name).lower()
                new_column.type = "JSONB"
                new_column.is_required = dsl_field.is_required
                new_column.is_unique = dsl_field.is_unique
                self.columns.append(new_column)
                continue  # Skip join table creation

            # Handle arrays of Object types - join tables (entity relationships)
            if isinstance(dsl_field.value, dsl.Object) and dsl_field.is_array:
                # Join table handling in build_jointables()
                continue

            # Handle Base types with new semantics
            if isinstance(dsl_field.value, dsl.Base):
                if dsl_field.is_opaque:
                    # @opaque = JSONB storage (FIXED SEMANTICS!)
                    new_column = Column()
                    new_column.name = qfilter.snakecase(dsl_field.name).lower()
                    new_column.type = "JSONB"
                    new_column.is_required = dsl_field.is_required
                    new_column.is_unique = dsl_field.is_unique
                    self.columns.append(new_column)
                else:
                    # DEFAULT = Flatten columns (NEW DEFAULT!)
                    embedded_prefix = qfilter.snakecase(dsl_field.name).lower() + "_"
                    self.columns.extend(_extract_embedded_columns(dsl_field.value, embedded_prefix))
                continue  # Skip rest of logic for Base types

            # Normal column creation for non-Base types
            new_column = Column.from_ref(dsl_field)
            self.columns.append(new_column)

            # one to one object relation (only for Objects now)
            if isinstance(dsl_field.value, dsl.Object):
                ref_table_name = qfilter.snakecase(dsl_field.value.name).upper()
                field_name = qfilter.snakecase(dsl_field.name).upper()

                self.constraints.extend(
                    [
                        _build_fk_constraint(self.name, field_name, new_column.name, ref_table_name),
                    ]
                )

                # Ensure the foreign key column is unique
                new_column.is_unique = True

    def build_jointables(self) -> list[Table]:
        """Creates all jointables for many to many relations"""

        return_tables = []

        for dsl_field in self._ref.fields:
            # Only Object type arrays create join tables (Base types are always JSONB)
            if not (isinstance(dsl_field.value, dsl.Object) and dsl_field.is_array):
                continue

            # create a new table for the many to many relation
            if isinstance(dsl_field.value, dsl.Object):
                source_table_name = self.name
                fiel_name = qfilter.snakecase(dsl_field.name).upper()
                ref_table_name = qfilter.snakecase(dsl_field.value.name).upper()

                new_table = Table()
                new_table.name = f"{source_table_name}_{fiel_name}_TO_{ref_table_name}"
                new_table.is_jointable = True

                # new table has two columns, one for each side of the relation
                column_a = Column()
                column_a.name = f"{self.name.lower()}_id"
                column_a.type = "BIGINT"
                column_a.is_required = True
                column_b = Column()
                column_b.name = f"{qfilter.snakecase(dsl_field.value.name).lower()}_id"
                column_b.type = "BIGINT"
                column_b.is_required = True

                new_table.columns.extend([column_a, column_b])

                # add the foreign key constraints
                self.constraints.extend(
                    [
                        _build_fk_constraint(new_table.name, self.name, column_a.name, self.name),
                        _build_fk_constraint(new_table.name, ref_table_name, column_b.name, ref_table_name),
                    ]
                )

                # add the new table to the return list
                return_tables.append(new_table)

        return return_tables


def _build_fk_constraint(table_name: str, fk_target: str, column_name: str, ref_table_name: str) -> str:
    """Helper to build a foreign key constraint string."""
    fk_name = f"FK_{table_name}_{fk_target}"
    return (
        f"alter table if exists {util.Store.config.table_prefix}{table_name} add constraint {fk_name} "
        f"foreign key ({column_name}) references {util.Store.config.table_prefix}{ref_table_name}(id);"
    )


def _extract_embedded_columns(ref, prefix=""):
    """Recursively flattens Base type fields into columns with prefixes.

    Note: This function is only called for Base types WITHOUT @opaque directive.
    Base types with @opaque are stored as JSONB and don't reach this function.
    """
    columns = []
    for field in ref.fields:
        if isinstance(field.value, dsl.Base):
            # Recursively flatten nested Base types (always flatten, ignore @opaque for nested)
            nested_prefix = prefix + qfilter.snakecase(field.name).lower() + "_"
            columns.extend(_extract_embedded_columns(field.value, nested_prefix))
        else:
            columns.append(Column.from_ref(field, prefix))
    return columns
