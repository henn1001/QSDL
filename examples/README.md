# Examples

QSDL examples are split into one generated gold project and source-only Spring smoke cases.

## Canonical project

[`00-pet-store/`](00-pet-store/) is a multifile Pet Store schema and generated Spring Boot project. It demonstrates namespaces, CRUD and custom operations, enums, audit fields, value bases, opaque values, relations, OpenAPI, and Flyway output. Generated output is checked in. See the Pet Store README for [regeneration instructions](00-pet-store/README.md#regenerate-in-place) and [which files are hand-maintained](00-pet-store/README.md#generated-versus-hand-maintained-files).

## Spring smoke matrix

The numbered directories contain source-only schemas and optional case-local `config.json` files:

| Directory | Coverage |
| --- | --- |
| `01-basics` | scalar, enum, constraint, scalar visibility |
| `02-nested-values` | bases, flattening, opaque and transient values |
| `03-relations` | nested objects, composition and aggregation |
| `04-apis` | custom operations and Spring directives |
| `05-complex` | multifile imports, no database, long identifiers |
| `06-dto-selection` | selective request/response DTOs |

Run the bounded Spring generation and Maven compilation matrix (requires `qsdl` and Maven):

```bash
python examples/run-spring-smoke.py --list
python examples/run-spring-smoke.py
```

Disposable projects and logs are written below ignored `xtmp/examples-spring-smoke/`. PlantUML and i18n are intentionally not part of this runner; those targets are covered by functional and end-to-end tests.
