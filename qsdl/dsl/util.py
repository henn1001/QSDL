# Copyright (C) 2022 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""QSDL Utility functions"""

from typing import Union

import qsdl.dsl.models as dsl

ValueType = Union[dsl.Scalar, dsl.Base, dsl.Api, dsl.Object, dsl.Field, dsl.Operation]


def get_directive_of_name(name: str, entity: ValueType) -> dsl.Directive:
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
