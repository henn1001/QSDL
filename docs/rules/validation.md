# Validation rules

This page consolidates **validation and structural rules** described in the repository root
[`README.md`](../../README.md).

> Scope note
>
> This content is sourced from `README.md` only. Implementation details and additional constraints may
> exist in DSL processors.

## Schema header ordering

The schema header fields (`title`, `version`, `description`, `servers`) are optional, but the README
states that their **order is important** when provided.

## Enum constraints

- Enums must contain at least one value.

## Api constraints

The root README lists these constraints for `Api`:

- An Api must contain at least one Operation.
- An Api must only specify **two methods per path** (with and without ID). This constraint overlaps
  with all used paths including those produced by `Object` CRUD generation.
- Api names must be globally unique (also overlapping with auto-generated CRUD operations for Objects).

## Relationship constraints

For relationship directives:

- `@composition` may be used on an Object field to create a parent-child relation.
  - The field value must be a **list of Object**.
- `@aggregation` may be used on an Object field to create an independent relation.
  - The field value must be a **list of Object**.

## Inheritance / overriding constraints

- `@override` needs to be used on a field that redefines an inherited field.
