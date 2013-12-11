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
gimbal_constraint['y_hole_z_position']               = 10.0
gimbal_constraint['y_hole_x_position']               = 6.0
## x_hole
gimbal_constraint['x_hole_diameter']                 = 4.0
gimbal_constraint['x_hole_z_position']               = -6.0
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
gimbal_constraint['bagel_axle_diameter']                   = 10.0
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
gimbal_constraint['face_rod_hole_h_distance']  = 5.0
gimbal_constraint['face_rod_hole_v_distance']  = 5.0
# top
gimbal_constraint['top_rod_hole_diameter']     = 4.0
gimbal_constraint['top_rod_hole_h_distance']   = 10.0
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
### output
gimbal_constraint['simulation_enable'] = False

##### crest specific
### outline
gimbal_constraint['gear_module']         = 3.0
gimbal_constraint['virtual_tooth_nb']    = 40
gimbal_constraint['portion_tooth_nb']    = 20
gimbal_constraint['free_mounting_width'] = 15.0
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
## part thickness
gimbal_constraint['crest_thickness']                   = 5.0
### manufacturing
gimbal_constraint['crest_cnc_router_bit_radius']       = 0.5

##### gimbal angles
### roll-pitch angles
gimbal_constraint['bottom_angle']    = 0.0
gimbal_constraint['top_angle']       = 0.0
### pan_tilt angles # can be set only if roll-pitch angles are left to 0.0
gimbal_constraint['pan_angle']       = -30*math.pi/180 #0.0
gimbal_constraint['tilt_angle']      = 45*math.pi/180 #0.0

### output
gimbal_constraint['tkinter_view']           = True
gimbal_constraint['output_file_basename'] = "" # set a not-empty string if you want to generate the output files
#gimbal_constraint['output_file_basename'] = "test_output/gimbal_macro.svg"  # to generate the SVG file with mozman svgwrite
#gimbal_constraint['output_file_basename'] = "test_output/gimbal_macro.dxf"  # to generate the DXF file with mozman svgwrite
#gimbal_constraint['output_file_basename'] = "test_output/gimbal_macro"      # to generate the Brep and DXF file with FreeCAD
gimbal_constraint['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'

################################################################
# action
################################################################

my_gimbal = cnc25d_design.gimbal(gimbal_constraint)

try: # display if a freecad object
  Part.show(my_gimbal)
except:
  pass


