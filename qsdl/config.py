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

"""Global QSDL Configuration"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from qsdl.dsl.models import Schema

if TYPE_CHECKING:
    from qsdl.generators import ConfigType


class Config:
    """A configuration class that holds relevant data for QSDL"""

    # the unparsed schema definition
    raw_schema: str = None

    # the parsed schema definition.
    schema: Schema = None

    # path to a output folder
    output_path: Path = None

    # the used generator
    generator: Callable = None

    # Generator specific parameters
    config: ConfigType = None

    # All registered generators
    available_generators: str = ["openapi", "graphql", "plantuml", "spring"]
