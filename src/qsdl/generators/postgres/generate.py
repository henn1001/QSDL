# Copyright 2026 henn1001
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
from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import Schema
from qsdl.render import render_text
from qsdl.writer import DirectoryWriter

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


def build_files(schema: Schema, config: Config) -> GeneratedFiles:
    """Build PostgreSQL artifacts in memory."""

    # save to store
    util.Store.schema = schema
    util.Store.config = config

    template_path = Path(__file__).parent / "template" / "schema.j2"
    tables = parse_models(schema)

    # build the render arguments
    context = {
        "tables": tables,
        "config": config,
    }

    files = GeneratedFiles()
    files.add_text(config.file_name, render_text(template_path, context))
    return files


# Temporary compatibility wrapper; remove in Work Package 05.
def generate(schema: Schema, output_path: Path, config: Config) -> None:
    """Generate PostgreSQL files through the legacy filesystem API."""
    DirectoryWriter(output_path).write(build_files(schema, config))
