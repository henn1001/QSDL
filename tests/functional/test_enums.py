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

from . import wrapper_generate
from . import wrapper_generate_failure


class TestEnum:
    """Test Enums.

    1. `Enum` names should use `PascalCase`.

    2. `Enum` values should use `ALL_CAPS`.

    3. `Enum` should at least contain one value.

    4. `Enum` can be used as `Field` value.

    5. `Enum` can be used as `Argument` value.
    """

    def test_enum_1_negative(self):
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("enum wrong { OPEN } ")
        inputs.append("enum Wro-Ng { OPEN } ")
        inputs.append("enum WRO_NG { OPEN } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_enum_2_negative(self):
        """Verify value naming convention"""
        inputs = []

        inputs.append("enum Enum { Open } ")
        inputs.append("enum Enum { opEN } ")
        inputs.append("enum Enum { OP-EN } ")
        inputs.append("enum Enum { open } ")
        inputs.append("enum Enum { OPEN } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_enum_3_negative(self):
        """Verify empty enums"""
        test_input = """\
            enum Enum {
            }
        """

        wrapper_generate_failure(test_input)

    def test_usage(self):
        """Verify usage."""
        test_input = """\
            enum Enum {
                OPEN
                CLOSED
            }

            interface Interface {
                value: Enum
            }

            type Object {
                value: Enum
                values: Enum
            }

            type Query {
                query(input: Enum): Enum @path(value="somepath")
                queries(input: [Enum]): [Enum] @path(value="somepath")
            }
        """

        openapi = wrapper_generate(test_input)

        # TODO: add openAPI verification
