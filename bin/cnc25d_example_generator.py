#!/usr/bin/python
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

bwf_script_name="box_wood_frame_example.py"

# copy from ../cnc25d/tests/box_wood_frame_macro.py without the import stuff
bwf_script_content='''#!/usr/bin/python
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design box_wood_frame
You can also use this file as a FreeCAD macro from the GUI
Don't be afraid, look at the code. It's very simple to hack
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

from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
from cnc25d import box_wood_frame
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

bwf_box_width = 400.0
bwf_box_depth = 400.0
bwf_box_height = 400.0
bwf_fitting_height = 30.0
bwf_h_plank_width = 50.0
bwf_v_plank_width = 30.0
bwf_plank_height = 20.0
bwf_d_plank_width = 30.0
bwf_d_plank_height = 10.0
bwf_crenel_depth = 5.0
bwf_wall_diagonal_size = 50.0
bwf_tobo_diagonal_size = 100.0
bwf_diagonal_lining_top_height = 20.0
bwf_diagonal_lining_bottom_height = 20.0
bwf_module_width = 1
bwf_router_bit_radius = 2.0
bwf_cutting_extra = 2.0 # doesn't affect the cnc cutting plan
bwf_slab_thickness = 5.0
bwf_output_file_basename = "" # set a not-empty string if you want to generate the output files
#bwf_output_file_basename = "my_output_dir/" 
#bwf_output_file_basename = "my_output_dir/my_output_basename" 
#bwf_output_file_basename = "my_output_basename" 



################################################################
# action
################################################################

bwf_assembly = box_wood_frame.box_wood_frame(bwf_box_width, bwf_box_depth, bwf_box_height,
                                              bwf_fitting_height, bwf_h_plank_width, bwf_v_plank_width, bwf_plank_height,
                                              bwf_d_plank_width, bwf_d_plank_height, bwf_crenel_depth,
                                              bwf_wall_diagonal_size, bwf_tobo_diagonal_size,
                                              bwf_diagonal_lining_top_height, bwf_diagonal_lining_bottom_height,
                                              bwf_module_width, bwf_router_bit_radius, bwf_cutting_extra,
                                              bwf_slab_thickness, bwf_output_file_basename)
Part.show(bwf_assembly)


'''

### gearwheel script example

gw_script_name="gearwheel_example.py"

# copy from ../cnc25d/tests/gearwheel_macro.py without the import stuff
gw_script_content='''#!/usr/bin/python
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design gearwheel
You can also use this file as a FreeCAD macro from the GUI
Look at the code. It's very simple to hack
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

from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import gearwheel
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

# gear parameters
gw_gear_type = 'ee'
gw_gear_tooth_nb = 17
gw_gear_module = 3.0
gw_gear_primitive_diameter = 0.0
gw_gear_base_diameter = 16.0
gw_gear_tooth_half_height = 5.0
gw_gear_addendum_dedendum_parity = 50.0
gw_gear_addendum_height_pourcentage = 100.0
gw_gear_dedendum_height_pourcentage = 100.0
gw_gear_hollow_height_pourcentage = 25.0
gw_gear_router_bit_radius = 2.0
gw_gear_initial_angle = 0*math.pi
# gear contact parameters
gw_second_gear_position_angle = 0*math.pi
gw_second_gear_additional_axe_length = 0.0
gw_gear_force_angle = 20*math.pi/180
# second gear parameters
gw_second_gear_tooth_nb = 14
gw_second_gear_primitive_diameter = 0.0
gw_second_gear_base_diameter = 14.0
gw_second_gear_tooth_half_height = 5.0
gw_second_gear_addendum_dedendum_parity = 50.0
gw_second_gear_addendum_height_pourcentage = 100.0
gw_second_gear_dedendum_height_pourcentage = 100.0
gw_second_gear_hollow_height_pourcentage = 25.0
gw_second_gear_router_bit_radius = 2.0
# simulation
gw_simulation_enable = True
gw_simulation_zoom = 4.0
# axe parameters
gw_axe_type = "square"
gw_axe_size_1 = 30.0
gw_axe_size_2 = 5.0
gw_axe_router_bit_radius = 4.0
# portion parameter
gw_portion_tooth_nb = 0
# wheel hollow parameters
gw_wheel_hollow_internal_diameter = 30.0
gw_wheel_hollow_external_diameter = 60.0
gw_wheel_hollow_leg_number = 3
gw_wheel_hollow_leg_width = 5.0
gw_wheel_hollow_router_bit_radius = 4.0
# part split parameter
gw_part_split = 0
# center position parameters
gw_center_position_x = 0.0
gw_center_position_y = 0.0
# gearwheel linear extrusion
gw_gearwheel_height = 1.0
# cnc router_bit constraint
gw_cnc_router_bit_radius = 2.0
# manufacturing technology related
gw_gear_tooth_resolution = 5
gw_gear_skin_thickness = 0.0
# output
gw_output_file_basename = "" # set a not-empty string if you want to generate the output files
#gw_output_file_basename = "my_output_dir/" 
#gw_output_file_basename = "my_output_dir/my_output_basename" 
#gw_output_file_basename = "my_output_basename" 



################################################################
# action
################################################################

my_gw = gearwheel.gearwheel(
          gw_gear_type,
          gw_gear_tooth_nb,
          gw_gear_module,
          gw_gear_primitive_diameter,
          gw_gear_base_diameter,
          gw_gear_tooth_half_height,
          gw_gear_addendum_dedendum_parity,
          gw_gear_addendum_height_pourcentage,
          gw_gear_dedendum_height_pourcentage,
          gw_gear_hollow_height_pourcentage,
          gw_gear_router_bit_radius,
          gw_gear_initial_angle,
          gw_second_gear_position_angle,
          gw_second_gear_additional_axe_length,
          gw_gear_force_angle,
          gw_second_gear_tooth_nb,
          gw_second_gear_primitive_diameter,
          gw_second_gear_base_diameter,
          gw_second_gear_tooth_half_height,
          gw_second_gear_addendum_dedendum_parity,
          gw_second_gear_addendum_height_pourcentage,
          gw_second_gear_dedendum_height_pourcentage,
          gw_second_gear_hollow_height_pourcentage,
          gw_second_gear_router_bit_radius,
          gw_simulation_enable,
          gw_simulation_zoom,
          gw_axe_type,
          gw_axe_size_1,
          gw_axe_size_2,
          gw_axe_router_bit_radius,
          gw_portion_tooth_nb,
          gw_wheel_hollow_internal_diameter,
          gw_wheel_hollow_external_diameter,
          gw_wheel_hollow_leg_number,
          gw_wheel_hollow_leg_width,
          gw_wheel_hollow_router_bit_radius,
          gw_part_split,
          gw_center_position_x,
          gw_center_position_y,
          gw_gearwheel_height,
          gw_cnc_router_bit_radius,
          gw_gear_tooth_resolution,
          gw_gear_skin_thickness,
          gw_output_file_basename)

#Part.show(my_gw)


'''

### cnc25d_api_example script

cgf_script_name="cnc25d_api_example.py"

# copy from ../cnc25d/tests/cnc25d_api_macro.py without the import stuff
cgf_script_content='''#!/usr/bin/python
#
# copy/paste of cnc25d/tests/cnc25d_api_macro.py
#
#!/usr/bin/python
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
cnc25d_api_macro.py tests and demonstrates the Cnc25D API.
Use it as an example of usage of the Cnc25D API when you want to create your own design.
"""

# List of the functions of the Cnc25D API:
#   cnc25d_api.importing_freecad()
#   cnc25d_api.outline_shift_x(outline, x-offset, x-coefficient)
#   cnc25d_api.outline_shift_y(outline, y-offset, y-coefficient)
#   cnc25d_api.outline_shift_xy(outline, x-offset, x-coefficient, y-offset, y-coefficient)
#   cnc25d_api.outline_rotate(outline, center-x, center-y, rotation_angle)
#   cnc25d_api.outline_close(outline)
#   cnc25d_api.outline_reverse(outline)
#   cnc25d_api.cnc_cut_outline(outline, mark_string)
#   cnc25d_api.outline_arc_line(outline, backend)
#   cnc25d_api.outline_circle((center-x, center-y), radius, backend)
#   cnc25d_api.Two_Canvas(Tkinter.Tk()) # object constructor
#   cnc25d_api.place_plank(freecad_part_object, x-size, y-size, z-size, flip, orientation, x-position, y-position, z-position)
#   cnc25d_api.export_to_dxf(freecad_part_object, direction_vector, depth, filename)
#   cnc25d_api.export_xyz_to_dxf(freecad_part_object, x-size, y-size, z-size, x-depth-list, y-depth-list, z-depth-list, filename)


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
import os, errno # to create the output directory
import math # to get the pi number
import Tkinter # to display the outline in a small GUI
import svgwrite
from dxfwrite import DXFEngine


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
# Display the outline in a Tkinter GUI
################################################################

## display my_outline_for_cnc with Tkinter
print("Display the outlines with Tkinter")
tk_root = Tkinter.Tk()
my_canvas = cnc25d_api.Two_Canvas(tk_root)
# callback function for display_backend
def sub_canvas_graphics(ai_angle_position):
  r_canvas_graphics = []
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc, 'tkinter'), 'red', 1))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_x_shifted, 'tkinter'), 'red', 1))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_y_shifted, 'tkinter'), 'red', 1))
  turning_outline = cnc25d_api.outline_rotate(my_outline_for_cnc_xy_shifted, big_length*4, big_length*4, ai_angle_position)
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(turning_outline, 'tkinter'), 'red', 1))
  r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_rotated, 'tkinter'), 'green', 2))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_closed, 'tkinter'), 'blue', 1))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_outline_for_cnc_reverse, 'tkinter'), 'blue', 1))
  r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_circle((100,100), 40, 'tkinter'), 'orange', 1)) # create a circle
  r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(my_curve, 'tkinter'), 'green', 2))
  r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(my_curve_for_cnc, 'tkinter'), 'blue', 1))
  return(r_canvas_graphics)
# end of callback function
my_canvas.add_canvas_graphic_function(sub_canvas_graphics)
tk_root.mainloop()

#
l_output_dir = "test_output"
print("Create the output directory: {:s}".format(l_output_dir))
try:
  os.makedirs(l_output_dir)
except OSError as exc:
  if exc.errno == errno.EEXIST and os.path.isdir(l_output_dir):
    pass
  else:
    raise

################################################################
# Write the outline in a SVG file
################################################################

## write my_outline_for_cnc in a SVG file
print("Write the outlines in a SVG file with svgwrite")
output_svg_file_name =  "{:s}/outlines_with_svgwrite.svg".format(l_output_dir)
print("Generate the file {:s}".format(output_svg_file_name))
object_svg = svgwrite.Drawing(filename = output_svg_file_name)
svg_figures = [my_outline_for_cnc, my_outline_for_cnc_rotated]
for i_ol in svg_figures:
  svg_outline = cnc25d_api.outline_arc_line(i_ol, 'svgwrite')
  for one_line_or_arc in svg_outline:
    object_svg.add(one_line_or_arc)
one_svg_circle = cnc25d_api.outline_circle((100,100), 40, 'svgwrite') # create a circle
object_svg.add(one_svg_circle)
object_svg.save()

################################################################
# Write the outline in a DXF file
################################################################

## write my_outline_for_cnc in a DXF file
print("Write the outlines in a DXF file with dxfwrite")
output_dxf_file_name =  "{:s}/outlines_with_dxfwrite.dxf".format(l_output_dir)
print("Generate the file {:s}".format(output_dxf_file_name))
object_dxf = DXFEngine.drawing(output_dxf_file_name)
#object_dxf.add_layer("my_dxf_layer")
dxf_figures = [my_outline_for_cnc, my_outline_for_cnc_rotated]
for i_ol in dxf_figures:
  dxf_outline = cnc25d_api.outline_arc_line(i_ol, 'dxfwrite')
  for one_line_or_arc in dxf_outline:
    object_dxf.add(one_line_or_arc)
one_dxf_circle = cnc25d_api.outline_circle((100,100), 40, 'dxfwrite') # create a circle
object_dxf.add(one_dxf_circle)
object_dxf.save()

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
my_part_face2 = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(cnc25d_api.outline_shift_y(my_outline, 4*big_length,0.5), 'freecad_short_version').Edges))
my_part_solid2 = my_part_face2.extrude(Base.Vector(0,0,big_length)) # straight linear extrusion
# creation of a circle with the cnc25d workflow
my_part_face3 = Part.Face(Part.Wire(cnc25d_api.outline_circle((100,100),40, 'freecad').Edges))
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
my_part_solid.exportBrep("{:s}/my_assembly.brep".format(l_output_dir))
#print("Generate {:s}/my_assembly.step".format(l_output_dir))
#my_part_solid.exportStep("{:s}/my_assembly.step".format(l_output_dir))

# my_assembly sliced and projected in 2D DXF
print("Generate {:s}/my_assembly.dxf".format(l_output_dir))
xy_slice_list = [ 0.1+20*i for i in range(12) ]
xz_slice_list = [ 0.1+20*i for i in range(9) ]
yz_slice_list = [ 0.1+20*i for i in range(9) ]
cnc25d_api.export_xyz_to_dxf(my_assembly, 3*big_length, 3*big_length, 4*big_length, xy_slice_list, xz_slice_list, yz_slice_list, "{:s}/my_assembly.dxf".format(l_output_dir))

################################################################
# End of the script
################################################################

# bye message
print("cnc25d_api_macro.py says Bye!")


'''

### Generating the script examples

ceg_example_list={
  bwf_script_name : bwf_script_content,
  gw_script_name : gw_script_content,
  cgf_script_name : cgf_script_content}

print("\nThis executable helps you to generate the following cnc25d script examples in the current directory:")
for l_example in ceg_example_list.keys():
  print("  +  {:s}".format(l_example))
user_choice=raw_input("Do you want to generate all these upper files in the current directory? [yes/No] ")
if((user_choice=='yes')or(user_choice=='y')):
  for l_example in ceg_example_list.keys():
    fh_output = open(l_example, 'w')
    fh_output.write(ceg_example_list[l_example])
    fh_output.close()
  print("All cnc25d script examples have been created in the current directory :)")
else:
  print("Choose which cnc25d script example you want to generate in the current directory:")
  for l_example in ceg_example_list.keys():
    print("cnc25d script example : {:s}".format(l_example))
    user_choice=raw_input("Do you want to generate the file {:s} in the current directory? [yes/No] ".format(l_example))
    if((user_choice=='yes')or(user_choice=='y')):
      fh_output = open(l_example, 'w')
      fh_output.write(ceg_example_list[l_example])
      fh_output.close()
      print(ceg_instructions.format(l_example, l_example, l_example))
    else:
      print("The script example {:s} has not been created.".format(l_example))


