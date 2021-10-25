# Copyright (C) 2020 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Spring Generator Parent class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import HibernateParentInfo, ModelClass, ModelField


@dataclass
class Parent:
    """Contains the ModelClass and specifies the relation type"""

    model: ModelClass = None
    field: ModelField = None
    hibernate: HibernateParentInfo = None
    predicate: str = None

    def build(self, parent: ModelClass, child: ModelClass) -> Parent:
        """Builds self from Parent and Child ModelClass"""

        self.model = parent

        for parent_field in parent.fields:
            if parent_field.type == child.name:
                self.field = parent_field

        for child_field in child.fields:
            if child_field.type == parent.name:
                self.predicate = child_field.name
                self.predicate += ".any()" if child_field.is_array else ""

        return self
