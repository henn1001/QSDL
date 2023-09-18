```plantuml
@startuml
set namespaceSeparator .


class entity.Schema  {
  title : STRING
  version : STRING
  description : Description
  servers : list[STRING]
}


class entity.Type <<abstract>> {
}


class entity.ValueType <<abstract>> {
}


class entity.Import  {
  importURI : STRING
}


class entity.Scalar  {
  name : ID
}


class entity.Enum  {
  description : Description
  name : ID
  namespace : STRING
  values : list[ID]
}


class entity.Base  {
  description : Description
  name : ID
  is_deprecated : optional<BOOL>
  namespace : STRING
}


class entity.Object  {
  description : Description
  name : ID
  is_deprecated : optional<BOOL>
  namespace : STRING
}


class entity.Field  {
  description : Description
  name : ID
  is_array : optional<BOOL>
  is_required : optional<BOOL>
  is_query : optional<BOOL>
  is_read_only : optional<BOOL>
  is_write_only : optional<BOOL>
  is_composition : optional<BOOL>
  is_aggregation : optional<BOOL>
  is_unique : optional<BOOL>
  is_hidden : optional<BOOL>
  min_size : INT
  max_size : INT
}


class entity.Api  {
  description : Description
  is_deprecated : optional<BOOL>
  namespace : STRING
  generate : optional<list[STRING]>
}


class entity.Operation  {
  description : Description
  name : ID
  is_array : optional<BOOL>
  is_required : optional<BOOL>
  path : STRING
  method : Method
  is_pageable : optional<BOOL>
  consumes : STRING
  produces : STRING
}


class entity.Argument  {
  name : ID
  is_array : optional<BOOL>
  is_required : optional<BOOL>
  is_query : optional<BOOL>
  is_header : optional<BOOL>
}


class entity.Directive  {
  name : ID
  value : STRING
}


entity.Schema *--> entity.Import: imports 0..*
entity.Schema *--> entity.Type: types 0..*
entity.Type <|-- entity.Scalar
entity.Type <|-- entity.Enum
entity.Type <|-- entity.Base
entity.Type <|-- entity.Api
entity.Type <|-- entity.Object
entity.ValueType <|-- entity.Scalar
entity.ValueType <|-- entity.Enum
entity.ValueType <|-- entity.Base
entity.ValueType <|-- entity.Object
entity.Scalar *--> entity.Directive: directives 0..*
entity.Enum *--> entity.Directive: directives 0..*
entity.Base o--> entity.Base: supertype
entity.Base *--> entity.Directive: directives 0..*
entity.Base *--> entity.Field: fields 1..*
entity.Object o--> entity.Base: supertype
entity.Object *--> entity.Directive: directives 0..*
entity.Object *--> entity.Field: fields 0..*
entity.Object *--> entity.Api: api
entity.Field o--> entity.ValueType: value
entity.Field *--> entity.Directive: directives 0..*
entity.Api *--> entity.Directive: directives 0..*
entity.Api *--> entity.Operation: operations 0..*
entity.Operation *--> entity.Argument: arguments 1..*
entity.Operation o--> entity.ValueType: value
entity.Operation *--> entity.Argument: response_headers 1..*
entity.Operation *--> entity.Directive: directives 0..*
entity.Argument o--> entity.ValueType: value

legend
  Match rules:
  |= Name  |= Rule details |
  | Description |  |
  | Method | GET\|POST\|PUT\|PATCH\|DELETE |
  | Comment | \\/\\/.*$ |
  | MultiLine | (\?ms)\\\"\{3\}(.+\?)\\\"\{3\} |
  | SingleLine | \\\"([^\\\"\\n\\r]+\?)\\\" |
end legend

@enduml
```