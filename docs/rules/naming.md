# Naming & conventions

This page consolidates **naming and uniqueness constraints** described in the repository root
[`README.md`](../../README.md).

> Scope note
>
> This content is sourced from `README.md` only.

## Type naming rules

### Enum

- Enum names must use `PascalCase`.
- Enum values must use `ALL_CAPS`.

### Base

- Base names must use `PascalCase`.

### Object

- Object names must use `PascalCase`.

## Uniqueness rules

From the root README:

- Base names must be unique across `Object`, `Base`, and `Scalar`.
- Object names must be unique across `Object`, `Base`, and `Scalar`.
- Api names must be globally unique (and must not conflict with auto-generated CRUD operations for Objects).
