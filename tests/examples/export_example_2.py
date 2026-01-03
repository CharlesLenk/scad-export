from scad_export import export, Folder, Model


exportables=Folder(
    name='scad_export/example',
    contents=[
        Folder(
            name='cubes',
            contents=[Model(name='cube', x=size, y=size, z=size) for size in range(5, 16, 5)]
        ),
        Folder(
            name='cylinders',
            contents=[Model(name='cylinder', d=10, z=height) for height in range(10, 31, 10)]
        ),
        Folder(
            name='spheres',
            contents=[Model(name='sphere', d=diameter) for diameter in range(15, 26, 5)]
        )
    ]
)

export(exportables)
