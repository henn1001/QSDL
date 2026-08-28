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
- LOG-203: Multiple instances of same directive on same entity not allowed
"""

import qsdl.dsl.textx as xtx
from qsdl.dsl.util import get_directive_of_name

from .conftest import ParseFixture


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
