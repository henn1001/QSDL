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
from dataclasses import dataclass
from pathlib import Path

import dacite

from qsdl import logger, plugins
from qsdl.artifacts import GeneratedFile, GeneratedFiles
from qsdl.dsl import Schema
from qsdl.dsl.textx import parse_schema
from qsdl.exceptions import QsdlException
from qsdl.generators import GeneratorConfig, GeneratorDefinition
from qsdl.writer import DirectoryWriter

log = logger.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class _PreparedGeneration:
    """The parsed and configured inputs for one generation request."""

    name: str
    definition: GeneratorDefinition
    schema: Schema
    config: GeneratorConfig


def resolve_config(
    definition: GeneratorDefinition,
    config_path: Path | str | list[Path | str] | tuple[Path | str, ...] | None,
    raw_config: Mapping[str, object] | None,
) -> GeneratorConfig:
    """Create a config from defaults, config files (merged in order), and raw overrides."""
    overrides: dict[str, object] = {}

    paths = (
        [] if config_path is None else list(config_path) if isinstance(config_path, (list, tuple)) else [config_path]
    )
    for entry in paths:
        config_file = Path(entry)
        with config_file.open(encoding="utf-8") as json_file:
            file_data = json.load(json_file)
        if not isinstance(file_data, Mapping):
            raise QsdlException(f"configuration file root must be a mapping: {config_file}")
        overrides.update(file_data)

    if raw_config is not None:
        if not isinstance(raw_config, Mapping):
            raise QsdlException(f"config must be a mapping, got {raw_config!r}")
        overrides.update(raw_config)

    overrides = plugins.apply_overrides(definition, overrides)

    return dacite.from_dict(
        data_class=definition.config_class,
        data=overrides,
        config=dacite.Config(cast=definition.config_class._dactive_casts),
    )


def _prepare(
    generator_ref: str,
    *,
    input_path: Path | None,
    raw_schema: str | None,
    config_path: Path | str | list[Path | str] | tuple[Path | str, ...] | None,
    raw_config: Mapping[str, object] | None,
) -> _PreparedGeneration:
    """Resolve a generator request, configure it, and parse its schema once."""
    generator_name, definition = plugins.resolve(generator_ref)
    config = resolve_config(definition, config_path, raw_config)
    schema = parse_schema(input_path, raw_schema, directive_specs=definition.directive_specs, collect_errors=True)

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
    config_path: Path | str | list[Path | str] | tuple[Path | str, ...] | None = None,
    config: Mapping[str, object] | None = None,
) -> GeneratedFiles:
    """Build generator output in memory without materializing it."""
    if not generator_name:
        raise QsdlException("a generator is required")
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
    config_path: Path | str | list[Path | str] | tuple[Path | str, ...] | None = None,
    config: Mapping[str, object] | None = None,
) -> None:
    """Build generator output and materialize it below ``output_path``."""
    if generator_name is None:
        raise QsdlException("a generator is required")

    prepared = _prepare(
        generator_name,
        input_path=input_path,
        raw_schema=raw_schema,
        config_path=config_path,
        raw_config=config,
    )

    log.info("calling generator")
    files = _invoke(prepared, output_path)
    DirectoryWriter(output_path).write(files)
    log.info("all done!")
