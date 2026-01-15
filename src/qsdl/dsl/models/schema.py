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

"""Schema class"""

from __future__ import annotations

from dataclasses import dataclass, field

from qsdl import dsl


@dataclass
class Schema:
    """textX Schema class"""

    # defined in entity.tx
    imports: list[any] = field(default_factory=list)
    title: str | None = None
    version: str | None = None
    description: list[str] = field(default_factory=list)
    servers: list[str] = field(default_factory=list)
    types: list[dsl.Scalar | dsl.Enum | dsl.Base | dsl.Api | dsl.Object] = field(default_factory=list)

    # required by textX
    _tx_filename: str = ""
    _tx_fqn: str = "entity.Schema"
