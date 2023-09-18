# QSDL

A Schema-Definition-Language Generator inspired by GraphQL.

## Overview

The QSDL Generator allows a domain model based approach to generate OpenAPI and GraphQL specifications. The Language is inspired by GraphQL with minor modifications to accommodate OpenAPI and sensible QoL features.

The idea is offer a minimal approach to a API definition in order to define CRUD access to a domain model graph where domain objects have parent-child like dependencies. A simple Object definition in QSDL will generate the GET ALL / POST / GET / PUT / PATCH / DELETE Operations.

![gif](https://s8.gifyu.com/images/ezgif.com-video-to-gif590dea37aa704f90.gif)

Internally QSDL leverages [textX](https://github.com/textX/textX) for describing the meta-language and [Jinja2](https://github.com/pallets/jinja) as template generator.

Currently the following generators are available:

* OpenAPI
* SpringBoot
* PlantUML

### Requirements

The QSDL package currently supports the Python version:

* 3.11.x

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

    $ echo "type Project { name: String }" > project.qsdl
    $ qsdl project.qsdl -g openapi
    $ tree srcgen/
      srcgen/
      └── openapi.yaml

      0 directories, 6 files

To view help documentation, use the following:

    $ qsdl --help

```
Usage: qsdl [OPTIONS] INPUT_PATH

Runs the QSDL generator with the provided schema definition file.

Args:
    input_path (str):   The path to the schema definition file.

Returns:
    int:                0 on success, 1 on failure

Options:
-g, --generator [openapi|graphql|plantuml|spring|void]
                                The requested generator.
-c, --config_path PATH          Path to a config json file.
-o, --output_path PATH          Path to a output folder. Default: 'srcgren/'
-pv, --print_version            Prints a .qversion file to the output
                                folder.
--version                       Show the version and exit.
--help                          Show this message and exit.
```

## Examples

Examples can be found in `util/examples/`.

* [Example API](util/examples/input.qsdl)

# Language

The language definition can be found [here](qsdl/dsl/definition/entity.qsdl) and as PlantUML representation [here](qsdl/dsl/definition/entity.md). Let's try to go over it from the top.

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
$`~~~~          Scalar | Enum | Base | Object | Api                   `$

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

- `Int`
- `Long`
- `Float`
- `Double`
- `String`
- `Boolean`
- `Date`
- `Object`
- `Void`

> Note: In order to correctly interpret new scalars for a specific generator, directives can be used to provide a conversion map.

Example:
```
scalar UUID @openapi("string, format: uuid, pattern: ^.*$") @spring("UUID")
```

For openapi, three values can be provided which translate to "type", "format" and "pattern".

> Note: Parsing here is a bit tricky and done by splitting via ', '. The whitespace after the comma is especially important to not split commas within the provided regex.

```
description:
    type: string
    format: uuid

// decimal with max precision of 4
description:
    type: string
    pattern: ^[0-9]*(?:\.[0-9]{0,4})?$
```

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
$`~~~~          supertype=Base?                                             `$\
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
    * `Int`
    * `Long`
    * `Float`
    * `Double`
    * `String`
    * `Boolean`
    * `Date`
    * `Object`

2.  `Field` of `Base` value may be a `Enum`.

3.  `Field` of `Base` value may be a `Base`.

4.  `Field` of `Base` value may be a `Object`.

5.  `Field` of `Base` value may be a list when enclosed with brackets.

6.  `Field` of `Base` value may be marked as required.

Example:

    "The very basic type all Domain Objects should have."
    base BaseType {
        "The Object name."
        name: String! @query

        "Optional description"
        description: String

        "Accepts any valid json object."
        meta_inf: Object
    }

    "Maybe some Domain Objects need date information."
    base BaseTypeDated extends BaseType {
        creation_date: Date @readOnly
        last_update_date: Date @readOnly
    }

## Object

$`          Object:                                                         `$\
$`~~~~          description=Description?                                    `$\
$`~~~~          name=ID                                                     `$\
$`~~~~          supertype=Base?                                             `$\
$`~~~~          directives*=Directive                                       `$\
$`~~~~          fields+=Field                                               `$\
$`~~~~          api=Api?                                                    `$

Object types represent the core of our schema. A Object definition will result into the generation of several CRUD path definitions for OpenAPI and Query/Mutations for GraphQL. The auto-generated CRUD operations can be overwritten by providing a Api type.

Object Rules:

1.  `Object` names must use `PascalCase`.

2.  `Object` can inherit `Field`s from a `Base`.

3.  `Object` name must be unique between `Object`, `Base` and `Scalar`.

Field Rules:

1.  `Field` of `Object` may be a `Scalar` value with one one of the following:
    * `Int`
    * `Long`
    * `Float`
    * `Double`
    * `String`
    * `Boolean`
    * `Date`
    * `Object`

2.  `Field` of `Object` value may be a `Enum`.

3.  `Field` of `Object` value may be a `Base`.

4.  `Field` of `Object` value may be a `Object`.

5.  `Field` of `Object` value may be a list when enclosed with brackets.

6.  `Field` of `Object` value may be marked as required.

Example:

    base BaseType {
        name: String! @query
        description: String
        creation_by: String @readOnly
        creation_date: Date @readOnly
        last_update_by: String @readOnly
        last_update_date: Date @readOnly
        meta_inf: Object
    }

    type Project extends BaseType {
        archive: Boolean @writeOnly
        archived: Boolean @readOnly
    }

    type QueryBuilder{
        request: String! @writeOnly
        response: Object @readOnly

         extend api {
            submitQuery(body: QueryMachine): QueryMachine @path("query/submit") @method(POST)
        }
    }

## Api

$`          Api:                                                      `$\
$`~~~~          description=Description?                                    `$\
$`~~~~          name=ID                                                     `$\
$`~~~~          directives*=Directive                                       `$\
$`~~~~          operations+=Operation                                       `$

Api types can be used to create API Endpoints and Query/Mutation.

Api Rules:

1.  `Api` can at least contain one `Operation`.

2.  `Api` may be used multiple times for a schema to define custom operations.

3.  `Api` may be used once inside a `Object` to overwrite the default CRUD operations.

4.  `Api` must only specify two methods per path (with and without ID). This overlaps with all used paths including `Object`s.

5.  `Api` names must be globally unique. This overlaps with auto generated CRUD operations for `Object`s.

Operation Rules:

1.  `Operation` of `Api` value may be a `Scalar` value with one one of the following:
    * `Int`
    * `Long`
    * `Float`
    * `Double`
    * `String`
    * `Boolean`
    * `Date`
    * `Object`
    * `Void`

2.  `Operation` of `Api` value may be a `Enum`.

3.  `Operation` of `Api` value may be a `Base`.

4.  `Operation` of `Api` value may be a `Object`.

5.  `Operation` of `Api` value may be a list when enclosed with brackets.

6.  `Operation` of `Api` value may be marked as required.

Example:

    extend api {
        submitObject(body: Object): Void @path("/foo") @method(POST)
    }

## Directive

There are certain builtin directives that can be used to modify the generation behavior.

1.  `Directive` `@query` may be use on any `Base` or `Object` `Field` to create a query parameter for the get all method.

2.  `Directive` `@unique` may be use on any `Base` or `Object` `Field` to mark a `Field` as unique.

3.  `Directive` `@hidden` may be use on any `Base` or `Object` `Field` to mark a `Field` as hidden.

4.  `Directive` `@readOnly` may be use on any `Base` or `Object` `Field` to mark a `Field` as read only.

5.  `Directive` `@writeOnly` may be use on any `Base` or `Object` `Field` to mark a `Field` as write only.

6.  `Directive` `@composition` may be used on a `Object` `Field` to create a parent-child relation. The `Field` value must be a list `Object`.

7.  `Directive` `@aggregation` may be used on a `Object` `Field` to create a independent relation. The `Field` value must be a list `Object`.

8.  `Directive` `@path` must be used on any `Api` `Field` which are not part of a `Object`. This specifies the API Path.

9.  `Directive` `@path` must be used on any `Api` `Field` which is part of a `Object`. This specifies the API Path.

10. `Directive` `@method` may be used on any `Api` `Field` to specify the REST Method. Valid values are GET | POST | PUT | PATCH | DELETE.

11. `Directive` `@namespace` may be used on any `Base`, `Api` or `Object` for grouping.

12.  `Directive` `@pagination` may be used on any `Api` `Field` for converting response in a pageable object.

13.  `Directive` `@produce` may be used on any `Api` `Field` for changing the mime type.

14.  `Directive` `@consumes` may be used on any `Api` `Field` for changing the mime type.

15.  `Directive` `@generate` may be used on `Api` to specify the generated operations. Valid values are GET_ALL, CREATE, GET, REPLACE, UPDATE, DELETE, ADD, REMOVE.

16.  `Directive` `@minSize` may be used on `String`, `Int`, `Long` typed `Object Field` for setting minimum (length) of the value.

17.  `Directive` `@maxSize` may be used on `String`, `Int`, `Long` typed `Object Field` for setting maximum (length) of the value.

18.  `Directive` `@headers` may be used on any `Api` or `Field` for adding response headers to the operation.

19.  `Directive` `@force-generate` may be used on any `Base` or `Enum` to force the generation regardless wether the entity is used anywhere or not.
