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

from __future__ import annotations

from pathlib import Path
from typing import List

import pathspec

import qsdl.dsl.textx as xtx
from qsdl.dsl.models import Schema
from qsdl.render import render

from . import util
from .config import Config
from .models import ApiClass, ModelClass


def parse_models(schema: Schema) -> List[ModelClass]:
    """Parse QSDL schema into custom models.

    Args:
        schema (Schema): The QSDL schema model.
    Returns:
        List[ModelClass]: The parsed models.
    """
    models = []

    enum_list = xtx.get_children_of_enum(schema)
    base_list = xtx.get_children_of_base(schema)
    obj_list = xtx.get_children_of_object(schema)

    for entity in enum_list + base_list + obj_list:
        new_model = ModelClass().build(entity)

        # filter unused models
        if new_model.is_used:
            models.append(new_model)

    # add domain parents for each model
    util.add_parents_to_model(models)

    # add hibernate related info to model and fields
    util.add_hibernate_info(models)

    return models


def parse_apis(schema: Schema) -> List[ApiClass]:
    """Parse QSDL schema into custom apis.

    Args:
        schema (Schema): The QSDL schema model.

    Returns:
        List[ApiClass]: The parsed apis.
    """
    apis = []

    api_list = xtx.get_children_of_api(schema)

    for entity in api_list:
        new_api = ApiClass().build(entity)
        apis.append(new_api)

    return apis


def remove_ignored_files(output_path: Path, api_files: list, model_files: list, supporting_files: list):
    """Removes all generated files mentioned in .qsdl-ignore.

    Utilizes the pathspec python package.
    https://github.com/cpburnz/python-path-specification

    Args:
        output_path (Path): [description]
        domain_files (list): [description]
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


def generate_openapi(output_path: Path):
    """Helper that calls the openapi generator.

    Args:
        output_path (Path): The requested destination.
    """
    gen_schema_file = output_path / "src/main/resources/openapi.yaml"
    gen_schema_file.parent.mkdir(exist_ok=True, parents=True)

    import qsdl.core as core  # pylint: disable=import-outside-toplevel
    from qsdl.config import Config as core_config  # pylint: disable=import-outside-toplevel

    core.generate(core_config.raw_schema, gen_schema_file.parent, "openapi")


def generate(schema: Schema, output_path: Path, config: Config):
    """Generator func for spring"""

    if config.id_type not in ["Long", "String"]:
        raise ValueError("id_type must be `Long` or `String`")

    # for development
    if isinstance(config.database, list):
        config.database = "hibernate"

    # sets the id type and schema
    util.custom_types["ID"] = config.id_type
    util.Store.schema = schema
    util.Store.config = config

    base_package = config.group_id.replace(".", "/")

    # parse models and apis
    util.Store.models = models = parse_models(schema)
    apis = parse_apis(schema)

    # loop and generate domain files
    api_files = []

    for api in apis:
        # fmt: off
        api_files.append(("src/main/java/controller/Controller.j2", f"src/main/java/{base_package}/controller/{api.name}Controller.java", api))
        api_files.append(("src/main/java/service/Service.j2", f"src/main/java/{base_package}/service/{api.name}Service.java", api))

        if api.model:
            api_files.append(("src/test/java/controller/DControllerTest.j2", f"src/test/java/{base_package}/controller/{api.name}ControllerTest.java", api))
            api_files.append(("src/test/java/service/ServiceTest.j2", f"src/test/java/{base_package}/service/{api.name}ServiceTest.java", api))

        if api.model and config.database == "hibernate":
            api_files.append(("src/main/java/repository/Repository.j2", f"src/main/java/{base_package}/repository/{api.name}Repository.java", api))
            api_files.append(("src/test/java/repository/RepositoryTest.j2", f"src/test/java/{base_package}/repository/{api.name}RepositoryTest.java", api))
        # fmt: on

    # loop and generate model files
    model_files = []

    for model in models:
        # fmt: off
        model_files.append(("src/main/java/domain/Pojo.j2", f"src/main/java/{base_package}/domain/{model.name}.java", model))
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
        ("src/test/resources/application.properties.j2", "src/test/resources/application.properties"),
        ("src/main/resources/logback-spring.j2", "src/main/resources/logback-spring.xml"),
        ("src/main/resources/public/index.j2", "src/main/resources/public/index.html"),
        ("src/main/resources/public/error/404.j2", "src/main/resources/public/error/404.html"),
        # main
        ("src/main/java/package-info.j2", f"src/main/java/{base_package}/package-info.java"),
        ("src/main/java/SpringBootApp.j2", f"src/main/java/{base_package}/SpringBootApp.java"),
        ("src/test/java/TestConfig.j2", f"src/test/java/{base_package}/TestConfig.java"),
        # config
        ("src/main/java/config/AppConfiguration.j2", f"src/main/java/{base_package}/config/AppConfiguration.java"),
        ("src/main/java/config/AppProperties.j2", f"src/main/java/{base_package}/config/AppProperties.java"),
        ("src/main/java/config/AsyncConfig.j2", f"src/main/java/{base_package}/config/AsyncConfig.java"),
        ("src/main/java/config/SchedulerConfig.j2", f"src/main/java/{base_package}/config/SchedulerConfig.java"),
        ("src/main/java/config/PersistenceConfig.j2", f"src/main/java/{base_package}/config/PersistenceConfig.java"),
        ("src/main/java/config/Errors.j2", f"src/main/java/{base_package}/config/Errors.java"),
        ("src/main/java/config/Constants.j2", f"src/main/java/{base_package}/config/Constants.java"),
        # api
        ("src/main/java/controller/BaseController.j2", f"src/main/java/{base_package}/controller/BaseController.java"),
        ("src/main/java/controller/HomeController.j2", f"src/main/java/{base_package}/controller/HomeController.java"),
        # util
        ("src/main/java/util/Json.j2", f"src/main/java/{base_package}/util/Json.java"),
        ("src/main/java/util/Time.j2", f"src/main/java/{base_package}/util/Time.java"),
        ("src/main/java/util/Validator.j2", f"src/main/java/{base_package}/util/Validator.java"),
        ("src/main/java/util/IdGenerator.j2", f"src/main/java/{base_package}/util/IdGenerator.java"),
        ("src/main/java/util/NodeConverter.j2", f"src/main/java/{base_package}/util/NodeConverter.java"),
        ("src/main/java/util/PredicateBuilder.j2", f"src/main/java/{base_package}/util/PredicateBuilder.java"),
        # exception
        ("src/main/java/exception/AppException.j2", f"src/main/java/{base_package}/exception/AppException.java"),
        ("src/main/java/exception/GlobalExceptionHandler.j2", f"src/main/java/{base_package}/exception/GlobalExceptionHandler.java"),
        # model
        ("src/main/java/model/AppError.j2", f"src/main/java/{base_package}/model/AppError.java"),
        ("src/main/java/model/AppPageable.j2", f"src/main/java/{base_package}/model/AppPageable.java"),
        ("src/main/java/model/AbstractPersistentObject.j2", f"src/main/java/{base_package}/model/AbstractPersistentObject.java"),
        ("src/main/java/model/AbstractPersistentBase.j2", f"src/main/java/{base_package}/model/AbstractPersistentBase.java"),
        ("src/main/java/model/ObjectList.j2", f"src/main/java/{base_package}/model/ObjectList.java"),
        # tests
        ("src/test/java/controller/ControllerTest.j2", f"src/test/java/{base_package}/controller/ControllerTest.java")
    ]
    # fmt: on

    if config.database == "hibernate":
        # fmt: off
        supporting_files.append(("src/main/java/repository/BaseRepository.j2", f"src/main/java/{base_package}/repository/BaseRepository.java"))
        supporting_files.append(("src/main/java/repository/BaseRepositoryImpl.j2", f"src/main/java/{base_package}/repository/BaseRepositoryImpl.java"))
        # fmt: on

    # remove ignored files from generator
    remove_ignored_files(output_path, api_files, model_files, supporting_files)

    # build the render arguments
    context = {
        "title": config.title,
        "group_id": config.group_id,
        "artifact_id": config.artifact_id,
        "base_package": config.group_id,
        "basePath": schema.servers[0] if schema.servers else "/api/v1",
        "database": config.database,
        "encapsulation": config.encapsulation,
    }

    # generate supporting files
    for src, dest in supporting_files:
        output_file = output_path / dest
        template_path = Path(__file__).parent / "template" / src
        macro_path = Path(__file__).parent / "template" / "_macro"
        render(output_file, context, template_path, macro_path=macro_path)

    # generate models
    for src, dest, model in model_files:
        context["model"] = model
        output_file = output_path / dest
        template_path = Path(__file__).parent / "template" / src
        macro_path = Path(__file__).parent / "template" / "_macro"
        render(output_file, context, template_path, macro_path=macro_path)

    # generate apis
    for src, dest, api in api_files:
        context["api"] = api
        context["model"] = api.model
        output_file = output_path / dest
        template_path = Path(__file__).parent / "template" / src
        macro_path = Path(__file__).parent / "template" / "_macro"
        render(output_file, context, template_path, macro_path=macro_path)

    # run openapi generator to create spec file
    generate_openapi(output_path)
