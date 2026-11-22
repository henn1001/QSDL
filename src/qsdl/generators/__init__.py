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

"""Generator contract and builtin registry."""

import importlib
import inspect
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, is_dataclass
from pathlib import Path
from typing import Any, ClassVar, get_type_hints

from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import DirectiveSpec, Schema
from qsdl.dsl.processors.directive_parser import validate_directive_specs
from qsdl.exceptions import QsdlException
from qsdl.generators.base_config import BaseConfig

GeneratorConfig = BaseConfig
GeneratorConfigClass = type[BaseConfig]
GeneratorType = Callable[[Schema, GeneratorConfig, Path | None], GeneratedFiles]


class Generator(ABC):
    """Explicit generator plugin contract."""

    config_class: GeneratorConfigClass
    directive_specs: ClassVar[tuple[DirectiveSpec[Any], ...]] = ()

    @abstractmethod
    def generate(self, schema: Schema, config: GeneratorConfig, output_path: Path | None) -> GeneratedFiles:
        """Generate artifacts for ``schema``."""


def validate_generator(plugin: Generator) -> None:
    """Validate the runtime shape and annotations of a generator plugin."""
    if not (
        isinstance(plugin.config_class, type)
        and is_dataclass(plugin.config_class)
        and issubclass(plugin.config_class, BaseConfig)
    ):
        raise TypeError("generator config_class must be a BaseConfig dataclass")
    if not isinstance(plugin.directive_specs, tuple):
        raise TypeError("generator directive_specs must be a tuple")
    validate_directive_specs(plugin.directive_specs)
    signature = inspect.signature(plugin.generate)
    if len(signature.parameters) != 3:
        raise TypeError("generator method must accept exactly schema, config, and output_path")
    hints = get_type_hints(plugin.generate)
    if hints.get("config") is not plugin.config_class:
        raise TypeError("generator method's config annotation must match config_class")
    if hints.get("return") is not GeneratedFiles:
        raise TypeError("generator method must be annotated to return GeneratedFiles")


@dataclass(frozen=True, slots=True)
class GeneratorDefinition:
    """Registered generator plugin."""

    plugin: Generator

    def __post_init__(self) -> None:
        validate_generator(self.plugin)

    @property
    def generator(self) -> GeneratorType:
        """Return the plugin generation method."""
        return self.plugin.generate

    @property
    def directive_specs(self) -> tuple[DirectiveSpec[Any], ...]:
        """Return the plugin's opt-in directive definitions."""
        return self.plugin.directive_specs

    @property
    def config_class(self) -> GeneratorConfigClass:
        """Return the plugin configuration class."""
        return self.plugin.config_class


def _definition_from_module(module: object, source: str) -> GeneratorDefinition:
    plugin = getattr(module, "generator", None)
    if not isinstance(plugin, Generator):
        raise QsdlException(f"generator {source} must export generator: Generator")
    try:
        return GeneratorDefinition(plugin)
    except TypeError as error:
        raise QsdlException(f"generator {source} has an invalid contract: {error}") from error


def load_generators() -> dict[str, GeneratorDefinition]:
    """Load all generators from the generators directory."""
    generators: dict[str, GeneratorDefinition] = {}
    generators_dir = Path(__file__).parent

    for folder in generators_dir.iterdir():
        if folder.is_dir() and (folder / "__init__.py").exists():
            try:
                module = importlib.import_module(f".{folder.name}", package=__name__)
                generators[folder.name] = _definition_from_module(module, folder.name)
            except (ImportError, QsdlException) as error:
                print(f"Error loading module '{folder.name}': {error}", file=sys.stderr)

    return generators


GENERATORS: dict[str, GeneratorDefinition] = load_generators()


def get_definition(generator_name: str) -> GeneratorDefinition:
    """Return a registered generator definition."""
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
    """Return a fresh generator configuration instance."""
    return create_config(generator_name)
