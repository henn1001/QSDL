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

"""Generator Utility functions"""

from __future__ import annotations

import qsdl.dsl.models as dsl
import qsdl.dsl.util as qutil

from .config import Config, Directive


class Store:
    """Parsed data storage class"""

    schema: dsl.Schema
    config: Config


custom_types = {
    "Int": "INTEGER",
    "Long": "BIGINT",
    "Float": "REAL",
    "Double": "DOUBLE PRECISION",
    "String": "TEXT",
    "Boolean": "BOOLEAN",
    "ID": "integer",
    "Date": "DATE",
    "Datetime": "TIMESTAMP",
    "Object": "JSONB",
}


def custom_type(entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> str:
    """Converts builtin types to generator specific types."""
    return qutil.map_custom_type(entity, custom_types, entity.name, Directive.TYPE, ["format", "pattern"], "type")
