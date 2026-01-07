# Change Request: Base Type Handling - Introduce `@opaque` for Opaque Storage

## Status
**Proposed** - Implementation pending
**Scope:** PostgreSQL generator (BREAKING CHANGE) & Spring Boot generator (NEW)
**Priority:** Medium - Fix incorrect `@opaque` semantics, introduce `@opaque` directive
**Implementation Order:** PostgreSQL fixes → Spring Boot implementation

## Executive Summary

**Critical Issue:** The PostgreSQL generator implements `@opaque` with **incorrect semantics** - it currently means "flatten columns" but should mean "opaque storage" (JSONB) for optimization.

**Design Philosophy:**
- **Base types** are value objects for grouping fields, not real domain entities
- **Real relationships** should use `type` (Object) with `@composition` or `@aggregation`
- **Default behavior:** Flatten base type fields into parent table (simple value objects)
- **`@opaque` directive:** Database-level hint for opaque storage (JSONB by default, user can optimize to separate table)
- **Keep it simple:** Replace `@opaque` with `@opaque`, one clear optimization path

**Current State (INCORRECT):**
- **PostgreSQL:** `@opaque` = flatten columns ❌ (wrong semantics!)
- **PostgreSQL:** Default = separate table with FK ❌ (should flatten!)
- **Spring Boot:** Ignores `@opaque` completely ❌ (not implemented)
- **Directive name:** `@opaque` confuses with JPA `@Embeddable` ❌

**Correct Semantics (This Proposal):**
- **Default (no directive):** `field: Base` → Flatten columns with prefix (value object)
- **`@opaque` directive:** `field: Base @opaque` → Opaque storage (JSONB or separate table)
- **For real relationships:** Use `type` with `@composition`/`@aggregation` (NOT base types)

**Proposed solution:**
1. **Rename directive:** `@opaque` → `@opaque` (clearer semantics)
2. **Fix PostgreSQL:**
   - Change default from FK to flattening (BREAKING)
   - Change `@opaque` (was `@opaque`) from flattening to JSONB (BREAKING)
3. **Implement in Spring Boot:**
   - Default: JPA `@Embedded` with `@AttributeOverrides`
   - `@opaque`: Hibernate `@JdbcTypeCode(SqlTypes.JSON)`
4. **Multi-generator friendly:** OpenAPI ignores `@opaque` (still nested object in spec)

**Why `@opaque`:**
- ✅ Database optimization hint, not API concern
- ✅ Doesn't imply specific storage (JSONB, separate table, etc.)
- ✅ No confusion with JPA `@Embeddable`
- ✅ User can change implementation post-generation

**Impact:**
- **Default users:** ⚠️ BREAKING - Changes from FK to flattened columns
- **`@opaque` users:** ⚠️ BREAKING - Rename to `@opaque`, changes from flattened to JSONB
- **Migration:** Replace `@opaque` with `@opaque`, schema changes required
- Better semantics: Base types as value objects by default, `@opaque` for optimization

## Detailed Summary

Fix the PostgreSQL generator's incorrect `@opaque` semantics (currently means "flatten" but should mean "JSONB"), then implement correct semantics in Spring Boot generator. Default behavior for base type fields should be column flattening (simpler, better for value objects), not separate entity tables.

## Current State Analysis

### PostgreSQL Generator ❌ WRONG SEMANTICS
**File:** `src/qsdl/generators/postgres/models/table.py:108-110`

| Scenario | Current Behavior | Semantic Issue |
|----------|------------------|----------------|
| `field: Base` (no directive) | Creates separate table with FK | ❌ Too complex for value objects |
| `field: Base @opaque` | Flattens columns with prefix | ❌ **Wrong!** Should be JSONB |
| `field: [Base]` | Creates join table | ✅ Correct |

**Test:** `tests/functional/generators/test_postgres.py:304`
- ✅ Passes but tests WRONG behavior
- ⚠️ Needs update after fix

**Problem:** The directive name `@opaque` suggests "embedded in document/JSON" but currently means "embedded in table columns".

### Spring Boot Generator ❌ NOT IMPLEMENTED
**File:** `src/qsdl/generators/spring/template/_macro/Hibernate.j2:59-64`

| Scenario | Current Behavior | Issue |
|----------|------------------|-------|
| `field: Base` | `@OneToOne` + separate entity | Too complex for value objects |
| `field: Base @opaque` | **Ignores directive**, still `@OneToOne` | Not implemented |
| `field: [Base]` | `@OneToMany` + separate entity | Correct (join table) |

**Problem:** Ignores `@opaque` directive completely, always creates entity relationships.

## Visual Overview

### Current Behavior - BOTH WRONG
```
QSDL: type User { address: Address }  // No directive
         ↓
PostgreSQL: Creates FK to separate table ❌
CREATE TABLE t_user (
  id BIGINT PRIMARY KEY,
  address_address_id BIGINT REFERENCES t_address(id)
);
CREATE TABLE t_address (id BIGINT PRIMARY KEY, street TEXT, city TEXT);
         ↓
Spring: Creates @OneToOne entity ❌
@OneToOne
@JoinColumn(name = "address_address_id")
private AddressEntity address;
→ Two tables for a value object!
```

```
QSDL: type User { address: Address @opaque }
         ↓
PostgreSQL: Flattens columns ❌ (should be JSONB!)
CREATE TABLE t_user (
  id BIGINT PRIMARY KEY,
  address_street TEXT,
  address_city TEXT
);
         ↓
Spring: Ignores directive ❌
@OneToOne  // Still creates entity, ignores @opaque!
private AddressEntity address;
→ Schema mismatch: flattened SQL vs entity relationship
```

### Proposed Behavior - Default Flattening ✅
**Default (no directive):** Value object, flatten into parent table

```
QSDL: type User { address: Address }  // No directive
         ↓
PostgreSQL: Flatten columns ✅ (NEW)
CREATE TABLE t_user (
  id BIGINT PRIMARY KEY,
  address_street TEXT,
  address_city TEXT
);
         ↓
Spring: JPA @Embedded ✅ (NEW)
@Embedded
@AttributeOverrides({
  @AttributeOverride(name = "street", column = @Column(name = "address_street")),
  @AttributeOverride(name = "city", column = @Column(name = "address_city"))
})
private AddressEmbeddable address;
         ✅ ONE TABLE, VALUE OBJECT SEMANTICS
```

### Proposed Behavior - JSONB with @opaque ✅
**`@opaque` directive:** Optimization for JSONB document storage

```
QSDL: type User { address: Address @opaque }
         ↓
PostgreSQL: JSONB storage ✅ (FIXED!)
CREATE TABLE t_user (
  id BIGINT PRIMARY KEY,
  address JSONB  -- {"street": "...", "city": "..."}
);
         ↓
Spring: Hibernate JSONB ✅ (NEW)
@JdbcTypeCode(SqlTypes.JSON)
@Column(columnDefinition = "jsonb")
private Address address;  // POJO (not @Embeddable)
         ✅ ONE TABLE, JSONB OPTIMIZATION
```

### For Real Relationships - Use type + @composition
**Don't use base types for entity relationships:**

```
QSDL:
type Address {  // Use 'type' not 'base'
  street: String
  city: String
}

type User {
  address: Address @composition  // Real entity relationship
}
         ↓
PostgreSQL: FK to separate table
CREATE TABLE t_user (
  address_address_id BIGINT REFERENCES t_address(id)
);
         ↓
Spring: @OneToOne relationship
@OneToOne @JoinColumn(...)
private AddressEntity address;
         ✅ Use this pattern for real relationships
```

## Current Behavior (Problem)

### Base Type Inheritance (`extends BaseType`)
- **Already working correctly** - Fields are flattened at DSL parsing stage
- `Project extends BaseType` results in all BaseType fields being present in Project.java and ProjectEntity
- No code changes needed for this scenario

### Base Type as Field (`field: BaseType`)
- **Currently creates OneToOne entity relationships** with separate tables
- `AbstractPersistentBase` class exists but is currently **unused**
- Example: `metrics: [Metric]` where Metric is a base type
  - Currently generates MetricEntity with its own table
  - Creates OneToOne foreign key relationship
  - Requires separate entity management

### Problems with Current Approach
- Current `@embedded` directive has **wrong semantics** (flattening instead of opaque storage)
- Spring Boot **ignores** the `@embedded` directive completely
- Default creates unnecessary entity tables for simple value objects
- No clear optimization path for complex/sparse data
- Directive name `@embedded` confuses with JPA `@Embeddable`

## Proposed Behavior Rules

### Summary Table

| QSDL Syntax | Current PostgreSQL | Current Spring | New PostgreSQL | New Spring | Change |
|-------------|-------------------|----------------|----------------|------------|---------|
| `field: Base` | FK to table | `@OneToOne` entity | Flatten columns | `@Embedded` | ⚠️ BREAKING |
| `field: Base @opaque` | Flatten columns | Ignores (still `@OneToOne`) | JSONB column | `@JdbcTypeCode` POJO | ⚠️ BREAKING |
| `field: [Base]` | Join table | `@OneToMany` entity | Join table | `@OneToMany` entity | ✅ No change |
| `field: [Base] @opaque` | Join table | `@OneToMany` entity | JSONB array | `@JdbcTypeCode` List | ✅ Enhancement |

**Semantic Meaning:**
- **No directive:** Base type is a **value object** (address, coordinates, etc.)
- **`@opaque`:** Base type is **document data** stored as JSONB (optimization)
- **For entity relationships:** Use `type` with `@composition` or `@aggregation` (NOT base types)

**Migration Impact:**
- **Current default users:** ⚠️ BREAKING - FK → flattened columns
- **Current `@opaque` users:** ⚠️ BREAKING - flattened columns → JSONB
- **Migration path:** Most users need schema changes

### Rule 1: Default Flattening (NEW DEFAULT)
**When:** `field: Base` (no directive)
**Result:** Flatten fields into parent table with column prefix

**Use case:** Simple value objects (Address, Coordinates, etc.)

```qsdl
base Address {
  street: String
  city: String
}

type User {
  address: Address  // No directive = flatten
}
```

**PostgreSQL:**
```sql
CREATE TABLE t_user (
  id BIGINT PRIMARY KEY,
  address_street TEXT,  -- Prefixed with field name
  address_city TEXT
);
```

**Spring Boot (UserEntity.java):**
```java
@Entity
@Table(name = "t_user")
public class UserEntity extends AbstractPersistentObject {
  @Embedded
  @AttributeOverrides({
    @AttributeOverride(name = "street", column = @Column(name = "address_street")),
    @AttributeOverride(name = "city", column = @Column(name = "address_city"))
  })
  private AddressEmbeddable address;
}
```

**Spring Boot (AddressEmbeddable.java):**
```java
@Embeddable
public class AddressEmbeddable {
  private String street;
  private String city;
}
```

### Rule 2: JSONB Storage with @opaque (FIXED)
**When:** `field: Base @opaque`
**Result:** Store as single JSONB column

**Use case:** Complex/sparse data, document storage, schema flexibility

```qsdl
base PerformanceData {
  nav: Float
  navCurrency: String
  totalExpenseRatio: Float
}

type FinancialInstrument {
  performanceData: PerformanceData @opaque  // Store as JSONB
}
```

**PostgreSQL Schema:**
```sql
CREATE TABLE t_financial_instrument (
  id BIGINT PRIMARY KEY,
  performance_data JSONB  -- {"nav": 123.45, "navCurrency": "EUR", ...}
);
```

**Spring Boot (FinancialInstrumentEntity.java):**
```java
@JdbcTypeCode(SqlTypes.JSON)
@Column(columnDefinition = "jsonb")
private PerformanceData performanceData;  // POJO, not @Embeddable
```

**Migration Note:** Current schemas using `@opaque` must migrate to JSONB schema.

### Rule 3: Arrays - Default Join Tables
**When:** `field: [Base]` (array without directive)
**Result:** Create join table (UNCHANGED)

```qsdl
base Variant {
  size: String
  color: String
}

type Product {
  variants: [Variant]  // Default: join table
}
```

**PostgreSQL Schema:**
```sql
CREATE TABLE t_product (id BIGINT PRIMARY KEY);
CREATE TABLE t_variant (id BIGINT PRIMARY KEY, size TEXT, color TEXT);
CREATE TABLE t_product_variants_to_t_variant (
  source_id BIGINT REFERENCES t_product(id),
  target_id BIGINT REFERENCES t_variant(id)
);
```

**Why:** Allows SQL queries/filtering on individual items, referential integrity.

### Rule 4: Arrays as JSONB with @opaque (NEW)
**When:** `field: [Base] @opaque` (array with directive)
**Result:** Store entire array as JSONB column

```qsdl
base Variant {
  size: String
  color: String
}

type Product {
  variants: [Variant] @opaque  // Store as JSON array
}
```

**PostgreSQL Schema:**
```sql
CREATE TABLE t_product (
  id BIGINT PRIMARY KEY,
  variants JSONB  -- [{"size": "M", "color": "red"}, ...]
);
```

**Spring Boot (ProductEntity.java):**
```java
@JdbcTypeCode(SqlTypes.JSON)
@Column(columnDefinition = "jsonb")
private List<Variant> variants;
```

**Use when:** Large arrays (100+ items), no need for SQL querying of individual items

## When to Use Which Approach

### Default (No Directive) - Flatten Columns ✅
**When to use:**
- Simple value objects (2-5 fields)
- Fields are always/mostly populated
- Need database-level validation and constraints
- Want standard SQL indexing
- **Examples:** Address, ContactInfo, AuditMetadata, Coordinates, MoneyAmount

**Benefits:**
- Clean, normalized database schema
- Full SQL query capabilities on nested fields
- Database-level constraints and validation
- Standard B-tree indexes

**Trade-offs:**
- Schema migrations needed if base type structure changes
- Can increase column count (but acceptable for small base types)

### `@opaque` - Opaque Database Storage ⚠️
**Database optimization hint** - Tells generators to treat field as opaque at database layer.

**When to use:**
- Complex nested structures (8+ fields)
- Sparse/optional data (many fields will be NULL most of the time)
- Document-like or semi-structured data
- Structure evolves frequently (want to avoid migrations)
- No need for SQL querying/indexing of nested fields
- **Examples:** DebtInstrumentData (20+ fields), TechnicalIndicators, RawAPIResponse, ConfigurationBlob

**Generated by default:**
- **PostgreSQL:** JSONB column (opaque binary storage)
- **Spring Boot:** `@JdbcTypeCode(SqlTypes.JSON)` with POJO
- **OpenAPI:** Nested object (ignores the hint - API doesn't care about DB storage)

**User can optimize further:**
- Change JSONB to separate table if needed (e.g., for very large objects)
- Change `@JdbcTypeCode` to `@OneToOne` entity relationship
- `@opaque` indicates "database-opaque", not specific implementation

**Benefits:**
- Schema flexibility (add/remove fields without migrations)
- Single column instead of many (by default)
- Good for sparse data
- PostgreSQL JSONB has GIN indexing support

**Trade-offs:**
- No database-level validation on nested fields (with JSONB)
- Querying nested fields requires JSONB operators (more complex)
- GIN indexes only, not B-tree (with JSONB)
- Application-layer validation only (Bean Validation)

**Migration Warning:** Current `@embedded` users must:
1. Rename directive: `@embedded` → `@opaque`
2. Migrate schema: flattened columns → JSONB column

### For Real Entity Relationships - Use `type` + `@composition`
**When you need actual entity relationships (not value objects):**

```qsdl
type Address {  // Use 'type', not 'base'!
  street: String
  city: String
}

type User {
  address: Address @composition
}
```

**When to use:**
- Address is a real entity with its own lifecycle
- Multiple users can share the same address
- Need referential integrity
- Need to query addresses independently

**Don't use base types for this!**

### Arrays: Default (Join Table)
**Use when:**
- Small to medium collections (< 100 items)
- Need SQL queries/filtering on individual items
- Need referential integrity
- Items may be shared across parents
- **Examples:** Product variants, User roles, Tags

### Arrays: `@opaque` (JSONB Array) ✅ NEW
**Use when:**
- Large collections (100+ items)
- Read-heavy, rarely filtered
- Items unique to parent (no sharing)
- Schema flexibility important
- **Examples:** Price history, Log entries, Event sequences, Audit trail

## Examples

### Example 1: Simple Nesting (Flatten)
```qsdl
base AuditInfo {
  createdAt: Datetime
  updatedAt: Datetime
}

type Product {
  name: String
  audit: AuditInfo  // Flatten (only 2 fields)
}
```
Result: `audit_createdAt`, `audit_updatedAt` columns

### Example 2: Complex Document (JSONB)
```qsdl
base DebtInstrumentData {
  totalIssuedNominalAmount: String
  maturityDate: Date
  currency: String
  minimumTradedValue: Float
  fixedRate: Float
  bondSeniority: String
  bondType: String
  indexBenchmark: IndexBenchmark
}

type FinancialInstrument {
  isin: String
  debtInstrumentData: DebtInstrumentData @opaque  // Too many fields
}
```
Result: Single `debtInstrumentData JSONB` column

### Example 3: Nested Arrays (Always JSONB)
```qsdl
base ContactInfo {
  email: String
  phone: String
}

base Address {
  street: String
  contacts: [ContactInfo]  // Nested array
}

type Company {
  locations: [Address]  // Outer array
}
```
Result: `locations JSONB` with full nesting

## Trade-offs

| Aspect | Flattened Columns | JSONB with @opaque |
|--------|-------------------|----------------------|
| Database validation | ✅ Full constraints | ❌ None |
| Indexing | ✅ Standard indexes | ⚠️ GIN indexes only |
| Query performance | ✅ Fast | ⚠️ Slower for deep paths |
| Schema flexibility | ❌ DDL changes needed | ✅ No schema changes |
| Application validation | ✅ Jackson/Bean Validation | ✅ Jackson/Bean Validation |
| Column count | ⚠️ Can explode | ✅ Fixed |

## Implementation Checklist

**Implementation Order:**
1. DSL grammar (rename directive)
2. PostgreSQL generator (fix semantics)
3. Spring Boot generator (implement)
4. Tests
5. Documentation

### Phase 0: DSL Grammar - Rename Directive

#### 0.1 Update Grammar
**File: `src/qsdl/dsl/definition/entity.tx`**
- [x] **Line 113:** Change `is_embedded?='@embedded'` to `is_opaque?='@opaque'`

#### 0.2 Update DSL Model
**File: `src/qsdl/dsl/models/field.py`**
- [x] **Line ~42:** Rename field from `is_embedded: bool = False` to `is_opaque: bool = False`

### Phase 1: PostgreSQL Generator - BREAKING CHANGES ⚠️

#### 1.1 Fix @opaque Semantics and Change Default (CRITICAL)
**File: `src/qsdl/generators/postgres/models/table.py`**
- [x] **Line 108-110:** REVERSE logic - `@opaque` should create JSONB, not flatten
- [x] **Line 57-59:** Change default from FK to flattening for base type fields
- [x] Update `_extract_embedded_columns()` to run for default (not `@opaque`)

**Current (WRONG):**
```python
# Line 57-59: Creates FK by default
if _ref.value._tx_fqn in ["entity.Base", "entity.Object"]:
    column.name += f"_{_ref.value.name.lower()}_id"
    column.type = "BIGINT"

# Line 108-110: @opaque flattens (wrong!)
if isinstance(dsl_field.value, dsl.Base) and dsl_field.is_opaque:
    embedded_prefix = qfilter.snakecase(dsl_field.name).lower() + "_"
    self.columns.extend(_extract_embedded_columns(dsl_field.value, embedded_prefix))
```

**Proposed (CORRECT):**
```python
if isinstance(dsl_field.value, dsl.Base):
    if dsl_field.is_opaque:
        # @opaque = JSONB storage (FIXED!)
        column.type = "JSONB"
        column.name = qfilter.snakecase(dsl_field.name).lower()
        # Don't add to columns yet, handle separately
    else:
        # DEFAULT = Flatten columns (NEW!)
        embedded_prefix = qfilter.snakecase(dsl_field.name).lower() + "_"
        self.columns.extend(_extract_embedded_columns(dsl_field.value, embedded_prefix))
        continue  # Skip normal column addition
```

#### 1.2 Update Table Generation Logic
**File: `src/qsdl/generators/postgres/generate.py`**
- [x] **Line 42-45:** Update `is_relevant_base()` logic
- [x] Base types need tables only if used without `@opaque`
- [x] Skip table generation for bases only used with `@opaque` (JSONB)

#### 1.3 Add JSONB Array Support
**File: `src/qsdl/generators/postgres/models/table.py`**
- [x] **Line 105-106:** Check for `@opaque` on arrays
- [x] If `field.is_array and field.is_opaque`, create JSONB column instead of join table
- [x] Update column type to JSONB for embedded arrays

**New logic:**
```python
if dsl_field.is_array and (dsl_field.is_object or dsl_field.is_base):
    if dsl_field.is_opaque:
        # NEW: JSONB array storage
        new_column.type = "JSONB"
    else:
        # Existing: Join table
        self.join_tables.extend(...)
```

### Phase 2: Spring Boot Generator - Implementation

#### 2.1 Entity Generation - Add @Embedded Support
**File: `src/qsdl/generators/spring/template/_macro/Hibernate.j2`**
- [ ] **Line 59-64:** Update to check `field.is_opaque`
- [ ] Default (no directive): Generate `@Embedded` with `@AttributeOverrides`
- [ ] `@opaque`: Generate `@JdbcTypeCode(SqlTypes.JSON)`

**New logic template:**
```jinja2
{% if field.is_base and not field.is_array %}
  {% if field.is_opaque %}
    {# @opaque = JSONB storage #}
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private {{field.type}} {{field.name}};
  {% else %}
    {# Default = Flatten with @Embedded #}
    @Embedded
    @AttributeOverrides({
      {% for base_field in field.type_fields %}
      @AttributeOverride(
        name = "{{base_field.name}}",
        column = @Column(name = "{{field.name|snake}}_{{base_field.name|snake}}")
      ){{ "," if not loop.last }}
      {% endfor %}
    })
    private {{field.type}}Embeddable {{field.name}};
  {% endif %}
{% endif %}
```

#### 2.2 Create @Embeddable Template
**New File: `src/qsdl/generators/spring/template/src/main/java/domain/Embeddable.j2`**
- [ ] Create template for `@Embeddable` classes
- [ ] Generate fields with JPA annotations
- [ ] Support nested embeddables (recursive base types)
- [ ] Add Lombok annotations (`@Getter`, `@Setter`, `@NoArgsConstructor`)
- [ ] Handle validation annotations (`@NotNull`, `@Size`)

#### 2.3 Generate @Embeddable Classes
**File: `src/qsdl/generators/spring/generate.py`**
- [ ] Add logic to generate `*Embeddable.java` classes for base types
- [ ] Only generate if base is used without `@opaque` (default flattening)
- [ ] Place in same package as entities (or DTOs)

#### 2.4 MapStruct Mapper Updates
**File: `src/qsdl/generators/spring/template/src/main/java/domain/MapStruct.j2`**
- [ ] Add mapping methods for DTO ↔ Embeddable conversions
- [ ] Handle nested embeddables correctly
- [ ] JSONB fields: Direct POJO mapping (already works)

#### 2.5 Array JSONB Support
**File: `src/qsdl/generators/spring/template/_macro/Hibernate.j2`**
- [ ] Check for `field.is_array and field.is_opaque`
- [ ] Generate `@JdbcTypeCode(SqlTypes.JSON)` for embedded arrays
- [ ] Use `List<PojoType>` instead of entity relationships

### Phase 3: Testing

#### 3.1 Update Existing PostgreSQL Tests ⚠️
**File: `tests/functional/generators/test_postgres.py:304`**
- [ ] **CRITICAL:** Update `test_embedded()` - will FAIL with new semantics
- [ ] Rewrite: `@opaque` should generate JSONB, not flattened columns
- [ ] Add `test_default_flattening()` for no-directive behavior

**Example updated test:**
```python
def test_embedded_jsonb(self):  # RENAMED
    """@opaque should create JSONB column, not flatten"""
    test_input = """
        base Address {
            street: String
            city: String
        }
        type User {
            address: Address @opaque
        }
    """
    expected_schema = """
        create table if not exists T_USER (
          id BIGINT ...,
          address JSONB  -- Not flattened columns!
        );
    """

def test_default_flattening(self):  # NEW
    """Default (no directive) should flatten columns"""
    test_input = """
        base Address {
            street: String
            city: String
        }
        type User {
            address: Address
        }
    """
    expected_schema = """
        create table if not exists T_USER (
          id BIGINT ...,
          address_street TEXT,  -- Flattened!
          address_city TEXT
        );
    """
```

#### 3.2 Add New PostgreSQL Tests
**File: `tests/functional/generators/test_postgres.py`**
- [ ] `test_nested_flattening()`: Test nested base types (Address with ContactInfo)
- [ ] `test_array_embedded()`: Test `[Base] @opaque` creates JSONB array
- [ ] `test_mixed_base_usage()`: Same base with @opaque and without

#### 3.3 Add Spring Boot Tests
**File: `tests/functional/generators/test_spring.py`**
- [ ] `test_default_flattening_entity()`: Verify `@Embedded` + `@AttributeOverrides`
- [ ] `test_embedded_jsonb_entity()`: Verify `@JdbcTypeCode(SqlTypes.JSON)`
- [ ] `test_embeddable_class_generation()`: Verify `*Embeddable.java` created
- [ ] `test_mapper_with_embeddables()`: Verify MapStruct compilation
- [ ] `test_array_embedded_entity()`: Verify JSONB array handling

### Phase 4: Documentation & Migration
- [ ] Update `@opaque` directive docs with CORRECT semantics (JSONB, not flatten)
- [ ] Create migration guide with before/after schema examples
- [ ] Update `examples/spring/relation.qsdl` with directive examples
- [ ] Document trade-offs comparison table (flatten vs JSONB)
- [ ] Add warning about schema migrations required
- [ ] Document `AbstractPersistentBase` status (can be removed?)

## Warnings to Generate

When user uses patterns with limitations:

```
⚠️ Warning: Field 'performanceData' uses @opaque with JSONB storage.
   Database-level validation disabled. Only application-layer validation
   (Jackson/Bean Validation) will be enforced.
```

```
⚠️ Warning: Field 'variants' contains array of base types.
   Stored as JSONB - consider using 'type' with @composition for:
   - Large collections (>100 items)
   - Complex querying/filtering needs
   - Database referential integrity requirements
```

## Current Architecture Details

### Field Flattening for Inheritance
When using `extends BaseType`, field flattening happens at the DSL parsing stage:
- **File:** `src/qsdl/dsl/processors/model_parser.py` (lines 111-162)
- **Function:** `get_all_fields_as_list(entity)`
- **Result:** By the time Spring generator runs, `Project` already has all fields from `BaseType`

### Current Base Type Field Handling
When a base type is used as a field (not inheritance):
- **File:** `src/qsdl/generators/spring/template/_macro/Hibernate.j2` (lines 59-64)
- **Current behavior:** Generates `@OneToOne` relationship with foreign key
- **Result:** Separate entity table created for the base type

```jinja2
{% elif not field.is_array and (field.is_object or field.is_base) %}
@OneToOne(cascade = CascadeType.ALL, orphanRemoval = true)
@JoinColumn(name = "{{field.name|snake}}_{{field.type|snake}}_id")
```

### AbstractPersistentBase
- **File:** `src/qsdl/generators/spring/template/src/main/java/model/AbstractPersistentBase.j2`
- **Current status:** Generated but **unused** in current examples
- **Purpose:** Intended for base types that become entities
- **Contains:** `id`, `uid`, `iv` fields with JPA annotations
- **Comment (line 12):** "QSDL utilizes Entities over Embeddable for Base-Classes because it's compatible for most use cases."

### What Needs to Change
1. **Keep:** Field flattening for `extends BaseType` (inheritance)
2. **Change:** Base type fields should use `@Embedded` by default (not `@OneToOne`)
3. **Add:** Support for `@opaque` directive to use JSONB instead
4. **Add:** New `@Embeddable` class generation for base types
5. **Deprecate (optional):** `AbstractPersistentBase` if no longer needed

## Migration Path

### For Existing Schemas
**Breaking Change:** Yes, this changes the default behavior for base type fields

**Option 1: Introduce New Directive (Safer)**
- Keep current `@OneToOne` as default
- Introduce `@flatten` directive to opt-in to `@Embedded` behavior
- Introduce `@opaque` directive for JSONB storage
- Users must explicitly choose the new behavior

**Option 2: Change Default (More disruptive)**
- Change default to `@Embedded` (flattening)
- Introduce `@entity` directive to keep old `@OneToOne` behavior
- Update existing examples to use `@entity` if needed
- Add migration notes in CHANGELOG

**Recommendation:** Option 1 for safety, with clear documentation about the new preferred approach.

### Backward Compatibility Strategy
1. **Phase 1:** Implement `@flatten` and `@opaque` as opt-in features
2. **Phase 2:** Add deprecation warnings for unmarked base type fields
3. **Phase 3:** Change default behavior in next major version (v2.0.0)
4. Document migration path with before/after examples

### Future Considerations
- Custom PostgreSQL composite types for base type arrays (advanced)
- Generate JSONB check constraints for validation (if feasible)
- Performance optimization hints in documentation
- Consider `@Embeddable` vs JSONB performance benchmarks

## Open Questions

### 1. Directive Naming
- Should we use `@opaque` for JSONB or `@jsonb` for clarity?
- Should flattening directive be `@flatten`, `@embeddable`, or `@inline`?
- Current proposal: `@opaque` for JSONB (matches existing grammar)

### 2. Migration Strategy
- **Option A (Safe):** Keep `@OneToOne` as default, add `@flatten` and `@opaque` as opt-in
- **Option B (Breaking):** Change default to `@Embedded`, add `@entity` to preserve old behavior
- **Recommendation:** Depends on project maturity and number of existing users

### 3. Nested Base Types
- Should deeply nested base types (3+ levels) auto-trigger `@opaque` with a warning?
- Example: `base Address { contact: ContactInfo }` where `ContactInfo` is also a base
- How many nesting levels before we recommend JSONB?

### 4. Array Handling
- Should we allow `@opaque` on arrays or is it implicit?
- Current proposal: Always JSONB for arrays, `@opaque` is redundant
- Should we warn if user adds `@opaque` to an array field?

### 5. DTO Representation
- For flattened base types, should DTOs also flatten or keep nested structure?
- Current proposal: Keep nested structure in DTOs (better API ergonomics)
- MapStruct handles the translation between nested DTO and flat entity

### 6. Validation
- How should `@Valid` cascade work with `@Embedded` vs JSONB?
- Should we generate different validation annotations based on storage strategy?
- Bean Validation works for both, but constraints in JSONB are not enforced at DB level

### 7. AbstractPersistentBase Future
- Keep it for backward compatibility or remove entirely?
- If keeping, when should it be used vs `@Embeddable`?
- Document the use case if retained

## Real-World Examples

### Example 1: Financial Instruments
- **Scenario:** 150+ potential fields across different instrument types
- **Problem:** Not all instruments have all fields (sparse data)
- **Solution:** Use `@opaque` for instrument-specific data blocks
- **File:** Custom schema (not in examples/)

### Example 2: Audit Information
- **Scenario:** `createdAt`, `updatedAt`, `createdBy`, `updatedBy` (4 fields)
- **Current:** Flattened via `extends BaseType`
- **Proposed:** Could use `@Embedded` if used as field instead of inheritance
- **File:** `examples/spring/relation.qsdl` (lines 22-30)

### Example 3: Product Variants
- **Scenario:** Array of variants with size, color, price
- **Current:** Would create `VariantEntity` with `@OneToOne`
- **Proposed:** Use JSONB for array storage
- **File:** `examples/openapi/input.qsdl` (lines 15-23)

## References

### Code Files
- **DSL Parser:** `src/qsdl/dsl/processors/model_parser.py` (field flattening logic)
- **Spring Generator:** `src/qsdl/generators/spring/generate.py` (entity generation)
- **Entity Template:** `src/qsdl/generators/spring/template/src/main/java/domain/Entity.j2`
- **Hibernate Macros:** `src/qsdl/generators/spring/template/_macro/Hibernate.j2` (lines 59-64)
- **AbstractPersistentBase:** `src/qsdl/generators/spring/template/src/main/java/model/AbstractPersistentBase.j2`

### Test Files
- **Postgres Test:** `tests/functional/generators/test_postgres.py:304` (test_embedded - needs update)
- **Spring Test:** `tests/functional/generators/test_spring.py` (needs new tests)

### Example Schemas
- **Inheritance Example:** `examples/spring/relation.qsdl` (BaseType inheritance)
- **Nested Base Types:** `examples/openapi/input.qsdl` (Metric with nested Rating)

### Related Issues
- Comment in AbstractPersistentBase.j2: "QSDL utilizes Entities over Embeddable... should be optimized post-generation"
- This change request IS that optimization

---

**Decisions Made:**
1. ✅ Directive name: `@opaque` (database optimization hint)
2. ✅ Default behavior: Flatten columns (value object semantics)
3. ✅ `@opaque` behavior: JSONB storage (opaque to database, user can optimize)
4. ✅ No new directives: Keep it simple

**Implementation Required:**
1. Rename: `@embedded` → `@opaque` in DSL grammar
2. Fix PostgreSQL: Reverse semantics + change default
3. Implement Spring Boot: `@Embedded` default + `@JdbcTypeCode` for opaque
4. Update tests: Fix test_embedded, add test_default_flattening
5. Migration guide: Document schema changes required


## Appendix: Why `@opaque`?

### The Directive Name Decision

We chose `@opaque` over `@embedded`, `@json`, `@jsonb`, and other alternatives for these reasons:

1. **Multi-Generator Perspective**
   - QSDL generates code for multiple targets: PostgreSQL, Spring Boot, OpenAPI
   - `@opaque` is a **database-level hint** that OpenAPI can safely ignore
   - The API spec still shows nested objects regardless of database storage

2. **Implementation Flexibility**
   - `@opaque` means "treat as opaque at database layer"
   - **Default generation:** PostgreSQL JSONB + Spring `@JdbcTypeCode`
   - **User optimization:** Can manually change to separate table if needed
   - Name doesn't lock us into specific implementation (JSONB, separate table, etc.)

3. **No Confusion with JPA**
   - JPA `@Embeddable` is used for **default flattening** behavior
   - Hibernate `@Embedded` annotation is used for flattened fields
   - `@opaque` clearly distinct from JPA terminology

4. **Semantic Clarity**
   - "Opaque" = database cannot see/index internal structure
   - Opposite of "transparent" relational decomposition (flattening)
   - Clear that it's an optimization/storage concern, not domain modeling

5. **User Mental Model**
   ```qsdl
   base Address {
     street: String
     city: String
   }
   
   type User {
     address: Address        // Transparent: DB sees street/city columns
     metadata: Config @opaque // Opaque: DB sees single JSONB blob
   }
   ```

### Comparison with Alternatives

| Name | Pros | Cons | Verdict |
|------|------|------|---------|
| `@json` | Clear, universal | Implies JSON (what if user changes to table?) | ❌ Too specific |
| `@jsonb` | Matches PostgreSQL | PostgreSQL-specific, not portable | ❌ Not database-agnostic |
| `@embedded` | Existing directive | Conflicts with JPA `@Embeddable` | ❌ Confusing |
| `@document` | Semantic | Less obvious it means opaque storage | ⚠️ Okay but less clear |
| `@opaque` | Database-agnostic, no confusion, flexible | New terminology | ✅ **BEST** |

### Real-World Usage

```qsdl
base SimpleAddress {
  street: String
  city: String
}

base ComplexInstrumentData {
  // 25+ fields, sparse, evolves frequently
  totalIssuedNominalAmount: String
  maturityDate: Date
  currency: String
  minimumTradedValue: Float
  fixedRate: Float
  // ... 20 more fields
}

type Bond {
  isin: String
  issueDate: Date
  
  // Simple value object → flatten (default)
  billingAddress: SimpleAddress
  
  // Complex sparse data → opaque storage
  debtInstrumentData: ComplexInstrumentData @opaque
}
```

**Generated PostgreSQL:**
```sql
CREATE TABLE t_bond (
  id BIGINT PRIMARY KEY,
  isin TEXT,
  issue_date DATE,
  
  -- Flattened (transparent to DB)
  billing_address_street TEXT,
  billing_address_city TEXT,
  
  -- Opaque (DB doesn't see internal structure)
  debt_instrument_data JSONB
);
```

**User can later optimize:**
If `debt_instrument_data` grows too large, user can manually change generated code:
- Move JSONB to separate table with FK
- `@opaque` still makes semantic sense: "opaque to main table structure"

---

**Final Note:** `@opaque` is a **hint for database generators**, not a strict rule. It guides default code generation while allowing users to optimize post-generation based on their specific needs.
