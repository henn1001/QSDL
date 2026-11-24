"""Structured diagnostics and error policies for QSDL analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from textx import get_model
from textx.exceptions import TextXSemanticError

if TYPE_CHECKING:
    from qsdl import dsl


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A schema issue with an optional one-based start and character span."""

    code: str
    message: str
    filename: Path | None = None
    line: int | None = None
    column: int | None = None
    length: int | None = None
    severity: Literal["error"] = "error"


class SchemaValidationError(TextXSemanticError):
    """A rejected schema with all diagnostics and the first issue's textX location."""

    def __init__(self, diagnostics: tuple[Diagnostic, ...]) -> None:
        self.diagnostics = diagnostics
        first = diagnostics[0]
        super().__init__(
            first.message,
            filename=str(first.filename) if first.filename else None,
            line=first.line,
            col=first.column,
            nchar=first.length,
        )


class Reporter:
    """Apply the strict or collecting policy for a single schema load."""

    def __init__(self, *, collecting: bool = False) -> None:
        self.collecting = collecting
        self.diagnostics: list[Diagnostic] = []
        self.namespace_complete = True
        self.ambiguous_types: set[str] = set()
        self.unavailable_fields: set[int] = set()
        self.invalid_nodes: set[int] = set()

    def reference_available(self, name: str) -> bool:
        """Whether a linked reference can be used as an unambiguous type."""
        return self.namespace_complete and name not in self.ambiguous_types

    def type_available(self, value: dsl.Scalar | dsl.Enum | dsl.Base | dsl.Object) -> bool:
        """Whether a type declaration and its effective field set are usable."""
        return (
            self.reference_available(value.name)
            and id(value) not in self.invalid_nodes
            and id(value) not in self.unavailable_fields
            and not value.directives.is_invalid()
        )

    def error(
        self,
        code: str,
        message: str,
        *,
        filename: str | Path | None = None,
        line: int | None = None,
        col: int | None = None,
        nchar: int | None = None,
        cause: Exception | None = None,
        invalid: object | None = None,
    ) -> None:
        """Report an error with the same location semantics as textX."""
        if not self.collecting:
            error = TextXSemanticError(message, filename=filename, line=line, col=col, nchar=nchar)
            if cause is not None:
                raise error from cause
            raise error
        if invalid is not None:
            self.invalid_nodes.add(id(invalid))
        self.diagnostics.append(Diagnostic(code, message, Path(filename) if filename else None, line, col, nchar))


def reporter_for(node: object) -> Reporter:
    """Get the policy shared by the root model and its imports."""
    params = get_model(node)._tx_model_params
    return params.get("reporter") or Reporter()
