import shutil
import string
from concurrent.futures import ThreadPoolExecutor
from numbers import Number
from pathlib import Path
from subprocess import PIPE, Popen

from .export_config import ExportConfig, NamingStrategy
from .exportable import Exportable, Folder, Image, Model


def _flatten_folders(item, current_path = '', folders_and_parts = None):
    if folders_and_parts is None:
        folders_and_parts = {}
    if isinstance(item, Exportable):
        folders_and_parts.setdefault(current_path, []).append(item)
    elif isinstance(item, Folder):
        for subitem in item.contents:
            folders_and_parts.update(_flatten_folders(subitem, current_path + '/' + item.name, folders_and_parts))
    return folders_and_parts

def _format_name(name, naming_strategy: NamingStrategy):
    formatted_name = name
    if naming_strategy is NamingStrategy.SPACE:
        formatted_name = string.capwords(formatted_name.strip().replace('_', ' '))
    elif naming_strategy is NamingStrategy.UNDERSCORE:
        formatted_name = formatted_name.lower().replace(' ', '_')
    return formatted_name

def _format_path_name(path, naming_strategy: NamingStrategy):
    return '/'.join([_format_name(folder, naming_strategy) for folder in path.split('/')])

def _format_part_name(name, naming_strategy: NamingStrategy, format, count = 1):
    formatted_name = name + ('_{}'.format(count) if count > 1 else '')
    formatted_name = _format_name(formatted_name, naming_strategy)
    return formatted_name + format

def _get_exportable_args(exportable: Exportable, config: ExportConfig):
    args=[
        config.openscad_location,
        config.export_file_path
    ]
    if config.manifold_supported:
        args.append('--enable=manifold')
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

def _export_file(config: ExportConfig, folder_path, exportable: Exportable):
    output_format = exportable.output_format
    if isinstance(exportable, Model):
        output_format = output_format if output_format else config.default_model_format

    output_file_name = _format_part_name(exportable.file_name, config.output_naming_strategy, output_format)

    formatted_folder_path = _format_path_name(folder_path, config.output_naming_strategy)
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
            part_copy_name = _format_part_name(exportable.file_name, config.output_naming_strategy, output_format, count)
            shutil.copy(output_directory + output_file_name, output_directory + part_copy_name)
            output += '\nFinished exporting: ' + formatted_folder_path + '/' + part_copy_name
    else:
        output = 'Failed to export: "{}/{}", Error: "{}"'.format(formatted_folder_path, output_file_name, err.decode('UTF-8').strip())
    return output

def export(nested_exportables, config: ExportConfig = None):
    if config is None:
        config = ExportConfig()

    if config.initialized:
        with ThreadPoolExecutor(max_workers = config.parallelism) as executor:
            print('Starting export')
            futures = []
            folders_and_exportables = _flatten_folders(nested_exportables)
            for folder_path, exportables in folders_and_exportables.items():
                for exportable in exportables:
                    futures.append(executor.submit(_export_file, config, folder_path, exportable))
            for future in futures:
                print(future.result())
            print('Done!')
    else:
        print('Export skipped because config was not initialized.')
