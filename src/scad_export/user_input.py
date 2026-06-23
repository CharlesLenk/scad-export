import ctypes
import platform
from functools import cached_property
from tkinter import Tk, filedialog

class Picker():
    def __init__(self, initial_directory, window_title=''):
        self.initial_directory = initial_directory
        self.window_title = window_title

    @cached_property
    def _root_window(self):
        # Prevents blurry picker window for Windows
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
        self.file_types = file_types

    def get_value(self):
        root = super()._root_window
        root.update()
        if self.file_types:
            value = filedialog.askopenfilename(parent=root, title=self.window_title, initialdir=self.initial_directory, filetypes=self.file_types)
        else:
            value = filedialog.askopenfilename(parent=root, title=self.window_title, initialdir=self.initial_directory)
        return value

class Option:
    def __init__(self, display_name, value):
        self.display_name = display_name
        self.value = value

    def __str__(self):
        return self.display_name
    
    def __repr__(self):
        return self.display_name

class Validation:
    def __init__(self, validation_function, **kwargs):
        self.validation_function = validation_function
        self.kwargs = kwargs

    def is_valid(self, value):
        return self.validation_function(value, **self.kwargs)
            
def _is_in_list(value, list):
    return value if str(value).lower() in [str(item).lower() for item in list] else ''

def picker_prompt(input_name, validation: Validation, picker: Picker):
    input_value = picker.get_value()
    while not validation.is_valid(input_value):
        input_value = input('{}: "{}" invalid.\nPress [Enter] to retry, or type "q" to quit: '.format(input_name, input_value))
        if input_value.strip().lower() == 'q':
            raise Exception('User quit.')
        else:
            input_value = picker.get_value()
    return input_value

def value_prompt(input_name, validation: Validation):
    input_template = 'Enter {} or type "q" to quit: '
    input_value = input(input_template.format(input_name))
    while not validation.is_valid(input_value) and input_value.strip().lower() != 'q':
        print('{}: "{}" invalid'.format(input_name, input_value))
        input_value = input(input_template.format(input_name))
    if input_value.strip().lower() == 'q':
        raise Exception('User quit.')
    return input_value

def option_prompt(input_name, validation: Validation, options = None, picker: Picker = None):
    picker_option = '[Enter custom value using file picker]'
    terminal_option = '[Enter custom value using terminal]'
    # Remove duplicates while preserving order
    options = list(dict.fromkeys(options)) if options else []
    
    valid_options = {}
    for option in options:
        option_value = option.value if isinstance(option, Option) else option
        if validation.is_valid(option_value):
            valid_options[len(valid_options) + 1] = option

    if picker:
        valid_options[len(valid_options) + 1] = picker_option
    valid_options[len(valid_options) + 1] = terminal_option

    selected_option = 1
    if len(valid_options) > 1:
        prompt = ''
        for option_number, option in valid_options.items():
            prompt += '  {} - {}\n'.format(option_number, option)
        print('\nChoose {}:\n{}'.format(input_name, prompt))
        option_select_validation = Validation(_is_in_list, list=valid_options.keys())
        selected_option = int(value_prompt("option number", option_select_validation))

    choice = valid_options[selected_option]
    if choice == terminal_option:
        return value_prompt(input_name, validation)
    elif choice == picker_option:
        return picker_prompt(input_name, validation, picker)
    else:
        return choice.value if isinstance(choice, Option) else choice
