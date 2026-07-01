from pathlib import Path

from scad_export.export_config import (
    _is_directory,
    _is_directory_writable,
    _is_file_with_extension,
)


class TestIsDirectory:
    def test_real_directory_passes(self, tmp_path):
        assert _is_directory(str(tmp_path))

    def test_nonexistent_path_fails(self, tmp_path):
        # Regression: must actually call is_dir(), not reference the method.
        assert not _is_directory(str(tmp_path / 'does_not_exist'))

    def test_file_is_not_a_directory(self, tmp_path):
        f = tmp_path / 'a.txt'
        f.write_text('x')
        assert not _is_directory(str(f))

    def test_empty_string_fails(self):
        assert not _is_directory('')


class TestIsDirectoryWritable:
    def test_writable_directory_passes(self, tmp_path):
        assert _is_directory_writable(str(tmp_path))

    def test_nonexistent_fails(self, tmp_path):
        assert not _is_directory_writable(str(tmp_path / 'nope'))


class TestIsFileWithExtension:
    def test_matching_extension_passes(self, tmp_path):
        f = tmp_path / 'map.scad'
        f.write_text('')
        assert _is_file_with_extension(str(f), '.scad')

    def test_accepts_path_object(self, tmp_path):
        f = tmp_path / 'map.scad'
        f.write_text('')
        assert _is_file_with_extension(Path(f), '.scad')

    def test_string_input_does_not_raise(self, tmp_path):
        # Regression: previously str input hit str.exists() -> AttributeError.
        f = tmp_path / 'map.scad'
        f.write_text('')
        assert _is_file_with_extension(str(f), '.scad')

    def test_wrong_extension_fails(self, tmp_path):
        # Regression: extension was never actually validated.
        f = tmp_path / 'notes.txt'
        f.write_text('')
        assert not _is_file_with_extension(str(f), '.scad')

    def test_missing_file_fails(self, tmp_path):
        assert not _is_file_with_extension(str(tmp_path / 'missing.scad'), '.scad')
