import copy
from pathlib import Path, PurePosixPath

import plantuml
import pytest

from qsdl.core import build
from qsdl.dsl.textx import parse_schema
from qsdl.generators.i18n import I18nConfig
from qsdl.generators.i18n import generator as i18n_generator

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

    assert files.paths() == (PurePosixPath("en.yaml"),)
    content = files.text("en.yaml")
    assert "domain:\n" in content
    assert "\n  User:" in content
    assert "constant:\n  Status:" in content
    assert "OPEN:" in content


def test_i18n_includes_inheritance_but_omits_ignored_overrides() -> None:
    files = build(
        generator_name="i18n",
        raw_schema="""
        base Details { label: String visible: String }
        type Item extends Details { label: String @override @ignore note: String }
        """,
    )
    content = files.text("en.yaml")
    assert "domain.Item:\n" in content
    assert "\n  visible:" in content
    assert "\n  note:" in content
    assert "\n  label:" not in content


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


def test_i18n_generator_reads_existing_translations_without_writing(tmp_path: Path) -> None:
    schema = parse_schema(raw_schema=SCHEMA)
    config = I18nConfig()
    target = tmp_path / "en.yaml"
    existing = "domain:\n  User:\n    name: Existing Name\n"
    target.write_text(existing, encoding="utf-8")

    files = i18n_generator.generate(schema, config, tmp_path)

    assert "Existing Name" in files.text("en.yaml")
    assert files.paths() == (PurePosixPath("en.yaml"),)
    assert sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()) == [Path("en.yaml")]
    assert target.read_text(encoding="utf-8") == existing


def test_i18n_generation_does_not_mutate_config() -> None:
    schema = parse_schema(raw_schema=SCHEMA)
    config = I18nConfig(extra_locales="de", split_files=True, single_file=False)
    original = copy.deepcopy(config)

    i18n_generator.generate(schema, config)

    assert config == original


def test_i18n_builds_do_not_leak_locale_configuration() -> None:
    first = build(generator_name="i18n", raw_schema=SCHEMA, config={"locale": "fr"})
    second = build(generator_name="i18n", raw_schema=SCHEMA, config={"locale": "de"})

    assert first.exists("fr.yaml")
    assert second.exists("de.yaml")
    assert not second.exists("fr.yaml")


def test_i18n_validates_translation_paths_as_artifact_paths() -> None:
    with pytest.raises(ValueError, match=r"artifact path cannot contain '\.\.'"):
        build(generator_name="i18n", raw_schema=SCHEMA, config={"locale": "../en"})


def test_plantuml_renders_shared_diamond_field_once(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plantuml.PlantUML, "processes", lambda *_: b"png")
    files = build(
        generator_name="plantuml",
        raw_schema="""
        base Root { label: String }
        base Left extends Root { first: Int }
        base Right extends Root { second: Int }
        type Diamond extends Left, Right { note: String }
        """,
    )
    fields = files.text("plantuml.md").split("class Diamond ", 1)[1].split("{\n", 1)[1].split("\n\n", 1)[0]
    assert fields.splitlines() == [
        "    label: String",
        "    first: Int",
        "    second: Int",
        "    id: ID",
        "    note: String",
    ]


def test_plantuml_does_not_restore_ignored_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plantuml.PlantUML, "processes", lambda *_: b"png")
    files = build(
        generator_name="plantuml",
        raw_schema="""
        base Named @force-generate { label: String keep: String }
        type Item extends Named { label: Int @override @ignore note: String }
        """,
    )
    base, item = files.text("plantuml.md").split("class Item ", 1)
    assert "label: String" in base
    fields = item.split("{\n", 1)[1].split("\n\n", 1)[0]
    assert fields.splitlines() == ["    keep: String", "    id: ID", "    note: String"]


@pytest.mark.parametrize(
    ("source", "expected_fields"),
    [
        (
            """
            base Details { hidden: String @ignore visible: String }
            type Item extends Details { note: String }
            """,
            ["visible: String", "id: ID", "note: String"],
        ),
        (
            """
            base Left { label: String first: Int }
            base Right { label: Int second: Int }
            type Item extends Left, Right { label: Long @override note: String }
            """,
            ["label: Long", "first: Int", "second: Int", "id: ID", "note: String"],
        ),
    ],
    ids=["ignored-field-from-unused-base", "override-replaces-distinct-candidates"],
)
def test_plantuml_renders_resolved_fields(
    monkeypatch: pytest.MonkeyPatch, source: str, expected_fields: list[str]
) -> None:
    monkeypatch.setattr(plantuml.PlantUML, "processes", lambda *_: b"png")
    markdown = build(generator_name="plantuml", raw_schema=source).text("plantuml.md")
    fields = markdown.split("class Item ", 1)[1].split("{\n", 1)[1].split("\n\n", 1)[0]
    assert [line.strip() for line in fields.splitlines()] == expected_fields


def test_plantuml_returns_markdown_and_exact_png_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = (b"enum", b"base", b"overview")
    calls: list[str] = []

    def processes(_plantuml: plantuml.PlantUML, definition: str) -> bytes:
        calls.append(definition)
        return responses[len(calls) - 1]

    monkeypatch.setattr(plantuml.PlantUML, "processes", processes)
    schema = (
        SCHEMA
        + """
    type Team {
        label: String
    }

    type Owner extends Details {
        users: [User]! @composition
        teams: [Team]! @aggregation
    }
    """
    )
    files = build(generator_name="plantuml", raw_schema=schema)

    markdown = files.text("plantuml.md")
    assert "Owner --* User" in markdown
    assert "Owner --o Team" in markdown
    owner_fields = markdown.split("class Owner ", 1)[1].split("}", 1)[0]
    assert owner_fields.index("value: String") < owner_fields.index("id: ID")
    assert files.bytes("plantuml.enums.png") == b"enum"
    assert files.bytes("plantuml.bases.png") == b"base"
    assert files.bytes("plantuml.overview.png") == b"overview"
    assert len(calls) == 3
