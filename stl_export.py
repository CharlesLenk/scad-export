import os
import shutil
import string
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen, PIPE
from .export_config import ExportConfig, NamingStrategy
from .part import Folder, Part, Image

def is_part_definition(dictionary):
    return all(not isinstance(value, dict) for value in dictionary.values())

def flatten_to_folders_and_parts(item, current_path = '', folders_and_parts = {}):
    if isinstance(item, Part):
        folders_and_parts.setdefault(current_path, []).append(item)
    elif isinstance(item, Folder):
        for subitem in item.contents:
            folders_and_parts.update(flatten_to_folders_and_parts(subitem, current_path + '/' + item.name, folders_and_parts))
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

def generate_part_stl(config: ExportConfig, output_directory, folder, part: Part):
    part_file_name = format_part_name(part.file_name, config.get_part_naming_strategy(), '.stl')
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
        output = 'Finished generating: ' + folder + '/' + part_file_name
        count = part.quantity
        for count in range(2, count + 1):
            part_copy_name = format_part_name(part.file_name, config.get_part_naming_strategy(), '.stl', count)
            shutil.copy(output_directory + part_file_name, output_directory + part_copy_name)
            output += '\nFinished generating: ' + folder + '/' + part_copy_name
    else:
        output = 'Failed to generate: ' + folder + '/' + part_file_name + ', Error: ' + str(err)
    return output

def generate_image(config: ExportConfig, output_directory, folder, image: Image):
    image_file_name = image.name + '.png'

    args = [
        config.openScadLocation,
        '-Dpart="' + image.name + '"',
        '--camera=' + image.camera_position,
        '--colorscheme=Tomorrow Night',
        '--imgsize=2000,1200',
        '-o' + config.get_project_root() + '/instructions/images/' + image_file_name,
        config.get_project_root() + '/src/scad/assembly image map.scad'
    ]

    if config.get_manifold_support():
        args.extend(['--enable=manifold', '--render=true'])
    else:
        args.extend(['-D$fs=0.4', '-D$fa=0.8'])

    process = Popen(args, stdout=PIPE, stderr=PIPE)
    _, err = process.communicate()

    output = ""
    if (process.returncode == 0):
        output += 'Finished generating: ' + image_file_name
    else:
        output += 'Failed to generate: ' + image_file_name + ', Error: ' + str(err)
    return output

def generate_parts(parts, threads = os.cpu_count()):
    config = ExportConfig()
    with ThreadPoolExecutor(max_workers = threads) as executor:
        print('Starting STL generation')
        futures = []
        for folder, part_group in flatten_to_folders_and_parts(parts).items():
            formatted_folder_name = format_path_name(folder, config.get_part_naming_strategy())
            output_directory = config.get_stl_output_directory() + formatted_folder_name + '/'
            for part in part_group:
                futures.append(executor.submit(generate_part_stl, config, output_directory, formatted_folder_name, part))
        for future in futures:
            print(future.result())
        print('Done!')
