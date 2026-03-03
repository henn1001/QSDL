from pathlib import Path

import pytest

from tests.e2e import assert_mvn
from tests.e2e.base_e2e_test import BaseE2ETest


class TestE2EQueryFilterObject(BaseE2ETest):
    """Test E2E for query filter object generation."""

    TESTCASE = """\
      type Project {
        name: String! @queryList
        archived: Boolean @query
        tags: [String] @queryList
      }

      extend api {
        searchProjects(name: String, archived: Boolean, tags: [String]): [Project]
          @path("/projects/search")
          @method(GET)
          @pagination
      }
    """

    def test_openapi(self, openapi_schema: dict) -> None:
        """asserts generated OpenAPI spec contains filter schema + parameter"""

        get = openapi_schema["paths"]["/projects/search"]["get"]
        parameters = get["parameters"]

        # explicit query params from the operation signature
        assert parameters[0]["name"] == "name"
        assert parameters[1]["name"] == "archived"
        assert parameters[2]["name"] == "tags"

        # pagination params from @pagination
        assert parameters[3]["$ref"] == "#/components/parameters/cursor"
        assert parameters[4]["$ref"] == "#/components/parameters/limit"
        assert parameters[5]["$ref"] == "#/components/parameters/count"

        # openapi generator does not expose the filter DTO as a component schema;
        # it keeps explicit query parameters instead.

        # CRUD GET /projects uses the filter object when @query/@queryList is present on fields
        projects_get = openapi_schema["paths"]["/projects"]["get"]
        project_parameters = projects_get["parameters"]
        assert project_parameters[0]["name"] == "filter"
        filter_properties = project_parameters[0]["schema"]["properties"]

        assert filter_properties["name"]["type"] == "array"
        assert filter_properties["name"]["items"]["type"] == "string"

        assert filter_properties["archived"]["type"] == "boolean"

        assert filter_properties["tags"]["type"] == "array"
        assert filter_properties["tags"]["items"]["type"] == "string"

    def test_spring(self, srcgen: Path) -> None:
        """asserts Spring filter DTOs are generated with @queryList as List<T>"""
        src_root = srcgen / "src" / "main" / "java"
        assert src_root.exists()

        # Check CRUD filter
        crud_filter_files = list(src_root.rglob("GetProjectsFilter.java"))
        assert len(crud_filter_files) == 1
        crud_contents = crud_filter_files[0].read_text(encoding="utf-8")
        assert "record GetProjectsFilter" in crud_contents
        # @queryList fields should be List<T>
        assert "List<String> name" in crud_contents
        # @query fields should remain scalar
        assert "Boolean archived" in crud_contents
        # tags field with @queryList should be List<String>
        assert "List<String> tags" in crud_contents

        # Check custom operation filter
        filter_files = list(src_root.rglob("SearchProjectsFilter.java"))
        assert len(filter_files) == 1
        contents = filter_files[0].read_text(encoding="utf-8")
        assert "record SearchProjectsFilter" in contents
        assert 'JsonProperty(value = "name")' in contents
        assert 'JsonProperty(value = "archived")' in contents
        assert 'JsonProperty(value = "tags")' in contents
        # Verify custom operation parameters match their declaration
        assert "String name" in contents  # explicit String parameter
        assert "Boolean archived" in contents  # explicit Boolean parameter
        assert "List<String> tags" in contents  # explicit [String] parameter

    @pytest.mark.integration
    def test_integration(self, srcgen: Path) -> None:
        """runs mvn clean test to verify generated code compiles and tests pass"""
        assert_mvn()
