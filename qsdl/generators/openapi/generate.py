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

"""OpenAPI Generator"""

from pathlib import Path

from textx import model as mfunc

from qsdl import util
from qsdl.render import render

custom_types = {
    "Int": "integer",
    "Long": "integer",
    "Float": "number",
    "Double": "number",
    "String": "string",
    "Boolean": "boolean",
    "ID": "integer",
    "Date": "string",
    "Object": "object",
}


def oapi_type(scalar) -> str:
    """Maps Scalars to custom types.

    Args:
        input_type (str): The typ to map.

    Returns:
        str: The mapped OpenApi type name or the Scalar name.
    """
    return custom_types.get(scalar.name, scalar.name)


def generate(model, output_path, parameters):
    """Generator func for OpenAPI"""

    if parameters.id_type not in ["integer", "string"]:
        raise ValueError("id_type must be `integer` or `string`")

    # sets the id type
    custom_types["ID"] = parameters.id_type

    output_file = output_path / "openapi.yaml"
    template_path = Path(__file__).parent / "template" / "openapi.j2"

    # build the render arguments
    context = {
        "model": model,
        "mfunc": mfunc,
        "util": util,
        "parameters": parameters,
    }

    render(output_file, context, template_path, "oapi_type", oapi_type)
