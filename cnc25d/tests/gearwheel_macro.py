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
gw_constraint['simulation_enable']    = False
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
### design output : view the gearwheel with tkinter or write files
gw_constraint['tkinter_view'] = True
gw_constraint['output_file_basename'] = "" # set a not-empty string if you want to generate the output files
#gw_constraint['output_file_basename'] = "test_output/gearwheel_macro.svg"  # to generate the SVG file with mozman svgwrite
#gw_constraint['output_file_basename'] = "test_output/gearwheel_macro.dxf"  # to generate the DXF file with mozman svgwrite
#gw_constraint['output_file_basename'] = "test_output/gearwheel_macro"      # to generate the Brep and DXF file with FreeCAD
gw_constraint['return_type'] = 'freecad_object' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'



################################################################
# action
################################################################

my_gw = cnc25d_design.gearwheel(gw_constraint)

try: # works if gw_constraint['return_type'] = 'freecad_object'
  Part.show(my_gw)
except:
  pass


