# Proposal

## Why

QSDL parses a dedicated block of core directives before generic directives. A core directive after a custom one can be ignored or reported as a false duplicate; for example, `@path("run") @headers(X-Token: String) @method(POST)` currently produces a GET route. Generators also interpret opaque directives independently, without a way to declare their payload and owner rules to QSDL.

## What Changes

- Allow core and custom directives to be interleaved on the same declaration without changing their meaning.
- Reject repeated names at the second occurrence and malformed recognized core payloads at the offending directive. **BREAKING:** An unsupported `@method(TRACE)` that silently fell back to GET will now fail.
- Retain all attached directives, including synthetic ones, in one ordered collection per owner. Iteration, name lookup, typed lookup, and built-in accessors return the same attached node. Expose one canonical value per directive through `.directive` and the ordered collection. Represent defaults and inheritance with synthetic nodes.
- Let built-in and external generators opt in by declaring directive specs. Core binds and validates only the selected generator's declared names. Migrate all existing built-in generator directives: Spring's `@spring-package` and `@spring-controller`, and the `@spring`, `@openapi`, and `@postgres` scalar mappings. Preserve valid payload behavior and precedence. Generators with no directives need no definitions.
- **BREAKING (model API):** The collection no longer exposes unchecked list mutation. Name lookup can now return recognized core or generator nodes with typed values, not just opaque string values. For the selected generator, malformed payloads or unsupported owners for its declared names now produce errors.

## Capabilities

### New Capabilities

- `directive-processing`: Order-independent directive interpretation, identity-preserving lookup, and opt-in generator directive validation.

### Modified Capabilities

## Impact

The change affects the textX grammar, DSL model and processors, the generator plugin contract, and directive consumers in Spring, OpenAPI, and PostgreSQL. **BREAKING (model API):** Remove directive-backed owner attributes across all DSL models; consumers use canonical directive nodes instead. Generator tests verify scalar mapping compatibility and that equivalent directive permutations produce equivalent artifacts.
