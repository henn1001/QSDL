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

import click

from pathlib import Path

from qsdl.core import generate


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("-o", "--output_path", help="Path to a output folder.", type=click.Path())
def entrypoint(input_path: str, output_path: str = None) -> int:
    """Runs the QSDL generator with the provided schema definition file.

    \b
    Args:
        input_path (str):   The path to the schema definition file.
    \b
        output_path (str):  Path to a output folder. Defaults to a 
                            srcgen folder at the definition location.

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

    sys.exit(generate(schema, output_folder))


if __name__ == "__main__":
    entrypoint(None)
