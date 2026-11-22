from pathlib import Path

import plantuml
import pytest
import yaml
from textx.exceptions import TextXSemanticError

from qsdl.core import build
from qsdl.dsl.textx import parse_schema
from qsdl.generators import get_definition
from qsdl.generators.openapi.config import OPENAPI_SCALAR, OpenApiScalarMapping
from qsdl.generators.postgres.config import POSTGRES_SCALAR
from qsdl.generators.spring import generator as spring_generator
from qsdl.generators.spring.config import SPRING_SCALAR, SpringScalarMapping

EXAMPLE = Path(__file__).resolve().parents[3] / "examples/01-basics/03-custom-scalars/schema.qsdl"
MAPPINGS = (SPRING_SCALAR, OPENAPI_SCALAR, POSTGRES_SCALAR)


@pytest.mark.parametrize("target", ["spring", "openapi", "postgres"])
def test_scalar_example_is_order_independent(target: str) -> None:
    raw = EXAMPLE.read_text(encoding="utf-8")
    reordered = raw.replace(
        '@openapi("string, format: email") @spring("String") @postgres("TEXT")',
        '@postgres("TEXT") @spring("String") @openapi("string, format: email")',
    )
    assert reordered != raw
    original = build(generator_name=target, input_path=EXAMPLE)
    assert list(original) == list(build(generator_name=target, raw_schema=reordered))

    active = get_definition(target).directive_specs
    schema = parse_schema(EXAMPLE, directive_specs=active)
    email = next(scalar for scalar in schema.types if scalar.name == "EmailAddress")
    expected = {
        "spring": SpringScalarMapping("String"),
        "openapi": OpenApiScalarMapping("string", format="email"),
        "postgres": "TEXT",
    }
    for spec in MAPPINGS:
        node = email.directives.by_name(spec.name)
        if spec.name == target:
            assert node is email.directives.get(spec)
            assert node.value == expected[target]
        else:
            assert email.directives.get(spec) is None
            assert node.spec is None and isinstance(node.value, str)


RAW = r"""
scalar Token @spring("String, entity: java.math.BigInteger, pattern: ^[0-9]{1,38}$")
    @openapi("string, format: token, pattern: ^[0-9]{1,38}$") @postgres('TEXT')

type Item {
    token: Token
    count: Int
}
"""


def assert_openapi_mapping(content: str) -> None:
    properties = yaml.safe_load(content)["components"]["schemas"]["Item"]["properties"]
    assert properties["token"] == {"type": "string", "format": "token", "pattern": "^[0-9]{1,38}$", "maxLength": 255}
    assert properties["count"] == {"type": "integer", "format": "int32", "minimum": 0}


def test_scalar_mapping_options_fallbacks_and_spring_bundled_artifacts() -> None:
    schema = parse_schema(raw_schema=RAW, directive_specs=spring_generator.directive_specs)
    token = schema.types[0]
    assert token.directives.get(SPRING_SCALAR).value == SpringScalarMapping(
        "String", entity="java.math.BigInteger", pattern="^[0-9]{1,38}$"
    )
    spring = spring_generator.generate(schema, spring_generator.config_class())
    request = spring.text("src/main/java/app/api/general/contract/ItemRequest.java")
    entity = spring.text("src/main/java/app/api/general/persistence/ItemEntity.java")
    assert '@Pattern(regexp = "^[0-9]{1,38}$")' in request
    assert "private java.math.BigInteger token;" in entity
    assert "private Integer count;" in entity

    openapi = build(generator_name="openapi", raw_schema=RAW)
    assert_openapi_mapping(openapi.text("openapi.yaml"))
    assert spring.text("src/main/resources/openapi.yaml") == openapi.text("openapi.yaml")
    postgres = build(generator_name="postgres", raw_schema=RAW)
    (sql,) = postgres
    assert "token TEXT" in sql.content and "count INTEGER" in sql.content
    assert spring.text(f"src/main/resources/db/migration/{sql.path}") == sql.content
    assert token.directives.get(OPENAPI_SCALAR) is token.directives.get(POSTGRES_SCALAR) is None
    assert token.directives.by_name("openapi").spec is None
    assert token.directives.by_name("postgres").spec is None


@pytest.mark.parametrize(
    ("target", "annotation"),
    [
        ("openapi", "@openapi"),
        ("openapi", "@openapi(string)"),
        ("openapi", '@openapi("")'),
        ("openapi", '@openapi("format: uuid")'),
        ("openapi", '@openapi("string, entity: UUID")'),
        ("openapi", '@openapi("string, format: uuid, format: email")'),
        ("openapi", '@openapi("string, pattern")'),
        ("spring", '@spring("String, format: uuid")'),
        ("spring", '@spring("String, entity:")'),
        ("spring", '@spring("String, pattern: a, pattern: b")'),
        ("postgres", '@postgres("")'),
        ("postgres", "@postgres(TEXT)"),
    ],
)
def test_invalid_scalar_mapping_is_located_only_for_selected_target(target: str, annotation: str) -> None:
    raw = f"scalar Token {annotation}\ntype Item {{ token: Token }}"
    inert = parse_schema(raw_schema=raw).types[0].directives[0]
    assert inert.spec is None
    alternate = "openapi" if target == "spring" else "spring"
    assert build(generator_name=alternate, raw_schema=raw).paths()
    with pytest.raises(TextXSemanticError, match=f"Invalid @{target}") as error:
        build(generator_name=target, raw_schema=raw)
    assert (error.value.line, error.value.col) == (1, len("scalar Token ") + 1)


@pytest.mark.parametrize("target", ["spring", "openapi", "postgres"])
def test_selected_scalar_mapping_rejects_other_owners(target: str) -> None:
    raw = f'type Item @{target}("non-empty") {{ name: String }}'
    assert parse_schema(raw_schema=raw).types[0].directives[0].spec is None
    with pytest.raises(TextXSemanticError, match=f"@{target} is not supported") as error:
        build(generator_name=target, raw_schema=raw)
    assert (error.value.line, error.value.col) == (1, raw.index("@") + 1)


@pytest.mark.parametrize("target", ["plantuml", "i18n", "void"])
def test_generator_without_definitions_uses_core_only(target: str, monkeypatch: pytest.MonkeyPatch) -> None:
    if target == "plantuml":
        monkeypatch.setattr(plantuml.PlantUML, "processes", lambda *_: b"diagram")
    assert get_definition(target).directive_specs == ()
    annotated = 'type Foo @spring-package(not quoted) @namespace("Domain") { label: String @readOnly }'
    core_only = annotated.replace(" @spring-package(not quoted)", "")
    assert list(build(generator_name=target, raw_schema=annotated)) == list(
        build(generator_name=target, raw_schema=core_only)
    )
    with pytest.raises(TextXSemanticError, match="Invalid @readOnly"):
        build(generator_name=target, raw_schema=annotated.replace("@readOnly", "@readOnly()"))
