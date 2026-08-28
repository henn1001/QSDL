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

"""Tests for SEM-2xx rules: Scalar rules.

Rules covered:
- SEM-201: Scalars are leaf types and cannot be extended
- SEM-202: Builtin scalars: Int, Long, Float, Double, String, Boolean, Date, Datetime, Object, Void
"""

import qsdl.dsl.textx as xtx
from qsdl import dsl

from .conftest import ParseFixture


class TestSemScalar:
    """Tests for SEM-201 to SEM-202: Scalar rules."""

    def test_SEM_201_scalar_is_leaf_type_positive(self, parse: ParseFixture) -> None:
        """SEM-201: Scalars are leaf types."""
        schema = parse("""
            type Foo {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "name")
        assert isinstance(field.value, dsl.Scalar)

    def test_SEM_201_custom_scalar_positive(self, parse: ParseFixture) -> None:
        """SEM-201: Custom scalars can be defined."""
        schema = parse("""
            scalar Email

            type User {
                email: Email
            }
        """)
        scalars = xtx.get_children_of_scalar(schema)
        custom = next((s for s in scalars if s.name == "Email"), None)
        assert custom is not None

    def test_SEM_202_builtin_int_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Int is available."""
        schema = parse("""
            type Foo {
                value: Int
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "Int"

    def test_SEM_202_builtin_long_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Long is available."""
        schema = parse("""
            type Foo {
                value: Long
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "Long"

    def test_SEM_202_builtin_float_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Float is available."""
        schema = parse("""
            type Foo {
                value: Float
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "Float"

    def test_SEM_202_builtin_double_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Double is available."""
        schema = parse("""
            type Foo {
                value: Double
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "Double"

    def test_SEM_202_builtin_string_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar String is available."""
        schema = parse("""
            type Foo {
                value: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "String"

    def test_SEM_202_builtin_boolean_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Boolean is available."""
        schema = parse("""
            type Foo {
                value: Boolean
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "Boolean"

    def test_SEM_202_builtin_date_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Date is available."""
        schema = parse("""
            type Foo {
                value: Date
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "Date"

    def test_SEM_202_builtin_datetime_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Datetime is available."""
        schema = parse("""
            type Foo {
                value: Datetime
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "Datetime"

    def test_SEM_202_builtin_object_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Object (generic) is available."""
        schema = parse("""
            type Foo {
                value: Object
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "value")
        assert field.value.name == "Object"

    def test_SEM_202_builtin_void_positive(self, parse: ParseFixture) -> None:
        """SEM-202: Builtin scalar Void is available for operations."""
        schema = parse("""
            extend api {
                doSomething: Void @path("action")
            }
        """)
        operations = xtx.get_children_of_operation(schema)
        op = next(o for o in operations if o.name == "doSomething")
        assert op.value is None or op.value.name == "Void"
