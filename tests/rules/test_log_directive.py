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

"""Tests for LOG-2xx rules: Directive & Metadata.

Rules covered:
- LOG-201: Directives are generator-agnostic or generator-specific
- LOG-202: Custom directives are preserved in the model
- LOG-203: Duplicate directive names on the same entity are semantic errors
"""

import pytest

import qsdl.dsl.textx as xtx
from qsdl.dsl.util import get_directive_of_name

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestLogDirective:
    """Tests for LOG-201 to LOG-203: Directive & Metadata."""

    def test_LOG_201_core_directive_positive(self, parse: ParseFixture) -> None:
        """LOG-201: Core directives like @readOnly are generator-agnostic."""
        schema = parse("""
            type Foo {
                created: Datetime @readOnly
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "created")
        assert field.is_read_only is True

    def test_LOG_201_generator_directive_positive(self, parse: ParseFixture) -> None:
        """LOG-201: Generator-specific directives like @openapi(...) are supported."""
        schema = parse("""
            scalar Email @openapi("string, format:email")

            type User {
                email: Email
            }
        """)
        scalars = xtx.get_children_of_scalar(schema)
        email_scalar = next(s for s in scalars if s.name == "Email")
        directive = get_directive_of_name("openapi", email_scalar)
        assert directive is not None
        assert directive.value == "string, format:email"

    def test_LOG_202_custom_directive_preserved_positive(self, parse: ParseFixture) -> None:
        """LOG-202: Custom directives are preserved in the model."""
        schema = parse("""
            type Foo @myCustom("value") {
                field: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        directive = get_directive_of_name("myCustom", obj)
        assert directive is not None
        assert directive.value == "value"

    def test_LOG_202_multiple_different_directives_positive(self, parse: ParseFixture) -> None:
        """LOG-202: Multiple different directives on same entity are preserved."""
        schema = parse("""
            type Foo @first("a") @second("b") {
                field: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        first = get_directive_of_name("first", obj)
        second = get_directive_of_name("second", obj)
        assert first is not None
        assert first.value == "a"
        assert second is not None
        assert second.value == "b"

    def test_LOG_202_field_directive_preserved_positive(self, parse: ParseFixture) -> None:
        """LOG-202: Custom directives on fields are preserved."""
        schema = parse("""
            type Foo {
                field: String @custom("test")
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "field")
        directive = get_directive_of_name("custom", field)
        assert directive is not None
        assert directive.value == "test"

    @pytest.mark.parametrize(
        "raw",
        [
            """
                type Foo @custom @custom {
                    field: String
                }
            """,
            """
                scalar Email @openapi("string") @openapi("string")
            """,
            """
                type Foo {
                    field: String @custom @custom
                }
            """,
            """
                extend api @custom @custom {
                    getFoo: String @path("foo")
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo") @custom @custom
                }
            """,
            """
                type Foo @namespace("One") @namespace("Two") {
                    field: String
                }
            """,
            """
                type Foo {
                    field: String @readOnly @readOnly
                }
            """,
            """
                type Foo {
                    field: String @minSize(1) @minSize(2)
                }
            """,
            """
                extend api @namespace("One") @namespace("Two") {
                    getFoo: String @path("foo")
                }
            """,
            """
                type Foo {
                    field: String
                    extend api @generate("GET") @generate("GET") {}
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo") @path("bar")
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo") @method(GET) @method(POST)
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo") @pagination @pagination
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo")
                        @consumes("application/json") @consumes("text/plain")
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo")
                        @produces("application/json") @produces("text/plain")
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo")
                        @headers(X-Token: String) @headers(X-Request: String)
                }
            """,
        ],
    )
    def test_LOG_203_duplicate_directive_negative(
        self, raw: str, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """LOG-203: Repeated custom and special directives are semantic errors."""
        parse_expect_semantic_error(raw)
