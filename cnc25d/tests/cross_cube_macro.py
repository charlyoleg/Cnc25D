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
my_cc.write_info_txt("test_output/cross_cube_macro")
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



