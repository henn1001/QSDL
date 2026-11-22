# Library generation

QSDL's library pipeline separates generation from filesystem materialization. Use
`qsdl.core.build()` when generated content should remain in memory, and use a
`DirectoryWriter` when it should be written to a local directory.

## Build in memory

Pass a schema string with `raw_schema`:

```python
from qsdl.core import build

files = build(
    generator_name="openapi",
    raw_schema="type User { name: String }",
)

openapi_yaml = files.text("openapi.yaml")
```

A schema can instead be read from a caller-supplied path. Configuration files
and mapping overrides are optional; mapping values take precedence over values
from the configuration file.

```python
from pathlib import Path

from qsdl.core import build

files = build(
    generator_name="spring",
    input_path=Path("schema.qsdl"),
    config_path=Path("generator.json"),
    config={"database": "NO"},
)
```

`GeneratedFiles` provides content and path inspection without filesystem reads:

```python
if files.exists("openapi.yaml"):
    yaml_text = files.text("openapi.yaml")

for path in files.paths():
    print(path)
```

Text artifacts are read with `text()`. Binary artifacts, such as the PNG files
from PlantUML, are read with `bytes()`:

```python
files = build(generator_name="plantuml", raw_schema="type User { name: String }")
png = files.bytes("plantuml.overview.png")
```

## Invoke a generator directly

`build()` and `generate()` activate the selected generator's definitions
automatically. If you call a generator instance's method yourself, pass its
`directive_specs` to `parse_schema()`:

```python
from qsdl.dsl.textx import parse_schema
from qsdl.generators.openapi import generator

schema = parse_schema(
    raw_schema='scalar Token @openapi("string, format: uuid")\ntype User { token: Token }',
    directive_specs=generator.directive_specs,
)
files = generator.generate(schema, generator.config_class())
```

Without `directive_specs`, parsing binds only core directives. Generator
annotations are still available by name as opaque nodes, but typed lookups don't
find them. Definitions apply for that parse and its imports only. See
[Directive definitions](../generators/plugins.md#directive-definitions) to opt in
from a plugin.

## Inspect a completed schema

`parse_schema()` exposes directive-backed values through attached nodes. For
example, an omitted method has a synthetic `GET` node, while the normalized
path retains its source location:

```python
from qsdl.dsl.textx import get_children_of_operation, parse_schema

schema = parse_schema(raw_schema='extend api { run(): String @path("run") }')
(run,) = get_children_of_operation(schema)
assert run.directive.path.value == "/run"
assert run.directive.path.origin == "source"
assert run.directive.method.value == "GET"
assert run.directive.method.origin == "synthetic"
```

See [Directive definitions](../generators/plugins.md#directive-definitions) for typed lookups.

## Materialize output

Use `DirectoryWriter` to write an in-memory result below a chosen root:

```python
from pathlib import Path

from qsdl.writer import DirectoryWriter

report = DirectoryWriter(Path("srcgen")).write(files)
```

`write()` returns a `WriteReport` with `written`/`skipped` results.

`core.generate()` is the convenience and compatibility API for the same
filesystem-oriented operation. Note its public signature requires the
positional `output_path` and returns `None`:

```python
from pathlib import Path

from qsdl.core import generate

generate(Path("srcgen"), generator_name="openapi", raw_schema="type User { name: String }")
```

## Output rules

- Artifact paths are relative POSIX paths, independent of the host filesystem.
- Duplicate artifact paths are errors when generators construct/return `GeneratedFiles` (`GeneratedFiles.add()`/`extend()`); generation does not silently overwrite
  an artifact.
- Ignore files (`.qignore`, or the legacy `.qsdl-ignore`) affect
  `DirectoryWriter` materialization, not the result returned by `build()`.
- Each `build()` creates a fresh generator configuration instance, so separate
  builds do not share configuration mutations.
