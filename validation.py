import os
import platform
import shutil

class Validation:
    def __init__(self, validation_function, **kwargs):
        self.validation_function = validation_function
        self.kwargs = kwargs

    def is_valid(self, value):
        return self.validation_function(value, **self.kwargs)

def is_openscad_location_valid(location):
    # If MacOS and executable not found, try pathing to it in .app package.
    if platform.system() == 'Darwin' and shutil.which(location) is None:
        location += '/Contents/MacOS/OpenSCAD'
    location = os.path.normpath(location)
    return location if shutil.which(location) is not None else ''

def is_directory(directory):
    directory = os.path.normpath(directory)
    return directory if os.path.isdir(directory) else ''

def is_path_writable(directory):
    directory = os.path.normpath(directory)
    return directory if os.access(os.path.dirname(directory), os.W_OK) else ''

def get_file_path(search_directory, file_name):
    file_path = ''
    for root, _, files in os.walk(search_directory):
        if file_name in files:
            file_path = str(os.path.normpath(os.path.join(root, file_name)))
    return file_path

def is_file_with_extension(file_name, file_extension, search_directory):
    file_path = get_file_path(search_directory, file_name)
    return file_path if file_name.lower().endswith(file_extension) and file_path else ''

def is_in_list(value, list):
    value = str(value).lower()
    return value if value in [str(item).lower() for item in list] else ''
