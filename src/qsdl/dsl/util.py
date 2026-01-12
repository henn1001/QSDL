# Copyright 2025 henn1001
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

"""QSDL Utility functions"""

import qsdl.dsl.models as dsl
import qsdl.dsl.textx as xtx

ValueType = dsl.Scalar | dsl.Base | dsl.Api | dsl.Object | dsl.Field | dsl.Operation


def get_directive_of_name(name: str, entity: ValueType) -> dsl.Directive | None:
    """Returns the first directive with a given name if available.

    Args:
        name (str): The name of the directive
        entity (Union[dsl.Scalar, dsl.Base, dsl.Api, dsl.Object, dsl.Field, dsl.Operation]): The entity which contains directives.

    Returns:
        dsl.Directive: Either the directive or None
    """
    match = [x for x in entity.directives if x.name == name]

    return match[0] if match else None


def description_wrapper(raw_string: str) -> list[str]:
    """Formats a multiline string if needed"""
    strings = []

    if raw_string:
        # first we split by new lines
        splits = raw_string.split("\n")

        # our ident is defined by the first line that starts with non whitespace
        first_line_detected = False
        count = 0

        for string in splits:
            # we skip the beginning and end of the comment if it is empty
            # we also strip the string if the first_line_detected logic does not apply
            if string.startswith('"""') or string.endswith('"""'):
                # dont strip when we detected a first_line and we rather want to remove padding
                if string.endswith('"""') and count == 0:
                    string = string.strip()

                string = string.replace('"""', "")

                if string.isspace() or not string:
                    continue
            else:
                # remove all quotes
                if string.startswith('"') or string.endswith('"'):
                    string = string.replace('"', "")

                # our first valid line starts after the tripple quote
                # it should be a non space character
                # we count the spaces via lstrip
                if string and not string.isspace() and not first_line_detected:
                    count = len(string) - len(string.lstrip(" "))
                    first_line_detected = True

            # after we identified the ident - calc padding and remove it
            padding = " " * count
            string = string.replace(padding, "", 1) if padding else string

            # finally add string to the list
            strings.append(string)

    return strings


def map_custom_type(  # pylint: disable=too-many-arguments
    entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object,
    mapping: dict[str, str | None],
    default: str,
    directive: str,
    args: list[str],
    arg_picker: str = "type",
) -> str | None:
    """
    Generic converter for custom mappings.

    Args:
        entity: The entity object to map.
        mapping: The dict that contains the mapping between builtin types and custom types of a generator.
        override_index: Index of the override to fetch from get_type_override.

    Returns:
        The mapped value or the entity name if no mapping exists.
    """
    name = entity.name
    override = None

    if isinstance(entity, dsl.Scalar):
        override = get_type_override(entity, directive, args).get(arg_picker)

    return override if override else mapping.get(name, default)


def get_type_override(
    entity: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object,
    directive: str,
    keys: list[str],
) -> dict[str, str]:
    """
    Checks and returns custom scalar overrides.

    Args:
        entity: The scalar object.

    Returns:
        A tuple containing the type, format, and pattern overrides.
    """
    ret = {"type": None}

    # Check and fetch the openapi directive
    custom_directive = get_directive_of_name(directive, entity)

    if custom_directive and ", " in custom_directive.value:
        # Split multiple values
        splits = [x.strip() for x in custom_directive.value.split(", ")]

        # First value is always without key accessor
        ret["type"] = splits[0]

        # Check for other keys dynamically
        for key in keys or []:
            ret[key] = next((x.replace(f"{key}:", "").strip() for x in splits if x.startswith(f"{key}:")), None)

    elif custom_directive:
        # Only the first value is present
        ret["type"] = custom_directive.value.strip()

    return ret


def get_composition_fields(schema: dsl.Schema, obj_name: str) -> list[dsl.Field]:
    """Returns all Fields whose value is this Object.

    Args:
        obj_name (str): The Object which value the fields should have.
        filter_relations (bool, optional): Include only relation fields. Defaults to True.

    Returns:
        list[dsl.Field]: The list of Fields.
    """
    fields = []

    fields = xtx.get_children_of_field(schema)

    fields = [
        x
        for x in fields
        if isinstance(x.parent, dsl.Object) and x.value.name == obj_name and x.is_array and not x.is_aggregation
    ]

    return fields
