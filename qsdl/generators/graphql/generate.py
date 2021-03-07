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

from qsdl import config
from qsdl.generators.generic import get_args
from qsdl.render import render


def generate():
    """Generator func for GraphQL"""

    output_file = config.output_path / "schema.graphql"
    template_path = Path(__file__).parent / "template" / "graphql.j2"

    # build the render arguments
    args = get_args()

    render(output_file, args, template_path)
