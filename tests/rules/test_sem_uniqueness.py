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

"""Tests for SEM-1xx rules: Uniqueness constraints.

Rules covered:
- SEM-101: Type names must be unique globally
- SEM-102: Field names must be unique per-type (including inherited)
- SEM-103: Enum values must be unique per-enum
- SEM-104: Operation names/IDs must be globally unique across APIs, including generated CRUD
- SEM-105: Operation routes must be globally unique by HTTP method and normalized URI template
"""

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestSemUniqueness:
    """Tests for SEM-101 to SEM-105: Uniqueness constraints."""

    def test_SEM_101_unique_type_names_positive(self, parse: ParseFixture) -> None:
        """SEM-101: Different type names are allowed."""
        schema = parse("""
            enum Status { OPEN }
            base Auditable { createdAt: Datetime }
            type User extends Auditable {
                name: String
                status: Status
            }
            type Order { total: Float }
        """)
        objects = xtx.get_children_of_object(schema)
        assert len(objects) == 2
        user = next(o for o in objects if o.name == "User")
        assert len(user.supertypes) == 1
        status_field = next(f for f in user.fields if f.name == "status")
        assert status_field.value.name == "Status"

    def test_SEM_101_duplicate_object_names_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-101: Duplicate Object names are rejected."""
        parse_expect_semantic_error("""
            type Foo { name: String }
            type Foo { other: Int }
        """)

    def test_SEM_101_duplicate_object_base_names_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-101: Object and Base with same name are rejected."""
        parse_expect_semantic_error("""
            base Foo { name: String }
            type Foo { other: Int }
        """)

    def test_SEM_101_duplicate_object_enum_names_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-101: Object and Enum with same name are rejected."""
        parse_expect_semantic_error("""
            enum Foo { OPEN }
            type Foo { name: String }
        """)

    def test_SEM_102_unique_field_names_positive(self, parse: ParseFixture) -> None:
        """SEM-102: Different field names within a type are allowed."""
        schema = parse("""
            type Foo {
                name: String
                age: Int
                active: Boolean
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field_names = [f.name for f in obj.fields]
        assert len(field_names) == len(set(field_names))

    def test_SEM_102_duplicate_field_names_negative(self, parse_expect_semantic_error: ParseExpectErrorFixture) -> None:
        """SEM-102: Duplicate field names within a type are rejected."""
        parse_expect_semantic_error("""
            type Foo {
                name: String
                name: Int
            }
        """)

    def test_SEM_103_unique_enum_values_positive(self, parse: ParseFixture) -> None:
        """SEM-103: Different enum values are allowed."""
        schema = parse("""
            enum Status {
                OPEN
                CLOSED
                PENDING
            }
            type Foo {
                status: Status
            }
        """)
        enums = xtx.get_children_of_enum(schema)
        status_enum = next(e for e in enums if e.name == "Status")
        assert len(status_enum.values) == 3
        assert len(status_enum.values) == len(set(status_enum.values))

    def test_SEM_103_duplicate_enum_values_negative(self, parse_expect_semantic_error: ParseExpectErrorFixture) -> None:
        """SEM-103: Duplicate enum values are rejected."""
        parse_expect_semantic_error("""
            enum Status {
                OPEN
                OPEN
            }
            type Foo {
                status: Status
            }
        """)

    def test_SEM_104_unique_operation_names_positive(self, parse: ParseFixture) -> None:
        """SEM-104: Different operation names within an Api are allowed."""
        schema = parse("""
            extend api {
                getFoo: String @path("foo")
                getBar: String @path("bar")
            }
        """)
        apis = xtx.get_children_of_api(schema)
        operations = xtx.get_children_of_operation(schema)
        assert len(apis) == 1
        assert len(operations) == 2

    def test_SEM_104_duplicate_operation_names_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-104: Duplicate operation names within an Api are rejected."""
        parse_expect_semantic_error("""
            extend api {
                getFoo: String @path("foo")
                getFoo: String @path("bar")
            }
        """)

    def test_SEM_104_duplicate_operation_names_across_apis_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-104: Duplicate operation names across Api blocks are rejected."""
        parse_expect_semantic_error("""
            extend api {
                lookup: String @path("first")
            }
            extend api {
                lookup: String @path("second")
            }
        """)

    def test_SEM_104_generated_and_custom_operation_names_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-104: Custom and generated operation names share one global namespace."""
        parse_expect_semantic_error("""
            type User {
                name: String
            }
            extend api {
                getUser: String @path("lookup")
            }
        """)

    def test_SEM_105_same_path_with_different_methods_positive(self, parse: ParseFixture) -> None:
        """SEM-105: Different HTTP methods may use the same normalized path."""
        schema = parse("""
            extend api {
                getItems: String @path("items") @method(GET)
                createItems: String @path("/ITEMS/") @method(POST)
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        routes = [(operation.method, operation.path) for operation in operations]
        assert [operation.path for operation in operations] == ["/items", "/items"]
        assert len(routes) == len(set(routes))

    def test_SEM_105_duplicate_normalized_routes_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-105: Duplicate method and normalized path pairs are rejected."""
        parse_expect_semantic_error("""
            extend api {
                first: String @path("same")
                second: String @path("/SAME/")
            }
        """)

    def test_SEM_105_generated_and_custom_routes_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-105: Custom and generated operation routes share one global namespace."""
        parse_expect_semantic_error("""
            type User {
                name: String
            }
            extend api {
                listUsers: String @path("/USERS/") @method(GET)
            }
        """)
