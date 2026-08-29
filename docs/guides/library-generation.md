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
files = build(generator_name="plantuml", raw_schema=schema)
png = files.bytes("plantuml.overview.png")
```

## Materialize output

Use `DirectoryWriter` to write an in-memory result below a chosen root:

```python
from pathlib import Path

from qsdl.writer import DirectoryWriter

DirectoryWriter(Path("srcgen")).write(files)
```

`core.generate()` is the convenience and compatibility API for the same
filesystem-oriented operation:

```python
from pathlib import Path

from qsdl.core import generate

generate(Path("srcgen"), generator_name="openapi", raw_schema=schema)
```

## Output rules

- Artifact paths are relative POSIX paths, independent of the host filesystem.
- Duplicate artifact paths are errors; generation does not silently overwrite
  an artifact.
- Ignore files (`.qignore`, or the legacy `.qsdl-ignore`) affect
  `DirectoryWriter` materialization, not the result returned by `build()`.
- Each `build()` creates a fresh generator configuration instance, so separate
  builds do not share configuration mutations.
