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

"""Tests for LOG-4xx rules: Import & Composition.

Rules covered:
- LOG-401: Schemas may import other .qsdl files via import "path/to/file.qsdl"
- LOG-402: Imported types are merged; duplicates cause validation error
- LOG-403: Circular imports are not allowed
"""

from pathlib import Path

import pytest

import qsdl.dsl.textx as xtx
from qsdl.dsl.textx import parse_schema

from .conftest import QsdlFileFixture


class TestLogImport:
    """Tests for LOG-401 to LOG-403: Import & Composition."""

    def test_LOG_401_import_types_positive(self, qsdl_file: QsdlFileFixture, tmp_path: Path) -> None:
        """LOG-401: Import types from another file."""
        qsdl_file(
            "base.qsdl",
            """
            base Auditable {
                createdAt: Datetime
            }
        """,
        )
        main_file = qsdl_file(
            "main.qsdl",
            """
            import "base.qsdl"

            type User extends Auditable {
                name: String
            }
        """,
        )
        schema = parse_schema(input_path=main_file)
        objects = xtx.get_children_of_object(schema)
        assert len(objects) == 1
        obj = objects[0]
        assert obj.name == "User"
        assert len(obj.supertypes) == 1
        assert obj.supertypes[0].name == "Auditable"
        field_names = [f.name for f in obj.fields]
        assert "createdAt" in field_names
        assert "name" in field_names

    def test_LOG_401_import_enum_positive(self, qsdl_file: QsdlFileFixture, tmp_path: Path) -> None:
        """LOG-401: Import enum from another file."""
        qsdl_file(
            "enums.qsdl",
            """
            enum Status {
                OPEN
                CLOSED
            }
        """,
        )
        main_file = qsdl_file(
            "main.qsdl",
            """
            import "enums.qsdl"

            type Task {
                status: Status
            }
        """,
        )
        schema = parse_schema(input_path=main_file)
        enums = xtx.get_children_of_enum(schema)
        assert len(enums) == 1
        assert enums[0].name == "Status"

    def test_LOG_401_import_multiple_files_positive(self, qsdl_file: QsdlFileFixture, tmp_path: Path) -> None:
        """LOG-401: Import from multiple files."""
        qsdl_file(
            "audit.qsdl",
            """
            base Auditable {
                createdAt: Datetime
            }
        """,
        )
        qsdl_file(
            "status.qsdl",
            """
            enum Status {
                ACTIVE
                INACTIVE
            }
        """,
        )
        main_file = qsdl_file(
            "main.qsdl",
            """
            import "audit.qsdl"
            import "status.qsdl"

            type User extends Auditable {
                name: String
                status: Status
            }
        """,
        )
        schema = parse_schema(input_path=main_file)
        objects = xtx.get_children_of_object(schema)
        assert len(objects) == 1
        obj = objects[0]
        assert len(obj.supertypes) == 1
        assert obj.supertypes[0].name == "Auditable"
        status_field = next(f for f in obj.fields if f.name == "status")
        assert status_field.value.name == "Status"

    def test_LOG_402_duplicate_type_negative(self, qsdl_file: QsdlFileFixture, tmp_path: Path) -> None:
        """LOG-402: Duplicate type names across imports cause error."""
        qsdl_file(
            "first.qsdl",
            """
            type Foo {
                field: String
            }
        """,
        )
        main_file = qsdl_file(
            "main.qsdl",
            """
            import "first.qsdl"

            type Foo {
                other: Int
            }
        """,
        )
        with pytest.raises(Exception, match=".+"):
            parse_schema(input_path=main_file)

    def test_LOG_403_circular_import_negative(self, qsdl_file: QsdlFileFixture, tmp_path: Path) -> None:
        """LOG-403: Circular imports are detected and rejected."""
        qsdl_file(
            "a.qsdl",
            """
            import "b.qsdl"

            base A {
                field: String
            }
        """,
        )
        qsdl_file(
            "b.qsdl",
            """
            import "a.qsdl"

            base B {
                field: Int
            }
        """,
        )
        main_file = qsdl_file(
            "main.qsdl",
            """
            import "a.qsdl"

            type Foo extends A {
                name: String
            }
        """,
        )
        with pytest.raises(Exception, match=".+"):
            parse_schema(input_path=main_file)
