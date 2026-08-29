# Copyright 2026 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the language-level description syntax."""

from .conftest import ParseExpectErrorFixture


class TestDescription:
    """Test that descriptions cannot be empty."""

    def test_empty_single_line_description_negative(self, parse_expect_syntax_error: ParseExpectErrorFixture) -> None:
        """Single-line descriptions require at least one character."""
        parse_expect_syntax_error('description: ""')

    def test_empty_multi_line_description_negative(self, parse_expect_syntax_error: ParseExpectErrorFixture) -> None:
        """Multi-line descriptions require at least one character."""
        parse_expect_syntax_error('description: """"""')
