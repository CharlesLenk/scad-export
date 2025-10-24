from scad_export.export import export
from scad_export.exportable import Folder, Model

exportables=Folder(
    name='scad_export/example',
    contents=[
        Folder(
            name='cubes',
            contents=[Model(name='cube', file_name='cube_{}'.format(size), x=size, y=size, z=size) for size in range(5, 16, 5)]
        ),
        Folder(
            name='cylinders',
            contents=[Model(name='cylinder', file_name='cylinder_{}'.format(height), d=10, z=height) for height in range(10, 31, 10)]
        ),
        Folder(
            name='spheres',
            contents=[Model(name='sphere', file_name='sphere_{}'.format(diameter), d=diameter) for diameter in range(15, 26, 5)]
        )
    ]
)

export(exportables)
