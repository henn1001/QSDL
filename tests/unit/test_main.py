import subprocess
import sys
from pathlib import Path


class TestMain:
    """Test module main functionality."""

    def test_module_generate_void(self, tmp_path: Path) -> None:
        """``python -m qsdl`` invokes the CLI and materializes its destination."""
        schema = tmp_path / "input.qsdl"
        schema.write_text("type Item { name: String }\n")
        output = tmp_path / "srcgen"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "qsdl",
                "generate",
                "void",
                "-i",
                str(schema),
                "-o",
                str(output),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert output.is_dir()
        assert "QSDL Generator: void" in result.stderr

    def test_module_help_lists_generate(self) -> None:
        """The module entrypoint exposes the root CLI commands."""
        result = subprocess.run([sys.executable, "-m", "qsdl", "--help"], capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stderr
        assert "generate" in result.stdout
