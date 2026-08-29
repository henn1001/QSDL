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

"""Jinja2 rendering helpers."""

from collections.abc import Mapping
from pathlib import Path, PurePosixPath

import jinja2

import qsdl.filter as qfilter
from qsdl.artifacts import GeneratedFiles
from qsdl.writer import DirectoryWriter, IgnorePolicy


def render_text(
    template_path: Path,
    context: Mapping[str, object],
    *,
    macro_path: Path | None = None,
    type_name: str | None = None,
    type_def: object = None,
) -> str:
    """Render a Jinja template to text without performing filesystem output."""
    loaders = [jinja2.FileSystemLoader(template_path.parent)]

    if macro_path is not None:
        loaders.append(jinja2.FileSystemLoader(macro_path.parent))

    loader = jinja2.ChoiceLoader(loaders)
    jinja_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    if type_name is not None and type_def is not None:
        jinja_env.filters[type_name] = type_def

    jinja_env.filters["pluralize"] = qfilter.pluralize
    jinja_env.filters["pascal"] = qfilter.pascalcase
    jinja_env.filters["camel"] = qfilter.camelcase
    jinja_env.filters["snake"] = qfilter.snakecase
    jinja_env.filters["spinal"] = qfilter.spinalcase
    jinja_env.filters["capital"] = qfilter.capitalcase
    jinja_env.filters["regex_replace"] = qfilter.regex_replace

    template = jinja_env.get_template(template_path.name)
    return template.render(context)


def is_ignored(output_file: Path, output_root: Path) -> bool:
    """Check whether a filesystem destination matches the output ignore policy."""
    output_file = Path(output_file)
    output_root = Path(output_root)
    ignore_policy = IgnorePolicy.from_directory(output_root)

    if output_file.is_file() and output_file.name in (".qignore", ".qsdl-ignore"):
        return True

    try:
        relative = output_file.relative_to(output_root)
    except ValueError as exc:
        raise ValueError(f"output file is outside output root: {output_file!s}") from exc

    return ignore_policy.matches(PurePosixPath(relative.as_posix()))


def render(  # pylint: disable=too-many-arguments
    output_file: Path,
    context: dict,
    template_path: Path,
    output_root: Path,
    macro_path: Path | None = None,
    type_name: str | None = None,
    type_def: object = None,
) -> None:
    """Render a template through the compatibility filesystem API."""
    content = render_text(
        template_path,
        context,
        macro_path=macro_path,
        type_name=type_name,
        type_def=type_def,
    )

    try:
        relative_output = Path(output_file).relative_to(Path(output_root))
    except ValueError as exc:
        raise ValueError(f"output file is outside output root: {output_file!s}") from exc

    files = GeneratedFiles()
    files.add_text(PurePosixPath(relative_output.as_posix()), content)
    DirectoryWriter(output_root).write(files)
