from pathlib import Path

from .spring_test_utils import SpringTestUtils


class TestSpringSpecifics:
    """Direct Spring output checks retained from the legacy Spring specifics suite."""

    def test_custom_folder_layout(self) -> None:
        """Configured Spring packages should determine generated source locations."""
        schema = Path("examples/openapi/input.qsdl").read_text(encoding="utf-8")
        config = {
            "base_package": "com.supertest",
            "api_path": "generated.iface",
            "config_path": "shared.config",
            "controller_path": "generated.api",
            "domain_path": "generated.object",
            "enum_path": "generated.constants",
            "exception_path": "shared.exceptions",
            "model_path": "shared.models",
            "repository_path": "generated.repositorys",
            "service_path": "generated.service",
            "util_path": "shared.utils",
        }

        output_path = SpringTestUtils.generate(schema, config=config)

        api_content = SpringTestUtils.read_file(
            output_path, "src/main/java/com/supertest/generated/iface/DefaultApi.java"
        )
        SpringTestUtils.assert_contains(api_content, "package com.supertest.generated.iface;")
        assert SpringTestUtils.file_exists(
            output_path, "src/main/java/com/supertest/generated/api/DefaultController.java"
        )
        assert SpringTestUtils.file_exists(output_path, "src/main/java/com/supertest/generated/object/Project.java")

    def test_controller_directive_sets_controller_name(self) -> None:
        """The Spring controller directive should rename the generated API/controller pair."""
        schema = """\
            extend api @spring-controller("Buzzword") {
                submitQuery(arg: String): Object @path("query") @method(PATCH)
            }

            type Buzzword @namespace("Incident") {
                name: String!
                extend api @generate("CREATE") {}
            }
        """

        output_path = SpringTestUtils.generate(schema)

        controller_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/api/BuzzwordController.java"
        )
        SpringTestUtils.assert_contains(controller_content, "public class BuzzwordController", "submitQuery")
        api_content = SpringTestUtils.read_file(output_path, "src/main/java/app/server/api/BuzzwordApi.java")
        SpringTestUtils.assert_contains(api_content, '@PatchMapping(value = "/query",', "submitQuery")

    def test_string_ids_use_external_uid_in_services(self) -> None:
        """String identifiers should use the external UID lookup in generated services."""
        schema = Path("examples/openapi/input.qsdl").read_text(encoding="utf-8")

        output_path = SpringTestUtils.generate(schema, config={"id_type": "STRING"})

        service_content = SpringTestUtils.read_file(output_path, "src/main/java/app/server/service/ProjectService.java")
        SpringTestUtils.assert_contains(
            service_content,
            "ProjectEntity fetchProjectFromDb(String id)",
            "projectRepository.findByUid(id)",
        )

    def test_no_database_omits_persistence_artifacts(self) -> None:
        """NO database mode should omit JPA repositories and entities."""
        schema = Path("examples/openapi/input.qsdl").read_text(encoding="utf-8")

        output_path = SpringTestUtils.generate(schema, config={"database": "NO"})

        configuration_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/config/AppConfiguration.java"
        )
        SpringTestUtils.assert_not_contains(configuration_content, "@EnableJpaRepositories")
        assert not SpringTestUtils.file_exists(output_path, "src/main/java/app/server/domain/entity/ProjectEntity.java")
        assert not SpringTestUtils.file_exists(
            output_path, "src/main/java/app/server/repository/ProjectRepository.java"
        )

    def test_package_placeholders_use_directives_and_namespace(self) -> None:
        """Package placeholders should use Spring package directives and namespaces."""
        schema = Path("examples/other/package_example.qsdl").read_text(encoding="utf-8")
        config = {
            "api_path": "{package}.api",
            "controller_path": "{package}.api",
            "domain_path": "{package}.dto",
            "entity_path": "{package}.db",
            "mapper_path": "{package}.mapper",
            "repository_path": "{package}.db",
            "service_path": "{package}.service",
            "enum_path": "common.constants",
            "exception_path": "common.exceptions",
            "model_path": "common.models",
            "config_path": "common.config",
            "util_path": "common.util",
        }

        output_path = SpringTestUtils.generate(schema, config=config)

        for relative_path in (
            "src/main/java/app/server/custom/api/DefaultApi.java",
            "src/main/java/app/server/project/dto/Project.java",
            "src/main/java/app/server/user/dto/User.java",
            "src/main/java/app/server/incident/dto/Ticket.java",
            "src/main/java/app/server/project/db/ProjectEntity.java",
        ):
            assert SpringTestUtils.file_exists(output_path, relative_path)

        ticket_content = SpringTestUtils.read_file(output_path, "src/main/java/app/server/incident/dto/Ticket.java")
        SpringTestUtils.assert_contains(ticket_content, "package app.server.incident.dto;")
