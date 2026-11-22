# Design

## Context

See [proposal.md](proposal.md) and the [directive-processing spec](specs/directive-processing/spec.md). textX 4.4.0 runs object processors depth-first after resolving references for both the root and imported models. An owner callback can bind the complete directive list before `parse_schema()` merges the imports and completes the schema. The generation pipeline already resolves a generator before parsing the schema.

## Goals / Non-Goals

- **Goals:** Use one attachment and lookup model on every directive owner; support typed definitions declared by the selected generator; keep generated output and effective field semantics stable for valid existing schemas.
- **Non-goals:** Build a round-trip source model, support live recomputation after directive changes, redesign scalar mapping syntax or fallback behavior, or create a global plugin registry.

## Decisions

### Bind the ordered collection in the owner callback

Use one `directives*=Directive` list for each existing owner (`Scalar`, `Enum`, `Base`, `Object`, `Field`, `Api`, `Operation`) in `src/qsdl/dsl/definition/entity.tx`. Remove the dedicated directive productions and `Method` rule; keep type references and `!`, `?`, `^` argument modifiers in the grammar. Capture raw payload text, parentheses presence (distinguishing `@flag` from `@flag()`), and source location; a `)` inside single- or double-quoted strings does not end a payload. Do not scan raw schema text outside textX.

Treat temporary textX `Directive` parse instances as construction inputs, not the public identity boundary. Owner callbacks in `obj_processors.py` pass the complete raw list to `directive_parser.py` to validate directive names, reject exact-name duplicates at the second occurrence, decode recognized specs, and bind the public `Directives` collection. Capture `textx.get_location()` (and copy `_tx_position` / `_tx_position_end` or provide a unified location helper) before replacing temporary parse nodes so semantic diagnostics in both root and imported files report exact locations. Update `get_children_of_directive(schema)` to iterate `owner.directives` across `_directive_owners(schema)` rather than relying on `textx.model.get_children_of_type()` traversing a custom `Sequence`.

Remove the standalone directive normalization callback and `_GRAMMAR_DIRECTIVES` presence checks. Keep the normalized `str | None` representation for opaque nodes; core string decoders follow textX `STRING` conversion (supporting both `'...'` and `"..."` and escaped quotes). Preserve signed integer syntax, empty `@generate()` lists, explicit `0` and `""`, and the distinction between absent and empty payloads. Leave formerly accepted `@force-generate` payloads presence-based so binding the flag does not introduce a new payload restriction there; all other core flags reject parentheses.

*Rationale & alternatives:* Binding in owner callbacks gives even direct metamodel parses an ordered `Directives` collection and owner-local diagnostics immediately, whereas deferring all binding to `model_post_processor()` would leave half-parsed raw textX nodes exposed on imported models before merge. Scanning source text outside textX was rejected because textX already tracks exact file/line/column across imports.

### Expose one attached node through every lookup

Use one immutable node type stored in a single ordered collection per owner, with stateless typed views for built-in directives:

```python
@dataclass(frozen=True, slots=True)
class RawDirective:
    name: str
    has_parens: bool
    raw_value: str | None
    location: SourceLocation


@dataclass(frozen=True, slots=True)
class DirectiveSpec[T]:
    name: str
    owners: tuple[type[DirectiveOwner], ...]
    decode: Callable[[RawDirective], T]
    validate_value: Callable[[T], None] | None = None


@dataclass(frozen=True)
class Directive[T]:
    parent: DirectiveOwner
    name: str
    value: T
    spec: DirectiveSpec[T] | None  # None when no active spec claims (name, owner)
    origin: Literal["source", "synthetic"]
    location: SourceLocation | None


class Directives(Sequence[Directive[Any]]):
    # Iteration and indexing use attachment order; the collection owns the nodes.
    def get[T](self, spec: DirectiveSpec[T]) -> Directive[T] | None: ...
    def by_name(self, name: str) -> Directive[Any] | None: ...
    def attach_synthetic[T](self, spec: DirectiveSpec[T], value: T) -> Directive[T]: ...


class ObjectDirectiveView:
    def __init__(self, directives: Directives) -> None:
        self._directives = directives

    @property
    def namespace(self) -> Directive[str] | None:
        return self._directives.get(NAMESPACE)
```

- **Lookup and identity:** `get(spec)` matches `node.spec is spec`, not just `node.name == spec.name`; an opaque node on an unsupported owner (e.g., `@namespace("Domain")` on `Scalar`) or from an unselected generator is returned by `by_name()`, never by `get(spec)`. Built-in flag specs are `DirectiveSpec[bool]` and decode bare `@flag` to `True`.
- **Owner views:** Each owner exposes `owner.directive` returning a stateless view over `owner.directives` (`EnumDirectiveView`, `BaseDirectiveView`, `ObjectDirectiveView`, `FieldDirectiveView`, `ApiDirectiveView`, `OperationDirectiveView`, and an empty `ScalarDirectiveView` on `Scalar` for uniform owner shape). Views store no values and construct/delegate cheaply over linear lookup in `Directives` (add an internal dict index only if profiling warrants it). Migrate `qutil.get_directive_of_name()` to `entity.directives.by_name(name)` without cloning nodes.
- **Synthetic attachment:** Replace public `list` mutation with `directives.attach_synthetic(spec, value)`. It validates `isinstance(owner, spec.owners)`, exact-name uniqueness in `owner.directives`, and `spec.validate_value(value)` (or type check for flags/strings), then appends a new `Directive(..., origin="synthetic", location=None)` owned by that recipient without reordering source nodes. Propagating `@force-generate` attaches a synthetic node only when `FORCE_GENERATE` is absent, preserving any explicit source node. Spring's synthetic filter and request-body `Base` helpers attach their own synthetic `SPRING_PACKAGE` nodes rather than sharing `namespace_source`'s node instance.

Worked caller contract:

```qsdl
type Foo @spring-package("pkg") @namespace("Domain") {
    label: String @readOnly
    extend api {
        run(): String @path("run") @headers(X-Token: String) @method(POST)
    }
}
```

```python
# Object: built-in names get typed accessors; generator specs use typed keys.
namespace = foo.directive.namespace  # Directive[str] | None
assert namespace is not None
assert namespace is foo.directives.get(NAMESPACE)
assert namespace is foo.directives.by_name("namespace")
assert namespace is foo.directives[1]
assert namespace.value == "Domain"

package = foo.directives.get(SPRING_PACKAGE)  # Directive[str] | None (when Spring active)
assert package is foo.directives[0]

# Field: a flag is a Directive[bool] node when present, None when absent.
assert label.directive.is_read_only
assert label.directives.get(READ_ONLY) is not None
assert not label.directive.is_write_only

# Operation: the attached node exposes the completed value.
assert run.directive.path is not None and run.directive.path.value == "/run"
assert run.directive.method is not None and run.directive.method.value == "POST"
assert run.directive.method.origin == "source"
# With no @method, the completed operation has a synthetic GET node.
```

```text
foo.directives[1] -------------------+
foo.directives.by_name("namespace") -+--> one Directive[str](name="namespace", value="Domain")
foo.directives.get(NAMESPACE) -------+
foo.directive.namespace -------------+
```

*Rationale & alternatives:* A separate `core_directives` value bag or consuming core directives out of `owner.directives` would split source order and force callers to check two stores. Stateless views over a single sequence preserve source order, node identity, and static typing simultaneously.

### Complete canonical values in the directive collection

Remove directive projections and compatibility aliases from every owner. Validators, generators, and templates read typed nodes. Compute relation status from the composition and aggregation nodes rather than storing a separate flag. Keep structural fields such as names, type references, and argument modifiers.

During schema construction, normalize source paths and resolve source headers before publishing the completed model. Internal completion may replace a provisional immutable node in its existing slot, retaining its spec, owner, source location, and origin. All completed lookups return the same final node. A custom operation still requires a source `@path`.

- `@generate` exposes the validated immutable tuple, including `()` for `@generate()`. Consumers read the tuple directly.
- `@headers` validates declaration syntax during binding and resolves names after imports are merged. The completed node holds an immutable tuple of resolved header records with name, type, and array status. The unresolved declarations are construction inputs, not a second public value.
- Append synthetic method and media type nodes for applicable defaults. Generated CRUD operations attach synthetic path, method, and other directive-backed values instead of setting owner fields.
- Append a synthetic API namespace node when the value is inherited. Spring uses node origin to distinguish explicit API namespace from inherited namespace and preserve package precedence.

Keep explicit empty values on their source nodes and preserve existing output behavior. Synthetic completion must not overwrite a source annotation.

### Scope generator definitions to the parse request

Declare each built-in directive once in a single core catalog (`src/qsdl/dsl/directives.py` or `directive_parser.py`). Neither `entity.tx` nor `obj_processors.py` redeclares supported names, owners, or payload syntax.

Extend the generator contract and parse entrypoints explicitly:
- `Generator.directive_specs: ClassVar[tuple[DirectiveSpec[Any], ...]] = ()` (exposed via `GeneratorDefinition.directive_specs`). `validate_generator()` verifies `directive_specs` is a `tuple` of `DirectiveSpec` instances with valid directive names (`_DIRECTIVE_NAME`), non-empty `owners` drawn from `DirectiveOwner`, no duplicate names within the generator, and no name collisions with the built-in core catalog.
- `parse_schema(input_path: Path | None = None, raw_schema: str | None = None, *, directive_specs: Sequence[DirectiveSpec[Any]] = ()) -> dsl.Schema` validates caller-supplied `directive_specs` against the same collision/duplication rules and passes the active spec table through parse-scoped `model_params` (or a parse-scoped context read by `obj_processors` and propagated by `CanonicalImportURI` via `model._tx_model_params`) so root and imported schemas bind against the exact same specs without mutating shared metamodel state.
- `core._prepare()` passes `directive_specs=definition.directive_specs` into `parse_schema(...)`. Direct `parse_schema()` calls without `directive_specs` activate only core specs; library callers invoking `generator.generate(schema, config)` directly pass `directive_specs=generator.directive_specs` when they want typed generator directives bound.

Binding rules per `(name, owner)` during a parse:
1. If a core spec matches `(name, type(owner))`, bind and decode with that core spec; malformed payloads raise a located `TextXSemanticError`.
2. Else if the selected generator declares `name`: if `isinstance(owner, spec.owners)`, bind and decode with that generator spec (raising a located `TextXSemanticError` on malformed payloads); otherwise raise a located `TextXSemanticError` for unsupported owner.
3. Otherwise (including a core directive name used on an unsupported owner, an unselected generator's directive name, or an unknown custom directive), retain an opaque `Directive[str | None]` with `spec=None` and `normalize_directive_value(raw_value)` (whilst rejecting invalid directive identifier casing in `validate_member_names`).

*Rationale & alternatives:* Passing `directive_specs` per parse request avoids a global plugin registry (which would cause cross-target collisions or order-dependent import side effects) while still catching typos in `@spring-package` owners/payloads before generation starts when Spring is selected. Keeping core names on unsupported owners opaque preserves backward compatibility for schemas using generic annotations like `@namespace` on a `Scalar`, whereas generator-declared names explicitly opt into owner checking for that target.

### Migrate each built-in generator's directives

| Generator | Specs, value types, and supported owners |
| --- | --- |
| Spring | `SPRING_PACKAGE: DirectiveSpec[str]` on `(Base, Object, Enum, Api)`; `SPRING_CONTROLLER: DirectiveSpec[str]` on `(Api,)`; `SPRING_SCALAR: DirectiveSpec[SpringScalarMapping]` on `(Scalar,)` |
| OpenAPI | `OPENAPI_SCALAR: DirectiveSpec[OpenApiScalarMapping]` on `(Scalar,)` |
| PostgreSQL | `POSTGRES_SCALAR: DirectiveSpec[str]` on `(Scalar,)` |
| PlantUML, i18n, void | `directive_specs = ()` (built-in DSL specs only) |

Payload contracts for built-in generator specs:
- `SPRING_PACKAGE`, `SPRING_CONTROLLER`, `POSTGRES_SCALAR`: require a single non-empty quoted string; bare `@spring-package`, empty `""`, or unquoted tokens raise a located `TextXSemanticError`. Preserve Spring package precedence and controller target resolution.
- `SPRING_SCALAR`: require a single quoted string decoded into `@dataclass(frozen=True, slots=True) class SpringScalarMapping: type: str; entity: str | None = None; pattern: str | None = None`. Split segments on `", "` (preserving commas without a trailing space inside regex quantifiers such as `{1,38}`). The first segment must be a non-empty `type` (not `key: value`); subsequent segments must be `key: value` with `key in {"entity", "pattern"}`, no duplicate keys, and non-empty `value`. Any violation raises a located `TextXSemanticError` when Spring is selected.
- `OPENAPI_SCALAR`: require a single quoted string decoded into `@dataclass(frozen=True, slots=True) class OpenApiScalarMapping: type: str; format: str | None = None; pattern: str | None = None`, using the same `", "` segment rule and validating `key in {"format", "pattern"}`, no duplicates, and non-empty values.

Replace `qutil.map_custom_type()` / `qutil.get_type_override()` usage in Spring, OpenAPI, and PostgreSQL with typed lookups (`scalar.directives.get(SPRING_SCALAR)`, etc.) while keeping built-in scalar fallback tables (`custom_types`, `custom_type_formats`) unchanged. Only the selected target binds its definitions; the other targets' scalar directives remain opaque `Directive[str | None]`. Do not add prefix or spelling checks for undeclared names.

Spring also renders bundled OpenAPI and Flyway artifacts. Those renderers use valid scalar mappings for their respective targets without binding them to the Spring schema. The render-scoped fallback leaves the source nodes opaque and does not raise errors for inactive definitions.

```text
built-in specs + selected generator specs
    --> textX captures ordered RawDirective inputs
    --> owner callback validates duplicates & binds Directives
          |--> indexing / by_name / get(spec) / owner.directive.<x> return the same Directive[T]
    --> parse_schema() merges imports and completes canonical directive nodes
    --> generator consumes owner.directive and owner.directives.get(GENERATOR_SPEC)
```

## Risks / Trade-offs

- **Earlier diagnostics** → Owner-local duplicate and payload errors fire during model loading rather than post-merge validation, which can precede circular-import diagnostics. Mitigation: test source locations in imported files and verify `CanonicalImportURI` propagates `model_params` cleanly.
- **Collection and textX migration** → Replacing `list[Directive]` and temporary textX parse nodes can break callers mutating `.directives` or calling `get_children_of_directive()` / `get_location()`. Mitigation: audit all `.directives` sites (`inherit_force_generation`, Spring synthetic filter/request bases, validators), route `get_children_of_directive()` through `_directive_owners()`, and preserve location metadata on bound `Directive[T]` nodes.
- **Generator isolation and direct callers** → Two parses in one process with different generators must not leak bound specs, and tests/callers invoking `parse_schema()` + `generator.generate()` directly will see opaque generator directives unless they pass `directive_specs`. Mitigation: scope active specs strictly to each `parse_schema()` call, document `parse_schema(..., directive_specs=...)` in `docs/generators/plugins.md` and `docs/guides/library-generation.md`, and test multi-generator sequential parses.
- **Payload versus output** → Explicit `0` and `""` survive binding (`directive.min_size.value == 0`, `directive.default.value == ""`), while downstream templates check truthiness in places. Mitigation: assert typed payload survival in rule tests while preserving existing Spring and OpenAPI rendering rules for omitted vs empty values.
