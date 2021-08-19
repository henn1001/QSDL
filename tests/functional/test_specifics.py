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

from tests import wrapper_generate, wrapper_generate_failure


class TestSpecifics:
    """Test specific functionality.

    01. It is not allowed to create the same relation multiple times.

    """

    def test_specifics_01_negative(self):
        """Check relation duplicates"""
        inputs = []

        test_input = """\
            type Foo {
                field1: String
            }

            type Bar {
                field2: Foo @composition
                field2: Foo @composition
            }
        """
        inputs.append(test_input)

        test_input = """\
            type Foo {
                field1: String
            }

            type Bar {
                field2: Foo @aggregation
                field2: Foo @aggregation
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)
