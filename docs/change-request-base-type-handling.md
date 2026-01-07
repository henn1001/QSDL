# Change Request: Base Type Handling in PostgreSQL Generator

## Status
**Proposed** - Implementation pending

## Summary
Clarify and standardize how `base` types are represented in PostgreSQL database schema, introducing the `@embedded` directive to control JSONB vs column flattening behavior.

## Current Behavior (Problem)

- `@embedded` directive exists but purpose is unclear
- Inconsistent handling of base types across different scenarios
- No clear strategy for complex nested structures
- Risk of column explosion with deeply nested base types

## Proposed Behavior

### Rule 1: Default Flattening (Single Base Type)
**When:** Single base type field WITHOUT `@embedded`
**Result:** Flatten fields into parent table with prefix

```qsdl
base Address {
  street: String
  city: String
}

type User {
  address: Address  // No @embedded
}
```

**PostgreSQL:**
```sql
create table T_USER (
  id BIGINT primary key,
  address_street TEXT,
  address_city TEXT
);
```

### Rule 2: JSONB Storage (Single Base Type with @embedded)
**When:** Single base type field WITH `@embedded`
**Result:** Store entire object as JSONB column

```qsdl
base PerformanceData {
  nav: Float
  navCurrency: String
  totalExpenseRatio: Float
}

type FinancialInstrument {
  performanceData: PerformanceData @embedded
}
```

**PostgreSQL:**
```sql
create table T_FINANCIAL_INSTRUMENT (
  id BIGINT primary key,
  performanceData JSONB  -- {nav: 123.45, navCurrency: "EUR", ...}
);
```

### Rule 3: Arrays Always Use JSONB
**When:** Array of base types (regardless of `@embedded`)
**Result:** Always JSONB (no flattening possible)

```qsdl
base Variant {
  size: String
  color: String
}

type Product {
  variants: [Variant]  // @embedded is implicit for arrays
}
```

**PostgreSQL:**
```sql
create table T_PRODUCT (
  id BIGINT primary key,
  variants JSONB  -- [{size: "M", color: "red"}, ...]
);
```

## When to Use @embedded

### ✅ Use @embedded When:
- Field contains 5+ nested fields (avoid column explosion)
- Data is document-like or semi-structured
- Fields are optional/sparse (only populated for certain subtypes)
- No need for indexing or querying individual nested fields
- Structure may evolve frequently

### ❌ Don't Use @embedded When:
- Only 2-3 fields in base type (flattening is cleaner)
- Need to query/index individual nested fields
- Want database-level constraints on nested fields
- Fields are always populated

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
  debtInstrumentData: DebtInstrumentData @embedded  // Too many fields
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

| Aspect | Flattened Columns | JSONB with @embedded |
|--------|-------------------|----------------------|
| Database validation | ✅ Full constraints | ❌ None |
| Indexing | ✅ Standard indexes | ⚠️ GIN indexes only |
| Query performance | ✅ Fast | ⚠️ Slower for deep paths |
| Schema flexibility | ❌ DDL changes needed | ✅ No schema changes |
| Application validation | ✅ Jackson/Bean Validation | ✅ Jackson/Bean Validation |
| Column count | ⚠️ Can explode | ✅ Fixed |

## Implementation Checklist

### PostgreSQL Generator
- [ ] Update field generation logic to check for `@embedded`
- [ ] Implement flattening as default for single base types
- [ ] Implement JSONB storage when `@embedded` present
- [ ] Handle nested base types recursively
- [ ] Always use JSONB for base type arrays

### Spring Boot Generator
- [ ] Generate Java Records for base types (not `@Embeddable`)
- [ ] Use `@Column(columnDefinition = "jsonb")` for `@embedded` fields
- [ ] Add `@Valid` annotations for nested validation
- [ ] Map QSDL `!` to `@NotNull` in Records
- [ ] Map QSDL `@minSize/@maxSize` to `@Size` in Records

### Documentation
- [ ] Update directive reference for `@embedded`
- [ ] Add examples of flattening vs JSONB
- [ ] Document validation differences
- [ ] Add guidelines for when to use `@embedded`

### Testing
- [ ] Test default flattening behavior
- [ ] Test `@embedded` JSONB storage
- [ ] Test nested base types (multiple levels)
- [ ] Test arrays of base types
- [ ] Test mixed scenarios
- [ ] Test validation on JSONB fields

## Warnings to Generate

When user uses patterns with limitations:

```
⚠️ Warning: Field 'performanceData' uses @embedded with JSONB storage.
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

## Migration Path

### For Existing Schemas
1. Default remains flattening (backward compatible)
2. Users can opt-in to JSONB with `@embedded`
3. No breaking changes to existing generated code

### Future Consideration
- Custom PostgreSQL composite types for base type arrays (advanced)
- Generate JSONB check constraints for validation (if feasible)
- Performance optimization hints in documentation

## Open Questions

1. Should deeply nested base types (3+ levels) auto-trigger `@embedded` with a warning?
2. Should we allow `@embedded` on arrays or make it implicit/redundant?
3. Should we generate Jackson mixins for additional JSONB control?

## References

- Test file: `tests/functional/generators/test_postgres.py:304` (test_embedded)
- Real-world example: Financial instrument API with 150+ potential columns
- Discussion: Base types are field groupings, not domain entities

---

**Decision Required:** Approve this change before implementation begins.
