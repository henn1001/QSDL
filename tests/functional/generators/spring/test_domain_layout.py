from .spring_test_utils import SpringTestUtils


class TestSpringDomainLayout:
    """Test spring generator with domain layout configuration"""

    def test_cross_namespace_operation_imports(self) -> None:
        """When using domain layout, operations returning types from different namespaces should have correct imports"""
        # Given: An operation in "User" namespace that returns a type from "Project" namespace
        test_input = """\
            type Project @namespace("Project")  {
                name: String
            }

            extend api @namespace("User")  {
                getProjectFromUser(name: String): Project @path("user")
            }
        """

        # When: Generate with domain layout config
        output_path = SpringTestUtils.generate(test_input, "util/domain_config.json")

        # Then: Verify the Controller imports Project from the correct package
        controller_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/common/api/DefaultController.java"
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.server.project.dto.Project;",  # Should import Project from project package
            "public ResponseEntity<Project> getProjectFromUser",  # Uses Project as return type
        )

        # Should NOT have wildcard import to common.dto (which doesn't exist in domain layout)
        # or if it does exist, Project should not rely on it
        assert "import app.server.project.dto.Project;" in controller_content

        # Then: Verify the Api interface also has correct imports
        api_content = SpringTestUtils.read_file(output_path, "src/main/java/app/server/common/api/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.server.project.dto.Project;",  # Should import Project from project package
            "ResponseEntity<Project> getProjectFromUser",  # Uses Project as return type
        )

        # Then: Verify the Service has correct imports (Project is generated with CRUD)
        service_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/project/service/ProjectService.java"
        )
        SpringTestUtils.assert_contains(
            service_content,
            "import app.server.project.dto.Project;",
            "import app.server.project.dto.ProjectRequest;",
            "import app.server.project.db.ProjectEntity;",
            "import app.server.project.db.QProjectEntity;",
            "import app.server.project.db.ProjectRepository;",
            "import app.server.project.mapper.ProjectMapper;",
        )
        SpringTestUtils.assert_not_contains(
            service_content,
            ".*;",  # No wildcard imports in Service
        )

    def test_cross_namespace_operation_with_body_parameter(self) -> None:
        """Operations with body parameters from different namespaces should have correct imports"""
        # Given: An operation that takes a parameter from another namespace
        test_input = """\
            type Project @namespace("Project")  {
                name: String!
            }

            extend api @namespace("User")  {
                addProject(project: Project): Project @method(POST) @path("user/projects")
            }
        """

        # When: Generate with domain layout config
        output_path = SpringTestUtils.generate(test_input, "util/domain_config.json")

        # Then: Verify imports for both parameter and return type
        controller_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/common/api/DefaultController.java"
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.server.project.dto.Project;",  # Import for return type
            "import app.server.project.dto.ProjectRequest;",  # Import for body parameter
        )

        api_content = SpringTestUtils.read_file(output_path, "src/main/java/app/server/common/api/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.server.project.dto.Project;",
            "import app.server.project.dto.ProjectRequest;",
        )

        # Then: Verify Service has no wildcard imports
        service_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/project/service/ProjectService.java"
        )
        SpringTestUtils.assert_contains(
            service_content,
            "import app.server.project.dto.Project;",
            "import app.server.project.dto.ProjectRequest;",
        )
        SpringTestUtils.assert_not_contains(service_content, ".*;")  # No wildcard imports

    def test_multiple_cross_namespace_types(self) -> None:
        """Operations using multiple types from different namespaces should have all correct imports"""
        # Given: Operations using types from multiple namespaces
        test_input = """\
            type Project @namespace("Project")  {
                name: String!
            }

            type User @namespace("User")  {
                username: String!
            }

            extend api @namespace("Admin")  {
                findProject(): Project @path("admin/find-project")
                findUser(): User @path("admin/find-user")
            }
        """

        # When: Generate with domain layout config
        output_path = SpringTestUtils.generate(test_input, "util/domain_config.json")

        # Then: Verify all cross-namespace imports are present
        controller_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/common/api/DefaultController.java"
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.server.project.dto.Project;",
            "import app.server.user.dto.User;",
        )

        api_content = SpringTestUtils.read_file(output_path, "src/main/java/app/server/common/api/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.server.project.dto.Project;",
            "import app.server.user.dto.User;",
        )

    def test_no_wildcard_imports_in_api(self) -> None:
        """Api files should not contain wildcard imports"""
        # Given: An operation with same-namespace types (using base to avoid CRUD conflicts)
        test_input = """\
            base ProjectBase @namespace("Project")  {
                name: String!
            }

            type Project @namespace("Project")  {
                title: String!
            }

            extend api @namespace("Project")  {
                customOperation(input: ProjectBase): Project @path("custom") @method(POST)
            }
        """

        # When: Generate with domain layout config
        output_path = SpringTestUtils.generate(test_input, "util/domain_config.json")

        # Then: Api file should have explicit imports, no wildcards (generated in common since no CRUD)
        api_content = SpringTestUtils.read_file(output_path, "src/main/java/app/server/common/api/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.server.project.dto.ProjectBase;",
            "import app.server.project.dto.Project;",
        )
        SpringTestUtils.assert_not_contains(
            api_content,
            ".*;",  # No wildcard imports
        )

    def test_no_wildcard_imports_in_controller(self) -> None:
        """Controller files should not contain wildcard imports"""
        # Given: An operation with same-namespace types (using base to avoid CRUD conflicts)
        test_input = """\
            base ProjectBase @namespace("Project")  {
                name: String!
            }

            type Project @namespace("Project")  {
                title: String!
            }

            extend api @namespace("Project")  {
                customOperation(input: ProjectBase): Project @path("custom") @method(POST)
            }
        """

        # When: Generate with domain layout config
        output_path = SpringTestUtils.generate(test_input, "util/domain_config.json")

        # Then: Controller file should have explicit imports, no wildcards (generated in common since no CRUD)
        controller_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/common/api/DefaultController.java"
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.server.project.dto.ProjectBase;",
            "import app.server.project.dto.Project;",
        )
        SpringTestUtils.assert_not_contains(
            controller_content,
            ".*;",  # No wildcard imports
        )
        SpringTestUtils.assert_not_contains(
            controller_content,
            "import app.server.project.dto.*;",
            ".*",  # No wildcard imports at all
        )

    def test_no_wildcard_imports_in_service(self) -> None:
        """Service files should not contain wildcard imports and should include QueryDSL Q-class imports"""
        test_input = """\
            type Project @namespace("Project") {
                name: String!
            }

            type User @namespace("User") {
                username: String!
            }
        """

        output_path = SpringTestUtils.generate(test_input, "util/domain_config.json")

        user_service_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/user/service/UserService.java"
        )
        SpringTestUtils.assert_contains(
            user_service_content,
            "import app.server.user.dto.User;",
            "import app.server.user.dto.UserRequest;",
            "import app.server.user.db.UserEntity;",
            "import app.server.user.db.QUserEntity;",  # QueryDSL import
            "import app.server.user.db.UserRepository;",
            "import app.server.user.mapper.UserMapper;",
        )
        SpringTestUtils.assert_not_contains(user_service_content, ".*;")  # No wildcard imports

        project_service_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/project/service/ProjectService.java"
        )
        SpringTestUtils.assert_contains(
            project_service_content,
            "import app.server.project.dto.Project;",
            "import app.server.project.dto.ProjectRequest;",
            "import app.server.project.db.ProjectEntity;",
            "import app.server.project.db.QProjectEntity;",  # QueryDSL import
        )
        SpringTestUtils.assert_not_contains(project_service_content, ".*;")  # No wildcard imports

    def test_cross_namespace_operation_imports_base_response(self) -> None:
        """Operations returning a base type from another namespace should have correct imports."""
        test_input = """\
            base ProjectBase @namespace("Project") {
                name: String!
            }

            extend api @namespace("User") {
                getProjectBase(): ProjectBase @path("user/project-base")
            }
        """

        output_path = SpringTestUtils.generate(test_input, "util/domain_config.json")

        controller_content = SpringTestUtils.read_file(
            output_path, "src/main/java/app/server/common/api/DefaultController.java"
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.server.project.dto.ProjectBase;",
            "public ResponseEntity<ProjectBase> getProjectBase",
        )

        api_content = SpringTestUtils.read_file(output_path, "src/main/java/app/server/common/api/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.server.project.dto.ProjectBase;",
            "ResponseEntity<ProjectBase> getProjectBase",
        )

    def test_filter_respects_domain_package(self) -> None:
        """Query filters should use the package selected by the model's Spring package directive."""
        test_input = """\
            type Project @namespace("ProjectNS") @spring-package("project") {
                name: String! @query
            }
        """
        config = {
            "domain_path": "app.server.{package}.dto",
            "package_placeholder_fallback": "common",
        }

        output_path = SpringTestUtils.generate(test_input, config=config)

        assert SpringTestUtils.file_exists(output_path, "src/main/java/app/server/project/dto/GetProjectsFilter.java")
        assert not SpringTestUtils.file_exists(output_path, "src/main/java/app/server/common/dto/GetProjectsFilter.java")
