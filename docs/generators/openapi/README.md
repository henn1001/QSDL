# OpenAPI generator

The OpenAPI generator produces an OpenAPI 3.1.0 specification (YAML format) from your QSDL schema, enabling interactive API documentation, client code generation, and API contract testing.

## Output

The generator creates a single `openapi.yaml` file containing:

- **API metadata**: Title, version, description, and servers from your schema.
- **Paths and operations**: All custom API operations with request/response schemas, parameters, and HTTP methods.
- **Models**: Schemas for all types (enum, base, object) used in the API, including generated paginated list types.
- **Security schemes**: Default API key authentication.
- **Tags**: Namespace-based operation grouping for better organization.
- **Pagination support**: Automatic wrapper models and cursor/limit parameters for paginated operations.

## Configuration

| Name      | Type | Default | Description                                                                      | Required |
| --------- | ---- | ------- | -------------------------------------------------------------------------------- | -------- |
| `id_type` | enum | `LONG`  | Type representation for ID fields. Options: `LONG` (int64) or `STRING` (string). | No       |

## Scalar-to-OpenAPI Type Mapping

| QSDL Scalar | OpenAPI Type      | Format                                   |
| ----------- | ----------------- | ---------------------------------------- |
| `Int`       | integer           | int32                                    |
| `Long`      | integer           | int64                                    |
| `Float`     | number            | float                                    |
| `Double`    | number            | double                                   |
| `String`    | string            | —                                        |
| `Boolean`   | boolean           | —                                        |
| `ID`        | integer or string | int64 or — (depends on `id_type` config) |
| `Date`      | string            | date                                     |
| `Datetime`  | string            | date-time                                |
| `Object`    | object            | —                                        |

## Default CRUD Operations

Each `type` in your schema automatically generates standard CRUD endpoints (unless overridden with `extend api { ... }`):

- **GET** `/types` — List all instances (supports pagination with `@pagination` directive).
- **POST** `/types` — Create a new instance.
- **GET** `/types/{id}` — Retrieve a specific instance.
- **PATCH** `/types/{id}` — Update a specific instance.
- **DELETE** `/types/{id}` — Delete a specific instance.

Example: A `type Project` generates:

- `GET /projects` (paginated)
- `POST /projects`
- `GET /projects/{id}`
- `PATCH /projects/{id}`
- `DELETE /projects/{id}`

## Custom Operations

Define custom operations using the `extend api { ... }` block within a type or at the global level. Operations are rendered as OpenAPI paths.

**Example schema:**

```qsdl
type Buzzword {
  name: String!

  extend api {
    getBuzzwords(name: String): [Buzzword] @path("/buzzwords") @pagination
    createBuzzword(body: Buzzword): Buzzword @path("/buzzwords") @method(POST)
    getBuzzword: Buzzword @path("/buzzwords/{id}")
    deleteBuzzword: Void @path("/buzzwords/{id}") @method(DELETE)
  }
}
```

**Generated OpenAPI paths:**

```yaml
paths:
  /buzzwords:
    get:
      operationId: getBuzzwords
      parameters:
        - name: name
          in: query
          schema:
            type: string
        - $ref: "#/components/parameters/cursor"
        - $ref: "#/components/parameters/limit"
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/BuzzwordList"
    post:
      operationId: createBuzzword
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Buzzword"
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Buzzword"
  /buzzwords/{id}:
    get:
      operationId: getBuzzword
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
            format: int64
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Buzzword"
    delete:
      operationId: deleteBuzzword
      responses:
        "200":
          description: OK
```

## Directives & Modifiers

QSDL directives influence OpenAPI output:

| Directive         | Context   | Effect                                                                                        |
| ----------------- | --------- | --------------------------------------------------------------------------------------------- |
| `@query`          | Field     | Field becomes a query parameter in auto-generated list operations.                            |
| `@readOnly`       | Field     | Field is excluded from request schemas (only in responses).                                   |
| `@writeOnly`      | Field     | Field is excluded from response schemas (only in requests).                                   |
| `@hidden`         | Field     | Field is completely excluded from OpenAPI output.                                             |
| `@namespace(...)` | Type      | Type is tagged with the namespace for grouping in OpenAPI UI.                                 |
| `@pagination`     | Operation | Operation response is wrapped in a list model with `items`, `next_cursor`, and `total_count`. |
| `@method(...)`    | Operation | Specifies HTTP method (GET, POST, PUT, PATCH, DELETE, etc.). Defaults to GET.                 |
| `@path(...)`      | Operation | Specifies the endpoint path. Can include path parameters like `{id}`.                         |

## Pagination

Mark a list operation with `@pagination` to generate a paginated response model. The generator automatically creates a wrapper type (e.g., `ProjectList`) with:

- `items: [Project]!` — Array of results.
- `next_cursor: String` — Cursor for fetching the next page.
- `total_count: Long` — Total number of results available.

**Example:**

```qsdl
type Project {
  name: String!

  extend api {
    listProjects: [Project] @path("/projects") @pagination
  }
}
```

**Generated model:**

```yaml
components:
  schemas:
    ProjectList:
      type: object
      required:
        - items
      properties:
        items:
          type: array
          items:
            $ref: "#/components/schemas/Project"
        next_cursor:
          type: string
        total_count:
          type: integer
          format: int64
```

**Generated operation:**

```yaml
paths:
  /projects:
    get:
      operationId: listProjects
      parameters:
        - $ref: "#/components/parameters/cursor"
        - $ref: "#/components/parameters/limit"
        - $ref: "#/components/parameters/count"
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ProjectList"
```

## Base Types & Composition

Base types become OpenAPI schemas and are included in the components section. Types that extend a base inherit all base fields in their schema definition.

Composition and aggregation relationships are represented as nested object references in the schema.

**Example:**

```qsdl
base Metadata {
  createdBy: String @readOnly
  createdDate: Datetime @readOnly
}

type User extends Metadata {
  name: String!
  email: String!
}
```

**Generated schema:**

```yaml
components:
  schemas:
    User:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
        email:
          type: string
        createdBy:
          type: string
          readOnly: true
        createdDate:
          type: string
          format: date-time
          readOnly: true
```

## Enums

Enum types are rendered as OpenAPI schemas with an `enum` constraint listing all values.

**Example:**

```qsdl
enum Status {
  OPEN
  IN_PROGRESS
  CLOSED
}
```

**Generated schema:**

```yaml
components:
  schemas:
    Status:
      type: string
      enum:
        - OPEN
        - IN_PROGRESS
        - CLOSED
```

## Security

By default, all operations require an API key header (`Authorization`). This is configured in the OpenAPI security schemes section:

```yaml
security:
  - ApiKeyAuth: []

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: Authorization
```
