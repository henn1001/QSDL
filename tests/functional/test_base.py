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


class TestBase:
    """Test Bases.

    01. `Base` names must use `PascalCase`.

    02. `Base` must at least contain one `Field`.

    03. `Base` may inherit `Field`s from a `Base`.

    04. `Base` name must be unique between `Object`, `Base` and `Scalar`.

    """

    def test_base_01_positive(self):
        """Verify PascalCase naming convention"""
        test_input = """\
            base Base {
                field: ID
            }
        """

        wrapper_generate(test_input)

    def test_base_01_negative(self):
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("base wrong { test: String } ")
        inputs.append("base Wro-Ng { test: String } ")
        inputs.append("base WRO_NG { test: String } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_base_02_positive(self):
        """Verify empty fields"""
        test_input = """\
            base Base {
                field: ID
            }
        """

        wrapper_generate(test_input)

    def test_base_02_negative(self):
        """Verify empty fields"""
        test_input = """\
            base Base {
            }
        """

        wrapper_generate_failure(test_input)

    def test_base_03_positive(self):
        """Verify base implements base"""
        test_input = """\
            base BaseOne {
                id: ID
            }

            base BaseTwo implements BaseOne {
                name: String
            }
        """

        wrapper_generate(test_input)
