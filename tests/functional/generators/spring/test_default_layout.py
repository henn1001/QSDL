"""Regression coverage for the default domain-first Spring layout."""

from qsdl.generators.spring.config import SpringConfig

from .spring_test_utils import SpringTestUtils


def test_default_config_uses_domain_first_layout() -> None:
    config = SpringConfig()
    assert config.base_package == "app"
    assert config.api_path == "app.api.{package}.web"
    assert config.domain_path == "app.api.{package}.contract"
    assert config.controller_path == "app.api.{package}.web"
    assert config.repository_path == "app.api.{package}.persistence"
    assert config.config_path == "app.shared.config"
    assert config.exception_path == "app.shared.exception"
    assert config.model_path == "app.shared.model"
    assert config.util_path == "app.shared.util"
    assert config.entity_path == "app.api.{package}.persistence"
    assert config.mapper_path == "app.api.{package}.mapping"
    assert config.service_path == "app.api.{package}"
    assert config.enum_path == "app.shared.constants"
    assert config.shared_controller_path == "app.shared.web"
    assert config.shared_repository_path == "app.shared.persistence"
    assert config.package_placeholder_fallback == "general"


def test_default_generation_separates_domain_and_shared_support() -> None:
    files = SpringTestUtils.generate(
        """
        enum State { ACTIVE }
        type Project @namespace("Project") { state: State }
        """
    )

    assert SpringTestUtils.file_exists(files, "src/main/java/app/api/project/ProjectService.java")
    assert SpringTestUtils.file_exists(files, "src/main/java/app/api/project/web/ProjectApi.java")
    assert SpringTestUtils.file_exists(files, "src/main/java/app/api/project/contract/Project.java")
    assert SpringTestUtils.file_exists(files, "src/main/java/app/api/project/persistence/ProjectEntity.java")
    assert SpringTestUtils.file_exists(files, "src/main/java/app/api/project/mapping/ProjectMapper.java")
    assert SpringTestUtils.file_exists(files, "src/main/java/app/shared/web/BaseController.java")
    assert SpringTestUtils.file_exists(files, "src/main/java/app/shared/persistence/AbstractRepository.java")
    assert SpringTestUtils.file_exists(files, "src/main/java/app/shared/constants/State.java")
    assert "app.shared.persistence.AbstractRepository" in files.text(
        "src/main/java/app/api/project/persistence/ProjectRepository.java"
    )
