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

"""Utility functions"""

import stringcase


def custom_type(input_type: str) -> str:
    """Maps Scalars to Java types.

    Args:
        input_type (str): The typ to map.

    Returns:
        str: The mapped Java type name or the Scalar name.
    """
    return {
        "Int": "Integer",
        "Long": "Long",
        "Float": "Float",
        "Double": "Double",
        "String": "String",
        "Boolean": "Boolean",
        "ID": "Long",
        "Date": "OffsetDateTime",
        "Object": "Object",
        "Void": "Void",
    }.get(input_type, input_type)


def has_list(entity):
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.array:
                ret = True
                break

    return ret


def has_float(entity):
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.value.name in ["Float", "Double"]:
                ret = True
                break

    return ret


def has_date(entity):
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.value.name in ["Date"]:
                ret = True
                break

    return ret


def has_enum(entity):
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.value._tx_fqn in ["Enum"]:
                ret = True
                break

    return ret


def has_model(entity):
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.value._tx_fqn in ["entity.Base", "entity.Object"]:
                ret = True
                break

    return ret


def has_required(entity):
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.non_nullable:
                ret = True
                break

    return ret


def has_relation(entity):
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if field.composition or field.aggregation:
                ret = True
                break

    return ret


def has_relation_not_nested(entity):
    ret = False

    if entity._tx_fqn in ["entity.Base", "entity.Object"]:

        for field in entity.fields:

            if (field.composition or field.aggregation) and not field.nested:
                ret = True
                break

    return ret


def get_class_name(old_name):
    new_name = stringcase.pascalcase(old_name)

    return new_name


def get_attr_name(old_name):
    new_name = stringcase.camelcase(old_name)

    return new_name


def get_enum_values(entity):
    values = []

    if entity._tx_fqn not in ["entity.Enum"]:
        raise ValueError

    for value in entity.values:
        values.append(value)

    return values


def get_model_imports(entity):
    """Returns all imports for this model.
    """
    imports = []

    if entity._tx_fqn not in ["entity.Enum", "entity.Base", "entity.Object"]:
        raise ValueError

    # note: the order is already sorted
    if has_date(entity):
        _import = ["java.time.OffsetDateTime"]
        imports.extend(_import)

    if has_list(entity):
        _import = ["java.util.ArrayList", "java.util.List"]
        imports.extend(_import)

    if entity._tx_fqn != "entity.Enum":
        _import = ["java.util.Objects"]
        imports.extend(_import)

    if has_list(entity) or has_model(entity):
        _import = ["javax.validation.Valid"]
        imports.extend(_import)

    if has_required(entity):
        _import = ["javax.validation.constraints.*"]
        imports.extend(_import)

    if has_enum(entity) or entity._tx_fqn == "entity.Enum":
        _import = ["com.fasterxml.jackson.annotation.JsonCreator"]
        imports.extend(_import)

    if has_relation_not_nested(entity):
        _import = ["com.fasterxml.jackson.annotation.JsonIgnore"]
        imports.extend(_import)

    if entity._tx_fqn != "entity.Enum":
        _import = ["com.fasterxml.jackson.annotation.JsonProperty"]
        imports.extend(_import)

    if has_enum(entity) or entity._tx_fqn == "entity.Enum":
        _import = ["com.fasterxml.jackson.annotation.JsonValue"]
        imports.extend(_import)

    if has_date(entity):
        _import = ["org.springframework.format.annotation.DateTimeFormat"]
        imports.extend(_import)

    return imports


def getter(field):
    return "get" + stringcase.capitalcase(field.name)


def setter(field):
    return "set" + stringcase.capitalcase(field.name)

