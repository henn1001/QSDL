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
* fix nested inputs for GraphQL
* implement Operations to query/mutation in GraphQL
* write readme
* write more openapi tests
* write graphql tests
