# bell_bagel_assembly_macro.py
# the macro to generate a bell_bagel_assembly, a component of a gimbal system
# created by charlyoleg on 2013/12/02
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
this piece of code is an example of how to use the parametric design bell_bagel_assembly
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

bba_constraint = {} # This python-dictionary contains all the constraint-parameters to build the bell_bagel_assembly assembly (component of a gimbal)
###### bell
### bell_face
## bulk
bba_constraint['axle_internal_diameter']          = 20.0
bba_constraint['axle_external_diameter']          = 0.0
bba_constraint['leg_length']                      = 40.0
bba_constraint['bell_face_height']                = 80.0
bba_constraint['bell_face_width']                 = 80.0
### bell_base_disc
bba_constraint['base_diameter']                   = 160.0
## wall_thickness
bba_constraint['face_thickness']                  = 6.0
bba_constraint['side_thickness']                  = 4.0
bba_constraint['base_thickness']                  = 8.0
## axle_hole
bba_constraint['axle_hole_nb']                    = 6
bba_constraint['axle_hole_diameter']              = 4.0
bba_constraint['axle_hole_position_diameter']     = 0.0
bba_constraint['axle_hole_angle']                 = 0.0
## leg
bba_constraint['leg_spare_width']                 = 10.0
bba_constraint['leg_smoothing_radius']            = 30.0
## motor_hole
bba_constraint['motor_hole_diameter']             = 4.0
bba_constraint['motor_hole_x_distance']           = 40.0
bba_constraint['motor_hole_z_distance']           = 50.0
bba_constraint['motor_hole_z_position']           = 40.0
## internal_buttress
bba_constraint['int_buttress_x_length']           = 10.0
bba_constraint['int_buttress_z_width']            = 5.0
bba_constraint['int_buttress_z_distance']         = 50.0
bba_constraint['int_buttress_x_position']         = 10.0
bba_constraint['int_buttress_z_position']         = 10.0
bba_constraint['int_buttress_int_corner_length']  = 5.0
bba_constraint['int_buttress_ext_corner_length']  = 5.0
bba_constraint['int_buttress_bump_length']        = 10.0
bba_constraint['int_buttress_arc_height']         = -2.0
bba_constraint['int_buttress_smoothing_radius']   = 10.0
## external_buttress
bba_constraint['ext_buttress_z_length']           = 10.0
bba_constraint['ext_buttress_x_width']            = 5.0
bba_constraint['ext_buttress_x_distance']         = 20.0
bba_constraint['ext_buttress_z_position']         = 40.0
bba_constraint['ext_buttress_y_length']           = 10.0
bba_constraint['ext_buttress_y_position']         = 20.0
bba_constraint['ext_buttress_face_int_corner_length']   = 5.0
bba_constraint['ext_buttress_face_ext_corner_length']   = 5.0
bba_constraint['ext_buttress_face_bump_length']         = 10.0
bba_constraint['ext_buttress_base_int_corner_length']   = 5.0
bba_constraint['ext_buttress_base_ext_corner_length']   = 5.0
bba_constraint['ext_buttress_base_bump_length']         = 10.0
bba_constraint['ext_buttress_arc_height']               = -5.0
bba_constraint['ext_buttress_smoothing_radius']         = 10.0
### bell_side
## hollow
bba_constraint['hollow_z_height']                 = 10.0
bba_constraint['hollow_y_width']                  = 20.0
bba_constraint['hollow_spare_width']              = 10.0
## base_hole
bba_constraint['base_hole_nb']                    = 8
bba_constraint['base_hole_diameter']              = 4.0
bba_constraint['base_hole_position_diameter']     = 0.0
bba_constraint['base_hole_angle']                 = 0.0
### xyz-axles
## y_hole
bba_constraint['y_hole_diameter']                 = 4.0
bba_constraint['y_hole_z_top_position']           = 10.0
bba_constraint['y_hole_z_bottom_position']        = 10.0
bba_constraint['y_hole_x_position']               = 6.0
## x_hole
bba_constraint['x_hole_diameter']                 = 4.0
bba_constraint['x_hole_z_top_position']           = -6.0
bba_constraint['x_hole_z_bottom_position']        = -6.0
bba_constraint['x_hole_y_position']               = 6.0
## z_hole
bba_constraint['z_hole_diameter']                 = 4.0
bba_constraint['z_hole_external_diameter']        = 0.0
bba_constraint['z_hole_position_length']          = 15.0
### bell manufacturing
bba_constraint['bell_cnc_router_bit_radius']      = 1.0
bba_constraint['bell_extra_cut_thickness']        = 0.0
###### bagel
## bagel diameter
bba_constraint['bagel_axle_diameter']                   = 10.0
bba_constraint['bagel_axle_internal_diameter']          = 0.0
bba_constraint['bagel_axle_external_diameter']          = 0.0
## bagel thickness
bba_constraint['external_bagel_thickness']        = 2.0
bba_constraint['internal_bagel_thickness']        = 2.0
### bagel manufacturing
bba_constraint['bagel_extra_cut_thickness']       = 0.0

################################################################
# action
################################################################

my_bba = cnc25d_design.bba(bba_constraint)
my_bba.outline_display()
my_bba.write_figure_svg("test_output/bba_macro")
my_bba.write_figure_dxf("test_output/bba_macro")
my_bba.write_figure_brep("test_output/bba_macro")
my_bba.write_assembly_brep("test_output/bba_macro")
my_bba.write_freecad_brep("test_output/bba_macro")
#my_bba.run_simulation("") # no simulation for axle_lid
my_bba.view_design_configuration()
#my_bba.run_self_test("")
#my_bba.cli("--output_file_basename test_output/alm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_bba.get_fc_obj_3dconf('bell_bagel_assembly_conf1'))



