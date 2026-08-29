from tests import wrapper_generate


class TestObjectField:
    """Retain Base/Object reference rendering; c1 owns scalar and constraint matrices."""

    def test_field_object_03_positive(self) -> None:
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

    def test_field_object_04_positive(self) -> None:
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
