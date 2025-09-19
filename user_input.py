from sys import exit
from .validation import Validation, is_in_list
from tkinter import filedialog, Tk
import ctypes
import platform
from functools import cached_property

class Picker():
    def __init__(self, initial_directory, window_title=''):
        self.initial_directory = initial_directory
        self.window_title = window_title

    @cached_property
    def _root_window(self):
        if platform.system() == 'Windows':
            ctypes.windll.user32.SetProcessDPIAware()
        root = Tk()
        root.wm_attributes('-alpha', 0)
        root.wm_attributes('-topmost', 1)
        return root

    def get_value(self):
        pass

class DirectoryPicker(Picker):
    def __init__(self, initial_directory, window_title='Choose Directory'):
        super().__init__(initial_directory, window_title)

    def get_value(self):
        root = super()._root_window
        root.update()
        value = filedialog.askdirectory(parent=root, title=self.window_title, initialdir=self.initial_directory)
        return value

class FilePicker(Picker):
    def __init__(self, initial_directory, window_title='Choose File', file_types:tuple=None):
        super().__init__(initial_directory, window_title)
        if not file_types:
            file_types=[("All Files", "*.*")]
        self.file_types = file_types

    def get_value(self):
        root = super()._root_window
        root.update()
        value = filedialog.askopenfilename(parent=root, title=self.window_title, initialdir=self.initial_directory, filetypes=self.file_types)
        return value

def picker_prompt(input_name, validation: Validation, picker: Picker):
    input_value = picker.get_value()
    while not validation.is_valid(input_value) and input_value.strip().lower() != 'q':
        input_value = input('{}: "{}" invalid.\nPress [Enter] to retry, or type "q" to quit: '.format(input_name, input_value))
        if input_value.strip().lower() == 'q':
            exit('Quitting.')
        else:
            input_value = picker.get_value()
    return validation.is_valid(input_value)

def value_prompt(input_name, validation: Validation):
    input_template = 'Enter {} or type "q" to quit: '
    input_value = input(input_template.format(input_name))
    while not validation.is_valid(input_value) and input_value.strip().lower() != 'q':
        print('{}: "{}" invalid'.format(input_name, input_value))
        input_value = input(input_template.format(input_name))
    if input_value.strip().lower() == 'q':
        exit('Quitting.')
    return validation.is_valid(input_value)

def option_prompt(input_name, validation: Validation, choices = None, picker: Picker = None):
    picker_choice = None
    terminal_choice = None

    if choices is None:
        choices = []
    else:
        choices = list(dict.fromkeys(choices))
    valid_choices = [choice for choice in choices if validation.is_valid(choice)]

    if picker:
        valid_choices.append('[Enter custom value using file picker]')
        picker_choice = len(valid_choices)
    valid_choices.append('[Enter custom value using terminal]')
    terminal_choice = len(valid_choices)

    choice_count = len(valid_choices)
    if choice_count > 1:
        prompt = ''
        for index, choice in enumerate(valid_choices):
            prompt += '  {} - {}\n'.format(index + 1, choice)
        print('\nChoose {}:\n{}'.format(input_name, prompt))
        choice_select_validation = Validation(is_in_list, list=list(range(1, choice_count + 1)))
        selected_choice = value_prompt("option number", choice_select_validation)

    if choice_count == 1 or int(selected_choice) == terminal_choice:
        return value_prompt(input_name, validation)
    elif int(selected_choice) == picker_choice:
        return picker_prompt(input_name, validation, picker)
    else:
        return validation.is_valid(valid_choices[int(selected_choice) - 1])
