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

"""Core generation."""

import json
from collections.abc import Mapping
from dataclasses import dataclass, fields
from enum import Enum
from pathlib import Path

import dacite
import inquirer
from pyfiglet import Figlet

from qsdl import logger
from qsdl.artifacts import GeneratedFile, GeneratedFiles
from qsdl.dsl import Schema
from qsdl.dsl.textx import parse_schema
from qsdl.generators import (
    GeneratorConfig,
    GeneratorConfigClass,
    GeneratorDefinition,
    available_generators,
    create_config,
    get_definition,
)
from qsdl.writer import DirectoryWriter

log = logger.getLogger(__name__)


class Color:
    """For printing stuff nicer to console."""

    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


@dataclass(frozen=True, slots=True)
class _PreparedGeneration:
    """The parsed and configured inputs for one generation request."""

    name: str
    definition: GeneratorDefinition
    schema: Schema
    config: GeneratorConfig


def _convert_prompt_answer(field_type: object, value: object) -> object:
    """Convert an interactive answer to its declared dataclass field type."""
    if not isinstance(field_type, type) or not issubclass(field_type, Enum):
        return value
    if isinstance(value, field_type):
        return value

    try:
        return field_type(value)
    except ValueError:
        return field_type[str(value)]


def prompt_user() -> tuple[str, GeneratorConfig]:
    """Prompt for a generator and its request-local configuration."""
    figlet = Figlet(font="speed")

    print(Color.BOLD)
    print(figlet.renderText("QSDL"))
    print("! Would you like a cup of tea with that?")
    print(Color.END)

    questions = [
        inquirer.List(
            "generator",
            message="Which generator do you want to use?",
            choices=available_generators(),
            default="void",
        ),
    ]

    answers = inquirer.prompt(questions)
    generator_name = answers["generator"]
    config = create_config(generator_name)

    questions = []
    for config_field in fields(config):
        value = getattr(config, config_field.name)
        field_type = config_field.type

        if isinstance(value, bool):
            question = inquirer.Confirm(
                config_field.name,
                message="Please select: " + config_field.name,
                default=value,
            )
        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            question = inquirer.List(
                config_field.name,
                message="Please select: " + config_field.name,
                choices=tuple(field_type.__members__),
                default=value,
            )
        else:
            question = inquirer.Text(
                config_field.name,
                message="Please select: " + config_field.name,
                default=value,
            )

        questions.append(question)

    answers = inquirer.prompt(questions)
    for config_field in fields(config):
        if config_field.name in answers:
            value = _convert_prompt_answer(config_field.type, answers[config_field.name])
            setattr(config, config_field.name, value)

    return generator_name, config


def _resolve_config(
    config_class: GeneratorConfigClass,
    config_path: Path | None,
    raw_config: Mapping[str, object] | None,
) -> GeneratorConfig:
    """Create a config from defaults, a config file, and raw overrides."""
    overrides: dict[str, object] = {}

    if config_path is not None:
        config_file = Path(config_path)
        with config_file.open(encoding="utf-8") as json_file:
            file_data = json.load(json_file)
        if not isinstance(file_data, Mapping):
            raise TypeError(f"configuration file root must be a mapping: {config_file}")
        overrides.update(file_data)

    if raw_config is not None:
        if not isinstance(raw_config, Mapping):
            raise TypeError(f"config must be a mapping, got {raw_config!r}")
        overrides.update(raw_config)

    return dacite.from_dict(
        data_class=config_class,
        data=overrides,
        config=dacite.Config(cast=config_class._dactive_casts),
    )


def _prepare(
    generator_name: str,
    *,
    input_path: Path | None,
    raw_schema: str | None,
    config_path: Path | None,
    raw_config: Mapping[str, object] | None,
    config_instance: GeneratorConfig | None = None,
) -> _PreparedGeneration:
    """Resolve a generator request, configure it, and parse its schema once."""
    definition = get_definition(generator_name)
    config = (
        config_instance
        if config_instance is not None
        else _resolve_config(definition.config_class, config_path, raw_config)
    )
    schema = parse_schema(input_path, raw_schema)

    log.info("QSDL Generator: %s", generator_name)
    log.info("QSDL Config: %s", config)

    return _PreparedGeneration(generator_name, definition, schema, config)


def _validate_result(files: object, generator_name: str) -> GeneratedFiles:
    """Validate the artifact collection returned by a generator."""
    if not isinstance(files, GeneratedFiles):
        raise TypeError(f"generator {generator_name!r} returned {files!r}, expected GeneratedFiles")

    for artifact in files:
        if not isinstance(artifact, GeneratedFile):
            raise TypeError(f"generator {generator_name!r} returned an invalid artifact: {artifact!r}")

    return files


def _invoke(prepared: _PreparedGeneration, output_path: Path | None) -> GeneratedFiles:
    """Invoke a generator with its configured destination path."""
    files = prepared.definition.generator(prepared.schema, prepared.config, output_path)
    return _validate_result(files, prepared.name)


def build(
    *,
    generator_name: str,
    input_path: Path | None = None,
    raw_schema: str | None = None,
    config_path: Path | None = None,
    config: Mapping[str, object] | None = None,
) -> GeneratedFiles:
    """Build generator output in memory without materializing it."""
    prepared = _prepare(
        generator_name,
        input_path=input_path,
        raw_schema=raw_schema,
        config_path=config_path,
        raw_config=config,
    )
    return _invoke(prepared, None)


def generate(
    output_path: Path,
    *,
    generator_name: str | None = None,
    input_path: Path | None = None,
    raw_schema: str | None = None,
    config_path: Path | None = None,
    config: Mapping[str, object] | None = None,
) -> None:
    """Build generator output and materialize it below ``output_path``."""
    config_instance = None
    if generator_name is None:
        generator_name, config_instance = prompt_user()

    prepared = _prepare(
        generator_name,
        input_path=input_path,
        raw_schema=raw_schema,
        config_path=config_path,
        raw_config=config,
        config_instance=config_instance,
    )

    log.info("calling generator")
    files = _invoke(prepared, output_path)
    DirectoryWriter(output_path).write(files)
    log.info("all done!")
