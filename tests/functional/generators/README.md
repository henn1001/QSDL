# Functional generator tests

Generator-output assertions have an explicit target owner:

- `openapi/` contains direct OpenAPI assertions and `openapi_test_utils.py`.
- `spring/` contains direct Spring assertions. Until WP-10 moves the existing
  modules, new Spring tests may import `SpringTestUtils` from
  `tests.functional.generators.spring`.
- `postgres/` is reserved for PostgreSQL-only rendering details. The existing
  SQL snapshots remain owned by E2E scenarios unless a detail cannot be tested
  there.

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
