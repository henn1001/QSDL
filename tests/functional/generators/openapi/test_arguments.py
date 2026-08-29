from pathlib import Path
from typing import Any

from tests.functional.generators.openapi import generate_openapi


def operation_parameter(openapi: dict[str, Any], path: str, method: str = "get") -> dict[str, Any]:
    """Return the first rendered parameter for an operation."""
    return openapi["paths"][path][method]["parameters"][0]


def request_schema(openapi: dict[str, Any], path: str, method: str = "post") -> dict[str, Any]:
    """Return the JSON request schema for an operation."""
    return openapi["paths"][path][method]["requestBody"]["content"]["application/json"]["schema"]


def test_argument_locations_and_request_shapes(tmp_path: Path) -> None:
    schema = """
        enum Bar {
            OPEN
            CLOSED
        }

        base Foo {
            field: String
        }

        type Fruit {
            field: String
        }

        extend api {
            pathArg: Void @path("path/{arg}")
            intQuery(arg: Int): Void @path("int-query")
            floatQuery(arg: Float): Void @path("float-query")
            stringQuery(arg: String): Void @path("string-query")
            booleanQuery(arg: Boolean): Void @path("boolean-query")
            dateQuery(arg: Date): Void @path("date-query")
            datetimeQuery(arg: Datetime): Void @path("datetime-query")
            objectQuery(arg: Object): Void @path("object-query")
            enumQuery(arg: Bar): Void @path("enum-query")
            baseQuery(arg: Foo): Void @path("base-query")
            fruitQuery(arg: Fruit): Void @path("fruit-query")
            arrayQuery(arg: [String]): Void @path("array-query")

            intBody(arg: Int): Void @path("int-body") @method(POST)
            floatBody(arg: Float): Void @path("float-body") @method(POST)
            stringBody(arg: String): Void @path("string-body") @method(POST)
            booleanBody(arg: Boolean): Void @path("boolean-body") @method(POST)
            dateBody(arg: Date): Void @path("date-body") @method(POST)
            datetimeBody(arg: Datetime): Void @path("datetime-body") @method(POST)
            objectBody(arg: Object): Void @path("object-body") @method(POST)
            enumBody(arg: Bar): Void @path("enum-body") @method(POST)
            baseBody(arg: Foo): Void @path("base-body") @method(POST)
            fruitBody(arg: Fruit): Void @path("fruit-body") @method(POST)
            arrayPost(arg: [String]): Void @path("array-post") @method(POST)
            arrayPut(arg: [String]): Void @path("array-put") @method(PUT)
            arrayPatch(arg: [String]): Void @path("array-patch") @method(PATCH)
            mixedBody(arg: String, optional: String?, required: Int!?): Void
                @path("mixed-body") @method(POST)
        }
    """

    openapi = generate_openapi(schema, tmp_path)
    schemas = openapi.get("components", {}).get("schemas", {})

    query_cases = [
        ("/path/{arg}", "integer", "int64", "path", False),
        ("/int-query", "integer", "int32", "query", False),
        ("/float-query", "number", "float", "query", False),
        ("/string-query", "string", None, "query", False),
        ("/boolean-query", "boolean", None, "query", False),
        ("/date-query", "string", "date", "query", False),
        ("/datetime-query", "string", "date-time", "query", False),
        ("/object-query", "object", None, "query", False),
        ("/enum-query", None, None, "query", True),
        ("/base-query", None, None, "query", True),
        ("/fruit-query", None, None, "query", True),
    ]
    for path, expected_type, expected_format, location, is_reference in query_cases:
        parameter = operation_parameter(openapi, path)
        assert parameter["in"] == location
        if expected_type:
            assert parameter["schema"]["type"] == expected_type
        if expected_format:
            assert parameter["schema"]["format"] == expected_format
        if is_reference:
            assert parameter["schema"]["$ref"]

    array_parameter = operation_parameter(openapi, "/array-query")
    assert array_parameter["schema"] == {"type": "array", "items": {"type": "string"}}

    scalar_bodies = [
        ("/int-body", "IntBodyRequest", "integer", "int32"),
        ("/float-body", "FloatBodyRequest", "number", "float"),
        ("/string-body", "StringBodyRequest", "string", None),
        ("/boolean-body", "BooleanBodyRequest", "boolean", None),
        ("/date-body", "DateBodyRequest", "string", "date"),
        ("/datetime-body", "DatetimeBodyRequest", "string", "date-time"),
    ]
    for path, title, expected_type, expected_format in scalar_bodies:
        body = request_schema(openapi, path)
        assert body["title"] == title
        assert body["type"] == "object"
        assert body["properties"]["arg"]["type"] == expected_type
        if expected_format:
            assert body["properties"]["arg"]["format"] == expected_format
        assert title not in schemas

    object_body = request_schema(openapi, "/object-body")
    assert object_body["title"] == "ObjectBodyRequest"
    assert object_body["type"] == "object"
    assert "ObjectBodyRequest" not in schemas

    enum_body = request_schema(openapi, "/enum-body")
    assert enum_body["title"] == "EnumBodyRequest"
    assert enum_body["properties"]["arg"] == {"$ref": "#/components/schemas/Bar"}
    assert "EnumBodyRequest" not in schemas

    assert request_schema(openapi, "/base-body") == {"$ref": "#/components/schemas/Foo"}
    assert request_schema(openapi, "/fruit-body") == {"$ref": "#/components/schemas/Fruit"}

    for path, method, title in [
        ("/array-post", "post", "ArrayPostRequest"),
        ("/array-put", "put", "ArrayPutRequest"),
        ("/array-patch", "patch", "ArrayPatchRequest"),
    ]:
        body = request_schema(openapi, path, method)
        assert body["title"] == title
        assert body["properties"]["arg"] == {"type": "array", "items": {"type": "string"}}
        assert title not in schemas

    mixed_parameters = openapi["paths"]["/mixed-body"]["post"]["parameters"]
    assert [(parameter["name"], parameter["required"]) for parameter in mixed_parameters] == [
        ("optional", False),
        ("required", True),
    ]
    assert mixed_parameters[0]["schema"]["type"] == "string"
    assert mixed_parameters[1]["schema"]["type"] == "integer"
    mixed_body = request_schema(openapi, "/mixed-body")
    assert mixed_body["title"] == "MixedBodyRequest"
    assert mixed_body["properties"]["arg"] == {"type": "string"}
    assert "MixedBodyRequest" not in schemas
