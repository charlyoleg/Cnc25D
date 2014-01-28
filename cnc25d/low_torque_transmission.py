# low_torque_transmission.py
# generates an epicyclic_gearing and simulates the sun/planet gear or the planet/annulus gear.
# created by charlyoleg on 2014/01/28
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


"""
low_torque_transmission.py is a parametric generator of epicylic gearing with an electric motor at the input and a hexagonal-axle at the output.
As every Cnc25D designs, you can view the 2D-figures in a Tk-window, generate the SVG, DXF and Brep files, simulate the sun/planet and planet/annulus gear.
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

import math
import sys, argparse
#from datetime import datetime
#import os, errno
#import re # to detect .dxf or .svg
#import Tkinter # to display the outline in a small GUI
#
import Part
#from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import gearring
import gearwheel
import gear_profile # to get the high-level parameter to find the angle position
#import axle_lid

################################################################
# low_torque_transmission constraint_constructor
################################################################

def ltt_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the low_torque_transmission design
  """
  r_parser = ai_parser
  ### structure
  r_parser.add_argument('--sun_gear_tooth_nb','--sgn', action='store', type=int, default=19,
    help="Set the number of gear-teeth of the sun-gear. Default: 19")
  r_parser.add_argument('--planet_gear_tooth_nb','--pgn', action='store', type=int, default=31,
    help="Set the number of gear-teeth of the planet-gear. Default: 31")
  r_parser.add_argument('--planet_nb','--pn', action='store', type=int, default=0,
    help="Set the number of planets. If equal to zero, the maximum possible number of planets is set. Default: 0")
  ### gear
  r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=1.0,
    help="Set the module of the sun, planet and annulus gear. Default: 1.0")
  r_parser.add_argument('--gear_router_bit_radius','--grr', action='store', type=float, default=0.1,
    help="Set the router_bit radius used to create the gear hollow of the first gear_profile. Default: 0.1")
  r_parser.add_argument('--gear_tooth_resolution','--gtr', action='store', type=int, default=2,
    help="It sets the number of segments of the gear involute. Default: 2")
  r_parser.add_argument('--gear_skin_thickness','--gst', action='store', type=float, default=0.0,
    help="Add or remove radial thickness on the gear involute to compensate the fabrication process. Default: 0.0")
  r_parser.add_argument('--gear_addendum_dedendum_parity_slack','--gadps', action='store', type=float, default=0.0,
    help="Decrease the gear_addendum_dedendum_parity to add some slack. Default: 0.0")
  r_parser.add_argument('--gearring_dedendum_to_hollow_pourcentage','--gdthp', action='store', type=float, default=0.0,
    help="Decrease the dedendum height pourcentage and increase the gear-hollow height pourcentage of the gearring. Use it with large gear_skin_thickness or gear_router_bit_radius. Default: 0.0")
  r_parser.add_argument('--gear_addendum_height_pourcentage','--gadhp', action='store', type=float, default=100.0,
    help="Set the gear_addendum_height_pourcentage of the sun-gear, planet-gear and annulus-gear. Use it to compensate gear_skin_thickness. Default: 100.0")
  ### sun-gear
  r_parser.add_argument('--sun_axle_diameter','--sad', action='store', type=float, default=5.0,
    help="Set the diameter of the sun-gear cylindrical axle. The sun-axle-hole lights the sun part. If set to 0.0, no axle hole is created. Default: 5.0")
  r_parser.add_argument('--sun_spacer_length','--ssl', action='store', type=float, default=1.0,
    help="Set the length between the internal and external radius of the sun-spacer ring. If set to 0.0, no sun-spacer ring is created. Default: 1.0")
  r_parser.add_argument('--sun_spacer_width','--ssw', action='store', type=float, default=0.5,
    help="Set the width (z-size) of the sun-spacer ring. If set to 0.0, no sun-spacer ring is created. Default: 0.5")
  ### planet-gear
  r_parser.add_argument('--planet_axle_diameter','--pad', action='store', type=float, default=5.0,
    help="Set the diameter of the planet-gear cylindrical axle. Default: 5.0")
  r_parser.add_argument('--planet_spacer_length','--psl', action='store', type=float, default=1.0,
    help="Set the length between the internal and external radius of the planet-spacer ring. If set to 0.0, no planet-spacer ring is created. Default: 1.0")
  r_parser.add_argument('--planet_spacer_width','--psw', action='store', type=float, default=1.0,
    help="Set the width (z-size) of the planet-spacer ring. If set to 0.0, no planet-spacer ring is created. Default: 1.0")
  ### planet-carrier
  # planet-carrier axle
  r_parser.add_argument('--planet_carrier_axle_diameter','--pcad', action='store', type=float, default=5.0,
    help="Set the diameter of the planet-carrier cylindrical axle. Default: 5.0")
  r_parser.add_argument('--planet_carrier_spacer_length','--pcsl', action='store', type=float, default=1.0,
    help="Set the length between the internal and external radius of the planet-carrier-spacer ring. If set to 0.0, no planet-carrier-spacer ring is created. Default: 1.0")
  r_parser.add_argument('--rear_planet_carrier_spacer_width','--rpcsw', action='store', type=float, default=1.0,
    help="Set the width (z-size) of the rear-planet-carrier-spacer ring. If set to 0.0, no rear-planet_carrier-spacer ring is created. Default: 1.0")
  r_parser.add_argument('--planet_carrier_axle_holder_diameter','--pcahd', action='store', type=float, default=10.0,
    help="Set the diameter of the planet-carrier-axle-holder. Default: 10.0")
  # planet-carrier rear, middle, front
  r_parser.add_argument('--planet_carrier_external_diameter','--pced', action='store', type=float, default=0.0,
    help="Set the external diameter of the rear, middle and front planet-carrier. If set to 0.0, the maximal possible value is selected. Default: 0.0")
  # planet-carrier rear
  r_parser.add_argument('--planet_carrier_internal_diameter','--pcid', action='store', type=float, default=0.0,
    help="Set the internal diameter of the rear and middle planet-carrier. If set to 0.0, a default value is selected. Default: 0.0")
  r_parser.add_argument('--planet_carrier_rear_smooth_radius','--pcrsr', action='store', type=float, default=0.0,
    help="Set the smoothing radius to generate the outlines of the rear-planet-carrier. Default: 0.0")
  # planet-carrier middle
  r_parser.add_argument('--planet_carrier_middle_clearance_diameter','--pcmcd', action='store', type=float, default=0.0,
    help="Set the clearnace diameter around the planet gear for the middle planet-carrier. If set to 0.0, the minimal value is selected. Default: 0.0")
  r_parser.add_argument('--planet_carrier_middle_smooth_radius','--pcmsr', action='store', type=float, default=0.0,
    help="Set the smoothing radius to generate the outlines of the middle-planet-carrier. Default: 0.0")
  # planet-carrier fitting
  r_parser.add_argument('--planet_carrier_fitting_square_l1','--pcfsl1', action='store', type=float, default=5.0,
    help="Set the length_1 of the square-fitting between middle and front planet-carrier. If set to 0.0, no square fitting is generated. Default: 5.0")
  r_parser.add_argument('--planet_carrier_fitting_square_l2','--pcfsl2', action='store', type=float, default=5.0,
    help="Set the length_2 of the square-fitting between middle and front planet-carrier. If set to 0.0, no square fitting is generated. Default: 5.0")
  r_parser.add_argument('--planet_carrier_fitting_square_extra_cut','--pcfsec', action='store', type=float, default=0.0,
    help="Set the extra-cut length of the square-fitting for the front planet-carrier. Default: 0.0")
  r_parser.add_argument('--planet_carrier_fitting_hole_diameter','--pcfhd', action='store', type=float, default=1.3,
    help="Set the diameter of hole-fitting. If set to 0.0, no hole-fitting is created. Default: 1.3")
  r_parser.add_argument('--planet_carrier_fitting_hole_position','--pcfhp', action='store', type=float, default=4.0,
    help="Set the length between the square-fitting and hole-fitting. Default: 4.0")
  r_parser.add_argument('--planet_carrier_fitting_double_hole_distance','--pcfdhd', action='store', type=float, default=4.0,
    help="Set the length between the double-hole-fitting. If set to 0.0, a single fitting-hole is created. Default: 4.0")
  ## planet_carrier_angle
  r_parser.add_argument('--planet_carrier_angle','--pca', action='store', type=float, default=0.0,
    help="Set the initial angle of the planet carrier. It impacts the initial sun-gear angle. Default: 0.0")
  ### annulus: inherit dictionary entries from gearring
  i_gearring = gearring.gearring()
  r_parser = i_gearring.get_constraint_constructor()(r_parser, 1)
  ### first step z-dimension
  r_parser.add_argument('--planet_width','--pw', action='store', type=float, default=5.0,
    help="Set the z-size of the planet gearwheel. Default: 5.0")
  r_parser.add_argument('--front_planet_carrier_width','--fpcw', action='store', type=float, default=2.0,
    help="Set the z-size of the front-planet-carrier. Default: 2.0")
  r_parser.add_argument('--rear_planet_carrier_width','--rpcw', action='store', type=float, default=2.0,
    help="Set the z-size of the rear-planet-carrier. Default: 2.0")
  r_parser.add_argument('--planet_slack','--ps', action='store', type=float, default=0.2,
    help="Set the slack thickness between planet-gearwheel and planet-carrier. Default: 0.2")
  r_parser.add_argument('--step_slack','--ss', action='store', type=float, default=1.0,
    help="Set the minimal slack thickness between front and rear planet-carrier. Default: 1.0")
  ### output step z-dimension
  r_parser.add_argument('--output_planet_width','--opw', action='store', type=float, default=10.0,
    help="Set the z-size of the output-step planet gearwheel. Default: 10.0")
  r_parser.add_argument('--output_front_planet_carrier_width','--ofpcw', action='store', type=float, default=3.0,
    help="Set the z-size of the output-step front-planet-carrier. Default: 3.0")
  r_parser.add_argument('--output_rear_planet_carrier_width','--orpcw', action='store', type=float, default=3.0,
    help="Set the z-size of the output-step rear-planet-carrier. Default: 3.0")
  ### output_shaft
  r_parser.add_argument('--hexagon_hole_diameter','--ohhd', action='store', type=float, default=10.0,
    help="Set the diameter of the hole of the hexagin-output-shaft. Default: 10.0")
  r_parser.add_argument('--hexagon_length','--ohl', action='store', type=float, default=20.0,
    help="Set the length between two opposite sides of the hexagin-output-shaft. Default: 20.0")
  r_parser.add_argument('--hexagon_smooth_radius','--ohsr', action='store', type=float, default=1.0,
    help="Set the smoothing radius for the hexagon outline of the output-shaft. Default: 1.0")
  r_parser.add_argument('--hexagon_width','--hw', action='store', type=float, default=20.0,
    help="Set the z-size of the hexagin-output-shaft. Default: 20.0")
  ### output_holder
  r_parser.add_argument('--output_cover_radius_slack','--ocds', action='store', type=float, default=1.0,
    help="Set the slack between the output_front_planet_carrier_radius and the output_cover_radius. Default: 1.0")
  r_parser.add_argument('--output_cover_width','--ocw', action='store', type=float, default=2.0,
    help="Set the z-size of the output_cover. Default: 2.0")
  r_parser.add_argument('--output_holder_width','--ohw', action='store', type=float, default=20.0,
    help="Set the z-size of the output_holder. Default: 20.0")
  ### output_axle_holder
  r_parser.add_argument('--output_axle_diameter','--oad', action='store', type=float, default=5.0,
    help="Set the diameter of the output-axle. Default: 5.0")
  r_parser.add_argument('--axle_holder_width','--ahw', action='store', type=float, default=4.0,
    help="Set the z-size of the output_axle_holder-plate. Default: 4.0")
  r_parser.add_argument('--axle_holder_A','--aha', action='store', type=float, default=4.0,
    help="Set the length axle_holder_A of the output_axle_holder. Default: 4.0")
  r_parser.add_argument('--axle_holder_B','--ahb', action='store', type=float, default=4.0,
    help="Set the length axle_holder_B of the output_axle_holder. Default: 4.0")
  r_parser.add_argument('--axle_holder_C','--ahc', action='store', type=float, default=4.0,
    help="Set the length axle_holder_C of the output_axle_holder. Default: 4.0")
  r_parser.add_argument('--axle_holder_D','--ahd', action='store', type=float, default=10.0,
    help="Set the length axle_holder_D of the output_axle_holder. Default: 10.0")
  ### input gearwheel
  r_parser.add_argument('--input_axle_diameter','--iad', action='store', type=float, default=2.0,
    help="Set the diameter of the motor shaft. Default: 2.0")
  r_parser.add_argument('--input_sun_width','--isw', action='store', type=float, default=10.0,
    help="Set the z-size of the input-gearwheel. Default: 10.0")
  r_parser.add_argument('--input_slack','--is', action='store', type=float, default=2.0,
    help="Set the maximal slack between the motor_holder and the first rear_planet_carrier. Default: 2.0")
  ### motor_holder
  r_parser.add_argument('--motor_x_width','--mxw', action='store', type=float, default=28.0,
    help="Set the x-width or the diameter of the motor. Default: 28.0")
  r_parser.add_argument('--motor_y_width','--myw', action='store', type=float, default=0.0,
    help="Set the y-width of the motor. If set to 0.0, the motor shape is a circle and not a rectangle. Default: 0.0")
  r_parser.add_argument('--motor_holder_width','--mhw', action='store', type=float, default=3.0,
    help="Set the z-size of the motor_holder-plate. Default: 3.0")
  r_parser.add_argument('--motor_holder_A','--mha', action='store', type=float, default=5.0,
    help="Set the length motor_holder_A of the motor_holder. Default: 5.0")
  r_parser.add_argument('--motor_holder_B','--mhb', action='store', type=float, default=5.0,
    help="Set the length motor_holder_B of the motor_holder. Default: 5.0")
  r_parser.add_argument('--motor_holder_C','--mhc', action='store', type=float, default=5.0,
    help="Set the length motor_holder_C of the motor_holder. Default: 5.0")
  r_parser.add_argument('--motor_holder_D','--mhd', action='store', type=float, default=10.0,
    help="Set the length motor_holder_D of the motor_holder. Default: 10.0")
  r_parser.add_argument('--motor_holder_E','--mhe', action='store', type=float, default=2.0,
    help="Set the length motor_holder_E of the motor_holder. Default: 2.0")
  r_parser.add_argument('--motor_holder_leg_width','--mhlw', action='store', type=float, default=4.0,
    help="Set the thickness of the legs of the motor_holder. Default: 4.0")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1,
    help="Set the minimum router_bit radius of the low_torque_transmission design. Default: 0.1")
  # return
  return(r_parser)

################################################################
# constraint conversion
################################################################


################################################################
# low_torque_transmission constraint_check
################################################################

def ltt_constraint_check(c):
  """ check the low_torque_transmission constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  return(c)

################################################################
# low_torque_transmission 2D-figures construction
################################################################

def ltt_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the low_torque_transmission design
  """
  ### precision
  radian_epsilon = math.pi/1000
  ###
  r_figures = {}
  r_height = {}
  #
  ###
  return((r_figures, r_height))

      
################################################################
# low_torque_transmission 3D assembly-configuration construction
################################################################

def ltt_3d_construction(c):
  """ construct the 3D-assembly-configurations of the low_torque_transmission
  """
  #
  r_assembly = {}
  r_slice = {}
  #
  return((r_assembly, r_slice))


################################################################
# low_torque_transmission simulation
################################################################

def eg_sim_planet_sun(c):
  """ define the epicyclic_gearing first simulation: planet-sun
  """
  pg_c_list = planet_gearwheel_constraint(c)
  sg_c = pg_c_list[0]
  sg_c['gear_type'] = 'e'
  sg_c['second_gear_type'] = 'e'
  # gear_profile simulation
  i_gear_profile = gear_profile.gear_profile()
  i_gear_profile.apply_external_constraint(sg_c)
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def eg_sim_annulus_planet(c):
  """ define the epicyclic_gearing second simulation: annulus-planet
  """
  sg_c = annulus_gearring_constraint(c)
  sg_c['gear_type'] = 'i'
  sg_c['second_gear_type'] = 'e'
  # gear_profile gear_profile
  i_gear_profile = gear_profile.gear_profile()
  i_gear_profile.apply_external_constraint(sg_c)
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def ltt_2d_simulations():
  """ return the dictionary defining the available simulation for low_torque_transmission
  """
  r_sim = {}
  r_sim['eg_sim_planet_sun'] = eg_sim_planet_sun
  r_sim['eg_sim_annulus_planet'] = eg_sim_annulus_planet
  return(r_sim)


################################################################
# low_torque_transmission info
################################################################

def ltt_info(c):
  """ create the text info related to the low_torque_transmission
  """
  r_info = ""
#  r_info += """
#sun_gear_tooth_nb:        \t{:d}
#planet_gear_tooth_nb:     \t{:d}
#annulus_gear_tooth_nb:    \t{:d}
#smallest_gear_tooth_nb:   \t{:d}
#planet_nb:                \t{:d}
#planet_number_max:        \t{:d}
#epicyclic_gearing_ratio:  \t{:0.3f}  1/R: {:0.3f}  1/R2: {:0.3f}  1/R3: {:0.3f}  1/R4: {:0.3f}  1/R5: {:0.3f}
#""".format(c['sun_gear_tooth_nb'], c['planet_gear_tooth_nb'], c['annulus_gear_tooth_nb'], c['smallest_gear_tooth_nb'], c['planet_nb'], c['planet_number_max'], c['epicyclic_gearing_ratio'], 1.0/c['epicyclic_gearing_ratio'], 1.0/c['epicyclic_gearing_ratio']**2, 1.0/c['epicyclic_gearing_ratio']**3, 1.0/c['epicyclic_gearing_ratio']**4, 1.0/c['epicyclic_gearing_ratio']**5)
#  r_info += """
#gear_module:              \t{:0.3f}
#gear_router_bit_radius:   \t{:0.3f}
#gear_tooth_resolution:    \t{:d}
#gear_skin_thickness:      \t{:0.3f}
#gear_addendum_dedendum_parity_slack: {:0.3f}
#""".format(c['gear_module'], c['gear_router_bit_radius'], c['gear_tooth_resolution'], c['gear_skin_thickness'], c['gear_addendum_dedendum_parity_slack'])
  #print(r_info)
  return(r_info)


################################################################
# self test
################################################################

def ltt_self_test():
  """
  This is the non-regression test of low_torque_transmission.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , "--sun_gear_tooth_nb 20 --planet_gear_tooth_nb 31 --gear_module 1.0 --planet_nb 3"],
    ["last test"            , "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --planet_nb 4"]]
  return(r_tests)

################################################################
# low_torque_transmission design declaration
################################################################

class ltt(cnc25d_api.bare_design):
  """ low_torque_transmission design
  """
  def __init__(self, constraint={}):
    """ configure the low_torque_transmission design
    """
    self.design_setup(
      s_design_name             = "LTT_design",
      f_constraint_constructor  = ltt_constraint_constructor,
      f_constraint_check        = ltt_constraint_check,
      f_2d_constructor          = ltt_2d_construction,
      d_2d_simulation           = ltt_2d_simulations(),
      f_3d_constructor          = ltt_3d_construction,
      f_info                    = ltt_info,
      l_display_figure_list     = [],
      s_default_simulation      = '',
      l_2d_figure_file_list     = [], # all figures
      l_3d_figure_file_list     = [],
      l_3d_conf_file_list       = [],
      f_cli_return_type         = None,
      l_self_test_list          = ltt_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("low_torque_transmission.py says hello!\n")
  my_ltt = ltt()
  #my_ltt.cli()
  my_ltt.cli("--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_eg.get_fc_obj_3dconf('ltt_3dconf1'))


