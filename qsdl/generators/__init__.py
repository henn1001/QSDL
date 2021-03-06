"""QGEN - Generator interface"""

from pathlib import Path
from typing import Any, Callable
from .openapi import Config as openapi_config
from .openapi import generate as openapi_generator
from .graphql import Config as graphql_config
from .graphql import generate as graphql_generator
from .plantuml import Config as plantuml_config
from .plantuml import generate as plantuml_generator


def get_config(generator: str) -> Any:
    """Returns the config for a specific generator"""

    if generator == "openapi":
        return openapi_config()
    if generator == "graphql":
        return graphql_config()
    if generator == "plantuml":
        return plantuml_config()
    else:
        raise Exception("unknown generator")


def get_generator(generator: str) -> Callable[[None], None]:
    """Returns a callable generator for a specific generator"""

    if generator == "openapi":
        return openapi_generator
    if generator == "graphql":
        return graphql_generator
    if generator == "plantuml":
        return plantuml_generator
    else:
        raise Exception("unknown generator")
