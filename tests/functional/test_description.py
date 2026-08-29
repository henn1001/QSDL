from tests import wrapper_generate


class TestDescription:
    """Test rendered descriptions.

    Language-level description syntax and empty-description validation are
    covered independently in ``tests/rules/test_description.py``.
    """

    def test_description_01_positive(self) -> None:
        """Verify SingleLine for all entitys."""

        test_input = """\
            description: "single line description"

            "single line description"
            enum Foo {
                DUMMY
            }

            "single line description"
            base Bar @force-generate {
                "single line description"
                field: String
            }

            "single line description"
            extend api {
                "single line description"
                field: Void @path("path")
            }

            "single line description"
            type Fruit {
                "single line description"
                field: String
            }
        """

        openapi = wrapper_generate(test_input)

        desr = "single line description"

        assert desr in openapi["info"]["description"]

        schema = openapi["components"]["schemas"]
        assert desr in schema["Bar"]["description"]
        assert desr in schema["Bar"]["properties"]["field"]["description"]

        assert desr in openapi["paths"]["/path"]["get"]["description"]

        schema = openapi["components"]["schemas"]
        assert desr in schema["Fruit"]["description"]
        assert desr in schema["Fruit"]["properties"]["field"]["description"]

    def test_description_02_positive(self) -> None:
        """Verify MultiLine for all entitys."""

        test_input = """\
            description: \"""
            Multi line description
            \"""

            \"""
            Multi line description
            \"""
            enum Foo {
                DUMMY
            }

            \"""
            Multi line description
            \"""
            base Bar @force-generate {
                \"""
                Multi line description
                \"""
                field: String
            }

            \"""
            Multi line description
            \"""
            extend api {
                \"""
                Multi line description
                \"""
                field: Void @path("path")
            }

            \"""
            Multi line description
            \"""
            type Fruit {
                \"""
                Multi line description
                \"""
                field: String
            }
        """

        openapi = wrapper_generate(test_input)

        desr = "Multi line description"

        assert desr in openapi["info"]["description"]

        schema = openapi["components"]["schemas"]
        assert desr in schema["Bar"]["description"]
        assert desr in schema["Bar"]["properties"]["field"]["description"]

        assert desr in openapi["paths"]["/path"]["get"]["description"]

        schema = openapi["components"]["schemas"]
        assert desr in schema["Fruit"]["description"]
        assert desr in schema["Fruit"]["properties"]["field"]["description"]
