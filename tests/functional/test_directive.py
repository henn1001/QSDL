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

    1. `Directive` @query may be use on any Base or Object Field to create a query parameter for the get all method.

    2. `Directive` @nested may be use on any Base or Object Field when the Field value is a Object. This creates a nested JSON Object.

    3. `Directive` @nested must be use on any Base or Object Field when the Field value is a Base. This creates a nested JSON Object.

    3. `Directive` @readOnly may be use on any Base or Object Field to mark a field as read only.

    4. `Directive` @writeOnly may be use on any Base or Object Field to mark a field as write only.

    5. `Directive` @composition

    6. `Directive` @aggregation

    7. `Directive` @path must be used on any Operation Field which are not part of a Object. This specifies the API Path.

    7. `Directive` @path may be used on any Operation Field which is part of a Object. This specifies the API Path.

    8. `Directive` @method

    """
