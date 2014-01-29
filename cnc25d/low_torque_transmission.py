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
  r_parser.add_argument('--step_nb','--sn', action='store', type=int, default=2,
    help="Set the number of epicyclic-step (including the output step). Default: 2")
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
  # inheritance
  gr_c = c.copy()
  c['annulus_gear_tooth_nb'] = c['sun_gear_tooth_nb'] + 2*c['planet_gear_tooth_nb']
  gr_c['gear_tooth_nb'] = c['annulus_gear_tooth_nb']
  i_gr = gearring.gearring()
  i_gr.apply_external_constraint(gr_c)
  # planet number
  planet_size_angle = 2*math.asin(float(c['planet_gear_tooth_nb']+2)/(c['planet_gear_tooth_nb']+c['sun_gear_tooth_nb']))
  planet_number_max_securoty_coef = 1.0
  c['planet_number_max'] = int(2*math.pi/(planet_size_angle*planet_number_max_securoty_coef))
  #print("dbg244: planet_number_max:", c['planet_number_max'])
  if(c['planet_nb']==0):
    c['planet_nb'] = c['planet_number_max']
  if(c['planet_nb']>c['planet_number_max']):
    print("ERR247: Error, planet_nb {:d} is bigger than planet_number_max {:d}".format(c['planet_nb'], c['planet_number_max']))
    sys.exit(2)
  if(c['planet_nb']<1):
    print("ERR251: Error, planet_nb {:d} must be bigger or equal to 1".format(c['planet_nb']))
    sys.exit(2)
  # epicyclic fitting
  epicyclic_tooth_check = (2*(c['sun_gear_tooth_nb'] + c['planet_gear_tooth_nb'])) % c['planet_nb']
  if(epicyclic_tooth_check != 0):
    print("WARN243: Warning, not respected epicyclic-gearing-tooth-nb relation: 2*(sun_gear_tooth_nb {:d} + planet_gear_tooth_nb {:d}) % planet_nb {:d} == {:d} (should be 0)".format(c['sun_gear_tooth_nb'], c['planet_gear_tooth_nb'], c['planet_nb'], epicyclic_tooth_check))
  c['planet_angle_inc'] = 2*math.pi/c['planet_nb']
  c['planet_circle_radius'] = (c['sun_gear_tooth_nb'] + c['planet_gear_tooth_nb'])*c['gear_module']/2.0
  c['planet_angle_position'] = []
  c['planet_x_position'] = []
  c['planet_y_position'] = []
  for i in range(c['planet_nb']):
    c['planet_angle_position'].append(c['planet_carrier_angle']+i*c['planet_angle_inc'])
    c['planet_x_position'].append(0.0 + c['planet_circle_radius']*math.cos(c['planet_angle_position'][i]))
    c['planet_y_position'].append(0.0 + c['planet_circle_radius']*math.sin(c['planet_angle_position'][i]))
  annulus_planet_c = {}
  annulus_planet_c['gear_type'] = 'i'
  annulus_planet_c['second_gear_type'] = 'e'
  annulus_planet_c['gear_tooth_nb'] = c['annulus_gear_tooth_nb']
  annulus_planet_c['gear_module'] = c['gear_module']
  annulus_planet_c['gear_initial_angle'] = 0.0 # just an arbitrary value
  annulus_planet_c['second_gear_tooth_nb'] = c['planet_gear_tooth_nb']
  #annulus_planet_c['second_gear_position_angle'] = c['planet_angle_position'][0]+math.pi # first planet angle position
  annulus_planet_c['second_gear_additional_axis_length'] = 0.0 # in epicyclic_gearing it's difficult to imagine something else
  i_gp = gear_profile.gear_profile(annulus_planet_c)
  c['planet_oriantation_angles'] = [] # gear_initial_angle for planets
  for i in range(c['planet_nb']):
    annulus_planet_c['second_gear_position_angle'] = c['planet_angle_position'][i] + math.pi
    i_gp.apply_external_constraint(annulus_planet_c)
    #i_gp.run_simulation('gear_profile_simulation_A') # dbg
    c['planet_oriantation_angles'].append(i_gp.get_constraint()['second_positive_initial_angle'])
  planet_sun_c = {}
  planet_sun_c['gear_type'] = 'e'
  planet_sun_c['second_gear_type'] = 'e'
  planet_sun_c['gear_module'] = c['gear_module']
  planet_sun_c['gear_tooth_nb'] = c['planet_gear_tooth_nb']
  planet_sun_c['second_gear_tooth_nb'] = c['sun_gear_tooth_nb']
  planet_sun_c['second_gear_additional_axis_length'] = 0.0 # in epicyclic_gearing it's difficult to imagine something else
  sun_half_tooth_angle = math.pi/c['sun_gear_tooth_nb']
  c['sun_oriantation_angles'] = [] # gear_initial_angle for sun
  for i in range(c['planet_nb']):
    planet_sun_c['center_position_x'] = c['planet_x_position'][i]
    planet_sun_c['center_position_y'] = c['planet_y_position'][i]
    planet_sun_c['gear_initial_angle'] = c['planet_oriantation_angles'][i]
    planet_sun_c['second_gear_position_angle'] = c['planet_angle_position'][i] + math.pi
    #print("dbg295: gear_initial_angle, second_gear_position_angle:", planet_sun_c['gear_initial_angle'], planet_sun_c['second_gear_position_angle'])
    i_gp.apply_external_constraint(planet_sun_c)
    sun_x_position = i_gp.get_constraint()['g2_ix']
    sun_y_position = i_gp.get_constraint()['g2_iy']
    c['sun_oriantation_angles'].append(i_gp.get_constraint()['second_positive_initial_angle'])
    #c['sun_oriantation_angles'].append(math.fmod(i_gp.get_constraint()['second_positive_initial_angle']+sun_half_tooth_angle, 2*sun_half_tooth_angle)-sun_half_tooth_angle) # it is better to do this normaization when comparing
    if(abs(sun_x_position - 0.0)>radian_epsilon):
      print("ERR286: Error, sun_x_position {:0.3f} is not at the expected coordinate 0.0".format(sun_x_position))
      sys.exit(2)
    if(abs(sun_y_position - 0.0)>radian_epsilon):
      print("ERR289: Error, sun_y_position {:0.3f} is not at the expected coordinate 0.0".format(sun_y_position))
      sys.exit(2)
    #if(abs(c['sun_oriantation_angles'][i]-c['sun_oriantation_angles'][0])>radian_epsilon):
    if(abs(math.fmod(c['sun_oriantation_angles'][i]-c['sun_oriantation_angles'][0]+sun_half_tooth_angle, 2*sun_half_tooth_angle)-sun_half_tooth_angle)>radian_epsilon):
      print("ERR293: Error, {:d}-sun_oriantation_angles {:0.3f} is different from 0-sun_oriantation_angles {:0.3f}".format(i, c['sun_oriantation_angles'][i], c['sun_oriantation_angles'][0]))
      #print("dbg306: sun_half_tooth_angle:", sun_half_tooth_angle, 2*sun_half_tooth_angle, i_gp.get_constraint()['second_pi_module_angle'])
      #print("dbg307: sun_oriantation_angles:", c['sun_oriantation_angles'])
      #print("dbg308: planet_oriantation_angles:", c['planet_oriantation_angles'])
      sys.exit(2)
  c['sun_oriantation_angle'] = c['sun_oriantation_angles'][0]
  # sun axle and spacer
  c['sun_axle_radius'] = c['sun_axle_diameter']/2.0
  if(c['sun_axle_diameter']+2*c['sun_spacer_length']>c['gear_module']*(c['sun_gear_tooth_nb']-3)):
    print("ERR310: Error, sun_axle_diameter {:0.3f} or sun_spacer_length {:0.3f} are too big compare to gear_module {:0.3f} and sun_gear_tooth_nb {:d}".format(c['sun_axle_diameter'], c['sun_spacer_length'], c['gear_module'], c['sun_gear_tooth_nb']))
    sys.exit(2)
  # planet axle and spacer
  if(c['planet_axle_diameter']+2*c['planet_spacer_length']>c['gear_module']*(c['planet_gear_tooth_nb']-3)):
    print("ERR311: Error, planet_axle_diameter {:0.3f} or planet_spacer_length {:0.3f} are too big compare to gear_module {:0.3f} and planet_gear_tooth_nb {:d}".format(c['planet_axle_diameter'], c['planet_spacer_length'], c['gear_module'], c['planet_gear_tooth_nb']))
    sys.exit(2)
  # planet_carrier axle and spacer
  if(c['planet_carrier_axle_diameter']+2*c['planet_carrier_spacer_length']>c['gear_module']*(c['planet_gear_tooth_nb']-3)):
    print("ERR315: Error, planet_carrier_axle_diameter {:0.3f} or planet_carrier_spacer_length {:0.3f} are too big compare to gear_module {:0.3f} and planet_gear_tooth_nb {:d}".format(c['planet_carrier_axle_diameter'], c['planet_carrier_spacer_length'], c['gear_module'], c['planet_gear_tooth_nb']))
    sys.exit(2)
  if(c['planet_carrier_axle_holder_diameter']>c['gear_module']*(c['planet_gear_tooth_nb']-3)):
    print("ERR318: Error, planet_carrier_axle_holder_diameter {:0.3f} is too big compare to gear_module {:0.3f} and planet_gear_tooth_nb {:d}".format(c['planet_carrier_axle_holder_diameter'], c['gear_module'], c['planet_gear_tooth_nb']))
    sys.exit(2)
  if(c['planet_axle_diameter']+2*c['planet_spacer_length']>c['planet_carrier_axle_holder_diameter']):
    print("ERR321: Error, planet_carrier_axle_holder_diameter {:0.3f} is too small compare to planet_axle_diameter {:0.3f} and planet_spacer_length {:0.3f}".format(c['planet_axle_diameter'], c['planet_spacer_length'], c['planet_carrier_axle_holder_diameter']))
    sys.exit(2)
  c['planet_carrier_axle_holder_radius'] = c['planet_carrier_axle_holder_diameter']/2.0
  # planet_carrier_external_diameter
  c['planet_carrier_external_diameter_max'] = c['gear_module']*(c['annulus_gear_tooth_nb']-4)
  if(c['planet_carrier_external_diameter']==0):
    c['planet_carrier_external_diameter'] = c['planet_carrier_external_diameter_max']
  c['planet_carrier_external_radius'] = c['planet_carrier_external_diameter']/2.0
  if(c['planet_carrier_external_diameter']>c['planet_carrier_external_diameter_max']):
    print("ERR329: Error, planet_carrier_external_diameter {:0.3f} is bigger than planet_carrier_external_diameter_max {:0.3f}".format(c['planet_carrier_external_diameter'], c['planet_carrier_external_diameter_max']))
    sys.exit(2)
  if(c['planet_carrier_external_radius']<c['planet_circle_radius']-c['planet_carrier_axle_holder_radius']+radian_epsilon):
    print("ERR325: Error, planet_carrier_external_radius {:0.3f} is too small compare to planet_circle_radius {:0.3f} and planet_carrier_axle_holder_radius {:0.3f}".format(c['planet_carrier_external_radius'], c['planet_circle_radius'], c['planet_carrier_axle_holder_radius']))
    sys.exit(2)
  # planet_carrier_internal_diameter
  c['planet_carrier_internal_diameter_min'] = c['gear_module']*(c['sun_gear_tooth_nb']+4)
  c['planet_carrier_internal_diameter_default'] = 2*c['planet_circle_radius']
  if(c['planet_carrier_internal_diameter']==0):
    c['planet_carrier_internal_diameter'] = c['planet_carrier_internal_diameter_default']
  c['planet_carrier_internal_radius'] = c['planet_carrier_internal_diameter']/2.0
  if(c['planet_carrier_internal_diameter']<c['planet_carrier_internal_diameter_min']):
    print("ERR342: Error, planet_carrier_internal_diameter {:0.3f} is smaller than planet_carrier_internal_diameter_min {:0.3f}".format(c['planet_carrier_internal_diameter'], c['planet_carrier_internal_diameter_min']))
    sys.exit(2)
  if(c['planet_carrier_internal_diameter']>c['planet_carrier_external_diameter']-radian_epsilon):
    print("ERR345: Error, planet_carrier_internal_diameter {:0.3f} is bigger than planet_carrier_external_diameter {:0.3f}".format(c['planet_carrier_internal_diameter'], c['planet_carrier_external_diameter']))
    sys.exit(2)
  # planet_carrier_rear_smooth_radius
  if(c['planet_carrier_rear_smooth_radius']<c['cnc_router_bit_radius']):
    c['planet_carrier_rear_smooth_radius'] = c['cnc_router_bit_radius']
  if(c['planet_carrier_rear_smooth_radius']>min(c['planet_carrier_internal_radius'], c['planet_carrier_axle_holder_radius'])):
    print("ERR351: Error, planet_carrier_rear_smooth_radius {:0.3f} is too big compare to planet_carrier_internal_radius {:0.3f} and planet_carrier_axle_holder_radius {:0.3f}".format(c['planet_carrier_rear_smooth_radius'], c['planet_carrier_internal_radius'],  c['planet_carrier_axle_holder_radius']))
    sys.exit(2)
  # planet_carrier_middle_clearance_diameter
  c['planet_carrier_middle_clearance_diameter_min'] = c['gear_module']*(c['planet_gear_tooth_nb']+4)
  if(c['planet_carrier_middle_clearance_diameter']==0):
    c['planet_carrier_middle_clearance_diameter'] = c['planet_carrier_middle_clearance_diameter_min']
  c['planet_carrier_middle_clearance_radius'] = c['planet_carrier_middle_clearance_diameter']/2.0
  if(c['planet_carrier_middle_clearance_diameter']<c['planet_carrier_middle_clearance_diameter_min']):
    print("ERR370: Error, planet_carrier_middle_clearance_diameter {:0.3f} is smaller than planet_carrier_middle_clearance_diameter_min {:0.3f}".format(c['planet_carrier_middle_clearance_diameter'], c['planet_carrier_middle_clearance_diameter_min']))
    sys.exit(2)
  # planet_carrier_middle_smooth_radius
  if(c['planet_carrier_middle_smooth_radius']<c['cnc_router_bit_radius']):
    c['planet_carrier_middle_smooth_radius'] = c['cnc_router_bit_radius']
  # pre-calculations for middle-planet_carrier
  lOA = c['planet_circle_radius']
  lAG = c['planet_carrier_middle_clearance_radius']
  lOG = c['planet_carrier_external_radius']
  lOH = c['planet_carrier_internal_radius']
  cos_OAG = (float(lOA**2+lAG**2-lOG**2)/(2*lOA*lAG))
  aOAG = math.acos(cos_OAG)
  cos_OAH = (float(lOA**2+lAG**2-lOH**2)/(2*lOA*lAG))
  aOAH = math.acos(cos_OAH)
  c['middle_planet_carrier_aOAG'] = aOAG
  c['middle_planet_carrier_aOAH'] = aOAH
  c['middle_planet_carrier_internal_radius'] = c['planet_carrier_internal_radius']
  aDOA = c['planet_angle_inc']/2.0
  lAB = 2*lOA*math.sin(aDOA)
  planet_carrier_middle_smooth_radius_plus = 1.1*c['planet_carrier_middle_smooth_radius'] # a bit more to ensure a good cnc_cut
  if(lAB<2*c['planet_carrier_middle_clearance_radius']+2*planet_carrier_middle_smooth_radius_plus):
    lAD = lAB/2.0
    lAE = c['planet_carrier_middle_clearance_radius']+planet_carrier_middle_smooth_radius_plus
    cos_DAE = float(lAD)/lAE
    print("dbg401: cos_DAE", cos_DAE)
    aDAE = math.acos(cos_DAE)
    aOAD = math.pi/2 - c['planet_angle_inc']/2.0
    aOAF = aOAD + aDAE
    if(aOAG<aOAF):
      print("ERR395: Error, planet_carrier_external_radius {:0.3f} is too small compare to planet_carrier_middle_clearance_radius {:0.3f} or planet_carrier_middle_smooth_radius {:0.3f}".format(c['planet_carrier_external_radius'], c['planet_carrier_middle_clearance_radius'], c['planet_carrier_middle_smooth_radius']))
      sys.exit(2)
    elif(aOAH<aOAF):
      c['middle_planet_carrier_aOAH'] = aOAF # a bit more to ensure a good cnc_cut
      lDE = math.sqrt(lAE**2-lAD**2)
      lOD = math.sqrt(lOA**2-lAD**2)
      c['middle_planet_carrier_internal_radius'] = lOD + lDE
  # planet_carrier_fitting_square
  c['planet_carrier_fitting_square'] = False
  c['planet_carrier_fitting_hole_ref'] = c['planet_carrier_external_radius']
  if((c['planet_carrier_fitting_square_l1']==0)and(c['planet_carrier_fitting_square_l2']==0)):
    c['planet_carrier_fitting_square'] = True
    def sub_fitting_square(ai_r, ai_l1, ai_l2):
      """ compute some parameter for the planet_carrier fitting_square for the middle and front (with extra_cut)
      """
      r = {}
      lOA = ai_r
      lDA = ai_l1/2.0
      lAB = ai_l2
      aDOA = math.asin(float(lDA)/lOA)
      r['ext_angle'] = aDOA
      aOAB = aDOA # because (OD)//(AB)
      lOB2 = lAB**2 + lOA**2 - 2*lAB*lOA*math.cos(aOAB) # law of cosines within OAB
      lOB = math.sqrt(lOB2)
      lBC = lDA
      aCOB = math.asin(float(lBC)/lOB)
      r['int_angle'] = aCOB
      r['int_radius'] = lOB
      lOC = math.sqrt(lOB**2-lBC**2)
      c['ref_radius'] = lOC
      return(r)
    middle_fs = sub_fitting_square(c['planet_carrier_external_radius'],
                  c['planet_carrier_fitting_square_l1'], c['planet_carrier_fitting_square_l2'])
    c['middle_planet_carrier_fitting_square_ext_angle'] = middle_fs['ext_angle']
    c['middle_planet_carrier_fitting_square_int_angle'] = middle_fs['int_angle']
    c['middle_planet_carrier_fitting_square_int_radius'] = middle_fs['int_radius']
    if(middle_fs['ref_radius']<c['middle_planet_carrier_internal_radius']):
      print("ERR435: Error, planet_carrier_fitting_square_l2 {:0.3f} is too big".format(c['planet_carrier_fitting_square_l2']))
      sys.exit(2)
    c['planet_carrier_fitting_hole_ref'] = middle_fs['ref_radius']
    front_fs = sub_fitting_square(c['planet_carrier_external_radius'],
                c['planet_carrier_fitting_square_l1']+2*c['planet_carrier_fitting_square_extra_cut'],
                c['planet_carrier_fitting_square_l2']+c['planet_carrier_fitting_square_extra_cut'])
    c['front_planet_carrier_fitting_square_ext_angle'] = front_fs['ext_angle']
    c['front_planet_carrier_fitting_square_int_angle'] = front_fs['int_angle']
    c['front_planet_carrier_fitting_square_int_radius'] = front_fs['int_radius']
  c['planet_carrier_fitting_hole_radius'] = c['planet_carrier_fitting_hole_diameter']/2.0
  if(c['planet_carrier_fitting_hole_radius']>0):
    lOB = c['planet_carrier_fitting_hole_ref'] - c['planet_carrier_fitting_hole_position']
    lBC = c['planet_carrier_fitting_double_hole_distance']/2.0
    lOC = math.sqrt(lOB**2+lBC**2)
    aBOC = math.atan(float(lBC)/lOB)
    c['planet_carrier_fitting_hole_position_radius'] = lOC
    c['planet_carrier_fitting_hole_position_angle'] = aBOC
  # step_nb
  if(c['step_nb']<1):
    print("ERR456: Error, step_nb {:d} is bigger or equal to 1".format(c['step_nb']))
    sys.exit(2)
  # first step z-dimension
  c['middle_planet_carrier_width'] = c['rear_planet_carrier_spacer_width'] + c['planet_slack'] + c['planet_width'] + c['planet_spacer_width']
  c['sun_width'] = c['step_slack'] + c['rear_planet_carrier_width'] + c['middle_planet_carrier_width'] - c['sun_spacer_width']
  c['step_width'] = c['rear_planet_carrier_width'] + c['middle_planet_carrier_width'] + c['front_planet_carrier_width']
  # output step z-dimension
  c['output_middle_planet_carrier_width'] = c['rear_planet_carrier_spacer_width'] + c['planet_slack'] + c['output_planet_width'] + c['planet_spacer_width']
  c['output_sun_width'] = c['step_slack'] + c['output_rear_planet_carrier_width'] + c['output_middle_planet_carrier_width'] - c['sun_spacer_width']
  c['output_step_width'] = c['output_rear_planet_carrier_width'] + c['output_middle_planet_carrier_width'] + c['output_front_planet_carrier_width']
  # gearring_holder z-dimension
  c['gearring_holder_width'] = c['input_slack'] + (c['step_nb']-1)*(c['step_width']+c['step_slack']) + c['output_step_width'] - c['output_cover_width']
  # hexagon_hole_diameter
  c['hexagon_hole_radius'] = c['hexagon_hole_diameter']/2.0
  if(c['hexagon_hole_radius']<c['sun_axle_radius']):
    print("ERR472: Error, hexagon_hole_radius {:0.3f} is smaller than sun_axle_radius {:0.3f}".format(c['hexagon_hole_radius'], c['sun_axle_radius']))
    sys.exit(2)
  if(c['hexagon_length']<c['hexagon_hole_diameter']+radian_epsilon):
    print("ERR475: Error, hexagon_length {:0.3f} must be bigger than hexagon_hole_diameter {:0.3f}".format(c['hexagon_length'], c['hexagon_hole_diameter']))
    sys.exit(2)
  c['hexagon_angle'] = math.pi/6
  c['hexagon_radius'] = c['hexagon_length']/2.0/math.cos(c['hexagon_angle'])
  if(c['hexagon_radius']>c['planet_carrier_external_radius']-radian_epsilon):
    print("ERR480: Error, hexagon_length {:0.3f} is too big compare to planet_carrier_external_diameter {:0.3f}".format(c['hexagon_length'], c['planet_carrier_external_diameter']))
    sys.exit(2)
  # hexagon_smooth_radius
  if(c['hexagon_smooth_radius']<c['cnc_router_bit_radius']):
    c['hexagon_smooth_radius'] = c['cnc_router_bit_radius']
  if(c['hexagon_smooth_radius']>c['hexagon_length']/2.0-radian_epsilon):
    print("ERR486: Error, hexagon_smooth_radius {:0.3f} is too big compare to hexagon_length {:0.3f}".format(c['hexagon_smooth_radius'], c['hexagon_length']))
    sys.exit(2)
  # output_cover_width, output_holder_width, hexagon_width
  if(c['output_cover_width']>c['output_holder_width']):
    print("ERR490: output_cover_width {:0.3f} is too big compare to output_holder_width {:0.3f}".format(c['output_cover_width'], c['output_holder_width']))
    sys.exit(2)
  c['output_cover_depth'] = c['hexagon_width'] - (c['output_holder_width'] - c['output_cover_width'])
  if(c['output_cover_depth']<0):
    print("ERR494: Error, output_cover_depth {:0.3f} < 0. output_cover_width{:0.3f} or hexagon_width {:0.3f} too small or output_holder_width {:0.3f} too big".format(c['output_cover_depth'], c['output_cover_width'], c['hexagon_width'], c['output_holder_width']))
    sys.exit(2)
  if(c['output_cover_depth']>c['output_cover_width']):
    print("ERR497: Error, output_cover_depth {:0.3f} is too big compare to output_cover_width {:0.3f}".format(c['output_cover_depth'], c['output_cover_width']))
    sys.exit(2)
  if(c['output_cover_depth']>c['input_slack']):
    print("ERR500: Error, input_slack {:0.3f} is too small compare to output_cover_depth {:0.3f}".format(c['input_slack'], c['output_cover_depth']))
    sys.exit(2)
  # output_cover_radius_slack
  c['holder_radius'] = i_gr.get_constraint()['holder_radius']
  if(c['planet_carrier_external_radius']+c['output_cover_radius_slack']>c['holder_radius']-radian_epsilon):
    print("ERR508: Error, output_cover_radius_slack {:0.3f} is too big compare to planet_carrier_external_radius {:0.3f} and holder_radius {:0.3f}".format(c['output_cover_radius_slack'], c['planet_carrier_external_radius'], c['holder_radius']))
    sys.exit(2)
  # output_axle_holder
  c['output_axle_radius'] = c['output_axle_diameter']/2.0
  if(c['output_axle_radius']<radian_epsilon):
    print("ERR513: Error, output_axle_diameter {:0.3f} is too small".format(c['output_axle_diameter']))
    sys.exit(2)
  if(c['axle_holder_D']<c['output_axle_diameter']-radian_epsilon):
    print("ERR516: Error, axle_holder_D {:0.3f} is too small compare to output_axle_diameter {:0.3f}".format(c['axle_holder_D'], c['output_axle_diameter']))
    sys.exit(2)
  if(c['axle_holder_D']/2.0+c['axle_holder_B']>c['holder_radius']):
    print("ERR519: Error, axle_holder_D {:0.3f} or axle_holder_B {:0.3f} are too big compare to holder_radius {:0.3f}".format(c['axle_holder_D'], c['axle_holder_B'], c['holder_radius']))
    sys.exit(2)
  # input_axle_diameter
  c['input_axle_radius'] = c['input_axle_diameter']/2.0
  if(c['input_axle_radius']>c['sun_axle_radius']):
    print("ERR521: Error, input_axle_radius {:0.3f} is too big compare to sun_axle_radius {:0.3f}".format(c['input_axle_radius'], c['sun_axle_radius']))
    sys.exit(2)
  # input_sun_width
  if(c['input_sun_width']<c['sun_width']):
    print("ERR525: Error, input_sun_width {:0.3f} is too small compare to sun_width {:0.3f}".format(c['input_sun_width'], c['sun_width']))
    sys.exit(2)
  # motor_holder
  c['motor_shape_rectangle_ncircle'] = True
  if(c['motor_y_width']==0):
    c['motor_shape_rectangle_ncircle'] = False
  if(c['motor_x_width']<c['gear_module']*(c['sun_gear_tooth_nb']+2)):
    print("WARN532: Warning, motor_x_width {:0.3f} is small compare to the sun-gear".format(c['motor_x_width']))
  if(c['motor_shape_rectangle_ncircle']):
    if(c['motor_y_width']<c['gear_module']*(c['sun_gear_tooth_nb']+2)):
      print("WARN535: Warning, motor_y_width {:0.3f} is small compare to the sun-gear".format(c['motor_y_width']))
  motor_xy_width_max = max(c['motor_x_width'], c['motor_y_width'])
  if((motor_xy_width_max/2.0+c['motor_holder_E']+c['motor_holder_B'])>c['holder_radius']):
    print("ERR541: Error, motor_holder_E {:0.3f} or motor_holder_B {:0.3f} are too big compare to holder_radius {:0.3f}".format(c['motor_holder_E'], c['motor_holder_B'], c['holder_radius']))
    sys.exit(2)
  motor_xy_width_min = c['motor_x_width']
  if(c['motor_shape_rectangle_ncircle']):
    motor_xy_width_min = min(c['motor_x_width'], c['motor_y_width'])
  if(c['motor_holder_leg_width']>motor_xy_width_min/4.0):
    print("ERR545: Error, motor_holder_leg_width {:0.3f} is too big compare to motor_xy_width_min {:0.3f}".format(c['motor_holder_leg_width'], motor_xy_width_min))
    sys.exit(2)
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


