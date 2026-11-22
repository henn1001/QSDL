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

"""Spring parent relation model."""

from __future__ import annotations

from dataclasses import InitVar, dataclass, field

from .. import models as spring
from .. import util
from ..config import IDTYPE, Database


@dataclass
class Parent:
    """A parent model, its relation field, and the inverse field on the child."""

    model: spring.ModelClass = field(repr=False, compare=False)
    child: InitVar[spring.ModelClass]
    child_field: spring.ModelField = field(init=False, repr=False, compare=False)
    hibernate: spring.HibernateParentInfo | None = field(init=False, default=None)
    field: spring.ModelField = field(init=False)

    def __post_init__(self, child: spring.ModelClass) -> None:
        self.field = util.get_field_for(self.model, child)
        self.child_field = util.get_field_for(child, self.model)
        if util.Store.config.database == Database.HIBERNATE:
            self.hibernate = spring.HibernateParentInfo(self.child_field, util.Store.config.id_type == IDTYPE.LONG)

    @property
    def predicate(self) -> str:
        """QueryDSL path to the parent, through a collection when necessary."""
        suffix = ".any()" if self.child_field.source.is_array else ""
        return f"{self.child_field.name}{suffix}"
