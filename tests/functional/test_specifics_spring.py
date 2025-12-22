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
    def test_specifics_01(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(2)
    def test_specifics_02(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(3)
    def test_specifics_03(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(4)
    def test_specifics_04(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(5)
    def test_specifics_05(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(6)
    def test_specifics_06(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(7)
    def test_specifics_07(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(8)
    def test_specifics_08(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(9)
    def test_specifics_09(self) -> None:
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

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(10)
    def test_specifics_10(self) -> None:
        """Verify usage of folder layout config"""

        test_input = Path("examples/openapi/input.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output / "src", ignore_errors=True)

        config = {
            "base_package": "com.supertest",
            "api_path": "generated.iface",
            "config_path": "shared.config",
            "controller_path": "generated.api",
            "domain_path": "generated.object",
            "enum_path": "generated.constants",
            "exception_path": "shared.exceptions",
            "model_path": "shared.models",
            "repository_path": "generated.repositorys",
            "service_path": "generated.service",
            "util_path": "shared.utils",
        }

        # generate
        assert generate(test_output, generator_name="spring", input_path=test_input, config=config) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(11)
    def test_specifics_11(self) -> None:
        """Verify usage of generate and controller directive"""
        test_input = """\
            extend api @spring-controller("Buzzword") {
                submitQury(arg1: String, arg2: [Int]): Object @path("query") @method(PATCH)
            }

            type Buzzword @namespace("Incident"){
                name: String!
                extend api @generate("UPDATE") {}
            }

        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(12)
    def test_specifics_12(self) -> None:
        """Verify usage of string identifier"""

        test_input = Path("examples/openapi/input.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output / "src", ignore_errors=True)

        config = {
            "id_type": "STRING",
        }

        # generate
        assert generate(test_output, generator_name="spring", input_path=test_input, config=config) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(13)
    def test_specifics_13(self) -> None:
        """Verify usage of encapsulation"""

        test_input = Path("examples/openapi/input.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output, ignore_errors=True)

        config = {
            "encapsulation": False,
        }

        # generate
        assert generate(test_output, generator_name="spring", input_path=test_input, config=config) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(14)
    def test_specifics_14(self) -> None:
        """Verify usage of no database"""

        test_input = Path("examples/openapi/input.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output / "src", ignore_errors=True)

        config = {
            "database": "NO",
        }

        # generate
        assert generate(test_output, generator_name="spring", input_path=test_input, config=config) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(15)
    def test_specifics_15(self) -> None:
        """Verify usage of folder layout config"""

        test_input = Path("examples/other/package_example.qsdl")
        test_output = Path("srcgen/")

        shutil.rmtree(test_output / "src", ignore_errors=True)

        config = {
            "api_path": "{package}.api",
            "controller_path": "{package}.api",
            "domain_path": "{package}.dto",
            "entity_path": "{package}.db",
            "mapper_path": "{package}.mapper",
            "repository_path": "{package}.db",
            "service_path": "{package}.service",
            "enum_path": "common.constants",
            "exception_path": "common.exceptions",
            "model_path": "common.models",
            "config_path": "common.config",
            "util_path": "common.util",
        }

        # generate
        assert generate(test_output, generator_name="spring", input_path=test_input, config=config) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0

    @pytest.mark.order(16)
    def test_specifics_16(self) -> None:
        """Test nested Object"""
        test_input = """\
            scalar Decimal @spring("String, entity: java.math.BigDecimal, pattern: ^(-)?[0-9][0-9]*(?:.[0-9]{1,18})?$")

            type Foo {
                field1: Decimal
                field2: [Decimal]
            }
        """

        test_input = textwrap.dedent(test_input)
        test_output = Path("srcgen/")

        shutil.rmtree(test_output / "src", ignore_errors=True)

        # generate
        assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

        # run tests
        assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0
