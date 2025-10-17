from enum import StrEnum


class ModelFormat(StrEnum):
    _3MF = '.3mf'
    STL = '.stl'

class ColorScheme(StrEnum):
    CORNFIELD = 'Cornfield'
    METALLIC  = 'Metallic'
    SUNSET = 'Sunset'
    STARNIGHT = 'Starnight'
    BEFORE_DAWN = 'BeforeDawn'
    NATURE = 'Nature'
    DAYLIGHT_GEM = 'Daylight Gem'
    NOCTURNAL_GEM = 'Nocturnal Gem'
    DEEP_OCEAN = 'DeepOcean'
    SOLARIZED = 'Solarized'
    TOMORROW = 'Tomorrow'
    TOMORROW_NIGHT = 'Tomorrow Night'
    CLEAR_SKY = 'ClearSky'
    MONOTONE = 'Monotone'

class ImageSize():
    def __init__(self, width = 1600, height = 900):
        self.width = width
        self.height = height

class Folder():
    def __init__(self, name, contents):
        self.name = name
        self.contents = contents

class Exportable():
    def __init__(self, name, output_format, file_name = None, quantity = 1, **kwargs):
        self.name = name
        self.file_name = file_name if file_name else name
        self.output_format = output_format
        self.quantity = quantity
        self.user_args = kwargs if kwargs else {}
        self.user_args['name'] = name

class Model(Exportable):
    def __init__(self, name, file_name = None, quantity = 1, format: ModelFormat = None, **kwargs):
        self.quantity = quantity
        super().__init__(name, format.value if format else '', file_name, quantity, **kwargs)

class Drawing(Exportable):
    def __init__(self, name, file_name = None, quantity = 1, **kwargs):
        self.quantity = quantity
        super().__init__(name, '.dxf', file_name, quantity, **kwargs)

class Image(Exportable):
    def __init__(self, name, camera_position, file_name = None, image_size: ImageSize = None, color_scheme = None, **kwargs):
        self.name = name
        self.image_size = image_size
        self.color_scheme = color_scheme
        self.camera_position = camera_position
        super().__init__(name = name, output_format = '.png', file_name = file_name, **kwargs)
