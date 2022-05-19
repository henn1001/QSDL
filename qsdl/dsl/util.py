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

"""QSDL Utility functions"""

from typing import Union

import qsdl.dsl.models as dsl


def get_directive_of_name(
    name: str, entity: Union[dsl.Base, dsl.Api, dsl.Object, dsl.Field, dsl.Operation]
) -> dsl.Directive:
    """Returns the first directive with a given name if available.

    Args:
        name (str): The name of the directive
        entity (Union[dsl.Base, dsl.Api, dsl.Object, dsl.Field, dsl.Operation]): The entity which contains directives.

    Returns:
        dsl.Directive: Either the directive or None
    """
    match = [x for x in entity.directives if x.name == name]

    if match:
        return match[0]
    else:
        return None
