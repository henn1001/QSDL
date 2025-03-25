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

import stringcase

import qsdl.dsl.models as dsl
import qsdl.dsl.util as qutil

from .. import models as spring
from .. import util
from ..config import Directive


@dataclass
class ModelField:
    """The field of a Java Model"""

    name: str = None
    json_key: str = None
    description: list[str] = field(default_factory=list)

    type: str = None
    entity_type: str = None
    pattern: str = None
    is_array: bool = False

    is_required: bool = False
    is_read_only: bool = False
    is_write_only: bool = False
    is_unique: bool = False
    is_hidden: bool = False
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

    hibernate: spring.HibernateFieldInfo = None

    getter: str = None
    setter: str = None

    min_size: str = None
    max_size: str = None
    default: str = None

    def build(self, _ref: dsl.Field) -> ModelField:
        """Init our dataclass by reading information from _ref"""

        # rename to naming convention
        self.name = stringcase.camelcase(_ref.name)
        self.json_key = _ref.name
        self.description = _ref.description

        self.type = util.custom_type(_ref.value)
        self.entity_type = util.custom_type_entity(_ref.value) or self.type
        self.pattern = util.custom_type_pattern(_ref.value)
        self.is_array = _ref.is_array

        self.is_required = _ref.is_required
        self.is_read_only = _ref.is_read_only
        self.is_write_only = _ref.is_write_only
        self.is_unique = _ref.is_unique
        self.is_hidden = _ref.is_hidden
        self.is_query = _ref.is_query

        self.is_enum = _ref.value._tx_fqn in ["entity.Enum"]
        self.is_base = _ref.value._tx_fqn in ["entity.Base"]
        self.is_object = _ref.value._tx_fqn in ["entity.Object"]
        self.is_id = _ref.value.name == "ID"
        self.is_date = _ref.value.name in ["Date", "Datetime"]

        # relation model
        self.is_composition = _ref.is_composition
        self.is_aggregation = _ref.is_aggregation
        self.is_relation = self.is_composition or self.is_aggregation

        self.getter = "get" + stringcase.pascalcase(self.name)
        self.setter = "set" + stringcase.pascalcase(self.name)

        self._add_constraints(_ref)

        return self

    def _add_constraints(self, _ref: dsl.Field):
        """Adds min max constraints"""

        if self.type == "String":
            self.min_size = f"{_ref.min_size}" if _ref.min_size else "0"
            self.max_size = f"{_ref.max_size}" if _ref.max_size else "255"

        if self.type == "Integer":
            self.min_size = f"{_ref.min_size}" if _ref.min_size else "0"
            self.max_size = f"{_ref.max_size}" if _ref.max_size else "Integer.MAX_VALUE"

        if self.type == "Long":
            self.min_size = f"{_ref.min_size}" if _ref.min_size else "0"
            self.max_size = f"{_ref.max_size}" if _ref.max_size else "Long.MAX_VALUE"

        # default value is a bit tricky
        if self.is_enum:
            self.default = f"{self.type}.{_ref.default}" if _ref.default else None
        elif self.type == "String":
            self.default = f'"{_ref.default}"' if _ref.default else None
        elif self.type == "Integer":
            self.default = f"{_ref.default}" if _ref.default else None
        elif self.type == "Long":
            self.default = f"{_ref.default}l" if _ref.default else None
        elif self.type == "Float":
            self.default = f"{_ref.default}f" if _ref.default else None
        elif self.type == "Double":
            self.default = f"{_ref.default}d" if _ref.default else None
        elif self.type == "Boolean":
            self.default = "true" if _ref.default.lower() == "true" else "false" if _ref.default else None
        else:
            self.default = f"{_ref.default}" if _ref.default else None


@dataclass
class ModelClass:
    """The Java Model for the Domain Class Object"""

    name: str = None
    namespace: str = None
    description: list[str] = field(default_factory=list)

    is_enum: bool = False
    is_base: bool = False
    is_object: bool = False

    fields: list[ModelField] = field(default_factory=list)
    constants: list[str] = field(default_factory=list)

    # addons
    is_supertype: bool = False
    is_entity: bool = False
    is_aggregated: bool = False
    has_relation: bool = False
    has_required: bool = False
    has_query: bool = False
    has_objectnode: bool = False

    package: spring.Package = None
    imports: dict[str, list[str]] = field(default_factory=dict)

    hibernate: spring.HibernateModelInfo = None

    parents: list[spring.Parent] = field(default_factory=list)

    def build(self, _ref: dsl.Enum | dsl.Base | dsl.Object) -> ModelClass:
        """Init our dataclass by reading information from _ref"""

        # rename to naming convention
        self.name = _ref.name
        self.namespace = stringcase.lowercase(_ref.namespace)

        self.description = _ref.description

        # identify type
        self.is_enum = _ref._tx_fqn in ["entity.Enum"]
        self.is_base = _ref._tx_fqn in ["entity.Base"]
        self.is_object = _ref._tx_fqn in ["entity.Object"]

        # addons
        self.is_supertype = util.is_supertype(_ref) if self.is_base else False
        self.is_entity = util.is_used_as_field_value(_ref)
        self.is_aggregated = util.has(_ref, is_aggregated=True)
        self.has_relation = util.has(_ref, has_relation=True)
        self.has_required = util.has(_ref, has_required_ignore_id=True)
        self.has_query = util.has(_ref, has_query=True)
        self.has_objectnode = util.has(_ref, has_type=["Object"])

        # handle package path and imports
        self.package = spring.Package(util.Store.config)
        package_directive = qutil.get_directive_of_name(Directive.PACKAGE, _ref)

        if package_directive:
            self.package.set_namespace(package_directive.value)

        # add attributes
        self._add_attributes(_ref)
        self._add_constants(_ref)
        self._add_relations(_ref)
        self._add_foreign_keys(_ref)

        return self

    def _add_attributes(self, _ref: dsl.Enum | dsl.Base | dsl.Object):
        """Creates and adds all visible attributes to a ModelClass"""

        # filter on base and object
        if not (self.is_base or self.is_object):
            return

        # filter only non relations
        dsl_fields = [x for x in _ref.fields if not x.is_relation]

        for dsl_field in dsl_fields:
            new_model_field = ModelField().build(dsl_field)

            self.fields.append(new_model_field)

    def _add_constants(self, _ref: dsl.Enum | dsl.Base | dsl.Object):
        """Adds all values for Enums"""

        # filter only enum
        if not self.is_enum:
            return

        for value in _ref.values:
            self.constants.append(value)

    def _add_relations(self, _ref: dsl.Enum | dsl.Base | dsl.Object):
        """Creates and adds all explicit relation attributes to a ModelClass"""

        # filter on object
        if not self.is_object:
            return

        # filter only relations
        dsl_fields = [x for x in _ref.fields if x.is_relation]

        for dsl_field in dsl_fields:
            new_model_field = ModelField().build(dsl_field)
            new_model_field.name = stringcase.camelcase(new_model_field.type)
            new_model_field.name += "s" if new_model_field.is_array else ""

            self.fields.append(new_model_field)

    def _add_foreign_keys(self, _ref: dsl.Enum | dsl.Base | dsl.Object):
        """Creates and adds all implicit relation attributes to a ModelClass"""

        # filter on object
        if not self.is_object:
            return

        # get the fields of all parents that
        # use self as aggregation or composition
        # TODO: add nested Objects
        dsl_fields = util.get_parent_fields(self.name)

        for dsl_field in dsl_fields:
            parent = dsl_field.parent

            # create a new field for self that represents the other side
            # of the reference
            fk_field = dsl.Field()

            # aggregations
            fk_field.name = stringcase.camelcase(parent.name)
            fk_field.name += "s" if dsl_field.is_aggregation else ""

            fk_field.value = parent
            fk_field.is_array = dsl_field.is_aggregation
            fk_field.is_aggregation = dsl_field.is_aggregation
            fk_field.is_composition = dsl_field.is_composition

            new_model_field = ModelField().build(fk_field)
            new_model_field.is_relation_owner = True
            new_model_field.foreign_key_name = dsl_field.name
            new_model_field.foreign_key_is_array = dsl_field.is_array

            self.fields.append(new_model_field)

            # update relation flag because these do not get picked up by the util method
            self.has_relation = True
