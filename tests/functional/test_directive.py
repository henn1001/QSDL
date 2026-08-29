from tests import wrapper_generate


class TestDirective:
    """Test OpenAPI-specific directive rendering retained for WP-09.

    Core directive parsing and validation belongs to ``tests/rules/`` or the
    existing void-based directive tests. Query filtering, relationship
    validation, and inheritance override behavior have dedicated owners.
    """

    def test_directive_03_positive(self) -> None:
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

    def test_directive_04_positive(self) -> None:
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

    def test_directive_05_positive(self) -> None:
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

    def test_directive_06_positive(self) -> None:
        """Verify usage of @composition"""
        test_input = """\
            type Foo {
                field: Int
                composition: [Bar]! @composition
            }

            type Bar {
                field: Int
            }
        """

        openapi = wrapper_generate(test_input)

        assert "composition" not in openapi["components"]["schemas"]["Foo"]["properties"]

        assert "/foos/{foo_id}/bars" in openapi["paths"]
        assert "/foos/{foo_id}/bars/{id}" in openapi["paths"]

    def test_directive_07_positive(self) -> None:
        """Verify usage of @aggregation"""
        test_input = """\
            type Foo {
                aggregation: [Bar]! @aggregation
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

    def test_directive_08_positive(self) -> None:
        """Verify custom paths on object APIs are rendered correctly."""
        test_input = """\
            type Foo {
                field: Int

                extend api {
                    getObject: String @path("foos")
                    getObjectss: [String] @path("objectss")
                }
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/foos"]["get"]["operationId"] == "getObject"
        assert openapi["paths"]["/objectss"]["get"]["operationId"] == "getObjectss"

    def test_directive_10_positive(self) -> None:
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

    def test_directive_11_positive(self) -> None:
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
        assert "Test" in openapi["paths"]["/bars/{id}"]["patch"]["tags"]
        assert "Test" in openapi["paths"]["/bars/{id}"]["delete"]["tags"]

        assert "Test" in openapi["paths"]["/path"]["get"]["tags"]

    def test_directive_18_positive(self) -> None:
        """Verify usage of @force-generate"""
        test_input = """\

            base Foo {
                world: String
                fruit: String
            }

            base Apple {
                world: String
                fruit: String
            }

            base FooBar @force-generate {
                world: String
                fruit: Apple
            }

            base FruitFoo {
                world: String
                fruit: String
            }

            enum Fruit {
                FOO
                BAR
            }

            enum Fruity @force-generate {
                FOO
                BAR
            }

            type Bar {
                world: FruitFoo
            }
        """

        openapi = wrapper_generate(test_input)

        assert "Foo" not in openapi["components"]["schemas"]
        assert "Apple" in openapi["components"]["schemas"]
        assert "FooBar" in openapi["components"]["schemas"]
        assert "FruitFoo" in openapi["components"]["schemas"]
        assert "Fruit" not in openapi["components"]["schemas"]
        assert "Fruity" in openapi["components"]["schemas"]
        assert "Bar" in openapi["components"]["schemas"]

    def test_directive_19_positive(self) -> None:
        """Verify usage of @default"""
        test_input = """\
            enum Fruit {
                APPLE
                MELON
            }

            type Foo {
                field1 : String @default("test")
                field2 : Int @default("1")
                field3 : Long @default("1")
                field4: Float @default("1.1")
                field5: Double @default("1.1")
                field6 : Boolean @default("true")
                field7: Fruit @default("APPLE")
                field8 : Boolean @default("false")
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Foo"]["properties"]
        assert properties["field1"]["default"] == "test"
        assert properties["field2"]["default"] == 1
        assert properties["field3"]["default"] == 1
        assert properties["field4"]["default"] == 1.1
        assert properties["field5"]["default"] == 1.1
        assert properties["field6"]["default"]
        assert properties["field7"]["default"] == "APPLE"
        assert not properties["field8"]["default"]

    def test_directive_20_positive(self) -> None:
        """Verify usage of @force-generate"""
        test_input = """\
            base AA {
                world: String @ignore
            }

            base Foo extends AA {
                world: String @override
                fruit: String @ignore
            }

            type Bar {
                world: String
                fruit: String @ignore
                nested: Foo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Foo"]["properties"]
        assert "world" in properties
        assert "fruit" not in properties

        properties = openapi["components"]["schemas"]["Bar"]["properties"]
        assert "world" in properties
        assert "fruit" not in properties
