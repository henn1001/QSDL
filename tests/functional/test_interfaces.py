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


class TestInterface:
    """Test Interfaces.

    1. `Interface` names should use `PascalCase`.

    2. `Interface` should at least contain one value.

    3. `Interface` can be used as `Field` value for `Object`s when marked as `@nested`.

    4. `Interface` can be used as `Field` value for `Operations`.

    5. `Interface` can be used as `Argument` value for `Operations`.

    6. `Interface` can be used as a superType by `Interface`s.

    7. `Interface` can be used as a superType by `Object`s.

    """

    def test_interface_1_positive(self):
        """Verify PascalCase naming convention"""
        test_input = """\
            interface Interface {
                field: ID
            }
        """

        wrapper_generate(test_input)

    def test_interface_1_negative(self):
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("interface wrong { test: String } ")
        inputs.append("interface Wro-Ng { test: String } ")
        inputs.append("interface WRO_NG { test: String } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_interface_2_positive(self):
        """Verify empty interfaces"""
        test_input = """\
            interface Interface {
                field: ID
            }
        """

        wrapper_generate(test_input)

    def test_interface_2_negative(self):
        """Verify empty interfaces"""
        test_input = """\
            interface Interface {
            }
        """

        wrapper_generate_failure(test_input)

    def test_interface_3_positive(self):
        """Verify nested interfaces"""
        test_input = """\
            interface Interface {
                field: ID
            }

            type Object {
                field: Interface @nested
            }
        """

        wrapper_generate(test_input)

    def test_interface_3_negative(self):
        """Verify nested interfaces"""
        test_input = """\
            interface Interface {
                field: ID
            }

            type Object {
                field: Interface
            }
        """

        wrapper_generate_failure(test_input)

    def test_interface_4_positive(self):
        """Verify interface as operations response"""
        test_input = """\
            interface Interface {
                field: ID
            }

            type Query {
                field: Interface @path(value="test")
            }
        """

        wrapper_generate(test_input)

    def test_interface_5_positive(self):
        """Verify interface as argument value"""
        test_input = """\
            interface Interface {
                field: ID
            }

            type Query {
                field(arg: Interface): Void @path(value="test")
            }
        """

        wrapper_generate(test_input)

    def test_interface_6_positive(self):
        """Verify interface implenets interface"""
        test_input = """\
            interface InterfaceOne {
                id: ID
            }

            interface InterfaceTwo implements InterfaceOne {
                name: String
            }
        """

        wrapper_generate(test_input)

    def test_interface_7_positive(self):
        """Verify object implements interface"""
        test_input = """\
            interface Interface {
                id: ID
            }

            type Object implements Interface {
                name: String
            }
        """

        wrapper_generate(test_input)
