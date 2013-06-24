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

