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
from textx.exceptions import TextXSemanticError

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

    def test_LOG_401_nested_imports_positive(self, qsdl_file: QsdlFileFixture) -> None:
        """LOG-401: Transitive imports are merged."""
        qsdl_file(
            "common.qsdl",
            """
            base Common @force-generate {
                commonValue: String
            }
        """,
        )
        qsdl_file(
            "nested.qsdl",
            """
            import "common.qsdl"

            base Nested extends Common @force-generate {
                nestedValue: String
            }
        """,
        )
        main_file = qsdl_file(
            "main.qsdl",
            """
            import "nested.qsdl"

            type User extends Nested {
                name: String
            }
        """,
        )

        schema = parse_schema(input_path=main_file)
        bases = {base.name for base in xtx.get_children_of_base(schema)}
        assert {"Common", "Nested"}.issubset(bases)
        user = xtx.get_children_of_object(schema)[0]
        assert {field.name for field in user.fields} >= {"commonValue", "nestedValue", "name"}

    def test_LOG_401_shared_import_positive(self, qsdl_file: QsdlFileFixture) -> None:
        """LOG-401: A shared transitive import is merged once."""
        qsdl_file(
            "common.qsdl",
            """
            base Common @force-generate {
                commonValue: String
            }
        """,
        )
        qsdl_file(
            "left.qsdl",
            """
            import "common.qsdl"

            base Left extends Common {
                leftValue: String
            }
        """,
        )
        qsdl_file(
            "right.qsdl",
            """
            import "common.qsdl"

            base Right extends Common {
                rightValue: String
            }
        """,
        )
        main_file = qsdl_file(
            "main.qsdl",
            """
            import "left.qsdl"
            import "right.qsdl"

            type User extends Left, Right {
                name: String
            }
        """,
        )

        schema = parse_schema(input_path=main_file)
        assert sum(base.name == "Common" for base in xtx.get_children_of_base(schema)) == 1

    def test_LOG_401_canonical_aliases_positive(self, tmp_path: Path) -> None:
        """LOG-401: Aliases to one physical file are merged once."""
        common_file = tmp_path / "common.qsdl"
        common_file.write_text("base Common @force-generate { value: String }\n", encoding="utf-8")
        alias_file = tmp_path / "common-alias.qsdl"
        alias_file.symlink_to(common_file)
        main_file = tmp_path / "main.qsdl"
        main_file.write_text(
            """
            import "common.qsdl"
            import "common-alias.qsdl"

            type User extends Common {
                name: String
            }
            """,
            encoding="utf-8",
        )

        schema = parse_schema(input_path=main_file)
        assert sum(base.name == "Common" for base in xtx.get_children_of_base(schema)) == 1

    def test_LOG_401_metamodel_reuse_positive(self, qsdl_file: QsdlFileFixture) -> None:
        """LOG-401: Import loading state does not leak between model loads."""
        qsdl_file("first-base.qsdl", "base FirstBase { firstValue: String }")
        first_main = qsdl_file(
            "first-main.qsdl",
            'import "first-base.qsdl"\ntype First extends FirstBase { value: String }',
        )
        qsdl_file("second-base.qsdl", "base SecondBase { secondValue: String }")
        second_main = qsdl_file(
            "second-main.qsdl",
            'import "second-base.qsdl"\ntype Second extends SecondBase { value: String }',
        )

        metamodel = xtx.get_metamodel()
        first_schema = metamodel.model_from_file(first_main)
        second_schema = metamodel.model_from_file(second_main)

        assert first_schema.types[0].supertypes[0].name == "FirstBase"
        assert second_schema.types[0].supertypes[0].name == "SecondBase"

    def test_LOG_401_same_basename_imports_positive(self, tmp_path: Path) -> None:
        """LOG-401: Distinct files with the same basename are both merged."""
        first_dir = tmp_path / "first"
        second_dir = tmp_path / "second"
        first_dir.mkdir()
        second_dir.mkdir()
        (first_dir / "common.qsdl").write_text(
            "base FirstCommon @force-generate { firstValue: String }\n",
            encoding="utf-8",
        )
        (second_dir / "common.qsdl").write_text(
            "base SecondCommon @force-generate { secondValue: String }\n",
            encoding="utf-8",
        )
        main_file = tmp_path / "main.qsdl"
        main_file.write_text(
            """
            import "first/common.qsdl"
            import "second/common.qsdl"

            type User extends FirstCommon, SecondCommon {
                name: String
            }
            """,
            encoding="utf-8",
        )

        schema = parse_schema(input_path=main_file)
        bases = {base.name for base in xtx.get_children_of_base(schema)}
        assert {"FirstCommon", "SecondCommon"}.issubset(bases)

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

    def test_LOG_401_invalid_extension_negative(self, qsdl_file: QsdlFileFixture) -> None:
        """LOG-401: Imports must reference .qsdl files."""
        qsdl_file(
            "schema.txt",
            """
            type Imported {
                value: String
            }
        """,
        )
        main_file = qsdl_file(
            "main.qsdl",
            """
            import "schema.txt"

            type User {
                name: String
            }
        """,
        )

        with pytest.raises(TextXSemanticError, match="must use the \\.qsdl extension"):
            parse_schema(input_path=main_file)

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
        with pytest.raises(TextXSemanticError, match="Names for scalars, enums, bases and objects must be unique"):
            parse_schema(input_path=main_file)

    def test_LOG_402_duplicate_type_same_basename_negative(self, tmp_path: Path) -> None:
        """LOG-402: Duplicate types in distinct same-basename files are rejected."""
        first_dir = tmp_path / "first"
        second_dir = tmp_path / "second"
        first_dir.mkdir()
        second_dir.mkdir()
        (first_dir / "common.qsdl").write_text("type Foo { firstValue: String }\n", encoding="utf-8")
        (second_dir / "common.qsdl").write_text("type Foo { secondValue: String }\n", encoding="utf-8")
        main_file = tmp_path / "main.qsdl"
        main_file.write_text(
            'import "first/common.qsdl"\nimport "second/common.qsdl"\n',
            encoding="utf-8",
        )

        with pytest.raises(TextXSemanticError, match="Names for scalars, enums, bases and objects must be unique"):
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
        with pytest.raises(TextXSemanticError, match="Circular import detected: .*a\\.qsdl.*b\\.qsdl.*a\\.qsdl"):
            parse_schema(input_path=main_file)
