# gear_profile_macro.py
# the macro to generate a gear_profile.
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design gear_profile
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
from cnc25d import gear_profile
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

### first gear
# general
gp_gear_type                      = 'e'
gp_gear_tooth_nb                  = 18
gp_gear_module                    = 10.0
gp_gear_primitive_diameter        = 0
gp_gear_addendum_dedendum_parity  = 50.0
# tooth height
gp_gear_tooth_half_height           = 0 # 10.0
gp_gear_addendum_height_pourcentage = 100.0
gp_gear_dedendum_height_pourcentage = 100.0
gp_gear_hollow_height_pourcentage   = 25.0
gp_gear_router_bit_radius           = 3.0
# positive involute
gp_gear_base_diameter       = 0
gp_gear_force_angle         = 0
gp_gear_tooth_resolution    = 2
gp_gear_skin_thickness      = 0
# negative involute (if zero, negative involute = positive involute)
gp_gear_base_diameter_n     = 0
gp_gear_force_angle_n       = 0
gp_gear_tooth_resolution_n  = 0
gp_gear_skin_thickness_n    = 0
### second gear
# general
gp_second_gear_type                     = 'e'
gp_second_gear_tooth_nb                 = 0 #25
gp_second_gear_primitive_diameter       = 0
gp_second_gear_addendum_dedendum_parity = 0 # 50.0
# tooth height
gp_second_gear_tooth_half_height            = 0
gp_second_gear_addendum_height_pourcentage  = 100.0
gp_second_gear_dedendum_height_pourcentage  = 100.0
gp_second_gear_hollow_height_pourcentage    = 25.0
gp_second_gear_router_bit_radius            = 0
# positive involute
gp_second_gear_base_diameter      = 0
gp_second_gear_tooth_resolution   = 0
gp_second_gear_skin_thickness     = 0
# negative involute (if zero, negative involute = positive involute)
gp_second_gear_base_diameter_n    = 0
gp_second_gear_tooth_resolution_n = 0
gp_second_gear_skin_thickness_n   = 0
### position
# first gear position
gp_center_position_x                    = 0.0
gp_center_position_y                    = 0.0
gp_gear_initial_angle                   = 0.0
# second gear position
gp_second_gear_position_angle           = 0.0
gp_second_gear_additional_axis_length   = 0.0
### portion
gp_portion_tooth_nb     = 10
gp_portion_first_end    = 3
gp_portion_last_end     = 3
### output1
gp_gear_profile_height  = 20.0
gp_simulation_enable    = True
gp_output_file_basename = "" # set a not-empty string if you want to generate the output files
#gp_output_file_basename = "test_output/gearwheel_macro.svg"  # to generate the SVG file with mozman svgwrite
#gp_output_file_basename = "test_output/gearwheel_macro.dxf"  # to generate the DXF file with mozman svgwrite
#gp_output_file_basename = "test_output/gearwheel_macro"      # to generate the Brep and DXF file with FreeCAD



################################################################
# action
################################################################

my_gp = gear_profile.gear_profile(
            ### first gear
            # general
            ai_gear_type                      = gp_gear_type,
            ai_gear_tooth_nb                  = gp_gear_tooth_nb,
            ai_gear_module                    = gp_gear_module,
            ai_gear_primitive_diameter        = gp_gear_primitive_diameter,
            ai_gear_addendum_dedendum_parity  = gp_gear_addendum_dedendum_parity,
            # tooth height
            ai_gear_tooth_half_height           = gp_gear_tooth_half_height,
            ai_gear_addendum_height_pourcentage = gp_gear_addendum_height_pourcentage,
            ai_gear_dedendum_height_pourcentage = gp_gear_dedendum_height_pourcentage,
            ai_gear_hollow_height_pourcentage   = gp_gear_hollow_height_pourcentage,
            ai_gear_router_bit_radius           = gp_gear_router_bit_radius,
            # positive involute
            ai_gear_base_diameter       = gp_gear_base_diameter,
            ai_gear_force_angle         = gp_gear_force_angle,
            ai_gear_tooth_resolution    = gp_gear_tooth_resolution,
            ai_gear_skin_thickness      = gp_gear_skin_thickness,
            # negative involute (if zero, negative involute = positive involute)
            ai_gear_base_diameter_n     = gp_gear_base_diameter_n,
            ai_gear_force_angle_n       = gp_gear_force_angle_n,
            ai_gear_tooth_resolution_n  = gp_gear_tooth_resolution_n,
            ai_gear_skin_thickness_n    = gp_gear_skin_thickness_n,
            ### second gear
            # general
            ai_second_gear_type                     = gp_second_gear_type,
            ai_second_gear_tooth_nb                 = gp_second_gear_tooth_nb,
            ai_second_gear_primitive_diameter       = gp_second_gear_primitive_diameter,
            ai_second_gear_addendum_dedendum_parity = gp_second_gear_addendum_dedendum_parity,
            # tooth height
            ai_second_gear_tooth_half_height            = gp_second_gear_tooth_half_height,
            ai_second_gear_addendum_height_pourcentage  = gp_second_gear_addendum_height_pourcentage,
            ai_second_gear_dedendum_height_pourcentage  = gp_second_gear_dedendum_height_pourcentage,
            ai_second_gear_hollow_height_pourcentage    = gp_second_gear_hollow_height_pourcentage,
            ai_second_gear_router_bit_radius            = gp_second_gear_router_bit_radius,
            # positive involute
            ai_second_gear_base_diameter      = gp_second_gear_base_diameter,
            ai_second_gear_tooth_resolution   = gp_second_gear_tooth_resolution,
            ai_second_gear_skin_thickness     = gp_second_gear_skin_thickness,
            # negative involute (if zero, negative involute = positive involute)
            ai_second_gear_base_diameter_n    = gp_second_gear_base_diameter_n,
            ai_second_gear_tooth_resolution_n = gp_second_gear_tooth_resolution_n,
            ai_second_gear_skin_thickness_n   = gp_second_gear_skin_thickness_n,
            ### position
            # first gear position
            ai_center_position_x                    = gp_center_position_x,
            ai_center_position_y                    = gp_center_position_y,
            ai_gear_initial_angle                   = gp_gear_initial_angle,
            # second gear position
            ai_second_gear_position_angle           = gp_second_gear_position_angle,
            ai_second_gear_additional_axis_length   = gp_second_gear_additional_axis_length,
            ### portion
            ai_portion_tooth_nb     = gp_portion_tooth_nb,
            ai_portion_first_end    = gp_portion_first_end,
            ai_portion_last_end     = gp_portion_last_end,
            ### output
            ai_gear_profile_height  = gp_gear_profile_height,
            ai_simulation_enable    = gp_simulation_enable,    # gp_simulation_enable,
            ai_output_file_basename = gp_output_file_basename)

#print("dbg339: my_gp:", my_gp)
#Part.show(my_gp)


