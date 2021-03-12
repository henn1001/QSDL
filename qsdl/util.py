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

import inflect
from textx import model as xtx

from qsdl import config
from qsdl.dsl.models import Scalar


def pluralize(word: str) -> str:
    """Returns the plural form of a word using inflect.

    Args:
        word (str): A word.

    Returns:
        str: Plural form of the word.
    """
    return inflect.engine().plural(word)


def get_namespaces() -> list:
    """Return all NameSpaces.

    Returns:
        list[str]: All NameSpaces
    """
    namespaces = []

    for obj in config.domain_objects:
        if obj.namespace and obj.namespace not in namespaces:
            namespaces.append(obj.namespace)

    return namespaces


def get_domain_objects() -> list:
    """Return all global domain objects.

    Returns:
        list: [entity.Object]
    """
    return config.domain_objects


def get_operations() -> list:
    """Return all global operations.

    Returns:
        list: [Operations]
    """
    return config.operations


def get_operations_of_object(obj: object) -> list:
    """Return all operations for this Object.

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """
    # hasattr will filter out custom queries and mutations without any object relations
    operations = list(
        filter(lambda x: (hasattr(x.ref, "name") and x.ref.name == obj.name), config.operations)
    )
    return operations


def get_operations_of_object_of_queries(obj: object) -> list:
    """Return all operations for this Object with method == get

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """
    operations = list(
        filter(
            lambda x: (hasattr(x.ref, "name") and x.ref.name == obj.name) and x.method == "get",
            config.operations,
        )
    )
    return operations


def get_operations_of_object_of_mutations(obj: object) -> list:
    """Return all operations for this Object with method != get

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """
    operations = list(
        filter(
            lambda x: (hasattr(x.ref, "name") and x.ref.name == obj.name) and x.method != "get",
            config.operations,
        )
    )
    return operations


def get_queries_of_operation(operation: object) -> list:
    """Return all operations for this Object with method == get

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """

    name_list = []
    for field in operation.fields:
        name_list.append(field.name)

    operations = list(
        filter(lambda x: x.name in name_list and x.method == "get", config.operations,)
    )
    return operations


def get_mutations_of_operation(operation: object) -> list:
    """Return all operations for this Object with method != get

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """
    name_list = []
    for field in operation.fields:
        name_list.append(field.name)

    operations = list(
        filter(lambda x: x.name in name_list and x.method != "get", config.operations,)
    )
    return operations


def get_operations_of_queries() -> list:
    """Return all operations with method == get

    Returns:
        list: [Operations]
    """
    operations = list(filter(lambda x: x.method == "get", config.operations))
    return operations


def get_operations_of_mutations() -> list:
    """Return all operations with method != get

    Returns:
        list: [Operations]
    """
    operations = list(filter(lambda x: x.method != "get", config.operations))
    return operations


def get_compositions(obj: object) -> list:
    """Return all Objects who are using this Object as composition.

    Args:
        obj (object): entity.Object

    Returns:
        list: [entity.Object]
    """
    comp_fields = []

    occurrence = get_parents(obj)
    comp_fields = list(
        filter(lambda x: x.composition and x.value._tx_fqn == "entity.Object", occurrence)
    )

    return comp_fields


def get_aggregation(obj: object) -> list:
    """Return all Objects who are using this Object as aggregation.

    Args:
        obj (object): entity.Object

    Returns:
        list: [entity.Object]
    """
    agg_fields = []

    occurrence = get_parents(obj)
    agg_fields = list(
        filter(lambda x: x.aggregation and x.value._tx_fqn == "entity.Object", occurrence)
    )

    return agg_fields


def get_parents(obj: object) -> list:
    """Returns all Objects who make use of this Object.

    Args:
        obj (object): entity.Object

    Returns:
        list: [entity.Object]
    """
    parents = []

    fields = xtx.get_children_of_type("Field", config.model)

    parents = list(filter(lambda x: x.value == obj, fields))

    return parents


def get_childs(obj: object) -> list:
    """Returns all aggregation and compositions for a Object.

    Args:
        obj (object): entity.Object

    Returns:
        list: [entity.Object]
    """
    childs = []
    child_fields = []

    child_fields.extend(
        list(filter(lambda x: x.composition and x.value._tx_fqn == "entity.Object", obj.fields))
    )
    child_fields.extend(
        list(filter(lambda x: x.aggregation and x.value._tx_fqn == "entity.Object", obj.fields))
    )

    for field in child_fields:
        childs.append(field.value)

    return childs


def get_fields_as_list(entity: object) -> list:
    """Returns all fields ob a object including its supertype as list.

    Args:
        entity (object): entity.Object

    Returns:
        list: [entity.Field]
    """
    tmp = entity
    fields = []

    while True:
        tmp_list = []
        for field in tmp.fields:
            tmp_list.append(field)

        fields = tmp_list + fields
        if not tmp.supertype:
            break

        tmp = tmp.supertype

    return fields


def get_filtered_fields(field: object) -> bool:
    """A filter for fields.

    We only want to include composition or aggregations when they are nested.

    Args:
        field (object): entity.Field

    Returns:
        bool: Returns True for usable fields.
    """
    ret = False

    if not (
        (
            (field.composition and field.value._tx_fqn == "entity.Object")
            or (field.aggregation and field.value._tx_fqn == "entity.Object")
        )
        and not field.nested
    ):
        ret = True

    return ret


def get_operation_id(obj: object, append: str = "") -> str:
    """Returns the operation id name for OpenAPI.

    Args:
        obj (object): entity.Object
        append (str, optional): To pluralize the name. Defaults to "".

    Returns:
        str: Tue operation id
    """
    operation_id = None

    if obj.name not in config.dupl_objects:
        operation_id = obj.name.capitalize() + append

    elif obj.d_parent:
        operation_id = obj.name.capitalize() + append + "For" + obj.d_parent.name.capitalize()
    else:
        operation_id = obj.name.capitalize() + append

    return operation_id


def has_query(entity: object) -> bool:
    """Checks if a Object has a query directive.

    Args:
        entity (object): entity.Object

    Returns:
        bool: Return true for any query.
    """
    ret = False

    if entity.supertype:
        ret = has_query(entity.supertype)

    for field in entity.fields:
        if field.query:
            ret = True
            break

    return ret


def get_required(entity: object) -> list:
    """Returns all non_nullable fields of a Object.

    Args:
        entity (object): entity.Object

    Returns:
        list: [entity.Field]
    """
    tmp = entity
    fields = []

    while True:
        tmp_list = []
        for field in tmp.fields:
            if field.non_nullable:
                tmp_list.append(field)

        fields = tmp_list + fields
        if not tmp.supertype:
            break

        tmp = tmp.supertype

    return fields


def get_id(entity: object) -> str:
    """Returns the name of the ID of a Objects, Queries or Mutations.

    Args:
        entity (object): Either entity.Object or entity.Field.

    Returns:
        str: The name of the ID. None if no ID is found.
    """
    field_entity_name = None

    if entity._tx_fqn == "entity.Object" or entity._tx_fqn == "entity.Base":

        if entity.supertype:
            field_entity_name = get_id(entity.supertype)

        for field in entity.fields:
            if field.value.name == "ID":
                return field.name

    if entity._tx_fqn == "entity.Field":

        for argument in entity.arguments:
            if argument.value.name == "ID":
                return argument.name

    return field_entity_name


def get_id_field(entity: object) -> object:
    """Returns the field of the ID of a Objects, Queries or Mutations.

    Args:
        entity (object): Either entity.Object or entity.Field.

    Returns:
        object: The entity.Field of the ID. None if no ID is found.
    """
    field_entity = None

    if entity._tx_fqn == "entity.Object" or entity._tx_fqn == "entity.Base":

        if entity.supertype:
            field_entity = get_id_field(entity.supertype)

        for field in entity.fields:
            if field.value.name == "ID":
                return field

    if entity._tx_fqn == "entity.Field":

        for argument in entity.arguments:
            if argument.value.name == "ID":
                return argument

    return field_entity


def has_composition(obj):
    """Checks if the object has any composition.

    Args:
        obj (object): entity.Object

    Returns:
        bool: Returns true for any composition.
    """
    ret = False

    for field in obj.fields:
        if field.composition and field.value._tx_fqn == "entity.Object":
            ret = True
            break

    return ret


def is_composition(child: object, parent: object) -> bool:
    """Checks if the child is a composition of a parent.

    Args:
        child (object): entity.Object
        parent (object): entity.Object

    Returns:
        bool: True if the child is a composition.
    """
    ret = False

    if parent:
        for field in parent.fields:
            if field.value.name == child.name and (
                field.composition and field.value._tx_fqn == "entity.Object"
            ):
                ret = True
                break

    return ret


def has_aggregation(obj: object) -> bool:
    """Checks if the object has any aggregation.

    Args:
        obj (object): entity.Object

    Returns:
        bool: Returns true for any aggregation.
    """
    ret = False

    for field in obj.fields:
        if field.aggregation and field.value._tx_fqn == "entity.Object":
            ret = True
            break

    return ret


def is_aggregation(child: object, parent: object) -> bool:
    """Checks if the child is a aggregation of a parent.

    Args:
        child (object): entity.Object
        parent (object): entity.Object

    Returns:
        bool: True if the child is a aggregation.
    """
    ret = False

    if parent:
        for field in parent.fields:
            if field.value.name == child.name and (
                field.aggregation and field.value._tx_fqn == "entity.Object"
            ):
                ret = True
                break

    return ret


def is_nested(entity: object) -> bool:
    """Checks if the provided object or base is nested.

    Args:
        entity (object): entity.Object or entity.Base

    Returns:
        bool: [description]
    """
    ret = False

    for field in xtx.get_children_of_type("Field", config.model):
        if field.value == entity:
            if field.nested:
                ret = True
                break

    for arg in xtx.get_children_of_type("Argument", config.model):
        if arg.value == entity:
            ret = True
            break

    return ret


def get_path_base(entity: object, parent: object = None, append_id: bool = False) -> str:
    """Returns the path string for a operation.

    Args:
        entity (object): Either entity.Object or entity.Field.
        parent (object, optional): The parent, entity.Object.
            Defaults to None.
        include_id (bool, optional): Enables the inclusion of the own ID.
            Defaults to False.

    Returns:
        str: The path string as used by OpenApi.
    """

    if entity._tx_fqn == "entity.Object":
        path = "/" + pluralize(entity.name)

        if append_id:
            path = path + "/{" + get_id(entity) + "}"

        if parent:
            path = (
                "/"
                + pluralize(parent.name)
                + "/{"
                + parent.name
                + "_"
                + get_id(parent)
                + "}"
                + path
            )

    if entity._tx_fqn == "entity.Field":
        if entity.path:
            path = "/" + entity.path
        else:
            path = "/" + pluralize(entity.parent.parent.name)

        if get_id(entity):
            path = path + "/{" + get_id(entity) + "}"

        if parent:
            path = (
                "/"
                + pluralize(parent.name)
                + "/{"
                + parent.name
                + "_"
                + get_id(parent)
                + "}"
                + path
            )

    return path.lower()


def is_path_unique(operation_path: str) -> bool:
    """Checks if the operation path has already been used.

    Args:
        operation_path (str): The operation path.

    Returns:
        bool: True if the path has not been used yet.
    """
    ret = False

    if operation_path not in config.used_paths:
        config.used_paths.append(operation_path)
        ret = True

    return ret


def get_operation_method(field: object) -> str:
    """
    Returns the operations method.

    Args:
        field (object): The Field entity.

    Returns:
        str: The operation method.
    """
    method = None

    if field.method is None or field.method == "GET":
        method = "get"

    elif field.method == "PUT":
        method = "put"

    elif field.method == "PATCH":
        method = "patch"

    elif field.method == "DELETE":
        method = "delete"

    elif field.method == "POST":
        method = "post"

    else:
        print("something went wrong in get_operation_method")

    return method


def get_path_parameters(entity: object, parent: object = None, include_id: bool = False) -> list:
    """Returns a list of all path parameters.

    If a parent is provided, include the parents ID.

    For the default CRUD operations, include the object ID.

    For custom queries and mutations, include the parameter ID.

    Args:
        entity (object): Either entity.Object or entity.Field.
        parent (object, optional): The parent, entity.Object.
            Defaults to None.
        include_id (bool, optional): Enables the inclusion of the own ID.
            Defaults to False.

    Returns:
        list: [{name, type, in, required}]
    """
    parameters = []

    if parent:
        name = parent.name.lower() + "_" + get_id(parent)
        param = {
            "name": name,
            "type": get_id_field(parent),
            "in": "path",
            "required": "true",
        }
        parameters.append(param)

    if entity._tx_fqn == "entity.Object" or entity._tx_fqn == "entity.Base":

        if include_id:
            name = get_id(entity)
            param = {
                "name": name,
                "type": get_id_field(entity),
                "in": "path",
                "required": "true",
            }
            parameters.append(param)

    if entity._tx_fqn == "entity.Field":

        for argument in entity.arguments:
            if argument.value.name == "ID":
                name = get_id(entity)
                param = {
                    "name": name,
                    "type": get_id_field(entity),
                    "in": "path",
                    "required": "true",
                }
                parameters.append(param)

    return parameters


def get_query_parameters(entity: object) -> list:
    """Returns a list of all query parameters.

    For the default CRUD operations this will the fields flagged with
        a querydirective.

    For custom queries, this will be all parameters except ID.

    Args:
        entity (object): Either entity.Object or entity.Field.

    Returns:
        list: [{name, type, in, required}]
    """
    parameters = []

    if entity._tx_fqn == "entity.Object" or entity._tx_fqn == "entity.Base":

        tmp = entity
        while True:
            for field in tmp.fields:
                if field.query:
                    param = {"name": field.name, "type": field, "in": "query", "required": "false"}
                    parameters.append(param)

            if tmp.supertype:
                tmp = tmp.supertype
            else:
                break

    if entity._tx_fqn == "entity.Field":

        for argument in entity.arguments:
            if argument.value.name != "ID":
                param = {
                    "name": argument.name,
                    "type": argument,
                    "in": "query",
                    "required": "false",
                }
                parameters.append(param)

    return parameters


def get_request_parameters(entity: object) -> list:
    """Returns a list of all request body parameters.

    For the default CRUD operations this will be the object itself.

    For custom queries and mutations, this will be all parameters except ID.

    Args:
        entity (object): Either entity.Object or entity.Field.

    Returns:
        list: [Scalar | Enum | Input | Object]
    """
    parameters = []

    if entity._tx_fqn == "entity.Object" or entity._tx_fqn == "entity.Base":
        parameters.append(entity)

    if entity._tx_fqn == "entity.Field":

        for argument in entity.arguments:
            if argument.value.name != "ID":
                parameters.append(argument)

    return parameters
