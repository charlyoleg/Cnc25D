#!/usr/bin/env python
#
# cnc25d_api_macro.py
# test and demonstrate the Cnc25D API
# created by charlyoleg on 2013/06/13
#
# (C) Copyright 2013 charlyoleg
#
# This file is part of the Cnc25D Python package.
# 
# Cnc25D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cnc25D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cnc25D.  If not, see <http://www.gnu.org/licenses/>.

# 

"""
cnc25d_api_macro.py tests and demonstrates the Cnc25D API.
Use it as an example of usage of the Cnc25D API when you want to create your own design.
"""

# List of the functions of the Cnc25D API:
#   cnc25d_api.importing_freecad() => 0
#   cnc25d_api.outline_shift_x(outline-AB, x-offset, x-coefficient) => outline-AB
#   cnc25d_api.outline_shift_y(outline-AB, y-offset, y-coefficient) => outline-AB
#   cnc25d_api.outline_shift_xy(outline-AB, x-offset, x-coefficient, y-offset, y-coefficient) => outline-AB
#   cnc25d_api.outline_rotate(outline-AB, center-x, center-y, rotation_angle) => outline-AB
#   cnc25d_api.outline_close(outline-AB) => outline-AB
#   cnc25d_api.outline_reverse(outline-AB) => outline-AB
#   cnc25d_api.cnc_cut_outline(outline-A, error_mark_string) => outline-B
#   cnc25d_api.smooth_outline_c_curve(outline-C, precision, router_bit_radius, error_mark_string) => outline-B
#   cnc25d_api.smooth_outline_b_curve(outline-B, precision, router_bit_radius, error_mark_string) => outline-B
#   cnc25d_api.ideal_outline(outline-AC, error_mark_string) => outline-B
#   cnc25d_api.outline_arc_line(outline-B, backend) => Tkinter or svgwrite or dxfwrite or FreeCAD stuff
#   cnc25d_api.Two_Canvas(Tkinter.Tk()) # object constructor
#   cnc25d_api.figure_simple_display(graphic_figure, overlay_figure, parameter_info) => 0
#   cnc25d_api.write_figure_in_svg(figure, filename) => 0
#   cnc25d_api.write_figure_in_dxf(figure, filename) => 0
#   cnc25d_api.figure_to_freecad_25d_part(figure, extrusion_height) => freecad_part_object
#   cnc25d_api.place_plank(freecad_part_object, x-size, y-size, z-size, flip, orientation, x-position, y-position, z-position) => freecad_part_object
#   cnc25d_api.export_to_dxf(freecad_part_object, direction_vector, depth, filename) => 0
#   cnc25d_api.export_xyz_to_dxf(freecad_part_object, x-size, y-size, z-size, x-depth-list, y-depth-list, z-depth-list, filename) => 0
#   cnc25d_api.mkdir_p(directory) => 0
#   cnc25d_api.get_effective_args(default_args) => [args]
#   cnc25d_api.generate_output_file_add_argument(argparse_parser) => argparse_parser
#   cnc25d_api.generate_output_file(figure, filename, extrusion_height, info_txt) => 0


################################################################
# import
################################################################

try:    # when working on the source files
  from cnc25d import cnc25d_api # import the Cnc25D API modules
except: # when working with an installed Cnc25D package
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api # import the Cnc25D API modules
# add the FreeCAD library path to the search path
cnc25d_api.importing_freecad()
# import the FreeCAD library
import Part
from FreeCAD import Base
#
#import os, errno # to create the output directory
import math # to get the pi number
import Tkinter # to display the outline in a small GUI
#import svgwrite
#from dxfwrite import DXFEngine


################################################################
# Start programming
################################################################

# hello message
print("cnc25d_api_macro.py starts")

################################################################
# Define your router_bit constraint
################################################################

# define the CNC router_bit radius
my_router_bit_radius = 4.0 # in mm

################################################################
# Design your XY outline of your 2.5D part design
################################################################

# some design constant
big_length = 60
small_length = 20

# Create an outline.
# A outline is list of segments. A segment is a line or an arc.
# The first element of an outline is the Start point, defined with its two coordinates.
# The junction between two segments is called a corner.
# The cnc25d_api.cnc_cut_outline() function can modify the corners of an outline.
# For each corner, define is you want to keep it (r=0 =unchanged), smooth it (r>0) or enlarge it (r<0).
# A line-segment is defined by its last point coordinates and its corner request (r).
# An arc-segment is defined by its middle point and last point coordinates and its corner request (r).
# If the router_bit radius is positive, the angle is smoothed for this radius.
# If the router_bit radius is negative, the angle is enlarged for this radius.
# If the router_bit radius is zero, the angle is unchanged
# If you want a closed outline, the last point must be equal to the Start point.
my_outline = [
  [ 0*big_length+0*small_length,  0*big_length+0*small_length,    my_router_bit_radius], # Start point
  [ 1*big_length+1*small_length,  0*big_length+0*small_length,    my_router_bit_radius], # a line
  [ 1*big_length+0.6*small_length,  0*big_length+0.75*small_length,  1*big_length+1*small_length,  0*big_length+2*small_length,    my_router_bit_radius], # an arc
  [ 1*big_length+1.5*small_length,  0*big_length+2.20*small_length,  1*big_length+2*small_length,  0*big_length+2*small_length,    my_router_bit_radius], # an other arc
  [ 1*big_length+1.8*small_length,  0*big_length+1.00*small_length,  1*big_length+2*small_length,  0*big_length+0*small_length,    my_router_bit_radius], # an other arc
  [ 3*big_length+0*small_length,  0*big_length+0*small_length,    my_router_bit_radius], # an other line
  [ 3*big_length-0.3*small_length,  0.5*big_length+0*small_length,  3*big_length+0*small_length,  1*big_length+0*small_length,    my_router_bit_radius], # an other arc
  [ 2*big_length+0*small_length,  1*big_length+0*small_length, -1*my_router_bit_radius], # this corner will be enlarged
  [ 2*big_length+0*small_length,  2*big_length+0*small_length,    my_router_bit_radius],
  [ 1*big_length+0*small_length,  2*big_length+0*small_length,  0*my_router_bit_radius], # this corner will be leaved unchanged
  [ 1*big_length+0*small_length,  1*big_length+0*small_length,    my_router_bit_radius],
  [ 0*big_length+0*small_length,  1*big_length+0*small_length,    my_router_bit_radius],
  [ 0*big_length+0*small_length,  0*big_length+0*small_length,  0*my_router_bit_radius]] # The last point is equal to the Start point. The router_bit request must be set to zero.

my_curve=[
  [20,0],
  [22,10],
  [25,20],
  [29,30],
  [35,40],
  [43,50],
  [60,60]]

################################################################
# Combine your outline and your router_bit constraint
################################################################

## use the Cnc25D API function cnc_cut_outline to create a makable outline from the wished outline
# the second argument is just used to enhance the error, warning and debug messages
my_outline_for_cnc = cnc25d_api.cnc_cut_outline(my_outline, 'api_example')
# other help functions to manipulate outlines
#outline_shift_x
my_outline_for_cnc_x_shifted = cnc25d_api.outline_shift_x(my_outline_for_cnc, big_length*4, 1)
#outline_shift_y
my_outline_for_cnc_y_shifted = cnc25d_api.outline_shift_y(my_outline_for_cnc, big_length*6, -1)
#outline_shift_xy
my_outline_for_cnc_xy_shifted = cnc25d_api.outline_shift_xy(my_outline_for_cnc, big_length*4, 0.5, big_length*4, 0.5)
#outline_rotate
my_outline_for_cnc_rotated = cnc25d_api.outline_rotate(my_outline_for_cnc, big_length*2, big_length*2, math.pi/4)
#outline_close
# it has no effect because the outline is already closed
# notice that the help functions to manipulate outlines can be used before or after applying the function cnc25d_api.cnc_cut_outline()
my_outline_for_cnc_closed = cnc25d_api.cnc_cut_outline(cnc25d_api.outline_close(cnc25d_api.outline_shift_x(my_outline, -1*big_length, 0.25)), 'api_example2')
#outline_reverse
# reverse the order of the segments. If the outline is closed, it changes the orientation from CW to CCW and vice versa
my_outline_for_cnc_reverse = cnc25d_api.cnc_cut_outline(cnc25d_api.outline_reverse(cnc25d_api.outline_shift_x(my_outline, -2*big_length, 0.25)), 'api_example3')
# curve
radian_precision = math.pi/100
my_curve_for_cnc = cnc25d_api.smooth_outline_b_curve(my_curve, radian_precision, my_router_bit_radius, 'api_example4')

################################################################
# ********** Work at outline-level ***********
################################################################

################################################################
# Display the outline in a Tkinter GUI
################################################################

## display my_outline_for_cnc with Tkinter
print("Display the outlines with Tkinter")
tk_root = Tkinter.Tk()
my_canvas = cnc25d_api.Two_Canvas(tk_root)
# callback function for display_backend
def sub_canvas_graphics(ai_rotation_direction, ai_angle_position):
  r_canvas_graphics = []
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc, 'tkinter'), 'red', 1))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_x_shifted, 'tkinter'), 'red', 1))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_y_shifted, 'tkinter'), 'red', 1))
  turning_outline = cnc25d_api.outline_rotate(my_outline_for_cnc_xy_shifted, big_length*4, big_length*4, ai_angle_position)
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(turning_outline, 'tkinter'), 'red', 1))
  r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_rotated, 'tkinter'), 'green', 2))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_closed, 'tkinter'), 'blue', 1))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_reverse, 'tkinter'), 'blue', 1))
  #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_circle((100,100), 40, 'tkinter'), 'orange', 1)) # create a circle (obsolete)
  r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((100, 100, 40), 'tkinter'), 'orange', 1)) # create a circle
  r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(my_curve, 'tkinter'), 'green', 2))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_curve_for_cnc, 'tkinter'), 'blue', 1))
  return(r_canvas_graphics)
# end of callback function
my_canvas.add_canvas_graphic_function(sub_canvas_graphics)
tk_root.mainloop()
del (my_canvas, tk_root) # because Tkinter will be used again later in this script

#
l_output_dir = "test_output"
print("Create the output directory: {:s}".format(l_output_dir))
cnc25d_api.mkdir_p(l_output_dir)

################################################################
# Write the outline in a SVG file
################################################################

## write my_outline_for_cnc in a SVG file
print("Write the outlines in a SVG file with svgwrite")
output_svg_file_name =  "{:s}/outlines_with_svgwrite.svg".format(l_output_dir)
my_circle = (100, 100, 40)
svg_figures = [my_outline_for_cnc, my_outline_for_cnc_rotated, my_circle] # figure = list of (format B) outlines
cnc25d_api.write_figure_in_svg(svg_figures, output_svg_file_name)

################################################################
# Write the outline in a DXF file
################################################################

## write my_outline_for_cnc in a DXF file
print("Write the outlines in a DXF file with dxfwrite")
output_dxf_file_name =  "{:s}/outlines_with_dxfwrite.dxf".format(l_output_dir)
dxf_figures = [my_outline_for_cnc, my_outline_for_cnc_rotated, my_circle] # figure = list of (format B) outlines
cnc25d_api.write_figure_in_dxf(dxf_figures, output_dxf_file_name)

################################################################
# Extrude the outline to make it 3D
################################################################

## extrude the outline to make a 3D part with FreeCAD
my_freecad_part_outline = cnc25d_api.outline_arc_line(my_outline_for_cnc, 'freecad')
my_part_edges = my_freecad_part_outline.Edges
my_part_wire = Part.Wire(my_part_edges)
my_part_face = Part.Face(my_part_wire)
my_part_solid = my_part_face.extrude(Base.Vector(0,0,big_length)) # straight linear extrusion
# short version:
#my_part_face2 = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(cnc25d_api.outline_shift_y(my_outline, 4*big_length,0.5), 'freecad_short_version').Edges))
#my_part_solid2 = my_part_face2.extrude(Base.Vector(0,0,big_length)) # straight linear extrusion
my_part2_B = cnc25d_api.cnc_cut_outline(cnc25d_api.outline_shift_y(my_outline, 4*big_length,0.5), 'freecad_short_version')
my_part_solid2 = cnc25d_api.figure_to_freecad_25d_part([my_part2_B], big_length)
# creation of a circle with the cnc25d workflow
#my_part_face3 = Part.Face(Part.Wire(cnc25d_api.outline_circle((100,100),40, 'freecad').Edges))
my_part_face3 = Part.Face(Part.Wire(cnc25d_api.outline_arc_line((100, 100, 40), 'freecad').Edges))
my_part_solid3 = my_part_face3.extrude(Base.Vector(0,0,big_length/2)) # straight linear extrusion


# visualize the part with the FreeCAD GUI
#Part.show(my_part_solid)
Part.show(my_part_solid2)
Part.show(my_part_solid3)

################################################################
# Create a 3D assembly
################################################################

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

################################################################
# Generate output files from your 3D design
################################################################

# my_part in 3D
print("Generate {:s}/my_part.stl".format(l_output_dir))
my_part_solid.exportStl("{:s}/my_part.stl".format(l_output_dir))
print("Generate {:s}/my_part.brep".format(l_output_dir))
my_part_solid.exportBrep("{:s}/my_part.brep".format(l_output_dir))
#print("Generate {:s}/my_part.step".format(l_output_dir))
#my_part_solid.exportStep("{:s}/my_part.step".format(l_output_dir))

# my_part in 2D DXF
print("Generate {:s}/my_part.dxf".format(l_output_dir))
cnc25d_api.export_to_dxf(my_part_solid, Base.Vector(0,0,1), 1.0, "{:s}/my_part.dxf".format(l_output_dir)) # slice my_part in the XY plan at a height of 1.0

# my_assembly in 3D
print("Generate {:s}/my_assembly.stl".format(l_output_dir))
my_assembly.exportStl("{:s}/my_assembly.stl".format(l_output_dir))
print("Generate {:s}/my_assembly.brep".format(l_output_dir))
my_assembly.exportBrep("{:s}/my_assembly.brep".format(l_output_dir))
#print("Generate {:s}/my_assembly.step".format(l_output_dir))
#my_assembly.exportStep("{:s}/my_assembly.step".format(l_output_dir))

# my_assembly sliced and projected in 2D DXF
print("Generate {:s}/my_assembly.dxf".format(l_output_dir))
xy_slice_list = [ 0.1+20*i for i in range(12) ]
xz_slice_list = [ 0.1+20*i for i in range(9) ]
yz_slice_list = [ 0.1+20*i for i in range(9) ]
cnc25d_api.export_xyz_to_dxf(my_assembly, 3*big_length, 3*big_length, 4*big_length, xy_slice_list, xz_slice_list, yz_slice_list, "{:s}/my_assembly.dxf".format(l_output_dir))

################################################################
# ********** Work at figure-level ***********
################################################################

wfl_outer_rectangle_A = [
  [-60, -40, 10],
  [ 60, -40,  5],
  [ 60,  40,  5],
  [-60,  40,  5],
  [-60, -40,  0]]
wfl_outer_rectangle_B = cnc25d_api.cnc_cut_outline(wfl_outer_rectangle_A, "wfl_outer_rectangle_A") # convert from format-A to format-B

wfl_inner_square_A = [
  [-10, -10, -5],
  [ 10, -10, -4],
  [ 10,  10, -3],
  [-10,  10, -2],
  [-10, -10,  0]]
wfl_inner_square_B = cnc25d_api.cnc_cut_outline(wfl_inner_square_A, "wfl_inner_square_B")  # convert from format-A to format-B

wfl_inner_circle1 = [30,0, 15]
wfl_inner_circle2 = [40,0, 10]

wfl_figure = [wfl_outer_rectangle_B, wfl_inner_square_B, wfl_inner_circle1, wfl_inner_circle2]
wfl_overlay_figure = [wfl_outer_rectangle_A, wfl_inner_square_A, wfl_inner_circle1, wfl_inner_circle2]

wfl_parameter_info = """
those lines will appers
in the parameter window.
Might be usefull to provide some info to the user!
"""

# display the figure
cnc25d_api.figure_simple_display(wfl_figure, wfl_overlay_figure, wfl_parameter_info)

wfl_extrude_height = 20.0
# create a FreeCAD part
wfl_part = cnc25d_api.figure_to_freecad_25d_part(wfl_figure, wfl_extrude_height)

# wfl_part in 3D BRep
print("Generate {:s}/wfl_part.brep".format(l_output_dir))
wfl_part.exportBrep("{:s}/wfl_part.brep".format(l_output_dir))
# wfl_part in 2D DXF
print("Generate {:s}/wfl_part.dxf".format(l_output_dir))
cnc25d_api.export_to_dxf(wfl_part, Base.Vector(0,0,1), wfl_extrude_height/2, "{:s}/wfl_part.dxf".format(l_output_dir)) # slice wfl_part in the XY plan at a height of wfl_extrude_height/2


################################################################
# End of the script
################################################################

# bye message
print("cnc25d_api_macro.py says Bye!")

