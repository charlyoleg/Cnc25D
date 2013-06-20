#!/usr/bin/python
#
# cnc25d_example_generator.py
# it generates examples of python scripts that use the cnc25d package
# created by charlyoleg on 2013/06/03
# license: CC BY SA 3.0

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
# license: CC BY SA 3.0

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

from cnc25d import importing_freecad
importing_freecad.importing_freecad()

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
bwf_reamer_radius = 2.0
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
                                              bwf_module_width, bwf_reamer_radius, bwf_cutting_extra,
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
# license: CC BY SA 3.0

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

from cnc25d import importing_freecad
importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

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
gw_gear_tooth_height = 5.0
gw_gear_addendum_dedendum_parity = 50.0
gw_gear_addendum_height_pourcentage = 100.0
gw_gear_dedendum_height_pourcentage = 100.0
gw_gear_hollow_height_pourcentage = 25.0
gw_gear_reamer_radius = 2.0
gw_gear_initial_angle = 0*math.pi
# gear contact parameters
gw_second_gear_position_angle = 0*math.pi
gw_second_gear_additional_axe_length = 0.0
gw_gear_force_angle = 20*math.pi/180
# second gear parameters
gw_second_gear_tooth_nb = 14
gw_second_gear_primitive_diameter = 0.0
gw_second_gear_base_diameter = 14.0
gw_second_gear_tooth_height = 5.0
gw_second_gear_addendum_dedendum_parity = 50.0
gw_second_gear_addendum_height_pourcentage = 100.0
gw_second_gear_dedendum_height_pourcentage = 100.0
gw_second_gear_hollow_height_pourcentage = 25.0
gw_second_gear_reamer_radius = 2.0
# simulation
gw_simulation_enable = True
gw_simulation_zoom = 4.0
# axe parameters
gw_axe_type = "square"
gw_axe_size_1 = 30.0
gw_axe_size_2 = 5.0
gw_axe_reamer_radius = 4.0
# portion parameter
gw_portion_tooth_nb = 0
# wheel hollow parameters
gw_wheel_hollow_internal_diameter = 30.0
gw_wheel_hollow_external_diameter = 60.0
gw_wheel_hollow_leg_number = 3
gw_wheel_hollow_leg_width = 5.0
gw_wheel_hollow_reamer_radius = 4.0
# part split parameter
gw_part_split = 0
# center position parameters
gw_center_position_x = 0.0
gw_center_position_y = 0.0
# cnc reamer constraint
gw_cnc_reamer_radius = 2.0
# tooth resolution
gw_gear_tooth_resolution = 5
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
          gw_gear_tooth_height,
          gw_gear_addendum_dedendum_parity,
          gw_gear_addendum_height_pourcentage,
          gw_gear_dedendum_height_pourcentage,
          gw_gear_hollow_height_pourcentage,
          gw_gear_reamer_radius,
          gw_gear_initial_angle,
          gw_second_gear_position_angle,
          gw_second_gear_additional_axe_length,
          gw_gear_force_angle,
          gw_second_gear_tooth_nb,
          gw_second_gear_module,
          gw_second_gear_primitive_diameter,
          gw_second_gear_base_diameter,
          gw_second_gear_tooth_height,
          gw_second_gear_addendum_dedendum_parity,
          gw_second_gear_addendum_height_pourcentage,
          gw_second_gear_dedendum_height_pourcentage,
          gw_second_gear_hollow_height_pourcentage,
          gw_second_gear_reamer_radius,
          gw_simulation_enable,
          gw_simulation_zoom,
          gw_axe_type,
          gw_axe_size_1,
          gw_axe_size_2,
          gw_axe_reamer_radius,
          gw_portion_tooth_nb,
          gw_wheel_hollow_internal_diameter,
          gw_wheel_hollow_external_diameter,
          gw_wheel_hollow_leg_number,
          gw_wheel_hollow_leg_width,
          gw_wheel_hollow_reamer_radius,
          gw_part_split,
          gw_center_position_x,
          gw_center_position_y,
          gw_cnc_reamer_radius,
          gw_gear_tooth_resolution,
          gw_output_file_basename)

Part.show(my_gw)


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
# license: CC BY SA 3.0
# 

"""
cnc25d_api_macro.py tests and demonstrates the Cnc25D API.
Use it as an example of usage of the Cnc25D API when you want to create your own design.
"""

# import the FreeCAD library
from cnc25d import importing_freecad
importing_freecad.importing_freecad()
import Part # this module is part of the FreeCAD library
from FreeCAD import Base

# import the Cnc25D API modules
from cnc25d import cnc_cut_outline, export_2d

# hello message
print("cnc25d_api_macro.py starts")

# define the CNC reamer radius
my_reamer_radius = 5.0 # in mm

# some design constant
big_length = 60
small_length = 20

# create a free polygon.
# A polygon is list of points. A point is a list of three elements: x coordinate, y coordiante, reamer radius.
# If the reamer radius is positive, the angle is smoothed for this radius.
# If the reamer radius is negative, the angle is enlarged for this radius.
# If the reamer radius is zero, the angle is unchanged
my_polygon = [
  [ 0*big_length+0*small_length,  0*big_length+0*small_length,    my_reamer_radius],
  [ 1*big_length+1*small_length,  0*big_length+0*small_length,    my_reamer_radius],
  [ 1*big_length+1*small_length,  0*big_length+2*small_length,    my_reamer_radius],
  [ 1*big_length+2*small_length,  0*big_length+2*small_length,    my_reamer_radius],
  [ 1*big_length+2*small_length,  0*big_length+0*small_length,    my_reamer_radius],
  [ 3*big_length+0*small_length,  0*big_length+0*small_length,    my_reamer_radius],
  [ 3*big_length+0*small_length,  1*big_length+0*small_length,    my_reamer_radius],
  [ 2*big_length+0*small_length,  1*big_length+0*small_length, -1*my_reamer_radius],
  [ 2*big_length+0*small_length,  2*big_length+0*small_length,    my_reamer_radius],
  [ 1*big_length+0*small_length,  2*big_length+0*small_length,    my_reamer_radius],
  [ 1*big_length+0*small_length,  1*big_length+0*small_length,    my_reamer_radius],
  [ 0*big_length+0*small_length,  1*big_length+0*small_length,    my_reamer_radius]]

# use the Cnc25D API function cnc_cut_outline to create a makable outline from the wished polygon
my_part_outline = cnc_cut_outline.cnc_cut_outline(my_polygon)
# extrude the outline to make a 3D part
my_part_edges = my_part_outline.Edges
my_part_wire = Part.Wire(my_part_edges)
my_part_face = Part.Face(my_part_wire)
# short version: my_part_face = Part.Face(Part.Wire(cnc_cut_outline.cnc_cut_outline(my_part_outline).Edges))
my_part_solid = my_part_face.extrude(Base.Vector(0,0,big_length)) # straight linear extrusion

# visualize the part with the FreeCAD GUI
#Part.show(my_part_solid)

# create three my_part and place them using the Cnc25D API function plank_place
my_part_a = cnc_cut_outline.place_plank(my_part_solid.copy(), 3*big_length, 2*big_length, 1*big_length, 'i', 'xz', 0, 0, 0)
my_part_b = cnc_cut_outline.place_plank(my_part_solid.copy(), 3*big_length, 2*big_length, 1*big_length, 'i', 'zx', 0, 0, big_length)
my_part_c = cnc_cut_outline.place_plank(my_part_solid.copy(), 3*big_length, 2*big_length, 1*big_length, 'z', 'yz', 2*big_length, 0, 0)
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
export_2d.export_to_dxf(my_part_solid, Base.Vector(0,0,1), 1.0, "my_part.dxf") # slice my_part in the XY plan at a height of 1.0
print("The file my_part.dxf has been generated")

# my_assembly in 3D STL
my_assembly.exportStl("my_assembly.stl")
print("The file my_assembly.stl has been generated")

# my_assembly sliced and projected in 2D DXF
xy_slice_list = [ 0.1+20*i for i in range(12) ]
xz_slice_list = [ 0.1+20*i for i in range(9) ]
yz_slice_list = [ 0.1+20*i for i in range(9) ]
export_2d.export_xyz_to_dxf(my_assembly, 3*big_length, 3*big_length, 4*big_length, xy_slice_list, xz_slice_list, yz_slice_list, "my_assembly.dxf")
print("The file my_assembly.dxf has been generated")

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


