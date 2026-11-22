# Model Field Resolution

## Purpose

Define what fields a type declares, how QSDL resolves inherited fields, and which fields validators and generators consume.

## ADDED Requirements

### Requirement: Declared field ownership

The completed Python model SHALL expose only source-declared fields in each Base or Object's `.fields`, in source order. Each declaration SHALL retain its original owner, including when inherited or marked `@ignore`.

#### Scenario: Inherited and ignored declarations
- **WHEN** a child inherits a field from a Base and declares its own ignored field
- **THEN** the child's `.fields` contains the ignored declaration but neither the inherited declaration nor a generated ID
- **AND** the Base's field still belongs to the Base

### Requirement: Effective inheritance

QSDL SHALL expose an ordered effective field view that merges supertypes in declaration order, counts a shared declaration only once, and rejects distinct declarations of the same name unless the child resolves the conflict with `@override`. A replacement SHALL keep the inherited field's position. An override that changes the inherited value type SHALL still emit a warning.

#### Scenario: Diamond with a shared declaration
- **WHEN** two supertypes inherit the same field from a common Base
- **THEN** the effective view contains that original field node once

#### Scenario: Distinct inherited declarations conflict
- **WHEN** two supertypes contribute distinct fields with the same name and the child has no local `@override` for that field
- **THEN** QSDL reports a field redefinition semantic error

#### Scenario: A local override resolves the conflict
- **WHEN** the child declares a matching field with `@override`
- **THEN** the child's declaration replaces the inherited candidates at their first inherited position without changing either supertype's declaration

### Requirement: Circular inheritance diagnostics

QSDL SHALL reject circular `extends` chains with a source-located semantic error that identifies the cycle before any validation that depends on inherited fields.

#### Scenario: A cycle reached from an Object
- **WHEN** an Object extends a Base in a circular `extends` chain
- **THEN** QSDL reports the cycle instead of failing with a recursion error while validating the Object's fields

### Requirement: Generation-visible fields

QSDL SHALL expose a generation-visible field view that excludes effective fields marked `@ignore` and retains the existing generated ID for Objects. Filtering SHALL NOT restore an inherited field hidden by an ignored override or change declaration ownership.

#### Scenario: Ignored override
- **WHEN** an Object overrides an inherited field with a field marked `@override @ignore`
- **THEN** the completed effective view includes the override, but the generation-visible view includes neither the override nor the replaced field

#### Scenario: Object ID
- **WHEN** QSDL completes an Object
- **THEN** its effective and generation-visible views start with the generated required, read-only `id`, which is absent from its declaration list

### Requirement: Type reachability during completion

Completion SHALL terminate when calculating type retention and propagating `@force-generate`, including when Base field references revisit a type. Retention and propagation SHALL continue to consider resolved fields before `@ignore` filtering. This requirement does not constrain how generators handle recursive value types.

#### Scenario: Repeated references from a forced Base
- **WHEN** force generation reaches the same Base more than once through field references
- **THEN** completion terminates and the recipient has at most one `@force-generate` node

#### Scenario: A type referenced only by an ignored field
- **WHEN** an Object's ignored field is its only reference to an otherwise unused Enum
- **THEN** completion retains the Enum for generation but does not expose the field in the generation-visible view
