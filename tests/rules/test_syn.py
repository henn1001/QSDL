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

"""Tests for SYN-* naming convention rules.

Rules covered:
- SYN-001: Scalar names
- SYN-002: Enum names
- SYN-003: Base names
- SYN-004: Object names
- SYN-005: Enum values
- SYN-006: Field names
- SYN-007: Operation names
- SYN-008: Argument names
- SYN-009: Custom directive names
"""

import pytest

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestSynNaming:
    """Tests for naming conventions validated after parsing."""

    def test_SYN_001_scalar_pascalcase_positive(self, parse: ParseFixture) -> None:
        """SYN-001: Scalar names use PascalCase and may contain digits."""
        schema = parse("""
            scalar UUID
            scalar V2

            type User {
                uuid: UUID
                version: V2
            }
        """)
        scalar_names = [scalar.name for scalar in xtx.get_children_of_scalar(schema)]
        assert "UUID" in scalar_names
        assert "V2" in scalar_names

    @pytest.mark.parametrize("name", ["email", "email_address", "Email-Address"])
    def test_SYN_001_scalar_invalid(self, name: str, parse_expect_name_error: ParseExpectErrorFixture) -> None:
        """SYN-001: Scalar names that are not PascalCase are rejected by validation."""
        parse_expect_name_error(f"scalar {name}")

    def test_SYN_002_enum_pascalcase_positive(self, parse: ParseFixture) -> None:
        """SYN-002: Enum names use PascalCase."""
        schema = parse("""
            enum UserStatus {
                OPEN
            }
            type User {
                status: UserStatus
            }
        """)
        enum = xtx.get_children_of_enum(schema)[0]
        assert enum.name == "UserStatus"

    @pytest.mark.parametrize("name", ["status", "user_status", "User-Status"])
    def test_SYN_002_enum_invalid(self, name: str, parse_expect_name_error: ParseExpectErrorFixture) -> None:
        """SYN-002: Enum names that are not PascalCase are rejected by validation."""
        parse_expect_name_error(f"enum {name} {{ OPEN }}")

    def test_SYN_003_base_pascalcase_positive(self, parse: ParseFixture) -> None:
        """SYN-003: Base names use PascalCase."""
        schema = parse("""
            base Auditable @force-generate {
                created_at: Datetime
            }
            type User extends Auditable {
                name: String
            }
        """)
        base = xtx.get_children_of_base(schema)[0]
        assert base.name == "Auditable"

    @pytest.mark.parametrize("name", ["auditable", "audit_fields", "Audit-Fields"])
    def test_SYN_003_base_invalid(self, name: str, parse_expect_name_error: ParseExpectErrorFixture) -> None:
        """SYN-003: Base names that are not PascalCase are rejected by validation."""
        parse_expect_name_error(f"base {name} {{ created_at: Datetime }}")

    def test_SYN_004_object_pascalcase_positive(self, parse: ParseFixture) -> None:
        """SYN-004: Object names use PascalCase."""
        schema = parse("""
            type UserProfile {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.name == "UserProfile"

    @pytest.mark.parametrize("name", ["user", "user_profile", "User-Profile"])
    def test_SYN_004_object_invalid(self, name: str, parse_expect_name_error: ParseExpectErrorFixture) -> None:
        """SYN-004: Object names that are not PascalCase are rejected by validation."""
        parse_expect_name_error(f"type {name} {{ name: String }}")

    def test_SYN_005_enum_values_allcaps_positive(self, parse: ParseFixture) -> None:
        """SYN-005: Enum values use ALL_CAPS with optional underscore-separated words."""
        schema = parse("""
            enum Status {
                OPEN
                IN_PROGRESS
                V2
            }
            type User {
                status: Status
            }
        """)
        status = xtx.get_children_of_enum(schema)[0]
        assert status.values == ["OPEN", "IN_PROGRESS", "V2"]

    @pytest.mark.parametrize("value", ["open", "Open", "openStatus", "IN-PROGRESS", "IN__PROGRESS"])
    def test_SYN_005_enum_value_invalid(self, value: str, parse_expect_name_error: ParseExpectErrorFixture) -> None:
        """SYN-005: Lowercase, mixed-case, and malformed enum values are rejected."""
        parse_expect_name_error(f"enum Status {{ {value} }}")

    def test_SYN_006_field_camelcase_and_snake_case_positive(self, parse: ParseFixture) -> None:
        """SYN-006: Fields support both camelCase and snake_case."""
        schema = parse("""
            type UserProfile {
                firstName: String
                first_name: String
                entity_id: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert [field.name for field in obj.fields if field.name != "id"] == ["firstName", "first_name", "entity_id"]

    @pytest.mark.parametrize("name", ["Name", "first-name", "first__name", "_internal", "custom_"])
    def test_SYN_006_field_invalid(self, name: str, parse_expect_name_error: ParseExpectErrorFixture) -> None:
        """SYN-006: Fields must start lowercase and cannot use malformed separators."""
        parse_expect_name_error(f"type User {{ {name}: String }}")

    def test_SYN_007_operation_names_support_camelcase_and_snake_case(self, parse: ParseFixture) -> None:
        """SYN-007: Operations support both camelCase and snake_case."""
        schema = parse("""
            extend api {
                findByName: String @path("find-by-name")
                find_by_name: String @path("find-by-name-snake")
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        assert {operation.name for operation in operations} >= {"findByName", "find_by_name"}

    @pytest.mark.parametrize("name", ["FindByName", "find-by-name", "find__by_name", "_find"])
    def test_SYN_007_operation_invalid(self, name: str, parse_expect_name_error: ParseExpectErrorFixture) -> None:
        """SYN-007: Operations reject invalid separators and casing."""
        parse_expect_name_error(f'extend api {{ {name}: String @path("{name}") }}')

    def test_SYN_008_argument_names_support_camelcase_and_snake_case(self, parse: ParseFixture) -> None:
        """SYN-008: Arguments support both camelCase and snake_case."""
        schema = parse("""
            extend api {
                findByName(firstName: String, first_name: String): String @path("find-by-name")
            }
        """)
        operation = next(
            operation for operation in xtx.get_children_of_operation(schema) if operation.name == "findByName"
        )
        assert [argument.name for argument in operation.arguments] == ["firstName", "first_name"]

    @pytest.mark.parametrize("name", ["SomeHeader", "some-header", "some__name", "_internal"])
    def test_SYN_008_argument_invalid(self, name: str, parse_expect_name_error: ParseExpectErrorFixture) -> None:
        """SYN-008: Arguments reject invalid separators and casing."""
        parse_expect_name_error(f'extend api {{ search({name}: String): String @path("search-{name}") }}')

    def test_SYN_009_custom_directive_styles_positive(self, parse: ParseFixture) -> None:
        """SYN-009: Custom directives support camelCase, snake_case, and kebab-case."""
        schema = parse("""
            enum Status @force-generate {
                ACTIVE
            }
            type User @readOnly @query_list @spring-package("domain") @api-v2 {
                status: Status
            }
        """)
        directives = xtx.get_children_of_directive(schema)
        assert {directive.name for directive in directives} >= {
            "force-generate",
            "readOnly",
            "query_list",
            "spring-package",
            "api-v2",
        }

    @pytest.mark.parametrize(
        "name",
        [
            "ReadOnly",
            "read_only-name",
            "read-onlyName",
            "_internal",
            "-internal",
            "custom_",
            "custom-",
            "custom__directive",
            "custom--directive",
            "2fast",
        ],
    )
    def test_SYN_009_custom_directive_invalid(
        self, name: str, parse_expect_name_error: ParseExpectErrorFixture
    ) -> None:
        """SYN-009: Custom directives reject mixed, repeated, leading, and trailing separators."""
        parse_expect_name_error(f"type User @{name} {{ name: String }}")
