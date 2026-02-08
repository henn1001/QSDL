# AGENTS.md

Agent-focused notes for working in this repository. Keep changes small, run the relevant checks, and follow existing conventions.

## Agent Workflow Rule

When tasked with a new implementation:
- Do not add new tests on your own.
- Do not run tests on your own.
- For larger/complex changes, finish the implementation first, then ask once whether the user wants to add tests and/or run tests.
- IMPORTANT: if changing DSL behavior, generators, or documentation claims about constraints, first check and respect `docs/core/rules.md`.

## Project Scope & Layout

QSDL is a Schema Definition Language (GraphQL-inspired) and code/spec generator.
Primary responsibilities of this repo:
- Parse `.qsdl` schema files into a Python object graph (TextX-based DSL).
- Validate/post-process the model (processors).
- Generate outputs via generators (OpenAPI, Spring Boot, PlantUML, etc.) using Jinja2 templates.

High-level layout:
- `src/qsdl/`: library + CLI entrypoint.
- `src/qsdl/dsl/`: grammar, AST models, parsing, processors.
- `src/qsdl/generators/`: generator implementations + templates.
- `examples/`: sample schemas/configs + generated example outputs.
- `tests/`: unit/functional/e2e coverage.
- `docs/`: documentation (wiki-style Markdown; intended to be publishable as a doc site later).

## Documentation (docs/)

The documentation is maintained under `docs/` and is intended to be:

- **Wiki-like**: many small pages with stable links, not one large README.
- **Future site-ready**: structure should map cleanly to static-site tools (e.g., a sidebar/tree based on folders).

Guidelines for doc changes:

- Keep the entrypoint at `docs/README.md` as the index.
- Prefer task-oriented pages (Overview → Prerequisites → Configuration → Usage → Examples → Troubleshooting).
- Put DSL semantics and invariants under `docs/core/` (rules, language, directives).
- Put generator-specific behavior under `docs/generators/<name>/`.
- When moving/renaming pages, keep old links working where practical (add a small stub page pointing to the new location).

Generator quick map:
- `src/qsdl/generators/openapi/`: OpenAPI YAML generation.
- `src/qsdl/generators/spring/`: Spring Boot generation (largest surface area; DTO/entity/service/etc.).
- `src/qsdl/generators/plantuml/`: PlantUML diagrams.
- `src/qsdl/generators/postgres/`: PostgreSQL schema (SQL migration) generation.
- `src/qsdl/generators/void/`: No-op generator (useful for parsing/validation only).
- `src/qsdl/generators/i18n/`: i18n resource generation.

When changing behavior, think in this order:
1) DSL model rules (processors/util) should be correct and generator-agnostic.
2) Generator-specific mapping/rendering belongs in `generators/*`.
3) Keep templates deterministic (avoid embedding business logic in Jinja2 where a helper would do).

Where to implement changes (examples):
- Schema invariants/validation (e.g. forbid ambiguous relations, enforce @override rules): `src/qsdl/dsl/processors/*` or `src/qsdl/dsl/util.py`.
- Generator-only mapping (e.g. how a Scalar maps to OpenAPI schema vs Spring type): `src/qsdl/generators/<gen>/`.
- Output layout/boilerplate changes (e.g. package structure, annotations, filenames): generator templates under `src/qsdl/generators/<gen>/template/`.

## Common Entrypoints

- CLI app: `src/qsdl/__main__.py` (Typer entrypoint; exposed as `qsdl`).
- Generation workflow: `src/qsdl/core.py`.
- Parsing/building the DSL model: `src/qsdl/dsl/textx.py:parse_schema`.

## DSL Glossary (Core Model Terms)

This is the vocabulary used across processors and generators.

- `Schema`: root of a parsed `.qsdl` file set; contains metadata (title/version/servers/description) and all defined types.
- `Type`: umbrella concept for all definable elements in a schema (Scalar/Enum/Base/Object/Api).
- `Scalar`: primitive-ish leaf type. Builtins include `Int`, `Long`, `Float`, `Double`, `String`, `Boolean`, `Date`, `Datetime`, `Object`, `Void`.
  - Generators often map scalars to target types; scalars can be overridden via generator directives (see `get_type_override`).
- `Enum`: closed set of string values. Intended for constrained domain/state fields.
- `Base`: reusable structural type that holds `Field`s; used for shared shapes and inheritance (e.g. common audit fields).
- `Object`: primary domain entity type; typically drives CRUD generation and relationship modeling.
- `Field`: named attribute on a `Base` or `Object` with a value type (Scalar/Enum/Base/Object), plus modifiers/directives.
  - Common flags seen in code: required (`!`), array (`[...]`), relation markers (composition/aggregation), visibility (`hidden`), layer control (`transient`/`ignored`), io (`readOnly`/`writeOnly`), query param (`query`).
- `Api`: container for custom endpoints/operations; can also appear under an `Object` to override default CRUD behavior.
- `Operation`: a single API endpoint definition (method/path/params/return type), usually with directives like `@path`, `@method`, `@produce`, `@consumes`, `@pagination`, `@generate`.
- `Argument`: operation parameter definition (name + type). In generators this becomes body/path/query/header parameters depending on directives and/or naming rules.
- `Directive`: annotation attached to many entities (Schema/Type/Field/Operation/etc.) used to steer generation.
  - Some directives are generic DSL semantics (`@override`, `@ignore`), others are generator-specific (`@openapi(...)`, `@spring(...)`).

Practical guidance:
- Prefer implementing DSL invariants in processors/utilities; keep generator mapping rules inside the generator.
- When you need “all X in the schema”, use `xtx.get_children_of_*` instead of local traversal.

## Quick Commands (uv/pytest/ruff)

This repo targets Python 3.13+ and uses `uv` for dependency management.

```bash
# Install/sync dependencies
uv sync

# Run all tests (default: excludes "integration" marker)
uv run pytest

# Run a single test file
uv run pytest tests/functional/test_specifics_spring.py

# Run a single test (node id)
uv run pytest tests/functional/test_specifics_spring.py::TestSpecificsSpring::test_specifics_14 -v

# Run tests matching a substring
uv run pytest -k type_overrides

# Include integration tests (overrides addopts marker selection)
uv run pytest -m integration

# Lint (ruff)
uv run ruff check .

# Auto-fix what ruff can
uv run ruff check . --fix

# Format (if formatter is enabled for your ruff version)
uv run ruff format .
```

Notes:
- Pytest config lives in `pyproject.toml` (`[tool.pytest.ini_options]`) and writes reports to `dist/tests/`.
- Ruff config lives in `pyproject.toml` (`line-length = 120`, lint selects include `I` import sorting and `ANN` typing rules).

## Local Generation Smoke Tests

The CLI entrypoint is `qsdl` (see `[project.scripts]` in `pyproject.toml`).

```bash
# Generate OpenAPI
uv run qsdl examples/openapi/input.qsdl -g openapi -o srcgen/

# Spring generator example outputs
uv run qsdl examples/spring/relation.qsdl -g spring -o examples/spring/basic_layout
uv run qsdl examples/spring/relation.qsdl -g spring -c util/domain_config.json -o examples/spring/domain_layout
```

Useful:
- The schema language reference is described in `README.md`.
- The TextX grammar lives at `src/qsdl/dsl/definition/entity.tx`.

## Code Style Guidelines

### Formatting

- Target 120 char lines (ruff configured; `E501` ignored, but keep readability).
- Use f-strings for logging/strings where appropriate, but prefer logger formatting (`log.info("%s", value)`) to avoid eager formatting.
- Prefer small, pure helper functions when transforming the DSL model.

### Imports

- Follow ruff/isort (`I`) ordering: stdlib, third-party, local.
- Prefer `from collections.abc import ...` over `typing` for runtime types.
- In-module aliases:
  - `import qsdl.dsl.textx as xtx` is the canonical alias for textX helper/proxy access.

### Typing

- Use Python 3.13 type syntax (`X | Y`, `list[str]`, `dict[str, T]`).
- Keep return types accurate; many utilities intentionally return `None` when absent.
- Prefer narrow unions (see `ValueType` in `src/qsdl/dsl/util.py`) over `Any`.

### Naming

- Python: `snake_case` functions/vars, `PascalCase` classes.
- QSDL schema constraints (from project docs):
  - Type names (`Object`, `Base`, `Enum`) should be `PascalCase`.
  - Enum values should be `ALL_CAPS`.

### Error Handling & Logging

- Use `log = logger.getLogger(__name__)` and `log.info/warning/error`.
- Raise specific exceptions where feasible; this codebase currently uses `Exception` in a few places for DSL validation.
- When validating schema invariants:
  - Log an error message that includes the conflicting entities.
  - Then raise to abort generation (don’t continue with an inconsistent model).

### File/Path Handling

- Use `pathlib.Path` for paths.
- Use explicit encoding (`utf-8`) when reading/writing text files.

## DSL Parsing & Model Traversal

### `src/qsdl/dsl/textx.py` get_children_* proxies

Intent: provide typed wrappers around `textx.model.get_children_of_type(...)`.

Why it exists:
- TextX returns untyped lists (and the type name is passed as a string).
- These proxy helpers centralize the string type names (e.g. `"Field"`, `"Object"`) and give static typing to callers.

How to use:
- Prefer these wrappers over calling `textx.model.get_children_of_type` directly.
- They operate on the fully parsed (and post-processed) `dsl.Schema` object graph.

Common patterns:
- Walk the full schema for a given DSL node kind:
  - `xtx.get_children_of_field(schema)` to find all fields globally.
  - `xtx.get_children_of_operation(schema)` to find custom API ops.

### `src/qsdl/dsl/util.py` helpers

This module contains higher-level, domain-aware helpers built on top of the parsed DSL model.

Key helpers and their intent:
- `get_directive_of_name(name, entity)`:
  - Fetches the first directive match by name; use for optional directives.
- `get_type_override(entity, directive, keys)`:
  - Parses generator-specific scalar overrides from directives.
  - Important: override parsing splits by `", "` (comma+space). Do not change delimiter lightly.
- `map_custom_type(entity, mapping, default, directive, args, arg_picker="type")`:
  - Generic mapping for generator type conversions; scalar directives can override mapping.
- Relationship helpers (require a schema because they search globally):
  - `get_parents(schema, obj)` uses `xtx.get_children_of_field(schema)` to find fields whose value is `obj`.
  - `get_compositions(schema, obj)`/`get_aggregation(schema, obj)` filter those parents by relation kind.
  - `get_composition_fields(schema, obj_name)` finds array relationship fields pointing to an object name.
- Inheritance/flattening helper:
  - `get_all_fields_as_list(entity)` recursively merges fields from supertypes and enforces `@override`.
  - If a child redefines an inherited field without `@override`, it logs an error and raises.
- Traversal helper:
  - `traverse_fields(entity, predicate, ...)` is a generic recursive scanner over fields (optionally nested).
  - Use it to answer questions like “does this object contain any readOnly fields?” without duplicating loops.

Guidance:
- Prefer `util.py` helpers when implementing generators/processors; they encode project rules.
- When adding new helpers, keep them side-effect free unless they are explicitly validators.

## Testing Guidance

- Tests live under `tests/` with unit, functional, and e2e coverage.
- Default pytest run excludes integration tests (`-m 'not integration'` in `pyproject.toml`).
- When fixing a bug, add/adjust the narrowest test:
  1) unit (`tests/unit`) for pure functions,
  2) functional (`tests/functional`) for schema/model behavior,
  3) e2e (`tests/e2e`) for generation outputs.
