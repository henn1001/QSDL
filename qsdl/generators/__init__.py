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

import importlib
from pathlib import Path
from typing import Callable, Type

from qsdl.dsl.models import Schema
from qsdl.generators.base_config import BaseConfig

ConfigType = Type[BaseConfig]
GeneratorType = Callable[[Schema, Path, ConfigType], None]


def load_generators() -> dict[str, tuple[GeneratorType, BaseConfig]]:
    """Loads all generators from the generators directory."""
    generators = {}

    # Path to the folder containing your generator modules
    generators_dir = Path(__file__).parent

    # Dynamically load modules
    for folder in generators_dir.iterdir():
        if folder.is_dir() and (folder / "__init__.py").exists():
            try:
                # Dynamically import the module
                module = importlib.import_module(f".{folder.name}", package=__name__)

                # Check for required exports
                generate = getattr(module, "generate", None)
                config_class = getattr(module, "Config", None)

                if generate and config_class:
                    # Instantiate the config and add to GENERATORS
                    generators[folder.name] = (generate, config_class())
            except ImportError as e:
                print(f"Error loading module '{folder.name}': {e}")

    return generators


# Initialize the GENERATORS dictionary
GENERATORS = load_generators()


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
