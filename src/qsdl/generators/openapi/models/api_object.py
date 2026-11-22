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

"""OpenAPI operation and parameter projections."""

from dataclasses import dataclass, field

import qsdl.casing as qfilter
import qsdl.dsl.util as qutil
from qsdl import dsl
from qsdl.dsl.directives import ResponseHeader

from .. import util


@dataclass
class Parameter:
    """Schema metadata for an argument, response body, or response header."""

    source: dsl.Argument | dsl.Operation | ResponseHeader = field(repr=False, compare=False)
    type: str = field(init=False)
    format: str | None = field(init=False)
    pattern: str | None = field(init=False)
    ref: str | None = field(init=False)

    def __post_init__(self) -> None:
        value = self.source.value
        self.type = util.custom_type(value)
        self.format = util.custom_type_format(value)
        self.pattern = None if isinstance(self.source, dsl.Operation) else util.custom_type_pattern(value)
        if isinstance(self.source, dsl.Operation) and self.source.directive.is_pageable:
            self.type += "List"
        self.ref = f"#/components/schemas/{self.type}" if isinstance(value, dsl.Enum | dsl.Base | dsl.Object) else None

    @property
    def is_ref_body(self) -> bool:
        return isinstance(self.source.value, dsl.Base | dsl.Object)


@dataclass
class Operation:
    """An operation projected into an OpenAPI path."""

    source: dsl.Operation = field(repr=False, compare=False)
    tag: str = field(init=False)
    path: str = field(init=False)
    method: str = field(init=False)
    parameters: list[Parameter] = field(init=False)
    path_parameters: list[Parameter] = field(init=False)
    query_parameters: list[Parameter] = field(init=False)
    body_parameters: list[Parameter] = field(init=False)
    response: Parameter | None = field(init=False)
    response_headers: list[Parameter] = field(init=False)
    consumes: str | None = field(init=False)
    produces: str | None = field(init=False)
    request_dto_name: str | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        source = self.source
        directive = source.directive
        self.tag = qutil.render_namespace(source.domain_parent if source.is_aggregated else source.parent)
        self.path = directive.path.value
        self.method = directive.method.value.lower()
        self.consumes = qutil.render_media_type(directive.consumes, applicable=bool(source.body_parameters))
        self.produces = qutil.render_media_type(directive.produces, applicable=source.value is not None)

        if (
            source.body_parameters
            and self.method not in ("get", "delete")
            and not (
                len(source.body_parameters) == 1 and isinstance(source.body_parameters[0].value, dsl.Base | dsl.Object)
            )
        ):
            self.request_dto_name = qfilter.pascalcase(source.name) + "Request"

        self.parameters = [Parameter(arg) for arg in source.arguments if arg.is_path or arg.is_query or arg.is_header]
        self.path_parameters = [param for param in self.parameters if param.source.is_path]
        self.query_parameters = [
            param for param in self.parameters if not param.source.is_path and param.source.is_query
        ]
        self.body_parameters = [
            Parameter(arg)
            for arg in source.arguments
            if arg.is_body and not (arg.is_path or arg.is_query or arg.is_header) and directive.method.value != "DELETE"
        ]
        self.response = Parameter(source) if source.value else None
        self.response_headers = [Parameter(header) for header in directive.headers.value] if directive.headers else []
