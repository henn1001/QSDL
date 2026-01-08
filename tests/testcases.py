"""
Centralized test cases collection for QSDL generators.

This module provides reusable test input strings organized by complexity levels,
covering all functionality from scalar types to complex scenarios.
"""

# ============================================================================
# GROUP 1: SCALAR TYPES & BASIC FEATURES
# ============================================================================

BASIC_TYPES = """\
  base A {
    int: Int
    long: Long
  }

  base B extends A {
    float: Float
    double: Double
    string: String
  }

  type Foo extends B {
    boolean: Boolean
    date: Date
    datetime: Datetime
    object: Object
  }
"""

BASIC_TYPES_AS_LIST = """\
  type Foo {
    int: [Int]
    long: [Long]
    float: [Float]
    double: [Double]
    string: [String]
    boolean: [Boolean]
    date: [Date]
    datetime: [Datetime]
    object: [Object]
  }
"""

ENUM_USAGE = """\
  enum Status {
    OPEN
    TO_DO
    CLOSED
  }

  type Foo {
    status: Status
    states: [Status]
  }
"""

REQUIRE_AND_UNIQUE = """\
  type TableFour {
    aaa: String!
    bbb: [String]!
    ccc: String @unique
    ddd: [String] @unique
    eee: String! @unique
    fff: [String]! @unique
  }
"""


# ============================================================================
# GROUP 2: BASE TYPE - DEFAULT FLATTENING BEHAVIOR
# ============================================================================

DEFAULT_FLATTENING = """\
  base Bar {
    field: String
  }
  base A {
    int: Int
    long: Long
  }
  base B extends A {
    float: Float
    double: Double
    string: String
    fruit: Bar
  }
  type Foo {
    a: B
    b: B
    boolean: Boolean
    date: Date
    datetime: Datetime
    object: Object
  }
"""

NESTED_BASE_FLATTENING = """\
  base ContactInfo {
    email: String
    phone: String
  }
  base Address {
    street: String
    city: String
    contact: ContactInfo
  }
  type Company {
    name: String
    headquarters: Address
  }
"""

MULTIPLE_BASE_FIELDS_SAME_TYPE = """\
  base Address {
    street: String
    city: String
  }
  type User {
    name: String
    billingAddress: Address
    shippingAddress: Address
    mailingAddress: Address
  }
"""

BASE_FLATTENING_WITH_CONSTRAINTS = """\
  base Credentials {
    username: String! @unique
    password: String!
  }
  type User {
    name: String
    credentials: Credentials
  }
"""


# ============================================================================
# GROUP 3: BASE TYPE - @opaque DIRECTIVE (JSONB)
# ============================================================================

OPAQUE_JSONB = """\
  base Address {
    street: String
    city: String
  }
  type User {
    primaryAddress: Address @opaque
    secondaryAddress: Address @opaque
    name: String
  }
"""

OPAQUE_NESTED_BASE = """\
  base ContactInfo {
    email: String
    phone: String
  }
  base Address {
    street: String
    city: String
    contact: ContactInfo
  }
  type Company {
    name: String
    headquarters: Address @opaque
  }
"""

OPAQUE_BASE_WITH_CONSTRAINTS = """\
  base Metadata {
    key: String! @unique
    value: String!
  }
  type Document {
    title: String
    metadata: Metadata @opaque
  }
"""

BASE_ARRAY_JSONB = """\
  base Variant {
    size: String
    color: String
  }
  type Product {
    name: String
    variants: [Variant]
    other: [Variant] @opaque
  }
"""


# ============================================================================
# GROUP 4: MIXED BASE TYPE USAGE
# ============================================================================

MIXED_BASE_SAME_TYPE = """\
  base Address {
    street: String
    city: String
    zipCode: String
  }
  type Company {
    name: String
    primaryAddress: Address
    billingAddress: Address @opaque
    shippingAddresses: [Address]
  }
"""

MIXED_BASE_AND_OBJECT_FIELDS = """\
  base Address {
    street: String
    city: String
  }
  type Manager {
    name: String
  }
  type Employee {
    name: String
    homeAddress: Address
    manager: Manager
  }
"""


# ============================================================================
# GROUP 5: OBJECT TYPE RELATIONSHIPS
# ============================================================================

ONE_TO_ONE = """\
  type User {
    primary_metric: Metric
    secondary_metric: Metric
  }
  type Metric {
    likes: Int
  }
"""

ONE_TO_MANY = [
    """\
      type User {
        metric: [Metric]
      }
      type Metric {
        likes: Int
      }
    """,
    """\
      type User {
        metric: [Metric] @aggregation
      }
      type Metric {
        likes: Int
      }
    """,
    """\
      type User {
        metric: [Metric] @composition
      }
      type Metric {
        likes: Int
      }
    """,
]

NESTED_OBJECT_RELATIONSHIPS = """\
  type Country {
    name: String
  }
  type City {
    name: String
    country: Country
  }
  type Address {
    street: String
    city: City
  }
  type Company {
    name: String
    headquarters: Address
  }
"""

OBJECT_ARRAYS_WITH_DIRECTIVES = """\
  type Tag {
    name: String
  }
  type Category {
    name: String
  }
  type Product {
    name: String
    tags: [Tag] @composition
    categories: [Category] @aggregation
  }
"""


# ============================================================================
# GROUP 6: COMPLEX SCENARIOS & DEEP NESTING
# ============================================================================

DEEPLY_NESTED_BASE_TYPES = """\
  base GeoCoordinates {
    latitude: Float
    longitude: Float
  }
  base ContactInfo {
    email: String
    phone: String
    location: GeoCoordinates
  }
  base Address {
    street: String
    city: String
    contact: ContactInfo
  }
  type Company {
    name: String
    headquarters: Address
  }
"""

DEEPLY_NESTED_BASE_WITH_OPAQUE = """\
  base Rating {
    stars: Int
    review: String
  }
  base Author {
    name: String
    rating: Rating
  }
  base BookMetadata {
    isbn: String
    author: Author
    publisher: String
  }
  type Book {
    title: String
    metadata: BookMetadata @opaque
  }
"""

COMPLEX_MIXED_BASE_OBJECT_ARRAYS = """\
  base Address {
    street: String
    city: String
  }
  base Metadata {
    key: String
    value: String
  }
  type Department {
    name: String
  }
  type Employee {
    name: String
    homeAddress: Address
    workAddress: Address @opaque
    metadata: [Metadata]
    department: Department
    skills: [String]
  }
"""

BASE_AND_OBJECT_SAME_STRUCTURE = """\
  base AddressValue {
    street: String
    city: String
  }
  type AddressEntity {
    street: String
    city: String
  }
  type Person {
    name: String
    homeAddress: AddressValue
    workAddress: AddressEntity
  }
"""

DEEP_COMPOSITION_CHAIN = """\
  type Employee {
    name: String
    email: String
  }
  type Team {
    name: String
    members: [Employee] @composition
  }
  type Department {
    name: String
    teams: [Team] @composition
  }
  type Organization {
    name: String
    departments: [Department] @composition
  }
"""

DEEP_AGGREGATION_CHAIN = """\
  type Address {
    street: String
    city: String
  }
  type Student {
    name: String
    addresses: [Address] @aggregation
  }
  type Course {
    name: String
    students: [Student] @aggregation
  }
  type University {
    name: String
    courses: [Course] @aggregation
  }
"""

MIXED_COMPOSITION_AGGREGATION = """\
  type Tag {
    name: String
  }
  type Project {
    name: String
    tags: [Tag] @aggregation
  }
  type Company {
    name: String
    ownedProjects: [Project] @composition
    industryTags: [Tag] @aggregation
  }
"""

COMPLEX_ENTITY_GRAPH = """\
  type Customer {
    name: String
    email: String
  }
  type Product {
    name: String
    price: Float
  }
  type OrderItem {
    quantity: Int
    product: Product
  }
  type Order {
    orderNumber: String
    customer: Customer
    items: [OrderItem] @composition
    relatedProducts: [Product] @aggregation
  }
"""

OBJECT_SCALAR_ARRAY = """\
  type Foo {
    metadata: [Object]
  }
"""

TWO_PARENT_ONE_CHILD = """\
  type Fruit {
    name: String
  }
  type Foo {
    name: String
    basket: [Fruit] @composition
  }
  type Bar {
    name: String
    basket: [Fruit] @composition
  }
"""
