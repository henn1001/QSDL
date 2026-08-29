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

"""Generator Main entrypoint"""

from pathlib import Path

import plantuml
import textx.model

from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import Schema
from qsdl.render import render_text

from . import util
from .config import Config


def generate_pngs(markdown: str) -> tuple[bytes, ...]:
    """Convert the PlantUML sections in Markdown into PNG bytes."""
    definitions = []
    linereader = False
    section = ""

    # Keep the existing section extraction semantics while reading Markdown in memory.
    for line in markdown.splitlines(keepends=True):
        if line == "@startuml\n":
            section = ""
            linereader = True

        if line == "@enduml\n":
            definitions.append(section)
            linereader = False

        if linereader:
            section = section + line

    if len(definitions) != 3:
        raise ValueError(f"expected 3 PlantUML definitions, got {len(definitions)}")

    uml = plantuml.PlantUML("http://www.plantuml.com/plantuml/img/")
    return tuple(uml.processes(definition) for definition in definitions)


def generate(schema: Schema, config: Config, output_path: Path | None = None) -> GeneratedFiles:
    """Generate PlantUML Markdown and PNG artifacts in memory."""
    template_path = Path(__file__).parent / "template" / "uml.j2"

    util.schema = schema

    # build the render arguments
    context = {
        "schema": schema,
        "xtx": textx.model,
        "util": util,
        "config": config,
    }

    markdown = render_text(template_path, context)
    files = GeneratedFiles()
    files.add_text("plantuml.md", markdown)

    png_paths = ("plantuml.enums.png", "plantuml.bases.png", "plantuml.overview.png")
    for path, png in zip(png_paths, generate_pngs(markdown), strict=True):
        files.add_bytes(path, png)

    return files
