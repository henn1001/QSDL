# Copyright (C) 2022 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from tests import wrapper_generate
from tests import wrapper_generate_failure

import qsdl


class TestMain:
    """Test module main functionality.


    """

    def test_module_call(self):
        """Verify that we can call the module"""

        assert os.system("python -m qsdl examples/openapi/input.qsdl -g openapi -o srcgen/") == 0

        assert os.system("python -m qsdl examples/openapi/input.qsdl -g plantuml -o srcgen/") == 0

        assert os.system("python -m qsdl examples/openapi/input.qsdl -g spring -o srcgen/") == 0

        assert os.system("python -m qsdl examples/openapi/input.qsdl -g void -o srcgen/") == 0

        assert os.system("python -m qsdl examples/multifile/multifile.qsdl -g void -o srcgen/") == 0

        assert os.system("python -m qsdl --help") == 0
