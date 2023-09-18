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

import json
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

    @pytest.mark.order(1)
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
                field5: Bar
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(2)
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
                field5: Bar
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(3)
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

    @pytest.mark.order(4)
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

    @pytest.mark.order(5)
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

    @pytest.mark.order(6)
    def test_specifics_06(self):
        """Test custom operations with composition"""
        test_input = """\
            type Bar {
                field1: String!

                extend api {
                    createBar(body: Bar): Bar @path("/foos/{foo_id}/bars") @method(POST)
                    editBar(body: Bar): Bar @path("/foos/{foo_id}/bars/{id}") @method(POST)
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

    @pytest.mark.order(7)
    def test_specifics_07(self):
        """Test custom operations with aggregation"""
        test_input = """\
            type Bar {
                field1: String!

                extend api {
                    createBar(body: Bar): Bar @path("/foos/{foo_id}/bars") @method(POST)
                    editBar(body: Bar): Bar @path("/foos/{foo_id}/bars/{id}") @method(POST)
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

    @pytest.mark.order(8)
    def test_specifics_08(self):
        """Test custom operations"""
        test_input = """\

            base Bar {
                field1: String!
            }

            extend api {
                createBar(body: Bar): Bar @path("/bars") @method(POST)
                editBar(body: Bar): Bar @path("/bars/{id}") @method(POST)
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(9)
    def test_specifics_09(self):
        """Verify usage of relations without parent endpoints"""
        test_input = """\
            type Foo {
                field1: String
            }

            type Bar {
                name: String
                foos: [Foo] @aggregation

                extend api {    }
            }

            type Fruit  {
                name: String
                foos: [Foo] @composition

                extend api {    }
            }

        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(10)
    def test_specifics_10(self):
        """Verify usage of folder layout config"""

        test_input = Path("util/examples/input.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)
        test_output.mkdir()

        config = {
            "base_package": "com.supertest",
            "api_path": "com.supertest.generated.iface",
            "config_path": "com.supertest.shared.config",
            "controller_path": "com.supertest.generated.api",
            "domain_path": "com.supertest.generated.object",
            "enum_path": "com.supertest.generated.constants",
            "exception_path": "com.supertest.shared.exceptions",
            "model_path": "com.supertest.shared.models",
            "repository_path": "com.supertest.generated.repositorys",
            "service_path": "com.supertest.generated.service",
            "util_path": "com.supertest.shared.utils",
        }

        # generate
        assert generate("spring", test_output, input_path=test_input, config=config) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(11)
    def test_specifics_11(self):
        """Verify usage of generate and controller directive"""
        test_input = """\
            extend api @controller("Buzzword") {
                submitQury(arg1: String, arg2: [Int]): Object @path("query") @method(PATCH)
            }

            type Buzzword @namespace("Incident"){
                name: String!
                extend api @generate("UPDATE") {}
            }

        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        # generate
        assert generate("spring", test_output, raw_schema=test_input) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(12)
    def test_specifics_12(self):
        """Verify usage of string identifier"""

        test_input = Path("util/examples/input.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)
        test_output.mkdir()

        config = {
            "id_type": "STRING",
        }

        # generate
        assert generate("spring", test_output, input_path=test_input, config=config) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(13)
    def test_specifics_13(self):
        """Verify usage of encapsulation"""

        test_input = Path("util/examples/input.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)
        test_output.mkdir()

        config = {
            "encapsulation": True,
        }

        # generate
        assert generate("spring", test_output, input_path=test_input, config=config) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(14)
    def test_specifics_14(self):
        """Verify usage of no database"""

        test_input = Path("util/examples/input.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)
        test_output.mkdir()

        config = {
            "database": "NO",
        }

        # generate
        assert generate("spring", test_output, input_path=test_input, config=config) == 0

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0
