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

"""Schema post-processor"""

from textx import model as xtx
from textx.metamodel import TextXMetaModel

from qsdl.dsl.models import Schema

from .validate import validate


def schema_processor(schema: Schema, metamodel: TextXMetaModel):
    """Callable that will be called after each successful model parse.

    We use this to validate and enrich the schema.

    Args:
        schema (Schema): The parsed schema definition.
        metamodel (TextXMetaModel): The metamodel.

    Raises:
        TextXSemanticError: Exception for logical errors.
    """

    validate(schema, metamodel)
