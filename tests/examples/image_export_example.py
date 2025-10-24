from scad_export.export import export
from scad_export.export_config import ExportConfig
from scad_export.exportable import ColorScheme, Folder, Image, ImageSize

exportables=Folder(
    name='scad_export/example',
    contents=[
        Folder(
            name='images',
            contents=[
                Image(name='cube', camera_position='0,-2,1,51,0,128,154', x=5, y=5, z=5),
                Image(name='cylinder', camera_position='0,-2,1,51,0,128,154', d=10, z=10),
                Image(name='sphere', camera_position='0,-2,1,51,0,128,154', d=15),
            ]
        )
    ]
)

config = ExportConfig(
    default_image_color_scheme=ColorScheme.TOMORROW_NIGHT,
    default_image_size=ImageSize(width=500, height=500)
)

export(exportables, config)
