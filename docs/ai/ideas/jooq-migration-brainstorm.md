# Brainstorming: Migrating Generated Spring Boot Services to jOOQ

> **Status: idea / exploratory assessment**
>
> This document records a possible direction for replacing Hibernate and QueryDSL in QSDL-generated Spring Boot services with jOOQ. It is a brainstorming document, not a committed implementation plan, roadmap, or design decision. The current generated service and QSDL generator are unchanged by this assessment.

## Executive assessment

The migration is feasible.

- The assessed generated service is a good candidate for jOOQ.
- A manual migration of this example would be medium-low effort.
- Adding jOOQ as a supported QSDL Spring generator backend would be medium-high effort.
- The migration is not a dependency-only replacement. jOOQ has no persistence context, dirty checking, entity lifecycle callbacks, lazy relationship handling, or ORM cascades. Those behaviors must either be removed or implemented explicitly.

The strongest long-term architecture would be:

```text
QSDL -> PostgreSQL/Flyway schema -> jOOQ generated schema classes -> repositories/services
```

The generated PostgreSQL schema should be the source of truth for jOOQ code generation. This avoids independently reproducing database naming and relation rules in a Hibernate-oriented generator.

## Current generated model

The assessed service is generated from `examples/spring/relation.qsdl` and uses the generated output under `examples/spring/domain_layout`.

### Project and Role

`ProjectEntity` and `RoleEntity` model a one-to-many composition:

```text
t_project
  ^
t_role.roles_project_id
```

The relationship is represented by:

- `ProjectEntity.roles`, an inverse `@OneToMany` collection
- `RoleEntity.project`, the owning `@ManyToOne` relationship
- `CascadeType.ALL` on the project-side collection

Deleting a project through Hibernate therefore deletes its roles. The Flyway schema currently contains the foreign key but does not specify `ON DELETE CASCADE`.

### Ticket and User

`TicketEntity` and `UserEntity` model a many-to-many aggregation:

```text
t_ticket
    ^
t_ticket_to_t_user(ticket_id, user_id)
    v
t_user
```

The join table is owned by `UserEntity`; `TicketEntity` is the inverse side. The generated API exposes relation operations as separate endpoints instead of exposing entity collections directly.

This is jOOQ-friendly. The join table can be treated as a first-class repository concern rather than being represented as a bidirectional object graph.

### Shared entity behavior

`AbstractEntity` provides:

- Internal numeric `Long id`
- External unique `uid`
- Optimistic locking through `iv`
- Creation and modification timestamps
- `@PrePersist` UID and creation-date generation
- `@PreUpdate` modification-date generation

The generated API uses external string IDs while relation queries and cursor pagination use the internal numeric ID. This distinction must be preserved in a jOOQ implementation.

## QueryDSL usage

QueryDSL is used in a relatively small area:

- `common/db/BaseRepository.java`
- `common/db/BaseRepositoryImpl.java`
- `common/util/PredicateBuilder.java`
- Generated `Q*Entity` classes

The actual queries cover:

1. Generic count queries
2. Generic list queries
3. Cursor pagination
4. Project-name filtering
5. Project/role parent filtering
6. Ticket/user join filtering

There are no large custom QueryDSL queries or complicated projections in this example.

The existing relation predicates map directly to jOOQ conditions:

```text
role.project.id = projectId
```

becomes a condition on `t_role.roles_project_id`, and:

```text
user.tickets.any().id = ticketId
```

becomes an explicit join from `t_user` through `t_ticket_to_t_user`.

The QueryDSL replacement is therefore straightforward for this sample. The main non-trivial part is replacing Spring Data's automatic QueryDSL filter binding.

## What maps cleanly to jOOQ

| Capability | Feasibility | Notes |
|---|---|---|
| Basic CRUD | High | Direct `insert`, `select`, `update`, and `delete` statements |
| Lookup by `uid` | High | Unique database column already exists |
| Project/role queries | High | Foreign-key condition or explicit join |
| Ticket/user queries | High | Explicit join-table query |
| Cursor pagination | High | Preserve `id <= cursor`, `ORDER BY id DESC`, and `limit + 1` |
| PostgreSQL constraints | High | Existing keys, unique constraints, and check constraint are usable |
| DTOs/controllers | High | API layer can remain mostly unchanged |
| MapStruct | Medium | Mappers must target jOOQ records/POJOs or direct projections instead of entities |
| Flyway | High | Should remain the database migration mechanism |
| Spring transactions | High | Use a JDBC transaction manager with the Spring-managed `DSLContext` |

## Behaviors requiring explicit design

### Entity lifecycle callbacks

Hibernate currently performs several actions implicitly:

- Generates `uid` on insert
- Sets `creationDate`
- Sets `modificationDate` on update
- Initializes and increments the version field

jOOQ repository code must perform these actions explicitly. The insert path should set `uid`, creation timestamp, and the initial version. The update path should set the modification timestamp and increment the version.

### Optimistic locking

`iv` is currently a Hibernate `@Version` field. A jOOQ update should include the expected version in its predicate:

```text
update t_user
set name = ?, mail = ?, iv = iv + 1, modification_date = ?
where id = ? and iv = ?
```

The affected-row count must be checked. A result of zero should be treated as a stale version or missing row rather than silently succeeding.

### Cascading deletes

The Flyway baseline does not define `ON DELETE CASCADE`. Direct jOOQ deletes must therefore delete dependent records first.

Deleting a project requires either:

```text
delete from t_role where roles_project_id = ?
delete from t_project where id = ?
```

or a database-level cascade.

Deleting a user or ticket requires clearing rows in `t_ticket_to_t_user` first. Otherwise the foreign-key constraints can reject the parent deletion.

Two valid strategies exist:

1. Preserve the existing schema and implement ordered deletes in repositories.
2. Add a Flyway migration with explicit database-level cascades.

Database-level cascades would be reasonable for the current composition and join-table semantics, but would constitute an intentional schema behavior change.

### Relation add/remove concurrency

The current add operation loads a user, checks the collection, mutates it, and saves the entity. A jOOQ implementation can directly insert into the join table.

The join-table primary key already prevents duplicate links. PostgreSQL-specific code could use `ON CONFLICT DO NOTHING` and interpret an affected-row count of zero as the existing “already attached” application error.

Removal should use both relation keys:

```text
delete from t_ticket_to_t_user
where ticket_id = ? and user_id = ?
```

This is simpler and avoids loading an entity graph.

## Type and schema risks

### Timestamp representation

The Flyway schema uses:

```sql
creation_date TIMESTAMP
modification_date TIMESTAMP
```

PostgreSQL `TIMESTAMP` is timestamp without time zone, while the Java model uses `OffsetDateTime`. The H2 Hibernate log also shows timestamp-with-time-zone columns being generated.

This means the H2-generated schema and PostgreSQL Flyway schema are not fully equivalent. jOOQ will likely map PostgreSQL `TIMESTAMP` to `LocalDateTime` unless a custom forced type or converter is configured.

Before migration, decide whether to:

- Use `TIMESTAMPTZ` and retain `OffsetDateTime`
- Keep `TIMESTAMP` and use `LocalDateTime`
- Add an explicit jOOQ converter/forced type

This issue exists independently of jOOQ and should be resolved before relying on generated type mappings.

### JSONB

`ProjectEntity.metaInf` currently uses Hibernate JSON annotations and an `ObjectNodeConverter`. jOOQ will normally expose PostgreSQL JSONB as `org.jooq.JSONB`.

A suitable boundary would be:

- Use jOOQ `JSONB` inside the repository
- Convert to/from Jackson 3 `ObjectNode` at the repository or mapper boundary
- Keep `ObjectNode` in the API DTOs

A custom jOOQ binding is possible but is probably unnecessary for this service.

### Enum storage

`Status` is stored as text with a check constraint rather than as a PostgreSQL enum. jOOQ can safely use `status.name()` for writes and `Status.valueOf(...)` for reads. A jOOQ forced type can be added later if stronger generated typing is desired.

### Schema selection

The PostgreSQL profile uses the `spring` schema, while the H2 profile currently uses its default schema. jOOQ code generation and runtime rendering must agree on whether tables are schema-qualified.

Because JSONB, timestamps, and schema behavior differ between the profiles, PostgreSQL/Testcontainers should be the primary persistence test environment. H2 should only remain supported if its compatibility is deliberately verified.

## Recommended jOOQ architecture

The jOOQ implementation should not recreate the Hibernate entity graph.

A possible structure is:

```text
db/
  jooq/generated/
    Tables.java
    TProject.java
    TProjectRecord.java
    ...
  ProjectRepository.java
  RoleRepository.java
  UserRepository.java
  TicketRepository.java
  TicketUserRelationRepository.java
```

Repositories should inject one Spring-managed `DSLContext` and expose typed operations such as:

- `findByUid`
- `findPage`
- `insert`
- `update`
- `delete`
- `findByProjectUidAndUid`
- `findUsersForTicket`
- `addUserToTicket`
- `removeUserFromTicket`

The service and controller contracts can remain mostly unchanged.

MapStruct may remain, but mappings need to change from:

```text
DTO <-> JPA entity
```

to either:

```text
jOOQ record/POJO <-> DTO
```

or direct jOOQ projections into DTOs. Direct projections are likely preferable for API reads because they avoid loading columns and relationships that are not part of the response.

## QSDL generator impact

The current Spring generator is strongly coupled to Hibernate/JPA.

### Configuration

`src/qsdl/generators/spring/config.py` currently supports `HIBERNATE` and `NO`. jOOQ would need to be introduced as a first-class persistence option, such as `JOOQ`.

### Generator branches

`src/qsdl/generators/spring/generate.py` only emits persistence artifacts for Hibernate. Services also return no persistence implementation for non-Hibernate modes. jOOQ therefore needs its own generation branch.

### Templates requiring redesign

At least the following areas are Hibernate-specific:

- `template/pom.j2`
- `template/src/main/resources/application.j2`
- `template/src/main/java/config/AppConfiguration.j2`
- `template/src/main/java/domain/Entity.j2`
- `template/src/main/java/repository/Repository.j2`
- `template/src/main/java/repository/BaseRepository.j2`
- `template/src/main/java/repository/BaseRepositoryImpl.j2`
- `template/src/main/java/service/Service.j2`
- `template/_macro/Operation.j2`
- `template/src/main/java/util/PredicateBuilder.j2`
- Repository and service test templates

`BaseRepositoryImpl` should not be adapted generically. It depends on `SimpleJpaRepository`, `EntityManager`, `JPAQueryFactory`, and Hibernate dirty checking. A jOOQ backend should generate typed repositories instead.

### Shared relation metadata

The generator currently creates `HibernateModelInfo` and `HibernateParentInfo`. A jOOQ backend needs metadata for:

- Table and column names
- Parent foreign-key columns
- Join-table names and columns
- Insertable and updateable fields
- Projection fields
- Cursor field
- Version field

This metadata should preferably be derived from the PostgreSQL schema generator or generated jOOQ schema rather than duplicating Hibernate naming rules. This matters for names such as `roles_project_id`, which are based on the relation field name.

### Query filter generation

`PredicateBuilder` delegates to Spring Data QueryDSL binding. A jOOQ backend should generate a whitelisted condition builder from QSDL query fields.

The generated filter implementation must define explicitly:

- Exact versus contains matching for strings
- Case sensitivity
- Null behavior
- Supported operators
- Date and enum conversion
- Collection handling

This is manageable but has no direct drop-in replacement.

## Dependency and configuration changes

The generated project would likely remove:

- `spring-boot-starter-data-jpa`
- `querydsl-apt`
- `querydsl-jpa`
- Hibernate-specific utility libraries
- `hypersistence-utils-hibernate`
- Hibernate Envers when auditing is enabled
- JPA test dependencies
- QueryDSL generated sources
- `EntityManager` and `TestEntityManager`

It would add:

- `spring-boot-starter-jooq`
- jOOQ code-generation Maven configuration
- PostgreSQL code-generation support

Spring MVC, validation, Flyway, P6Spy, Actuator, MapStruct, and Testcontainers can remain.

The generated `spring.jpa.*` properties should be removed. Spring `@Transactional` can remain, provided the application uses a JDBC transaction manager and the jOOQ `DSLContext` participates in that transaction.

## Testing impact

The current repository tests use:

- `@DataJpaTest`
- `TestEntityManager`
- JPA repository interfaces
- QueryDSL predicates
- Entity collection mutation
- Hibernate cascade behavior

They would need to use jOOQ/JDBC-oriented tests, such as `@JooqTest` or `@JdbcTest`, with explicit row setup.

The most important integration cases are:

- UID lookup
- Cursor pagination boundaries
- Project deletion with roles
- User deletion with ticket links
- Ticket deletion with ticket links
- Duplicate relation insertion
- Optimistic-lock conflicts
- JSONB round trips
- Timestamp mapping
- PostgreSQL schema selection

The existing Testcontainers PostgreSQL setup is useful. The repository tests currently use H2, but PostgreSQL should be preferred for dialect-sensitive persistence behavior.

## Suggested migration sequence

1. Freeze the current behavioral contract:
   - External IDs
   - Cursor semantics
   - Null-inclusive updates
   - Java-side defaults
   - Delete behavior
   - Duplicate relation errors

2. Resolve schema inconsistencies:
   - `TIMESTAMP` versus `TIMESTAMPTZ`
   - `spring` schema handling
   - JSONB mapping
   - Database-level cascade policy

3. Make Flyway/PostgreSQL authoritative for jOOQ code generation.

4. Generate jOOQ classes from a reproducible migrated schema, not from production credentials.

5. Implement typed jOOQ repositories for the four model tables and the ticket/user join table.

6. Replace entity mutation in services with explicit insert/update/delete operations.

7. Preserve transactions, optimistic locking, defaults, and application-level error mapping.

8. Replace JPA/QueryDSL configuration and tests.

9. Remove the old dependencies and generated QueryDSL/JPA artifacts.

10. Add a first-class `JOOQ` backend to the QSDL Spring generator.

## Final recommendation

For the generated example, jOOQ is technically viable and should not require a database data migration if the existing schema is retained.

The migration is most attractive when the target services need:

- Explicit SQL and predictable joins
- Efficient projections/read models
- More complex PostgreSQL-specific queries
- Less ORM lifecycle behavior
- Better alignment between Java code and the actual database schema

For this small example, performance alone is not a sufficient reason to migrate. The primary benefits would be explicit persistence behavior and a schema-first architecture.

For QSDL itself, jOOQ should be implemented as a separate persistence backend rather than as a set of conditional changes to the Hibernate templates. The existing relation model is compatible with jOOQ, but composition, aggregation, lifecycle, filtering, and optimistic locking must be represented explicitly in the generated repositories and services.
