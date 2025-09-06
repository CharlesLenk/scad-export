import json
import os
import sys
from subprocess import Popen, PIPE
from functools import cache
from threading import Lock
from enum import StrEnum, auto
from .validation import *

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

class ExportConfig:
    _locks = {}
    _lock_lock = Lock()
    _config = {}

    @cache
    def _get_lock(self, key):
        with self._lock_lock:
            return self._locks.setdefault(key, Lock())

    def _get_working_directory(self):
        return str(os.path.dirname(os.path.realpath(__file__)))

    def _get_config_path(self):
        return os.path.join(self._get_working_directory(), 'export config.json')

    def _load_config(self):
        try:
            with open(self._get_config_path(), 'r') as file:
                self._config = json.load(file)
        except Exception as e:
            if self.debug_enabled():
                print('Failed to load config with error: {}'.format(e))
            pass

    def _persist(self, key, value):
        with self._get_lock('_persist'):
            if self.debug_enabled():
                print('Storing config key=value: {}={}'.format(key, value))
            self._config[key] = value
            with open(self._get_config_path(), 'w+') as file:
                json.dump(self._config, file, indent=2)

    def __init__(
            self,
            naming_strategy: NamingStrategy = NamingStrategy.SPACE,
            image_color_scheme: ColorScheme = ColorScheme.CORNFIELD,
            debug = False
        ):
        self.naming_strategy = naming_strategy
        self.image_color_scheme = image_color_scheme
        self.debug = debug
        self._load_config()

    def _get_entry_point_script_name(self):
        return sys.modules['__main__'].__file__.split('/')[-1][0:-3]

    def _get_export_file_names(self):
        matching_files = []
        for _, _, files in os.walk(self.get_project_root()):
            for file_name in files:
                if file_name.endswith('export map.scad'):
                    matching_files.append(file_name)
        return matching_files
    
    def _get_config_value(self, key):
        if self.debug_enabled():
            print('Retrieving config key: ' + key)
        value = self._config.get(key, '')
        if self.debug_enabled() and not value:
            print('No value found for key: ' + key)
        return value

    @cache
    def _get_openscad_location(self):
        open_scad_location_name = 'openScadLocation'
        validation = Validation(is_openscad_location_valid)
        if not validation.is_valid(self._get_config_value(open_scad_location_name)):
            options = [
                'openscad',
                'C:\\Program Files\\OpenSCAD (Nightly)\\openscad.exe',
                'C:\\Program Files\\OpenSCAD\\openscad.exe',
                '/Applications/OpenSCAD.app',
                '~/Applications/OpenSCAD.app'
            ]
            openscad_location = option_prompt('OpenSCAD executable location', validation, options)
            self._persist(open_scad_location_name, openscad_location)
        return self._get_config_value(open_scad_location_name)

    @cache
    def get_openscad_location(self):
        with self._get_lock('get_openscad_location'):
            return self._get_openscad_location()

    @cache
    def _get_project_root(self):
        project_root_name = 'projectRoot'
        if not os.path.isdir(self._get_config_value(project_root_name)):
            process = Popen(
                ['git', 'rev-parse', '--show-superproject-working-tree'],
                cwd=self._get_working_directory(),
                stdout=PIPE,
                stderr=PIPE
            )
            project_root, _ = process.communicate()
            project_root = str(project_root, encoding='UTF-8').strip()
            if not project_root:
                project_root = os.path.dirname(self._get_working_directory())
            project_root = option_prompt('project root folder', Validation(is_directory), [project_root])
            self._persist(project_root_name, project_root)
        return self._get_config_value(project_root_name)

    @cache
    def get_project_root(self):
        with self._get_lock('get_project_root'):
            return self._get_project_root()

    @cache
    def _get_export_file_path(self):
        config_key = self._get_entry_point_script_name() + '.exportMapFile'
        if not os.path.isfile(self._get_config_value(config_key)):            
            valid_export_files = self._get_export_file_names()
            if self.debug:
                print('Found export files: ' + ', '.join(valid_export_files))

            validation = Validation(is_file_with_extension, additional_args=['.scad', self.get_project_root()])
            value = option_prompt('export map file', validation, valid_export_files)
            self._persist(config_key, value)
        return self._get_config_value(config_key)

    @cache
    def get_export_file_path(self):
        with self._get_lock('get_export_file_path'):
            return self._get_export_file_path()

    @cache
    def _get_output_directory(self):
        config_key = self._get_entry_point_script_name() + '.outputDirectory'
        output_directory = self._get_config_value(config_key)
        validation = Validation(is_path_writable)
        if not validation.is_valid(output_directory):
            options = [
                os.path.join(os.path.expanduser('~'), 'Desktop'),
                self.get_project_root()
            ]
            stl_output_directory = option_prompt('output directory', validation, options)
            self._persist(config_key, stl_output_directory)
        return self._get_config_value(config_key)

    @cache
    def get_output_directory(self):
        with self._get_lock('get_output_directory'):
            return self._get_output_directory()

    @cache
    def _get_manifold_support(self):
        process = Popen([self.get_openscad_location(), '-h'], stdout=PIPE, stderr=PIPE)
        _, out = process.communicate()
        return 'manifold' in str(out)

    @cache
    def get_manifold_support(self):
        with self._get_lock('get_manifold_support'):
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
    def get_shared_args(self):
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
