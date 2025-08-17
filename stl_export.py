import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen, PIPE
from export_config import ExportConfig
from numbers import Number

def is_part_definition(dictionary):
    return all(not isinstance(value, dict) for value in dictionary.values())

def flatten_to_folders_and_parts(parts, current_path = ''):
    folders_and_parts = {}
    for key, value in parts.items():
        if is_part_definition(value):
            if folders_and_parts.get(current_path):
                folders_and_parts[current_path].update({ key: value })
            else:
                folders_and_parts[current_path] = { key: value }
        else:
            folders_and_parts.update(flatten_to_folders_and_parts(value, current_path + '/' + key))
    return folders_and_parts

def generate_part(export_config, output_directory, folder, part):
    part_file_name = part[0] + '.stl'
    os.makedirs(output_directory, exist_ok=True)

    args = [
        export_config.openSCADLocation,
        '-o' + output_directory + part_file_name,
        export_config.exportFilePath
    ]

    for arg, value in part[1].items():
        if isinstance(value, Number) and arg != 'quantity':
            args.append('-D' + arg + '=' + str(value))
        elif isinstance(value, str):
            args.append('-D' + arg + '="' + value + '"')

    if export_config.manifoldSupport:
        args.append('--enable=manifold')

    process = Popen(args, stdout=PIPE, stderr=PIPE)
    _, err = process.communicate()

    count = part[1].get('quantity', 1)
    output = ""
    if (process.returncode == 0):
        output += 'Finished generating: ' + folder + '/' + part_file_name
        for count in range(2, count + 1):
            part_copy_name = part[0] + '_' + str(count) + '.stl'
            shutil.copy(output_directory + part_file_name, output_directory + part_copy_name)
            output += '\nFinished generating: ' + folder + '/' + part_copy_name
    else:
        output += 'Failed to generate: ' + folder + '/' + part_file_name + ', Error: ' + str(err)
    return output

def print_parts(part_map):
    export_config = ExportConfig()
    with ThreadPoolExecutor(max_workers = os.cpu_count()) as executor:
        print('Starting STL generation')
        futures = []
        for folder, part_group in flatten_to_folders_and_parts(part_map).items():
            output_directory = export_config.stlOutputDirectory + folder + '/'
            for part in part_group.items():
                futures.append(executor.submit(generate_part, export_config, output_directory, folder, part))
        for future in futures:
            print(future.result())
        print('Done!')
