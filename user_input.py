from sys import exit
from .validation import Validation, is_in_list

def value_prompt(input_name, validation: Validation):
    input_template = 'Enter {} or "q" to quit: '
    input_value = input(input_template.format(input_name))
    while not validation.is_valid(input_value) and input_value.strip().lower() != 'q':
        print('{}: "{}" invalid'.format(input_name, input_value))
        input_value = input(input_template.format(input_name))
    if input_value.strip().lower() == 'q':
        exit('Quitting.')
    return validation.is_valid(input_value)

def option_prompt(input_name, validation: Validation, choices = []):
    valid_choices = [choice for choice in choices if validation.is_valid(choice)]
    valid_choices.append('[Enter custom value]')
    choice_count = len(valid_choices)
    if choice_count > 1:
        prompt = ''
        for index, choice in enumerate(valid_choices):
            prompt += '  {} - {}\n'.format(index + 1, choice)
        print('\nChoose {}:\n{}'.format(input_name, prompt))

        choice_select_validation = Validation(is_in_list, list=list(range(1, choice_count + 1)))
        selected_choice = value_prompt("option number", choice_select_validation)
    if choice_count == 1 or str(selected_choice) == str(choice_count):
        return value_prompt(input_name, validation)
    else:
        return validation.is_valid(valid_choices[int(selected_choice) - 1])
