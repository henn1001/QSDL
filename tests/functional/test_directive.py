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


class TestDirective:
    """Test Directives.

    These directives change the OpenAPI generation.

    01. `Directive` @query may be use on any `Base` or Object` `Field` to create a query parameter for the get all method.

    02. `Directive` @nested may be use on any `Base` or `Object` `Field` when the `Field` value is a `Object`. This creates a nested JSON `Object`.

    03. `Directive` @nested must be use on any `Base` or `Object` `Field` when the `Field` value is a `Base`. This creates a nested JSON `Object`.

    04. `Directive` @readOnly may be use on any `Base` or `Object` `Field` to mark a `Field` as read only.

    05. `Directive` @writeOnly may be use on any `Base` or `Object` `Field` to mark a `Field` as write only.

    06. `Directive` @composition may be used on a `Object` `Field` to create a parent-child relation. The `Field` value must be a `Object`.

    07. `Directive` @aggregation may be used on a `Object` `Field` to create a independent relation. The `Field` value must be a `Object`.

    08. `Directive` @path must be used on any `Operation` `Field` which are not part of a `Object`. This specifies the API Path.

    09. `Directive` @path may be used on any `Operation` `Field` which is part of a `Object`. This specifies the API Path.

    10. `Directive` @method may be used on any `Operation` `Field` to specify the REST Method. Valid values are GET | POST | PUT | DELETE.

    11. `Directive` @namespace may be used on any `Base`, `Operation` or `Object` for grouping.

    """

    def test_directive_01_positive(self):
        """Verify usage of @query"""
        test_input = """\
            base Base {
                id: ID
                name: String @query
            }

            type Type implements Base {
                world: String @query
            }
        """

        wrapper_generate(test_input)

    def test_directive_02_positive(self):
        """Verify usage of @nested"""
        test_input = """\
            base Base {
                id: ID
                field1: Type @nested
            }

            type Type {
                id: ID
                name: String
            }

            type Test implements Base {
                field2: [Type] @nested
            }
        """

        wrapper_generate(test_input)

    def test_directive_03_positive(self):
        """Verify usage of @nested"""
        test_input = """\
            base Base {
                id: ID
                field1: Nested @nested
            }

            base Nested {
                id: ID
                name: String
            }

            type Test implements Base {
                field2: [Nested] @nested
            }
        """

        wrapper_generate(test_input)

    def test_directive_03_negative(self):
        """Verify usage of @nested"""
        test_input = """\
            base Base {
                id: ID
                field1: Nested
            }

            base Nested {
                id: ID
                name: String
            }

            type Test implements Base {
                field2: [Nested]
            }
        """

        wrapper_generate_failure(test_input)

    def test_directive_04_positive(self):
        """Verify usage of @readOnly"""
        test_input = """\
            base Base {
                id: ID
                name: String @readOnly
            }

            type Type implements Base {
                world: String @readOnly
            }
        """

        wrapper_generate(test_input)

    def test_directive_05_positive(self):
        """Verify usage of @writeOnly"""
        test_input = """\
            base Base {
                id: ID
                name: String @writeOnly
            }

            type Type implements Base {
                world: String @writeOnly
            }
        """

        wrapper_generate(test_input)

    def test_directive_06_positive(self):
        """Verify usage of @composition"""
        test_input = """\
            type One {
                field: ID 
                composition: Two @composition
            }

            type Two {
                field: ID 
            }
        """

        wrapper_generate(test_input)

    def test_directive_06_negative(self):
        """Verify usage of @composition"""
        test_input = """\
            type One {
                field: ID 
                composition: String @composition
            }
        """

        wrapper_generate_failure(test_input)

    def test_directive_07_positive(self):
        """Verify usage of @aggregation"""
        test_input = """\
            type One {
                field: ID 
                composition: Two @aggregation
            }

            type Two {
                field: ID 
            }
        """

        wrapper_generate(test_input)

    def test_directive_07_negative(self):
        """Verify usage of @aggregation"""
        test_input = """\
            type One {
                field: ID 
                composition: String @aggregation
            }
        """

        wrapper_generate_failure(test_input)

    def test_directive_08_positive(self):
        """Verify usage of @path"""
        test_input = """\
            extend Operation {
                getObjects: [String] @path(value:"objects")
            }
        """

        wrapper_generate(test_input)

    def test_directive_08_negative(self):
        """Verify usage of @path"""
        test_input = """\
            extend Operation {
                getObjects: [String]
            }
        """

        wrapper_generate_failure(test_input)

    def test_directive_09_positive(self):
        """Verify usage of @path"""
        test_input = """\
            type Type {
                id : ID

                extend Operation {
                    getObjects: [String] @path(value:"objects")
                }
            }


        """

        wrapper_generate(test_input)

    def test_directive_10_positive(self):
        """Verify usage of @method"""
        test_input = """\
            extend Operation {
                field1: Void @path(value:"path") @method(value: GET)
                field2: Void @path(value:"path") @method(value: POST)
                field3: Void @path(value:"path") @method(value: PUT)
                field4: Void @path(value:"path") @method(value: DELETE)
            }
        """

        wrapper_generate(test_input)

    def test_directive_11_positive(self):
        """Verify usage of @namespace"""
        test_input = """\
            base Base @namespace(value:"Test") {
                field : String
            }

            type Type @namespace(value:"Test") {
                field : String
            }

            extend Operation @namespace(value:"Test") {
                field : String @path(value:"path")
            }
        """

        wrapper_generate(test_input)
