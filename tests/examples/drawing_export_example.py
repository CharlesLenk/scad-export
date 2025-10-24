from scad_export.export import export
from scad_export.exportable import Drawing, Folder

exportables=Folder(
    name='scad_export/example/circle',
    contents=[
        Drawing(
            name='circle',
            diameter=10
        )
    ]
)

export(exportables)
