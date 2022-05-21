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
            base Fruit {
                field1: String!
            }

            base Bar {
                field1: String!
                field2: Fruit
                field3: [Fruit]
            }

            type Foo {
                field1: String!
                field2: Bar
                field3: [Bar]
                field4: [String]
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_02(self):
        """Test nested Object"""
        test_input = """\
            type Fruit {
                field1: String!
            }

            type Bar {
                field1: String!
                field2: Fruit
                field3: [Fruit]
            }

            type Foo {
                field1: String!
                field2: Bar
                field3: [Bar]
                field4: [String]
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_03(self):
        """Test Composition"""
        test_input = """\
            type Fruit {
                field1: String!
            }

            type Bar {
                field1: String!
                field2: [Fruit] @composition
            }

            type Foo {
                field1: String!
                field2: [Bar] @composition
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_04(self):
        """Test Aggregation"""
        test_input = """\
            type Fruit {
                field1: String!
            }

            type Bar {
                field1: String!
                field2: [Fruit] @aggregation
            }

            type Foo {
                field1: String!
                field2: [Bar] @aggregation
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_05(self):
        """Test Composition with two parents"""
        test_input = """\
            type Fruit {
                field1: String!
            }

            type Bar {
                field1: String!
                field2: [Fruit] @composition
            }

            type Foo {
                field1: String!
                field2: [Fruit] @composition
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_06(self):
        """Test custom operations with composition"""
        test_input = """\
            type Bar {
                field1: String!

                extend Api {
                    createBar(body: Bar): Bar @path(value:"/foos/{foo_id}/bars") @method(value: POST)
                    editBar(body: Bar): Bar @path(value:"/foos/{foo_id}/bars/{id}") @method(value: POST)
                }

            }

            type Foo {
                field1: String!
                field2: [Bar] @composition
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_07(self):
        """Test custom operations with aggregation"""
        test_input = """\
            type Bar {
                field1: String!

                extend Api {
                    createBar(body: Bar): Bar @path(value:"/foos/{foo_id}/bars") @method(value: POST)
                    editBar(body: Bar): Bar @path(value:"/foos/{foo_id}/bars/{id}") @method(value: POST)
                }

            }

            type Foo {
                field1: String!
                field2: [Bar] @aggregation
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_08(self):
        """Test custom operations"""
        test_input = """\

            base Bar {
                field1: String!
            }

            extend Api {
                createBar(body: Bar): Bar @path(value:"/bars") @method(value: POST)
                editBar(body: Bar): Bar @path(value:"/bars/{id}") @method(value: POST)
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    def test_specifics_09(self):
        """Verify usage of relations without parent endpoints"""
        test_input = """\
            type Foo {
                field1: String
            }

            type Bar {
                name: String
                foos: [Foo] @aggregation

                extend Api {    }
            }

            type Fruit  {
                name: String
                foos: [Foo] @composition

                extend Api {    }
            }

        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0
