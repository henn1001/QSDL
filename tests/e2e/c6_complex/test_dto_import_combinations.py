from pathlib import Path

import pytest

from tests.e2e import assert_mvn
from tests.e2e.base_e2e_test import BaseE2ETest


class TestE2EDtoImportCombinations(BaseE2ETest):
    """Compile DTOs for mixed nested Base/Object and opaque-field combinations."""

    CONFIG = {
        "api_path": "app.server.{package}.api",
        "controller_path": "app.server.{package}.api",
        "domain_path": "app.server.{package}.domain",
        "entity_path": "app.server.{package}.domain.entity",
        "mapper_path": "app.server.{package}.domain.mapper",
        "repository_path": "app.server.{package}.repository",
        "service_path": "app.server.{package}.service",
        "package_placeholder_fallback": "common",
    }

    TESTCASE = """\
      base PlainLeaf @namespace("Shared") {
        content: String
      }

      base SplitLeaf @namespace("Shared") {
        content: String
        created_at: Date @readOnly
      }

      base WriteOnlyLeaf @namespace("Shared") {
        content: String
        secret: String @writeOnly
      }

      base PlainContainer @namespace("Shared") {
        plain: PlainLeaf
        opaque: PlainLeaf @opaque
        values: [PlainLeaf]
        opaque_values: [PlainLeaf] @opaque
      }

      base SplitContainer @namespace("Shared") {
        plain: PlainLeaf
        split: SplitLeaf
        splits: [SplitLeaf]
        write_only: WriteOnlyLeaf
        opaque_split: SplitLeaf @opaque
        opaque_splits: [SplitLeaf] @opaque
      }

      type NestedObject @namespace("Nested") {
        content: String
      }

      base ObjectContainer @namespace("Shared") {
        nested: NestedObject
        nested_list: [NestedObject]
        opaque: PlainLeaf @opaque
      }

      base RequestOnly @namespace("Shared") {
        content: String
        secret: String @writeOnly
      }

      base ResponseOnly @namespace("Shared") {
        content: String
        generated_at: Date @readOnly
      }

      type Gateway @namespace("Gateway") {
        plain: PlainLeaf
        plain_list: [PlainLeaf]
        opaque_plain: PlainLeaf @opaque
        opaque_plain_list: [PlainLeaf] @opaque
        plain_container: PlainContainer
        opaque_split: SplitLeaf @opaque
        nested: NestedObject
        nested_list: [NestedObject]
      }

      extend api @namespace("External") {
        submit(data: RequestOnly): Void @path("submit") @method(POST)
        submit_split(data: SplitContainer): SplitContainer @path("submit-split") @method(POST)
        submit_objects(data: ObjectContainer): ObjectContainer @path("submit-objects") @method(POST)
        fetch(): ResponseOnly @path("fetch") @method(GET)
      }
    """

    def test_generated_request_types_and_imports(self, srcgen: Path) -> None:
        """Request DTOs must reference the variant that is actually generated."""
        domain_root = srcgen / "src" / "main" / "java" / "app" / "server"
        shared = domain_root / "shared" / "domain"
        gateway = domain_root / "gateway" / "domain"
        nested = domain_root / "nested" / "domain"

        for type_name in ("PlainLeaf", "PlainContainer"):
            assert (shared / f"{type_name}.java").is_file()
            assert not (shared / f"{type_name}Request.java").exists()

        for type_name in ("SplitLeaf", "SplitContainer", "ObjectContainer", "WriteOnlyLeaf"):
            assert (shared / f"{type_name}.java").is_file()
            assert (shared / f"{type_name}Request.java").is_file()

        assert (nested / "NestedObject.java").is_file()
        assert (nested / "NestedObjectRequest.java").is_file()
        assert (shared / "RequestOnlyRequest.java").is_file()
        assert not (shared / "RequestOnly.java").exists()
        assert (shared / "ResponseOnly.java").is_file()
        assert not (shared / "ResponseOnlyRequest.java").exists()

        gateway_request = (gateway / "GatewayRequest.java").read_text(encoding="utf-8")
        assert "import app.server.shared.domain.PlainLeaf;" in gateway_request
        assert "import app.server.shared.domain.PlainContainer;" in gateway_request
        assert "import app.server.shared.domain.SplitLeafRequest;" in gateway_request
        assert "import app.server.nested.domain.NestedObjectRequest;" in gateway_request
        assert "import app.server.shared.domain.PlainLeafRequest;" not in gateway_request
        assert "PlainLeaf plain" in gateway_request
        assert "List<PlainLeaf> plainList" in gateway_request
        assert "PlainContainer plainContainer" in gateway_request
        assert "SplitLeafRequest opaqueSplit" in gateway_request
        assert "NestedObjectRequest nested" in gateway_request
        assert "List<NestedObjectRequest> nestedList" in gateway_request

        split_request = (shared / "SplitContainerRequest.java").read_text(encoding="utf-8")
        assert "PlainLeaf plain" in split_request
        assert "SplitLeafRequest split" in split_request
        assert "List<SplitLeafRequest> splits" in split_request
        assert "WriteOnlyLeafRequest writeOnly" in split_request
        assert "SplitLeafRequest opaqueSplit" in split_request
        assert "List<SplitLeafRequest> opaqueSplits" in split_request

        object_request = (shared / "ObjectContainerRequest.java").read_text(encoding="utf-8")
        assert "import app.server.nested.domain.NestedObjectRequest;" in object_request
        assert "NestedObjectRequest nested" in object_request
        assert "List<NestedObjectRequest> nestedList" in object_request

    def test_opaque_mapper_types_and_cross_namespace_imports(self, srcgen: Path) -> None:
        """Opaque mappers must use existing request DTOs and import their real packages."""
        mapper = (
            srcgen / "src" / "main" / "java" / "app" / "server" / "gateway" / "domain" / "mapper" / "GatewayMapper.java"
        ).read_text(encoding="utf-8")

        assert "import app.server.shared.domain.PlainLeaf;" in mapper
        assert "import app.server.shared.domain.PlainLeafRequest;" not in mapper
        assert "import app.server.shared.domain.SplitLeaf;" in mapper
        assert "import app.server.shared.domain.SplitLeafRequest;" in mapper
        assert "import app.server.nested.domain.mapper.NestedObjectMapper;" in mapper
        assert mapper.count("PlainLeaf toPlainLeaf(PlainLeaf request);") == 1
        assert "SplitLeaf toSplitLeaf(SplitLeafRequest request);" in mapper
        assert '@Mapping(target = "createdAt", ignore = true)' in mapper

    def test_custom_operations_use_only_generated_variants(self, srcgen: Path) -> None:
        """Direct Base operation parameters must resolve request-only/response-only DTOs."""
        api = (srcgen / "src" / "main" / "java" / "app" / "server" / "external" / "api" / "DefaultApi.java").read_text(
            encoding="utf-8"
        )

        assert "import app.server.shared.domain.RequestOnlyRequest;" in api
        assert "import app.server.shared.domain.ResponseOnly;" in api
        assert "import app.server.shared.domain.SplitContainer;" in api
        assert "import app.server.shared.domain.SplitContainerRequest;" in api
        assert "import app.server.shared.domain.ObjectContainer;" in api
        assert "import app.server.shared.domain.ObjectContainerRequest;" in api
        assert "RequestOnlyRequest data" in api
        assert "SplitContainerRequest data" in api
        assert "ResponseEntity<SplitContainer> submit_split" in api
        assert "ObjectContainerRequest data" in api
        assert "ResponseEntity<ObjectContainer> submit_objects" in api
        assert "ResponseEntity<ResponseOnly> fetch" in api

    @pytest.mark.integration
    def test_integration(self, srcgen: Path) -> None:
        """Maven must compile all generated source for this mixed DTO graph."""
        assert_mvn()
