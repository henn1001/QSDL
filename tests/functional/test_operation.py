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

    01. `Operation` must at least contain one `Field`.

    02. `Operations may be used multiple times for a schema to define custom operations.

    03. `Operation` may be used once inside a `Object` to overwrite the default CRUD operations.

    04. `Operation` must only specify two methods per path (with and without ID). This overlaps with all used paths including `Object`s.

    05. `Operation` names must be globally unique. This overlaps with auto generated CRUD operations for `Object`s.

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
        """Verify operation multiple usage in schema"""
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
        """Verify operation CRUD overwrite"""
        test_input = """\
            type Type {
                id: ID
                name: String

                extend Operation {
                    getTypes: [Type]
                }
            }
        """

        wrapper_generate(test_input)

    def test_operation_03_negative(self):
        """Verify operation CRUD overwrite"""
        test_input = """\
            type Type {
                id: ID
                name: String

                extend Operation {
                    getType: Type
                }

                extend Operation {
                    getTypes: [Type]
                }
            }
        """

        wrapper_generate_failure(test_input)

    def test_operation_04_negative(self):
        """Verify unique paths"""
        inputs = []

        test_input = """\
            extend Operation {
                getObject1: String @path(value:"object")
                getObject2: String @path(value:"object")
            }
        """
        inputs.append(test_input)

        test_input = """\
            type Type {
                id: ID
                name: String
            }

            extend Operation {
                getObject: String @path(value:"type")
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_operation_05_negative(self):
        """Verify unique operation names"""
        inputs = []

        test_input = """\
            extend Operation {
                getObject: String @path(value:"object1")
                getObject: String @path(value:"object2")
            }
        """
        inputs.append(test_input)

        test_input = """\
            type Type {
                id: ID
                name: String
            }

            extend Operation {
                getType: String @path(value:"test")
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)

