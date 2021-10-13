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