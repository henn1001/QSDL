# Copyright 2025 henn1001
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

"""Spring Generator Api class"""

from __future__ import annotations

from dataclasses import dataclass, field

from qsdl import dsl

from .. import util


@dataclass
class Parameter:
    """Custom dataclass"""

    name: str = None
    json_key: str = None

    type: str = None
    is_array: bool = False
    is_required: bool = False

    is_query: bool = False
    is_path: bool = False
    is_header: bool = False
    is_body: bool = False

    ref: str = None
    is_ref_body: bool = False

    # addon
    format: str = None
    pattern: str = None

    def build(self, _ref: dsl.Argument) -> Parameter:
        """Builds self from dsl.Argument"""

        self.name = _ref.name
        self.json_key = _ref.name

        self.type = util.custom_type(_ref.value)
        self.format = util.custom_type_format(_ref.value)
        self.pattern = util.custom_type_pattern(_ref.value)

        self.is_array = _ref.is_array
        self.is_required = _ref.is_required

        self.is_path = _ref.is_path
        self.is_query = _ref.is_query
        self.is_header = _ref.is_header
        self.is_body = _ref.is_body

        if isinstance(_ref.value, dsl.Enum | dsl.Base | dsl.Object):
            self.ref = f"#/components/schemas/{self.type}"

        if isinstance(_ref.value, dsl.Base | dsl.Object):
            self.is_ref_body = True

        return self


@dataclass
class Operation:
    """The Operation/Methods for a Api"""

    # computed attributes
    name: str = None
    tag: str = None
    summary: str = None
    description: list[str] = field(default_factory=list)
    path: str = None
    method: str = None
    is_deprecated: bool = False
    is_generated: bool = False
    is_pageable: bool = False

    parameters: list[Parameter] = field(default_factory=list)
    path_parameters: list[Parameter] = field(default_factory=list)
    query_parameters: list[Parameter] = field(default_factory=list)
    header_parameters: list[Parameter] = field(default_factory=list)
    body_parameters: list[Parameter] = field(default_factory=list)

    response: Parameter = None
    response_headers: list[Parameter] = field(default_factory=list)

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
        self._add_response(_ref)
        self._add_response_headers(_ref)

        return self

    def _add_parameters(self, _ref: dsl.Operation) -> None:
        """Creates and adds all parameters to a Operation"""

        for argument in _ref.arguments:
            new_param = Parameter().build(argument)

            # we need to explicitly split parameters and requestbody for openapi
            if new_param.is_path:
                self.path_parameters.append(new_param)
                self.parameters.append(new_param)
            elif new_param.is_query:
                self.query_parameters.append(new_param)
                self.parameters.append(new_param)
            elif new_param.is_header:
                self.header_parameters.append(new_param)
                self.parameters.append(new_param)
            elif new_param.is_body and _ref.method != "DELETE":
                self.body_parameters.append(new_param)

    def _add_response(self, _ref: dsl.Operation) -> None:
        """Creates and adds a response parameter to a Operation"""

        if _ref.value:
            new_param = Parameter()
            new_param.name = _ref.value.name
            new_param.json_key = _ref.value.name
            new_param.is_array = _ref.is_array

            new_param.type = util.custom_type(_ref.value)
            new_param.format = util.custom_type_format(_ref.value)

            if _ref.is_pageable:
                new_param.name += "List"
                new_param.json_key += "List"
                new_param.type += "List"
                new_param.is_array = False

            if isinstance(_ref.value, dsl.Enum | dsl.Base | dsl.Object):
                new_param.ref = f"#/components/schemas/{new_param.type}"

            self.response = new_param

    def _add_response_headers(self, _ref: dsl.Operation) -> None:
        """Creates and adds a response header to a Operation"""

        for argument in _ref.response_headers:
            new_param = Parameter().build(argument)

            self.response_headers.append(new_param)


@dataclass
class ApiObject:
    """Custom dataclass"""

    # computed attributes
    name: str = None
    tag: str = None
    description: list[str] = field(default_factory=list)
    operations: list = field(default_factory=list)

    def build(self, _ref: dsl.Api) -> ApiObject:
        """Builds self from dsl.Api"""

        self.name = _ref.parent.name if isinstance(_ref.parent, dsl.Object) else "Default"
        self.tag = _ref.namespace
        self.description = _ref.description

        self._add_operations(_ref.operations)

        return self

    def _add_operations(self, operations: list[Operation]) -> None:
        new_operations: list[Operation] = []

        for operation in operations:
            new_operation = Operation().build(operation)
            new_operations.append(new_operation)

        # makes sure the sorting is alligned with the way openapi specifies endpoints
        new_operations.sort(key=lambda x: x.path)

        self.operations = new_operations
