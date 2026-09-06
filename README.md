# QSDL

**A Schema-Definition Language and code/spec generator inspired by GraphQL.**

QSDL is a minimal, expressive language for defining domain models and APIs. Write a clean schema once, generate OpenAPI specs, Spring Boot code, database migrations, and UML diagrams—all from a single source of truth.

## What is QSDL?

QSDL (Schema-Definition Language) lets you define your domain model and API contracts in a concise, GraphQL-inspired syntax. It handles the repetitive scaffolding and keeps your API definitions consistent across tools and frameworks.

**Key features:**

- 📋 **Domain-centric**: Define types, relationships, and constraints in one place
- 🔄 **Multi-target generation**: Generate OpenAPI, Spring Boot, PostgreSQL, PlantUML, and more
- 🚀 **Auto CRUD**: A simple type definition automatically generates GET/POST/PUT/PATCH/DELETE operations
- 🎯 **Type-safe**: Built-in scalars, enums, composition, and validation rules
- 🔗 **Relationship modeling**: Express parent-child dependencies and composition patterns naturally

## Quick Start

### Requirements

- **Python 3.13+**

### Installation

**Using uv (recommended):**

```bash
# Install latest unreleased version directly from the repository
uv tool install git+https://github.com/henn1001/QSDL

# If you want to update a previously installed version
uv tool install git+https://github.com/henn1001/QSDL
uv tool upgrade qsdl
```

**For development:**

```bash
git clone https://github.com/henn1001/QSDL && cd qsdl && bash dev.sh init
```

## Usage

### Basic Example

```bash
echo "type Project { name: String }" > project.qsdl
qsdl generate openapi -i project.qsdl -o srcgen/
```

### CLI Options

```
qsdl generate GENERATOR -i INPUT [-o OUTPUT] [-c CONFIG ...] [-S KEY=VALUE ...]

Arguments:
  GENERATOR                   Builtin generator name or path to a custom generator.

Options:
  -i, --input PATH            Schema definition file (required).
  -o, --output PATH           Output folder. Default: 'srcgen/' next to the input file.
  -c, --config PATH           JSON config file. Repeatable; later files win.
  -S, --set KEY=VALUE         Override one config field. Repeatable; wins over files.
  --write-version             Write a .qversion file to the output folder.
```

```bash
# Override config fields directly, no file needed
qsdl generate spring -i project.qsdl -S title=MyApp -S database=NO

# Inspect and author configuration
qsdl config show spring
qsdl config init spring -o config.json
qsdl config validate spring -c config.json
```

For detailed usage and examples, see [CLI documentation](./docs/cli.md).

## Generator Overview

| Generator       | Purpose                  | Output                                        |
| --------------- | ------------------------ | --------------------------------------------- |
| **OpenAPI**     | REST API specification   | YAML/JSON OpenAPI 3.0+ document               |
| **Spring Boot** | Java backend scaffolding | Spring entities, DTOs, services, repositories |
| **PostgreSQL**  | Database schema          | SQL schema scripts                            |
| **PlantUML**    | Architecture diagrams    | PlantUML class/ER diagrams                    |
| **i18n**        | Internationalization     | Language resource files                       |
| **Void**        | Parse & validate only    | No output (useful for validation)             |

## Documentation

Complete documentation is available in the [`docs/`](./docs/) folder. Start with:

- **[Overview](./docs/overview.md)** — Comprehensive guide to QSDL concepts and workflows (start here!)
- **[Full Documentation Index](./docs/README.md)** — Complete navigation for all topics

**Quick links to key topics:**

- [Language overview](./docs/core/language.md) — Syntax and type definitions
- [CLI usage](./docs/cli.md) — Command-line reference
- [Basic data modeling](./docs/guides/basic-data-modeling.md) — Design best practices

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for local setup, validation, documentation conventions, and pull-request expectations.

## Examples

Find example schemas in [`examples/`](examples/). Each generator has working samples demonstrating features.

## Formal Specification

The complete QSDL grammar is specified in the TextX definition file:
[`src/qsdl/dsl/definition/entity.tx`](src/qsdl/dsl/definition/entity.tx)
