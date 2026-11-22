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

"""Spring Data repository names."""

from __future__ import annotations

from dataclasses import dataclass, field

import qsdl.casing as qfilter
from qsdl import dsl

from .. import models as spring


@dataclass(frozen=True, eq=False)
class HibernateParentInfo:
    """Repository lookups through the child's field pointing to its parent."""

    source: spring.ModelField = field(repr=False, compare=False)
    is_id_long: bool

    @property
    def find_by_parent_id_and_id(self) -> str:
        return f"findBy{qfilter.pascalcase(self.source.name)}IdAndId"

    @property
    def find_by_parent_id_and_uid(self) -> str:
        return f"findBy{qfilter.pascalcase(self.source.name)}IdAndUid"

    @property
    def find_by_parent_and_id(self) -> str:
        return self.find_by_parent_id_and_id if self.is_id_long else self.find_by_parent_id_and_uid


@dataclass(frozen=True, eq=False)
class HibernateModelInfo:
    """Repository lookup and parameter names for an object."""

    source: dsl.Object = field(repr=False, compare=False)
    is_id_long: bool

    @property
    def parameter_joined_id(self) -> str:
        return qfilter.raw_camelcase(self.source.name) + "Id"

    @property
    def find_by_id(self) -> str:
        return "findById" if self.is_id_long else "findByUid"
