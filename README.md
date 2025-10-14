# OpenSCAD Export

OpenSCAD is a powerful parametric modeling program, but has some limitations. One of these limitations is that exporting models in OpenSCAD is a manual process, which makes exporting a large number of parts to separate files or folders tedious and slow. This project aims to address that limitation by allowing the parts and folder paths to be defined programmatically, and using multithreading to render parts in parallel, leading to an overall much faster and automated export for complex projects.

# Setup

## Prerequisites

* [Python](https://www.python.org/downloads/) - Python 3.13 or newer is needed to run this script.
* [OpenSCAD](https://openscad.org/) - OpenSCAD should be installed on your system, preferably in the default location for your OS.
* [Git](https://git-scm.com/) - While not strictly required, having git installed and on your classpath makes downloading and using this project easier.

## Adding the Script to a Project

This script is intended to be added as a submodule to a git project, but will also work in other contexts.

* For git projects, use the command below to add this project as a submodule:

    `git submodule add https://github.com/CharlesLenk/openscad_export.git`

* For non-git projects, use git to clone the script and copy it into your project folder.

# Usage

## Export Map Definition

A `.scad` file is needed to define the parts to export. For most projects, it's easiest to use this script by having a single `export map.scad` file which imports all parts that you want to export. This file should contain an `if/else` statement which selects the part by a variable called "name".

An example of the `export map.scad` file is available in the [example project](https://github.com/CharlesLenk/openscad-export-example?tab=readme-ov-file#example-export-mapscad).

## Export Script Definition

The parts to export and folder structure are defined in a Python script. 

The supported exportable parts are:
* [Model](#model) - Supports exporting 3D models to the 3MF or STL formats.
* [Drawing](#drawing) - Supports exporting a 2D OpenSCAD project to the DXF format.
* [Image](#images) - Supports exporting an image of a model to the PNG format.

Clink the links to see the parameters for each type. Additional key/value arguments provided will be passed to OpenSCAD as arguments. 



[see example project](A few examples of the part definition are provided in the [example project](https://github.com/CharlesLenk/openscad-export-example/tree/main?tab=readme-ov-file#scad-example).).

## Running

Run your export script using Python. When first run, the configuration will attempt to load a saved config file. If not found, it will search for following automatically:
* The location of OpenSCAD on your system. This will search the default install locations for Windows, MacOS, and Linux.
* The root directory of the current Git project, or the parent of the `openscad_export` folder if a git project is not found.
* A `.scad` file in the project root that defines each part to export.
    * The auto-detection looks specifically for files ending with the name `export map.scad`, but any name can be used if manually selecting a file.
* A valid folder to export the STL files to.

For each of the above, the script will issue a command link prompt if you want to use of the found if defaults. If the script fails to find the default, or if you choose not to use the default, you'll be prompted for the value to use. Custom values can be entered using file or directory picker (recommended), or using the command line directly.

The values you select will be saved to a file called `export config.json` in the same directory as `export_config.py`. The values in this file will be checked each time the script is run, but won't reprompt unless they are found to be invalid. To force a reprompt, delete the specific value you want to be reprompted for, or delete the `export config.json` file.

In addition to the user-selected values above, the export config also supports optional [export configuration](#export-configuration) such as setting the default export type for model files, or configuring how many threads to use while exporting.

**Manifold**

The configuration will also check if your current version of OpenSCAD supports Manifold, a much faster rendering engine supported starting with the 2024 OpenSCAD development preview.

# Configuration Parameters

## Export Configuration

The export configuration also supports additional parameters to configure defaults to use for all exports of a type, or to configure how the export itself runs. To set these options create an instance of the export config and pass the desired arguments like in the [image export example](https://github.com/CharlesLenk/openscad-export-example/blob/main/image_export_example.py#L19).

|field name|type|default|description|
|-|-|-|-|
|output_naming_strategy|NamingStrategy|`NamingStrategy.SPACE`|The output file name format. The values supported are `NamingStrategy.SPACE` which formats the file names with spaces, and `NamingStrategy.UNDERSCORE` which formats the file names as lower case separated by underscores.|
|default_model_format|ModelFormat|`ModelFormat._3MF`|The default file type for exported models. Supported values are `ModelFormat._3MF` and `ModelFormat.STL`. If you want to override the model type for a single part, use the [model level setting](#model).|
|default_image_color_scheme|ColorScheme|`ColorScheme.CORNFIELD`|The default color scheme to use for exported images. Supports all OpenSCAD color schemes. To override the color scheme for a single image, use the [image level setting](#image).|
|default_image_size|ImageSize|`ImageSize(1600, 900)`|The default image resolution to use for exported images. To override the resolution for a single image, use the [image level setting](#image).|
|parallelism|integer|System CPU count|The number of parts to render in parallel. If you want to reduce the performance impact of rendering while accepting longer run times, set this value to a number below the number of CPU cores. Setting this value to `1` will cause only one part to render at a time.|
|debug|boolean|`false`|Whether the export should output debug statements to the console.|

## Part Configuration

### Model

Supports exporting 3D models to the 3MF or STL formats.

|field name|type|default|required|description|
|-|-|-|-|-|
|name|string|`N/A`|true|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|file_name|string|The `name` formatted using the [output_naming_strategy](#export-configuration)|false|The name to use for the output file.|
|quantity|integer|`1`|false|The number of copies of the exported part to create. The copies are made using filesystem copy, rather than rendering the part multiple times.|
|format|ModelFormat|[default_model_format](#export-configuration)|false|The output format to use for the model. Supported values are `ModelFormat._3MF` and `ModelFormat.STL`. To set the default for all models, set the [default_model_format](#export-configuration).|

### Drawing

Supports exporting a 2D OpenSCAD project to the DXF format.

|field name|type|default|required|description|
|-|-|-|-|-|
|name|string|`N/A`|true|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|file_name|string|The `name` formatted using the [output_naming_strategy](#export-configuration)|false|The name to use for the output file.|
|quantity|integer|`1`|false|The number of copies of the exported part to create. The copies are made using filesystem copy, rather than rendering the part multiple times.|

### Image

Supports exporting an image of a model to the PNG format.

|field name|type|default|required|description|
|-|-|-|-|-|
|name|string|`N/A`|true|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|camera_position|string|`N/A`|true|The camera position to use for the picture of the model. The camera coordinates can be found at the bottom of the OpenSCAD application window when previewing a model. To make copying the coordinates easier, a custom function like [echo cam](https://github.com/CharlesLenk/openscad-utilities/blob/main/render.scad#L18) can be used to output the camera position to the OpenSCAD console.|
|file_name|string|The `name` formatted using the [output_naming_strategy](#export-configuration)|false|The name to use for the output file.|
|image_size|ImageSize|[default_image_size](#export-configuration)|false|The resolution of the output image. If you want all images to use the same resolution, set the [default_image_size](#export-configuration).|
|color_scheme|ColorScheme|[default_image_color_scheme](#export-configuration)|false|Overrides the color scheme to use when taking the image. To set the default for all images, set the [default_image_color_scheme](#export-configuration).|

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
