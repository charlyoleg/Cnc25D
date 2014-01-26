# motor_lid_macro.py
# the macro to generate a motor_lid.
# created by charlyoleg on 2013/11/15
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
this piece of code is an example of how to use the parametric design motor_lid
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

ml_constraint = {}
### annulus-holder: inherit dictionary entries from gearring
### holder
ml_constraint['holder_diameter']            = 120.0
ml_constraint['holder_crenel_number']       = 6
ml_constraint['holder_position_angle']      = 0.0
### holder-hole
ml_constraint['holder_hole_position_radius']   = 0.0
ml_constraint['holder_hole_diameter']          = 5.0
ml_constraint['holder_double_hole_diameter']   = 0.0
ml_constraint['holder_double_hole_length']     = 0.0
ml_constraint['holder_double_hole_position']   = 0.0
### holder-crenel
ml_constraint['holder_crenel_position']        = 4.0
ml_constraint['holder_crenel_height']          = 2.0
ml_constraint['holder_crenel_width']           = 10.0
ml_constraint['holder_crenel_skin_width']      = 5.0
ml_constraint['holder_crenel_router_bit_radius']   = 1.0
ml_constraint['holder_smoothing_radius']       = 0.0
#### axle_lid
ml_constraint['clearance_diameter']           = 100.0
ml_constraint['central_diameter']             = 40.0
ml_constraint['axle_hole_diameter']           = 22.0
ml_constraint['annulus_holder_axle_hole_diameter'] = 0.0
### input axle-B
ml_constraint['axle_B_place']             = 'small' # 'small' or 'large' # useful when the gearring has an odd number of crenels
ml_constraint['axle_B_distance']          = 65.0
ml_constraint['axle_B_angle']             = 0.0
ml_constraint['axle_B_diameter']          = 3.0
ml_constraint['axle_B_external_diameter'] = 10.0
ml_constraint['axle_B_hole_diameter']     = 15.0
ml_constraint['axle_B_central_diameter']  = 12.0
### input axle-C
ml_constraint['axle_C_distance']          = 40.0
ml_constraint['axle_C_angle']             = 0.0
ml_constraint['axle_C_hole_diameter']     = 10.0
ml_constraint['axle_C_external_diameter'] = 30.0
### motor screws
ml_constraint['motor_screw1_diameter']    = 2.0
ml_constraint['motor_screw1_angle']       = 0.0
ml_constraint['motor_screw1_x_length']    = 10.0
ml_constraint['motor_screw1_y_length']    = 0.0
ml_constraint['motor_screw2_diameter']    = 0.0
ml_constraint['motor_screw2_angle']       = 0.0
ml_constraint['motor_screw2_x_length']    = 0.0
ml_constraint['motor_screw2_y_length']    = 0.0
ml_constraint['motor_screw3_diameter']    = 0.0
ml_constraint['motor_screw3_angle']       = 0.0
ml_constraint['motor_screw3_x_length']    = 0.0
ml_constraint['motor_screw3_y_length']    = 0.0
### holder-C
ml_constraint['fastening_BC_hole_diameter']     = 2.0
ml_constraint['fastening_BC_external_diameter'] = 6.0
ml_constraint['fastening_BC_bottom_position_diameter']  = 30.0
ml_constraint['fastening_BC_bottom_angle']              = 3.14/4
ml_constraint['fastening_BC_top_position_diameter']     = 30.0
ml_constraint['fastening_BC_top_angle']                 = 3.14/4
### leg
ml_constraint['leg_type']             = 'none' # 'none', 'rear' or 'side'
ml_constraint['leg_length']           = 0.0
ml_constraint['foot_length']          = 0.0
ml_constraint['toe_length']           = 0.0
ml_constraint['leg_hole_diameter']    = 0.0
ml_constraint['leg_hole_distance']    = 0.0
ml_constraint['leg_hole_length']      = 0.0
ml_constraint['leg_border_length']    = 0.0
ml_constraint['leg_shift_length']     = 0.0
### general
ml_constraint['smoothing_radius']       = 3.0
ml_constraint['cnc_router_bit_radius']  = 0.1
ml_constraint['extrusion_height']     = 10.0

################################################################
# action
################################################################

my_ml = cnc25d_design.motor_lid(ml_constraint)
my_ml.outline_display()
my_ml.write_figure_svg("test_output/ml_macro")
my_ml.write_figure_dxf("test_output/ml_macro")
my_ml.write_figure_brep("test_output/ml_macro")
my_ml.write_assembly_brep("test_output/ml_macro")
my_ml.write_freecad_brep("test_output/ml_macro")
#my_ml.run_simulation("") # no simulation for motor_lid
my_ml.view_design_configuration()
#my_ml.run_self_test("")
#my_ml.cli("--output_file_basename test_output/mlm.dxf") # Warning: all constraint values are reset to their default values


if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_ml.get_fc_obj_3dconf('motor_lid_3dconf1'))



