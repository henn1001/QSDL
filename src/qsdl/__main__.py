# Copyright 2026 henn1001
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

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import dacite
import typer
from rich.console import Console
from rich.json import JSON

from qsdl import __version__, plugins
from qsdl.artifacts import GeneratedFiles
from qsdl.core import generate, resolve_config
from qsdl.exceptions import QsdlException
from qsdl.generators import available_generators
from qsdl.writer import DirectoryWriter

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
config_app = typer.Typer(no_args_is_help=True, help="Inspect and author generator configuration.")
app.add_typer(config_app, name="config")

err = Console(stderr=True)


def version_callback(value: bool) -> None:
    if value:
        print(__version__)
        raise typer.Exit()


@app.callback()
def _root(
    version: Annotated[
        bool, typer.Option("--version", callback=version_callback, is_eager=True, help="Show the version and exit.")
    ] = False,
) -> None:
    """QSDL code/spec generator."""


def _fail(message: str) -> None:
    err.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(1)


def _write_version_file(output: Path) -> None:
    files = GeneratedFiles()
    files.add_text(".qversion", __version__)
    # A separate writer call intentionally applies the destination ignore policy here too.
    DirectoryWriter(output).write(files)


# fmt: off
GeneratorArg = Annotated[str, typer.Argument(help="Builtin generator name or path to a custom generator (.py file or package dir).")]
InputOpt = Annotated[Path, typer.Option("-i", "--input", exists=True, dir_okay=False, readable=True, help="Schema definition file.")]
OutputOpt = Annotated[Path | None, typer.Option("-o", "--output", help="Output folder.")]
ConfigOpt = Annotated[list[Path] | None, typer.Option("-c", "--config", exists=True, dir_okay=False, readable=True, help="JSON config file. Repeatable; later files win. Overridden by --set.")]
SetOpt = Annotated[list[str] | None, typer.Option("-S", "--set", metavar="KEY=VALUE", help="Override one config field. Repeatable; last duplicate wins. Highest precedence.")]
writeOpt = Annotated[bool, typer.Option("--write-version", help="Write a .qversion file.")]
# fmt: on


@app.command(name="generate")
def generate_cmd(
    generator: GeneratorArg,
    input_path: InputOpt,
    output_path: OutputOpt = None,
    config: ConfigOpt = None,
    set_: SetOpt = None,
    write_version: writeOpt = False,
) -> None:
    """Generate output for GENERATOR from a schema."""
    try:
        output = output_path or input_path.parent / "srcgen"
        overrides = plugins.parse_set_args(set_ or [])
        generate(
            output,
            generator_name=generator,
            input_path=input_path,
            config_path=config,
            config=overrides,
        )
        if write_version:
            _write_version_file(output)
    except (QsdlException, dacite.DaciteError, OSError, json.JSONDecodeError) as error:
        _fail(str(error))


@config_app.command("show")
def config_show(generator: GeneratorArg) -> None:
    """Print the default JSON config for GENERATOR."""
    try:
        _, definition = plugins.resolve(generator)
        Console().print(JSON.from_data(asdict(definition.config_class())))
    except (QsdlException, dacite.DaciteError) as error:
        _fail(str(error))


@config_app.command("init")
def config_init(
    generator: GeneratorArg,
    output_path: Annotated[Path | None, typer.Option("-o", "--output", help="Config file to write.")] = None,
) -> None:
    """Write the default JSON config for GENERATOR to a file."""
    try:
        name, definition = plugins.resolve(generator)
        output = output_path or Path(f"{name}.json")
        output.write_text(json.dumps(asdict(definition.config_class()), indent=2) + "\n", encoding="utf-8")
    except (QsdlException, dacite.DaciteError, OSError) as error:
        _fail(str(error))


@config_app.command("validate")
def config_validate(
    generator: GeneratorArg,
    config: ConfigOpt = None,
    set_: SetOpt = None,
) -> None:
    """Validate config files and --set overrides against GENERATOR."""
    try:
        name, definition = plugins.resolve(generator)
        resolve_config(definition, config, plugins.parse_set_args(set_ or []))
        Console().print(f"[green]valid[/green] config for {name!r}")
    except (QsdlException, dacite.DaciteError, OSError, json.JSONDecodeError) as error:
        _fail(str(error))


@app.command(name="list")
def list_generators() -> None:
    """List available builtin generators."""
    for name in available_generators():
        print(name)


if __name__ == "__main__":
    app()
