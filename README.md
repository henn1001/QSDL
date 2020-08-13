# QSDL

A Schema-Definition-Language Generator inspired by GraphQl.

## Overview

The QSDL Generator allows a domain model based approach to generate OpenAPI and GraphQL specifications. The Language is mainly inspired by GraphQL with minor modifications to accommodate OpenAPI and sensible QoL features.

Internally QSDL leverages mainly [textX](https://github.com/textX/textX) for describing the meta-language and [Jinja2](https://github.com/pallets/jinja) as template generator.

Currently the following generators are available:

* OpenAPI

* GraphQL

* PlantUML

## Language


## ToDo:
* remove input
* refactor query and mutation to operation
* fix nested inputs for GraphQL
* write readme
* write more openapi tests
* write graphql tests

## Requirements


Input values can be Scalar, Enum, or Input.
Output values can be Scalar, Object, Base, Union, or Enum.

Field
    name (name: Input) : output



### Object

* `Object` names should use `PascalCase`

* `Object` can be used as `Field` value.

* `Object` can be used as `Argument` value.

### Field

* `Field` names should use `camelCase`. 

* `Field` values can be either a `Scalar`, `Enum`, `Base` or  `Object`.

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

* A description can be added after version, for `Enum`, `Base`, `Query`, `Mutation`, `Object` or `Field`.

* A description can be `SingleLine` or `MultiLine`.

* A `SingleLine` description should be presented between quotation marks and at least one character in between e.g. `"X"`.

* A `MultiLine` description should be presented between three quotation marks and at least one character in between e.g. `""\"X\"""`.

## Semantic checks
* If composition or aggregation is used, the object needs to have a ID field

## Test cases

| ID  | Description | Covered |
| --- | ----------- | ------- |
| 01  |             |         |
| 02  |             |         |