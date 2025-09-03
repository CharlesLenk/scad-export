import json
import shutil
import platform
import os
import sys
from subprocess import Popen, PIPE
from functools import cache
from threading import Lock
from enum import StrEnum, auto

conf_file_name = 'export config.json'
default_export_map_file_name = 'export map.scad'

class NamingStrategy(StrEnum):
    SPACE = auto()
    UNDERSCORE = auto()

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

def is_openscad_location_valid(location):
    return location if shutil.which(location) is not None else ''

def is_directory(directory):
    return directory if os.path.isdir(directory) else ''

def is_path_writable(directory):
    return directory if os.access(os.path.dirname(directory), os.W_OK) else ''

def get_export_file_names(search_directory):
    matching_files = []
    for _, _, files in os.walk(search_directory):
        for file_name in files:
            if file_name.endswith(default_export_map_file_name):
                matching_files.append(file_name)
    return matching_files
            
def get_file_path(search_directory, file_name):
    file_path = ''
    for root, _, files in os.walk(search_directory):
        if file_name in files:
            file_path = str(os.path.join(root, file_name))
    return file_path

def is_file_with_extension(file_name, extension, search_directory):
    file_path = get_file_path(search_directory, file_name)
    return file_path if file_name.lower().endswith(extension) and file_path else ''

def is_in_options(value, options):
    value = str(value).lower()
    return value if value in [str(option).lower() for option in options] else ''

def get_working_directory():
    return str(os.path.dirname(os.path.realpath(__file__)))

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

    def get_valid_value(self):
        return self.validation_function(*([self.prefix + self.value + self.postfix] + self.additional_args))

def value_prompt(validatable, input_name):
    input_value = input('Enter {} or "q" to quit: '.format(input_name))
    while not validatable.set_value(input_value).get_valid_value() and input_value.strip().lower() != 'q':
        print('{}: "{}" invalid'.format(input_name, input_value))
        input_value = input('Enter {} or "q" to quit: '.format(input_name))
    if input_value.strip().lower() == 'q':
        sys.exit('Quitting.')
    return validatable.get_valid_value()

def option_prompt(input_name, options = []):
    prompt = ''
    option_count = len(options) + 1
    for index, option in enumerate(options):
        prompt += '  ' + str(index + 1) + ' - ' + option.get_valid_value() + '\n'
    prompt+= '  ' + str(option_count) + ' - ' + "[Enter custom value]" + '\n'

    print('\nChoose ' + input_name + ':')
    print(prompt)
    validate = Validateable(is_in_options,  '', additional_args = [list(range(1, option_count + 1))])
    choice = value_prompt(validate, "option number")
    if str(choice) == str(option_count):
        return value_prompt(options[0].set_value(''), input_name)
    else:
        return options[int(choice) - 1].get_valid_value()

class ExportConfig:
    open_scad_location_name = 'openScadLocation'
    open_scad_location_lock = Lock()
    project_root_name = 'projectRoot'
    project_root_lock = Lock()
    export_map_file_name = 'exportMapFile'
    export_map_file_lock = Lock()
    output_directory_name = 'outputDirectory'
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
                self.config.update({ field_name : value})
                json.dump(self.config, file, indent=2)

    def __init__(
            self,
            naming_strategy: NamingStrategy = NamingStrategy.SPACE,
            image_color_scheme: ColorScheme = ColorScheme.CORNFIELD,
            debug = False
        ):
        self.naming_strategy = naming_strategy
        self.image_color_scheme = image_color_scheme
        self.debug = debug
        conf_file = os.path.join(get_working_directory(), conf_file_name)
        if os.path.isfile(conf_file):
            with open(conf_file, 'r') as file:
                self.config = json.load(file)

    @cache
    def _get_openscad_location(self):
        if not is_openscad_location_valid(self.config.get(self.open_scad_location_name, '')):
            system = platform.system()
            validateable = Validateable(is_openscad_location_valid, 'openscad')
            if not validateable.get_valid_value():
                if system == 'Windows':
                    validateable.set_value('C:\\Program Files\\OpenSCAD (Nightly)\\openscad.exe')
                    if not validateable.get_valid_value():
                        validateable.set_value('C:\\Program Files\\OpenSCAD\\openscad.exe')
                elif system == 'Darwin':
                    validateable.set_value('/Applications/OpenSCAD.app')
                    validateable.postfix = '/Contents/MacOS/OpenSCAD'
                    if not validateable.get_valid_value():
                        validateable.set_value('~/Applications/OpenSCAD.app')
            openscad_location = option_prompt('OpenSCAD executable location', [validateable])
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
            if not project_root:
                project_root = os.path.dirname(get_working_directory())
            project_root = option_prompt('project root folder', [Validateable(is_directory, project_root)])
            self.persist(self.project_root_name, project_root)
        return self.config.get(self.project_root_name)

    @cache
    def get_project_root(self):
        with self.project_root_lock:
            return self._get_project_root()

    @cache
    def _get_export_file_path(self):
        config_key = sys.modules['__main__'].__file__.split('/')[-1][0:-3]
        if self.debug:
            print('Checking config for SCAD export file with key: ' + config_key + '.' + self.export_map_file_name)
        if not os.path.isfile(self.config.get(config_key + '.' + self.export_map_file_name, '')):
            if self.debug:
                print('SCAD export file not found under key: ' + config_key + '.' + self.export_map_file_name)
            valid_export_files = get_export_file_names(self.get_project_root())
            if self.debug:
                print('Valid export files: ' + ', '.join(valid_export_files))
            validatables = []
            for file in valid_export_files:
                validatables.append(
                    Validateable(
                        is_file_with_extension,
                        file,
                        additional_args = ['.scad', self.get_project_root()]
                    )
                )
            value = option_prompt('export map file', validatables)
            self.persist(config_key + '.' + self.export_map_file_name, value)
        return self.config.get(config_key + '.' + self.export_map_file_name)

    @cache
    def get_export_file_path(self):
        with self.export_map_file_lock:
            return self._get_export_file_path()

    @cache
    def _get_output_directory(self):
        config_key = sys.modules['__main__'].__file__.split('/')[-1][0:-3]
        output_directory = self.config.get(config_key + '.' + self.output_directory_name, '')
        if not is_path_writable(output_directory):
            validatables = []
            validatables.append(
                Validateable(
                    is_path_writable,
                    os.path.join(os.path.expanduser('~'), 'Desktop')
                )
            )
            validatables.append(
                Validateable(
                    is_path_writable,
                    self.get_project_root()
                )
            )
            stl_output_directory = option_prompt('output directory', validatables)
            self.persist(config_key + '.' + self.output_directory_name, stl_output_directory)
        return self.config.get(config_key + '.' + self.output_directory_name)

    @cache
    def get_output_directory(self):
        with self.stl_output_directory_lock:
            return self._get_output_directory()

    @cache
    def _get_manifold_support(self):
        process = Popen([self.get_openscad_location(), '-h'], stdout=PIPE, stderr=PIPE)
        _, out = process.communicate()
        return 'manifold' in str(out)

    @cache
    def get_manifold_support(self):
        with self.manifold_support_lock:
            return self._get_manifold_support()

    @cache
    def get_output_naming_strategy(self):
        return self.naming_strategy

    @cache
    def get_image_color_scheme(self):
        return self.image_color_scheme

    @cache
    def debug_enabled(self):
        return self.debug

    @cache
    def get_common_args(self):
        args = [
            self.get_openscad_location(),
            self.get_export_file_path(),
            '--colorscheme=' + self.image_color_scheme
        ]
        if self.get_manifold_support():
            args += ['--enable=manifold', '--render=true']
        else:
            args += ['-D$fs=0.4', '-D$fa=0.8']
        return args
