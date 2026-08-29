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

from collections.abc import Mapping
from pathlib import Path

import qsdl.dsl.textx as xtx
from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import Schema
from qsdl.generators.openapi import Config as OpenApiConfig
from qsdl.generators.openapi import generate as generate_openapi
from qsdl.generators.openapi.config import IDTYPE as OpenApiIDType
from qsdl.generators.postgres import Config as PostgresConfig
from qsdl.generators.postgres import generate as generate_postgres
from qsdl.render import render_text

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


def _add_rendered(
    files: GeneratedFiles,
    *,
    destination: str,
    template: str,
    context: Mapping[str, object],
    macro_path: Path,
) -> None:
    """Render a Spring template and add its content to the artifact collection."""
    template_path = Path(__file__).parent / "template" / template
    files.add_text(
        destination,
        render_text(template_path, context, macro_path=macro_path),
    )


def build_files(schema: Schema, config: Config) -> GeneratedFiles:
    """Build Spring, OpenAPI, and PostgreSQL artifacts in memory."""

    if config.id_type not in IDTYPE.__members__:
        raise ValueError("id_type must be `LONG` or `STRING`")

    if config.id_type == IDTYPE.LONG:
        id_name = "id"
        id_type = "Long"
    else:
        id_name = "uid"
        id_type = "String"

    files = GeneratedFiles()

    # Reset generator-local state for every build.
    util.Store.schema = schema
    util.Store.config = config
    util.Store.models = []
    util.Store.apis = []
    util.Store.enums = []
    util.Store.packages = []
    util.Store.package = package = Package(config)
    util.Store.is_id_long = id_type == "Long"
    util.custom_types["ID"] = id_type

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
        if model.is_query_filter:
            model_files.append(("src/main/java/domain/Request.j2", f"src/main/java/{model.package.domain}/{model.name}.java", model))
        elif model.has_request:
            model_files.append(("src/main/java/domain/Request.j2", f"src/main/java/{model.package.domain}/{model.name}Request.java", model))
        if model.has_response and not model.is_query_filter:
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
        (".qignore.j2", ".qignore"),
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
        ("src/main/java/util/TimeUtil.j2", f"src/main/java/{package.util}/TimeUtil.java"),
        ("src/main/java/util/Validator.j2", f"src/main/java/{package.util}/Validator.java"),
        ("src/main/java/util/IdGenerator.j2", f"src/main/java/{package.util}/IdGenerator.java"),
        ("src/main/java/util/PredicateBuilder.j2", f"src/main/java/{package.util}/PredicateBuilder.java"),
        ("src/main/java/util/WorkLoopOrchestrator.j2", f"src/main/java/{package.util}/WorkLoopOrchestrator.java"),
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
        supporting_files.append(("src/main/java/model/AbstractEntity.j2", f"src/main/java/{package.model}/AbstractEntity.java"))
        supporting_files.append(("src/main/java/repository/AbstractRepository.j2", f"src/main/java/{package.repository}/AbstractRepository.java"))
        supporting_files.append(("src/main/java/repository/BaseRepository.j2", f"src/main/java/{package.repository}/BaseRepository.java"))
        supporting_files.append(("src/main/java/repository/BaseRepositoryImpl.j2", f"src/main/java/{package.repository}/BaseRepositoryImpl.java"))
        supporting_files.append(("src/test/java/AbstractDataJpaTest.j2", f"src/test/java/{package.base}/AbstractDataJpaTest.java"))
        supporting_files.append(("src/test/java/AbstractIntegrationTest.j2", f"src/test/java/{package.base}/AbstractIntegrationTest.java"))
        # fmt: on

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
    macro_path = Path(__file__).parent / "template" / "_macro"

    # generate supporting files
    for src, dest in supporting_files:
        _add_rendered(files, destination=dest, template=src, context=context, macro_path=macro_path)

    # generate models
    for src, dest, model in model_files:
        _add_rendered(
            files,
            destination=dest,
            template=src,
            context=context | {"model": model},
            macro_path=macro_path,
        )

    # generate apis
    for src, dest, api in api_files:
        _add_rendered(
            files,
            destination=dest,
            template=src,
            context=context | {"api": api, "model": api.model},
            macro_path=macro_path,
        )

    # generate enums
    for src, dest, enum in enum_files:
        _add_rendered(
            files,
            destination=dest,
            template=src,
            context=context | {"enum": enum},
            macro_path=macro_path,
        )

    openapi_config = OpenApiConfig(id_type=OpenApiIDType(config.id_type.value))
    postgres_config = PostgresConfig(table_prefix=config.table_prefix)

    files.extend(
        generate_openapi(schema, openapi_config),
        prefix="src/main/resources",
    )
    files.extend(
        generate_postgres(schema, postgres_config),
        prefix="src/main/resources/db/migration",
    )

    return files


def generate(schema: Schema, config: Config) -> GeneratedFiles:
    """Generate Spring artifacts in memory."""
    return build_files(schema, config)
