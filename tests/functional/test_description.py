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

from tests import wrapper_generate
from tests import wrapper_generate_failure


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
            enum Enum {
                DUMMY
            }

            "single line description"
            base Base{
                "single line description"
                null: Void
            }

            "single line description"
            extend Operation {
                "single line description"
                null: Void @path(value:"x")
            }

            "single line description"
            type Object {
                "single line description"
                null: Void
            }
        """

        openapi = wrapper_generate(test_input)

        # TODO: add openAPI description verification

    def test_description_02_positive(self):
        """Verify MultiLine for all entitys."""

        test_input = """\
            description: \"""
            Multi line description
            \"""

            \"""
            Multi line description
            \"""
            enum Enum {
                DUMMY
            }

            \"""
            Multi line description
            \"""
            base Base {
                \"""
                Multi line description
                \"""
                null: Void
            }

            \"""
            Multi line description
            \"""
            extend Operation {
                \"""
                Multi line description
                \"""
                null: Void @path(value:"x")
            }

            \"""
            Multi line description
            \"""
            type Object {
                \"""
                Multi line description
                \"""
                null: Void
            }
        """

        openapi = wrapper_generate(test_input)

        # TODO: add openAPI description verification

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
