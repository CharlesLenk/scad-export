import logging
import shutil
import string
import subprocess
from concurrent.futures import ThreadPoolExecutor
from numbers import Number
from pathlib import Path

from .export_config import ExportConfig, NamingFormat
from .exceptions import MeshRepairError
from .exportable import Exportable, Folder, Image, Model
from .mesh_repair import check_available, repair_mesh_file

logger = logging.getLogger(__name__)


def _flatten_paths(item, current_path = '', paths_and_exportables = None):
    if paths_and_exportables is None:
        paths_and_exportables = {}
    if isinstance(item, Exportable):
        paths_and_exportables.setdefault(current_path, []).append(item)
    elif isinstance(item, Folder):
        for subitem in item.contents:
            _flatten_paths(subitem, f'{current_path}/{item.name}', paths_and_exportables)
    return paths_and_exportables

def _format_name(name, naming_format: NamingFormat):
    formatted_name = name
    if naming_format is NamingFormat.TITLE_CASE:
        formatted_name = string.capwords(formatted_name.strip().replace('_', ' '))
    elif naming_format is NamingFormat.SNAKE_CASE:
        formatted_name = formatted_name.lower().replace(' ', '_')
    return formatted_name

def _format_path_name(path, naming_format: NamingFormat):
    return '/'.join(_format_name(folder, naming_format) for folder in path.split('/'))

def _format_part_name(name, naming_format: NamingFormat, file_format, user_args, count = 1):
    formatted_name = name
    for key, value in user_args.items():
        formatted_name += f'_({key}-{value})'
    if count > 1:
        formatted_name += f'_{count}'
    return _format_name(formatted_name, naming_format) + file_format

def _get_exportable_args(exportable: Exportable, config: ExportConfig):
    args = [
        config.openscad_location,
        config.export_file_path
    ]
    if config.manifold_supported:
        args.append('--backend=Manifold')
    args.append(f'-Dname="{exportable.name}"')
    for arg, value in exportable.user_args.items():
        if isinstance(value, bool):
            args.append(f'-D{arg}={"true" if value else "false"}')
        elif isinstance(value, Number):
            args.append(f'-D{arg}={value}')
        elif isinstance(value, str):
            args.append(f'-D{arg}="{value}"')

    if isinstance(exportable, Image):
        args.append(f'--camera={exportable.camera_position}')
        color_scheme = exportable.color_scheme if exportable.color_scheme else config.default_image_color_scheme
        args.append(f'--colorscheme={color_scheme}')
        image_size = exportable.image_size if exportable.image_size else config.default_image_size
        args.append(f'--imgsize={image_size.width},{image_size.height}')
        if config.manifold_supported:
            args.append('--render=true')
        else:
            args.append('-D$fs=0.4')
            args.append('-D$fa=0.8')

    return args

def _export_file(folder_path, exportable: Exportable, config: ExportConfig):
    file_format = exportable.file_format
    if isinstance(exportable, Model):
        file_format = file_format if file_format else config.default_model_format

    output_file_name = _format_part_name(exportable.file_name, config.output_naming_format, file_format, exportable.user_args)

    formatted_folder_path = _format_path_name(folder_path, config.output_naming_format)
    output_directory = config.output_directory + formatted_folder_path + '/'
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    args = _get_exportable_args(exportable, config)
    args.append('-o' + output_directory + output_file_name)

    logger.debug('OpenSCAD args for %s: %s', output_file_name, args)

    try:
        result = subprocess.run(args, capture_output=True, timeout=config.export_timeout)
    except subprocess.TimeoutExpired:
        return f'Failed to export: "{formatted_folder_path}/{output_file_name}", Error: "Timed out after {config.export_timeout}s"'

    if result.returncode == 0:
        if isinstance(exportable, Model) and exportable.mesh_repair:
            try:
                repair_mesh_file(output_directory + output_file_name)
            except MeshRepairError as e:
                return f'Failed to export: "{formatted_folder_path}/{output_file_name}", Error: "{e}"'

        output = f'Finished exporting: {formatted_folder_path}/{output_file_name}'
        for count in range(2, exportable.quantity + 1):
            part_copy_name = _format_part_name(exportable.file_name, config.output_naming_format, file_format, exportable.user_args, count)
            shutil.copy(output_directory + output_file_name, output_directory + part_copy_name)
            output += f'\nFinished exporting: {formatted_folder_path}/{part_copy_name}'
    else:
        output = f'Failed to export: "{formatted_folder_path}/{output_file_name}", Error: "{result.stderr.decode("UTF-8").strip()}"'
    return output

def export(exportables: Folder, config: ExportConfig | None = None):
    if config is None:
        config = ExportConfig()

    paths_and_exportables = _flatten_paths(exportables)
    if any(
        isinstance(exportable, Model) and exportable.mesh_repair
        for path_exportables in paths_and_exportables.values()
        for exportable in path_exportables
    ):
        check_available()

    with ThreadPoolExecutor(max_workers = config.parallelism) as executor:
        logger.info('Starting export')
        futures = []
        for path, path_exportables in paths_and_exportables.items():
            for exportable in path_exportables:
                futures.append(executor.submit(_export_file, path, exportable, config))
        for future in futures:
            logger.info(future.result())
        logger.info('Done!')
