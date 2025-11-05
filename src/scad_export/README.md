# Project Files

High-level overview of the files in this project.

|File|Summary|
|-|-|
|export_config.py|Primary configuration for the export. Uses `export config.json` to read and write system level configuration. Also contains default values for the export.|
|export.py|Creates directories, formats arguments, and invokes OpenSCAD in parallel to export files.|
|exportable.py|Classes for configuring the different types of objects that can be exported.|
|user_input.py|Functions for collecting input from the user. Used during auto-configuration of system-level settings.|
