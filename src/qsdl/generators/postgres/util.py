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

"""Generator Utility functions"""

from __future__ import annotations

import qsdl.dsl.models as dsl
import qsdl.dsl.util as qutil
import qsdl.filter as qfilter
from qsdl import dsl

from .config import Config, Directive
from .models import Column, Table


class Store:
    """Parsed data storage class"""

    schema: dsl.Schema
    config: Config


custom_types = {
    "Int": "INTEGER",
    "Long": "BIGINT",
    "Float": "REAL",
    "Double": "DOUBLE PRECISION",
    "String": "TEXT",
    "Boolean": "BOOLEAN",
    "ID": "integer",
    "Date": "DATE",
    "Datetime": "TIMESTAMP",
    "Object": "JSONB",
}


def custom_type(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, custom_types, entity.name, Directive.TYPE, ["format", "pattern"], "type")


def T_PREFIX() -> str:
    return Store.config.table_prefix.upper()


def build_jointables(table: Table) -> list[Table]:
    """Creates all jointables for many to many relations (aggregation)"""

    return_tables = []

    for dsl_field in table._ref.fields:
        # Only Object type arrays create join tables (Base types are always JSONB)
        if not (isinstance(dsl_field.value, dsl.Object) and dsl_field.is_array and dsl_field.is_aggregation):
            continue

        source_table_name = table.name
        field_name = qfilter.snakecase(dsl_field.name).upper()
        ref_table_name = T_PREFIX() + qfilter.snakecase(dsl_field.value.name).upper()

        name_left = table._ref.name.lower()
        name_right = qfilter.snakecase(dsl_field.value.name).lower()

        new_table = Table()
        new_table.name = f"{source_table_name}_{field_name}_TO_{ref_table_name}"
        new_table.is_jointable = True

        # new table has two columns, one for each side of the relation
        column_a = Column()
        column_a.name = f"{name_left}_id"
        column_a.type = "BIGINT"
        column_a.is_required = True
        column_b = Column()
        column_b.name = f"{name_right}_id"
        column_b.type = "BIGINT"
        column_b.is_required = True

        new_table.columns.extend([column_a, column_b])

        # add the foreign key constraints
        table.constraints.extend(
            [
                build_fk_constraint(new_table.name, name_left.upper(), column_a.name, table.name),
                build_fk_constraint(new_table.name, name_right.upper(), column_b.name, ref_table_name),
            ]
        )

        # add the new table to the return list
        return_tables.append(new_table)

    return return_tables


def build_composition_fks(table: Table) -> None:
    """Adds foreign key columns for composition relationships where this table is the child.

    For composition relationships, the child table gets a foreign key pointing to the parent.
    This matches the Hibernate/JPA pattern of @ManyToOne/@OneToMany relationships.

    Args:
        table: The child table to add foreign keys to
    """
    # Find all composition fields that reference this Object
    composition_fields = qutil.get_composition_fields(Store.schema, table._ref.name)

    for field in composition_fields:
        # field.parent is the parent Object that has the composition
        parent_obj = field.parent
        parent_table_name = T_PREFIX() + qfilter.snakecase(parent_obj.name).upper()

        # Add foreign key column to this (child) table pointing to parent
        fk_column = Column()
        fk_column.name = f"{parent_obj.name.lower()}_id"
        fk_column.type = "BIGINT"
        fk_column.is_required = True  # Compositions typically require the parent
        table.columns.append(fk_column)

        # Add foreign key constraint
        table.constraints.append(
            build_fk_constraint(table.name, parent_obj.name.upper(), fk_column.name, parent_table_name)
        )


def build_fk_constraint(table_name: str, fk_target: str, column_name: str, ref_table_name: str) -> str:
    """Helper to build a foreign key constraint string."""
    fk_name = f"FK_{table_name}_{fk_target}"
    return (
        f"alter table if exists {table_name} add constraint {fk_name} "
        f"foreign key ({column_name}) references {ref_table_name}(id);"
    )


def extract_embedded_columns(ref, prefix="") -> list[Column]:
    """Recursively flattens Base type fields into columns with prefixes.

    Note: This function is only called for Base types WITHOUT @opaque directive.
    Base types with @opaque are stored as JSONB and don't reach this function.
    """
    columns = []
    for field in ref.fields:
        if isinstance(field.value, dsl.Base):
            # Recursively flatten nested Base types (always flatten, ignore @opaque for nested)
            nested_prefix = prefix + qfilter.snakecase(field.name).lower() + "_"
            columns.extend(extract_embedded_columns(field.value, nested_prefix))
        else:
            columns.append(Column.from_ref(field, prefix))
    return columns
