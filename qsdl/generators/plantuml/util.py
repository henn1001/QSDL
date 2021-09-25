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

"""PlantUML Generator Utility functions"""

import qsdl.dsl.textx as xtx
from qsdl.dsl.models import Field, Schema

# the parsed schema definition.
schema: Schema = None


def get_compositions(obj: object) -> list:
    """Return all Objects who are using this Object as composition.

    Args:
        obj (object): entity.Object

    Returns:
        list: [entity.Object]
    """
    comp_fields = []

    fields = xtx.get_children_of_field(schema)
    parents = list(filter(lambda x: x.value == obj, fields))

    comp_fields = list(
        filter(lambda x: x.is_composition and x.value._tx_fqn == "entity.Object", parents)
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

    fields = xtx.get_children_of_field(schema)
    parents = list(filter(lambda x: x.value == obj, fields))

    agg_fields = list(
        filter(lambda x: x.is_aggregation and x.value._tx_fqn == "entity.Object", parents)
    )

    return agg_fields


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
