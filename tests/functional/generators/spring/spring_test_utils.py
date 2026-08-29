import textwrap
from pathlib import Path

from qsdl.artifacts import GeneratedFiles
from qsdl.core import build


class SpringTestUtils:
    """Shared helpers for in-memory Spring generator tests."""

    @staticmethod
    def generate(
        test_input: str,
        config_path: str | Path | None = None,
        config: dict[str, object] | None = None,
    ) -> GeneratedFiles:
        """Build a Spring project and return its generated artifacts."""
        return build(
            generator_name="spring",
            raw_schema=textwrap.dedent(test_input),
            config_path=Path(config_path) if config_path is not None else None,
            config=config,
        )

    @staticmethod
    def read_file(files: GeneratedFiles, relative_path: str) -> str:
        """Read text from a generated artifact."""
        return files.text(relative_path)

    @staticmethod
    def file_exists(files: GeneratedFiles, relative_path: str) -> bool:
        """Check whether a generated artifact exists."""
        return files.exists(relative_path)

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
