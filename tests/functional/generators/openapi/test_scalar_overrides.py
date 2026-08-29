from typing import Any

from tests.functional.generators.openapi import generate_openapi


def test_scalar_override_parses_multiple_attributes_and_extra_whitespace() -> None:
    schema = """
        scalar Exact @openapi("string, format: uuid, pattern: ^[a-f]+$")
        scalar Spaced @openapi("number,    pattern: ^[0-9]+$, format: decimal")

        type Record {
            exact: Exact
            spaced: Spaced
        }
    """

    openapi = generate_openapi(schema)
    properties: dict[str, Any] = openapi["components"]["schemas"]["Record"]["properties"]

    assert properties["exact"] == {
        "type": "string",
        "format": "uuid",
        "pattern": "^[a-f]+$",
        "maxLength": 255,
    }
    assert properties["spaced"] == {
        "type": "number",
        "format": "decimal",
        "pattern": "^[0-9]+$",
        "minimum": 0,
    }
