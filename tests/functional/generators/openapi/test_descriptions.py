from pathlib import Path

import pytest

from tests.functional.generators.openapi import generate_openapi


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ('"single line description"', "single line description"),
        ('"""\n            Multi line description\n            """', "Multi line description"),
    ],
)
def test_descriptions_are_rendered_for_openapi_entities(
    tmp_path: Path, description: str, expected: str
) -> None:
    schema = f"""
        description: {description}

        {description}
        enum Status @force-generate {{
            OPEN
        }}

        {description}
        base Common @force-generate {{
            {description}
            value: String
        }}

        {description}
        type User extends Common {{
            {description}
            name: String
        }}

        {description}
        extend api {{
            {description}
            ping: Void @path("ping")
        }}
    """

    openapi = generate_openapi(schema, tmp_path)
    schemas = openapi["components"]["schemas"]

    assert expected in openapi["info"]["description"]
    assert expected in schemas["Status"]["description"]
    assert expected in schemas["Common"]["description"]
    assert expected in schemas["Common"]["properties"]["value"]["description"]
    assert expected in schemas["User"]["description"]
    assert expected in schemas["User"]["properties"]["name"]["description"]
    assert expected in openapi["paths"]["/ping"]["get"]["description"]
