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

from tests import wrapper_generate
from tests import wrapper_generate_failure


class TestEnum:
    """Test Enums.

    01. `Enum` names must use `PascalCase`.

    02. `Enum` values must use `ALL_CAPS`.

    03. `Enum` must at least contain one value.

    """

    def test_enum_01_negative(self):
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("enum wrong { OPEN } ")
        inputs.append("enum Wro-Ng { OPEN } ")
        inputs.append("enum WRO_NG { OPEN } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_enum_02_negative(self):
        """Verify value naming convention"""
        inputs = []

        inputs.append("enum Enum { Open } ")
        inputs.append("enum Enum { opEN } ")
        inputs.append("enum Enum { OP-EN } ")
        inputs.append("enum Enum { open } ")
        inputs.append("enum Enum { OPEN } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_enum_03_negative(self):
        """Verify empty enums"""
        test_input = """\
            enum Enum {
            }
        """

        wrapper_generate_failure(test_input)
