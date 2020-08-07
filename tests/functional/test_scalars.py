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
from pathlib import Path

import yaml

from qsdl.core import generate


class TestScalarsOpenApi:
    def test_basic(self):
        """Verify that we can use basic types"""

        test_input = """\
            title: "Test API"
            version: "1.0"
            description: "Test"

            servers: ["https://localhost:8080/api/v1"]

            type Scalar {
                id: ID
                int: Int
                float: Float
                string: String
                boolean: Boolean
                date: Date
                object: Object
            }
        """

        test_input = textwrap.dedent(test_input)
        test_input_file = "tests/functional/test_input.tx"

        with open(test_input_file, "w") as file:
            file.write(test_input)

        generate(test_input_file, output_folder="srcgen/")

        openapi_file = Path("srcgen/openapi.yaml")

        assert openapi_file.is_file()

        with open(openapi_file) as file:
            openapi = yaml.load(file, Loader=yaml.FullLoader)

        properties = openapi["components"]["schemas"]["Scalar"]["properties"]

        for key, value in properties.items():
            if key == "id":
                assert value["type"] == "string"
            elif key == "int":
                assert value["type"] == "integer"
                assert value["format"] == "int32"
            elif key == "float":
                assert value["type"] == "number"
                assert value["format"] == "float"
            elif key == "string":
                assert value["type"] == "string"
            elif key == "boolean":
                assert value["type"] == "boolean"
            elif key == "date":
                assert value["type"] == "string"
                assert value["format"] == "date-time"
            elif key == "object":
                assert value["type"] == "object"
            else:
                assert False

    def test_array(self):
        """Verify that we can use array types"""

        test_input = """\
            title: "Test API"
            version: "1.0"
            description: "Test"

            servers: ["https://localhost:8080/api/v1"]

            type Scalar {
                int: [Int]
                float: [Float]
                string: [String]
                boolean: [Boolean]
                date: [Date]
                object: [Object]
            }
        """

        test_input = textwrap.dedent(test_input)
        test_input_file = "tests/functional/test_input.tx"

        with open(test_input_file, "w") as file:
            file.write(test_input)

        generate(test_input_file, output_folder="srcgen/")

        openapi_file = Path("srcgen/openapi.yaml")

        assert openapi_file.is_file()

        with open(openapi_file) as file:
            openapi = yaml.load(file, Loader=yaml.FullLoader)

        properties = openapi["components"]["schemas"]["Scalar"]["properties"]

        for key, value in properties.items():
            if key == "int":
                assert value["type"] == "array"
                assert value["items"]["type"] == "integer"
                assert value["format"] == "int32"
            elif key == "float":
                assert value["type"] == "array"
                assert value["items"]["type"] == "number"
                assert value["format"] == "float"
            elif key == "string":
                assert value["type"] == "array"
                assert value["items"]["type"] == "string"
            elif key == "boolean":
                assert value["type"] == "array"
                assert value["items"]["type"] == "boolean"
            elif key == "date":
                assert value["type"] == "array"
                assert value["items"]["type"] == "string"
                assert value["format"] == "date-time"
            elif key == "object":
                assert value["type"] == "array"
                assert value["items"]["type"] == "object"
            else:
                assert False

    def test_id_array(self):
        """Verify that we can not use array IDs"""

        test_input = """\
            title: "Test API"
            version: "1.0"
            description: "Test"

            servers: ["https://localhost:8080/api/v1"]

            type Scalar {
                id: [ID]
            }
        """

        test_input = textwrap.dedent(test_input)
        test_input_file = "tests/functional/test_input.tx"

        with open(test_input_file, "w") as file:
            file.write(test_input)

        # with pytest.raises(TextXSemanticError):
        assert generate(test_input_file, output_folder="srcgen/") != 0

