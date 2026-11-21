from .spring_test_utils import SpringTestUtils


class TestSpringSpecifics:
    """Direct Spring output checks for configured and default layouts."""

    PROJECT_SCHEMA = """
        type Project { name: String! }
    """

    def test_custom_folder_layout(self) -> None:
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
        files = SpringTestUtils.generate(self.PROJECT_SCHEMA, config=config)
        api_content = SpringTestUtils.read_file(files, "src/main/java/com/supertest/generated/iface/ProjectApi.java")
        SpringTestUtils.assert_contains(api_content, "package com.supertest.generated.iface;")
        assert SpringTestUtils.file_exists(files, "src/main/java/com/supertest/generated/api/ProjectController.java")
        assert SpringTestUtils.file_exists(files, "src/main/java/com/supertest/generated/object/Project.java")

    def test_controller_directive_sets_controller_name(self) -> None:
        schema = """
            extend api @spring-controller("Buzzword") {
                submitQuery(arg: String): Object @path("query") @method(PATCH)
            }
            type Buzzword @namespace("incident") { name: String! }
        """
        files = SpringTestUtils.generate(schema)
        controller_content = SpringTestUtils.read_file(
            files, "src/main/java/app/api/incident/web/BuzzwordController.java"
        )
        SpringTestUtils.assert_contains(controller_content, "public class BuzzwordController", "submitQuery")
        api_content = SpringTestUtils.read_file(files, "src/main/java/app/api/incident/web/BuzzwordApi.java")
        SpringTestUtils.assert_contains(api_content, '@PatchMapping(value = "/query",', "submitQuery")

    def test_string_ids_use_external_uid_in_services(self) -> None:
        files = SpringTestUtils.generate(self.PROJECT_SCHEMA, config={"id_type": "STRING"})
        service_content = SpringTestUtils.read_file(files, "src/main/java/app/api/general/ProjectService.java")
        SpringTestUtils.assert_contains(
            service_content, "ProjectEntity fetchProjectFromDb(String id)", "projectRepository.findByUid(id)"
        )

    def test_no_database_omits_persistence_artifacts(self) -> None:
        files = SpringTestUtils.generate(self.PROJECT_SCHEMA, config={"database": "NO"})
        configuration_content = SpringTestUtils.read_file(
            files, "src/main/java/app/shared/config/AppConfiguration.java"
        )
        SpringTestUtils.assert_not_contains(configuration_content, "@EnableJpaRepositories")
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/api/general/persistence/ProjectEntity.java")
        assert not SpringTestUtils.file_exists(
            files, "src/main/java/app/api/general/persistence/ProjectRepository.java"
        )

    def test_package_placeholders_use_directives_and_namespace(self) -> None:
        schema = """
            type Project @namespace("project") { name: String! }
            type User @namespace("user") { name: String! }
            type Ticket @namespace("incident") { name: String! }
        """
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
        files = SpringTestUtils.generate(schema, config=config)
        for relative_path in (
            "src/main/java/app/project/dto/Project.java",
            "src/main/java/app/user/dto/User.java",
            "src/main/java/app/incident/dto/Ticket.java",
            "src/main/java/app/project/db/ProjectEntity.java",
        ):
            assert SpringTestUtils.file_exists(files, relative_path)
        ticket_content = SpringTestUtils.read_file(files, "src/main/java/app/incident/dto/Ticket.java")
        SpringTestUtils.assert_contains(ticket_content, "package app.incident.dto;")
