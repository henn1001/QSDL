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

    01. When a Object is used as Field value for another Object, a reference by ID is created.

    """

    def test_specifics_01_positive(self):
        """Verify object reference"""
        test_input = """\
            type One {
                id: ID
            }

            type Two {
                id: ID
                one: Two
            }
        """

        wrapper_generate(test_input)

    def test_specifics_01_negative(self):
        """Verify object reference"""
        test_input = """\
            type One {
                id: String
            }

            type Two {
                id: ID
                one: Two
            }
        """

        wrapper_generate_failure(test_input)

        # FIXME: failing
