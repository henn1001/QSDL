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


class TestObject:
    """Test Objects.

    01. `Object` names must use `PascalCase`.

    02. `Object` must at least contain one `Field`.

    03. `Object` can inherit `Field`s from a `Base`.

    04. `Object` name must be unique between `Object`, `Base` and `Scalar`.

    """

    def test_object_01_positive(self):
        """Verify PascalCase naming convention"""
        test_input = """\
            type Foo {
                field: String
            }
        """

        wrapper_generate(test_input)

    def test_object_01_negative(self):
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append("type wrong { field: String } ")
        inputs.append("type Wro-Ng { field: String } ")
        inputs.append("type WRO_NG { field: String } ")

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_object_02_positive(self):
        """Verify empty fields"""
        test_input = """\
            type Foo {
                field: ID
            }
        """

        wrapper_generate(test_input)

    def test_object_02_negative(self):
        """Verify empty fields"""
        test_input = """\
            type Foo {
            }
        """

        wrapper_generate_failure(test_input)

    def test_object_03_positive(self):
        """Verify object implements base"""
        test_input = """\
            base Foo {
                id: ID
            }

            type Bar implements Foo {
                name: String
            }
        """

        openapi = wrapper_generate(test_input)

        ref = openapi["components"]["schemas"]["Bar"]["allOf"][0]
        properties = openapi["components"]["schemas"]["Bar"]["allOf"][1]["properties"]

        assert "Foo" in ref["$ref"]
        assert "name" in properties
