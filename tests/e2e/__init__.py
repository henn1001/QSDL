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
