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

from tests import wrapper_generate, wrapper_generate_failure


class TestObjectField:
    """Test Fields for Objects.

    01. `Field` of `Object` may be a `Scalar` value with one one of the following:
        * `Int`
        * `Long`
        * `Float`
        * `Double`
        * `String`
        * `Boolean`
        * `Date`
        * `Object`

    02. `Field` of `Object` value may be a `Enum`.

    03. `Field` of `Object` value may be a `Base`.

    04. `Field` of `Object` value may be a `Object`.

    05. `Field` of `Object` value may be a list when enclosed with brackets.

    07. `Field` of `Object` value may be marked as required.

    """

    def test_field_object_01_positive(self):
        """Verify that we can use basic types"""

        test_input = """\
            type Foo {
                int: Int
                long: Long
                float: Float
                double: Double
                string: String
                boolean: Boolean
                date: Date
                datetime: Datetime
                object: Object
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Foo"]["properties"]

        for key, value in properties.items():
            if key == "id":
                assert value["type"] == "integer"
                assert value["format"] == "int64"
            elif key == "int":
                assert value["type"] == "integer"
                assert value["format"] == "int32"
            elif key == "long":
                assert value["type"] == "integer"
                assert value["format"] == "int64"
            elif key == "float":
                assert value["type"] == "number"
                assert value["format"] == "float"
            elif key == "double":
                assert value["type"] == "number"
                assert value["format"] == "double"
            elif key == "string":
                assert value["type"] == "string"
            elif key == "boolean":
                assert value["type"] == "boolean"
            elif key == "date":
                assert value["type"] == "string"
                assert value["format"] == "date"
            elif key == "datetime":
                assert value["type"] == "string"
                assert value["format"] == "date-time"
            elif key == "object":
                assert value["type"] == "object"
            else:
                assert False

    def test_field_object_02_positive(self):
        """Verify enum usage."""
        test_input = """\
            enum Foo {
                OPEN
                CLOSED
            }

            type Bar {
                field: Foo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert properties["field"]["$ref"]

    def test_field_object_03_positive(self):
        """Verify base usage"""
        test_input = """\
            base Foo {
                field: Int
            }

            type Bar {
                field: Foo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert properties["field"]["$ref"] == "#/components/schemas/Foo"

    def test_field_object_04_positive(self):
        """Verify object usage"""
        test_input = """\
            type Foo {
                field: Int
            }

            type Bar {
                field: Foo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert properties["field"]["$ref"] == "#/components/schemas/Foo"

    def test_field_object_05_positive(self):
        """Verify that we can use array types"""

        test_input = """\
            type Foo {
                int: [Int]
                float: [Float]
                string: [String]
                boolean: [Boolean]
                date: [Date]
                datetime: [Datetime]
                object: [Object]
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Foo"]["properties"]

        for key, value in properties.items():
            if key == "id":
                assert value["type"] == "integer"
                assert value["format"] == "int64"
            elif key == "int":
                assert value["type"] == "array"
                assert value["items"]["type"] == "integer"
                assert value["items"]["format"] == "int32"
            elif key == "float":
                assert value["type"] == "array"
                assert value["items"]["type"] == "number"
                assert value["items"]["format"] == "float"
            elif key == "string":
                assert value["type"] == "array"
                assert value["items"]["type"] == "string"
            elif key == "boolean":
                assert value["type"] == "array"
                assert value["items"]["type"] == "boolean"
            elif key == "date":
                assert value["type"] == "array"
                assert value["items"]["type"] == "string"
                assert value["items"]["format"] == "date"
            elif key == "datetime":
                assert value["type"] == "array"
                assert value["items"]["type"] == "string"
                assert value["items"]["format"] == "date-time"
            elif key == "object":
                assert value["type"] == "array"
                assert value["items"]["type"] == "object"
            else:
                assert False

    def test_field_object_07_positive(self):
        """Verify required"""
        test_input = """\
            type Foo {
                field1: String!
                field2: [String]!
            }
        """

        openapi = wrapper_generate(test_input)

        required = openapi["components"]["schemas"]["Foo"]["required"]

        assert "field1" in required
        assert "field2" in required
