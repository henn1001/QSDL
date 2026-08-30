import difflib
import subprocess
import textwrap
from collections.abc import Mapping
from pathlib import Path

from qsdl.core import generate


def wrapper_generate(
    test_input: str, output_path: Path, config: Mapping[str, object] | None = None
) -> Path:
    """Generate Spring Boot code into an isolated test directory.

    Args:
        test_input (str): The QSDL definition.
        output_path (Path): The isolated output directory for this test class.
        config (Mapping[str, object] | None): Optional generator configuration.

    Returns:
        Path: The output directory path.
    """
    test_input = textwrap.dedent(test_input)
    output_path.mkdir(parents=True, exist_ok=True)
    assert generate(output_path, generator_name="spring", raw_schema=test_input, config=config) is None

    return output_path


def assert_postgres(schema: str, expected_schema: str) -> None:
    """Asserts that the generated schema matches the expected schema.

    Args:
        schema (str): The generated schema.
        expected_schema (str): The expected schema.

    Raises:
        AssertionError: If the schemas don't match, with a unified diff.
    """
    schema_lines = [line.strip() for line in schema.splitlines() if line.strip() and not line.startswith("--")]
    expected_lines = [line.strip() for line in expected_schema.splitlines() if line.strip()]

    if schema_lines != expected_lines:
        diff = difflib.unified_diff(expected_lines, schema_lines, fromfile="Expected", tofile="Generated", lineterm="")
        diff = "\n".join(diff)
        raise AssertionError(f"Schema mismatch:\n{diff}")


def assert_mvn(srcgen: Path) -> None:
    """Run Maven for an isolated generated project without reading the terminal."""
    result = subprocess.run(
        ["mvn", "-q", "clean", "test"],
        cwd=srcgen,
        stdin=subprocess.DEVNULL,
        check=False,
    )
    assert result.returncode == 0
