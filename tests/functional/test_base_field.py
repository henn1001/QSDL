from tests import wrapper_generate


class TestBaseField:
    """Retain Base-only reference rendering; c1 owns shared scalar matrices."""

    def test_field_base_03_positive(self) -> None:
        """Verify base usage"""
        test_input = """\
            base Foo {
                field: Int
            }

            base Bar @force-generate {
                field: Foo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert properties["field"]["$ref"] == "#/components/schemas/Foo"

    def test_field_base_04_positive(self) -> None:
        """Verify object usage"""
        test_input = """\
            type Foo {
                field: Int
            }

            base Bar @force-generate {
                field: Foo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert properties["field"]["$ref"] == "#/components/schemas/Foo"
