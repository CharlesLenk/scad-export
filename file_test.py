import json
import os
import sys
import re
from subprocess import Popen, PIPE
from functools import cached_property
from threading import Lock
from enum import StrEnum, auto
from pathlib import Path
from tkinter import filedialog
import ctypes

ctypes.windll.user32.SetProcessDPIAware()

test = filedialog.askdirectory()
print(test)