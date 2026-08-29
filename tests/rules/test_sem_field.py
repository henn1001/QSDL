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

"""Tests for SEM-6xx rules: Field rules.

Rules covered:
- SEM-601: A Field references a ValueType (Scalar, Enum, Base, or Object)
- SEM-602: A Field may be required (! suffix)
- SEM-603: A Field may be array ([...] wrapper)
- SEM-604: A Field may be read-only (@readOnly)
- SEM-605: A Field may be write-only (@writeOnly)
- SEM-606: A Field cannot be both @readOnly and @writeOnly
- SEM-607: A Field may override an inherited field via @override
- SEM-608: A Field without @override cannot redefine an inherited field
- SEM-609: Object fields cannot use reserved metadata names
- SEM-610: Query fields reference only Scalars or Enums
- SEM-611: @opaque applies only to Base-valued fields
"""

import re

import pytest
from textx.exceptions import TextXSemanticError

import qsdl.dsl.textx as xtx
from qsdl import dsl

from .conftest import ParseExpectErrorFixture, ParseFixture


def assert_semantic_error(parse: ParseFixture, raw: str, message: str) -> None:
    """Assert a specific validator error without masking unrelated failures."""
    with pytest.raises(TextXSemanticError, match=re.escape(message)):
        parse(raw)


class TestSemField:
    """Tests for SEM-6xx: Field rules."""

    def test_SEM_601_field_references_scalar_positive(self, parse: ParseFixture) -> None:
        """SEM-601: Field can reference a Scalar."""
        schema = parse("""
            type Foo {
                name: String
                age: Int
                active: Boolean
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        fields = {f.name: f for f in obj.fields}
        assert isinstance(fields["name"].value, dsl.Scalar)
        assert fields["name"].value.name == "String"
        assert isinstance(fields["age"].value, dsl.Scalar)
        assert fields["age"].value.name == "Int"
        assert isinstance(fields["active"].value, dsl.Scalar)
        assert fields["active"].value.name == "Boolean"

    def test_SEM_601_field_references_enum_positive(self, parse: ParseFixture) -> None:
        """SEM-601: Field can reference an Enum."""
        schema = parse("""
            enum Status {
                OPEN
                CLOSED
            }
            type Foo {
                status: Status
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "status")
        assert isinstance(field.value, dsl.Enum)
        assert field.value.name == "Status"

    def test_SEM_601_field_references_base_positive(self, parse: ParseFixture) -> None:
        """SEM-601: Field can reference a Base."""
        schema = parse("""
            base Address {
                street: String
                city: String
            }
            type Person {
                homeAddress: Address
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "homeAddress")
        assert isinstance(field.value, dsl.Base)
        assert field.value.name == "Address"

    def test_SEM_601_field_references_object_positive(self, parse: ParseFixture) -> None:
        """SEM-601: Field can reference an Object."""
        schema = parse("""
            type Department {
                name: String
            }
            type Employee {
                department: Department
            }
        """)
        objects = xtx.get_children_of_object(schema)
        employee = next(o for o in objects if o.name == "Employee")
        field = next(f for f in employee.fields if f.name == "department")
        assert isinstance(field.value, dsl.Object)
        assert field.value.name == "Department"

    def test_SEM_602_field_required_positive(self, parse: ParseFixture) -> None:
        """SEM-602: A Field may be required (! suffix)."""
        schema = parse("""
            type Foo {
                required: String!
                optional: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        fields = {f.name: f for f in obj.fields}
        assert fields["required"].is_required is True
        assert fields["optional"].is_required is False

    def test_SEM_603_field_array_positive(self, parse: ParseFixture) -> None:
        """SEM-603: A Field may be array ([...] wrapper)."""
        schema = parse("""
            type Foo {
                tags: [String]
                single: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        fields = {f.name: f for f in obj.fields}
        assert fields["tags"].is_array is True
        assert fields["single"].is_array is False

    def test_SEM_603_field_array_required_positive(self, parse: ParseFixture) -> None:
        """SEM-603: Array fields can also be required."""
        schema = parse("""
            type Foo {
                tags: [String]!
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "tags")
        assert field.is_array is True
        assert field.is_required is True

    def test_SEM_604_field_readOnly_positive(self, parse: ParseFixture) -> None:
        """SEM-604: A Field may be read-only (@readOnly)."""
        schema = parse("""
            type Foo {
                createdAt: Datetime @readOnly
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        fields = {f.name: f for f in obj.fields}
        assert fields["createdAt"].is_read_only is True
        assert fields["name"].is_read_only is False

    def test_SEM_605_field_writeOnly_positive(self, parse: ParseFixture) -> None:
        """SEM-605: A Field may be write-only (@writeOnly)."""
        schema = parse("""
            type User {
                password: String @writeOnly
                username: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        fields = {f.name: f for f in obj.fields}
        assert fields["password"].is_write_only is True
        assert fields["username"].is_write_only is False

    def test_SEM_606_readOnly_writeOnly_conflict_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-606: A Field cannot be both @readOnly and @writeOnly."""
        parse_expect_semantic_error("""
            type Foo {
                field: String @readOnly @writeOnly
            }
        """)

    def test_SEM_607_override_inherited_field_positive(self, parse: ParseFixture) -> None:
        """SEM-607: A Field may override an inherited field via @override."""
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
        assert field.is_override is True
        assert field.value.name == "Long"

    def test_SEM_607_override_preserves_field_positive(self, parse: ParseFixture) -> None:
        """SEM-607: Override replaces parent field in flattened list."""
        schema = parse("""
            base Parent {
                name: String
                value: Int
            }
            type Child extends Parent {
                value: Long @override
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field_names = [f.name for f in obj.fields]
        assert "name" in field_names
        assert "value" in field_names
        value_field = next(f for f in obj.fields if f.name == "value")
        assert value_field.value.name == "Long"

    def test_SEM_608_redefinition_without_override_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-608: Field without @override cannot redefine inherited field."""
        parse_expect_semantic_error("""
            base Parent {
                field: Int
            }
            type Child extends Parent {
                field: String
            }
        """)

    def test_SEM_608_redefinition_in_base_without_override_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-608: Base extending Base also requires @override for redefinition."""
        parse_expect_semantic_error("""
            base Parent {
                field: Int
            }
            base Child extends Parent {
                field: String
            }
        """)

    @pytest.mark.parametrize("reserved_name", ["id", "uid", "iv"])
    def test_SEM_609_object_reserved_field_negative(self, reserved_name: str, parse: ParseFixture) -> None:
        """SEM-609: Object fields cannot use generated entity metadata names."""
        assert_semantic_error(
            parse,
            f"""
                type User {{
                    {reserved_name}: String
                }}
            """,
            f'The Object User uses a reserved word "{reserved_name}".',
        )

    def test_SEM_609_inherited_object_reserved_field_negative(self, parse: ParseFixture) -> None:
        """SEM-609: Objects cannot inherit a reserved field from a Base."""
        assert_semantic_error(
            parse,
            """
                base Metadata {
                    id: String
                }
                type User extends Metadata {
                    name: String
                }
            """,
            'The Object User uses a reserved word "id".',
        )

    def test_SEM_609_base_id_positive(self, parse: ParseFixture) -> None:
        """SEM-609: A standalone Base may define an id field."""
        schema = parse("""
            base Metadata @force-generate {
                id: String
            }
        """)
        base = xtx.get_children_of_base(schema)[0]
        assert [field.name for field in base.fields] == ["id"]

    def test_SEM_610_query_scalar_and_enum_positive(self, parse: ParseFixture) -> None:
        """SEM-610: Query directives accept scalar and enum values."""
        schema = parse("""
            enum Status {
                ACTIVE
            }
            type Searchable {
                name: String @query
                tags: [String] @queryList
                status: Status @query
            }
        """)
        searchable = xtx.get_children_of_object(schema)[0]
        fields = {field.name: field for field in searchable.fields}
        assert fields["name"].is_query is True
        assert fields["tags"].is_query_list is True
        assert fields["status"].is_query is True

    @pytest.mark.parametrize("directive", ["query", "queryList"])
    @pytest.mark.parametrize(
        ("declaration", "value_type"),
        [
            ("base Filter { term: String }", "Filter"),
            ("type Target { value: String }", "Target"),
        ],
    )
    def test_SEM_610_query_structured_value_negative(
        self, directive: str, declaration: str, value_type: str, parse: ParseFixture
    ) -> None:
        """SEM-610: Query directives reject Base- and Object-valued fields."""
        assert_semantic_error(
            parse,
            f"""
                {declaration}
                type Searchable {{
                    filter: {value_type} @{directive}
                }}
            """,
            "The Field filter for Searchable declares a invalid value as query.",
        )

    def test_SEM_611_opaque_base_positive(self, parse: ParseFixture) -> None:
        """SEM-611: @opaque is valid for a Base-valued field."""
        schema = parse("""
            base Metadata {
                source: String
            }
            type Item {
                metadata: Metadata @opaque
            }
        """)
        item = xtx.get_children_of_object(schema)[0]
        field = next(field for field in item.fields if field.name == "metadata")
        assert field.is_opaque is True

    def test_SEM_611_opaque_non_base_negative(self, parse: ParseFixture) -> None:
        """SEM-611: @opaque rejects a Scalar-valued field."""
        assert_semantic_error(
            parse,
            """
                type Item {
                    metadata: String @opaque
                }
            """,
            "The Field metadata for Item declares opaque on a non Base value.",
        )
