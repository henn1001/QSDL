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


class TestDirective:
    """Test Directives.

    These directives change the OpenAPI generation.

    01. `Directive` `@query` may be use on any `Base` or `Object` `Field` to create a query parameter for the get all method.

    02. `Directive` `@unique` may be use on any `Base` or `Object` `Field` to mark a `Field` as unique.

    03. `Directive` `@hidden` may be use on any `Base` or `Object` `Field` to mark a `Field` as hidden.

    04. `Directive` `@readOnly` may be use on any `Base` or `Object` `Field` to mark a `Field` as read only.

    05. `Directive` `@writeOnly` may be use on any `Base` or `Object` `Field` to mark a `Field` as write only.

    06. `Directive` `@composition` may be used on a `Object` `Field` to create a parent-child relation. The `Field` value must be a list `Object`.

    07. `Directive` `@aggregation` may be used on a `Object` `Field` to create a independent relation. The `Field` value must be a list `Object`.

    08. `Directive` `@path` must be used on any `Api` `Field` which are not part of a `Object`. This specifies the API Path.

    09. `Directive` `@path` must be used on any `Api` `Field` which is part of a `Object`. This specifies the API Path.

    10. `Directive` `@method` may be used on any `Api` `Field` to specify the REST Method. Valid values are GET | POST | PUT | PATCH | DELETE.

    11. `Directive` `@namespace` may be used on any `Base`, `Api` or `Object` for grouping.

    12.  `Directive` `@pagination` may be used on any `Api` `Field` for converting response in a pageable object.

    13.  `Directive` `@produce` may be used on any `Api` `Field` for changing the mime type.

    14.  `Directive` `@consumes` may be used on any `Api` `Field` for changing the mime type.

    15.  `Directive` `@generate` may be used on `Api` to specify the generated operations. Valid values are GET_ALL, CREATE, GET, REPLACE, UPDATE, DELETE, ADD, REMOVE.

    16.  `Directive` `@minSize` may be used on `String`, `Int`, `Long` typed `Object Field` for setting minimum length of the value.

    17.  `Directive` `@maxSize` may be used on `String`, `Int`, `Long` typed `Object Field` for setting maximum length of the value.

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
        assert parameter[0]["name"] == "query"
        assert parameter[0]["schema"]["example"]["name"]
        assert parameter[0]["schema"]["example"]["world"]

    def test_directive_03_positive(self):
        """Verify usage of @hidden"""
        test_input = """\

            type Bar {
                world: String
                fruit: String @hidden
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]
        assert "fruit" not in properties

    def test_directive_04_positive(self):
        """Verify usage of @readOnly"""
        test_input = """\
            enum Fruit {
                APPLE
                MELON
            }

            base Foo {
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

        properties = openapi["components"]["schemas"]["Bar"]["properties"]
        assert properties["name"]["readOnly"]
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

        properties = openapi["components"]["schemas"]["Bar"]["properties"]
        assert properties["name"]["writeOnly"]
        assert properties["world"]["writeOnly"]
        assert properties["enum"]["writeOnly"]
        assert properties["enum"]["$ref"]
        assert properties["base"]["writeOnly"]
        assert properties["base"]["$ref"]

    def test_directive_06_positive(self):
        """Verify usage of @composition"""
        test_input = """\
            type Foo {
                field: Int
                composition: [Bar] @composition
            }

            type Bar {
                field: Int
            }
        """

        openapi = wrapper_generate(test_input)

        assert "composition" not in openapi["components"]["schemas"]["Foo"]["properties"]

        assert "/foos/{foo_id}/bars" in openapi["paths"]
        assert "/foos/{foo_id}/bars/{id}" in openapi["paths"]

    def test_directive_06_negative(self):
        """Verify usage of @composition"""
        inputs = []

        test_input = """\
            type Foo {
                field: Int
                ignored: String @composition
            }

            type Bar {
                field: Int
            }
        """
        inputs.append(test_input)

        test_input = """\
            type Foo {
                field: Int
            }

            base Bar {
                field: Foo @composition
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_directive_07_positive(self):
        """Verify usage of @aggregation"""
        test_input = """\
            type Foo {
                aggregation: [Bar] @aggregation
            }

            type Bar {
                field: Int
            }
        """

        openapi = wrapper_generate(test_input)

        assert "aggregation" not in openapi["components"]["schemas"]["Foo"]["properties"]

        assert "/foos/{foo_id}/bars" in openapi["paths"]
        assert "/foos/{foo_id}/bars/{id}/add" in openapi["paths"]
        assert "/foos/{foo_id}/bars/{id}/remove" in openapi["paths"]

    def test_directive_07_negative(self):
        """Verify usage of @aggregation"""
        inputs = []

        test_input = """\
            type Foo {
                ignored: String @aggregation
            }

            type Bar {
                field: Int
            }
        """
        inputs.append(test_input)

        test_input = """\
            type Foo {
                field: Int
            }

            base Bar {
                field: Foo @aggregation
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_directive_08_positive(self):
        """Verify usage of @path"""
        test_input = """\
            extend api {
                getObjects: [String] @path("objects")
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/objects"]["get"]["operationId"] == "getObjects"

    def test_directive_08_negative(self):
        """Verify usage of @path"""
        test_input = """\
            extend api {
                getObjects: [String]
            }
        """

        wrapper_generate_failure(test_input)

    def test_directive_09_positive(self):
        """Verify usage of @path"""
        test_input = """\
            type Foo {
                field : Int

                extend api {
                    getObject: String @path("foos")
                    getObjects: [String] @path("objects")
                }
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/foos"]["get"]["operationId"] == "getObject"
        assert openapi["paths"]["/objects"]["get"]["operationId"] == "getObjects"

    def test_directive_10_positive(self):
        """Verify usage of @method"""
        test_input = """\
            extend api {
                field1: Void @path("path") @method(GET)
                field2: Void @path("path") @method(POST)
                field3: Void @path("path") @method(PUT)
                field4: Void @path("path") @method(PATCH)
                field5: Void @path("path") @method(DELETE)
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
            base Foo @namespace("Test") {
                field : String
            }

            type Bar @namespace("Test") {
                field : Int
            }

            extend api @namespace("Test") {
                field : String @path("path")
            }
        """

        openapi = wrapper_generate(test_input)

        assert "Test" in openapi["paths"]["/bars"]["get"]["tags"]
        assert "Test" in openapi["paths"]["/bars"]["post"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{id}"]["get"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{id}"]["put"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{id}"]["patch"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{id}"]["delete"]["tags"]

        assert "Test" in openapi["paths"]["/path"]["get"]["tags"]
