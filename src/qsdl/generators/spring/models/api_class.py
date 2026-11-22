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

"""Spring controller and operation models."""

from __future__ import annotations

from dataclasses import dataclass, field

import qsdl.casing as qfilter
import qsdl.dsl.util as qutil
from qsdl import dsl

from .. import models as spring
from .. import util
from ..config import SPRING_CONTROLLER, SPRING_PACKAGE


@dataclass
class Parameter:
    """Java projection of an operation argument."""

    source: dsl.Argument = field(repr=False, compare=False)
    name: str = field(init=False)
    type: str = field(init=False)

    def __post_init__(self) -> None:
        self.name = qfilter.raw_camelcase(self.source.name)
        self.type = util.argument_type(self.source)

    @property
    def is_model(self) -> bool:
        """Whether the parameter references a schema base or object."""
        return isinstance(self.source.value, dsl.Base | dsl.Object)


@dataclass
class Operation:
    """Java projection of a schema operation."""

    source: dsl.Operation = field(repr=False, compare=False)
    method: str = field(init=False)
    parent: spring.Parent | None = field(init=False, default=None)
    path_parameters: list[Parameter] = field(init=False, default_factory=list)
    body_parameters: list[Parameter] = field(init=False, default_factory=list)
    response_type: str = field(init=False)
    consumes: str | None = field(init=False)
    produces: str | None = field(init=False)
    filter_name: str | None = field(init=False)
    request_dto_name: str | None = field(init=False)

    def __post_init__(self) -> None:
        source = self.source
        directive = source.directive
        self.method = directive.method.value.lower()

        if source.domain_object and source.domain_parent:
            self.parent = util.get_parent_for(source.domain_object.name, source.domain_parent.name)

        self.consumes = qutil.render_media_type(directive.consumes, applicable=bool(source.body_parameters))
        self.produces = qutil.render_media_type(directive.produces, applicable=source.value is not None)

        self.path_parameters = [Parameter(argument) for argument in source.path_parameters]
        if self.method != "delete":
            self.body_parameters = [Parameter(argument) for argument in source.body_parameters]

        if source.value is None:
            self.response_type = "Void"
        else:
            value_type = util.custom_type(source.value)
            if directive.is_pageable:
                self.response_type = f"CursorPage<{value_type}>"
            elif source.is_array:
                self.response_type = f"List<{value_type}>"
            else:
                self.response_type = value_type

        self.filter_name = util.resolve_query_filter(source)
        self.request_dto_name = util.resolve_request_body_dto(source)


@dataclass
class ApiClass:
    """Controller and service model, including operations merged from other APIs."""

    source: dsl.Api = field(repr=False, compare=False)
    name: str = field(init=False)
    model: spring.ModelClass | None = field(init=False, default=None)
    operations: list[Operation] = field(init=False)
    package_priority: int = field(init=False, default=0)
    package: spring.Package = field(init=False)

    def __post_init__(self) -> None:
        source = self.source
        owner = source.parent
        self.name = self.controller_target or (owner.name if isinstance(owner, dsl.Object) else "Default")

        if isinstance(owner, dsl.Object):
            self.model = util.get_model_for(owner.name)

        self.operations = [Operation(operation) for operation in source.operations]

        # API-local directives take priority over the owning Object. An inherited
        # namespace is only an API tag and cannot override an Object's @spring-package.
        package_directive = source.directives.get(SPRING_PACKAGE)
        namespace = source.directive.namespace
        if package_directive:
            self.package = spring.Package(util.Store.config, package_directive.value)
            self.package_priority = 3
        elif namespace and namespace.origin == "source" and namespace.value:
            self.package = spring.Package(util.Store.config, qfilter.lowercase(namespace.value))
            self.package_priority = 2
        elif self.model:
            self.package = self.model.package
            self.package_priority = 1
        else:
            self.package = spring.Package(util.Store.config)

    @property
    def controller_target(self) -> str | None:
        """The explicitly targeted controller, if any."""
        directive = self.source.directives.get(SPRING_CONTROLLER)
        return directive.value if directive else None
