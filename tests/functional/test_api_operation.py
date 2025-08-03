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

from tests import wrapper_generate


class TestApiOperation:
    """Test Fields for Operations.

    01. `Operation` of `Api` value may be a `Scalar` value with one one of the following:
        * `Int`
        * `Long`
        * `Float`
        * `Double`
        * `String`
        * `Boolean`
        * `Date`
        * `Object`
        * `Void`

    02. `Operation` of `Api` value may be a `Enum`.

    03. `Operation` of `Api` value may be a `Base`.

    04. `Operation` of `Api` value may be a `Object`.

    05. `Operation` of `Api` value may be a list when enclosed with brackets.

    07. `Operation` of `Api` value may be marked as required.

    """

    def test_api_operation_01_positive(self) -> None:
        """Verify that we can use basic types"""

        test_input = """\
            extend api {
                int: Int @path("path2")
                long: Long @path("path3")
                float: Float @path("path4")
                double: Double @path("path5")
                string: String @path("path6")
                boolean: Boolean @path("path7")
                date: Date @path("path8")
                datetime: Datetime @path("path9")
                object: Object @path("path10")
            }
        """

        openapi = wrapper_generate(test_input)

        def get_schema(openapi: dict, path: str, method: str) -> dict:
            var = openapi["paths"][path][method]["responses"]
            return var["200"]["content"]["application/json"]["schema"]

        ops = [
            ("/path2", "get", "integer", "int32"),
            ("/path3", "get", "integer", "int64"),
            ("/path4", "get", "number", "float"),
            ("/path5", "get", "number", "double"),
            ("/path6", "get", "string", None),
            ("/path7", "get", "boolean", None),
            ("/path8", "get", "string", "date"),
            ("/path9", "get", "string", "date-time"),
            ("/path10", "get", "object", None),
        ]

        for _path, _method, _type, _format in ops:
            schema = get_schema(openapi, _path, _method)

            assert schema["type"] == _type

            if _format:
                assert schema["format"] == _format

    def test_api_operation_02_positive(self) -> None:
        """Verify enum usage."""
        test_input = """\
            enum Foo {
                OPEN
                CLOSED
            }

            extend api {
                field: Foo @path("path")
            }
        """

        openapi = wrapper_generate(test_input)

        def get_schema(openapi: dict, path: str) -> dict:
            var = openapi["paths"][path]["get"]["responses"]
            return var["200"]["content"]["application/json"]["schema"]

        assert get_schema(openapi, "/path")["$ref"]

    def test_api_operation_03_positive(self) -> None:
        """Verify base usage"""
        test_input = """\
            base Foo {
                field: String
            }

            extend api {
                field: Foo @path("path")
            }
        """

        openapi = wrapper_generate(test_input)

        def get_schema(openapi: dict, path: str) -> dict:
            var = openapi["paths"][path]["get"]["responses"]
            return var["200"]["content"]["application/json"]["schema"]

        assert get_schema(openapi, "/path")["$ref"] == "#/components/schemas/Foo"

    def test_api_operation_04_positive(self) -> None:
        """Verify object usage"""
        test_input = """\
            type Foo {
                field: String
            }

            extend api {
                field: Foo @path("path")
            }
        """

        openapi = wrapper_generate(test_input)

        def get_schema(openapi: dict, path: str) -> dict:
            var = openapi["paths"][path]["get"]["responses"]
            return var["200"]["content"]["application/json"]["schema"]

        assert get_schema(openapi, "/path")["$ref"] == "#/components/schemas/Foo"

    def test_api_operation_05_positive(self) -> None:
        """Verify that we can use array types"""

        test_input = """\
            extend api {
                int: [Int] @path("path2")
                float: [Float] @path("path3")
                string: [String] @path("path4")
                boolean: [Boolean] @path("path5")
                date: [Date] @path("path6")
                datetime: [Datetime] @path("path7")
                object: [Object] @path("path8")
            }
        """

        openapi = wrapper_generate(test_input)

        def get_schema(openapi: dict, path: str, method: str) -> dict:
            var = openapi["paths"][path][method]["responses"]
            return var["200"]["content"]["application/json"]["schema"]

        ops = [
            ("/path2", "get", "integer", "int32"),
            ("/path3", "get", "number", "float"),
            ("/path4", "get", "string", None),
            ("/path5", "get", "boolean", None),
            ("/path6", "get", "string", "date"),
            ("/path7", "get", "string", "date-time"),
            ("/path8", "get", "object", None),
        ]

        for _path, _method, _type, _format in ops:
            schema = get_schema(openapi, _path, _method)

            assert schema["type"] == "array"
            assert schema["items"]["type"] == _type

            if _format:
                assert schema["items"]["format"] == _format

    def test_api_operation_07_positive(self) -> None:
        """Verify required"""
        test_input = """\
            extend api {
                field1: String! @path("path1")
                field2: [String]! @path("path2")
            }
        """

        wrapper_generate(test_input)
