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

"""Generator Utility functions"""

import qsdl.casing as qfilter
import qsdl.dsl.util as qutil
from qsdl import dsl
from qsdl.generators.directive_payloads import scalar_mapping

from .config import POSTGRES_SCALAR, PostgresConfig
from .models import Column, ForeignKeyColumn, JoinTable, Table


class Store:
    """Parsed data storage class"""

    schema: dsl.Schema
    config: PostgresConfig


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
    mapping = scalar_mapping(entity, POSTGRES_SCALAR)
    return mapping if mapping is not None else custom_types.get(entity.name, entity.name)


def T_PREFIX() -> str:
    return Store.config.table_prefix.lower()


def build_jointables(table: Table) -> list[JoinTable]:
    """Creates all jointables for many to many relations (aggregation)"""

    return_tables = []

    for dsl_field in table.source.generation_fields:
        # Only Object type arrays create join tables (Base types are always JSONB)
        if not (isinstance(dsl_field.value, dsl.Object) and dsl_field.is_array and dsl_field.directive.is_aggregation):
            continue

        source_table_name = table.name
        ref_table_name = T_PREFIX() + qfilter.snakecase(dsl_field.value.name).lower()

        name_left = table.source.name.lower()
        name_right = qfilter.snakecase(dsl_field.value.name).lower()

        column_a = ForeignKeyColumn(f"{name_left}_id", is_required=True)
        column_b = ForeignKeyColumn(f"{name_right}_id", is_required=True)
        new_table = JoinTable(f"{source_table_name}_to_{ref_table_name}", (column_a, column_b))

        # add the foreign key constraints
        table.constraints.extend(
            [
                build_fk_constraint(new_table.name, name_left.lower(), column_a.name, table.name),
                build_fk_constraint(new_table.name, name_right.lower(), column_b.name, ref_table_name),
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
    dsl_fields = qutil.get_composition_fields(Store.schema, table.source.name)

    for dsl_field in dsl_fields:
        # field.parent is the parent Object that has the composition
        parent_obj = dsl_field.parent
        ref_table_name = T_PREFIX() + qfilter.snakecase(parent_obj.name).lower()
        field_name = f"{qfilter.snakecase(dsl_field.name)}_{parent_obj.name}".lower()

        # Add foreign key column to this (child) table pointing to parent
        fk_column = ForeignKeyColumn(f"{field_name}_id")
        table.columns.append(fk_column)

        # Add foreign key constraint
        table.constraints.append(build_fk_constraint(table.name, field_name, fk_column.name, ref_table_name))


def build_fk_constraint(table_name: str, fk_target: str, column_name: str, ref_table_name: str) -> str:
    """Helper to build a foreign key constraint string."""
    fk_name = f"fk_{table_name}_{fk_target}"
    return (
        f"ALTER TABLE IF EXISTS {table_name} ADD CONSTRAINT {fk_name} "
        f"FOREIGN KEY ({column_name}) REFERENCES {ref_table_name}(id);"
    )


def extract_embedded_columns(ref: dsl.Base, prefix: str = "") -> list[Column]:
    """Recursively flattens Base type fields into columns with prefixes.

    Note: This function is only called for Base types WITHOUT @opaque directive.
    Base types with @opaque are stored as JSONB and don't reach this function.
    """
    columns = []
    for field in ref.generation_fields:
        # Skip fields that are transient - these should not be persisted to the DB
        if field.directive.is_transient:
            continue

        if isinstance(field.value, dsl.Base):
            # Recursively flatten nested Base types (always flatten, ignore @opaque for nested)
            nested_prefix = prefix + qfilter.snakecase(field.name).lower() + "_"
            columns.extend(extract_embedded_columns(field.value, nested_prefix))
        else:
            columns.append(Column(field, prefix))
    return columns
