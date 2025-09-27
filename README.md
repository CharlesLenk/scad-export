# openscad-export
Script for parallel export of OpenSCAD parts. What and why

# Usage

## Prequisits

* [Python 3.13](https://www.python.org/downloads/) or newer is needed to run this script.
* Git. This script will perform some autoconfiguration when first run. For the autoconfiguration to work:
    * Git must be installed and on your classpath.
    * The script must be run from a Git repository that your project files are in.
The autoconfiguration isn't required to use the script, you'll just need to manually input the root folder the script should use for your project.

## Project Configuration

### Add the script to your project

This script is intended to be added as a submodule to a Git project, but will also work in other contexts.

* For Git projects, use `git submodule add https://github.com/CharlesLenk/openscad_export.git`
* For non-Git projects, clone the script and copy it into your project folder.

### Part Definition

How to define file for SCAD part update.
Link examples.

Overrides
* Model
* Drawing
* Image

Example

### Export Map Definition

### Running

# Configuration

Config location

## Input Values
Option selection
When first run, this script will attempt to find the following automatically:
* The location of OpenSCAD on your system. This will search the default install location for Windows, MacOS, and Linux.
* The root directory of the current Git project.
* A `.scad` file that defines each part to export.
* The current `Desktop` folder to export the STL files to.

For each of these values, the script will prompt if you want to use the default. If the script fails to find the default, or if you choose not to use the default, you'll be prompted for the value to use.

The script will also check if your current version of OpenSCAD supports Manifold.

## Default values
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
    