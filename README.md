# QSDL

A Schema-Definition-Language Generator inspired by GraphQL.

## Overview

The QSDL Generator allows a domain model based approach to generate OpenAPI and GraphQL specifications. The Language is inspired by GraphQL with minor modifications to accommodate OpenAPI and sensible QoL features.

Internally QSDL leverages [textX](https://github.com/textX/textX) for describing the meta-language and [Jinja2](https://github.com/pallets/jinja) as template generator.

Currently the following generators are available:

- OpenAPI

- GraphQL

- PlantUML

### Requirements

The QSDL package works on Python versions:

- 3.6.x and greater
- 3.7.x and greater
- 3.8.x and greater

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

## Language

coming soon...