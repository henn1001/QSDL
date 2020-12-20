# Copyright (C) 2020 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from tests import wrapper_generate, wrapper_generate_failure


class TestDescription:
    """Test descriptions.

    01. A description may be added after version, for `Enum`, `Base`, `Operation`, `Object` or `Field`.

    02. A description may be `SingleLine` or `MultiLine`.

    03. A `SingleLine` description must be presented between quotation marks and at least one character in between e.g. `"X"`.

    04. A `MultiLine` description must be presented between three quotation marks and at least one character in between e.g. `""\"X\"""`.

    """

    def test_description_01_positive(self):
        """Verify SingleLine for all entitys."""

        test_input = """\
            description: "single line description"

            "single line description"
            enum Foo {
                DUMMY
            }

            "single line description"
            base Bar{
                "single line description"
                field: String
            }

            "single line description"
            extend Operation {
                "single line description"
                field: Void @path(value:"path")
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

    def test_description_02_positive(self):
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
            base Bar {
                \"""
                Multi line description
                \"""
                field: String
            }

            \"""
            Multi line description
            \"""
            extend Operation {
                \"""
                Multi line description
                \"""
                field: Void @path(value:"path")
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

    def test_description_03_negative(self):
        """Verify SingleLine minimum character."""

        test_input = """\
            description: ""
        """

        wrapper_generate_failure(test_input)

    def test_description_04_negative(self):
        """Verify MultiLine minimum character."""

        test_input = """\
            description: ""\"""\"
        """

        wrapper_generate_failure(test_input)
