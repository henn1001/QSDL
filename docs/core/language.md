# QSDL language

This page is a concise **language tour** of QSDL: the constructs you can write in a `.qsdl` schema file
and how they fit together.

QSDL is implemented as a TextX-based DSL. The definitive source for the language syntax is the TextX
grammar file: [`src/qsdl/dsl/definition/entity.tx`](../../src/qsdl/dsl/definition/entity.tx).

This document exists to provide a human-friendly overview with small examples, without requiring you to
read the grammar directly.

## Schema

```text
title: STRING
version: STRING
description: STRING | """..."""
servers: [STRING, ...]

import "./other.qsdl"

# followed by any number of type definitions
```

A `.qsdl` file may start with a small **schema header**. All header fields are **optional**: you can
write a completely valid QSDL file that only contains type definitions (and optionally imports).

The header is mainly used as metadata for generators (for example OpenAPI generation).

### Schema header fields

#### `title`

Human-readable API/schema name.

#### `version`

Human-readable version string (for example `"1.0"`).

#### `description`

Free-form documentation text.

**Description syntax (applies everywhere):** Any place in QSDL that allows a description can use either

- a single-line string: `"..."`
- a multiline triple-quoted string: `"""..."""`

This is not limited to the schema header; the same description syntax is used throughout the language
(for example on `enum`, `base`, `type`, `field`, `extend api`, and `operation`).

#### `servers`

A list of server base URLs. This is typically used by generators that produce API descriptions.

**Examples:**

```qsdl
title: "Test API"
version: "1.0"
description: "A description"

servers: ["https://localhost:8080/api/v1", "https://localhost:8082/api/v1"]
```

Description can also be multiline:

```qsdl
description: """
A
multi
line
description.
"""
```

## Import

```text
import STRING
```

Schemas can import other schema files.

Imports are **optional**. Use them to split a larger schema into multiple files (for example `common` types
and feature-specific types).

An import statement references another `.qsdl` file via a string path.

> Note
>
> Imported files are loaded automatically and treated as if their type definitions were part of the main
> schema.
>
> The exact rules for how the import path is resolved depend on the underlying parser/scoping mechanism.
> If you run into “file not found” issues, prefer explicit relative paths like `"./common.qsdl"` and keep
> imported schemas next to (or below) the file that imports them.

> Note
>
> When you split a schema across multiple files, QSDL merges them into a single schema and then removes
> unused helper types (currently: unused `base` and `enum` definitions). If you want to keep a `base` or
> `enum` around even when it is not referenced yet, use `@force-generate`.

**Examples:**

```qsdl
import "./common.qsdl"
```

## Type

```text
scalar ...
enum ...
base ...
type ...
extend api ...
```

Types are the top-level building blocks in QSDL. A schema can contain any mix of these five type kinds:

- **`scalar`**: introduce a new primitive-ish type (usually to map to generator-specific target types).
- **`enum`**: a closed set of string values.
- **`base`**: a reusable “shape” (a set of fields) that can be extended by other bases and objects.
- **`type`**: an **object** (your main domain entity). Many generators treat these as the primary inputs for
  CRUD APIs, persistence, DTOs, etc.
- **`extend api`**: define custom API operations/endpoints.

You can define as many types as you need.

In the following sections, each type kind is described in more detail with syntax and examples.

## Scalar

```text
scalar Name [directives...]
```

Scalar types represent primitive leaf types which can be used as assignments.

In most schemas, the builtin scalars are sufficient:

- `Int`
- `Long`
- `Float`
- `Double`
- `String`
- `Boolean`
- `Date`
- `Datetime`
- `Object`
- `Void`

If you still need an additional scalar (for example `UUID`, `Email`, `Money`), you can declare your own:

```qsdl
scalar UUID
```

### Generator mapping for custom scalars

Declaring a scalar only introduces a new name in the schema. To generate useful output, a generator must
also know **how to map that scalar** to its target type system.

To do that, attach a generator-specific directive to the scalar. If you omit such a directive, generators
typically fall back to using the scalar name as-is (so `UUID` will be treated as `UUID` unless the generator
has a built-in mapping for it).

Generator-specific scalar typing is currently supported for OpenAPI, Spring, and Postgres, using directives
that follow the generator name:

- `@openapi("...")`
- `@spring("...")`
- `@postgres("...")`

**Examples:**

```qsdl
scalar UUID @openapi("string, format: uuid, pattern: ^.*$") @spring("UUID")
```

## Enum

```text
"Description"?
enum Name [directives...] {
    VALUE
    ...
}
```

Enum types represent a **fixed set of allowed values**. Use them for fields with a closed list of states or
categories (for example status, role, type).

Enum values are identifiers (not quoted strings) and are typically written in `ALL_CAPS`.

Like other description fields in QSDL, enums can have an optional description using either a single-line
string or a triple-quoted multiline string.

> Note: `@force-generate`
>
> QSDL removes unused `enum`s (and `base`s) during schema processing. If you want to keep an enum even when
> it is currently unused, add the `@force-generate` directive.

**Examples:**

```qsdl
enum Status {
    OPEN
    TO_DO
    CLOSED
}
```

**Usable directives**

- `@namespace("...")`
- `@force-generate`
- Any custom directive

## Base

```text
"Description"?
base Name [extends BaseName (, BaseName ...)] [directives...] {
    field
    ...
}
```

Base types let you define a **reusable set of fields**.

Think of a `base` as a building block you can plug into multiple places:

- Use it as a **shared parent** for objects (to avoid repeating common fields like `created_at`, `updated_at`,
  `tenant_id`, ...).
- Use it as a **standalone model** for request/response shapes in custom APIs.
- Use it as a **field type** inside other models (nesting): a field can reference a base to group related
  values under one name.

Unlike `type` (objects), a `base` usually does not represent a top-level domain entity on its own. It’s
primarily a way to keep your schema DRY and consistent.

A base can also extend **one or more** other bases. This is useful to compose “aspects” of your model, for
example `AuditFields` + `Ownership` + `SoftDelete`.

> Note: `@force-generate`
>
> QSDL removes unused `base` types (and `enum`s) during schema processing to keep generation output clean.
> If you want to ensure a base is kept even when it is not referenced yet (for example because you plan to
> reference it later), mark it with `@force-generate`.

**Examples:**

```qsdl
"The very basic type all Domain Objects should have."
base BaseType {
    "The Object name."
    name: String! @query

    "Optional description"
    description: String

    "Accepts any valid json object."
    meta_inf: Object
}

"Group related values by nesting another base as a field."
base Address {
    street: String!
    zip: String!
    city: String!
}

base BaseTypeWithAddress extends BaseType {
    address: Address
}

"Maybe some Domain Objects need date information."
base BaseTypeDated extends BaseType {
    creation_date: Date @readOnly
    last_update_date: Date @readOnly
}

"Combine multiple common aspects into one base."
base AuditedOwned extends BaseAudit, BaseOwned {
    # This base inherits fields from both supertypes.
}
```

**Usable directives**

- `@deprecated`
- `@namespace("...")`
- `@force-generate`
- Any custom directive

## Object

```text
"Description"?
type Name [extends BaseName (, BaseName ...)] [directives...] {
    field
    ...

    # optional: custom API block inside the object
    extend api { ... }
}
```

Object types (`type`) usually represent your **main domain entities**.

They are the core of most schemas: objects define the data structures that other parts of the schema refer
to (fields, operations, request/response models).

QSDL automatically creates a set of CRUD-style operations for each object as part of schema processing.
Generators then use these operations to produce the actual output (for example an OpenAPI spec or Spring
controllers).

An object can extend one or more `base` types to reuse common fields.

### Custom API operations on an object

If you want to add or override endpoints related to a specific object, you can put an `extend api { ... }`
block inside the object. This is optional.

If you don’t write any operations, QSDL still provides an implicit CRUD API for each object.

**Examples:**

```qsdl
type Project extends BaseType {
    archive: Boolean @writeOnly
    archived: Boolean @readOnly
}
```

For an object named `Project`, the implicit operations look like this (QSDL syntax):

```qsdl
# implicit operations (conceptual)
extend api {
    getProjects(): [Project] @path("projects") @method(GET) @pagination
    createProject(body: Project): Project @path("projects") @method(POST)
    getProject(id: Long!): Project @path("projects") @method(GET)
    updateProject(id: Long!, body: Project): Project @path("projects") @method(PATCH)
    deleteProject(id: Long!): Void @path("projects") @method(DELETE)
}
```

The exact paths and parameters depend on the object name and configured conventions, but the naming and
HTTP methods follow this pattern.

**Usable directives**

- `@deprecated`
- `@namespace("...")`
- Any custom directive

## Field

```text
"Description"?
name: TypeName | [TypeName] (!) [directives...]
```

Fields are the **atomic building blocks** of your schema. They define named attributes on `Base` and `Object`
types, specifying what data each type holds and how that data can be used.

Every field has:

- a **name** (identifier)
- a **type** (what kind of value it holds)
- optional **modifiers** (required, array, read-only, etc.)
- optional **directives** (for generation control and additional semantics)

Fields are where most of your schema semantics are expressed: they define relationships between types,
constrain I/O visibility, mark query parameters, enforce uniqueness, and more.

### Field types

In `name: TypeName`, the `TypeName` must refer to a type that exists in your schema (or is built in).
In other words, a field value can be one of:

- a **`scalar`** (including builtin scalars like `String`, `Boolean`, `Int`, `Date`, ...)
- an **`enum`** (a field of an enum type is constrained to that enum's values)
- a **`base`** (nesting: fields can reference bases to group related values)
- an **`object`** (`type`: fields can form relationships to other domain entities)

### Field modifiers

QSDL provides two built-in type modifiers that appear after the type name:

#### `!` (required/non-null)

Marks the field as **required**. A field without `!` is optional and can be `null`.

```qsdl
name: String!        # required
nickname: String     # optional
count: Int!          # required integer
```

#### `[...]` (array/list)

Marks the field as a **collection**. Array items are of the specified type; use `!` to constrain them.

```qsdl
tags: [String]       # array of strings (items nullable, array nullable)
items: [Item]!       # required array
```

**Examples:**

```qsdl
type User {
    "User's full name (searchable)."
    name: String! @query

    "Email address (must be unique)."
    email: String! @unique

    "User's password (write-only, never returned)."
    password: String! @writeOnly

    "Birth date (optional)."
    birth_date: Date

    "User's profile information (nested base)."
    profile: UserProfile

    "Tags associated with this user (array)."
    tags: [String]

    "Projects owned by this user (composition: delete user → delete owned projects)."
    owned_projects: [Project] @composition

    "List of roles/permissions (read-only, computed server-side)."
    roles: [Role]! @readOnly

    "Field with a default value."
    status: String @default("active")
}
```

**Usable directives**

Built-in field directives:

- `@queryList`
- `@query`
- `@readOnly`
- `@writeOnly`
- `@composition`
- `@aggregation`
- `@opaque`
- `@unique`
- `@hidden`
- `@transient`
- `@ignore`
- `@override`
- `@minSize(<int>)`
- `@maxSize(<int>)`
- `@default("...")`
- Any custom directive

## Api

```text
"Description"?
extend api [directives...] {
    operation
    ...
}
```

Api blocks let you define **custom API operations** (endpoints).

You can place an `extend api` block at the **top level** of your schema (global operations) or **inside an Object**
(object-specific operations).

By default, QSDL automatically generates CRUD operations for each `Object`. If you want to add additional
operations, override the implicit ones, or define completely custom endpoints, use an `extend api` block.

Think of an api block as a collection of endpoint definitions:

- Each endpoint has a name, takes arguments, and returns a result type.
- You attach directives like `@path`, `@method`, and `@pagination` to specify how the endpoint should be exposed.
- Generators use this information to produce code (OpenAPI specs, Spring controllers, etc.).

**Examples:**

A global custom operation:

```qsdl
extend api {
    "Submit a query for processing and get the result back."
    submitQuery(body: QueryMachine): QueryMachine @path("query/submit") @method(POST)
}
```

Operations inside an object (to override or extend the implicit CRUD):

```qsdl
type Project {
    name: String!

    "Custom endpoints for this specific object."
    extend api @generate("CREATE", "GET", "UPDATE") {
        "Archive a project (custom endpoint)."
        archive(id: Long!): Project @path("projects/{id}/archive") @method(PATCH)
    }
}
```

**Usable directives**

- `@namespace("...")`
- `@generate("GET_ALL", "CREATE", "GET", "REPLACE", "UPDATE", "DELETE", "ADD", "REMOVE")`
  (comma-separated list; controls which implicit CRUD operations to generate)
- Any custom directive

## Operation

```text
"Description"?
name(arg: Type, ...): ReturnType | [ReturnType] (!) [directives...]
```

An operation is a **single endpoint definition** inside an api block.

Every operation has:

- a **name** (the operation identifier)
- **arguments** (optional; the inputs it accepts)
- a **return type** (what the operation produces)
- **directives** (to specify HTTP method, path, pagination, etc.)

> Note
>
> The `@path("...")` directive is **required** for custom operations. The `@method(...)` directive defaults to
> `GET` if not provided.
>
> Path parameters (placeholders like `{id}` in `@path("items/{id}")`) are always strings. They do not require
> a matching argument in the operation signature; however, if you do define an argument with the same name,
> it will shadow the path parameter and cause a conflict.

**Examples:**

```qsdl
extend api {
    "Retrieve a specific item by ID (ID is a path parameter)."
    getItem(): Item @path("items/{id}") @method(GET)

    "Create a new item."
    createItem(body: Item): Item @path("items") @method(POST)

    "Search items by name (with pagination)."
    searchItems(name: String?): [Item] @path("items/search") @method(GET) @pagination
}
```

**Usable directives**

Built-in operation directives:

- `@path("...")` – **Required.** Sets the API path; use `{name}` for path parameters.
- `@method(GET|POST|PUT|PATCH|DELETE)` – HTTP method; defaults to `GET` if not specified.
- `@pagination` – Convert response into a pageable object.
- `@consumes("...")` – Override the media type consumed (e.g., `multipart/form-data`).
- `@produces("...")` – Override the media type produced.
- `@headers(name: Type, ...)` – Define additional response headers the operation returns.
  - Example: `@headers(X-RateLimit: Int, X-Total-Count: Int)`

Plus any custom directive.

## Argument

```text
name: Type
name: Type!
name: [Type]

name: Type?   # query argument
name: Type^   # header argument
```

Arguments define **inputs to operations**. Every argument has a name and a type, and can be annotated with
modifiers to control how it is passed (in the path, query string, or request body).

How arguments are interpreted depends on the HTTP method and modifiers:

- **GET**: Arguments without modifiers become **query parameters**.
- **POST/PUT/PATCH**: Arguments without modifiers become **request body** fields. Use `?` to make them query
  parameters instead.
- **DELETE**: Arguments **must be query parameters** (use `?` modifier). Request body arguments (without modifiers) are not allowed.

For all HTTP methods, use `{name}` in the `@path` to create **path parameters** (always strings, do not require a matching argument in the operation signature).

You can also explicitly mark arguments as **header parameters** using `^`.

**Important:** Do not define an argument with the same name as a path parameter; this creates a schema parsing error.

### Argument modifiers

Arguments support the following modifiers to control how they are passed to an operation:

| Modifier | Name             | Meaning                                                        |
| -------- | ---------------- | -------------------------------------------------------------- |
| `!`      | Required         | The argument must be provided.                                 |
| `[...]`  | Array            | The argument is a collection.                                  |
| `?`      | Query parameter  | The argument is passed as a query string parameter (explicit). |
| `^`      | Header parameter | The argument is passed as an HTTP header.                      |

**Modifier interaction with HTTP method:**

The default behavior changes by HTTP method; modifiers override defaults:

| Modifier             | GET                      | POST/PUT/PATCH        | DELETE                   |
| -------------------- | ------------------------ | --------------------- | ------------------------ |
| (none)               | Query parameter          | Request body field    | ❌ Not allowed           |
| `!` (required)       | Required query parameter | Required body field   | Required query parameter |
| `?` (explicit query) | Query parameter          | Query parameter       | Query parameter          |
| `^` (header)         | Header parameter         | Header parameter      | Header parameter         |
| `[...]` (array)      | Array query param        | Array in request body | Array query param        |

Modifiers can be combined (e.g., `Int!?` means a required query parameter of type Int).

**Examples:**

GET operations with query parameters and path parameters:

```qsdl
extend api {
    "Retrieve an item by its ID (ID is a path parameter, no argument needed)."
    getItem(): Item @path("items/{id}") @method(GET)

    "Search items by name (name is a query parameter)."
    search(name: String?): [Item] @path("items/search") @method(GET)
}
```

POST operations with request body and query parameters:

```qsdl
extend api {
    "Create a new item from the request body."
    createItem(body: Item): Item @path("items") @method(POST)

    "Create items in bulk (items in body, flag as query param)."
    createBulk(items: [Item]!, dryRun: Boolean?): [Item] @path("items/bulk") @method(POST)
}
```

DELETE operations (path parameters and optional query parameters):

```qsdl
extend api {
    "Delete an item by ID (path parameter only)."
    deleteItem(): Void @path("items/{id}") @method(DELETE)

    "Delete items with optional filters (query parameters only)."
    deleteItems(filter: String?, hardDelete: Boolean?): Void @path("items") @method(DELETE)
}
```

## Directive

```text
@name
@name("string")
@name(param1, param2)
```

Directives are **annotations** attached to scalars, types, fields, operations, and api blocks.
They control generation behavior and express additional semantics (like constraints, I/O visibility, and relationships).

Directives fall into several categories:

- **Built-in directives**: Part of the core QSDL language (e.g., `@query`, `@readOnly`, `@composition`).
- **Generator-specific directives**: Control how a particular generator (OpenAPI, Spring, etc.) maps your schema
  (e.g., `@openapi("...")`, `@spring("...")`).
- **Custom directives**: Application-defined annotations for domain-specific metadata.

Most directives are optional; they provide additional information to generators and don't affect the core schema structure.

**Examples:**

Field-level directives (control I/O and constraints):

```qsdl
type User {
    "Email address (searchable, must be unique)."
    email: String! @query @unique

    "Password (write-only, never returned in responses)."
    password: String! @writeOnly

    "Created timestamp (read-only, server-managed)."
    created_at: Datetime @readOnly
}
```

Type-level directives (organize and control generation):

```qsdl
type Project @namespace("core") {
    name: String!
    archived: Boolean
}

scalar UUID @openapi("string, format: uuid") @spring("UUID")
```

Relationship and constraint directives:

```qsdl
type Project {
    "Tasks owned by this project (parent-child relationship)."
    tasks: [Task] @composition

    "Team members assigned to this project (independent reference)."
    team: [User] @aggregation
}
```

For a complete reference of all directives, their constraints, and generator-specific variants, see [Directives](./directives.md).
