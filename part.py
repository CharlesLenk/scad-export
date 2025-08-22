from numbers import Number

class Part:
    def __init__(self, part_name, file_name, quantity = 1, args = {}):
        self.part_name = part_name
        self.file_name = file_name
        self.quantity = quantity
        self.args = args
        self

    def get_additional_args(self):
        formatted_args = []
        for arg, value in self.args:
            if isinstance(value, Number) and arg != 'quantity':
                formatted_args.append('-D' + arg + '=' + str(value))
            elif isinstance(value, str):
                formatted_args.append('-D' + arg + '="' + value + '"')
        return formatted_args


class Image:
    def __init__(self):
        self


# part_map = {
#     'Cupiter': {
#         'Frame': {
#             'Lens': {
#                 'part': 'lens'
#             },