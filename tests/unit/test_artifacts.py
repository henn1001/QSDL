from pathlib import PurePosixPath

import pytest

from qsdl.artifacts import GeneratedFile, GeneratedFiles


@pytest.mark.parametrize(
    "path",
    ["", ".", "/absolute.txt", "nested/../file.txt", "nested\\file.txt"],
)
def test_artifact_paths_reject_unsafe_values(path: str) -> None:
    files = GeneratedFiles()

    with pytest.raises((TypeError, ValueError)):
        files.add(path, "content")


def test_artifact_paths_accept_root_and_nested_posix_files() -> None:
    files = GeneratedFiles()

    files.add_text("openapi.yaml", "openapi")
    files.add_bytes(PurePosixPath("nested/output.bin"), b"binary")

    assert files.paths() == (PurePosixPath("nested/output.bin"), PurePosixPath("openapi.yaml"))


def test_text_and_bytes_accessors_round_trip_and_enforce_content_type() -> None:
    files = GeneratedFiles()
    files.add_text("text.txt", "héllo")
    files.add_bytes("image.png", b"\x89PNG")

    assert files.text("text.txt") == "héllo"
    assert files.bytes("image.png") == b"\x89PNG"

    with pytest.raises(TypeError):
        files.bytes("text.txt")
    with pytest.raises(TypeError):
        files.text("image.png")
    with pytest.raises(KeyError):
        files.text("missing.txt")


def test_duplicate_add_fails_and_replace_is_explicit() -> None:
    files = GeneratedFiles()
    files.add_text("value.txt", "before")

    with pytest.raises(ValueError, match="duplicate"):
        files.add_text("value.txt", "duplicate")
    with pytest.raises(KeyError):
        files.replace("missing.txt", "value")

    files.replace("value.txt", "after")
    assert files.text("value.txt") == "after"


def test_extend_prefixes_paths_and_rejects_collisions_without_partial_changes() -> None:
    files = GeneratedFiles()
    files.add_text("root.txt", "root")

    child = GeneratedFiles()
    child.add_text("one.txt", "one")
    child.add_bytes("nested/two.bin", b"two")
    files.extend(child, prefix="child")

    assert files.paths() == (
        PurePosixPath("child/nested/two.bin"),
        PurePosixPath("child/one.txt"),
        PurePosixPath("root.txt"),
    )

    receiver = GeneratedFiles()
    receiver.add_text("nested/existing.txt", "original")
    collision = GeneratedFiles()
    collision.add_text("existing.txt", "replacement")
    collision.add_text("new.txt", "new")

    with pytest.raises(ValueError, match="duplicate"):
        receiver.extend(collision, prefix="nested")

    assert receiver.paths() == (PurePosixPath("nested/existing.txt"),)
    assert receiver.text("nested/existing.txt") == "original"


def test_iteration_is_sorted_by_logical_path() -> None:
    files = GeneratedFiles()
    files.add_text("z.txt", "z")
    files.add_text("a.txt", "a")
    files.add_text("nested/b.txt", "b")

    assert [artifact.path for artifact in files] == [
        PurePosixPath("a.txt"),
        PurePosixPath("nested/b.txt"),
        PurePosixPath("z.txt"),
    ]
    assert len(files) == 3


def test_generated_file_validates_its_content_and_path() -> None:
    assert GeneratedFile(PurePosixPath("value.txt"), "value").content == "value"

    with pytest.raises(TypeError):
        GeneratedFile(PurePosixPath("value.txt"), object())
    with pytest.raises(ValueError):
        GeneratedFile(PurePosixPath("../value.txt"), "value")
