from pathlib import Path, PurePosixPath

import pytest

from qsdl.artifacts import GeneratedFiles
from qsdl.writer import DirectoryWriter


def test_writer_creates_parents_and_preserves_exact_text_and_bytes(tmp_path: Path) -> None:
    files = GeneratedFiles()
    files.add_text("nested/text.txt", "héllo\n")
    files.add_bytes("nested/data.bin", b"\x00\xff\x01")

    report = DirectoryWriter(tmp_path).write(files)

    assert report.written == (PurePosixPath("nested/data.bin"), PurePosixPath("nested/text.txt"))
    assert report.skipped == ()
    assert (tmp_path / "nested/text.txt").read_bytes() == "héllo\n".encode("utf-8")
    assert (tmp_path / "nested/data.bin").read_bytes() == b"\x00\xff\x01"


def test_writer_leaves_unrelated_stale_files_untouched(tmp_path: Path) -> None:
    stale = tmp_path / "stale.txt"
    stale.write_text("keep", encoding="utf-8")

    files = GeneratedFiles()
    files.add_text("new.txt", "new")
    DirectoryWriter(tmp_path).write(files)

    assert stale.read_text(encoding="utf-8") == "keep"


def test_writer_applies_qignore_to_relative_posix_paths(tmp_path: Path) -> None:
    (tmp_path / ".qignore").write_text("src/**/ignored.java\n*.tmp\n", encoding="utf-8")
    files = GeneratedFiles()
    files.add_text("src/main/ignored.java", "ignored")
    files.add_text("src/main/kept.java", "kept")
    files.add_text("notes.tmp", "ignored")

    report = DirectoryWriter(tmp_path).write(files)

    assert report.written == (PurePosixPath("src/main/kept.java"),)
    assert report.skipped == (PurePosixPath("notes.tmp"), PurePosixPath("src/main/ignored.java"))
    assert not (tmp_path / "src/main/ignored.java").exists()


def test_writer_uses_legacy_ignore_file_when_preferred_file_is_absent(tmp_path: Path) -> None:
    (tmp_path / ".qsdl-ignore").write_text("ignored.txt\n", encoding="utf-8")
    files = GeneratedFiles()
    files.add_text("ignored.txt", "ignored")
    files.add_text("kept.txt", "kept")

    report = DirectoryWriter(tmp_path).write(files)

    assert report.written == (PurePosixPath("kept.txt"),)
    assert report.skipped == (PurePosixPath("ignored.txt"),)


def test_writer_prefers_qignore_when_both_ignore_files_exist(tmp_path: Path) -> None:
    (tmp_path / ".qignore").write_text("ignored.txt\n", encoding="utf-8")
    (tmp_path / ".qsdl-ignore").write_text("kept.txt\n", encoding="utf-8")
    files = GeneratedFiles()
    files.add_text("ignored.txt", "ignored")
    files.add_text("kept.txt", "kept")

    report = DirectoryWriter(tmp_path).write(files)

    assert report.written == (PurePosixPath("kept.txt"),)
    assert report.skipped == (PurePosixPath("ignored.txt"),)


def test_generated_qignore_is_not_used_to_filter_the_same_batch(tmp_path: Path) -> None:
    files = GeneratedFiles()
    files.add_text(".qignore", "sibling.txt\n")
    files.add_text("sibling.txt", "written")

    report = DirectoryWriter(tmp_path).write(files)

    assert report.written == (PurePosixPath(".qignore"), PurePosixPath("sibling.txt"))
    assert (tmp_path / "sibling.txt").read_text(encoding="utf-8") == "written"


def test_existing_ignore_files_are_not_overwritten(tmp_path: Path) -> None:
    qignore = tmp_path / ".qignore"
    legacy = tmp_path / ".qsdl-ignore"
    qignore.write_text("existing qignore", encoding="utf-8")
    legacy.write_text("existing legacy", encoding="utf-8")
    files = GeneratedFiles()
    files.add_text(".qignore", "new qignore")
    files.add_text(".qsdl-ignore", "new legacy")

    report = DirectoryWriter(tmp_path).write(files)

    assert report.written == ()
    assert report.skipped == (PurePosixPath(".qignore"), PurePosixPath(".qsdl-ignore"))
    assert qignore.read_text(encoding="utf-8") == "existing qignore"
    assert legacy.read_text(encoding="utf-8") == "existing legacy"


def test_ignore_policy_is_reloaded_for_each_write(tmp_path: Path) -> None:
    ignore_file = tmp_path / ".qignore"
    ignore_file.write_text("value.txt\n", encoding="utf-8")
    files = GeneratedFiles()
    files.add_text("value.txt", "value")

    first = DirectoryWriter(tmp_path).write(files)
    ignore_file.write_text("", encoding="utf-8")
    second = DirectoryWriter(tmp_path).write(files)

    assert first.skipped == (PurePosixPath("value.txt"),)
    assert second.written == (PurePosixPath("value.txt"),)


def test_writer_rejects_a_parent_symlink_that_escapes_root(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "root"
    root.mkdir()
    link = root / "escape"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks are not available on this platform")

    files = GeneratedFiles()
    files.add_text("escape/file.txt", "must not be written")

    with pytest.raises(ValueError, match="escapes writer root"):
        DirectoryWriter(root).write(files)

    assert not (outside / "file.txt").exists()
