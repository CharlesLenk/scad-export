from scad_export import Folder, Model, export

exportables=Folder(
    name='scad_export/example/list_flattening',
    contents=[
        [Model(name='sphere', d=diameter) for diameter in range(15, 26, 5)],
        Model(name='cube', x=10, y=10, z=10)
    ]
)

export(exportables)
