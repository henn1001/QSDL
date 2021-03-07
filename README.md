# QSDL

A Schema-Definition-Language Generator inspired by GraphQL.

## Overview

The QSDL Generator allows a domain model based approach to generate OpenAPI and GraphQL specifications. The Language is inspired by GraphQL with minor modifications to accommodate OpenAPI and sensible QoL features.

The idea is offer a minimal approach to a API definition in order to define CRUD access to a domain model graph where domain objects have parent-child like dependencies. A simple Object definition in QSDL will generate the GET ALL / POST / GET / PUT / PATCH / DELETE Operations in OpenAPI and GraphQL.

![gif](https://s8.gifyu.com/images/ezgif.com-video-to-gif590dea37aa704f90.gif)

Internally QSDL leverages [textX](https://github.com/textX/textX) for describing the meta-language and [Jinja2](https://github.com/pallets/jinja) as template generator.

Currently the following generators are available:

* OpenAPI
* GraphQL
* PlantUML

### Requirements

The QSDL package works on Python versions:

* 3.6.x and greater
* 3.7.x and greater
* 3.8.x and greater

### Installation

The safest way to install QSDL is to use [pip](https://pip.pypa.io/en/stable/) in a `virtualenv`:

    $ pip install qsdl --extra-index-url https://@gitlab.com/api/v4/projects/20759213/packages/pypi/simple

or, if you are not installing in a `virtualenv`, to install globally:

    $ sudo pip install qsdl --extra-index-url https://@gitlab.com/api/v4/projects/20759213/packages/pypi/simple

or for your user:

    $ pip install --user qsdl --extra-index-url https://@gitlab.com/api/v4/projects/20759213/packages/pypi/simple

If you have the QSDL package installed and want to upgrade to the latest version you can run:

    $ pip install --upgrade qsdl --extra-index-url https://@gitlab.com/api/v4/projects/20759213/packages/pypi/simple

This will install the QSDL package as well as all dependencies.

### Usage

The QSDL CLI command has the following structure:

    $ qsdl [OPTIONS] INPUT_PATH

For example, to run the generator on a minimal schema definition file:

    $ echo "type Project { id: ID name: String }" > project.tx
    $ qsdl project.tx
    $ tree srcgen/
      srcgen/
      ├── openapi.yaml
      ├── plantuml.bases.png
      ├── plantuml.enums.png
      ├── plantuml.md
      ├── plantuml.overview.png
      └── schema.graphql

      0 directories, 6 files

To view help documentation, use the following:

    $ qsdl --help

To get the version of the QSDL CLI:

    $ qsdl --version

## Examples

Examples can be found in `util/examples/`.

* [Example API](util/examples/input.tx)

# Language

The language definition can be found [here](qsdl/dsl/definition/entity.tx) and as PlantUML representation [here](qsdl/dsl/definition/entity.md). Let's try to go over it from the top.

## Schema

$`          Schema:                                                         `$\
$`~~~~          title=STRING?                                               `$\
$`~~~~          version=STRING?                                             `$\
$`~~~~          description=Description?                                    `$\
$`~~~~          servers+=STRING?                                            `$\
$`~~~~          types*=Type                                                 `$

A schema file starts with four optional fields. You should already be familiar with them if you know OpenAPI.

> Note: The order is important. 

Example:

    title: "Test API"
    version: "1.0"
    description: "A description"

    servers: ["https://localhost:8080/api/v1", "https://localhost:8082/api/v1"]

Descriptions can also be multiline:

    description: """
    A
    multi
    line
    description.
    """

The servers field is a List and needs to be put in between brackets.

## Type

$`          Type:                                                           `$\
$`~~~~          Scalar | Enum | Base | Object | Operation                   `$

We can then go ahead and define multiple types. These are the five main types of the language.

## Scalar

$`          Scalar:                                                         `$\
$`~~~~          name=ID                                                     `$

Scalar types represent the primitive types which can be used as assignments.

Example:

    scalar Double;
    scalar File;
    scalar Image;


There are already several builtin types available.

- `ID`
- `Int`
- `Long`
- `Float`
- `Double`
- `String`
- `Boolean`
- `Date`
- `Object`
- `Void`

> Note: For the OpenAPI generator there is no support for other scalar types than the pre-defined.

## Enum

$`          Enum:                                                           `$\
$`~~~~          description=Description?                                    `$\
$`~~~~          name=ID                                                     `$\
$`~~~~          values+=Value                                               `$

Enum types are similar to Scalars but they represent a set of possible String values.

Rules:

01. `Enum` names must use `PascalCase`.

02. `Enum` values must use `ALL_CAPS`.

03. `Enum` must at least contain one value.

Example:

    enum Status {
        OPEN
        TO_DO
        CLOSED
    }

## Base

$`          Base:                                                           `$\
$`~~~~          description=Description?                                    `$\
$`~~~~          name=ID                                                     `$\
$`~~~~          superType=Base?                                             `$\
$`~~~~          directives*=Directive                                       `$\
$`~~~~          fields+=Field                                               `$

Base types can be seen as a combination of OpenAPIs Data Models and Interfaces/Inputs from GraphQL. They do not trigger any special actions like Objects do but they can be used throughout the schema to describe inputs, responses or as super types to define common field values.

Base Rules:

1.  `Base` names must use `PascalCase`.

2.  `Base` must at least contain one `Field`.

3.  `Base` may inherit `Field`s from a `Base`.

4.  `Base` name must be unique between `Object`, `Base` and `Scalar`.

Field Rules:

1.  `Field` of `Base` may be a `Scalar` value with one one of the following:
    * `ID`
    * `Int`
    * `Long`
    * `Float`
    * `Double`
    * `String`
    * `Boolean`
    * `Date`
    * `Object`

2.  `Field` of `Base` value may be a `Enum`.

3.  `Field` of `Base` value may be a `Base` when marked as `@nested`.

4.  `Field` of `Base` value may be a `Object`.

5.  `Field` of `Base` value may be a list when enclosed with brackets.

6.  `Field` of `Base` value may not be a list for `Scalar` `ID`.

7.  `Field` of `Base` value and list value may be marked as mandatory.

8.  `Field` of `Base` values may only have one `ID`. This includes inherited values.

Example:

    "The very basic type all Domain Objects should have."
    base BaseType {
        "The Object identifier."
        id: ID! @readOnly

        "The Object name."
        name: String! @query

        "Optional description"
        description: String

        "Accepts any valid json object."
        meta_inf: Object
    }

    "Maybe some Domain Objects need date information."
    base BaseTypeDated implements BaseType {
        creation_date: Date @readOnly
        last_update_date: Date @readOnly
    }

## Object

$`          Object:                                                         `$\
$`~~~~          description=Description?                                    `$\
$`~~~~          name=ID                                                     `$\
$`~~~~          superType=Base?                                             `$\
$`~~~~          directives*=Directive                                       `$\
$`~~~~          fields+=Field                                               `$\
$`~~~~          operation=Operation?                                        `$

Object types represent the core of our schema. A Object definition will result into the generation of several CRUD path definitions for OpenAPI and Query/Mutations for GraphQL. The auto-generated CRUD operations can be overwritten by providing a Operation type.

Object Rules:

1.  `Object` names must use `PascalCase`.

2.  `Object` must at least contain one `Field`.

3.  `Object` can inherit `Field`s from a `Base`.

4.  `Object` name must be unique between `Object`, `Base` and `Scalar`.

Field Rules:

1.  `Field` of `Object` may be a `Scalar` value with one one of the following:
    * `ID`
    * `Int`
    * `Long`
    * `Float`
    * `Double`
    * `String`
    * `Boolean`
    * `Date`
    * `Object`

2.  `Field` of `Object` value may be a `Enum`.

3.  `Field` of `Object` value may be a `Base` when marked as `@nested`.

4.  `Field` of `Object` value may be a `Object`.

5.  `Field` of `Object` value may be a list when enclosed with brackets.

6.  `Field` of `Object` value may not be a list for `Scalar` `ID`.

7.  `Field` of `Object` value and list value may be marked as mandatory.

8.  `Field` of `Object` values may only have one `ID`. This includes inherited values.

Example:

    base BaseType {
        id: ID! @readOnly
        name: String! @query
        description: String
        creation_by: String @readOnly
        creation_date: Date @readOnly
        last_update_by: String @readOnly
        last_update_date: Date @readOnly
        meta_inf: Object
    }

    type Project implements BaseType {
        archive: Boolean @writeOnly
        archived: Boolean @readOnly
    }

    type QueryBuilder{
        request: String! @writeOnly
        response: Object @readOnly

         extend Operation {
            submitQuery(body: QueryMachine): QueryMachine @path(value:"query/submit") @method(value: POST)
        }
    }

## Operation

$`          Operation:                                                      `$\
$`~~~~          description=Description?                                    `$\
$`~~~~          name=ID                                                     `$\
$`~~~~          directives*=Directive                                       `$\
$`~~~~          fields+=Field                                               `$

Operation types can be used to create API Endpoints and Query/Mutation.

Operation Rules:

1.  `Operation` must at least contain one `Field`.

2.  `Operation` may be used multiple times for a schema to define custom operations.

3.  `Operation` may be used once inside a `Object` to overwrite the default CRUD operations.

4.  `Operation` must only specify two methods per path (with and without ID). This overlaps with all used paths including `Object`s.

5.  `Operation` names must be globally unique. This overlaps with auto generated CRUD operations for `Object`s.

Field Rules:

1.  `Field` of `Operation` may be a `Scalar` value with one one of the following:
    * `ID`
    * `Int`
    * `Long`
    * `Float`
    * `Double`
    * `String`
    * `Boolean`
    * `Date`
    * `Object`
    * `Void`

2.  `Field` of `Operation` value may be a `Enum`.

3.  `Field` of `Operation` value may be a `Base`.

4.  `Field` of `Operation` value may be a `Object`.

5.  `Field` of `Operation` value may be a list when enclosed with brackets.

6.  `Field` of `Operation` value and list value may be marked as mandatory.

Example:

    extend Operation {
        submitObject(body: Object): Void @path(value:"(object)") @method(value: POST)
    }

## Directive

There are certain builtin directives that can be used to modify the generation behavior.

1.  `Directive` `@query` may be use on any `Base` or `Object` `Field` to create a query parameter for the get all method.

2.  `Directive` `@nested` may be use on any `Base` or `Object` `Field` when the `Field` value is a `Object`. This creates a nested JSON `Object`.

3.  `Directive` `@nested` must be use on any `Base` or `Object` `Field` when the `Field` value is a `Base`. This creates a nested JSON `Object`.

4.  `Directive` `@readOnly` may be use on any `Base` or `Object` `Field` to mark a `Field` as read only.

5.  `Directive` `@writeOnly` may be use on any `Base` or `Object` `Field` to mark a `Field` as write only.

6.  `Directive` `@composition` may be used on a `Object` `Field` to create a parent-child relation. The `Field` value must be a `Object`.

7.  `Directive` `@aggregation` may be used on a `Object` `Field` to create a independent relation. The `Field` value must be a `Object`.

8.  `Directive` `@path` must be used on any `Operation` `Field` which are not part of a `Object`. This specifies the API Path.

9.  `Directive` `@path` may be used on any `Operation` `Field` which is part of a `Object`. This specifies the API Path.

10. `Directive` `@method` may be used on any `Operation` `Field` to specify the REST Method. Valid values are GET | POST | PUT | PATCH | DELETE.

11. `Directive` `@namespace` may be used on any `Base`, `Operation` or `Object` for grouping.
