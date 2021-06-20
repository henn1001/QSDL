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


class TestSpecificsOpenAPI:
    """Test specific OpenAPI functionality.

    01. Referencing a `Object` for a `Field` value requires a `ID`.

    02. Referencing a `Object` for a `Field` value with @composition or @aggregation requires a `ID`.

    03. `Directive` @namespace must use `PascalCase`.

    04. `Field` of `Api` value may be one `Object` or `Base` and can only be mixed with a additional `ID`.

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

    def test_specifics_03_positive(self):
        """Verify PascalCase naming convention"""
        test_input = """\
            type Foo @namespace(value:"Test") {
                field: String
            }
        """

        wrapper_generate(test_input)

    def test_specifics_03_negative(self):
        """Verify PascalCase naming convention"""
        inputs = []

        inputs.append('type Foo @namespace(value:"wrong") { field: String } ')
        inputs.append('type Foo @namespace(value:"Wro-Ng") { field: String } ')
        inputs.append('type Foo @namespace(value:"WRO_NG") { field: String } ')

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_specifics_04_positive(self):
        """Verify object and base usage"""
        test_input = """\
            type Foo {
                field: ID
            }

            base Fruit {
                field: ID
            }

            extend Api {
                field1(body: Foo): Void @path(value:"path1")
                field2(arg: ID, body: Foo): Void @path(value:"path2")
                field3(arg: Fruit): Void @path(value:"path3")
                field4(arg: ID, body: Fruit): Void @path(value:"path4")
            }
        """

        wrapper_generate(test_input)

    def test_specifics_04_negative(self):
        """Verify object and base usage"""
        inputs = []

        test_input = 'base Foo { field: ID } extend Api { field1(arg: String, body: Foo): Void @path(value:"path1") }'
        inputs.append(test_input)

        test_input = 'base Foo { field: ID } extend Api { field1(arg: Foo, body: Foo): Void @path(value:"path1") }'
        inputs.append(test_input)

        test_input = 'type Foo { field: ID } extend Api { field1(arg: String, body: Foo): Void @path(value:"path1") }'
        inputs.append(test_input)

        test_input = 'type Foo { field: ID } extend Api { field1(arg: Foo, body: Foo): Void @path(value:"path1") }'
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)
