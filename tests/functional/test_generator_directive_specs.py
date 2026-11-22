from pathlib import Path

import pytest
from textx.exceptions import TextXSemanticError

from qsdl import dsl, plugins
from qsdl.core import build
from qsdl.dsl.directives import NAMESPACE, decode_string
from qsdl.dsl.textx import parse_schema
from qsdl.generators import validate_generator

PLUGIN = """
from dataclasses import dataclass
from pathlib import Path

from qsdl import dsl
from qsdl.artifacts import GeneratedFiles
from qsdl.dsl.directives import decode_string
from qsdl.generators import Generator
from qsdl.generators.base_config import BaseConfig

LABEL = dsl.DirectiveSpec("plugin-label", (dsl.Scalar,), decode_string)

@dataclass
class PluginConfig(BaseConfig):
    pass

class Plugin(Generator):
    config_class = PluginConfig
    directive_specs = (LABEL,)

    def generate(self, schema: dsl.Schema, config: PluginConfig, output_path: Path | None) -> GeneratedFiles:
        files = GeneratedFiles()
        for scalar in schema.types:
            node = scalar.directives.get(LABEL)
            if node is not None:
                assert node is scalar.directives.by_name("plugin-label")
                files.add_text(f"{scalar.name}.txt", node.value)
        return files

generator = Plugin()
"""


@pytest.fixture
def directive_plugin(tmp_path: Path) -> Path:
    path = tmp_path / "label_plugin.py"
    path.write_text(PLUGIN, encoding="utf-8")
    return path


LABEL = dsl.DirectiveSpec("plugin-label", (dsl.Scalar,), decode_string)


@pytest.mark.parametrize(
    ("specs", "message"),
    [
        ([LABEL], "must be a tuple"),
        ((object(),), "only DirectiveSpec"),
        ((LABEL, LABEL), "duplicate directive spec"),
        ((NAMESPACE,), "conflicts with a core directive"),
        ((dsl.DirectiveSpec("Bad", (dsl.Scalar,), decode_string),), "invalid directive name"),
        ((dsl.DirectiveSpec("label", (), decode_string),), "supported QSDL owner classes"),
        ((dsl.DirectiveSpec("label", (dsl.Schema,), decode_string),), "supported QSDL owner classes"),
    ],
)
def test_validate_generator_directive_contract(directive_plugin: Path, specs: object, message: str) -> None:
    _, definition = plugins.resolve(str(directive_plugin))
    plugin = definition.plugin
    plugin.directive_specs = specs
    with pytest.raises(TypeError, match=message):
        validate_generator(plugin)


@pytest.mark.parametrize(("specs", "message"), [((LABEL, LABEL), "duplicate"), ((NAMESPACE,), "conflicts")])
def test_direct_parse_validates_supplied_specs(specs: tuple[dsl.DirectiveSpec, ...], message: str) -> None:
    with pytest.raises(TypeError, match=message):
        parse_schema(raw_schema="scalar Token", directive_specs=specs)


def test_plugin_binding_is_exact_and_parse_scoped(directive_plugin: Path, tmp_path: Path) -> None:
    source = tmp_path / "root.qsdl"
    imported = tmp_path / "model.qsdl"
    source.write_text('import "model.qsdl"\nscalar Root @plugin-label("root")\n', encoding="utf-8")
    imported.write_text('scalar Token @plugin-label("imported") @plugin-labl(not quoted)\n', encoding="utf-8")
    _, definition = plugins.resolve(str(directive_plugin))
    (spec,) = definition.directive_specs

    first = build(generator_name=str(directive_plugin), input_path=source)
    assert first.text("Root.txt") == "root" and first.text("Token.txt") == "imported"
    assert not build(generator_name="void", input_path=source).paths()

    plain = parse_schema(source)
    plain_token = next(scalar for scalar in plain.types if scalar.name == "Token")
    assert plain_token.directives.get(spec) is None
    assert plain_token.directives.by_name("plugin-label").value == "imported"

    typed = parse_schema(source, directive_specs=definition.directive_specs)
    token = next(scalar for scalar in typed.types if scalar.name == "Token")
    bound, opaque = token.directives
    assert bound is token.directives.get(spec) and bound.value == "imported"
    assert token.directives.get(LABEL) is None  # same name, different definition
    assert opaque is token.directives.by_name("plugin-labl") and opaque.spec is None
    assert build(generator_name=str(directive_plugin), input_path=source).text("Token.txt") == "imported"


@pytest.mark.parametrize("imported", [False, True])
@pytest.mark.parametrize(
    ("schema", "message"),
    [
        ("scalar Token @plugin-label(noQuotes)", "Invalid @plugin-label"),
        ('type Foo @plugin-label("wrong owner") {}', "@plugin-label is not supported"),
    ],
)
def test_plugin_diagnostics_are_located_and_inactive_names_are_opaque(
    directive_plugin: Path, tmp_path: Path, schema: str, message: str, imported: bool
) -> None:
    source = tmp_path / "root.qsdl"
    annotated = tmp_path / "model.qsdl" if imported else source
    if imported:
        source.write_text('import "model.qsdl"\n', encoding="utf-8")
    annotated.write_text(schema, encoding="utf-8")

    with pytest.raises(TextXSemanticError, match=message) as error:
        build(generator_name=str(directive_plugin), input_path=source)
    assert (error.value.filename, error.value.line, error.value.col) == (
        str(annotated),
        1,
        schema.index("@plugin-label") + 1,
    )
    assert not build(generator_name="void", input_path=source).paths()
    assert parse_schema(source).types[0].directives.by_name("plugin-label").spec is None
