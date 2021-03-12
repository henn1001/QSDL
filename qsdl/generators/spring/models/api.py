from dataclasses import dataclass, field
from typing import List

import stringcase

from .. import util


@dataclass
class _Parameter:

    name: str = None
    json_key: str = None
    description: str = None
    type: str = None
    is_array: bool = False
    is_required: bool = False

    is_query: bool = False
    is_path: bool = False
    is_body: bool = False

    def __post_init__(self):
        _ = None


@dataclass
class _Operation:

    # the textx object
    _ref: object

    # computed attributes
    name: str = None
    tag: str = None
    summary: str = None
    description: str = None
    path: str = None
    method: str = None
    is_deprecated: bool = False

    parameters: List[_Parameter] = field(default_factory=list)
    path_parameters: List[_Parameter] = field(default_factory=list)
    query_parameters: List[_Parameter] = field(default_factory=list)
    body_parameters: List[_Parameter] = field(default_factory=list)
    response: _Parameter = None

    def __post_init__(self):

        self.name = self._ref.name
        self.tag = self._ref.tag
        self.summary = self._ref.summary
        self.description = self._ref.description
        self.path = self._ref.path
        self.method = self._ref.method

        self._add_parameters()

    def _add_parameters(self):

        for p in self._ref.parameters:
            param = _Parameter()
            param.name = stringcase.camelcase(p["name"])
            param.json_key = p["name"]
            param.is_required = p["required"].lower() == "true"
            param.is_array = False

            if isinstance(p["type"], dict):
                param.type = util.custom_type(p["type"]["value"].name)
            else:
                param.type = util.custom_type(p["type"].value.name)

            if p["in"] == "path":
                param.is_path = True
                self.path_parameters.append(param)

            if p["in"] == "query":
                param.is_query = True
                self.query_parameters.append(param)

            self.parameters.append(param)

        for p in self._ref.request:
            if p._tx_fqn == "entity.Object":
                param = _Parameter()
                # param.name = stringcase.camelcase(p.name)
                param.name = "body"
                param.json_key = p.name
                param.is_required = True
                param.is_array = False

                param.type = util.custom_type(p.name)

            else:
                # entity.Field?
                param = _Parameter()
                param.name = stringcase.camelcase(p.name)
                param.json_key = p.name
                param.is_required = p.non_nullable
                param.is_array = p.array

                param.type = util.custom_type(p.value.name)

            param.is_body = True
            self.body_parameters.append(param)
            self.parameters.append(param)

        if self._ref.response:
            p = self._ref.response

            if isinstance(p, dict):
                # entity.Object?

                param = _Parameter()
                param.name = stringcase.camelcase(p["value"].name)
                param.json_key = p["value"].name
                param.is_required = False
                param.is_array = p["array"]
                param.type = util.custom_type(p["value"].name)

                if p["paging"]:
                    param.name += "List"
                    param.json_key += "List"
                    param.type += "List"

                self.response = param if param.type != "Void" else None
            else:
                # entity.Field?
                param = _Parameter()
                param.name = stringcase.camelcase(p.value.name)
                param.json_key = p.value.name
                param.is_required = p.non_nullable
                param.is_array = p.array
                param.type = util.custom_type(p.value.name)

                self.response = param if param.type != "Void" else None


@dataclass
class Api:

    _ref: object

    # computed attributes
    name: str = None
    capital_name: str = None
    tag: str = None
    description: str = None
    operations: List = field(default_factory=list)
    imports: List = field(default_factory=list)

    def __post_init__(self):

        tag_and_name = self._ref[0]
        operations = self._ref[1]

        self.name = tag_and_name[1]
        self.capital_name = stringcase.capitalcase(self.name)
        self.tag = tag_and_name[0]
        self.description = None

        self._add_operations(operations)

    def _add_operations(self, operations):

        for operation in operations:
            new_operation = _Operation(operation)
            self.operations.append(new_operation)
