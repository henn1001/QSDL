# Copyright (C) 2022 henn1001

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
from typing import Callable, Union

from qsdl.dsl.models import Schema

from .graphql import Config as GraphqlConfig
from .graphql import generate as graphql_generator
from .openapi import Config as OpenapiConfig
from .openapi import generate as openapi_generator
from .plantuml import Config as PlantumlConfig
from .plantuml import generate as plantuml_generator
from .spring import Config as SpringConfig
from .spring import generate as spring_generator
from .void import Config as VoidConfig
from .void import generate as void_generator

ConfigType = Union[GraphqlConfig, OpenapiConfig, PlantumlConfig, SpringConfig]
GeneratorType = Callable[[Schema, Path, ConfigType], None]


GENERATORS = {
    "openapi": (openapi_generator, OpenapiConfig()),
    "graphql": (graphql_generator, GraphqlConfig()),
    "plantuml": (plantuml_generator, PlantumlConfig()),
    "spring": (spring_generator, SpringConfig()),
    "void": (void_generator, VoidConfig()),
}


def get_generator(generator_name: str) -> GeneratorType:
    """Returns a callable generator for a specific generator

    Args:
        generator_name (str): The requested generator.

    Raises:
        Exception: For unknown generators.

    Returns:
        GeneratorType: The generator config class.
    """
    if generator_name not in GENERATORS:
        raise Exception("unknown generator")

    return GENERATORS.get(generator_name)[0]


def get_config(generator_name: str) -> ConfigType:
    """Returns the config for a specific generator

    Args:
        generator_name (str): The requested generator.

    Raises:
        Exception: For unknown generators.

    Returns:
        ConfigType: The generator config class.
    """
    if generator_name not in GENERATORS:
        raise Exception("unknown generator")

    return GENERATORS.get(generator_name)[1]
