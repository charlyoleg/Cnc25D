# crest.py
# generates the crest, an optional part for the cross_cube assembly
# created by charlyoleg on 2013/12/07
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


"""
crest.py generates the crest part, an optional part for the cross_cube assembly.
The main function displays in a Tk-interface the crest part, or generates the design as files or returns the design as FreeCAD Part object.
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
import cross_cube_sub
import gear_profile


################################################################
# crest constraint_constructor
################################################################

def crest_constraint_constructor(ai_parser, ai_variant=0):
  """
  Add arguments relative to the crest
  """
  r_parser = ai_parser
  # parameter inheritance from cross_cube_sub
  r_parser = cross_cube_sub.cross_cube_sub_constraint_constructor(r_parser, 2)
  # parameter inheritance from gear_profile
  i_gear_profile = gear_profile.gear_profile()
  r_parser = i_gear_profile.get_constraint_constructor()(r_parser, 4)
  ### outline
  r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=3.0,
    help="Set the gear-module of the crest. Default: 3.0")
  r_parser.add_argument('--virtual_tooth_nb','--vtn', action='store', type=int, default=60,
    help="Set the virtual number of gear-teeth of the crest. Default: 60")
  r_parser.add_argument('--portion_tooth_nb','--ptn', action='store', type=int, default=30,
    help="Set the number of teeth of the gear-portion of the crest. Default: 30")
  r_parser.add_argument('--free_mounting_width','--fmw', action='store', type=float, default=15.0,
    help="Set the width that must be kept free to mount the crest in a cross_cube (minimum: face_B1_thickness + cnc_router_bit_radius). Default: 15.0")
  ### crest_hollow
  r_parser.add_argument('--crest_hollow_leg_nb','--chln', action='store', type=int, default=4,
    help="Set the number of crest-hollow_legs. Possible values: 1(filled), 2(end-legs only), 3, 4, etc. Default: 4")
  r_parser.add_argument('--end_leg_width','--elw', action='store', type=float, default=10.0,
    help="Set the width of the two end-legs of the crest. Default: 10.0")
  r_parser.add_argument('--middle_leg_width','--mlw', action='store', type=float, default=0.0,
    help="Set the width of the middle-legs of the crest. If equal to 0.0, set to end_leg_width. Default: 0.0")
  r_parser.add_argument('--crest_hollow_external_diameter','--ched', action='store', type=float, default=0.0,
    help="Set the diameter of the crest-hollow-external circle. If equal to 0.0, set to gear_hollow_radius - delta. Default: 0.0")
  r_parser.add_argument('--crest_hollow_internal_diameter','--chid', action='store', type=float, default=0.0,
    help="Set the diameter of the crest-hollow-internal circle. If equal to 0.0, set to minimal_crest_hollow_internal_radius. Default: 0.0")
  r_parser.add_argument('--floor_width','--fw', action='store', type=float, default=0.0,
    help="Set the width between the cross_cube-top-holes and the crest-gear-hollow. If equal to 0.0, set to end_leg_width. Default: 0.0")
  r_parser.add_argument('--crest_hollow_smoothing_radius','--chsr', action='store', type=float, default=0.0,
    help="Set the smoothing radius for the crest-hollow. If equal to 0.0, set to 0.5*maximal_crest_hollow_smoothing_radius. Default: 0.0")
  ### gear_holes
  r_parser.add_argument('--fastening_hole_diameter','--fhd', action='store', type=float, default=5.0,
    help="Set the diameter of the crest-gear-fastening-holes. Default: 5.0")
  r_parser.add_argument('--fastening_hole_position','--fhp', action='store', type=float, default=0.0,
    help="Set the position relative to the gear-hollow-external circle of the crest-gear-fastening-holes. Default: 0.0")
  r_parser.add_argument('--centring_hole_diameter','--chd', action='store', type=float, default=1.0,
    help="Set the diameter of the crest-gear-centring-holes. Default: 1.0")
  r_parser.add_argument('--centring_hole_distance','--chdi', action='store', type=float, default=8.0,
    help="Set the distance between a pair of crest-gear-centring-holes. Default: 8.0")
  r_parser.add_argument('--centring_hole_position','--chp', action='store', type=float, default=0.0,
    help="Set the position relative to the gear-hollow-external circle of the crest-gear-centring-holes. Default: 0.0")
  ## part thickness
  r_parser.add_argument('--crest_thickness','--ct', action='store', type=float, default=5.0,
    help="Set the thickness (z-size) of the crest. Default: 5.0")
  ### manufacturing
  r_parser.add_argument('--crest_cnc_router_bit_radius','--ccrbr', action='store', type=float, default=0.5,
    help="Set the minimal router_bit radius for the crest part. Default: 0.5")
  ### output
  # return
  return(r_parser)

################################################################
# constraint_conversion
################################################################

def gear_profile_constraint(c):
  """ prepare the gear_profile constraint
  """
  gp_c = c.copy()
  gp_c['gear_type'] = 'e'
  gp_c['gear_module'] = c['gear_module']
  gp_c['gear_tooth_nb'] = c['virtual_tooth_nb']
  #gp_c['portion_tooth_nb'] = c['portion_tooth_nb']
  #gp_c['portion_first_end'] = 2 # slope-bottom
  #gp_c['portion_last_end'] = 2 # slope-bottom
  gp_c['cut_portion'] = [c['portion_tooth_nb'], 2, 2]
  gp_c['center_position_x'] = 0.0
  gp_c['center_position_y'] = 0.0
  gp_c['gear_initial_angle'] = math.pi/2-math.pi*(c['portion_tooth_nb']-0)/c['virtual_tooth_nb']
  return(gp_c)
    
################################################################
# crest constraint_check
################################################################

def crest_constraint_check(c):
  """ check the crest constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  ### outline
  #gear_module
  if(c['gear_module']<radian_epsilon):
    print("ERR194: Error, gear_module {:0.3f} must be strictly positive".format(c['gear_module']))
    sys.exit(2)
  #virtual_tooth_nb
  if((c['virtual_tooth_nb']-3)*c['gear_module']<0.9*c['cube_width']):
    print("ERR198: Error, virtual_tooth_nb {:d} is too small compare to gear_module {:0.3f} and cube_width {:0.3f}".format(c['virtual_tooth_nb'], c['gear_module'], c['cube_width']))
    sys.exit(2)
  gear_hollow_radius = (c['virtual_tooth_nb']-2)*c['gear_module']/2.0
  minimal_gear_portion_angle = 2*math.asin(c['cube_width']/(2.0*gear_hollow_radius))
  maximal_gear_portion_angle = 2*(math.pi-math.asin((c['cube_width']/2.0+c['free_mounting_width'])/gear_hollow_radius))
  #portion_tooth_nb
  gear_portion_angle = 2*math.pi*(c['portion_tooth_nb']+1)/c['virtual_tooth_nb']
  if(gear_portion_angle<minimal_gear_portion_angle):
    print("ERR205: Error, portion_tooth_nb {:d} is too small compare to gear_module {:0.3f}, virtual_tooth_nb {:d} and cube_width {:0.3f}".format(c['portion_tooth_nb'], c['gear_module'], c['virtual_tooth_nb'], c['cube_width']))
    sys.exit(2)
  if(gear_portion_angle>maximal_gear_portion_angle):
    print("ERR208: Error, portion_tooth_nb {:d} is too big compare to gear_module {:0.3f}, virtual_tooth_nb {:d}, free_mounting_width {:0.3f} and cube_width {:0.3f}".format(c['portion_tooth_nb'], c['gear_module'], c['virtual_tooth_nb'], c['free_mounting_width'], c['cube_width']))
    sys.exit(2)
  #free_mounting_width
  if(c['free_mounting_width']<max(c['face_B1_thickness'], c['face_B2_thickness'])+c['crest_cnc_router_bit_radius']):
    print("ERR212: Error, free_mounting_width {:0.3f} is too small compare to face_B1_thickness {:0.3f}, face_B2_thickness {:0.3f} and crest_cnc_router_bit_radius {:0.3f}".format(c['free_mounting_width'], c['face_B1_thickness'], c['face_B2_thickness'], c['crest_cnc_router_bit_radius']))
    sys.exit(2)
  if(c['free_mounting_width']+c['cube_width']/2.0>gear_hollow_radius):
    print("ERR215: Error, free_mounting_width {:0.3f} is too big compare to cube_width {:0.3f} and gear_hollow_radius {:0.3f}".format(c['free_mounting_width'], c['cube_width'], gear_hollow_radius))
    sys.exit(2)
  ### crest_hollow
  #crest_hollow_leg_nb # possible values: 1(filled), 2(end-legs only), 3, 4 ...
  if(c['crest_hollow_leg_nb']<1):
    print("ERR220: Error, crest_hollow_leg_nb {:d} must be bigger or equal to 1".format(c['crest_hollow_leg_nb']))
    sys.exit(2)
  #end_leg_width
  if(c['end_leg_width']<radian_epsilon):
    print("ERR224: Error, end_leg_width {:0.3f} must be strictly positive".format(c['end_leg_width']))
    sys.exit(2)
  if(c['end_leg_width']>0.7*2*math.pi*gear_hollow_radius*gear_portion_angle/c['crest_hollow_leg_nb']):
    print("ERR228: Error, end_leg_width {:0.3f} is too big compare to gear_hollow_radius {:0.3f}, gear_portion_angle {:0.3f} and crest_hollow_leg_nb {:d}".format(c['end_leg_width'], gear_hollow_radius, gear_portion_angle, c['crest_hollow_leg_nb']))
    sys.exit(2)
  #middle_leg_width
  if(c['middle_leg_width']==0):
    c['middle_leg_width'] = c['end_leg_width']
  if(c['middle_leg_width']<radian_epsilon):
    print("ERR232: Error, middle_leg_width {:0.3f} must be strictly positive".format(c['middle_leg_width']))
    sys.exit(2)
  if(c['middle_leg_width']>0.7*2*math.pi*gear_hollow_radius*gear_portion_angle/c['crest_hollow_leg_nb']):
    print("ERR235: Error, middle_leg_width {:0.3f} is too big compare to gear_hollow_radius {:0.3f}, gear_portion_angle {:0.3f} and crest_hollow_leg_nb {:d}".format(c['middle_leg_width'], gear_hollow_radius, gear_portion_angle, c['crest_hollow_leg_nb']))
    sys.exit(2)
  #crest_hollow_external_diameter
  c['crest_hollow_external_radius'] = c['crest_hollow_external_diameter']/2.0
  if(c['crest_hollow_external_radius']==0):
    c['crest_hollow_external_radius'] = gear_hollow_radius - 1.5*c['gear_module']
  if(c['crest_hollow_external_radius']>gear_hollow_radius):
    print("ERR244: Error, crest_hollow_external_radius {:0.3f} is too big compare to gear_hollow_radius {:0.3f}".format(c['crest_hollow_external_radius'], gear_hollow_radius))
    sys.exit(2)
  #crest_hollow_internal_diameter
  c['crest_hollow_internal_radius'] = c['crest_hollow_internal_diameter']/2.0
  minimal_crest_hollow_internal_radius = math.sqrt((c['cube_width']/2.0)**2+(c['top_thickness']+c['height_margin']+c['axle_diameter']/2.0)**2)
  if(c['crest_hollow_internal_radius']==0):
    c['crest_hollow_internal_radius'] = minimal_crest_hollow_internal_radius
  if(c['crest_hollow_internal_radius']<minimal_crest_hollow_internal_radius):
    print("ERR252: Error, crest_hollow_internal_radius {:0.3f} must be bigger than minimal_crest_hollow_internal_radius {:0.3f}".format(c['crest_hollow_internal_radius'], minimal_crest_hollow_internal_radius))
    sys.exit(2)
  #floor_width
  if(c['floor_width']==0):
    c['floor_width'] = c['end_leg_width']
  if(c['floor_width']<radian_epsilon):
    print("ERR257: Error, floor_width {:0.3f} must be strictly positive".format(c['floor_width']))
    sys.exit(2)
  if(c['floor_width']+c['top_thickness']+c['height_margin']+c['axle_diameter']/2.0>gear_hollow_radius):
    print("ERR260: Error, floor_width {:0.3f} is too big compare to top_thickness {:0.3f}, height_margin {:0.3f}, axle_diameter {:0.3f} and gear_hollow_radius {:0.3f}".format(c['floor_width'], c['top_thickness'], c['height_margin'], c['axle_diameter'], gear_hollow_radius))
    sys.exit(2)
  #crest_hollow_smoothing_radius
  max_leg_width = max(c['end_leg_width'], c['middle_leg_width'])
  maximal_crest_hollow_smoothing_radius = (c['crest_hollow_external_radius']*float(gear_portion_angle)/c['crest_hollow_leg_nb'] - max_leg_width)/3.0
  if(c['crest_hollow_smoothing_radius']==0):
    c['crest_hollow_smoothing_radius'] = min(0.5*maximal_crest_hollow_smoothing_radius, 0.2*abs(c['crest_hollow_external_radius']-c['crest_hollow_internal_radius']))
  if(c['crest_hollow_smoothing_radius']<c['crest_cnc_router_bit_radius']):
    print("ERR267: Error, crest_hollow_smoothing_radius {:0.3f} must be bigger than crest_cnc_router_bit_radius {:0.3f}".format(c['crest_hollow_smoothing_radius'], c['crest_cnc_router_bit_radius']))
    sys.exit(2)
  if(c['crest_hollow_smoothing_radius']>maximal_crest_hollow_smoothing_radius):
    print("ERR270: Error, crest_hollow_smoothing_radius {:0.3f} must be smaller than maximal_crest_hollow_smoothing_radius {:0.3f}".format(c['crest_hollow_smoothing_radius'], maximal_crest_hollow_smoothing_radius))
    sys.exit(2)
  if(c['crest_hollow_external_radius']<c['crest_hollow_internal_radius']+2.5*c['crest_hollow_smoothing_radius']):
    print("ERR265: Error, crest_hollow_external_radius {:0.3f} is too small compare to crest_hollow_internal_radius {:0.3f} and crest_hollow_smoothing_radius {:0.3f}".format(c['crest_hollow_external_radius'], c['crest_hollow_internal_radius'], c['crest_hollow_smoothing_radius']))
    sys.exit(2)
  ### gear_holes
  #fastening_hole_diameter
  c['fastening_hole_radius'] = c['fastening_hole_diameter']/2.0
  #fastening_hole_position
  if(c['crest_hollow_external_radius'] + c['fastening_hole_position'] + c['fastening_hole_radius']>gear_hollow_radius):
    print("ERR282: Error, fastening_hole_position {:0.3f} or fastening_hole_radius {:0.3f} are too big compare to crest_hollow_external_radius {:0.3f} and gear_hollow_radius {:0.3f}".format(c['fastening_hole_position'], c['fastening_hole_radius'], c['crest_hollow_external_radius'], gear_hollow_radius))
    sys.exit(2)
  #centring_hole_diameter
  c['centring_hole_radius'] = c['centring_hole_diameter']/2.0
  #centring_hole_distance
  if(c['centring_hole_distance']<2.1*c['centring_hole_radius']):
    print("ERR288: Error, centring_hole_distance {:0.3f} is too small compare to centring_hole_radius {:0.3f}".format(c['centring_hole_distance'], c['centring_hole_radius']))
    sys.exit(2)
  #centring_hole_position
  if(c['crest_hollow_external_radius'] + c['centring_hole_position'] + c['centring_hole_radius']>gear_hollow_radius):
    print("ERR292: Error, centring_hole_position {:0.3f} or centring_hole_radius {:0.3f} are too big compare to crest_hollow_external_radius {:0.3f} and gear_hollow_radius {:0.3f}".format(c['centring_hole_position'], c['centring_hole_radius'], c['crest_hollow_external_radius'], gear_hollow_radius))
    sys.exit(2)
  ## part thickness
  #crest_thickness
  if(c['crest_thickness']<radian_epsilon):
    print("ERR297: Error, crest_thickness {:0.3f} must be strictly positive".format(c['crest_thickness']))
    sys.exit(2)
  ### manufacturing
  #crest_cnc_router_bit_radius
  if(c['gear_router_bit_radius']<c['crest_cnc_router_bit_radius']):
    c['gear_router_bit_radius'] = c['crest_cnc_router_bit_radius']
  if(c['cross_cube_cnc_router_bit_radius']<c['crest_cnc_router_bit_radius']):
    c['cross_cube_cnc_router_bit_radius'] = c['crest_cnc_router_bit_radius']
  return(c)

################################################################
# crest 2D-figures construction
################################################################

def crest_2d_construction(c):
  """ construct the 2D-figures with outlines at the A-format for the crest design
  """
  ### precision
  radian_epsilon = math.pi/1000
  ###
  cx = c['cube_width']/2.0
  cy = c['top_thickness']+c['height_margin']+c['axle_diameter']/2.0+c['inter_axle_length']
  cube_height = 2*c['top_thickness']+2*c['height_margin']+c['axle_diameter']+c['inter_axle_length']

  # inheritance from cross_cube_sub
  bottom_outline_A = cnc25d_api.rotate_and_translate_figure(cross_cube_sub.cross_cube_face_top_outline(c, c['face_B1_thickness'], c['face_B2_thickness']), c['cube_width']/2.0, cube_height/2.0, math.pi, 0.0, 0.0)
  cross_cube_hole_figure_A = cnc25d_api.rotate_and_translate_figure(cross_cube_sub.cross_cube_face_holes(c, c['face_B1_thickness'], c['face_B2_thickness']), c['cube_width']/2.0, cube_height/2.0, math.pi, 0.0, 0.0)

  # inheritance from gear_profile
  i_gear_profile = gear_profile.gear_profile()
  gp_c = gear_profile_constraint(c)
  gp_c['center_position_x'] = cx
  gp_c['center_position_y'] = cy
  i_gear_profile.apply_external_constraint(gp_c)
  gear_profile_B = i_gear_profile.get_A_figure('first_gear')[0]
  # gear_profile check
  if(abs(gear_profile_B[0][1]-gear_profile_B[-1][-1])>radian_epsilon):
    print("ERR335: Error, extremities of the gear_profile_B have different y-coordiante {:0.3f} {:0.3f}".format(gear_profile_B[0][1], gear_profile_B[-1][-1]))
    sys.exit(2)
  # gear_profile extremity angle
  crest_gear_angle = math.atan2(gear_profile_B[0][1]-cy, gear_profile_B[0][0]-cx)
 
  ## crest outline
  crest_long_nshort = True
  free_mounting_width = c['free_mounting_width']
  if(gear_profile_B[0][1]>3*cube_height/4.0+radian_epsilon):
    crest_long_nshort = False
    free_mounting_width = c['crest_cnc_router_bit_radius']
  crest_outline_A = []
  crest_outline_A.append((gear_profile_B[-1][-2], gear_profile_B[-1][-1], 0))
  crest_outline_A.append((cx+c['crest_hollow_external_radius']*math.cos(math.pi-crest_gear_angle), cy+c['crest_hollow_external_radius']*math.sin(math.pi-crest_gear_angle), c['crest_cnc_router_bit_radius']))
  crest_outline_A.append((bottom_outline_A[0][0]-free_mounting_width, bottom_outline_A[0][1], c['crest_cnc_router_bit_radius']))
  crest_outline_A.extend(bottom_outline_A[1:-1])
  crest_outline_A.append((bottom_outline_A[-1][0]+free_mounting_width, bottom_outline_A[-1][1], c['crest_cnc_router_bit_radius']))
  crest_outline_A.append((cx+c['crest_hollow_external_radius']*math.cos(crest_gear_angle), cy+c['crest_hollow_external_radius']*math.sin(crest_gear_angle), c['crest_cnc_router_bit_radius']))
  crest_outline_A.append((gear_profile_B[0][0], gear_profile_B[0][1], 0))
  crest_outline_B = cnc25d_api.cnc_cut_outline(crest_outline_A, "crest_outline_A")
  crest_outline_B.extend(gear_profile_B[1:])
  ## crest holes
  crest_hole_A = []
  crest_hole_A.extend(cross_cube_hole_figure_A) 
  # cross_cube top holes
  ccthy = cy + c['axle_diameter']/2.0+c['height_margin']
  cw5 = c['cube_width']/5
  tt = c['top_thickness']
  ccect = c['cross_cube_extra_cut_thickness']
  cccrbr = c['cross_cube_cnc_router_bit_radius']
  cc_top_hole = []
  cc_top_hole.append((-1*ccect, -1*ccect, -1*cccrbr))
  cc_top_hole.append((cw5+1*ccect, -1*ccect, -1*cccrbr))
  cc_top_hole.append((cw5+1*ccect, tt+1*ccect, -1*cccrbr))
  cc_top_hole.append((-1*ccect, tt+1*ccect, -1*cccrbr))
  cc_top_hole.append((-1*ccect, -1*ccect, 0))
  crest_hole_A.append(cnc25d_api.outline_shift_xy(cc_top_hole, 1*cw5, 1, ccthy, 1))
  crest_hole_A.append(cnc25d_api.outline_shift_xy(cc_top_hole, 3*cw5, 1, ccthy, 1))
  # crest hollow
  cher = c['crest_hollow_external_radius']
  chir = c['crest_hollow_internal_radius']
  chln = c['crest_hollow_leg_nb']
  chsr = c['crest_hollow_smoothing_radius']
  if(crest_long_nshort):
    first_leg_ex_angle = math.asin((c['end_leg_width']+3*cube_height/4.0-cy)/cher)
    first_leg_in_angle = math.asin((c['end_leg_width']+3*cube_height/4.0-cy)/chir)
    first_leg_hole_angle = math.asin((c['end_leg_width']/2.0+3*cube_height/4.0-cy)/cher)
  else:
    first_leg_ex_angle = crest_gear_angle + 2*math.atan(c['end_leg_width']/(2.0*cher))
    first_leg_in_angle = crest_gear_angle + 2*math.atan(c['end_leg_width']/(2.0*chir))
    first_leg_hole_angle = crest_gear_angle + math.atan(c['end_leg_width']/(2.0*cher))
  if(c['crest_hollow_leg_nb']>1):
    leg_step_angle = 0
    if(chln>2):
      leg_step_angle = (math.pi-2*first_leg_ex_angle)/(chln-1)
    middle_leg_ex_half_angle = math.atan(c['middle_leg_width']/(2.0*cher))
    middle_leg_in_half_angle = math.atan(c['middle_leg_width']/(2.0*chir))
    smoothing_ex_half_angle = math.atan(float(chsr)/(cher-chsr))
    smoothing_in_half_angle = math.atan(float(chsr)/(chir+chsr))
    ex1_angles = []
    ex2_angles = []
    ex1_angles.append(first_leg_ex_angle)
    for i in range(chln-2):
      ex1_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle + middle_leg_ex_half_angle)
      ex2_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle - middle_leg_ex_half_angle)
    ex2_angles.append(math.pi-first_leg_ex_angle)
    in1_angles = []
    in2_angles = []
    in1_angles.append(first_leg_in_angle)
    for i in range(chln-2):
      in1_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle + middle_leg_in_half_angle)
      in2_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle - middle_leg_in_half_angle)
    in2_angles.append(math.pi-first_leg_in_angle)
    for i in range(chln-1):
      ea1 = ex1_angles[i]
      ea2 = ex2_angles[i]
      ma = (ex1_angles[i]+ex2_angles[i])/2.0
      ia1 = in1_angles[i]
      ia2 = in2_angles[i]
      if((ea2-ea1)<2.1*smoothing_ex_half_angle):
        print("ERR419: Error, crest_hollow_smoothing_radius {:0.3f} or crest_hollow_leg_nb {:d} are too big".format(chsr, chln))
        sys.exit(2)
      hollow = []
      hollow.append((cx+cher*math.cos(ea1), cy+cher*math.sin(ea1), chsr))
      hollow.append((cx+cher*math.cos(ma), cy+cher*math.sin(ma), cx+cher*math.cos(ea2), cy+cher*math.sin(ea2), chsr))
      if((ia2-ia1)<2.1*smoothing_in_half_angle):
        hollow.append((cx+chir*math.cos(ma), cy+chir*math.sin(ma), chsr))
      else:
        hollow.append((cx+chir*math.cos(ia2), cy+chir*math.sin(ia2), chsr))
        hollow.append((cx+chir*math.cos(ma), cy+chir*math.sin(ma), cx+chir*math.cos(ia1), cy+chir*math.sin(ia1), chsr))
      hollow.append((cx+cher*math.cos(ea1), cy+cher*math.sin(ea1), 0))
      crest_hole_A.append(hollow[:])
      #[todo] optimization with floor_width
  # crest gear holes
  hole_half_angle = math.atan(c['centring_hole_distance']/(2.0*(cher+c['centring_hole_position'])))
  hole_step_angle = 0
  if(chln>2):
    hole_step_angle = (math.pi-2*first_leg_hole_angle)/(chln-1)
  hole_angles = []
  hole_angles.append(first_leg_hole_angle)
  for i in range(chln-2):
    #hole_angles.append(first_leg_hole_angle + (i+1)*hole_step_angle)
    hole_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle)
  hole_angles.append(math.pi-first_leg_hole_angle)
  for a in hole_angles:
    crest_hole_A.append((cx+(cher+c['fastening_hole_position'])*math.cos(a), cy+(cher+c['fastening_hole_position'])*math.sin(a), c['fastening_hole_radius']))
    crest_hole_A.append((cx+(cher+c['centring_hole_position'])*math.cos(a-hole_half_angle), cy+(cher+c['centring_hole_position'])*math.sin(a-hole_half_angle), c['centring_hole_radius']))
    crest_hole_A.append((cx+(cher+c['centring_hole_position'])*math.cos(a+hole_half_angle), cy+(cher+c['centring_hole_position'])*math.sin(a+hole_half_angle), c['centring_hole_radius']))
  ## crest figure
  crest_figure = []
  crest_figure.append(crest_outline_B)
  crest_figure.extend(cnc25d_api.cnc_cut_figure(crest_hole_A, "crest_hole_A"))
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['crest_fig'] = crest_figure
  r_height['crest_fig'] = c['crest_thickness']
  ###
  return((r_figures, r_height))

################################################################
# crest simulation
################################################################

def crest_simulation_A(c):
  """ define the crest simulation
  """
  # inherit from gear_profile
  i_gear_profile = gear_profile.gear_profile()
  i_gear_profile.apply_external_constraint(gear_profile_constraint(c))
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def crest_2d_simulations():
  """ return the dictionary defining the available simulation for crest
  """
  r_sim = {}
  r_sim['crest_simulation_A'] = crest_simulation_A
  return(r_sim)

################################################################
# crest 3D assembly-configuration construction
################################################################

def crest_3d_construction(c):
  """ construct the 3D-assembly-configurations of the crest
  """
  #
  # conf1
  crest_3dconf1 = []
  crest_3dconf1.append(('crest_fig',  0.0, 0.0, 0.0, 0.0, c['crest_thickness'], 'i', 'xy', 0.0, 0.0, 0.0))
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['crest_3dconf1'] = crest_3dconf1
  ct = c['crest_thickness']
  cr = (c['virtual_tooth_nb']+2)*c['gear_module']/2.0
  r_slice['crest_3dconf1'] = (2*cr,2*cr,ct, -cr,-cr,0.0, [0.5*ct], [], [])
  #
  return((r_assembly, r_slice))




################################################################
# crest_info
################################################################

def crest_info(c):
  """ create the text info related to the crest design
  """
  r_info = ""
  r_info += """
crest gear:
gear_module:          {:0.3f}
virtual_tooth_nb:     {:d}
portion_tooth_nb:     {:d}
free_mounting_width:  {:0.3f}
""".format(c['gear_module'], c['virtual_tooth_nb'], c['portion_tooth_nb'], c['free_mounting_width'])
  r_info += """
crest hollow:
crest_hollow_leg_nb:            {:d}
end_leg_width:                  {:0.3f}
middle_leg_width:               {:0.3f}
crest_hollow_external_radius:   {:0.3f}   diameter: {:0.3f}
crest_hollow_internal_radius:   {:0.3f}   diameter: {:0.3f}
floor_width:                    {:0.3f}
crest_hollow_smoothing_radius:  {:0.3f}
""".format(c['crest_hollow_leg_nb'], c['end_leg_width'], c['middle_leg_width'], c['crest_hollow_external_radius'], 2*c['crest_hollow_external_radius'], c['crest_hollow_internal_radius'], 2*c['crest_hollow_internal_radius'], c['floor_width'], c['crest_hollow_smoothing_radius'])
  r_info += """
gear holes:
fastening_hole_radius:    {:0.3f}   diameter: {:0.3f}
fastening_hole_position:  {:0.3f}
centring_hole_radius:     {:0.3f}   diameter: {:0.3f}
centring_hole_distance:   {:0.3f}
centring_hole_position:   {:0.3f}
""".format(c['fastening_hole_radius'], 2*c['fastening_hole_radius'], c['fastening_hole_position'], c['centring_hole_radius'], 2*c['centring_hole_radius'], c['centring_hole_distance'], c['centring_hole_position'])
  r_info += """
crest manufacturing:
crest_cnc_router_bit_radius: {:0.3f}
""".format(c['crest_cnc_router_bit_radius'])
  r_info += cross_cube_sub.cross_cube_face_parameter_info(c)
  return(r_info)

################################################################
# self test
################################################################

def crest_self_test():
  """
  This is the non-regression test of crest.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , ""],
    ["short and no leg"  , "--portion_tooth_nb 20 --crest_hollow_leg_nb 1"],
    ["short and end-legs"  , "--portion_tooth_nb 20 --crest_hollow_leg_nb 2"],
    ["short and 3 legs"  , "--portion_tooth_nb 20 --crest_hollow_leg_nb 3"],
    ["short and 4 legs"  , "--portion_tooth_nb 20 --crest_hollow_leg_nb 4"],
    ["long and no leg"  , "--portion_tooth_nb 35 --crest_hollow_leg_nb 1"],
    ["long and end-legs"  , "--portion_tooth_nb 35 --crest_hollow_leg_nb 2"],
    ["long and 5 legs"  , "--portion_tooth_nb 35 --crest_hollow_leg_nb 5"],
    ["extra cut" , "--cross_cube_extra_cut_thickness 1.0"],
    ["extra cut negative" , "--cross_cube_extra_cut_thickness -0.5"],
    ["gear_simulation", "--s2d --second_gear_tooth_nb 17"],
    ["outputfile" , "--output_file_basename test_output/crest_self_test.dxf"],
    ["last test"            , ""]]
  return(r_tests)

################################################################
# crest design declaration
################################################################

class crest(cnc25d_api.bare_design):
  """ crest design
  """
  def __init__(self, constraint={}):
    """ configure the crest design
    """
    self.design_setup(
      s_design_name             = "crest_design",
      f_constraint_constructor  = crest_constraint_constructor,
      f_constraint_check        = crest_constraint_check,
      f_2d_constructor          = crest_2d_construction,
      d_2d_simulation           = crest_2d_simulations(),
      f_3d_constructor          = crest_3d_construction,
      f_info                    = crest_info,
      l_display_figure_list     = ['crest_fig'],
      s_default_simulation      = "",
      l_2d_figure_file_list     = [], # all figures (actualy just crest_fig :)
      l_3d_figure_file_list     = [],
      l_3d_conf_file_list       = ['crest_3dconf1'],
      f_cli_return_type         = None,
      l_self_test_list          = crest_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("crest.py says hello!\n")
  my_c = crest()
  my_c.cli()
  #my_c.cli("--cross_cube_extra_cut_thickness 1.0")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_c.get_fc_obj('crest_3dconf1'))


