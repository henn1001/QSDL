from tests import wrapper_generate_failure


class TestEnum:
    """Test Enums.

    01. `Enum` names must use `PascalCase`.

    02. `Enum` values must use `ALL_CAPS`.

    03. `Enum` must at least contain one value.

    """

    def test_enum_01_negative(self) -> None:
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("enum wrong { OPEN } ")
        inputs.append("enum Wro-Ng { OPEN } ")
        inputs.append("enum WRO_NG { OPEN } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_enum_02_negative(self) -> None:
        """Verify value naming convention"""
        inputs = []

        inputs.append("enum Foo { Open } ")
        inputs.append("enum Foo { opEN } ")
        inputs.append("enum Foo { OP-EN } ")
        inputs.append("enum Foo { open } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_enum_03_negative(self) -> None:
        """Verify empty enums"""
        test_input = """\
            enum Foo {
            }
        """

        wrapper_generate_failure(test_input)
