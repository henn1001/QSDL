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

"""Generator Main entrypoint"""

from pathlib import Path

from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import Schema
from qsdl.writer import DirectoryWriter

from .config import Config


def build_files(schema: Schema, config: Config) -> GeneratedFiles:
    """Build an empty artifact collection."""
    _ = schema
    _ = config
    return GeneratedFiles()


# Temporary compatibility wrapper; remove in Work Package 05.
def generate(schema: Schema, output_path: Path, config: Config) -> None:
    """Generate no files through the legacy filesystem API."""
    DirectoryWriter(output_path).write(build_files(schema, config))
