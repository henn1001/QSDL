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

from tests import wrapper_generate, wrapper_generate_failure


class TestArgument:
    """Test Arguments.

    01. `Argument` names must use `TBD`.

    02. `Argument` must contain at least one name/value pair.

    03. `Argument` value must be one of the following
        * `Scalar`
        * `Enum`
        * `Base`
        * `Object`

    04. `Argument` may contain a maximum of one `Scalar` value of `ID`.

    05. `Argument` value may be a list when enclosed with brackets.

    06. `Argument` value and list value may be marked as mandatory.

    07. `Argument` name/value pairs for get methods are query parameters. [OpenAPI]

    08. `Argument` name/value pairs for post/put/patch methods are requestBody. [OpenAPI]

    09. `Argument` value must be a `Scalar` of `ID` for delete method. Other types are ignored. [OpenAPI]

    10. `Argument` must be used by `Field` of `Operation` only. Other usages are ignored. [OpenAPI]

    11. `Argument` value may not be a list for `Scalar` `ID`.

    """

    def test_argument_01_positive(self):
        """Verify TBD naming convention"""
        test_input = """\
            extend Operation {
                field(arg: String): Void @path(value:"path")
            }
        """

        wrapper_generate(test_input)

    def test_argument_01_negative(self):
        """Verify TBD naming convention"""
        inputs = []

        inputs.append('extend Operation { field(a-a: String): Void @path(value:"path") } ')

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_argument_02_positive(self):
        """Verify empty arguments"""
        test_input = """\
            extend Operation {
                field(arg: String): Void @path(value:"path")
            }
        """

        wrapper_generate(test_input)

    def test_argument_02_negative(self):
        """Verify empty arguments"""
        test_input = """\
            extend Operation {
            }
        """

        wrapper_generate_failure(test_input)

    def test_argument_03_positive(self):
        """Verify  argument value types"""
        test_input = """\
            enum Bar {
                OPEN
                CLOSED
            }

            base Foo {
                field: String
            }

            type Fruit {
                field: String
            }

            extend Operation {
                field1(arg: ID): Void @path(value:"path1")
                field2(arg: Int): Void @path(value:"path2")
                field3(arg: Float): Void @path(value:"path3")
                field4(arg: String): Void @path(value:"path4")
                field5(arg: Boolean): Void @path(value:"path5")
                field6(arg: Date): Void @path(value:"path6")
                field7(arg: Object): Void @path(value:"path7")
                field8(arg: Foo): Void @path(value:"path8")
                field9(arg: Bar): Void @path(value:"path9")
                field10(arg: Fruit): Void @path(value:"path10")
            }
        """

        wrapper_generate(test_input)

    def test_argument_03_negative(self):
        """Verify  argument value types"""
        test_input = """\

            extend Operation {
                field1(arg: String): Void @path(value:"path1")
                field2(arg: field1): Void @path(value:"path2")
            }
        """

        wrapper_generate_failure(test_input)

    def test_argument_04_negative(self):
        """Verify multiple IDs"""
        test_input = """\
            extend Operation {
                field(arg1: ID, arg2: ID): Void @path(value:"path")
            }
        """

        wrapper_generate_failure(test_input)

    def test_argument_05_positive(self):
        """Verify value list"""
        test_input = """\
            extend Operation {
                field1(arg: [String]): Void @path(value:"path1")
                field2(arg: [String]): Void @path(value:"path2") @method(value: POST)
                field3(arg: [String]): Void @path(value:"path3") @method(value: PUT)
                field4(arg: [String]): Void @path(value:"path4") @method(value: PATCH)
            }
        """

        openapi = wrapper_generate(test_input)

        def get_schema_parameters(openapi, path, method):
            var = openapi["paths"][path][method]["parameters"]
            return var[0]["schema"]

        def get_schema_request(openapi, path, method):
            var = openapi["paths"][path][method]["requestBody"]
            return var["content"]["application/json"]["schema"]

        schema = get_schema_parameters(openapi, "/path1", "get")
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "string"

        schema = get_schema_request(openapi, "/path2", "post")
        assert schema["properties"]["arg"]["type"] == "array"
        assert schema["properties"]["arg"]["items"]["type"] == "string"

        schema = get_schema_request(openapi, "/path3", "put")
        assert schema["properties"]["arg"]["type"] == "array"
        assert schema["properties"]["arg"]["items"]["type"] == "string"

        schema = get_schema_request(openapi, "/path4", "patch")
        assert schema["properties"]["arg"]["type"] == "array"
        assert schema["properties"]["arg"]["items"]["type"] == "string"

    def test_argument_06_positive(self):
        """Verify required"""
        test_input = """\
            extend Operation {
                field1(arg: String!): Void @path(value:"path1")
                field2(arg: [String]!): Void @path(value:"path2")
                field3(arg: [String!]!): Void @path(value:"path3")
            }
        """

        wrapper_generate(test_input)

    def test_argument_07_positive(self):
        """Verify argument is query for get"""
        test_input = """\
            enum Bar {
                OPEN
                CLOSED
            }

            base Foo {
                field: String
            }

            type Fruit {
                field: String
            }

            extend Operation {
                field1(arg: ID): Void @path(value:"path1")
                field2(arg: Int): Void @path(value:"path2")
                field3(arg: Float): Void @path(value:"path3")
                field4(arg: String): Void @path(value:"path4")
                field5(arg: Boolean): Void @path(value:"path5")
                field6(arg: Date): Void @path(value:"path6")
                field7(arg: Object): Void @path(value:"path7")
                field8(arg: Bar): Void @path(value:"path8")
                field9(arg: Foo): Void @path(value:"path9")
                field10(arg: Fruit): Void @path(value:"path10")
            }
        """

        openapi = wrapper_generate(test_input)

        def get_parameter(openapi, path, method):
            var = openapi["paths"][path][method]["parameters"]
            return var[0]

        ops = [
            ("/path1/{arg}", "get", "integer", "int64", "path"),
            ("/path2", "get", "integer", "int32", "query"),
            ("/path3", "get", "number", "float", "query"),
            ("/path4", "get", "string", None, "query"),
            ("/path5", "get", "boolean", None, "query"),
            ("/path6", "get", "string", "date-time", "query"),
            ("/path7", "get", "object", None, "query"),
            ("/path8", "get", None, None, "query"),
            ("/path9", "get", None, None, "query"),
            ("/path10", "get", None, None, "query"),
        ]

        for _path, _method, _type, _format, _in in ops:
            parameter = get_parameter(openapi, _path, _method)

            assert parameter["in"] == _in

            if _type:
                assert parameter["schema"]["type"] == _type

            if _format:
                assert parameter["schema"]["format"] == _format

            if _path in ["/path8", "/path9", "/path10"]:
                assert parameter["schema"]["$ref"]

    def test_argument_08_positive(self):
        """Verify argument is requestbody for post/put/patch"""
        test_input = """\
            enum Bar {
                OPEN
                CLOSED
            }

            base Foo {
                field: String
            }

            type Fruit {
                field: String
            }

            extend Operation {
                field2(arg: Int): Void @path(value:"path2") @method(value: POST)
                field3(arg: Float): Void @path(value:"path3") @method(value: POST)
                field4(arg: String): Void @path(value:"path4") @method(value: POST)
                field5(arg: Boolean): Void @path(value:"path5") @method(value: POST)
                field6(arg: Date): Void @path(value:"path6") @method(value: POST)
                field7(arg: Object): Void @path(value:"path7") @method(value: POST)
                field8(arg: Bar): Void @path(value:"path8") @method(value: POST)
                field9(arg: Foo): Void @path(value:"path9") @method(value: POST)
                field10(arg: Fruit): Void @path(value:"path10") @method(value: POST)
            }
        """

        openapi = wrapper_generate(test_input)

        def get_schema_request(openapi, path, method):
            var = openapi["paths"][path][method]["requestBody"]
            return var["content"]["application/json"]["schema"]

        ops = [
            ("/path2", "post", "integer", "int32"),
            ("/path3", "post", "number", "float"),
            ("/path4", "post", "string", None),
            ("/path5", "post", "boolean", None),
            ("/path6", "post", "string", "date-time"),
            ("/path7", "post", None, None),
            ("/path8", "post", None, None),
            ("/path9", "post", None, None),
            ("/path10", "post", None, None),
        ]

        for _path, _method, _type, _format in ops:
            schema = get_schema_request(openapi, _path, _method)

            if _type:
                assert schema["properties"]["arg"]["type"] == _type

            if _format:
                assert schema["properties"]["arg"]["format"] == _format

            if _path in ["/path7"]:
                assert schema["type"] == "object"
                assert "properties" not in schema

            if _path in ["/path8"]:
                assert schema["properties"]["arg"]["$ref"]

            if _path in ["/path9", "/path10"]:
                assert schema["$ref"]

    def test_argument_09_positive(self):
        """Verify argument is only of ID for delete"""
        test_input = """\
            enum Bar {
                OPEN
                CLOSED
            }

            base Foo {
                field: String
            }

            type Fruit {
                field: String
            }

            extend Operation {
                field1(arg: ID): Void @path(value:"path") @method(value: DELETE)
                field2(arg: Int): Void @path(value:"path2") @method(value: DELETE)
                field3(arg: Float): Void @path(value:"path3") @method(value: DELETE)
                field4(arg: String): Void @path(value:"path4") @method(value: DELETE)
                field5(arg: Boolean): Void @path(value:"path5") @method(value: DELETE)
                field6(arg: Date): Void @path(value:"path6") @method(value: DELETE)
                field7(arg: Object): Void @path(value:"path7") @method(value: DELETE)
                field8(arg: Bar): Void @path(value:"path8") @method(value: DELETE)
                field9(arg: Foo): Void @path(value:"path9") @method(value: DELETE)
                field10(arg: Fruit): Void @path(value:"path10") @method(value: DELETE)
            }
        """

        openapi = wrapper_generate(test_input)

        ops = [
            "/path2",
            "/path3",
            "/path4",
            "/path5",
            "/path6",
            "/path7",
            "/path8",
            "/path9",
            "/path10",
        ]

        for _path in ops:

            if _path in ["/path1"]:
                assert openapi["paths"][_path]["delete"]["parameters"][0]["in"] == "path"
            else:
                assert "parameters" not in openapi["paths"][_path]["delete"]
                assert "requestBody" not in openapi["paths"][_path]["delete"]

    def test_argument_10_positive(self):
        """Verify argument is only used in operations"""
        test_input = """\
            base Foo {
                field(arg: String): String
            }

            type Bar {
                field(arg: String): String
            }
        """

        wrapper_generate(test_input)

    def test_argument_11_negative(self):
        """Verify that we can not use array IDs"""
        test_input = """\
            extend Operation {
                field(arg: [ID]): Void @path(value:"path")
            }
        """

        wrapper_generate_failure(test_input)
