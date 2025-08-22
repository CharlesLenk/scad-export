# openscad-export
Script for parallel export of OpenSCAD parts.

# Usage

## Prequisitsss

### Python
(Python 3)[https://www.python.org/downloads/] is needed to run this script.

### Git
This script will perform some autoconfiguration when first run. For the autoconfiguration to work:
* Git must be installed and on your classpath.
* The script must be run from a Git repository that your project files are in.
The autoconfiguration isn't required to use the script, you'll just need to manually input the root folder the script should use for your project.

## Configuration

### Add the script to your project

* For Git projects, use `git submodule add https://github.com/CharlesLenk/openscad_export.git`
* For non-Git projects, clone the script and copy it into your project folder.

### Autoconfiguration
When first run, this script will attempt to find the following automatically:
* The location of OpenSCAD on your system. This will search the default install location for Windows, MacOS, and Linux.
* The root directory of the current Git project.
* A `.scad` file that defines each part to export.
* The current `Desktop` folder to export the STL files to.

For each of these values, the script will prompt if you want to use the default. If the script fails to find the default, or if you choose not to use the default, you'll be prompted for the value to use.

The script will also check if your current version of OpenSCAD supports Manifold.




This script is intended to be added as a submodule to a Git project, but will also work in other contexts.

* export_config.py
    * Functions for reading and writing export config values. Does nothing if run directly.
* stl_export.py
    * Exports STLs for the project.

