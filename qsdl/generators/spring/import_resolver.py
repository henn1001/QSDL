# Copyright (C) 2022 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Spring Generator Java import resolver"""

import qsdl.dsl.models as dsl
from . import models as spring
from . import util


def resolve_dynamic_imports():
    """resolve all model related dynamic imports"""

    namespaced_packages = {}

    for model in util.Store.models:

        if model.package._namespace not in namespaced_packages:
            namespaced_packages[model.package._namespace] = model.package

        model.imports["domain"] = get_model_imports(model)
        model.imports["entity"] = get_entity_imports(model)
        model.imports["mapper"] = get_mapper_imports(model)
        model.imports["repo"] = get_repository_imports(model)
        model.imports["repo_tests"] = get_repository_tests_imports(model)

        model.imports["service_tests"] = get_service_tests_imports(model)
        model.imports["controller_tests"] = get_controller_tests_imports(model)

    util.Store.packages = list(namespaced_packages.values())


def sort_and_remove_duplicates(imports: list[str]) -> list[str]:
    """removes duplicates in a simple list of strings and sorts them"""
    imports = list(dict.fromkeys(imports))
    imports.sort()
    return imports


def get_api_imports(api_class: spring.ApiClass, entity: dsl.Api) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if util.controller_has(entity, has_enum=True):
        imprt = f"import {util.Store.package.enum}.*;"
        imports.append(imprt)

    imprt = f"import {api_class.package.domain}.*;"
    imports.append(imprt)

    imprt = f"import {api_class.package.model}.*;"
    imports.append(imprt)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_controller_imports(api_class: spring.ApiClass, entity: dsl.Api) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if util.controller_has(entity, has_enum=True):
        imprt = f"import {util.Store.package.enum}.*;"
        imports.append(imprt)

    if api_class.package.controller != api_class.package.api:
        imprt = f"import {api_class.package.api}.{api_class.name}Api;"
        imports.append(imprt)

    imprt = f"import {api_class.package.domain}.*;"
    imports.append(imprt)

    imprt = f"import {api_class.package.model}.*;"
    imports.append(imprt)

    if api_class.package.controller != util.Store.package.controller:
        imprt = f"import {util.Store.package.controller}.BaseController;"
        imports.append(imprt)

    if entity.has_generated:
        imprt = f"import {api_class.package.service}.{api_class.name}Service;"
        imports.append(imprt)

    if entity.has_generated:
        imprt = f"import {util.Store.package.util}.Validator;"
        imports.append(imprt)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_controller_tests_imports(model: spring.ModelClass) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if not model.is_object and not model.is_base:
        return imports

    imprt = [
        f"import {util.Store.config.base_package}.TestConfig;",
        f"import {util.Store.config.base_package}.TestUtils;",
        f"import {util.Store.package.config}.ErrorCodes;",
        f"import {util.Store.package.util}.Json;",
        f"import {util.Store.package.model}.AppError;",
        f"import {util.Store.package.model}.CursorPage;",
        f"import {model.package.domain}.{model.name};",
        f"import {model.package.service}.{model.name}Service;",
    ]

    imports.extend(imprt)

    # parents = [f"import {parent.model.package.entity}.{parent.model.name}Entity;" for parent in model.parents]
    # repos = [f"import {parent.model.package.repository}.{parent.model.name}Repository;" for parent in model.parents]

    imports.extend(imprt)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_service_imports(api_class: spring.ApiClass, entity: dsl.Api) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if util.controller_has(entity, has_enum=True):
        imprt = f"import {util.Store.package.enum}.*;"
        imports.append(imprt)

    imprt = f"import {api_class.package.domain}.*;"
    imports.append(imprt)

    imprt = f"import {util.Store.package.model}.*;"
    imports.append(imprt)

    imprt = f"import {util.Store.package.exception}.*;"
    imports.append(imprt)

    if util.Store.config.database == "HIBERNATE":
        imprt = [
            f"import {api_class.package.entity}.*;",
            f"import {api_class.package.mapper}.*;",
            f"import {api_class.package.repository}.*;",
            f"import {util.Store.package.repository}.*;",
            f"import {util.Store.package.util}.PredicateBuilder;",
        ]

        imports.extend(imprt)

        if api_class.model:
            for parent in api_class.model.parents:
                imprt = [
                    f"import {parent.model.package.domain}.*;",
                    f"import {parent.model.package.entity}.*;",
                    f"import {parent.model.package.mapper}.*;",
                    f"import {parent.model.package.repository}.*;",
                ]

                imports.extend(imprt)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_service_tests_imports(model: spring.ModelClass) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if not model.is_object and not model.is_base:
        return imports

    imprt = [
        f"import {util.Store.config.base_package}.TestConfig;",
        f"import {util.Store.config.base_package}.TestUtils;",
        f"import {util.Store.package.config}.ErrorCodes;",
        f"import {util.Store.package.exception}.AppException;",
        f"import {util.Store.package.model}.AppError;",
        f"import {util.Store.package.model}.Context;",
        f"import {util.Store.package.model}.CursorPage;",
        f"import {util.Store.package.model}.CursorPageable;",
        f"import {util.Store.package.util}.Json;",
        f"import {model.package.domain}.{model.name};",
        f"import {model.package.entity}.{model.name}Entity;",
        f"import {model.package.mapper}.{model.name}MapStruct;",
        f"import {model.package.repository}.{model.name}Repository;",
    ]

    imports.extend(imprt)

    parents = [f"import {parent.model.package.entity}.{parent.model.name}Entity;" for parent in model.parents]
    repos = [f"import {parent.model.package.repository}.{parent.model.name}Repository;" for parent in model.parents]

    imports.extend(imprt + parents + repos)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_model_imports(model: spring.ModelClass) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if not model.is_object and not model.is_base:
        return imports

    enums = [f"import {util.Store.package.enum}.{field.type};" for field in model.fields if field.is_enum]
    imports.extend(enums)

    imports.append(f"import {util.Store.package.model}.AbstractClass;")

    # check for nested, get their respective spring.ModelClass and use the package
    nested_entities = [
        field.type for field in model.fields if (field.is_object or field.is_base) and not field.is_relation
    ]
    nested_models = [util.get_model_for(type) for type in nested_entities]

    imprt = [
        f"import {nested.package.domain}.{nested.name};"
        for nested in nested_models
        if nested.package.domain != model.package.domain
    ]
    imports.extend(imprt)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_entity_imports(model: spring.ModelClass) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if not model.is_object and not model.is_base:
        return imports

    enums = [f"import {util.Store.package.enum}.{field.type};" for field in model.fields if field.is_enum]
    imports.extend(enums)

    if model.is_base:
        imports.append(f"import {util.Store.package.model}.AbstractPersistentBase;")
    elif model.is_object:
        imports.append(f"import {util.Store.package.model}.AbstractPersistentObject;")

    # check for nested, get their respective spring.ModelClass and use the package
    nested_entities = [field.type for field in model.fields if field.is_object or field.is_base]
    nested_models = [util.get_model_for(type) for type in nested_entities]

    imprt = [
        f"import {nested.package.entity}.{nested.name}Entity;"
        for nested in nested_models
        if nested.package.entity != model.package.entity
    ]
    imports.extend(imprt)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_mapper_imports(model: spring.ModelClass) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if model.is_object or model.is_entity:
        imprt = f"import {model.package.domain}.{model.name};"
        imports.append(imprt)

        imprt = f"import {model.package.entity}.{model.name}Entity;"
        imports.append(imprt)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_repository_imports(model: spring.ModelClass) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if model.is_object or model.is_entity:
        imprt = f"import {model.package.entity}.{model.name}Entity;"
        imports.append(imprt)

        if model.package.repository != util.Store.package.repository:
            imprt = f"import {util.Store.package.repository}.*;"
            imports.append(imprt)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports


def get_repository_tests_imports(model: spring.ModelClass) -> list[str]:
    """Helper for dynamic imports"""
    imports = []

    if model.is_object or model.is_entity:
        imprt = [
            f"import {model.package.entity}.*;",
            f"import {util.Store.package.repository}.*;",
            f"import {util.Store.package.model}.*;",
        ]
        imports.extend(imprt)

        parents = [f"import {parent.model.package.entity}.{parent.model.name}Entity;" for parent in model.parents]
        repos = [f"import {parent.model.package.repository}.{parent.model.name}Repository;" for parent in model.parents]

        nested_entities = [field.type for field in model.fields if field.is_relation]
        nested_models = [util.get_model_for(type) for type in nested_entities]
        relations = [f"import {nested.package.entity}.{nested.name}Entity;" for nested in nested_models]

        imports.extend(parents + repos + relations)

    # remove duplicates and sort
    imports = sort_and_remove_duplicates(imports)

    return imports
