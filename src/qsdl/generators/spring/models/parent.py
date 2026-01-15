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

"""Spring Generator Parent class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from .. import models as spring
from .. import util


@dataclass
class Parent:
    """Contains the spring.ModelClass and specifies the relation type"""

    model: spring.ModelClass = None
    field: spring.ModelField = None
    hibernate: spring.HibernateParentInfo = None
    predicate: str = None

    def build(self, parent: spring.ModelClass, child: spring.ModelClass) -> Self:
        """Builds self from Parent and Child spring.ModelClass"""

        self.model = parent
        self.field = util.get_field_for(parent, child)

        child_field = util.get_field_for(child, parent)
        self.predicate = child_field.name + ".any()" if child_field.is_array else child_field.name

        return self
