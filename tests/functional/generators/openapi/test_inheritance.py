from pathlib import Path
from typing import Any

from tests.functional.generators.openapi import generate_openapi


def test_inherited_base_fields_are_flattened_in_base_and_object_schemas(tmp_path: Path) -> None:
    schema = """
        base Fruit {
            banana: Int
        }

        base Foo extends Fruit {
            field: Int
        }

        base Bar extends Foo, Fruit @force-generate {
            barName: String
        }

        type Entity extends Foo, Fruit {
            entityName: String
        }
    """

    openapi = generate_openapi(schema, tmp_path)
    schemas: dict[str, Any] = openapi["components"]["schemas"]

    assert set(schemas["Bar"]["properties"]) >= {"banana", "field", "barName"}
    assert set(schemas["Entity"]["properties"]) >= {"banana", "field", "entityName"}
