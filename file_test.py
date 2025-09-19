import json
import os
import sys
import re
from subprocess import Popen, PIPE
from functools import cached_property
from threading import Lock
from enum import StrEnum, auto
from pathlib import Path
from tkinter import filedialog, Tk
import ctypes


# ctypes.windll.user32.SetProcessDPIAware()
root = Tk()
root.wm_attributes('-alpha', 0)
root.wm_attributes('-topmost', 1)
test = filedialog.askdirectory(parent=root)
test = filedialog.askopenfilename(parent=root)
print(test)

