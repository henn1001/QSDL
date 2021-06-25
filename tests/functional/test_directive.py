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


class TestDirective:
    """Test Directives.

    These directives change the OpenAPI generation.

    01. `Directive` `@query` may be use on any `Base` or `Object` `Field` to create a query parameter for the get all method.

    02. `Directive` `@nested` may be use on any `Base` or `Object` `Field` when the `Field` value is a `Object`. This creates a nested JSON `Object`.

    03. `Directive` `@nested` must be use on any `Base` or `Object` `Field` when the `Field` value is a `Base`. This creates a nested JSON `Object`.

    04. `Directive` `@readOnly` may be use on any `Base` or `Object` `Field` to mark a `Field` as read only.

    05. `Directive` `@writeOnly` may be use on any `Base` or `Object` `Field` to mark a `Field` as write only.

    06. `Directive` `@composition` may be used on a `Object` `Field` to create a parent-child relation. The `Field` value must be a `Object`.

    07. `Directive` `@aggregation` may be used on a `Object` `Field` to create a independent relation. The `Field` value must be a `Object`.

    08. `Directive` `@path` must be used on any `Api` `Field` which are not part of a `Object`. This specifies the API Path.

    09. `Directive` `@path` may be used on any `Api` `Field` which is part of a `Object`. This specifies the API Path.

    10. `Directive` `@method` may be used on any `Api` `Field` to specify the REST Method. Valid values are GET | POST | PUT | PATCH | DELETE.

    11. `Directive` `@namespace` may be used on any `Base`, `Api` or `Object` for grouping.

    """

    def test_directive_01_positive(self):
        """Verify usage of @query"""
        test_input = """\
            base Foo {
                name: String @query
            }

            type Bar extends Foo {
                world: String @query
            }
        """

        openapi = wrapper_generate(test_input)

        parameter = openapi["paths"]["/bars"]["get"]["parameters"]

        assert parameter[0]["in"] == "query"
        assert parameter[0]["name"] in ["name", "world"]

        assert parameter[1]["in"] == "query"
        assert parameter[1]["name"] in ["name", "world"]

    def test_directive_02_positive(self):
        """Verify usage of @nested"""
        test_input = """\
            base Foo {
                id: ID
                field1: Bar @nested
            }

            type Bar {
                id: ID
                name: String
            }

            type Fruit extends Foo {
                field2: [Bar] @nested
            }
        """

        openapi = wrapper_generate(test_input)

        ref = openapi["components"]["schemas"]["Fruit"]["allOf"][0]
        properties = openapi["components"]["schemas"]["Fruit"]["allOf"][1]["properties"]

        assert "Foo" in ref["$ref"]
        assert properties["field2"]["items"]["$ref"]

    def test_directive_03_positive(self):
        """Verify usage of @nested"""
        test_input = """\
            base Foo {
                id: ID
                field1: Bar @nested
            }

            base Bar {
                id: ID
                name: String
            }

            type Fruit extends Foo {
                field2: [Bar] @nested
            }
        """

        openapi = wrapper_generate(test_input)

        ref = openapi["components"]["schemas"]["Fruit"]["allOf"][0]
        properties = openapi["components"]["schemas"]["Fruit"]["allOf"][1]["properties"]

        assert "Foo" in ref["$ref"]
        assert properties["field2"]["items"]["$ref"]

    def test_directive_03_negative(self):
        """Verify usage of @nested"""
        test_input = """\
            base Base {
                id: ID
                field1: Nested
            }

            base Nested {
                id: ID
                name: String
            }

            type Test extends Base {
                field2: [Nested]
            }
        """

        wrapper_generate_failure(test_input)

    def test_directive_04_positive(self):
        """Verify usage of @readOnly"""
        test_input = """\
            enum Fruit {
                APPLE
                MELON
            }

            base Foo {
                id: ID
                name: String @readOnly
            }

            type Bar extends Foo {
                world: String @readOnly
                enum: Fruit @readOnly
                base: Foo @readOnly @nested
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Foo"]["properties"]
        assert properties["name"]["readOnly"]

        ref = openapi["components"]["schemas"]["Bar"]["allOf"][0]
        properties = openapi["components"]["schemas"]["Bar"]["allOf"][1]["properties"]
        assert "Foo" in ref["$ref"]
        assert properties["world"]["readOnly"]
        assert properties["enum"]["readOnly"]
        assert properties["enum"]["$ref"]
        assert properties["base"]["readOnly"]
        assert properties["base"]["$ref"]

    def test_directive_05_positive(self):
        """Verify usage of @writeOnly"""
        test_input = """\
            enum Fruit {
                APPLE
                MELON
            }

            base Foo {
                id: ID
                name: String @writeOnly
            }

            type Bar extends Foo {
                world: String @writeOnly
                enum: Fruit @writeOnly
                base: Foo @writeOnly @nested
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Foo"]["properties"]
        assert properties["name"]["writeOnly"]

        ref = openapi["components"]["schemas"]["Bar"]["allOf"][0]
        properties = openapi["components"]["schemas"]["Bar"]["allOf"][1]["properties"]
        assert "Foo" in ref["$ref"]
        assert properties["world"]["writeOnly"]
        assert properties["enum"]["writeOnly"]
        assert properties["enum"]["$ref"]
        assert properties["base"]["writeOnly"]
        assert properties["base"]["$ref"]

    def test_directive_06_positive(self):
        """Verify usage of @composition"""
        test_input = """\
            type Foo {
                field: ID 
                composition: Bar @composition
                ignored: String @composition
            }

            type Bar {
                field: ID 
            }
        """

        openapi = wrapper_generate(test_input)

        assert "composition" not in openapi["components"]["schemas"]["Foo"]["properties"]
        assert "ignored" in openapi["components"]["schemas"]["Foo"]["properties"]

        assert "/foos/{foo_field}/bars" in openapi["paths"]
        assert "/foos/{foo_field}/bars/{field}" in openapi["paths"]

    def test_directive_07_positive(self):
        """Verify usage of @aggregation"""
        test_input = """\
            type Foo {
                field: ID 
                aggregation: Bar @aggregation
                ignored: String @aggregation
            }

            type Bar {
                field: ID 
            }
        """

        openapi = wrapper_generate(test_input)

        assert "aggregation" not in openapi["components"]["schemas"]["Foo"]["properties"]
        assert "ignored" in openapi["components"]["schemas"]["Foo"]["properties"]

        assert "/foos/{foo_field}/bars" in openapi["paths"]
        assert "/foos/{foo_field}/bars/{field}/add" in openapi["paths"]
        assert "/foos/{foo_field}/bars/{field}/remove" in openapi["paths"]

    def test_directive_08_positive(self):
        """Verify usage of @path"""
        test_input = """\
            extend Api {
                getObjects: [String] @path(value:"objects")
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/objects"]["get"]["operationId"] == "getObjects"

    def test_directive_08_negative(self):
        """Verify usage of @path"""
        test_input = """\
            extend Api {
                getObjects: [String]
            }
        """

        wrapper_generate_failure(test_input)

    def test_directive_09_positive(self):
        """Verify usage of @path"""
        test_input = """\
            type Foo {
                id : ID

                extend Api {
                    getObject: String
                    getObjects: [String] @path(value:"objects")
                }
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/foos"]["get"]["operationId"] == "getObject"
        assert openapi["paths"]["/objects"]["get"]["operationId"] == "getObjects"

    def test_directive_10_positive(self):
        """Verify usage of @method"""
        test_input = """\
            extend Api {
                field1: Void @path(value:"path") @method(value: GET)
                field2: Void @path(value:"path") @method(value: POST)
                field3: Void @path(value:"path") @method(value: PUT)
                field4: Void @path(value:"path") @method(value: PATCH)
                field5: Void @path(value:"path") @method(value: DELETE)
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/path"]["get"]["operationId"] == "field1"
        assert openapi["paths"]["/path"]["post"]["operationId"] == "field2"
        assert openapi["paths"]["/path"]["put"]["operationId"] == "field3"
        assert openapi["paths"]["/path"]["patch"]["operationId"] == "field4"
        assert openapi["paths"]["/path"]["delete"]["operationId"] == "field5"

    def test_directive_11_positive(self):
        """Verify usage of @namespace"""
        test_input = """\
            base Foo @namespace(value:"Test") {
                field : String
            }

            type Bar @namespace(value:"Test") {
                field : ID
            }

            extend Api @namespace(value:"Test") {
                field : String @path(value:"path")
            }
        """

        openapi = wrapper_generate(test_input)

        assert "Test" in openapi["paths"]["/bars"]["get"]["tags"]
        assert "Test" in openapi["paths"]["/bars"]["post"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{field}"]["get"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{field}"]["put"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{field}"]["patch"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{field}"]["delete"]["tags"]

        assert "Test" in openapi["paths"]["/path"]["get"]["tags"]
