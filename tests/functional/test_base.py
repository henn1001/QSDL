from tests import wrapper_generate, wrapper_generate_failure


class TestBase:
    """Test Bases.

    01. `Base` names must use `PascalCase`.

    03. `Base` may inherit `Field`s from a `Base`.

    04. `Base` name must be unique between `Object`, `Base` and `Scalar`.

    """

    def test_base_01_positive(self) -> None:
        """Verify PascalCase naming convention"""
        test_input = """\
            base Foo {
                field: Int
            }
        """

        wrapper_generate(test_input)

    def test_base_01_negative(self) -> None:
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("base wrong { test: String } ")
        inputs.append("base Wro-Ng { test: String } ")
        inputs.append("base WRO_NG { test: String } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

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
