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

from typing import List, Union

from textx import model as xtx

from qsdl.dsl.models import Api, Argument, Base, Field, Object, Scalar, Schema
from qsdl.dsl.models.operation import Operation
from qsdl.filter import pluralize


def get_id(entity: Union[Operation, Object, Base]) -> str:
    """Returns the name of the ID of a Objects or Api or None if no ID exists.

    The supertype of Base|Objects is searched as well.

    Args:
        entity (Union[Field, Object]): Either entity.Object or entity.Field.

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

    elif entity._tx_fqn == "entity.Operation":

        for argument in entity.arguments:
            if argument.value.name == "ID":
                return argument.name

    return field_entity_name


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
    """Returns all Fields whos value is this Object.

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

    tmp = obj
    while True:
        for field in tmp.fields:
            if field.is_query:
                fields.append(field)

        if tmp.supertype:
            tmp = tmp.supertype
        else:
            break

    return fields


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
            path = path + "/{" + get_id(entity) + "}"

        if parent_obj:
            path = "/" + pluralize(parent_obj.name) + "/{" + parent_obj.name + "_" + get_id(parent_obj) + "}" + path

    elif entity._tx_fqn == "entity.Operation":

        if entity.path:
            path = entity.path
        else:
            path = pluralize(entity.parent.parent.name)

        if not path.startswith("/"):
            path = "/" + path

        if get_id(entity):
            path = path + "/{" + get_id(entity) + "}"

        if parent_obj:
            path = "/" + pluralize(parent_obj.name) + "/{" + parent_obj.name + "_" + get_id(parent_obj) + "}" + path

    return path.lower()


def path_argument_builder(
    operation: Operation,
    obj: Object,
    parent_obj: Object = None,
    include_id: bool = False,
) -> List[Argument]:
    """Creates and returns the path arguments for a operation.

    Args:
        operation (Operation): The entity.Operation.
        obj (Object): The entity.Object the entity.Operation belongs to.
        parent_obj (Object, optional): The parent, entity.Object.
            Defaults to None.
        include_id (bool, optional): Enables the inclusion of the own ID.
            Defaults to False.

    Returns:
        List[Argument]: [entity.Argument]
    """
    arguments = []

    if parent_obj:
        argument = Argument()
        argument.parent = operation

        argument.name = parent_obj.name.lower() + "_" + get_id(parent_obj)
        argument.value = Scalar(name="ID")
        argument.path = True
        argument.is_required = True

        arguments.append(argument)

    if include_id:
        argument = Argument()
        argument.parent = operation

        argument.name = get_id(obj)
        argument.value = Scalar(name="ID")
        argument.path = True
        argument.is_required = True

        arguments.append(argument)

    return arguments


def query_argument_builder(
    operation: Operation,
    obj: Object,
) -> List[Argument]:
    """Creates and returns the query arguments for a operation.

    Args:
        operation (Operation): The entity.Operation.
        obj (Object): The entity.Object the entity.Operation belongs to.

    Returns:
        List[Argument]: [entity.Argument]
    """
    arguments = []

    query_fields = get_query_fields(obj)

    for operation in query_fields:
        argument = Argument()
        argument.parent = operation

        argument.name = operation.name
        argument.value = operation.value
        argument.is_query = True

        arguments.append(argument)

    return arguments


def body_argument_builder(
    operation: Operation,
    obj: Object,
    aggregation: bool = False,
) -> List[Argument]:
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

    if aggregation:
        argument.name = get_id(obj)
        argument.value = Scalar(name="ID")
        argument.body = True
        argument.is_required = True
    else:
        argument.name = "body"
        argument.value = obj
        argument.body = True

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

    if method == "getA":
        name = "get" + name_builder(obj, parent_obj if duplicate else None, "For", "s")
        path = path_builder(obj, parent_obj, False)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "GET"
        # field.array = True # disabled if we use pagination
        operation.is_pageable = True

        operation.summary = f"List {pluralize(obj.name)}"

        operation.path_parameters = path_argument_builder(operation, obj, parent_obj, False)
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

        operation.path_parameters = path_argument_builder(operation, obj, parent_obj, False)
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

        operation.path_parameters = path_argument_builder(operation, obj, parent_obj, True)
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

        operation.path_parameters = path_argument_builder(operation, obj, parent_obj, True)
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

        operation.path_parameters = path_argument_builder(operation, obj, parent_obj, True)
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

        operation.path_parameters = path_argument_builder(operation, obj, parent_obj, True)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "add":
        name = "add" + name_builder(obj, parent_obj if duplicate else None, "To")
        path = path_builder(obj, parent_obj, False) + "/add"

        operation.name = name
        operation.value = None
        operation.path = path
        operation.method = "POST"

        operation.summary = f"Add {obj.name}"

        operation.path_parameters = path_argument_builder(operation, obj, parent_obj, False)
        operation.query_parameters = []
        operation.body_parameters = body_argument_builder(operation, obj, True)
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == "remove":
        name = "remove" + name_builder(obj, parent_obj if duplicate else None, "From")
        path = path_builder(obj, parent_obj, False) + "/remove"

        operation.name = name
        operation.value = None
        operation.path = path
        operation.method = "POST"

        operation.summary = f"Remove {obj.name}"

        operation.path_parameters = path_argument_builder(operation, obj, parent_obj, False)
        operation.query_parameters = []
        operation.body_parameters = body_argument_builder(operation, obj, True)
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

    obj_id = get_id(obj)

    if obj_id and aggregation:
        methods = ["getA", "add", "remove"]
    elif aggregation:
        methods = ["getA"]
    elif obj_id:
        methods = ["getA", "post", "get", "put", "patch", "delete"]
    else:
        methods = ["getA", "post"]

    if not obj.api:
        obj.api = Api()
        obj.api.namespace = obj.namespace
        obj.api.parent = obj

    for method in methods:
        operation = operation_builder(obj, parent_obj, duplicate, method)
        obj.api.operations.append(operation)

    # pass down namespace of object to api
    obj.api.namespace = obj.namespace

    return obj


def parse_objects(schema: Schema):
    """Completes the parsed QSDL schema by creating Operations for each Object.

    Needs to be called before parse_operations.

    Args:
        schema (Schema): The QSDL schema model.
    """
    objects = xtx.get_children_of_type("Object", schema)
    objects = list(filter(lambda x: not x.api, objects))

    # loop over user defined Objects
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

            append_id = bool(get_id(operation))
            operation.path = path_builder(operation, None, append_id)

            # loop over operation arguments
            for argument in operation.arguments:

                # set the argument type
                if argument.value.name == "ID":
                    argument.path = True
                elif operation.method == "GET":
                    argument.is_query = True
                else:
                    argument.body = True

            operation.summary = operation.name
