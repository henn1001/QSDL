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

from pathlib import Path

import flatten_json
import stringcase
import yaml

import qsdl.dsl.models as dsl
import qsdl.dsl.textx as xtx

from .config import Config

_config: Config


def dump_to_yaml(obj: dsl.Object, translate: bool) -> dict:
    """Simple helper to dump all fields to yaml"""
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
    """Simple helper to dump all fields to yaml"""
    data = {}

    for value in enum.values:
        if translate:
            tmp = value.replace("_", " ").lower()
            data[value] = stringcase.capitalcase(tmp)
        else:
            data[value] = None

    return data


def merge_yaml(base_dict: dict, new_dict: dict) -> dict:
    """Simple helper to merge existing yaml data into newly generated ones"""
    if not base_dict:
        return

    ret_dict = {}
    base_dict = flatten_json.flatten(base_dict, separator=".")
    new_dict = flatten_json.flatten(new_dict, separator=".")

    if Config.remove_unused_keys:
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


def create_yaml(entity: dsl.Base | dsl.Object | dsl.Enum, locale: str, locale_folder: str) -> None:
    if not entity:
        return

    output_data = {}

    if not isinstance(entity, dsl.Enum):
        output_data = dump_to_yaml(entity, locale == _config.locale)
    else:
        output_data = dump_enum_to_yaml(entity, locale == _config.locale)

    output_file = locale_folder / f"{entity.name}.{_config.file_extension}"

    # if the yaml already exist, attempt merging
    if output_file.exists():
        with open(output_file, encoding="utf-8") as stream:
            yaml_data = yaml.safe_load(stream)

        output_data = merge_yaml(yaml_data, output_data)

    if _config.flatten:
        output_data = flatten_json.flatten(output_data, separator=".")

    # write dict to file
    with open(output_file, "w", encoding="utf-8") as file:
        yaml.dump(output_data, file, sort_keys=False, allow_unicode=True, width=9999)


def create_yaml_one(
    entities: list[dsl.Base | dsl.Object | dsl.Enum],
    locale: str,
    locale_folder: str,
    filename: str,
    append: str = "",
) -> None:
    if not entities:
        return

    output_data = {}

    for entity in entities:
        if not isinstance(entity, dsl.Enum):
            output_data[append + entity.name] = dump_to_yaml(entity, locale == _config.locale)
        else:
            output_data[append + entity.name] = dump_enum_to_yaml(entity, locale == _config.locale)

    output_file = locale_folder / f"{filename}.{_config.file_extension}"

    # if the yaml already exist, attempt merging
    if output_file.exists():
        with open(output_file, encoding="utf-8") as stream:
            yaml_data = yaml.safe_load(stream)

        output_data = merge_yaml(yaml_data, output_data)

    if _config.flatten:
        output_data = flatten_json.flatten(output_data, separator=".")

    # write dict to file
    with open(output_file, "w", encoding="utf-8") as file:
        yaml.dump(output_data, file, sort_keys=True, allow_unicode=True, width=9999)


def generate(schema: dsl.Schema, output_path: Path, config: Config) -> None:
    """Generator func for that does fancy stuff"""

    global _config
    _config = config

    # convert string to list
    config.extra_locales = [x.strip() for x in config.extra_locales.split(",")]

    objects = xtx.get_children_of_object(schema) if config.object else []
    bases = xtx.get_children_of_base(schema) if config.base else []
    enums = xtx.get_children_of_enum(schema) if config.enum else []

    for locale in [config.locale] + config.extra_locales:
        if not locale:
            continue

        locale_folder = output_path / locale
        locale_folder = locale_folder / config.subfolder if config.subfolder else locale_folder

        if not config.single_file or config.split_files:
            locale_folder.mkdir(exist_ok=True)

        if config.split_files:
            # create a yaml file for each domain object
            for entity in objects + bases + enums:
                create_yaml(entity, locale, locale_folder)
        elif config.single_file:
            create_yaml_one(objects + bases, locale, output_path, locale, append=config.single_file_name + ".")
            create_yaml_one(enums, locale, output_path, locale, append=config.single_file_enum_name + ".")
        else:
            # create one yml file for each type
            create_yaml_one(objects + bases, locale, locale_folder, config.single_file_name)
            create_yaml_one(enums, locale, locale_folder, config.single_file_enum_name)
