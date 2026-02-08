# QSDL Documentation Index

Welcome! This is the comprehensive documentation for QSDL.

## Getting Started

**Start here if you're new to QSDL:**

- **[Overview](./overview.md)** — What QSDL is, why you'd use it, and common workflows
- **[CLI](./cli.md)** — Command-line usage and options

## Core Language & Semantics

Learn the QSDL language and how to write schemas:

- **[Language overview](./core/language.md)** — Complete syntax reference with examples (types, fields, scalars, enums)
- **[Rules & requirements](./core/rules.md)** — All semantic and validation rules (with rule IDs for reference)
- **[Directives](./core/directives.md)** — Complete directive reference with all 22+ annotations

## Practical Guides

Step-by-step guides for common tasks:

- **[Basic data modeling](./guides/basic-data-modeling.md)** — How to design effective domain models
- **[Relationships](./guides/relationships.md)** — Composition, aggregation, and entity patterns

## Generators

Code and spec generation for different targets:

- **[Generators overview](./generators/README.md)** — How generators work and common patterns
- **[OpenAPI](./generators/openapi/README.md)** — REST API specification generation
- **[Spring Boot](./generators/spring/README.md)** — Java backend scaffolding
- **[PostgreSQL](./generators/postgres/README.md)** — Database schema generation
- **[PlantUML](./generators/plantuml/README.md)** — Architecture and ER diagrams
- **[i18n](./generators/i18n/README.md)** — Internationalization resources
- **[Void](./generators/void/README.md)** — Validation-only generator

## Reference

Quick lookup and troubleshooting:

- **[Glossary](./reference/glossary.md)** — Key terms and concepts
- **[FAQ](./reference/faq.md)** — Frequently asked questions
- **[Troubleshooting](./reference/troubleshooting.md)** — Common issues and solutions

## Documentation Conventions

These guidelines help keep the docs consistent and maintainable:

- **Structure:** Prefer task-oriented pages with sections like Overview → Prerequisites → Configuration → Usage → Examples → Troubleshooting
- **Location:** 
  - Core language rules and semantics go in `docs/core/`
  - Practical how-to guides go in `docs/guides/`
  - Generator-specific behavior goes in `docs/generators/<generator_name>/`
  - Reference material (glossary, FAQ, troubleshooting) goes in `docs/reference/`
- **Linking:** Use relative paths; future doc site generation tools will handle the conversion
