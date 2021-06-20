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


class TestApi:
    """Test Operations.

    01. `Api` must at least contain one `Operation`.

    02. `Api` may be used multiple times for a schema to define custom operations.

    03. `Api` may be used once inside a `Object` to overwrite the default CRUD operations.

    04. `Api` must only specify two methods per path (with and without ID). This overlaps with all used paths including `Object`s.

    05. `Api` names must be globally unique. This overlaps with auto generated CRUD operations for `Object`s.

    """

    def test_api_01_positive(self):
        """Verify empty Operation"""
        test_input = """\
            extend Api {
                getFoo: Object @path(value:"foo")
            }
        """

        openapi = wrapper_generate(test_input)

        assert "get" in openapi["paths"]["/foo"]
        assert "getFoo" in openapi["paths"]["/foo"]["get"]["operationId"]

    def test_api_01_negative(self):
        """Verify empty Operation"""
        test_input = """\
            extend Api {
            }
        """

        wrapper_generate_failure(test_input)

    def test_api_02_positive(self):
        """Verify Api multiple usage in schema"""
        test_input = """\
            extend Api {
                getFoo: Object @path(value:"foo")
            }

            extend Api {
                getBar: Object @path(value:"bar")
            }

            extend Api {
                getFruit: Object @path(value:"fruit")
            }
        """

        openapi = wrapper_generate(test_input)

        assert "get" in openapi["paths"]["/foo"]
        assert "getFoo" in openapi["paths"]["/foo"]["get"]["operationId"]

        assert "get" in openapi["paths"]["/bar"]
        assert "getBar" in openapi["paths"]["/bar"]["get"]["operationId"]

        assert "get" in openapi["paths"]["/fruit"]
        assert "getFruit" in openapi["paths"]["/fruit"]["get"]["operationId"]

    def test_api_03_positive(self):
        """Verify Api CRUD overwrite"""
        test_input = """\
            type Foo {
                id: ID
                name: String

                extend Api {
                    getFoo: Foo
                }
            }
        """

        openapi = wrapper_generate(test_input)

        assert "get" in openapi["paths"]["/foos"]
        assert "getFoo" in openapi["paths"]["/foos"]["get"]["operationId"]

        assert "post" not in openapi["paths"]["/foos"]
        assert "put" not in openapi["paths"]["/foos"]
        assert "patch" not in openapi["paths"]["/foos"]
        assert "delete" not in openapi["paths"]["/foos"]

    def test_api_03_negative(self):
        """Verify Api CRUD overwrite"""
        test_input = """\
            type Type {
                id: ID
                name: String

                extend Api {
                    getType: Type
                }

                extend Api {
                    getTypes: [Type]
                }
            }
        """

        wrapper_generate_failure(test_input)

    def test_api_04_negative(self):
        """Verify unique paths"""
        inputs = []

        test_input = """\
            extend Api {
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

            extend Api {
                getObject: String @path(value:"types")
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_api_05_negative(self):
        """Verify unique Api names"""
        inputs = []

        test_input = """\
            extend Api {
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

            extend Api {
                getType: String @path(value:"test")
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)
