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

"""Spring Generator"""

from pathlib import Path
from typing import List

import pathspec
from textx import model as xtx

from qsdl.dsl.models import Field, Object, Scalar, Schema
from qsdl.render import render

from . import util
from .config import Config
from .models import Api, Model


def parse_apis(schema: Schema) -> List[Api]:
    """Parse QSDL schema into custom API model.

    Args:
        schema (Schema): The QSDL schema model.

    Returns:
        List[Api]: A list of custom API models.
    """
    apis = []

    entities = xtx.get_children_of_type("Api", schema)

    for entity in entities:
        new_api = Api(entity)
        apis.append(new_api)

    return apis


def parse_models(schema: Schema) -> List[Model]:
    """Parse QSDL schema into custom models.

    Args:
        schema (Schema): The QSDL schema model.
    Returns:
        List[Model]: The parsed models.
    """
    models = []

    enum_list = xtx.get_children_of_type("Enum", schema)
    base_list = xtx.get_children_of_type("Base", schema)
    object_list = xtx.get_children_of_type("Object", schema)

    for obj in enum_list + base_list:
        model = Model(obj)
        models.append(model)

    for obj in object_list:
        model = Model(obj)
        models.append(model)

        # add paging response for all objects with default CRUD endpoints
        if obj.is_crud:
            model = get_paginated_object(obj, model)
            model.is_crud = False
            models.insert(-1, model)

    return models


def get_paginated_object(obj: Object, model: Model) -> Model:
    """Returns a pagable custom model that is used to return a given model.

    Args:
        obj (Object): The QSDL Object.
        model (Model): The custom Model.

    Returns:
        Model: The pagable custom model.
    """

    # represents the model
    new_object = Object()
    new_object.name = model.name + "List"
    new_object._tx_fqn = "entity.Object"

    # contains the item list of the entity
    item_field = Field()
    item_field.name = "items"
    item_field.is_array = True
    item_field.is_required = True
    item_field.is_nested = True
    item_field.value = obj
    item_field._tx_fqn = "entity.Field"
    new_object.fields.append(item_field)

    # next cursor
    cursor_field = Field(name="next_cursor")
    string_scalar = Scalar(name="String")
    string_scalar._tx_fqn = "entity.Scalar"
    cursor_field.value = string_scalar
    cursor_field._tx_fqn = "entity.Field"
    new_object.fields.append(cursor_field)

    # total count
    count_field = Field(name="total_count")
    long_scalar = Scalar(name="Long")
    long_scalar._tx_fqn = "entity.Scalar"
    count_field.value = long_scalar
    count_field._tx_fqn = "entity.Field"
    new_object.fields.append(count_field)

    # init the new model class
    model = Model(new_object)
    model.is_pagination = True

    return model


def remove_ignored_files(output_path: Path, api_files: list, model_files: list, supporting_files: list):
    """Removes all generated files mentioned in .qsdl-ignore.

    Utilizes the pathspec python package.
    https://github.com/cpburnz/python-path-specification

    Args:
        api_files (list): [description]
        model_files (list): [description]
        supporting_files (list): [description]
    """
    ignorefile_path = output_path / ".qsdl-ignore"

    if ignorefile_path.is_file():
        supporting_files.remove((".qsdl-ignore.j2", ".qsdl-ignore"))

        # read the spec
        with open(ignorefile_path, "r") as infile:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", infile)

        # loop over each all files and remove matches
        # note the copy() - we dont want to modify the list directly
        for src, dest, _ in api_files.copy():
            if spec.match_file(output_path / dest):
                api_files.remove((src, dest, _))

        for src, dest, _ in model_files.copy():
            if spec.match_file(output_path / dest):
                model_files.remove((src, dest, _))

        for src, dest in supporting_files.copy():
            if spec.match_file(output_path / dest):
                supporting_files.remove((src, dest))


def generate(schema: Schema, output_path: Path, config: Config):
    """Generator func for spring"""

    if config.id_type not in ["Long", "String"]:
        raise ValueError("id_type must be `Long` or `String`")

    # sets the id type and schema
    util.custom_types["ID"] = config.id_type
    util.schema = schema

    base_package = config.group_id.replace(".", "/")

    # for development
    if isinstance(config.database, list):
        config.database = "hibernate"

    # loop and generate api files
    api_files = []

    for api in parse_apis(schema):
        # fmt: off
        api_files.append(("src/main/java/api/Controller.j2", f"src/main/java/{base_package}/api/{api.name}Controller.java", api))
        api_files.append(("src/main/java/api/Service.j2", f"src/main/java/{base_package}/service/{api.name}Service.java", api))
        if config.database == "hibernate" and api.domain_object :
            api_files.append(("src/main/java/repository/Repository.j2", f"src/main/java/{base_package}/repository/{api.name}Repository.java", api))
        # fmt: on

    # loop and generate model_files
    model_files = []

    for model in parse_models(schema):
        # fmt: off
        model_files.append(("src/main/java/model/Pojo.j2", f"src/main/java/{base_package}/model/{model.name}.java", model))
        # fmt: on

    # fmt: off
    supporting_files = [
        # root
        ("pom.j2", "pom.xml"),
        ("README.j2", "README.md"),
        (".qsdl-ignore.j2", ".qsdl-ignore"),
        (".gitignore.j2", ".gitignore"),
        # vscode
        (".vscode/eclipse-java-google-style.j2", ".vscode/eclipse-java-google-style.xml"),
        (".vscode/settings.j2", ".vscode/settings.json"),
        # resources
        ("src/main/resources/application.properties.j2", "src/main/resources/application.properties"),
        ("src/main/resources/logback-spring.j2", "src/main/resources/logback-spring.xml"),
        ("src/main/resources/public/index.j2", "src/main/resources/public/index.html"),
        ("src/main/resources/public/error/404.j2", "src/main/resources/public/error/404.html"),
        # main
        ("src/main/java/package-info.j2", f"src/main/java/{base_package}/package-info.java"),
        ("src/main/java/SpringBootApp.j2", f"src/main/java/{base_package}/SpringBootApp.java"),
        # config
        ("src/main/java/config/ApplicationConfig.j2", f"src/main/java/{base_package}/config/ApplicationConfig.java"),
        ("src/main/java/config/ApplicationProperties.j2", f"src/main/java/{base_package}/config/ApplicationProperties.java"),
        ("src/main/java/config/AsyncConfig.j2", f"src/main/java/{base_package}/config/AsyncConfig.java"),
        ("src/main/java/config/SchedulerConfig.j2", f"src/main/java/{base_package}/config/SchedulerConfig.java"),
        ("src/main/java/config/HomeController.j2", f"src/main/java/{base_package}/config/HomeController.java"),
        # constants
        ("src/main/java/constant/AppError.j2", f"src/main/java/{base_package}/constant/AppError.java"),
        ("src/main/java/constant/Constants.j2", f"src/main/java/{base_package}/constant/Constants.java"),
        # util
        ("src/main/java/util/Json.j2", f"src/main/java/{base_package}/util/Json.java"),
        ("src/main/java/util/Time.j2", f"src/main/java/{base_package}/util/Time.java"),
        ("src/main/java/util/Validator.j2", f"src/main/java/{base_package}/util/Validator.java"),
        ("src/main/java/util/IdGenerator.j2", f"src/main/java/{base_package}/util/IdGenerator.java"),
        # exception
        ("src/main/java/exception/ApiException.j2", f"src/main/java/{base_package}/exception/ApiException.java"),
        ("src/main/java/exception/GlobalExceptionHandler.j2", f"src/main/java/{base_package}/exception/GlobalExceptionHandler.java"),
        # model
        ("src/main/java/model/ApiError.j2", f"src/main/java/{base_package}/model/ApiError.java"),
        ("src/main/java/model/ApiPageable.j2", f"src/main/java/{base_package}/model/ApiPageable.java"),
        ("src/main/java/model/AbstractPersistentObject.j2", f"src/main/java/{base_package}/model/AbstractPersistentObject.java"),
    ]
    # fmt: on

    # remove ignored files from generator
    remove_ignored_files(output_path, api_files, model_files, supporting_files)

    # build the render arguments
    context = {
        "title": config.title,
        "group_id": config.group_id,
        "artifact_id": config.artifact_id,
        "base_package": config.group_id,
        "basePath": "/v1",
        "database": config.database,
        "util": util,
    }

    # generate supporting files
    for src, dest in supporting_files:
        output_file = output_path / dest
        template_path = Path(__file__).parent / "template" / src
        render(output_file, context, template_path)

    # generate models
    for src, dest, model in model_files:
        context["model"] = model
        output_file = output_path / dest
        template_path = Path(__file__).parent / "template" / src
        render(output_file, context, template_path)

    # generate apis
    for src, dest, api in api_files:
        context["api"] = api
        output_file = output_path / dest
        template_path = Path(__file__).parent / "template" / src
        render(output_file, context, template_path)

    # copy spec
    gen_schema_file = output_path / "src/main/resources/openapi.yaml"
    gen_schema_file.parent.mkdir(exist_ok=True, parents=True)

    import qsdl.core as core # pylint: disable=import-outside-toplevel
    from qsdl.config import Config as core_config # pylint: disable=import-outside-toplevel
    core.generate(core_config.raw_schema, gen_schema_file.parent, "openapi")
