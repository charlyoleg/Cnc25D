# planet_carrier.py
# generates a planet_carrier to be used by the low_torque_transmission  and high_torque_transmission.
# created by charlyoleg on 2014/03/13
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
planet_carrier.py is a parametric sub-design for low_torque_transmission and high_torque_transmission.
As every Cnc25D designs, you can view the 2D-figures in a Tk-window, generate the SVG, DXF and Brep files.
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
#import gearring
#import gearwheel
#import gear_profile # to get the high-level parameter to find the angle position
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
  r_parser.add_argument('--z31_planet_gear_tooth_nb','--z31pgn', action='store', type=int, default=31,
    help="Set the number of gear-teeth of the input planet-gear. Default: 31")
  r_parser.add_argument('--z32_planet_gear_tooth_nb','--z32pgn', action='store', type=int, default=0,
    help="Set the number of gear-teeth of the output planet-gear. If set to 0, z31 is used. Default: 0")
  r_parser.add_argument('--planet_nb','--pn', action='store', type=int, default=0,
    help="Set the number of planets. If equal to zero, the maximum possible number of planets is set. Default: 0")
  ### gear
  r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=1.0,
    help="Set the module of the sun, planet and annulus gear. Default: 1.0")
  ### sun-gear
  r_parser.add_argument('--sun_spacer_width','--ssw', action='store', type=float, default=0.5,
    help="Set the width (z-size) of the sun-spacer ring. If set to 0.0, no sun-spacer ring is created. Default: 0.5")
  ### planet-gear
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
  ### first step z-dimension
  r_parser.add_argument('--planet_width','--pw', action='store', type=float, default=5.0,
    help="Set the z-size of the planet gearwheel. Default: 5.0")
  r_parser.add_argument('--front_planet_carrier_width','--fpcw', action='store', type=float, default=2.0,
    help="Set the z-size of the front-planet-carrier. Default: 2.0")
  r_parser.add_argument('--rear_planet_carrier_width','--rpcw', action='store', type=float, default=2.0,
    help="Set the z-size of the rear-planet-carrier. Default: 2.0")
  r_parser.add_argument('--planet_slack','--ps', action='store', type=float, default=0.2,
    help="Set the slack thickness between planet-gearwheel and planet-carrier. Default: 0.2")
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
  c['radian_epsilon'] = radian_epsilon
  # planet number
  planet_size_angle = 2*math.asin(float(c['z31_planet_gear_tooth_nb']+2)/(c['z31_planet_gear_tooth_nb']+c['sun_gear_tooth_nb']))
  planet_number_max_securoty_coef = 1.0
  c['planet_number_max'] = int(2*math.pi/(planet_size_angle*planet_number_max_securoty_coef))
  #print("dbg244: planet_number_max:", c['planet_number_max'])
  if(c['planet_nb']==0):
    c['planet_nb'] = c['planet_number_max']
  cnc25d_api.check(c, "ERR316", "c['planet_nb']<=c['planet_number_max']")
  cnc25d_api.check(c, "ERR317", "c['planet_nb']>=1")
  # epicyclic fitting
  #epicyclic_tooth_check = (2*(c['sun_gear_tooth_nb'] + c['z31_planet_gear_tooth_nb'])) % c['planet_nb']
  #if(epicyclic_tooth_check != 0):
  #  print("WARN243: Warning, not respected epicyclic-gearing-tooth-nb relation: 2*(sun_gear_tooth_nb {:d} + z31_planet_gear_tooth_nb {:d}) % planet_nb {:d} == {:d} (should be 0)".format(c['sun_gear_tooth_nb'], c['z31_planet_gear_tooth_nb'], c['planet_nb'], epicyclic_tooth_check))
  c['planet_angle_inc'] = 2*math.pi/c['planet_nb']
  c['planet_circle_radius'] = (c['sun_gear_tooth_nb'] + c['z31_planet_gear_tooth_nb'])*c['gear_module']/2.0
  c['planet_angle_position'] = []
  c['planet_x_position'] = []
  c['planet_y_position'] = []
  for i in range(c['planet_nb']):
    c['planet_angle_position'].append(c['planet_carrier_angle']+i*c['planet_angle_inc'])
    c['planet_x_position'].append(0.0 + c['planet_circle_radius']*math.cos(c['planet_angle_position'][i]))
    c['planet_y_position'].append(0.0 + c['planet_circle_radius']*math.sin(c['planet_angle_position'][i]))
  annulus_planet_c = gp_ap_c.copy()
  i_gp = gear_profile.gear_profile(annulus_planet_c)
  c['planet_oriantation_angles'] = [] # gear_initial_angle for planets
  for i in range(c['planet_nb']):
    annulus_planet_c['second_gear_position_angle'] = c['planet_angle_position'][i] + math.pi
    i_gp.apply_external_constraint(annulus_planet_c)
    #i_gp.run_simulation('gear_profile_simulation_A') # dbg
    c['planet_oriantation_angles'].append(i_gp.get_constraint()['second_positive_initial_angle'])
  planet_sun_c = gp_ps_c.copy()
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
    angle_diff = math.fmod(c['sun_oriantation_angles'][i]-c['sun_oriantation_angles'][0]+11*sun_half_tooth_angle, 2*sun_half_tooth_angle)-sun_half_tooth_angle # might habe issue when the difference is negative
    if(abs(angle_diff)>radian_epsilon):
      print("ERR293: Error, {:d}-sun_oriantation_angles {:0.3f} is different from 0-sun_oriantation_angles {:0.3f}".format(i, c['sun_oriantation_angles'][i], c['sun_oriantation_angles'][0]))
      #print("dbg306: sun_half_tooth_angle:", sun_half_tooth_angle, 2*sun_half_tooth_angle, i_gp.get_constraint()['second_pi_module_angle'])
      #print("dbg307: sun_oriantation_angles:", c['sun_oriantation_angles'])
      #print("dbg369: angle_diff:", angle_diff)
      #print("dbg308: planet_oriantation_angles:", c['planet_oriantation_angles'])
      sys.exit(2)
  c['sun_oriantation_angle'] = c['sun_oriantation_angles'][0]
  # sun axle and spacer
  c['sun_axle_radius'] = c['sun_axle_diameter']/2.0
  c['sun_gear_hollow_diameter'] = c['gear_module']*(c['sun_gear_tooth_nb']-3)
  cnc25d_api.check(c, "ERR372", "c['sun_axle_diameter']+2*c['sun_spacer_length']<=c['sun_gear_hollow_diameter']")
  # planet axle and spacer
  c['planet_axle_radius'] = c['planet_axle_diameter']/2.0
  c['planet_gear_hollow_diameter'] = c['gear_module']*(c['z31_planet_gear_tooth_nb']-3)
  cnc25d_api.check(c, "ERR376", "c['planet_axle_diameter']+2*c['planet_spacer_length']<=c['planet_gear_hollow_diameter']")
  # planet_carrier axle and spacer
  c['planet_carrier_axle_radius'] = c['planet_carrier_axle_diameter']/2.0
  cnc25d_api.check(c, "ERR379", "c['planet_carrier_axle_diameter']+2*c['planet_carrier_spacer_length']<=c['planet_gear_hollow_diameter']")
  cnc25d_api.check(c, "ERR380", "c['planet_carrier_axle_holder_diameter']<=c['planet_gear_hollow_diameter']")
  cnc25d_api.check(c, "ERR381", "c['planet_axle_diameter']+2*c['planet_spacer_length']<=c['planet_carrier_axle_holder_diameter']")
  c['planet_carrier_axle_holder_radius'] = c['planet_carrier_axle_holder_diameter']/2.0
  # planet_carrier_external_diameter
  c['planet_carrier_external_diameter_max'] = c['gear_module']*(c['annulus_gear_tooth_nb']-4)
  if(c['planet_carrier_external_diameter']==0):
    c['planet_carrier_external_diameter'] = c['planet_carrier_external_diameter_max']
  c['planet_carrier_external_radius'] = c['planet_carrier_external_diameter']/2.0
  cnc25d_api.check(c, "ERR388", "c['planet_carrier_external_diameter']<=c['planet_carrier_external_diameter_max']")
  cnc25d_api.check(c, "ERR389", "c['planet_carrier_external_radius']>c['planet_circle_radius']-c['planet_carrier_axle_holder_radius']+c['radian_epsilon']")
  # planet_carrier_internal_diameter
  c['planet_carrier_internal_diameter_min'] = c['gear_module']*(c['sun_gear_tooth_nb']+4)
  c['planet_carrier_internal_diameter_default'] = 2*c['planet_circle_radius']
  if(c['planet_carrier_internal_diameter']==0):
    c['planet_carrier_internal_diameter'] = c['planet_carrier_internal_diameter_default']
  c['planet_carrier_internal_radius'] = c['planet_carrier_internal_diameter']/2.0
  cnc25d_api.check(c, "ERR396", "c['planet_carrier_internal_diameter']>=c['planet_carrier_internal_diameter_min']")
  cnc25d_api.check(c, "ERR397", "c['planet_carrier_internal_diameter']<=c['planet_carrier_external_diameter']-c['radian_epsilon']")
  # planet_carrier_rear_smooth_radius
  if(c['planet_carrier_rear_smooth_radius']<c['cnc_router_bit_radius']):
    c['planet_carrier_rear_smooth_radius'] = c['cnc_router_bit_radius']
  cnc25d_api.check(c, "ERR401", "c['planet_carrier_rear_smooth_radius']<=min(c['planet_carrier_internal_radius'], c['planet_carrier_axle_holder_radius'])")
  # planet_carrier_middle_clearance_diameter
  c['planet_carrier_middle_clearance_diameter_min'] = c['gear_module']*(c['z31_planet_gear_tooth_nb']+4)
  if(c['planet_carrier_middle_clearance_diameter']==0):
    c['planet_carrier_middle_clearance_diameter'] = c['planet_carrier_middle_clearance_diameter_min']
  c['planet_carrier_middle_clearance_radius'] = c['planet_carrier_middle_clearance_diameter']/2.0
  cnc25d_api.check(c, "ERR407", "c['planet_carrier_middle_clearance_diameter']>=c['planet_carrier_middle_clearance_diameter_min']")
  # planet_carrier_middle_smooth_radius
  if(c['planet_carrier_middle_smooth_radius']<c['cnc_router_bit_radius']):
    c['planet_carrier_middle_smooth_radius'] = c['cnc_router_bit_radius']
  # pre-calculations for middle-planet_carrier
  lOA = c['planet_circle_radius']
  lAG = c['planet_carrier_middle_clearance_radius']
  lOG = c['planet_carrier_external_radius']
  lOH = c['planet_carrier_internal_radius']
  cos_OAG = float(lOA**2+lAG**2-lOG**2)/(2*lOA*lAG)
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
    #print("dbg401: cos_DAE", cos_DAE)
    aDAE = math.acos(cos_DAE)
    aOAD = math.pi/2 - c['planet_angle_inc']/2.0
    aOAF = aOAD + aDAE
    if(aOAG<aOAF):
      print("ERR435: Error, planet_carrier_external_radius {:0.3f} is too small compare to planet_carrier_middle_clearance_radius {:0.3f} or planet_carrier_middle_smooth_radius {:0.3f}".format(c['planet_carrier_external_radius'], c['planet_carrier_middle_clearance_radius'], c['planet_carrier_middle_smooth_radius']))
      sys.exit(2)
    elif(aOAH<aOAF):
      c['middle_planet_carrier_aOAH'] = aOAF # a bit more to ensure a good cnc_cut
      lDE = math.sqrt(lAE**2-lAD**2)
      lOD = math.sqrt(lOA**2-lAD**2)
      c['middle_planet_carrier_internal_radius'] = lOD + lDE
  # pre-calculations for rear-planet_carrier
  c['rear_planet_carrier_external_intersection'] = False
  if(c['planet_circle_radius']+0.8*c['planet_carrier_axle_holder_radius']>c['planet_carrier_external_radius']): # 0.8 is arbitrary and ensure a good cnc_cut
    c['rear_planet_carrier_external_intersection'] = True
    lOA = c['planet_circle_radius']
    lAG = c['planet_carrier_axle_holder_radius']
    lOG = c['planet_carrier_external_radius']
    cos_AOG = float(lOA**2+lOG**2-lAG**2)/(2*lOA*lOG)
    aAOG = math.acos(cos_AOG)
    c['rear_planet_carrier_external_intersection_angle'] = aAOG
  c['rear_planet_carrier_internal_intersection'] = False
  if(c['planet_circle_radius']-0.8*c['planet_carrier_axle_holder_radius']<c['planet_carrier_internal_radius']): # 0.8 is arbitrary and ensure a good cnc_cut
    c['rear_planet_carrier_internal_intersection'] = True
    lOA = c['planet_circle_radius']
    lAG = c['planet_carrier_axle_holder_radius']
    lOG = c['planet_carrier_internal_radius']
    cos_AOG = float(lOA**2+lOG**2-lAG**2)/(2*lOA*lOG)
    aAOG = math.acos(cos_AOG)
    c['rear_planet_carrier_internal_intersection_angle'] = aAOG
  # planet_carrier_fitting_square
  c['planet_carrier_fitting_square'] = False
  c['planet_carrier_fitting_hole_ref'] = c['planet_carrier_external_radius']
  if((c['planet_carrier_fitting_square_l1']!=0)and(c['planet_carrier_fitting_square_l2']!=0)):
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
      r['ref_radius'] = lOC
      return(r)
    middle_fs = sub_fitting_square(c['planet_carrier_external_radius'],
                  c['planet_carrier_fitting_square_l1'], c['planet_carrier_fitting_square_l2'])
    c['middle_planet_carrier_fitting_square_ext_angle'] = middle_fs['ext_angle']
    c['middle_planet_carrier_fitting_square_int_angle'] = middle_fs['int_angle']
    c['middle_planet_carrier_fitting_square_int_radius'] = middle_fs['int_radius']
    if(middle_fs['ref_radius']<c['middle_planet_carrier_internal_radius']):
      print("ERR491: Error, planet_carrier_fitting_square_l2 {:0.3f} is too big".format(c['planet_carrier_fitting_square_l2']))
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
  cnc25d_api.check(c, "ERR509", "c['step_nb']>=1")
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
  cnc25d_api.check(c, "ERR522", "c['hexagon_hole_radius']>=c['sun_axle_radius']")
  cnc25d_api.check(c, "ERR523", "c['hexagon_length']>c['hexagon_hole_diameter']+c['radian_epsilon']")
  c['hexagon_angle'] = math.pi/6
  c['hexagon_radius'] = c['hexagon_length']/2.0/math.cos(c['hexagon_angle'])
  cnc25d_api.check(c, "ERR526", "c['hexagon_radius']<c['planet_carrier_external_radius']-c['radian_epsilon']")
  # hexagon_smooth_radius
  if(c['hexagon_smooth_radius']<c['cnc_router_bit_radius']):
    c['hexagon_smooth_radius'] = c['cnc_router_bit_radius']
  cnc25d_api.check(c, "ERR530", "c['hexagon_smooth_radius']<c['hexagon_length']/2.0-c['radian_epsilon']")
  # output_cover_width, output_holder_width, hexagon_width
  c['output_holder_width2'] = c['output_holder_width'] + c['output_cover_width']
  c['output_cover_depth'] = c['hexagon_width'] - c['output_holder_width']
  cnc25d_api.check(c, "ERR534", "c['output_cover_depth']>=0")
  cnc25d_api.check(c, "ERR535", "c['output_cover_depth']<=c['output_cover_width']")
  cnc25d_api.check(c, "ERR536", "c['output_cover_depth']<=c['input_slack']")
  # output_cover_radius_slack
  c['holder_radius'] = i_gr.get_constraint()['holder_radius']
  c['output_cover_radius'] = c['planet_carrier_external_radius']+c['output_cover_radius_slack']
  cnc25d_api.check(c, "ERR540", "c['output_cover_radius']<c['holder_radius']-c['radian_epsilon']")
  c['output_holder_radius'] = c['holder_radius'] - c['output_holder_thickness']
  cnc25d_api.check(c, "ERR542", "c['output_holder_radius']>=c['output_cover_radius']")
  c['output_holder_crenel_nb_default'] = int((c['holder_crenel_number']+1)/2)+1
  if(c['output_holder_crenel_nb']==0):
    c['output_holder_crenel_nb'] = c['output_holder_crenel_nb_default']
  # output_axle_holder
  c['output_axle_radius'] = c['output_axle_diameter']/2.0
  cnc25d_api.check(c, "ERR548", "c['output_axle_radius']>c['radian_epsilon']")
  cnc25d_api.check(c, "ERR549", "c['axle_holder_D']>c['output_axle_diameter']-c['radian_epsilon']")
  cnc25d_api.check(c, "ERR550", "c['axle_holder_D']/2.0+c['axle_holder_B']<=c['holder_radius']")
  c['output_axle_cylinder_width'] = c['axle_holder_A'] + c['axle_holder_C']
  c['output_axle_cylinder_thickness'] = c['axle_holder_D']/2.0 - c['output_axle_radius']
  c['axle_holder_leg_x'] = c['axle_holder_A'] + c['axle_holder_C']
  c['axle_holder_leg_y'] = c['axle_holder_B'] + c['output_axle_cylinder_thickness']
  c['axle_holder_leg_width'] = c['axle_holder_D']/4.0
  # input_axle_diameter
  c['input_axle_radius'] = c['input_axle_diameter']/2.0
  cnc25d_api.check(c, "ERR558", "c['input_axle_radius']<=c['sun_axle_radius']")
  # input_sun_width
  c['input_sun_width_min'] = c['sun_width']
  if(c['input_sun_width']==0):
    c['input_sun_width'] = c['input_sun_width_min']
  cnc25d_api.check(c, "ERR563", "c['input_sun_width']>=c['input_sun_width_min']")
  # motor_holder
  c['motor_shape_rectangle_ncircle'] = True
  if(c['motor_y_width']==0):
    c['motor_shape_rectangle_ncircle'] = False
  if(c['motor_x_width']<c['gear_module']*(c['sun_gear_tooth_nb']+2)):
    print("WARN532: Warning, motor_x_width {:0.3f} is small compare to the sun-gear".format(c['motor_x_width']))
  if(c['motor_shape_rectangle_ncircle']):
    if(c['motor_y_width']<c['gear_module']*(c['sun_gear_tooth_nb']+2)):
      print("WARN535: Warning, motor_y_width {:0.3f} is small compare to the sun-gear".format(c['motor_y_width']))
  c['motor_xy_width_max'] = max(c['motor_x_width'], c['motor_y_width'])
  cnc25d_api.check(c, "ERR574", "(c['motor_xy_width_max']/2.0+c['motor_holder_E']+c['motor_holder_B'])<=c['holder_radius']")
  c['motor_xy_width_min'] = c['motor_x_width']
  if(c['motor_shape_rectangle_ncircle']):
    c['motor_xy_width_min'] = min(c['motor_x_width'], c['motor_y_width'])
  cnc25d_api.check(c, "ERR578", "c['motor_holder_leg_width']<=c['motor_xy_width_min']/4.0")
  c['motor_holder_leg_x'] = c['motor_holder_A'] + c['motor_holder_C'] + c['motor_holder_D']
  c['motor_holder_leg_y'] = c['motor_holder_B'] + c['motor_holder_E']
  #
  c['epicyclic_gearing_ratio'] = float(c['sun_gear_tooth_nb'])/(c['sun_gear_tooth_nb']+c['annulus_gear_tooth_nb'])
  c['ltt_ratio'] = c['epicyclic_gearing_ratio']**c['step_nb']
  # part quantity
  c['planet_gear_q'] = (c['step_nb']-1)*c['planet_nb']
  c['output_planet_gear_q'] = c['planet_nb']
  c['rear_planet_carrier_q'] = c['step_nb']-1
  c['front_planet_carrier_q'] = max(c['step_nb']-2, 0)
  c['output_front_planet_carrier_q'] = 1 if(c['step_nb']>1) else 0
  c['output_rear_planet_carrier_q'] = 1
  c['output_shaft_q'] = 1
  c['input_sun_gear_q'] = 1
  c['motor_holder_q'] = 1
  c['gearring_holder_q'] = 1
  c['output_holder_q'] = 1
  c['output_axle_holder_q'] = 1
  #
  c['gr_c'] = gr_c.copy()
  c['gp_ap_c'] = gp_ap_c.copy()
  c['gp_ps_c'] = gp_ps_c.copy()
  c['gp_s_c'] = gp_s_c.copy()
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
  rfc = cnc25d_api.Figure_Collection("ltt") # return_figure_collection
  # gearring_holder
  fig_gearring_holder = cnc25d_api.Figure('gearring_holder')
  i_gr = gearring.gearring()
  i_gr.apply_external_constraint(c['gr_c'])
  fig_gearring_holder.merge_figure(i_gr.get_A_figure('gearring_fig'), extrudable = True)
  fig_gearring_holder.set_height(c['gearring_holder_width'])
  rfc.add_figure(fig_gearring_holder)
  # planet_gear
  fig_planet_gear = cnc25d_api.Figure('planet_gear')
  gwp_c = c['gp_ps_c'].copy()
  gwp_c['axle_type'] = 'circle'
  gwp_c['axle_x_width'] = c['planet_axle_diameter']
  i_gwp = gearwheel.gearwheel()
  i_gwp.apply_external_constraint(gwp_c)
  fig_planet_gear.merge_figure(i_gwp.get_A_figure('gearwheel_fig'), extrudable = True)
  fig_planet_gear.set_height(c['planet_width'])
  rfc.add_figure(fig_planet_gear)
  # planet_spacer
  fig_planet_spacer = cnc25d_api.Figure('planet_spacer')
  fig_planet_spacer.add_external_outline(cnc25d_api.Circle_Outline("ps_ext_circle", c['planet_axle_radius']+c['planet_spacer_length'], 0.0, 0.0))
  fig_planet_spacer.add_hole_outline(cnc25d_api.Circle_Outline("ps_int_circle", c['planet_axle_radius'], 0.0, 0.0))
  fig_planet_spacer.set_height(c['planet_spacer_width'])
  rfc.add_figure(fig_planet_spacer)
  # sun_gear
  fig_sun_gear = cnc25d_api.Figure('sun_gear')
  gws_c = c['gp_s_c'].copy()
  gws_c['axle_type'] = 'circle'
  gws_c['axle_x_width'] = c['sun_axle_diameter']
  i_gws = gearwheel.gearwheel()
  i_gws.apply_external_constraint(gws_c)
  fig_sun_gear.merge_figure(i_gws.get_A_figure('gearwheel_fig'), extrudable = True)
  fig_sun_gear.set_height(c['sun_width'])
  rfc.add_figure(fig_sun_gear)
  # sun_spacer
  fig_sun_spacer = cnc25d_api.Figure('sun_spacer')
  fig_sun_spacer.add_external_outline(cnc25d_api.Circle_Outline("ss_ext_circle", c['sun_axle_radius']+c['sun_spacer_length'], 0.0, 0.0))
  fig_sun_spacer.add_hole_outline(cnc25d_api.Circle_Outline("ss_int_circle", c['sun_axle_radius'], 0.0, 0.0))
  fig_sun_spacer.set_height(c['planet_spacer_width'])
  rfc.add_figure(fig_sun_spacer)
  # planet_carrier_middle_holes
  fig_planet_carrier_holes = cnc25d_api.Figure('planet_carrier_holes')
  planet_carrier_middle_holes = []
  for i in range(c['planet_nb']):
    planet_carrier_middle_holes.append(cnc25d_api.Figure('planet_carrier_middle_hole_{:d}'.format(i)))
    pca = c['planet_angle_position'][i] + c['planet_angle_inc']/2.0 # planet_carrier_angle reference
    if(c['planet_carrier_fitting_hole_radius']>0): # create holes
      a = pca - c['planet_carrier_fitting_hole_position_angle']
      planet_carrier_middle_holes[i].add_undefine_outline(cnc25d_api.Circle_Outline('h1', c['planet_carrier_fitting_hole_radius'], 0.0+c['planet_carrier_fitting_hole_position_radius']*math.cos(a), 0.0+c['planet_carrier_fitting_hole_position_radius']*math.sin(a)))
      if(c['planet_carrier_fitting_double_hole_distance']>0): # create two holes
        a = pca + c['planet_carrier_fitting_hole_position_angle']
        planet_carrier_middle_holes[i].add_undefine_outline(cnc25d_api.Circle_Outline('h2', c['planet_carrier_fitting_hole_radius'], 0.0+c['planet_carrier_fitting_hole_position_radius']*math.cos(a), 0.0+c['planet_carrier_fitting_hole_position_radius']*math.sin(a)))
    fig_planet_carrier_holes.merge_figure(planet_carrier_middle_holes[i])
  # planet_carrier_middles
  planet_carrier_middle_figs = []
  fig_planet_carrier_middle_overview = cnc25d_api.Figure("planet_carrier_middle_overview")
  for i in range(c['planet_nb']):
    pca = c['planet_angle_position'][i] + c['planet_angle_inc']/2.0 # planet_carrier_angle reference
    ap1c = c['planet_angle_position'][i] # position angle of the previous planet center
    ap2c = c['planet_angle_position'][i]+c['planet_angle_inc'] # position angle of the following planet center
    p1x = 0.0 + c['planet_circle_radius']*math.cos(ap1c) # previous planet center coordinates
    p1y = 0.0 + c['planet_circle_radius']*math.sin(ap1c)
    p2x = 0.0 + c['planet_circle_radius']*math.cos(ap2c) # following planet center coordinates
    p2y = 0.0 + c['planet_circle_radius']*math.sin(ap2c)
    pcmcr = c['planet_carrier_middle_clearance_radius'] # alias
    mpcir = c['middle_planet_carrier_internal_radius']
    pcer = c['planet_carrier_external_radius']
    pcmsr = c['planet_carrier_middle_smooth_radius']
    aOAG = c['middle_planet_carrier_aOAG']
    aOAH = c['middle_planet_carrier_aOAH']
    a1i = ap1c + math.pi - aOAH # angle planet-1 to internal circle
    a1m = ap1c + math.pi - (aOAH + (aOAG-aOAH)/2.0) # angle planet-1 to middle of internal-external circle
    a1e = ap1c + math.pi - aOAG # angle planet-1 to external circle
    a2i = ap2c + math.pi + aOAH # angle planet-2 to internal circle
    a2m = ap2c + math.pi + (aOAH + (aOAG-aOAH)/2.0) # angle planet-2 to middle of internal-external circle
    a2e = ap2c + math.pi + aOAG # angle planet-2 to external circle
    ol = cnc25d_api.Arc_Line_Outline('planet_carrier_middle_ext_ol')
    ol.add_StartPoint(p2x+pcmcr*math.cos(a2i), p2y+pcmcr*math.sin(a2i), rbr=pcmsr) # start point: planet-2 clearance-circle intersection with internal-circle. Going CCW
    ol.add_ArcThrTo(0.0+mpcir*math.cos(pca), 0.0+mpcir*math.sin(pca), p1x+pcmcr*math.cos(a1i), p1y+pcmcr*math.sin(a1i), rbr=pcmsr) # internal circle arc
    ol.add_ArcThrTo(p1x+pcmcr*math.cos(a1m), p1y+pcmcr*math.sin(a1m), p1x+pcmcr*math.cos(a1e), p1y+pcmcr*math.sin(a1e), rbr=pcmsr) # planet-1 clearance arc
    ol.add_ArcThrTo(0.0+pcer*math.cos(pca), 0.0+pcer*math.sin(pca), p2x+pcmcr*math.cos(a2e), p2y+pcmcr*math.sin(a2e), rbr=pcmsr) # external circle arc
    ol.close_with_ArcThr(p2x+pcmcr*math.cos(a2m), p2y+pcmcr*math.sin(a2m)) # planet-2 clearance arc
    #print("dbg705: ol:", ol.ol)
    #cnc25d_api.figure_simple_display([ol.cnc_cut()], [ol.ideal()], "debug")
    #
    planet_carrier_middle_figs.append(cnc25d_api.Figure("planet_carrier_middle_{:d}".format(i)))
    planet_carrier_middle_figs[i].add_external_outline(ol)
    planet_carrier_middle_figs[i].merge_figure(planet_carrier_middle_holes[i], extrudable = True)
    planet_carrier_middle_figs[i].set_height(c['middle_planet_carrier_width'])
    fig_planet_carrier_middle_overview.merge_figure(planet_carrier_middle_figs[i])
    #
    rfc.add_figure(planet_carrier_middle_figs[i])
  # epicyclic_middle_overview
  fig_epicyclic_middle_overview = cnc25d_api.Figure("epicyclic_middle_overview")
  fig_epicyclic_middle_overview.merge_figure(fig_gearring_holder)
  for i in range(c['planet_nb']):
    fig_epicyclic_middle_overview.merge_figure(fig_planet_gear.rotate(0.0, 0.0, c['planet_oriantation_angles'][i]).translate(c['planet_x_position'][i], c['planet_y_position'][i]))
    fig_epicyclic_middle_overview.merge_figure(fig_planet_spacer.rotate(0.0, 0.0, c['planet_oriantation_angles'][i]).translate(c['planet_x_position'][i], c['planet_y_position'][i]))
  fig_epicyclic_middle_overview.merge_figure(fig_sun_gear.rotate(0.0, 0.0, c['sun_oriantation_angle']))
  fig_epicyclic_middle_overview.merge_figure(fig_sun_spacer.rotate(0.0, 0.0, c['sun_oriantation_angle']))
  fig_epicyclic_middle_overview.merge_figure(fig_planet_carrier_middle_overview)
  rfc.add_figure(fig_epicyclic_middle_overview)
  # rear_planet_carrier
  fig_rear_planet_carrier = cnc25d_api.Figure("planet_carrier_rear")
  if(c['rear_planet_carrier_external_intersection']):
    eol = cnc25d_api.Arc_Line_Outline("rear_planet_carrier_exl_ol") # external outline of rear_planet_carrier
    le = c['planet_carrier_external_radius']
    lh = c['planet_circle_radius'] + c['planet_carrier_axle_holder_radius']
    a1 = c['rear_planet_carrier_external_intersection_angle']
    a2 = c['planet_angle_inc']/2.0
    a3 = c['planet_angle_inc'] - c['rear_planet_carrier_external_intersection_angle']
    a4 = c['planet_angle_inc']
    a5 = c['planet_angle_inc'] + c['rear_planet_carrier_external_intersection_angle']
    sr = c['planet_carrier_rear_smooth_radius']
    ar = c['planet_angle_position'][0]
    eol.add_StartPoint(0.0+le*math.cos(ar+a1), 0.0+le*math.sin(ar+a1), rbr=sr) # first point of the outline with intersections
    for i in range(c['planet_nb']):
      ar = c['planet_angle_position'][i] # planet_carrier_angle reference
      eol.add_ArcThrTo(0.0+le*math.cos(ar+a2), 0.0+le*math.sin(ar+a2), 0.0+le*math.cos(ar+a3), 0.0+le*math.sin(ar+a3), rbr=sr)
      eol.add_ArcThrTo(0.0+lh*math.cos(ar+a4), 0.0+lh*math.sin(ar+a4), 0.0+le*math.cos(ar+a5), 0.0+le*math.sin(ar+a5), rbr=sr)
    eol.close_insurance()
  else:
    eol = cnc25d_api.Circle_Outline("rear_planet_carrier_exl_ol", c['planet_carrier_external_radius'], 0.0, 0.0)
  fig_rear_planet_carrier.add_external_outline(eol)
  if(c['rear_planet_carrier_internal_intersection']):
    iol = cnc25d_api.Arc_Line_Outline("rear_planet_carrier_int_ol") # internal outline of rear_planet_carrier
    li = c['planet_carrier_internal_radius']
    lh = c['planet_circle_radius'] - c['planet_carrier_axle_holder_radius']
    a1 = c['rear_planet_carrier_internal_intersection_angle']
    a2 = c['planet_angle_inc']/2.0
    a3 = c['planet_angle_inc'] - c['rear_planet_carrier_internal_intersection_angle']
    a4 = c['planet_angle_inc']
    a5 = c['planet_angle_inc'] + c['rear_planet_carrier_internal_intersection_angle']
    sr = c['planet_carrier_rear_smooth_radius']
    ar = c['planet_angle_position'][0]
    iol.add_StartPoint(0.0+li*math.cos(ar+a1), 0.0+li*math.sin(ar+a1), rbr=sr) # first point of the outline with intersections
    for i in range(c['planet_nb']):
      ar = c['planet_angle_position'][i] # planet_carrier_angle reference
      iol.add_ArcThrTo(0.0+li*math.cos(ar+a2), 0.0+li*math.sin(ar+a2), 0.0+li*math.cos(ar+a3), 0.0+li*math.sin(ar+a3), rbr=sr)
      iol.add_ArcThrTo(0.0+lh*math.cos(ar+a4), 0.0+lh*math.sin(ar+a4), 0.0+li*math.cos(ar+a5), 0.0+li*math.sin(ar+a5), rbr=sr)
    iol.close_insurance()
  else:
    iol = cnc25d_api.Circle_Outline("rear_planet_carrier_int_ol", c['planet_carrier_internal_radius'], 0.0, 0.0)
  fig_rear_planet_carrier.add_hole_outline(iol)
  for i in range(c['planet_nb']):
    fig_rear_planet_carrier.add_hole_outline(cnc25d_api.Circle_Outline("planet_axle_{:d}".format(i), c['planet_carrier_axle_radius'], c['planet_x_position'][i], c['planet_y_position'][i])) # add planet_axle hole
  fig_rear_planet_carrier.merge_figure(fig_planet_carrier_holes, extrudable=True) # rod holes
  #print("dbg790: fig_rear_planet_carrier:", fig_rear_planet_carrier)
  #cnc25d_api.figure_simple_display(fig_rear_planet_carrier.cnc_cut(), fig_rear_planet_carrier.ideal(), "debug")
  fig_rear_planet_carrier.set_height(c['rear_planet_carrier_width'])
  rfc.add_figure(fig_rear_planet_carrier)
  # planet_carrier_spacer
  fig_spacer = cnc25d_api.Figure("planet_carrier_spacer")
  fig_spacer.add_external_outline(cnc25d_api.Circle_Outline("ext", c['planet_carrier_axle_radius']+c['planet_carrier_spacer_length'], 0.0, 0.0))
  fig_spacer.add_hole_outline(cnc25d_api.Circle_Outline("int", c['planet_carrier_axle_radius'], 0.0, 0.0))
  fig_spacer.set_height = c['rear_planet_carrier_spacer_width']
  planet_carrier_spacer_figs = []
  for i in range(c['planet_nb']):
    planet_carrier_spacer_figs.append(cnc25d_api.Figure("planet_carrier_spacer_{:d}".format(i)))
    planet_carrier_spacer_figs[i].merge_figure(fig_spacer.translate(c['planet_x_position'][i], c['planet_y_position'][i]), extrudable=True)
    rfc.add_figure(planet_carrier_spacer_figs[i])
  # planet_carrier_fitting_square
  if(c['planet_carrier_fitting_square']):
    le = c['planet_carrier_external_radius'] # alias
    ae = c['middle_planet_carrier_fitting_square_ext_angle']
    li = c['middle_planet_carrier_fitting_square_int_radius']
    ai = c['middle_planet_carrier_fitting_square_int_angle']
    planet_carrier_fitting_square_figs = []
    for i in range(c['planet_nb']):
      ar = c['planet_angle_position'][i] + c['planet_angle_inc']/2.0
      ol = cnc25d_api.Arc_Line_Outline("planet_carrier_fitting_square_{:d}".format(i))
      ol.add_StartPoint(0.0+le*math.cos(ar-ae), 0.0+le*math.sin(ar-ae), rbr=0)
      ol.add_ArcThrTo(0.0+le*math.cos(ar), 0.0+le*math.sin(ar), 0.0+le*math.cos(ar+ae), 0.0+le*math.sin(ar+ae), rbr=0)
      ol.add_LineTo(0.0+li*math.cos(ar+ai), 0.0+li*math.sin(ar+ai), rbr=0)
      ol.add_LineTo(0.0+li*math.cos(ar-ai), 0.0+li*math.sin(ar-ai), rbr=0)
      ol.close_with_Line() #ol.add_LineTo(0.0+le*math.cos(ar-ae), 0.0+le*math.sin(ar-ae), rbr=0)
      planet_carrier_fitting_square_figs.append(cnc25d_api.Figure('planet_carrier_fitting_square_{:d}'.format(i)))
      planet_carrier_fitting_square_figs[i].add_external_outline(ol)
      planet_carrier_fitting_square_figs[i].set_height(c['front_planet_carrier_width'])
      rfc.add_figure(planet_carrier_fitting_square_figs[i])
  # front_planet_carrier
  fig_front_planet_carrier = cnc25d_api.Figure("planet_carrier_front")
  if(c['planet_carrier_fitting_square']): # todo: integrate the planet_carrier_axle_holder
    ol = cnc25d_api.Arc_Line_Outline("front_planet_carrier_ext_ol")
    le = c['planet_carrier_external_radius'] # alias
    ae = c['front_planet_carrier_fitting_square_ext_angle']
    li = c['front_planet_carrier_fitting_square_int_radius']
    ai = c['front_planet_carrier_fitting_square_int_angle']
    ainc =  c['planet_angle_inc']/2.0
    rbr = c['cnc_router_bit_radius']
    sr = c['cnc_router_bit_radius']
    ar = c['planet_angle_position'][0] + ainc
    ol.add_StartPoint((0.0+le*math.cos(ar-ae), 0.0+le*math.sin(ar-ae), rbr=sr))
    for i in range(c['planet_nb']):
      ar = c['planet_angle_position'][i] + ainc
      ol.add_LineTo((0.0+li*math.cos(ar-ai), 0.0+li*math.sin(ar-ai), rbr=-rbr))
      ol.add_LineTo((0.0+li*math.cos(ar+ai), 0.0+li*math.sin(ar+ai), rbr=-rbr))
      ol.add_LineTo((0.0+le*math.cos(ar+ae), 0.0+le*math.sin(ar+ae), rbr=sr))
      ol.add_ArcThrTo((0.0+le*math.cos(ar+ainc), 0.0+le*math.sin(ar+ainc), 0.0+le*math.cos(ar+2*ainc-ae), 0.0+le*math.sin(ar+2*ainc-ae), rbr=sr))
    ol.close_insurance()
  else:
    ol = cnc25d_api.Circle_Outline("front_planet_carrier_ext_ol", c['planet_carrier_external_radius'], 0.0, 0.0)
  fig_front_planet_carrier.add_external_outline(ol)
  for i in range(c['planet_nb']):
    fig_front_planet_carrier.add_hole_outline(cnc25d_api.Circle_Outline("planet_axle_{:d}".format(i), c['planet_carrier_axle_radius'], c['planet_x_position'][i], c['planet_y_position'][i])) # add planet_axle hole
  fig_front_planet_carrier.add_hole_outline(cnc25d_api.Circle_Outline("sun_axle", c['sun_axle_radius'], 0.0, 0.0)) # add sun_axle hole
  fig_front_planet_carrier.merge_figure(fig_planet_carrier_holes, extrudable=True) # rod holes
  fig_front_planet_carrier.set_height(c['front_planet_carrier_width'])
  rfc.add_figure(fig_front_planet_carrier)
  #print("dbg846: fig_front_planet_carrier:", fig_front_planet_carrier)
  #cnc25d_api.figure_simple_display(fig_front_planet_carrier.cnc_cut(), fig_front_planet_carrier.ideal(), "debug")
  # planet_carrier_overview
  fig_planet_carrier_overview = cnc25d_api.Figure("planet_carrier_overview")
  fig_planet_carrier_overview.merge_figure(fig_gearring_holder)
  fig_planet_carrier_overview.merge_figure(fig_rear_planet_carrier)
  for i in range(c['planet_nb']):
    fig_planet_carrier_overview.merge_figure(planet_carrier_spacer_figs[i])
    fig_planet_carrier_overview.merge_figure(planet_carrier_middle_figs[i])
    fig_planet_carrier_overview.merge_figure(planet_carrier_fitting_square_figs[i])
  fig_planet_carrier_overview.merge_figure(fig_front_planet_carrier)
  fig_planet_carrier_overview.merge_figure(fig_sun_gear)
  fig_planet_carrier_overview.merge_figure(fig_sun_spacer)
  rfc.add_figure(fig_planet_carrier_overview)
  # output_hexagon
  fig_output_hexagon = cnc25d_api.Figure("output_hexagon")
  le = c['hexagon_radius'] # alias
  sr = c['hexagon_smooth_radius']
  ae = 2*math.pi/6
  ol = cnc25d_api.Arc_Line_Outline("output_hexagon_ext_ol")
  ol_piece = []
  for i in range(6):
    ol_piece.add_LineTo((0.0+le*math.cos((i+1)*ae), 0.0+le*math.sin((i+1)*ae), rbr=sr))
  ol.add_piece(ol_piece)
  ol.close_with_Line()
  fig_output_hexagon.add_external_outline(ol)
  fig_output_hexagon.add_hole_outline(cnc25d_api.Circle_Outline("output_hexagon_int_ol", c['hexagon_hole_radius'], 0.0, 0.0))
  fig_output_hexagon.set_height(c['hexagon_width'])
  rfc.add_figure(fig_output_hexagon)
  # input_sun_gear
  fig_input_sun_gear = cnc25d_api.Figure("input_sun_gear")
  gws_c = c['gp_s_c'].copy()
  gws_c['axle_type'] = 'circle'
  gws_c['axle_x_width'] = c['input_axle_diameter']
  i_gws = gearwheel.gearwheel()
  i_gws.apply_external_constraint(gws_c)
  fig_input_sun_gear.merge_figure(i_gws.get_A_figure('gearwheel_fig'), extrudable=True)
  fig_input_sun_gear.set_height(c['input_sun_width'])
  rfc.add_figure(fig_input_sun_gear)
  # output_cover
  fig_output_cover = cnc25d_api.Figure("output_cover")
  gr_c = c['gr_c'].copy()
  gr_c['holder_diameter'] = 2*c['holder_radius']
  gr_c['gear_tooth_nb'] = 0
  gr_c['gear_primitive_diameter'] = 2*c['output_cover_radius']
  i_gr = gearring.gearring()
  i_gr.apply_external_constraint(gr_c)
  fig_output_cover.merge_figure(i_gr.get_A_figure('gearring_fig'), extrudable=True)
  fig_output_cover.set_height(c['output_cover_width'])
  rfc.add_figure(fig_output_cover)
  #cnc25d_api.figure_simple_display(fig_output_cover.cnc_cut(), fig_output_cover.ideal(), "debug")
  # motor_holder
  fig_motor_holder = cnc25d_api.Figure("motor_holder")
  fig_motor_holder.merge_figure(i_gr.get_A_figure('gearring_without_hole_fig'), extrudable=True)
  if(c['motor_shape_rectangle_ncircle']):
    hol = cnc25d_api.Arc_Line_Outline(" motor_holder_hole") # motor_holder hole outline
    hx = c['motor_x_width']/2.0
    hy = c['motor_y_width']/2.0
    rbr = c['cnc_router_bit_radius']
    hol.add_StartPoint(hx, hy, rbr=-rbr)
    hol.add_LineTo(-hx, hy, rbr=-rbr)
    hol.add_LineTo(-hx, -hy, rbr=-rbr)
    hol.add_LineTo(hx, -hy, rbr=-rbr)
    hol.close_with_Line()
  else:
    hol = cnc25d_api.Circle_Outline("motor_holder_hole", c['motor_x_width']/2.0, 0.0, 0.0)
  fig_motor_holder.add_hole_outline(hol)
  fig_motor_holder.set_height(c['motor_holder_width'])
  rfc.add_figure(fig_motor_holder)
  #cnc25d_api.figure_simple_display(fig_motor_holder.cnc_cut(), fig_motor_holder.ideal(), "debug")
  # motor_holder_leg
  fig_motor_holder_leg = cnc25d_api.Figure("motor_holder_leg")
  x1 = 0.0 + c['motor_holder_A']
  x2 = x1 + c['motor_holder_C']
  x3 = x2 + c['motor_holder_D']
  y1 = 0.0 + c['motor_holder_E']
  y2 = y1 + c['motor_holder_B']
  ol = cnc25d_api.Arc_Line_Outline("motor_holder_leg_ext_ol")
  ol.add_StartPoint(0, 0, rbr=0) # start point of the motor_holder_leg outline
  ol.add_LineTo(x3, 0, rbr=0)
  ol.add_LineTo(x3, y1, rbr=0)
  ol.add_LineTo(x2, y1, rbr=0)
  ol.add_LineTo(x1, y2, rbr=0)
  ol.add_LineTo(0, y2, rbr=0)
  ol.close_with_Line()
  fig_motor_holder_leg.add_external_outline(ol)
  fig_motor_holder_leg.set_height = c['motor_holder_leg_width']
  rfc.add_figure(fig_motor_holder_leg)
  # output_axle_holder_plate
  fig_output_axle_holder_plate = cnc25d_api.Figure('output_axle_holder_plate')
  fig_output_axle_holder_plate.merge_figure(i_gr.get_A_figure('gearring_without_hole_fig'), extrudable=True)
  fig_output_axle_holder_plate.add_hole_outline(cnc25d_api.Circle_Outline("hole", c['output_axle_radius'], 0.0, 0.0))
  fig_output_axle_holder_plate.set_height(c['axle_holder_width'])
  rfc.add_figure(fig_output_axle_holder_plate)
  # output_axle_holder_cylinder
  fig_cylinder = cnc25d_api.Figure("output_axle_holder_cylinder")
  fig_cylinder.add_external_outline(cnc25d_api.Circle_Outline("ext_ol", c['axle_holder_D']/2.0, 0.0, 0.0))
  fig_cylinder.add_hole_outline(cnc25d_api.Circle_Outline("int_ol", c['output_axle_radius'], 0.0, 0.0))
  fig_cylinder.set_height(c['output_axle_cylinder_width'])
  rfc.add_figure(fig_cylinder)
  # output_axle_holder_leg
  fig_output_axle_holder_leg = cnc25d_api.Figure("output_axle_holder_leg")
  x1 = 0.0 + c['axle_holder_A']
  x2 = x1 + c['axle_holder_C']
  y1 = 0.0 + c['output_axle_cylinder_thickness']
  y2 = y1 + c['axle_holder_B']
  ol = cnc25d_api.Arc_Line_Outline("leg")
  ol.add_StartPoint(0, 0, rbr=0) # start point of the motor_holder_leg outline
  ol.add_LineTo(x2, 0, rbr=0)
  ol.add_LineTo(x2, y1, rbr=0)
  ol.add_LineTo(x1, y2, rbr=0)
  ol.add_LineTo(0, y2, rbr=0)
  ol.close_with_Line()
  fig_output_axle_holder_leg.add_external_outline(ol)
  fig_output_axle_holder_leg.set_height(c['axle_holder_leg_width'])
  rfc.add_figure(fig_output_axle_holder_leg)
  # output_holder
  fig_output_holder = cnc25d_api.Figure("output_holder")
  gr_c = c['gr_c'].copy()
  gr_c['holder_diameter'] = 2*c['holder_radius']
  gr_c['gear_tooth_nb'] = 0
  gr_c['gear_primitive_diameter'] = 2*c['output_holder_radius']
  gr_c['holder_crenel_number_cut'] = c['output_holder_crenel_nb_default']
  #print("dbg962: holder_crenel_number, holder_crenel_number_cut:", c['holder_crenel_number'], gr_c['holder_crenel_number_cut'])
  #i_gr = gearring.gearring()
  i_gr.apply_external_constraint(gr_c)
  fig_output_holder.merge_figure(i_gr.get_A_figure('gearring_cut'), extrudable=True)
  fig_output_holder.set_height(c['output_holder_width'])
  rfc.add_figure(fig_output_holder)
  #cnc25d_api.figure_simple_display(fig_output_holder.cnc_cut(), fig_output_holder.ideal(), "debug")
  ###
  return(rfc)

      
################################################################
# low_torque_transmission 3D assembly-configuration construction
################################################################

def ltt_3d_construction(c):
  """ construct the 3D-assembly-configurations of the low_torque_transmission
  """
  #
  r_assembly = {}
  r_slice = {}
  # planet_gear
  r_assembly['planet_gear'] = (
    ('planet_gear', 0.0, 0.0, 0.0, 0.0, c['planet_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('planet_spacer', 0.0, 0.0, 0.0, 0.0, c['planet_spacer_width'], 'i', 'xy', 0.0, 0.0, c['planet_width']))
  r_slice['planet_gear'] = ()
  # output_planet_gear
  r_assembly['output_planet_gear'] = (
    ('planet_gear', 0.0, 0.0, 0.0, 0.0, c['output_planet_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('planet_spacer', 0.0, 0.0, 0.0, 0.0, c['planet_spacer_width'], 'i', 'xy', 0.0, 0.0, c['output_planet_width']))
  r_slice['output_planet_gear'] = ()
  # rear_planet_carrier
  assembly = []
  assembly.append(('planet_carrier_rear', 0.0, 0.0, 0.0, 0.0, c['rear_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, 0.0))
  for i in range(c['planet_nb']):
    assembly.append(('planet_carrier_middle_{:d}'.format(i), 0.0, 0.0, 0.0, 0.0, c['middle_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, c['rear_planet_carrier_width']))
    assembly.append(('planet_carrier_spacer_{:d}'.format(i), 0.0, 0.0, 0.0, 0.0, c['rear_planet_carrier_spacer_width'], 'i', 'xy', 0.0, 0.0, c['rear_planet_carrier_width']))
    assembly.append(('planet_carrier_fitting_square_{:d}'.format(i), 0.0, 0.0, 0.0, 0.0, c['front_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, c['rear_planet_carrier_width']+c['middle_planet_carrier_width']))
  r_assembly['rear_planet_carrier'] = assembly[:]
  r_slice['rear_planet_carrier'] = ()
  # output_rear_planet_carrier
  assembly = []
  assembly.append(('planet_carrier_rear', 0.0, 0.0, 0.0, 0.0, c['output_rear_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, 0.0))
  for i in range(c['planet_nb']):
    assembly.append(('planet_carrier_middle_{:d}'.format(i), 0.0, 0.0, 0.0, 0.0, c['output_middle_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, c['output_rear_planet_carrier_width']))
    assembly.append(('planet_carrier_spacer_{:d}'.format(i), 0.0, 0.0, 0.0, 0.0, c['rear_planet_carrier_spacer_width'], 'i', 'xy', 0.0, 0.0, c['output_rear_planet_carrier_width']))
    assembly.append(('planet_carrier_fitting_square_{:d}'.format(i), 0.0, 0.0, 0.0, 0.0, c['output_front_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, c['output_rear_planet_carrier_width']+c['output_middle_planet_carrier_width']))
  r_assembly['output_rear_planet_carrier'] = assembly[:]
  r_slice['output_rear_planet_carrier'] = ()
  # front_planet_carrier
  r_assembly['front_planet_carrier'] = (
    ('planet_carrier_front', 0.0, 0.0, 0.0, 0.0, c['front_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('sun_gear', 0.0, 0.0, 0.0, 0.0, c['sun_width'], 'i', 'xy', 0.0, 0.0, c['front_planet_carrier_width']),
    ('sun_spacer', 0.0, 0.0, 0.0, 0.0, c['sun_spacer_width'], 'i', 'xy', 0.0, 0.0, c['front_planet_carrier_width']+c['sun_width']))
  r_slice['front_planet_carrier'] = ()
  # output_front_planet_carrier
  r_assembly['output_front_planet_carrier'] = (
    ('planet_carrier_front', 0.0, 0.0, 0.0, 0.0, c['front_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('sun_gear', 0.0, 0.0, 0.0, 0.0, c['output_sun_width'], 'i', 'xy', 0.0, 0.0, c['front_planet_carrier_width']),
    ('sun_spacer', 0.0, 0.0, 0.0, 0.0, c['sun_spacer_width'], 'i', 'xy', 0.0, 0.0, c['front_planet_carrier_width']+c['output_sun_width']))
  r_slice['output_front_planet_carrier'] = ()
  # output_shaft
  r_assembly['output_shaft'] = (
    ('planet_carrier_front', 0.0, 0.0, 0.0, 0.0, c['output_front_planet_carrier_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('output_hexagon', 0.0, 0.0, 0.0, 0.0, c['hexagon_width'], 'i', 'xy', 0.0, 0.0, c['output_front_planet_carrier_width']))
  r_slice['output_shaft'] = ()
  # input_sun_gear
  r_assembly['input_sun_gear'] = (
    ('input_sun_gear', 0.0, 0.0, 0.0, 0.0, c['input_sun_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('sun_spacer', 0.0, 0.0, 0.0, 0.0, c['sun_spacer_width'], 'i', 'xy', 0.0, 0.0, c['input_sun_width']))
  r_slice['input_sun_gear'] = ()
  # motor_holder
  r_assembly['motor_holder'] = (
    ('motor_holder', 0.0, 0.0, 0.0, 0.0, c['motor_holder_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('motor_holder_leg', 0.0, 0.0, c['motor_holder_leg_x'], c['motor_holder_leg_y'], c['motor_holder_leg_width'], 'i', 'zx', c['motor_x_width']/2.0, -c['motor_holder_leg_width']/2.0, c['motor_holder_width']),
    ('motor_holder_leg', 0.0, 0.0, c['motor_holder_leg_x'], c['motor_holder_leg_y'], c['motor_holder_leg_width'], 'x', 'zx', -c['motor_x_width']/2.0-c['motor_holder_leg_y'], -c['motor_holder_leg_width']/2.0, c['motor_holder_width']),
    ('motor_holder_leg', 0.0, 0.0, c['motor_holder_leg_x'], c['motor_holder_leg_y'], c['motor_holder_leg_width'], 'i', 'zy', -c['motor_holder_leg_width']/2.0, c['motor_x_width']/2.0, c['motor_holder_width']),
    ('motor_holder_leg', 0.0, 0.0, c['motor_holder_leg_x'], c['motor_holder_leg_y'], c['motor_holder_leg_width'], 'x', 'zy', -c['motor_holder_leg_width']/2.0, -c['motor_x_width']/2.0-c['motor_holder_leg_y'], c['motor_holder_width']))

  r_slice['motor_holder'] = ()
  # gearring_holder
  r_assembly['gearring_holder'] = [('gearring_holder', 0.0, 0.0, 0.0, 0.0, c['gearring_holder_width'], 'i', 'xy', 0.0, 0.0, 0.0)]
  r_slice['gearring_holder'] = ()
  # output_holder
  r_assembly['output_holder'] = (
    ('output_cover', 0.0, 0.0, 0.0, 0.0, c['output_cover_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('output_holder', 0.0, 0.0, 0.0, 0.0, c['output_holder_width'], 'i', 'xy', 0.0, 0.0, c['output_cover_width']))
  r_slice['output_holder'] = ()
  # output_axle_holder
  r_assembly['output_axle_holder'] = (
    ('output_axle_holder_plate', 0.0, 0.0, 0.0, 0.0, c['axle_holder_width'], 'i', 'xy', 0.0, 0.0, 0.0),
    ('output_axle_holder_cylinder', 0.0, 0.0, 0.0, 0.0, c['output_axle_cylinder_width'], 'i', 'xy', 0.0, 0.0, c['axle_holder_width']),
    ('output_axle_holder_leg', 0.0, 0.0, c['axle_holder_leg_x'], c['axle_holder_leg_y'], c['axle_holder_leg_width'], 'i', 'zx', c['output_axle_radius'], -c['axle_holder_leg_width']/2.0, c['axle_holder_width']),
    ('output_axle_holder_leg', 0.0, 0.0, c['axle_holder_leg_x'], c['axle_holder_leg_y'], c['axle_holder_leg_width'], 'x', 'zx', -c['output_axle_radius']-c['axle_holder_leg_y'], -c['axle_holder_leg_width']/2.0, c['axle_holder_width']),
    ('output_axle_holder_leg', 0.0, 0.0, c['axle_holder_leg_x'], c['axle_holder_leg_y'], c['axle_holder_leg_width'], 'i', 'zy', -c['axle_holder_leg_width']/2.0, c['output_axle_radius'], c['axle_holder_width']),
    ('output_axle_holder_leg', 0.0, 0.0, c['axle_holder_leg_x'], c['axle_holder_leg_y'], c['axle_holder_leg_width'], 'x', 'zy', -c['axle_holder_leg_width']/2.0, -c['output_axle_radius']-c['axle_holder_leg_y'], c['axle_holder_width']))

  r_slice['output_axle_holder'] = ()
  #
  return((r_assembly, r_slice))


################################################################
# low_torque_transmission simulation
################################################################

def eg_sim_planet_sun(c):
  """ define the epicyclic_gearing first simulation: planet-sun
  """
  # gear_profile simulation
  i_gear_profile = gear_profile.gear_profile(c['gp_ps_c'])
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def eg_sim_annulus_planet(c):
  """ define the epicyclic_gearing second simulation: annulus-planet
  """
  # gear_profile simulation
  i_gear_profile = gear_profile.gear_profile(c['gp_ap_c'])
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
  r_info += """
sun_gear_tooth_nb:        \t{:d}
z31_planet_gear_tooth_nb: \t{:d}
z32_planet_gear_tooth_nb: \t{:d}
annulus_gear_tooth_nb:    \t{:d}
smallest_gear_tooth_nb:   \t{:d}
planet_nb:                \t{:d}
planet_number_max:        \t{:d}
""".format(c['sun_gear_tooth_nb'], c['z31_planet_gear_tooth_nb'], c['z32_planet_gear_tooth_nb'], c['annulus_gear_tooth_nb'], c['smallest_gear_tooth_nb'], c['planet_nb'], c['planet_number_max'])
  r_info += """
gear_module:              \t{:0.3f}
""".format(c['gear_module'])
  r_info += """
sun_spacer_width:         \t{:0.3f}
  """.format(c['sun_spacer_width'])
  r_info += """
planet_spacer_width:          \t{:0.3f}
  """.format(c['planet_spacer_width'])
  r_info += """
planet_carrier_axle_radius:           \t{:0.3f}   diameter: {:0.3f}
planet_carrier_spacer_length:         \t{:0.3f}
planet_carrier_axle_holder_radius:    \t{:0.3f}   diameter: {:0.3f}
rear_planet_carrier_spacer_width:     \t{:0.3f}
  """.format(c['planet_carrier_axle_radius'], 2*c['planet_carrier_axle_radius'], c['planet_carrier_spacer_length'], c['planet_carrier_axle_holder_radius'], 2*c['planet_carrier_axle_holder_radius'], c['rear_planet_carrier_spacer_width'])
  r_info += """
planet_carrier_external_radius:     \t{:0.3f}   diameter: {:0.3f}
planet_carrier_external_max_radius: \t{:0.3f}   diameter: {:0.3f}
planet_carrier_internal_radius:     \t{:0.3f}   diameter: {:0.3f}
planet_carrier_internal_min_radius: \t{:0.3f}   diameter: {:0.3f}
planet_carrier_rear_smooth_radius:  \t{:0.3f}
planet_circle_radius:               \t{:0.3f}   diameter: {:0.3f}
  """.format(c['planet_carrier_external_radius'], 2*c['planet_carrier_external_radius'], c['planet_carrier_external_diameter_max']/2.0, c['planet_carrier_external_diameter_max'], c['planet_carrier_internal_radius'], 2*c['planet_carrier_internal_radius'], c['planet_carrier_internal_diameter_min']/2.0, c['planet_carrier_internal_diameter_min'], c['planet_carrier_rear_smooth_radius'], c['planet_circle_radius'], 2*c['planet_circle_radius'])
  r_info += """
planet_carrier_middle_clearance_radius:     \t{:0.3f}   diameter: {:0.3f}
planet_carrier_middle_clearance_min_radius: \t{:0.3f}   diameter: {:0.3f}
planet_carrier_middle_smooth_radius:        \t{:0.3f}
middle_planet_carrier_internal_radius:      \t{:0.3f}   diameter: {:0.3f}
  """.format(c['planet_carrier_middle_clearance_radius'], 2*c['planet_carrier_middle_clearance_radius'], c['planet_carrier_middle_clearance_diameter_min'], c['planet_carrier_middle_clearance_diameter_min']/2.0, c['planet_carrier_middle_smooth_radius'], c['middle_planet_carrier_internal_radius'], 2*c['middle_planet_carrier_internal_radius'])
  r_info += """
planet_carrier_fitting_square_l1:             \t{:0.3f}
planet_carrier_fitting_square_l2:             \t{:0.3f}
planet_carrier_fitting_square_extra_cut:      \t{:0.3f}
planet_carrier_fitting_square:                \t{:d}
planet_carrier_fitting_hole_radius:           \t{:0.3f}   diameter: {:0.3f}
planet_carrier_fitting_hole_position:         \t{:0.3f}
planet_carrier_fitting_double_hole_distance:  \t{:0.3f}
  """.format(c['planet_carrier_fitting_square_l1'], c['planet_carrier_fitting_square_l2'], c['planet_carrier_fitting_square_extra_cut'], c['planet_carrier_fitting_square'], c['planet_carrier_fitting_hole_radius'], 2*c['planet_carrier_fitting_hole_radius'], c['planet_carrier_fitting_hole_position'], c['planet_carrier_fitting_double_hole_distance'])
  r_info += """
planet_carrier_angle:   \t{:0.3f} (radian)      {:0.3f} (degree)
  """.format(c['planet_carrier_angle'], c['planet_carrier_angle']*180/math.pi)
  r_info += """
planet_width:                 \t{:0.3f}
front_planet_carrier_width:   \t{:0.3f}
rear_planet_carrier_width:    \t{:0.3f}
rear_planet_carrier_spacer_width: \t{:0.3f}
planet_spacer_width:          \t{:0.3f}
sun_spacer_width:             \t{:0.3f}
planet_slack:                 \t{:0.3f}
step_slack:                   \t{:0.3f}
middle_planet_carrier_width:  \t{:0.3f}
sun_width:                    \t{:0.3f}
step_width:                   \t{:0.3f}
  """.format(c['planet_width'], c['front_planet_carrier_width'], c['rear_planet_carrier_width'], c['rear_planet_carrier_spacer_width'], c['planet_spacer_width'], c['sun_spacer_width'], c['planet_slack'], c['step_slack'], c['middle_planet_carrier_width'], c['sun_width'], c['step_width'])
  r_info += """
holder_radius:          \t{:0.3f}   diameter: {:0.3f}
cnc_router_bit_radius:  \t{:0.3f}
  """.format(c['holder_radius'], 2*c['holder_radius'], c['cnc_router_bit_radius'])
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
    ["simplest test"        , "--sun_gear_tooth_nb 20 --z31_planet_gear_tooth_nb 31 --gear_module 1.0 --planet_nb 3"],
    ["last test"            , "--sun_gear_tooth_nb 19 --z31_planet_gear_tooth_nb 31 --gear_module 1.0 --planet_nb 4"]]
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
      l_display_figure_list     = ['epicyclic_middle_overview', 'planet_carrier_overview'],
      s_default_simulation      = '',
      l_2d_figure_file_list     = [], # all figures
      l_3d_figure_file_list     = None, # no figure
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
  my_ltt.cli("--sun_gear_tooth_nb 19 --z31_planet_gear_tooth_nb 31 --gear_module 1.0")
  if(cnc25d_api.interpretor_is_freecad()):
    #Part.show(my_ltt.get_fc_obj_3dconf('planet_gear'))
    #Part.show(my_ltt.get_fc_obj_3dconf('output_planet_gear'))
    #Part.show(my_ltt.get_fc_obj_3dconf('rear_planet_carrier'))
    #Part.show(my_ltt.get_fc_obj_3dconf('front_planet_carrier'))
    Part.show(my_ltt.get_fc_obj_3dconf('output_rear_planet_carrier'))
    #Part.show(my_ltt.get_fc_obj_3dconf('output_front_planet_carrier'))
    #Part.show(my_ltt.get_fc_obj_3dconf('input_sun_gear'))
    #Part.show(my_ltt.get_fc_obj_3dconf('motor_holder'))
    #Part.show(my_ltt.get_fc_obj_3dconf('gearring_holder'))
    #Part.show(my_ltt.get_fc_obj_3dconf('output_holder'))
    #Part.show(my_ltt.get_fc_obj_3dconf('output_axle_holder'))


