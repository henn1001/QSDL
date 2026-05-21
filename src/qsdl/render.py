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

"""Jinja2 render unit"""

from pathlib import Path

import jinja2
import pathspec

import qsdl.filter as qfilter
from qsdl import logger

log = logger.getLogger(__name__)

# Module-level cache for ignore specs keyed by output_root path.
_ignore_cache: dict[Path, pathspec.PathSpec | None] = {}


def _load_ignore_spec(output_root: Path) -> pathspec.PathSpec | None:
    """Load the ignore spec for the given output root (cached).

    Looks for `.qignore` first, then falls back to `.qsdl-ignore` for
    backward compatibility.

    Args:
        output_root: The root output directory.

    Returns:
        A compiled PathSpec, or None if no ignore file exists.
    """
    if output_root in _ignore_cache:
        return _ignore_cache[output_root]

    for filename in (".qignore", ".qsdl-ignore"):
        ignore_path = output_root / filename
        if ignore_path.is_file():
            with open(ignore_path, encoding="utf-8") as infile:
                spec = pathspec.PathSpec.from_lines("gitwildmatch", infile)
            _ignore_cache[output_root] = spec
            log.info("loaded ignore file: %s", ignore_path)
            return spec

    _ignore_cache[output_root] = None
    return None


def is_ignored(output_file: Path, output_root: Path) -> bool:
    """Check whether a file should be skipped based on the ignore spec.

    Args:
        output_file: The absolute path of the file to be rendered.
        output_root: The root output directory where the ignore file lives.

    Returns:
        True if the file matches an ignore pattern.
    """
    spec = _load_ignore_spec(output_root)
    if spec is None:
        return False

    # do not overwrite ignore file itself
    if output_file.is_file() and output_file.name in (".qignore", ".qsdl-ignore"):
        return True

    relative = output_file.relative_to(output_root)
    return spec.match_file(str(relative))


def render(  # pylint: disable=too-many-arguments
    output_file: Path,
    context: dict,
    template_path: Path,
    output_root: Path,
    macro_path: Path = None,
    type_name: str = None,
    type_def: object = None,
) -> None:
    """Pass the python object graph to jinja for template rendering.

    Args:
        output_file (Path): The output path.
        context (dict): The context for jinja template.
        template_path (Path): The path to the jinja template.
        output_root (Path): Root output directory for ignore-file resolution.
        macro_path (Path, optional): [description]. Defaults to None.
        type_name (str, optional): [description]. Defaults to None.
        type_def (object, optional): [description]. Defaults to None.
    """
    if is_ignored(output_file, output_root):
        log.info("skipping ignored file: %s", output_file)
        return

    # initialize the template engine.
    loaders = []

    loaders.append(jinja2.FileSystemLoader(template_path.parent))

    if macro_path:
        loaders.append(jinja2.FileSystemLoader(macro_path.parent))

    loader = jinja2.ChoiceLoader(loaders)

    jinja_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    # register the filter for mapping Entity type names to type defs.
    if type_name and type_def:
        jinja_env.filters[type_name] = type_def

    jinja_env.filters["pluralize"] = qfilter.pluralize
    jinja_env.filters["pascal"] = qfilter.pascalcase
    jinja_env.filters["camel"] = qfilter.camelcase
    jinja_env.filters["snake"] = qfilter.snakecase
    jinja_env.filters["spinal"] = qfilter.spinalcase
    jinja_env.filters["capital"] = qfilter.capitalcase
    jinja_env.filters["regex_replace"] = qfilter.regex_replace

    # load the template
    template = jinja_env.get_template(template_path.name)

    # generate folders if needed
    output_file.parent.mkdir(exist_ok=True, parents=True)

    # generate code
    log.info("rendering file: %s", output_file)
    tmp = template.render(context)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(tmp)
