import textwrap
from pathlib import Path

import pytest
import yaml

from qsdl.core import generate


def wrapper_generate(test_input: str) -> dict:
    """Generates and returns the OpenAPI spec as dict.

    Args:
        test_input (str): The QSDL definition.

    Returns:
        dict: The OpenAPI specification as dict.
    """
    test_seed = ""
    test_input = textwrap.dedent(test_input)
    test_output = Path("srcgen/" + test_seed + "/")

    # generate
    assert generate(test_output, generator_name="openapi", raw_schema=test_input) is None

    openapi_file = Path("srcgen/" + test_seed + "/" + "openapi.yaml")

    assert openapi_file.is_file()

    with open(openapi_file, encoding="utf-8") as file:
        openapi = yaml.load(file, Loader=yaml.FullLoader)

    return openapi


def wrapper_generate_failure(test_input: str) -> None:
    """Expect the generation to fail.

    Args:
        test_input (str): The QSDL definition.
    """
    test_seed = ""
    # test_seed = str(uuid.uuid4())[:8] needed when we want to test in parallel
    test_input = textwrap.dedent(test_input)
    test_output = Path("srcgen/" + test_seed + "/")

    # generate
    with pytest.raises(Exception):  # noqa: B017
        generate(test_output, generator_name="openapi", raw_schema=test_input)
