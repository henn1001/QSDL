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
        files = SpringTestUtils.generate(test_input)

        # Then: Verify the Controller imports Project from the correct package
        controller_content = SpringTestUtils.read_file(files, "src/main/java/app/api/user/web/DefaultController.java")
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.api.project.contract.Project;",  # Should import Project from project package
            "public ResponseEntity<Project> getProjectFromUser",  # Uses Project as return type
        )

        # Should NOT have wildcard import to common.dto (which doesn't exist in domain layout)
        # or if it does exist, Project should not rely on it
        assert "import app.api.project.contract.Project;" in controller_content

        # Then: Verify the Api interface also has correct imports
        api_content = SpringTestUtils.read_file(files, "src/main/java/app/api/user/web/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.api.project.contract.Project;",  # Should import Project from project package
            "ResponseEntity<Project> getProjectFromUser",  # Uses Project as return type
        )

        # Then: Verify the Service has correct imports (Project is generated with CRUD)
        service_content = SpringTestUtils.read_file(files, "src/main/java/app/api/project/ProjectService.java")
        SpringTestUtils.assert_contains(
            service_content,
            "import app.api.project.contract.Project;",
            "import app.api.project.contract.ProjectRequest;",
            "import app.api.project.persistence.ProjectEntity;",
            "import app.api.project.persistence.QProjectEntity;",
            "import app.api.project.persistence.ProjectRepository;",
            "import app.api.project.mapping.ProjectMapper;",
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
        files = SpringTestUtils.generate(test_input)

        # Then: Verify imports for both parameter and return type
        controller_content = SpringTestUtils.read_file(files, "src/main/java/app/api/user/web/DefaultController.java")
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.api.project.contract.Project;",  # Import for return type
            "import app.api.project.contract.ProjectRequest;",  # Import for body parameter
        )

        api_content = SpringTestUtils.read_file(files, "src/main/java/app/api/user/web/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.api.project.contract.Project;",
            "import app.api.project.contract.ProjectRequest;",
        )

        # Then: Verify Service has no wildcard imports
        service_content = SpringTestUtils.read_file(files, "src/main/java/app/api/project/ProjectService.java")
        SpringTestUtils.assert_contains(
            service_content,
            "import app.api.project.contract.Project;",
            "import app.api.project.contract.ProjectRequest;",
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
        files = SpringTestUtils.generate(test_input)

        # Then: Verify all cross-namespace imports are present
        controller_content = SpringTestUtils.read_file(files, "src/main/java/app/api/admin/web/DefaultController.java")
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.api.project.contract.Project;",
            "import app.api.user.contract.User;",
        )

        api_content = SpringTestUtils.read_file(files, "src/main/java/app/api/admin/web/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.api.project.contract.Project;",
            "import app.api.user.contract.User;",
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
        files = SpringTestUtils.generate(test_input)

        # Then: Api file should have explicit imports, no wildcards (generated in project since no CRUD)
        api_content = SpringTestUtils.read_file(files, "src/main/java/app/api/project/web/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.api.project.contract.ProjectBase;",
            "import app.api.project.contract.Project;",
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
        files = SpringTestUtils.generate(test_input)

        # Then: Controller file should have explicit imports, no wildcards (generated in project since no CRUD)
        controller_content = SpringTestUtils.read_file(
            files, "src/main/java/app/api/project/web/DefaultController.java"
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.api.project.contract.ProjectBase;",
            "import app.api.project.contract.Project;",
        )
        SpringTestUtils.assert_not_contains(
            controller_content,
            ".*;",  # No wildcard imports
        )
        SpringTestUtils.assert_not_contains(
            controller_content,
            "import app.api.project.contract.*;",
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

        files = SpringTestUtils.generate(test_input)

        user_service_content = SpringTestUtils.read_file(files, "src/main/java/app/api/user/UserService.java")
        SpringTestUtils.assert_contains(
            user_service_content,
            "import app.api.user.contract.User;",
            "import app.api.user.contract.UserRequest;",
            "import app.api.user.persistence.UserEntity;",
            "import app.api.user.persistence.QUserEntity;",  # QueryDSL import
            "import app.api.user.persistence.UserRepository;",
            "import app.api.user.mapping.UserMapper;",
        )
        SpringTestUtils.assert_not_contains(user_service_content, ".*;")  # No wildcard imports

        project_service_content = SpringTestUtils.read_file(files, "src/main/java/app/api/project/ProjectService.java")
        SpringTestUtils.assert_contains(
            project_service_content,
            "import app.api.project.contract.Project;",
            "import app.api.project.contract.ProjectRequest;",
            "import app.api.project.persistence.ProjectEntity;",
            "import app.api.project.persistence.QProjectEntity;",  # QueryDSL import
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

        files = SpringTestUtils.generate(test_input)

        controller_content = SpringTestUtils.read_file(files, "src/main/java/app/api/user/web/DefaultController.java")
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.api.project.contract.ProjectBase;",
            "public ResponseEntity<ProjectBase> getProjectBase",
        )

        api_content = SpringTestUtils.read_file(files, "src/main/java/app/api/user/web/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "import app.api.project.contract.ProjectBase;",
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

        files = SpringTestUtils.generate(test_input, config=config)

        assert SpringTestUtils.file_exists(files, "src/main/java/app/server/project/dto/GetProjectsFilter.java")
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/server/common/dto/GetProjectsFilter.java")
