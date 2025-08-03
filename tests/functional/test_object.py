from tests import wrapper_generate, wrapper_generate_failure


class TestObject:
    """Test Objects.

    01. `Object` names must use `PascalCase`.

    03. `Object` can inherit `Field`s from a `Base`.

    04. `Object` name must be unique between `Object`, `Base` and `Scalar`.

    """

    def test_object_01_positive(self) -> None:
        """Verify PascalCase naming convention"""
        test_input = """\
            type Foo {
                field: String
            }
        """

        wrapper_generate(test_input)

    def test_object_01_negative(self) -> None:
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("type wrong { field: String } ")
        inputs.append("type Wro-Ng { field: String } ")
        inputs.append("type WRO_NG { field: String } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

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
