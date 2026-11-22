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

"""OpenAPI schema component models."""

from __future__ import annotations

from dataclasses import dataclass, field

import qsdl.casing as qfilter
import qsdl.dsl.util as qutil
from qsdl import dsl

from .. import util


@dataclass
class ModelField:
    """OpenAPI schema metadata for a DSL field."""

    source: dsl.Field = field(repr=False, compare=False)
    name: str = field(init=False)
    type: str = field(init=False)
    ref: str | None = field(init=False, default=None)
    format: str | None = field(init=False)
    pattern: str | None = field(init=False)
    min_size: str | None = field(init=False, default=None)
    max_size: str | None = field(init=False, default=None)
    default: str | None = field(init=False)

    def __post_init__(self) -> None:
        source = self.source
        self.name = qfilter.raw_camelcase(source.name)
        self.type = util.custom_type(source.value)
        self.format = util.custom_type_format(source.value)
        self.pattern = util.custom_type_pattern(source.value)
        if isinstance(source.value, dsl.Enum | dsl.Base | dsl.Object):
            self.ref = f"#/components/schemas/{self.type}"

        directive = source.directive
        min_size = directive.min_size.value if directive.min_size is not None else None
        max_size = directive.max_size.value if directive.max_size is not None else None
        default = directive.default.value if directive.default is not None else None

        if self.type == "string" and self.format not in ["date", "date-time"]:
            self.min_size = f"minLength: {min_size}" if min_size else None
            self.max_size = f"maxLength: {max_size}" if max_size else "maxLength: 255"

        if self.type in ["integer", "number"]:
            self.min_size = f"minimum: {min_size}" if min_size else "minimum: 0"
            self.max_size = f"maximum: {max_size}" if max_size else None

        self.default = f"default: {default}" if default else None


@dataclass
class ModelObject:
    """An OpenAPI schema component backed by a DSL declaration."""

    source: dsl.Enum | dsl.Base | dsl.Object = field(repr=False, compare=False)
    name: str = field(init=False)
    is_enum: bool = field(init=False)
    attributes: list[ModelField] = field(init=False, default_factory=list)
    constants: list[str] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.name = qfilter.pascalcase(self.source.name)
        self.is_enum = isinstance(self.source, dsl.Enum)
        if isinstance(self.source, dsl.Enum):
            self.constants = util.get_enum_values(self.source)
        else:
            self.attributes = [
                ModelField(source)
                for source in self.source.generation_fields
                if not qutil.is_relation(source) and not source.directive.is_hidden
            ]

    @property
    def required_fields(self) -> list[ModelField]:
        """Return the required attributes."""
        return [attribute for attribute in self.attributes if attribute.source.is_required]
