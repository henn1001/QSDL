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

from qsdl import logger
from qsdl.dsl.processors.model_parser import parse_objects, parse_operations
from qsdl.dsl.processors.model_validator import validate, validate_operations

if TYPE_CHECKING:
    from qsdl.dsl.models import Schema


log = logger.getLogger(__name__)


def model_processor(schema: Schema, metamodel: TextXMetaModel):
    """Callable that will be called after each successful model parse.

    Args:
        schema (Schema): The QSDL schema model.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """

    _ = schema
    _ = metamodel


def model_post_processor(schema: Schema, metamodel: TextXMetaModel):
    """Callable that should be called after the schema has been generated and merged.

    We use this to validate and complete the schema.

    Args:
        schema (Schema): The QSDL schema model.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """

    log.info("running schema validation...")

    # run post validation
    validate(schema, metamodel)

    # adds missing domain related information to all custom operations
    # it is important that this is done before parsing the objects
    parse_operations(schema)

    # creates and adds operations for domain objects to the schema
    parse_objects(schema)

    # validate operation uniqueness
    validate_operations(schema)

    log.info("schema successfully loaded")


def get_all_imports(schema: Schema) -> list:
    """Recursively collect all imports"""

    imports = []

    for imprt in schema.imports:
        loaded_schema: Schema = imprt._tx_loaded_models[0]

        tmp = get_all_imports(loaded_schema)

        imports.extend(tmp)
        imports.append(imprt)

    return imports


def sort_all_imports(imports: list):
    """Remove duplicates in import list"""

    ret = {}

    # loop over all imports and normalize the name to store in dict
    for imprt in imports:
        name = imprt.importURI

        # get last piece via split
        name = name.split("/")[-1].split("\\")[-1]
        ret[name] = imprt

    return ret.values()


def model_merger(schema: Schema):
    """Callable that should be called after the schema has been generated.

    We use this to combine multiple schema files into one.

    Args:
        schema (Schema): The QSDL schema model.
    """

    # iterate over the imports and merge types
    imports = get_all_imports(schema)

    # remove duplicates
    imports = sort_all_imports(imports)

    # down merge all imported types into our main schema
    for imprt in imports:
        loaded_schema: Schema = imprt._tx_loaded_models[0]
        schema.types.extend(loaded_schema.types)
