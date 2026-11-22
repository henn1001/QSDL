# Design

## Context

`src/qsdl/dsl/processors/model_processor.py` orchestrates post-processing of the linked, merged schema. `model_parser.py` currently completes declared operations, mutates field containment, builds CRUD operations, propagates force generation, and prunes fields and types. Some validators resolve inherited fields before the circular-supertype check. The built-in generators consume the already-pruned model. See `proposal.md` and `specs/model-field-resolution/spec.md` for the intended contract.

## Goals / Non-Goals

**Goals:** Give each post-processing pass an explicit input view. Resolve inheritance once per type, preserve declaration identity and source locations, and keep existing generator behavior except for PlantUML field-list differences required by resolved inheritance and `@ignore` semantics.

**Non-Goals:** No new recursive value-type support in renderers, no import or directive binding overhaul, and no general renaming or module splitting in `processors/`.

## Decisions

### Keep declaration containment separate from resolved views

`Base.fields` and `Object.fields` stay grammar-owned. Expose ordered read-only sequences as `effective_fields` and `generation_fields` on the completed model. The effective view contains resolved declarations and, after validation, the generated Object ID. The generation view filters the effective view by `@ignore`. Keep synthetic IDs owned by their Object but outside declaration containment. Inherited entries refer to the original `Field` rather than copies, preserving directive attachment and diagnostics.

A schema-local resolver processes the `extends` graph in parent-first order and records completed results by node identity. Detect an active-path revisit and report the cycle before inherited-field validation. Preserve the existing merge order, shared-node diamond handling, and override diagnostics. Do not resolve on every property access or keep a compatibility alias on `.fields`: either would hide which semantics the caller requested, and lazy recursion would repeat diagnostics or work.

### Render resolved fields in PlantUML

Use `generation_fields` for diagram field lists instead of resolving inheritance again in the renderer. A field shared through a diamond appears once. A local `@override` replaces all inherited candidates of that name. An effective `@ignore` field is omitted whether declared or inherited, and an ignored override does not restore a replaced field. Output differences that follow these field-list rules are intentional; unrelated PlantUML output and other generators' output remain unchanged for valid supported schemas.

### Make completion order explicit in `model_processor.py`

1. After import merge and directive binding, validate declared structure and resolve inheritance before reserved-name and Base-argument checks that need effective fields. Validate reserved metadata names before adding IDs.
2. Complete declared operations, including normalized routes, argument placement, and resolved response-header types. Then add synthetic ID metadata and build CRUD using the unfiltered effective field view. Keep existing API suppression, generation selection, and relationship behavior.
3. Select the types to retain using the completed, unfiltered model. Expose the filtered view to generators, then keep final operation name and route checks on the completed operations.

Rename or extract functions in `model_parser.py` along these boundaries. Keep CRUD builder logic and directive defaults intact. Merely moving all builders into new modules would not make their dependencies explicit.

### Walk value references once for type selection

Seed reachability from Object effective fields, operation return types, arguments, resolved response headers, and explicit `@force-generate` roots. Follow Base effective field values to other Bases or Enums. Track visits by node identity. Distinguish ordinary reachability from force propagation: a previously reachable Base must still be expanded in force mode when reached by a forced path. Preserve explicit directive nodes; attach a synthetic force directive only where absent. Do not treat `extends` edges as generation roots or change the retention policy for otherwise unused supertypes. Calculate the retained set before updating the generation type inventory.

This replaces repeated per-candidate scans and unguarded recursion. A visited set on the inheritance graph alone cannot protect value reference traversal, and moving ignore filtering ahead of reachability would change which types survive.

## Risks / Trade-offs

- Missed consumer migration → Audit both direct `.fields` reads and textX field walks, including generator helpers and templates. Declaration validators and binding walks continue to use containment; generator projections use generation-visible fields. Helpers shared by CRUD and renderers must select the view explicitly where their semantics diverge.
- Phase drift → Assert that query and relationship discovery for CRUD and reachability still see the unfiltered view, while generator-side traversals use the filtered view. Cover ignored overrides and types reachable only through ignored fields.
- Recursive value types beyond completion → Scope the termination guarantee to field resolution and type selection; do not add target-specific recursive rendering changes.

## Migration Plan

Migrate core consumers and all built-in generators in the same change. Document `.fields`, `effective_fields`, and `generation_fields` for library and plugin callers. Compare generated output on existing examples before and after the migration. No schema or stored-data migration is needed; reverting the code change restores the previous Python field contract.
