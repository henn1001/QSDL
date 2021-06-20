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

"""Model validation"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Union

from textx import model as xtx
from textx.exceptions import TextXSemanticError
from textx.metamodel import TextXMetaModel

if TYPE_CHECKING:
    from qsdl.dsl.models import Base, Field, Object, Schema


def validate(schema: Schema, metamodel: TextXMetaModel):
    """Check for logical input errors and provide better error messages.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    validate_type_names(schema, metamodel)
    validate_field_id(schema, metamodel)
    validate_parameter_id(schema, metamodel)
    validate_array_id(schema, metamodel)
    validate_reference(schema, metamodel)
    validate_custom_operations_path(schema, metamodel)
    validate_nested_bases(schema, metamodel)


def validate_type_names(schema: Schema, metamodel: TextXMetaModel):
    """Validate the naming convention.

    Expect that NameSpaces, Scalars, Enums, Bases and Objects
    start with a uppercase letter.

    The used regex is ^[A-Z][a-zA-Z]*$"

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    entities = []

    entities.extend(xtx.get_children_of_type("Scalar", schema))
    entities.extend(xtx.get_children_of_type("Enum", schema))
    entities.extend(xtx.get_children_of_type("Base", schema))
    entities.extend(xtx.get_children_of_type("Object", schema))

    for entity in entities:
        if not re.match(r"^[A-Z][a-zA-Z]*$", entity.name):
            msg = f"The type {entity.name} does not conform to the naming convention."
            raise TextXSemanticError(msg, filename=schema._tx_filename)

        if (
            entity._tx_fqn == "entity.Object"
            and entity.namespace
            and not re.match(r"^[A-Z][a-zA-Z]*$", entity.namespace)
        ):
            msg = f"The namespace of type {entity.name} does not conform to the naming convention."
            raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_field_id(schema: Schema, metamodel: TextXMetaModel):
    """Check that Objects only have one normal ID field.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # loop for objects and their supertypes (bases)
    objects = xtx.get_children_of_type("Object", schema)
    objects.extend(xtx.get_children_of_type("Base", schema))

    for obj in objects:
        count = 0
        tmp = obj

        while True:
            # check for multiple IDs
            for field in tmp.fields:
                if field.value.name == "ID":
                    count = count + 1

                # should be moved
                if field.value.name == "Void":
                    msg = f"Invalid Void Field value for Object {obj.name}"
                    raise TextXSemanticError(msg, filename=schema._tx_filename)

            if tmp.supertype:
                tmp = tmp.supertype
            else:
                break

        if count > 1:
            msg = f"More than one ID found for Object {obj.name}"
            raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_parameter_id(schema: Schema, metamodel: TextXMetaModel):
    """Check that Fields only have one normal ID parameter.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # loop for custom queries and mutations
    fields = xtx.get_children_of_type("Field", schema)

    for field in fields:
        count = 0

        # check for multiple IDs
        for argument in field.arguments:
            if argument.value.name == "ID":
                count = count + 1

        if count > 1:
            msg = f"More than one ID found for Operation {field.name}"
            raise TextXSemanticError(msg, filename=schema._tx_filename)

        # check for multiple refs or mix
        count = 0
        is_ref = False

        for argument in field.arguments:
            if argument.value.name != "ID":
                count = count + 1

                if argument.value._tx_fqn in ["entity.Object", "entity.Base"]:
                    is_ref = True

        if is_ref and count > 1:
            msg = (
                f"The Operation {field.name} references more than one Object "
                "or tries to mix them. Currently not supported"
            )
            raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_array_id(schema: Schema, metamodel: TextXMetaModel):
    """Check that Fields only have one normal ID parameter.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    fields = xtx.get_children_of_type("Field", schema)

    for field in fields:
        if field.parent._tx_fqn in ["entity.Object", "entity.Base"]:

            if field.value.name == "ID" and field.array:
                msg = f"Array ID found for the field {field.name}."
                raise TextXSemanticError(msg, filename=schema._tx_filename)

        for argument in field.arguments:

            if argument.value.name == "ID" and argument.array:
                msg = f"Array ID found for argument {argument.name}"
                raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_reference(schema: Schema, metamodel: TextXMetaModel):
    """Check that referenced objects use a ID.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    entities = xtx.get_children_of_type("Object", schema)
    for ent in entities:
        if (has_aggregation(ent) and not get_id(ent)) or (has_composition(ent) and not get_id(ent)):
            msg = f"The type {ent.name} specifies a composition or aggregation but no ID value."
            raise TextXSemanticError(msg, filename=schema._tx_filename)

        fields = list(
            filter(
                lambda x: x.value._tx_fqn == "entity.Object"
                and (not x.nested and not x.composition and not x.aggregation),
                ent.fields,
            )
        )

        for field in fields:
            if not get_id(field.value):
                msg = f"The field {field.name} of type {ent.name} references a type with no ID."
                raise TextXSemanticError(msg, filename=schema._tx_filename)

    entities = xtx.get_children_of_type("Base", schema)
    for ent in entities:
        if (has_aggregation(ent) and not get_id(ent)) or (has_composition(ent) and not get_id(ent)):
            msg = f"The base {ent.name} specifies a composition or aggregation but no ID value."
            raise TextXSemanticError(msg, filename=schema._tx_filename)

        fields = list(
            filter(
                lambda x: x.value._tx_fqn == "entity.Object"
                and (not x.nested and not x.composition and not x.aggregation),
                ent.fields,
            )
        )

        for field in fields:
            if not get_id(field.value):
                msg = f"The field {field.name} of base {ent.name} references a type with no ID."
                raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_custom_operations_path(schema: Schema, metamodel: TextXMetaModel):
    """Check that custom operations specify a path.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # get all queries who do not belong to objects
    operations = xtx.get_children_of_type("Operation", schema)
    operations = list(filter(lambda x: x.parent._tx_fqn != "entity.Object", operations))

    for operation in operations:
        for field in operation.fields:
            if not field.path:
                msg = f"The custom Operation {field.name} needs to specify a path."
                raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_nested_bases(schema: Schema, metamodel: TextXMetaModel):
    """Check that used bases are declared as nested.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    bases = xtx.get_children_of_type("Base", schema)

    for base in bases:
        for field in xtx.get_children_of_type("Field", schema):
            if field.parent._tx_fqn in ["entity.Object", "entity.Base"] and field.value == base:
                if not field.nested:
                    msg = f"The Base {base.name} is used but is not declared as nested."
                    raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_operations(schema: Schema):
    """Checks if we have any duplicate operation names or paths.

    Args:
        schema (Schema): The parsed schema definition.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    names = []
    paths = []

    operations = xtx.get_children_of_type("Operation", schema)

    for operation in operations:
        for field in operation.fields:
            names.append(field.name)
            paths.append(field.method + field.path)

    if len(names) != len(set(names)):
        msg = "Duplicate operation names found."
        raise TextXSemanticError(msg, filename=schema._tx_filename)

    if len(paths) != len(set(paths)):
        msg = "Duplicate operation paths found."
        raise TextXSemanticError(msg, filename=schema._tx_filename)


def get_id(entity: Union[Base, Object, Field]) -> str:
    """Returns the name of the ID of a Objects, Queries or Mutations.

    Args:
        entity (object): Either entity.Object or entity.Field.

    Returns:
        str: The name of the ID. None if no ID is found.
    """
    field_entity_name = None

    if entity._tx_fqn == "entity.Object" or entity._tx_fqn == "entity.Base":

        if entity.supertype:
            field_entity_name = get_id(entity.supertype)

        for field in entity.fields:
            if field.value.name == "ID":
                return field.name

    if entity._tx_fqn == "entity.Field":

        for argument in entity.arguments:
            if argument.value.name == "ID":
                return argument.name

    return field_entity_name


def has_composition(obj: Object) -> bool:
    """Checks if the object has any composition.

    Args:
        obj (object): entity.Object

    Returns:
        bool: Returns true for any composition.
    """
    ret = False

    for field in obj.fields:
        if field.composition and field.value._tx_fqn == "entity.Object":
            ret = True
            break

    return ret


def has_aggregation(obj: Object) -> bool:
    """Checks if the object has any aggregation.

    Args:
        obj (object): entity.Object

    Returns:
        bool: Returns true for any aggregation.
    """
    ret = False

    for field in obj.fields:
        if field.aggregation and field.value._tx_fqn == "entity.Object":
            ret = True
            break

    return ret
