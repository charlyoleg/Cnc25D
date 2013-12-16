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
### output
crest_constraint['simulation_enable'] = False

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

##### output
crest_constraint['tkinter_view']           = True
crest_constraint['output_file_basename'] = "" # set a not-empty string if you want to generate the output files
#crest_constraint['output_file_basename'] = "test_output/crest_macro.svg"  # to generate the SVG file with mozman svgwrite
#crest_constraint['output_file_basename'] = "test_output/crest_macro.dxf"  # to generate the DXF file with mozman svgwrite
#crest_constraint['output_file_basename'] = "test_output/crest_macro"      # to generate the Brep and DXF file with FreeCAD
crest_constraint['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'

################################################################
# action
################################################################

my_crest = cnc25d_design.crest(crest_constraint)

try: # display if a freecad object
  Part.show(my_crest)
except:
  pass


