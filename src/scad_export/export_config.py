import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from enum import StrEnum, auto
from functools import cached_property
from pathlib import Path
from threading import Lock

from .exceptions import ConfigError
from .exportable import ColorScheme, ImageSize, ModelFormat
from .user_input import DirectoryPicker, FilePicker, Option, Validation, option_prompt

logger = logging.getLogger(__name__)


def _configure_logging(debug):
    package_logger = logging.getLogger('scad_export')
    if not package_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        package_logger.addHandler(handler)
    package_logger.setLevel(logging.DEBUG if debug else logging.INFO)


class NamingFormat(StrEnum):
    NONE = auto()
    TITLE_CASE = auto()
    SNAKE_CASE = auto()


class ExportConfig:
    _config_write_lock = Lock()

    def __init__(
        self,
        output_naming_format: NamingFormat = NamingFormat.TITLE_CASE,
        default_model_format: ModelFormat = ModelFormat._3MF,
        default_image_color_scheme: ColorScheme = ColorScheme.CORNFIELD,
        default_image_size: ImageSize | None = None,
        parallelism = os.cpu_count(),
        export_timeout: float | None = None,
        debug = False
    ):
        _configure_logging(debug)
        self.output_naming_format = output_naming_format
        self.default_model_format = default_model_format
        self.default_image_color_scheme = default_image_color_scheme
        self.default_image_size = default_image_size if default_image_size else ImageSize()
        self.parallelism = parallelism
        self.export_timeout = export_timeout
        self.debug = debug

        try:
            self._config = self._load_from_drive()
            self.openscad_location
            self.project_root
            self.export_file_path
            self.output_directory
            self.manifold_supported
        except OSError as e:
            raise ConfigError(str(e)) from e

    @cached_property
    def _entry_point_script_directory(self):
        return Path(sys.modules['__main__'].__file__).resolve().parent

    @cached_property
    def _entry_point_script_name(self):
        return Path(sys.modules['__main__'].__file__).stem

    @cached_property
    def _config_path(self):
        path = self._entry_point_script_directory / 'export config.json'
        logger.debug('Using config path: %s', path)
        return path

    def _load_from_drive(self):
        try:
            with self._config_path.open('r') as file:
                return json.load(file)
        except Exception as e:
            logger.debug('Failed to load config with error: %s', e)
            return {}

    def _persist(self, key, value):
        with self._config_write_lock:
            logger.debug('Saving config: "%s" = "%s"', key, value)
            self._config[key] = str(value)
            with self._config_path.open('w') as file:
                json.dump(self._config, file, indent=2)

    def _get_export_files(self):
        base_dir = Path(self.project_root)
        return list(base_dir.rglob('*export map.scad'))

    def _get_config_value(self, key):
        value = self._config.get(key, '')
        if value:
            logger.debug('Found saved value "%s" = "%s"', key, value)
        else:
            logger.debug('No saved value found for "%s"', key)
        return value

    @cached_property
    def _git_project_root(self):
        git_root = ''
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                cwd=self._entry_point_script_directory,
                capture_output=True,
                timeout=15,
            )
            root_string = result.stdout.decode('UTF-8').strip()
            logger.debug('Git output when retrieving project root: %s, error: %s', root_string, result.stderr)
            if root_string:
                git_root = Path(root_string).resolve(strict=False)
        except Exception as e:
            logger.debug('Failed using git to find project root with error: %s', e)
        return git_root

    @cached_property
    def openscad_location(self):
        open_scad_location_name = 'openScadLocation'
        validation = Validation(_is_openscad_path_valid)

        if not validation.is_valid(self._get_config_value(open_scad_location_name)):
            options = [
                'openscad',
                'C:\\Program Files\\OpenSCAD (Nightly)\\openscad.exe',
                'C:\\Program Files\\OpenSCAD\\openscad.exe',
                '/Applications/OpenSCAD.app',
                '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD',
                '~/Applications/OpenSCAD.app',
                '~/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
            ]
            match platform.system():
                case 'Windows':
                    file_type = ('OpenSCAD .exe', '*.exe')
                case 'Darwin':
                    file_type = ('OpenSCAD .app', '*.*')
                case _:
                    file_type = ('OpenSCAD Executable', '*.*')
            picker = FilePicker('/', window_title='Choose OpenSCAD Executable', file_types=[file_type])
            openscad_location = option_prompt('OpenSCAD executable location', validation, options, picker)
            self._persist(open_scad_location_name, openscad_location)
        return self._get_config_value(open_scad_location_name)

    @cached_property
    def project_root(self):
        project_root_name = 'projectRoot'
        validation = Validation(_is_directory)
        if not validation.is_valid(self._get_config_value(project_root_name)):
            current_script_dir = self._entry_point_script_directory
            picker = DirectoryPicker(current_script_dir, window_title='Choose Project Root Directory')
            project_root = option_prompt('project root folder', validation, [self._git_project_root if self._git_project_root else current_script_dir], picker)
            self._persist(project_root_name, project_root)
        return self._get_config_value(project_root_name)

    @cached_property
    def export_file_path(self):
        config_key = self._entry_point_script_name + '.exportMapFile'
        if not os.path.isfile(self._get_config_value(config_key)):
            valid_export_files = self._get_export_files()
            logger.debug('Found export files: %s', ', '.join(file.name for file in valid_export_files))

            options = [Option(display_name=str(file.relative_to(Path(self.project_root))), value=file) for file in valid_export_files]
            validation = Validation(_is_file_with_extension, file_extension='.scad')
            picker = FilePicker(self.project_root, window_title='Choose Export Map File', file_types=[('Export Map .scad', '*.scad')])
            choice = option_prompt('export map file', validation, options, picker)
            self._persist(config_key, choice)
        return self._get_config_value(config_key)

    @cached_property
    def output_directory(self):
        config_key = self._entry_point_script_name + '.outputDirectory'
        output_directory = self._get_config_value(config_key)
        validation = Validation(_is_directory_writable)
        if not validation.is_valid(output_directory):
            home = Path.home()
            options = [home / 'Desktop', home, self.project_root]
            picker = DirectoryPicker(home, window_title='Choose Output Directory')
            stl_output_directory = option_prompt('output directory', validation, options, picker)
            self._persist(config_key, stl_output_directory)
        return self._get_config_value(config_key)

    @cached_property
    def manifold_supported(self):
        try:
            # OpenSCAD writes its help text (which lists supported backends) to stderr.
            result = subprocess.run([self.openscad_location, '-h'], capture_output=True, timeout=30)
            help_text = result.stderr.decode('UTF-8', errors='replace')
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug('Failed to query OpenSCAD for manifold support: %s', e)
            return False
        is_manifold_supported = 'manifold' in help_text.lower()
        logger.debug('Manifold supported: %s', is_manifold_supported)
        return is_manifold_supported


def _is_openscad_path_valid(path):
    path = Path(path).resolve(strict=False)
    return path if shutil.which(path) else ''


def _is_directory(directory):
    if not directory:
        return ''
    directory = Path(directory).resolve(strict=False)
    return directory if directory.is_dir() else ''


def _is_directory_writable(directory):
    return directory if _is_directory(directory) and os.access(directory, os.W_OK) else ''


def _is_file_with_extension(file, file_extension):
    path = Path(file)
    return path if path.is_file() and path.suffix == file_extension else ''
