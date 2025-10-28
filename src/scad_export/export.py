import shutil
import string
from concurrent.futures import ThreadPoolExecutor
from numbers import Number
from pathlib import Path
from subprocess import PIPE, Popen

from .export_config import ExportConfig, NamingFormat
from .exportable import Exportable, Folder, Image, Model


def _flatten_paths(item, current_path = '', paths_and_exportables = None):
    if paths_and_exportables is None:
        paths_and_exportables = {}
    if isinstance(item, Exportable):
        paths_and_exportables.setdefault(current_path, []).append(item)
    elif isinstance(item, Folder):
        for subitem in item.contents:
            paths_and_exportables.update(_flatten_paths(subitem, current_path + '/' + item.name, paths_and_exportables))
    return paths_and_exportables

def _format_name(name, naming_format: NamingFormat):
    formatted_name = name
    if naming_format is NamingFormat.TITLE_CASE:
        formatted_name = string.capwords(formatted_name.strip().replace('_', ' '))
    elif naming_format is NamingFormat.SNAKE_CASE:
        formatted_name = formatted_name.lower().replace(' ', '_')
    return formatted_name

def _format_path_name(path, naming_format: NamingFormat):
    return '/'.join([_format_name(folder, naming_format) for folder in path.split('/')])

def _format_part_name(name, naming_format: NamingFormat, file_format, user_args, count = 1):
    formatted_name = name
    if naming_format is not NamingFormat.NONE:
        for key, value in user_args.items():
            formatted_name += '_({}-{})'.format(key, value)
    formatted_name += ('_{}'.format(count) if count > 1 else '')
    formatted_name = _format_name(formatted_name, naming_format)
    return formatted_name + file_format

def _get_exportable_args(exportable: Exportable, config: ExportConfig):
    args=[
        config.openscad_location,
        config.export_file_path
    ]
    if config.manifold_supported:
        args.append('--enable=manifold')
    args.append('-Dname="{}"'.format(exportable.name))
    for arg, value in exportable.user_args.items():
        if isinstance(value, Number):
            args.append('-D{}={}'.format(arg, value))
        elif isinstance(value, str):
            args.append('-D{}="{}"'.format(arg, value))

    if isinstance(exportable, Image):
        args.append('--camera={}'.format(exportable.camera_position))
        color_scheme = exportable.color_scheme if exportable.color_scheme else config.default_image_color_scheme
        args.append('--colorscheme={}'.format(color_scheme))
        image_size = exportable.image_size if exportable.image_size else config.default_image_size
        args.append('--imgsize={},{}'.format(image_size.width, image_size.height))
        if config.manifold_supported:
            args.append('--render=true')
        else:
            args.append('-D$fs=0.4')
            args.append('-D$fa=0.8')

    return args

def _export_file(folder_path, exportable: Exportable, config: ExportConfig):
    output_format = exportable.output_format
    if isinstance(exportable, Model):
        output_format = output_format if output_format else config.default_model_format

    output_file_name = _format_part_name(exportable.file_name, config.output_naming_format, output_format, exportable.user_args)

    formatted_folder_path = _format_path_name(folder_path, config.output_naming_format)
    output_directory = config.output_directory + formatted_folder_path + '/'
    Path.mkdir(Path(output_directory), parents=True, exist_ok=True)

    args = _get_exportable_args(exportable, config)
    args.append('-o' + output_directory + output_file_name)

    if config.debug:
        print('\nOpenSCAD args for {}:\n{}\n'.format(output_file_name, args))

    process = Popen(args, stdout=PIPE, stderr=PIPE)
    _, err = process.communicate()

    output = ""
    if (process.returncode == 0):
        output = 'Finished exporting: ' + formatted_folder_path + '/' + output_file_name
        for count in range(2, exportable.quantity + 1):
            part_copy_name = _format_part_name(exportable.file_name, config.output_naming_format, output_format, exportable.user_args, count)
            shutil.copy(output_directory + output_file_name, output_directory + part_copy_name)
            output += '\nFinished exporting: ' + formatted_folder_path + '/' + part_copy_name
    else:
        output = 'Failed to export: "{}/{}", Error: "{}"'.format(formatted_folder_path, output_file_name, err.decode('UTF-8').strip())
    return output

def export(exportables: Folder, config: ExportConfig = None):
    if config is None:
        config = ExportConfig()

    if config.initialized:
        with ThreadPoolExecutor(max_workers = config.parallelism) as executor:
            print('Starting export')
            futures = []
            paths_and_exportables = _flatten_paths(exportables)
            for path, path_exportables in paths_and_exportables.items():
                for exportable in path_exportables:
                    futures.append(executor.submit(_export_file, path, exportable, config))
            for future in futures:
                print(future.result())
            print('Done!')
    else:
        print('Export skipped because config was not initialized.')
