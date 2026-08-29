from tests import wrapper_generate


class TestBase:
    """Test Bases.

    OpenAPI-specific Base inheritance rendering remains here until WP-09.

    Validation coverage for naming and inheritance is owned by tests/rules.

    """

    def test_base_03_positive(self) -> None:
        """Verify base extends base"""
        test_input = """\
            base Fruit {
                banana: Int
            }

            base Foo extends Fruit {
                field: Int
                bananaaa: Int
            }

            base Bar extends Foo @force-generate {
                name: String
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert "banana" in properties
        assert "field" in properties
        assert "name" in properties

    def test_base_03_positive_2(self) -> None:
        """Verify base extends base"""
        test_input = """\
            base Fruit {
                banana: Int
            }

            base Foo {
                field: Int
            }

            base Bar extends Foo, Fruit @force-generate {
                name: String
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert "banana" in properties
        assert "field" in properties
        assert "name" in properties
