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

"""Spring Generator Model class"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

import stringcase

from .. import util

if TYPE_CHECKING:
    import qsdl.dsl.models as dsl


@dataclass
class ModelField:
    """The field of a Schema Model"""

    name: str = None
    json_key: str = None
    description: str = None

    type: str = None
    is_array: bool = False

    is_required: bool = False
    is_read_only: bool = False
    is_write_only: bool = False

    is_enum: bool = False
    is_base: bool = False
    is_object: bool = False
    is_id: bool = False
    is_date: bool = False

    is_composition: bool = False
    is_aggregation: bool = False
    is_relation: bool = False

    # addon
    format: str = None
    min_size: str = None
    max_size: str = None

    def build(self, _ref: dsl.Field) -> ModelField:
        """Builds self from dsl.Field"""

        # rename to naming convention
        self.name = stringcase.camelcase(_ref.name)
        self.json_key = _ref.name
        self.description = _ref.description

        self.type = util.custom_type(_ref.value.name)
        self.format = util.custom_type_format(_ref.value.name)

        self._add_constraints(_ref)

        self.is_array = _ref.is_array
        self.is_enum = _ref.value._tx_fqn in ["entity.Enum"]
        self.is_base = _ref.value._tx_fqn in ["entity.Base"]
        self.is_object = _ref.value._tx_fqn in ["entity.Object"]
        self.is_id = _ref.value.name == "ID"
        self.is_date = _ref.value.name == "Date"

        self.is_required = _ref.is_required

        self.is_read_only = _ref.is_read_only
        self.is_write_only = _ref.is_write_only

        # relation model
        self.is_composition = _ref.is_composition
        self.is_aggregation = _ref.is_aggregation
        self.is_relation = _ref.is_relation

        return self

    def _add_constraints(self, _ref: dsl.Field):
        """Adds min max constraints"""

        if _ref.value.name == "String":
            self.min_size = f"minLength: {_ref.min_size}" if _ref.min_size else None
            self.max_size = f"maxLength: {_ref.max_size}" if _ref.max_size else "maxLength: 255"

        if _ref.value.name == "Int":
            self.min_size = f"minimum: {_ref.min_size}" if _ref.min_size else "minimum: 0"
            self.max_size = f"maximum: {_ref.max_size}" if _ref.max_size else None

        if _ref.value.name == "Long":
            self.min_size = f"minimum: {_ref.min_size}" if _ref.min_size else "minimum: 0"
            self.max_size = f"maximum: {_ref.max_size}" if _ref.max_size else None


@dataclass
class ModelObject:
    """The Schema Model for the Openapi schema"""

    # computed attributes
    name: str = None
    description: str = None
    is_enum: bool = False
    is_base: bool = False
    is_object: bool = False
    extends: str = None
    attributes: List[ModelField] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)

    # addons
    is_supertype: bool = False
    is_nested: bool = False

    def build(self, _ref: Union[dsl.Enum, dsl.Base, dsl.Object]) -> ModelObject:
        """Builds self from Union[dsl.Enum, dsl.Base, dsl.Object]"""

        # rename to naming convention
        self.name = stringcase.pascalcase(_ref.name)

        self.description = _ref.description

        # identify type
        self.is_enum = _ref._tx_fqn in ["entity.Enum"]
        self.is_base = _ref._tx_fqn in ["entity.Base"]
        self.is_object = _ref._tx_fqn in ["entity.Object"]

        if not self.is_enum and _ref.supertype:
            self.extends = stringcase.pascalcase(_ref.supertype.name)

        # attributes
        if not self.is_enum:
            self._add_attributes(_ref)
        else:
            self.constants = util.get_enum_values(_ref)

        # addons
        self.is_supertype = util.is_supertype(_ref) if self.is_base else False
        self.is_nested = util.is_nested(_ref)

        return self

    def _add_attributes(self, _ref: Union[dsl.Enum, dsl.Base, dsl.Object]):

        if _ref._tx_fqn not in ["entity.Base", "entity.Object"]:
            raise ValueError

        for entity_field in _ref.fields:
            # filter hidden relations
            if not entity_field.is_relation:
                attribute = ModelField().build(entity_field)
                self.attributes.append(attribute)

    def get_required(self):
        """Returns a list of required attributes."""
        required = []

        for attribute in self.attributes:
            if attribute.is_required:
                required.append(attribute)

        return required
