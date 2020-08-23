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


class TestArgument:
    """Test Arguments.

    1. `Argument` names must use `TBD`.

    2. `Argument` must contain at least one name/value pair.

    3. `Argument` value must be one of the following
        * `Scalar`
        * `Enum`
        * `Base`
        * `Object`

    4. `Argument` may contain a maximum of one `Scalar` value of `ID`.

    5. `Argument` value may be a list when enclosed with brackets.

    6. `Argument` value and list value may be marked as mandatory.

    7. `Argument` name/value pairs for get methods are query parameters. [OpenAPI]

    8. `Argument` name/value pairs for post/put methods are requestBody. [OpenAPI]

    9. `Argument` value must be a `Scalar` of `ID` for delete method. [OpenAPI]

    10. `Argument` must be used by `Field` of `Operation` only.

    """

    def test_argument_1_positive(self):
        """Verify TBD naming convention"""
        test_input = """\
            extend Operation {
                field(arg: String): Void @path(value:"path")
            }
        """

        wrapper_generate(test_input)

    def test_argument_1_negative(self):
        """Verify TBD naming convention"""
        inputs = []

        inputs.append('extend Operation { field(a-a: String): Void @path(value:"path") } ')

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_argument_2_positive(self):
        """Verify empty arguments"""
        test_input = """\
            extend Operation {
                field(arg: String): Void @path(value:"path")
            }
        """

        wrapper_generate(test_input)

    def test_argument_2_negative(self):
        """Verify empty arguments"""
        test_input = """\
            extend Operation {
            }
        """

        wrapper_generate_failure(test_input)

    def test_argument_3_positive(self):
        """Verify  argument value types"""
        test_input = """\
            base Base {
                field: ID
            }

            enum Enum {
                OPEN
                CLOSED
            }

            type Object {
                field: String
            }

            extend Operation {
                field1(arg: String): Void @path(value:"path1")
                field2(arg: Enum): Enum @path(value:"path2")
                field3(arg: Base): Void @path(value:"path3")
                field4(arg: Object): Void @path(value:"path4")
            }
        """

        wrapper_generate(test_input)

    def test_argument_3_negative(self):
        """Verify  argument value types"""
        test_input = """\

            extend Operation {
                field1(arg: String): Void @path(value:"path1")
                field2(arg: field1): Void @path(value:"path2")
            }
        """

        wrapper_generate_failure(test_input)

    def test_argument_4_positive(self):
        """Verify multiple IDs"""
        test_input = """\
            extend Operation {
                field(arg: ID): Void @path(value:"path")
            }
        """

        wrapper_generate(test_input)

    def test_argument_4_negative(self):
        """Verify multiple IDs"""
        test_input = """\
            extend Operation {
                field(arg1: ID, arg2: ID): Void @path(value:"path")
            }
        """

        wrapper_generate_failure(test_input)

    def test_argument_5_positive(self):
        """Verify value list"""
        test_input = """\
            extend Operation {
                field1(arg: [String]): Void @path(value:"path1")
                field2(arg: [String]): Void @path(value:"path2") @post
            }
        """

        wrapper_generate(test_input)

        # TODO: verify openAPI
        assert False

    def test_argument_6_positive(self):
        """Verify required"""
        test_input = """\
            extend Operation {
                field1(arg: String!): Void @path(value:"path1")
                field2(arg: [String]!): Void @path(value:"path2")
                field3(arg: [String!]!): Void @path(value:"path3")

                field4(arg: String!): Void @path(value:"path4") @post
                field5(arg: [String]!): Void @path(value:"path5") @post
                field6(arg: [String!]!): Void @path(value:"path6") @post
            }
        """

        wrapper_generate(test_input)

        # TODO: verify openAPI
        assert False

    def test_argument_7_positive(self):
        """Verify argument is query for get"""
        test_input = """\
            extend Operation {
                field(arg: String): Void @path(value:"path")
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/path"]["get"]["parameters"][0]["in"] == "query"

    def test_argument_8_positive(self):
        """Verify argument is requestbody for post/put"""
        test_input = """\
            extend Operation {
                field1(arg: String): Void @path(value:"path") @post
                field2(arg: String): Void @path(value:"path") @put
            }
        """

        openapi = wrapper_generate(test_input)

        assert openapi["paths"]["/path"]["post"]["requestBody"]["content"]

        assert openapi["paths"]["/path"]["put"]["requestBody"]["content"]

    def test_argument_9_positive(self):
        """Verify argument is only of ID for delete"""
        test_input = """\
            extend Operation {
                field1(arg: ID): Void @path(value:"path") @delete
            }
        """

        wrapper_generate(test_input)

    def test_argument_9_negative(self):
        """Verify argument is only of ID for delete"""
        test_input = """\
            extend Operation {
                field1(arg: String): Void @path(value:"path") @delete
            }
        """

        wrapper_generate_failure(test_input)

    def test_argument_10_negative(self):
        """Verify argument is only used in operations"""
        inputs = []

        # inputs.append("base Base { field(arg: String): String }")
        inputs.append("type Object { field(arg: String): String }")

        for test_input in inputs:
            wrapper_generate_failure(test_input)
