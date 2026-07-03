// Name is required, and it always passed by the export script.
name = "";

// These additional parameters are optional. To define optional parameters, the name of
// the parameter here must match the name in the part definition.
x = 10;
y = 10;
z = 10;
d = 10;

// Which part to render is based on the "name" field.
if (name == "cube")
    cube([x, y, z]);
else if (name == "cylinder")
    cylinder(d = d, h = z);
else if (name == "sphere")
    sphere(d = d);
else if (name == "circle")
    circle(d = d);
