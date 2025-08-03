import os


class TestMain:
    """Test module main functionality."""

    def test_module_call(self) -> None:
        """Verify that we can call the module"""

        assert os.system("python -m qsdl examples/openapi/input.qsdl -g openapi -o srcgen/") == 0

        assert os.system("python -m qsdl examples/openapi/input.qsdl -g plantuml -o srcgen/") == 0

        assert os.system("python -m qsdl examples/openapi/input.qsdl -g spring -o srcgen/") == 0

        assert os.system("python -m qsdl examples/openapi/input.qsdl -g void -o srcgen/") == 0

        assert os.system("python -m qsdl examples/multifile/multifile.qsdl -g void -o srcgen/") == 0

        assert os.system("python -m qsdl --help") == 0
