# Tasks

## 1. Shared diagnostics and input loading

- [x] 1.1 Introduce structured diagnostics and strict/collecting reporting policies in `src/qsdl/dsl/`. Thread the policy through the existing textX entry point and imported models. Verify strict parsing still raises the expected exception type and collecting mode retains distinct source locations.
- [x] 1.2 Expose standalone analysis and translate expected textX syntax, import-loading, and unresolved-reference failures into blocking diagnostics. Add rule coverage for malformed root syntax, a missing import, and an unknown type in an imported file; verify that no dependent checks run.

## 2. QSDL rule collection

- [x] 2.1 Report directive and declaration violations at individual checks, including multiple violations in the same loop. Retain invalid directive state separately from absent directives. Test an imported malformed directive alongside two root field duplicates and verify duplicate-directive attribution to the second occurrence.
- [x] 2.2 Make import-graph and field-resolution checks continue where prerequisites are valid. Test that a cycle or field conflict does not hide an unrelated declaration error and that no dependent check consumes an ambiguous type or invalid effective field set.
- [x] 2.3 Apply dependency checks to argument and operation completion and check collisions among valid declared and generated operations. Test that an invalid method does not imply a default-route collision and that a valid declared-versus-CRUD collision is still reported beside an unrelated error.

## 3. Standalone CLI

- [x] 3.1 Add `qsdl validate -i/--input` in `src/qsdl/__main__.py` with deterministic rendering and core-only validation. Extend `tests/unit/test_cli.py` to verify success and failure exit status, multi-file path and position reporting, no plugin loading or artifact writes, and opaque generator-only directives.
- [x] 3.2 Document `qsdl validate` in `docs/cli.md`, including the blocking-error boundary and its difference from `generate void`. Verify the documented command against the existing multi-file example.

## 4. Cross-path regression

- [x] 4.1 Verify that `generate` still applies the selected generator's directives and rejects invalid schemas before generator invocation or file writes. Run Ruff and the default test suite for the shared DSL changes; if generated Spring behavior can be affected, run only the relevant isolated integration tests per `CONTRIBUTING.md` and `AGENTS.md`.
