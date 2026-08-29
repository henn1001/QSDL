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

"""Tests for SEM-4xx rules: Base rules.

Rules covered:
- SEM-401: Base types define reusable field collections
- SEM-402: Base may extend zero or more other Bases
- SEM-403: Base may be marked @deprecated
- SEM-404: Base cannot be directly instantiated (used only for inheritance)
- SEM-405: Bases may have optional namespace via @namespace(...)
"""

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestSemBase:
    """Tests for SEM-401 to SEM-405: Base rules."""

    def test_SEM_401_base_defines_fields_positive(self, parse: ParseFixture) -> None:
        """SEM-401: Base types define reusable field collections."""
        schema = parse("""
            base Auditable {
                createdAt: Datetime
                updatedAt: Datetime
            }
            type Foo extends Auditable {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        base = obj.supertypes[0]
        assert base.name == "Auditable"
        field_names = [f.name for f in base.fields]
        assert "createdAt" in field_names
        assert "updatedAt" in field_names

    def test_SEM_402_base_extends_nothing_positive(self, parse: ParseFixture) -> None:
        """SEM-402: Base may extend zero Bases."""
        schema = parse("""
            base Simple {
                name: String
            }
            type Foo extends Simple {
                other: Int
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        simple = obj.supertypes[0]
        assert simple.supertypes == []

    def test_SEM_402_base_extends_one_positive(self, parse: ParseFixture) -> None:
        """SEM-402: Base may extend one Base."""
        schema = parse("""
            base Parent {
                parentField: String
            }
            base Child extends Parent {
                childField: Int
            }
            type Foo extends Child {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        child = obj.supertypes[0]
        assert child.name == "Child"
        assert len(child.supertypes) == 1
        assert child.supertypes[0].name == "Parent"

    def test_SEM_402_base_extends_multiple_positive(self, parse: ParseFixture) -> None:
        """SEM-402: Base may extend multiple Bases."""
        schema = parse("""
            base Auditable {
                createdAt: Datetime
            }
            base Identifiable {
                uuid: String
            }
            base Combined extends Auditable, Identifiable {
                name: String
            }
            type Foo extends Combined {
                other: Int
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        combined = obj.supertypes[0]
        assert combined.name == "Combined"
        assert len(combined.supertypes) == 2
        supertype_names = [s.name for s in combined.supertypes]
        assert "Auditable" in supertype_names
        assert "Identifiable" in supertype_names

    def test_SEM_402_base_circular_inheritance_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-402: Circular inheritance is detected and rejected."""
        parse_expect_semantic_error("""
            base A extends B {
                fieldA: Int
            }
            base B extends A {
                fieldB: Int
            }
        """)

    def test_SEM_403_base_deprecated_positive(self, parse: ParseFixture) -> None:
        """SEM-403: Base may be marked @deprecated."""
        schema = parse("""
            base OldStyle @deprecated @namespace("LegacyCommon") {
                legacy: String
            }
            type Foo extends OldStyle {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        old_style = obj.supertypes[0]
        assert old_style.is_deprecated is True
        assert old_style.namespace == "LegacyCommon"

    def test_SEM_403_base_not_deprecated_positive(self, parse: ParseFixture) -> None:
        """SEM-403: Base without @deprecated is not deprecated."""
        schema = parse("""
            base Modern {
                current: String
            }
            type Foo extends Modern {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        modern = obj.supertypes[0]
        assert modern.is_deprecated is False
