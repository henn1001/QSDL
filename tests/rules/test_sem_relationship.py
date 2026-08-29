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
"""

import qsdl.dsl.textx as xtx

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestSemRelationship:
    """Tests for SEM-701 to SEM-704: Relationship rules."""

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
