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

"""Spring Generator Api class"""

from __future__ import annotations

from typing import TYPE_CHECKING

import stringcase

from .. import util

if TYPE_CHECKING:
    from . import ModelClass, ModelField


class HibernateFieldInfo:
    """Custom dataclass"""

    def __init__(self, field: ModelField):
        pass


class HibernateParentInfo:
    """Custom dataclass"""

    def __init__(self, model: ModelClass, parent: ModelClass):
        """
        Example:
          method_joined_id      = TicketIdAndId
        """
        self.method_joined_id = stringcase.pascalcase(util.get_field_for(model, parent).name) + "IdAndId"


class HibernateModelInfo:
    """Custom dataclass"""

    def __init__(self, model: ModelClass):
        """
        Example:
          method_joined_id      = ProjectId
          parameter_joined_id   = projectId
        """
        self.method_joined_id = stringcase.pascalcase(model.name) + "Id"
        self.parameter_joined_id = stringcase.camelcase(model.name) + "Id"
