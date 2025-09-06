from numbers import Number
from enum import StrEnum

class ModelFormat(StrEnum):
    _3MF = '.3mf'
    STL = '.stl'

class Folder:
    def __init__(self, name, contents):
        self.name = name
        self.contents = contents

class Exportable():
    def __init__(self, name, output_format, file_name = None, quantity = 1, args = None):
        self.name = name
        self.file_name = file_name if file_name else name
        self.output_format = output_format
        self.quantity = quantity
        self.args = args if args else {}
        self.args['part'] = name

    def get_output_format(self):
        return self.output_format
    
    def get_quantity(self):
        return self.quantity

    def get_args(self):
        formatted_args = []
        for arg, value in self.args.items():
            if isinstance(value, Number):
                formatted_args.append('-D' + arg + '=' + str(value))
            elif isinstance(value, str):
                formatted_args.append('-D' + arg + '="' + value + '"')
        return formatted_args

class Model(Exportable):
    def __init__(self, name, file_name = None, quantity = 1, args = None, format: ModelFormat = ModelFormat._3MF):
        self.quantity = quantity
        super().__init__(name, format.value, file_name, quantity, args)

class Drawing(Exportable):
    def __init__(self, name, file_name = None, quantity = 1, args = None):
        self.quantity = quantity
        super().__init__(name, '.dxf', file_name, quantity, args)

class Image(Exportable):
    def __init__(self, name, camera_position, width = 1600, height = 900, file_name = None, args = None):
        self.name = name
        self.width = width
        self.height = height
        self.camera_position = camera_position
        super().__init__(name = name, output_format = '.png', file_name = file_name, args = args)

    def get_args(self):
        formatted_args = super().get_args()
        formatted_args += [
            '--camera=' + self.camera_position,
            '--imgsize={},{}'.format(self.width, self.height)
        ]
        return formatted_args
