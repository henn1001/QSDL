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

"""Model domain parser"""

import re
from typing import List, Union

from textx import model as xtx

from qsdl.dsl.models import Api, Argument, Field, Object, Scalar, Schema
from qsdl.dsl.models.operation import Operation
from qsdl.filter import pluralize


def get_compositions(schema: Schema, obj: Object) -> List[Field]:
    """Return all Fields who are using this Object as composition.

    Args:
        schema (Schema): The QSDL schema model.
        obj (Object): entity.Object

    Returns:
        List[Field]: [entity.Field]
    """
    comp_fields = []

    fields = get_parents(schema, obj)

    fltr = filter(lambda x: x.is_composition and x.value._tx_fqn == "entity.Object", fields)
    comp_fields = list(fltr)

    return comp_fields


def get_aggregation(schema: Schema, obj: Object) -> List[Field]:
    """Return all Fields who are using this Object as aggregation.

    Args:
        schema (Schema): The QSDL schema model.
        obj (Object): entity.Object

    Returns:
        List[Field]: [entity.Field]
    """
    agg_fields = []

    fields = get_parents(schema, obj)

    fltr = filter(lambda x: x.is_aggregation and x.value._tx_fqn == "entity.Object", fields)
    agg_fields = list(fltr)

    return agg_fields


def get_parents(schema: Schema, obj: Object) -> List[Field]:
    """Returns all Fields whose value is this Object.

    Args:
        schema (Schema): The QSDL schema model.
        obj (Object): entity.Object

    Returns:
        List[Field]: [entity.Field]
    """
    parents = []

    fields = xtx.get_children_of_type("Field", schema)

    fltr = filter(lambda x: x.value == obj, fields)
    parents = list(fltr)

    return parents


def get_query_fields(obj: Object) -> List[Field]:
    """Returns a list of all query parameters.

    For the default CRUD operations this will return the fields flagged with
    a query-directive.

    Args:
        obj (Object): entity.Object

    Returns:
        List[Field]: [entity.Field]
    """
    fields = []

    for field in obj.fields:
        if field.is_query:
            fields.append(field)

    return fields


def get_all_fields_as_list(entity: Object) -> List[Field]:
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


def id_builder(obj: Object) -> Field:
    """Creates and returns a ID field.

    Args:
        obj (Object): entity.Object

    Returns:
        Field: entity.Field
    """
    field = Field()
    field.name = "id"
    field.value = Scalar(name="ID")
    field.is_read_only = True
    field.is_required = True
    field.parent = obj

    return field


def name_builder(
    obj: Object,
    parent_obj: Object = None,
    combiner: str = "For",
    append: str = "",
) -> str:
    """Returns the operation name for CRUD Objects.

    Args:
        obj (Object): The Object this operations belongs to.
        parent_obj (Object, optional): The parent Object if any.
            Defaults to None.
        combiner (str, optional): Word that combines the Objects.
            Defaults to "For".
        append (str, optional): Allows to append a string.
            Defaults to "".

    Returns:
        str: The operation name
    """
    operation_name = None

    if parent_obj:
        operation_name = obj.name.capitalize() + append + combiner + parent_obj.name.capitalize()
    else:
        operation_name = obj.name.capitalize() + append

    return operation_name


def path_builder(
    entity: Union[Field, Object],
    parent_obj: Object = None,
    append_id: bool = False,
) -> str:
    """Creates and returns the path string for a operation.

    Args:
        entity (Union[Field, Object]): Either entity.Object or entity.Field.
        parent (Object, optional): The parent, entity.Object.
            Defaults to None.
        include_id (bool, optional): Enables the inclusion of the own ID.
            Defaults to False.

    Returns:
        str: The path string as used by OpenApi.
    """
    if entity._tx_fqn == "entity.Object":

        path = pluralize(entity.name)

        if not path.startswith("/"):
            path = "/" + path

        if append_id:
            path = path + "/{id}"

        if parent_obj:
            path = "/" + pluralize(parent_obj.name) + "/{" + parent_obj.name + "_id}" + path

    elif entity._tx_fqn == "entity.Operation":

        path = entity.path

        if not path.startswith("/"):
            path = "/" + path

        if path.endswith("/"):
            path = path[:-1]

    return path.lower()


def path_argument_builder(operation: Operation) -> List[Argument]:
    """Creates and returns the path arguments for a operation path.

    ID arguments are identified within {brackets}.

    Args:
        operation (Operation): The entity.Operation.

    Returns:
        List[Argument]: [entity.Argument]
    """
    arguments = []

    regex = r"{(.+?)}+?"
    matches = re.findall(regex, operation.path)

    for match in matches:
        argument = Argument()
        argument.parent = operation

        argument.name = match.lower()
        argument.value = Scalar(name="ID")
        argument.is_path = True
        argument.is_required = True

        arguments.append(argument)

    return arguments


def query_argument_builder(operation: Operation, obj: Object) -> List[Argument]:
    """Creates and returns the query arguments for a operation.

    Args:
        operation (Operation): The entity.Operation.
        obj (Object): The entity.Object the entity.Operation belongs to.

    Returns:
        List[Argument]: [entity.Argument]
    """
    arguments = []

    query_fields = get_query_fields(obj)

    for field in query_fields:
        argument = Argument()
        argument.parent = operation

        argument.name = field.name
        argument.value = field.value
        argument.is_query = True

        arguments.append(argument)

    return arguments


def body_argument_builder(operation: Operation, obj: Object) -> List[Argument]:
    """Creates and returns the query arguments for a operation.

    Args:
        operation (Operation): The entity.Operation.
        obj (Object): The entity.Object the entity.Operation belongs to.
        aggregation (bool, optional): For aggregations, the body containts the aggregated Objects ID.
            Defaults to False.

    Returns:
        List[Argument]: [entity.Argument]
    """
    arguments = []

    argument = Argument()
    argument.parent = operation
    argument.name = "body"
    argument.value = obj
    argument.is_body = True

    arguments.append(argument)

    return arguments


def operation_builder(
    obj: Object,
    parent_obj: Object = None,
    duplicate: bool = False,
    method: str = None,
) -> Operation:
    """Creates and returns the Operation for an Object.

    Args:
        obj (Object): The entity.Object.
        parent_obj (Object, optional): The parent Object if any.
            Defaults to None.
        duplicate (bool, optional): Wether we want to dervice the Operation name from a parent.
            Defaults to False.
        method (str, optional): The Operations method.
            Defaults to None.

    Returns:
        Field: The created Operation
    """
    # parse parameters
    api = obj.api

    obj = api.parent

    operation = Operation()
    operation.parent = api
    operation.domain_object = obj
    operation.domain_parent = parent_obj

    if method == "getA":
        name = "get" + name_builder(obj, parent_obj if duplicate else None, "For", "s")
        path = path_builder(obj, parent_obj, False)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "GET"
        operation.is_array = True
        operation.is_pageable = True

        operation.summary = f"List {pluralize(obj.name)}"

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = query_argument_builder(operation, obj)
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "post":
        name = "create" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, False)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "POST"

        operation.summary = f"Create a {obj.name}"

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = body_argument_builder(operation, obj)
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "get":
        name = "get" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, True)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "GET"

        operation.summary = f"Read the specified {obj.name}"

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "put":
        name = "replace" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, True)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "PUT"

        operation.summary = f"Replace the specified {obj.name}"

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = body_argument_builder(operation, obj)
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "patch":
        name = "update" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, True)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "PATCH"

        operation.summary = f"Update the specified {obj.name}"

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = body_argument_builder(operation, obj)
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "delete":
        name = "delete" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, True)

        operation.name = name
        operation.value = None
        operation.path = path
        operation.method = "DELETE"

        operation.summary = f"Delete the specified {obj.name}"

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "add":
        name = "add" + name_builder(obj, parent_obj if duplicate else None, "To")
        path = path_builder(obj, parent_obj, True) + "/add"

        operation.name = name
        operation.value = None
        operation.path = path
        operation.method = "POST"

        operation.summary = f"Add {obj.name}"

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "remove":
        name = "remove" + name_builder(obj, parent_obj if duplicate else None, "From")
        path = path_builder(obj, parent_obj, True) + "/remove"

        operation.name = name
        operation.value = None
        operation.path = path
        operation.method = "POST"

        operation.summary = f"Remove {obj.name}"

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    return operation


def api_builder(
    obj: Object,
    parent_obj: Object = None,
    aggregation: bool = False,
    duplicate: bool = False,
) -> Object:
    """Creates and adds Operations for an Object.

    Args:
        obj (Object): The entity.Object.
        parent_obj (Object, optional):  The parent Object if any.
            Defaults to None.
        aggregation (bool, optional): Aggregations don't follow the CRUD pattern.
            Defaults to False.
        duplicate (bool, optional): Wether we want to dervice the Operation name from a parent.
            Defaults to False.

    Returns:
        Object: The entity.Object.
    """
    methods = []

    if aggregation:
        methods = ["getA", "add", "remove"]
    else:
        methods = ["getA", "post", "get", "put", "patch", "delete"]

    # it is importent here to only create the api once because
    # we might loop multiple times over this object to add
    # aggregations and compositions
    if not obj.api:
        obj.api = Api()
        obj.api.namespace = obj.namespace
        obj.api.parent = obj

    for method in methods:
        operation = operation_builder(obj, parent_obj, duplicate, method)
        obj.api.operations.append(operation)

    return obj


def parse_objects(schema: Schema):
    """Completes the parsed QSDL schema by creating Operations for each Object.

    Needs to be called before parse_operations.

    Args:
        schema (Schema): The QSDL schema model.
    """
    objects = xtx.get_children_of_type("Object", schema)
    bases = xtx.get_children_of_type("Base", schema)

    # inherit all fields of parent objects
    for entity in bases+ objects:
        entity.fields = get_all_fields_as_list(entity)

    # add id fields for all objects
    for obj in objects:
        id_field = id_builder(obj)
        obj.fields.insert(0, id_field)

    # filter custom definitions and add default apis for the rest
    objects = list(filter(lambda x: not x.api, objects))
    for obj in objects:

        # flag crud object
        obj.is_crud = True

        # aggregations
        agg_fields = get_aggregation(schema, obj)
        duplicate = len(agg_fields) > 1

        # build aggregations
        for field in agg_fields:
            obj = api_builder(obj, field.parent, True, True)

        # compositions
        comp_fields = get_compositions(schema, obj)
        duplicate = len(comp_fields) > 1

        # build compositions
        for field in get_compositions(schema, obj):
            obj = api_builder(obj, field.parent, False, duplicate)

        # build root objects
        if not comp_fields:
            obj = api_builder(obj)


def parse_operations(schema: Schema):
    """Completes the parsed QSDL schema by adding default and missing information to Apis.

    Needs to be called before parse_objects.

    Args:
        schema (Schema): The QSDL schema model.
    """
    apis = xtx.get_children_of_type("Api", schema)

    # loop over user defined APIs
    for api in apis:

        # pass down namespace of object to api
        if api.parent._tx_fqn == "entity.Object" and not api.namespace:
            api.namespace = api.parent.namespace

        # loop over operation per API
        for operation in api.operations:

            # assign get if no other method is specified
            if not operation.method:
                operation.method = "GET"

            # remove void return values
            if operation.value.name == "Void":
                operation.value = None

            operation.path = path_builder(operation)

            # fetch and add path parameters
            id_arguments = path_argument_builder(operation)
            operation.arguments = id_arguments + operation.arguments

            # loop over operation arguments
            for argument in operation.arguments:

                # set the argument type
                if argument.value.name == "ID":
                    argument.is_path = True
                elif operation.method == "GET":
                    argument.is_query = True
                else:
                    argument.is_body = True

            operation.summary = operation.name
