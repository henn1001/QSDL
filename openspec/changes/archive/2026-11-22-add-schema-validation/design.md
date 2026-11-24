# Design

## Context

`src/qsdl/dsl/textx.py` constructs a textX model, whose imports and references are resolved before object processors bind directives. QSDL then merges imported declarations and invokes `model_post_processor`. That processor validates declarations, resolves fields, validates arguments, completes operations, creates synthetic IDs and CRUD operations, and checks operation uniqueness. `src/qsdl/core.py` supplies the selected generator's directive definitions and invokes generation only after parsing and completion succeed.

## Goals / Non-Goals

**Goals:** Use the same QSDL rules in standalone validation and strict parsing. Keep diagnostic collection separate from CLI rendering and keep invalid models inside the analysis pipeline.

**Non-Goals:** No replacement parser, unresolved-reference recovery, editor transport, workspace buffer handling, or generator-specific validation mode for the new command.

## Decisions

### One pipeline, two error policies

Share the load, merge, validation, and completion code. Give individual QSDL checks a reporting interface: strict parsing raises on the first error and preserves the existing exception contract; validation records diagnostics and continues where inputs remain usable. Pass the policy through textX model parameters so imported object processors use the same policy and active directive definitions as the root. Do not catch one exception per validator: validators often have several independent checks inside the same loop.

Return diagnostics from standalone analysis, not a partially completed `Schema`. Represent each issue with a stable code, severity, message, and owning file and source span when known. Capture positions from the originating node before merging or synthesizing declarations; use related source declarations or a file-level location for synthetic elements. Leave unknown positions unset. Convert expected textX and input-loading failures into diagnostics at the analysis boundary; do not hide unexpected programming errors as invalid input.

### Continue by dependency, not by pass

Keep the existing stage order and track which facts are unavailable in collecting mode. A failed directive must not be treated as if the directive were absent: independent field checks can still run, but an invalid `@method` must not fall back to `GET` during validation. Resolve fields per type; an inheritance cycle or unresolved field conflict blocks checks that need that effective field set, not declaration checks on unrelated types. A bad import graph must not be used as a complete namespace, but already loaded declarations can still be checked locally where safe. When duplicate type declarations leave a reference ambiguous, do not derive dependent diagnostics from an arbitrary chosen type.

Keep operation collision checking for operations whose inputs are valid, including CRUD routes safely derived from valid objects. Do not use incomplete operations or field sets for collision checks. This preserves checks that depend on completion without feeding a partial schema to any generator or duplicating the route-derivation rules.

### Keep CLI integration at the edge

`qsdl validate` calls the diagnostics path with core definitions only. It renders the collected diagnostics sorted by file and source position with a stable tie-breaker, without resolving a generator plugin or opening an output directory. Reusing `generate void` would preserve its fail-fast path and tie analysis to generator setup. A later LSP can consume the structured diagnostics without parsing CLI text; editor locations and buffer-backed imports can be addressed in that change.

## Risks / Trade-offs

- **Incomplete feedback for syntax or unresolved references** → Return the blocking diagnostic and document that textX did not provide a linked model. Do not guess at downstream errors.
- **Cascade or missing diagnostics** → Test a bad directive beside unrelated violations, and test an invalid dependency next to a valid operation collision so neither false positives nor schema-wide suppression slip through.
- **Generation behavior drift** → Reuse strict mode through the existing entry point and run rule, directive, import, and generator regressions. No migration is needed; `validate` is additive.
