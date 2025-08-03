# Copyright (C) 2022 henn1001

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

import stringcase

from .. import models as spring
from .. import util


class HibernateFieldInfo:
    """Custom dataclass"""

    def __init__(self, field: spring.ModelField) -> None:
        pass


class HibernateParentInfo:
    """Custom dataclass"""

    def __init__(self, model: spring.ModelClass, parent: spring.ModelClass) -> None:
        """
        Example:
          method_joined_id      = TicketIdAndId
          method_joined_uid      = TicketUidAndUid
        """
        self.method_joined_id = stringcase.pascalcase(util.get_field_for(model, parent).name) + "IdAndId"
        self.method_joined_uid = stringcase.pascalcase(util.get_field_for(model, parent).name) + "IdAndUid"

        self.find_by_parentid_and_id = "findBy"
        self.find_by_parentid_and_id += self.method_joined_id if util.Store.is_id_long else self.method_joined_uid


class HibernateModelInfo:
    """Custom dataclass"""

    def __init__(self, model: spring.ModelClass) -> None:
        """
        Example:
          method_joined_id      = ProjectId
          parameter_joined_id   = projectId
        """
        self.method_joined_id = stringcase.pascalcase(model.name) + "Id"
        self.parameter_joined_id = stringcase.camelcase(model.name) + "Id"

        self.find_by_id = "findById" if util.Store.is_id_long else "findByUid"
