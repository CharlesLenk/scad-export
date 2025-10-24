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
                Model(name='cube', file_name='cube_5', x=5, y=5, z=5),
                Model(name='cube', file_name='cube_10', x=10, y=10, z=10),
                Model(name='cube', file_name='cube_15', x=15, y=15, z=15)
            ]
        ),
        Folder(
            name='cylinders',
            contents=[
                Model(name='cylinder', file_name='cylinder_10', d=10, z=10),
                Model(name='cylinder', file_name='cylinder_20', d=10, z=20),
                Model(name='cylinder', file_name='cylinder_30', d=10, z=30)
            ]
        ),
        Folder(
            name='spheres',
            contents=[
                Model(name='sphere', file_name='sphere_15', d=15),
                Model(name='sphere', file_name='sphere_20', d=20),
                Model(name='sphere', file_name='sphere_25', d=25)
            ]
        )
    ]
)

# Invoke the logic to export the exportables to files and folders.
export(exportables)
