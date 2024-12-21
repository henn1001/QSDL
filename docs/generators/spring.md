# Spring Generator

This generator provides a boilerplate for a - mostly domain driven - Application with Spring Boot.

## Configuration

These options may be applied when using the cli or via a config.json

```json
{
    "title": "SpringBootApp",
    "group_id": "app",
    "base_package": "app.server",
    "artifact_id": "app",
    "database": "HIBERNATE | NO",
    "use_encapsulation": false,
    "use_builder": true,
    "use_auditing": false,
    "id_type": "LONG | STRING",
    "api_path": "api",
    "controller_path": "controller",
    "service_path": "service",
    "domain_path": "domain.dto",
    "entity_path": "domain.entity",
    "mapper_path": "domain.mapper",
    "repository_path": "repository",
    "enum_path": "constants",
    "exception_path": "exceptions",
    "model_path": "models",
    "config_path": "config",
    "util_path": "util",
    "package_placeholder_fallback": "global"
}
```

## Types

The following type conversion map is used between the builtin QSDL types and Java types.

```json
{
    "Int": "Integer",
    "Long": "Long",
    "Float": "Float",
    "Double": "Double",
    "String": "String",
    "Boolean": "Boolean",
    "ID": "Long",
    "Date": "LocalDate",
    "Datetime": "OffsetDateTime",
    "Object": "ObjectNode",
    "Void": "Void",
}
```

Additional types can be defined via scalars.

```
scalar UUID @spring("UUID")
```


For spring, three values can be provided which translate to "type", "entity" and "pattern".

> Note: Parsing here is a bit tricky and done by splitting via ', '. The whitespace after the comma is especially important to not split commas within the provided regex.

Example:
```
scalar BigInt @spring("String, entity: java.math.BigInteger, pattern: ^-?[0-9]{1,38}$")

scalar Decimal @spring("String, entity: java.math.BigDecimal, pattern: ^(-)?[0-9][0-9]*(?:.[0-9]{1,18})?$")
```
