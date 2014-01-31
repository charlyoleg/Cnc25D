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
my_sgw.write_info_txt("test_output/sgw_macro")
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


