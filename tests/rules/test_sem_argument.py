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
- SEM-903: An Argument may be query (? suffix)
- SEM-904: An Argument may be header (^ suffix)
- SEM-905: Argument without explicit location is inferred from context
"""

import qsdl.dsl.textx as xtx

from .conftest import ParseFixture


class TestSemArgument:
    """Tests for SEM-901 to SEM-905: Argument rules."""

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
        """SEM-903: Argument may be query (? suffix)."""
        schema = parse("""
            extend api {
                search(filter: String?): [String] @path("search")
            }
        """)
        args = xtx.get_children_of_argument(schema)
        filter_arg = next(a for a in args if a.name == "filter")
        assert filter_arg.is_query is True

    def test_SEM_904_argument_header_positive(self, parse: ParseFixture) -> None:
        """SEM-904: Argument may be header (^ suffix)."""
        schema = parse("""
            extend api {
                secure(token: String^): String @path("secure")
            }
        """)
        args = xtx.get_children_of_argument(schema)
        token_arg = next(a for a in args if a.name == "token")
        assert token_arg.is_header is True

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
