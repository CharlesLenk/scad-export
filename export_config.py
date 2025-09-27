import json
import os
import platform
import re
import sys
from enum import StrEnum, auto
from functools import cached_property
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Lock

from .exportable import ColorScheme, ImageSize, ModelFormat
from .user_input import DirectoryPicker, FilePicker, option_prompt
from .validation import *


class NamingStrategy(StrEnum):
    SPACE = auto()
    UNDERSCORE = auto()

class ExportConfig:
    _config_write_lock = Lock()

    def __init__(
        self,
        output_naming_strategy: NamingStrategy = NamingStrategy.SPACE,
        default_model_format: ModelFormat = ModelFormat._3MF,
        default_image_color_scheme: ColorScheme = ColorScheme.CORNFIELD,
        default_image_size: ImageSize = ImageSize(),
        debug = False
    ):
        self.debug = debug
        self._config = self._load_from_drive()

        self.openscad_location
        self.project_root
        self.export_file_path
        self.output_directory
        self.manifold_supported

        self.output_naming_strategy = output_naming_strategy
        self.default_model_format = default_model_format
        self.default_image_color_scheme = default_image_color_scheme
        self.default_image_size = default_image_size

    def _get_script_directory(self):
        return str(Path(__file__).resolve().parent)

    def _get_config_path(self):
        return os.path.join(self._get_script_directory(), 'export config.json')

    def _load_from_drive(self):
        try:
            with open(self._get_config_path(), 'r') as file:
                return json.load(file)
        except Exception as e:
            if self.debug:
                print('Failed to load config with error: {}'.format(e))
            return {}

    def _persist(self, key, value):
        with self._config_write_lock:
            if self.debug:
                print('Saving config: {}={}'.format(key, value))
            self._config[key] = value
            with open(self._get_config_path(), 'w+') as file:
                json.dump(self._config, file, indent=2)

    def _get_entry_point_script_name(self):
        return re.split('/|\\\\', sys.modules['__main__'].__file__)[-1][0:-3]

    def _get_export_file_names(self):
        matching_files = []
        for _, _, files in os.walk(self.project_root):
            for file_name in files:
                if file_name.endswith('export map.scad'):
                    matching_files.append(file_name)
        return matching_files

    def _get_config_value(self, key):
        value = self._config.get(key, '')
        if self.debug and value:
            print('Found saved value {}={}'.format(key, value))
        elif self.debug and not value:
            print('No saved value found for {}'.format(key))
        return value

    @cached_property
    def openscad_location(self):
        open_scad_location_name = 'openScadLocation'
        validation = Validation(is_openscad_path_valid)

        if not validation.is_valid(self._get_config_value(open_scad_location_name)):
            options = [
                'openscad',
                'C:\\Program Files\\OpenSCAD (Nightly)\\openscad.exe',
                'C:\\Program Files\\OpenSCAD\\openscad.exe',
                '/Applications/OpenSCAD.app',
                '~/Applications/OpenSCAD.app'
            ]
            file_type = ('OpenSCAD Executable', '*.*')
            if platform.system() == 'Windows':
                file_type = ('OpenSCAD .exe', '*.exe')
            if platform.system() == 'Darwin':
                file_type = ('OpenSCAD .app', '*.*')
            picker = FilePicker('/', window_title='Choose OpenSCAD Executable', file_types=[file_type])
            openscad_location = option_prompt('OpenSCAD executable location', validation, options, picker)
            self._persist(open_scad_location_name, openscad_location)
        return self._get_config_value(open_scad_location_name)

    @cached_property
    def project_root(self):
        project_root_name = 'projectRoot'
        validation = Validation(is_directory)
        if not validation.is_valid(self._get_config_value(project_root_name)):
            git_root = ''
            try:
                process = Popen(
                    ['git', 'rev-parse', '--show-superproject-working-tree'],
                    cwd=self._get_script_directory(),
                    stdout=PIPE,
                    stderr=PIPE
                )
                out, err = process.communicate()
                git_root = Path(str(out, encoding='UTF-8')).resolve(strict=False)
                if self.debug:
                    print('Git output when retrieving project root: {}, error: {}'.format(out, err))
            except Exception as e:
                if self.debug:
                    print('Failed using git to find project root with error: {}'.format(e))
                pass

            current_script_dir = os.path.dirname(self._get_script_directory())
            picker = DirectoryPicker(self._get_script_directory(), window_title='Choose Project Root Directory')
            project_root = option_prompt('project root folder', validation, [git_root, current_script_dir], picker)
            self._persist(project_root_name, project_root)
        return self._get_config_value(project_root_name)

    @cached_property
    def export_file_path(self):
        config_key = self._get_entry_point_script_name() + '.exportMapFile'
        if not os.path.isfile(self._get_config_value(config_key)):
            valid_export_files = self._get_export_file_names()
            if self.debug:
                print('Found export files: ' + ', '.join(valid_export_files))

            validation = Validation(is_file_with_extension, file_extension='.scad', search_directory=self.project_root)
            picker = FilePicker(self.project_root, window_title='Choose Export Map File', file_types=[('Export Map .scad', '*.scad')])
            value = option_prompt('export map file', validation, valid_export_files, picker)
            self._persist(config_key, value)
        return self._get_config_value(config_key)

    @cached_property
    def output_directory(self):
        config_key = self._get_entry_point_script_name() + '.outputDirectory'
        output_directory = self._get_config_value(config_key)
        validation = Validation(is_path_writable)
        if not validation.is_valid(output_directory):
            options = [
                os.path.join(os.path.expanduser('~'), 'Desktop'),
                os.path.expanduser('~'),
                self.project_root
            ]
            picker = DirectoryPicker(os.path.expanduser('~'), window_title='Choose Output Directory')
            stl_output_directory = option_prompt('output directory', validation, options, picker)
            self._persist(config_key, stl_output_directory)
        return self._get_config_value(config_key)

    @cached_property
    def manifold_supported(self):
        process = Popen([self.openscad_location, '-h'], stdout=PIPE, stderr=PIPE)
        _, out = process.communicate()
        return 'manifold' in str(out)
