from pathlib import Path

import pytest
from textx.exceptions import TextXSemanticError

from qsdl.dsl.textx import parse_schema
from qsdl.generators.spring import generator
from qsdl.generators.spring.config import SPRING_CONTROLLER, SPRING_PACKAGE

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

        files = SpringTestUtils.generate(schema)

        for package, name in (
            ("namespaceonly", "NamespaceOnly"),
            ("packageonly", "PackageOnly"),
            ("explicit", "Both"),
        ):
            assert SpringTestUtils.file_exists(files, f"src/main/java/app/api/{package}/contract/{name}.java")

        assert not SpringTestUtils.file_exists(files, "src/main/java/app/api/namespace/contract/Both.java")

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

        enum_content = SpringTestUtils.read_file(files, "src/main/java/app/enumpackage/constant/State.java")
        dto_content = SpringTestUtils.read_file(files, "src/main/java/app/item/domain/Item.java")
        SpringTestUtils.assert_contains(
            enum_content,
            "package app.enumpackage.constant;",
        )
        SpringTestUtils.assert_contains(
            dto_content,
            "import app.enumpackage.constant.State;",
        )
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/enumnamespace/constant/State.java")

    def test_api_package_precedence(self) -> None:
        """An API's @spring-package should override its @namespace package."""
        schema = """\
            extend api @namespace("ApiNamespace") @spring-package("apipackage") {
                ping: Void @path("ping")
            }
        """

        files = SpringTestUtils.generate(schema)

        api_content = SpringTestUtils.read_file(files, "src/main/java/app/api/apipackage/web/DefaultApi.java")
        SpringTestUtils.assert_contains(
            api_content,
            "package app.api.apipackage.web;",
            "ResponseEntity<Void> ping()",
        )
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/api/apinamespace/web/DefaultApi.java")

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

            type EmptyApi @namespace("ModelNamespace") @spring-package("owner") {
                name: String!
                extend api @namespace("") { emptyPing: Void @path("empty") }
            }

            type PackageApi @namespace("ModelNamespace") @spring-package("model") {
                name: String!

                extend api @namespace("ApiNamespace") @spring-package("api") {
                    packagePing: Void @path("package")
                }
            }
        """

        parsed = parse_schema(raw_schema=schema, directive_specs=generator.directive_specs)
        apis = {obj.name: obj.api for obj in parsed.types}
        for name, origin, value in (
            ("Inherited", "synthetic", "InheritedNamespace"),
            ("NamespaceApi", "source", "ApiNamespace"),
            ("EmptyApi", "source", ""),
        ):
            api = apis[name]
            node = api.directive.namespace
            assert node.origin == origin and node.value == value
            assert node.parent is api and (node.location is None) == (origin == "synthetic")

        files = SpringTestUtils.generate(schema)

        for package, name in (
            ("owner", "Inherited"),
            ("owner", "EmptyApi"),
            ("apinamespace", "NamespaceApi"),
            ("api", "PackageApi"),
        ):
            assert SpringTestUtils.file_exists(files, f"src/main/java/app/api/{package}/web/{name}Api.java")

        assert SpringTestUtils.file_exists(files, "src/main/java/app/api/model/contract/NamespaceApi.java")
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/api/inheritednamespace/web/InheritedApi.java")

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

        files = SpringTestUtils.generate(schema)

        custom_api = SpringTestUtils.read_file(files, "src/main/java/app/api/custom/web/DefaultApi.java")
        other_api = SpringTestUtils.read_file(files, "src/main/java/app/api/other/web/DefaultApi.java")
        SpringTestUtils.assert_contains(custom_api, "customPing()")
        SpringTestUtils.assert_not_contains(custom_api, "namespacedPing()")
        SpringTestUtils.assert_contains(other_api, "namespacedPing()")
        SpringTestUtils.assert_not_contains(other_api, "customPing()")

    def test_spring_controller_keeps_target_package(self) -> None:
        """Merged operations follow declaration order, independent of controller ownership."""
        schema = """\
            extend api @spring-controller("Target") @spring-package("custom") {
                before: Void @path("before")
            }

            type Target @namespace("Target") @spring-package("target") {
                name: String!

                extend api @generate("CREATE") {
                    inside: Void @path("inside")
                }
            }

            extend api @spring-controller("Target") @spring-package("custom") {
                ping: Void @path("ping")
            }
        """

        files = SpringTestUtils.generate(schema)

        controller_content = SpringTestUtils.read_file(files, "src/main/java/app/api/target/web/TargetController.java")
        SpringTestUtils.assert_contains(
            controller_content,
            "package app.api.target.web;",
            "public ResponseEntity<Void> ping()",
        )
        assert not SpringTestUtils.file_exists(files, "src/main/java/app/api/custom/web/TargetController.java")
        api_content = SpringTestUtils.read_file(files, "src/main/java/app/api/target/web/TargetApi.java")
        for content in (api_content, controller_content):
            assert content.index("before()") < content.index("inside()") < content.index("createTarget(")
            assert content.index("createTarget(") < content.index("ping()")

    def test_api_namespace_can_split_api_and_model_packages(self) -> None:
        """API-local namespaces should not break imports for generated model services."""
        schema = """\
            type Epic @namespace("Epic") @spring-package("owner") {
                name: String!

                extend api @namespace("Other") @generate("CREATE") {}
            }
        """

        files = SpringTestUtils.generate(schema)

        service_content = SpringTestUtils.read_file(files, "src/main/java/app/api/other/EpicService.java")
        controller_content = SpringTestUtils.read_file(files, "src/main/java/app/api/other/web/EpicController.java")
        SpringTestUtils.assert_contains(
            service_content,
            "import app.api.owner.contract.Epic;",
            "import app.api.owner.contract.EpicRequest;",
            "import app.api.owner.persistence.EpicEntity;",
            "import app.api.owner.mapping.EpicMapper;",
        )
        SpringTestUtils.assert_contains(
            controller_content,
            "import app.api.owner.mapping.EpicMapper;",
            "import app.api.other.EpicService;",
        )


def test_package_example_artifact_parity_under_reordering() -> None:
    example = Path(__file__).resolve().parents[4] / "examples/04-apis/16-package-and-controller-directives/schema.qsdl"
    raw = example.read_text(encoding="utf-8")
    reordered = raw.replace(
        '@namespace("Projects") @spring-package("project")',
        '@spring-package("project") @namespace("Projects")',
    ).replace(
        '@namespace("Operations") @spring-package("operations") @spring-controller("Project")',
        '@spring-controller("Project") @spring-package("operations") @namespace("Operations")',
    )
    assert reordered != raw
    before, after = SpringTestUtils.generate(raw), SpringTestUtils.generate(reordered)
    assert list(before) == list(after)
    assert "projectHealth(@PathVariable" in after.text("src/main/java/app/api/project/web/ProjectApi.java")


def test_spring_package_and_controller_activation() -> None:
    raw = """
        type Foo @spring-package("pkg") @namespace("Domain") @spring-pakage(unquoted) {
            label: String @readOnly
            extend api @spring-controller("Foo") {
                run(): String @path("run") @headers(X-Token: String) @method(POST)
            }
        }
    """
    (plain,) = parse_schema(raw_schema=raw).types
    assert plain.directives[0].spec is None
    assert plain.directives.get(SPRING_PACKAGE) is None
    assert plain.api.directives.get(SPRING_CONTROLLER) is None

    (foo,) = parse_schema(raw_schema=raw, directive_specs=generator.directive_specs).types
    assert foo.directives.get(SPRING_PACKAGE) is foo.directives[0]
    assert foo.directives[0].value == "pkg"
    assert foo.directives.by_name("spring-pakage").spec is None
    assert foo.api.directives.get(SPRING_CONTROLLER) is foo.api.directives[0]
    assert foo.api.directives[0].value == "Foo"


@pytest.mark.parametrize(
    ("raw", "name", "message"),
    [
        ("type Foo @spring-package {}", "spring-package", "Invalid @spring-package"),
        ('type Foo @spring-package("") {}', "spring-package", "Invalid @spring-package"),
        ("type Foo @spring-package(pkg) {}", "spring-package", "Invalid @spring-package"),
        ('scalar Foo @spring-package("pkg")', "spring-package", "not supported"),
        ("extend api @spring-controller(Foo) {}", "spring-controller", "Invalid @spring-controller"),
        ('type Foo @spring-controller("Foo") {}', "spring-controller", "not supported"),
    ],
)
def test_invalid_spring_directives_are_only_errors_with_spring(raw: str, name: str, message: str) -> None:
    assert parse_schema(raw_schema=raw).types[0].directives.by_name(name).spec is None
    with pytest.raises(TextXSemanticError, match=message) as error:
        SpringTestUtils.generate(raw)
    assert (error.value.line, error.value.col) == (1, raw.index(f"@{name}") + 1)


def test_synthetic_operation_models_have_independent_package_nodes(monkeypatch: pytest.MonkeyPatch) -> None:
    from qsdl.generators.spring.models import ModelClass

    recipients = {}
    initialize = ModelClass.__post_init__

    def capture(model: ModelClass) -> None:
        recipients[model.name] = model.source
        initialize(model)

    monkeypatch.setattr(ModelClass, "__post_init__", capture)
    schema = parse_schema(
        raw_schema="""
        extend api @spring-package("pkg") {
            search(name: String?, description: String?): String @path("search")
            run(label: String): String @path("run") @method(POST)
        }
        """,
        directive_specs=generator.directive_specs,
    )
    files = generator.generate(schema, generator.config_class())
    assert files.exists("src/main/java/app/api/pkg/contract/SearchFilter.java")
    assert files.exists("src/main/java/app/api/pkg/contract/RunRequest.java")

    original = schema.types[0].directives.get(SPRING_PACKAGE)
    filter_ref, request_ref = (recipients[name] for name in ("SearchFilter", "RunRequest"))
    for ref in (filter_ref, request_ref):
        node = ref.directives.get(SPRING_PACKAGE)
        assert node is ref.directives[0] and node is not original
        assert node.origin == "synthetic" and node.parent is ref and node.value == original.value
    assert filter_ref.directives[0] is not request_ref.directives[0]
