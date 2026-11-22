# Copyright 2026 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for LOG-2xx rules: Directive & Metadata.

Rules covered:
- LOG-201: Directives are generator-agnostic or generator-specific
- LOG-202: Custom directives are preserved in the model
- LOG-203: Duplicate directive names on the same entity are semantic errors
"""

from pathlib import Path

import pytest
from textx import get_location
from textx.exceptions import TextXSemanticError, TextXSyntaxError

import qsdl.dsl.textx as xtx
from qsdl import dsl
from qsdl.dsl.directives import FORCE_GENERATE, HEADERS, NAMESPACE, READ_ONLY

from .conftest import ParseExpectErrorFixture, ParseFixture


class TestLogDirective:
    """Tests for LOG-201 to LOG-203: Directive & Metadata."""

    def test_LOG_201_core_directive_positive(self, parse: ParseFixture) -> None:
        """LOG-201: Core directives like @readOnly are generator-agnostic."""
        schema = parse("""
            type Foo {
                created: Datetime @readOnly
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "created")
        assert field.directive.is_read_only

    def test_LOG_201_generator_directive_positive(self, parse: ParseFixture) -> None:
        """LOG-201: Generator-specific directives like @openapi(...) are supported."""
        schema = parse("""
            scalar Email @openapi("string, format:email")

            type User {
                email: Email
            }
        """)
        scalars = xtx.get_children_of_scalar(schema)
        email_scalar = next(s for s in scalars if s.name == "Email")
        directive = email_scalar.directives.by_name("openapi")
        assert directive is not None
        assert directive.value == "string, format:email"

    def test_LOG_202_custom_directive_preserved_positive(self, parse: ParseFixture) -> None:
        """LOG-202: Custom directives are preserved in the model."""
        schema = parse("""
            type Foo @myCustom("value") {
                field: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        directive = obj.directives.by_name("myCustom")
        assert directive is not None
        assert directive.value == "value"

    def test_LOG_202_multiple_different_directives_positive(self, parse: ParseFixture) -> None:
        """LOG-202: Multiple different directives on same entity are preserved."""
        schema = parse("""
            type Foo @first("a") @second("b") {
                field: String
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        first = obj.directives.by_name("first")
        second = obj.directives.by_name("second")
        assert first is not None
        assert first.value == "a"
        assert second is not None
        assert second.value == "b"

    def test_LOG_202_field_directive_preserved_positive(self, parse: ParseFixture) -> None:
        """LOG-202: Custom directives on fields are preserved."""
        schema = parse("""
            type Foo {
                field: String @custom("test")
            }
        """)
        obj = xtx.get_children_of_object(schema)[0]
        field = next(f for f in obj.fields if f.name == "field")
        directive = field.directives.by_name("custom")
        assert directive is not None
        assert directive.value == "test"

    @pytest.mark.parametrize("reverse", [False, True])
    def test_interleaved_directives(self, parse: ParseFixture, reverse: bool) -> None:
        from qsdl.dsl.directives import HEADERS, METHOD, NAMESPACE, OVERRIDE, PATH, WRITE_ONLY

        def ordered(*annotations: str) -> str:
            return " ".join(reversed(annotations) if reverse else annotations)

        schema = parse(f"""
            base Labelled {{ label: String }}
            type Foo extends Labelled {ordered('@spring-package("pkg")', '@namespace("Domain")')} {{
                label: String {ordered("@custom", "@override", "@readOnly")}
                extend api {ordered("@custom", '@namespace("Routes")')} {{
                    run(): String {ordered('@path("run")', "@headers(X-Token: String)", "@method(POST)")}
                }}
            }}
        """)
        foo = xtx.get_children_of_object(schema)[0]
        (label,) = [field for field in foo.fields if field.name == "label"]
        api = xtx.get_children_of_api(schema)[0]
        run = next(operation for operation in api.operations if operation.name == "run")

        for owner, names, bound in (
            (foo, ["spring-package", "namespace"], [(NAMESPACE, foo.directive.namespace)]),
            (
                label,
                ["custom", "override", "readOnly"],
                [(OVERRIDE, label.directives.get(OVERRIDE)), (READ_ONLY, label.directives.get(READ_ONLY))],
            ),
            (api, ["custom", "namespace"], [(NAMESPACE, api.directive.namespace)]),
            (
                run,
                ["path", "headers", "method"],
                [(PATH, run.directive.path), (HEADERS, run.directive.headers), (METHOD, run.directive.method)],
            ),
        ):
            if reverse:
                names.reverse()
            assert [node.name for node in owner.directives if node.origin == "source"] == names
            for index, name in enumerate(names):
                assert owner.directives[index] is owner.directives.by_name(name)
            for spec, node in bound:
                assert node is not None
                assert node is owner.directives.get(spec) is owner.directives.by_name(spec.name)

        assert foo.directive.namespace.value == "Domain"
        assert foo.directives.by_name("spring-package").value == "pkg"
        assert label.directive.is_override
        assert label.parent is foo
        assert label.directive.is_read_only
        assert not label.directive.is_write_only
        assert label.directives.get(WRITE_ONLY) is None
        assert api.directive.namespace.value == "Routes"
        assert run.directive.path.value == "/run"
        assert run.directive.method.value == "POST"
        assert [header.name for header in run.directive.headers.value] == ["X-Token"]

    @pytest.mark.parametrize(
        "raw",
        [
            """
                type Foo @custom @custom {
                    field: String
                }
            """,
            """
                scalar Email @openapi("string") @openapi("string")
            """,
            """
                type Foo {
                    field: String @custom @custom
                }
            """,
            """
                extend api @custom @custom {
                    getFoo: String @path("foo")
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo") @custom @custom
                }
            """,
            """
                type Foo @namespace("One") @namespace("Two") {
                    field: String
                }
            """,
            """
                type Foo {
                    field: String @readOnly @readOnly
                }
            """,
            """
                type Foo {
                    field: String @minSize(1) @minSize(2)
                }
            """,
            """
                extend api @namespace("One") @namespace("Two") {
                    getFoo: String @path("foo")
                }
            """,
            """
                type Foo {
                    field: String
                    extend api @generate("GET") @generate("GET") {}
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo") @path("bar")
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo") @method(GET) @method(POST)
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo") @pagination @pagination
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo")
                        @consumes("application/json") @consumes("text/plain")
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo")
                        @produces("application/json") @produces("text/plain")
                }
            """,
            """
                extend api {
                    getFoo: String @path("foo")
                        @headers(X-Token: String) @headers(X-Request: String)
                }
            """,
        ],
    )
    def test_LOG_203_duplicate_directive_negative(
        self, raw: str, parse_expect_semantic_error: ParseExpectErrorFixture
    ) -> None:
        """LOG-203: Repeated custom and special directives are semantic errors."""
        parse_expect_semantic_error(raw)


def test_metamodel_binds_opaque_and_core_directives() -> None:
    schema = xtx.get_metamodel().model_from_str(
        'scalar Email @namespace("Domain") @custom(left => right) @bare @empty()\ntype Foo @namespace("Domain") {}'
    )
    scalar, foo = schema.types
    namespace, custom, bare, empty = scalar.directives
    assert namespace.spec is None and namespace.value == "Domain"
    assert scalar.directives.get(NAMESPACE) is None
    assert custom.spec is None and custom.value == "left => right"
    assert bare.value is None and empty.value == ""
    assert foo.directive.namespace is foo.directives[0]
    assert all(node.origin == "source" for node in xtx.get_children_of_directive(schema))
    assert namespace.location == get_location(namespace) == {"filename": None, "line": 1, "col": 14, "nchar": 20}


@pytest.mark.parametrize("raw", ["scalar Token @custom)", "scalar Token @custom(inner(nested))"])
def test_unbalanced_directive_parentheses_are_syntax_errors(raw: str) -> None:
    with pytest.raises(TextXSyntaxError):
        xtx.get_metamodel().model_from_str(raw)


def test_imported_directive_source_and_duplicate_location(tmp_path: Path) -> None:
    root = tmp_path / "root.qsdl"
    imported = tmp_path / "model.qsdl"
    root.write_text('import "model.qsdl"\n')
    first = 'type Foo @namespace("One") @custom'
    imported.write_text(first + " {}\n")
    schema = xtx.parse_schema(root)
    node = schema.types[0].directive.namespace
    assert node.location == get_location(node) == {"filename": str(imported), "line": 1, "col": 10, "nchar": 17}

    imported.write_text(first + ' @namespace("Two") {}\n')
    with pytest.raises(TextXSemanticError, match="specifies @namespace more than once") as error:
        xtx.parse_schema(root)
    assert (error.value.filename, error.value.line, error.value.col) == (str(imported), 1, len(first) + 2)


@pytest.mark.parametrize(
    ("schema", "name"),
    [
        ("type Foo { value: String @readOnly() }", "readOnly"),
        ('extend api { run(): String @path("run") @method(TRACE) }', "method"),
        ('extend api { run(): String @path("run") @method("POST") }', "method"),
        ('type Foo { extend api @generate("INVALID") {} }', "generate"),
        ('extend api @generate("INVALID") {}', "generate"),
        ('extend api { run(): String @path("run") @headers(bad_name: String) }', "headers"),
        ('extend api { run(): String @path("run") @headers(X-Token: [String) }', "headers"),
    ],
)
def test_malformed_core_payload_location(schema: str, name: str) -> None:
    with pytest.raises(TextXSemanticError, match=f"Invalid @{name}") as error:
        xtx.parse_schema(raw_schema=schema)
    assert (error.value.line, error.value.col) == (1, schema.index(f"@{name}") + 1)


def test_payloads_and_effective_defaults() -> None:
    schema = xtx.parse_schema(
        raw_schema=r"""
        type Foo @namespace('Domain') {
            label: String @minSize(+0) @default("")
            quoted: String @default("one\"two")
            extend api @generate() {
                run(): String @path('run(test\')')
            }
        }
        extend api {
            write(value: String): String @path("write") @method(POST)
        }
    """
    )
    foo, standalone = schema.types
    fields = {field.name: field for field in foo.fields}
    label = fields["label"]
    assert label.directive.min_size.value == 0
    assert label.directive.default.value == ""
    assert fields["quoted"].directive.default.value == 'one"two'
    assert foo.api.directive.generate.value == ()
    assert foo.api.directive.namespace.value == "Domain"
    assert foo.api.directive.namespace.origin == "synthetic"
    assert [node.name for node in foo.api.directives] == ["generate", "namespace"]

    run = foo.api.operations[0]
    assert run.directive.path.value == "/run(test')"
    assert run.directive.method.value == "GET"
    assert run.directive.produces.value == "application/json"
    assert run.directive.consumes is None
    assert [node.name for node in run.directives] == ["path", "method", "produces"]
    write = standalone.operations[0]
    assert write.directive.consumes.value == "application/json"
    assert write.directive.consumes.origin == "synthetic"

    direct = xtx.get_metamodel().model_from_str("type Foo { label: String @minSize(-2) }")
    assert direct.types[0].fields[0].directive.min_size.value == -2


def test_missing_custom_path_is_not_defaulted() -> None:
    with pytest.raises(TextXSemanticError, match="path"):
        xtx.parse_schema(raw_schema="extend api { run(): String }")


def test_headers_resolve_imported_type_in_canonical_node(tmp_path: Path) -> None:
    root = tmp_path / "root.qsdl"
    imported = tmp_path / "model.qsdl"
    imported.write_text('enum Token { READY }\nextend api { run(): String @path("Run/") @headers(X-Token: [Token]) }\n')
    root.write_text('import "model.qsdl"\n')
    schema = xtx.parse_schema(root)
    operation = xtx.get_children_of_operation(schema)[0]
    path, headers, method, produces = operation.directives
    assert path is operation.directive.path
    assert path.value == "/run" and path.origin == "source"
    assert (
        path.location
        == get_location(path)
        == {"filename": str(imported), "line": 2, "col": 28, "nchar": len('@path("Run/")')}
    )
    assert headers is operation.directive.headers is operation.directives.get(HEADERS)
    assert headers is operation.directives.by_name("headers")
    assert headers.origin == "source" and headers.location["filename"] == str(imported)
    (header,) = headers.value
    assert header.value is xtx.get_children_of_enum(schema)[0]
    assert header.name == "X-Token" and header.is_array
    assert method is operation.directive.method and method.value == "GET"
    assert produces is operation.directive.produces and produces.value == "application/json"
    assert all(node.origin == "synthetic" and node.location is None for node in (method, produces))
    assert operation.directive.consumes is None


def test_force_generation_attaches_recipient_nodes() -> None:
    schema = xtx.parse_schema(
        raw_schema="""
        enum Status @label { READY }
        enum Explicit @force-generate(legacy payload) { READY }
        base Payload @custom { status: Status }
        base Root @force-generate {
            payload: Payload
            explicit: Explicit
        }
    """
    )
    by_name = {owner.name: owner for owner in schema.types}
    root, payload, status, explicit = (by_name[name] for name in ("Root", "Payload", "Status", "Explicit"))
    nodes = [owner.directives.get(FORCE_GENERATE) for owner in (root, payload, status, explicit)]
    assert len({id(node) for node in nodes}) == 4
    assert [node.origin for node in nodes] == ["source", "synthetic", "synthetic", "source"]
    assert [node.name for node in payload.directives] == ["custom", "force-generate"]
    assert [node.name for node in status.directives] == ["label", "force-generate"]
    for owner, node in zip((root, payload, status, explicit), nodes, strict=True):
        assert node is owner.directives[-1] is owner.directives.get(FORCE_GENERATE)
        assert node is owner.directives.by_name("force-generate")
        assert node.parent is owner and node.value is True
        assert (node.location is None) == (node.origin == "synthetic")


def test_synthetic_attachment_validation() -> None:
    scalar = dsl.Scalar("Token")
    with pytest.raises(TypeError, match="not supported"):
        scalar.directives.attach_synthetic(FORCE_GENERATE, True)
    base = dsl.Base(parent=None, name="Payload")
    with pytest.raises(ValueError, match="expected True"):
        base.directives.attach_synthetic(FORCE_GENERATE, False)
    assert not base.directives
    node = base.directives.attach_synthetic(FORCE_GENERATE, True)
    with pytest.raises(ValueError, match="already attached"):
        base.directives.attach_synthetic(FORCE_GENERATE, True)
    assert list(base.directives) == [node]


def test_generated_crud_uses_owned_synthetic_nodes() -> None:
    schema = xtx.parse_schema(raw_schema='type Item @namespace("Domain") { name: String }')
    (item,) = xtx.get_children_of_object(schema)
    api = item.api
    assert api.directive.generate is None
    assert api.directive.namespace.value == "Domain"
    assert api.directive.namespace.parent is api
    assert api.directive.namespace.origin == "synthetic"
    assert item.directive.namespace.origin == "source"
    id_field, label = item.fields
    assert id_field.directive.is_read_only
    assert id_field.directives.get(READ_ONLY).origin == "synthetic"
    assert not label.directive.is_read_only

    expected = {
        "getItems": ("GET", "/items", True, None, "application/json"),
        "createItem": ("POST", "/items", False, "application/json", "application/json"),
        "getItem": ("GET", "/items/{id}", False, None, "application/json"),
        "updateItem": ("PATCH", "/items/{id}", False, "application/merge-patch+json", "application/json"),
        "deleteItem": ("DELETE", "/items/{id}", False, None, None),
    }
    assert set(expected) == {operation.name for operation in api.operations}
    for operation in api.operations:
        view = operation.directive
        assert (
            view.method.value,
            view.path.value,
            view.is_pageable,
            view.consumes.value if view.consumes else None,
            view.produces.value if view.produces else None,
        ) == expected[operation.name]
        for node in operation.directives:
            assert node.parent is operation
            assert node.origin == "synthetic" and node.location is None
            assert operation.directives.get(node.spec) is operation.directives.by_name(node.name) is node

    removed = (
        (item, ("namespace",)),
        (api, ("namespace", "namespace_is_explicit", "generate")),
        (id_field, ("is_read_only", "is_write_only", "is_relation", "default", "min_size", "max_size")),
        (api.operations[0], ("path", "method", "is_pageable", "consumes", "produces", "response_headers")),
        (dsl.Base(parent=schema, name="Payload"), ("namespace",)),
        (dsl.Enum(parent=schema, name="Status"), ("namespace",)),
    )
    for owner, attributes in removed:
        assert not any(hasattr(owner, attribute) for attribute in attributes)


def test_empty_source_values_are_not_replaced_by_defaults() -> None:
    schema = xtx.parse_schema(
        raw_schema="""
        type Item @namespace("Domain") {
            name: String
            extend api @namespace("") @generate() {
                update(name: String): String @path("update") @method(PATCH) @consumes("") @produces("")
                other(name: String): String @path("other") @method(PATCH)
            }
        }
    """
    )
    api = xtx.get_children_of_api(schema)[0]
    assert api.directive.generate.value == ()
    assert api.directive.namespace.origin == "source" and api.directive.namespace.value == ""
    update, other = api.operations
    for node in (update.directive.consumes, update.directive.produces):
        assert node.value == "" and node.origin == "source"
    assert other.directive.consumes.value == "application/json"
    assert other.directive.consumes.origin == "synthetic"
