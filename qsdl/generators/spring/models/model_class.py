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

import qsdl.dsl.models as dsl

from .. import util

if TYPE_CHECKING:
    from . import HibernateFieldInfo, HibernateModelInfo, HibernateParentInfo


@dataclass
class Parent:
    """Contains the ModelClass and specifies the relation type"""

    model: ModelClass
    is_aggregation: bool
    is_composition: bool = False
    hibernate: HibernateParentInfo = None

    def __post_init__(self):
        self.is_composition = not self.is_aggregation


@dataclass
class ModelField:
    """The field of a Java Model"""

    # the textx object
    _ref: dsl.Field

    # computed attributes
    name: str = None
    json_key: str = None
    description: str = None

    type: str = None
    is_array: bool = False

    is_required: bool = False
    is_read_only: bool = False
    is_write_only: bool = False
    is_query: bool = False

    is_enum: bool = False
    is_base: bool = False
    is_object: bool = False
    is_id: bool = False
    is_date: bool = False

    is_composition: bool = False
    is_aggregation: bool = False
    is_relation: bool = False
    is_relation_owner: bool = False
    foreign_key_name: str = None
    foreign_key_is_array: bool = False

    hibernate: HibernateFieldInfo = None

    getter: str = None
    setter: str = None

    def __post_init__(self):
        """Init our dataclass by reading information from _ref"""

        # rename to naming convention
        self.name = stringcase.camelcase(self._ref.name)
        self.json_key = self._ref.name
        self.description = self._ref.description

        self.type = util.custom_type(self._ref.value.name)
        self.is_array = self._ref.is_array

        self.is_required = self._ref.is_required
        self.is_read_only = self._ref.is_read_only
        self.is_write_only = self._ref.is_write_only
        self.is_query = self._ref.is_query

        self.is_enum = self._ref.value._tx_fqn in ["entity.Enum"]
        self.is_base = self._ref.value._tx_fqn in ["entity.Base"]
        self.is_object = self._ref.value._tx_fqn in ["entity.Object"]
        self.is_id = self._ref.value.name == "ID"
        self.is_date = self._ref.value.name == "Date"

        # relation model
        self.is_composition = self._ref.is_composition
        self.is_aggregation = self._ref.is_aggregation
        self.is_relation = self.is_composition or self.is_aggregation

        self.getter = "get" + stringcase.pascalcase(self.name)
        self.setter = "set" + stringcase.pascalcase(self.name)


@dataclass
class ModelClass:
    """The Java Model for the Domain Class Object"""

    # the textx object
    _ref: Union[dsl.Enum, dsl.Base, dsl.Object]

    # computed attributes
    name: str = None
    description: str = None

    is_enum: bool = False
    is_base: bool = False
    is_object: bool = False

    fields: List[ModelField] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)

    imports: List[str] = field(default_factory=list)

    # addons
    is_crud: bool = False
    is_supertype: bool = False
    is_nested: bool = False
    has_aggregation: bool = False
    has_required: bool = False
    has_query: bool = False

    hibernate: HibernateModelInfo = None

    parents: List[Parent] = field(default_factory=list)

    def __post_init__(self):
        """Init our dataclass by reading information from _ref"""

        # rename to naming convention
        self.name = self._ref.name

        self.description = self._ref.description

        # identify type
        self.is_enum = self._ref._tx_fqn in ["entity.Enum"]
        self.is_base = self._ref._tx_fqn in ["entity.Base"]
        self.is_object = self._ref._tx_fqn in ["entity.Object"]

        # add attributes
        self._add_attributes()
        self._add_constants()
        self._add_relations()
        self._add_foreign_keys()

        # collect imports
        self.imports = util.get_model_imports(self._ref)

        # addons
        self.is_crud = self._ref.is_crud if self.is_object else False
        self.is_supertype = util.is_supertype(self._ref) if self.is_base else False
        self.is_nested = util.is_nested(self._ref)
        self.has_aggregation = util.has(self._ref, has_aggregation=True)
        self.has_required = util.has(self._ref, has_required_ignore_id=True)
        self.has_query = util.has(self._ref, has_query=True)

    def _add_attributes(self):
        """Creates and adds all visible attributes to a ModelClass"""

        # filter on base and object
        if not (self.is_base or self.is_object):
            return

        # filter only non relations
        dsl_fields = [x for x in self._ref.fields if not x.is_relation]

        for dsl_field in dsl_fields:
            new_model_field = ModelField(dsl_field)

            self.fields.append(new_model_field)

    def _add_constants(self):
        """Adds all values for Enums"""

        # filter only enum
        if not self.is_enum:
            return

        for value in self._ref.values:
            self.constants.append(value)

    def _add_relations(self):
        """Creates and adds all explicit relation attributes to a ModelClass"""

        # filter on object
        if not self.is_object:
            return

        # filter only relations
        dsl_fields = [x for x in self._ref.fields if x.is_relation]

        for dsl_field in dsl_fields:
            new_model_field = ModelField(dsl_field)
            # TODO: rename new_model_field name

            self.fields.append(new_model_field)

    def _add_foreign_keys(self):
        """Creates and adds all implicit relation attributes to a ModelClass"""

        # filter on object
        if not self.is_object:
            return

        # get the fields of all parents that
        # use self as aggregation or composition
        # TODO: add nested Objects
        dsl_fields = util.get_parent_fields(self._ref)

        for dsl_field in dsl_fields:
            parent = dsl_field.parent

            # create a new field for self that represents the other side
            # of the reference
            fk_field = dsl.Field()

            # aggregations
            fk_field.name = stringcase.snakecase(parent.name)
            fk_field.name = fk_field.name + "s" if dsl_field.is_aggregation else fk_field.name

            fk_field.value = parent
            fk_field.is_array = dsl_field.is_aggregation
            fk_field.is_aggregation = dsl_field.is_aggregation
            fk_field.is_composition = dsl_field.is_composition

            new_model_field = ModelField(fk_field)
            new_model_field.is_relation_owner = True
            new_model_field.foreign_key_name = dsl_field.name
            new_model_field.foreign_key_is_array = dsl_field.is_array

            self.fields.append(new_model_field)
