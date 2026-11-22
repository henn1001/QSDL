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
from collections.abc import Iterator

from textx import get_location
from textx.exceptions import TextXSemanticError

import qsdl.dsl.textx as xtx
import qsdl.dsl.util as qutil
from qsdl import dsl, logger
from qsdl.casing import pluralize
from qsdl.dsl.directives import CONSUMES, FORCE_GENERATE, METHOD, NAMESPACE, PAGINATION, PATH, PRODUCES, READ_ONLY
from qsdl.exceptions import QsdlException

from . import CrudGeneratorEnum as CrudEnum
from .directive_parser import complete_response_headers

log = logger.getLogger(__name__)


def resolve_fields(schema: dsl.Schema) -> None:
    """Resolve the extends graph parent-first, without changing declaration containment."""
    resolved: set[int] = set()
    for entity in schema.types:
        if not isinstance(entity, dsl.Base | dsl.Object) or id(entity) in resolved:
            continue
        stack: list[tuple[dsl.Base | dsl.Object, Iterator[dsl.Base]]] = [(entity, iter(entity.supertypes))]
        active = {id(entity): 0}
        while stack:
            current, parents = stack[-1]
            parent = next(parents, None)
            if parent is None:
                current._resolved_fields = _merge_fields(current)
                resolved.add(id(current))
                del active[id(current)]
                stack.pop()
            elif id(parent) in active:
                cycle = [node.name for node, _ in stack[active[id(parent)] :]] + [parent.name]
                msg = f"Circular inheritance detected in Base supertypes: {' -> '.join(cycle)}"
                raise TextXSemanticError(msg, **get_location(parent))
            elif id(parent) not in resolved:
                active[id(parent)] = len(stack)
                stack.append((parent, iter(parent.supertypes)))


def _merge_fields(entity: dsl.Base | dsl.Object) -> tuple[dsl.Field, ...]:
    inherited: dict[str, list[dsl.Field]] = {}
    overrides = {field.name for field in entity.fields if field.directive.is_override}
    for parent in entity.supertypes:
        for field in parent.effective_fields:
            candidates = inherited.setdefault(field.name, [])
            if any(field is candidate for candidate in candidates):
                continue
            if candidates and field.name not in overrides:
                _raise_field_redefinition(entity, candidates[0], field)
            candidates.append(field)

    fields = {name: candidates[0] for name, candidates in inherited.items()}
    for field in entity.fields:
        duplicate = fields.get(field.name)
        if duplicate is not None and not field.directive.is_override:
            _raise_field_redefinition(entity, duplicate, field)
        fields[field.name] = field

        changed = next((other for other in inherited.get(field.name, ()) if other.value is not field.value), None)
        if changed is not None:
            log.warning(
                "The inherited field '%s' of '%s' was redefined with a different type by '%s'.",
                changed.name,
                changed.parent.name,
                entity.name,
            )
    return tuple(fields.values())


def _raise_field_redefinition(entity: dsl.Base | dsl.Object, first: dsl.Field, other: dsl.Field) -> None:
    log.error(
        "The field '%s' of '%s' conflicts with a declaration in '%s' while resolving '%s'.",
        first.name,
        first.parent.name,
        other.parent.name,
        entity.name,
    )
    raise TextXSemanticError("Field redefinition without @override is not allowed.", **get_location(other))


def id_builder(obj: dsl.Object) -> dsl.Field:
    """Creates and returns a ID field.

    Args:
        obj (dsl.Object): entity.dsl.Object

    Returns:
        dsl.Field: entity.dsl.Field
    """
    field = dsl.Field(parent=obj, name="id", value=dsl.Scalar(name="ID"))
    field.directives.attach_synthetic(READ_ONLY, True)
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
    entity: dsl.Object,
    parent_obj: dsl.Object | None = None,
    append_id: bool = False,
) -> str:
    """Creates and returns the path string for a operation.

    Args:
        entity (dsl.Object): Object for which a CRUD route is generated.
        parent (dsl.Object, optional): The parent, entity.dsl.Object.
            Defaults to None.
        include_id (bool, optional): Enables the inclusion of the own ID.
            Defaults to False.

    Returns:
        str: The path string as used by OpenApi.
    """
    path = pluralize(entity.name)

    if not path.startswith("/"):
        path = "/" + path

    if append_id:
        path = path + "/{id}"

    if parent_obj:
        path = "/" + pluralize(parent_obj.name) + "/{" + parent_obj.name + "_id}" + path

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
    matches = re.findall(regex, operation.directive.path.value)

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

    query_fields = qutil.get_query_fields(obj.effective_fields)

    for field in query_fields:
        argument = dsl.Argument(operation, field.name, field.value)
        argument.is_query = True
        argument.is_array = field.directive.is_query_list

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
        raise QsdlException("The object must have an api instance before creating operations.")

    # parse parameters
    # api = obj.api

    # We need to set name later, so we'll set it to a temporary value first
    operation = dsl.Operation(parent=obj.api, name="temp")
    operation.domain_object = obj
    operation.domain_parent = parent_obj
    operation.is_generated = True

    if method == CrudEnum.GET_ALL:
        name = "get" + name_builder(obj, parent_obj if duplicate else None, "For", "s")
        path = path_builder(obj, parent_obj, False)

        operation.name = name
        operation.value = obj
        operation.directives.attach_synthetic(PATH, path)
        operation.directives.attach_synthetic(METHOD, "GET")
        operation.is_array = True
        operation.directives.attach_synthetic(PAGINATION, True)

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
        operation.directives.attach_synthetic(PATH, path)
        operation.directives.attach_synthetic(METHOD, "POST")

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
        operation.directives.attach_synthetic(PATH, path)
        operation.directives.attach_synthetic(METHOD, "GET")

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
        operation.directives.attach_synthetic(PATH, path)
        operation.directives.attach_synthetic(METHOD, "PATCH")

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
        operation.directives.attach_synthetic(PATH, path)
        operation.directives.attach_synthetic(METHOD, "DELETE")

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
        operation.directives.attach_synthetic(PATH, path)
        operation.directives.attach_synthetic(METHOD, "POST")

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
        operation.directives.attach_synthetic(PATH, path)
        operation.directives.attach_synthetic(METHOD, "POST")

        operation.summary = name
        operation.description = [f"Remove {obj.name}"]

        operation.path_parameters = path_argument_builder(operation)
        operation.query_parameters = []
        operation.body_parameters = []
        operation.arguments = operation.path_parameters + operation.query_parameters + operation.body_parameters

    complete_media_defaults(operation)

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
        if obj.api and (generate := obj.api.directive.generate) and generate.value:
            methods = [method for method in methods if method in generate.value]

    # it is importent here to only create the api once because
    # we might loop multiple times over this object to add
    # aggregations and compositions
    if not obj.api:
        obj.api = dsl.Api(parent=obj)
        inherit_namespace(obj.api)

    for method in methods:
        operation = operation_builder(obj, parent_obj, duplicate, method)
        operation.is_aggregated = aggregation
        obj.api.operations.append(operation)
        obj.api.has_generated = True

    return obj


def retain_used_types(schema: dsl.Schema) -> None:
    """Retain Base and Enum types reachable by value before @ignore filtering."""
    pending: list[tuple[dsl.Base | dsl.Enum, bool]] = []

    def enqueue(value: dsl.Scalar | dsl.Object | dsl.Base | dsl.Enum | None, forced: bool = False) -> None:
        if isinstance(value, dsl.Base | dsl.Enum):
            pending.append((value, forced))

    for entity in schema.types:
        if isinstance(entity, dsl.Base | dsl.Enum) and entity.directive.is_force_generate:
            enqueue(entity, forced=True)
        elif isinstance(entity, dsl.Object):
            for field in entity.effective_fields:
                enqueue(field.value)

    for operation in xtx.get_children_of_operation(schema):
        enqueue(operation.value)
        for argument in operation.arguments:
            enqueue(argument.value)
        if headers := operation.directive.headers:
            for header in headers.value:
                enqueue(header.value)

    reachable: set[int] = set()
    forced_reachable: set[int] = set()
    while pending:
        entity, forced = pending.pop()
        key = id(entity)
        if key in forced_reachable or (not forced and key in reachable):
            continue
        reachable.add(key)
        # A Base already expanded in ordinary mode may still need to propagate force.
        if forced:
            forced_reachable.add(key)
            if not entity.directive.is_force_generate:
                entity.directives.attach_synthetic(FORCE_GENERATE, True)
        if isinstance(entity, dsl.Base):
            for field in entity.effective_fields:
                enqueue(field.value, forced)

    schema.types[:] = [
        entity for entity in schema.types if not isinstance(entity, dsl.Base | dsl.Enum) or id(entity) in reachable
    ]


def add_object_ids(schema: dsl.Schema) -> None:
    """Prepend synthetic IDs to the effective fields, outside declaration containment."""
    for obj in xtx.get_children_of_object(schema):
        obj._resolved_fields = (id_builder(obj), *obj.effective_fields)


def generate_crud(schema: dsl.Schema) -> None:
    """Add automatic CRUD and relationship operations after completing explicit APIs."""
    objects = xtx.get_children_of_object(schema)

    # An explicit object API controls automatic CRUD generation. In particular,
    # an empty API intentionally suppresses all automatic CRUD for that object.
    # Objects without an API, or with @generate, proceed to api_builder.
    for obj in objects:
        if obj.api and (not (generate := obj.api.directive.generate) or not generate.value):
            continue

        # aggregations
        agg_fields = qutil.get_aggregation(schema, obj, include_ignored=True)

        # build aggregations
        for field in agg_fields:
            obj = api_builder(obj, field.parent, True, True)

        # compositions
        comp_fields = qutil.get_compositions(schema, obj, include_ignored=True)
        duplicate = len(comp_fields) > 1

        # build compositions
        for field in comp_fields:
            obj = api_builder(obj, field.parent, False, duplicate)

        # build root objects
        if not comp_fields:
            obj = api_builder(obj)


def complete_operations(schema: dsl.Schema) -> None:
    """Complete the routes, arguments, and typed metadata of declared operations."""
    apis = xtx.get_children_of_api(schema)

    # loop over user defined APIs
    for api in apis:
        inherit_namespace(api)

        # loop over operation per API
        for operation in api.operations:
            # assign get if no other method is specified
            if operation.directive.method is None:
                operation.directives.attach_synthetic(METHOD, "GET")

            # remove void return values
            if operation.value.name == "Void":
                operation.value = None

            path = operation.directive.path.value
            path = path if path.startswith("/") else "/" + path
            operation.directives._complete_source(PATH, path.removesuffix("/").lower())

            # fetch and add path parameters
            id_arguments = path_argument_builder(operation)
            operation.arguments = id_arguments + operation.arguments

            # loop over operation arguments
            for argument in operation.arguments:
                # Explicit locations take precedence over method-based inference.
                if argument.is_path:
                    operation.path_parameters.append(argument)
                elif argument.is_header:
                    operation.header_parameters.append(argument)
                elif argument.is_query:
                    operation.query_parameters.append(argument)
                elif operation.directive.method.value == "GET":
                    argument.is_query = True
                    operation.query_parameters.append(argument)
                else:
                    argument.is_body = True
                    operation.body_parameters.append(argument)

            operation.summary = operation.name

            complete_media_defaults(operation)
            complete_response_headers(schema, operation)


def inherit_namespace(api: dsl.Api) -> None:
    """Attach the owning object's namespace to an API that declares none."""
    if (
        api.directive.namespace is None
        and isinstance(api.parent, dsl.Object)
        and (namespace := api.parent.directive.namespace) is not None
    ):
        api.directives.attach_synthetic(NAMESPACE, namespace.value)


def complete_media_defaults(operation: dsl.Operation) -> None:
    """Attach default @produces and @consumes values that the source omitted."""
    if operation.directive.produces is None and operation.value:
        operation.directives.attach_synthetic(PRODUCES, "application/json")
    if operation.directive.consumes is None and operation.body_parameters:
        merge_patch = operation.is_generated and operation.directive.method.value == "PATCH"
        media = "application/merge-patch+json" if merge_patch else "application/json"
        operation.directives.attach_synthetic(CONSUMES, media)
