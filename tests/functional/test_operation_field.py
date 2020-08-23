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

from tests import wrapper_generate
from tests import wrapper_generate_failure


class TestOperationField:
    """Test Fields for Operations.

    01. `Field` of `Operation` may be a `Scalar` value with one one of the following:
        * `ID`
        * `Int`
        * `Float`
        * `String`
        * `Boolean`
        * `Date`
        * `Object`
        * `Void`

    02. `Field` of `Operation` value may be a `Enum`.

    03. `Field` of `Operation` value may be a `Base`.

    04. `Field` of `Operation` value may be a `Object`.

    05. `Field` of `Operation` value may be a list when enclosed with brackets.

    07. `Field` of `Operation` value and list value may be marked as mandatory.

    """

    def test_field_object_01_positive(self):
        """Verify that we can use basic types"""

        test_input = """\
            extend Operation {
                id: ID @path(value:"path1")
                int: Int @path(value:"path2")
                float: Float @path(value:"path3")
                string: String @path(value:"path4")
                boolean: Boolean @path(value:"path5")
                date: Date @path(value:"path6")
                object: Object @path(value:"path7")
            }
        """

        openapi = wrapper_generate(test_input)

    def test_field_object_02_positive(self):
        """Verify enum usage."""
        test_input = """\
            enum Enum {
                OPEN
                CLOSED
            }

            extend Operation {
                field: Enum @path(value:"test")
            }
        """

        openapi = wrapper_generate(test_input)

    def test_field_operation_03_positive(self):
        """Verify base usage"""
        test_input = """\
            base Base {
                field: ID
            }

            extend Operation {
                field: Base @path(value:"test")
            }
        """

        wrapper_generate(test_input)

    def test_field_object_04_positive(self):
        """Verify object usage"""
        test_input = """\
            type One {
                field: ID
            }

            base Type {
                field: One @path(value:"test")
            }
        """

        wrapper_generate(test_input)

    def test_field_object_05_positive(self):
        """Verify that we can use array types"""

        test_input = """\
            extend Operation {
                int: [Int] @path(value:"path2")
                float: [Float] @path(value:"path3")
                string: [String] @path(value:"path4")
                boolean: [Boolean] @path(value:"path5")
                date: [Date] @path(value:"path6")
                object: [Object] @path(value:"path7")
            }
        """

        openapi = wrapper_generate(test_input)

    def test_field_object_07_negative(self):
        """Verify required"""
        test_input = """\
            extend Operation {
                field1: String! @path(value:"path1")
                field2: [String]! @path(value:"path2")
                field3: [String!]! @path(value:"path3")
            }
        """

        wrapper_generate(test_input)
