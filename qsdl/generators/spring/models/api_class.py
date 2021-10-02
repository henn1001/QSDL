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
from typing import List

import stringcase

import qsdl.dsl.models as dsl

from .. import util


@dataclass
class Parameter:
    """Method parameters and return value."""

    name: str = None
    json_key: str = None

    type: str = None
    is_array: bool = False

    is_required: bool = False
    is_query: bool = False
    is_path: bool = False
    is_body: bool = False

    def build(self, _ref: dsl.Argument) -> Parameter:
        """Builds self from dsl.Argument"""

        self.name = stringcase.camelcase(_ref.name)
        self.json_key = _ref.name

        self.type = util.custom_type(_ref.value.name)
        self.is_array = _ref.is_array

        self.is_required = _ref.is_required
        self.is_path = _ref.is_path
        self.is_query = _ref.is_query
        self.is_body = _ref.is_body

        return self


@dataclass
class Operation:
    """The Operation/Methods for a Api"""

    name: str = None
    tag: str = None
    summary: str = None
    description: str = None

    path: str = None
    method: str = None

    is_deprecated: bool = False
    is_crud: bool = False
    is_pageable: bool = False

    domain_object: dsl.Object = None
    domain_parent: dsl.Object = None

    parameters: List[Parameter] = field(default_factory=list)
    path_parameters: List[Parameter] = field(default_factory=list)
    query_parameters: List[Parameter] = field(default_factory=list)
    body_parameters: List[Parameter] = field(default_factory=list)

    response: Parameter = None

    def build(self, _ref: dsl.Operation) -> Operation:
        """Builds self from dsl.Operation"""

        self.name = _ref.name
        self.tag = _ref.parent.namespace
        self.summary = _ref.summary
        self.description = _ref.description

        self.path = _ref.path
        self.method = _ref.method.lower()

        self.is_deprecated = False
        self.is_crud = _ref.parent.parent.is_crud if _ref.parent.parent._tx_fqn == "entity.Object" else False
        self.is_pageable = _ref.is_pageable

        self.domain_object = _ref.domain_object
        self.domain_parent = _ref.domain_parent

        self._add_parameters(_ref)
        self._add_response(_ref)

        return self

    def _add_parameters(self, _ref: dsl.Operation):
        """Creates and adds all parameters to a Operation"""

        for argument in _ref.arguments:
            new_param = Parameter().build(argument)

            self.parameters.append(new_param)

            if new_param.is_path:
                self.path_parameters.append(new_param)
            elif new_param.is_query:
                self.query_parameters.append(new_param)
            elif new_param.is_body and not _ref.method == "DELETE":
                self.body_parameters.append(new_param)

    def _add_response(self, _ref: dsl.Operation):
        """Creates and adds a response parameter to a Operation"""

        if _ref.value:
            new_param = Parameter()
            new_param.name = stringcase.camelcase(_ref.value.name)
            new_param.json_key = _ref.value.name
            new_param.is_array = _ref.is_array

            new_param.type = util.custom_type(_ref.value.name)

            if _ref.is_pageable:
                new_param.name = "ObjectList"
                new_param.json_key = "ObjectList"
                new_param.type = "ObjectList"
                new_param.is_array = False

            self.response = new_param

    def get_aggregation_parameter(self) -> List[str]:
        ret = "error"

        for param in self.domain_parent.fields:
            if param.value == self.domain_object:
                ret = param.name
                break

        return ret

    def get_read_only_parameters(self, encapsulation) -> List[str]:
        ret = []

        # first get all fields
        filtered_fields = util.get_filtered_fields_as_list(self.domain_object)

        # get read only fields
        field_names = [x.name for x in filtered_fields if x.is_read_only and x.name.lower() != "id"]

        for name in field_names:
            getter = stringcase.pascalcase(name) if encapsulation else stringcase.camelcase(name)
            ret.append(getter)

        return ret

    def get_writable_parameters(self, encapsulation) -> List[str]:
        ret = []

        # first get all fields
        filtered_fields = util.get_filtered_fields_as_list(self.domain_object)

        # get read only fields
        field_names = [x.name for x in filtered_fields if not x.is_read_only]

        for name in field_names:
            getter = stringcase.pascalcase(name) if encapsulation else stringcase.camelcase(name)
            ret.append(getter)

        return ret

    def get_repo_find_all_name(self) -> str:
        ret = "findAll"
        ret += "By" + stringcase.pascalcase(self.path_parameters[0].name) if self.domain_parent else ""
        return ret

    def get_repo_count_name(self) -> str:
        ret = "count"
        ret += "By" + stringcase.pascalcase(self.path_parameters[0].name) if self.domain_parent else ""
        return ret

    def get_repo_find_all_parameters(self) -> str:
        ret = ""
        for parameter in self.path_parameters:
            ret += parameter.name
            ret += ", "

        # add pagable object or remove last seperator
        if self.is_pageable:
            ret += "pageable"
        else:
            ret = ret[:-2]
        return ret

    def get_repo_by_id_name(self) -> str:
        ret = "By"
        for parameter in self.path_parameters:
            ret += stringcase.pascalcase(parameter.name)
            ret += "And"
        return ret[:-3]

    def get_repo_by_id_parameters(self) -> str:
        ret = ""
        for parameter in self.path_parameters:
            ret += parameter.name
            ret += ", "
        return ret[:-2]


@dataclass
class ApiClass:
    """The Java Model for the Controller and Service Class"""

    name: str = None
    tag: str = None
    description: str = None

    operations: List[Operation] = field(default_factory=list)

    def build(self, _ref: dsl.Api) -> ApiClass:
        """Builds self from dsl.Api"""

        # The api name equals the object name to unless it is not part of a object
        self.name = _ref.parent.name if _ref.parent._tx_fqn == "entity.Object" else "Default"
        self.tag = stringcase.lowercase(_ref.namespace)
        self.description = _ref.description

        # add methods
        self._add_operations(_ref)

        return self

    def _add_operations(self, _ref: dsl.Api):
        """Creates and adds all Operations to a ApiClass"""

        for operation in _ref.operations:
            new_operation = Operation().build(operation)

            self.operations.append(new_operation)
