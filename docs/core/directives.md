# Directives

This page documents **where directives can be applied** in QSDL and what they control.

> Scope note
>
> This page does not attempt to fully document generator-specific behavior. Generator-specific directives/arguments 
> should be documented under `docs/generators/<name>/`.

## General directives

These directives apply to types, scalars, enums, and API blocks for organization and control over generation behavior.

| Directive           | Purpose                                                                       | Applies to                    |
| ------------------- | ----------------------------------------------------------------------------- | ----------------------------- |
| `@namespace(String)` | Organize types and operations into logical groups (packages, API tags, etc.). | Scalar, Enum, Base, Object, Api |
| `@deprecated`       | Mark a type or API as deprecated to guide generators on handling legacy structures. | Base, Object, Api             |
| `@force-generate`   | Force generation of an unused type (by default, unused Enum and Base are removed). | Enum, Base                    |
| `@openapi(...)`     | Map custom scalar to OpenAPI type (generator-specific). | Scalar                        |
| `@spring(...)`      | Map custom scalar to Spring type (generator-specific). | Scalar                        |
| `@postgres(...)`    | Map custom scalar to PostgreSQL type (generator-specific). | Scalar                        |

### Examples

**Type organization with `@namespace`:**

```qsdl
scalar UUID @namespace("common")

enum Status @namespace("domain") {
    OPEN
    CLOSED
}

base AuditFields @namespace("common") {
    created_at: Datetime @readOnly
}

type Project @namespace("projects") {
    name: String!
}

extend api @namespace("admin") {
    archiveAll(): Void @path("admin/archive-all") @method(POST)
}
```

**Deprecation and custom scalar mapping:**

```qsdl
base LegacyBase @deprecated {
    old_field: String
}

type OldObject @deprecated {
    name: String
}

scalar UUID @openapi("string, format: uuid") @spring("UUID") @postgres("UUID")

enum FutureStatus @force-generate {
    PLANNED
    ACTIVE
    ARCHIVED
}
```

See `docs/generators/<name>/` for detailed generator-specific directive syntax.

---

## Field directives

Field directives control how fields appear in APIs, databases, and responses.

### Query and I/O modifiers

| Directive    | Purpose                                                      |
| ------------ | ------------------------------------------------------------ |
| `@query`     | Create a query parameter for the get-all operation.          |
| `@queryList` | Similar to `@query`, but for list-type fields (filtering).   |
| `@readOnly`  | Field is returned in responses but cannot be set in requests |
| `@writeOnly` | Field is accepted in requests but not returned in responses  |

**Example:**

```qsdl
type Project {
    name: String! @query          # Can filter projects by name
    created_at: Datetime @readOnly # Returned in responses, cannot be set
    password: String! @writeOnly   # Accepted on create/update, never returned
}
```

### Relationship directives

| Directive      | Purpose                                               |
| -------------- | ----------------------------------------------------- |
| `@composition` | Parent-child relationship (array field only).         |
| `@aggregation` | Independent reference relationship (array field only) |

Use `@composition` when deleting a parent should delete its children. Use `@aggregation` for independent many-to-many or reference relationships.

**Example:**

```qsdl
type User {
    # Children of this user; delete user → delete projects
    owned_projects: [Project] @composition
    
    # Independent references; delete user → keep teams
    team_memberships: [Team] @aggregation
}
```

### Constraint and semantic modifiers

| Directive           | Purpose                                                           |
| ------------------- | ----------------------------------------------------------------- |
| `@unique`           | Field values must be unique across all records.                   |
| `@default("value")` | Provide a default value (used in schema/documentation).           |
| `@minSize(int)`     | Set minimum length (strings) or value (numbers).                  |
| `@maxSize(int)`     | Set maximum length (strings) or value (numbers).                  |
| `@opaque`           | Treat field as opaque data (not inspected/decomposed).            |
| `@hidden`           | Exclude field from API data layer.                                |
| `@transient`        | Exclude field from database layer (requests/responses only).      |
| `@ignore`           | Exclude field from generation (useful for documentation).         |
| `@override`         | **Required** when redefining an inherited field from a base.      |

**Example:**

```qsdl
type User {
    email: String! @unique                          # Must be unique
    birth_date: Date                                # Optional
    status: String @default("active")               # Default value
    internal_id: String @hidden                     # Not exposed in API
    temp_data: String @transient                    # Not persisted
    notes: String @maxSize(500)                     # Length constraint
}

base AuditFields {
    created_at: Datetime @readOnly
}

type Project extends AuditFields {
    created_at: Datetime! @readOnly @override       # Redefine with stricter type
}
```

---

## Api directives

Api blocks support `@deprecated` and `@namespace` (see [Cross-cutting directives](#cross-cutting-directives)).

### `@generate(String, ...)`

**Applies to:** `Api`

Control which implicit CRUD operations to generate for an object's custom API block.

**Valid values:** `GET_ALL`, `CREATE`, `GET`, `REPLACE`, `UPDATE`, `DELETE`, `ADD`, `REMOVE`

**Example:**

```qsdl
type Project {
    name: String!
    
    extend api @generate("GET_ALL", "GET", "UPDATE") {
        # Implicit DELETE is skipped due to @generate
        archive(id: Long!): Project @path("projects/{id}/archive") @method(PATCH)
    }
}
```

---

## Operation directives

Operation directives specify how endpoints are exposed and behave.

### Required directive

| Directive       | Purpose                                             |
| --------------- | --------------------------------------------------- |
| `@path(String)` | **Required.** Sets the API path; use `{name}` for path parameters. |

### Optional directives

| Directive              | Purpose                                                       |
| ---------------------- | ------------------------------------------------------------- |
| `@method(HTTP_METHOD)` | HTTP method (GET, POST, PUT, PATCH, DELETE); defaults to GET. |
| `@pagination`          | Convert response into a pageable object.                      |
| `@consumes(String)`    | Override the media type consumed (e.g., `multipart/form-data`).|
| `@produces(String)`    | Override the media type produced.                             |
| `@headers(name: Type, ...)` | Define additional response headers the operation returns. |

**Example:**

```qsdl
extend api {
    "Retrieve an item by ID."
    getItem(): Item @path("items/{id}") @method(GET)

    "Create a new item."
    createItem(body: Item): Item @path("items") @method(POST)

    "Search items by name with pagination."
    searchItems(name: String?): [Item] @path("items/search") @method(GET) @pagination

    "Get items with custom headers."
    getItemsWithHeaders(): [Item] @path("items") 
        @headers(X-Total-Count: Int, X-Page-Number: Int)
}
```

---

## Argument directives

Arguments use **modifiers** (not full directives) to control how they are passed to operations.

See [Language: Argument](./language.md#argument) for details on `!`, `[...]`, `?`, and `^` modifiers.
