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
  is_transient : optional<BOOL>
  is_ignored : optional<BOOL>
  min_size : INT
  max_size : INT
  default : STRING
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


entity.Schema *--> "0..*" entity.Import: imports
entity.Schema *--> "0..*" entity.Type: types
entity.Type <|-- entity.Scalar
entity.Type <|-- entity.Enum
entity.Type <|-- entity.Base
entity.Type <|-- entity.Api
entity.Type <|-- entity.Object
entity.ValueType <|-- entity.Scalar
entity.ValueType <|-- entity.Enum
entity.ValueType <|-- entity.Base
entity.ValueType <|-- entity.Object
entity.Scalar *--> "0..*" entity.Directive: directives
entity.Enum *--> "0..*" entity.Directive: directives
entity.Base --> "1..*" entity.Base: supertypes
entity.Base *--> "0..*" entity.Directive: directives
entity.Base *--> "0..*" entity.Field: fields
entity.Object --> "1..*" entity.Base: supertypes
entity.Object *--> "0..*" entity.Directive: directives
entity.Object *--> "0..*" entity.Field: fields
entity.Object *-->  entity.Api: api
entity.Field -->  entity.ValueType: value
entity.Field *--> "0..*" entity.Directive: directives
entity.Api *--> "0..*" entity.Directive: directives
entity.Api *--> "0..*" entity.Operation: operations
entity.Operation *--> "1..*" entity.Argument: arguments
entity.Operation -->  entity.ValueType: value
entity.Operation *--> "1..*" entity.Argument: response_headers
entity.Operation *--> "0..*" entity.Directive: directives
entity.Argument -->  entity.ValueType: value

legend
  Match rules:
  |= Name  |= Rule details |
  | Comment | \\/\\/.*$ |
  | Method | GET\|POST\|PUT\|PATCH\|DELETE |
  | Description |  |
  | SingleLine | \\\"([^\\\"\\n\\r]+\?)\\\" |
  | MultiLine | (\?ms)\\\"\{3\}(.+\?)\\\"\{3\} |
end legend

@enduml
```