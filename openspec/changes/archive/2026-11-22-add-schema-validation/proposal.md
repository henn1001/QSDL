# Proposal

## Why

QSDL usually stops at the first schema error, so users must repeat validation after each fix. A standalone validation command should report independent errors together without generating artifacts.

## What Changes

- Add `qsdl validate -i <schema.qsdl>` for core QSDL validation, including imports. Report source-located diagnostics in a deterministic order and exit nonzero on errors.
- Collect independent QSDL rule violations after textX parses and links the schema. If syntax, import loading, or reference resolution blocks analysis, report the blocking failure; parser recovery and batching unresolved references are out of scope.
- Share QSDL's post-processing and validation rules across analysis and generation. Keep generation strict: only a fully completed, valid schema reaches a generator.
- Keep diagnostics independent of CLI formatting so a future QSDL language server can reuse them. This change does not ship an LSP or add generator selection to `validate`.

## Capabilities

### New Capabilities

- `schema-validation`: Standalone schema validation, diagnostic collection, and its blocking-error boundary.

### Modified Capabilities

None. Directive interpretation and field resolution retain their existing semantics.

## Impact

QSDL's textX adapter, import diagnostics, directive binding, and model processing will need changes. The CLI gains a command and documentation; `generate` and the existing `void` generator retain their contracts. No new parser or language-server dependency is required.
