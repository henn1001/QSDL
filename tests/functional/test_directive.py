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

    1. `Directive` @query can used on any Base or Object Field to create a query parameter for the get all method. [OpenAPI]

    2. `Directive` @nested

    3. `Directive` @readOnly

    4. `Directive` @writeOnly

    5. `Directive` @composition

    6. `Directive` @aggregation

    7. `Directive` @path(value:"somepath")

    8. `Directive` @post

    9. `Directive` @put

    10. `Directive` @delete

    """
