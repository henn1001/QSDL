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

"""Tests for LOG-3xx rules: Schema Header Ordering.

Rules covered:
- LOG-301: Schema header fields must appear in order: title, version, description, servers
- LOG-302: All schema header fields are optional
"""

from .conftest import ParseFixture


class TestLogSchema:
    """Tests for LOG-301 to LOG-302: Schema Header Ordering."""

    def test_LOG_302_all_header_fields_optional_positive(self, parse: ParseFixture) -> None:
        """LOG-302: Schema without any header fields is valid."""
        schema = parse("""
            type Foo {
                field: String
            }
        """)
        assert schema.title == ""
        assert schema.version == ""
        assert schema.description == []

    def test_LOG_302_title_only_positive(self, parse: ParseFixture) -> None:
        """LOG-302: Schema with only title is valid."""
        schema = parse("""
            title: "My API"

            type Foo {
                field: String
            }
        """)
        assert schema.title == "My API"
        assert schema.version == ""

    def test_LOG_302_version_only_positive(self, parse: ParseFixture) -> None:
        """LOG-302: Schema with only version is valid."""
        schema = parse("""
            version: "1.0.0"

            type Foo {
                field: String
            }
        """)
        assert schema.version == "1.0.0"

    def test_LOG_301_correct_order_positive(self, parse: ParseFixture) -> None:
        """LOG-301: Schema header fields in correct order."""
        schema = parse("""
            title: "My API"
            version: "1.0.0"
            description: "API Description"

            type Foo {
                field: String
            }
        """)
        assert schema.title == "My API"
        assert schema.version == "1.0.0"
        assert schema.description is not None

    def test_LOG_301_title_version_positive(self, parse: ParseFixture) -> None:
        """LOG-301: Title before version is valid."""
        schema = parse("""
            title: "Test"
            version: "2.0"

            type Foo {
                field: String
            }
        """)
        assert schema.title == "Test"
        assert schema.version == "2.0"
