import difflib
import shutil
import subprocess
import textwrap
from pathlib import Path

from qsdl.core import generate


def wrapper_generate(test_input: str) -> Path:
    """Generates Spring Boot code and returns the output path.

    Args:
        test_input (str): The QSDL definition.

    Returns:
        Path: The output directory path.
    """
    test_input = textwrap.dedent(test_input)
    test_output = Path("srcgen/")

    # generate
    shutil.rmtree(test_output / "src", ignore_errors=True)
    assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

    return test_output


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


def assert_mvn() -> None:
    assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0
