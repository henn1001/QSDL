"""Helpers for direct OpenAPI generator tests."""

import textwrap
from typing import Any

import yaml

from qsdl.core import build


def generate_openapi(test_input: str) -> dict[str, Any]:
    """Build OpenAPI output in memory and return its parsed YAML mapping."""
    files = build(generator_name="openapi", raw_schema=textwrap.dedent(test_input))
    openapi = yaml.safe_load(files.text("openapi.yaml"))

    assert isinstance(openapi, dict), "Expected an OpenAPI mapping"
    return openapi
