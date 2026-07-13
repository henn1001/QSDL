from pathlib import Path

import pytest

from tests.e2e import assert_mvn
from tests.e2e.base_e2e_test import BaseE2ETest


class TestE2EQueryFilterObject(BaseE2ETest):
    """Test E2E for query filter object generation."""

    TESTCASE = """\
      base AnotherFilter {
        name: String! @query
      }

      type Project {
        name: String! @queryList
        archived: Boolean @query
        some_query: Int @query
        tags: [String] @queryList
      }

      extend api {
        searchProjects(name: String, archived: Boolean, tags: [String]): [Project]
          @path("/projects/search")
          @method(GET)
          @pagination

        searchOneProject(filter: AnotherFilter!): Project
          @path("/projects/searchV2")
          @method(GET)
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
        assert filter_properties["some_query"]["type"] == "integer"

        assert filter_properties["tags"]["type"] == "array"
        assert filter_properties["tags"]["items"]["type"] == "string"

        # custom operation with Base query parameter should use that schema directly
        search_get = openapi_schema["paths"]["/projects/searchv2"]["get"]
        search_parameters = search_get["parameters"]
        assert search_parameters[0]["name"] == "filter"
        assert search_parameters[0]["schema"]["$ref"] == "#/components/schemas/AnotherFilter"

    def test_spring(self, srcgen: Path) -> None:
        """Asserts Spring query filters preserve Java property names for Querydsl."""
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
        # @query fields use the canonical Java property name internally, while
        # the public query parameter remains snake_case through @JsonProperty.
        assert "Integer someQuery" in crud_contents
        assert 'JsonProperty(value = "some_query")' in crud_contents
        assert "import app.server.util.PredicateBuilder.QueryFilter;" in crud_contents
        assert ") implements QueryFilter" in crud_contents
        assert 'queryParameters.put("someQuery", List.of(String.valueOf(someQuery)));' in crud_contents
        assert 'queryParameters.put("some_query"' not in crud_contents

        # tags field with @queryList should be List<String> and retain all values.
        assert "List<String> tags" in crud_contents
        assert 'queryParameters.put("tags", tags.stream().map(String::valueOf).toList());' in crud_contents

        predicate_builder_files = list(src_root.rglob("PredicateBuilder.java"))
        assert len(predicate_builder_files) == 1
        predicate_builder_contents = predicate_builder_files[0].read_text(encoding="utf-8")
        assert "public interface QueryFilter" in predicate_builder_contents
        assert "Map<String, List<String>> toQueryParameters();" in predicate_builder_contents
        assert "build(QueryFilter filter, Class<T> domainClass)" in predicate_builder_contents
        assert "JsonUtil.mapper()" not in predicate_builder_contents

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

        # Operation with single Base query parameter should use base directly
        search_filter_files = list(src_root.rglob("SearchOneProjectFilter.java"))
        assert len(search_filter_files) == 0

        controller_files = list(src_root.rglob("DefaultController.java"))
        assert len(controller_files) == 1
        controller_contents = controller_files[0].read_text(encoding="utf-8")
        assert "searchOneProject(AnotherFilter filter" in controller_contents
        assert "SearchOneProjectFilter" not in controller_contents

    @pytest.mark.integration
    def test_integration(self, srcgen: Path) -> None:
        """runs mvn clean test to verify generated code compiles and tests pass"""
        assert_mvn()
