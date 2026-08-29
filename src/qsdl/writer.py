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

"""Filesystem materialization for generated artifacts."""

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import pathspec

from qsdl import logger
from qsdl.artifacts import GeneratedFiles

log = logger.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class WriteReport:
    """Result of materializing generated artifacts."""

    written: tuple[PurePosixPath, ...]
    skipped: tuple[PurePosixPath, ...]


class IgnorePolicy:
    """A compiled output ignore policy."""

    def __init__(self, spec: pathspec.PathSpec | None = None) -> None:
        self._spec = spec

    @classmethod
    def from_directory(cls, root: Path) -> "IgnorePolicy":
        """Load the preferred ignore file from an output directory."""
        root = Path(root)
        for filename in (".qignore", ".qsdl-ignore"):
            ignore_path = root / filename
            if ignore_path.is_file():
                return cls.from_text(ignore_path.read_text(encoding="utf-8"))
        return cls()

    @classmethod
    def from_text(cls, patterns: str) -> "IgnorePolicy":
        """Build an ignore policy from pattern text."""
        if not isinstance(patterns, str):
            raise TypeError(f"ignore patterns must be str, got {patterns!r}")
        return cls(pathspec.PathSpec.from_lines("gitwildmatch", patterns.splitlines()))

    def matches(self, path: PurePosixPath) -> bool:
        """Return whether a logical artifact path matches the policy."""
        if not isinstance(path, PurePosixPath):
            raise TypeError(f"ignored path must be PurePosixPath, got {path!r}")
        return self._spec is not None and self._spec.match_file(path.as_posix())


class DirectoryWriter:
    """Materialize generated artifacts below a local directory."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def write(self, files: GeneratedFiles) -> WriteReport:
        """Write artifacts while applying the destination's ignore policy."""
        if not isinstance(files, GeneratedFiles):
            raise TypeError(f"can only write GeneratedFiles, got {files!r}")

        self.root.mkdir(parents=True, exist_ok=True)
        resolved_root = self.root.resolve(strict=False)
        ignore_policy = IgnorePolicy.from_directory(self.root)
        written: list[PurePosixPath] = []
        skipped: list[PurePosixPath] = []

        for artifact in files:
            path = artifact.path
            destination = self.root.joinpath(*path.parts)
            if ignore_policy.matches(path):
                log.info("skipping ignored file: %s", destination)
                skipped.append(path)
                continue

            if path in (PurePosixPath(".qignore"), PurePosixPath(".qsdl-ignore")) and destination.exists():
                log.info("skipping existing ignore file: %s", destination)
                skipped.append(path)
                continue

            resolved_destination = destination.resolve(strict=False)
            self._require_below_root(path, destination, resolved_destination, resolved_root)

            destination.parent.mkdir(parents=True, exist_ok=True)
            resolved_destination = destination.resolve(strict=False)
            self._require_below_root(path, destination, resolved_destination, resolved_root)

            log.info("writing file: %s", destination)
            if isinstance(artifact.content, str):
                destination.write_bytes(artifact.content.encode("utf-8"))
            else:
                destination.write_bytes(artifact.content)
            written.append(path)

        return WriteReport(tuple(written), tuple(skipped))

    @staticmethod
    def _require_below_root(
        path: PurePosixPath,
        destination: Path,
        resolved_destination: Path,
        resolved_root: Path,
    ) -> None:
        if not resolved_destination.is_relative_to(resolved_root):
            raise ValueError(
                f"artifact path escapes writer root: {path.as_posix()!r} -> "
                f"{destination!s} resolves outside {resolved_root!s}"
            )
