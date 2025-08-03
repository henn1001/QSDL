from qsdl.dsl import textx


class TestCore:
    """Test core functions."""

    def test_get_metamodel_plantuml(self) -> None:
        """Verify that we can print the plantuml model"""

        assert textx.get_metamodel(print_uml=True)
