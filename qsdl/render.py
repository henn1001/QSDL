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

"""Jinja2 render unit"""

from pathlib import Path

import jinja2

from qsdl.util import pluralize


def render(
    output_file: Path,
    args: dict,
    template_path: Path,
    type_name: str = None,
    type_def: object = None,
):
    """Pass the python object graph to jinja for template rendering.

    Args:
        output_file (Path): The output path.
        args (dict): The python object graph.
        template_path (Path): The path to the j2 template.
        type_name (str, optional): [description]. Defaults to None.
        type_def (object, optional): [description]. Defaults to None.
    """

    # initialize the template engine.
    template_folder = template_path.parent

    loader = jinja2.FileSystemLoader(template_folder)
    jinja_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    # register the filter for mapping Entity type names to type names.
    if type_name and type_def:
        jinja_env.filters[type_name] = type_def

    jinja_env.filters["pluralize"] = pluralize

    # load the template
    template = jinja_env.get_template(template_path.name)

    # testing Area

    # generate folders if needed
    output_file.parent.mkdir(exist_ok=True, parents=True)

    # generate code
    with open(output_file, "w") as file:
        tmp = template.render(args)
        file.write(tmp)
