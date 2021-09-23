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

import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

from qsdl.core import generate


@pytest.mark.skip(reason="no way of currently testing this")
class TestSpecificsSpring:
    """Test specific functionality.

    01. Test nested Base.

    """

    def test_specifics_01(self):
        """Test nested Base"""
        test_input = """\
            base Bar {
                field1: Int
                field2: Long
                field3: Float
                field4: Double
                field5: String
                field6: Boolean
                field7: Date
                field8: Object
            }

            type Foo {
                field1: String!
                field2: Bar
                field3: [Bar]
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate(test_input, test_output, "spring") == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_02(self):
        """Test nested Object

        TODO:: - Resolve issues with updates/deletion/orphanremoval
        """
        test_input = """\
            type Bar {
                field1: Int
                field2: Long
                field3: Float
                field4: Double
                field5: String
                field6: Boolean
                field7: Date
                field8: Object
            }

            type Foo {
                field1: String!
                field2: Bar
                field3: [Bar]
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate(test_input, test_output, "spring") == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_03(self):
        """Test single Composition

        Note:
        """
        test_input = """\
            type Bar {
                field1: Int
                field2: Long
                field3: Float
                field4: Double
                field5: String
                field6: Boolean
                field7: Date
                field8: Object
            }

            type Foo {
                field1: String!
                field2: Bar @composition
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate(test_input, test_output, "spring") == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0
