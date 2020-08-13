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

"""Some description.

More description.
"""

import sys

from pathlib import Path

from qsdl.core import generate


def entrypoint(input_str: str = None, output: str = None) -> int:
    """This will be our cli interface

    Args:
        input (str): The path to the schema definition file.
        output (str, optional): Path to a output folder.
            Defaults to a srcgen folder at the definition location.

    Returns:
        int: 0 on success, 1 on failure
    """

    input_path = Path(input_str)

    if not input_path.exists():
        print(f"No such file or directory: '{input_path}'")
        sys.exit(1)

    with open(input_path) as file:
        schema = file.read()

    if output:
        output_folder = Path(output)
    else:
        output_folder = input_path.parent / "srcgen"

    sys.exit(generate(schema, output_folder))


if __name__ == "__main__":
    entrypoint("tests/input.tx", output="srcgen/")
