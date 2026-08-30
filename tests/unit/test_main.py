import subprocess
import sys
from pathlib import Path


class TestMain:
    """Test module main functionality."""

    def test_module_call(self, tmp_path: Path) -> None:
        """Verify that we can call the module without sharing generated files."""

        output_path = tmp_path / "srcgen"

        def run_cli(*args: str) -> None:
            result = subprocess.run([sys.executable, "-m", "qsdl", *args], check=False)
            assert result.returncode == 0

        run_cli("examples/openapi/input.qsdl", "-g", "openapi", "-o", str(output_path))
        run_cli("examples/openapi/input.qsdl", "-g", "plantuml", "-o", str(output_path))
        run_cli("examples/openapi/input.qsdl", "-g", "spring", "-o", str(output_path))
        run_cli("examples/openapi/input.qsdl", "-g", "void", "-o", str(output_path))
        run_cli("examples/multifile/multifile.qsdl", "-g", "void", "-o", str(output_path))
        run_cli("--help")
