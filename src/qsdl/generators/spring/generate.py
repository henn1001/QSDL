# Copyright 2025 henn1001
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

"""Generator Main entrypoint"""

from __future__ import annotations

from pathlib import Path

import pathspec

import qsdl.dsl.textx as xtx
from qsdl.dsl.models import Schema
from qsdl.render import render

from . import import_resolver as resolver
from . import util
from .config import IDTYPE, Config
from .models import ApiClass, ModelClass, Package


def parse_apis(schema: Schema) -> list[ApiClass]:
    """Parse QSDL schema into custom apis.

    Args:
        schema (Schema): The QSDL schema model.

    Returns:
        list[ApiClass]: The parsed apis.
    """
    apis = []

    api_list = xtx.get_children_of_api(schema)

    for api in api_list:
        # we can skip empty apis
        if not api.operations:
            continue

        api_class = ApiClass().build(api)
        apis.append(api_class)

    apis = util.sort_api_controller(apis)

    return apis


def parse_models(schema: Schema) -> list[ModelClass]:
    """Parse QSDL schema into custom models.

    Args:
        schema (Schema): The QSDL schema model.
    Returns:
        list[ModelClass]: The parsed models.
    """
    models = []

    enum_list = xtx.get_children_of_enum(schema)
    base_list = xtx.get_children_of_base(schema)
    obj_list = xtx.get_children_of_object(schema)

    for entity in enum_list + base_list + obj_list:
        new_model = ModelClass().build(entity)
        models.append(new_model)

    # add domain parents for each model
    util.add_parents_to_model(models)

    # add hibernate related info to model and fields
    util.add_hibernate_info(models)

    return models


def remove_ignored_files(output_path: Path, api_files: list, model_files: list, supporting_files: list) -> None:
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
        with open(ignorefile_path, encoding="utf-8") as infile:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", infile)

        # loop over each all files and remove matches
        # note the copy() - we dont want to modify the list directly
        for src, dest, _ in api_files.copy():
            if spec.match_file(dest):
                api_files.remove((src, dest, _))

        for src, dest, _ in model_files.copy():
            if spec.match_file(dest):
                model_files.remove((src, dest, _))

        for src, dest in supporting_files.copy():
            if spec.match_file(dest):
                supporting_files.remove((src, dest))


def generate_openapi(output_path: Path) -> None:
    """Helper that calls the openapi generator.

    Args:
        output_path (Path): The requested destination.
    """
    gen_schema_file = output_path / "src/main/resources/openapi.yaml"
    gen_schema_file.parent.mkdir(exist_ok=True, parents=True)

    from qsdl import core  # pylint: disable=import-outside-toplevel
    from qsdl.config import Config as core_config  # pylint: disable=import-outside-toplevel

    core.generate(
        gen_schema_file.parent,
        generator_name="openapi",
        input_path=core_config.input_path,
        raw_schema=core_config.raw_schema,
        config={"id_type": util.Store.config.id_type},
    )


def generate(schema: Schema, output_path: Path, config: Config) -> None:
    """Generator func for spring"""

    if config.id_type not in IDTYPE.__members__:
        raise ValueError("id_type must be `LONG` or `STRING`")

    if config.id_type == IDTYPE.LONG:
        id_name = "id"
        id_type = "Long"
    else:
        id_name = "uid"
        id_type = "String"

    # sets the id type and schema
    util.custom_types["ID"] = id_type
    util.Store.schema = schema
    util.Store.config = config
    util.Store.package = package = Package(config)
    util.Store.is_id_long = id_type == "Long"

    # parse models and apis
    util.Store.models = models = parse_models(schema)
    util.Store.apis = apis = parse_apis(schema)

    # resolve all dynamic imports
    resolver.resolve_dynamic_imports()

    # enable slashing
    package.slashed = True

    # loop and generate domain files
    api_files = []

    for api in apis:
        api.package.slashed = True

        # fmt: off
        api_files.append(("src/main/java/api/Api.j2", f"src/main/java/{api.package.api}/{api.name}Api.java", api))
        api_files.append(("src/main/java/api/Controller.j2", f"src/main/java/{api.package.controller}/{api.name}Controller.java", api))

        if api.model and api.has_generated:
            api_files.append(("src/main/java/service/Service.j2", f"src/main/java/{api.package.service}/{api.name}Service.java", api))
            api_files.append(("src/test/java/api/DControllerTest.j2", f"src/test/java/{api.package.controller}/{api.name}ControllerTest.java", api))

            if config.database == "HIBERNATE":
                api_files.append(("src/test/java/service/ServiceTest.j2", f"src/test/java/{api.package.service}/{api.name}ServiceTest.java", api))
        # fmt: on
        api.package.slashed = False

    # loop and generate model files
    model_files = []

    for model in models:
        model.package.slashed = True
        # fmt: off
        if model.is_enum:
            model_files.append(("src/main/java/constant/Enum.j2", f"src/main/java/{model.package.enum}/{model.name}.java", model))
        else:
            model_files.append(("src/main/java/domain/Pojo.j2", f"src/main/java/{model.package.domain}/{model.name}.java", model))

        # generate entities for both objects and base entities
        if config.database == "HIBERNATE" and (model.is_object or model.is_entity) and not model.is_enum:
            model_files.append(("src/main/java/domain/Entity.j2", f"src/main/java/{model.package.entity}/{model.name}Entity.java", model))
            model_files.append(("src/main/java/domain/MapStruct.j2", f"src/main/java/{model.package.mapper}/{model.name}MapStruct.java", model))

        if config.database == "HIBERNATE" and model.is_object:
            model_files.append(("src/main/java/repository/Repository.j2", f"src/main/java/{model.package.repository}/{model.name}Repository.java", model))
            model_files.append(("src/test/java/repository/RepositoryTest.j2", f"src/test/java/{model.package.repository}/{model.name}RepositoryTest.java", model))
        # fmt: on
        model.package.slashed = False

    # fmt: off
    supporting_files = [
        # root
        ("pom.j2", "pom.xml"),
        ("README.j2", "README.md"),
        (".qsdl-ignore.j2", ".qsdl-ignore"),
        (".gitignore.j2", ".gitignore"),
        ("dev.j2", "dev.sh"),
        ("docker-compose.j2", "docker-compose.yml"),
        # vscode
        (".vscode/extensions.j2", ".vscode/extensions.json"),
        (".vscode/launch.j2", ".vscode/launch.json.template"),
        (".vscode/settings.j2", ".vscode/settings.json.template"),
        # resources
        ("src/main/resources/application.j2", "src/main/resources/application.yaml"),
        ("src/main/resources/logback-spring.j2", "src/main/resources/logback-spring.xml"),
        ("src/main/resources/public/index.j2", "src/main/resources/public/index.html"),
        ("src/main/resources/public/error/404.j2", "src/main/resources/public/error/404.html"),
        # main
        ("src/main/java/SpringBootApp.j2", f"src/main/java/{package.base}/SpringBootApp.java"),
        ("src/test/java/TestConfig.j2", f"src/test/java/{package.base}/TestConfig.java"),
        ("src/test/java/TestUtils.j2", f"src/test/java/{package.base}/TestUtils.java"),
        # config
        ("src/main/java/config/AppConfiguration.j2", f"src/main/java/{package.config}/AppConfiguration.java"),
        ("src/main/java/config/AppProperties.j2", f"src/main/java/{package.config}/AppProperties.java"),
        # constants
        ("src/main/java/constant/ErrorCode.j2", f"src/main/java/{package.enum}/ErrorCode.java"),
        ("src/main/java/constant/Constant.j2", f"src/main/java/{package.enum}/Constant.java"),
        # api
        ("src/main/java/api/BaseController.j2", f"src/main/java/{package.controller}/BaseController.java"),
        ("src/main/java/api/HomeController.j2", f"src/main/java/{package.controller}/HomeController.java"),
        # util
        ("src/main/java/util/Json.j2", f"src/main/java/{package.util}/Json.java"),
        ("src/main/java/util/Time.j2", f"src/main/java/{package.util}/Time.java"),
        ("src/main/java/util/Validator.j2", f"src/main/java/{package.util}/Validator.java"),
        ("src/main/java/util/IdGenerator.j2", f"src/main/java/{package.util}/IdGenerator.java"),
        ("src/main/java/util/PredicateBuilder.j2", f"src/main/java/{package.util}/PredicateBuilder.java"),
        ("src/main/java/util/TaskScheduler.j2", f"src/main/java/{package.util}/TaskScheduler.java"),
        # exception
        ("src/main/java/exception/AppException.j2", f"src/main/java/{package.exception}/AppException.java"),
        ("src/main/java/exception/AppExceptionUtil.j2", f"src/main/java/{package.exception}/AppExceptionUtil.java"),
        ("src/main/java/exception/GlobalExceptionHandler.j2", f"src/main/java/{package.exception}/GlobalExceptionHandler.java"),
        # model
        ("src/main/java/model/AbstractClass.j2", f"src/main/java/{package.model}/AbstractClass.java"),
        ("src/main/java/model/AppError.j2", f"src/main/java/{package.model}/AppError.java"),
        ("src/main/java/model/CursorPageable.j2", f"src/main/java/{package.model}/CursorPageable.java"),
        ("src/main/java/model/CursorPage.j2", f"src/main/java/{package.model}/CursorPage.java"),
        ("src/main/java/model/Context.j2", f"src/main/java/{package.model}/Context.java"),
        # tests
        ("src/test/java/api/ControllerTest.j2", f"src/test/java/{package.controller}/ControllerTest.java")
    ]
    # fmt: on

    if config.database == "HIBERNATE":
        # fmt: off
        supporting_files.append( ("src/main/java/model/AbstractPersistentObject.j2", f"src/main/java/{package.model}/AbstractPersistentObject.java"))
        supporting_files.append(("src/main/java/model/AbstractPersistentBase.j2", f"src/main/java/{package.model}/AbstractPersistentBase.java"))
        supporting_files.append(("src/main/java/repository/AbstractRepository.j2", f"src/main/java/{package.repository}/AbstractRepository.java"))
        supporting_files.append(("src/main/java/repository/BaseRepository.j2", f"src/main/java/{package.repository}/BaseRepository.java"))
        supporting_files.append(("src/main/java/repository/BaseRepositoryImpl.j2", f"src/main/java/{package.repository}/BaseRepositoryImpl.java"))
        supporting_files.append(("src/test/java/AbstractDataJpaTest.j2", f"src/test/java/{package.base}/AbstractDataJpaTest.java"))
        supporting_files.append(("src/test/java/AbstractIntegrationTest.j2", f"src/test/java/{package.base}/AbstractIntegrationTest.java"))
        # fmt: on

    # remove ignored files from generator
    remove_ignored_files(output_path, api_files, model_files, supporting_files)

    # enable dotting
    package.slashed = False

    # build the render arguments
    context = {
        "title": config.title,
        "group_id": config.group_id,
        "artifact_id": config.artifact_id,
        "base_package": config.base_package,
        "package": package,
        "packages": util.Store.packages,
        "basePath": schema.servers[0] if schema.servers else "/api/v1",
        "database": config.database,
        "use_encapsulation": config.use_encapsulation,
        "use_builder": config.use_builder,
        "use_auditing": config.use_auditing,
        "id_name": id_name,
        "id_type": id_type,
        "generate_imports_for_template": resolver.generate_imports_for_template,
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
