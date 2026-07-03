class ScadExportError(Exception):
    pass

class ConfigError(ScadExportError):
    pass

class UserQuitError(ScadExportError):
    pass
