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

"""Spring domain model and field projections."""

from __future__ import annotations

from dataclasses import InitVar, dataclass, field

import qsdl.casing as qfilter
import qsdl.dsl.util as qutil
from qsdl import dsl
from qsdl.dsl.directives import AGGREGATION, COMPOSITION

from .. import models as spring
from .. import util
from ..config import IDTYPE, Database


@dataclass
class ModelField:
    """A schema field projected into a Java DTO or Hibernate entity."""

    source: dsl.Field = field(repr=False, compare=False)
    java_name: InitVar[str | None] = None
    dto_nested_path: str | None = None
    foreign_key: dsl.Field | None = field(default=None, repr=False, compare=False)

    name: str = field(init=False)
    type: str = field(init=False)
    entity_type: str = field(init=False)
    pattern: str | None = field(init=False)
    min_size: str | None = field(init=False, default=None)
    max_size: str | None = field(init=False, default=None)
    default: str | None = field(init=False)
    nested_type_has_request: bool = field(init=False, default=False)

    def __post_init__(self, java_name: str | None) -> None:
        self.name = java_name if java_name is not None else util.java_identifier(self.source.name)
        self.type = util.custom_type(self.source.value)
        self.entity_type = util.custom_type_entity(self.source.value) or self.type
        self.pattern = util.custom_type_pattern(self.source.value)
        self._add_constraints()

    @property
    def is_name_escaped(self) -> bool:
        """Whether the original name required escaping rather than only casing."""
        name = self.source.name
        return self.dto_nested_path is None and util.java_identifier(name) != qfilter.camelcase(name)

    @property
    def is_enum(self) -> bool:
        return isinstance(self.source.value, dsl.Enum)

    @property
    def is_base(self) -> bool:
        return isinstance(self.source.value, dsl.Base)

    @property
    def is_object(self) -> bool:
        return isinstance(self.source.value, dsl.Object)

    @property
    def is_relation(self) -> bool:
        return qutil.is_relation(self.source)

    def _add_constraints(self) -> None:
        """Adds min max constraints"""
        directive = self.source.directive
        min_size = directive.min_size.value if directive.min_size is not None else None
        max_size = directive.max_size.value if directive.max_size is not None else None
        default = directive.default.value if directive.default is not None else None

        if self.type == "String":
            self.min_size = f"{min_size}" if min_size else "0"
            self.max_size = f"{max_size}" if max_size else "255"

        if self.type == "Integer":
            self.min_size = f"{min_size}" if min_size else "0"
            self.max_size = f"{max_size}" if max_size else "Integer.MAX_VALUE"

        if self.type == "Long":
            self.min_size = f"{min_size}L" if min_size else "0L"
            self.max_size = f"{max_size}L" if max_size else "Long.MAX_VALUE"

        # default value is a bit tricky
        if self.is_enum:
            self.default = f"{self.type}.{default}" if default else None
        elif self.type == "String":
            self.default = f'"{default}"' if default else None
        elif self.type == "Integer":
            self.default = f"{default}" if default else None
        elif self.type == "Long":
            self.default = f"{default}l" if default else None
        elif self.type == "Float":
            self.default = f"{default}f" if default else None
        elif self.type == "Double":
            self.default = f"{default}d" if default else None
        elif self.type == "Boolean":
            self.default = "true" if str(default).lower() == "true" else "false" if default else None
        else:
            self.default = f"{default}" if default else None


@dataclass
class ModelClass:
    """A Java domain model projected from a schema base or object."""

    source: dsl.Base | dsl.Object = field(repr=False, compare=False)
    is_query_filter: bool = False
    has_request: bool = True
    has_response: bool = field(init=False, default=True)

    fields: list[ModelField] = field(init=False)
    entity_fields: list[ModelField] = field(init=False)
    is_aggregated: bool = field(init=False)
    has_required: bool = field(init=False)
    has_query: bool = field(init=False)

    package: spring.Package = field(init=False)
    hibernate: spring.HibernateModelInfo | None = field(init=False, default=None)
    parents: list[spring.Parent] = field(init=False, default_factory=list)
    mappers: list[dsl.Base | dsl.Object] = field(init=False)

    def __post_init__(self) -> None:
        source = self.source
        self.package = spring.Package(util.Store.config, util.package_namespace(source))

        parent_fields = util.get_parent_fields(source.name)
        self.is_aggregated = any(field.directive.is_aggregation for field in parent_fields)
        self.has_required = any(
            field.is_required and field.name != "id" and not qutil.is_relation(field)
            for field in source.generation_fields
        )
        self.has_query = any(
            field.directive.is_query or field.directive.is_query_list for field in source.generation_fields
        )

        mappers = {}
        for nested_field in util.extract_fields_for_mapper(source):
            mappers.setdefault(nested_field.value.name, nested_field.value)
        self.mappers = list(mappers.values())

        fields = [field for field in source.generation_fields if not qutil.is_relation(field)]
        self.fields = [ModelField(field) for field in fields]
        self.entity_fields = util.extract_embedded_columns(fields)

        if isinstance(source, dsl.Object):
            if util.Store.config.database == Database.HIBERNATE:
                self.hibernate = spring.HibernateModelInfo(source, util.Store.config.id_type == IDTYPE.LONG)
            self._add_relations()
            self._add_foreign_keys(parent_fields)

    @property
    def name(self) -> str:
        return self.source.name

    @property
    def is_object(self) -> bool:
        return isinstance(self.source, dsl.Object)

    @property
    def request_fields(self) -> list[ModelField]:
        """Fields rendered in a request record."""
        return [field for field in self._dto_fields() if not field.source.directive.is_read_only]

    @property
    def response_fields(self) -> list[ModelField]:
        """Fields rendered in a response record."""
        return [field for field in self._dto_fields() if not field.source.directive.is_write_only]

    def _dto_fields(self) -> list[ModelField]:
        return [field for field in self.fields if not field.is_relation and not field.source.directive.is_hidden]

    def _add_relations(self) -> None:
        for source in self.source.generation_fields:
            if not qutil.is_relation(source):
                continue
            name = qfilter.raw_camelcase(util.custom_type(source.value)) + ("s" if source.is_array else "")
            field = ModelField(source, java_name=name)
            self.fields.append(field)
            self.entity_fields.append(field)

    def _add_foreign_keys(self, parent_fields: list[dsl.Field]) -> None:
        for source in parent_fields:
            parent = source.parent
            is_aggregation = source.directive.is_aggregation
            name = qfilter.raw_camelcase(parent.name) + ("s" if is_aggregation else "")

            # The synthetic field is the child/owning side of the relation.
            inverse = dsl.Field(parent=self.source, name=name, value=parent, is_array=is_aggregation)
            for spec in (AGGREGATION, COMPOSITION):
                if source.directives.get(spec):
                    inverse.directives.attach_synthetic(spec, True)

            field = ModelField(inverse, foreign_key=source)
            self.fields.append(field)
            self.entity_fields.append(field)
