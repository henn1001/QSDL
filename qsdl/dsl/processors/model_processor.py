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

"""Model post-processor"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textx.metamodel import TextXMetaModel

from qsdl.dsl.processors.model_parser import parse_objects, parse_operations
from qsdl.dsl.processors.model_validator import validate, validate_operations

if TYPE_CHECKING:
    from qsdl.dsl.models import Schema


def model_processor(schema: Schema, metamodel: TextXMetaModel):
    """Callable that will be called after each successful model parse.

    We use this to validate and complete the schema.

    Args:
        schema (Schema): The QSDL schema model.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """

    # run post validation
    validate(schema, metamodel)

    # adds missing domain related information to all custom operations
    # it is important that this is done before parsing the objects
    parse_operations(schema)

    # creates and adds operations for domain objects to the schema
    parse_objects(schema)

    # validate operation uniqueness
    validate_operations(schema)
