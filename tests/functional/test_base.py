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

from . import wrapper_generate
from . import wrapper_generate_failure


class Testbase:
    """Test Bases.

    1. `Base` names should use `PascalCase`.

    2. `Base` should at least contain one value.

    3. `Base` can be used as `Field` value for `Object`s when marked as `@nested`.

    4. `Base` can be used as `Field` value for `Operations`.

    5. `Base` can be used as `Argument` value for `Operations`.

    6. `Base` can be used as a superType by `Base`s.

    7. `Base` can be used as a superType by `Object`s.

    """

    def test_base_1_positive(self):
        """Verify PascalCase naming convention"""
        test_input = """\
            base Base {
                field: ID
            }
        """

        wrapper_generate(test_input)

    def test_base_1_negative(self):
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("base wrong { test: String } ")
        inputs.append("base Wro-Ng { test: String } ")
        inputs.append("base WRO_NG { test: String } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_base_2_positive(self):
        """Verify empty bases"""
        test_input = """\
            base Base {
                field: ID
            }
        """

        wrapper_generate(test_input)

    def test_base_2_negative(self):
        """Verify empty bases"""
        test_input = """\
            base Base {
            }
        """

        wrapper_generate_failure(test_input)

    def test_base_3_positive(self):
        """Verify nested bases"""
        test_input = """\
            base Base {
                field: ID
            }

            type Object {
                field: Base @nested
            }
        """

        wrapper_generate(test_input)

    def test_base_3_negative(self):
        """Verify nested bases"""
        test_input = """\
            base Base {
                field: ID
            }

            type Object {
                field: Base
            }
        """

        wrapper_generate_failure(test_input)

    def test_base_4_positive(self):
        """Verify base as operations response"""
        test_input = """\
            base Base {
                field: ID
            }

            extend Operation {
                field: Base @path(value="test")
            }
        """

        wrapper_generate(test_input)

    def test_base_5_positive(self):
        """Verify base as argument value"""
        test_input = """\
            base Base {
                field: ID
            }

            extend Operation {
                field(arg: Base): Void @path(value="test")
            }
        """

        wrapper_generate(test_input)

    def test_base_6_positive(self):
        """Verify base implenets base"""
        test_input = """\
            base BaseOne {
                id: ID
            }

            base BaseTwo implements BaseOne {
                name: String
            }
        """

        wrapper_generate(test_input)

    def test_base_7_positive(self):
        """Verify object implements base"""
        test_input = """\
            base Base {
                id: ID
            }

            type Object implements Base {
                name: String
            }
        """

        wrapper_generate(test_input)
