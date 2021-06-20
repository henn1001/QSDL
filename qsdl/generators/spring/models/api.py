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

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

import stringcase

from .. import util

if TYPE_CHECKING:
    from qsdl.dsl.models import Field, Operation


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


@dataclass
class _Operation:
    """Custom dataclass"""

    # the textx object
    _ref: Field

    # computed attributes
    name: str = None
    tag: str = None
    summary: str = None
    description: str = None
    path: str = None
    method: str = None
    is_deprecated: bool = False
    is_crud: bool = False
    is_pageable: bool = False

    parameters: List[_Parameter] = field(default_factory=list)
    path_parameters: List[_Parameter] = field(default_factory=list)
    query_parameters: List[_Parameter] = field(default_factory=list)
    body_parameters: List[_Parameter] = field(default_factory=list)
    response: _Parameter = None

    def __post_init__(self):

        self.name = self._ref.name
        self.tag = self._ref.parent.namespace
        self.summary = self._ref.summary
        self.description = self._ref.description
        self.path = self._ref.path
        self.method = self._ref.method.lower()
        # self.is_crud = field.is_crud
        self.is_pageable = self._ref.is_pageable

        self._add_parameters()

        # remove reference for faster debugging
        self._ref = None

    def _add_parameters(self):

        for argument in self._ref.arguments:
            param = _Parameter()
            param.name = stringcase.camelcase(argument.name)
            param.json_key = argument.name
            param.is_required = argument.non_nullable
            param.is_array = argument.array

            param.type = util.custom_type(argument.value.name)

            param.is_path = argument.path
            param.is_query = argument.query
            param.is_body = argument.body

            if param.is_path:
                self.path_parameters.append(param)
                self.parameters.append(param)
            if param.is_query:
                self.query_parameters.append(param)
                self.parameters.append(param)
            if param.is_body and not self._ref.method == "DELETE":
                self.body_parameters.append(param)
                self.parameters.append(param)

        # response
        if self._ref.value:
            param = _Parameter()
            param.name = stringcase.camelcase(self._ref.value.name)
            param.json_key = self._ref.value.name
            param.is_required = False
            param.is_array = self._ref.array

            param.type = util.custom_type(self._ref.value.name)

            if self._ref.is_pageable:
                param.name += "List"
                param.json_key += "List"
                param.type += "List"

            self.response = param


@dataclass
class Api:
    """Custom dataclass"""

    _ref: Operation

    # computed attributes
    name: str = None
    capital_name: str = None
    tag: str = None
    description: str = None
    operations: List = field(default_factory=list)

    def __post_init__(self):

        name = self._ref.parent.name if self._ref.parent._tx_fqn == "entity.Object" else "Default"

        self.name = stringcase.lowercase(name)
        self.capital_name = stringcase.capitalcase(name)
        self.tag = stringcase.lowercase(self._ref.namespace)
        self.description = self._ref.description

        self._add_operations(self._ref.fields)

        # remove reference for faster debugging
        self._ref = None

    def _add_operations(self, operations):

        for operation in operations:
            new_operation = _Operation(operation)
            self.operations.append(new_operation)
