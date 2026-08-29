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

"""In-memory representations of generated files."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import PurePosixPath

type FileContent = str | bytes


def _artifact_path(value: str | PurePosixPath) -> PurePosixPath:
    """Validate and normalize a logical artifact path."""
    if not isinstance(value, (str, PurePosixPath)):
        raise TypeError(f"artifact path must be str or PurePosixPath, got {value!r}")

    if value == "":
        raise ValueError(f"artifact path cannot be empty: {value!r}")

    raw_value = value if isinstance(value, str) else value.as_posix()
    if "\\" in raw_value:
        raise ValueError(f"artifact path must use POSIX separators: {value!r}")

    path = PurePosixPath(value)
    if path.is_absolute():
        raise ValueError(f"artifact path must be relative: {value!r}")
    if path == PurePosixPath("."):
        raise ValueError(f"artifact path cannot be empty or '.': {value!r}")
    if ".." in path.parts:
        raise ValueError(f"artifact path cannot contain '..': {value!r}")

    return path


def _file_content(value: object) -> FileContent:
    """Validate generated file content without coercing it."""
    if not isinstance(value, (str, bytes)):
        raise TypeError(f"generated file content must be str or bytes, got {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class GeneratedFile:
    """One generated file with a logical path and its content."""

    path: PurePosixPath
    content: FileContent

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", _artifact_path(self.path))
        object.__setattr__(self, "content", _file_content(self.content))


class GeneratedFiles:
    """A mutable, deterministically ordered collection of generated files."""

    def __init__(self, files: Iterable[GeneratedFile] | None = None) -> None:
        self._files: dict[PurePosixPath, GeneratedFile] = {}
        if files is not None:
            for artifact in files:
                if not isinstance(artifact, GeneratedFile):
                    raise TypeError(f"generated files must contain GeneratedFile values, got {artifact!r}")
                self.add(artifact.path, artifact.content)

    def add(self, path: str | PurePosixPath, content: FileContent) -> None:
        """Add an artifact, rejecting duplicate paths."""
        artifact = GeneratedFile(_artifact_path(path), _file_content(content))
        if artifact.path in self._files:
            raise ValueError(f"duplicate generated artifact path: {artifact.path.as_posix()!r}")
        self._files[artifact.path] = artifact

    def add_text(self, path: str | PurePosixPath, content: str) -> None:
        """Add a text artifact."""
        if not isinstance(content, str):
            raise TypeError(f"text artifact content must be str, got {content!r}")
        self.add(path, content)

    def add_bytes(self, path: str | PurePosixPath, content: bytes) -> None:
        """Add a binary artifact."""
        if not isinstance(content, bytes):
            raise TypeError(f"binary artifact content must be bytes, got {content!r}")
        self.add(path, content)

    def replace(self, path: str | PurePosixPath, content: FileContent) -> None:
        """Replace an existing artifact explicitly."""
        artifact_path = _artifact_path(path)
        if artifact_path not in self._files:
            raise KeyError(artifact_path)
        self._files[artifact_path] = GeneratedFile(artifact_path, _file_content(content))

    def text(self, path: str | PurePosixPath) -> str:
        """Return text content for an artifact."""
        artifact = self._files[_artifact_path(path)]
        if not isinstance(artifact.content, str):
            raise TypeError(f"artifact content is binary: {artifact.path.as_posix()!r}")
        return artifact.content

    def bytes(self, path: str | PurePosixPath) -> bytes:
        """Return binary content for an artifact."""
        artifact = self._files[_artifact_path(path)]
        if not isinstance(artifact.content, bytes):
            raise TypeError(f"artifact content is text: {artifact.path.as_posix()!r}")
        return artifact.content

    def exists(self, path: str | PurePosixPath) -> bool:
        """Return whether an artifact path is present."""
        return _artifact_path(path) in self._files

    def paths(self) -> tuple[PurePosixPath, ...]:
        """Return artifact paths in deterministic order."""
        return tuple(sorted(self._files, key=lambda path: path.as_posix()))

    def extend(self, other: "GeneratedFiles", *, prefix: str | PurePosixPath = ".") -> None:
        """Add another collection under an optional logical path prefix."""
        if not isinstance(other, GeneratedFiles):
            raise TypeError(f"can only extend with GeneratedFiles, got {other!r}")

        prefix_path = _prefix_path(prefix)
        staged: list[GeneratedFile] = []
        staged_paths: set[PurePosixPath] = set()

        for artifact in other:
            artifact_path = _artifact_path(artifact.path)
            result_path = artifact_path if prefix_path == PurePosixPath(".") else prefix_path / artifact_path
            staged_artifact = GeneratedFile(result_path, artifact.content)
            if staged_artifact.path in self._files or staged_artifact.path in staged_paths:
                raise ValueError(f"duplicate generated artifact path: {staged_artifact.path.as_posix()!r}")
            staged.append(staged_artifact)
            staged_paths.add(staged_artifact.path)

        for artifact in staged:
            self._files[artifact.path] = artifact

    def __iter__(self) -> Iterator[GeneratedFile]:
        """Iterate over artifacts in deterministic order."""
        for path in self.paths():
            yield self._files[path]

    def __len__(self) -> int:
        return len(self._files)


def _prefix_path(value: str | PurePosixPath) -> PurePosixPath:
    """Validate an extension prefix, allowing the explicit no-prefix value."""
    if (isinstance(value, str) and value == ".") or (isinstance(value, PurePosixPath) and value == PurePosixPath(".")):
        return PurePosixPath(".")
    return _artifact_path(value)
