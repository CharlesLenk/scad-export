# SCAD Export Examples

This folder contains examples of how to use [SCAD Export](https://github.com/CharlesLenk/scad_export). The documentation here is limited to the examples, for usage documentation see the SCAD Export readme.

# SCAD Example

#### [`example export map.scad`](example%20export%20map.scad)

 Provides an example of how to configure the OpenSCAD parts for export. The `name` variable is used to determine which part to export. Dimensions are provided with defaults, and can be overridden by the export script.

 The parts in this example are simple and configured inline in the if/else statement. For more complex projects, parts can be written in separate `.scad` files and imported into the export map.

# Python Examples

#### [`export_example.py`](export_example.py)

This example uses the `Model` export type to export three cubes, three cylinders, and three spheres of different sizes. Each type of shape is exported to a separate folder. The additional dimensional arguments given in each `Model` definition are passed into `example export map.scad` and override the default values, allowing the export of multiple sizes of the same Model.

#### [`export_example_2.py`](export_example_2.py)

The output of this example is identical to `export_example.py`. Since the models to export are configured in a Python script, features such as loops and list comprehension can be used to define the parts to export if many sizes are needed.

#### [`drawing_export_example.py`](drawing_export_example.py)

Demonstrates using the `Drawing` type to export a 2D circle to DXF. Drawings only support 2D types, but the usage is otherwise similar to `Model`.

This example also demonstrates setting the "quantity", which creates the given number of copies of the file (3 copies in this example).

#### [`image_export_example.py`](image_export_example.py)

Shows how to use the `Image` export type to export images of a model to PNG.
