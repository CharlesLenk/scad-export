from scad_export.exportable import (
    ColorScheme,
    Drawing,
    Exportable,
    Folder,
    Image,
    ImageSize,
    Model,
    ModelFormat,
)


class TestFolder:
    def test_flattens_nested_lists(self):
        folder = Folder('root', [[Model('a'), Model('b')], Model('c')])
        assert [item.name for item in folder.contents] == ['a', 'b', 'c']

    def test_deeply_nested_lists(self):
        folder = Folder('root', [[[Model('a')], Model('b')]])
        assert [item.name for item in folder.contents] == ['a', 'b']

    def test_preserves_nested_folders_as_single_items(self):
        inner = Folder('inner', [Model('a')])
        outer = Folder('outer', [inner, Model('b')])
        assert outer.contents[0] is inner
        assert outer.contents[1].name == 'b'

    def test_single_item(self):
        folder = Folder('root', Model('a'))
        assert folder.contents[0].name == 'a'


class TestExportable:
    def test_file_name_defaults_to_name(self):
        e = Exportable('widget', '.stl')
        assert e.file_name == 'widget'

    def test_explicit_file_name_is_kept(self):
        e = Exportable('widget', '.stl', file_name='custom')
        assert e.file_name == 'custom'

    def test_kwargs_become_user_args(self):
        e = Exportable('widget', '.stl', x=1, y=2)
        assert e.user_args == {'x': 1, 'y': 2}

    def test_no_kwargs_is_empty_dict(self):
        assert Exportable('widget', '.stl').user_args == {}

    def test_default_quantity(self):
        assert Exportable('widget', '.stl').quantity == 1


class TestModel:
    def test_format_sets_file_format(self):
        assert Model('m', format=ModelFormat.STL).file_format == '.stl'

    def test_no_format_is_empty(self):
        assert Model('m').file_format == ''

    def test_quantity_and_user_args(self):
        m = Model('m', quantity=3, depth=5)
        assert m.quantity == 3
        assert m.user_args == {'depth': 5}


class TestDrawing:
    def test_format_is_dxf(self):
        assert Drawing('d').file_format == '.dxf'


class TestImage:
    def test_format_is_png(self):
        img = Image('i', camera_position='0,0,0,0,0,0,0')
        assert img.file_format == '.png'

    def test_attributes_and_user_args(self):
        size = ImageSize(500, 500)
        img = Image(
            'i',
            camera_position='0,-2,1,51,0,128,154',
            image_size=size,
            color_scheme=ColorScheme.TOMORROW_NIGHT,
            d=10,
        )
        assert img.camera_position == '0,-2,1,51,0,128,154'
        assert img.image_size is size
        assert img.color_scheme is ColorScheme.TOMORROW_NIGHT
        assert img.user_args == {'d': 10}


class TestEnums:
    def test_model_format_values(self):
        assert ModelFormat.STL == '.stl'
        assert ModelFormat._3MF == '.3mf'

    def test_color_scheme_is_str(self):
        assert ColorScheme.CORNFIELD == 'Cornfield'
        assert f'{ColorScheme.DAYLIGHT_GEM}' == 'Daylight Gem'
