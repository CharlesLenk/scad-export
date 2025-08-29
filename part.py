from numbers import Number

class Folder:
    def __init__(self, name, contents):
        self.name = name
        self.contents = contents

class Exportable():
    def __init__(self, name, output_format, file_name = '', args = {}):
        self.name = name
        self.file_name = name if not file_name else file_name
        self.output_format = output_format
        args['part'] = name
        self.args = args

    def get_output_format(self):
        return self.output_format

    def format_args(self):
        formatted_args = []
        for arg, value in self.args.items():
            if isinstance(value, Number):
                formatted_args.append('-D' + arg + '=' + str(value))
            elif isinstance(value, str):
                formatted_args.append('-D' + arg + '="' + value + '"')
        return formatted_args

class ExportableModel(Exportable):
    def __init__(self, name, output_format, file_name, quantity, args):
        self.quantity = quantity
        super().__init__(name, output_format, file_name, args)

class ExportStl(ExportableModel):
    def __init__(self, name, file_name = '', quantity = 1, args = {}):
        super().__init__(name, '.stl', file_name, quantity, args)

class Export3mf(ExportableModel):
    def __init__(self, name, file_name = '', quantity = 1, args = {}):
        super().__init__(name, '.3mf', file_name, quantity, args)

class ExportDxf(ExportableModel):
    def __init__(self, name, file_name = '', quantity = 1, args = {}):
        super().__init__(name, '.dxf', file_name, quantity, args)

class ExportPng(Exportable):
    def __init__(self, name, camera_position, width = 1600, height = 900, file_name = '', args = {}):
        self.name = name
        self.width = width
        self.height = height
        self.camera_position = camera_position
        super().__init__(name, '.png', file_name, args)
