from pathlib import Path
from typing import Any

from tests.functional.generators.openapi import generate_openapi


def test_field_visibility_io_and_ignore_directives(tmp_path: Path) -> None:
    schema = """
        enum Status {
            OPEN
        }

        base Details {
            value: String @readOnly
            secret: String @writeOnly
        }

        type User extends Details {
            hidden: String @hidden
            readOnly: String @readOnly
            readStatus: Status @readOnly
            readDetails: Details @readOnly
            writeOnly: String @writeOnly
            writeStatus: Status @writeOnly
            writeDetails: Details @writeOnly
            ignored: String @ignore
            visible: String
        }
    """

    openapi = generate_openapi(schema, tmp_path)
    properties = openapi["components"]["schemas"]["User"]["properties"]

    assert "hidden" not in properties
    assert "ignored" not in properties
    assert properties["value"]["readOnly"] is True
    assert properties["secret"]["writeOnly"] is True
    assert properties["readOnly"]["readOnly"] is True
    assert properties["readStatus"] == {"$ref": "#/components/schemas/Status", "readOnly": True}
    assert properties["readDetails"] == {"$ref": "#/components/schemas/Details", "readOnly": True}
    assert properties["writeOnly"]["writeOnly"] is True
    assert properties["writeStatus"] == {"$ref": "#/components/schemas/Status", "writeOnly": True}
    assert properties["writeDetails"] == {"$ref": "#/components/schemas/Details", "writeOnly": True}
    assert "readOnly" not in properties["visible"]
    assert "writeOnly" not in properties["visible"]


def test_default_directive_is_rendered_with_yaml_value_types(tmp_path: Path) -> None:
    schema = """
        enum Status {
            OPEN
            CLOSED
        }

        type User {
            name: String @default("guest")
            age: Int @default("1")
            count: Long @default("1")
            ratio: Float @default("1.5")
            score: Double @default("1.5")
            enabled: Boolean @default("true")
            disabled: Boolean @default("false")
            status: Status @default("OPEN")
        }
    """

    openapi = generate_openapi(schema, tmp_path)
    properties = openapi["components"]["schemas"]["User"]["properties"]

    assert properties["name"]["default"] == "guest"
    assert properties["age"]["default"] == 1
    assert properties["count"]["default"] == 1
    assert properties["ratio"]["default"] == 1.5
    assert properties["score"]["default"] == 1.5
    assert properties["enabled"]["default"] is True
    assert properties["disabled"]["default"] is False
    assert properties["status"]["default"] == "OPEN"


def test_query_directive_on_read_only_crud_fields(tmp_path: Path) -> None:
    schema = """
        type Project {
            name: String! @query
            description: String
            creation_by: String @readOnly @query
            creation_date: Date @readOnly @query
            last_update_by: String @readOnly @query
            last_update_date: Datetime @readOnly
            meta_inf: Object
        }
    """

    openapi = generate_openapi(schema, tmp_path)
    parameters = openapi["paths"]["/projects"]["get"]["parameters"]
    assert len(parameters) == 4
    assert [parameter["$ref"] for parameter in parameters[1:]] == [
        "#/components/parameters/cursor",
        "#/components/parameters/limit",
        "#/components/parameters/count",
    ]

    filter_properties = parameters[0]["schema"]["properties"]
    assert set(filter_properties) == {"name", "creation_by", "creation_date", "last_update_by"}
    assert filter_properties["name"] == {"type": "string"}
    assert filter_properties["creation_by"] == {"type": "string"}
    assert filter_properties["creation_date"] == {"type": "string", "format": "date"}
    assert filter_properties["last_update_by"] == {"type": "string"}


def test_force_generated_base_and_referenced_components(tmp_path: Path) -> None:
    schema = """
        base Unused {
            value: String
        }

        base Value {
            amount: Int
        }

        enum ForcedStatus @force-generate {
            ACTIVE
        }

        enum UnusedStatus {
            INACTIVE
        }

        type Entity {
            name: String
        }

        base Payload @force-generate {
            value: Value
            entity: Entity
        }
    """

    openapi = generate_openapi(schema, tmp_path)
    schemas: dict[str, Any] = openapi["components"]["schemas"]

    assert "Payload" in schemas
    assert schemas["Payload"]["properties"]["value"] == {"$ref": "#/components/schemas/Value"}
    assert schemas["Payload"]["properties"]["entity"] == {"$ref": "#/components/schemas/Entity"}
    assert "Value" in schemas
    assert "Entity" in schemas
    assert "ForcedStatus" in schemas
    assert "Unused" not in schemas
    assert "UnusedStatus" not in schemas


def test_namespace_tags_and_custom_path_methods_are_rendered(tmp_path: Path) -> None:
    schema = """
        type User @namespace("Domain") {
            name: String
        }

        extend api @namespace("PublicApi") {
            lookup: String @path("lookup")
            create: String @path("lookup") @method(POST)
        }
    """

    openapi = generate_openapi(schema, tmp_path)

    assert openapi["paths"]["/users"]["get"]["tags"] == ["Domain"]
    assert openapi["paths"]["/lookup"]["get"]["operationId"] == "lookup"
    assert openapi["paths"]["/lookup"]["get"]["tags"] == ["PublicApi"]
    assert openapi["paths"]["/lookup"]["post"]["operationId"] == "create"
    assert openapi["paths"]["/lookup"]["post"]["tags"] == ["PublicApi"]
