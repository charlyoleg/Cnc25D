#!/usr/bin/env python
#
# simple_cnc25d_api_macro.py
# simple test and demonstration the Cnc25D API
# created by charlyoleg on 2013/08/27
#
# (C) Copyright 2013 charlyoleg
#
# This file is part of the Cnc25D Python package.
# 
# Cnc25D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cnc25D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Cnc25D.  If not, see <http://www.gnu.org/licenses/>.

# 

"""
simple_cnc25d_api_macro.py tests and demonstrates the basics of Cnc25D API.
Use it as a simple example of usage of the Cnc25D API when you want to create your own design.
This script focus on the figure-level API functions
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
#   cnc25d_api.outline_arc_line(outline-B, backend) => Tkinter or svgwrite or dxfwrite or FreeCAD stuff
#   cnc25d_api.Two_Canvas(Tkinter.Tk()) # object constructor
#   cnc25d_api.figure_simple_display(figure) => 0
#   cnc25d_api.write_figure_in_svg(figure, filename) => 0
#   cnc25d_api.write_figure_in_dxf(figure, filename) => 0
#   cnc25d_api.figure_to_freecad_25d_part(figure, extrusion_height) => freecad_part_object
#   cnc25d_api.place_plank(freecad_part_object, x-size, y-size, z-size, flip, orientation, x-position, y-position, z-position) => freecad_part_object
#   cnc25d_api.export_to_dxf(freecad_part_object, direction_vector, depth, filename) => 0
#   cnc25d_api.export_xyz_to_dxf(freecad_part_object, x-size, y-size, z-size, x-depth-list, y-depth-list, z-depth-list, filename) => 0
#   cnc25d_api.mkdir_p(directory) => 0
#   cnc25d_api.get_effective_args(default_args) => [args]
#   cnc25d_api.generate_output_file_add_argument(argparse_parser) => argparse_parser
#   cnc25d_api.generate_output_file(figure, filename, extrusion_height) => 0


################################################################
# import
################################################################

# import the Cnc25D API modules
from cnc25d import cnc25d_api
# add the FreeCAD library path to the search path
cnc25d_api.importing_freecad()
# import the FreeCAD library
import Part
from FreeCAD import Base
#
import math # to get the pi number
#import Tkinter # to display the outline in a small GUI
#import svgwrite
#from dxfwrite import DXFEngine


################################################################
# Start programming
################################################################

# hello message
print("simple_cnc25d_api_macro.py starts")

################################################################
# Define your router_bit constraint
################################################################

# define the CNC router_bit radius
#router_bit_radius = 4.0 # in mm

################################################################
# Design your XY outline of your 2.5D part design
################################################################

outer_rectangle_A = [ # format-A outline
  [-60, -40, 10], # first point of the outline
  [ 60, -40,  5], # first segment
  [ 60,  40,  0], # second segment
  [-60,  40,  5], # third segment
  [-60, -40,  0]] # last segment
outer_rectangle_B = cnc25d_api.cnc_cut_outline(outer_rectangle_A, "outer_rectangle_A") # convert from format-A to format-B

inner_shape_A = [     # format-A outline
  [  0, 0,  5],           # first point of the outline
  [ 40, 0, -5],           # first segment: it's a line
  [ 20, 30,  0,  0,  0]]  # second and last segment: it's an arc
inner_shape_B = cnc25d_api.cnc_cut_outline(inner_shape_A, "inner_shape_A")  # convert from format-A to format-B

inner_circle1 = [-30, 0, 15] # circle of center (-30, 0) and radius 15

simple_figure = [outer_rectangle_B, inner_shape_B, inner_circle1]

# display the figure
cnc25d_api.figure_simple_display(simple_figure)

simple_extrude_height = 20.0
# create a FreeCAD part
simple_part = cnc25d_api.figure_to_freecad_25d_part(simple_figure, simple_extrude_height)

# create the test_output_dir
test_output_dir = "test_output"
cnc25d_api.mkdir_p(test_output_dir)

# write the SVG file with mozman svgwrite
cnc25d_api.write_figure_in_svg(simple_figure, "{:s}/simple_part_mozman.svg".format(test_output_dir))

# write the DXF file with mozman dxfwrite
cnc25d_api.write_figure_in_dxf(simple_figure, "{:s}/simple_part_mozman.dxf".format(test_output_dir))

# simple_part in 3D BRep
print("Generate {:s}/simple_part.brep".format(test_output_dir))
simple_part.exportBrep("{:s}/simple_part.brep".format(test_output_dir))
# simple_part in 2D DXF
print("Generate {:s}/simple_part.dxf".format(test_output_dir))
# slice simple_part in the XY plan at a height of simple_extrude_height/2
cnc25d_api.export_to_dxf(simple_part, Base.Vector(0,0,1), simple_extrude_height/2, "{:s}/simple_part.dxf".format(test_output_dir))

# view the simple_part
Part.show(simple_part)

################################################################
# End of the script
################################################################

# bye message
print("simple_cnc25d_api_macro.py says Bye!")

