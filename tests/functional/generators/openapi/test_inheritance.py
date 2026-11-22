from typing import Any

from tests.functional.generators.openapi import generate_openapi


def test_inherited_base_fields_are_flattened_in_base_and_object_schemas() -> None:
    schema = """
        base Fruit {
            banana: Int
        }

        base Foo extends Fruit {
            field: Int
            note: String
        }

        base Bar extends Foo, Fruit @force-generate {
            barName: String
        }

        type Entity extends Foo, Fruit {
            entityName: String
            note: String @override @ignore
        }
    """

    openapi = generate_openapi(schema)
    schemas: dict[str, Any] = openapi["components"]["schemas"]

    assert set(schemas["Bar"]["properties"]) >= {"banana", "field", "barName"}
    assert list(schemas["Entity"]["properties"]) == ["id", "banana", "field", "entityName"]
