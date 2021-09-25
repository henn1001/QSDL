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
import traceback
from pathlib import Path
from typing import Tuple

from dacite import from_dict
from pyfiglet import Figlet
from PyInquirer import prompt
from textx.exceptions import TextXSemanticError, TextXSyntaxError

from qsdl import logger
from qsdl.config import Config
from qsdl.dsl.textx import parse_schema
from qsdl.generators import ConfigType, GeneratorType, get_config, get_generator

log = logger.getLogger(__name__)


class Color:
    """For printing stuff nicer to console"""

    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def prompt_user() -> Tuple[GeneratorType, ConfigType]:
    """Greets and prompts the user with a interactive interface.

    Provides a selectable list of generators and their respective
    configuration.

    Returns:
        Tuple[GeneratorType, ConfigType]: Callable generator func and
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
            "choices": Config.available_generators,
        }
    ]

    answers = prompt(questions)
    generator_name = answers["generator"]

    # get config and callable generator for provided generator
    config = get_config(generator_name)
    generator = get_generator(generator_name)

    # prompt user with available configuration and defaults
    questions = []

    for key, value in config.__dict__.items():
        question = {
            "name": key,
        }

        if isinstance(value, bool):
            question["type"] = "confirm"
            question["message"] = "Please select: " + key
            question["default"] = value
        elif isinstance(value, list):
            question["type"] = "list"
            question["message"] = "Please select: " + key
            question["choices"] = value
            question["default"] = value[0]
        else:
            question["type"] = "input"
            question["message"] = "Please enter: " + key
            question["default"] = value

        questions.append(question)

    answers = prompt(questions)

    # loop over provided answers and update generator paramaters
    for key, value in answers.items():
        config.__setattr__(key, value)

    return generator, config


def init(generator_name: str, config_path: Path = None) -> Tuple[GeneratorType, ConfigType]:
    """Initialise QSDL.

    A user can either utilize a interactive prompt for selecting and
    configuring a generator, or provide this information via flags.

    Args:
        generator_name (str): The requested generator.
        config_path (Path, optional): Path to the config.json. Defaults to None.

    Returns:
        Tuple[GeneratorType, ConfigType]: Callable generator func and
                                  config dataclass.
    """

    # initialise global config
    # important when core.generate is called directly multiple times
    Config.raw_schema = None
    Config.schema = None
    Config.output_path = None
    Config.generator = None
    Config.config = None

    if generator_name:
        # flag mode
        # fetch default config and generator
        config = get_config(generator_name)
        generator = get_generator(generator_name)

        # optionally overwrite the default configuration with user provided data
        if config_path:
            with open(config_path) as json_file:
                data = json.load(json_file)
                config = from_dict(data_class=config.__class__, data=data)
    else:
        # prompt mode
        generator, config = prompt_user()

    log.info("QSDL Generator: %s", generator_name)
    log.info("QSDL Config: %s", config)

    return generator, config


def generate(raw_schema: str, output_path: Path, generator_name: str, config_path: Path = None) -> int:
    """The main function of QSDL.

    Generates various things from the provided schema definition.

    Args:
        raw_schema (str): The schema definition.
        output_path (Path): Path to a output folder.
        generator_name (str, optional): The requested generator.
        config_path (Path, optional): Path to the config.json.

    Returns:
        int: 0 on success, 1 on failure
    """
    try:
        # initiliase the global config and fetch the generator and its parameters
        Config.generator, Config.config = init(generator_name, config_path)

        # build a model from schema definition file
        Config.schema = parse_schema(raw_schema)

        # set global config
        Config.raw_schema = raw_schema
        Config.output_path = output_path

        # create the output folder
        output_path.mkdir(exist_ok=True, parents=True)

        # call generator
        log.info("calling generator")
        Config.generator(Config.schema, Config.output_path, Config.config)  # pylint: disable=not-callable # fmt: skip
        log.info("all done!")

    except (TextXSyntaxError, TextXSemanticError, Exception):  # pylint: disable=W0703
        traceback.print_exc()
        return 1

    return 0
