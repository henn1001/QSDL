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


class TestObjectField:
    """Test Fields for Objects.

    1. `Field` of `Object` can be a `Scalar` value with one one of the following:
        * `ID`
        * `Int`
        * `Float`
        * `String`
        * `Boolean`
        * `Date`
        * `Object`
        * `Void`

    2. `Field` of `Object` value can be a `Enum`.

    3. `Field` of `Object` value can be a `Base` when marked as `@nested`.

    4. `Field` of `Object` value can be a `Object`.

    5. `Field` of `Object` value can be a list when enclosed with brackets.

    6. `Field` of `Object` value can not be a list for `Scalar` `ID`.

    7. `Field` of `Object` value and list value can be marked as mandatory.

    8. `Field` of `Object` values can only have one `ID`. This includes inherited values.

    """

    def test_field_object_1_positive(self):
        """Verify that we can use basic types"""

        test_input = """\
            base Type {
                id: ID
                int: Int
                float: Float
                string: String
                boolean: Boolean
                date: Date
                object: Object
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Type"]["properties"]

        for key, value in properties.items():
            if key == "id":
                assert value["type"] == "string"
            elif key == "int":
                assert value["type"] == "integer"
                assert value["format"] == "int32"
            elif key == "float":
                assert value["type"] == "number"
                assert value["format"] == "float"
            elif key == "string":
                assert value["type"] == "string"
            elif key == "boolean":
                assert value["type"] == "boolean"
            elif key == "date":
                assert value["type"] == "string"
                assert value["format"] == "date-time"
            elif key == "object":
                assert value["type"] == "object"
            else:
                assert False

    def test_field_object_2_positive(self):
        """Verify enum usage."""
        test_input = """\
            enum Enum {
                OPEN
                CLOSED
            }

            base Type {
                value: Enum
            }
        """

        openapi = wrapper_generate(test_input)

    def test_field_object_3_positive(self):
        """Verify base usage"""
        test_input = """\
            base Base {
                field: ID
            }

            base Type {
                field: Base @nested
            }
        """

        wrapper_generate(test_input)

    def test_field_object_3_negative(self):
        """Verify base usage"""
        test_input = """\
            base Base {
                field: ID
            }

            base Type {
                field: Base
            }
        """

        wrapper_generate_failure(test_input)

    def test_field_object_4_positive(self):
        """Verify object usage"""
        test_input = """\
            type One {
                field: ID
            }

            base Type {
                field: One
            }
        """

        wrapper_generate(test_input)

    def test_field_object_5_positive(self):
        """Verify that we can use array types"""

        test_input = """\
            base Type {
                int: [Int]
                float: [Float]
                string: [String]
                boolean: [Boolean]
                date: [Date]
                object: [Object]
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Type"]["properties"]

        for key, value in properties.items():
            if key == "int":
                assert value["type"] == "array"
                assert value["items"]["type"] == "integer"
                assert value["format"] == "int32"
            elif key == "float":
                assert value["type"] == "array"
                assert value["items"]["type"] == "number"
                assert value["format"] == "float"
            elif key == "string":
                assert value["type"] == "array"
                assert value["items"]["type"] == "string"
            elif key == "boolean":
                assert value["type"] == "array"
                assert value["items"]["type"] == "boolean"
            elif key == "date":
                assert value["type"] == "array"
                assert value["items"]["type"] == "string"
                assert value["format"] == "date-time"
            elif key == "object":
                assert value["type"] == "array"
                assert value["items"]["type"] == "object"
            else:
                assert False

    def test_field_object_6_negative(self):
        """Verify that we can not use array IDs"""

        test_input = """\
            base Type {
                field: [ID]
            }
        """

        wrapper_generate_failure(test_input)

    def test_field_object_7_negative(self):
        """Verify required"""
        test_input = """\
            base Type {
                field1: String!
                field2: [String]!
                field3: [String!]!
            }
        """

        wrapper_generate(test_input)

    def test_field_object_8_negative(self):
        """Verify multiple IDs"""

        test_input = """\
            base One {
                id: ID
            }

            base Two implements One{
                name: String
            }

            base Three implements Two {
                field: ID
            }
        """

        wrapper_generate_failure(test_input)
