# CLI Reference

This document describes the QSDL command-line interface, options, input/output handling, and configuration.

## Overview

The QSDL CLI is the primary interface for generating code and specifications from schema definition files. It follows a simple pattern:

```
qsdl [OPTIONS] [INPUT_PATH]
```

Where:

- **INPUT_PATH** — Path to a `.qsdl` schema file (required for generation)
- **OPTIONS** — Configure the generator and behavior

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
qsdl myschema.qsdl -g openapi
```

This outputs files to the default `srcgen/` directory.

### Print a Generator's Default Configuration

Print the default configuration for a generator as formatted JSON:

```bash
qsdl --print-default-config -g spring
```

The command does not require a schema and writes only JSON to stdout, so the
result can be saved directly as a configuration file:

```bash
qsdl --print-default-config -g spring > config.json
qsdl myschema.qsdl -g spring -c config.json
```

Enums are printed using their JSON values. Generator-specific configuration
initialization is applied, so the output reflects the configuration received by
the generator at runtime.

### Specifying Output Directory

```bash
qsdl myschema.qsdl -g spring -o ./src/
```

### Using a Configuration File

Some generators support configuration. Pass a JSON config file:

```bash
qsdl myschema.qsdl -g spring -c config.json -o ./generated/
```

### Include Version File

The `-pv` flag writes a `.qversion` file to the output directory containing the QSDL version:

```bash
qsdl myschema.qsdl -g openapi -pv
```

Output:

```
srcgen/
├── openapi.yaml
└── .qversion
```

## Options

```
qsdl [OPTIONS] [INPUT_PATH]

Arguments:
  INPUT_PATH                  The path to the schema definition file. Required for generation.

Options:
  -g, --generator TEXT        The requested generator.
  -c, --config_path PATH      Path to a config json file.
  -o, --output_path PATH      Path to a output folder. Default: 'srcgen/'
  -pv, --print_version        Prints a .qversion file to the output folder.
  --print-default-config      Print the default JSON config and exit.
  --version                   Show the version and exit.
  --help                      Show this message and exit.
```

### Arguments

**`INPUT_PATH`** — Path to your `.qsdl` schema file. Required for generation.

### Options

**`-g, --generator TEXT`** — Which generator to use (`openapi`, `spring`, `postgres`, `plantuml`, `i18n`, or `void`). The CLI accepts any string and resolves it to a generator at runtime; unknown names fail during generation setup.

**`-o, --output_path PATH`** — Where to write generated files. Defaults to `srcgen/` in the same directory as the input file.

**`-c, --config_path PATH`** — Path to a JSON configuration file with generator-specific options. See [Configuration](#configuration) for details.

**`-pv, --print_version`** — Write a `.qversion` file to the output directory with the QSDL version.

**`--print-default-config`** — Print the default JSON configuration for the selected generator. Requires `-g/--generator`.

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
# Protect all files in the config directory
src/main/java/app/server/config/**

# Protect custom utility classes
src/main/java/app/server/util/CustomHelper.java

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
   qsdl schema.qsdl -g spring -o ./src/
   ```

2. **Add custom code** to some generated files

3. **Create .qignore** in `./src/` with:

   ```
   src/main/java/app/server/config/**
   src/main/java/app/server/util/CustomService.java
   ```

4. **Regenerate** (these files will be skipped):
   ```bash
   qsdl schema.qsdl -g spring -o ./src/
   ```

The `.qignore` file itself is also protected and won't be overwritten.

## Configuration

Generators support configuration via JSON files. Pass a config file with the `-c` flag:

```bash
qsdl schema.qsdl -g spring -c config.json -o ./generated/
```

QSDL loads the JSON file, merges it with defaults, and applies the configuration to the generator.

For generator-specific configuration options, see the documentation for each generator:

- **[OpenAPI Configuration](./generators/openapi/README.md)** — Options for OpenAPI spec generation
- **[Spring Boot Configuration](./generators/spring/README.md)** — Packages, database, auditing, and more
- **[PostgreSQL Configuration](./generators/postgres/README.md)** — Schema file names and table prefixes
- **[PlantUML Configuration](./generators/plantuml/README.md)** — (No configuration options)
- **[i18n Configuration](./generators/i18n/README.md)** — (No configuration options)
- **[Void Configuration](./generators/void/README.md)** — (No configuration options)

### Interactive Configuration (Prompt Mode)

If you don't provide a generator name with `-g` but do provide `INPUT_PATH`, QSDL enters interactive mode:

```bash
$ qsdl schema.qsdl
```

This prompts you to:

1. Select a generator from a list (defaults to `void`)
2. Configure generator options interactively (every generator-config field is prompted)

(With no arguments at all, the CLI shows help instead of entering prompt mode; `INPUT_PATH` is still required for generation.)

## Next Steps

- [Overview](./overview.md) — Understand QSDL concepts
- [Language overview](./core/language.md) — Learn the QSDL syntax
- [Generators overview](./generators/README.md) — Detailed generator documentation
