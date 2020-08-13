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

"""PlantUML generation"""

from pathlib import Path

import plantuml

from textx.export import PlantUmlRenderer
from textx.export import metamodel_export
from textx.metamodel import TextXMetaModel

from qsdl import __folder__


def draw_metamodel(metamodel: TextXMetaModel):
    """Exports a PlantUml diagram of the metamodel.

    Args:
        metamodel (TextXMetaModel): The metamodel to draw.
    """
    out_path = Path(__folder__) / "definition" / "entity.md"

    metamodel_export(metamodel, out_path, renderer=PlantUmlRenderer())

    with open(out_path, "r+") as file:
        tmp = file.readlines()
        file.seek(0)
        tmp.insert(0, "```plantuml\n")
        tmp.append("```")
        file.writelines(tmp)
        file.truncate()


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
