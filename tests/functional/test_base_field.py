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


class TestBaseField:
    """Test Fields for Bases.

    01. `Field` of `Base` may be a `Scalar` value with one one of the following:
        * `ID`
        * `Int`
        * `Float`
        * `String`
        * `Boolean`
        * `Date`
        * `Object`
        * `Void`

    02. `Field` of `Base` value may be a `Enum`.

    03. `Field` of `Base` value may be a `Base` when marked as `@nested`.

    04. `Field` of `Base` value may be a `Object`.

    05. `Field` of `Base` value may be a list when enclosed with brackets.

    06. `Field` of `Base` value may not be a list for `Scalar` `ID`.

    07. `Field` of `Base` value and list value may be marked as mandatory.

    08. `Field` of `Base` values may only have one `ID`. This includes inherited values.

    """

    def test_field_base_01_positive(self):
        """Verify that we can use basic types"""

        test_input = """\
            base Foo {
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

        properties = openapi["components"]["schemas"]["Foo"]["properties"]

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

    def test_field_base_02_positive(self):
        """Verify enum usage."""
        test_input = """\
            enum Foo {
                OPEN
                CLOSED
            }

            base Bar {
                field: Foo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert properties["field"]["type"] == "string"
        assert properties["field"]["enum"] == ["OPEN", "CLOSED"]

    def test_field_base_03_positive(self):
        """Verify base usage"""
        test_input = """\
            base Foo {
                field: ID
            }

            base Bar {
                field: Foo @nested
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert properties["field"]["$ref"] == "#/components/schemas/Foo"

    def test_field_base_03_negative(self):
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

    def test_field_base_04_positive(self):
        """Verify object usage"""
        test_input = """\
            type Foo {
                field: ID
            }

            base Bar {
                field: Foo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert properties["field"]["type"] == "string"

    def test_field_base_05_positive(self):
        """Verify that we can use array types"""

        test_input = """\
            base Foo {
                int: [Int]
                float: [Float]
                string: [String]
                boolean: [Boolean]
                date: [Date]
                object: [Object]
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Foo"]["properties"]

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

    def test_field_base_06_negative(self):
        """Verify that we can not use array IDs"""

        test_input = """\
            base Foo {
                field: [ID]
            }
        """

        wrapper_generate_failure(test_input)

    def test_field_base_07_positive(self):
        """Verify required"""
        test_input = """\
            base Foo {
                field1: String!
                field2: [String]!
                field3: [String!]!
            }
        """

        openapi = wrapper_generate(test_input)

        required = openapi["components"]["schemas"]["Foo"]["required"]

        assert "field1" in required
        assert "field2" in required
        assert "field3" in required

    def test_field_base_08_negative(self):
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
