import os
import sys
import types

# Make the src/ layout importable without requiring an install.
_SRC = os.path.join(os.path.dirname(__file__), '..', 'src')
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

# scad_export.user_input imports tkinter at module load. The code under test
# never opens a GUI, so stub tkinter to keep the suite hermetic (no Tk runtime
# or display required, e.g. on CI runners).
if 'tkinter' not in sys.modules:
    tk = types.ModuleType('tkinter')
    tk.Tk = object
    tk.filedialog = types.ModuleType('tkinter.filedialog')
    sys.modules['tkinter'] = tk
    sys.modules['tkinter.filedialog'] = tk.filedialog
