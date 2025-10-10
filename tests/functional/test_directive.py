from tests import wrapper_generate, wrapper_generate_failure


class TestDirective:
    """Test Directives.

    These directives change the OpenAPI generation.

    1.  `Directive` `@query` may be use on any `Field` to create a query parameter for the get all method.

    2.  `Directive` `@unique` may be use on any `Field` to mark it as unique.

    3.  `Directive` `@hidden` may be use on any `Field` exclude it from api data layer.

    4.  `Directive` `@readOnly` may be use on any `Field` to mark it as read only.

    5.  `Directive` `@writeOnly` may be use on any `Field` to mark it as write only.

    6.  `Directive` `@composition` may be used on a `Object` `Field` to create a parent-child relation. The `Field` value must be a list `Object`.

    7.  `Directive` `@aggregation` may be used on a `Object` `Field` to create a independent relation. The `Field` value must be a list `Object`.

    8.  `Directive` `@path` must be used on any `Operation` This specifies the API Path.

    9.  `Directive` `@method` may be used on any `Operation` to specify the REST Method. Valid values are GET | POST | PUT | PATCH | DELETE.

    10. `Directive` `@namespace` may be used on any `Base`, `Api` or `Object` for grouping.

    11. `Directive` `@pagination` may be used on any `Operation` for converting response in a pageable object.

    12. `Directive` `@produce` may be used on any `Operation` for changing the mime type.

    13. `Directive` `@consumes` may be used on any `Operation` for changing the mime type.

    14. `Directive` `@generate` may be used on `Api` to specify the generated operations. Valid values are GET_ALL, CREATE, GET, REPLACE, UPDATE, DELETE, ADD, REMOVE.

    15. `Directive` `@minSize` may be used on `String`, `Int`, `Long` typed `Field` for setting minimum (length) of the value.

    16. `Directive` `@maxSize` may be used on `String`, `Int`, `Long` typed `Field` for setting maximum (length) of the value.

    17. `Directive` `@headers` may be used on any `Api` or `Oeration` for adding response headers to the operation.

    18. `Directive` `@force-generate` may be used on any `Base` or `Enum` to force the generation regardless wether the entity is used anywhere or not.

    19. `Directive` `@default("value")` may be used on `Object Field` for setting a default value.

    20. `Directive` `@ignore` may be used on 'Field` to exclude it from the generation.

    21. `Directive` `@transient` may be used on `Field` to exclude it from database layer.

    22. `Directive` `@override` needs to be used on a `Field` which is redefining an inherited field.
    """

    def test_directive_01_positive(self) -> None:
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
        assert parameter[0]["name"] == "name"

        assert parameter[1]["in"] == "query"
        assert parameter[1]["name"] == "world"

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

    def test_directive_06_negative(self) -> None:
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

    def test_directive_07_positive(self) -> None:
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

    def test_directive_07_negative(self) -> None:
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

    def test_directive_08_positive(self) -> None:
        """Verify usage of @path"""
        test_input = """\
            extend api {
                getObjects: [String] @path("objects")
            }
            
            type Foo {
                field : Int

                extend api {
                    getObject: String @path("foos")
                    getObjectss: [String] @path("objectss")
                }
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/objects"]["get"]["operationId"] == "getObjects"
        assert openapi["paths"]["/foos"]["get"]["operationId"] == "getObject"
        assert openapi["paths"]["/objectss"]["get"]["operationId"] == "getObjectss"

    def test_directive_08_negative(self) -> None:
        """Verify usage of @path"""
        test_input = """\
            extend api {
                getObjects: [String]
            }

            type Foo {
                field : Int

                extend api {
                    getObject: String
                    getObjects: [String]
                }
            }
        """

        wrapper_generate_failure(test_input)

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
        assert "Test" in openapi["paths"]["/bars/{id}"]["put"]["tags"]
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

    def test_directive_22_positive(self) -> None:
        """Verify usage of @query"""
        test_input = """\
            base Fruit {
                name: String @query
            }

            base Foo extends Fruit {
                apple: String
            }

            type Bar extends Foo {
                name: String @override
            }
        """

        wrapper_generate(test_input)

    def test_directive22_negative(self) -> None:
        """Verify usage of @query"""
        test_input = """\
            base Fruit {
                name: String @query
            }

            base Foo extends Fruit {
                apple: String
            }

            type Bar extends Foo {
                name: String
            }
        """

        wrapper_generate_failure(test_input)
