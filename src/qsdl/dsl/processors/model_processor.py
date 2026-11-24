# Copyright 2026 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Model post-processor"""

from textx.metamodel import TextXMetaModel

import qsdl.dsl.processors.model_parser as parser
import qsdl.dsl.processors.model_validator as validator
from qsdl import dsl, logger

log = logger.getLogger(__name__)


def model_processor(schema: dsl.Schema, metamodel: TextXMetaModel) -> None:
    """Callable that will be called after each successful model parse.

    Args:
        schema (dsl.Schema): The QSDL schema model.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """

    _ = schema
    _ = metamodel


def model_post_processor(schema: dsl.Schema, metamodel: TextXMetaModel) -> None:
    """Validate and complete the merged schema.

    Args:
        schema (dsl.Schema): The QSDL schema model.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """

    log.info("running schema validation...")

    # Order matters: each stage consumes the model prepared by earlier stages.
    # Resolve inheritance before field-dependent checks, and check reserved names
    # before adding synthetic IDs so those checks see only user declarations.
    validator.validate_declarations(schema, metamodel)
    parser.resolve_fields(schema)
    validator.validate_reserved_words(schema)
    validator.validate_arguments(schema, metamodel)

    # Complete declared operations before CRUD adds its own. CRUD discovery
    # uses the resolved fields rather than just the fields declared locally.
    completed = parser.complete_operations(schema)
    parser.generate_crud(schema)

    # Check uniqueness across both operation sets, including collisions between them.
    validator.validate_operations(schema, completed)
