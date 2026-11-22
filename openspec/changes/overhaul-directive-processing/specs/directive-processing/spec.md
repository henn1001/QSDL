# Spec Delta

## Purpose

Define how QSDL retains, looks up, and interprets core and extension directives on a declaration, including definitions supplied by the selected generator.

## ADDED Requirements

### Requirement: Order-independent directive interpretation

QSDL SHALL interpret each recognized directive on its supported declaration regardless of its position relative to other directives. Reordering valid directives SHALL preserve effective model values and generated behavior, while the collection reflects the new source order.

#### Scenario: Custom operation with interleaved directives
- **WHEN** an operation declares `@path("run") @headers(X-Token: String) @method(POST)` in any order
- **THEN** it generates a POST route at `/run` with the `X-Token` response header

#### Scenario: Field override after an extension directive
- **WHEN** a field redefines an inherited field and declares `@custom @override`
- **THEN** it replaces the inherited field and retains `@custom`

#### Scenario: Namespace after a Spring package directive
- **WHEN** an object declares `@spring-package("pkg") @namespace("Domain")` or the reverse
- **THEN** its effective namespace is `Domain` and Spring uses the same package in both cases

### Requirement: Ordered attachment and node identity

QSDL SHALL retain each source directive on its owner in declaration order, including recognized directives. Enumeration, name lookup, typed lookup, and built-in accessors SHALL return the same attached node when they resolve the same occurrence. Typed lookup SHALL require the node's bound definition, not only a matching name.

#### Scenario: Built-in access returns the attached node
- **WHEN** an object declares `@spring-package("pkg") @namespace("Domain")`
- **THEN** the namespace accessor, typed namespace lookup, name lookup, and the second collection entry all return the same node with the decoded string value `Domain`

#### Scenario: Present and absent flag directives
- **WHEN** a field declares `@readOnly` and omits `@writeOnly`
- **THEN** the read-only accessor and typed lookup return the same attached flag node with boolean value `True`, the write-only accessor and typed lookup return `None`, and the effective flags reflect presence

#### Scenario: Core name on a different declaration
- **WHEN** a scalar declares `@namespace("Domain")`, a name recognized as core on other declaration kinds
- **THEN** name lookup returns the opaque node with its normalized value `Domain`, and typed namespace lookup does not return it

### Requirement: Synthetic directive attachment

QSDL SHALL expose synthetic directives through the same collection and lookup paths as source directives and distinguish their origin. Attaching a synthetic directive SHALL append a new node owned by its recipient and SHALL reject duplicate names, unsupported owners, and invalid typed values. Attachment SHALL NOT reorder source directives.

#### Scenario: Inherited force generation
- **WHEN** force generation propagates to a referenced base or enum that has no `@force-generate`
- **THEN** the recipient gains its own synthetic node, accessible by iteration and lookup, and the original annotation stays on its owner

#### Scenario: Recipient already has the directive
- **WHEN** force generation reaches a recipient that already declares `@force-generate`
- **THEN** propagation leaves the original source node in place and does not attach a second node

### Requirement: Canonical directive values

QSDL SHALL expose directive-backed values only through the attached nodes, with no parallel attributes on any owner. In a completed schema, source nodes SHALL expose normalized and resolved values while retaining source location and order. Defaults, inherited values, and directive-backed settings on generated owners SHALL be represented by synthetic nodes when no source node supplies the value. A directive with no source occurrence or applicable default or inheritance SHALL remain absent.

#### Scenario: Route completion exposes canonical nodes
- **WHEN** an operation declares `@path("run")` and omits `@method`
- **THEN** `.directive.path.value` is `/run` on the source node and `.directive.method.value` is `GET` on a synthetic node

#### Scenario: API namespace inheritance
- **WHEN** an object has a namespace and its API omits `@namespace`
- **THEN** the API exposes the inherited value on its own synthetic namespace node; an explicit API namespace remains a source node and retains precedence

#### Scenario: Response header type is resolved against imports
- **WHEN** `@headers` names a type declared in an imported schema
- **THEN** the completed operation exposes the resolved header type in `.directive.headers.value`, with no separate response header attribute

### Requirement: Selected generator directive definitions

Any built-in or external generator MAY declare directive definitions. QSDL SHALL bind and validate exact names from the selected generator for that invocation, reject definitions that conflict with built-in names or each other, and leave names not recognized in that invocation opaque with their existing normalized payloads. A generator with no definitions SHALL run with only the built-in DSL definitions active.

#### Scenario: Spring typed lookup returns the attached node
- **WHEN** Spring is selected and a supported owner declares `@spring-package("pkg")`
- **THEN** typed package lookup returns the original attached node with value `pkg` and Spring applies its existing package precedence

#### Scenario: Inactive definitions and undeclared names remain opaque
- **WHEN** a schema declares `@spring-package("pkg")` without selecting Spring, or declares `@spring-pakage("pkg")` with Spring selected
- **THEN** name lookup returns the opaque node and no typed Spring definition is bound to it

#### Scenario: Selected generator rejects malformed or misplaced directives
- **WHEN** a name declared by the selected generator has a malformed payload or appears on an unsupported owner
- **THEN** QSDL reports a semantic error at that directive before invoking generation

#### Scenario: Conflicting definitions
- **WHEN** the selected generator declares a built-in name or declares the same name twice
- **THEN** QSDL rejects the conflicting definitions instead of binding the directive ambiguously

#### Scenario: Generator has no definitions
- **WHEN** a generator with no directive definitions is selected for a schema with core and generator-specific directives
- **THEN** core directives still take effect, and the generator-specific directives remain opaque

### Requirement: Built-in generator directive coverage

Each built-in generator that interprets its own directives SHALL declare and retrieve those directives through the shared mechanism. Valid directives SHALL retain their existing effects and precedence, including Spring package and controller selection and Spring, OpenAPI, and PostgreSQL scalar mappings.

#### Scenario: One scalar declares mappings for several targets
- **WHEN** a scalar declares `@spring("UUID") @openapi("string, format: uuid") @postgres("UUID")` in any order and QSDL generates each target in turn
- **THEN** only the selected target's mapping is bound on each invocation, the other two nodes remain opaque, and each target produces the same mapping regardless of directive order

#### Scenario: Scalar mapping options retain their effects
- **WHEN** a scalar supplies Spring `entity` or `pattern` options, or OpenAPI `format` or `pattern` options
- **THEN** the selected generator uses those options with the existing mapping and fallback behavior

#### Scenario: Malformed scalar mapping is rejected for the selected target
- **WHEN** a scalar declares a bare `@openapi`, an unquoted `@openapi(string)`, an empty mapped type, or an unknown or malformed key-value option and OpenAPI is selected
- **THEN** QSDL reports a semantic error at `@openapi`

### Requirement: Duplicate directive diagnostics

QSDL SHALL reject a repeated exact directive name on the same declaration and report the location of its second occurrence.

#### Scenario: Duplicate with a custom directive between occurrences
- **WHEN** an imported object declares `@namespace("One") @custom @namespace("Two")`
- **THEN** QSDL reports a semantic error at the second `@namespace` in the imported file

### Requirement: Shared directive syntax

QSDL SHALL accept a bare `@name` or `@name(payload)` and distinguish a bare name from empty parentheses. A closing parenthesis inside a single- or double-quoted string SHALL NOT end the payload. Each recognized directive definition governs its own payload syntax; opaque directives need only fit the shared syntax. Unquoted nested parentheses are not part of that syntax.

#### Scenario: Different payload forms on one operation
- **WHEN** an operation declares `@path("run") @headers(X-Token: String) @method(POST)`
- **THEN** QSDL decodes a quoted path, a header declaration, and an unquoted method token without requiring a common payload type

#### Scenario: Opaque payload does not need to match a known form
- **WHEN** an undeclared directive has a well-formed payload such as `@custom(left => right)`
- **THEN** QSDL retains the opaque value `left => right`

### Requirement: Recognized core payload validation

QSDL SHALL reject a malformed payload for a recognized core directive with a semantic error at the directive, rather than treating it as an extension or falling back to a default.

#### Scenario: Unsupported method
- **WHEN** an operation declares `@method(TRACE)`
- **THEN** QSDL reports a semantic error at `@method` instead of generating a GET route

#### Scenario: Quoted value where a token is required
- **WHEN** an operation declares `@method("POST")`
- **THEN** QSDL reports a semantic error at `@method` because the definition requires an unquoted token

#### Scenario: Parentheses on a flag
- **WHEN** a field declares `@readOnly()`
- **THEN** QSDL reports a semantic error at `@readOnly`

#### Scenario: Unsupported CRUD token in generate list
- **WHEN** a standalone or object `extend api` declares `@generate("INVALID")`
- **THEN** QSDL reports a semantic error at `@generate`

### Requirement: Supported core payloads remain valid

QSDL SHALL preserve existing core payload forms, including signed integers, single- and double-quoted strings with escaped quotes, and empty quoted-string lists for `@generate()`.

#### Scenario: Explicit zero and empty string
- **WHEN** a field declares `@minSize(0)` and `@default("")`
- **THEN** its typed minimum size is zero and its typed default is the empty string

#### Scenario: Closing parenthesis in a quoted string
- **WHEN** an operation declares `@path('run(test)')`
- **THEN** QSDL uses the entire quoted string as the path payload

#### Scenario: Empty generation list
- **WHEN** an API declares `@generate()`
- **THEN** QSDL accepts it as an empty list
