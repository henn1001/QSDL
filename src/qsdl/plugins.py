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

"""Resolve builtin and custom :class:`qsdl.generators.Generator` plugins."""

import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import fields
from enum import Enum
from pathlib import Path
from types import ModuleType, UnionType
from typing import Annotated, Any, Literal, Union, get_args, get_origin, get_type_hints

from qsdl.exceptions import QsdlException
from qsdl.generators import GENERATORS, Generator, GeneratorDefinition, available_generators

_CUSTOM_MODULE_PREFIX = "qsdl_custom_"
# Custom modules remain loaded for the process lifetime. Repeated resolution of
# the same resolved path returns this cached definition rather than re-executing it.
_CUSTOM_GENERATORS: dict[Path, GeneratorDefinition] = {}


def _definition_from_module(module: ModuleType, *, source: str) -> GeneratorDefinition:
    """Read the one explicit plugin export from a loaded module."""
    plugin = getattr(module, "generator", None)
    if not isinstance(plugin, Generator):
        raise QsdlException(f"custom generator {source} must export generator: Generator")
    try:
        return GeneratorDefinition(plugin)
    except TypeError as error:
        raise QsdlException(f"custom generator {source} has an invalid contract: {error}") from error


def _module_name(entry: Path) -> str:
    """Return a valid and path-unique module name."""
    digest = hashlib.sha256(str(entry).encode()).hexdigest()[:16]
    stem = re.sub(r"\W", "_", entry.stem)
    return f"{_CUSTOM_MODULE_PREFIX}{stem}_{digest}"


def _load_module(entry: Path, *, source: str) -> GeneratorDefinition:
    """Import a custom module once from an absolute path without sys.path changes."""
    entry = entry.resolve()
    if cached := _CUSTOM_GENERATORS.get(entry):
        return cached

    safe_name = _module_name(entry)
    package_locations = [str(entry.parent)] if entry.name == "__init__.py" else None
    spec = importlib.util.spec_from_file_location(safe_name, entry, submodule_search_locations=package_locations)
    if spec is None or spec.loader is None:
        raise QsdlException(f"custom generator {source} could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[safe_name] = module
    try:
        spec.loader.exec_module(module)
        definition = _definition_from_module(module, source=source)
    except Exception as error:
        sys.modules.pop(safe_name, None)
        if isinstance(error, QsdlException):
            raise
        raise QsdlException(f"custom generator {source} failed to import: {error}") from error
    _CUSTOM_GENERATORS[entry] = definition
    return definition


def load_file(path: Path) -> tuple[str, GeneratorDefinition]:
    """Load a custom generator from a single ``.py`` file."""
    name = path.stem
    if name in GENERATORS:
        raise QsdlException(f"custom generator {path} shadows builtin generator {name!r}")
    return name, _load_module(path, source=str(path))


def load_package(path: Path) -> tuple[str, GeneratorDefinition]:
    """Load a custom generator from a package directory."""
    entry = path / "__init__.py"
    if not entry.is_file():
        raise QsdlException(f"custom generator {path} is a directory without __init__.py")
    name = path.name
    if name in GENERATORS:
        raise QsdlException(f"custom generator {path} shadows builtin generator {name!r}")
    return name, _load_module(entry, source=str(path))


def _suggest(ref: str) -> str:
    options = ", ".join(available_generators())
    return f"unknown generator {ref!r}; available generators: {options}"


def resolve(ref: str) -> tuple[str, GeneratorDefinition]:
    """Resolve a builtin name or custom generator path."""
    candidate = Path(ref)
    looks_like_path = (
        candidate.suffix == ".py" or "/" in ref or "\\" in ref or candidate.name != ref or candidate.exists()
    )
    if looks_like_path:
        if not candidate.exists():
            raise QsdlException(f"generator path {ref!r} does not exist")
        if candidate.is_file():
            if candidate.suffix != ".py":
                raise QsdlException(f"generator path {ref!r} is not a .py file or package directory")
            return load_file(candidate)
        return load_package(candidate)
    if ref not in GENERATORS:
        raise QsdlException(_suggest(ref))
    return ref, GENERATORS[ref]


def describe_config_fields(definition: GeneratorDefinition) -> tuple[str, ...]:
    """Return the overridable config field names for error messages."""
    return tuple(f.name for f in fields(definition.config_class) if not f.name.startswith("_"))


def _coerce_scalar(field_type: object, key: str, value: str) -> object:
    if field_type is str or field_type is Any:
        return value
    if field_type is bool:
        normalized = value.strip().lower()
        if normalized in ("true", "1", "yes", "on"):
            return True
        if normalized in ("false", "0", "no", "off"):
            return False
        raise QsdlException(f"invalid value for {key!r}: {value!r} is not a boolean")
    if isinstance(field_type, type) and issubclass(field_type, Enum):
        try:
            return field_type(value)
        except ValueError:
            try:
                return field_type[value]
            except KeyError:
                members = ", ".join(field_type.__members__)
                raise QsdlException(f"invalid value for {key!r}: {value!r}; expected one of: {members}") from None
    if field_type is int:
        try:
            return int(value)
        except ValueError:
            raise QsdlException(f"invalid value for {key!r}: {value!r} is not an integer") from None
    if field_type is float:
        try:
            return float(value)
        except ValueError:
            raise QsdlException(f"invalid value for {key!r}: {value!r} is not a number") from None
    return value


def coerce_override(field_type: object, key: str, value: str) -> object:
    """Coerce CLI values for scalars, unions, literals, and JSON containers.

    ``--set`` uses normal scalar spelling. Lists, mappings, and tuples use a
    JSON value; unsupported annotations remain strings and dacite validates them.
    """
    origin = get_origin(field_type)
    args = get_args(field_type)
    if origin is Annotated:
        return coerce_override(args[0], key, value)
    if origin in (Union, UnionType):
        if type(None) in args and value.strip().lower() in ("none", "null"):
            return None
        errors: list[QsdlException] = []
        for member in args:
            if member is type(None):
                continue
            try:
                return coerce_override(member, key, value)
            except QsdlException as error:
                errors.append(error)
        if errors:
            raise errors[0]
        return value
    if origin is Literal:
        for literal in args:
            if coerce_override(type(literal), key, value) == literal:
                return literal
        expected = ", ".join(repr(item) for item in args)
        raise QsdlException(f"invalid value for {key!r}: {value!r}; expected one of: {expected}")
    if origin in (list, set, frozenset, tuple, dict):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise QsdlException(f"invalid value for {key!r}: {value!r} is not JSON") from None
    return _coerce_scalar(field_type, key, value)


def parse_set_args(entries: tuple[str, ...] | list[str]) -> dict[str, str]:
    """Parse repeatable ``KEY=VALUE`` overrides; last duplicate wins."""
    overrides: dict[str, str] = {}
    for entry in entries:
        key, separator, value = entry.partition("=")
        key = key.strip()
        if not separator or not key:
            raise QsdlException(f"invalid --set {entry!r}; expected KEY=VALUE")
        overrides[key] = value
    return overrides


def apply_overrides(definition: GeneratorDefinition, raw: dict[str, object]) -> dict[str, object]:
    """Validate keys and coerce string overrides using resolved annotations."""
    field_types = get_type_hints(definition.config_class)
    valid = tuple(name for name in field_types if not name.startswith("_"))
    coerced: dict[str, object] = {}
    for key, value in raw.items():
        if key not in field_types or key.startswith("_"):
            raise QsdlException(f"unknown config key {key!r}; valid keys: {', '.join(valid)}")
        coerced[key] = coerce_override(field_types[key], key, value) if isinstance(value, str) else value
    return coerced
