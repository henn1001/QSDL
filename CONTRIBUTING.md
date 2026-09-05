# Contributing to QSDL

QSDL uses [uv](https://docs.astral.sh/uv/) for Python environments and dependency management.

## Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- A JDK and [Maven](https://maven.apache.org/) for integration tests that compile generated Spring Boot projects

## Set up a development environment

Clone the repository and initialize the project:

```bash
git clone https://github.com/henn1001/QSDL.git
cd QSDL
bash dev.sh init
```

`dev.sh init` runs `uv sync --all-extras` and creates local VS Code configuration files from the available templates. If you do not use VS Code, initialize the environment directly:

```bash
uv sync --all-extras
```

Use `uv run ...` to run commands in the project environment without activating the virtual environment.

## Repository layout

| Path                   | Purpose                                                                          |
| ---------------------- | -------------------------------------------------------------------------------- |
| `src/qsdl/`            | QSDL library and CLI implementation                                              |
| `src/qsdl/dsl/`        | Grammar, model types, parsing, and validation                                    |
| `src/qsdl/generators/` | OpenAPI, Spring Boot, PostgreSQL, PlantUML, i18n, and validation-only generators |
| `tests/rules/`         | Syntax, semantic, and logical DSL rule tests                                     |
| `tests/unit/`          | Small, isolated library and CLI tests                                            |
| `tests/functional/`    | Parser, processor, and generator behavior tests                                  |
| `tests/e2e/`           | Generated-output tests, including Spring Boot compilation tests                  |
| `examples/`            | Example schemas and representative generated output                              |
| `docs/`                | User and developer documentation                                                 |
| `dev.sh`               | Development command helpers                                                      |

For QSDL syntax and CLI usage, start with [`README.md`](README.md) and [`docs/README.md`](docs/README.md).

## Change workflow

1. Create a focused branch or change set.
2. Make the change in its source of truth.
3. Add or update the narrowest relevant test layer.
4. Run the applicable checks below and review the complete diff.
5. Open a pull request describing the change and validation performed.

For DSL semantics, validation, or documentation claims about constraints, read [`docs/core/rules.md`](docs/core/rules.md) first. Keep shared DSL behavior in `src/qsdl/dsl/`; keep target-specific mapping and rendering in `src/qsdl/generators/<generator>/`.

For generator changes, start with the matching sample in `examples/`. Update the schema, configuration, or generator source, then regenerate and review derived output; do not edit generated output by hand. See the [CLI documentation](docs/cli.md) for output and ignore-file behavior.

## Choose validation

| Change                               | Expected validation                                                               |
| ------------------------------------ | --------------------------------------------------------------------------------- |
| Python implementation                | Format, lint, and run the narrowest relevant test.                                |
| DSL syntax, semantics, or validation | Read `docs/core/rules.md` and add or update rules or functional coverage.         |
| Generator behavior                   | Run focused generator coverage and regenerate/review the matching example output. |
| Generated Spring Boot output         | Run the affected integration-marked tests; JDK and Maven are required.            |
| Documentation                        | Check affected links, examples, and `docs/README.md` when adding a page.          |

Run the default suite for broad or cross-cutting changes. Run integration-marked tests whenever the requested change can affect generated Spring Boot projects.

## Checks and useful commands

Run the project checks directly through `uv`:

```bash
# Format Python files
uv run ruff format

# Lint Python files
uv run ruff check .

# Run the default test suite; integration-marked tests are excluded
uv run pytest

# Run a focused test file or test selection
uv run pytest tests/rules/test_sem_field.py
uv run pytest -k relationship

# Run integration-marked tests
uv run pytest -m integration

# Build the Python package
uv build
```

The default pytest configuration writes test and coverage reports under `dist/`. The integration-marked end-to-end tests invoke Maven for generated Spring Boot projects, so they require a compatible JDK and Maven installation.

The helpers in `dev.sh` provide equivalent commands:

```bash
bash dev.sh lint
bash dev.sh test
bash dev.sh test-integration
bash dev.sh build
bash dev.sh clean
```

`dev.sh lint` calls `ruff` directly. If `ruff` is not already on your `PATH`, activate the project environment first or use the `uv run ruff ...` commands above.

## Python style

The authoritative lint configuration is in [`pyproject.toml`](pyproject.toml). In particular:

- Format with Ruff and keep lines readable within the configured 120-character limit.
- Keep imports sorted according to Ruff.
- Use Python 3.13 typing syntax and complete type annotations for new code.
- Use `snake_case` for functions, methods, variables, and modules; use `PascalCase` for classes.
- Use docstrings for public functions and classes. Follow the [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md) for docstring structure and general Python conventions.
- Use comments to explain non-obvious decisions or constraints, not obvious code.

For QSDL schemas, follow the naming and semantic rules in [`docs/core/rules.md`](docs/core/rules.md).

## Documentation changes

Keep documentation close to the behavior it describes:

- Core language rules and semantics belong in `docs/core/`.
- How-to material belongs in `docs/guides/`.
- Generator-specific behavior belongs in `docs/generators/<generator>/`.
- Reference material belongs in `docs/reference/`.
- Add relative links to related pages and update [`docs/README.md`](docs/README.md) when adding a page.

## Commits and pull requests

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), for example:

```text
feat(openapi): add support for response headers
fix(dsl): reject duplicate operation routes
docs: clarify generator configuration
```

QSDL follows [Semantic Versioning](https://semver.org/). Release automation uses the commit history to update the changelog and version metadata; contributors normally should not bump versions in feature or bug-fix commits.

Before opening a pull request, confirm that:

- the description explains the problem, approach, and validation performed;
- the change is focused and documented where necessary;
- relevant tests and lint checks pass;
- generated output has been regenerated and reviewed when applicable; and
- no temporary files, local configuration, or unrelated changes are included.

QSDL is distributed under the [Apache License 2.0](LICENSE).
