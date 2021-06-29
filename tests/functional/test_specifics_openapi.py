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

    03. `Directive` @namespace must use `PascalCase`.

    """

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
