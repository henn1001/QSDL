# Copyright (C) 2020 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""QSDL

A Schema-Definition-Language Generator inspired by GraphQL.
"""

import sys
from pathlib import Path

import click

from qsdl import __version__
from qsdl.core import generate


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("-o", "--output_path", help="Path to a output folder. Default: 'srcgren/'", type=click.Path())
@click.option("--openapi/--no-openapi", help="Enables the OpenAPI generator. Default: 'true'", default=True)
@click.option("--graphql/--no-graphql", help="Enables the GraphQL generator. Default: 'true'", default=True)
@click.option("--plantuml", help="Enables the PlantUML generator. Default: 'false'", is_flag=True)
@click.version_option(__version__, prog_name="QSDL")
def entrypoint(
    input_path: str,
    output_path: str = None,
    openapi: bool = True,
    graphql: bool = True,
    plantuml: bool = False,
) -> int:
    """Runs the QSDL generator with the provided schema definition file.

    \b
    Args:
        input_path (str):   The path to the schema definition file.

    \b
    Returns:
        int:                0 on success, 1 on failure
    """
    input_path = Path(input_path)

    with open(input_path) as file:
        schema = file.read()

    if output_path:
        output_folder = Path(output_path)
    else:
        output_folder = input_path.parent / "srcgen"

    # set generator options
    options = {"openapi": openapi, "graphql": graphql, "plantuml": plantuml}

    sys.exit(generate(schema, output_folder, options))


if __name__ == "__main__":
    entrypoint(None)
