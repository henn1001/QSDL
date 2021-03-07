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

"""GraphQL Generator"""

from pathlib import Path

from textx import model as mfunc

from qsdl import util
from qsdl.render import render


def generate(model, output_path, parameters):
    """Generator func for GraphQL"""

    output_file = output_path / "schema.graphql"
    template_path = Path(__file__).parent / "template" / "graphql.j2"

    # build the render arguments
    context = {
        "model": model,
        "mfunc": mfunc,
        "util": util,
        "parameters": parameters,
    }

    render(output_file, context, template_path)
