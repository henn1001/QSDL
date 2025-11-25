# Copyright 2025 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""QSDL

A Schema-Definition-Language Generator inspired by GraphQL.
"""

from pathlib import Path
from typing import Annotated

import typer

from qsdl import __version__
from qsdl.core import generate

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


def version_callback(value: bool) -> None:
    if value:
        print(__version__)
        raise typer.Exit()


h_input_path = "The path to the schema definition file."
h_generator = "The requested generator."
h_config_path = "Path to a config json file."
h_output_path = "Path to a output folder. Default: 'srcgen/'"
h_print_version = "Prints a .qversion file to the output folder."


@app.command()
def entrypoint(
    input_path: Annotated[Path, typer.Argument(..., help=h_input_path, exists=True)],
    generator: Annotated[str | None, typer.Option("-g", "--generator", help=h_generator)] = None,
    config_path: Annotated[Path | None, typer.Option("-c", "--config_path", help=h_config_path, exists=True)] = None,
    output_path: Annotated[Path | None, typer.Option("-o", "--output_path", help=h_output_path)] = None,
    print_version: Annotated[bool, typer.Option("-pv", "--print_version", help=h_print_version)] = False,
    version: Annotated[bool, typer.Option("--version", callback=version_callback, is_eager=True)] = False,
) -> None:
    # set default output path if not provided
    output_path = output_path or input_path.parent / "srcgen"

    # print version
    if print_version:
        with open(output_path / ".qversion", "w", encoding="utf-8") as file:
            file.write(__version__)

    generate(output_path, generator_name=generator, input_path=input_path, config_path=config_path)


if __name__ == "__main__":
    app()
