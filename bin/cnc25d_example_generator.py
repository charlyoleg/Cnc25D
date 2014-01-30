#!/usr/bin/env python
#
# cnc25d_example_generator.py
# it generates examples of python scripts that use the cnc25d package
# created by charlyoleg on 2013/06/03
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


"""
cnc25d_example_generator.py is the unique binary delivered with the Cnc25D distribution. It aims at generating script examples that use the cnc25d package.
In addition, it checks if FreeCAD is correctly installed on the host computer.
"""

##############################################################################
# import
##############################################################################

import os, re, sys
import subprocess

##############################################################################
# Checking FreeCAD installation
##############################################################################

### check if FreeCAD exists and checks the version number

# create a tempory script that checks the FreeCAD versions
checking_freecad_version_script = """
import sys
freecad_version = FreeCAD.Version()
FreeCAD.Console.PrintMessage("FREECAD_VERSION_START{:s}FREECAD_VERSION_STOP".format(freecad_version))
sys.exit(0)
"""
# We don't use the /tmp directory for an easier compatibility with windows
checking_freecad_version_script_name = "tmp_checking_freecad_version.py"
fh_output = open(checking_freecad_version_script_name, 'w')
fh_output.write(checking_freecad_version_script)
fh_output.close()
l_cmdline = "freecad -c {:s}".format(checking_freecad_version_script_name)
#print("dbg226: l_cmdline:", l_cmdline)
try:
  #freecad_return_code = subprocess.call(l_cmdline.split(' '), stdin=None, stdout=None, stderr=None, shell=False)
  freecad_output = subprocess.check_output(l_cmdline.split(' '), stdin=None, stderr=None, shell=False)
except:
  print("ERR054: Error, FreeCAD is not installed on your system!")
  print("Please, install the latest FreeCAD version on your system and re-run this script.")
  sys.exit(1)
# remove the tempory script
os.remove(checking_freecad_version_script_name)
#print("dbg111: freecad_return_code:", freecad_return_code)
#print("dbg112: freecad_output:", freecad_output)
# extract the verion from the freecad_output
freecad_verion = re.sub(r'\n', '', freecad_output, re.DOTALL)
freecad_verion = re.sub(r'^.*FREECAD_VERSION_START\[', '', freecad_verion, re.DOTALL) 
freecad_verion = re.sub(r'\]FREECAD_VERSION_STOP.*$', '', freecad_verion, re.DOTALL)
freecad_verion = re.sub(r",\s+'", ",'", freecad_verion, re.DOTALL)
freecad_verion = re.sub(r"'", "", freecad_verion, re.DOTALL)
freecad_verion = freecad_verion.split(',')
#print("dbg113: freecad_verion:", freecad_verion)
freecad_verion_major = int(freecad_verion[0])
freecad_verion_minor = int(freecad_verion[1])
if((freecad_verion_major==0)and(freecad_verion_minor<13)):
  print("ERR056: Error, Your FreeCAD version is too old! You have {:d}.{:d} and 0.13 or newer is needed.".format(freecad_verion_major, freecad_verion_minor))
  print("Please, install the latest FreeCAD version on your system and re-run this script.")
  sys.exit(1)
#info
print("The FreeCAD version {:d}.{:d} is installed on your system.".format(freecad_verion_major, freecad_verion_minor))

### check if the FreeCAD Library can be imported

#print("dbg449: sys.path:", sys.path)

try:
  import cnc25d.importing_freecad
except:
  print("ERR058: Error, cnc25d package is not installed!")
  print("Please, install the cnc25d package with the command 'sudo pip install Cnc25D -U'")
  sys.exit(1)

cnc25d.importing_freecad.importing_freecad()

try:
  FreeCAD.Console.PrintMessage("FreeCAD run from Cnc25D :)\n")
except:
  print("ERR060: Error, the package cnc25d can not use the FreeCAD library")
  sys.exit(1)

##############################################################################
# Creating the script example
##############################################################################
ceg_instructions="""
The example script {:s} has been created :)
To use it, just run the following command:
> python {:s}
You can rename, move, copy and edit the script {:s}
"""

### box_wood_frame script example
bwf_script_name="eg01_box_wood_frame_example.py"
# copy from ../cnc25d/tests/box_wood_frame_macro.py without the import stuff
bwf_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/box_wood_frame_macro.py
#
# box_wood_frame_macro.py
# the macro for a wood frame for building a shell or a straw house.
# created by charlyoleg on 2013/05/31
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design box_wood_frame
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. box_wood_frame will use a default value
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

bwf_constraint = {} # This python-dictionary contains all the constraint-parameters to build the box_wood_frame
bwf_constraint['box_width'] = 400.0
bwf_constraint['box_depth'] = 400.0
bwf_constraint['box_height'] = 400.0
bwf_constraint['fitting_height'] = 30.0
bwf_constraint['h_plank_width'] = 50.0
bwf_constraint['v_plank_width'] = 30.0
bwf_constraint['plank_height'] = 20.0
bwf_constraint['d_plank_width'] = 30.0
bwf_constraint['d_plank_height'] = 10.0
bwf_constraint['crenel_depth'] = 5.0
bwf_constraint['wall_diagonal_size'] = 50.0
bwf_constraint['tobo_diagonal_size'] = 100.0
bwf_constraint['diagonal_lining_top_height'] = 20.0
bwf_constraint['diagonal_lining_bottom_height'] = 20.0
bwf_constraint['module_width'] = 1
bwf_constraint['router_bit_radius'] = 2.0
bwf_constraint['cutting_extra'] = 2.0 # doesn't affect the cnc cutting plan
bwf_constraint['slab_thickness'] = 5.0

################################################################
# action
################################################################

my_bwf = cnc25d_design.box_wood_frame(bwf_constraint)
my_bwf.outline_display()
my_bwf.write_figure_svg("test_output/bwf_macro")
my_bwf.write_figure_dxf("test_output/bwf_macro")
my_bwf.write_figure_brep("test_output/bwf_macro")
my_bwf.write_assembly_brep("test_output/bwf_macro")
my_bwf.write_freecad_brep("test_output/bwf_macro")
#my_bwf.run_simulation("") # no simulation for box_wood_frame
my_bwf.view_design_configuration()
#my_bwf.run_self_test("")
#my_bwf.cli("--output_file_basename test_output/bwfm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_bwf.get_fc_obj_3dconf('bwf_3dconf1'))


'''

### cnc25d_api_example script
cgf_script_name="eg03_cnc25d_api_example.py"
# copy from ../cnc25d/tests/cnc25d_api_macro.py
cgf_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/cnc25d_api_macro.py
#
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
#   cnc25d_api.export_to_svg(freecad_part_object, direction_vector, depth, filename) => 0
#   cnc25d_api.export_xyz_to_dxf(freecad_part_object, x-size, y-size, z-size, x-depth-list, y-depth-list, z-depth-list, filename) => 0
#   cnc25d_api.mkdir_p(directory) => 0
#   cnc25d_api.get_effective_args(default_args) => [args]
#   cnc25d_api.generate_output_file_add_argument(argparse_parser) => argparse_parser
#   cnc25d_api.get_output_file_suffix(filename) => (basename, suffix)
#   cnc25d_api.generate_output_file(figure, filename, extrusion_height, info_txt) => 0
#   cnc25d_api.freecad_object_output_file(freecad_object, filename, brep, stl, slice_xyz) => 0
#   cnc25d_api.generate_3d_assembly_output_file(3D_conf, filename, brep, stl, slice_xyz) => 0
#   cnc25d_api.rotate_and_translate_figure(figure, x-center, y-center, angle, x-translate, y-translate) => figure
#   cnc25d_api.flip_rotate_and_translate_figure(figure, x-zero, y-zero, x-size, y-size, x-flip, y-flip, angle, x-translate, y-translate) => figure
#   cnc25d_api.cnc_cut_figure(A-figure, error_msg_id) => B-figure
#   cnc25d_api.ideal_figure(A-figure, error_msg_id) => B-figure
#   cnc25d_api.figures_to_freecad_assembly(3D_conf) => freecad_part_object


################################################################
# import
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
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


'''

### simple_cnc25d_api_example script
sca_script_name="eg02_simple_cnc25d_api_example.py"
# copy from ../cnc25d/tests/simple_cnc25d_api_macro.py
sca_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/simple_cnc25d_api_macro.py
#
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
#   cnc25d_api.ideal_outline(outline-AC, error_mark_string) => outline-B
#   cnc25d_api.outline_arc_line(outline-B, backend) => Tkinter or svgwrite or dxfwrite or FreeCAD stuff
#   cnc25d_api.Two_Canvas(Tkinter.Tk()) # object constructor
#   cnc25d_api.figure_simple_display(graphic_figure, overlay_figure, parameter_info) => 0
#   cnc25d_api.write_figure_in_svg(figure, filename) => 0
#   cnc25d_api.write_figure_in_dxf(figure, filename) => 0
#   cnc25d_api.figure_to_freecad_25d_part(figure, extrusion_height) => freecad_part_object
#   cnc25d_api.place_plank(freecad_part_object, x-size, y-size, z-size, flip, orientation, x-position, y-position, z-position) => freecad_part_object
#   cnc25d_api.export_to_dxf(freecad_part_object, direction_vector, depth, filename) => 0
#   cnc25d_api.export_to_svg(freecad_part_object, direction_vector, depth, filename) => 0
#   cnc25d_api.export_xyz_to_dxf(freecad_part_object, x-size, y-size, z-size, x-depth-list, y-depth-list, z-depth-list, filename) => 0
#   cnc25d_api.mkdir_p(directory) => 0
#   cnc25d_api.get_effective_args(default_args) => [args]
#   cnc25d_api.generate_output_file_add_argument(argparse_parser) => argparse_parser
#   cnc25d_api.get_output_file_suffix(filename) => (basename, suffix)
#   cnc25d_api.generate_output_file(figure, filename, extrusion_height, info_txt) => 0
#   cnc25d_api.freecad_object_output_file(freecad_object, filename, brep, stl, slice_xyz) => 0
#   cnc25d_api.generate_3d_assembly_output_file(3D_conf, filename, brep, stl, slice_xyz) => 0
#   cnc25d_api.rotate_and_translate_figure(figure, x-center, y-center, angle, x-translate, y-translate) => figure
#   cnc25d_api.flip_rotate_and_translate_figure(figure, x-zero, y-zero, x-size, y-size, x-flip, y-flip, angle, x-translate, y-translate) => figure
#   cnc25d_api.cnc_cut_figure(A-figure, error_msg_id) => B-figure
#   cnc25d_api.ideal_figure(A-figure, error_msg_id) => B-figure
#   cnc25d_api.figures_to_freecad_assembly(3D_conf) => freecad_part_object


################################################################
# import
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api # import the Cnc25D API modules
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
overlay_figure = [outer_rectangle_A, inner_shape_A, inner_circle1]

simple_figure_info = """
Some info there
that will appear in the parameter window
"""

# display the figure
cnc25d_api.figure_simple_display(simple_figure, overlay_figure, simple_figure_info)

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


'''

### gear_profile script example
gp_script_name="eg04_gear_profile_example.py"
# copy from ../cnc25d/tests/gear_profile_macro.py
gp_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gear_profile_macro.py
#
# gear_profile_macro.py
# the macro to generate a gear_profile.
# created by charlyoleg on 2013/08/27
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design gear_profile
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import gear_profile
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

gp_constraint = {}
### first gear
# general
gp_constraint['gear_type']                      = 'e'
gp_constraint['gear_tooth_nb']                  = 18
gp_constraint['gear_module']                    = 10.0
gp_constraint['gear_primitive_diameter']        = 0
gp_constraint['gear_addendum_dedendum_parity']  = 50.0
# tooth height
gp_constraint['gear_tooth_half_height']           = 0 # 10.0
gp_constraint['gear_addendum_height_pourcentage'] = 100.0
gp_constraint['gear_dedendum_height_pourcentage'] = 100.0
gp_constraint['gear_hollow_height_pourcentage']   = 25.0
gp_constraint['gear_router_bit_radius']           = 3.0
# positive involute
gp_constraint['gear_base_diameter']       = 0
gp_constraint['gear_force_angle']         = 0
gp_constraint['gear_tooth_resolution']    = 2
gp_constraint['gear_skin_thickness']      = 0
# negative involute (if zero, negative involute = positive involute)
gp_constraint['gear_base_diameter_n']     = 0
gp_constraint['gear_force_angle_n']       = 0
gp_constraint['gear_tooth_resolution_n']  = 0
gp_constraint['gear_skin_thickness_n']    = 0
### second gear
# general
gp_constraint['second_gear_type']                     = 'e'
gp_constraint['second_gear_tooth_nb']                 = 25
gp_constraint['second_gear_primitive_diameter']       = 0
gp_constraint['second_gear_addendum_dedendum_parity'] = 0 # 50.0
# tooth height
gp_constraint['second_gear_tooth_half_height']            = 0
gp_constraint['second_gear_addendum_height_pourcentage']  = 100.0
gp_constraint['second_gear_dedendum_height_pourcentage']  = 100.0
gp_constraint['second_gear_hollow_height_pourcentage']    = 25.0
gp_constraint['second_gear_router_bit_radius']            = 0
# positive involute
gp_constraint['second_gear_base_diameter']      = 0
gp_constraint['second_gear_tooth_resolution']   = 0
gp_constraint['second_gear_skin_thickness']     = 0
# negative involute (if zero, negative involute = positive involute)
gp_constraint['second_gear_base_diameter_n']    = 0
gp_constraint['second_gear_tooth_resolution_n'] = 0
gp_constraint['second_gear_skin_thickness_n']   = 0
### gearbar specific
gp_constraint['gearbar_slope']                  = 0.0
gp_constraint['gearbar_slope_n']                = 0.0
### position
# first gear position
gp_constraint['center_position_x']                    = 0.0
gp_constraint['center_position_y']                    = 0.0
gp_constraint['gear_initial_angle']                   = 0.0
# second gear position
gp_constraint['second_gear_position_angle']           = 0.0
gp_constraint['second_gear_additional_axis_length']   = 0.0
### portion
gp_constraint['cut_portion']     = (10, 3, 3) # (portion_tooth_nb, portion_first_end, portion_last_end)
### z-dimension
gp_constraint['gear_profile_height']  = 20.0



################################################################
# action
################################################################

my_gp = gear_profile.gear_profile(gp_constraint)
my_gp.outline_display()
my_gp.write_figure_svg("test_output/gear_profile_macro")
my_gp.write_figure_dxf("test_output/gear_profile_macro")
my_gp.write_figure_brep("test_output/gear_profile_macro")
my_gp.write_assembly_brep("test_output/gear_profile_macro")
my_gp.write_freecad_brep("test_output/gear_profile_macro")
my_gp.run_simulation("")
my_gp.view_design_configuration()
#my_gp.run_self_test("")
#my_gp.cli("--output_file_basename test_output/gpm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_gp.get_fc_obj_3dconf('gp_assembly_conf1'))



'''

### gearwheel script example
gw_script_name="eg05_gearwheel_example.py"
# copy from ../cnc25d/tests/gearwheel_macro.py
gw_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gearwheel_macro.py
#
# gearwheel_macro.py
# the macro to generate a gearwheel.
# created by charlyoleg on 2013/06/19
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design gearwheel
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

gw_constraint = {}
##### from gear_profile
### first gear
# general
#gw_constraint['gear_type']                      = 'e'
gw_constraint['gear_tooth_nb']                  = 18
gw_constraint['gear_module']                    = 10.0
gw_constraint['gear_primitive_diameter']        = 0
gw_constraint['gear_addendum_dedendum_parity']  = 50.0
# tooth height
gw_constraint['gear_tooth_half_height']           = 0 # 10.0
gw_constraint['gear_addendum_height_pourcentage'] = 100.0
gw_constraint['gear_dedendum_height_pourcentage'] = 100.0
gw_constraint['gear_hollow_height_pourcentage']   = 25.0
gw_constraint['gear_router_bit_radius']           = 3.0
# positive involute
gw_constraint['gear_base_diameter']       = 0
gw_constraint['gear_force_angle']         = 0
gw_constraint['gear_tooth_resolution']    = 2
gw_constraint['gear_skin_thickness']      = 0
# negative involute (if zero, negative involute = positive involute)
gw_constraint['gear_base_diameter_n']     = 0
gw_constraint['gear_force_angle_n']       = 0
gw_constraint['gear_tooth_resolution_n']  = 0
gw_constraint['gear_skin_thickness_n']    = 0
### second gear
# general
gw_constraint['second_gear_type']                     = 'e'
gw_constraint['second_gear_tooth_nb']                 = 25
gw_constraint['second_gear_primitive_diameter']       = 0
gw_constraint['second_gear_addendum_dedendum_parity'] = 0 # 50.0
# tooth height
gw_constraint['second_gear_tooth_half_height']            = 0
gw_constraint['second_gear_addendum_height_pourcentage']  = 100.0
gw_constraint['second_gear_dedendum_height_pourcentage']  = 100.0
gw_constraint['second_gear_hollow_height_pourcentage']    = 25.0
gw_constraint['second_gear_router_bit_radius']            = 0
# positive involute
gw_constraint['second_gear_base_diameter']      = 0
gw_constraint['second_gear_tooth_resolution']   = 0
gw_constraint['second_gear_skin_thickness']     = 0
# negative involute (if zero, negative involute = positive involute)
gw_constraint['second_gear_base_diameter_n']    = 0
gw_constraint['second_gear_tooth_resolution_n'] = 0
gw_constraint['second_gear_skin_thickness_n']   = 0
### gearbar specific
gw_constraint['gearbar_slope']                  = 0.0
gw_constraint['gearbar_slope_n']                = 0.0
### position
# first gear position
gw_constraint['center_position_x']                    = 0.0
gw_constraint['center_position_y']                    = 0.0
gw_constraint['gear_initial_angle']                   = 0.0
# second gear position
gw_constraint['second_gear_position_angle']           = 0.0
gw_constraint['second_gear_additional_axis_length']   = 0.0
### portion
#gw_constraint['portion_tooth_nb']     = 0
#gw_constraint['portion_first_end']    = 0
#gw_constraint['portion_last_end']     = 0
### output
gw_constraint['gear_profile_height']  = 20.0
##### from gearwheel
### axle
gw_constraint['axle_type']                = 'circle'
gw_constraint['axle_x_width']             = 20.0
gw_constraint['axle_y_width']             = 0.0
gw_constraint['axle_router_bit_radius']   = 2.0
### crenel
gw_constraint['crenel_number']       = 2
gw_constraint['crenel_type']         = 'rectangle' # 'rectangle' or 'circle'
gw_constraint['crenel_mark_nb']      = 0
gw_constraint['crenel_diameter']     = 0.0
gw_constraint['crenel_angle']        = 0.0
gw_constraint['crenel_tooth_align']  = 0
gw_constraint['crenel_width']        = 10.0
gw_constraint['crenel_height']       = 5.0
gw_constraint['crenel_router_bit_radius']      = 1.0
### wheel-hollow = legs
gw_constraint['wheel_hollow_leg_number']        = 7
gw_constraint['wheel_hollow_leg_width']         = 10.0
gw_constraint['wheel_hollow_leg_angle']         = 0.0
gw_constraint['wheel_hollow_internal_diameter'] = 40.0
gw_constraint['wheel_hollow_external_diameter'] = 125.0
gw_constraint['wheel_hollow_router_bit_radius'] = 5.0
### cnc router_bit constraint
gw_constraint['cnc_router_bit_radius']          = 1.0



################################################################
# action
################################################################

my_gw = cnc25d_design.gearwheel(gw_constraint)
my_gw.outline_display()
my_gw.write_figure_svg("test_output/gearwheel_macro")
my_gw.write_figure_dxf("test_output/gearwheel_macro")
my_gw.write_figure_brep("test_output/gearwheel_macro")
my_gw.write_assembly_brep("test_output/gearwheel_macro")
my_gw.write_freecad_brep("test_output/gearwheel_macro")
my_gw.run_simulation("")
my_gw.view_design_configuration()
#my_gw.run_self_test("")
#my_gw.cli("--output_file_basename test_output/gwm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_gw.get_fc_obj_3dconf('gearwheel_3dconf1'))




'''

### gearring script example
gr_script_name="eg06_gearring_example.py"
# copy from ../cnc25d/tests/gearring_macro.py
gr_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gearring_macro.py
#
# gearring_macro.py
# the macro to generate a gearring.
# created by charlyoleg on 2013/10/03
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design gearring
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

gr_constraint = {}
##### from gear_profile
### first gear
# general
#gr_constraint['gear_type']                      = 'i'
gr_constraint['gear_tooth_nb']                  = 31
gr_constraint['gear_module']                    = 10.0
gr_constraint['gear_primitive_diameter']        = 0
gr_constraint['gear_addendum_dedendum_parity']  = 50.0
# tooth height
gr_constraint['gear_tooth_half_height']           = 0 # 10.0
gr_constraint['gear_addendum_height_pourcentage'] = 100.0
gr_constraint['gear_dedendum_height_pourcentage'] = 100.0
gr_constraint['gear_hollow_height_pourcentage']   = 25.0
gr_constraint['gear_router_bit_radius']           = 0.0
# positive involute
gr_constraint['gear_base_diameter']       = 0
gr_constraint['gear_force_angle']         = 0
gr_constraint['gear_tooth_resolution']    = 2
gr_constraint['gear_skin_thickness']      = 0
# negative involute (if zero, negative involute = positive involute)
gr_constraint['gear_base_diameter_n']     = 0
gr_constraint['gear_force_angle_n']       = 0
gr_constraint['gear_tooth_resolution_n']  = 0
gr_constraint['gear_skin_thickness_n']    = 0
### second gear
# general
#gr_constraint['second_gear_type']                     = 'e'
gr_constraint['second_gear_tooth_nb']                 = 19
gr_constraint['second_gear_primitive_diameter']       = 0
gr_constraint['second_gear_addendum_dedendum_parity'] = 0 # 50.0
# tooth height
gr_constraint['second_gear_tooth_half_height']            = 0
gr_constraint['second_gear_addendum_height_pourcentage']  = 100.0
gr_constraint['second_gear_dedendum_height_pourcentage']  = 100.0
gr_constraint['second_gear_hollow_height_pourcentage']    = 25.0
gr_constraint['second_gear_router_bit_radius']            = 0
# positive involute
gr_constraint['second_gear_base_diameter']      = 0
gr_constraint['second_gear_tooth_resolution']   = 0
gr_constraint['second_gear_skin_thickness']     = 0
# negative involute (if zero, negative involute = positive involute)
gr_constraint['second_gear_base_diameter_n']    = 0
gr_constraint['second_gear_tooth_resolution_n'] = 0
gr_constraint['second_gear_skin_thickness_n']   = 0
### gearbar specific
#gr_constraint['gearbar_slope']                  = 0.0
#gr_constraint['gearbar_slope_n']                = 0.0
### position
# first gear position
gr_constraint['center_position_x']                    = 0.0
gr_constraint['center_position_y']                    = 0.0
gr_constraint['gear_initial_angle']                   = 0.0
# second gear position
gr_constraint['second_gear_position_angle']           = 0.0
gr_constraint['second_gear_additional_axis_length']   = 0.0
### portion
#gr_constraint['portion_tooth_nb']     = 0
#gr_constraint['portion_first_end']    = 0
#gr_constraint['portion_last_end']     = 0
### z-dimension
gr_constraint['gear_profile_height']  = 20.0
##### from gearring
### holder
gr_constraint['holder_diameter']            = 360.0
gr_constraint['holder_crenel_number']       = 6
gr_constraint['holder_position_angle']      = 0.0
gr_constraint['holder_crenel_number_cut']   = 0
### holder-hole
gr_constraint['holder_hole_position_radius']   = 0.0
gr_constraint['holder_hole_diameter']          = 10.0
gr_constraint['holder_hole_mark_nb']           = 0
gr_constraint['holder_double_hole_diameter']   = 0.0
gr_constraint['holder_double_hole_length']     = 0.0
gr_constraint['holder_double_hole_position']   = 0.0
gr_constraint['holder_double_hole_mark_nb']    = 0
### holder-crenel
gr_constraint['holder_crenel_position']        = 10.0
gr_constraint['holder_crenel_height']          = 10.0
gr_constraint['holder_crenel_width']           = 10.0
gr_constraint['holder_crenel_skin_width']      = 10.0
gr_constraint['holder_crenel_router_bit_radius']   = 1.0
gr_constraint['holder_smoothing_radius']       = 0.0
### holder-hole-B (experimental)
gr_constraint['holder_hole_B_diameter']          = 10.0
gr_constraint['holder_crenel_B_position']        = 10.0
gr_constraint['holder_hole_B_crenel_list']       = []
### cnc router_bit constraint
gr_constraint['cnc_router_bit_radius']          = 1.0

################################################################
# action
################################################################

my_gr = cnc25d_design.gearring(gr_constraint)
my_gr.outline_display()
my_gr.write_figure_svg("test_output/gearring_macro")
my_gr.write_figure_dxf("test_output/gearring_macro")
my_gr.write_figure_brep("test_output/gearring_macro")
my_gr.write_assembly_brep("test_output/gearring_macro")
my_gr.write_freecad_brep("test_output/gearring_macro")
my_gr.run_simulation("")
my_gr.view_design_configuration()
#my_gr.run_self_test("")
#my_gr.cli("--output_file_basename test_output/grm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_gr.get_fc_obj_3dconf('gearring_3dconf1'))



'''

### gearbar script example
gb_script_name="eg07_gearbar_example.py"
# copy from ../cnc25d/tests/gearbar_macro.py
gb_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gearbar_macro.py
#
# gearbar_macro.py
# the macro to generate a gearbar
# created by charlyoleg on 2013/10/02
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design gearbar
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

gb_constraint = {}
##### from gear_profile
### first gear
# general
#gb_constraint['gear_type']                      = 'l'
gb_constraint['gear_tooth_nb']                  = 5
gb_constraint['gear_module']                    = 10.0
gb_constraint['gear_primitive_diameter']        = 0
gb_constraint['gear_addendum_dedendum_parity']  = 50.0
# tooth height
gb_constraint['gear_tooth_half_height']           = 0 # 10.0
gb_constraint['gear_addendum_height_pourcentage'] = 100.0
gb_constraint['gear_dedendum_height_pourcentage'] = 100.0
gb_constraint['gear_hollow_height_pourcentage']   = 25.0
gb_constraint['gear_router_bit_radius']           = 3.0
# positive involute
gb_constraint['gear_base_diameter']       = 0
gb_constraint['gear_force_angle']         = 0
gb_constraint['gear_tooth_resolution']    = 2
gb_constraint['gear_skin_thickness']      = 0
# negative involute (if zero, negative involute = positive involute)
gb_constraint['gear_base_diameter_n']     = 0
gb_constraint['gear_force_angle_n']       = 0
gb_constraint['gear_tooth_resolution_n']  = 0
gb_constraint['gear_skin_thickness_n']    = 0
### second gear
# general
#gb_constraint['second_gear_type']                     = 'e'
gb_constraint['second_gear_tooth_nb']                 = 25
gb_constraint['second_gear_primitive_diameter']       = 0
gb_constraint['second_gear_addendum_dedendum_parity'] = 0 # 50.0
# tooth height
gb_constraint['second_gear_tooth_half_height']            = 0
gb_constraint['second_gear_addendum_height_pourcentage']  = 100.0
gb_constraint['second_gear_dedendum_height_pourcentage']  = 100.0
gb_constraint['second_gear_hollow_height_pourcentage']    = 25.0
gb_constraint['second_gear_router_bit_radius']            = 0
# positive involute
gb_constraint['second_gear_base_diameter']      = 230.0
gb_constraint['second_gear_tooth_resolution']   = 0
gb_constraint['second_gear_skin_thickness']     = 0
# negative involute (if zero, negative involute = positive involute)
gb_constraint['second_gear_base_diameter_n']    = 0
gb_constraint['second_gear_tooth_resolution_n'] = 0
gb_constraint['second_gear_skin_thickness_n']   = 0
### gearbar specific
gb_constraint['gearbar_slope']                  = 0.0
gb_constraint['gearbar_slope_n']                = 0.0
### position
# first gear position
gb_constraint['center_position_x']                    = 0.0
gb_constraint['center_position_y']                    = 0.0
gb_constraint['gear_initial_angle']                   = 0.0
# second gear position
gb_constraint['second_gear_position_angle']           = 0.0
gb_constraint['second_gear_additional_axis_length']   = 0.0
### portion
gb_constraint['cut_portion']     = (8, 3, 3) # (portion_tooth_nb, portion_first_end, portion_last_end)
### output
gb_constraint['gear_profile_height']  = 20.0
##### from gearwheel
### gearbar
gb_constraint['gearbar_height']                 = 30.0
### gearbar-hole
gb_constraint['gearbar_hole_height_position']   = 10.0
gb_constraint['gearbar_hole_diameter']          = 10.0
gb_constraint['gearbar_hole_offset']            = 0
gb_constraint['gearbar_hole_increment']         = 1

################################################################
# action
################################################################

my_gb = cnc25d_design.gearbar(gb_constraint)
my_gb.outline_display()
my_gb.write_figure_svg("test_output/gearbar_macro")
my_gb.write_figure_dxf("test_output/gearbar_macro")
my_gb.write_figure_brep("test_output/gearbar_macro")
my_gb.write_assembly_brep("test_output/gearbar_macro")
my_gb.write_freecad_brep("test_output/gearbar_macro")
my_gb.run_simulation("")
my_gb.view_design_configuration()
#my_gb.run_self_test("")
#my_gb.cli("--output_file_basename test_output/gbm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_gb.get_fc_obj_3dconf('gearbar_3dconf1'))



'''

### split_gearwheel script example
sgw_script_name="eg08_split_gearwheel_example.py"
# copy from ../cnc25d/tests/split_gearwheel_macro.py
sgw_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/split_gearwheel_macro.py
#
# split_gearwheel_macro.py
# the macro to generate a split_gearwheel.
# created by charlyoleg on 2013/10/03
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design split_gearwheel
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

sgw_constraint = {}
##### from gear_profile
### first gear
# general
#sgw_constraint['gear_type']                      = 'e'
sgw_constraint['gear_tooth_nb']                  = 27
sgw_constraint['gear_module']                    = 10.0
sgw_constraint['gear_primitive_diameter']        = 0
sgw_constraint['gear_addendum_dedendum_parity']  = 50.0
# tooth height
sgw_constraint['gear_tooth_half_height']           = 0 # 10.0
sgw_constraint['gear_addendum_height_pourcentage'] = 100.0
sgw_constraint['gear_dedendum_height_pourcentage'] = 100.0
sgw_constraint['gear_hollow_height_pourcentage']   = 25.0
sgw_constraint['gear_router_bit_radius']           = 3.0
# positive involute
sgw_constraint['gear_base_diameter']       = 0
sgw_constraint['gear_force_angle']         = 0
sgw_constraint['gear_tooth_resolution']    = 2
sgw_constraint['gear_skin_thickness']      = 0
# negative involute (if zero, negative involute = positive involute)
sgw_constraint['gear_base_diameter_n']     = 0
sgw_constraint['gear_force_angle_n']       = 0
sgw_constraint['gear_tooth_resolution_n']  = 0
sgw_constraint['gear_skin_thickness_n']    = 0
### second gear
# general
sgw_constraint['second_gear_type']                     = 'e'
sgw_constraint['second_gear_tooth_nb']                 = 25
sgw_constraint['second_gear_primitive_diameter']       = 0
sgw_constraint['second_gear_addendum_dedendum_parity'] = 0 # 50.0
# tooth height
sgw_constraint['second_gear_tooth_half_height']            = 0
sgw_constraint['second_gear_addendum_height_pourcentage']  = 100.0
sgw_constraint['second_gear_dedendum_height_pourcentage']  = 100.0
sgw_constraint['second_gear_hollow_height_pourcentage']    = 25.0
sgw_constraint['second_gear_router_bit_radius']            = 0
# positive involute
sgw_constraint['second_gear_base_diameter']      = 0
sgw_constraint['second_gear_tooth_resolution']   = 0
sgw_constraint['second_gear_skin_thickness']     = 0
# negative involute (if zero, negative involute = positive involute)
sgw_constraint['second_gear_base_diameter_n']    = 0
sgw_constraint['second_gear_tooth_resolution_n'] = 0
sgw_constraint['second_gear_skin_thickness_n']   = 0
### gearbar specific
sgw_constraint['gearbar_slope']                  = 0.0
sgw_constraint['gearbar_slope_n']                = 0.0
### position
# first gear position
sgw_constraint['center_position_x']                    = 0.0
sgw_constraint['center_position_y']                    = 0.0
sgw_constraint['gear_initial_angle']                   = 0.0
# second gear position
sgw_constraint['second_gear_position_angle']           = 0.0
sgw_constraint['second_gear_additional_axis_length']   = 0.0
### portion
#sgw_constraint['portion_tooth_nb']     = 0
#sgw_constraint['portion_first_end']    = 0
#sgw_constraint['portion_last_end']     = 0
### z-dimension
sgw_constraint['gear_profile_height']  = 20.0
#sgw_constraint['output_file_basename'] = "test_output/bla"
##### from split_gearwheel
### split
sgw_constraint['split_nb']                 = 6
sgw_constraint['split_initial_angle']      = 0.0
sgw_constraint['low_split_diameter']       = 100.0
sgw_constraint['low_split_type']           = 'circle'
sgw_constraint['high_split_diameter']      = 0.0
sgw_constraint['high_split_type']          = 'h'
sgw_constraint['split_router_bit_radius']  = 1.0
### low-holes
sgw_constraint['low_hole_circle_diameter']   = 0.0
sgw_constraint['low_hole_diameter']          = 10.0
sgw_constraint['low_hole_nb']                = 1
### high-holes
sgw_constraint['high_hole_circle_diameter']  = 0.0
sgw_constraint['high_hole_diameter']         = 10.0
sgw_constraint['high_hole_nb']               = 2
### cnc router_bit constraint
sgw_constraint['cnc_router_bit_radius']          = 1.0



################################################################
# action
################################################################

my_sgw = cnc25d_design.split_gearwheel(sgw_constraint)
my_sgw.outline_display()
my_sgw.write_figure_svg("test_output/sgw_macro")
my_sgw.write_figure_dxf("test_output/sgw_macro")
my_sgw.write_figure_brep("test_output/sgw_macro")
my_sgw.write_assembly_brep("test_output/sgw_macro")
my_sgw.write_freecad_brep("test_output/sgw_macro")
my_sgw.run_simulation("")
my_sgw.view_design_configuration()
#my_sgw.run_self_test("")
#my_sgw.cli("--output_file_basename test_output/alm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_sgw.get_fc_obj_3dconf('split_gearwheel_3dconf1'))



'''

### epicyclic_gearing script example
eg_script_name="eg09_epicyclic_gearing_example.py"
# copy from ../cnc25d/tests/epicyclic_gearing_macro.py
eg_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/epicyclic_gearing_macro.py
#
# epicyclic_gearing_macro.py
# the macro to generate an epicyclic_gearing.
# created by charlyoleg on 2013/10/03
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design epicyclic_gearing
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################

eg_constraint = {}
#### epicyclic_gearing dictionary entries
### structure
eg_constraint['sun_gear_tooth_nb']       = 20
eg_constraint['planet_gear_tooth_nb']    = 31
eg_constraint['planet_nb']               = 3
### gear
eg_constraint['gear_module']             = 1.0
eg_constraint['gear_router_bit_radius']  = 0.1
eg_constraint['gear_tooth_resolution']   = 2
eg_constraint['gear_skin_thickness']     = 0.0
eg_constraint['gear_addendum_dedendum_parity_slack']      = 0.0
eg_constraint['gearring_dedendum_to_hollow_pourcentage']  = 0.0
eg_constraint['gear_addendum_height_pourcentage']         = 100.0
### sun-gear
eg_constraint['sun_axle_type']           = 'circle' # 'none', 'circle' or 'rectangle'
eg_constraint['sun_axle_x_width']        = 12.0
eg_constraint['sun_axle_y_width']        = 0.0
eg_constraint['sun_crenel_nb']           = 4
eg_constraint['sun_crenel_tooth_align']  = 0
eg_constraint['sun_crenel_type']         = 'rectangle' # 'rectangle' or 'circle'
eg_constraint['sun_crenel_mark_nb']      = 0
eg_constraint['sun_crenel_diameter']     = 0.0
eg_constraint['sun_crenel_width']        = 3.0
eg_constraint['sun_crenel_height']       = 1.0
eg_constraint['sun_crenel_router_bit_radius']   = 0.1
### planet-gear
eg_constraint['planet_axle_diameter']      = 10.0
eg_constraint['planet_crenel_nb']          = 0
eg_constraint['planet_crenel_tooth_align'] = 0
eg_constraint['planet_crenel_type']        = 'rectangle' # 'rectangle' or 'circle'
eg_constraint['planet_crenel_mark_nb']     = 0
eg_constraint['planet_crenel_diameter']    = 0.0
eg_constraint['planet_crenel_width']       = 4.0
eg_constraint['planet_crenel_height']      = 2.0
eg_constraint['planet_crenel_router_bit_radius']  = 0.1
### planet gear carrier
eg_constraint['carrier_central_diameter']               = 0.0
eg_constraint['carrier_leg_diameter']                   = 0.0
eg_constraint['carrier_peripheral_disable']             = False
eg_constraint['carrier_hollow_disable']                 = False
eg_constraint['carrier_peripheral_external_diameter']   = 0.0
eg_constraint['carrier_peripheral_internal_diameter']   = 0.0
eg_constraint['carrier_leg_middle_diameter']            = 0.0
eg_constraint['carrier_smoothing_radius']               = 0.0
eg_constraint['carrier_leg_hole_diameter']              = 10.0
## carrier peripheral crenel
eg_constraint['carrier_crenel_width']                = 4.0
eg_constraint['carrier_crenel_height']               = 2.0
eg_constraint['carrier_crenel_router_bit_radius']    = 0.1
eg_constraint['carrier_hole_position_diameter']      = 0.0
eg_constraint['carrier_hole_diameter']               = 0.0
eg_constraint['carrier_double_hole_length']          = 0.0
## planet carrier angle
eg_constraint['planet_carrier_angle']                = 0.0
### annulus: inherit dictionary entries from gearring
### holder
eg_constraint['holder_diameter']            = 0.0
eg_constraint['holder_crenel_number']       = 6
eg_constraint['holder_position_angle']      = 0.0
### holder-hole
eg_constraint['holder_hole_position_radius']   = 0.0
eg_constraint['holder_hole_diameter']          = 5.0
eg_constraint['holder_hole_mark_nb']           = 0
eg_constraint['holder_double_hole_diameter']   = 0.0
eg_constraint['holder_double_hole_length']     = 0.0
eg_constraint['holder_double_hole_position']   = 0.0
eg_constraint['holder_double_hole_mark_nb']    = 0
### holder-crenel
eg_constraint['holder_crenel_position']        = 4.0
eg_constraint['holder_crenel_height']          = 2.0
eg_constraint['holder_crenel_width']           = 10.0
eg_constraint['holder_crenel_skin_width']      = 5.0
eg_constraint['holder_crenel_router_bit_radius']   = 1.0
eg_constraint['holder_smoothing_radius']       = 0.0
### holder-hole-B (experimental)
eg_constraint['holder_hole_B_diameter']          = 10.0
eg_constraint['holder_crenel_B_position']        = 10.0
eg_constraint['holder_hole_B_crenel_list']       = []
#### side-cover
### input-gearwheel
eg_constraint['input_gearwheel_tooth_nb']                  = 0
eg_constraint['input_gearwheel_module']                    = 1.0
eg_constraint['input_gearwheel_axle_diameter']             = 0.0
eg_constraint['input_gearwheel_crenel_number']             = 0
eg_constraint['input_gearwheel_crenel_position_diameter']  = 0.0
eg_constraint['input_gearwheel_crenel_diameter']           = 0.0
eg_constraint['input_gearwheel_crenel_angle']              = 0.0
eg_constraint['input_cover_extra_space']                   = 0.0
### output-gearwheel
eg_constraint['output_gearwheel_tooth_nb']                  = 0
eg_constraint['output_gearwheel_module']                    = 1.0
eg_constraint['output_gearwheel_axle_diameter']             = 0.0
eg_constraint['output_gearwheel_crenel_number']             = 0
eg_constraint['output_gearwheel_crenel_position_diameter']  = 0.0
eg_constraint['output_gearwheel_crenel_diameter']           = 0.0
eg_constraint['output_gearwheel_crenel_angle']              = 0.0
eg_constraint['output_cover_extra_space']                   = 0.0
### axle-lid
eg_constraint['top_clearance_diameter']     = 0.0
eg_constraint['top_axle_hole_diameter']     = 0.0
eg_constraint['top_central_diameter']       = 0.0
### general
eg_constraint['cnc_router_bit_radius']   = 0.1
eg_constraint['gear_profile_height']     = 10.0

################################################################
# action
################################################################

my_eg = cnc25d_design.epicyclic_gearing(eg_constraint)
my_eg.outline_display()
my_eg.write_figure_svg("test_output/epicyclic_macro")
my_eg.write_figure_dxf("test_output/epicyclic_macro")
my_eg.write_figure_brep("test_output/epicyclic_macro")
my_eg.write_assembly_brep("test_output/epicyclic_macro")
my_eg.write_freecad_brep("test_output/epicyclic_macro")
my_eg.run_simulation("eg_sim_planet_sun")
my_eg.run_simulation("eg_sim_annulus_planet")
my_eg.view_design_configuration()
#my_eg.run_self_test("")
#my_eg.cli("--output_file_basename test_output/egm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_eg.get_fc_obj_3dconf('epicyclic_gearing_3dconf1'))



'''

### axle_lid script example
al_script_name="eg10_axle_lid_example.py"
# copy from ../cnc25d/tests/axle_lid_macro.py
al_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/axle_lid_macro.py
#
# axle_lid_macro.py
# the macro to generate an axle_lid.
# created by charlyoleg on 2013/10/15
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design axle_lid
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################

al_constraint = {}
### annulus-holder: inherit dictionary entries from gearring
### holder
al_constraint['holder_diameter']            = 120.0
al_constraint['holder_crenel_number']       = 6
al_constraint['holder_position_angle']      = 0.0
### holder-hole
al_constraint['holder_hole_position_radius']   = 0.0
al_constraint['holder_hole_diameter']          = 5.0
al_constraint['holder_double_hole_diameter']   = 0.0
al_constraint['holder_double_hole_length']     = 0.0
al_constraint['holder_double_hole_position']   = 0.0
### holder-crenel
al_constraint['holder_crenel_position']        = 4.0
al_constraint['holder_crenel_height']          = 2.0
al_constraint['holder_crenel_width']           = 10.0
al_constraint['holder_crenel_skin_width']      = 5.0
al_constraint['holder_crenel_router_bit_radius']   = 1.0
al_constraint['holder_smoothing_radius']       = 0.0
#### axle_lid
al_constraint['clearance_diameter']           = 100.0
al_constraint['central_diameter']             = 40.0
al_constraint['axle_hole_diameter']           = 22.0
al_constraint['annulus_holder_axle_hole_diameter'] = 0.0
### axle-B
al_constraint['output_axle_B_place']              = 'none' # 'none', 'small' or 'large' # useful when the gearring has an odd number of crenels
al_constraint['output_axle_distance']             = 0.0
al_constraint['output_axle_angle']                = 0.0
al_constraint['output_axle_B_internal_diameter']  = 0.0
al_constraint['output_axle_B_external_diameter']  = 0.0
al_constraint['output_axle_B_crenel_number']              = 0
al_constraint['output_axle_B_crenel_diameter']            = 0.0
al_constraint['output_axle_B_crenel_position_diameter']   = 0.0
al_constraint['output_axle_B_crenel_angle']               = 0.0
al_constraint['input_axle_B_enable']                      = False
### leg
al_constraint['leg_type']             = 'none' # 'none', 'rear' or 'side'
al_constraint['leg_length']           = 0.0
al_constraint['foot_length']          = 0.0
al_constraint['toe_length']           = 0.0
al_constraint['leg_hole_diameter']    = 0.0
al_constraint['leg_hole_distance']    = 0.0
al_constraint['leg_hole_length']      = 0.0
al_constraint['leg_border_length']    = 0.0
al_constraint['leg_shift_length']     = 0.0
### general
al_constraint['smoothing_radius']       = 0.0
al_constraint['cnc_router_bit_radius']  = 0.1
al_constraint['extrusion_height']     = 10.0

################################################################
# action
################################################################

my_al = cnc25d_design.axle_lid(al_constraint)
my_al.outline_display()
my_al.write_figure_svg("test_output/axle_lid_macro")
my_al.write_figure_dxf("test_output/axle_lid_macro")
my_al.write_figure_brep("test_output/axle_lid_macro")
my_al.write_assembly_brep("test_output/axle_lid_macro")
my_al.write_freecad_brep("test_output/axle_lid_macro")
#my_al.run_simulation("") # no simulation for axle_lid
my_al.view_design_configuration()
#my_al.run_self_test("")
#my_al.cli("--output_file_basename test_output/alm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_al.get_fc_obj_3dconf('axle_lid_3dconf1'))



'''

### motor_lid script example
ml_script_name="eg11_motor_lid_example.py"
# copy from ../cnc25d/tests/motor_lid_macro.py
ml_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/motor_lid_macro.py
#
# motor_lid_macro.py
# the macro to generate a motor_lid.
# created by charlyoleg on 2013/11/15
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design motor_lid
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################

ml_constraint = {}
### annulus-holder: inherit dictionary entries from gearring
### holder
ml_constraint['holder_diameter']            = 120.0
ml_constraint['holder_crenel_number']       = 6
ml_constraint['holder_position_angle']      = 0.0
### holder-hole
ml_constraint['holder_hole_position_radius']   = 0.0
ml_constraint['holder_hole_diameter']          = 5.0
ml_constraint['holder_double_hole_diameter']   = 0.0
ml_constraint['holder_double_hole_length']     = 0.0
ml_constraint['holder_double_hole_position']   = 0.0
### holder-crenel
ml_constraint['holder_crenel_position']        = 4.0
ml_constraint['holder_crenel_height']          = 2.0
ml_constraint['holder_crenel_width']           = 10.0
ml_constraint['holder_crenel_skin_width']      = 5.0
ml_constraint['holder_crenel_router_bit_radius']   = 1.0
ml_constraint['holder_smoothing_radius']       = 0.0
#### axle_lid
ml_constraint['clearance_diameter']           = 100.0
ml_constraint['central_diameter']             = 40.0
ml_constraint['axle_hole_diameter']           = 22.0
ml_constraint['annulus_holder_axle_hole_diameter'] = 0.0
### input axle-B
ml_constraint['axle_B_place']             = 'small' # 'small' or 'large' # useful when the gearring has an odd number of crenels
ml_constraint['axle_B_distance']          = 65.0
ml_constraint['axle_B_angle']             = 0.0
ml_constraint['axle_B_diameter']          = 3.0
ml_constraint['axle_B_external_diameter'] = 10.0
ml_constraint['axle_B_hole_diameter']     = 15.0
ml_constraint['axle_B_central_diameter']  = 12.0
### input axle-C
ml_constraint['axle_C_distance']          = 40.0
ml_constraint['axle_C_angle']             = 0.0
ml_constraint['axle_C_hole_diameter']     = 10.0
ml_constraint['axle_C_external_diameter'] = 30.0
### motor screws
ml_constraint['motor_screw1_diameter']    = 2.0
ml_constraint['motor_screw1_angle']       = 0.0
ml_constraint['motor_screw1_x_length']    = 10.0
ml_constraint['motor_screw1_y_length']    = 0.0
ml_constraint['motor_screw2_diameter']    = 0.0
ml_constraint['motor_screw2_angle']       = 0.0
ml_constraint['motor_screw2_x_length']    = 0.0
ml_constraint['motor_screw2_y_length']    = 0.0
ml_constraint['motor_screw3_diameter']    = 0.0
ml_constraint['motor_screw3_angle']       = 0.0
ml_constraint['motor_screw3_x_length']    = 0.0
ml_constraint['motor_screw3_y_length']    = 0.0
### holder-C
ml_constraint['fastening_BC_hole_diameter']     = 2.0
ml_constraint['fastening_BC_external_diameter'] = 6.0
ml_constraint['fastening_BC_bottom_position_diameter']  = 30.0
ml_constraint['fastening_BC_bottom_angle']              = 3.14/4
ml_constraint['fastening_BC_top_position_diameter']     = 30.0
ml_constraint['fastening_BC_top_angle']                 = 3.14/4
### leg
ml_constraint['leg_type']             = 'none' # 'none', 'rear' or 'side'
ml_constraint['leg_length']           = 0.0
ml_constraint['foot_length']          = 0.0
ml_constraint['toe_length']           = 0.0
ml_constraint['leg_hole_diameter']    = 0.0
ml_constraint['leg_hole_distance']    = 0.0
ml_constraint['leg_hole_length']      = 0.0
ml_constraint['leg_border_length']    = 0.0
ml_constraint['leg_shift_length']     = 0.0
### general
ml_constraint['smoothing_radius']       = 3.0
ml_constraint['cnc_router_bit_radius']  = 0.1
ml_constraint['extrusion_height']     = 10.0

################################################################
# action
################################################################

my_ml = cnc25d_design.motor_lid(ml_constraint)
my_ml.outline_display()
my_ml.write_figure_svg("test_output/ml_macro")
my_ml.write_figure_dxf("test_output/ml_macro")
my_ml.write_figure_brep("test_output/ml_macro")
my_ml.write_assembly_brep("test_output/ml_macro")
my_ml.write_freecad_brep("test_output/ml_macro")
#my_ml.run_simulation("") # no simulation for motor_lid
my_ml.view_design_configuration()
#my_ml.run_self_test("")
#my_ml.cli("--output_file_basename test_output/mlm.dxf") # Warning: all constraint values are reset to their default values


if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_ml.get_fc_obj_3dconf('motor_lid_3dconf1'))




'''

### bell script example
bell_script_name="eg12_bell_example.py"
# copy from ../cnc25d/tests/bell_macro.py
bell_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/bell_macro.py
#
# bell_macro.py
# the macro to generate a bell piece, the extremity of a gimbal system
# created by charlyoleg on 2013/12/01
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design bell
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it.  Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

bell_constraint = {} # This python-dictionary contains all the constraint-parameters to build the bell piece (part of a gimbal)
### bell_face
## bulk
bell_constraint['axle_internal_diameter']          = 20.0
bell_constraint['axle_external_diameter']          = 0.0
bell_constraint['leg_length']                      = 40.0
bell_constraint['bell_face_height']                = 80.0
bell_constraint['bell_face_width']                 = 80.0
### bell_base_disc
bell_constraint['base_diameter']                   = 160.0
## wall_thickness
bell_constraint['face_thickness']                  = 6.0
bell_constraint['side_thickness']                  = 4.0
bell_constraint['base_thickness']                  = 8.0
## axle_hole
bell_constraint['axle_hole_nb']                    = 6
bell_constraint['axle_hole_diameter']              = 4.0
bell_constraint['axle_hole_position_diameter']     = 0.0
bell_constraint['axle_hole_angle']                 = 0.0
## leg
bell_constraint['leg_spare_width']                 = 10.0
bell_constraint['leg_smoothing_radius']            = 30.0
## motor_hole
bell_constraint['motor_hole_diameter']             = 4.0
bell_constraint['motor_hole_x_distance']           = 40.0
bell_constraint['motor_hole_z_distance']           = 50.0
bell_constraint['motor_hole_z_position']           = 40.0
## internal_buttress
bell_constraint['int_buttress_x_length']           = 10.0
bell_constraint['int_buttress_z_width']            = 5.0
bell_constraint['int_buttress_z_distance']         = 50.0
bell_constraint['int_buttress_x_position']         = 10.0
bell_constraint['int_buttress_z_position']         = 10.0
bell_constraint['int_buttress_int_corner_length']  = 5.0
bell_constraint['int_buttress_ext_corner_length']  = 5.0
bell_constraint['int_buttress_bump_length']        = 10.0
bell_constraint['int_buttress_arc_height']         = -2.0
bell_constraint['int_buttress_smoothing_radius']   = 10.0
## external_buttress
bell_constraint['ext_buttress_z_length']           = 10.0
bell_constraint['ext_buttress_x_width']            = 5.0
bell_constraint['ext_buttress_x_distance']         = 20.0
bell_constraint['ext_buttress_z_position']         = 40.0
bell_constraint['ext_buttress_y_length']           = 10.0
bell_constraint['ext_buttress_y_position']         = 20.0
bell_constraint['ext_buttress_face_int_corner_length']   = 5.0
bell_constraint['ext_buttress_face_ext_corner_length']   = 5.0
bell_constraint['ext_buttress_face_bump_length']         = 10.0
bell_constraint['ext_buttress_base_int_corner_length']   = 5.0
bell_constraint['ext_buttress_base_ext_corner_length']   = 5.0
bell_constraint['ext_buttress_base_bump_length']         = 10.0
bell_constraint['ext_buttress_arc_height']               = -5.0
bell_constraint['ext_buttress_smoothing_radius']         = 10.0
### bell_side
## hollow
bell_constraint['hollow_z_height']                 = 10.0
bell_constraint['hollow_y_width']                  = 20.0
bell_constraint['hollow_spare_width']              = 10.0
## base_hole
bell_constraint['base_hole_nb']                    = 8
bell_constraint['base_hole_diameter']              = 4.0
bell_constraint['base_hole_position_diameter']     = 0.0
bell_constraint['base_hole_angle']                 = 0.0
### xyz-axles
## y_hole
bell_constraint['y_hole_diameter']                 = 4.0
bell_constraint['y_hole_z_top_position']           = 10.0
bell_constraint['y_hole_z_bottom_position']        = 10.0
bell_constraint['y_hole_x_position']               = 6.0
## x_hole
bell_constraint['x_hole_diameter']                 = 4.0
bell_constraint['x_hole_z_top_position']           = -6.0
bell_constraint['x_hole_z_bottom_position']        = -6.0
bell_constraint['x_hole_y_position']               = 6.0
## z_hole
bell_constraint['z_hole_diameter']                 = 4.0
bell_constraint['z_hole_external_diameter']        = 0.0
bell_constraint['z_hole_position_length']          = 15.0
### manufacturing
bell_constraint['bell_cnc_router_bit_radius']      = 1.0
bell_constraint['bell_extra_cut_thickness']        = 0.0

################################################################
# action
################################################################

my_bell = cnc25d_design.bell(bell_constraint)
my_bell.outline_display()
my_bell.write_figure_svg("test_output/bell_macro")
my_bell.write_figure_dxf("test_output/bell_macro")
my_bell.write_figure_brep("test_output/bell_macro")
my_bell.write_assembly_brep("test_output/bell_macro")
my_bell.write_freecad_brep("test_output/bell_macro")
#my_bell.run_simulation("") # no simulation for bell
my_bell.view_design_configuration()
#my_bell.run_self_test("")
#my_bell.cli("--output_file_basename test_output/bm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_bell.get_fc_obj_3dconf('bell_assembly_conf2'))



'''

### bagel script example
bagel_script_name="eg13_bagel_example.py"
# copy from ../cnc25d/tests/bagel_macro.py
bagel_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/bagel_macro.py
#
# bagel_macro.py
# the macro to generate a bagel, the axle-guidance of the bell piece
# created by charlyoleg on 2013/12/02
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design bagel
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it.  Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

bagel_constraint = {} # This python-dictionary contains all the constraint-parameters to build the bagel piece (part of a gimbal)
### bagel_face
## bulk
bagel_constraint['bagel_axle_diameter']                   = 10.0
bagel_constraint['bagel_axle_internal_diameter']          = 0.0
bagel_constraint['bagel_axle_external_diameter']          = 0.0
## axle_hole
bagel_constraint['axle_hole_nb']                    = 6
bagel_constraint['axle_hole_diameter']              = 4.0
bagel_constraint['axle_hole_position_diameter']     = 0.0
bagel_constraint['axle_hole_angle']                 = 0.0
## wall_thickness
bagel_constraint['external_bagel_thickness']        = 2.0
bagel_constraint['middle_bagel_thickness']          = 6.0
bagel_constraint['internal_bagel_thickness']        = 2.0
### manufacturing
bagel_constraint['bagel_extra_cut_thickness']       = 0.0

################################################################
# action
################################################################

my_bagel = cnc25d_design.bagel(bagel_constraint)
my_bagel.outline_display()
my_bagel.write_figure_svg("test_output/bagel_macro")
my_bagel.write_figure_dxf("test_output/bagel_macro")
my_bagel.write_figure_brep("test_output/bagel_macro")
my_bagel.write_assembly_brep("test_output/bagel_macro")
my_bagel.write_freecad_brep("test_output/bagel_macro")
#my_bagel.run_simulation("") # no simulation for bagel
my_bagel.view_design_configuration()
#my_bagel.run_self_test("")
#my_bagel.cli("--output_file_basename test_output/bm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_bagel.get_fc_obj_3dconf('bagel_assembly_conf1'))



'''

### bell_bagel_assembly script example
bba_script_name="eg14_bell_bagel_assembly_example.py"
# copy from ../cnc25d/tests/bell_bagel_assembly_macro.py
bba_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/bell_bagel_assembly_macro.py
#
# bell_bagel_assembly_macro.py
# the macro to generate a bell_bagel_assembly, a component of a gimbal system
# created by charlyoleg on 2013/12/02
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design bell_bagel_assembly
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it.  Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

bba_constraint = {} # This python-dictionary contains all the constraint-parameters to build the bell_bagel_assembly assembly (component of a gimbal)
###### bell
### bell_face
## bulk
bba_constraint['axle_internal_diameter']          = 20.0
bba_constraint['axle_external_diameter']          = 0.0
bba_constraint['leg_length']                      = 40.0
bba_constraint['bell_face_height']                = 80.0
bba_constraint['bell_face_width']                 = 80.0
### bell_base_disc
bba_constraint['base_diameter']                   = 160.0
## wall_thickness
bba_constraint['face_thickness']                  = 6.0
bba_constraint['side_thickness']                  = 4.0
bba_constraint['base_thickness']                  = 8.0
## axle_hole
bba_constraint['axle_hole_nb']                    = 6
bba_constraint['axle_hole_diameter']              = 4.0
bba_constraint['axle_hole_position_diameter']     = 0.0
bba_constraint['axle_hole_angle']                 = 0.0
## leg
bba_constraint['leg_spare_width']                 = 10.0
bba_constraint['leg_smoothing_radius']            = 30.0
## motor_hole
bba_constraint['motor_hole_diameter']             = 4.0
bba_constraint['motor_hole_x_distance']           = 40.0
bba_constraint['motor_hole_z_distance']           = 50.0
bba_constraint['motor_hole_z_position']           = 40.0
## internal_buttress
bba_constraint['int_buttress_x_length']           = 10.0
bba_constraint['int_buttress_z_width']            = 5.0
bba_constraint['int_buttress_z_distance']         = 50.0
bba_constraint['int_buttress_x_position']         = 10.0
bba_constraint['int_buttress_z_position']         = 10.0
bba_constraint['int_buttress_int_corner_length']  = 5.0
bba_constraint['int_buttress_ext_corner_length']  = 5.0
bba_constraint['int_buttress_bump_length']        = 10.0
bba_constraint['int_buttress_arc_height']         = -2.0
bba_constraint['int_buttress_smoothing_radius']   = 10.0
## external_buttress
bba_constraint['ext_buttress_z_length']           = 10.0
bba_constraint['ext_buttress_x_width']            = 5.0
bba_constraint['ext_buttress_x_distance']         = 20.0
bba_constraint['ext_buttress_z_position']         = 40.0
bba_constraint['ext_buttress_y_length']           = 10.0
bba_constraint['ext_buttress_y_position']         = 20.0
bba_constraint['ext_buttress_face_int_corner_length']   = 5.0
bba_constraint['ext_buttress_face_ext_corner_length']   = 5.0
bba_constraint['ext_buttress_face_bump_length']         = 10.0
bba_constraint['ext_buttress_base_int_corner_length']   = 5.0
bba_constraint['ext_buttress_base_ext_corner_length']   = 5.0
bba_constraint['ext_buttress_base_bump_length']         = 10.0
bba_constraint['ext_buttress_arc_height']               = -5.0
bba_constraint['ext_buttress_smoothing_radius']         = 10.0
### bell_side
## hollow
bba_constraint['hollow_z_height']                 = 10.0
bba_constraint['hollow_y_width']                  = 20.0
bba_constraint['hollow_spare_width']              = 10.0
## base_hole
bba_constraint['base_hole_nb']                    = 8
bba_constraint['base_hole_diameter']              = 4.0
bba_constraint['base_hole_position_diameter']     = 0.0
bba_constraint['base_hole_angle']                 = 0.0
### xyz-axles
## y_hole
bba_constraint['y_hole_diameter']                 = 4.0
bba_constraint['y_hole_z_top_position']           = 10.0
bba_constraint['y_hole_z_bottom_position']        = 10.0
bba_constraint['y_hole_x_position']               = 6.0
## x_hole
bba_constraint['x_hole_diameter']                 = 4.0
bba_constraint['x_hole_z_top_position']           = -6.0
bba_constraint['x_hole_z_bottom_position']        = -6.0
bba_constraint['x_hole_y_position']               = 6.0
## z_hole
bba_constraint['z_hole_diameter']                 = 4.0
bba_constraint['z_hole_external_diameter']        = 0.0
bba_constraint['z_hole_position_length']          = 15.0
### bell manufacturing
bba_constraint['bell_cnc_router_bit_radius']      = 1.0
bba_constraint['bell_extra_cut_thickness']        = 0.0
###### bagel
## bagel diameter
bba_constraint['bagel_axle_diameter']                   = 10.0
bba_constraint['bagel_axle_internal_diameter']          = 0.0
bba_constraint['bagel_axle_external_diameter']          = 0.0
## bagel thickness
bba_constraint['external_bagel_thickness']        = 2.0
bba_constraint['internal_bagel_thickness']        = 2.0
### bagel manufacturing
bba_constraint['bagel_extra_cut_thickness']       = 0.0

################################################################
# action
################################################################

my_bba = cnc25d_design.bba(bba_constraint)
my_bba.outline_display()
my_bba.write_figure_svg("test_output/bba_macro")
my_bba.write_figure_dxf("test_output/bba_macro")
my_bba.write_figure_brep("test_output/bba_macro")
my_bba.write_assembly_brep("test_output/bba_macro")
my_bba.write_freecad_brep("test_output/bba_macro")
#my_bba.run_simulation("") # no simulation for bell_bagel_assembly
my_bba.view_design_configuration()
#my_bba.run_self_test("")
#my_bba.cli("--output_file_basename test_output/alm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_bba.get_fc_obj_3dconf('bell_bagel_assembly_conf1'))




'''

### crest script example
crest_script_name="eg15_crest_example.py"
# copy from ../cnc25d/tests/crest_macro.py
crest_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/crest_macro.py
#
# crest_macro.py
# the macro to generate a crest, the optinal gear of the cross_cube
# created by charlyoleg on 2013/12/11
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design crest
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it.  Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

crest_constraint = {} # This python-dictionary contains all the constraint-parameters to build the crest part (gear for cross_cube)

##### parameter inheritance from cross_cube_sub
### face A1, A2, B1 and B2
# height
crest_constraint['axle_diameter']       = 10.0
crest_constraint['inter_axle_length']   = 15.0
crest_constraint['height_margin']       = 10.0
crest_constraint['top_thickness']       = 5.0
# width
crest_constraint['cube_width']          = 60.0
crest_constraint['face_B1_thickness']   = 8.0
crest_constraint['face_B2_thickness']   = 6.0
crest_constraint['face_A1_thickness']   = crest_constraint['face_B1_thickness'] # not directly used by crest but inherited by cross_cube
crest_constraint['face_A2_thickness']   = crest_constraint['face_B2_thickness'] # not directly used by crest but inherited by cross_cube
### threaded rod
# face
crest_constraint['face_rod_hole_diameter']    = 4.0
crest_constraint['face_rod_hole_h_position']  = 5.0
crest_constraint['face_rod_hole_v_distance']  = 5.0
crest_constraint['face_rod_hole_v_position']  = 5.0
### hollow
# face hollow
crest_constraint['face_hollow_leg_nb']            = 1 # possible values: 1 (filled), 4, 8
crest_constraint['face_hollow_border_width']      = 0.0
crest_constraint['face_hollow_axle_width']        = 0.0
crest_constraint['face_hollow_leg_width']         = 0.0
crest_constraint['face_hollow_smoothing_radius']  = 0.0
### manufacturing
crest_constraint['cross_cube_cnc_router_bit_radius']  = 1.0
crest_constraint['cross_cube_extra_cut_thickness']  = 0.0

##### parameter inheritance from gear_profile
### first gear
# general
crest_constraint['gear_addendum_dedendum_parity'] = 50.0
# tooth height
crest_constraint['gear_tooth_half_height'] = 0.0
crest_constraint['gear_addendum_height_pourcentage'] = 100.0
crest_constraint['gear_dedendum_height_pourcentage'] = 100.0
crest_constraint['gear_hollow_height_pourcentage'] = 25.0
crest_constraint['gear_router_bit_radius'] = 0.1
# positive involute
crest_constraint['gear_base_diameter'] = 0.0
crest_constraint['gear_force_angle'] = 0.0
crest_constraint['gear_tooth_resolution'] = 2
crest_constraint['gear_skin_thickness'] = 0.0
# negative involute (if zero, negative involute'] = positive involute)
crest_constraint['gear_base_diameter_n'] = 0.0
crest_constraint['gear_force_angle_n'] = 0.0
crest_constraint['gear_tooth_resolution_n'] = 0
crest_constraint['gear_skin_thickness_n'] = 0.0
### second gear
# general
crest_constraint['second_gear_type'] = 'e'
crest_constraint['second_gear_tooth_nb'] = 0
crest_constraint['second_gear_primitive_diameter'] = 0.0
crest_constraint['second_gear_addendum_dedendum_parity'] = 0.0
# tooth height
crest_constraint['second_gear_tooth_half_height'] = 0.0
crest_constraint['second_gear_addendum_height_pourcentage'] = 100.0
crest_constraint['second_gear_dedendum_height_pourcentage'] = 100.0
crest_constraint['second_gear_hollow_height_pourcentage'] = 25.0
crest_constraint['second_gear_router_bit_radius'] = 0.0
# positive involute
crest_constraint['second_gear_base_diameter'] = 0.0
crest_constraint['second_gear_tooth_resolution'] = 0
crest_constraint['second_gear_skin_thickness'] = 0.0
# negative involute (if zero, negative involute'] = positive involute)
crest_constraint['second_gear_base_diameter_n'] = 0.0
crest_constraint['second_gear_tooth_resolution_n'] = 0
crest_constraint['second_gear_skin_thickness_n'] = 0.0
### gearbar specific
crest_constraint['gearbar_slope'] = 0.0
crest_constraint['gearbar_slope_n'] = 0.0
### position
# second gear position
crest_constraint['second_gear_position_angle'] = 0.0
crest_constraint['second_gear_additional_axis_length'] = 0.0

##### crest specific
### outline
crest_constraint['gear_module']         = 3.0
crest_constraint['virtual_tooth_nb']    = 60
crest_constraint['portion_tooth_nb']    = 30
crest_constraint['free_mounting_width'] = 15.0
### crest_hollow
crest_constraint['crest_hollow_leg_nb']  = 4 # possible values: 1(filled), 2(end-legs only), 3, 4 ...
crest_constraint['end_leg_width']                     = 10.0
crest_constraint['middle_leg_width']                  = 0.0
crest_constraint['crest_hollow_external_diameter']    = 0.0
crest_constraint['crest_hollow_internal_diameter']    = 0.0
crest_constraint['floor_width']                       = 0.0
crest_constraint['crest_hollow_smoothing_radius']     = 0.0
### gear_holes
crest_constraint['fastening_hole_diameter']           = 5.0
crest_constraint['fastening_hole_position']           = 0.0
crest_constraint['centring_hole_diameter']            = 1.0
crest_constraint['centring_hole_distance']            = 8.0
crest_constraint['centring_hole_position']            = 0.0
## part thickness
crest_constraint['crest_thickness']                   = 5.0
### manufacturing
crest_constraint['crest_cnc_router_bit_radius']       = 0.5


################################################################
# action
################################################################

my_crest = cnc25d_design.crest(crest_constraint)
my_crest.outline_display()
my_crest.write_figure_svg("test_output/crest_macro")
my_crest.write_figure_dxf("test_output/crest_macro")
my_crest.write_figure_brep("test_output/crest_macro")
my_crest.write_assembly_brep("test_output/crest_macro")
my_crest.write_freecad_brep("test_output/crest_macro")
my_crest.run_simulation("")
my_crest.view_design_configuration()
#my_crest.run_self_test("")
#my_crest.cli("--output_file_basename test_output/alm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_crest.get_fc_obj_3dconf('crest_3dconf1'))




'''

### cross_cube script example
cross_cube_script_name="eg16_cross_cube_example.py"
# copy from ../cnc25d/tests/cross_cube_macro.py
cross_cube_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/cross_cube_macro.py
#
# cross_cube_macro.py
# the macro to generate a cross_cube, the axle-holder of a gimbal system
# created by charlyoleg on 2013/12/11
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design cross_cube
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it.  Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

cc_constraint = {} # This python-dictionary contains all the constraint-parameters to build the cross_cube piece (piece of a gimbal)

##### cross_cube bare
### face A1, A2, B1 and B2
# height
cc_constraint['axle_diameter']       = 10.0
cc_constraint['inter_axle_length']   = 15.0
cc_constraint['height_margin']       = 10.0
cc_constraint['top_thickness']       = 5.0
# width
cc_constraint['cube_width']          = 60.0
cc_constraint['face_A1_thickness']   = 9.0
cc_constraint['face_A2_thickness']   = 7.0
cc_constraint['face_B1_thickness']   = 8.0
cc_constraint['face_B2_thickness']   = 6.0
### threaded rod
# face
cc_constraint['face_rod_hole_diameter']    = 4.0
cc_constraint['face_rod_hole_h_position']  = 5.0
cc_constraint['face_rod_hole_v_distance']  = 5.0
cc_constraint['face_rod_hole_v_position']  = 5.0
# top
cc_constraint['top_rod_hole_diameter']     = 4.0
cc_constraint['top_rod_hole_h_position']   = 10.0
### hollow
# face hollow
cc_constraint['face_hollow_leg_nb']            = 1 # possible values: 1 (filled), 4, 8
cc_constraint['face_hollow_border_width']      = 0.0
cc_constraint['face_hollow_axle_width']        = 0.0
cc_constraint['face_hollow_leg_width']         = 0.0
cc_constraint['face_hollow_smoothing_radius']  = 0.0
# top hollow
cc_constraint['top_hollow_leg_nb']             = 0 # possible values: 0 (empty), 1 (filled), 4, 8
cc_constraint['top_hollow_border_width']       = 0.0
cc_constraint['top_hollow_leg_width']          = 0.0
cc_constraint['top_hollow_smoothing_radius']   = 0.0
### axle
cc_constraint['axle_length']                   = 0.0
cc_constraint['spacer_diameter']               = 0.0
cc_constraint['spacer_length']                 = 0.0
### manufacturing
cc_constraint['cross_cube_cnc_router_bit_radius']  = 1.0
cc_constraint['cross_cube_extra_cut_thickness']  = 0.0 #0.0 1.0 for freecad gui inspection

### select crest on face
cc_constraint['face_A1_crest'] = True
cc_constraint['face_A2_crest'] = False
cc_constraint['face_B1_crest'] = True
cc_constraint['face_B2_crest'] = False

####### crest option
##### parameter inheritance from gear_profile
### first gear
# general
cc_constraint['gear_addendum_dedendum_parity'] = 50.0
# tooth height
cc_constraint['gear_tooth_half_height'] = 0.0
cc_constraint['gear_addendum_height_pourcentage'] = 100.0
cc_constraint['gear_dedendum_height_pourcentage'] = 100.0
cc_constraint['gear_hollow_height_pourcentage'] = 25.0
cc_constraint['gear_router_bit_radius'] = 0.1
# positive involute
cc_constraint['gear_base_diameter'] = 0.0
cc_constraint['gear_force_angle'] = 0.0
cc_constraint['gear_tooth_resolution'] = 2
cc_constraint['gear_skin_thickness'] = 0.0
# negative involute (if zero, negative involute'] = positive involute)
cc_constraint['gear_base_diameter_n'] = 0.0
cc_constraint['gear_force_angle_n'] = 0.0
cc_constraint['gear_tooth_resolution_n'] = 0
cc_constraint['gear_skin_thickness_n'] = 0.0
### second gear
# general
cc_constraint['second_gear_type'] = 'e'
cc_constraint['second_gear_tooth_nb'] = 0
cc_constraint['second_gear_primitive_diameter'] = 0.0
cc_constraint['second_gear_addendum_dedendum_parity'] = 0.0
# tooth height
cc_constraint['second_gear_tooth_half_height'] = 0.0
cc_constraint['second_gear_addendum_height_pourcentage'] = 100.0
cc_constraint['second_gear_dedendum_height_pourcentage'] = 100.0
cc_constraint['second_gear_hollow_height_pourcentage'] = 25.0
cc_constraint['second_gear_router_bit_radius'] = 0.0
# positive involute
cc_constraint['second_gear_base_diameter'] = 0.0
cc_constraint['second_gear_tooth_resolution'] = 0
cc_constraint['second_gear_skin_thickness'] = 0.0
# negative involute (if zero, negative involute'] = positive involute)
cc_constraint['second_gear_base_diameter_n'] = 0.0
cc_constraint['second_gear_tooth_resolution_n'] = 0
cc_constraint['second_gear_skin_thickness_n'] = 0.0
### gearbar specific
cc_constraint['gearbar_slope'] = 0.0
cc_constraint['gearbar_slope_n'] = 0.0
### position
# second gear position
cc_constraint['second_gear_position_angle'] = 0.0
cc_constraint['second_gear_additional_axis_length'] = 0.0

##### crest specific
### outline
cc_constraint['gear_module']         = 3.0
cc_constraint['virtual_tooth_nb']    = 60
cc_constraint['portion_tooth_nb']    = 30
cc_constraint['free_mounting_width'] = 15.0
### crest_hollow
cc_constraint['crest_hollow_leg_nb']  = 4 # possible values: 1(filled), 2(end-legs only), 3, 4 ...
cc_constraint['end_leg_width']                     = 10.0
cc_constraint['middle_leg_width']                  = 0.0
cc_constraint['crest_hollow_external_diameter']    = 0.0
cc_constraint['crest_hollow_internal_diameter']    = 0.0
cc_constraint['floor_width']                       = 0.0
cc_constraint['crest_hollow_smoothing_radius']     = 0.0
### gear_holes
cc_constraint['fastening_hole_diameter']           = 5.0
cc_constraint['fastening_hole_position']           = 0.0
cc_constraint['centring_hole_diameter']            = 1.0
cc_constraint['centring_hole_distance']            = 8.0
cc_constraint['centring_hole_position']            = 0.0
## part thickness
cc_constraint['crest_thickness']                   = 5.0
### manufacturing
cc_constraint['crest_cnc_router_bit_radius']       = 0.5


################################################################
# action
################################################################

my_cc = cnc25d_design.cross_cube(cc_constraint)
my_cc.outline_display()
my_cc.write_figure_svg("test_output/cross_cube_macro")
my_cc.write_figure_dxf("test_output/cross_cube_macro")
my_cc.write_figure_brep("test_output/cross_cube_macro")
my_cc.write_assembly_brep("test_output/cross_cube_macro")
my_cc.write_freecad_brep("test_output/cross_cube_macro")
my_cc.run_simulation("") 
my_cc.view_design_configuration()
#my_cc.run_self_test("")
#my_cc.cli("--output_file_basename test_output/alm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_cc.get_fc_obj_3dconf('cross_cube_bare_assembly'))




'''

### gimbal script example
gimbal_script_name="eg17_gimbal_example.py"
# copy from ../cnc25d/tests/gimbal_macro.py
gimbal_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gimbal_macro.py
#
# gimbal_macro.py
# the macro to generate a gimbal, a mechanism with the roll-pitch angles as degrees of freedom
# created by charlyoleg on 2013/12/11
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design gimbal
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it.  Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
from cnc25d import cnc25d_design
#
import Part
#
import math

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

gimbal_constraint = {} # This python-dictionary contains all the constraint-parameters to build the gimbal

####### bell_bagel
###### bell
### bell_face
## bulk
gimbal_constraint['axle_internal_diameter']          = 20.0
gimbal_constraint['axle_external_diameter']          = 0.0
gimbal_constraint['leg_length']                      = 60.0
gimbal_constraint['bell_face_height']                = 80.0
gimbal_constraint['bell_face_width']                 = 80.0
### bell_base_disc
gimbal_constraint['base_diameter']                   = 160.0
## wall_thickness
gimbal_constraint['face_thickness']                  = 6.0
gimbal_constraint['side_thickness']                  = 4.0
gimbal_constraint['base_thickness']                  = 8.0
## axle_hole
gimbal_constraint['axle_hole_nb']                    = 6
gimbal_constraint['axle_hole_diameter']              = 4.0
gimbal_constraint['axle_hole_position_diameter']     = 0.0
gimbal_constraint['axle_hole_angle']                 = 0.0
## leg
gimbal_constraint['leg_spare_width']                 = 10.0
gimbal_constraint['leg_smoothing_radius']            = 30.0
## motor_hole
gimbal_constraint['motor_hole_diameter']             = 4.0
gimbal_constraint['motor_hole_x_distance']           = 40.0
gimbal_constraint['motor_hole_z_distance']           = 50.0
gimbal_constraint['motor_hole_z_position']           = 40.0
## internal_buttress
gimbal_constraint['int_buttress_x_length']           = 10.0
gimbal_constraint['int_buttress_z_width']            = 5.0
gimbal_constraint['int_buttress_z_distance']         = 50.0
gimbal_constraint['int_buttress_x_position']         = 10.0
gimbal_constraint['int_buttress_z_position']         = 10.0
gimbal_constraint['int_buttress_int_corner_length']  = 5.0
gimbal_constraint['int_buttress_ext_corner_length']  = 5.0
gimbal_constraint['int_buttress_bump_length']        = 10.0
gimbal_constraint['int_buttress_arc_height']         = -2.0
gimbal_constraint['int_buttress_smoothing_radius']   = 10.0
## external_buttress
gimbal_constraint['ext_buttress_z_length']           = 10.0
gimbal_constraint['ext_buttress_x_width']            = 5.0
gimbal_constraint['ext_buttress_x_distance']         = 20.0
gimbal_constraint['ext_buttress_z_position']         = 40.0
gimbal_constraint['ext_buttress_y_length']           = 10.0
gimbal_constraint['ext_buttress_y_position']         = 20.0
gimbal_constraint['ext_buttress_face_int_corner_length']   = 5.0
gimbal_constraint['ext_buttress_face_ext_corner_length']   = 5.0
gimbal_constraint['ext_buttress_face_bump_length']         = 10.0
gimbal_constraint['ext_buttress_base_int_corner_length']   = 5.0
gimbal_constraint['ext_buttress_base_ext_corner_length']   = 5.0
gimbal_constraint['ext_buttress_base_bump_length']         = 10.0
gimbal_constraint['ext_buttress_arc_height']               = -5.0
gimbal_constraint['ext_buttress_smoothing_radius']         = 10.0
### bell_side
## hollow
gimbal_constraint['hollow_z_height']                 = 10.0
gimbal_constraint['hollow_y_width']                  = 20.0
gimbal_constraint['hollow_spare_width']              = 10.0
## base_hole
gimbal_constraint['base_hole_nb']                    = 8
gimbal_constraint['base_hole_diameter']              = 4.0
gimbal_constraint['base_hole_position_diameter']     = 0.0
gimbal_constraint['base_hole_angle']                 = 0.0
### xyz-axles
## y_hole
gimbal_constraint['y_hole_diameter']                 = 4.0
gimbal_constraint['y_hole_z_top_position']           = 10.0 # int_buttress_z_width + y_hole_diameter/2 + delta or -1*(y_hole_diameter/2 + delta)
gimbal_constraint['y_hole_z_bottom_position']        = 10.0 # int_buttress_z_width + y_hole_diameter/2 + delta or -1*(y_hole_diameter/2 + delta)
gimbal_constraint['y_hole_x_position']               = 6.0
## x_hole
gimbal_constraint['x_hole_diameter']                 = 4.0
gimbal_constraint['x_hole_z_top_position']           = -6.0 # int_buttress_z_width + x_hole_diameter/2 + delta or -1*(x_hole_diameter/2 + delta)
gimbal_constraint['x_hole_z_bottom_position']        = -6.0 # int_buttress_z_width + x_hole_diameter/2 + delta or -1*(x_hole_diameter/2 + delta)
gimbal_constraint['x_hole_y_position']               = 6.0
## z_hole
gimbal_constraint['z_hole_diameter']                 = 4.0
gimbal_constraint['z_hole_external_diameter']        = 0.0
gimbal_constraint['z_hole_position_length']          = 15.0
### bell manufacturing
gimbal_constraint['bell_cnc_router_bit_radius']      = 1.0
gimbal_constraint['bell_extra_cut_thickness']        = 0.0 #0.0, 1.0
###### bagel
## bagel diameter
gimbal_constraint['bagel_axle_diameter']                   = 10.0 # a bit bigger than gimbal_constraint['axle_diameter']
gimbal_constraint['bagel_axle_internal_diameter']          = 0.0
gimbal_constraint['bagel_axle_external_diameter']          = 0.0
## bagel thickness
gimbal_constraint['external_bagel_thickness']        = 2.0
gimbal_constraint['internal_bagel_thickness']        = 2.0
### bagel manufacturing
gimbal_constraint['bagel_extra_cut_thickness']       = 0.0 #0.0, 1.0

####### cross_cube
##### cross_cube bare
### face A1, A2, B1 and B2
# height
gimbal_constraint['axle_diameter']       = 10.0
gimbal_constraint['inter_axle_length']   = 15.0
gimbal_constraint['height_margin']       = 10.0
gimbal_constraint['top_thickness']       = 5.0
# width
gimbal_constraint['cube_width']          = 60.0
gimbal_constraint['face_A1_thickness']   = 9.0
gimbal_constraint['face_A2_thickness']   = 7.0
gimbal_constraint['face_B1_thickness']   = 8.0
gimbal_constraint['face_B2_thickness']   = 6.0
### threaded rod
# face
gimbal_constraint['face_rod_hole_diameter']    = 4.0
gimbal_constraint['face_rod_hole_h_position']  = 5.0
gimbal_constraint['face_rod_hole_v_distance']  = 5.0 # must be bigger than face_rod_hole_diameter
gimbal_constraint['face_rod_hole_v_position']  = 5.0 # must be bigger than face_rod_hole_radius
# top
gimbal_constraint['top_rod_hole_diameter']     = 4.0
gimbal_constraint['top_rod_hole_h_position']   = 10.0
### hollow
# face hollow
gimbal_constraint['face_hollow_leg_nb']            = 1 # possible values: 1 (filled), 4, 8
gimbal_constraint['face_hollow_border_width']      = 0.0
gimbal_constraint['face_hollow_axle_width']        = 0.0
gimbal_constraint['face_hollow_leg_width']         = 0.0
gimbal_constraint['face_hollow_smoothing_radius']  = 0.0
# top hollow
gimbal_constraint['top_hollow_leg_nb']             = 0 # possible values: 0 (empty), 1 (filled), 4, 8
gimbal_constraint['top_hollow_border_width']       = 0.0
gimbal_constraint['top_hollow_leg_width']          = 0.0
gimbal_constraint['top_hollow_smoothing_radius']   = 0.0
### axle
gimbal_constraint['axle_length']                   = 0.0
gimbal_constraint['spacer_diameter']               = 0.0
gimbal_constraint['spacer_length']                 = 0.0
### manufacturing
gimbal_constraint['cross_cube_cnc_router_bit_radius']  = 1.0
gimbal_constraint['cross_cube_extra_cut_thickness']  = 0.0 #0.0, 1.0

### select crest on face: (True, False, False, True) is the combination for the gimbal angle convention
gimbal_constraint['face_A1_crest'] = True
gimbal_constraint['face_A2_crest'] = False
gimbal_constraint['face_B1_crest'] = False
gimbal_constraint['face_B2_crest'] = True

####### crest option
##### parameter inheritance from gear_profile
### first gear
# general
gimbal_constraint['gear_addendum_dedendum_parity'] = 50.0
# tooth height
gimbal_constraint['gear_tooth_half_height'] = 0.0
gimbal_constraint['gear_addendum_height_pourcentage'] = 100.0
gimbal_constraint['gear_dedendum_height_pourcentage'] = 100.0
gimbal_constraint['gear_hollow_height_pourcentage'] = 25.0
gimbal_constraint['gear_router_bit_radius'] = 0.1
# positive involute
gimbal_constraint['gear_base_diameter'] = 0.0
gimbal_constraint['gear_force_angle'] = 0.0
gimbal_constraint['gear_tooth_resolution'] = 2
gimbal_constraint['gear_skin_thickness'] = 0.0
# negative involute (if zero, negative involute'] = positive involute)
gimbal_constraint['gear_base_diameter_n'] = 0.0
gimbal_constraint['gear_force_angle_n'] = 0.0
gimbal_constraint['gear_tooth_resolution_n'] = 0
gimbal_constraint['gear_skin_thickness_n'] = 0.0
### second gear
# general
gimbal_constraint['second_gear_type'] = 'e'
gimbal_constraint['second_gear_tooth_nb'] = 0
gimbal_constraint['second_gear_primitive_diameter'] = 0.0
gimbal_constraint['second_gear_addendum_dedendum_parity'] = 0.0
# tooth height
gimbal_constraint['second_gear_tooth_half_height'] = 0.0
gimbal_constraint['second_gear_addendum_height_pourcentage'] = 100.0
gimbal_constraint['second_gear_dedendum_height_pourcentage'] = 100.0
gimbal_constraint['second_gear_hollow_height_pourcentage'] = 25.0
gimbal_constraint['second_gear_router_bit_radius'] = 0.0
# positive involute
gimbal_constraint['second_gear_base_diameter'] = 0.0
gimbal_constraint['second_gear_tooth_resolution'] = 0
gimbal_constraint['second_gear_skin_thickness'] = 0.0
# negative involute (if zero, negative involute'] = positive involute)
gimbal_constraint['second_gear_base_diameter_n'] = 0.0
gimbal_constraint['second_gear_tooth_resolution_n'] = 0
gimbal_constraint['second_gear_skin_thickness_n'] = 0.0
### gearbar specific
gimbal_constraint['gearbar_slope'] = 0.0
gimbal_constraint['gearbar_slope_n'] = 0.0
### position
# second gear position
gimbal_constraint['second_gear_position_angle'] = 0.0
gimbal_constraint['second_gear_additional_axis_length'] = 0.0

##### crest specific
### outline
gimbal_constraint['gear_module']         = 3.0
gimbal_constraint['virtual_tooth_nb']    = 40
gimbal_constraint['portion_tooth_nb']    = 20
gimbal_constraint['free_mounting_width'] = 15.0 # minimal recommended value: max(face_thickness) + cross_cube_cnc_router_bit_radius
### crest_hollow
gimbal_constraint['crest_hollow_leg_nb']  = 4 # possible values: 1(filled), 2(end-legs only), 3, 4 ...
gimbal_constraint['end_leg_width']                     = 10.0
gimbal_constraint['middle_leg_width']                  = 0.0
gimbal_constraint['crest_hollow_external_diameter']    = 0.0
gimbal_constraint['crest_hollow_internal_diameter']    = 0.0
gimbal_constraint['floor_width']                       = 0.0
gimbal_constraint['crest_hollow_smoothing_radius']     = 0.0
### gear_holes
gimbal_constraint['fastening_hole_diameter']           = 5.0
gimbal_constraint['fastening_hole_position']           = 0.0
gimbal_constraint['centring_hole_diameter']            = 1.0
gimbal_constraint['centring_hole_distance']            = 8.0
gimbal_constraint['centring_hole_position']            = 0.0

##### gimbal angles
### roll-pitch angles
gimbal_constraint['bottom_angle']    = 0.0
gimbal_constraint['top_angle']       = 0.0
### pan_tilt angles # can be set only if roll-pitch angles are left to 0.0
gimbal_constraint['pan_angle']       = -30*math.pi/180 #0.0
gimbal_constraint['tilt_angle']      = 45*math.pi/180 #0.0


################################################################
# action
################################################################

my_gimbal = cnc25d_design.gimbal(gimbal_constraint)
my_gimbal.outline_display()
my_gimbal.write_figure_svg("test_output/gimbal_macro")
my_gimbal.write_figure_dxf("test_output/gimbal_macro")
my_gimbal.write_figure_brep("test_output/gimbal_macro")
my_gimbal.write_assembly_brep("test_output/gimbal_macro")
my_gimbal.write_freecad_brep("test_output/gimbal_macro")
my_gimbal.run_simulation("")
my_gimbal.view_design_configuration()
#my_gimbal.run_self_test("")
#my_gimbal.cli("--output_file_basename test_output/gm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_gimbal.get_fc_obj_function('gimbal')) # Your attention please: here we use get_fc_obj_function() instead of get_fc_obj_3dconf()




'''

### low_torque_transmission script example
ltt_script_name="eg18_low_torque_transmission_example.py"
# copy from ../cnc25d/tests/low_torque_transmission_macro.py
ltt_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/low_torque_transmission_macro.py
#
# low_torque_transmission_macro.py
# the macro to generate a low_torque_transmission_macro epicyclic gearing.
# created by charlyoleg on 2014/01/30
#
# (C) Copyright 2014 charlyoleg
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design low_torque_transmission
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# low_torque_transmission constraint values
################################################################

ltt_c = {} # dictionary containing the low_torque_transmission constraint

### structure
ltt_c['sun_gear_tooth_nb']	= 19
ltt_c['planet_gear_tooth_nb']	= 31
ltt_c['planet_nb']	= 0
ltt_c['step_nb']	= 2

### gear
ltt_c['gear_module']	= 1.0
ltt_c['gear_skin_thickness']	= 0.0
ltt_c['gear_tooth_resolution']	= 2
ltt_c['gear_addendum_dedendum_parity_slack']	= 0.0
ltt_c['gearring_dedendum_to_hollow_pourcentage']	= 0.0
ltt_c['gear_addendum_height_pourcentage']	= 100.0
ltt_c['gear_router_bit_radius']	= 0.1

### sun-gear
ltt_c['sun_axle_diameter']	= 5.0
ltt_c['sun_spacer_length']	= 1.0
ltt_c['sun_spacer_width']	= 0.5

### planet-gear
ltt_c['planet_axle_diameter']	= 5.0
ltt_c['planet_spacer_length']	= 1.0
ltt_c['planet_spacer_width']	= 1.0

### planet-carrier
# planet-carrier axle
ltt_c['planet_carrier_axle_diameter']	= 5.0
ltt_c['planet_carrier_spacer_length']	= 1.0
ltt_c['rear_planet_carrier_spacer_width']	= 1.0
ltt_c['planet_carrier_axle_holder_diameter']	= 10.0

# planet-carrier rear, middle, front
ltt_c['planet_carrier_external_diameter']	= 0.0

# planet-carrier rear
ltt_c['planet_carrier_internal_diameter']	= 0.0
ltt_c['planet_carrier_rear_smooth_radius']	= 0.0

# planet-carrier middle
ltt_c['planet_carrier_middle_clearance_diameter']	= 0.0
ltt_c['planet_carrier_middle_smooth_radius']	= 0.0

# planet-carrier fitting
ltt_c['planet_carrier_fitting_square_l1']	= 5.0
ltt_c['planet_carrier_fitting_square_l2']	= 5.0
ltt_c['planet_carrier_fitting_square_extra_cut']	= 0.0
ltt_c['planet_carrier_fitting_hole_diameter']	= 1.3
ltt_c['planet_carrier_fitting_hole_position']	= 4.0
ltt_c['planet_carrier_fitting_double_hole_distance']	= 4.0

## planet_carrier_angle
ltt_c['planet_carrier_angle']	= 0.0

### annulus: inherit dictionary entries from gearring
### holder
ltt_c['holder_diameter']            = 0.0
ltt_c['holder_crenel_number']       = 6
ltt_c['holder_position_angle']      = 0.0
### holder-hole
ltt_c['holder_hole_position_radius']   = 0.0
ltt_c['holder_hole_diameter']          = 5.0
ltt_c['holder_hole_mark_nb']           = 0
ltt_c['holder_double_hole_diameter']   = 0.0
ltt_c['holder_double_hole_length']     = 0.0
ltt_c['holder_double_hole_position']   = 0.0
ltt_c['holder_double_hole_mark_nb']    = 0
### holder-crenel
ltt_c['holder_crenel_position']        = 5.0
ltt_c['holder_crenel_height']          = 5.0
ltt_c['holder_crenel_width']           = 5.0
ltt_c['holder_crenel_skin_width']      = 3.0
ltt_c['holder_crenel_router_bit_radius']   = 1.0
ltt_c['holder_smoothing_radius']       = 0.0
### holder-hole-B (experimental)
ltt_c['holder_hole_B_diameter']          = 10.0
ltt_c['holder_crenel_B_position']        = 10.0
ltt_c['holder_hole_B_crenel_list']       = []


### first step z-dimension
ltt_c['planet_width']	= 5.0
ltt_c['rear_planet_carrier_width']	= 2.0
ltt_c['front_planet_carrier_width']	= 2.0
ltt_c['planet_slack']	= 0.2
ltt_c['step_slack']	= 1.0
ltt_c['input_slack']	= 2.0

### output step z-dimension
ltt_c['output_planet_width']	= 10.0
ltt_c['output_rear_planet_carrier_width']	= 3.0
ltt_c['output_front_planet_carrier_width']	= 3.0

### output_shaft
ltt_c['hexagon_length']	= 20.0
ltt_c['hexagon_smooth_radius']	= 1.0
ltt_c['hexagon_hole_diameter']	= 10.0
ltt_c['hexagon_width']	= 20.0

### output_holder
ltt_c['output_cover_radius_slack']	= 1.0
ltt_c['output_holder_thickness']	= 4.0
ltt_c['output_cover_width']	= 2.0
ltt_c['output_holder_width']	= 20.0

### output_axle_holder
ltt_c['output_axle_diameter']	= 5.0
ltt_c['axle_holder_A']	= 4.0
ltt_c['axle_holder_B']	= 4.0
ltt_c['axle_holder_C']	= 4.0
ltt_c['axle_holder_D']	= 10.0
ltt_c['axle_holder_width']	= 4.0

### input gearwheel
ltt_c['input_axle_diameter']	= 2.0
ltt_c['input_sun_width']	= 10.0

### motor_holder
ltt_c['motor_holder_width']	= 3.0
ltt_c['motor_x_width']	= 28.0
ltt_c['motor_y_width']	= 0.0
ltt_c['motor_holder_A']	= 5.0
ltt_c['motor_holder_B']	= 5.0
ltt_c['motor_holder_C']	= 5.0
ltt_c['motor_holder_D']	= 10.0
ltt_c['motor_holder_E']	= 2.0
ltt_c['motor_holder_leg_width']	= 4.0

### cnc router_bit constraint
ltt_c['cnc_router_bit_radius']	= 0.1

################################################################
# action
################################################################

my_ltt = cnc25d_design.ltt(ltt_c)
my_ltt.outline_display()
my_ltt.write_figure_svg("test_output/ltt_macro")
my_ltt.write_figure_dxf("test_output/ltt_macro")
my_ltt.write_figure_brep("test_output/ltt_macro")
my_ltt.write_assembly_brep("test_output/ltt_macro")
my_ltt.write_freecad_brep("test_output/ltt_macro")
my_ltt.run_simulation("eg_sim_planet_sun")
my_ltt.run_simulation("eg_sim_annulus_planet")
my_ltt.view_design_configuration()
#my_ltt.run_self_test("")
#my_ltt.cli("--output_file_basename test_output/lttm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  #Part.show(my_ltt.get_fc_obj_3dconf('planet_gear'))
  #Part.show(my_ltt.get_fc_obj_3dconf('output_planet_gear'))
  #Part.show(my_ltt.get_fc_obj_3dconf('rear_planet_carrier'))
  #Part.show(my_ltt.get_fc_obj_3dconf('front_planet_carrier'))
  Part.show(my_ltt.get_fc_obj_3dconf('output_rear_planet_carrier'))
  #Part.show(my_ltt.get_fc_obj_3dconf('output_front_planet_carrier'))
  #Part.show(my_ltt.get_fc_obj_3dconf('input_sun_gear'))
  #Part.show(my_ltt.get_fc_obj_3dconf('motor_holder'))
  #Part.show(my_ltt.get_fc_obj_3dconf('gearring_holder'))
  #Part.show(my_ltt.get_fc_obj_3dconf('output_holder'))
  #Part.show(my_ltt.get_fc_obj_3dconf('output_axle_holder'))



'''


### Generating the script examples

ceg_example_list={
  bwf_script_name : bwf_script_content,
  cgf_script_name : cgf_script_content,
  sca_script_name : sca_script_content,
  gp_script_name : gp_script_content,
  gw_script_name : gw_script_content,
  gr_script_name : gr_script_content,
  gb_script_name : gb_script_content,
  sgw_script_name : sgw_script_content,
  eg_script_name : eg_script_content,
  al_script_name : al_script_content,
  ml_script_name : ml_script_content,
  bell_script_name : bell_script_content,
  bagel_script_name : bagel_script_content,
  bba_script_name : bba_script_content,
  crest_script_name : crest_script_content,
  cross_cube_script_name : cross_cube_script_content,
  gimbal_script_name : gimbal_script_content,
  ltt_script_name : ltt_script_content}

ceg_example_list_sorted_keys = sorted(ceg_example_list.keys())
print("\nThis executable helps you to generate the following cnc25d script examples in the current directory:")
for l_example in ceg_example_list_sorted_keys:
  print("  +  {:s}".format(l_example))
user_choice=raw_input("Do you want to generate all these upper files in the current directory? [yes/No] ")
if((user_choice=='yes')or(user_choice=='y')):
  for l_example in ceg_example_list_sorted_keys:
    fh_output = open(l_example, 'w')
    fh_output.write(ceg_example_list[l_example])
    fh_output.close()
  print("All cnc25d script examples have been created in the current directory :)")
else:
  print("Choose which cnc25d script example you want to generate in the current directory:")
  for l_example in ceg_example_list_sorted_keys:
    print("cnc25d script example : {:s}".format(l_example))
    user_choice=raw_input("Do you want to generate the file {:s} in the current directory? [yes/No] ".format(l_example))
    if((user_choice=='yes')or(user_choice=='y')):
      fh_output = open(l_example, 'w')
      fh_output.write(ceg_example_list[l_example])
      fh_output.close()
      print(ceg_instructions.format(l_example, l_example, l_example))
    else:
      print("The script example {:s} has not been created.".format(l_example))


