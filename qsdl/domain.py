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

"""Domain specific functions"""

from copy import copy

from textx import model as mfunc

from qsdl import config
from qsdl.util import get_id
from qsdl.util import get_id_field
from qsdl.util import get_childs
from qsdl.util import get_path_base
from qsdl.util import get_path_parameters
from qsdl.util import get_query_parameters
from qsdl.util import get_request_parameters
from qsdl.util import get_operation_id
from qsdl.util import get_operation_method
from qsdl.util import is_aggregation
from qsdl.util import get_aggregation
from qsdl.util import get_compositions
from qsdl.util import pluralize
from qsdl.util import Operation


def operation_helper(entity: object) -> tuple:
    """Returns namespace, d_parent and d_childs.

    Args:
        entity (object): entity.Object

    Returns:
        tuple: namespace, d_parent,d_childs.
    """

    namespace = None
    if entity.namespace:
        namespace = entity.namespace

    d_parent = None
    if hasattr(entity, "d_parent"):
        d_parent = entity.d_parent

    d_childs = None
    if hasattr(entity, "d_childs"):
        d_childs = entity.d_childs

    return namespace, d_parent, d_childs


def operation_helper_response(obj: object, array: bool = False) -> dict:
    """Returns the response field for CRUD operations.

    Args:
        obj (object): entity.Object
        array (bool, optional): Wether it should be a Array. Defaults to False.

    Returns:
        dict: The simplified response Field.
    """
    return {
        "readOnly": False,
        "writeOnly": False,
        "array": array,
        "value": obj,
    }


def get_custom_operation(entity: object, field: object, method: str) -> Operation:
    """Returns a custom Operation object for Queries and Mutation fields.

    Args:
        entity (object): entity.Object | entity.Query | entity.Mutation
        field (object): entity.Field
        method (str): The operations method.

    Returns:
        Operation: Operation
    """
    namespace, d_parent, d_childs = operation_helper(entity)

    if method == "get":
        name = field.name
        summary = field.name
        path = get_path_base(field, d_parent)
        method = "get"
        parameters = get_path_parameters(field, d_parent)
        parameters.extend(get_query_parameters(field))
        request = None
        response = field

    if method == "post":
        name = field.name
        summary = field.name
        path = get_path_base(field, d_parent)
        method = "post"
        parameters = get_path_parameters(field, d_parent)
        request = get_request_parameters(field)
        response = field

    if method == "put":
        name = field.name
        summary = field.name
        path = get_path_base(field, d_parent)
        method = "put"
        parameters = get_path_parameters(field, d_parent)
        request = get_request_parameters(field)
        response = field

    if method == "delete":
        name = field.name
        summary = field.name
        path = get_path_base(field, d_parent)
        method = "delete"
        parameters = get_path_parameters(field, d_parent)
        request = None
        response = field

    # build operation
    opr = Operation()
    opr.name = name
    opr.ref = entity
    opr.tag = namespace
    opr.summary = summary
    opr.description = field.description
    opr.path = path
    opr.method = method
    opr.parameters = parameters
    opr.request = request
    opr.response = response
    opr.parent = d_parent
    opr.childs = d_childs

    return opr


def build_custom_queries(entities: list) -> list:
    """Returns a list of operations for custom Queries and Mutations.

    Args:
        entities (list): [entity.Object | entity.Query | entity.Mutation]

    Returns:
        list: [Operation]
    """
    operations = []

    for entity in entities:

        fields = []

        if entity._tx_fqn == "entity.Object":
            if entity.query:
                fields.extend(entity.query.fields)
            if entity.mutation:
                fields.extend(entity.mutation.fields)

        if entity._tx_fqn in ["entity.Query", "entity.Mutation"]:
            fields.extend(entity.fields)

        for field in fields:

            method = get_operation_method(field)

            opr = get_custom_operation(entity, field, method)

            operations.append(opr)

    return operations


def get_crud_operation_aggregation(obj: object, method: str) -> Operation:
    """Returns a CRUD Operation object for a aggregation depending on the method.

    Args:
        obj (object): entity.Object
        method (str): The operations method.

    Returns:
        Operation: Operation
    """
    namespace, d_parent, d_childs = operation_helper(obj)

    if method == "getA":
        name = "get" + get_operation_id(obj, "s")
        summary = f"List {pluralize(obj.name)}"
        path = get_path_base(obj, obj.d_parent)
        method = "get"
        parameters = get_path_parameters(obj, obj.d_parent)
        parameters.extend(get_query_parameters(obj))
        request = None
        response = operation_helper_response(obj, True)

    elif method == "post":
        name = "add" + get_operation_id(obj)
        summary = f"Add {obj.name}"
        path = get_path_base(obj, obj.d_parent) + "/add"
        method = "post"
        parameters = get_path_parameters(obj, obj.d_parent)
        request = [get_id_field(obj)]
        response = None

    elif method == "delete":
        name = "remove" + get_operation_id(obj)
        summary = f"Remove {obj.name}"
        path = get_path_base(obj, obj.d_parent) + "/remove"
        method = "post"
        parameters = get_path_parameters(obj, obj.d_parent)
        request = [get_id_field(obj)]
        response = None

    # build operation
    opr = Operation()
    opr.name = name
    opr.ref = obj
    opr.tag = namespace
    opr.summary = summary
    opr.description = None
    opr.path = path
    opr.method = method
    opr.parameters = parameters
    opr.request = request
    opr.response = response
    opr.parent = d_parent
    opr.childs = d_childs

    return opr


def get_crud_operation(obj: object, method: str) -> Operation:
    """Returns a CRUD Operation object depending on the method.

    Args:
        obj (object): entity.Object
        method (str): The operations method.

    Returns:
        Operation: Operation
    """
    namespace, d_parent, d_childs = operation_helper(obj)

    if method == "getA":
        name = "get" + get_operation_id(obj, "s")
        summary = f"List {pluralize(obj.name)}"
        path = get_path_base(obj, obj.d_parent)
        method = "get"
        parameters = get_path_parameters(obj, obj.d_parent)
        parameters.extend(get_query_parameters(obj))
        request = None
        response = operation_helper_response(obj, True)

    elif method == "post":
        name = "create" + get_operation_id(obj)
        summary = f"Create a {obj.name}"
        path = get_path_base(obj, obj.d_parent)
        method = "post"
        parameters = get_path_parameters(obj, obj.d_parent)
        request = get_request_parameters(obj)
        response = operation_helper_response(obj)

    elif method == "get":
        name = "get" + get_operation_id(obj)
        summary = f"Read the specified {obj.name}"
        path = get_path_base(obj, obj.d_parent, True)
        method = "get"
        parameters = get_path_parameters(obj, obj.d_parent, True)
        request = None
        response = operation_helper_response(obj)

    elif method == "put":
        name = "update" + get_operation_id(obj)
        summary = f"Update the specified {obj.name}"
        path = get_path_base(obj, obj.d_parent, True)
        method = "put"
        parameters = get_path_parameters(obj, obj.d_parent, True)
        request = get_request_parameters(obj)
        response = operation_helper_response(obj)

    elif method == "delete":
        name = "delete" + get_operation_id(obj)
        summary = f"Delete the specified {obj.name}"
        path = get_path_base(obj, obj.d_parent, True)
        method = "delete"
        parameters = get_path_parameters(obj, obj.d_parent, True)
        request = None
        response = None

    # build operation
    opr = Operation()
    opr.name = name
    opr.ref = obj
    opr.tag = namespace
    opr.summary = summary
    opr.description = None
    opr.path = path
    opr.method = method
    opr.parameters = parameters
    opr.request = request
    opr.response = response
    opr.parent = d_parent
    opr.childs = d_childs

    return opr


def build_crud(objects: list) -> list:
    """Returns a list of operations for CRUD Objects.

    Args:
        objects (list): [entity.Object]

    Returns:
        list: [Operations]
    """
    operations = []

    for obj in objects:

        if is_aggregation(obj, obj.d_parent):
            for method in ["getA", "post", "delete"]:
                opr = get_crud_operation_aggregation(obj, method)
                operations.append(opr)

        elif get_id(obj):
            for method in ["getA", "post", "get", "put", "delete"]:
                opr = get_crud_operation(obj, method)
                operations.append(opr)

        else:
            for method in ["getA", "post"]:
                opr = get_crud_operation(obj, method)
                operations.append(opr)

    return operations


def check_duplicates():
    """Adds operation names to the global list and flags duplicates.

    This is needed in order to identify if we need to derive operation names
    from their parents.

    e.g. addUserForRole
    """
    config.dupl_objects = set()
    seen = set()

    for obj in config.domain_objects:
        if obj.name not in seen:
            seen.add(obj.name)
        else:
            config.dupl_objects.add(obj.name)


def get_endpoints() -> list:
    """Returns all possible endpoints/paths for OpenAPI.

    Returns:
        list: [entity.Object]
    """
    endpoints = []

    objects = mfunc.get_children_of_type("Object", config.model)

    for obj in objects:

        is_root = True

        comp_fields = get_compositions(obj)

        for field in comp_fields:
            tmp = copy(obj)
            tmp.d_parent = field.parent
            tmp.d_childs = get_childs(obj)
            endpoints.append(tmp)

            is_root = False

        agg_fields = get_aggregation(obj)

        for field in agg_fields:
            tmp = copy(obj)
            tmp.d_parent = field.parent
            tmp.d_childs = get_childs(obj)
            endpoints.append(tmp)

        if is_root:
            tmp = copy(obj)
            tmp.d_parent = None
            tmp.d_childs = get_childs(obj)
            endpoints.append(tmp)

    return endpoints


def build_domain_model(model: object):
    """Convert the model into a OpenAPI path/operation graph.

    Args:
        model (object): The python object graph.
    """
    operations = []

    config.model = model

    config.domain_objects = get_endpoints()
    check_duplicates()

    tmp = mfunc.get_children_of_type("Query", config.model)
    tmp.extend(mfunc.get_children_of_type("Mutation", config.model))

    # crud objects
    objects = []
    objects.extend(list(filter(lambda x: not x.query and not x.mutation, config.domain_objects)))
    crud_operations = build_crud(objects)
    operations.extend(crud_operations)

    # custom queries/mutations
    entities = []
    entities.extend(list(filter(lambda x: x.parent._tx_fqn != "entity.Object", tmp)))
    entities.extend(list(filter(lambda x: x.query or x.mutation, config.domain_objects)))
    custom_operations = build_custom_queries(entities)
    operations.extend(custom_operations)

    operations.sort(key=lambda x: x.path)

    config.operations = operations
