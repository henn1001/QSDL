# Copyright 2025 henn1001
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

"""Model Definitions"""

from .api import Api
from .argument import Argument
from .base import Base
from .directive import Directive
from .enum import Enum
from .field import Field
from .object import Object
from .operation import Operation
from .scalar import Scalar
from .schema import Schema

__all__ = [
    "Api",
    "Argument",
    "Base",
    "Directive",
    "Enum",
    "Field",
    "Object",
    "Operation",
    "Scalar",
    "Schema",
]


def all_dsl_models():  # noqa: ANN202
    """Returns all DSL classes.

    Returns:
        list: List of DSL classes.
    """
    return [
        Api,
        Argument,
        Base,
        Directive,
        Enum,
        Field,
        Object,
        Operation,
        Scalar,
        Schema,
    ]
