import shutil
import subprocess
import textwrap
from pathlib import Path

from qsdl.core import generate as qsdl_generate


class SpringTestUtils:
    """Shared helpers for Spring generator tests."""

    OUTPUT_PATH = Path("srcgen/")

    @staticmethod
    def generate(test_input: str, config_path: str | Path | None = None) -> Path:
        """Generate a Spring project and return its output path."""
        test_input = textwrap.dedent(test_input)
        shutil.rmtree(SpringTestUtils.OUTPUT_PATH / "src", ignore_errors=True)

        arguments = {
            "generator_name": "spring",
            "raw_schema": test_input,
        }
        if config_path is not None:
            arguments["config_path"] = config_path

        assert qsdl_generate(SpringTestUtils.OUTPUT_PATH, **arguments) is None
        return SpringTestUtils.OUTPUT_PATH

    @staticmethod
    def read_file(output_path: Path, relative_path: str) -> str:
        """Read a generated file."""
        file_path = output_path / relative_path
        assert file_path.exists(), f"Expected file not found: {file_path}"
        return file_path.read_text(encoding="utf-8")

    @staticmethod
    def file_exists(output_path: Path, relative_path: str) -> bool:
        """Check whether a generated file exists."""
        return (output_path / relative_path).exists()

    @staticmethod
    def assert_contains(content: str, *patterns: str) -> None:
        """Assert that generated content contains all specified patterns."""
        for pattern in patterns:
            assert pattern in content, f"Expected pattern not found: {pattern}\n\nContent:\n{content}"

    @staticmethod
    def assert_not_contains(content: str, *patterns: str) -> None:
        """Assert that generated content contains none of the specified patterns."""
        for pattern in patterns:
            assert pattern not in content, f"Unexpected pattern found: {pattern}\n\nContent:\n{content}"

    @staticmethod
    def assert_tests_succeed(output_path: Path | str = OUTPUT_PATH) -> None:
        """Run Maven tests for a generated Spring project."""
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd=output_path) == 0
