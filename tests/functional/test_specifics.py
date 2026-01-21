from tests.functional import wrapper_generate, wrapper_generate_failure


class TestSpecifics:
    """Test specific functionality.

    01. It is not allowed to create the same relation multiple times.

    02. 'id', 'uid' and 'iv' shall not be used on `Object` `Field`.

    03. 'id' may be used on `Base` `Field`.

    """

    def test_specifics_01_negative(self) -> None:
        """Check relation duplicates"""
        inputs = []

        test_input = """\
            type Foo {
                field1: String
            }

            type Bar {
                field2: Foo @composition
                field2: Foo @composition
            }
        """
        inputs.append(test_input)

        test_input = """\
            type Foo {
                field1: String
            }

            type Bar {
                field2: Foo @aggregation
                field2: Foo @aggregation
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_specifics_02_negative(self) -> None:
        """Check that 'id', 'uid', and 'iv' are not allowed on Object Field"""
        inputs = [
            """\
            type Foo {
                id: String
            }
            """,
            """\
            type Foo {
                uid: String
            }
            """,
            """\
            type Foo {
                iv: String
            }
            """,
        ]

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_specifics_03_positive(self) -> None:
        """Check that 'id' is allowed on Base Field"""
        test_input = """\
            base BaseType {
                id: String
            }
        """
        wrapper_generate(test_input)

    def test_specifics_03_negative(self) -> None:
        """Check that 'id' is allowed on Base Field"""
        test_input = """\
            base BaseTypeOne {
                id: String
            }

            base BaseTypeTwo extends BaseTypeOne {
                a: String
            }

            type Foo extends BaseTypeTwo {
                field1: String
            }
        """
        wrapper_generate_failure(test_input)
