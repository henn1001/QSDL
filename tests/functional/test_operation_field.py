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


class TestOperationField:
    """Test Fields for Operations.

    1. `Field` of `Operation` can be a `Scalar` value with one one of the following:
        * `ID`
        * `Int`
        * `Float`
        * `String`
        * `Boolean`
        * `Date`
        * `Object`
        * `Void`

    2. `Field` of `Operation` value can be a `Enum`.

    3. `Field` of `Operation` value can be a `Base`.

    4. `Field` of `Operation` value can be a `Object`.

    5. `Field` of `Operation` value can be a list when enclosed with brackets.

    6. `Field` of `Operation` value can not be a list for `Scalar` `ID`.

    7. `Field` of `Operation` value and list value can be marked as mandatory.

    """

    def test_field_operation_3_positive(self):
        """Verify base as operations response"""
        test_input = """\
            base Base {
                field: ID
            }

            extend Operation {
                field: Base @path(value:"test")
            }
        """

        wrapper_generate(test_input)

    def test_field_operation_6_negative(self):
        """Verify that we can not use array IDs"""

        test_input = """\
            extend Operation {
                field: [ID] @path(value:"path")
            }
        """

        wrapper_generate_failure(test_input)
