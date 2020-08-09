# QSDL

## ToDo:

* fix nested inputs for GraphQL
* write readme
* write more openapi tests
* write graphql tests

## Requirements


Input values can be Scalar, Enum, or Input.
Output values can be Scalar, Object, Interface, Union, or Enum.

Field
    name (name: Input) : output



### Scalar

* There are 7 build in `Scalar` types.

  * `Int`: A signed 32‐bit integer

  * `Float`:

  * `String`:

  * `Boolean`:

  * `ID`:

  * `Date`:

  * `Object`:


### Enum

* `Enum` names should use `PascalCase`

* `Enum` values should use `ALL_CAPS`, because they are similar to constants.

* `Enum` should at least contain one value.

* `Enum` can be used for `Field` assignment.

### Interface

* `Interface` names should use `PascalCase`

* `Interface` can be used for `Field` assignment together with a `@nested` `Directive`.

* `Interface` can be used as a superType by other `Interface`s or by `Object`s.

### Object

* `Object` names should use `PascalCase`

### Field

* `Field` names should use `camelCase`. 

* `Field` values can be either a `Scalar`, `Enum`, `Interface` or  `Object`.

* `Field` values should accept array assignments via brackets e.g. `[String]`

* `Field` values can be set mandatory by appending a exclamation mark e.g. `String!`. Additionally this applies to arrays to prevent null values e.g. `[String!]`

### Directive

* There are 3 build in `Directive`s.

    * `@query`:

    * `@nested`:

    * `@readOnly`:

    * `@writeOnly`:

    * `@composition`:

    * `@aggregation`:

### Description

* A description can be added for either a `Object` or `Field`.

* A description can be `SingleLine` or `MultiLine`.

* A `SingleLine` description should be presented between quotation marks and at least one character in between e.g. `"X"`.

* A `MultiLine` description should be presented between three quotation marks and at least one character in between e.g. `"""X"""`.

## Semantic checks
* If composition or aggregation is used, the object needs to have a ID field

## Test cases

| ID  | Description | Covered |
| --- | ----------- | ------- |
| 01  |             |         |
| 02  |             |         |