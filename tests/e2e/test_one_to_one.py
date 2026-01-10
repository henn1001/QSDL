from pathlib import Path

import pytest

from tests import testcases

from .base_e2e_test import BaseE2ETest


class TestE2EOneToOne(BaseE2ETest):
    """Test XXXX"""

    TESTCASE = testcases.ONE_TO_ONE

    def test_postgres(self, postgres_schema: str) -> None:
        """asserts generated Postgres schema is correct"""

        pass

    def test_openapi(self, openapi_schema: dict) -> None:
        """asserts generated OpenAPI spec is correct"""

        pass

    def test_spring(self, srcgen: Path) -> None:
        """asserts generated Spring Boot code is correct"""

        pass

    @pytest.mark.integration
    def test_integration(self, srcgen: Path) -> None:
        """runs mvn clean test to verify generated code compiles and tests pass"""

        pass
