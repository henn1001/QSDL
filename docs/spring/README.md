# Custom Directives

## @controller

Allows to move custom apis into a different controller.

```
    extend api @controller("Buzzword") {
        submitQury(arg1: String, arg2: [Int]): Object @path("query") @method(PATCH)
    }

    type Buzzword @namespace("Incident"){
        name: String!
        extend api @generate("UPDATE") {}
    }
```

# Example Use Cases

## Read-Only Nested Object

Given the following example:

```
type Foo extends {
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
scalar UUID @openapi("string,uuid") @spring("UUID")
scalar MultipartFile @openapi("string,binary") @spring("MultipartFile")

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
