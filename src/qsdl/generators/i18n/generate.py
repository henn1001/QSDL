# Copyright (C) 2020 henn1001

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

"""Generator Main entrypoint"""

from collections.abc import Mapping
from pathlib import Path, PurePosixPath

import flatten_json
import stringcase
import yaml

import qsdl.dsl.textx as xtx
from qsdl import dsl
from qsdl.artifacts import GeneratedFile, GeneratedFiles

from .config import Config

type ExistingTranslations = Mapping[PurePosixPath, str]
type Entity = dsl.Base | dsl.Object | dsl.Enum
type YamlOperation = tuple[PurePosixPath, str, tuple[Entity, ...], str, bool, bool]


def dump_to_yaml(obj: dsl.Base | dsl.Object, translate: bool) -> dict:
    """Simple helper to dump all fields to yaml."""
    data = {}

    data["__"] = obj.name if translate else None

    for field in obj.fields:
        if isinstance(field.value, dsl.Object | dsl.Base):
            data[field.name] = dump_to_yaml(field.value, translate)
        elif translate:
            data[field.name] = stringcase.sentencecase(field.name)
        else:
            data[field.name] = None

    return data


def dump_enum_to_yaml(enum: dsl.Enum, translate: bool) -> dict:
    """Simple helper to dump all fields to yaml."""
    data = {}

    for value in enum.values:
        if translate:
            tmp = value.replace("_", " ").lower()
            data[value] = stringcase.capitalcase(tmp)
        else:
            data[value] = None

    return data


def merge_yaml(base_dict: dict | None, new_dict: dict, remove_unused_keys: bool) -> dict | None:
    """Merge generated YAML data with existing translations without side effects."""
    if not base_dict:
        return None

    ret_dict = {}
    base_dict = flatten_json.flatten(base_dict, separator=".")
    new_dict = flatten_json.flatten(new_dict, separator=".")

    if remove_unused_keys:
        for key, value in new_dict.items():
            # if the key exists and is not empty, take value from origin
            if key in base_dict and base_dict[key] is not None:
                ret_dict[key] = base_dict[key]

            # else copy as is
            else:
                ret_dict[key] = value

    else:
        ret_dict = new_dict | base_dict

    ret_dict = flatten_json.unflatten(ret_dict, separator=".")

    return ret_dict


def _validated_path(path: PurePosixPath) -> PurePosixPath:
    """Validate a logical artifact path using the artifact contract."""
    return GeneratedFile(path, "").path


def _output_operations(schema: dsl.Schema, config: Config) -> list[YamlOperation]:
    """Describe the logical YAML writes for a generation request."""
    objects = xtx.get_children_of_object(schema) if config.object else []
    bases = xtx.get_children_of_base(schema) if config.base else []
    enums = xtx.get_children_of_enum(schema) if config.enum else []

    extra_locales = [item.strip() for item in config.extra_locales.split(",")]
    locales = [config.locale, *extra_locales]
    operations: list[YamlOperation] = []

    for locale in locales:
        if not locale:
            continue

        locale_folder = PurePosixPath(locale)
        if config.subfolder:
            locale_folder /= config.subfolder

        if config.split_files:
            for entity in objects + bases + enums:
                output_path = _validated_path(locale_folder / f"{entity.name}.{config.file_extension}")
                operations.append((output_path, locale, (entity,), "", False, False))
        elif config.single_file:
            output_path = _validated_path(PurePosixPath(f"{locale}.{config.file_extension}"))
            if objects or bases:
                operations.append((output_path, locale, tuple(objects + bases), config.single_file_name + ".", True, True))
            if enums:
                operations.append((output_path, locale, tuple(enums), config.single_file_enum_name + ".", True, True))
        else:
            if objects or bases:
                output_path = _validated_path(locale_folder / f"{config.single_file_name}.{config.file_extension}")
                operations.append((output_path, locale, tuple(objects + bases), "", True, True))
            if enums:
                output_path = _validated_path(locale_folder / f"{config.single_file_enum_name}.{config.file_extension}")
                operations.append((output_path, locale, tuple(enums), "", True, True))

    return operations


def _normalise_existing_files(existing_files: ExistingTranslations | None) -> dict[PurePosixPath, str]:
    """Validate and normalize explicitly supplied existing translation files."""
    if existing_files is None:
        return {}
    if not isinstance(existing_files, Mapping):
        raise TypeError(f"existing translation files must be a mapping, got {existing_files!r}")

    normalized: dict[PurePosixPath, str] = {}
    for path, content in existing_files.items():
        if not isinstance(content, str):
            raise TypeError(f"existing translation content must be str, got {content!r}")
        artifact = GeneratedFile(path, content)
        if artifact.path in normalized:
            raise ValueError(f"duplicate existing translation path: {artifact.path.as_posix()!r}")
        normalized[artifact.path] = content

    return normalized


def _entity_data(entity: Entity, locale: str, config: Config) -> dict:
    """Build the new YAML mapping for one schema entity."""
    translate = locale == config.locale
    if isinstance(entity, dsl.Enum):
        return dump_enum_to_yaml(entity, translate)
    return dump_to_yaml(entity, translate)


def _operation_data(entities: tuple[Entity, ...], locale: str, config: Config, append: str, combined: bool) -> dict:
    """Build the new YAML mapping for one logical write operation."""
    if combined:
        return {append + entity.name: _entity_data(entity, locale, config) for entity in entities}
    return _entity_data(entities[0], locale, config)


def _serialize(data: dict | None, sort_keys: bool) -> str:
    """Serialize generated YAML with the generator's existing options."""
    return yaml.dump(data, sort_keys=sort_keys, allow_unicode=True, width=9999)


def _generate_files(
    schema: dsl.Schema,
    config: Config,
    *,
    existing_files: ExistingTranslations | None = None,
) -> GeneratedFiles:
    """Build i18n YAML artifacts in memory."""
    existing = _normalise_existing_files(existing_files)
    pending: dict[PurePosixPath, str] = {}

    for path, locale, entities, append, sort_keys, combined in _output_operations(schema, config):
        output_data = _operation_data(entities, locale, config, append, combined)

        if path in pending:
            yaml_data = yaml.safe_load(pending[path])
            output_data = merge_yaml(yaml_data, output_data, config.remove_unused_keys)
        elif path in existing:
            yaml_data = yaml.safe_load(existing[path])
            output_data = merge_yaml(yaml_data, output_data, config.remove_unused_keys)

        if config.flatten:
            output_data = flatten_json.flatten(output_data, separator=".")

        pending[path] = _serialize(output_data, sort_keys)

    files = GeneratedFiles()
    for path, content in pending.items():
        files.add_text(path, content)
    return files


def _destination_for(root: Path, path: PurePosixPath, resolved_root: Path) -> Path:
    """Safely map a validated logical path below a directory root."""
    path = _validated_path(path)
    destination = root.joinpath(*path.parts)
    resolved_destination = destination.resolve(strict=False)
    if not resolved_destination.is_relative_to(resolved_root):
        raise ValueError(
            f"translation path escapes output root: {path.as_posix()!r} -> "
            f"{destination!s} resolves outside {resolved_root!s}"
        )
    return destination


def build_files_for_directory(schema: dsl.Schema, config: Config, output_root: Path) -> GeneratedFiles:
    """Build i18n artifacts after reading only requested existing translations."""
    root = Path(output_root)
    resolved_root = root.resolve(strict=False)
    existing: dict[PurePosixPath, str] = {}

    requested_paths = {operation[0] for operation in _output_operations(schema, config)}
    for path in sorted(requested_paths, key=lambda item: item.as_posix()):
        destination = _destination_for(root, path, resolved_root)
        if destination.is_file():
            existing[path] = destination.read_text(encoding="utf-8")

    return _generate_files(schema, config, existing_files=existing)


def generate(schema: dsl.Schema, config: Config) -> GeneratedFiles:
    """Generate i18n artifacts without reading an existing destination."""
    return _generate_files(schema, config)
