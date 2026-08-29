# Functional generator tests

Generator-output assertions have an explicit target owner:

- `openapi/` contains direct OpenAPI assertions and `openapi_test_utils.py`.
- `spring/` contains direct Spring assertions and exports `SpringTestUtils` from
  `tests.functional.generators.spring`.
- `postgres/` is reserved for PostgreSQL-only rendering details. The existing
  SQL snapshots remain owned by E2E scenarios unless a detail cannot be tested
  there.

## PostgreSQL ownership

The 29 PostgreSQL snapshots in the current cross-generator scenarios remain in
`tests/e2e/` and are not copied into `tests/functional/generators/postgres/`:

- `tests/e2e/c1_basics/`: basic scalar types, scalar arrays, custom scalar
  mappings, enum constraints, and required/unique columns (5 snapshots).
- `tests/e2e/c2_modeling/`: default and nested flattening, repeated and mixed
  Base fields, opaque JSONB storage, Base arrays, flattening constraints, and
  transient fields (11 snapshots).
- `tests/e2e/c5_relations/`: one-to-one and one-to-many foreign keys, nested
  relationships, composition and aggregation chains, mixed relations, and
  multiple parents (7 snapshots).
- `tests/e2e/c6_complex/`: combined object graphs, mixed Base/Object arrays,
  deep flattening, opaque nested Bases, and scalar-object arrays (6 snapshots).

These assertions are intentionally cross-generator: each scenario exercises
OpenAPI, Spring, and PostgreSQL output for the same model, while the SQL
expectation checks the PostgreSQL rendering. There is currently no
PostgreSQL-only detail that needs a direct functional test, so the PostgreSQL
functional package contains only its package marker. A future direct test
belongs there only for an isolated PostgreSQL rendering contract that cannot
fit naturally in an existing E2E scenario; it must not duplicate these
relation or flattening expectations.

The SQL checks in `generators/spring/test_entity_metadata.py` are ancillary to
that Spring entity-metadata scenario (they verify system timestamp aliases are
not emitted twice) and do not establish a second PostgreSQL test owner.

OpenAPI tests must use the target-specific helper rather than a generic wrapper:

```python
from tests.functional.generators.openapi import generate_openapi


def test_openapi_output(tmp_path: Path) -> None:
    openapi = generate_openapi(schema, tmp_path)
```

`generate_openapi` requires the caller to provide a temporary output directory,
generates `openapi.yaml` there, and loads that YAML into a mapping. It never
uses the repository-level `srcgen/` directory. Existing root tests and generic
wrappers remain temporarily for the later migration work packages; do not add
new imports of those wrappers.

## Directive and description ownership

The final ownership split established by WP-04 is:

- **Core language/rules:** directive parsing and validation are owned by `tests/rules/`, with the existing
  void-based directive tests retaining their composition and opaque coverage. In particular, query field semantics,
  relationship validity, duplicate directives, and inheritance overrides are not OpenAPI tests.
- **E2E scenarios:** query-filter output is owned by `tests/e2e/c3_advanced/test_query_filter_object.py`; custom
  operation payload/path behavior is owned by `tests/e2e/c3_advanced/test_operation_payload.py`. Positive relation
  output remains in the legacy directive test until the c5 E2E target assertions are implemented by WP-07.
- **Direct OpenAPI (final WP-09 location):** `@hidden`, `@readOnly`, `@writeOnly`, `@default`, `@ignore`,
  `@force-generate`, namespace-to-tag rendering, and rendering-specific `@path`/`@method` behavior. Rendered
  descriptions also remain direct OpenAPI assertions. These assertions currently remain in the legacy root files
  until WP-09 moves them under `generators/openapi/`.
- **Language descriptions:** empty-description rejection is generator-independent and is owned by
  `tests/rules/test_description.py`; rendered description output remains OpenAPI-specific.
