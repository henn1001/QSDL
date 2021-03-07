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

from qsdl import config
from qsdl.generators.generic import get_args
from qsdl.render import render


def oapi_type(scalar) -> str:
    """Maps Scalars to custom types.

    Args:
        input_type (str): The typ to map.

    Returns:
        str: The mapped OpenApi type name or the Scalar name.
    """
    return {
        "Int": "integer",
        "Long": "integer",
        "Float": "number",
        "Double": "number",
        "String": "string",
        "Boolean": "boolean",
        "ID": config.id_type,
        "Date": "string",
        "Object": "object",
    }.get(scalar.name, scalar.name)


def generate():
    """Generator func for OpenAPI"""

    output_file = config.output_path / "openapi.yaml"

    # build the render arguments
    args = get_args()

    render(output_file, args, "openapi.j2", "oapi_type", oapi_type)
