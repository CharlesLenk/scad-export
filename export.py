import os
import shutil
import string
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen, PIPE
from .export_config import ExportConfig, NamingStrategy
from .exportable import Folder, Exportable

def flatten_folders(item, current_path = '', folders_and_parts = {}):
    if isinstance(item, Exportable):
        folders_and_parts.setdefault(current_path, []).append(item)
    elif isinstance(item, Folder):
        for subitem in item.contents:
            folders_and_parts.update(flatten_folders(subitem, current_path + '/' + item.name, folders_and_parts))
    return folders_and_parts

def format_name(name, naming_strategy: NamingStrategy):
    formatted_name = name
    if naming_strategy is NamingStrategy.SPACE:
        formatted_name = string.capwords(formatted_name.strip().replace('_', ' '))
    elif naming_strategy is NamingStrategy.UNDERSCORE:
        formatted_name = formatted_name.lower().replace(' ', '_')
    return formatted_name

def format_path_name(path, naming_strategy: NamingStrategy):
    return '/'.join([format_name(folder, naming_strategy) for folder in path.split('/')])

def format_part_name(name, naming_strategy: NamingStrategy, format, count = 1):
    formatted_name = name + ('_{}'.format(count) if count > 1 else '')
    formatted_name = format_name(formatted_name, naming_strategy)
    return formatted_name + format

def export_file(config: ExportConfig, folder, exportable: Exportable):
    output_file_name = format_part_name(exportable.file_name, config.get_output_naming_strategy(), exportable.get_output_format())

    output_directory = config.get_output_directory() + folder + '/'
    os.makedirs(output_directory, exist_ok=True)

    args = config.get_common_args() + exportable.format_args()
    args.append('-o' + output_directory + output_file_name)

    if config.debug:
        print('OpenSCAD args for {}:'.format(output_file_name))
        print(args)
        print()

    process = Popen(args, stdout=PIPE, stderr=PIPE)
    _, err = process.communicate()

    output = ""
    if (process.returncode == 0):
        output = 'Finished exporting: ' + folder + '/' + output_file_name
        count = exportable.get_quantity()
        for count in range(2, count + 1):
            part_copy_name = format_part_name(exportable.file_name, config.get_output_naming_strategy(), exportable.get_output_format(), count)
            shutil.copy(output_directory + output_file_name, output_directory + part_copy_name)
            output += '\nFinished exporting: ' + folder + '/' + part_copy_name
    else:
        output = 'Failed to export: ' + folder + '/' + output_file_name + ', Error: ' + str(err)
    return output

def export_files(nested_exportables, config: ExportConfig = ExportConfig(), threads = os.cpu_count()):
    with ThreadPoolExecutor(max_workers = threads) as executor:
        print('Starting export')
        futures = []
        folders_and_exportables = flatten_folders(nested_exportables)
        for folder, exportables in folders_and_exportables.items():
            folder_name = format_path_name(folder, config.get_output_naming_strategy())
            for exportable in exportables:
                futures.append(executor.submit(export_file, config, folder_name, exportable))
        for future in futures:
            print(future.result())
        print('Done!')
