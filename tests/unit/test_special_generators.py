import copy
from pathlib import Path, PurePosixPath

import plantuml
import pytest

from qsdl.core import build
from qsdl.dsl.textx import parse_schema
from qsdl.generators.i18n import Config as I18nConfig
from qsdl.generators.i18n import build_files_for_directory, generate as generate_i18n


SCHEMA = """
    enum Status {
        OPEN
    }

    base Details {
        value: String
    }

    type User {
        name: String
        status: Status
        details: Details
    }
"""


def test_i18n_builds_in_memory_with_single_file_layout() -> None:
    files = build(generator_name="i18n", raw_schema=SCHEMA)

    assert files.exists("en/domain.yaml")
    assert files.exists("en/constant.yaml")
    assert "User" in files.text("en/domain.yaml")
    assert "OPEN" in files.text("en/constant.yaml")


def test_i18n_builds_split_files_for_each_locale() -> None:
    files = build(
        generator_name="i18n",
        raw_schema=SCHEMA,
        config={
            "split_files": True,
            "single_file": False,
            "subfolder": "messages",
            "extra_locales": "de",
        },
    )

    assert files.paths() == (
        PurePosixPath("de/messages/Details.yaml"),
        PurePosixPath("de/messages/Status.yaml"),
        PurePosixPath("de/messages/User.yaml"),
        PurePosixPath("en/messages/Details.yaml"),
        PurePosixPath("en/messages/Status.yaml"),
        PurePosixPath("en/messages/User.yaml"),
    )


def test_i18n_directory_adapter_reads_existing_translations_without_writing(tmp_path: Path) -> None:
    schema = parse_schema(raw_schema=SCHEMA)
    config = I18nConfig()
    target = tmp_path / "en/domain.yaml"
    target.parent.mkdir(parents=True)
    target.write_text("User:\n  name: Existing Name\n", encoding="utf-8")

    files = build_files_for_directory(schema, config, tmp_path)

    assert "Existing Name" in files.text("en/domain.yaml")
    assert not (tmp_path / "en/constant.yaml").exists()
    assert target.read_text(encoding="utf-8") == "User:\n  name: Existing Name\n"


def test_i18n_generation_does_not_mutate_config() -> None:
    schema = parse_schema(raw_schema=SCHEMA)
    config = I18nConfig(extra_locales="de", split_files=True, single_file=False)
    original = copy.deepcopy(config)

    generate_i18n(schema, config)

    assert config == original


def test_i18n_builds_do_not_leak_locale_configuration() -> None:
    first = build(generator_name="i18n", raw_schema=SCHEMA, config={"locale": "fr"})
    second = build(generator_name="i18n", raw_schema=SCHEMA, config={"locale": "de"})

    assert first.exists("fr/domain.yaml")
    assert second.exists("de/domain.yaml")
    assert not second.exists("fr/domain.yaml")


def test_plantuml_returns_markdown_and_exact_png_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = (b"enum", b"base", b"overview")
    calls: list[str] = []

    def processes(_plantuml: plantuml.PlantUML, definition: str) -> bytes:
        calls.append(definition)
        return responses[len(calls) - 1]

    monkeypatch.setattr(plantuml.PlantUML, "processes", processes)
    files = build(generator_name="plantuml", raw_schema=SCHEMA)

    assert files.text("plantuml.md")
    assert files.bytes("plantuml.enums.png") == b"enum"
    assert files.bytes("plantuml.bases.png") == b"base"
    assert files.bytes("plantuml.overview.png") == b"overview"
    assert len(calls) == 3
