# Tasks

## 1. Field resolution and validation

- [x] 1.1 Capture baseline generator output from the inheritance-and-override and deep Base flattening examples under `examples/02-nested-values/`, plus a relationship example under `examples/03-relations/`. Record the inputs and configurations so the same outputs can be compared after migration.
- [x] 1.2 Add ordered `effective_fields` and `generation_fields` views and resolve inherited declarations once per schema, before inherited-field validation in `model_processor.py`. Add rules tests for ownership, inherited order, shared diamonds, conflicting fields, type-changing overrides, and a source-located cycle error reached from an Object. Remove the old recursive resolver and `flattened` flags once their remaining consumers are migrated.
- [x] 1.3 Document the `.fields` compatibility break and the two new views in the library generation and plugin guides. Verify the documented field access against a completed schema with an inherited field, an ignored field, and a generated ID.

## 2. Post-processing stages

- [x] 2.1 Separate explicit operation completion, synthetic ID assembly outside `.fields`, and automatic CRUD generation. Make the unfiltered field view explicit for query and relationship discovery. Verify generated ID metadata, inherited query parameters, aggregation and composition routes, custom route defaults, and empty-API suppression with scoped tests.
- [x] 2.2 Replace repeated `is_used` scans and recursive force propagation with visited value-reference traversal, preserving force context and pre-ignore retention semantics. Add completion tests for reachable mutually referencing Bases with and without force generation, source versus synthetic directive identity, response-header references, and types reachable only through ignored fields.
- [x] 2.3 Stop rewriting declared fields for inheritance or `@ignore`. Verify that ignored overrides stay in the effective view but not the generation view, that filtering never resurrects the inherited field, and that generated IDs stay out of declaration walks.

## 3. Generator migration

- [x] 3.1 Migrate OpenAPI, Spring, PostgreSQL, PlantUML, and i18n renderers to the intended field views. Audit direct reads, shared traversals, and template helpers. Run focused generator tests covering inherited and ignored properties, relationships, and nested or opaque Base rendering, as applicable to each target.

## 4. Cross-target verification

- [x] 4.1 Regenerate the baseline examples and compare outputs, including field order, ID and query metadata, relationship routes, and PostgreSQL columns. Review any difference rather than hand-editing derived output.
- [x] 4.2 Run the configured format/lint checks and default pytest suite. Run scoped Spring integration cases such as `tests/e2e/c2_modeling/test_nested_base_flattening.py` and `tests/e2e/c3_advanced/test_query_filter_object.py` with the integration marker enabled; do not run the full integration suite.
