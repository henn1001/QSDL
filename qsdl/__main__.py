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
from qsdl import config
from qsdl.core import generate


@click.command()
# fmt: off
@click.argument("input_path", type=click.Path(exists=True))
@click.option("-g", "--generator", help="The requested generator.", type=click.Choice(config.available_generators))
@click.option("-c", "--config_path", help="Path to a config json file.", type=click.Path(exists=True))
@click.option("-o", "--output_path", help="Path to a output folder. Default: 'srcgren/'", type=click.Path())
@click.version_option(__version__, prog_name="QSDL")
# fmt: on
def entrypoint(input_path: str, generator: str = None, config_path: str = None, output_path: str = None) -> int:
    """Runs the QSDL generator with the provided schema definition file.

    \b
    Args:
        input_path (str):   The path to the schema definition file.

    \b
    Returns:
        int:                0 on success, 1 on failure
    """
    # convert to pathlib
    input_path = Path(input_path)
    config_path = Path(config_path) if config_path else None
    output_path = Path(output_path) if output_path else input_path.parent / "srcgen"

    with open(input_path) as file:
        schema = file.read()

    sys.exit(generate(schema, output_path, generator, config_path))


if __name__ == "__main__":
    entrypoint(None)
