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
from rich.text import Text
from textx.exceptions import TextXSemanticError, TextXSyntaxError

from qsdl import __version__
from qsdl.artifacts import GeneratedFiles
from qsdl.dsl.diagnostics import Diagnostic, SchemaValidationError
from qsdl.dsl.textx import analyze_schema
from qsdl.exceptions import QsdlException
from qsdl.writer import DirectoryWriter

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
config_app = typer.Typer(no_args_is_help=True, help="Inspect and author generator configuration.")
app.add_typer(config_app, name="config")


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
    """Validate QSDL schemas and generate code or specifications."""


def _fail(message: str) -> None:
    Console(stderr=True).print(Text.assemble(("Error: ", "bold red"), message), soft_wrap=True)
    raise typer.Exit(1)


def _write_version_file(output: Path) -> None:
    files = GeneratedFiles()
    files.add_text(".qversion", __version__)
    # A separate writer call intentionally applies the destination ignore policy here too.
    DirectoryWriter(output).write(files)


# fmt: off
GeneratorArg = Annotated[str, typer.Argument(help="Builtin generator name or path to a custom generator (.py file or package dir).")]
InputOpt = Annotated[Path, typer.Option("-i", "--input", help="Schema definition file.")]
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
    from qsdl import plugins
    from qsdl.core import generate

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
    except SchemaValidationError as error:
        _report_diagnostics(error.diagnostics, input_path)
    except (
        QsdlException,
        TextXSemanticError,
        TextXSyntaxError,
        dacite.DaciteError,
        OSError,
        json.JSONDecodeError,
    ) as error:
        _fail(str(error))


@app.command(name="validate")
def validate_cmd(input_path: InputOpt) -> None:
    """Validate a schema and its imports without invoking a generator."""
    _report_diagnostics(analyze_schema(input_path), input_path)


def _report_diagnostics(diagnostics: tuple[Diagnostic, ...], input_path: Path) -> None:
    if not diagnostics:
        return

    console = Console(stderr=True)
    for diagnostic in sorted(
        diagnostics,
        key=lambda d: (str(d.filename or input_path), d.line or 0, d.column or 0, d.code, d.message),
    ):
        location = str(diagnostic.filename or input_path)
        if diagnostic.line is not None:
            location += f":{diagnostic.line}"
            if diagnostic.column is not None:
                location += f":{diagnostic.column}"
        console.print(
            Text.assemble(
                (location, "cyan"),
                ": ",
                (diagnostic.severity, "bold red"),
                " ",
                (f"[{diagnostic.code}]", "yellow"),
                f": {diagnostic.message}",
            ),
            soft_wrap=True,
        )
    raise typer.Exit(1)


@config_app.command("show")
def config_show(generator: GeneratorArg) -> None:
    """Print the default JSON config for GENERATOR."""
    from qsdl import plugins

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
    from qsdl import plugins

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
    from qsdl import plugins
    from qsdl.core import resolve_config

    try:
        name, definition = plugins.resolve(generator)
        resolve_config(definition, config, plugins.parse_set_args(set_ or []))
        Console().print(f"[green]valid[/green] config for {name!r}")
    except (QsdlException, dacite.DaciteError, OSError, json.JSONDecodeError) as error:
        _fail(str(error))


@app.command(name="list")
def list_generators() -> None:
    """List available builtin generators."""
    from qsdl.generators import available_generators

    for name in available_generators():
        print(name)


if __name__ == "__main__":
    app()
