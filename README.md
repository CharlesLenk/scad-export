# OpenSCAD Export

OpenSCAD is a powerful parametric modeling program, but has some limitations. One of these limitations is that exporting models in OpenSCAD is a manual process, which makes exporting a large number of parts to separate files or folders tedious. This project aims to address that limitation using Python to define a list of parts to export and invoke OpenSCAD in parallel to export each.

# Usage

## Prerequisites

**Python**

* [Python 3.13](https://www.python.org/downloads/) or newer is needed to run this script.

**OpenSCAD**

* [OpenSCAD](https://openscad.org/) should be installed on your system, preferably in the default location for your OS.

**Git**

* While not strictly required, downloading and using this project is easier with git installed and on your classpath.

## Project Configuration

### Add the script to your project

This script is intended to be added as a submodule to a Git project, but will also work in other contexts.

* For Git projects, use the command below to add this project as a submodule.

`git submodule add https://github.com/CharlesLenk/openscad_export.git` 

* For non-Git projects, use git to clone the script and copy it into your project folder.

### Export Map Definition

A `.scad` file is needed to define the parts to export. For most projects, it's easiest to use this script by having a single `export map.scad` file which imports all parts that you want to export. This file should contain an `if/else` statement which selects the part by a variable called "name". An example of the export scad file is available in the [example project](https://github.com/CharlesLenk/openscad-export-example/blob/main/example%20export%20map.scad).

### Part Definition

The parts to export and folder structure are defined in a Python script. An few examples of the part definition are provided in the example project. 

The following export types are supported

def __init__(self, name, file_name = None, quantity = 1, format: ModelFormat = None, **kwargs):

**Model**

Supports exporting 3D models to the 3MF (default) or STL formats. 

Parameters

|field name|type|description|
|-|-|-|
|name|string|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|file_name|string|The name of the exported part. This field is options and will default to the value of the `name` field.|

* name
    * The name of the 
* file_name
* quantity
* format
* kwargs

**Drawing**

Supports exporting a 2D OpenSCAD project to the DXF format.

**Image**

Supports exporting an image of a project to the PNG format.


## Running

Run the script using Python. 

### Script Configuration

When first run, this script will attempt to find the following automatically:
* The location of OpenSCAD on your system. This will search the default install location for Windows, MacOS, and Linux.
* The root directory of the current Git project.
* A `.scad` file that defines each part to export.
* The current `Desktop` folder to export the STL files to.

Config location

Option selection

For each of these values, the script will prompt if you want to use the default. If the script fails to find the default, or if you choose not to use the default, you'll be prompted for the value to use.

The script will also check if your current version of OpenSCAD supports Manifold.

### Default values

Other defaults
CPU usage
Debug
Manifold

# Project Files

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
