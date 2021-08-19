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
from typing import TYPE_CHECKING

from textx import model as xtx
from textx.exceptions import TextXSemanticError

if TYPE_CHECKING:
    from textx.metamodel import TextXMetaModel

    from qsdl.dsl.models import Schema


def validate(schema: Schema, metamodel: TextXMetaModel):
    """Check for logical input errors and provide better error messages.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    validate_type_names(schema, metamodel)
    validate_arguments(schema, metamodel)
    validate_custom_operations_path(schema, metamodel)
    validate_field_directives(schema, metamodel)


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
            msg = f"The {entity._tx_fqn} {entity.name} does not conform to the naming convention."
            raise TextXSemanticError(msg, filename=schema._tx_filename)

        if (
            entity._tx_fqn == "entity.Object"
            and entity.namespace
            and not re.match(r"^[A-Z][a-zA-Z]*$", entity.namespace)
        ):
            msg = f"The namespace of {entity._tx_fqn} {entity.name} does not conform to the naming convention."
            raise TextXSemanticError(msg, filename=schema._tx_filename)

        if entity.name.upper() == "ID":
            msg = f"The {entity._tx_fqn} {entity.name} uses the reserved name ID."
            raise TextXSemanticError(msg, filename=schema._tx_filename)

    entities = []

    entities.extend(xtx.get_children_of_type("Field", schema))
    entities.extend(xtx.get_children_of_type("Argument", schema))

    for entity in entities:

        if entity.name.lower() == "id":
            msg = f"The {entity._tx_fqn} {entity.name} uses the reserved name ID."
            raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_arguments(schema: Schema, metamodel: TextXMetaModel):
    """Check that reference a maximum of one Object or Base.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # loop for custom operations
    operations = xtx.get_children_of_type("Operation", schema)

    for operation in operations:
        count = 0
        is_ref = False

        for argument in operation.arguments:
            count = count + 1

            if argument.value._tx_fqn in ["entity.Object", "entity.Base"]:
                is_ref = True

        if is_ref and count > 1:
            msg = (
                f"The Operation {operation.name} references more than one Object "
                "or tries to mix them. Currently not supported"
            )
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

    # loop for custom operations
    operations = xtx.get_children_of_type("Operation", schema)

    for operation in operations:
        if not operation.path:
            msg = f"The custom Operation {operation.name} needs to specify a path."
            raise TextXSemanticError(msg, filename=schema._tx_filename)


def validate_field_directives(schema: Schema, metamodel: TextXMetaModel):
    """Checks various rules that apply to field directives.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    bases = xtx.get_children_of_type("Base", schema)
    objects = xtx.get_children_of_type("Object", schema)

    for entity in bases + objects:
        for field in entity.fields:

            # verify that queries are only used on scalars
            if field.is_query and not field.value._tx_fqn == "entity.Scalar":
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as query."
                raise TextXSemanticError(msg, filename=schema._tx_filename)

            # verify that composition is used only on Objects
            if field.is_composition and not field.value._tx_fqn == "entity.Object":
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as composition."
                raise TextXSemanticError(msg, filename=schema._tx_filename)

            # verify that aggregation is used only on Objects and array
            if field.is_aggregation and not field.value._tx_fqn == "entity.Object":
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as aggregation."
                raise TextXSemanticError(msg, filename=schema._tx_filename)

            if field.is_aggregation and not field.is_array:
                msg = f"The Field {field.name} for {field.parent.name} declares a invalid value as aggregation."
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
        names.append(operation.name)
        paths.append(operation.method + operation.path)

    if len(names) != len(set(names)):
        msg = "Duplicate operation names found."
        raise TextXSemanticError(msg, filename=schema._tx_filename)

    if len(paths) != len(set(paths)):
        msg = "Duplicate operation paths found."
        raise TextXSemanticError(msg, filename=schema._tx_filename)
