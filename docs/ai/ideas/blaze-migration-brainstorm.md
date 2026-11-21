# Brainstorming: Migrating Generated Spring Boot Services to Blaze-Persistence

> **Status: idea / exploratory assessment**
>
> This document records a possible direction for replacing QueryDSL in QSDL-generated Spring Boot services with Blaze-Persistence. It is a brainstorming document, not a committed implementation plan, roadmap, or design decision. The current generated service and QSDL generator are unchanged by this assessment.

## Executive assessment

The migration is feasible and significantly cheaper than jOOQ.

- The assessed generated service is a good candidate for Blaze-Persistence.
- A manual migration of this example would be low effort.
- Adding Blaze-Persistence as a supported QSDL Spring query backend would be low-medium effort.
- Unlike jOOQ, this is largely a query-layer replacement. Hibernate, the persistence context, dirty checking, entity lifecycle callbacks, lazy relationship handling, `@Version` optimistic locking, and ORM cascades all stay as-is. Those behaviors do not need to be reimplemented.

The strongest long-term architecture would be:

```text
QSDL -> JPA entities (unchanged) -> Blaze CriteriaBuilderFactory -> repositories/services
                                     + optional Entity Views for read projections
```

The JPA entity model remains the source of truth. Blaze-Persistence sits on top of `EntityManager`/Hibernate instead of replacing it. This avoids the schema-first rewrite that jOOQ requires.

## Current generated model

The assessed service is generated from `examples/00-pet-store/domain/pet-store.qsdl` and uses the generated output under `examples/00-pet-store/`.

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

Blaze-Persistence preserves this behavior unchanged. No ordered deletes or database-level cascades are needed.

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

Blaze-Persistence preserves this mapping unchanged. Explicit join-table handling is only needed where custom queries want it; standard CRUD still goes through the entity graph.

### Shared entity behavior

`AbstractEntity` provides:

- Internal numeric `Long id`
- External unique `uid`
- Optimistic locking through `iv`
- Creation and modification timestamps
- `@PrePersist` UID and creation-date generation
- `@PreUpdate` modification-date generation

The generated API uses external string IDs while relation queries and cursor pagination use the internal numeric ID. This distinction is preserved in a Blaze-Persistence implementation without extra work, since entities and lifecycle callbacks are untouched.

## QueryDSL usage

QueryDSL is used in a relatively small area:

- `common/db/BaseRepository.java`
- `common/db/BaseRepositoryImpl.java`
- `common/util/PredicateBuilder.java`
- Generated `Q*Entity` classes

The actual queries cover:

1. Generic count queries
2. Generic list queries
3. Cursor pagination (`id <= cursor`, `ORDER BY id DESC`, `limit + 1`)
4. Project-name filtering
5. Project/role parent filtering
6. Ticket/user join filtering

Downstream services additionally use `BaseRepository.queryFactory()` directly in repository `default` methods, e.g.:

```java
default List<Long> findWithMissingBlockInfo(BlockChainEnum blockChain, long limit) {
    var e = QBlockchainRawEventEntity.blockchainRawEventEntity;
    return queryFactory()
            .select(e.blockNumber)
            .distinct()
            .from(e)
            .where(e.blockChain.eq(blockChain), e.blockTimestamp.isNull().or(e.blockHash.isNull()))
            .orderBy(e.blockNumber.asc())
            .limit(limit)
            .fetch();
}
```

This is the pattern that motivates the migration: it is readable and strongly typed today, but it depends on APT-generated `Q*` classes, the `jakarta` classifier hack, and a `queryFactory()` leak on the repository interface. `@Query` strings recover none of those properties, which is why it is not an acceptable replacement for these call sites.

The existing relation predicates map directly to Blaze predicates:

```text
role.project.id = projectId
```

becomes `.where("role.project.id").eq(projectId)`, and:

```text
user.tickets.any().id = ticketId
```

becomes an explicit Blaze join or an `EXISTS` subquery. The QueryDSL replacement is therefore straightforward for this sample. The main non-trivial part is replacing Spring Data's automatic QueryDSL filter binding with an explicit, whitelisted filter builder.

## What maps cleanly to Blaze-Persistence

| Capability | Feasibility | Notes |
|---|---|---|
| Basic CRUD | High | Unchanged, still `JpaRepository` / `EntityManager` |
| Lookup by `uid` | High | Unchanged derived query |
| Project/role queries | High | Direct Blaze `where` on FK path or join |
| Ticket/user queries | High | Blaze join or `EXISTS` subquery over join table |
| Cursor pagination | High | Preserve `id <= cursor`, `ORDER BY id DESC`, `limit + 1`; optionally `PaginatedCriteriaBuilder` |
| Custom scalar scans | High | `cbf.create(em, Long.class).from(...).select("DISTINCT ...")`, closest readable 1:1 to QueryDSL |
| Dynamic `getAll` filters | High | Plain `if (filter.x() != null) cb.where(...)` instead of `BooleanBuilder` |
| DTOs/controllers | High | API layer can remain unchanged |
| MapStruct | High | Unchanged for writes; optionally complemented by Entity Views for reads |
| Flyway | High | Unchanged |
| Spring transactions | High | Unchanged, still JPA transaction manager and `@Transactional` |
| `fetchCount()` | High | Replaced by Blaze count query / `PaginatedCriteriaBuilder.getTotalCount()` |

Example 1 — the downstream scan above, rewritten 1:1:

```java
public List<Long> findWithMissingBlockInfo(BlockChainEnum blockChain, long limit) {
    if (blockChain == null || limit <= 0) {
        return List.of();
    }
    return cbf.create(em, Long.class)
            .from(BlockchainRawEventEntity.class, "e")
            .select("DISTINCT e.blockNumber")
            .where("e.blockChain").eq(blockChain)
            .whereOr()
                .where("e.blockTimestamp").isNull()
                .where("e.blockHash").isNull()
            .endOr()
            .orderByAsc("e.blockNumber")
            .setMaxResults((int) limit)
            .getResultList();
}
```

Example 2 — dynamic `getAll` filter with the existing `CursorPage` contract:

```java
public CursorPage<ProjectEntity> findAll(GetProjectsFilter filter, CursorPageable pageable) {
    var cb = cbf.create(em, ProjectEntity.class, "p")
            .where("p.id").le(pageable.cursor())
            .orderByDesc("p.id");

    if (filter != null && filter.name() != null) {
        cb.where("p.name").eq(filter.name());
    }

    int fetch = pageable.limit() + 1;
    List<ProjectEntity> items = cb.setMaxResults(fetch).getResultList();
    Long total = pageable.count() ? cb.getCountQuery().getSingleResult() : null;

    // existing limit+1 / Base64 cursor logic unchanged
    return toCursorPage(items, pageable, total);
}
```

Type-safe variant with the JPA static metamodel (`hibernate-jpamodelgen`, no QueryDSL APT):

```java
cb.where(ProjectEntity_.NAME.getName()).eq(filter.name());
```

## Behaviors requiring explicit design

Far fewer than jOOQ. The following Hibernate behaviors are inherited, not reimplemented:

- `uid` generation, timestamps, `@Version` increments
- Cascading deletes (`Project -> Role`)
- Join-table collection mutation (`Ticket <-> User`)
- Lazy loading within `@Transactional` services

What does need a decision:

### Filter semantics

`PredicateBuilder` delegates to Spring Data QueryDSL bindings. A Blaze backend must generate a whitelisted condition builder from QSDL `@query` fields. The generated code must define explicitly per field:

- Exact versus contains matching for strings
- Case sensitivity
- Null behavior
- Supported operators
- Date and enum conversion
- Collection handling

This is the same work as for jOOQ, but the result is smaller: plain `if`-guarded Blaze `where` clauses instead of a parallel SQL model.

### Strong typing level

Blaze `where("p.name")` is string-based by default. Three tiers are available:

1. String paths — most readable, refactor-fragile.
2. `SingularAttribute` names via static metamodel — `ProjectEntity_.NAME.getName()`, refactor-safe, still readable.
3. Entity Views as read models — fully typed getters for projections.

QSDL should generate tier 2 for filter paths. Tier 1 is acceptable for hand-written custom queries.

### Entity Views scope

Entity Views are optional. Recommended boundary:

- Keep MapStruct `DTO <-> entity` for writes.
- Use Entity Views only for hot read projections (list endpoints, join-heavy reads) to avoid N+1 and over-fetching.
- Do not make every DTO an Entity View on day one; that doubles the mapping layer.

```java
@EntityView(ProjectEntity.class)
public interface ProjectView {
    @IdMapping String getUid();
    String getName();
}
```

### Pagination helper ownership

Blaze offers `PaginatedCriteriaBuilder` with `page(first, size)`, `getResultList()`, and `getTotalCount()` (with count-query optimization). QSDL can either:

1. Keep the hand-rolled `limit + 1` cursor logic and use Blaze only as the query builder (minimal diff), or
2. Adopt `PaginatedCriteriaBuilder` for the `count=true` path.

Option 1 is recommended for the first migration; the cursor contract (`Base64(id)`, `id <= cursor`) stays byte-identical.

### `queryFactory()` custom-query pattern

Downstream `default` methods on generated repositories must move. Recommended replacement:

```text
db/
  BlockchainRawEventRepository.java        // generated, stays thin
  BlockchainRawEventScan.java             // hand-written, injects CriteriaBuilderFactory
```

Repositories should inject `CriteriaBuilderFactory` (or `EntityManager`) instead of exposing `queryFactory()` on the interface. This also fixes testability: the scan class is a plain bean, mockable without a database.

## Type and schema risks

Same schema notes as the jOOQ assessment apply, but severity is lower because Hibernate remains the mapper.

### Timestamp representation

The Flyway schema uses:

```sql
creation_date TIMESTAMP
modification_date TIMESTAMP
```

PostgreSQL `TIMESTAMP` is timestamp without time zone, while the Java model uses `OffsetDateTime`. The H2 Hibernate log also shows timestamp-with-time-zone columns being generated.

Blaze inherits Hibernate's mapping, so no new converter is needed. The underlying `TIMESTAMP` vs `TIMESTAMPTZ` inconsistency should still be resolved, but it is not a migration blocker for Blaze the way it is for jOOQ.

### JSONB

`ProjectEntity.metaInf` currently uses Hibernate JSON annotations and an `ObjectNodeConverter`. Blaze queries path through the entity, so JSONB keeps working unchanged. Only custom Blaze projections over `metaInf` need attention (select the attribute, convert at the mapper boundary, keep `ObjectNode` in DTOs).

### Enum storage

`Status` is stored as text with a check constraint rather than as a PostgreSQL enum. Blaze binds the enum the same way Hibernate does. No forced-type configuration needed.

### Schema selection

The PostgreSQL profile uses the `spring` schema, while the H2 profile uses its default schema. Blaze inherits the Hibernate schema handling, so no extra schema-qualification work is needed. PostgreSQL/Testcontainers should still be the primary persistence test environment.

### Version risk to verify: Blaze vs Boot 4 / Hibernate 7

Blaze-Persistence 1.6.x tracks Hibernate 6.x and Jakarta. Spring Boot 4.1 moves the Hibernate baseline forward. Before committing, verify the Blaze release matrix for:

- Hibernate 7 support (Blaze 1.7+ line, if required by Boot 4.1)
- `blaze-persistence-integration-hibernate-6` vs `-7` artifact coordinates
- `blaze-persistence-integration-spring-data` compatibility with Spring Data JPA on Boot 4
- GraalVM reachability metadata for `CriteriaBuilderFactory` / Entity Views, if native images are built

If Blaze lags the Boot 4 baseline, the fallback is `JpaSpecificationExecutor` + static metamodel (zero new runtime), with Blaze reintroduced once its Hibernate 7 integration is green.

## Recommended Blaze architecture

Do not recreate repositories. Keep the current structure and swap the query engine:

```text
common/
  db/
    BaseRepository.java          // JpaRepository, no queryFactory()/entityManager()
    BaseRepositoryImpl.java      // SimpleJpaRepository + CriteriaBuilderFactory
    BlazeConfig.java             // CriteriaBuilderFactory + EntityViewManager beans
  util/
    BlazeFilter.java             // replaces PredicateBuilder.QueryFilter plumbing
    CursorPage.java              // unchanged
    CursorPageable.java          // unchanged
```

Repositories inject one Spring-managed `CriteriaBuilderFactory` (and `EntityManager` where needed) and expose the same typed operations as today:

- `findByUid`
- `findPage` / `findAll(filter, pageable)`
- `findUsersForTicket`
- `findWithMissingBlockInfo`-style scans (moved out of `default` methods into scan beans)

Service and controller contracts remain unchanged. MapStruct remains unchanged except where an Entity View projection is deliberately introduced.

## QSDL generator impact

Smaller than jOOQ. The generator stays Hibernate-first; only the query layer changes.

### Configuration

`src/qsdl/generators/spring/config.py` currently supports `HIBERNATE` and `NO`. Blaze does not need a new persistence option like jOOQ does. It needs a query-backend switch within Hibernate, e.g. `query: QUERYDSL | BLAZE`, defaulting to Blaze for new schemas.

### Generator branches

`src/qsdl/generators/spring/generate.py` keeps emitting persistence artifacts for Hibernate. Only the query-related files branch:

- Keep: `Entity.j2`, `Repository.j2`, `AbstractRepository.j2`, `Service.j2`, `Operation.j2`
- Replace: `BaseRepository.j2`, `BaseRepositoryImpl.j2`, `PredicateBuilder.j2`
- Add: `BlazeConfig.j2`, per-model filter-builder fragment

### Templates requiring redesign

- `template/pom.j2` — swap `querydsl-apt`/`querydsl-jpa` for `blaze-persistence-*` + `hibernate-jpamodelgen`
- `template/src/main/java/repository/BaseRepository.j2` — remove `queryFactory()`/`entityManager()`/`query()`/`findAll(Predicate)`
- `template/src/main/java/repository/BaseRepositoryImpl.j2` — Blaze cursor pagination + count
- `template/src/main/java/util/PredicateBuilder.j2` — explicit per-field Blaze conditions from `@query` markers
- `template/src/main/java/config/AppConfiguration.j2` — `CriteriaBuilderFactory` bean
- Repository and service test templates — Blaze setup instead of QueryDSL predicates
- Optionally: Entity View template for read-heavy models

`BaseRepositoryImpl` can be adapted generically (unlike jOOQ). It keeps extending `SimpleJpaRepository` and keeps `EntityManager`; only the query construction moves from `JPAQueryFactory`/`PathBuilder` to `CriteriaBuilderFactory`.

### Shared relation metadata

The existing `HibernateModelInfo` / `HibernateParentInfo` metadata is sufficient. A Blaze backend needs, per `@query` field:

- Entity attribute path
- Exact vs contains matching
- Case sensitivity
- Operator set

No table/column/FK metadata is needed because Blaze queries the entity model, not the schema. This is the main generator-effort saving versus jOOQ.

### Query filter generation

Same contract as jOOQ — explicit per-field semantics — but simpler output: `if`-guarded Blaze clauses. There is still no drop-in for `QuerydslBindingsFactory`; each QSDL `@query` field maps to one generated condition.

## Dependency and configuration changes

The generated project would remove:

- `querydsl-apt`
- `querydsl-jpa`
- QueryDSL `annotationProcessorPaths` entries
- `-Aquerydsl.generatedAnnotationClass` compiler arg
- QueryDSL generated sources (`Q*Entity`)
- `org.springframework.data.querydsl.*` imports

It would add:

- `blaze-persistence-core`
- `blaze-persistence-integration-hibernate-6` (or `-7`, pending Boot 4.1 matrix check)
- `blaze-persistence-entity-view-api` (+ `entity-view-impl` + processor, only if Entity Views are used)
- `blaze-persistence-integration-spring-data` (only if `BlazeSpecificationExecutor` is wanted)
- `hibernate-jpamodelgen` as the annotation processor (replaces `querydsl-apt`)

Kept unchanged:

- `spring-boot-starter-data-jpa`
- Hibernate, Flyway, validation, Actuator, MapStruct, Testcontainers
- `spring.jpa.*` properties
- `@Transactional` semantics and JPA transaction manager
- `hypersistence-utils` JSON mapping (still valid under Blaze)

## Testing impact

Much smaller than jOOQ. Repository tests stay `@DataJpaTest` + Testcontainers PostgreSQL:

- Replace `BooleanBuilder` / `Q*` setup with filter DTOs + Blaze-backed `findAll`
- Keep `TestEntityManager` row setup
- Keep UID lookup, cascade, and optimistic-lock tests unchanged
- Add: cursor boundary tests through the Blaze path, dynamic-filter matrix per `@query` field, Entity View projection tests (if introduced)

The most important integration cases are unchanged from today:

- UID lookup
- Cursor pagination boundaries
- Project deletion with roles
- User deletion with ticket links
- Ticket deletion with ticket links
- Duplicate relation insertion
- Optimistic-lock conflicts
- JSONB round trips
- Timestamp mapping

No move to `@JooqTest`/`@JdbcTest` is needed.

## Suggested migration sequence

1. Freeze the current behavioral contract:
   - External IDs
   - Cursor semantics (`limit + 1`, `Base64(id)`, `id <= cursor`)
   - Null-inclusive updates
   - Java-side defaults
   - Delete behavior
   - Duplicate relation errors

2. Verify the Blaze vs Boot 4.1 / Hibernate version matrix and pin `blaze-persistence-*` accordingly.

3. Introduce `CriteriaBuilderFactory` bean alongside QueryDSL (dual-write phase for queries only).

4. Migrate `BaseRepositoryImpl` cursor pagination to Blaze, keeping the `CursorPage` contract byte-identical.

5. Migrate `PredicateBuilder` to per-field Blaze filter builders; migrate one model end-to-end (e.g. `Project`) before the rest.

6. Move downstream `default queryFactory()` scans into injectable scan beans on Blaze; delete `queryFactory()` from `BaseRepository`.

7. Optionally introduce Entity Views for one hot read path; measure before expanding.

8. Remove QueryDSL dependencies, APT paths, and `Q*` sources.

9. Add Blaze + static-metamodel generation to the QSDL Spring generator behind a query-backend switch.

## Final recommendation

For QueryDSL removal with readability and strong typing intact, Blaze-Persistence is the best fit while services stay on Hibernate.

Choose Blaze when the goal is:

- Keep the ORM (lifecycle, cascades, `@Version`, lazy handling)
- Keep `CursorPage` semantics and service/controller contracts
- Recover readable, dynamic, refactor-safe queries without `@Query` strings
- Minimize QSDL generator churn (query-layer swap, not new persistence backend)

Choose jOOQ instead only when the goal is explicit SQL, schema-first codegen, and dropping the persistence context — at the cost of reimplementing lifecycle, locking, and cascades documented in the jOOQ assessment.

For this codebase, the recommended sequence is Blaze now (low effort, preserves behavior), Entity Views selectively for hot reads, and no jOOQ migration unless a service outgrows the ORM.
