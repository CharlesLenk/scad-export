from scad_export import Drawing, Folder, export

exportables=Folder(
    name='scad_export/example/circle',
    contents=Drawing(
        name='circle',
        quantity=3,
        d=10
    )
)

export(exportables)
