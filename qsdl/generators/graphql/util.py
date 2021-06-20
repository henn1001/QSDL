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

"""GraphQL Generator Utility functions"""

from textx import model as xtx

from qsdl.dsl.models import Schema

# the parsed schema definition.
schema: Schema = None


def get_operations_of_object_of_queries(obj: object) -> list:
    """Return all operations for this Object with method == get

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """
    operations = list(filter(lambda x: x.method == "GET", obj.api.fields))

    return operations


def get_operations_of_object_of_mutations(obj: object) -> list:
    """Return all operations for this Object with method != get

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """
    operations = list(filter(lambda x: x.method != "GET", obj.api.fields))

    return operations


def get_queries_of_operation(api: object) -> list:
    """Return all operations for this Object with method == get

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """
    operations = list(filter(lambda x: x.method == "GET", api.fields))

    return operations


def get_mutations_of_operation(api: object) -> list:
    """Return all operations for this Object with method != get

    Args:
        obj (object): entity.Object

    Returns:
        list: [Operations]
    """
    operations = list(filter(lambda x: x.method != "GET", api.fields))

    return operations


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
            (field.is_composition and field.value._tx_fqn == "entity.Object")
            or (field.is_aggregation and field.value._tx_fqn == "entity.Object")
        )
        and not field.is_nested
    ):
        ret = True

    return ret


def is_nested(entity: object) -> bool:
    """Checks if the provided object or base is nested.

    Args:
        entity (object): entity.Object or entity.Base

    Returns:
        bool: [description]
    """
    ret = False

    for field in xtx.get_children_of_type("Field", schema):
        if field.value == entity:
            if field.is_nested:
                ret = True
                break

    # for arg in xtx.get_children_of_type("Argument", Config.schema):
    #     if arg.value == entity:
    #         ret = True
    #         break

    return ret
