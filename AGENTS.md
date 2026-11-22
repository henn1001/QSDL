# QSDL

QSDL defines schemas and generates OpenAPI, Spring Boot, PostgreSQL, PlantUML, and i18n output. Its Python implementation is under `src/qsdl`.

- For language, CLI, or documentation work, use `docs/README.md` to find the relevant authoritative page.
- For DSL semantics, validation, or constraint claims, read `docs/core/rules.md`. Shared DSL behavior belongs in `src/qsdl/dsl/`; target-specific behavior belongs in `src/qsdl/generators/<generator>/`.
- For generator behavior, consult its page under `docs/generators/` and any matching sample under `examples/`. Change the schema, configuration, or generator source, then regenerate and review derived output.
- For validation by change type, follow `CONTRIBUTING.md#choose-validation`; `pyproject.toml` remains authoritative for tool configuration.
- Never run the entire integration tests at once (`pytest -m integration`) without authorization. Scoped and isolated tests are fine.
