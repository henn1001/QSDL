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

import stringcase
from textx import model as xtx

import qsdl.core as core
from qsdl import config
from qsdl.render import render

from . import util
from .parse import parse_apis, parse_ignored_files, parse_models


def generate(schema: object, output_path: Path, parameters: object):
    """Generator func for spring.
    """
    base_package = parameters.groupId.replace(".", "/")

    api_files = []

    # loop and generate api files
    for api in parse_apis(schema):

        # fmt: off
        if parameters.interfacePattern:
            api_files.append(("src/main/java/api/Api.j2", f"src/main/java/{base_package}/api/{api.tag}/{api.name}/{api.capital_name}Api.java", api))
            api_files.append(("src/main/java/api/ApiController.j2", f"src/main/java/{base_package}/api/{api.tag}/{api.name}/{api.capital_name}ApiController.java", api))
        else:
            api_files.append(("src/main/java/api/Controller.j2", f"src/main/java/{base_package}/api/{api.tag}/{api.name}/{api.capital_name}Controller.java", api))

        api_files.append(("src/main/java/api/Service.j2", f"src/main/java/{base_package}/api/{api.tag}/{api.name}/{api.capital_name}Service.java", api))
        # fmt: on

    model_files = []

    # loop and generate model_files
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
        ("src/main/java/constants/AppError.j2", f"src/main/java/{base_package}/constants/AppError.java"),
        ("src/main/java/constants/Constants.j2", f"src/main/java/{base_package}/constants/Constants.java"),
        # util
        ("src/main/java/util/Json.j2", f"src/main/java/{base_package}/util/Json.java"),
        ("src/main/java/util/Time.j2", f"src/main/java/{base_package}/util/Time.java"),
        ("src/main/java/util/Validator.j2", f"src/main/java/{base_package}/util/Validator.java"),
        # exception
        ("src/main/java/exception/ApiException.j2", f"src/main/java/{base_package}/exception/ApiException.java"),
        ("src/main/java/exception/GlobalExceptionHandler.j2", f"src/main/java/{base_package}/exception/GlobalExceptionHandler.java"),
        # model
        ("src/main/java/model/ApiError.j2", f"src/main/java/{base_package}/model/ApiError.java"),
        ("src/main/java/model/ApiPageable.j2", f"src/main/java/{base_package}/model/ApiPageable.java"),
    ]
    # fmt: on

    # remove ignored files from generator
    parse_ignored_files(output_path, api_files, model_files, supporting_files)

    # build the render arguments
    context = {
        "title": parameters.title,
        "groupId": parameters.groupId,
        "artifactId": parameters.artifactId,
        "basePackage": parameters.groupId,
        "basePath": "/v1",
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
    core.generate(config.schema, gen_schema_file.parent, "openapi")
