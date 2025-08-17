import json
import shutil
import platform
import os
import sys
from functools import cache
from subprocess import Popen, PIPE
from pathlib import PurePath
from threading import Lock

conf_file_name = 'export.conf'
default_export_file_name = 'export map.scad'

openSCADLocationName = 'openSCADLocation'
projectRootName = 'projectRoot'
exportFilePathName = 'exportFilePath'
stlOutputDirectoryName = 'stlOutputDirectory'

def is_openscad_location_valid(location):
    return shutil.which(location) is not None

def is_path_writable(directory):
    return os.access(os.path.dirname(directory), os.W_OK)

def is_valid_path(path):
    return os.path.isdir(os.path.dirname(path))

def get_file_path(file_name):
    project_root = _get_project_root()
    print('Searching for {} in {}'.format(file_name, project_root))
    for root, dirs, files in os.walk(project_root):
        if file_name in files:
            return str(os.path.join(root, file_name))

def is_scad_file(file_name):
    return file_name.lower().endswith('.scad') and get_file_path(file_name) is not None

def reprompt(validation_func, input_name):
    user_input = input('Enter {} or "q" to exit: '.format(input_name))
    while not validation_func(user_input) and user_input.strip() != 'q':
        print('{}: "{}" not accessible'.format(input_name, user_input))
        user_input = input('Enter {} or "q" to exit: '.format(input_name))
    if user_input == 'q':
        sys.exit('Quitting. {} must be set.'.format(input_name))
    else:
        return user_input

def _get_project_root():
    process = Popen(['git', 'rev-parse', '--show-toplevel'], cwd=str(PurePath(__file__).parents[1]), stdout=PIPE, stderr=PIPE)
    project_root, err = process.communicate()
    project_root = str(project_root, encoding='UTF-8').strip()
    if not is_valid_path(project_root):
        project_root = reprompt(os.path.isdir, 'project root folder')
    print('Project root: {}'.format(project_root))
    return project_root

def _get_export_file_path():
    export_file_name = default_export_file_name
    if not is_scad_file(export_file_name):
        export_file_name = reprompt(is_scad_file, 'export file name (.scad)')
    return get_file_path(export_file_name)

def _get_openscad_location():
    system = platform.system()
    location = ''
    if (system == 'Windows'):
        nightly_path = 'C:\\Program Files\\OpenSCAD (Nightly)\\openscad.exe'
        if (shutil.which(nightly_path) is not None):
            location = nightly_path
        else:
            location = 'C:\\Program Files\\OpenSCAD\\openscad.exe'
    elif (system == 'Darwin'):
        location = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
    elif (system == 'Linux'):
        location = 'openscad'
    if not is_openscad_location_valid(location):
        reprompt(is_openscad_location_valid, 'OpenSCAD executable location')
    return location

def _get_stl_output_directory():
    default = os.path.join(os.path.expanduser('~'), 'Desktop', 'stl_export')
    directory = ''
    if is_path_writable(default):
        user_input = input('Would you like to use default STL output directory of {}? (y/n): '.format(default))
        if user_input.strip() == 'y':
            directory = default
    if not is_path_writable(directory):
        directory = reprompt(is_path_writable, 'STL output directory')
    return directory

def _get_manifold_support(openscad_location):
    if openscad_location:
        process = Popen([openscad_location, '-h'], stdout=PIPE, stderr=PIPE)
        _, out = process.communicate()
        return 'manifold' in str(out)
    else:
        return False

class ExportConfig:
    def _validate(config):
        validated_config = config.copy()
        if not is_openscad_location_valid(config.get(openSCADLocationName, '')):
            validated_config[openSCADLocationName] = _get_openscad_location()
        if not is_valid_path(config.get(projectRootName, '')):
            validated_config[projectRootName] = _get_project_root()
        if not is_valid_path(config.get(exportFilePathName, '')):
            validated_config[exportFilePathName] = _get_export_file_path()
        if not is_path_writable(config.get(stlOutputDirectoryName, '')):
            validated_config[stlOutputDirectoryName] = _get_stl_output_directory()
        return validated_config

    def __init__(self):
        conf_file = os.path.join(PurePath(__file__).parents[0], conf_file_name)
        config = {}
        if os.path.isfile(conf_file):
            with open(conf_file, 'r') as file:
                config = json.load(file)
        validated_config = self._validate(config)
        if validated_config != config:
            with open(conf_file, 'w') as file:
                json.dump(validated_config, file, indent=2)
        self.openSCADLocation = validated_config[openSCADLocationName]
        self.manifoldSupport = _get_manifold_support(self.openSCADLocation)
        self.projectRoot = validated_config[projectRootName]
        self.exportFilePath = validated_config[exportFilePathName]
        self.stlOutputDirectory = validated_config[stlOutputDirectoryName]
