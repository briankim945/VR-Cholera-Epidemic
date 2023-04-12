import csv
import bpy
import mathutils

def create_cylinder(location, radius, height, name, color=(1,0,0,1)):
    bpy.ops.mesh.primitive_cylinder_add(location=mathutils.Vector((location[0] - 0.5, location[1] - 0.5, height/2.0)), radius=radius, depth=height)
    bpy.data.objects['Cylinder'].name = name
    obj = bpy.context.object
    obj.color = (0,0,1,1)


    # Create a material
    mat = bpy.data.materials.new("Color Material")
    # Activate its nodes
    mat.use_nodes = True
    # Get the principled BSDF (created by default)
    principled = mat.node_tree.nodes['Principled BSDF']
    # Assign the color
    principled.inputs['Base Color'].default_value = color
    # Assign the material to the object
    obj.data.materials.append(mat)


test_pumps = []
with open("C:/Users/Brian/Documents/Brown/VR Cholera/pump_map.csv") as fd:
    rd = csv.reader(fd, delimiter=",")
    for row in rd:
        if len(row) > 0:
            test_pumps.append([float(row[0]), float(row[1])])

test_deaths = []
with open("C:/Users/Brian/Documents/Brown/VR Cholera/death_map.csv") as fd:
    rd = csv.reader(fd, delimiter=",")
    for row in rd:
        if len(row) > 0:
            test_deaths.append([float(row[0]), float(row[1]), int(row[2])])

for i, point in enumerate(test_pumps):
    create_cylinder(point, 0.01, 0.2, f"pump_{i}", (0,0,1,1))
    
for i, point in enumerate(test_deaths):
    create_cylinder([point[0], point[1]], 0.005, point[2] / 100.0, f"death_{i}")