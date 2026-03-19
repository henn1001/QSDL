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

"""Generator Main entrypoint"""

from pathlib import Path

import qsdl.dsl.textx as xtx
from qsdl.dsl import Schema
from qsdl.render import render

from . import import_resolver as resolver
from . import util
from .config import IDTYPE, Config, Database
from .models import ApiClass, EnumClass, ModelClass, Package


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

    base_list = xtx.get_children_of_base(schema)
    obj_list = xtx.get_children_of_object(schema)

    for entity in base_list + obj_list:
        new_model = ModelClass().build(entity)
        models.append(new_model)

    # add domain parents for each model
    util.add_parents_to_model(models)

    # add hibernate related info to model and fields
    util.add_hibernate_info(models)

    # build models from operations query parameters
    filter_models = util.build_filter_models()
    models.extend(filter_models)

    # build request-body DTOs from write operations with inline scalar parameters
    request_body_models = util.build_request_body_models()
    models.extend(request_body_models)

    return models


def parse_enums(schema: Schema) -> list[EnumClass]:
    """Parse QSDL schema into custom enum models.

    Args:
        schema (Schema): The QSDL schema model.
    Returns:
        list[ModelClass]: The parsed enum models.
    """
    enums = []

    dsl_enums = xtx.get_children_of_enum(schema)

    for dsl_enum in dsl_enums:
        enum = EnumClass.from_ref(dsl_enum)
        enums.append(enum)

    return enums


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


def generate_postgres(output_path: Path) -> None:
    """Helper that calls the postgres generator.

    Args:
        output_path (Path): The requested destination.
    """
    gen_schema_folder = output_path / "src/main/resources/db/migration"
    gen_schema_folder.mkdir(exist_ok=True, parents=True)

    from qsdl import core  # pylint: disable=import-outside-toplevel
    from qsdl.config import Config as core_config  # pylint: disable=import-outside-toplevel

    core.generate(
        gen_schema_folder,
        generator_name="postgres",
        input_path=core_config.input_path,
        raw_schema=core_config.raw_schema,
        config={"table_prefix": util.Store.config.table_prefix},
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
    util.Store.models = parse_models(schema)
    util.Store.enums = parse_enums(schema)
    util.Store.apis = parse_apis(schema)

    # post-process models to determine which actually need Request DTOs based on API usage
    util.resolve_request_dto_usage()

    # resolve all dynamic imports
    resolver.resolve_dynamic_imports()

    # enable slashing
    package.slashed = True

    # loop and generate domain files
    api_files = []

    for api in util.Store.apis:
        api.package.slashed = True

        # fmt: off
        api_files.append(("src/main/java/api/Api.j2", f"src/main/java/{api.package.api}/{api.name}Api.java", api))
        api_files.append(("src/main/java/api/Controller.j2", f"src/main/java/{api.package.controller}/{api.name}Controller.java", api))

        if api.model and api.has_generated:
            api_files.append(("src/main/java/service/Service.j2", f"src/main/java/{api.package.service}/{api.name}Service.java", api))
            api_files.append(("src/test/java/api/DControllerTest.j2", f"src/test/java/{api.package.controller}/{api.name}ControllerTest.java", api))

            if config.database == Database.HIBERNATE:
                api_files.append(("src/test/java/service/ServiceTest.j2", f"src/test/java/{api.package.service}/{api.name}ServiceTest.java", api))
        # fmt: on
        api.package.slashed = False

    # loop and generate model files
    model_files = []

    for model in util.Store.models:
        model.package.slashed = True
        # fmt: off
        if model.has_request:
            model_files.append(("src/main/java/domain/Request.j2", f"src/main/java/{model.package.domain}/{model.name}Request.java", model))
        if model.has_response:
            model_files.append(("src/main/java/domain/Response.j2", f"src/main/java/{model.package.domain}/{model.name}.java", model))

        if model.is_object:
            model_files.append(("src/main/java/domain/Mapper.j2", f"src/main/java/{model.package.mapper}/{model.name}Mapper.java", model))

        if config.database == Database.HIBERNATE and model.is_object:
            model_files.append(("src/main/java/domain/Entity.j2", f"src/main/java/{model.package.entity}/{model.name}Entity.java", model))
            model_files.append(("src/main/java/repository/Repository.j2", f"src/main/java/{model.package.repository}/{model.name}Repository.java", model))
            model_files.append(("src/test/java/repository/RepositoryTest.j2", f"src/test/java/{model.package.repository}/{model.name}RepositoryTest.java", model))
        # fmt: on
        model.package.slashed = False

    # loop and generate enum files
    enum_files = []

    for enum in util.Store.enums:
        enum.package.slashed = True
        # fmt: off
        enum_files.append(("src/main/java/constant/Enum.j2", f"src/main/java/{enum.package.enum}/{enum.name}.java", enum))
        # fmt: on
        enum.package.slashed = False

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
        ("src/main/java/util/JsonUtil.j2", f"src/main/java/{package.util}/JsonUtil.java"),
        ("src/main/java/util/JsonMergePatchConverter.j2", f"src/main/java/{package.util}/JsonMergePatchConverter.java"),
        ("src/main/java/util/JsonMergePatchUtil.j2", f"src/main/java/{package.util}/JsonMergePatchUtil.java"),
        ("src/main/java/util/ObjectNodeConverter.j2", f"src/main/java/{package.util}/ObjectNodeConverter.java"),
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
    util.remove_ignored_files(output_path, api_files, model_files, supporting_files)

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
        "use_auditing": config.use_auditing,
        "id_name": id_name,
        "id_type": id_type,
        "generate_imports_for_template": resolver.generate_imports_for_template,
        "table_prefix": config.table_prefix,
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

    # generate enums
    for src, dest, enum in enum_files:
        context["enum"] = enum
        output_file = output_path / dest
        template_path = Path(__file__).parent / "template" / src
        macro_path = Path(__file__).parent / "template" / "_macro"
        render(output_file, context, template_path, macro_path=macro_path)

    # run openapi and postgres generator to create spec file
    generate_openapi(output_path)
    generate_postgres(output_path)
