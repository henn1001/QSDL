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


def diagram_fields(entity: dsl.Base | dsl.Object) -> tuple[dsl.Field, ...]:
    """Render generation fields, keeping inherited slots ahead of the Object ID."""
    fields = entity.generation_fields
    if not isinstance(entity, dsl.Object) or not entity.supertypes or not fields or fields[0].name != "id":
        return fields

    synthetic_id, *members = fields
    inherited_names = {field.name for parent in entity.supertypes for field in parent.effective_fields}
    position = next((i for i, field in enumerate(members) if field.name not in inherited_names), len(members))
    return (*members[:position], synthetic_id, *members[position:])
