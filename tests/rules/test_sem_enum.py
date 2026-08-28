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

"""Tests for SEM-3xx rules: Enum rules.

Rules covered:
- SEM-301: An Enum must contain at least one value
- SEM-302: Enum values are constrained domain values
- SEM-303: Enums may have optional namespace via @namespace(...)
"""

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestSemEnum:
    """Tests for SEM-301 to SEM-303: Enum rules."""

    def test_SEM_301_enum_with_values_positive(self, parse: ParseFixture) -> None:
        """SEM-301: Enum with at least one value is valid."""
        schema = parse("""
            enum Status {
                OPEN
            }
            type Foo {
                status: Status
            }
        """)
        enums = xtx.get_children_of_enum(schema)
        status_enum = next(e for e in enums if e.name == "Status")
        assert len(status_enum.values) >= 1

    def test_SEM_301_enum_with_multiple_values_positive(self, parse: ParseFixture) -> None:
        """SEM-301: Enum with multiple values is valid."""
        schema = parse("""
            enum Status {
                OPEN
                CLOSED
                PENDING
                IN_PROGRESS
            }
            type Foo {
                status: Status
            }
        """)
        enums = xtx.get_children_of_enum(schema)
        status_enum = next(e for e in enums if e.name == "Status")
        assert len(status_enum.values) == 4

    def test_SEM_301_empty_enum_negative(self, parse_expect_syntax_error: ParseExpectErrorFixture) -> None:
        """SEM-301: Empty enum is rejected."""
        parse_expect_syntax_error("""
            enum Status {
            }
        """)

    def test_SEM_302_enum_values_immutable_positive(self, parse: ParseFixture) -> None:
        """SEM-302: Enum values are constrained domain values."""
        schema = parse("""
            enum Priority {
                LOW
                MEDIUM
                HIGH
            }
            type Foo {
                priority: Priority
            }
        """)
        enums = xtx.get_children_of_enum(schema)
        priority_enum = next(e for e in enums if e.name == "Priority")
        assert priority_enum.values == ["LOW", "MEDIUM", "HIGH"]

    def test_SEM_303_enum_namespace_positive(self, parse: ParseFixture) -> None:
        """SEM-303: Enum may have optional namespace via @namespace(...)."""
        schema = parse("""
            enum Status @namespace("com.example.domain") {
                OPEN
                CLOSED
            }
            type Foo {
                status: Status
            }
        """)
        enums = xtx.get_children_of_enum(schema)
        status_enum = next(e for e in enums if e.name == "Status")
        assert status_enum.namespace == "com.example.domain"

    def test_SEM_303_enum_without_namespace_positive(self, parse: ParseFixture) -> None:
        """SEM-303: Enum without namespace is valid (optional)."""
        schema = parse("""
            enum Status {
                OPEN
                CLOSED
            }
            type Foo {
                status: Status
            }
        """)
        enums = xtx.get_children_of_enum(schema)
        status_enum = next(e for e in enums if e.name == "Status")
        assert status_enum.namespace is None or status_enum.namespace == ""
