import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

_IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
_PACKAGE = re.compile(r"^package\s+([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*);$", re.MULTILINE)
_INSTANCE_IO = """    private static <T> InstancioApi<T> instanceIo(Class<T> cls) {
        return Instancio.of(cls)
                .withSettings(instanceIoSettings)
                .set(all(ObjectNode.class), ((ObjectNode) JsonUtil.mapper().readTree("{}")).put("test", "data"));
    }"""


@dataclass(frozen=True, slots=True)
class TextEdit:
    """One exact text replacement for a generated file."""

    old_text: str
    new_text: str


def apply_text_edits(path: Path, edits: Sequence[TextEdit]) -> None:
    """Apply unique, non-overlapping text edits to a generated file."""
    source = path.read_text(encoding="utf-8")
    matches: list[tuple[int, int, TextEdit]] = []

    for edit in edits:
        if not edit.old_text:
            raise ValueError("text edit old_text cannot be empty")

        start = source.find(edit.old_text)
        if start == -1:
            raise AssertionError(f"text edit did not match {path}: {edit.old_text[:80]!r}")
        if source.find(edit.old_text, start + len(edit.old_text)) != -1:
            raise AssertionError(f"text edit matched more than once in {path}: {edit.old_text[:80]!r}")

        end = start + len(edit.old_text)
        if any(start < other_end and end > other_start for other_start, other_end, _ in matches):
            raise AssertionError(f"text edits overlap in {path}")
        matches.append((start, end, edit))

    for start, end, edit in sorted(matches, reverse=True):
        source = source[:start] + edit.new_text + source[end:]

    path.write_text(source, encoding="utf-8")


def _single_java_file(srcgen: Path, filename: str) -> Path:
    """Return the only generated Java file with the given name."""
    files = tuple(srcgen.rglob(filename))
    if len(files) != 1:
        raise AssertionError(f"expected one generated {filename}, found {len(files)}")
    return files[0]


def _qualified_class_name(java_file: Path, class_name: str) -> str:
    """Return a generated Java file's fully qualified class name."""
    match = _PACKAGE.search(java_file.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError(f"generated Java file has no package declaration: {java_file}")
    return f"{match.group(1)}.{class_name}"


def _validate_identifier(value: str, label: str) -> None:
    if _IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"invalid Java {label}: {value!r}")


def patch_test_utils(srcgen: Path, overrides: Mapping[str, Mapping[str, str]]) -> None:
    """Patch generated TestUtils with explicit Instancio values for selected classes."""
    if not overrides:
        return

    blocks: list[str] = []
    for class_name, field_values in overrides.items():
        _validate_identifier(class_name, "class name")
        if not field_values:
            raise ValueError(f"test data overrides for {class_name!r} cannot be empty")

        java_file = _single_java_file(srcgen, f"{class_name}.java")
        qualified_class_name = _qualified_class_name(java_file, class_name)
        lines = [f"        if (cls == {qualified_class_name}.class) {{"]

        for field_name, value in field_values.items():
            _validate_identifier(field_name, "field name")
            if not isinstance(value, str):
                raise TypeError(f"test data value for {class_name}.{field_name} must be a string")
            lines.append(f"            api.set(field({qualified_class_name}::{field_name}), {json.dumps(value)});")

        lines.append("        }")
        blocks.append("\n".join(lines))

    test_utils = _single_java_file(srcgen, "TestUtils.java")
    source = test_utils.read_text(encoding="utf-8")
    if source.count(_INSTANCE_IO) != 1:
        raise AssertionError("generated TestUtils instanceIo method did not match exactly once")

    replacement = (
        "    private static <T> InstancioApi<T> instanceIo(Class<T> cls) {\n"
        "        InstancioApi<T> api = Instancio.of(cls)\n"
        "                .withSettings(instanceIoSettings)\n"
        '                .set(all(ObjectNode.class), ((ObjectNode) JsonUtil.mapper().readTree("{}")).put("test", "data"));\n\n'
        + "\n\n".join(blocks)
        + "\n        return api;\n    }"
    )
    apply_text_edits(test_utils, [TextEdit(old_text=_INSTANCE_IO, new_text=replacement)])
