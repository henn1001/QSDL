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

import json
from pathlib import Path
from typing import Tuple

from dacite import from_dict
from pyfiglet import Figlet
from PyInquirer import prompt
from textx.exceptions import TextXSemanticError, TextXSyntaxError

from qsdl import __folder__, config
from qsdl.generators import get_config, get_generator
from qsdl.model import Color
from qsdl.parse import parse_domain_model, parse_schema


def prompt_user() -> Tuple:
    """Greets and prompts the user with a interactive interface.

    Provides a selectable list of generators and their respective
    configuration.

    Returns:
        Tuple[generator, config]: Callable generator func and
                                  config dataclass.
    """
    # provide greeting message
    figlet = Figlet(font="speed")

    print(Color.BOLD)
    print(figlet.renderText("QSDL"))
    print("! Would you like a cup of tea with that?")
    print(Color.END)

    # prompt user with available generators
    questions = [
        {
            "type": "list",
            "name": "generator",
            "message": "Which generator do you want to use?",
            "choices": config.generators,
        }
    ]

    answers = prompt(questions)
    generator_name = answers["generator"]

    # get config and callable generator for provided generator
    generator = get_generator(generator_name)
    gen_config = get_config(generator_name)

    # prompt user with available configuration and defaults
    questions = []

    for key, value in gen_config.__dict__.items():
        question = {
            "type": "input",
            "name": key,
            "message": "Please enter: " + key,
            "default": value,
        }
        questions.append(question)

    answers = prompt(questions)

    # loop over provided answers and update configuration
    for key, value in answers.items():
        gen_config.__setattr__(key, value)

    return generator, gen_config


def init(generator_name: str, config_path: Path = None) -> Tuple:
    """Initialise QSDL.

    A user can either utilize a interactive prompt for selecting and
    configuring a generator, or provide this information via flags.

    Args:
        generator_name (str): The requested generator.
        config_path (str, optional): Path to the config.json. Defaults to None.

    Returns:
        Tuple[generator, config]: Callable generator func and
                                  config dataclass.
    """
    if generator_name:
        # flag mode
        # fetch default config and generator
        gen_config = get_config(generator_name)
        generator = get_generator(generator_name)

        # optionally overwrite the default config with user provided data
        if config_path:
            with open(config_path) as json_file:
                data = json.load(json_file)
                gen_config = from_dict(data_class=gen_config.__class__, data=data)
    else:
        # prompt mode
        generator, gen_config = prompt_user()

    return generator, gen_config


def generate(
    schema: str, output_path: Path, generator_name: str, config_path: Path = None
) -> int:
    """The main function of QSDL.

    Generates various things from the provided schema definition.

    Args:
        schema (str): The schema definition.
        output_path (Path): Path to a output folder.
        generator_name (str, optional): The requested generator.
        config_path (Path, optional): Path to the config.json.

    Returns:
        int: 0 on success, 1 on failure
    """
    try:

        # initialise
        # fetch the generator and configuration
        generator, gen_config = init(generator_name, config_path)

        # build a model from schema definition file
        model = parse_schema(schema)

        # init domain model
        domain_objects, operations = parse_domain_model(model)

        # set global config
        config.output_path = output_path
        config.gen_config = gen_config

        # create the output folder
        output_path.mkdir(exist_ok=True, parents=True)

        # call generator
        generator()

    except (TextXSyntaxError, TextXSemanticError) as ex:
        print(ex)
        return 1

    return 0
