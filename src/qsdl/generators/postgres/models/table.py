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

"""PostgreSQL table models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

import qsdl.casing as qfilter
from qsdl import dsl

from .. import util
from .column import Column, ForeignKeyColumn


@dataclass
class Table:
    """A table backed by a DSL object."""

    source: dsl.Object
    name: str = field(init=False)
    columns: list[Column | ForeignKeyColumn] = field(default_factory=list, init=False)
    constraints: list[str] = field(default_factory=list, init=False)
    is_jointable: ClassVar[bool] = False

    def __post_init__(self) -> None:
        self.name = util.T_PREFIX() + qfilter.snakecase(self.source.name).lower()

        for dsl_field in self.source.generation_fields:
            if dsl_field.directive.is_transient:
                continue

            value = dsl_field.value
            if isinstance(value, dsl.Object) and dsl_field.is_array:
                # Relationships backed by arrays are handled separately.
                continue

            if isinstance(value, dsl.Base) and not (dsl_field.is_array or dsl_field.directive.is_opaque):
                prefix = qfilter.snakecase(dsl_field.name).lower() + "_"
                self.columns.extend(util.extract_embedded_columns(value, prefix))
                continue

            column = Column(dsl_field)
            self.columns.append(column)

            if isinstance(value, dsl.Object):
                ref_table_name = util.T_PREFIX() + qfilter.snakecase(value.name).lower()
                field_name = qfilter.snakecase(dsl_field.name).lower()
                self.constraints.append(util.build_fk_constraint(self.name, field_name, column.name, ref_table_name))


@dataclass
class JoinTable:
    """A synthetic table for an aggregation relationship."""

    name: str
    columns: tuple[ForeignKeyColumn, ForeignKeyColumn]
    constraints: ClassVar[tuple[()]] = ()
    is_jointable: ClassVar[bool] = True
