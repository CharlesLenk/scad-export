# SCAD Export

OpenSCAD is a powerful parametric modeling program, but has some limitations. One of these limitations is that exporting models to files in OpenSCAD is a manual process, which makes exporting a large number of models to separate files or folders tedious and slow. This project aims to address that limitation by allowing the model and folder paths to be defined programmatically, and using multithreading to render models in parallel, leading to an overall much faster and automated export for complex projects.

## Usage Overview

1. Install the [prerequisites](#prerequisites).
2. Write an [export map](#writing-the-scad-export-map) SCAD file to export from.
    * For the basic pattern, see [example export map.scad](https://github.com/CharlesLenk/scad-export/blob/main/tests/examples/example%20export%20map.scad).
3. Write an [export Python script](#writing-the-export-script) to define the parts to export, and to invoke the `export()` function.
    * [export_example.py](https://github.com/CharlesLenk/scad-export/blob/main/tests/examples/export_example.py) provides an example that uses the example export map SCAD file above.
4. [Run your script](#running-and-system-configuration) and enter the configuration values as prompted.
5. For API reference and advanced configuration, see the [API documentation](API_DOC.md) and the [examples](https://github.com/CharlesLenk/scad-export/tree/main/tests/examples).

## Prerequisites

* [Python](https://www.python.org/downloads/) - Python 3.13 or newer is needed to run this script.
* [OpenSCAD](https://openscad.org/) - OpenSCAD should be installed on your system, preferably in the default location for your OS.
* [Git](https://git-scm.com/) - While not strictly required, if used in a git project, SCAD Export will use git to perform auto-detection of required files and directories.
* [Install SCAD Export](#install-scad-export).

### Install SCAD Export

This project is available via pip.

`python3 -m pip install scad_export`

For Python package installation instructions, see the [Python docs](https://packaging.python.org/en/latest/tutorials/installing-packages/).

<details>
<summary>Downloading the source files (expand for details)</summary>
<br>
You can also install using less recommended options like:

* Adding the project as a git submodule (for git projects):<br>`git submodule add https://github.com/CharlesLenk/scad_export.git`

* Cloning the project, or downloading and extracting the zip, into your project folder.

If not installed using pip you'll need to either use relative imports, or write your Python code in the same folder as the scad_export Python files.
</details>
<br>

## Writing the SCAD Export Map

A `.scad` file is needed to define the models to export. This file should contain an `if/else` statement that selects which part to render by a variable called "name". For an example of this pattern, see `example export map.scad` in the [examples directory](https://github.com/CharlesLenk/scad-export/tree/main/tests/examples#example-export-mapscad).

For most projects, it's easiest to use this script by having a single `export map.scad` file which imports all parts that you want to export from separate `.scad` files.

It's not required to use the `export map.scad` naming convention, however the SCAD Export config will attempt to auto-detect files ending with the name `export map.scad`.

## Writing the Export Script

The export script does two things:

1. Configures folders and exportables (Models, Drawings, and Images) to export.
2. Invokes the `export()` function to run the export logic.

The exportable and folder structure are defined using Python. An example of how to configure this structure is available in the [examples](https://github.com/CharlesLenk/scad-export/tree/main/tests/examples#export_examplepy).

All exportables must be contained in at least one folder.

* [Folder](API_DOC.md#folder) - Contains Models, Drawings, Images, and Folders. The folder structure of the exported files will follow the folder structure configured in your export script.

The supported types of exportable are below. Click the links to see the full parameters for each type.

* [Model](API_DOC.md#model) - Supports exporting 3D models to the 3MF or STL formats.
* [Drawing](API_DOC.md#drawing) - Supports exporting a 2D OpenSCAD project to the DXF format.
* [Image](API_DOC.md#image) - Supports exporting an image of a model to the PNG format.

To configure defaults for all types or other export-level settings like the number of threads to use, see the [ExportConfig documentation](API_DOC.md#exportconfig).

After defining the exportables, your export script should call the `export()` function with your exportables as an argument like at the bottom of the [example script](https://github.com/CharlesLenk/scad-export/blob/main/tests/examples/export_example.py).

## Running and System Configuration

After [writing your export script](#writing-the-export-script), run it using Python.

When first run, the configuration will attempt to load a saved config file with system-specific settings. If not found, it will search for following:

1. The location of OpenSCAD on your computer. This will check if `openscad` is on your system path, then search the default install locations for your operating system.
    * This will also check if your installed OpenSCAD supports Manifold, a much faster rendering engine added starting with the 2024 OpenSCAD development preview. If available, Manifold will be used when rendering.
2. The root directory of the current git project, or the directory of your export script if a git project is not found.
3. A `.scad` file in the project root that defines each part to export.
    * The auto-detection looks specifically for files ending with the name `export map.scad`, but any name can be used if manually selecting a file.
4. A directory to export the rendered files to.

For each of the above, a command line prompt will let you select from the available defaults detected. If the script fails to find a valid default, or if you choose not to use the default, you'll be prompted for the value to use. Custom values can be entered using file picker (recommended), or using the command line directly.

The config values you select will be saved to a file called `export config.json` in the same directory as your Python script. The values in this file will be checked each time the script is run, but won't reprompt unless they are found to be invalid. To force a reprompt, delete the specific value you want to be reprompted for, or delete the `export config.json` file.

If you're using SCAD export in a git project, add `export config.json` to your `.gitignore` file. Since the configuration values are specific to your computer, uploading them will cause misconfigurations for other users exporting your project.
