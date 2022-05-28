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

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from .. import util

if TYPE_CHECKING:
    import qsdl.dsl.models as dsl


@dataclass
class Parameter:
    """Custom dataclass"""

    name: str = None
    json_key: str = None
    description: str = None
    type: str = None
    is_array: bool = False
    is_required: bool = False

    is_query: bool = False
    is_path: bool = False
    is_body: bool = False

    ref: str = None
    is_ref_body: bool = False
    format: str = None


@dataclass
class Operation:
    """Custom dataclass"""

    # computed attributes
    name: str = None
    tag: str = None
    summary: str = None
    description: str = None
    path: str = None
    method: str = None
    is_deprecated: bool = False
    is_generated: bool = False
    is_pageable: bool = False

    parameters: List[Parameter] = field(default_factory=list)
    path_parameters: List[Parameter] = field(default_factory=list)
    query_parameters: List[Parameter] = field(default_factory=list)
    body_parameters: List[Parameter] = field(default_factory=list)

    response: Parameter = None

    consumes: str = None
    produces: str = None

    def build(self, _ref: dsl.Operation) -> Operation:
        """Builds self from dsl.Operation"""

        self.name = _ref.name
        self.tag = _ref.parent.namespace
        self.summary = _ref.summary
        self.description = _ref.description
        self.path = _ref.path
        self.method = _ref.method.lower()
        self.is_generated = _ref.is_generated
        self.is_pageable = _ref.is_pageable

        # special for aggregations
        # we want to move them to the parent namespace
        if _ref.is_aggregated:
            self.tag = _ref.domain_parent.namespace

        self.consumes = _ref.consumes
        self.produces = _ref.produces

        self._add_parameters(_ref)

        return self

    def _add_parameters(self, _ref: dsl.Operation):

        for argument in _ref.arguments:
            param = Parameter()
            # param.name = stringcase.camelcase(argument.name)
            param.name = argument.name
            param.json_key = argument.name
            param.is_required = argument.is_required
            param.is_array = argument.is_array

            param.type = util.custom_type(argument.value.name)
            param.format = util.custom_type_format(argument.value.name)

            if argument.value._tx_fqn in ["entity.Enum", "entity.Base", "entity.Object"]:
                param.ref = f"#/components/schemas/{ param.type }"

            if argument.value._tx_fqn in ["entity.Base", "entity.Object"]:
                param.is_ref_body = True

            param.is_path = argument.is_path
            param.is_query = argument.is_query
            param.is_body = argument.is_body

            if param.is_path:
                self.path_parameters.append(param)
                self.parameters.append(param)
            if param.is_query:
                self.query_parameters.append(param)
                self.parameters.append(param)
            if param.is_body and _ref.method != "DELETE":
                self.body_parameters.append(param)

        # response
        if _ref.value:
            param = Parameter()
            # param.name = stringcase.camelcase(field.value.name)
            param.name = _ref.value.name
            param.json_key = _ref.value.name
            param.is_required = False
            param.is_array = _ref.is_array

            param.type = util.custom_type(_ref.value.name)
            param.format = util.custom_type_format(_ref.value.name)

            if _ref.is_pageable:
                param.name += "List"
                param.json_key += "List"
                param.type += "List"
                param.is_array = False

            if _ref.value._tx_fqn in ["entity.Enum", "entity.Base", "entity.Object"]:
                param.ref = f"#/components/schemas/{ param.type }"

            self.response = param


@dataclass
class ApiObject:
    """Custom dataclass"""

    # computed attributes
    name: str = None
    tag: str = None
    description: str = None
    operations: List = field(default_factory=list)

    def build(self, _ref: dsl.Api) -> ApiObject:
        """Builds self from dsl.Api"""

        self.name = _ref.parent.name if _ref.parent._tx_fqn == "entity.Object" else "Default"
        self.tag = _ref.namespace
        self.description = _ref.description

        self._add_operations(_ref.operations)

        return self

    def _add_operations(self, operations):

        for operation in operations:
            new_operation = Operation().build(operation)
            self.operations.append(new_operation)
