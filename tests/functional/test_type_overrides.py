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

import shutil
import textwrap
from pathlib import Path

from qsdl.core import generate
from tests import wrapper_generate


class TestTypeOverrides:
    """Test type override functionality.

    01. It is not allowed to create the same relation multiple times.

    """

    def test_openapi_scalar_types(self) -> None:
        test_input = """\
            scalar Foo @openapi("aaa")
            scalar Bar @openapi("bbb, format: bla")
            scalar Faa @openapi("ccc, pattern: ^:*$")
            scalar Fuu @openapi("ddd, format: bla, pattern: ^:*$")
            scalar Boo @openapi("eee,    pattern: ^:*$, format: bla")

            type Laa {
                one: Foo
                two: Bar
                three: Faa
                four: Fuu
                five: Boo
            }
        """

        openapi = wrapper_generate(test_input)

        properties = openapi["components"]["schemas"]["Laa"]["properties"]

        for key, value in properties.items():
            if key == "one":
                assert value["type"] == "aaa"
                assert value.get("format") is None
                assert value.get("pattern") is None
            if key == "two":
                assert value["type"] == "bbb"
                assert value.get("format") == "bla"
                assert value.get("pattern") is None
            if key == "three":
                assert value["type"] == "ccc"
                assert value.get("format") is None
                assert value.get("pattern") == "^:*$"
            if key == "four":
                assert value["type"] == "ddd"
                assert value.get("format") == "bla"
                assert value.get("pattern") == "^:*$"
            if key == "five":
                assert value["type"] == "eee"
                assert value.get("format") == "bla"
                assert value.get("pattern") == "^:*$"

    def test_specifics_01(self) -> None:
        """Test nested Base"""

        test_input = """\
            scalar Foo @spring("aaa")
            scalar Bar @spring("bbb, entity: bla")
            scalar Faa @spring("ccc, pattern: ^:*$")
            scalar Fuu @spring("ddd, entity: bla, pattern: ^:*$")
            scalar Boo @spring("eee,    pattern: ^:*$, entity: bla")

            type Laa {
                one: Foo
                two: Bar
                three: Faa
                four: Fuu
                five: Boo
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/tmp")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0
