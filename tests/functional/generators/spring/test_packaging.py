from .spring_test_utils import SpringTestUtils


class TestSpringPackaging:
    """Test Spring package selection and API/controller placement."""

    def test_type_package_precedence(self) -> None:
        """Type packages should prefer @spring-package over @namespace."""
        schema = """\
            type NamespaceOnly @namespace("NamespaceOnly") {
                name: String!
            }

            type PackageOnly @spring-package("packageonly") {
                name: String!
            }

            type Both @namespace("Namespace") @spring-package("explicit") {
                name: String!
            }
        """

        files = SpringTestUtils.generate(schema, "util/domain_config.json")

        for package, name in (
            ("namespaceonly", "NamespaceOnly"),
            ("packageonly", "PackageOnly"),
            ("explicit", "Both"),
        ):
            assert SpringTestUtils.file_exists(files, f"src/main/java/app/server/{package}/dto/{name}.java")

        assert not SpringTestUtils.file_exists(files, "src/main/java/app/server/namespace/dto/Both.java")

    def test_enum_package_precedence(self) -> None:
        """Enum packages should use @spring-package before @namespace."""
        schema = """\
            enum State @namespace("EnumNamespace") @spring-package("enumpackage") {
                OPEN
            }

            type Item @namespace("Item") {
                state: State
            }
        """
        config = {"enum_path": "{package}.constant", "domain_path": "{package}.domain"}

        files = SpringTestUtils.generate(schema, config=config)

        enum_content = SpringTestUtils.read_file(files, "src/main/java/app/server/enumpackage/constant/State.java")
        dto_content = SpringTestUtils.read_file(files, "src/main/java/app/server/item/domain/Item.java")
        SpringTestUtils.assert_contains(
            enum_content,
            "package app.server.enumpackage.constant;",
        )
        SpringTestUtils.assert_contains(
            dto_content,
            "import app.server.enumpackage.constant.State;",
        )
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/server/enumnamespace/constant/State.java")

    def test_api_package_precedence(self) -> None:
        """An API's @spring-package should override its @namespace package."""
        schema = """\
            extend api @namespace("ApiNamespace") @spring-package("apipackage") {
                ping: Void @path("ping")
            }
        """

        files = SpringTestUtils.generate(schema, "util/domain_config.json")

        api_content = SpringTestUtils.read_file(files, "src/main/java/app/server/apipackage/api/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "package app.server.apipackage.api;",
            "ResponseEntity<Void> ping()",
        )
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/server/apinamespace/api/DefaultApi.java")

    def test_object_api_package_precedence_and_namespace_inheritance(self) -> None:
        """Object APIs should respect API-local directives and owner package fallback."""
        schema = """\
            type Inherited @namespace("InheritedNamespace") @spring-package("owner") {
                name: String!

                extend api {
                    inheritedPing: Void @path("inherited")
                }
            }

            type NamespaceApi @namespace("ModelNamespace") @spring-package("model") {
                name: String!

                extend api @namespace("ApiNamespace") {
                    namespacePing: Void @path("namespace")
                }
            }

            type PackageApi @namespace("ModelNamespace") @spring-package("model") {
                name: String!

                extend api @namespace("ApiNamespace") @spring-package("api") {
                    packagePing: Void @path("package")
                }
            }
        """

        files = SpringTestUtils.generate(schema, "util/domain_config.json")

        for package, name in (
            ("owner", "Inherited"),
            ("apinamespace", "NamespaceApi"),
            ("api", "PackageApi"),
        ):
            assert SpringTestUtils.file_exists(files, f"src/main/java/app/server/{package}/api/{name}Api.java")

        assert SpringTestUtils.file_exists(files, "src/main/java/app/server/model/dto/NamespaceApi.java")
        assert not SpringTestUtils.file_exists(
            files, "src/main/java/app/server/inheritednamespace/api/InheritedApi.java"
        )

    def test_top_level_apis_with_different_packages_are_not_merged(self) -> None:
        """Default-named top-level APIs in different packages need separate controllers."""
        schema = """\
            extend api @spring-package("custom") {
                customPing: Void @path("custom-ping")
            }

            extend api @namespace("Other") {
                namespacedPing: Void @path("namespaced-ping")
            }
        """

        files = SpringTestUtils.generate(schema, "util/domain_config.json")

        custom_api = SpringTestUtils.read_file(files, "src/main/java/app/server/custom/api/DefaultApi.java")
        other_api = SpringTestUtils.read_file(files, "src/main/java/app/server/other/api/DefaultApi.java")
        SpringTestUtils.assert_contains(custom_api, "customPing()")
        SpringTestUtils.assert_not_contains(custom_api, "namespacedPing()")
        SpringTestUtils.assert_contains(other_api, "namespacedPing()")
        SpringTestUtils.assert_not_contains(other_api, "customPing()")

    def test_spring_controller_keeps_target_package(self) -> None:
        """@spring-controller should merge custom operations into the target package."""
        schema = """\
            type Target @namespace("Target") @spring-package("target") {
                name: String!

                extend api @generate("CREATE") {}
            }

            extend api @spring-controller("Target") @spring-package("custom") {
                ping: Void @path("ping")
            }
        """

        files = SpringTestUtils.generate(schema, "util/domain_config.json")

        controller_content = SpringTestUtils.read_file(
            files, "src/main/java/app/server/target/api/TargetController.java"
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "package app.server.target.api;",
            "public ResponseEntity<Void> ping()",
        )
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/server/custom/api/TargetController.java")

    def test_api_namespace_can_split_api_and_model_packages(self) -> None:
        """API-local namespaces should not break imports for generated model services."""
        schema = """\
            type Epic @namespace("Epic") @spring-package("owner") {
                name: String!

                extend api @namespace("Other") @generate("CREATE") {}
            }
        """

        files = SpringTestUtils.generate(schema, "util/domain_config.json")

        service_content = SpringTestUtils.read_file(files, "src/main/java/app/server/other/service/EpicService.java")
        controller_content = SpringTestUtils.read_file(files, "src/main/java/app/server/other/api/EpicController.java")
        SpringTestUtils.assert_contains(
            service_content,
            "import app.server.owner.dto.Epic;",
            "import app.server.owner.dto.EpicRequest;",
            "import app.server.owner.db.EpicEntity;",
            "import app.server.owner.mapper.EpicMapper;",
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.server.owner.mapper.EpicMapper;",
            "import app.server.other.service.EpicService;",
        )
