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

"""Tests for LOG-1xx rules: Inheritance & Overriding.

Rules covered:
- LOG-101: All inherited fields from supertypes appear in flattened field list
- LOG-102: Child redefining inherited field must use @override
- LOG-103: @override field must have same base type or compatible subtype
"""

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestLogInheritance:
    """Tests for LOG-101 to LOG-103: Inheritance & Overriding."""

    def test_LOG_101_inherited_fields_flattened_positive(self, parse: ParseFixture) -> None:
        """LOG-101: Inherited fields appear in flattened field list."""
        schema = parse("""
            base Auditable {
                createdAt: Datetime
                updatedAt: Datetime
            }
            base Identifiable {
                uuid: String
            }
            type User extends Auditable, Identifiable {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field_names = [f.name for f in obj.fields]
        assert "createdAt" in field_names
        assert "updatedAt" in field_names
        assert "uuid" in field_names
        assert "name" in field_names

    def test_LOG_101_deep_inheritance_flattened_positive(self, parse: ParseFixture) -> None:
        """LOG-101: Deep inheritance chain flattens all fields."""
        schema = parse("""
            base GrandParent {
                grandField: String
            }
            base Parent extends GrandParent {
                parentField: Int
            }
            type Child extends Parent {
                childField: Boolean
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field_names = [f.name for f in obj.fields]
        assert "grandField" in field_names
        assert "parentField" in field_names
        assert "childField" in field_names

    def test_LOG_102_override_required_negative(self, parse_expect_semantic_error: ParseExpectErrorFixture) -> None:
        """LOG-102: Redefining inherited field without @override is rejected."""
        parse_expect_semantic_error("""
            base Parent {
                field: Int
            }
            type Child extends Parent {
                field: String
            }
        """)

    def test_LOG_102_override_provided_positive(self, parse: ParseFixture) -> None:
        """LOG-102: Redefining with @override is allowed."""
        schema = parse("""
            base Parent {
                field: Int
            }
            type Child extends Parent {
                field: Long @override
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "field")
        assert field.value.name == "Long"
        assert field.is_override is True

    def test_LOG_103_override_same_type_positive(self, parse: ParseFixture) -> None:
        """LOG-103: Override with same type is valid."""
        schema = parse("""
            base Parent {
                field: String
            }
            type Child extends Parent {
                field: String @override
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "field")
        assert field.value.name == "String"

    def test_LOG_103_override_different_type_positive(self, parse: ParseFixture) -> None:
        """LOG-103: Override can change type (with warning in implementation)."""
        schema = parse("""
            base Parent {
                field: Int
            }
            type Child extends Parent {
                field: Long @override
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "field")
        assert field.value.name == "Long"
