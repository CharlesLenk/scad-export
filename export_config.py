import json
import shutil
import platform
import os
import sys
from subprocess import Popen, PIPE
from pathlib import PurePath
from functools import cache
from threading import Lock

conf_file_name = 'export config.json'
default_export_map_file_name = 'export map.scad'
default_export_parts_config_name = 'export parts.json'

def is_openscad_location_valid(location):
    return shutil.which(location) is not None

def is_path_writable(directory):
    return os.access(os.path.dirname(directory), os.W_OK)

def get_file_path(search_directory, file_name):
    for root, _, files in os.walk(search_directory):
        if file_name in files:
            return str(os.path.join(root, file_name))

def is_file_with_extension(file_name, extension, search_directory):
    return file_name.lower().endswith(extension) and get_file_path(search_directory, file_name) is not None

def get_working_directory():
    return str(PurePath(__file__).parents[0])

def yes_no_prompt(message):
    valid_inputs = ('y', 'n')
    response = input(message + ' (y/n): ')
    while response.lower() not in valid_inputs:
        print('{} not valid. Enter one of: {}'.format(response, valid_inputs))
        response = input(message)
    return response.lower() == 'y'

def reprompt(validatable, input_name):
    input_value = None
    print('\nAttempting to load default {}: {}'.format(input_name, validatable.value))
    if validatable.validate():
        if yes_no_prompt('Default {} ({}) is valid. Would you like to use it?'.format(input_name, validatable.value)):
            input_value = validatable.value
    else:
        print('Unable to load default {}'.format(input_name))

    if (input_value is None):
        input_value = input('Enter {} or "q" to exit: '.format(input_name))
        while not validatable.set_value(input_value).validate() and input_value.strip().lower() != 'q':
            print('{}: "{}" invalid or not accessible.'.format(input_name, input_value))
            input_value = input('Enter {} or "q" to exit: '.format(input_name))
        if input_value == 'q':
            sys.exit('Quitting. {} must be set.'.format(input_name))
    return validatable.value

class Validateable:
    def __init__(self, validation_function, value, prefix = '', postfix = '', additional_args = []):
        self.validation_function = validation_function
        self.value = value
        self.prefix = prefix
        self.postfix = postfix
        self.additional_args = additional_args

    def set_value(self, value):
        self.value = value
        return self

    def validate(self):
        return self.validation_function(*([self.prefix + self.value + self.postfix] + self.additional_args))

class ExportConfig:
    open_scad_location_name = 'openScadLocation'
    open_scad_location_lock = Lock()
    project_root_name = 'projectRoot'
    project_root_lock = Lock()
    export_map_file_name = 'exportMapFile'
    export_map_file_lock = Lock()
    stl_output_directory_name = 'stlOutputDirectory'
    stl_output_directory_lock = Lock()
    manifold_support_lock = Lock()
    config_write_lock = Lock()
    config = {}

    def persist(self, field_name, value):
        with self.config_write_lock:
            conf_file = os.path.join(get_working_directory(), conf_file_name)
            try:
                with open(conf_file, 'r') as file:
                    self.config = json.load(file)
            except Exception:
                pass
            with open(conf_file, 'w+') as file:
                self.config[field_name] = value
                json.dump(self.config, file, indent=2)

    def __init__(self):
        conf_file = os.path.join(get_working_directory(), conf_file_name)
        if os.path.isfile(conf_file):
            with open(conf_file, 'r') as file:
                self.config = json.load(file)

    @cache
    def _get_openscad_location(self):
        if not is_openscad_location_valid(self.config.get(self.open_scad_location_name, '')):
            system = platform.system()
            validateable = Validateable(is_openscad_location_valid, 'openscad')
            if not validateable.validate():
                if system == 'Windows':
                    nightly_path = 'C:\\Program Files\\OpenSCAD (Nightly)\\openscad.exe'
                    if is_openscad_location_valid(nightly_path):
                        validateable.set_value(nightly_path)
                    else:
                        validateable.set_value('C:\\Program Files\\OpenSCAD\\openscad.exe')
                elif system == 'Darwin':
                    validateable.set_value('/Applications/OpenSCAD.app')
                    validateable.postfix = '/Contents/MacOS/OpenSCAD'
            openscad_location = reprompt(validateable, 'OpenSCAD executable location')
            self.persist(self.open_scad_location_name, openscad_location)
        return self.config.get(self.open_scad_location_name)

    @cache
    def get_openscad_location(self):
        with self.open_scad_location_lock:
            return self._get_openscad_location()

    @cache
    def _get_project_root(self):
        if not os.path.isdir(self.config.get(self.project_root_name, '')):
            process = Popen(
                ['git', 'rev-parse', '--show-superproject-working-tree'],
                cwd=get_working_directory(),
                stdout=PIPE,
                stderr=PIPE
            )
            project_root, _ = process.communicate()
            project_root = str(project_root, encoding='UTF-8').strip()
            project_root = reprompt(Validateable(os.path.isdir, project_root), 'project root folder')
            self.persist(self.project_root_name, project_root)
        return self.config.get(self.project_root_name)

    @cache
    def get_project_root(self):
        with self.project_root_lock:
            return self._get_project_root()

    @cache
    def _get_export_file_path(self):
        if not os.path.isfile(self.config.get(self.export_map_file_name, '')):
            validateable = Validateable(
                is_file_with_extension,
                default_export_map_file_name,
                additional_args = ['.scad', self.get_project_root()]
            )
            export_file_name = reprompt(validateable, 'export map file (.scad)')
            export_map_file = get_file_path(self.get_project_root(), export_file_name)
            self.persist(self.export_map_file_name, export_map_file)
        return self.config.get(self.export_map_file_name)

    @cache
    def get_export_file_path(self):
        with self.export_map_file_lock:
            return self._get_export_file_path()

    @cache
    def _get_stl_output_directory(self):
        if not is_path_writable(self.config.get(self.stl_output_directory_name, '')):
            default = os.path.join(os.path.expanduser('~'), 'Desktop', 'stl_export')
            stl_output_directory = reprompt(Validateable(is_path_writable, default), 'STL output directory')
            self.persist(self.stl_output_directory_name, stl_output_directory)
        return self.config.get(self.stl_output_directory_name)

    @cache
    def get_stl_output_directory(self):
        with self.stl_output_directory_lock:
            return self._get_stl_output_directory()

    @cache
    def _get_manifold_support(self):
        process = Popen([self.get_openscad_location(), '-h'], stdout=PIPE, stderr=PIPE)
        _, out = process.communicate()
        return 'manifold' in str(out)

    @cache
    def get_manifold_support(self):
        with self.manifold_support_lock:
            return self._get_manifold_support()
