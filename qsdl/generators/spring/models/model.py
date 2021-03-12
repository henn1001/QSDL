from dataclasses import dataclass, field
from typing import List

import stringcase

from .. import util


@dataclass
class _Attribute:

    # the textx object
    _field: object

    # computed attributes
    name: str = None
    json_key: str = None
    description: str = None
    type: str = None
    is_array: bool = False
    is_model: bool = False
    is_date: bool = False
    is_required: bool = False
    is_read_only: bool = False
    is_write_only: bool = False
    is_nested: bool = False
    is_composition: bool = False
    is_aggregation: bool = False
    is_relation: bool = False
    getter: str = None
    setter: str = None

    def __post_init__(self):

        # rename to naming convention
        self.name = stringcase.camelcase(self._field.name)
        self.json_key = self._field.name
        self.description = self._field.description

        self.type = util.custom_type(self._field.value.name)

        self.is_array = self._field.array
        self.is_model = self._field.value._tx_fqn in ["entity.Base", "entity.Object"]
        self.is_enum = self._field.value._tx_fqn in ["entity.Enum"]
        self.is_date = self._field.value.name == "Date"

        self.is_required = self._field.non_nullable

        self.is_read_only = self._field.readonly
        self.is_write_only = self._field.writeonly

        # relation model
        self.is_nested = self._field.nested
        self.is_composition = self._field.composition
        self.is_aggregation = self._field.aggregation
        self.is_relation = self._field.composition or self._field.aggregation

        self.getter = "get" + stringcase.capitalcase(self.name)
        self.setter = "set" + stringcase.capitalcase(self.name)

        # special case for id references
        if (
            self._field.value._tx_fqn in ["entity.Object"]
            and not self.is_nested
            and not self.is_relation
        ):
            self.type = util.custom_type("ID")
            self.is_model = False


@dataclass
class Model:

    # the textx object
    _entity: object

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

    def __post_init__(self):

        # rename to naming convention
        self.name = util.get_class_name(self._entity.name)

        self.description = self._entity.description

        # identify type
        self.is_enum = self._entity._tx_fqn in ["entity.Enum"]
        self.is_base = self._entity._tx_fqn in ["entity.Base"]
        self.is_object = self._entity._tx_fqn in ["entity.Object"]

        if not self.is_enum and self._entity.supertype:
            self.extends = util.get_class_name(self._entity.supertype.name)

        # attributes
        if not self.is_enum:
            self._add_attributes()
        else:
            self.constants = util.get_enum_values(self._entity)

        # collect imports
        self.imports = util.get_model_imports(self._entity)

    def _add_attributes(self):

        if self._entity._tx_fqn not in ["entity.Base", "entity.Object"]:
            raise ValueError

        for entity_field in self._entity.fields:
            attribute = _Attribute(entity_field)
            self.attributes.append(attribute)
