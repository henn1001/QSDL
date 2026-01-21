import textwrap
from pathlib import Path

import pytest

from qsdl.core import generate


def wrapper_generate(test_input: str) -> bool:
    """Runs the void generator.

    Args:
        test_input (str): The QSDL definition.

    Returns:
        dict: The OpenAPI specification as dict.
    """
    test_input = textwrap.dedent(test_input)
    return generate(Path(), generator_name="void", raw_schema=test_input) is None


def wrapper_generate_failure(test_input: str) -> None:
    """Expect the generation to fail.

    Args:
        test_input (str): The QSDL definition.
    """
    test_input = textwrap.dedent(test_input)
    with pytest.raises(Exception):  # noqa: B017
        generate(Path(), generator_name="openapi", raw_schema=test_input)
