import pytest

from scad_export.export import (
    _flatten_paths,
    _format_name,
    _format_part_name,
    _format_path_name,
    _get_exportable_args,
)
from scad_export.export_config import NamingFormat
from scad_export.exportable import Folder, Image, ImageSize, Model


class FakeConfig:
    """Minimal stand-in for ExportConfig for arg-building tests."""
    openscad_location = 'openscad'
    export_file_path = 'map.scad'
    manifold_supported = False
    default_image_color_scheme = 'Cornfield'
    default_image_size = ImageSize(800, 600)
    default_model_format = '.3mf'
    output_naming_format = NamingFormat.NONE
    export_timeout = None


class TestFormatName:
    def test_none_is_unchanged(self):
        assert _format_name('my_Widget Name', NamingFormat.NONE) == 'my_Widget Name'

    def test_title_case(self):
        assert _format_name('my_widget_part', NamingFormat.TITLE_CASE) == 'My Widget Part'

    def test_snake_case(self):
        assert _format_name('My Widget Part', NamingFormat.SNAKE_CASE) == 'my_widget_part'


class TestFormatPathName:
    def test_each_segment_formatted(self):
        assert _format_path_name('/parent_folder/child', NamingFormat.TITLE_CASE) == '/Parent Folder/Child'

    def test_snake_case_path(self):
        assert _format_path_name('/Parent Folder/Child', NamingFormat.SNAKE_CASE) == '/parent_folder/child'


class TestFormatPartName:
    def test_plain_name_none_format(self):
        assert _format_part_name('widget', NamingFormat.NONE, '.stl', {}) == 'widget.stl'

    def test_user_args_interpolated_snake(self):
        assert _format_part_name('widget', NamingFormat.SNAKE_CASE, '.stl', {'size': 10}) == 'widget_(size-10).stl'

    def test_user_args_interpolated_title(self):
        assert _format_part_name('widget', NamingFormat.TITLE_CASE, '.stl', {'size': 10}) == 'Widget (size-10).stl'

    def test_count_suffix_added_when_greater_than_one(self):
        assert _format_part_name('widget', NamingFormat.SNAKE_CASE, '.stl', {'size': 10}, count=3) == 'widget_(size-10)_3.stl'

    def test_count_one_has_no_suffix(self):
        assert _format_part_name('widget', NamingFormat.SNAKE_CASE, '.stl', {}, count=1) == 'widget.stl'

    def test_none_format_ignores_user_args(self):
        # With NONE formatting, user args are not appended to the name.
        assert _format_part_name('widget', NamingFormat.NONE, '.stl', {'size': 10}) == 'widget.stl'


class TestFlattenPaths:
    def test_top_level_exportable(self):
        result = _flatten_paths(Folder('top', [Model('a')]))
        assert {k: [m.name for m in v] for k, v in result.items()} == {'/top': ['a']}

    def test_nested_folders_build_paths(self):
        tree = Folder('top', [Model('a'), Folder('sub', [Model('b'), Model('c')])])
        result = _flatten_paths(tree)
        assert {k: [m.name for m in v] for k, v in result.items()} == {
            '/top': ['a'],
            '/top/sub': ['b', 'c'],
        }

    def test_multiple_exportables_same_path(self):
        tree = Folder('top', [Model('a'), Model('b')])
        result = _flatten_paths(tree)
        assert [m.name for m in result['/top']] == ['a', 'b']


class TestGetExportableArgs:
    def test_basic_model_args(self):
        args = _get_exportable_args(Model('part'), FakeConfig())
        assert args[0] == 'openscad'
        assert args[1] == 'map.scad'
        assert '-Dname="part"' in args
        assert '--backend=Manifold' not in args

    def test_manifold_backend_added(self):
        cfg = FakeConfig()
        cfg.manifold_supported = True
        args = _get_exportable_args(Model('part'), cfg)
        assert '--backend=Manifold' in args

    def test_bool_args_render_as_openscad_literals(self):
        args = _get_exportable_args(Model('part', on=True, off=False), FakeConfig())
        assert '-Don=true' in args
        assert '-Doff=false' in args

    def test_numeric_and_string_args(self):
        args = _get_exportable_args(Model('part', n=5, label='hi'), FakeConfig())
        assert '-Dn=5' in args
        assert '-Dlabel="hi"' in args

    def test_image_args_with_defaults(self):
        img = Image('pic', camera_position='0,-2,1,51,0,128,154')
        args = _get_exportable_args(img, FakeConfig())
        assert '--camera=0,-2,1,51,0,128,154' in args
        assert '--colorscheme=Cornfield' in args
        assert '--imgsize=800,600' in args
        # Non-manifold image gets the smoothing defines instead of --render
        assert '-D$fs=0.4' in args
        assert '-D$fa=0.8' in args
        assert '--render=true' not in args

    def test_image_args_with_overrides_and_manifold(self):
        cfg = FakeConfig()
        cfg.manifold_supported = True
        img = Image('pic', camera_position='0,0,0,0,0,0,0', image_size=ImageSize(200, 100), color_scheme='Sunset')
        args = _get_exportable_args(img, cfg)
        assert '--colorscheme=Sunset' in args
        assert '--imgsize=200,100' in args
        assert '--render=true' in args
        assert '-D$fs=0.4' not in args


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, '-v']))
