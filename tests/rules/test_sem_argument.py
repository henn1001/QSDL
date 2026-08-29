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

"""Tests for SEM-9xx rules: Argument rules.

Rules covered:
- SEM-901: An Argument defines an Operation parameter
- SEM-902: An Argument may be required (! suffix)
- SEM-903: An Argument may be query (? suffix), with explicit-location precedence
- SEM-904: An Argument may be header (^ suffix), with explicit-location precedence
- SEM-905: Argument without explicit location is inferred from context and path takes precedence
- SEM-906: Query Base arguments contain only Scalar or Enum fields
- SEM-907: Object/Base operations have at most one unlocated argument
- SEM-908: DELETE operations cannot have body arguments
"""

import re

import pytest
from textx.exceptions import TextXSemanticError

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


def assert_semantic_error(parse: ParseFixture, raw: str, message: str) -> None:
    """Assert a specific validator error without masking unrelated failures."""
    with pytest.raises(TextXSemanticError, match=re.escape(message)):
        parse(raw)


class TestSemArgument:
    """Tests for SEM-901 to SEM-908: Argument rules."""

    def test_SEM_901_argument_defines_parameter_positive(self, parse: ParseFixture) -> None:
        """SEM-901: Argument defines an Operation parameter."""
        schema = parse("""
            extend api {
                search(query: String): [String] @path("search")
            }
        """)
        args = xtx.get_children_of_argument(schema)
        assert len(args) == 1
        assert args[0].name == "query"
        assert args[0].value.name == "String"

    def test_SEM_901_multiple_arguments_positive(self, parse: ParseFixture) -> None:
        """SEM-901: Operation can have multiple arguments."""
        schema = parse("""
            extend api {
                search(query: String, limit: Int, offset: Int): [String] @path("search")
            }
        """)
        args = xtx.get_children_of_argument(schema)
        arg_names = [a.name for a in args]
        assert "query" in arg_names
        assert "limit" in arg_names
        assert "offset" in arg_names

    def test_SEM_902_argument_required_positive(self, parse: ParseFixture) -> None:
        """SEM-902: Argument may be required (! suffix)."""
        schema = parse("""
            extend api {
                create(data: String!): String @path("items") @method("POST")
            }
        """)
        args = xtx.get_children_of_argument(schema)
        data_arg = next(a for a in args if a.name == "data")
        assert data_arg.is_required is True

    def test_SEM_902_argument_optional_positive(self, parse: ParseFixture) -> None:
        """SEM-902: Argument without ! is optional."""
        schema = parse("""
            extend api {
                search(query: String): [String] @path("search")
            }
        """)
        args = xtx.get_children_of_argument(schema)
        query_arg = next(a for a in args if a.name == "query")
        assert query_arg.is_required is False

    def test_SEM_903_argument_query_positive(self, parse: ParseFixture) -> None:
        """SEM-903: Argument may be query (? suffix) and overrides method inference."""
        schema = parse("""
            extend api {
                search(filter: String?): [String] @path("search") @method(POST)
            }
        """)
        operation = xtx.get_children_of_operation(schema)[0]
        args = xtx.get_children_of_argument(schema)
        filter_arg = next(a for a in args if a.name == "filter")
        assert filter_arg.is_query is True
        assert [argument.name for argument in operation.query_parameters] == ["filter"]
        assert operation.path_parameters == []
        assert operation.header_parameters == []
        assert operation.body_parameters == []

    @pytest.mark.parametrize("method", ["GET", "POST", "PUT", "PATCH", "DELETE"])
    def test_SEM_904_argument_header_positive(self, method: str, parse: ParseFixture) -> None:
        """SEM-904: A header argument stays a header for every HTTP method."""
        schema = parse(f"""
            extend api {{
                secure{method.title()}(token: String^): String @path("secure-{method.lower()}") @method({method})
            }}
        """)
        operation = xtx.get_children_of_operation(schema)[0]
        args = xtx.get_children_of_argument(schema)
        token_arg = next(a for a in args if a.name == "token")
        assert token_arg.is_header is True
        assert [argument.name for argument in operation.header_parameters] == ["token"]
        assert operation.path_parameters == []
        assert operation.query_parameters == []
        assert operation.body_parameters == []

    def test_SEM_903_904_argument_locations_are_mutually_exclusive(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-903/904: Query and header modifiers cannot be combined."""
        parse_expect_semantic_error("""
            extend api {
                search(filter: String?^): String @path("search")
            }
        """)

    def test_SEM_905_argument_location_inferred_from_method(self, parse: ParseFixture) -> None:
        """SEM-905: Unmodified arguments use the HTTP method default location."""
        schema = parse("""
            extend api {
                getItem(filter: String): String @path("get-item") @method(GET)
                createItem(data: String): String @path("create-item") @method(POST)
                replaceItem(data: String): String @path("replace-item") @method(PUT)
                patchItem(data: String): String @path("patch-item") @method(PATCH)
            }
        """)
        operations = {operation.name: operation for operation in xtx.get_children_of_operation(schema)}

        assert [argument.name for argument in operations["getItem"].query_parameters] == ["filter"]
        assert operations["getItem"].body_parameters == []
        assert [argument.name for argument in operations["createItem"].body_parameters] == ["data"]
        assert operations["createItem"].query_parameters == []
        assert [argument.name for argument in operations["replaceItem"].body_parameters] == ["data"]
        assert operations["replaceItem"].query_parameters == []
        assert [argument.name for argument in operations["patchItem"].body_parameters] == ["data"]
        assert operations["patchItem"].query_parameters == []

        for operation in operations.values():
            assert operation.path_parameters == []
            assert operation.header_parameters == []

    def test_SEM_905_path_arguments_take_precedence(self, parse: ParseFixture) -> None:
        """SEM-905: URI placeholders remain path parameters."""
        schema = parse("""
            extend api {
                getItem: String @path("items/{item_id}") @method(GET)
            }
        """)
        operation = xtx.get_children_of_operation(schema)[0]

        assert [argument.name for argument in operation.path_parameters] == ["item_id"]
        assert operation.query_parameters == []
        assert operation.header_parameters == []
        assert operation.body_parameters == []

    def test_SEM_905_argument_array_positive(self, parse: ParseFixture) -> None:
        """SEM-905: Argument can be array type."""
        schema = parse("""
            extend api {
                bulkCreate(items: [String]): [String] @path("items/bulk") @method("POST")
            }
        """)
        args = xtx.get_children_of_argument(schema)
        items_arg = next(a for a in args if a.name == "items")
        assert items_arg.is_array is True

    def test_SEM_906_query_base_with_scalar_fields_positive(self, parse: ParseFixture) -> None:
        """SEM-906: A query Base may contain scalar fields."""
        schema = parse("""
            base Filter {
                term: String
                page: Int
            }
            extend api {
                search(filter: Filter?): String @path("search")
            }
        """)
        operation = xtx.get_children_of_operation(schema)[0]
        assert [argument.name for argument in operation.query_parameters] == ["filter"]

    @pytest.mark.parametrize(
        "nested_declaration",
        ["base Address { city: String }", "type Address { city: String }"],
    )
    def test_SEM_906_query_base_with_nested_value_negative(self, nested_declaration: str, parse: ParseFixture) -> None:
        """SEM-906: A query Base cannot contain nested Base or Object fields."""
        assert_semantic_error(
            parse,
            f"""
                {nested_declaration}
                base Filter {{
                    address: Address
                }}
                extend api {{
                    search(filter: Filter?): String @path("search")
                }}
            """,
            "The Base type Filter used as query parameter in operation search contains a nested type field 'address'. Query parameters with Base types must only contain scalar/enum fields.",
        )

    @pytest.mark.parametrize(
        ("declaration", "value_type"),
        [
            ("type Item { value: String }", "Item"),
            ("base Item { value: String }", "Item"),
        ],
    )
    def test_SEM_907_single_reference_body_positive(
        self, declaration: str, value_type: str, parse: ParseFixture
    ) -> None:
        """SEM-907: An operation may have one unlocated Object or Base body argument."""
        schema = parse(f"""
            {declaration}
            extend api {{
                saveItem(item: {value_type}): String @path("custom-items") @method(POST)
            }}
        """)
        operation = next(
            operation for operation in xtx.get_children_of_operation(schema) if operation.name == "saveItem"
        )
        assert [argument.name for argument in operation.body_parameters] == ["item"]

    @pytest.mark.parametrize("declaration", ["type Item { value: String }", "base Item { value: String }"])
    def test_SEM_907_multiple_reference_body_arguments_negative(self, declaration: str, parse: ParseFixture) -> None:
        """SEM-907: An operation cannot mix multiple unlocated Object or Base arguments."""
        assert_semantic_error(
            parse,
            f"""
                {declaration}
                extend api {{
                    merge(first: Item, second: Item): String @path("merge-items") @method(POST)
                }}
            """,
            "The Operation merge references more than one Object or tries to mix them. Currently not supported",
        )

    def test_SEM_908_delete_query_argument_positive(self, parse: ParseFixture) -> None:
        """SEM-908: DELETE may use explicitly located query and header arguments."""
        schema = parse("""
            extend api {
                deleteItems(filter: String?, token: String^): Void @path("items") @method(DELETE)
            }
        """)
        operation = xtx.get_children_of_operation(schema)[0]
        assert [argument.name for argument in operation.query_parameters] == ["filter"]
        assert [argument.name for argument in operation.header_parameters] == ["token"]
        assert operation.body_parameters == []

    def test_SEM_908_delete_body_argument_negative(self, parse: ParseFixture) -> None:
        """SEM-908: DELETE rejects an unlocated body argument."""
        assert_semantic_error(
            parse,
            """
                extend api {
                    deleteItem(item: String): Void @path("items") @method(DELETE)
                }
            """,
            "The DELETE Operation deleteItem specifies a body. This is not supported.",
        )
