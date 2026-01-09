from pathlib import Path

import pytest

from tests import testcases

from . import wrapper_generate


@pytest.fixture(scope="class", autouse=True)
def srcgen() -> Path:
    return wrapper_generate(testcases.ONE_TO_ONE)


class TestE2EOneToOne:
    """Test XXXX"""

    def test_postgres(self, srcgen: Path) -> None:
        """asserts generated Postgres schema is correct"""

        pass

    def test_openapi(self, srcgen: Path) -> None:
        """asserts generated OpenAPI spec is correct"""

        pass

    def test_spring(self, srcgen: Path) -> None:
        """asserts generated Spring Boot code is correct"""

        pass

    # run this test only when special flag
    def test_integration(self, srcgen: Path) -> None:
        """runs mvn clean test to verify generated code compiles and tests pass"""

        pass
