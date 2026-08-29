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

"""Tests for SEM-7xx rules: Relationship rules.

Rules covered:
- SEM-701: @composition marks a parent-child relationship (required array)
- SEM-702: @aggregation marks an independent relationship (required array)
- SEM-703: A Field cannot be both @composition and @aggregation
- SEM-704: Composition/aggregation fields must reference Objects
- SEM-705: Self-referential fields are rejected
- SEM-706: Relationship directives are declared only on Object fields
- SEM-707: Relation target/kind pairs are unique per Object
"""

import re

import pytest
from textx.exceptions import TextXSemanticError

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


def assert_semantic_error(parse: ParseFixture, raw: str, message: str) -> None:
    """Assert a specific validator error without masking unrelated failures."""
    with pytest.raises(TextXSemanticError, match=re.escape(message)):
        parse(raw)


class TestSemRelationship:
    """Tests for SEM-701 to SEM-707: Relationship rules."""

    def test_SEM_701_composition_positive(self, parse: ParseFixture) -> None:
        """SEM-701: @composition marks parent-child relationship."""
        schema = parse("""
            type Child {
                value: String
            }
            type Parent {
                name: String
                children: [Child]! @composition
            }
        """)
        objects = xtx.get_children_of_object(schema)
        parent = next(o for o in objects if o.name == "Parent")
        children_field = next(f for f in parent.fields if f.name == "children")
        assert children_field.is_composition is True
        assert children_field.is_array is True
        assert children_field.is_required is True

    def test_SEM_701_composition_non_array_negative(self, parse_expect_semantic_error: ParseExpectErrorFixture) -> None:
        """SEM-701: @composition on non-array is rejected."""
        parse_expect_semantic_error("""
            type Child {
                value: String
            }
            type Parent {
                name: String
                child: Child @composition
            }
        """)

    def test_SEM_701_composition_optional_array_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-701: @composition on an optional array is rejected."""
        parse_expect_semantic_error("""
            type Child {
                value: String
            }
            type Parent {
                name: String
                children: [Child] @composition
            }
        """)

    def test_SEM_702_aggregation_positive(self, parse: ParseFixture) -> None:
        """SEM-702: @aggregation marks independent relationship."""
        schema = parse("""
            type Tag {
                name: String
            }
            type Article {
                title: String
                tags: [Tag]! @aggregation
            }
        """)
        objects = xtx.get_children_of_object(schema)
        article = next(o for o in objects if o.name == "Article")
        tags_field = next(f for f in article.fields if f.name == "tags")
        assert tags_field.is_aggregation is True
        assert tags_field.is_array is True
        assert tags_field.is_required is True

    def test_SEM_702_aggregation_non_array_negative(self, parse_expect_semantic_error: ParseExpectErrorFixture) -> None:
        """SEM-702: @aggregation on non-array is rejected."""
        parse_expect_semantic_error("""
            type Tag {
                name: String
            }
            type Article {
                title: String
                tag: Tag @aggregation
            }
        """)

    def test_SEM_702_aggregation_optional_array_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-702: @aggregation on an optional array is rejected."""
        parse_expect_semantic_error("""
            type Tag {
                name: String
            }
            type Article {
                title: String
                tags: [Tag] @aggregation
            }
        """)

    def test_SEM_703_composition_aggregation_conflict_negative(
        self, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """SEM-703: Field cannot be both @composition and @aggregation."""
        parse_expect_semantic_error("""
            type Child {
                value: String

                extend api { }
            }
            type Parent {
                name: String
                children: [Child]! @composition @aggregation
            }
        """)

    def test_SEM_704_composition_targets_object_positive(self, parse: ParseFixture) -> None:
        """SEM-704: Composition field references Object."""
        schema = parse("""
            type Child {
                value: String
            }
            type Parent {
                name: String
                children: [Child]! @composition
            }
        """)
        objects = xtx.get_children_of_object(schema)
        parent = next(o for o in objects if o.name == "Parent")
        children_field = next(f for f in parent.fields if f.name == "children")
        child_type = children_field.value
        assert child_type.name == "Child"

    def test_SEM_704_composition_on_scalar_negative(self, parse_expect_semantic_error: ParseExpectErrorFixture) -> None:
        """SEM-704: Composition on Scalar field is rejected."""
        parse_expect_semantic_error("""
            type Parent {
                name: String
                values: [String] @composition
            }
        """)

    def test_SEM_704_aggregation_on_scalar_negative(self, parse_expect_semantic_error: ParseExpectErrorFixture) -> None:
        """SEM-704: Aggregation on Scalar field is rejected."""
        parse_expect_semantic_error("""
            type Parent {
                name: String
                values: [String] @aggregation
            }
        """)

    @pytest.mark.parametrize(
        "declaration",
        [
            """
                type Node {
                    parent: Node
                }
            """,
            """
                base Node {
                    parent: Node
                }
            """,
        ],
    )
    def test_SEM_705_self_reference_negative(self, declaration: str, parse: ParseFixture) -> None:
        """SEM-705: An Object or Base cannot reference itself."""
        assert_semantic_error(parse, declaration, "The Field parent for Node references itself.")

    def test_SEM_705_non_self_reference_positive(self, parse: ParseFixture) -> None:
        """SEM-705: A field may reference a different Object."""
        schema = parse("""
            type Child {
                value: String
            }
            type Parent {
                child: Child
            }
        """)
        parent = next(entity for entity in xtx.get_children_of_object(schema) if entity.name == "Parent")
        assert next(field for field in parent.fields if field.name == "child").value.name == "Child"

    def test_SEM_706_relationship_in_base_negative(self, parse: ParseFixture) -> None:
        """SEM-706: Relationship directives are not allowed in Bases."""
        assert_semantic_error(
            parse,
            """
                type Child {
                    value: String
                }
                base Parent {
                    children: [Child]! @composition
                }
            """,
            "The Field children for Parent declares a relation inside a Base.",
        )

    def test_SEM_706_relationship_in_object_positive(self, parse: ParseFixture) -> None:
        """SEM-706: Relationship directives are valid on Object fields."""
        schema = parse("""
            type Child {
                value: String
            }
            type Parent {
                children: [Child]! @composition
            }
        """)
        parent = next(entity for entity in xtx.get_children_of_object(schema) if entity.name == "Parent")
        assert next(field for field in parent.fields if field.name == "children").is_composition is True

    @pytest.mark.parametrize("relation", ["composition", "aggregation"])
    def test_SEM_707_duplicate_relation_negative(self, relation: str, parse: ParseFixture) -> None:
        """SEM-707: An Object cannot repeat a target and relationship kind."""
        assert_semantic_error(
            parse,
            f"""
                type Child {{
                    value: String
                }}
                type Parent {{
                    firstChildren: [Child]! @{relation}
                    secondChildren: [Child]! @{relation}
                }}
            """,
            "The Field secondChildren for Parent creates a duplicate relation.",
        )

    def test_SEM_707_different_relation_target_positive(self, parse: ParseFixture) -> None:
        """SEM-707: The same relationship kind may target different Objects."""
        schema = parse("""
            type Project {
                name: String
            }
            type Task {
                name: String
            }
            type User {
                projects: [Project]! @composition
                tasks: [Task]! @composition
            }
        """)
        user = next(entity for entity in xtx.get_children_of_object(schema) if entity.name == "User")
        assert {field.name for field in user.fields if field.name in {"projects", "tasks"}} == {"projects", "tasks"}
