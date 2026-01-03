from scad_export import export, Drawing, Folder


exportables=Folder(
    name='scad_export/example/circle',
    contents=[
        Drawing(
            name='circle',
            quantity=3,
            diameter=10
        )
    ]
)

export(exportables)
