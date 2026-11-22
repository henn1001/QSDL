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
- LOG-103: @override replaces an inherited field; changed value types are allowed with a warning
"""

import pytest
from textx.exceptions import TextXSemanticError

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
        assert [f.name for f in obj.fields] == ["name"]
        assert [f.name for f in obj.effective_fields] == ["id", "createdAt", "updatedAt", "uuid", "name"]
        created = obj.effective_fields[1]
        assert created is obj.supertypes[0].fields[0]
        assert created.parent is obj.supertypes[0]

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
        assert [f.name for f in obj.effective_fields] == ["id", "grandField", "parentField", "childField"]
        (parent,) = obj.supertypes
        assert [f.name for f in parent.fields] == ["parentField"]
        assert [f.name for f in parent.effective_fields] == ["grandField", "parentField"]

    def test_LOG_101_multiple_inheritance_conflict_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """LOG-101: Conflicting fields from multiple supertypes are rejected."""
        parse_expect_semantic_error("""
            base First {
                field: String
            }
            base Second {
                field: Int
            }
            type Child extends First, Second {
                value: Boolean
            }
        """)

    def test_LOG_101_multiple_inheritance_conflict_resolved_by_override_positive(self, parse: ParseFixture) -> None:
        """LOG-101: A child override resolves conflicting fields from multiple supertypes."""
        schema = parse("""
            base First {
                field: String
            }
            base Second {
                field: Int
            }
            type Child extends First, Second {
                field: Long @override
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        fields = [field for field in obj.fields if field.name == "field"]
        assert len(fields) == 1
        assert fields[0].value.name == "Long"
        assert fields[0].directive.is_override

    def test_LOG_101_duplicate_supertype_positive(self, parse: ParseFixture) -> None:
        """LOG-101: Repeated inheritance of the same supertype does not duplicate fields."""
        schema = parse("""
            base Shared {
                sharedField: String
            }
            base Combined extends Shared, Shared {
                combinedField: Int
            }
            type Child extends Combined {
                childField: Boolean
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert [f.name for f in obj.effective_fields] == ["id", "sharedField", "combinedField", "childField"]

    def test_LOG_101_diamond_inheritance_positive(self, parse: ParseFixture) -> None:
        """LOG-101: Diamond inheritance includes shared fields only once."""
        schema = parse("""
            base Root {
                rootField: String
            }
            base Left extends Root {
                leftField: Int
            }
            base Right extends Root {
                rightField: Boolean
            }
            type Child extends Left, Right {
                childField: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert [f.name for f in obj.effective_fields] == ["id", "rootField", "leftField", "rightField", "childField"]
        root = obj.supertypes[0].supertypes[0]
        assert obj.effective_fields[1] is root.fields[0]

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
        assert field.directive.is_override

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

    def test_LOG_103_override_changed_type_positive(
        self, parse: ParseFixture, caplog: pytest.LogCaptureFixture
    ) -> None:
        """LOG-103: Override can change value type with a warning during model processing."""
        schema = parse("""
            base Parent {
                field: Int
            }
            type Child extends Parent {
                field: Long @override
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.effective_fields[1] is obj.fields[0]
        assert obj.effective_fields[1].value.name == "Long"
        assert sum("was redefined with a different type by 'Child'" in msg for msg in caplog.messages) == 1

    def test_cycle_reached_from_object(self, parse: ParseFixture) -> None:
        """Report the circular extends chain before inspecting inherited fields."""
        with pytest.raises(TextXSemanticError, match="Circular inheritance.*Left -> Right -> Left") as error:
            parse("type Entry extends Left {}\nbase Left extends Right {}\nbase Right extends Left {}")
        assert error.value.line == 2
        assert error.value.col == 1

    def test_ignored_override(self, parse: ParseFixture) -> None:
        """Ignore filtering does not restore the replaced parent field."""
        schema = parse("""
            base Named {
                label: String
                owner: String
            }
            type Item extends Named {
                label: String @override @ignore
                note: String
            }
        """)
        (item,) = xtx.get_children_of_object(schema)
        label, note = item.fields
        (parent,) = item.supertypes
        assert parent.fields[0].parent is parent
        assert label.parent is item
        assert [f.name for f in item.effective_fields] == ["id", "label", "owner", "note"]
        assert item.effective_fields[1] is label
        assert [f.name for f in item.generation_fields] == ["id", "owner", "note"]
        assert item.generation_fields[-1] is note
        assert [f.name for f in xtx.get_children_of_field(schema)] == ["label", "note"]
