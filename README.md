# QSDL

A Schema-Definition-Language Generator inspired by GraphQL.

## Overview

The QSDL Generator allows a domain model based approach to generate various specifications and boiler-code. The Language is inspired by GraphQL with minor modifications to accommodate OpenAPI and sensible QoL features.

The idea is offer a minimal approach to a API definition in order to define CRUD access to a domain model graph where domain objects have parent-child like dependencies. A simple Object definition in QSDL will generate the GET ALL / POST / GET / PUT / PATCH / DELETE Operations.

Internally QSDL leverages [textX](https://github.com/textX/textX) for describing the meta-language and [Jinja2](https://github.com/pallets/jinja) as template generator.

Currently the following generators are available:

- OpenAPI
- SpringBoot
- PlantUML

### Requirements

The QSDL package currently supports the Python version:

- 3.13

### Installation

### Using uv (Recommended)

```bash
# Install latest unreleased version directly from the repository
uv tool install git+https://gitlab.com/henn1001/qsdl

# If you want to update a previously installed version
uv tool install git+https://gitlab.com/henn1001/qsdl
uv tool upgrade qsdl

# Or install in development mode for local development
git clone https://gitlab.com/henn1001/qsdl
cd qsdl
uv sync
```

### Using pip(x)

```bash
# install the latest released version via pip
pip install qsdl --extra-index-url https://@gitlab.com/api/v4/projects/20759213/packages/pypi/simple

# or pipx
pipx install qsdl --extra-index-url https://@gitlab.com/api/v4/projects/20759213/packages/pypi/simple
```

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

Examples can be found in `examples/`.

- [Example API](examples/openapi/input.qsdl)

# Language Documentation

For comprehensive documentation on the QSDL language, see the [Documentation](./docs/) folder:

- **[Language overview](./docs/core/language.md)** — Type definitions, syntax, and examples
- **[Rules & requirements](./docs/core/rules.md)** — All DSL constraints and validation rules (with unique identifiers)
- **[Directives](./docs/core/directives.md)** — Complete reference for all 22 directives with examples
- **[Basic data modeling](./docs/guides/basic-data-modeling.md)** — Practical guide to designing schemas
- **[Relationships](./docs/guides/relationships.md)** — Composition, aggregation, and entity relationships

The language definition is formally specified in the TextX grammar file:
[`src/qsdl/dsl/definition/entity.tx`](src/qsdl/dsl/definition/entity.tx)
