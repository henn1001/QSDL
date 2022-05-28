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
    from qsdl.dsl.models import Api as QAPI
    from qsdl.dsl.models import Operation


@dataclass
class _Parameter:
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
class _Operation:
    """Custom dataclass"""

    # the textx object
    _ref: Operation

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

    parameters: List[_Parameter] = field(default_factory=list)
    path_parameters: List[_Parameter] = field(default_factory=list)
    query_parameters: List[_Parameter] = field(default_factory=list)
    body_parameters: List[_Parameter] = field(default_factory=list)

    response: _Parameter = None

    consumes: str = None
    produces: str = None

    def __post_init__(self):

        self.name = self._ref.name
        self.tag = self._ref.parent.namespace
        self.summary = self._ref.summary
        self.description = self._ref.description
        self.path = self._ref.path
        self.method = self._ref.method.lower()
        self.is_generated = self._ref.is_generated
        self.is_pageable = self._ref.is_pageable

        # special for aggregations
        # we want to move them to the parent namespace
        if self._ref.is_aggregated:
            self.tag = self._ref.domain_parent.namespace

        self.consumes = self._ref.consumes
        self.produces = self._ref.produces

        self._add_parameters()

    def _add_parameters(self):

        for argument in self._ref.arguments:
            param = _Parameter()
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
            if param.is_body and self._ref.method != "DELETE":
                self.body_parameters.append(param)

        # response
        if self._ref.value:
            param = _Parameter()
            # param.name = stringcase.camelcase(field.value.name)
            param.name = self._ref.value.name
            param.json_key = self._ref.value.name
            param.is_required = False
            param.is_array = self._ref.is_array

            param.type = util.custom_type(self._ref.value.name)
            param.format = util.custom_type_format(self._ref.value.name)

            if self._ref.is_pageable:
                param.name += "List"
                param.json_key += "List"
                param.type += "List"
                param.is_array = False

            if self._ref.value._tx_fqn in ["entity.Enum", "entity.Base", "entity.Object"]:
                param.ref = f"#/components/schemas/{ param.type }"

            self.response = param


@dataclass
class Api:
    """Custom dataclass"""

    _ref: QAPI

    # computed attributes
    name: str = None
    tag: str = None
    description: str = None
    operations: List = field(default_factory=list)

    def __post_init__(self):

        self.name = self._ref.parent.name if self._ref.parent._tx_fqn == "entity.Object" else "Default"
        self.tag = self._ref.namespace
        self.description = self._ref.description

        self._add_operations(self._ref.operations)

    def _add_operations(self, operations):

        for operation in operations:
            new_operation = _Operation(operation)
            self.operations.append(new_operation)
