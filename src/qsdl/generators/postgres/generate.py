# Copyright 2025 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generator"""

from pathlib import Path

import qsdl.dsl.textx as xtx
from qsdl.dsl import Schema
from qsdl.render import render

from . import util
from .config import Config
from .models import Table


def parse_models(schema: Schema) -> list[Table]:
    """Parse QSDL schema into custom models.

    Args:
        schema (Schema): The QSDL schema model.
    Returns:
        list[Table]: The parsed models.
    """
    models = []

    obj_list = xtx.get_children_of_object(schema)
    # NOTE: With new semantics, Base types are NEVER separate tables
    # They are either flattened (default) or stored as JSONB (@opaque)
    # Only Object types get their own tables

    for obj in obj_list:
        new_model = Table.from_ref(obj)
        models.append(new_model)

        # Handle composition relationships: add foreign keys for parent references
        util.build_composition_fks(new_model)

        # Handle aggregation relationships: - creates join tables for many-to-many
        jointables = util.build_jointables(new_model)
        models.extend(jointables)

    return models


def generate(schema: Schema, output_path: Path, config: Config) -> None:
    """Generator func for that does nothing"""

    output_file = output_path / config.file_name
    template_path = Path(__file__).parent / "template" / "schema.j2"

    # save to store
    util.Store.schema = schema
    util.Store.config = config

    tables = parse_models(schema)

    # build the render arguments
    context = {
        "tables": tables,
        "config": config,
    }

    render(output_file, context, template_path)
