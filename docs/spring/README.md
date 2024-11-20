# Spring Generator

This generator provides a boilerplate for a - mostly domain driven - Application with Spring Boot.

## Config options

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

# Custom Directives

## @spring

Allows you to declare the type conversion for scalars.

```
scalar Number @spring("BigInteger")
```

## @spring-package

Allows you to use a placeholder for the relevant package paths to further customize the project layout.

Given the following config and the example from [here](../../examples/other/package_example.qsdl)...
```json
{
    "api_path": "{package}.api",
    "controller_path": "{package}.api",
    "domain_path": "{package}.dto",
    "entity_path": "{package}.db",
    "mapper_path": "{package}.mapper",
    "repository_path": "{package}.db",
    "service_path": "{package}.service",
    "enum_path": "common.constants",
    "exception_path": "common.exceptions",
    "model_path": "common.models",
    "config_path": "common.config",
    "util_path": "common.util",
}
```

... generates the following layout

```
.
├── common
│   ├── config
│   ├── constants
│   ├── exceptions
│   ├── models
│   └── util
├── custom
│   ├── api
│   └── dto
├── global
│   ├── api
│   ├── db
│   ├── dto
│   ├── mapper
│   └── service
├── project
│   ├── api
│   ├── db
│   ├── dto
│   ├── mapper
│   └── service
├── user
│   ├── api
│   ├── db
│   ├── dto
│   ├── mapper
│   └── service
├── SpringBootApp.java
└── package-info.java
```

## @spring-controller

Allows to move custom apis into a different controller.

```
    extend api @spring-controller("Buzzword") {
        submitQury(arg1: String, arg2: [Int]): Object @path("query") @method(PATCH)
    }

    type Buzzword @namespace("Incident"){
        name: String!
        extend api @generate("UPDATE") {}
    }
```

## @spring-void-input

Prevent argument generation for custom operations.

```
extend api {
    uploadFile(file: MultipartFile!, docType: String, entityId: UUID!): Void @path("upload") @method(POST) @consumes("multipart/form-data") @spring-void-input
}
```

# Example Use Cases

## Read-Only Nested Object

Given the following example:

```
type Foo {
    bar_id: Int @writeOnly
    bar: Bar @readOnly
}

type Bar {
    field: String
}
```

The code needs to look like this:

```java
@Column(name = "tester_id")
@JsonProperty(value = "tester_id", access = JsonProperty.Access.WRITE_ONLY)
public Integer testerId;

@JoinColumn(name = "tester_id", insertable = false, updatable = false)
@ManyToOne(cascade=CascadeType.ALL)
@JsonProperty(value = "tester", access = JsonProperty.Access.READ_ONLY)
public Tester tester;
```

## Non-Array Composition/Aggregation

Given the following example:

```
type Bar {
    field1: String!
}

type Foo {
    field1: String!
    field2: Bar @composition
    field3: Bar @aggregation
}
```

This is currently not supported.

## Orphan-Removal

Auto-Deletion of childs is not exactly optimized by default.

https://thorben-janssen.com/avoid-cascadetype-delete-many-assocations/

## File Upload

Multipart-file upload could be specified and implemented in the following way

```
scalar UUID @openapi("string, format: uuid") @spring("UUID")
scalar MultipartFile @openapi("string, format: binary") @spring("MultipartFile")

extend api  {
    uploadFile(file: MultipartFile!, docType: String, entityId: UUID!): Void @path("upload") @method(POST) @consumes("multipart/form-data") @spring-void-input
}
```

```
public ResponseEntity<Void> uploadFile() throws Exception {

    StandardMultipartHttpServletRequest context = new StandardMultipartHttpServletRequest(request);

    MultipartFile file = context.getFile("file");
    String docType = context.getParameter("docType");
    String entityId = context.getParameter("entityId");

    return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
}
```
