# Schema Validation Specification

## Purpose

Validate a QSDL schema and its imports without generating artifacts, and report independent schema errors together so users can fix them in one pass.

## Requirements

### Requirement: Standalone core validation

`qsdl validate --input <path>` (short form `-i`) SHALL validate the root schema and its imports using core QSDL rules, without invoking a generator or writing artifacts. It SHALL exit zero if there are no errors and nonzero if there are errors.

#### Scenario: Valid multi-file schema
- **WHEN** a user validates a valid schema with relative imports
- **THEN** validation exits zero without writing generation output

#### Scenario: Generator-only directive
- **WHEN** a schema contains a syntactically valid opaque directive recognized only by a generator
- **THEN** standalone validation does not apply that generator's directive rules

### Requirement: Root-only server metadata

Semantic validation of `servers` SHALL apply only to the root schema. Imported `servers` values SHALL NOT be merged or semantically validated. Imported declarations SHALL still be validated, and syntax errors in any imported file SHALL still block analysis.

#### Scenario: Server metadata in an imported file
- **WHEN** an imported file has valid declarations and a syntactically valid `servers` list containing an unsupported URL
- **THEN** validation does not report a server URL error for the import
- **AND** validating the same file as the root reports the unsupported URL

### Requirement: Independent QSDL diagnostics

After the schema and its imports parse and link, standalone validation SHALL report independent QSDL rule violations together, including violations on separate nodes in the same validation pass. It SHALL NOT report a dependent violation based on a value or model relationship that failed validation.

#### Scenario: Independent violations in two files
- **WHEN** an imported declaration has an invalid core directive and two root declarations each contain duplicate fields
- **THEN** one invocation reports the invalid directive and both duplicate-field violations and exits nonzero

#### Scenario: An invalid method does not imply a route
- **WHEN** a custom operation has an invalid `@method` and would collide with another operation only if that invalid method were interpreted as `GET`
- **THEN** validation reports the invalid directive but does not report that route collision

#### Scenario: Collision in otherwise valid operations
- **WHEN** a declared operation conflicts with a generated CRUD operation and the model data needed to derive both routes is valid
- **THEN** standalone validation reports the route conflict without invoking a generator

### Requirement: Source attribution and ordering

The validation command SHALL render diagnostics in deterministic source order and identify the owning source file and position when available. When an issue has no source token, it SHALL identify the relevant declaration or file rather than invent a position.

#### Scenario: Imported directive location
- **WHEN** the second occurrence of a directive is in an imported file
- **THEN** the duplicate diagnostic identifies the imported file and the position of the second occurrence

### Requirement: Blocking front-end errors

If a root input, syntax, import-loading, or unresolved-reference failure prevents QSDL analysis, standalone validation and generation SHALL report a single diagnostic for the first blocking failure, exit nonzero, and skip downstream validation.

#### Scenario: Unresolved type blocks analysis
- **WHEN** textX cannot resolve a field's type
- **THEN** validation reports the unresolved reference and exits nonzero without reporting downstream errors inferred from the missing type

### Requirement: Strict generation boundary

Generation SHALL collect and report the same core schema diagnostics as standalone validation and SHALL also validate the selected generator's directive definitions. Generation SHALL require a fully completed schema; any schema error SHALL prevent generator invocation and artifact writing.

#### Scenario: Schema rejected before generation
- **WHEN** a schema contains errors that standalone validation reports
- **THEN** generation reports the same core errors without invoking the generator or writing its output
