import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen, PIPE
from .export_config import ExportConfig
from .part import Part, Folder

def is_part_definition(dictionary):
    return all(not isinstance(value, dict) for value in dictionary.values())

def flatten_to_folders_and_parts(item, current_path = '', folders_and_parts = {}):
    if isinstance(item, Part):
        folders_and_parts.setdefault(current_path, []).append(item)
    elif isinstance(item, Folder):
        for subitem in item.contents:
            folders_and_parts.update(flatten_to_folders_and_parts(subitem, current_path + '/' + item.name, folders_and_parts))
    return folders_and_parts

def generate_part_stl(config: ExportConfig, output_directory, folder, part: Part):
    part_file_name = part.file_name + '.stl'

    os.makedirs(output_directory, exist_ok=True)

    args = [
        config.get_openscad_location(),
        '-o' + output_directory + part_file_name,
        config.get_export_file_path()
    ] + part.get_additional_args()

    if config.get_manifold_support():
        args.append('--enable=manifold')

    process = Popen(args, stdout=PIPE, stderr=PIPE)
    _, err = process.communicate()

    output = ""
    if (process.returncode == 0):
        output = 'Finished generating: ' + folder + '/' + part.file_name
        count = part.quantity
        for count in range(2, count + 1):
            part_copy_name = part.file_name + '_' + str(count) + '.stl'
            shutil.copy(output_directory + part_file_name, output_directory + part_copy_name)
            output += '\nFinished generating: ' + folder + '/' + part_copy_name
    else:
        output = 'Failed to generate: ' + folder + '/' + part.file_name + ', Error: ' + str(err)
    return output

def generate_parts(parts, threads = os.cpu_count()):
    config = ExportConfig()
    with ThreadPoolExecutor(max_workers = threads) as executor:
        print('Starting STL generation')
        futures = []
        for folder, part_group in flatten_to_folders_and_parts(parts).items():
            output_directory = config.get_stl_output_directory() + folder + '/'
            for part in part_group:
                futures.append(executor.submit(generate_part_stl, config, output_directory, folder, part))
        for future in futures:
            print(future.result())
        print('Done!')
