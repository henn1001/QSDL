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

import textwrap
import uuid

from pathlib import Path

import yaml
import graphql

from qsdl.core import generate


def wrapper_generate(test_input: str) -> dict:
    """Generates and returns the OpenAPI spec as dict.

    Args:
        test_input (str): The QSDL definition.

    Returns:
        dict: The OpenAPI specification as dict.
    """
    test_seed = ""
    # test_seed = str(uuid.uuid4())[:8] needed when we want to test in parallel
    test_input = textwrap.dedent(test_input)
    test_output = Path("srcgen/" + test_seed + "/")

    # set generator options
    options = {"openapi": True, "graphql": True, "plantuml": False}

    assert generate(test_input, test_output, options) == 0

    openapi_file = Path("srcgen/" + test_seed + "/" + "openapi.yaml")
    graphql_file = Path("srcgen/" + test_seed + "/" + "schema.graphql")

    assert openapi_file.is_file()
    assert graphql_file.is_file()

    with open(openapi_file) as file:
        openapi = yaml.load(file, Loader=yaml.FullLoader)

    with open(graphql_file) as file:
        gql = graphql.build_schema(file.read())

    return openapi


def wrapper_generate_failure(test_input: str):
    """Expect the generation to fail.

    Args:
        test_input (str): The QSDL definition.
    """
    test_seed = ""
    # test_seed = str(uuid.uuid4())[:8] needed when we want to test in parallel
    test_input = textwrap.dedent(test_input)
    test_output = Path("srcgen/" + test_seed + "/")

    # set generator options
    options = {"openapi": True, "graphql": True, "plantuml": False}

    assert generate(test_input, test_output, options) != 0
