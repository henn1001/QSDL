# QSDL Documentation

This folder is intended to grow into a wiki-style documentation set that can later be published as a documentation website.

## Index

### Getting started
- [Overview](./overview.md)
- [CLI](./cli.md)

### Core (QSDL language)
- [Language overview](./core/language.md)
- [Directives](./core/directives.md)
- [Rules & requirements](./core/rules.md)

### Guides
- [Basic data modeling](./guides/basic-data-modeling.md)
- [Relationships](./guides/relationships.md)

### Generators
- [Generators overview](./generators/README.md)
- [OpenAPI](./generators/openapi/README.md)
- [Spring Boot](./generators/spring/README.md)
- [PostgreSQL](./generators/postgres/README.md)
- [PlantUML](./generators/plantuml/README.md)
- [Void (no-op)](./generators/void/README.md)
- [i18n](./generators/i18n/README.md)

### Reference
- [Glossary](./reference/glossary.md)
- [FAQ](./reference/faq.md)
- [Troubleshooting](./reference/troubleshooting.md)

## Conventions (for future docs)

- Prefer task-oriented pages (Overview  Prerequisites  Configuration  Usage  Examples  Troubleshooting).
- Keep generator-specific behavior under `docs/generators/<name>/`.
- Keep cross-generator and DSL invariants under `docs/core/` and `docs/rules/`.
