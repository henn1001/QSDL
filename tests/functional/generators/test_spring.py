import shutil
import subprocess
import textwrap
from pathlib import Path

from qsdl.core import generate


def wrapper_generate(test_input: str) -> None:
    """Generates and returns the OpenAPI spec as dict.

    Args:
        test_input (str): The QSDL definition.

    Returns:
        dict: The OpenAPI specification as dict.
    """
    test_input = textwrap.dedent(test_input)
    test_output = Path("srcgen/" + "/")

    # generate
    shutil.rmtree(test_output / "src", ignore_errors=True)
    assert generate(test_output, generator_name="spring", raw_schema=test_input) is None


def assert_tests_succeed() -> None:
    assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0


class TestGeneratorSpring:
    """Test spring generator"""

    def test_base_relations(self) -> None:
        # Given
        test_input = """\
          base Role {
            name: String!
          }
          
          type User {
            name: String!
            role: Role
          }
        """

        # When
        wrapper_generate(test_input)

        # # Then
        # assert_tests_succeed()

    def test_all_relations(self) -> None:
        # Given
        test_input = """\
          base Role {
            name: String!
          }
          
          type User {
            name: String!
          }
          
          type Ticket {
            name: String!
          }
          
          type Milestone {
            name: String!
          }
          
          type Project {
            name: String!
            role: Role
            roles: [Role]
            //admin: User
            //users: [User]
            //tickets: [Ticket] @composition
            //milestones: [Milestone] @aggregation
          }
        """

        # When
        wrapper_generate(test_input)

        # # Then
        # assert_tests_succeed()
