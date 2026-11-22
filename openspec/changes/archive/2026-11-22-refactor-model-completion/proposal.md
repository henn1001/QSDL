# Proposal

## Why

Model completion inserts inherited `Field` nodes into textX containment lists that do not own them. This obscures which fields were declared, makes traversal depend on processing order, and leaves validation and type reachability vulnerable to recursion in different graphs.

## What Changes

- Preserve declared field containment and expose a separate effective field view for validation and generation.
- **BREAKING (Python model API):** `Base.fields` and `Object.fields` will contain only source declarations. Callers that need inherited fields or generated IDs must use the effective view; callers that need the generation-visible subset must also account for `@ignore`.
- Reject circular `extends` chains with a semantic diagnostic before consumers inspect inherited fields. Make completion-time reachability and `@force-generate` propagation terminate on repeated Base references without promising generator support for recursive models.
- Separate field resolution, API completion, CRUD generation, and type selection in the post-processor. Keep DSL syntax, existing directive behavior, and generated output for valid supported schemas unchanged, except where PlantUML field lists change to follow resolved inheritance and `@ignore` semantics.

## Capabilities

### New Capabilities

- `model-field-resolution`: Define declaration ownership, effective field access, inheritance diagnostics, and the field view used for generation and type reachability.

### Modified Capabilities

None. The existing `directive-processing` requirements remain unchanged.

## Impact

- Centers on `src/qsdl/dsl/processors/model_parser.py` and its orchestration in `model_processor.py`; also affects DSL model classes, validators, and field traversal helpers.
- Migrate built-in generators and document the new field access contract for Python library and plugin callers.
- No changes to import resolution, directive binding, generator-specific flattening rules, or dependencies.
