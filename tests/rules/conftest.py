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

"""Shared fixtures for rule-based tests."""

import textwrap
from collections.abc import Callable
from pathlib import Path

import pytest
from textx.exceptions import TextXSemanticError, TextXSyntaxError

from qsdl.dsl import Schema
from qsdl.dsl.textx import parse_schema

ParseFixture = Callable[[str], Schema]
ParseExpectErrorFixture = Callable[[str], None]
QsdlFileFixture = Callable[[str, str], Path]


@pytest.fixture
def parse() -> ParseFixture:
    """Parse QSDL schema string and return the schema object.

    Usage:
        def test_example(parse):
            schema = parse('''
                type Foo {
                    name: String
                }
            ''')
            assert len(schema.types) == 1
    """

    def _parse(raw: str) -> Schema:
        return parse_schema(raw_schema=textwrap.dedent(raw))

    return _parse


@pytest.fixture
def parse_expect_syntax_error() -> ParseExpectErrorFixture:
    """Expect parsing to fail with a TextX syntax/grammar error.

    Use for grammar-only syntax errors.

    Usage:
        def test_example(parse_expect_syntax_error):
            parse_expect_syntax_error('type lowercase { field: String }')
    """

    def _parse(raw: str) -> None:
        with pytest.raises(TextXSyntaxError):
            parse_schema(raw_schema=textwrap.dedent(raw))

    return _parse


@pytest.fixture
def parse_expect_name_error() -> ParseExpectErrorFixture:
    """Expect a naming check to fail after model construction.

    Identifier-shaped tokens are accepted by the grammar so naming violations
    can normally be reported semantically. Lexically malformed names may still
    produce a TextX syntax error.
    """

    def _parse(raw: str) -> None:
        with pytest.raises((TextXSemanticError, TextXSyntaxError)):
            parse_schema(raw_schema=textwrap.dedent(raw))

    return _parse


@pytest.fixture
def parse_expect_semantic_error() -> ParseExpectErrorFixture:
    """Expect parsing to fail with a semantic or validation error.

    Use for SEM-* and LOG-* rules enforced by processors/validators.

    Usage:
        def test_example(parse_expect_semantic_error):
            parse_expect_semantic_error('''
                type Foo {
                    field: String @readOnly @writeOnly
                }
            ''')
    """

    def _parse(raw: str) -> None:
        with pytest.raises((TextXSemanticError, Exception)):
            parse_schema(raw_schema=textwrap.dedent(raw))

    return _parse


@pytest.fixture
def qsdl_file(tmp_path: Path) -> QsdlFileFixture:
    """Create a temporary .qsdl file for import tests.

    Usage:
        def test_import(qsdl_file, parse):
            base_file = qsdl_file('base.qsdl', '''
                base Auditable {
                    createdAt: Datetime
                }
            ''')
            # Use parse_schema with input_path for import support
    """

    def _create(name: str, content: str) -> Path:
        path = tmp_path / name
        path.write_text(textwrap.dedent(content), encoding="utf-8")
        return path

    return _create
