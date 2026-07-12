from pathlib import Path

import pytest

from tests.e2e import assert_mvn
from tests.e2e.base_e2e_test import BaseE2ETest


class TestE2EOperationPayload(BaseE2ETest):
    """Test E2E for request-body DTO generation for custom write operations.

    Covers the rule:
    - A write operation (POST/PUT/PATCH) whose body parameters are inline scalars
      (not a single Base/Object reference) generates a named ``{OperationId}Request`` DTO.
    - A write operation that already receives a single Base/Object body reference
      uses that type directly (no extra wrapper DTO).
    """

    TESTCASE = """\
      base Project {
        name: String!
        field: Int
      }

      extend api {
        createProjectA(name: String!, field: Int): Project
          @path("/projects/create-a")
          @method(POST)

        createProjectB(body: Project): Project
          @path("/projects/create-b")
          @method(POST)
      }
    """

    def test_openapi(self, openapi_schema: dict) -> None:
        """OpenAPI spec inlines CreateProjectARequest schema with title in requestBody."""
        schemas = openapi_schema.get("components", {}).get("schemas", {})

        # createProjectA → inline scalar → no component schema created
        assert "CreateProjectARequest" not in schemas, "Request DTO must be inline, not a component schema"

        # requestBody for createProjectA is inline with title
        post_a = openapi_schema["paths"]["/projects/create-a"]["post"]
        schema_a = post_a["requestBody"]["content"]["application/json"]["schema"]
        assert schema_a["title"] == "CreateProjectARequest"
        assert schema_a["type"] == "object"
        assert "name" in schema_a["required"]
        assert schema_a["properties"]["name"]["type"] == "string"
        assert schema_a["properties"]["name"]["maxLength"] == 255

        # createProjectB uses Project directly — no CreateProjectBRequest schema
        assert "CreateProjectBRequest" not in schemas

        # requestBody for createProjectB REFERENCES the Project schema directly
        post_b = openapi_schema["paths"]["/projects/create-b"]["post"]
        schema_b = post_b["requestBody"]["content"]["application/json"]["schema"]
        assert schema_b["$ref"] == "#/components/schemas/Project"

    def test_spring(self, srcgen: Path) -> None:
        """Spring generator creates CreateProjectARequest.java and uses it in the controller."""
        src_root = srcgen / "src" / "main" / "java"
        assert src_root.exists()

        # createProjectA → CreateProjectARequest.java must be generated
        dto_files = list(src_root.rglob("CreateProjectARequest.java"))
        assert len(dto_files) == 1, "Expected exactly one CreateProjectARequest.java"
        dto_content = dto_files[0].read_text(encoding="utf-8")
        assert "record CreateProjectARequest" in dto_content
        assert 'JsonProperty(value = "name")' in dto_content
        assert "String name" in dto_content

        # createProjectB → no CreateProjectBRequest should be generated
        wrapper_files = list(src_root.rglob("CreateProjectBRequest.java"))
        assert len(wrapper_files) == 0, "createProjectB must NOT generate a wrapper DTO"

        # DefaultApi / DefaultController must reference CreateProjectARequest in signature
        api_files = list(src_root.rglob("DefaultApi.java"))
        assert len(api_files) == 1
        api_content = api_files[0].read_text(encoding="utf-8")
        assert "CreateProjectARequest request" in api_content

        controller_files = list(src_root.rglob("DefaultController.java"))
        assert len(controller_files) == 1
        controller_content = controller_files[0].read_text(encoding="utf-8")
        assert "CreateProjectARequest request" in controller_content

        # createProjectB should use Project directly (no wrapper)
        assert "Project body" in controller_content

    @pytest.mark.integration
    def test_integration(self, srcgen: Path) -> None:
        """runs mvn clean test to verify generated code compiles and tests pass"""
        assert_mvn()
