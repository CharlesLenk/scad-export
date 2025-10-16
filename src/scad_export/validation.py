import os
import platform
import shutil
from pathlib import Path


class Validation:
    def __init__(self, validation_function, **kwargs):
        self.validation_function = validation_function
        self.kwargs = kwargs

    def is_valid(self, value):
        return self.validation_function(value, **self.kwargs)

def is_openscad_path_valid(path):
    # If MacOS and executable not found, try pathing to it in .app package.
    if platform.system() == 'Darwin' and shutil.which(path) is None:
        path += '/Contents/MacOS/OpenSCAD'
    path = Path(path).resolve(strict=False)
    return str(path) if shutil.which(path) else ''

def is_directory(directory):
    if directory:
        directory = Path(directory).resolve(strict=False)
        directory = directory if directory.is_dir() else ''
    return str(directory)

def is_directory_writable(directory):
    if directory:
        directory = Path(directory).resolve(strict=False)
        directory = directory if os.access(directory, os.W_OK) else ''
    return str(directory)

def get_file_path(search_directory, file_name):
    file_path = ''
    for root, _, files in os.walk(search_directory):
        if file_name in files:
            file_path = Path(root).joinpath(file_name).resolve(strict=False)
    return file_path

def is_file_with_extension(file_name, file_extension, search_directory):
    file_path = Path(file_name)
    if not file_path.exists():
        file_path = get_file_path(search_directory, file_name)
    return str(file_path) if file_path and str(file_path).lower().endswith(file_extension) else ''

def is_in_list(value, list):
    value = str(value).lower()
    return value if value in [str(item).lower() for item in list] else ''
