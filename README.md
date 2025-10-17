# SCAD Export

OpenSCAD is a powerful parametric modeling program, but has some limitations. One of these limitations is that exporting models in OpenSCAD is a manual process, which makes exporting a large number of parts to separate files or folders tedious and slow. This project aims to address that limitation by allowing the parts and folder paths to be defined programmatically, and using multithreading to render parts in parallel, leading to an overall much faster and automated export for complex projects.

# Installation

## Prerequisites

* [Python](https://www.python.org/downloads/) - Python 3.13 or newer is needed to run this script.
* [OpenSCAD](https://openscad.org/) - OpenSCAD should be installed on your system, preferably in the default location for your OS.
* [Git](https://git-scm.com/) - While not strictly required, if used in a git project, SCAD Export will use git to perform auto-detection of required files and directories.

## Adding SCAD Export to Your Project

### Using pip (Recommended)

This project is available via pip.

`python3 -m pip install scad_export`

For Python package installation instructions, see the [Python docs](https://packaging.python.org/en/latest/tutorials/installing-packages/).

### Downloading the source files

You can also install using less recommended options like:

* Adding the project as a git submodule (for git projects):

    `git submodule add https://github.com/CharlesLenk/scad_export.git`

* Cloning the project, or downloading and extracting the zip, into your project folder.

If not installed using pip you'll need to either use relative imports, or write your Python code in the same folder as the scad_export Python files.

# Usage

## Writing the SCAD Export Map

A `.scad` file is needed to define the parts to export. This file should contain an `if/else` statement that selects which part to render by a variable called "name". A file called `export map.scad` which demonstrates this pattern is available in the [example project](https://github.com/CharlesLenk/scad-export-example?tab=readme-ov-file#example-export-mapscad).

For most projects, it's easiest to use this script by having a single `export map.scad` file which imports all parts that you want to export from separate `.scad` files.

It's not required to use the `export map.scad` naming convention, however the SCAD Export config will attempt to auto-detect files ending with the name `export map.scad`.

## Writing the Export Script

The export script does two things:

1. Configures the list of files to export, and the folder structure.
2. Invokes the `export()` function to run the export logic.

The parts to export and folder structure are defined using Python. An example of how to configure parts and folders is available in the [example project](https://github.com/CharlesLenk/scad-export-example?tab=readme-ov-file#export_examplepy).

The supported exportable parts are below. Click the links to see the parameters for each type.

* [Folder](#folder) - Contains Models, Drawings, Images, and Folders. The folder structure of the exported files will follow the folder structure configured in your export script.
* [Model](#model) - Supports exporting 3D models to the 3MF or STL formats.
* [Drawing](#drawing) - Supports exporting a 2D OpenSCAD project to the DXF format.
* [Image](#image) - Supports exporting an image of a model to the PNG format.

After defining the parts and folder structure, your export script should call the `export()` function with your parts and folders as an argument like in the [example](https://github.com/CharlesLenk/scad-export-example/blob/main/export_example.py#L38).

## Running

After [writing your export script](#writing-the-export-script), run it using Python.

### System Configuration

When first run, the configuration will attempt to load a saved config file. If not found, it will search for following automatically:
* The location of OpenSCAD on your computer. This will check if `openscad` is on your system path, then search the default install locations for your operating system.
    * This will also check if your installed OpenSCAD supports Manifold, a much faster rendering engine added starting with the 2024 OpenSCAD development preview. If available, Manifold will be used when rendering.
* The root directory of the current git project, or the directory of your export script if a git project is not found.
* A `.scad` file in the project root that defines each part to export.
    * The auto-detection looks specifically for files ending with the name `export map.scad`, but any name can be used if manually selecting a file.
* A directory to export the rendered files to.

For each of the above, the script will issue a command line prompt that will let you select from the available defaults detected. If the script fails to find a valid default, or if you choose not to use the default, you'll be prompted for the value to use. Custom values can be entered using file picker (recommended), or using the command line directly.

In addition to the user-selected values above, the export config supports additional optional [configuration values](#exportconfig) such as setting the default export type for model files, or configuring how many threads to use while exporting.

#### Export Config File

The config values you select will be saved to a file called `export config.json` in the same directory as your Python script. The values in this file will be checked each time the script is run, but won't reprompt unless they are found to be invalid. To force a reprompt, delete the specific value you want to be reprompted for, or delete the `export config.json` file.

* If you're using SCAD export in a git project, add `export config.json` to your `.gitignore` file. Since the configuration values are specific to your computer, uploading them will cause misconfigurations for other users exporting your project.

# API Documentation

## Export

The `export()` function is invoked to export your files and folders.

### Import Path

`scad_export.export.export`

### Export Parameters

|field name|type|default|description|
|-|-|-|-|
|nested_exportables|`Folder`|`N/A` (Required)|A structure containing the files and folders to export.|
|config|`ExportConfig`|An `ExportConfig` instance without [additional parameters](#exportconfig-parameters) set.|System configuration and default values to use when exporting.|

## ExportConfig

The export configuration also supports additional parameters to configure defaults to use for all exports of a type, or to configure how the export itself runs. To set these options create an instance of the export config and pass the desired arguments like in the [image export example](https://github.com/CharlesLenk/scad-export-example/blob/main/image_export_example.py#L19). Make sure to pass the modified export config to the `export` function as a argument, also demonstrated in the example.

### Import Path

`scad_export.export_config.ExportConfig`

### ExportConfig Parameters

|field name|type|default|description|
|-|-|-|-|
|output_naming_strategy|`export_config.NamingStrategy`|`NamingStrategy.SPACE`|The output file name format. The values supported are `NamingStrategy.SPACE` which formats the file names with spaces, and `NamingStrategy.UNDERSCORE` which formats the file names as lower case separated by underscores.|
|default_model_format|`exportable.ModelFormat`|`ModelFormat._3MF`|The default file type for exported models. Supported values are `ModelFormat._3MF` and `ModelFormat.STL`. If you want to override the model type for a single part, use the [model level setting](#model-parameters).|
|default_image_color_scheme|`exportable.ColorScheme`|`ColorScheme.CORNFIELD`|The default color scheme to use for exported images. Supports all OpenSCAD color schemes. To override the color scheme for a single image, use the [image level setting](#image-parameters).|
|default_image_size|`exportable.ImageSize`|`ImageSize(1600, 900)`|The default image resolution to use for exported images. To override the resolution for a single image, use the [image level setting](#image-parameters).|
|parallelism|`integer`|System CPU count.|The number of parts to render in parallel. If you want to reduce the performance impact of rendering while accepting longer run times, set this value to a number below the number of CPU cores. Setting this value to `1` will cause only one part to render at a time.|
|debug|`boolean`|`False`|Whether the export should output debug statements to the console.|

## Exportables

### Folder

Folders specify the folder structure that should be used for output files.

### Import Path

`scad_export.exportable.Folder`

### Folder Parameters

|field name|type|default|description|
|-|-|-|-|
|name|`string`|`N/A` (Required)|The `name` of the folder. If the name includes any slash separators (`/`), a separate folder will be created for each segment of the name separated by slashes. The name will be formatted using the [output_naming_strategy](#exportconfig-parameters).|
|contents|`list`|`N/A` (Required)|A list of other exportable types, including [Models](#model), [Drawings](#drawing), [Images](#image), and nested Folders.|

### Model

Supports exporting 3D models to the 3MF or STL formats.

### Import Path

`scad_export.exportable.Model`

### Model Parameters

|field name|type|default|description|
|-|-|-|-|
|name|`string`|`N/A` (Required)|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|file_name|`string`|The `name` formatted using the [output_naming_strategy](#exportconfig-parameters).|The name to use for the output file.|
|quantity|`integer`|`1`|The number of copies of the exported part to create. The copies are made using filesystem copy, rather than rendering the part multiple times.|
|format|`exportable.ModelFormat`|[default_model_format](#exportconfig-parameters)|The output format to use for the model. Supported values are `ModelFormat._3MF` and `ModelFormat.STL`. To set the default for all models, set the [default_model_format](#exportconfig-parameters).|
|[any]|`string` or `number`|No default|Additional arguments can be defined dynamically and will be passed to your `.scad` file when rendering. For example, if you provide the argument "size = 5", then that's the same as having a variable in your `.scad` file called "size" with a value of "5".|

### Drawing

Supports exporting a 2D OpenSCAD project to the DXF format.

### Import Path

`scad_export.exportable.Drawing`

### Drawing Parameters

|field name|type|default|description|
|-|-|-|-|
|name|`string`|`N/A` (Required)|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|file_name|`string`|The `name` formatted using the [output_naming_strategy](#exportconfig-parameters).|The name to use for the output file.|
|quantity|`integer`|`1`|The number of copies of the exported part to create. The copies are made using filesystem copy, rather than rendering the part multiple times.|
|[any]|`string` or `number`|No default|Additional arguments can be defined dynamically and will be passed to your `.scad` file when rendering. For example, if you provide the argument "size = 5", then that's the same as having a variable in your `.scad` file called "size" with a value of "5".|

### Image

Supports exporting an image of a model to the PNG format.

### Import Path

`scad_export.exportable.Image`

### Image Parameters

|field name|type|default|description|
|-|-|-|-|
|name|`string`|`N/A` (Required)|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|camera_position|`string`|`N/A` (Required)|The camera position to use for the picture of the model. The camera coordinates can be found at the bottom of the OpenSCAD application window when previewing a model. To make copying the coordinates easier, a custom function like [echo cam](https://github.com/CharlesLenk/openscad-utilities/blob/main/render.scad#L18) can be used to output the camera position to the OpenSCAD console.|
|file_name|`string`|The `name` formatted using the [output_naming_strategy](#exportconfig-parameters).|The name to use for the output file.|
|image_size|`exportable.ImageSize`|[default_image_size](#exportconfig-parameters)|The resolution of the output image. If you want all images to use the same resolution, set the [default_image_size](#exportconfig-parameters).|
|color_scheme|`exportable.ColorScheme`|[default_image_color_scheme](#exportconfig-parameters)|Overrides the color scheme to use when taking the image. To set the default for all images, set the [default_image_color_scheme](#exportconfig-parameters).|
|[any]|`string` or `number`|No default|Additional arguments can be defined dynamically and will be passed to your `.scad` file when rendering. For example, if you provide the argument "size = 5", then that's the same as having a variable in your `.scad` file called "size" with a value of "5".|

# Project Files

High-level overview of the files in this project.

* export_config.py
    * Primary configuration for the export. Contains default values. Reads and writes `export config.json`.
* export.py
    * Formats arguments and invokes OpenSCAD in parallel for exporting parts.
* exportable.py
    * Classes for configuring the different types of objects that can be exported.
* user_input.py
    * Functions for collecting input from the user.
* validation.py
    * Validation functions for config values.
