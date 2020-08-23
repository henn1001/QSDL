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


class TestOperation:
    """Test Operations.

    01. `Operation`s must at least contain one `Field`.

    02. `Operation`s may be used multiple times for a schema to define custom operations.

    03. `Operation` `Field`s must specify a path with the @path `Directive`.

    04. `Operation` `Field`s may specify one method besides the default get with the @method(value: POST), @method(value: PUT), @method(value: DELETE) `Directive`.

    05. `Operation` `Field`s must only specify two methods per path (with and without ID). This overlaps with all used paths including `Object`s.

    06. `Operation`s may be used once inside a `Object` to overwrite the default CRUD operations.

    07. `Operation` `Field`s may optionally specify a path when used inside `Object`.

    08. `Operation`s may be part of a NameSpace.

    """

    def test_operation_01_positive(self):
        """Verify empty fields"""
        test_input = """\
            extend Operation {
                getObjects: [String] @path(value:"objects")
            }
        """

        wrapper_generate(test_input)

    def test_operation_01_negative(self):
        """Verify empty fields"""
        test_input = """\
            extend Operation {
            }
        """

        wrapper_generate_failure(test_input)

    def test_operation_02_positive(self):
        """Verify PascalCase naming convention"""
        test_input = """\
            extend Operation {
                getObject1: String @path(value:"object1")
            }

            extend Operation {
                getObject2: String @path(value:"object2")
            }

            extend Operation {
                getObject3: String @path(value:"object3")
            }
        """

        wrapper_generate(test_input)

    def test_operation_03_positive(self):
        """Verify empty fields"""
        test_input = """\
            extend Operation {
                getObjects: [String] @path(value:"objects")
            }
        """

        wrapper_generate(test_input)

    def test_operation_03_negative(self):
        """Verify empty fields"""
        test_input = """\
            extend Operation {
                getObjects: [String] @path(value:"objects")
            }
        """

        wrapper_generate_failure(test_input)

    def test_operation_010_positive(self):
        """Verify PascalCase naming convention"""
        test_input = """\
            type Object {
                id: ID
                name: String

                extend Operation {
                    getObjects: [Object]
                }
            }
        """

        wrapper_generate(test_input)
