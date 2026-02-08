# QSDL Overview

This page explains **what QSDL is**, **why you would use it**, and **how typical workflows work**.

## What is QSDL?

QSDL (Schema-Definition Language) is a minimal, expressive language for describing domain models and APIs. It lets you define your business entities, their relationships, and their API operations **once**, then generate consistent specifications and boilerplate code across multiple target platforms.

Think of it as a **single source of truth** for your domain model:

```qsdl
type User {
  email: String!
  name: String
  posts: [Post]  # Relationship to posts
}

type Post {
  title: String!
  content: String
  author: User!  # Back-reference
}
```

From this simple definition, QSDL can automatically generate:

- A complete **OpenAPI specification** (REST API contract)
- **Spring Boot entities and repositories** (with annotations and CRUD services)
- **PostgreSQL Schema** (create and manage database schema)
- **PlantUML diagrams** (visualize your domain model)

## Why QSDL?

### The Problem It Solves

When building APIs and services, you often need to maintain multiple representations of the same domain:

1. **Database schema** — SQL Schema or ORM mappings
2. **API contract** — OpenAPI/Swagger specifications
3. **Backend code** — Entity classes, DTOs, repositories, services
4. **Documentation** — Diagrams, relationships, constraints

Keeping these in sync is tedious and error-prone. If you change a field name, you must update:

- The database schema
- The entity class
- The DTO
- The API spec
- The documentation

**QSDL eliminates this friction** by generating all of these from a single schema definition.

### Key Principles

**1. Domain-centric thinking**

Define your domain model first. The API, database, and code follow naturally.

**2. Minimal ceremony**

No boilerplate in your schema. A simple `type` declaration generates full CRUD operations automatically. Override only when you need to.

**3. Consistency across tools**

Whether you're generating OpenAPI specs, Spring Boot code, or database schemas, the source of truth is identical. No more mismatches between the API spec and the database schema.

**4. Framework and language agnostic**

QSDL generates targets for different frameworks (Spring Boot, etc.) and multiple representation formats. You can use the same schema to generate specifications and code across different backends.

### Microservices: Synchronized API Contracts

QSDL is especially powerful in **microservice architectures** where multiple services need to work together. The problem: when services depend on shared data types, adding a field to a type affects all consuming services.

**Without QSDL:**

- Each service maintains its own API spec and data models
- A field change in one service requires manual updates in all dependent services
- Easy to miss a service—leading to API mismatches and bugs
- No visibility into which services are affected by a change

**With QSDL:**

- Define your **shared domain model once** in a central schema file
- All services generate from the same schema
- When you add a field, regenerate all services immediately
- **Version control** tracks exactly which services depend on what
- OpenAPI specs stay synchronized across services
- Database schemas align across services

**Example:** Three microservices that depend on a shared `User` type:

```qsdl
// shared/domain.qsdl
type User {
  id: String!
  email: String!
  name: String!
  department: String  # New field added
}
```

When you add `department`:

- All three services regenerate with the new field
- All APIs stay in sync
- All databases get the new column
- No manual coordination needed

This is **critical for maintaining consistency** in distributed systems where API contracts between services must work together.

## Common Workflows

### API-First Development

Design your API contract before writing backend code. Define your domain types in QSDL, then generate an OpenAPI specification for frontend teams to build against while backend teams implement the generated server code.

### Backend Scaffolding

Quickly bootstrap backend services. Define your domain model once, then generate Spring Boot entities, repositories, and services alongside a synchronized PostgreSQL schema—all from the same schema file.

### Synchronized Documentation

Keep architecture diagrams and entity relationship diagrams automatically in sync with your domain model. Generate PlantUML diagrams whenever your schema changes.

## Generation Targets

QSDL includes generators for multiple output formats. While each can be used independently, some are tightly coupled to work together seamlessly.

### OpenAPI

Generates an OpenAPI 3.0+ specification in YAML or JSON. Useful for:

- **API contract definition** — Document your REST API before implementation
- **API documentation** — Auto-generated, always in sync with your schema
- **Client code generation** — Feed the spec into OpenAPI Generator or similar tools

The OpenAPI generator is the **canonical API contract**. Other generators (especially Spring Boot) implement this contract directly.

### Spring Boot

Generates Java code for a Spring Boot application:

- JPA `@Entity` classes with field mappings
- Spring Data `@Repository` interfaces
- `@Service` classes with CRUD boilerplate
- `@RestController` classes with mapped endpoints

**Tightly coupled:** The Spring Boot generator **implements the OpenAPI contract** generated from your schema. REST endpoints, request/response schemas, and HTTP methods are derived from the same domain definition. It also pairs naturally with the PostgreSQL generator for database schema synchronization—entities map to tables, foreign keys to relationships.

### PostgreSQL

Generates SQL schema scripts:

- `CREATE TABLE` statements matching your domain model
- Column types derived from QSDL scalars
- Foreign keys and constraints
- Automatic schema versioning

**Tightly coupled:** Works seamlessly with Spring Boot—JPA entity annotations map directly to SQL columns and constraints. Both maintain consistency with the same domain definition.

### PlantUML

Generates PlantUML diagram source:

- Class diagrams showing entity structures
- ER diagrams showing relationships
- Inheritance hierarchies

Useful for architecture documentation and visualization. Can be generated independently or alongside code generation.

### i18n

Generates internationalization (i18n) resource files:

- Property files for multiple languages
- Localized labels, descriptions, and enum values

Supports translating domain model metadata for multi-language applications.

### Void

A no-op generator that validates the schema without producing output. Useful for:

- Linting and validation
- Catching schema errors early in CI/CD

No actual code generation—just schema validation.

## Next Steps

**Pick a starting point based on your goal:**

### Jump into the Language

Start here if you want to learn QSDL syntax and begin writing schemas:

- **[Language overview](./core/language.md)** — Learn syntax, type definitions, and basic structure
- **[Basic data modeling](./guides/basic-data-modeling.md)** — Best practices for designing domain models
- **[Relationships](./guides/relationships.md)** — Master composition, aggregation, and relationship patterns
- **[Directives](./core/directives.md)** — Learn annotations that control generation behavior

### Use the CLI to Generate

Ready to generate code? Start here:

- **[CLI documentation](./cli.md)** — Command-line usage, options, and examples
- **[Generator documentation](./generators/README.md)** — Overview of all available generators

### Explore Generator-Specific Docs

Dive deep into a specific generator:

- **[OpenAPI](./generators/openapi/README.md)** — API specification generation
- **[Spring Boot](./generators/spring/README.md)** — Java backend code generation
- **[PostgreSQL](./generators/postgres/README.md)** — Database schema generation
- **[PlantUML](./generators/plantuml/README.md)** — Diagram generation
- **[i18n](./generators/i18n/README.md)** — Internationalization resources
- **[Void](./generators/void/README.md)** — Schema validation

### Get Help

- **[Rules & Requirements](./core/rules.md)** — Schema constraints and validation rules
- **[FAQ](./reference/faq.md)** — Common questions and troubleshooting
- **[Glossary](./reference/glossary.md)** — QSDL terminology
