from tests import wrapper_generate


class TestObject:
    """Test Objects.

    OpenAPI-specific Object inheritance rendering remains here until WP-09.

    Validation coverage for naming and inheritance is owned by tests/rules.

    """

    def test_object_03_positive(self) -> None:
        """Verify object extends base"""
        test_input = """\
            base Fruit {
                banana: Int
            }

            base Foo extends Fruit {
                field: Int
            }

            type Bar extends Foo {
                name: String
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert "banana" in properties
        assert "field" in properties
        assert "name" in properties

    def test_object_03_positive_2(self) -> None:
        """Verify object extends base"""
        test_input = """\
            base Fruit {
                banana: Int
            }

            base Foo {
                field: Int
            }

            type Bar extends Foo, Fruit {
                name: String
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Bar"]["properties"]

        assert "banana" in properties
        assert "field" in properties
        assert "name" in properties
