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


class TestSpecificsOpenAPI:
    """Test specific OpenAPI functionality.

    01. Referencing a `Object` for a `Field` value requires a `ID`.

    02. Referencing a `Object` for a `Field` value with @composition or @aggregation requires a `ID`.

    """

    def test_specifics_01_positive(self):
        """Verify object reference"""
        test_input = """\
            type Foo {
                id: ID
            }

            type Bar {
                id: ID
                field: Foo
            }

            base Fruit {
                id: ID
                field: Foo
            }
        """

        wrapper_generate(test_input)

    def test_specifics_01_negative(self):
        """Verify object reference"""
        inputs = []

        test_input = "type Foo { id: String } type Bar { id: ID field: Foo }"
        inputs.append(test_input)

        test_input = "type Foo { id: String } base Bar { id: ID field: Foo }"
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_specifics_02_negative(self):
        """Verify object reference"""
        inputs = []

        test_input = "base Foo { id: String field: Bar @aggregation } type Bar { id: ID }"
        inputs.append(test_input)

        test_input = "base Foo { id: String field: Bar @composition } type Bar { id: ID }"
        inputs.append(test_input)

        test_input = "type Foo { id: String field: Bar @aggregation } type Bar { id: ID }"
        inputs.append(test_input)

        test_input = "type Foo { id: String field: Bar @composition } type Bar { id: ID }"
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)
