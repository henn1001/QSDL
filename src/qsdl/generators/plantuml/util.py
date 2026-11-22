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

"""Generator Utility functions"""

from qsdl import dsl


def diagram_fields(entity: dsl.Base | dsl.Object) -> list[dsl.Field]:
    """Keep inherited fields first in diagrams, ahead of synthetic object IDs."""
    fields = []

    # Support multiple supertypes
    for supertype in entity.supertypes:
        super_fields = diagram_fields(supertype)
        fields.extend(super_fields)

    # Add own fields, overriding inherited ones if needed
    for field in entity.fields:
        duplicate = [x for x in fields if hasattr(x, "name") and x.name == getattr(field, "name", None)]
        if not duplicate:
            fields.append(field)
        else:
            index = fields.index(duplicate[0])
            fields[index] = field

    return fields
