from pathlib import Path
from typing import Any

from tests.functional.generators.openapi import generate_openapi


def response_schema(openapi: dict[str, Any], path: str, method: str = "get") -> dict[str, Any]:
    """Return the JSON response schema for one rendered operation."""
    return openapi["paths"][path][method]["responses"]["200"]["content"]["application/json"]["schema"]


def test_operation_response_scalar_reference_and_array_schemas(tmp_path: Path) -> None:
    schema = """
        enum Status {
            OPEN
            CLOSED
        }

        base Result {
            value: String
        }

        type Thing {
            name: String
        }

        extend api {
            intResult: Int @path("int-result")
            longResult: Long @path("long-result")
            floatResult: Float @path("float-result")
            doubleResult: Double @path("double-result")
            stringResult: String @path("string-result")
            booleanResult: Boolean @path("boolean-result")
            dateResult: Date @path("date-result")
            datetimeResult: Datetime @path("datetime-result")
            jsonResult: Object @path("json-result")
            values: [Int] @path("values")
            statuses: [Status] @path("statuses")
            enumResult: Status @path("enum-result")
            baseResult: Result @path("base-result")
            objectResult: Thing @path("object-result")
            objects: [Thing] @path("objects")
        }
    """

    openapi = generate_openapi(schema, tmp_path)

    assert response_schema(openapi, "/int-result") == {"type": "integer", "format": "int32"}
    assert response_schema(openapi, "/long-result") == {"type": "integer", "format": "int64"}
    assert response_schema(openapi, "/float-result") == {"type": "number", "format": "float"}
    assert response_schema(openapi, "/double-result") == {"type": "number", "format": "double"}
    assert response_schema(openapi, "/string-result") == {"type": "string"}
    assert response_schema(openapi, "/boolean-result") == {"type": "boolean"}
    assert response_schema(openapi, "/date-result") == {"type": "string", "format": "date"}
    assert response_schema(openapi, "/datetime-result") == {"type": "string", "format": "date-time"}
    assert response_schema(openapi, "/json-result") == {"type": "object"}
    assert response_schema(openapi, "/values") == {"type": "array", "items": {"type": "integer", "format": "int32"}}
    assert response_schema(openapi, "/statuses") == {
        "type": "array",
        "items": {"$ref": "#/components/schemas/Status"},
    }

    assert response_schema(openapi, "/enum-result") == {"$ref": "#/components/schemas/Status"}
    assert response_schema(openapi, "/base-result") == {"$ref": "#/components/schemas/Result"}
    assert response_schema(openapi, "/object-result") == {"$ref": "#/components/schemas/Thing"}
    assert response_schema(openapi, "/objects") == {
        "type": "array",
        "items": {"$ref": "#/components/schemas/Thing"},
    }


def test_object_api_replaces_generated_crud_operations(tmp_path: Path) -> None:
    schema = """
        type Foo {
            name: String

            extend api {
                getFoo: Foo @path("/foos")
            }
        }

        extend api {
            getBar: Object @path("bar")
            getFruit: Object @path("fruit")
        }
    """

    openapi = generate_openapi(schema, tmp_path)

    assert openapi["paths"]["/foos"]["get"]["operationId"] == "getFoo"
    assert set(openapi["paths"]["/foos"]) == {"get"}
    assert openapi["paths"]["/bar"]["get"]["operationId"] == "getBar"
    assert openapi["paths"]["/fruit"]["get"]["operationId"] == "getFruit"
