#!/usr/bin/python
#
# cnc25d_api_macro.py
# test and demonstrate the Cnc25D API
# created by charlyoleg on 2013/06/13
# license: CC BY SA 3.0
# 

"""
cnc25d_api_macro.py tests and demonstrates the Cnc25D API.
Use it as an example of usage of the Cnc25D API when you want to create your own design.
"""

# import the Cnc25D API modules
from cnc25d import cnc25d_api
# import the FreeCAD library
cnc25d_api.importing_freecad()
import Part # this module is part of the FreeCAD library
from FreeCAD import Base

# hello message
print("cnc25d_api_macro.py starts")

# define the CNC router_bit radius
my_router_bit_radius = 5.0 # in mm

# some design constant
big_length = 60
small_length = 20

# create a free polygon.
# A polygon is list of points. A point is a list of three elements: x coordinate, y coordiante, router_bit radius.
# If the router_bit radius is positive, the angle is smoothed for this radius.
# If the router_bit radius is negative, the angle is enlarged for this radius.
# If the router_bit radius is zero, the angle is unchanged
my_polygon = [
  [ 0*big_length+0*small_length,  0*big_length+0*small_length,    my_router_bit_radius],
  [ 1*big_length+1*small_length,  0*big_length+0*small_length,    my_router_bit_radius],
  [ 1*big_length+1*small_length,  0*big_length+2*small_length,    my_router_bit_radius],
  [ 1*big_length+2*small_length,  0*big_length+2*small_length,    my_router_bit_radius],
  [ 1*big_length+2*small_length,  0*big_length+0*small_length,    my_router_bit_radius],
  [ 3*big_length+0*small_length,  0*big_length+0*small_length,    my_router_bit_radius],
  [ 3*big_length+0*small_length,  1*big_length+0*small_length,    my_router_bit_radius],
  [ 2*big_length+0*small_length,  1*big_length+0*small_length, -1*my_router_bit_radius],
  [ 2*big_length+0*small_length,  2*big_length+0*small_length,    my_router_bit_radius],
  [ 1*big_length+0*small_length,  2*big_length+0*small_length,    my_router_bit_radius],
  [ 1*big_length+0*small_length,  1*big_length+0*small_length,    my_router_bit_radius],
  [ 0*big_length+0*small_length,  1*big_length+0*small_length,    my_router_bit_radius]]

# use the Cnc25D API function cnc_cut_outline to create a makable outline from the wished polygon
my_part_outline = cnc25d_api.cnc_cut_outline(my_polygon, 'api_example')
# extrude the outline to make a 3D part
my_part_edges = my_part_outline.Edges
my_part_wire = Part.Wire(my_part_edges)
my_part_face = Part.Face(my_part_wire)
# short version: my_part_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline(my_part_outline, 'api_example').Edges))
my_part_solid = my_part_face.extrude(Base.Vector(0,0,big_length)) # straight linear extrusion

# visualize the part with the FreeCAD GUI
#Part.show(my_part_solid)

# create three my_part and place them using the Cnc25D API function plank_place
my_part_a = cnc25d_api.place_plank(my_part_solid.copy(), 3*big_length, 2*big_length, 1*big_length, 'i', 'xz', 0, 0, 0)
my_part_b = cnc25d_api.place_plank(my_part_solid.copy(), 3*big_length, 2*big_length, 1*big_length, 'i', 'zx', 0, 0, big_length)
my_part_c = cnc25d_api.place_plank(my_part_solid.copy(), 3*big_length, 2*big_length, 1*big_length, 'z', 'yz', 2*big_length, 0, 0)
# place_plank arguments: FreeCAD Part Object, x-size, y-size, z-size, flip, orientation, x-position, y-position, z-position
# with flip is one of the four possible values: 'i' as identity, 'x' as x-flip, 'y' or 'z'.
# with orientation one of the six possible values: 'xy', 'xz', 'yx', 'yz', 'zx' or 'zy'.

# create an assembly of three my_part
my_assembly = Part.makeCompound([my_part_a, my_part_b, my_part_c])
Part.show(my_assembly)

# generate the output files

# my_part in 3D STL
my_part_solid.exportStl("my_part.stl")
print("The file my_part.stl has been generated")

# my_part in 2D DXF
cnc25d_api.export_to_dxf(my_part_solid, Base.Vector(0,0,1), 1.0, "my_part.dxf") # slice my_part in the XY plan at a height of 1.0
print("The file my_part.dxf has been generated")

# my_assembly in 3D STL
my_assembly.exportStl("my_assembly.stl")
print("The file my_assembly.stl has been generated")

# my_assembly sliced and projected in 2D DXF
xy_slice_list = [ 0.1+20*i for i in range(12) ]
xz_slice_list = [ 0.1+20*i for i in range(9) ]
yz_slice_list = [ 0.1+20*i for i in range(9) ]
cnc25d_api.export_xyz_to_dxf(my_assembly, 3*big_length, 3*big_length, 4*big_length, xy_slice_list, xz_slice_list, yz_slice_list, "my_assembly.dxf")
print("The file my_assembly.dxf has been generated")

# bye message
print("cnc25d_api_macro.py says Bye!")

