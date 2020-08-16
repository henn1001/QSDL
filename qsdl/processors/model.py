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

"""Model pre-processor"""

import re

from textx import model as mfunc
from textx.metamodel import TextXMetaModel
from textx.exceptions import TextXSemanticError


from qsdl.util import get_id
from qsdl.util import has_composition
from qsdl.util import has_aggregation


def model_processor(model: object, metamodel: TextXMetaModel):
    """Check for logical input errors and provide better error messages.

    Args:
        model (object): The python object graph.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    validate_type_names(model, metamodel)
    validate_field_id(model, metamodel)
    validate_parameter_id(model, metamodel)
    validate_reference(model, metamodel)
    validate_custom_operations(model, metamodel)
    validate_nested_bases(model, metamodel)


def validate_type_names(model: object, metamodel: TextXMetaModel):
    """Validate the naming convention.

    Expect that NameSpaces, Scalars, Enums, Bases and Objects
    start with a uppercase letter.

    The used regex is ^[A-Z][a-zA-Z]*$"

    Args:
        model (object): The python object graph.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    entities = []

    entities.extend(mfunc.get_children_of_type("Scalar", model))
    entities.extend(mfunc.get_children_of_type("Enum", model))
    entities.extend(mfunc.get_children_of_type("Base", model))
    entities.extend(mfunc.get_children_of_type("Object", model))

    for entity in entities:
        if not re.match(r"^[A-Z][a-zA-Z]*$", entity.name):
            msg = f"The type {entity.name} does not conform to the naming convention."
            raise TextXSemanticError(msg, filename=model._tx_filename)

        if (
            entity._tx_fqn == "entity.Object"
            and entity.namespace
            and not re.match(r"^[A-Z][a-zA-Z]*$", entity.namespace)
        ):
            msg = f"The namespace of type {entity.name} does not conform to the naming convention."
            raise TextXSemanticError(msg, filename=model._tx_filename)


def validate_field_id(model: object, metamodel: TextXMetaModel):
    """Check that Objects only have one normal ID field.

    Args:
        model (object): The python object graph.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # loop for objects and their supertypes (bases)
    objects = mfunc.get_children_of_type("Object", model)

    for obj in objects:
        count = 0
        tmp = obj

        while True:
            # check for multiple IDs
            for field in tmp.fields:
                if field.value.name == "ID":
                    count = count + 1

                    if field.array:
                        msg = f"Array ID found for Object {obj.name}"
                        raise TextXSemanticError(msg, filename=model._tx_filename)

            if tmp.superType:
                tmp = tmp.superType
            else:
                break

        if count > 1:
            msg = f"More than one ID found for Object {obj.name}"
            raise TextXSemanticError(msg, filename=model._tx_filename)


def validate_parameter_id(model: object, metamodel: TextXMetaModel):
    """Check that Fields only have one normal ID parameter.

    Args:
        model (object): The python object graph.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # loop for custom queries and mutations
    fields = mfunc.get_children_of_type("Field", model)

    for field in fields:
        count = 0

        # check for multiple IDs
        for argument in field.arguments:
            if argument.value.name == "ID":
                count = count + 1

                if argument.array:
                    msg = f"Array ID found for Object {field.name}"
                    raise TextXSemanticError(msg, filename=model._tx_filename)

        if count > 1:
            msg = f"More than one ID found for Operation {field.name}"
            raise TextXSemanticError(msg, filename=model._tx_filename)

        # check for multiple refs or mix
        count = 0
        is_ref = False

        for argument in field.arguments:
            if argument.value.name != "ID":
                count = count + 1

                if argument.value._tx_fqn == "entity.Object":
                    is_ref = True

        if is_ref and count > 1:
            msg = (
                f"The Operation {field.name} references more than one Object "
                "or tries to mix them. Currently not supported"
            )
            raise TextXSemanticError(msg, filename=model._tx_filename)


def validate_reference(model: object, metamodel: TextXMetaModel):
    """Check that referenced objects use a ID.

    Args:
        model (object): The python object graph.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    objects = mfunc.get_children_of_type("Object", model)
    for obj in objects:
        if (has_aggregation(obj) and not get_id(obj)) or (has_composition(obj) and not get_id(obj)):
            msg = f"The type {obj.name} specifies a composition or aggregation but no ID value."
            raise TextXSemanticError(msg, filename=model._tx_filename)


def validate_custom_operations(model: object, metamodel: TextXMetaModel):
    """Check that custom queries and mutations specify a path.

    Args:
        model (object): The python object graph.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    # get all queries who do not belong to objects
    operations = mfunc.get_children_of_type("Operation", model)
    operations = list(filter(lambda x: x.parent._tx_fqn != "entity.Object", operations))

    for operation in operations:
        for field in operation.fields:
            if not field.path:
                msg = f"The custom Operation {field.name} needs to specify a path."
                raise TextXSemanticError(msg, filename=model._tx_filename)


def validate_nested_bases(model: object, metamodel: TextXMetaModel):
    """Check that used bases are declared as nested.

    Args:
        model (object): The python object graph.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """
    _ = metamodel

    bases = mfunc.get_children_of_type("Base", model)

    for base in bases:
        for field in mfunc.get_children_of_type("Field", model):
            if field.parent._tx_fqn == "entity.Object" and  field.value == base:
                if not field.nested:
                    msg = f"The Base {base.name} is used but is not declared as nested."
                    raise TextXSemanticError(msg, filename=model._tx_filename)
