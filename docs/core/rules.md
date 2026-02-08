# QSDL Rules & Requirements

This document defines all constraints, invariants, and validation rules for the QSDL language.
Rules are organized by category and may be referenced by their rule identifier (e.g., `SEM-101`, `LOG-302`).

## Notation

- **[SYN-NNN]** — Syntax/Grammar rules (enforced by `entity.tx` grammar)
- **[SEM-NNN]** — Semantic/DSL rules (enforced by processors/validators)
- **[LOG-NNN]** — Logical rules (checked after model construction)

---

## Part 1: Syntax & Naming Rules

### Identifiers & Naming Conventions

| ID      | Element                                     | Rule                               | Reference              |
| ------- | ------------------------------------------- | ---------------------------------- | ---------------------- |
| SYN-001 | All type names (Enum, Base, Object, Scalar) | Must use `PascalCase`              | entity.tx: `ID` rule   |
| SYN-002 | Enum values                                 | Must use `ALL_CAPS`                | entity.tx: Enum.values |
| SYN-003 | Field names                                 | Must use `camelCase` (via ID rule) | entity.tx: Field.name  |
| SYN-004 | Scalar names                                | Must use `PascalCase`              | entity.tx: Scalar.name |

### Uniqueness Constraints

| ID      | Element                    | Scope    | Rule                                                                                        |
| ------- | -------------------------- | -------- | ------------------------------------------------------------------------------------------- |
| SEM-101 | Type names                 | Global   | All type names (`Object`, `Base`, `Enum`, `Scalar`) must be unique across the entire schema |
| SEM-102 | Field names within a type  | Per-type | Field names must be unique within a single `Base` or `Object` (including inherited fields)  |
| SEM-103 | Enum values within an Enum | Per-enum | Enum values must be unique within a single `Enum` declaration                               |
| SEM-104 | Operation names within Api | Per-api  | Operation names must be unique within a single `Api` container                              |
| SEM-105 | Api/Path names             | Global   | Api names and generated CRUD paths must be globally unique across all operations            |

---

## Part 2: Type-Specific Rules

### Scalar Rules

| ID      | Rule                                                                                                         | Notes                                    |
| ------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------- |
| SEM-201 | Scalars are leaf types and cannot be extended                                                                | Scalars do not support `extends`         |
| SEM-202 | Builtin scalars: `Int`, `Long`, `Float`, `Double`, `String`, `Boolean`, `Date`, `Datetime`, `Object`, `Void` | Generators may map these to target types |

### Enum Rules

| ID      | Rule                                                                |
| ------- | ------------------------------------------------------------------- |
| SEM-301 | An Enum must contain **at least one value**                         |
| SEM-302 | Enum values are constrained domain values (immutable in generators) |
| SEM-303 | Enums may have optional namespace via `@namespace(...)`             |

### Base Rules

| ID      | Rule                                                                               | Notes                                |
| ------- | ---------------------------------------------------------------------------------- | ------------------------------------ |
| SEM-401 | Base types define reusable field collections                                       | Used for inheritance and composition |
| SEM-402 | Base may extend zero or more other Bases (linear inheritance chain recommended)    | `extends Base1, Base2, ...`          |
| SEM-403 | Base may be marked `@deprecated`                                                   | Applies to all consumers of the Base |
| SEM-404 | Base cannot be directly instantiated in generated code (used only for inheritance) | Only Objects are instantiable        |

### Object Rules

| ID      | Rule                                                      | Notes                                      |
| ------- | --------------------------------------------------------- | ------------------------------------------ |
| SEM-501 | Object represents a primary domain entity                 | Typically drives CRUD generation           |
| SEM-502 | Object may extend zero or more Bases                      | `extends Base1, Base2, ...`                |
| SEM-503 | Object may contain an optional `extend api { ... }` block | Overrides or extends default CRUD          |
| SEM-504 | Object may be marked `@deprecated`                        | Affects all generated endpoints and fields |
| SEM-505 | An Object must contain **at least one field**             | Empty objects are not allowed              |

### Field Rules

| ID      | Rule                                                             | Notes                                               |
| ------- | ---------------------------------------------------------------- | --------------------------------------------------- |
| SEM-601 | A Field references a `ValueType` (Scalar, Enum, Base, or Object) | `name : Type` or `name : [Type]` or `name : Type!`  |
| SEM-602 | A Field may be **required** (`!` suffix)                         | Indicates non-null in generated schemas             |
| SEM-603 | A Field may be **array** (`[...]` wrapper)                       | Indicates a collection type                         |
| SEM-604 | A Field may be **read-only** (`@readOnly`)                       | Not settable in input/write contexts                |
| SEM-605 | A Field may be **write-only** (`@writeOnly`)                     | Not visible in output/read contexts                 |
| SEM-606 | A Field cannot be both `@readOnly` and `@writeOnly`              | Logically conflicting                               |
| SEM-607 | A Field may override an inherited field via `@override`          | Required if parent Base defines the same field name |
| SEM-608 | A Field without `@override` cannot redefine an inherited field   | Will raise validation error                         |

### Relationship Rules

| ID      | Rule                                                                       | Notes                                            |
| ------- | -------------------------------------------------------------------------- | ------------------------------------------------ |
| SEM-701 | `@composition` marks a parent-child relationship                           | Field value must be `[Object]!` (required array) |
| SEM-702 | `@aggregation` marks an independent relationship                           | Field value must be `[Object]!` (required array) |
| SEM-703 | A Field cannot be both `@composition` and `@aggregation`                   | Mutually exclusive                               |
| SEM-704 | Composition/aggregation fields must reference Objects (not Base or Scalar) | Relationship targets must be concrete types      |

### Api & Operation Rules

| ID      | Rule                                                                          | Notes                                                              |
| ------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| SEM-801 | An Api must contain **at least one Operation**                                | Empty Api blocks are not allowed                                   |
| SEM-802 | An Operation defines an HTTP endpoint (method, path, parameters, return type) | `name(args) : ReturnType`                                          |
| SEM-803 | An Operation may specify `@path(...)` to define the URI template              | Default path derived from operation name if not specified          |
| SEM-804 | An Operation may specify `@method(...)` to define HTTP verb                   | Valid values: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`              |
| SEM-805 | An Operation may be marked `@pagination` to indicate list pagination support  | Generators interpret as offset/limit or cursor pagination          |
| SEM-806 | An Operation may declare response headers via `@headers(...)`                 | Headers are metadata on the HTTP response                          |
| SEM-807 | An Api can be used **multiple times** in a schema                             | Multiple Api blocks define separate custom endpoints               |
| SEM-808 | An Api can be used **once inside an Object** via `extend api { ... }`         | Used to override or extend auto-generated CRUD operations          |
| SEM-809 | Api endpoints must specify **unique paths** across all operations             | Maximum of two operations per path (with and without ID parameter) |

### Argument Rules

| ID      | Rule                                                                                            | Notes                                                        |
| ------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| SEM-901 | An Argument defines an Operation parameter                                                      | `name : Type`, `name : [Type]`, `name : Type!`               |
| SEM-902 | An Argument may be **required** (`!` suffix)                                                    | Indicates mandatory parameter                                |
| SEM-903 | An Argument may be **query** (`?` suffix)                                                       | Parameter appears in query string; default for most contexts |
| SEM-904 | An Argument may be **header** (`^` suffix)                                                      | Parameter appears in HTTP header                             |
| SEM-905 | An Argument without explicit location (`?` or `^`) is inferred as body or path based on context | POST/PUT/PATCH typically use body; GET uses query            |

---

## Part 3: Logical & Validation Rules

### Inheritance & Overriding

| ID      | Rule                                                                                      |
| ------- | ----------------------------------------------------------------------------------------- |
| LOG-101 | All inherited fields from supertypes must appear in the flattened field list of a type    |
| LOG-102 | If a child type redefines an inherited field name, it **must** use `@override`            |
| LOG-103 | An `@override` field must have the same base type as the parent (or a compatible subtype) |

### Directive & Metadata

| ID      | Rule                                                                                                                                     |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| LOG-201 | Directives are **generator-agnostic by default** (DSL core directives) or **generator-specific** (`@openapi(...)`, `@spring(...)`, etc.) |
| LOG-202 | Custom directives (`@myDirective(...)`) are preserved in the model and available to generators                                           |
| LOG-203 | Multiple instances of the same directive on the same entity are **not allowed** (last one wins or error, per parser)                     |

### Schema Header Ordering

| ID      | Rule                                                                                                         |
| ------- | ------------------------------------------------------------------------------------------------------------ |
| LOG-301 | Schema header fields, when provided, must appear in this order: `title`, `version`, `description`, `servers` |
| LOG-302 | All schema header fields are **optional**                                                                    |

### Import & Composition

| ID      | Rule                                                                                          |
| ------- | --------------------------------------------------------------------------------------------- |
| LOG-401 | Schemas may import other `.qsdl` files via `import "path/to/file.qsdl"`                       |
| LOG-402 | Imported types are merged into the parent schema namespace; duplicates cause validation error |
| LOG-403 | Circular imports are **not allowed**                                                          |

---

## Summary Table (Cross-Reference)

For quick lookup, here is a subset of high-impact rules:

| Category                 | High-Impact Rules                               |
| ------------------------ | ----------------------------------------------- |
| **Naming**               | SYN-001, SYN-002                                |
| **Uniqueness**           | SEM-101, SEM-102, SEM-103, SEM-104, SEM-105     |
| **Inheritance**          | SEM-402, SEM-502, LOG-102                       |
| **Relationships**        | SEM-701, SEM-702, SEM-704                       |
| **Required Constraints** | SEM-301 (Enum), SEM-505 (Object), SEM-801 (Api) |
| **Field Directives**     | SEM-604, SEM-605, SEM-606, SEM-607, SEM-608     |

---

## Notes for Implementation

- Rules prefixed **SYN-** are enforced by the TextX grammar (`src/qsdl/dsl/definition/entity.tx`).
- Rules prefixed **SEM-** are enforced by DSL processors (`src/qsdl/dsl/processors/`).
- Rules prefixed **LOG-** are enforced by post-processing validators and semantic checks.
- See `src/qsdl/dsl/util.py` for helper functions that implement many of these rules.
- Generator-specific mappings (e.g., how a Scalar maps to OpenAPI type) are **not** constrained here; they belong in generator-specific documentation.
