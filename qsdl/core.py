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

"""Core generation"""

from pathlib import Path

import jinja2
from textx import model as mfunc
from textx import metamodel_from_file
from textx.metamodel import TextXMetaModel

from textx.exceptions import TextXSyntaxError
from textx.exceptions import TextXSemanticError

from qsdl import __folder__
from qsdl import domain
from qsdl import util
from qsdl import uml
from qsdl.util import pluralize
from qsdl.util import Scalar
from qsdl.processors.model import model_processor
from qsdl.processors.objects import obj_processors


def get_metamodel(print_uml: bool = False) -> TextXMetaModel:
    """Builds and returns a meta-model for our meta language.

    Args:
        print_uml (bool, optional): Draw a PlantUml diagram of the model.
            Defaults to False.

    Returns:
        TextXMetaModel: The metamodel.
    """

    metamodel = None
    grammar_path = __folder__ / "definition" / "entity.tx"

    type_builtins = {
        "Int": Scalar(None, "Int"),
        "Float": Scalar(None, "Float"),
        "String": Scalar(None, "String"),
        "Boolean": Scalar(None, "Boolean"),
        "ID": Scalar(None, "ID"),
        "Date": Scalar(None, "Date"),
        "Object": Scalar(None, "Object"),
        "Void": Scalar(None, "Void"),
    }

    # parse the grammar file
    metamodel = metamodel_from_file(grammar_path, classes=[Scalar], builtins=type_builtins)

    # register pre-processors
    # these allow us to hook into the model and object creation
    metamodel.register_model_processor(model_processor)
    metamodel.register_obj_processors(obj_processors)

    # export model with plantuml
    if print_uml:
        uml.draw_metamodel(metamodel)

    return metamodel


def render(
    output_file: Path,
    model: object,
    template_name: str,
    type_name: str = None,
    type_def: object = None,
):
    """Pass the python object graph to jinja for template rendering.

    Args:
        output_file (Path): The output path.
        model (object): The python object graph.
        template_name (str): Our internally know template name.
        type_name (str, optional): The name of a callable type conversion function.
            Defaults to None.
        type_def (object, optional): A callable function which accepts the Scalar object.
            Defaults to None.
    """

    # initialize the template engine.
    template_folder = Path(__folder__) / "templates"

    loader = jinja2.FileSystemLoader(template_folder)
    jinja_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    # register the filter for mapping Entity type names to type names.
    if type_name and type_def:
        jinja_env.filters[type_name] = type_def
    jinja_env.filters["pluralize"] = pluralize

    # load the template
    template = jinja_env.get_template(template_name)

    # testing Area

    # generate code
    with open(output_file, "w") as file:
        tmp = template.render(model=model, mfunc=mfunc, util=util)
        file.write(tmp)


def generate_openapi(srcgen_folder: Path, model: object):
    """Generate a OpenAPI spec of the provided schema definition.

    Args:
        srcgen_folder (Path): Path to the output folder.
        model (object): The python object graph.
    """

    def oapi_type(scalar):
        """Maps Scalars to OpenApi types.

        Args:
            scalar (entity.Scalar): The entity Scalar object.

        Returns:
            str: The mapped OpenApi type name or the Scalar name.
        """
        return {
            "Int": "integer",
            "Float": "number",
            "String": "string",
            "Boolean": "boolean",
            "ID": "string",
            "Date": "string",
            "Object": "object",
        }.get(scalar.name, scalar.name)

    output_file = srcgen_folder / "openapi.yaml"

    render(output_file, model, "openapi.j2", "oapi_type", oapi_type)


def generate_graphql(srcgen_folder: Path, model: object):
    """Generate a GraphQL schema from the provided schema definition.

    Args:
        srcgen_folder (Path): Path to the output folder.
        model (object): The python object graph.
    """
    output_file = srcgen_folder / "schema.graphql"

    render(output_file, model, "graphql.j2")


def generate_plantuml(srcgen_folder: Path, model: object):
    """Generate a PlantUml overview of the provided schema definition.

    Args:
        srcgen_folder (Path): Path to the output folder.
        model (object): The python object graph.
    """
    output_file = srcgen_folder / "plantuml.md"

    render(output_file, model, "uml.j2")

    uml.generate_png(output_file)


def generate(schema: str, output_folder: Path) -> int:
    """The main function of QSDL.

    Generates various things from the provided schema definition.

    Args:
        schema (str): The schema definition.
        output_folder (str, optional): Path to a output folder.

    Returns:
        int: 0 on success, 1 on failure
    """
    try:

        # create the output folder
        output_folder.mkdir(exist_ok=True, parents=True)

        # instantiate the Entity meta-model
        metamodel = get_metamodel()

        # build a model from schema definition file
        model = metamodel.model_from_str(schema)

        # init domain model
        domain.build_domain_model(model)

        # call generators
        generate_openapi(output_folder, model)
        generate_graphql(output_folder, model)
        generate_plantuml(output_folder, model)

    except (TextXSyntaxError, TextXSemanticError) as ex:
        print(ex)
        return 1

    return 0
