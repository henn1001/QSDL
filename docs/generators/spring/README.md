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

## Configuration

All configuration options are provided either via a `config.json` file or CLI arguments.

| Name                           | Type                       | Default                         | Description                                                                   | Required |
| ------------------------------ | -------------------------- | ------------------------------- | ----------------------------------------------------------------------------- | -------- |
| `title`                        | string                     | `"SpringBootApp"`               | Application name; used for the main entry class.                              | No       |
| `group_id`                     | string                     | `"app"`                         | Maven group ID (reverse domain notation).                                     | No       |
| `artifact_id`                  | string                     | `"app"`                         | Maven artifact ID.                                                            | No       |
| `base_package`                 | string                     | `"app.server"`                  | Root Java package; all paths are relative to this.                            | No       |
| `database`                     | enum (`HIBERNATE` \| `NO`) | `HIBERNATE`                     | Enable Hibernate JPA annotations and persistence layer.                       | No       |
| `use_auditing`                 | boolean                    | `false`                         | Enable automatic audit fields (createdBy, createdAt, modifiedBy, modifiedAt). | No       |
| `table_prefix`                 | string                     | `"t_"`                          | Prefix for database table names.                                              | No       |
| `id_type`                      | enum (`LONG` \| `STRING`)  | `LONG`                          | ID type for domain objects (affects OpenAPI generation too).                  | No       |
| `api_path`                     | string                     | `"%placeholder%.api"`           | Package path for API endpoints.                                               | No       |
| `controller_path`              | string                     | `"%placeholder%.api"`           | Package path for controllers.                                                 | No       |
| `service_path`                 | string                     | `"%placeholder%.service"`       | Package path for services.                                                    | No       |
| `domain_path`                  | string                     | `"%placeholder%.domain"`        | Package path for DTOs and request/response models.                            | No       |
| `entity_path`                  | string                     | `"%placeholder%.domain.entity"` | Package path for Hibernate entities.                                          | No       |
| `mapper_path`                  | string                     | `"%placeholder%.domain.mapper"` | Package path for mappers (DTO ↔ Entity).                                      | No       |
| `repository_path`              | string                     | `"%placeholder%.repository"`    | Package path for Spring Data repositories.                                    | No       |
| `enum_path`                    | string                     | `"%placeholder%.constant"`      | Package path for enum types.                                                  | No       |
| `exception_path`               | string                     | `"%placeholder%.exception"`     | Package path for exception classes.                                           | No       |
| `model_path`                   | string                     | `"%placeholder%.model"`         | Package path for shared model/support classes.                                | No       |
| `config_path`                  | string                     | `"%placeholder%.config"`        | Package path for configuration classes.                                       | No       |
| `util_path`                    | string                     | `"%placeholder%.util"`          | Package path for utility classes.                                             | No       |
| `package_placeholder_fallback` | string                     | `"global"`                      | Fallback package name when `@spring-package` is not specified.                | No       |

**Note:** Path configuration accepts a placeholder token `%placeholder%` which is automatically replaced with the containing package (from `@spring-package` directive) or the fallback value.

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

The generator produces a Maven-based Spring Boot project with the following layout:

```
src/
├── main/
│   ├── java/
│   │   └── com/example/travel/
│   │       ├── TravelAPI.java               (Spring Boot entry point)
│   │       ├── <package>/
│   │       │   ├── api/                     (Controllers)
│   │       │   ├── service/                 (Business logic)
│   │       │   ├── dto/                     (Request/Response DTOs)
│   │       │   ├── entity/                  (JPA entities)
│   │       │   ├── mapper/                  (DTO ↔ Entity mappers)
│   │       │   └── repository/              (Spring Data repositories)
│   │       ├── constant/                    (Enums)
│   │       ├── exception/                   (Custom exceptions)
│   │       ├── model/                       (Shared models: CursorPage, AppError, etc.)
│   │       ├── config/                      (Spring configuration)
│   │       └── util/                        (Utility classes)
│   └── resources/
│       ├── application.yml                  (Spring application config)
│       ├── application-dev.yml              (Development profile)
│       ├── logback-spring.xml               (Logging configuration)
│       └── db/migration/                    (Flyway DB migrations, if postgres generated)
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
└── .qsdl-ignore                              (Files to exclude from generation)
```

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

This generates:

```
└── com/example/travel/
    ├── user/
    │   ├── api/UserController.java
    │   ├── dto/UserRequest.java
    │   ├── entity/UserEntity.java
    │   ├── mapper/UserMapper.java
    │   ├── repository/UserRepository.java
    │   └── service/UserService.java
    ├── order/
    │   ├── api/OrderController.java
    │   ├── dto/OrderRequest.java
    │   ├── entity/OrderEntity.java
    │   └── ...
    └── common/                             (shared cross-domain code)
        ├── config/
        ├── constants/
        ├── exception/
        ├── model/
        └── util/
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

Define custom scalar types using the `@spring` directive. The directive accepts up to three comma-separated values:

```qsdl
scalar UUID @spring("UUID")

scalar BigInt @spring("String, entity: java.math.BigInteger, pattern: ^-?[0-9]{1,38}$")

scalar Decimal @spring("String, entity: java.math.BigDecimal, pattern: ^(-)?[0-9][0-9]*(?:.[0-9]{1,18})?$")
```

The three optional fields are:

- **type** (first position, or unnamed): Java type for DTOs/API layer.
- **entity**: Java type for JPA entity layer (if different from API type).
- **pattern**: Regex validation pattern for the field.

**Important:** Parsing is done by splitting on `", "` (comma + space). Ensure you include the space after commas in your regex patterns.

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

Entities are JPA-annotated classes mapped to database tables. For each `type` in your schema, a corresponding entity is generated:

```java
@Entity
@Table(name = "t_user")
public class UserEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name")
    private String name;

    // ... getters, setters
}
```

### DTOs (Data Transfer Objects)

DTOs represent the API request/response layer. By default, a single DTO is generated per type. If a type has `@readOnly` or `@writeOnly` fields, the generator creates separate Request and Response DTOs:

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
    private LocalDateTime createdAt;
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

The Spring generator recognizes four custom directives for fine-tuning code generation:

### `@spring(...)`

Maps a scalar type to a Java type. Accepts up to three comma-separated fields:

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

Assigns a custom package namespace for code generation. Overrides the `package_placeholder_fallback` for a specific domain object:

**Syntax:**

```
@spring-package("package_name")
```

**Example:**

```qsdl
type User @spring-package("user") {
    name: String!
}

// Generates: com/example/travel/user/api/UserController.java
```

When applied to a top-level `extend api`, it groups custom operations into a dedicated controller:

```qsdl
extend api @spring-package("user") {
    getUserStats(userId: Long!): Object @path("stats") @method(GET)
}
```

### `@spring-controller`

Moves custom API operations into a different controller (by type name). Useful when multiple custom endpoints logically belong to the same domain entity:

**Syntax:**

```
@spring-controller("TypeName")
```

**Example:**

```qsdl
extend api @spring-controller("User") {
    getUserStats(userId: Long!): Object @path("stats") @method(GET)
}

// Generates: com/example/travel/user/api/UserController.java
// (merged with auto-generated User CRUD endpoints)
```

### `@spring-void-input`

Suppress argument generation for custom operations. Useful for endpoints that do not accept a request body:

**Syntax:**

```
@spring-void-input
```

**Example:**

```qsdl
extend api {
    uploadFile(file: MultipartFile!, docType: String, entityId: UUID!): Void
        @path("upload")
        @method(POST)
        @consumes("multipart/form-data")
        @spring-void-input
}
```

This prevents the generator from creating a request DTO for the operation. You implement the handler manually with direct multipart extraction.

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

### File Upload

Multipart file uploads use custom scalars and the `@spring-void-input` directive:

```qsdl
scalar MultipartFile @openapi("string, format: binary") @spring("MultipartFile")

extend api {
    uploadFile(file: MultipartFile!, docType: String, entityId: UUID!): Void
        @path("upload")
        @method(POST)
        @consumes("multipart/form-data")
        @spring-void-input
}
```

Implement the multipart handling manually:

```java
@PostMapping("/upload")
public ResponseEntity<Void> uploadFile(HttpServletRequest request) throws Exception {
    StandardMultipartHttpServletRequest context = new StandardMultipartHttpServletRequest(request);
    MultipartFile file = context.getFile("file");
    String docType = context.getParameter("docType");
    String entityId = context.getParameter("entityId");

    // ... handle file upload
    return new ResponseEntity<>(HttpStatus.NO_CONTENT);
}
```

## Limitations

- **Non-array Composition/Aggregation:** Composition and aggregation fields must be arrays (`[Type]!`). Singular relationships are not currently supported.
- **Orphan Removal:** The generated JPA cascade rules may not optimally handle orphan deletion in complex hierarchies. Review and tune `CascadeType` annotations post-generation if needed. (See: [Thorben Janssen on CascadeType.DELETE](https://thorben-janssen.com/avoid-cascadetype-delete-many-assocations/))
- **Custom Type Parsing:** Scalar override parsing splits by `", "` (comma + space). Regex patterns must not contain unescaped commas within the pattern value.
- **Manual Implementation Required:** The generator provides boilerplate and integration points, but business logic (service methods, repository queries, validation rules) must be implemented by hand.
