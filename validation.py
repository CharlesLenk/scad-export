import os
import platform
import shutil
import sys
    
class Validation:
    def __init__(self, validation_function, additional_args = []):
        self.validation_function = validation_function
        self.additional_args = additional_args

    def is_valid(self, value):
        return self.validation_function(*([value] + self.additional_args))

def is_openscad_location_valid(location):
    # If MacOS and executable not found, try pathing to it in .app package.
    if platform.system() == 'Darwin' and shutil.which(location) is None:
        location += '/Contents/MacOS/OpenSCAD'
    return location if shutil.which(location) is not None else ''

def is_directory(directory):
    return directory if os.path.isdir(directory) else ''

def is_path_writable(directory):
    return directory if os.access(os.path.dirname(directory), os.W_OK) else ''
            
def get_file_path(search_directory, file_name):
    file_path = ''
    for root, _, files in os.walk(search_directory):
        if file_name in files:
            file_path = str(os.path.join(root, file_name))
    return file_path

def is_file_with_extension(file_name, extension, search_directory):
    file_path = get_file_path(search_directory, file_name)
    return file_path if file_name.lower().endswith(extension) and file_path else ''

def is_in_list(value, list):
    value = str(value).lower()
    return value if value in [str(item).lower() for item in list] else ''

def value_prompt(input_name, validation: Validation):
    input_value = input('Enter {} or "q" to quit: '.format(input_name))
    while not validation.is_valid(input_value) and input_value.strip().lower() != 'q':
        print('{}: "{}" invalid'.format(input_name, input_value))
        input_value = input('Enter {} or "q" to quit: '.format(input_name))
    if input_value.strip().lower() == 'q':
        sys.exit('Quitting.')
    return validation.is_valid(input_value)

def option_prompt(input_name, validation: Validation, choices = []):
    prompt = ''
    valid_choices = [choice for choice in choices if validation.is_valid(choice)]
    choice_count = len(valid_choices) + 1
    if choice_count > 1:
        for index, choice in enumerate(valid_choices):
            prompt += '  ' + str(index + 1) + ' - ' + choice + '\n'
        prompt+= '  ' + str(choice_count) + ' - ' + "[Enter custom value]" + '\n'

        print('\nChoose ' + input_name + ':')
        print(prompt)
        choice_select_validation = Validation(is_in_list, [list(range(1, choice_count + 1))])
        selected_choice = value_prompt("option number", choice_select_validation)
    if choice_count == 1 or str(selected_choice) == str(choice_count):
        return value_prompt(input_name, validation)
    else:
        return validation.is_valid(valid_choices[int(selected_choice) - 1])
