from tests import wrapper_generate, wrapper_generate_failure


class TestDescription:
    """Test descriptions.

    01. A description may be added after version, for `Enum`, `Base`, `Api`, `Object` or `Field`.

    02. A description may be `SingleLine` or `MultiLine`.

    03. A `SingleLine` description must be presented between quotation marks and at least one character in between e.g. `"X"`.

    04. A `MultiLine` description must be presented between three quotation marks and at least one character in between e.g. `""\"X\"""`.

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

    def test_description_03_negative(self) -> None:
        """Verify SingleLine minimum character."""

        test_input = """\
            description: ""
        """

        wrapper_generate_failure(test_input)

    def test_description_04_negative(self) -> None:
        """Verify MultiLine minimum character."""

        test_input = """\
            description: ""\"""\"
        """

        wrapper_generate_failure(test_input)
