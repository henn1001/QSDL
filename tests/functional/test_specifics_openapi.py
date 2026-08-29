from tests import wrapper_generate


class TestSpecificsOpenAPI:
    def test_specifics_02_positive(self) -> None:
        test_input = """\
            base Foo {
                field1: Bar
            }

            type Bar {
                name: String
            }

            type Fruit extends Foo {
                field2: [Bar]
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Fruit"]["properties"]

        assert properties["field1"]["$ref"]
        assert properties["field2"]["items"]["$ref"]

    def test_specifics_04_positive(self) -> None:
        """Verify usage of relations without parent endpoints"""
        test_input = """\
            type Foo {
                field1: String
            }

            type Bar {
                name: String
                foos: [Foo]! @aggregation

                extend api {    }
            }

            type Fruit  {
                name: String
                foos: [Foo]! @composition

                extend api {    }
            }

        """

        openapi = wrapper_generate(test_input)

        schemas = openapi["components"]["schemas"]
        assert schemas["FooList"]
        assert schemas["Foo"]
        assert schemas["Bar"]
        assert schemas["Fruit"]

        paths = openapi["paths"]
        assert paths["/bars/{bar_id}/foos"]
        assert paths["/fruits/{fruit_id}/foos"]
        assert "/bars" not in paths
        assert "/bars" not in paths
