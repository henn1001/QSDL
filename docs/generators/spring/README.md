# Spring Boot Generator

The Spring Boot generator produces a complete domain-driven Spring Boot application scaffold from your QSDL schema. It generates domain entities, DTOs, mappers, services, repositories, and REST controllers—ready for database integration and API implementation.

## Overview

This generator targets modern Spring Boot applications with:

- **Domain-driven design**: Separation of entities (database layer) and DTOs (API layer)
- **Layered architecture**: Controllers → Services → Repositories → Database
- **Entity mapping**: Automatic DTO-to-Entity conversion with MapStruct-style mappers
- **Relationship handling**: Composition and aggregation patterns with Hibernate
- **Request/Response splitting**: Separate DTOs for write-only and read-only fields
- **Query filtering**: Automatic filter model generation for list endpoints
- **Optional integrations**: OpenAPI spec and PostgreSQL schema generation

## Running the generated application

The generated application uses the in-memory H2 database by default. Use the PostgreSQL profile when running against PostgreSQL:

```bash
mvn spring-boot:run
mvn spring-boot:run -Dspring-boot.run.profiles=h2
mvn spring-boot:run -Dspring-boot.run.profiles=postgres
```

The `postgres` profile expects PostgreSQL at `localhost:5432`. The generated `docker-compose.yml` starts the application and PostgreSQL together.

## Configuration

Configuration is optional: pass JSON config files with `-c/--config` (later files override earlier ones) and individual overrides with `-S/--set KEY=VALUE` (highest precedence). Use `qsdl config show spring` to inspect defaults, `qsdl config init spring` to write them, and `qsdl config validate spring` to validate a configuration without generating.

| Name                           | Type                       | Default                         | Description                                                                         | Required |
| ------------------------------ | -------------------------- | ------------------------------- | ----------------------------------------------------------------------------------- | -------- |
| `title`                        | string                     | `"SpringBootApp"`               | Application name; used for the main entry class.                                    | No       |
| `group_id`                     | string                     | `"app"`                         | Maven group ID (reverse domain notation).                                           | No       |
| `artifact_id`                  | string                     | `"app"`                         | Maven artifact ID.                                                                  | No       |
| `base_package`                 | string                     | `"app"`                         | Root Java package; all paths are relative to this.                                  | No       |
| `database`                     | enum (`HIBERNATE` \| `NO`) | `HIBERNATE`                     | Enable Hibernate JPA annotations and persistence layer.                             | No       |
| `use_auditing`                 | boolean                    | `false`                         | Enable automatic audit fields (createdBy, createdAt, modifiedBy, modifiedAt).       | No       |
| `table_prefix`                 | string                     | `"t_"`                          | Prefix for database table names.                                                    | No       |
| `id_type`                      | enum (`LONG` \| `STRING`)  | `LONG`                          | ID type for domain objects (affects OpenAPI generation too).                        | No       |
| `api_path`                     | string                     | `"api.{package}.web"`           | Domain API interface package.                                                       | No       |
| `controller_path`              | string                     | `"api.{package}.web"`           | Domain controller package.                                                           | No       |
| `service_path`                 | string                     | `"api.{package}"`               | Domain service package.                                                             | No       |
| `domain_path`                  | string                     | `"api.{package}.contract"`      | Domain DTO/request/response package.                                                | No       |
| `entity_path`                  | string                     | `"api.{package}.persistence"`  | Domain entity package.                                                              | No       |
| `mapper_path`                  | string                     | `"api.{package}.mapping"`       | Domain mapper package.                                                              | No       |
| `repository_path`              | string                     | `"api.{package}.persistence"`  | Domain repository package.                                                          | No       |
| `enum_path`                    | string                     | `"shared.constants"`            | Shared enum package.                                                                | No       |
| `exception_path`               | string                     | `"shared.exception"`            | Shared exception package.                                                           | No       |
| `model_path`                   | string                     | `"shared.model"`                | Shared model/support package.                                                       | No       |
| `config_path`                  | string                     | `"shared.config"`               | Shared configuration package.                                                       | No       |
| `util_path`                    | string                     | `"shared.util"`                 | Shared utility package.                                                             | No       |
| `shared_controller_path`       | string                     | `"shared.web"`                  | Shared controller support package.                                                  | No       |
| `shared_repository_path`       | string                     | `"shared.persistence"`          | Shared repository support package.                                                  | No       |
| `package_placeholder_fallback` | string                     | `"general"`                     | Fallback package name when neither `@spring-package` nor `@namespace` is specified. | No       |

`{package}` is resolved per domain object/API using `@spring-package`, then `@namespace`, then `package_placeholder_fallback`. Paths are prefixed with `base_package` unless they already start with it. Thus the default layout is `app/api/<namespace>/` for domain code and `app/shared/` for shared support. To retain an older layout, provide explicit `*_path` values in a config file; the defaults intentionally no longer provide that compatibility layout.

### Example Configuration

```json
{
  "title": "TravelAPI",
  "group_id": "com.example",
  "base_package": "com.example.travel",
  "artifact_id": "travel-api",
  "database": "HIBERNATE",
  "use_auditing": true,
  "id_type": "LONG",
  "api_path": "{package}.api",
  "controller_path": "{package}.api",
  "service_path": "{package}.service",
  "domain_path": "{package}.dto",
  "entity_path": "{package}.entity",
  "mapper_path": "{package}.mapper"
}
```

## Output Structure

The generator produces a Maven-based Spring Boot project with domain services at the domain package root:

```
app/api/<namespace>/{<Type>Service.java,web/<Type>Api.java,web/<Type>Controller.java,contract/,persistence/,mapping/}
app/shared/{config,constants,exception,model,util,web,persistence}/
```

For an explicit custom configuration, the generated project follows the configured package paths. The default layout is shown above; custom paths should be documented alongside the configuration that selects them.

<!-- Legacy custom-layout tree intentionally omitted: it was previously presented as the default. -->

<!--
```
src/
├── main/
│   ├── java/
│   │   └── com/example/travel/
│   │       ├── TravelAPI.java               (Spring Boot entry point)
│   │       ├── <package>/
│   │       │   ├── api/                     (Controllers and Api interfaces)
│   │       │   ├── service/                 (Business logic)
│   │       │   ├── dto/                     (Request/Response DTOs)
│   │       │   ├── entity/                  (JPA entities)
│   │       │   ├── mapper/                  (DTO ↔ Entity mappers)
│   │       │   └── repository/              (Spring Data repositories)
│   │       ├── constant/                    (Enums)
│   │       ├── exception/                   (Custom exceptions)
│   │       ├── model/                       (Shared models)
│   │       ├── config/                      (Spring configuration)
│   │       └── util/                        (Utility classes)
│   └── resources/
│       ├── application.yaml                 (Spring application config)
│       ├── logback-spring.xml               (Logging configuration)
│       └── db/migration/                    (Flyway DB migrations from the bundled PostgreSQL generator)
├── test/
│   └── java/
│       └── com/example/travel/
│           ├── AbstractIntegrationTest.java
│           ├── TestUtils.java
│           └── <package>/
│               ├── api/ControllerTest.java
│               ├── service/ServiceTest.java
│               └── repository/RepositoryTest.java
├── pom.xml                                  (Maven build config)
├── docker-compose.yml                       (PostgreSQL container for development)
└── .qignore                                  (Files to exclude from generation)
```

-->

### Package Layout with `@spring-package`

By default, the `package_placeholder_fallback` determines where files go. Use the `@spring-package` directive to organize code into domain-specific sub-packages:

```qsdl
type User @namespace("User") @spring-package("user") {
    name: String!
}

type Order @namespace("Order") @spring-package("order") {
    total: Float!
}
```

This generates domain code under `api/<namespace>/` and keeps shared support fixed under `shared/`:

```
com/example/travel/
├── api/user/{web,contract,persistence,mapping}/
├── api/order/{web,contract,persistence,mapping}/
└── shared/{config,constants,exception,model,util,web,persistence}/
```

## Type Mapping

QSDL scalars are mapped to Java types as follows:

| QSDL Scalar | Java Type                                        | Notes                        |
| ----------- | ------------------------------------------------ | ---------------------------- |
| `Int`       | `Integer`                                        | 32-bit integer               |
| `Long`      | `Long`                                           | 64-bit integer               |
| `Float`     | `Float`                                          | Single precision             |
| `Double`    | `Double`                                         | Double precision             |
| `String`    | `String`                                         | Text                         |
| `Boolean`   | `Boolean`                                        | Logical value                |
| `Date`      | `java.time.LocalDate`                            | Date only (no time)          |
| `Datetime`  | `java.time.OffsetDateTime`                       | Instant with timezone offset |
| `Object`    | `com.fasterxml.jackson.databind.node.ObjectNode` | Generic JSON object          |
| `Void`      | `Void`                                           | No return value              |

### Custom Scalars

On a `scalar` declaration, pass one quoted string to `@spring` with a non-empty Java type and up to two options:

```qsdl
scalar UUID @spring("UUID")

scalar BigInt @spring("String, entity: java.math.BigInteger, pattern: ^-?[0-9]{1,38}$")

scalar Decimal @spring("String, entity: java.math.BigDecimal, pattern: ^(-)?[0-9][0-9]*(?:.[0-9]{1,18})?$")
```

The first segment is the Java type used in DTOs and APIs. Add
`entity: JavaType` to override the JPA entity type or `pattern: regex` to
validate the field. Separate segments with a comma and a space (`, `). Omit
the space within regex quantifiers, as in `{1,38}`, so the comma stays in the
pattern. Empty option values, unknown keys, and repeated keys are errors.

### Type Override Examples

**UUID scalar for IDs:**

```qsdl
scalar UUID @spring("UUID") @openapi("string, format: uuid")
```

**JSON subtype with validation:**

```qsdl
scalar StrictJson @spring("String, entity: java.util.Map, pattern: ^\\{.*\\}$")
```

## Generated Artifacts

### Entities

Entities are JPA-annotated classes mapped to database tables. For each `type` in your schema, a corresponding entity is generated. Entities extend the generated `AbstractEntity`, which centralizes ID handling (the ID column is `id` or `uid` depending on `id_type`):

```java
@Entity
@Table(name = "t_user")
public class UserEntity extends AbstractEntity {
    @Column(name = "name")
    private String name;

    // ... getters, setters
}
```

(`@Id`/`@GeneratedValue` live in `AbstractEntity`, not in each entity.)

### DTOs (Data Transfer Objects)

DTOs represent the API request/response layer. Object types always generate separate Request and Response DTOs (generated IDs are `@readOnly`, which forces the split); `@readOnly`/`@writeOnly` fields additionally control which fields appear on each side:

```java
// Request DTO (omits read-only fields like id, createdAt)
public class UserRequest {
    private String name;
    private String email;
}

// Response DTO (includes read-only fields)
public class UserResponse {
    private Long id;
    private String name;
    private String email;
    private OffsetDateTime createdAt;
}
```

### Mappers

Mappers provide bidirectional conversion between entities and DTOs:

```java
public class UserMapper {
    public UserEntity requestToEntity(UserRequest request) { ... }
    public UserResponse entityToResponse(UserEntity entity) { ... }
}
```

### Repositories

Spring Data repositories provide CRUD and custom query methods:

```java
public interface UserRepository extends JpaRepository<UserEntity, Long> {
    Optional<UserEntity> findByEmail(String email);
}
```

### Services

Services encapsulate business logic and transaction boundaries:

```java
@Service
public class UserService {
    public UserResponse createUser(UserRequest request) { ... }
    public UserResponse findById(Long id) { ... }
    public List<UserResponse> listAll() { ... }
    public UserResponse updateUser(Long id, UserRequest request) { ... }
    public void deleteUser(Long id) { ... }
}
```

### Controllers

Controllers expose REST endpoints:

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @PostMapping
    public ResponseEntity<UserResponse> create(@RequestBody UserRequest request) { ... }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> findById(@PathVariable Long id) { ... }

    @GetMapping
    public ResponseEntity<List<UserResponse>> list(UserListFilter filter) { ... }
}
```

## Generator-Specific Directives

Spring validates the following directives when it is selected; for other targets they stay opaque. The bundled OpenAPI and Flyway artifacts still honor valid `@openapi` and `@postgres` scalar mappings.

In Python, inspect the namespace with `api.directive.namespace`. An inherited
namespace node has `origin == "synthetic"` and does not override the object's
`@spring-package`.

### `@spring(...)`

Maps a scalar to Java types. See [Custom scalars](#custom-scalars) for the payload rules.

**Syntax:**

```
@spring("type [, entity: javaType] [, pattern: regex]")
```

**Example:**

```qsdl
scalar UUID @spring("UUID")
scalar Money @spring("BigDecimal, entity: java.math.BigDecimal, pattern: ^\\d+(\\.\\d{2})?$")
```

### `@spring-package`

Assigns a Java package on a `base`, `type`, `enum`, or `extend api`. The payload must be a single non-empty quoted string. It takes priority over `@namespace` and `package_placeholder_fallback` on the same declaration.

**Syntax:**

```
@spring-package("package_name")
```

**Example:**

```qsdl
type User @spring-package("user") {
    name: String!
}

// With the default base package: app/api/user/web/UserController.java
```

For an API, package selection follows this order:

1. `@spring-package` on the API.
2. A non-empty `@namespace` declared on the API, not an inherited namespace.
3. `@spring-package` or `@namespace` on its owning object.
4. `package_placeholder_fallback`.

An API-level namespace therefore can place an object API in a different package from the object's DTOs. `@spring-controller` controls which controller receives operations; when it targets an object controller, that object's package remains authoritative.

```qsdl
extend api @spring-package("user") {
    getUserStats(userId: Long!): Object @path("stats") @method(GET)
}
```

### `@spring-controller`

On `extend api`, pass a single non-empty quoted type name to move custom operations into that type's controller.

**Syntax:**

```
@spring-controller("TypeName")
```

**Example:**

```qsdl
extend api @spring-controller("User") {
    getUserStats(userId: Long!): Object @path("stats") @method(GET)
}

// With the default base package: app/api/user/web/UserController.java
// (merged with auto-generated User CRUD endpoints)
```

## Common Patterns

### Read-Only Nested Objects

Mark relationship fields with `@readOnly` to indicate they are populated by the database but never updated via API:

```qsdl
type Ticket {
    assignedUserId: Long @writeOnly
    assignedUser: User @readOnly
}
```

Generated controller:

```java
@JsonProperty(value = "assignedUserId", access = JsonProperty.Access.WRITE_ONLY)
private Long assignedUserId;

@JoinColumn(name = "assigned_user_id", insertable = false, updatable = false)
@JsonProperty(value = "assignedUser", access = JsonProperty.Access.READ_ONLY)
private UserEntity assignedUser;
```

### Query Parameters & Filtering

Fields marked with `@query` become optional filter parameters on list endpoints:

```qsdl
type User {
    name: String! @query
    email: String! @query
    createdAt: Date @readOnly
}
```

Generates a filter model:

```java
public class UserListFilter {
    private String name;
    private String email;
}

// And in controller:
@GetMapping
public ResponseEntity<List<UserResponse>> list(UserListFilter filter) { ... }
```

### Composition Relationships

Compositions represent parent-child hierarchies where children are deleted when parents are deleted:

```qsdl
type Project {
    name: String!
    tasks: [Task]! @composition
}

type Task {
    title: String!
}
```

Generated with cascading delete:

```java
@OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
private List<TaskEntity> tasks = new ArrayList<>();
```

### Aggregation Relationships

Aggregations represent many-to-many relationships managed through join tables:

```qsdl
type Student {
    name: String!
    courses: [Course]! @aggregation
}

type Course {
    title: String!
}
```

Generated with join table:

```java
@ManyToMany
@JoinTable(
    name = "t_student_courses",
    joinColumns = @JoinColumn(name = "student_id"),
    inverseJoinColumns = @JoinColumn(name = "course_id")
)
private List<CourseEntity> courses = new ArrayList<>();
```

## Limitations

- **Non-array Composition/Aggregation:** Composition and aggregation fields must be arrays (`[Type]!`). Singular relationships are not currently supported.
- **Orphan Removal:** The generated JPA cascade rules may not optimally handle orphan deletion in complex hierarchies. Review and tune `CascadeType` annotations post-generation if needed. (See: [Thorben Janssen on CascadeType.DELETE](https://thorben-janssen.com/avoid-cascadetype-delete-many-assocations/))
- **Custom Type Parsing:** Scalar override parsing splits by `", "` (comma + space). Regex patterns must not contain unescaped commas within the pattern value.
- **Manual Implementation Required:** The generator provides boilerplate and integration points, but business logic (service methods, repository queries, validation rules) must be implemented by hand.
