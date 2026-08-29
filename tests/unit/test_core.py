import importlib
import json
from dataclasses import dataclass
from pathlib import Path

import pytest

import qsdl.generators as generator_registry
from qsdl.artifacts import GeneratedFiles
from qsdl.core import build, generate
from qsdl.dsl import Schema, textx
from qsdl.exceptions import QsdlException
from qsdl.generators import GeneratorDefinition, create_config
from qsdl.generators.base_config import BaseConfig


@dataclass
class ProbeConfig(BaseConfig):
    value: str = "default"
    other: str = "default-other"


def _register_probe(monkeypatch: pytest.MonkeyPatch, generator: object) -> None:
    monkeypatch.setitem(
        generator_registry.GENERATORS,
        "probe",
        GeneratorDefinition(generator=generator, config_class=ProbeConfig),  # type: ignore[arg-type]
    )


class TestCore:
    """Test core functions."""

    def test_get_metamodel_plantuml(self) -> None:
        """Verify that we can print the plantuml model"""

        assert textx.get_metamodel(print_uml=True)

    def test_unknown_generator_error_includes_name(self) -> None:
        with pytest.raises(QsdlException, match="missing-generator"):
            build(generator_name="missing-generator", raw_schema="")

    def test_create_config_returns_distinct_instances(self) -> None:
        first = create_config("spring")
        second = create_config("spring")

        assert first is not second
        first.title = "Changed"
        assert second.title == "SpringBootApp"

    def test_config_file_and_raw_mapping_override_defaults_in_order(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: list[ProbeConfig] = []

        def probe(schema: Schema, config: ProbeConfig) -> GeneratedFiles:
            captured.append(config)
            files = GeneratedFiles()
            files.add_text("config.txt", f"{config.value}:{config.other}")
            return files

        _register_probe(monkeypatch, probe)
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({"value": "file", "other": "file-other"}), encoding="utf-8")

        files = build(
            generator_name="probe",
            raw_schema="type User { name: String }",
            config_path=config_path,
            config={"value": "raw"},
        )

        assert files.text("config.txt") == "raw:file-other"
        assert captured[0].value == "raw"
        assert captured[0].other == "file-other"

    def test_invalid_config_roots_are_rejected(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _register_probe(monkeypatch, lambda schema, config: GeneratedFiles())
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

        with pytest.raises(TypeError, match="configuration file root must be a mapping"):
            build(generator_name="probe", raw_schema="", config_path=config_path)
        with pytest.raises(TypeError, match="config must be a mapping"):
            build(generator_name="probe", raw_schema="", config=["not a mapping"])  # type: ignore[arg-type]

    def test_builds_use_fresh_configs_even_when_a_generator_mutates_one(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: list[ProbeConfig] = []
        initial_values: list[str] = []

        def probe(schema: Schema, config: ProbeConfig) -> GeneratedFiles:
            captured.append(config)
            initial_values.append(config.value)
            config.value = "mutated"
            return GeneratedFiles()

        _register_probe(monkeypatch, probe)
        schema = "type User { name: String }"
        build(generator_name="probe", raw_schema=schema)
        build(generator_name="probe", raw_schema=schema)

        assert captured[0] is not captured[1]
        assert initial_values == ["default", "default"]

    def test_generator_returning_none_is_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def invalid_generator(schema: Schema, config: ProbeConfig) -> None:
            return None

        _register_probe(monkeypatch, invalid_generator)

        with pytest.raises(TypeError, match="expected GeneratedFiles"):
            build(generator_name="probe", raw_schema="type User { name: String }")

    def test_build_does_not_create_an_output_directory(self, tmp_path: Path) -> None:
        output_path = tmp_path / "not-created"

        files = build(generator_name="void", raw_schema="type User { name: String }")

        assert len(files) == 0
        assert not output_path.exists()

    def test_standard_generators_return_expected_in_memory_artifacts(self) -> None:
        schema = "type User { name: String }"

        openapi = build(generator_name="openapi", raw_schema=schema)
        postgres = build(generator_name="postgres", raw_schema=schema)
        spring = build(generator_name="spring", raw_schema=schema)

        assert openapi.exists("openapi.yaml")
        assert "User" in openapi.text("openapi.yaml")
        assert postgres.exists("V1_0_0__baseline.sql")
        assert "CREATE TABLE" in postgres.text("V1_0_0__baseline.sql")
        assert spring.exists("src/main/resources/openapi.yaml")
        assert spring.exists("src/main/resources/db/migration/V1_0_0__baseline.sql")

    def test_spring_children_receive_the_same_schema_and_keep_prefixes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        spring_module = importlib.import_module("qsdl.generators.spring.generate")
        seen: list[Schema] = []

        def child(schema: Schema, config: object) -> GeneratedFiles:
            seen.append(schema)
            files = GeneratedFiles()
            files.add_text("child.txt", "child")
            return files

        monkeypatch.setattr(spring_module, "generate_openapi", child)
        monkeypatch.setattr(spring_module, "generate_postgres", child)

        files = build(generator_name="spring", raw_schema="type User { name: String }")

        assert len(seen) == 2
        assert seen[0] is seen[1]
        assert files.text("src/main/resources/child.txt") == "child"
        assert files.text("src/main/resources/db/migration/child.txt") == "child"

    def test_spring_child_path_collision_is_propagated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        spring_module = importlib.import_module("qsdl.generators.spring.generate")

        def colliding_child(schema: Schema, config: object) -> GeneratedFiles:
            files = GeneratedFiles()
            files.add_text("application.yaml", "collision")
            return files

        monkeypatch.setattr(spring_module, "generate_openapi", colliding_child)

        with pytest.raises(ValueError, match="duplicate"):
            build(generator_name="spring", raw_schema="type User { name: String }")

    def test_generate_materializes_build_equivalent_content(self, tmp_path: Path) -> None:
        schema = "type User { name: String }"
        expected = build(generator_name="openapi", raw_schema=schema)

        assert generate(tmp_path, generator_name="openapi", raw_schema=schema) is None

        assert (tmp_path / "openapi.yaml").read_bytes() == expected.text("openapi.yaml").encode("utf-8")
