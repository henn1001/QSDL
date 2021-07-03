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

"""Spring Generator Model class"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

import stringcase

from qsdl.dsl.models import Field

from .. import util

if TYPE_CHECKING:
    from qsdl.dsl.models import Base, Enum, Object


@dataclass
class _Attribute:
    """Custom dataclass"""

    # the textx object
    _ref: Field

    # computed attributes
    name: str = None
    json_key: str = None
    description: str = None
    type: str = None
    is_array: bool = False
    is_enum: bool = False
    is_base: bool = False
    is_object: bool = False
    is_id: bool = False
    is_date: bool = False
    is_required: bool = False
    is_read_only: bool = False
    is_write_only: bool = False
    is_nested: bool = False
    is_composition: bool = False
    is_aggregation: bool = False
    is_relation: bool = False

    forgein_key_field: Field = None

    getter: str = None
    setter: str = None

    def __post_init__(self):

        # rename to naming convention
        self.name = stringcase.camelcase(self._ref.name)
        self.json_key = self._ref.name
        self.description = self._ref.description

        self.type = util.custom_type(self._ref.value.name)

        self.is_array = self._ref.is_array
        self.is_enum = self._ref.value._tx_fqn in ["entity.Enum"]
        self.is_base = self._ref.value._tx_fqn in ["entity.Base"]
        self.is_object = self._ref.value._tx_fqn in ["entity.Object"]
        self.is_id = self._ref.value.name == "ID"
        self.is_date = self._ref.value.name == "Date"

        self.is_required = self._ref.is_required

        self.is_read_only = self._ref.is_read_only
        self.is_write_only = self._ref.is_write_only

        # relation model
        self.is_nested = self._ref.is_nested
        self.is_composition = self._ref.is_composition
        self.is_aggregation = self._ref.is_aggregation
        self.is_relation = self._ref.is_composition or self._ref.is_aggregation

        self.getter = "get" + stringcase.capitalcase(self.name)
        self.setter = "set" + stringcase.capitalcase(self.name)

        # special case for id references
        if self._ref.value._tx_fqn in ["entity.Object"] and not self.is_nested and not self.is_relation:
            self.type = util.custom_type("ID")
            self.is_object = False


@dataclass
class Model:
    """Custom dataclass"""

    # the textx object
    _ref: Union[Enum, Base, Object]

    # computed attributes
    name: str = None
    description: str = None
    is_enum: bool = False
    is_base: bool = False
    is_object: bool = False
    extends: str = None
    attributes: List[_Attribute] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)

    imports: List[str] = field(default_factory=list)

    # addons
    is_crud: bool = False
    is_supertype: bool = False
    is_nested: bool = False
    is_pagination: bool = False

    def __post_init__(self):

        # rename to naming convention
        self.name = stringcase.pascalcase(self._ref.name)

        self.description = self._ref.description

        # identify type
        self.is_enum = self._ref._tx_fqn in ["entity.Enum"]
        self.is_base = self._ref._tx_fqn in ["entity.Base"]
        self.is_object = self._ref._tx_fqn in ["entity.Object"]

        if not self.is_enum and self._ref.supertype:
            self.extends = stringcase.pascalcase(self._ref.supertype.name)

        # attributes
        if not self.is_enum:
            self._add_attributes()
            self._add_foreign_keys()
        else:
            self.constants = util.get_enum_values(self._ref)

        # collect imports
        self.imports = util.get_model_imports(self._ref)

        # addons
        self.is_crud = self._ref.is_crud if self.is_object else False
        self.is_supertype = util.is_supertype(self._ref) if self.is_base else False
        self.is_nested = util.is_nested(self._ref)

    def _add_attributes(self):

        if self._ref._tx_fqn not in ["entity.Base", "entity.Object"]:
            raise ValueError

        for entity_field in self._ref.fields:
            attribute = _Attribute(entity_field)
            self.attributes.append(attribute)

    def _add_foreign_keys(self):

        # we only care about object relations
        if not self.is_object:
            return

        # get the fields of all parents that
        # use self as aggregation or composition
        fields = util.get_parent_fields(self._ref)

        for p_field in fields:
            parent = p_field.parent

            # create a new field for self that represents the other side
            # of the reference
            fk_field = Field()

            # aggregations
            fk_field.name = stringcase.snakecase(parent.name)
            fk_field.name = fk_field.name + "s" if p_field.is_aggregation else fk_field.name

            fk_field.value = parent
            fk_field.is_array = p_field.is_aggregation
            fk_field.is_aggregation = p_field.is_aggregation
            fk_field.is_composition = p_field.is_composition

            attribute = _Attribute(fk_field)
            attribute.forgein_key_field = p_field
            self.attributes.append(attribute)
