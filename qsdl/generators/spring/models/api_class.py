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

import stringcase

import qsdl.dsl.models as dsl
import qsdl.dsl.util as qutil

from .. import util

if TYPE_CHECKING:
    from . import ModelClass, Parent


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
    is_header: bool = False
    is_body: bool = False

    def build(self, _ref: dsl.Argument) -> Parameter:
        """Builds self from dsl.Argument"""

        self.name = stringcase.camelcase(_ref.name)
        self.json_key = _ref.name

        self.type = util.custom_type(_ref.value)
        self.is_array = _ref.is_array

        self.is_required = _ref.is_required
        self.is_path = _ref.is_path
        self.is_query = _ref.is_query
        self.is_header = _ref.is_header
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
    is_generated: bool = False
    is_pageable: bool = False

    parent: Parent = None

    parameters: List[Parameter] = field(default_factory=list)
    path_parameters: List[Parameter] = field(default_factory=list)
    query_parameters: List[Parameter] = field(default_factory=list)
    header_parameters: List[Parameter] = field(default_factory=list)
    body_parameters: List[Parameter] = field(default_factory=list)

    response: Parameter = None
    response_headers: List[Parameter] = field(default_factory=list)

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

        self.is_deprecated = False
        self.is_generated = _ref.is_generated
        self.is_pageable = _ref.is_pageable

        if _ref.domain_object and _ref.domain_parent:
            self.parent = util.get_parent_for(_ref.domain_object.name, _ref.domain_parent.name)

        self.consumes = _ref.consumes
        self.produces = _ref.produces

        self._add_parameters(_ref)
        self._add_response(_ref)
        self._add_response_headers(_ref)

        return self

    def _add_parameters(self, _ref: dsl.Operation):
        """Creates and adds all parameters to a Operation"""

        # special spring directive for producing empty controller functions
        # the user is assumed to use the request context here
        void_input = qutil.get_directive_of_name("spring-void-input", _ref)

        for argument in _ref.arguments:
            new_param = Parameter().build(argument)

            if void_input and not new_param.is_path:
                continue

            self.parameters.append(new_param)

            if new_param.is_path:
                self.path_parameters.append(new_param)
            elif new_param.is_query:
                self.query_parameters.append(new_param)
            elif new_param.is_header:
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

            new_param.type = util.custom_type(_ref.value)

            if _ref.is_pageable:
                new_param.name = "CursorPage"
                new_param.json_key = "CursorPage"
                new_param.type = "CursorPage"
                new_param.is_array = False

            self.response = new_param

    def _add_response_headers(self, _ref: dsl.Operation):
        """Creates and adds a response header to a Operation"""

        for argument in _ref.response_headers:
            new_param = Parameter().build(argument)

            self.response_headers.append(new_param)


@dataclass
class ApiClass:
    """The Java Model for the Controller and Service Class"""

    name: str = None
    namespace: str = None
    description: str = None

    model: ModelClass = None

    operations: List[Operation] = field(default_factory=list)

    # addons
    has_generated: bool = False
    has_objectnode: bool = False
    api_imports: List[str] = field(default_factory=list)
    controller_imports: List[str] = field(default_factory=list)
    service_imports: List[str] = field(default_factory=list)

    def build(self, _ref: dsl.Api) -> ApiClass:
        """Builds self from dsl.Api"""

        # The api name equals the object name to unless it is not part of a object
        self.name = _ref.parent.name if _ref.parent._tx_fqn == "entity.Object" else "Default"
        self.namespace = stringcase.lowercase(_ref.namespace)
        self.description = _ref.description

        # allow to overwrite the controller name
        controller_dir = qutil.get_directive_of_name("controller", _ref)
        self.name = controller_dir.value if controller_dir else self.name

        # add model
        if _ref.parent._tx_fqn == "entity.Object":
            self.model = util.get_model_for(_ref.parent.name)

        # add methods
        self._add_operations(_ref)

        self.has_generated = _ref.has_generated
        self.has_objectnode = util.controller_has(_ref, has_objectnode=True)
        self.api_imports = util.get_api_imports(_ref)
        self.controller_imports = util.get_controller_imports(_ref, self.name)
        self.service_imports = util.get_service_imports(_ref)

        return self

    def _add_operations(self, _ref: dsl.Api):
        """Creates and adds all Operations to a ApiClass"""

        for operation in _ref.operations:
            new_operation = Operation().build(operation)

            self.operations.append(new_operation)
