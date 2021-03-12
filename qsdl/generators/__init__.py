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

"""QSDL - Generator interface"""

from pathlib import Path
from typing import Any, Callable

from .graphql import Config as graphql_config
from .graphql import generate as graphql_generator
from .openapi import Config as openapi_config
from .openapi import generate as openapi_generator
from .plantuml import Config as plantuml_config
from .plantuml import generate as plantuml_generator
from .spring import Config as spring_config
from .spring import generate as spring_generator


def get_config(generator: str) -> Any:
    """Returns the config for a specific generator"""
    ret = None

    if generator == "openapi":
        ret = openapi_config()
    elif generator == "graphql":
        ret = graphql_config()
    elif generator == "plantuml":
        ret = plantuml_config()
    elif generator == "spring":
        ret = spring_config()
    else:
        raise Exception("unknown generator")

    return ret


def get_generator(generator: str) -> Callable[[None], None]:
    """Returns a callable generator for a specific generator"""
    ret = None

    if generator == "openapi":
        ret = openapi_generator
    elif generator == "graphql":
        ret = graphql_generator
    elif generator == "plantuml":
        ret = plantuml_generator
    elif generator == "spring":
        ret = spring_generator
    else:
        raise Exception("unknown generator")

    return ret
