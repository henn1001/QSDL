# Custom Generator Plugins

QSDL can load a generator from a Python file or package directory in addition to its builtin generators. A plugin is Python code executed in the QSDL process. Use only plugin paths you trust.

## Plugin contract

A plugin exports exactly one value named `generator`. It must be an instance of `qsdl.generators.Generator`.

```python
from dataclasses import dataclass
from pathlib import Path

from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import Schema
from qsdl.generators import Generator
from qsdl.generators.base_config import BaseConfig


@dataclass
class GreetingConfig(BaseConfig):
    greeting: str = "Hello"
    enabled: bool | None = None


class GreetingGenerator(Generator):
    config_class = GreetingConfig

    def generate(
        self,
        schema: Schema,
        config: GreetingConfig,
        output_path: Path | None = None,
    ) -> GeneratedFiles:
        files = GeneratedFiles()
        if config.enabled is not False:
            files.add_text("greeting.txt", f"{config.greeting}, {len(schema.types)} types\n")
        return files


generator = GreetingGenerator()
```

The loader validates the contract when it loads the plugin:

- `generator` is a `Generator` instance.
- `config_class` is a dataclass subclass of `BaseConfig`.
- `generate` accepts exactly `schema`, `config`, and `output_path` parameters.
- The `config` annotation is exactly `config_class`.
- The return annotation is `GeneratedFiles`.
- Optional `directive_specs` is a tuple of valid directive definitions.

`output_path` is the requested destination for the current invocation. A generator normally returns artifacts rather than writing files directly. QSDL validates the returned collection and writes it using its normal output and ignore-file policy. A generator that needs to inspect existing destination files may use `output_path`; the i18n generator is an example.

Do not store a per-invocation config or schema on the generator instance. Builtin generator instances are shared registry entries, so request data belongs in `generate` arguments or local variables.

## Read model fields

Plugins that used `Base.fields` or `Object.fields` for rendering should switch
to `generation_fields`. `.fields` now contains only source declarations,
including `@ignore` fields; it no longer includes inherited fields or generated
IDs. `generation_fields` includes resolved inherited fields and the generated
Object ID, excluding `@ignore` fields. Use `effective_fields` when you need the
same resolved fields before ignore filtering. See the
[library example](../guides/library-generation.md#choose-a-field-view).

## Directive definitions

A generator can declare `directive_specs`, a tuple of `DirectiveSpec` objects.
Each definition supplies an exact name, a non-empty tuple of supported QSDL owner
classes, a decoder, and optionally a typed value validator. A definition name
must follow the [directive naming rules](../core/rules.md#identifiers--naming-conventions) and
must not duplicate another definition or any core directive name.

For example, add this to the greeting plugin to accept `@plugin-label("text")`
on scalar declarations:

```python
from qsdl.dsl import DirectiveSpec, Scalar
from qsdl.dsl.directives import decode_string

LABEL = DirectiveSpec("plugin-label", (Scalar,), decode_string)
GreetingGenerator.directive_specs = (LABEL,)
```

In `generate`, read the typed node with `scalar.directives.get(LABEL)`.
Read core values through `owner.directive`: flags return a `bool` (`field.directive.is_read_only`), other directives return a node or `None`. For example, an
operation's `operation.directive.path.value` is its normalized route, and
`operation.directive.method.origin` distinguishes an explicit method from a
synthetic default. See [Inspect a completed schema](../guides/library-generation.md#inspect-a-completed-schema).

Use the same definition object for declaration and lookup. The decoder receives a
`RawDirective` with the name, parentheses presence, raw text, and location;
raise `ValueError` for invalid payloads. The optional validator receives the
decoded value and can reject it by raising `ValueError`. Use immutable values
for compound payloads.

QSDL binds these definitions before generation, in the root schema and imports.
A malformed payload or unsupported owner raises a semantic error at the
directive. Other generators leave the name opaque unless they declare their own
definition for it. If you invoke a generator directly, activate its definitions
with [`parse_schema(..., directive_specs=...)`](../guides/library-generation.md#invoke-a-generator-directly).

## File and package plugins

Pass either a `.py` file or a directory containing `__init__.py` as `GENERATOR`:

```bash
qsdl generate ./greeting.py -i schema.qsdl -o generated
qsdl generate ./greeting_plugin -i schema.qsdl -o generated
```

A custom file or directory whose basename matches a builtin generator name is rejected. For example, `./spring.py` cannot shadow the `spring` builtin.

QSDL resolves the plugin entry to an absolute path, derives a valid module name from that path plus a SHA-256 digest, and caches the successfully loaded plugin for the process lifetime. Resolving the same path again uses the cached generator and does not re-execute its module. Different paths with the same filename remain distinct. Package plugins support relative imports.

Restart QSDL after changing a plugin. A running process intentionally does not reload a cached plugin.

## Configuration

`config_class` is the complete configuration schema for the plugin. QSDL constructs it on every generation request using this precedence:

```text
default dataclass values < -c/--config files in command order < -S/--set overrides
```

The same construction path is used by generation and validation:

```bash
qsdl config show ./greeting.py
qsdl config init ./greeting.py -o greeting.json
qsdl config validate ./greeting.py -c greeting.json -S greeting=Hi
qsdl generate ./greeting.py -i schema.qsdl -c greeting.json -S enabled=false
```

Unknown keys fail. QSDL resolves postponed annotations with `typing.get_type_hints()` before coercing `--set` values. It supports strings, booleans, integers, floats, enums, `Annotated` types, unions (including optional values), literals, and JSON-encoded `list`, `set`, `frozenset`, `tuple`, and `dict` values. Use `null` or `none` for the `None` member of an optional union.

Config-file values are decoded as JSON and are then validated by `dacite` when QSDL creates `config_class`. `--set` is for concise scalar values; container values must be JSON:

```bash
-S enabled=false
-S retries=3
-S locales='["en", "de"]'
```

## Errors and debugging

Resolution, config-key, coercion, JSON, and config-construction errors are reported as clean CLI errors with exit status 1. Exceptions raised while a generator runs are not flattened by the CLI; they retain their traceback for plugin debugging.

For the complete command syntax, see the [CLI reference](../cli.md). For the in-memory artifact API, see [Library generation](../guides/library-generation.md).
