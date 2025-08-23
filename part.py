from numbers import Number

class Folder:
    def __init__(self, name, contents):
        self.name = name
        self.contents = contents

class Part:
    def __init__(self, name, file_name = '', quantity = 1, args = {}):
        self.name = name
        self.file_name = name if not file_name else file_name
        self.quantity = quantity
        args['part'] = name
        self.args = args
        self

    def get_additional_args(self):
        formatted_args = []
        for arg, value in self.args.items():
            if isinstance(value, Number) and arg != 'quantity':
                formatted_args.append('-D' + arg + '=' + str(value))
            elif isinstance(value, str):
                formatted_args.append('-D' + arg + '="' + value + '"')
        return formatted_args

class Image:
    def __init__(self, name, width, height, camera_position):
        self.name = name
        self.width = width
        self.height = height
        self.camera_position = camera_position
