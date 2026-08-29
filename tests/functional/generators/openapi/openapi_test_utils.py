"""Helpers for direct OpenAPI generator tests."""

import textwrap
from pathlib import Path
from typing import Any

import yaml

from qsdl.core import generate


def generate_openapi(test_input: str, output_path: Path) -> dict[str, Any]:
    """Generate OpenAPI output in a caller-provided temporary directory.

    Tests should pass pytest's ``tmp_path`` fixture (or another temporary
    directory) as ``output_path``.  The generated YAML is loaded and returned
    so direct OpenAPI tests do not depend on the repository's ``srcgen/``
    directory.
    """
    test_input = textwrap.dedent(test_input)
    assert generate(output_path, generator_name="openapi", raw_schema=test_input) is None
    return load_openapi(output_path)


def load_openapi(output_path: Path) -> dict[str, Any]:
    """Load the generated OpenAPI YAML from ``output_path``."""
    openapi_file = output_path / "openapi.yaml"
    assert openapi_file.is_file(), f"Expected OpenAPI file not found: {openapi_file}"

    with openapi_file.open(encoding="utf-8") as file:
        openapi = yaml.safe_load(file)

    assert isinstance(openapi, dict), f"Expected an OpenAPI mapping in {openapi_file}"
    return openapi
