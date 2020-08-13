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


class TestEnumsOpenApi:
    """Test Enums.

    * `Enum` names should use `PascalCase`.

    * `Enum` values should use `ALL_CAPS`.

    * `Enum` should at least contain one value.

    * A description can be added after version, for `Enum`,
        `Interface`, `Query`, `Mutation`, `Object` or `Field`.

    """

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

    def test_invalid_name(self):
        """Verify name naming convention"""
        inputs = []

        inputs.append(
            """\
            enum wrong {
                OPEN
            }
        """
        )

        inputs.append(
            """\
            enum Wro-Ng {
                OPEN
            }
        """
        )

        inputs.append(
            """\
            enum WRO_NG {
                OPEN
            }
        """
        )

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_invalid_values(self):
        """Verify value naming convention"""
        inputs = []

        inputs.append(
            """\
            enum Enum {
                Open
            }
        """
        )

        inputs.append(
            """\
            enum Enum {
                opEN
            }
        """
        )

        inputs.append(
            """\
            enum Enum {
                OP-EN
            }
        """
        )

        inputs.append(
            """\
            enum Enum {
                open
            }
        """
        )

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_empty_enum(self):
        """Verify empty enums"""
        test_input = """\
            enum Enum {
            }
        """

        wrapper_generate_failure(test_input)
