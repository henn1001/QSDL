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

"""QSDL - Generator interface"""

import importlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import Schema
from qsdl.exceptions import QsdlException
from qsdl.generators.base_config import BaseConfig

GeneratorConfig = BaseConfig
GeneratorConfigClass = type[BaseConfig]
GeneratorType = Callable[[Schema, GeneratorConfig], GeneratedFiles]
DirectoryGeneratorType = Callable[[Schema, GeneratorConfig, Path], GeneratedFiles]


@dataclass(frozen=True, slots=True)
class GeneratorDefinition:
    """Registered generator and the class used to configure it."""

    generator: GeneratorType
    config_class: GeneratorConfigClass
    directory_generator: DirectoryGeneratorType | None = None


def load_generators() -> dict[str, GeneratorDefinition]:
    """Load all generators from the generators directory."""
    generators: dict[str, GeneratorDefinition] = {}

    generators_dir = Path(__file__).parent

    for folder in generators_dir.iterdir():
        if folder.is_dir() and (folder / "__init__.py").exists():
            try:
                module = importlib.import_module(f".{folder.name}", package=__name__)

                generate = getattr(module, "generate", None)
                config_class = getattr(module, "Config", None)
                directory_generator = (
                    getattr(module, "build_files_for_directory", None) if folder.name == "i18n" else None
                )

                if generate and config_class:
                    generators[folder.name] = GeneratorDefinition(
                        generator=generate,
                        config_class=config_class,
                        directory_generator=directory_generator,
                    )
            except ImportError as error:
                print(f"Error loading module '{folder.name}': {error}")

    return generators


GENERATORS: dict[str, GeneratorDefinition] = load_generators()


def get_definition(generator_name: str) -> GeneratorDefinition:
    """Return the definition for a registered generator."""
    if generator_name not in GENERATORS:
        raise QsdlException(f"unknown generator: {generator_name}")
    return GENERATORS[generator_name]


def get_generator(generator_name: str) -> GeneratorType:
    """Return a registered generator callable."""
    return get_definition(generator_name).generator


def get_config_class(generator_name: str) -> GeneratorConfigClass:
    """Return the configuration class for a registered generator."""
    return get_definition(generator_name).config_class


def create_config(generator_name: str) -> GeneratorConfig:
    """Create a fresh configuration instance for a registered generator."""
    return get_config_class(generator_name)()


def available_generators() -> tuple[str, ...]:
    """Return registered generator names in deterministic order."""
    return tuple(sorted(GENERATORS))


def get_config(generator_name: str) -> GeneratorConfig:
    """Return a fresh generator configuration instance.

    This compatibility name is retained for callers of the previous registry
    API.  Configurations are never stored in the registry.
    """
    return create_config(generator_name)
