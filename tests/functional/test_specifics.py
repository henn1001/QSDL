from tests import wrapper_generate_failure


class TestSpecifics:
    """Test specific functionality.

    01. It is not allowed to create the same relation multiple times.

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
