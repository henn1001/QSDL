from pathlib import Path

import pytest
import yaml

from qsdl.generators.postgres.config import Config as PostgresConfig

from . import wrapper_generate


class BaseE2ETest:
    """Base class for E2E tests with reusable fixtures.

    Subclasses should set the TESTCASE class attribute to the testcase string
    they want to test.
    """

    TESTCASE: str

    @pytest.fixture(scope="class")
    def srcgen(self) -> Path:
        """Generates code using the testcase and returns output path."""
        assert self.TESTCASE is not None, "TESTCASE must be set in subclass"
        return wrapper_generate(self.TESTCASE)

    @pytest.fixture(scope="class")
    def postgres_schema(self, srcgen: Path) -> str:
        """Loads and returns the generated Postgres schema."""
        output_file = srcgen / "src/main/resources/db/migration" / PostgresConfig.file_name
        assert output_file.is_file()

        with open(output_file, encoding="utf-8") as file:
            return file.read()

    @pytest.fixture(scope="class")
    def openapi_schema(self, srcgen: Path) -> dict:
        """Loads and returns the generated OpenAPI schema."""
        openapi_file = srcgen / "src/main/resources" / "openapi.yaml"
        assert openapi_file.is_file()

        with open(openapi_file, encoding="utf-8") as file:
            return yaml.load(file, Loader=yaml.FullLoader)
