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

##### from gear_profile
### first gear
# general
#gw_gear_type                      = gw_gear_type
gw_gear_tooth_nb                  = 18
gw_gear_module                    = 10.0
gw_gear_primitive_diameter        = 0
gw_gear_addendum_dedendum_parity  = 50.0
# tooth height
gw_gear_tooth_half_height           = 0 # 10.0
gw_gear_addendum_height_pourcentage = 100.0
gw_gear_dedendum_height_pourcentage = 100.0
gw_gear_hollow_height_pourcentage   = 25.0
gw_gear_router_bit_radius           = 3.0
# positive involute
gw_gear_base_diameter       = 0
gw_gear_force_angle         = 0
gw_gear_tooth_resolution    = 2
gw_gear_skin_thickness      = 0
# negative involute (if zero, negative involute = positive involute)
gw_gear_base_diameter_n     = 0
gw_gear_force_angle_n       = 0
gw_gear_tooth_resolution_n  = 0
gw_gear_skin_thickness_n    = 0
### second gear
# general
gw_second_gear_type                     = 'e'
gw_second_gear_tooth_nb                 = 25
gw_second_gear_primitive_diameter       = 0
gw_second_gear_addendum_dedendum_parity = 0 # 50.0
# tooth height
gw_second_gear_tooth_half_height            = 0
gw_second_gear_addendum_height_pourcentage  = 100.0
gw_second_gear_dedendum_height_pourcentage  = 100.0
gw_second_gear_hollow_height_pourcentage    = 25.0
gw_second_gear_router_bit_radius            = 0
# positive involute
gw_second_gear_base_diameter      = 0
gw_second_gear_tooth_resolution   = 0
gw_second_gear_skin_thickness     = 0
# negative involute (if zero, negative involute = positive involute)
gw_second_gear_base_diameter_n    = 0
gw_second_gear_tooth_resolution_n = 0
gw_second_gear_skin_thickness_n   = 0
### position
# first gear position
gw_center_position_x                    = 0.0
gw_center_position_y                    = 0.0
gw_gear_initial_angle                   = 0.0
# second gear position
gw_second_gear_position_angle           = 0.0
gw_second_gear_additional_axis_length   = 0.0
### portion
#gw_portion_tooth_nb     = gw_portion_tooth_nb
#gw_portion_first_end    = gw_portion_first_end
#gw_portion_last_end     = gw_portion_last_end
### output
gw_gear_profile_height  = 20.0
gw_simulation_enable    = False    # gw_simulation_enable
#gw_output_file_basename = gw_output_file_basename
##### from gearwheel
### axle
gw_axle_type                = 'rectangle'
gw_axle_x_width             = 20.0
gw_axle_y_width             = 15.0
gw_axle_router_bit_radius   = 3.0
### wheel-hollow = legs
gw_wheel_hollow_leg_number        = 7
gw_wheel_hollow_leg_width         = 10.0
gw_wheel_hollow_leg_angle         = 0.0
gw_wheel_hollow_internal_diameter = 40.0
gw_wheel_hollow_external_diameter = 125.0
gw_wheel_hollow_router_bit_radius = 5.0
### cnc router_bit constraint
gw_cnc_router_bit_radius          = 1.0
### design output : view the gearwheel with tkinter or write files
gw_tkinter_view = True
gw_output_file_basename = "" # set a not-empty string if you want to generate the output files
#gw_output_file_basename = "test_output/gearwheel_macro.svg"  # to generate the SVG file with mozman svgwrite
#gw_output_file_basename = "test_output/gearwheel_macro.dxf"  # to generate the DXF file with mozman svgwrite
#gw_output_file_basename = "test_output/gearwheel_macro"      # to generate the Brep and DXF file with FreeCAD



################################################################
# action
################################################################

my_gw = gearwheel.gearwheel(
            ##### from gear_profile
            ### first gear
            # general
            #ai_gear_type                      = gw_gear_type,
            ai_gear_tooth_nb                  = gw_gear_tooth_nb,
            ai_gear_module                    = gw_gear_module,
            ai_gear_primitive_diameter        = gw_gear_primitive_diameter,
            ai_gear_addendum_dedendum_parity  = gw_gear_addendum_dedendum_parity,
            # tooth height
            ai_gear_tooth_half_height           = gw_gear_tooth_half_height,
            ai_gear_addendum_height_pourcentage = gw_gear_addendum_height_pourcentage,
            ai_gear_dedendum_height_pourcentage = gw_gear_dedendum_height_pourcentage,
            ai_gear_hollow_height_pourcentage   = gw_gear_hollow_height_pourcentage,
            ai_gear_router_bit_radius           = gw_gear_router_bit_radius,
            # positive involute
            ai_gear_base_diameter       = gw_gear_base_diameter,
            ai_gear_force_angle         = gw_gear_force_angle,
            ai_gear_tooth_resolution    = gw_gear_tooth_resolution,
            ai_gear_skin_thickness      = gw_gear_skin_thickness,
            # negative involute (if zero, negative involute = positive involute)
            ai_gear_base_diameter_n     = gw_gear_base_diameter_n,
            ai_gear_force_angle_n       = gw_gear_force_angle_n,
            ai_gear_tooth_resolution_n  = gw_gear_tooth_resolution_n,
            ai_gear_skin_thickness_n    = gw_gear_skin_thickness_n,
            ### second gear
            # general
            ai_second_gear_type                     = gw_second_gear_type,
            ai_second_gear_tooth_nb                 = gw_second_gear_tooth_nb,
            ai_second_gear_primitive_diameter       = gw_second_gear_primitive_diameter,
            ai_second_gear_addendum_dedendum_parity = gw_second_gear_addendum_dedendum_parity,
            # tooth height
            ai_second_gear_tooth_half_height            = gw_second_gear_tooth_half_height,
            ai_second_gear_addendum_height_pourcentage  = gw_second_gear_addendum_height_pourcentage,
            ai_second_gear_dedendum_height_pourcentage  = gw_second_gear_dedendum_height_pourcentage,
            ai_second_gear_hollow_height_pourcentage    = gw_second_gear_hollow_height_pourcentage,
            ai_second_gear_router_bit_radius            = gw_second_gear_router_bit_radius,
            # positive involute
            ai_second_gear_base_diameter      = gw_second_gear_base_diameter,
            ai_second_gear_tooth_resolution   = gw_second_gear_tooth_resolution,
            ai_second_gear_skin_thickness     = gw_second_gear_skin_thickness,
            # negative involute (if zero, negative involute = positive involute)
            ai_second_gear_base_diameter_n    = gw_second_gear_base_diameter_n,
            ai_second_gear_tooth_resolution_n = gw_second_gear_tooth_resolution_n,
            ai_second_gear_skin_thickness_n   = gw_second_gear_skin_thickness_n,
            ### position
            # first gear position
            ai_center_position_x                    = gw_center_position_x,
            ai_center_position_y                    = gw_center_position_y,
            ai_gear_initial_angle                   = gw_gear_initial_angle,
            # second gear position
            ai_second_gear_position_angle           = gw_second_gear_position_angle,
            ai_second_gear_additional_axis_length   = gw_second_gear_additional_axis_length,
            ### portion
            #ai_portion_tooth_nb     = gw_cut_portion[0],
            #ai_portion_first_end    = gw_cut_portion[1],
            #ai_portion_last_end     = gw_cut_portion[2],
            ### output
            ai_gear_profile_height  = gw_gear_profile_height,
            ai_simulation_enable    = gw_simulation_enable,    # gw_simulation_enable,
            #ai_output_file_basename = gw_output_file_basename,
            ##### from gearwheel
            ### axle
            ai_axle_type                = gw_axle_type,
            ai_axle_x_width             = gw_axle_x_width,
            ai_axle_y_width             = gw_axle_y_width,
            ai_axle_router_bit_radius   = gw_axle_router_bit_radius,
            ### wheel-hollow = legs
            ai_wheel_hollow_leg_number        = gw_wheel_hollow_leg_number,
            ai_wheel_hollow_leg_width         = gw_wheel_hollow_leg_width,
            ai_wheel_hollow_leg_angle         = gw_wheel_hollow_leg_angle,
            ai_wheel_hollow_internal_diameter = gw_wheel_hollow_internal_diameter,
            ai_wheel_hollow_external_diameter = gw_wheel_hollow_external_diameter,
            ai_wheel_hollow_router_bit_radius = gw_wheel_hollow_router_bit_radius,
            ### cnc router_bit constraint
            ai_cnc_router_bit_radius          = gw_cnc_router_bit_radius,
            ### design output : view the gearwheel with tkinter or write files
            ai_tkinter_view = gw_tkinter_view,
            ai_output_file_basename = gw_output_file_basename)

#Part.show(my_gw)

