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

"""Tests for SEM-5xx rules: Object rules.

Rules covered:
- SEM-501: Object represents a primary domain entity
- SEM-502: Object may extend zero or more Bases
- SEM-503: Object may contain an optional `extend api { ... }` block
- SEM-504: Object may be marked @deprecated
"""

import qsdl.dsl.textx as xtx

from .conftest import ParseFixture


class TestSemObject:
    """Tests for SEM-501 to SEM-504: Object rules."""

    def test_SEM_501_object_domain_entity_positive(self, parse: ParseFixture) -> None:
        """SEM-501: Object represents a primary domain entity."""
        schema = parse("""
            type User {
                name: String
                email: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.name == "User"
        assert len(obj.fields) >= 1

    def test_SEM_502_object_extends_nothing_positive(self, parse: ParseFixture) -> None:
        """SEM-502: Object may extend zero Bases."""
        schema = parse("""
            type Simple {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.supertypes == []

    def test_SEM_502_object_extends_one_positive(self, parse: ParseFixture) -> None:
        """SEM-502: Object may extend one Base."""
        schema = parse("""
            base Auditable {
                createdAt: Datetime
            }
            type User extends Auditable {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert len(obj.supertypes) == 1
        assert obj.supertypes[0].name == "Auditable"

    def test_SEM_502_object_extends_multiple_positive(self, parse: ParseFixture) -> None:
        """SEM-502: Object may extend multiple Bases."""
        schema = parse("""
            base Auditable {
                createdAt: Datetime
            }
            base Identifiable {
                uuid: String
            }
            type User extends Auditable, Identifiable {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert len(obj.supertypes) == 2
        supertype_names = [s.name for s in obj.supertypes]
        assert "Auditable" in supertype_names
        assert "Identifiable" in supertype_names

    def test_SEM_502_object_inherits_fields_positive(self, parse: ParseFixture) -> None:
        """SEM-502: Object inherits fields from Base."""
        schema = parse("""
            base Auditable {
                createdAt: Datetime
                updatedAt: Datetime
            }
            type User extends Auditable {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field_names = [f.name for f in obj.fields]
        assert "createdAt" in field_names
        assert "updatedAt" in field_names
        assert "name" in field_names

    def test_SEM_503_object_with_api_positive(self, parse: ParseFixture) -> None:
        """SEM-503: Object may contain an optional extend api block."""
        schema = parse("""
            type User {
                name: String

                extend api {
                    getByEmail(email: String): User @path("users/by-email")
                }
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.api is not None
        assert len(obj.api.operations) == 1

    def test_SEM_503_object_without_api_positive(self, parse: ParseFixture) -> None:
        """SEM-503: Object without explicit api block gets auto-generated api."""
        schema = parse("""
            type User {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.api is not None
        assert obj.api.has_generated is True

    def test_SEM_504_object_deprecated_positive(self, parse: ParseFixture) -> None:
        """SEM-504: Object may be marked @deprecated."""
        schema = parse("""
            type LegacyUser @deprecated {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.is_deprecated is True

    def test_SEM_504_object_not_deprecated_positive(self, parse: ParseFixture) -> None:
        """SEM-504: Object without @deprecated is not deprecated."""
        schema = parse("""
            type User {
                name: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        assert obj.is_deprecated is False
