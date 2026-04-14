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

"""Model domain parser"""

import re

import qsdl.dsl.textx as xtx
import qsdl.dsl.util as qutil
from qsdl import dsl, logger
from qsdl.filter import pluralize

from . import CrudGeneratorEnum as CrudEnum

log = logger.getLogger(__name__)


def id_builder(obj: dsl.Object) -> dsl.Field:
    """Creates and returns a ID field.

    Args:
        obj (dsl.Object): entity.dsl.Object

    Returns:
        dsl.Field: entity.dsl.Field
    """
    field = dsl.Field(parent=obj, name="id", value=dsl.Scalar(name="ID"))
    field.is_read_only = True
    field.is_required = True

    return field


def name_builder(
    obj: dsl.Object,
    parent_obj: dsl.Object | None = None,
    combiner: str = "For",
    append: str = "",
) -> str:
    """Returns the operation name for CRUD Objects.

    Args:
        obj (dsl.Object): The dsl.Object this operations belongs to.
        parent_obj (dsl.Object, optional): The parent dsl.Object if any.
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
    entity: dsl.Field | dsl.Object,
    parent_obj: dsl.Object | None = None,
    append_id: bool = False,
) -> str:
    """Creates and returns the path string for a operation.

    Args:
        entity (dsl.Field | dsl.Object): Either entity.dsl.Object or entity.dsl.Field.
        parent (dsl.Object, optional): The parent, entity.dsl.Object.
            Defaults to None.
        include_id (bool, optional): Enables the inclusion of the own ID.
            Defaults to False.

    Returns:
        str: The path string as used by OpenApi.
    """
    if isinstance(entity, dsl.Object):
        path = pluralize(entity.name)

        if not path.startswith("/"):
            path = "/" + path

        if append_id:
            path = path + "/{id}"

        if parent_obj:
            path = "/" + pluralize(parent_obj.name) + "/{" + parent_obj.name + "_id}" + path

    elif isinstance(entity, dsl.Operation):
        path = entity.path

        if not path.startswith("/"):
            path = "/" + path

        if path.endswith("/"):
            path = path[:-1]

    return path.lower()


def path_argument_builder(operation: dsl.Operation) -> list[dsl.Argument]:
    """Creates and returns the path arguments for a operation path.

    ID arguments are identified within {brackets}.

    Args:
        operation (dsl.Operation): The entity.dsl.Operation.

    Returns:
        list[dsl.Argument]: [entity.dsl.Argument]
    """
    arguments = []

    regex = r"{(.+?)}+?"
    matches = re.findall(regex, operation.path)

    for match in matches:
        argument = dsl.Argument(operation, match.lower(), dsl.Scalar(name="ID"))
        argument.is_path = True
        argument.is_required = True

        arguments.append(argument)

    return arguments


def query_argument_builder(operation: dsl.Operation, obj: dsl.Object) -> list[dsl.Argument]:
    """Creates and returns the query arguments for a operation.

    Args:
        operation (dsl.Operation): The entity.dsl.Operation.
        obj (dsl.Object): The entity.dsl.Object the entity.dsl.Operation belongs to.

    Returns:
        list[dsl.Argument]: [entity.dsl.Argument]
    """
    arguments = []

    query_fields = qutil.get_query_fields(obj)

    for field in query_fields:
        argument = dsl.Argument(operation, field.name, field.value)
        argument.is_query = True
        argument.is_array = field.is_query_list

        arguments.append(argument)

    return arguments


def body_argument_builder(operation: dsl.Operation, obj: dsl.Object) -> list[dsl.Argument]:
    """Creates and returns the query arguments for a operation.

    Args:
        operation (dsl.Operation): The entity.dsl.Operation.
        obj (dsl.Object): The entity.dsl.Object the entity.dsl.Operation belongs to.
        aggregation (bool, optional): For aggregations, the body containts the aggregated Objects ID.
            Defaults to False.

    Returns:
        list[dsl.Argument]: [entity.dsl.Argument]
    """
    arguments = []

    argument = dsl.Argument(operation, "request", obj)
    argument.is_body = True

    arguments.append(argument)

    return arguments


def operation_builder(
    obj: dsl.Object,
    parent_obj: dsl.Object | None = None,
    duplicate: bool = False,
    method: str | None = None,
) -> dsl.Operation:
    """Creates and returns the dsl.Operation for an dsl.Object.

    Args:
        obj (dsl.Object): The entity.dsl.Object.
        parent_obj (dsl.Object, optional): The parent dsl.Object if any.
            Defaults to None.
        duplicate (bool, optional): Wether we want to dervice the dsl.Operation name from a parent.
            Defaults to False.
        method (str, optional): The Operations method.
            Defaults to None.

    Returns:
        dsl.Field: The created dsl.Operation
    """
    if not obj.api:
        raise Exception("The object must have an api instance before creating operations.")

    # parse parameters
    # api = obj.api

    # We need to set name later, so we'll set it to a temporary value first
    operation = dsl.Operation(parent=obj.api, name="temp", path="temp")
    operation.domain_object = obj
    operation.domain_parent = parent_obj
    operation.is_generated = True

    if method == CrudEnum.GET_ALL:
        name = "get" + name_builder(obj, parent_obj if duplicate else None, "For", "s")
        path = path_builder(obj, parent_obj, False)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "GET"
        operation.is_array = True
        operation.is_pageable = True

        operation.summary = name
        operation.description = [f"List {pluralize(obj.name)}"]

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = query_argument_builder(operation, obj)
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == CrudEnum.CREATE:
        name = "create" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, False)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "POST"

        operation.summary = name
        operation.description = [f"Create a {obj.name}"]

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = body_argument_builder(operation, obj)
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == CrudEnum.GET:
        name = "get" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, True)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "GET"

        operation.summary = name
        operation.description = [f"Read the specified {obj.name}"]

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == CrudEnum.UPDATE:
        name = "update" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, True)

        operation.name = name
        operation.value = obj
        operation.path = path
        operation.method = "PATCH"

        operation.summary = name
        operation.description = [f"Update the specified {obj.name}"]

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = body_argument_builder(operation, obj)
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == CrudEnum.DELETE:
        name = "delete" + name_builder(obj, parent_obj if duplicate else None)
        path = path_builder(obj, parent_obj, True)

        operation.name = name
        operation.value = None
        operation.path = path
        operation.method = "DELETE"

        operation.summary = name
        operation.description = [f"Delete the specified {obj.name}"]

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == CrudEnum.ADD:
        name = "add" + name_builder(obj, parent_obj if duplicate else None, "To")
        path = path_builder(obj, parent_obj, True) + "/add"

        operation.name = name
        operation.value = None
        operation.path = path
        operation.method = "POST"

        operation.summary = name
        operation.description = [f"Add {obj.name}"]

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    elif method == CrudEnum.REMOVE:
        name = "remove" + name_builder(obj, parent_obj if duplicate else None, "From")
        path = path_builder(obj, parent_obj, True) + "/remove"

        operation.name = name
        operation.value = None
        operation.path = path
        operation.method = "POST"

        operation.summary = name
        operation.description = [f"Remove {obj.name}"]

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    # add produces/consumes
    operation.produces = "application/json" if operation.value else None
    operation.consumes = "application/json" if operation.body_parameters else None
    operation.consumes = "application/merge-patch+json" if operation.method == "PATCH" else operation.consumes

    return operation


def api_builder(
    obj: dsl.Object,
    parent_obj: dsl.Object | None = None,
    aggregation: bool = False,
    duplicate: bool = False,
) -> dsl.Object:
    """Creates and adds Operations for an dsl.Object.

    Args:
        obj (dsl.Object): The entity.dsl.Object.
        parent_obj (dsl.Object, optional):  The parent dsl.Object if any.
            Defaults to None.
        aggregation (bool, optional): Aggregations don't follow the CRUD pattern.
            Defaults to False.
        duplicate (bool, optional): Wether we want to derive the dsl.Operation name from a parent.
            Defaults to False.

    Returns:
        dsl.Object: The entity.dsl.Object.
    """
    methods = []

    if aggregation:
        methods = [
            CrudEnum.GET_ALL,
            CrudEnum.ADD,
            CrudEnum.REMOVE,
        ]
    else:
        methods = [
            CrudEnum.GET_ALL,
            CrudEnum.CREATE,
            CrudEnum.GET,
            CrudEnum.UPDATE,
            CrudEnum.DELETE,
        ]

        # allow selective generation if requested
        if obj.api and obj.api.generate:
            methods = [x for x in methods if x in obj.api.generate]

    # it is importent here to only create the api once because
    # we might loop multiple times over this object to add
    # aggregations and compositions
    if not obj.api:
        obj.api = dsl.Api(parent=obj, namespace=obj.namespace)

    for method in methods:
        operation = operation_builder(obj, parent_obj, duplicate, method)
        operation.is_aggregated = aggregation
        obj.api.operations.append(operation)
        obj.api.has_generated = True

    return obj


def is_used(schema: dsl.Schema, entity: dsl.Base | dsl.Enum) -> bool:
    """Checks if the provided dsl.Base or dsl.Enum is used anywhere.

    Args:
        schema (dsl.Schema): The QSDL schema model.
        entity (dsl.Base | dsl.Enum): Either entity.Base or entity.dsl.Enum.

    Returns:
        bool: True when used.
    """
    entity_list = []

    # handle @force-generate
    # we generate this regardless
    is_force_used = qutil.get_directive_of_name("force-generate", entity)

    if is_force_used:
        return True

    # we can safely check the direct usage for api operations
    entity_list += xtx.get_children_of_operation(schema)
    entity_list += xtx.get_children_of_argument(schema)

    # for objects, we first check all fields
    obj_list = xtx.get_children_of_object(schema)

    for obj in obj_list:
        entity_list += obj.fields

    for itr in entity_list:
        if itr.value == entity:
            return True

        # for nested entities, we extend the base.fields to the list
        # Note: we modify the list we are iterating on purpose
        if itr.value and isinstance(itr.value, dsl.Base):
            entity_list.extend(itr.value.fields)

    return False


def remove_unused(schema: dsl.Schema) -> None:
    """Get rid of all dangling Base and Enum entities.

    Args:
        schema (dsl.Schema): The QSDL schema model.
    """
    bases = xtx.get_children_of_base(schema)
    enums = xtx.get_children_of_enum(schema)

    for entity in bases + enums:
        used = is_used(schema, entity)

        if not used:
            schema.types.remove(entity)

    enums = xtx.get_children_of_enum(schema)


def remove_ignored(schema: dsl.Schema) -> None:
    """Get rid of all fields marked with the @ignore directive.

    Args:
        schema (dsl.Schema): The QSDL schema model.
    """

    bases = xtx.get_children_of_base(schema)
    objects = xtx.get_children_of_object(schema)

    for entity in objects + bases:
        for field in [x for x in entity.fields if x.is_ignored]:
            entity.fields.remove(field)
            log.info(
                "The field '%s' of '%s' was marked with @ignore and removed from generation.",
                field.name,
                entity.name,
            )


def inherit_force_generation(schema: dsl.Schema) -> None:
    """Inherits the force-generate directive to all childs

    Args:
        schema (dsl.Schema): The QSDL schema model.
    """
    bases = xtx.get_children_of_base(schema)

    forced_bases = [x for x in bases if qutil.get_directive_of_name("force-generate", x)]

    def recurser(base: dsl.Base) -> None:
        matched_entity = [x.value for x in base.fields if isinstance(x.value, dsl.Base | dsl.Enum)]

        for entity in matched_entity:
            entity.directives.append(dsl.Directive(entity, name="force-generate"))

            if isinstance(entity, dsl.Base):
                recurser(entity)

    for base in forced_bases:
        recurser(base)


def parse_objects(schema: dsl.Schema) -> None:
    """Completes the parsed QSDL schema by creating Operations for each dsl.Object.

    Needs to be called before parse_operations.

    Args:
        schema (dsl.Schema): The QSDL schema model.
    """
    objects = xtx.get_children_of_object(schema)
    bases = xtx.get_children_of_base(schema)

    # inherit all fields of parent objects
    for entity in bases + objects:
        entity.fields = qutil.get_all_fields_as_list(entity)
        entity.flattened = True

    # add id fields for all objects
    for obj in objects:
        id_field = id_builder(obj)
        obj.fields.insert(0, id_field)

    # we want to generate apis for all types that do not overwrite the api
    # or specify the generate directive
    objects = list(filter(lambda x: not x.api or x.api.generate, objects))
    for obj in objects:
        # aggregations
        agg_fields = qutil.get_aggregation(schema, obj)
        duplicate = len(agg_fields) > 1

        # build aggregations
        for field in agg_fields:
            obj = api_builder(obj, field.parent, True, True)

        # compositions
        comp_fields = qutil.get_compositions(schema, obj)
        duplicate = len(comp_fields) > 1

        # build compositions
        for field in qutil.get_compositions(schema, obj):
            obj = api_builder(obj, field.parent, False, duplicate)

        # build root objects
        if not comp_fields:
            obj = api_builder(obj)


def parse_operations(schema: dsl.Schema) -> None:
    """Completes the parsed QSDL schema by adding default and missing information to Apis.

    Needs to be called before parse_objects.

    Args:
        schema (dsl.Schema): The QSDL schema model.
    """
    apis = xtx.get_children_of_api(schema)

    # loop over user defined APIs
    for api in apis:
        # pass down namespace of object to api
        if isinstance(api.parent, dsl.Object) and not api.namespace:
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
                    operation.path_parameters.append(argument)
                elif operation.method == "GET" or argument.is_query:
                    argument.is_query = True
                    operation.query_parameters.append(argument)
                elif argument.is_header:
                    operation.header_parameters.append(argument)
                else:
                    argument.is_body = True
                    operation.body_parameters.append(argument)

            operation.summary = operation.name

            # add produces/consumes
            if not operation.produces:
                operation.produces = "application/json" if operation.value else None

            if not operation.consumes:
                operation.consumes = "application/json" if operation.body_parameters else None
