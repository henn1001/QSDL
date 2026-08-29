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

