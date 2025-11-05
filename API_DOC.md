# API Documentation

In this file you'll find the public interfaces for the code in this module.

## export.py

The `export()` function is invoked to export the configured exportables.

### Import Path

`scad_export.export.export`

### Export Parameters

|Field Name|Type|Default|Description|
|-|-|-|-|
|exportables|`Folder`|`N/A` (Required)|A [Folder](#folder) containing other [exportables](#exportablepy) to export.|
|config|[ExportConfig](#exportconfig)|An [ExportConfig](#exportconfig) instance without additional parameters set.|System configuration and default values to use when exporting.|

## export_config.py

### ExportConfig

The export configuration supports additional parameters to configure defaults to use for all exports, or to configure how the export itself runs like setting the number of threads to use.

To set these options create an instance of the `ExportConfig` and pass the desired arguments like in the [image export example](https://github.com/CharlesLenk/scad-export/blob/main/tests/examples/image_export_example.py). Make sure to pass the modified export config to the `export` function as a argument, also demonstrated in the example.

#### Import Path

`scad_export.export_config.ExportConfig`

#### ExportConfig Parameters

|Field Name|Type|Default|Description|
|-|-|-|-|
|output_naming_format|[NamingFormat](#namingformat)|`NamingFormat.TITLE_CASE`|The naming format to use for exported files and folders.|
|default_model_format|[ModelFormat](#modelformat)|`ModelFormat._3MF`|The default file type for exported models. If you want to override the model type for a single file, use the [model level setting](#model-parameters).|
|default_image_color_scheme|[ColorScheme](#colorscheme)|`ColorScheme.CORNFIELD`|The default color scheme to use for exported images. Supports all OpenSCAD color schemes. To override the color scheme for a single image, use the [image level setting](#image-parameters).|
|default_image_size|[ImageSize](#imagesize)|`ImageSize(1600, 900)`|The default image resolution to use for exported images. To override the resolution for a single image, use the [image level setting](#image-parameters).|
|parallelism|`integer`|System CPU count.|The number of models to render in parallel. If you want to reduce the performance impact of rendering while accepting longer run times, set this value to a number below the number of CPU cores. Setting this value to `1` will cause only one model to render at a time.|
|debug|`boolean`|`False`|Whether the export should output debug statements to the console.|

### NamingFormat

The format to use when generating the names of output files and folders. When formatting the name, the following will also be appended:

1. The file format (e.g. `.stl`).
2. The count if the quantity of the exportable is greater than `1`.
3. Any additional user-defined args given in the exportable definition. For example, in the [export example script](https://github.com/CharlesLenk/scad-export/blob/main/tests/examples/export_example.py), the first cube would have '(x-5) (y-5) (z-5)' appended to the file name.

#### Import Path

`scad_export.export_config.NamingFormat`

#### Values

|Name|Description|
|-|-|
|NONE|Use the folder and file name as written. If using this option, the file format and quantity will still be appended to the file name, but additional args will not.|
|TITLE_CASE|Capitalize each word and use space as a separator.|
|SNAKE_CASE|Lower-case each word and use underscore as a separator.|

## exportable.py

### Model

Supports exporting 3D models to the 3MF or STL formats.

#### Import Path

`scad_export.exportable.Model`

#### Model Parameters

|Field Name|Type|Default|Description|
|-|-|-|-|
|name|`string`|`N/A` (Required)|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|file_name|`string`|The `name` formatted using the [output_naming_format](#exportconfig-parameters).|The name to use for the output file.|
|quantity|`integer`|`1`|The number of copies of the exported file to create. The copies are made using filesystem copy, rather than rendering the model multiple times.|
|format|[ModelFormat](#modelformat)|[default_model_format](#exportconfig-parameters)|The output format to use for the model. To set the default for all models, set the [default_model_format](#exportconfig-parameters).|
|[any]|`string` or `number`|No default|Additional arguments can be defined dynamically and will be passed to your `.scad` file when rendering. For example, if you provide the argument "size = 5", then that's the same as having a variable in your `.scad` file called "size" with a value of "5".|

### Drawing

Supports exporting a 2D OpenSCAD project to the DXF format.

#### Import Path

`scad_export.exportable.Drawing`

#### Drawing Parameters

|Field Name|Type|Default|Description|
|-|-|-|-|
|name|`string`|`N/A` (Required)|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|file_name|`string`|The `name` formatted using the [output_naming_format](#exportconfig-parameters).|The name to use for the output file.|
|quantity|`integer`|`1`|The number of copies of the exported file to create. The copies are made using filesystem copy, rather than rendering the model multiple times.|
|[any]|`string` or `number`|No default|Additional arguments can be defined dynamically and will be passed to your `.scad` file when rendering. For example, if you provide the argument "size = 5", then that's the same as having a variable in your `.scad` file called "size" with a value of "5".|

### Image

Supports exporting an image of a model to the PNG format.

#### Import Path

`scad_export.exportable.Image`

#### Image Parameters

|Field Name|Type|Default|Description|
|-|-|-|-|
|name|`string`|`N/A` (Required)|The name of the part to export. This value is passed as an argument to the `.scad` export file as "name".|
|camera_position|`string`|`N/A` (Required)|The camera position to use for the picture of the model. The camera coordinates can be found at the bottom of the OpenSCAD application window when previewing a model. To make copying the coordinates easier, a custom function like [echo cam](https://github.com/CharlesLenk/openscad-utilities/blob/main/render.scad#L18) can be used to output the camera position to the OpenSCAD console.|
|file_name|`string`|The `name` formatted using the [output_naming_format](#exportconfig-parameters).|The name to use for the output file.|
|image_size|[ImageSize](#imagesize)|[default_image_size](#exportconfig-parameters)|The resolution of the output image. If you want all images to use the same resolution, set the [default_image_size](#exportconfig-parameters).|
|color_scheme|[ColorScheme](#colorscheme)|[default_image_color_scheme](#exportconfig-parameters)|Overrides the color scheme to use when taking the image. Supports all OpenSCAD color schemes. To set the default for all images, set the [default_image_color_scheme](#exportconfig-parameters).|
|[any]|`string` or `number`|No default|Additional arguments can be defined dynamically and will be passed to your `.scad` file when rendering. For example, if you provide the argument "size = 5", then that's the same as having a variable in your `.scad` file called "size" with a value of "5".|

### Folder

Folders specify the folder structure that should be used for output files. Folders can contain any number of other exportables, including additional Folders.

#### Import Path

`scad_export.exportable.Folder`

#### Folder Parameters

|Field Name|Type|Default|Description|
|-|-|-|-|
|name|`string`|`N/A` (Required)|The `name` of the folder. If the name includes any slash separators (`/`), a separate folder will be created for each segment of the name separated by slashes. The name will be formatted using the [output_naming_format](#exportconfig-parameters).|
|contents|`list`|`N/A` (Required)|A list of other exportable types, including [Models](#model), [Drawings](#drawing), [Images](#image), and nested Folders.|

### ModelFormat

Enum for select the model export type

#### Import Path

`scad_export.exportable.ModelFormat`

#### Values

|Name|Value|Description|
|-|-|-|
|_3MF|`.3mf`|Represents the 3MF format. The name begins with an underscore because names can't begin with numbers in Python.|
|STL|`.stl`|Represents the STL format.|

### ColorScheme

The default color scheme to use when exporting images. The value will be passed to OpenSCAD using the `--colorscheme` [command line arg](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Using_OpenSCAD_in_a_command_line_environment). Colors defined in your `.scad` code will override the values here.

#### Import Path

`scad_export.exportable.ColorScheme`

#### Values

|Name|Value|
|-|-|
|CORNFIELD|`Cornfield`|
|METALLIC|`Metallic`|
|SUNSET|`Sunset`|
|STAR_NIGHT|`Starnight`|
|BEFORE_DAWN|`BeforeDawn`|
|NATURE|`Nature`|
|DAYLIGHT_GEM|`Daylight Gem`|
|NOCTURNAL_GEM|`Nocturnal Gem`|
|DEEP_OCEAN|`DeepOcean`|
|SOLARIZED|`Solarized`|
|TOMORROW|`Tomorrow`|
|TOMORROW_NIGHT|`Tomorrow Night`|
|CLEAR_SKY|`ClearSky`|
|MONOTONE|`Monotone`|

### ImageSize

The width and height of an exported image in pixels.

#### Import Path

`scad_export.exportable.ImageSize`

#### Parameters

|Field Name|Type|Default|Description|
|-|-|-|-|
|width|`integer`|`1600`|The width of the image in pixels.|
|height|`integer`|`900`|The height of the image in pixels.|
