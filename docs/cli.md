# CLI Reference

This document describes the QSDL command-line interface, options, input/output handling, and configuration.

## Overview

The QSDL CLI is the primary interface for generating code and specifications from schema definition files. It has three command groups:

```
qsdl generate GENERATOR -i INPUT [-o OUTPUT] [-c CONFIG ...] [-S KEY=VALUE ...]
qsdl config (show | init | validate) GENERATOR [...]
qsdl list
```

Where:

- **GENERATOR** — A builtin generator name (`openapi`, `spring`, `postgres`, `plantuml`, `i18n`, `void`) or a path to a custom generator (a `.py` file or a package directory with an `__init__.py`). Unknown names fail with the list of available generators.
- **INPUT** — Path to a `.qsdl` schema file (required for generation).

## Installation

The `qsdl` command is installed automatically when you install the QSDL package:

```bash
# Via uv
uv tool install git+https://github.com/henn1001/QSDL

# Via pip/pipx
pip install git+https://github.com/henn1001/QSDL
pipx install git+https://github.com/henn1001/QSDL
```

After installation, the `qsdl` command is available in your PATH.

## Usage

### Basic Example

Generate OpenAPI specification from a schema:

```bash
qsdl generate openapi -i myschema.qsdl
```

This outputs files to `srcgen/` next to the input file.

### Show a Generator's Default Configuration

Print the default configuration for a generator as formatted JSON:

```bash
qsdl config show spring
```

Write it directly to a file to use as a starting point:

```bash
qsdl config init spring -o config.json
qsdl generate spring -i myschema.qsdl -c config.json
```

### Specifying Output Directory

```bash
qsdl generate spring -i myschema.qsdl -o ./src/
```

### Using Configuration Files

Config files are JSON. `-c` is repeatable; later files override earlier ones:

```bash
qsdl generate spring -i myschema.qsdl -c base.json -c override.json -o ./generated/
```

### Overriding Single Fields with --set

`-S/--set KEY=VALUE` overrides one generator config field without a file. It is repeatable and always wins over `-c` files:

```bash
qsdl generate spring -i myschema.qsdl -S title=MyApp -S database=NO
qsdl generate postgres -i myschema.qsdl -S table_prefix=app_
```

Keys are the generator's config field names; values are coerced to the declared type (`true`/`false` for booleans, member names for enums). Unknown keys fail and list the valid keys. Validate a combination without generating:

```bash
qsdl config validate spring -c config.json -S database=NO
```

### Include Version File

The `--write-version` flag writes a `.qversion` file to the output directory containing the QSDL version:

```bash
qsdl generate openapi -i myschema.qsdl --write-version
```

Output:

```
srcgen/
├── openapi.yaml
└── .qversion
```

## Options

```
qsdl generate GENERATOR -i INPUT [OPTIONS]

Arguments:
  GENERATOR                   Builtin generator name or path to a custom generator
                              (.py file or package directory).

Options:
  -i, --input PATH            Schema definition file (required).
  -o, --output PATH           Output folder. Default: 'srcgen/' next to the input file.
  -c, --config PATH           JSON config file. Repeatable; later files win.
  -S, --set KEY=VALUE         Override one config field. Repeatable; wins over files.
  --write-version             Write a .qversion file to the output folder.
  --help                      Show this message and exit.

qsdl config (show | init | validate) GENERATOR [...]
qsdl list
```

### Arguments

**`GENERATOR`** — Which generator to use: a builtin name or a path to a custom generator file/directory. Custom generators must export `generator`, an instance of `qsdl.generators.Generator`; loading a path executes that code.

**`INPUT`** — Path to your `.qsdl` schema file, via `-i/--input`. Required for generation.

### Options

**`-o, --output PATH`** — Where to write generated files. Defaults to `srcgen/` next to the input file.

**`-c, --config PATH`** — Path to a JSON configuration file with generator-specific options. Repeatable; later files override earlier ones. See [Configuration](#configuration) for details.

**`-S, --set KEY=VALUE`** — Override a single config field. Repeatable; overrides everything from `-c` files. Values are coerced to the field's declared type.

**`--write-version`** — Write a `.qversion` file to the output directory with the QSDL version.

**`qsdl config show GENERATOR`** — Print the default JSON configuration. Enums are printed using their JSON values.

**`qsdl config init GENERATOR -o FILE`** — Write the default JSON configuration to a file.

**`qsdl config validate GENERATOR [-c ...] [-S ...]`** — Validate config files and overrides without generating.

**`qsdl list`** — List available builtin generators.

**`--version`** — Print the installed QSDL version and exit.

**`--help`** — Show help text and exit.

## Input Files

### Schema File Format

QSDL schema files use the `.qsdl` extension. A minimal valid schema:

```qsdl
type User {
  name: String!
  email: String
}
```

Schema files may contain:

- **Type definitions** (`type`, `base`, `enum`)
- **API definitions** (`api`, `extend api`)
- **Directives** (annotations like `@readOnly`, `@namespace`)
- **Imports** (reference other `.qsdl` files)
- **Schema metadata** (title, version, description, servers)

For complete syntax, see [Language overview](./core/language.md).

### File Imports

QSDL schemas can be modular. Use `import` to include types from other files:

```qsdl
import "./common.qsdl"
import "./domain/users.qsdl"

type Order {
  user: User!  # Type defined in common.qsdl
}
```

When you provide a schema file with imports, QSDL resolves all imports automatically.

## Output

### File Overwriting and Protection

By default, QSDL **overwrites** existing output files on regeneration. This is intentional—it ensures your generated code stays synchronized with your schema.

However, you may want to **protect certain files** from being overwritten after you've added custom code to them.

### Using .qignore

The **Spring Boot generator** (and other generators) support a `.qignore` file to exclude specific files from being overwritten during regeneration.

#### How to Use

1. Create a `.qignore` file in your output directory
2. List patterns for files you want to protect (one per line)
3. Patterns follow **gitignore/dockerignore syntax** (glob-style wildcards)
4. When you regenerate, matched files will not be overwritten

#### Example .qignore

```
# Protect all files in the shared config directory
src/main/java/app/shared/config/**

# Protect custom utility classes
src/main/java/app/shared/util/CustomHelper.java

# Protect test files
src/test/**

# Protect resource files
src/main/resources/application.yaml
```

#### Pattern Syntax

The patterns follow **gitignore wildcard syntax**:

| Pattern          | Matches                                        |
| ---------------- | ---------------------------------------------- |
| `file.java`      | Exact filename                                 |
| `*.java`         | All Java files                                 |
| `path/to/*.java` | Java files in specific path                    |
| `path/**`        | All files under a directory and subdirectories |
| `src/main/**`    | All files under src/main/ tree                 |

#### Workflow Example

1. **First generation:**

   ```bash
   qsdl generate spring -i schema.qsdl -o ./src/
   ```

2. **Add custom code** to some generated files

3. **Create .qignore** in `./src/` with:

   ```
   src/main/java/app/shared/config/**
   src/main/java/app/shared/util/CustomService.java
   ```

4. **Regenerate** (these files will be skipped):
   ```bash
   qsdl generate spring -i schema.qsdl -o ./src/
   ```

The `.qignore` file itself is also protected and won't be overwritten.

## Configuration

Generators support configuration via JSON files and `--set` overrides. Precedence is: defaults < `-c` files in order < `--set`. Pass config files with `-c`:

```bash
qsdl generate spring -i schema.qsdl -c config.json -o ./generated/
```

QSDL loads the JSON file, merges it with defaults, and applies the configuration to the generator.

For generator-specific configuration options, see the documentation for each generator:

- **[OpenAPI Configuration](./generators/openapi/README.md)** — Options for OpenAPI spec generation
- **[Spring Boot Configuration](./generators/spring/README.md)** — Packages, database, auditing, and more
- **[PostgreSQL Configuration](./generators/postgres/README.md)** — Schema file names and table prefixes
- **[PlantUML Configuration](./generators/plantuml/README.md)** — (No configuration options)
- **[i18n Configuration](./generators/i18n/README.md)** — (No configuration options)
- **[Void Configuration](./generators/void/README.md)** — (No configuration options)

### Custom Generators

Any `GENERATOR` argument that looks like a path (contains a separator, ends in `.py`, or exists on disk) loads as a custom generator instead of a builtin. A single `.py` file or a package directory (with `__init__.py`) must export one `generator`: a `qsdl.generators.Generator` instance. The supplied adapter makes the contract concise:

```python
from qsdl.generators import Generator

class MyGenerator(Generator):
    config_class = Config

    def generate(self, schema: Schema, config: Config, output_path: Path | None) -> GeneratedFiles:
        ...

generator = MyGenerator()
```

`Config` must be a `BaseConfig` dataclass. `generate` must accept exactly `schema`, that exact `Config` type, and `output_path`, and be annotated to return `GeneratedFiles`. `-c` and `-S` validate against `Config`.

```bash
qsdl generate ./my_gen.py -i schema.qsdl -S greeting=hi
qsdl generate ./my_gen/ -i schema.qsdl -c my_gen.json
qsdl config show ./my_gen.py
```

A custom generator whose file stem matches a builtin name is rejected. Loading a path executes arbitrary code; only reference paths you trust. See [Custom generator plugins](./generators/plugins.md) for the complete contract, loading behavior, configuration, and error policy.

## Next Steps

- [Overview](./overview.md) — Understand QSDL concepts
- [Language overview](./core/language.md) — Learn the QSDL syntax
- [Generators overview](./generators/README.md) — Detailed generator documentation
