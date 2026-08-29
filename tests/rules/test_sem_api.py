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

"""Tests for SEM-8xx rules: Api & Operation rules.

Rules covered:
- SEM-801: An Api may contain zero or more Operations
- SEM-802: An Operation defines an HTTP endpoint
- SEM-803: A custom Operation must specify @path(...)
- SEM-804: An Operation may specify @method(...)
- SEM-805: An Operation may be marked @pagination
- SEM-806: An Operation may declare response headers via @headers(...)
- SEM-807: An Api can be used multiple times in a schema
- SEM-808: An Api can be used once inside an Object via extend api
- SEM-809: Api endpoints must specify unique method/path routes
- SEM-810: APIs may have optional namespace via @namespace(...)
"""

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestSemApi:
    """Tests for SEM-801 to SEM-810: Api & Operation rules."""

    def test_SEM_801_api_with_operation_positive(self, parse: ParseFixture) -> None:
        """SEM-801: An Api with operations is valid."""
        schema = parse("""
            extend api @namespace("PublicApi") {
                getFoo: String @path("foo")
            }
        """)
        apis = xtx.get_children_of_api(schema)
        assert len(apis) == 1
        assert apis[0].namespace == "PublicApi"
        assert len(apis[0].operations) == 1

    def test_SEM_801_empty_top_level_api_positive(self, parse: ParseFixture) -> None:
        """SEM-801: An empty top-level Api is a valid no-op."""
        schema = parse("""
            extend api {
            }
        """)
        apis = xtx.get_children_of_api(schema)
        assert len(apis) == 1
        assert len(apis[0].operations) == 0
        assert xtx.get_children_of_operation(schema) == []

    def test_SEM_801_empty_object_api_suppresses_crud(self, parse: ParseFixture) -> None:
        """SEM-801: An empty object Api suppresses automatic CRUD operations."""
        schema = parse("""
            type User {
                name: String

                extend api {
                }
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.api is not None
        assert obj.api.operations == []
        assert obj.api.has_generated is False
        assert xtx.get_children_of_operation(schema) == []

    def test_SEM_802_operation_defines_endpoint_positive(self, parse: ParseFixture) -> None:
        """SEM-802: Operation defines HTTP endpoint with return type."""
        schema = parse("""
            extend api {
                getUsers: [String] @path("users")
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        op = next(o for o in operations if o.name == "getUsers")
        assert op.name == "getUsers"
        assert op.path == "/users"
        assert op.is_array is True

    def test_SEM_803_operation_path_positive(self, parse: ParseFixture) -> None:
        """SEM-803: A custom Operation with @path(...) is valid and normalized."""
        schema = parse("""
            extend api {
                findByEmail: String @path("users/find-by-email")
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        op = next(o for o in operations if o.name == "findByEmail")
        assert op.path == "/users/find-by-email"

    def test_SEM_803_operation_without_path_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-803: A custom Operation without @path(...) is rejected."""
        parse_expect_semantic_error("""
            extend api {
                findByEmail: String
            }
        """)

    def test_SEM_804_operation_method_get_positive(self, parse: ParseFixture) -> None:
        """SEM-804: Operation may specify @method(GET)."""
        schema = parse("""
            extend api {
                getItem: String @path("item") @method("GET")
            }
        """)
        op = xtx.get_children_of_operation(schema)[0]
        assert op.method == "GET"

    def test_SEM_804_operation_method_post_positive(self, parse: ParseFixture) -> None:
        """SEM-804: Operation may specify @method(POST)."""
        schema = parse("""
            extend api {
                createItem(data: String): String @path("createitems") @method(POST)
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        op = next(o for o in operations if o.name == "createItem")
        assert op.method == "POST"

    def test_SEM_804_operation_method_put_positive(self, parse: ParseFixture) -> None:
        """SEM-804: Operation may specify @method(PUT)."""
        schema = parse("""
            extend api {
                updateItem(data: String): String @path("updateitems") @method(PUT)
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        op = next(o for o in operations if o.name == "updateItem")
        assert op.method == "PUT"

    def test_SEM_804_operation_method_patch_positive(self, parse: ParseFixture) -> None:
        """SEM-804: Operation may specify @method(PATCH)."""
        schema = parse("""
            extend api {
                patchItem(data: String): String @path("patchitems") @method(PATCH)
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        op = next(o for o in operations if o.name == "patchItem")
        assert op.method == "PATCH"

    def test_SEM_804_operation_method_delete_positive(self, parse: ParseFixture) -> None:
        """SEM-804: Operation may specify @method(DELETE)."""
        schema = parse("""
            extend api {
                deleteItem: Void @path("deleteitems") @method(DELETE)
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        op = next(o for o in operations if o.name == "deleteItem")
        assert op.method == "DELETE"

    def test_SEM_805_operation_pagination_positive(self, parse: ParseFixture) -> None:
        """SEM-805: Operation may be marked @pagination.

        NOTE: @pagination requires return type to be Object or Base, not Scalar.
        """
        schema = parse("""
            type Item {
                name: String
            }
            extend api {
                listItems: [Item] @path("listitems") @pagination
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        op = next(o for o in operations if o.name == "listItems")
        assert op.is_pageable is True

    def test_SEM_805_operation_no_pagination_positive(self, parse: ParseFixture) -> None:
        """SEM-805: Operation without @pagination is not pageable."""
        schema = parse("""
            extend api {
                listItems: [String] @path("items")
            }
        """)
        op = xtx.get_children_of_operation(schema)[0]
        assert op.is_pageable is False

    def test_SEM_806_response_headers_preserve_http_names(self, parse: ParseFixture) -> None:
        """SEM-806: Response headers may use hyphenated HTTP header names."""
        schema = parse("""
            extend api {
                listUsers(): [String] @path("custom-users")
                    @headers(X-Total-Count: Int, X-Page-Number: Int)
            }
        """)
        operation = next(
            operation for operation in xtx.get_children_of_operation(schema) if operation.name == "listUsers"
        )
        headers_directive = next(directive for directive in operation.directives if directive.name == "headers")
        assert headers_directive.value == "X-Total-Count: Int, X-Page-Number: Int"
        assert [(header.name, header.value.name, header.is_array) for header in operation.response_headers] == [
            ("X-Total-Count", "Int", False),
            ("X-Page-Number", "Int", False),
        ]

    def test_SEM_807_multiple_apis_positive(self, parse: ParseFixture) -> None:
        """SEM-807: Multiple Api blocks can be used in a schema."""
        schema = parse("""
            extend api {
                getFoo: String @path("foo")
            }
            extend api {
                getBar: String @path("bar")
            }
            extend api {
                getBaz: String @path("baz")
            }
        """)
        apis = xtx.get_children_of_api(schema)
        assert len(apis) == 3

    def test_SEM_808_api_inside_object_positive(self, parse: ParseFixture) -> None:
        """SEM-808: Api can be used once inside an Object."""
        schema = parse("""
            type User {
                name: String

                extend api {
                    findByName(name: String): User @path("users/by-name")
                }
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.api is not None
        assert len(obj.api.operations) == 1
        assert obj.api.has_generated is False
        assert all(not operation.is_generated for operation in obj.api.operations)

    def test_SEM_808_multiple_apis_in_object_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-808: Multiple api blocks in one Object are rejected."""
        parse_expect_semantic_error("""
            type User {
                name: String

                extend api {
                    findByName: User @path("users/by-name")
                }
                extend api {
                    findByEmail: User @path("users/by-email")
                }
            }
        """)

    def test_SEM_809_same_path_with_different_methods_positive(self, parse: ParseFixture) -> None:
        """SEM-809: Different HTTP methods may use the same normalized path."""
        schema = parse("""
            extend api {
                getFoo: String @path("items") @method(GET)
                createFoo: String @path("/ITEMS/") @method(POST)
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        routes = [(operation.method, operation.path) for operation in operations]
        assert [operation.path for operation in operations] == ["/items", "/items"]
        assert len(routes) == len(set(routes))

    def test_SEM_809_duplicate_routes_negative(self, parse_expect_semantic_error: ParseExpectErrorFixture) -> None:
        """SEM-809: Duplicate HTTP method and normalized path pairs are rejected."""
        parse_expect_semantic_error("""
            extend api {
                getFoo: String @path("same")
                getBar: String @path("/SAME/")
            }
        """)
