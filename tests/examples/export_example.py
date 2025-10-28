from scad_export.export import export
from scad_export.exportable import Folder, Model

exportables=Folder(
    # These folders are created relative to the configured export directory.
    name='scad_export/example',
    contents=[
        Folder(
            # Additional folders are created relative to the containing Folder configuration.
            name='cubes',
            contents=[
                # Override file_name to export each cube to a separate file, rather than overwriting the same file.
                # x, y, and z are user-defined arguments that are passed to the export .scad file.
                Model(name='cube', x=5, y=5, z=5),
                Model(name='cube', x=10, y=10, z=10),
                Model(name='cube', x=15, y=15, z=15)
            ]
        ),
        Folder(
            name='cylinders',
            contents=[
                Model(name='cylinder', d=10, z=10),
                Model(name='cylinder', d=10, z=20),
                Model(name='cylinder', d=10, z=30)
            ]
        ),
        Folder(
            name='spheres',
            contents=[
                Model(name='sphere', d=15),
                Model(name='sphere', d=20),
                Model(name='sphere', d=25)
            ]
        )
    ]
)

# Invoke the logic to export the exportables to files and folders.
export(exportables)
