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

"""PlantUML Generator"""

from pathlib import Path

import plantuml
from textx import model as xtx

from qsdl.dsl.models import Schema
from qsdl.render import render

from . import util
from .config import Config


def generate_png(uml_markdown_file: Path):
    """Converts a markdown file containing PlantUml definitions to pngs.

    Args:
        uml_markdown_file (Path): The path to a markdown file.
    """
    uml = plantuml.PlantUML("http://www.plantuml.com/plantuml/img/")

    # loop over markdown file and capture each start/end uml section
    definitions = []

    with open(uml_markdown_file, "r") as file:
        linereader = False
        section = ""

        for line in file:

            if line == "@startuml\n":
                section = ""
                linereader = True

            if line == "@enduml\n":
                definitions.append(section)
                linereader = False

            if linereader:
                section = section + line

    # these are our expected sections
    enums = uml_markdown_file.parent / (uml_markdown_file.stem + ".enums.png")
    bases = uml_markdown_file.parent / (uml_markdown_file.stem + ".bases.png")
    overview = uml_markdown_file.parent / (uml_markdown_file.stem + ".overview.png")

    files = [enums, bases, overview]

    # create the pngs and save them along the markdown file
    for definition in definitions:
        png = uml.processes(definition)

        png_file_name = files.pop(0)

        with open(png_file_name, "wb") as the_file:
            the_file.write(png)


def generate(schema: Schema, output_path: Path, config: Config):
    """Generator func for PlantUML"""

    output_file = output_path / "plantuml.md"
    template_path = Path(__file__).parent / "template" / "uml.j2"

    util.schema = schema

    # build the render arguments
    context = {
        "schema": schema,
        "xtx": xtx,
        "util": util,
        "config": config,
    }

    render(output_file, context, template_path)

    generate_png(output_file)
