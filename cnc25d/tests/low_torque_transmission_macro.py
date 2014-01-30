# low_torque_transmission_macro.py
# the macro to generate a low_torque_transmission_macro epicyclic gearing.
# created by charlyoleg on 2014/01/30
#
# (C) Copyright 2014 charlyoleg
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
this piece of code is an example of how to use the parametric design low_torque_transmission
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

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
# low_torque_transmission constraint values
################################################################

ltt_c = {} # dictionary containing the low_torque_transmission constraint

##### from gear_profile
### first gear
# general
#ltt_c['gear_type']                      = 'i'
ltt_c['gear_tooth_nb']                  = 31
ltt_c['gear_module']                    = 10.0
ltt_c['gear_primitive_diameter']        = 0
ltt_c['gear_addendum_dedendum_parity']  = 50.0
# tooth height
ltt_c['gear_tooth_half_height']           = 0 # 10.0
ltt_c['gear_addendum_height_pourcentage'] = 100.0
ltt_c['gear_dedendum_height_pourcentage'] = 100.0
ltt_c['gear_hollow_height_pourcentage']   = 25.0
ltt_c['gear_router_bit_radius']           = 0.0
# positive involute
ltt_c['gear_base_diameter']       = 0
ltt_c['gear_force_angle']         = 0
ltt_c['gear_tooth_resolution']    = 2
ltt_c['gear_skin_thickness']      = 0
# negative involute (if zero, negative involute = positive involute)
ltt_c['gear_base_diameter_n']     = 0
ltt_c['gear_force_angle_n']       = 0
ltt_c['gear_tooth_resolution_n']  = 0
ltt_c['gear_skin_thickness_n']    = 0
### second gear
# general
#ltt_c['second_gear_type']                     = 'e'
ltt_c['second_gear_tooth_nb']                 = 19
ltt_c['second_gear_primitive_diameter']       = 0
ltt_c['second_gear_addendum_dedendum_parity'] = 0 # 50.0
# tooth height
ltt_c['second_gear_tooth_half_height']            = 0
ltt_c['second_gear_addendum_height_pourcentage']  = 100.0
ltt_c['second_gear_dedendum_height_pourcentage']  = 100.0
ltt_c['second_gear_hollow_height_pourcentage']    = 25.0
ltt_c['second_gear_router_bit_radius']            = 0
# positive involute
ltt_c['second_gear_base_diameter']      = 0
ltt_c['second_gear_tooth_resolution']   = 0
ltt_c['second_gear_skin_thickness']     = 0
# negative involute (if zero, negative involute = positive involute)
ltt_c['second_gear_base_diameter_n']    = 0
ltt_c['second_gear_tooth_resolution_n'] = 0
ltt_c['second_gear_skin_thickness_n']   = 0
### gearbar specific
#ltt_c['gearbar_slope']                  = 0.0
#ltt_c['gearbar_slope_n']                = 0.0
### position
# first gear position
ltt_c['center_position_x']                    = 0.0
ltt_c['center_position_y']                    = 0.0
ltt_c['gear_initial_angle']                   = 0.0
# second gear position
ltt_c['second_gear_position_angle']           = 0.0
ltt_c['second_gear_additional_axis_length']   = 0.0
### portion
#ltt_c['portion_tooth_nb']     = 0
#ltt_c['portion_first_end']    = 0
#ltt_c['portion_last_end']     = 0
### z-dimension
ltt_c['gear_profile_height']  = 20.0
##### from gearring
### holder
ltt_c['holder_diameter']            = 360.0
ltt_c['holder_crenel_number']       = 6
ltt_c['holder_position_angle']      = 0.0
ltt_c['holder_crenel_number_cut']   = 0
### holder-hole
ltt_c['holder_hole_position_radius']   = 0.0
ltt_c['holder_hole_diameter']          = 10.0
ltt_c['holder_hole_mark_nb']           = 0
ltt_c['holder_double_hole_diameter']   = 0.0
ltt_c['holder_double_hole_length']     = 0.0
ltt_c['holder_double_hole_position']   = 0.0
ltt_c['holder_double_hole_mark_nb']    = 0
### holder-crenel
ltt_c['holder_crenel_position']        = 10.0
ltt_c['holder_crenel_height']          = 10.0
ltt_c['holder_crenel_width']           = 10.0
ltt_c['holder_crenel_skin_width']      = 10.0
ltt_c['holder_crenel_router_bit_radius']   = 1.0
ltt_c['holder_smoothing_radius']       = 0.0
### holder-hole-B (experimental)
ltt_c['holder_hole_B_diameter']          = 10.0
ltt_c['holder_crenel_B_position']        = 10.0
ltt_c['holder_hole_B_crenel_list']       = []
### cnc router_bit constraint
ltt_c['cnc_router_bit_radius']          = 1.0

ltt_c = {}
c = {}
c['cnc_router_bit_radius']	= 0.1
c['holder_hole_B_diameter']	= 5.0
c['front_planet_carrier_width']	= 2.0
c['output_planet_width']	= 10.0
c['planet_width']	= 5.0
c['planet_carrier_middle_clearance_diameter']	= 0.0
c['holder_double_hole_position']	= 0.0
c['motor_x_width']	= 28.0
c['planet_carrier_rear_smooth_radius']	= 0.0
c['planet_slack']	= 0.2
c['planet_carrier_fitting_square_extra_cut']	= 0.0
c['step_slack']	= 1.0
c['gear_addendum_dedendum_parity_slack']	= 0.0
c['planet_carrier_spacer_length']	= 1.0
c['holder_double_hole_length']	= 0.0
c['hexagon_smooth_radius']	= 1.0
c['holder_double_hole_diameter']	= 0.0
c['step_nb']	= 2
c['output_holder_width']	= 20.0
c['planet_spacer_width']	= 1.0
c['sun_spacer_length']	= 1.0
c['axle_holder_width']	= 4.0
c['output_cover_radius_slack']	= 1.0
c['output_rear_planet_carrier_width']	= 3.0
c['holder_crenel_B_position']	= 5.0
c['holder_crenel_position']	= 5.0
c['holder_crenel_width']	= 5.0
c['gearring_dedendum_to_hollow_pourcentage']	= 0.0
c['motor_holder_C']	= 5.0
c['motor_holder_B']	= 5.0
c['motor_holder_A']	= 5.0
c['motor_holder_E']	= 2.0
c['holder_position_angle']	= 0.0
c['planet_nb']	= 0
c['axle_holder_C']	= 4.0
c['axle_holder_B']	= 4.0
c['axle_holder_A']	= 4.0
c['axle_holder_D']	= 10.0
c['gear_addendum_height_pourcentage']	= 100.0
c['holder_hole_B_crenel_list']	= []
c['holder_hole_diameter']	= 5.0
c['holder_crenel_router_bit_radius']	= 1.0
c['motor_y_width']	= 0.0
c['holder_hole_mark_nb']	= 0
c['planet_carrier_fitting_square_l2']	= 5.0
c['output_axle_diameter']	= 5.0
c['rear_planet_carrier_width']	= 2.0
c['planet_carrier_fitting_square_l1']	= 5.0
c['planet_carrier_middle_smooth_radius']	= 0.0
c['planet_carrier_external_diameter']	= 0.0
c['rear_planet_carrier_spacer_width']	= 1.0
c['planet_carrier_internal_diameter']	= 0.0

ltt_c.update(c)

################################################################
# action
################################################################

my_ltt = cnc25d_design.ltt(ltt_c)
my_ltt.outline_display()
my_ltt.write_figure_svg("test_output/ltt_macro")
my_ltt.write_figure_dxf("test_output/ltt_macro")
my_ltt.write_figure_brep("test_output/ltt_macro")
my_ltt.write_assembly_brep("test_output/ltt_macro")
my_ltt.write_freecad_brep("test_output/ltt_macro")
my_ltt.run_simulation("eg_sim_planet_sun")
my_ltt.run_simulation("eg_sim_annulus_planet")
my_ltt.view_design_configuration()
#my_ltt.run_self_test("")
#my_ltt.cli("--output_file_basename test_output/lttm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_ltt.get_fc_obj_3dconf('rear_planet_carrier'))


