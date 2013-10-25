# gearwheel.py
# generates gearwheel and simulates gear.
# created by charlyoleg on 2013/06/19
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
gearwheel.py is a parametric generator of gearwheels.
The main function return the gear-wheel as FreeCAD Part object.
You can also simulate or view of the gearwheel and get a DXF, SVG or BRep file.
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import cnc25d_api
#cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

import math
import sys, argparse
#from datetime import datetime
#import os, errno
#import re
#import Tkinter # to display the outline in a small GUI
#
import Part
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import gear_profile

################################################################
# gearwheel dictionary-constraint-arguments default values
################################################################

def gearwheel_dictionary_init():
  """ create and initiate a gearwheel_dictionary with the default value
  """
  r_gwd = {}
  #### inherit dictionary entries from gear_profile
  r_gwd.update(gear_profile.gear_profile_dictionary_init())
  #### gearwheel dictionary entries
  ### axle
  r_gwd['axle_type']                = 'none' # 'none', 'circle', 'rectangle'
  r_gwd['axle_x_width']             = 10.0
  r_gwd['axle_y_width']             = 10.0
  r_gwd['axle_router_bit_radius']   = 0.1
  ### crenel
  r_gwd['crenel_number']      = 0
  r_gwd['crenel_type']        = 'rectangle' # 'rectangle' or 'circle'
  r_gwd['crenel_mark_nb']     = 0
  r_gwd['crenel_diameter']    = 0.0
  r_gwd['crenel_angle']       = 0.0
  r_gwd['crenel_width']       = 10.0
  r_gwd['crenel_height']      = 5.0
  r_gwd['crenel_router_bit_radius'] = 0.1
  ### wheel-hollow = legs
  r_gwd['wheel_hollow_leg_number']        = 0
  r_gwd['wheel_hollow_leg_width']         = 10.0
  r_gwd['wheel_hollow_leg_angle']         = 0.0
  r_gwd['wheel_hollow_internal_diameter'] = 0.0
  r_gwd['wheel_hollow_external_diameter'] = 0.0
  r_gwd['wheel_hollow_router_bit_radius'] = 0.0
  ### cnc router_bit constraint
  r_gwd['cnc_router_bit_radius']          = 0.1
  ### view the gearwheel with tkinter
  r_gwd['tkinter_view'] = False
  r_gwd['output_file_basename'] = ''
  ### optional
  r_gwd['args_in_txt'] = ''
  r_gwd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_gwd)

################################################################
# gearwheel argparse
################################################################

def gearwheel_add_argument(ai_parser):
  """
  Add arguments relative to the gearwheel in addition to the argument of gear_profile_add_argument()
  This function intends to be used by the gearwheel_cli, gearwheel_self_test
  """
  r_parser = ai_parser
  ### inherit arguments from gear_profile
  r_parser = gear_profile.gear_profile_add_argument(r_parser, 1)
  ### axle
  r_parser.add_argument('--axle_type','--at', action='store', default='none', dest='sw_axle_type',
    help="Select the type of axle for the first gearwheel. Possible values: 'none', 'circle' and 'rectangle'. Default: 'none'")
  r_parser.add_argument('--axle_x_width','--axw', action='store', type=float, default=10.0, dest='sw_axle_x_width',
    help="Set the axle cylinder diameter or the axle rectangle x-width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--axle_y_width','--ayw', action='store', type=float, default=10.0, dest='sw_axle_y_width',
    help="Set the axle rectangle y-width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--axle_router_bit_radius','--arr', action='store', type=float, default=0.1, dest='sw_axle_router_bit_radius',
    help="Set the router_bit radius of the first gearwheel rectangle axle. Default: 0.1")
  ### crenel
  r_parser.add_argument('--crenel_number','--cn', action='store', type=int, default=0, dest='sw_crenel_number',
    help="Set the number of crenels. The crenels are uniform distributed. The first crenel is centered on the crenel_angle. 0 means no crenel. Default: 0")
  r_parser.add_argument('--crenel_type','--ct', action='store', default='rectangle', dest='sw_crenel_type',
    help="Select the type of crenel for the first gearwheel. Possible values: 'rectangle' or 'circle'. Default: 'rectangle'")
  r_parser.add_argument('--crenel_mark_nb','--cmn', action='store', type=int, default=0, dest='sw_crenel_mark_nb',
    help="Set the number of crenels that must be marked. Default: 0")
  r_parser.add_argument('--crenel_diameter','--cd', action='store', type=float, default=0.0, dest='sw_crenel_diameter',
    help="Set the bottom diameter of the crenels. If equal to 0.0, it is set to the axle diameter. Default: 0.0")
  r_parser.add_argument('--crenel_angle','--ca', action='store', type=float, default=0.0, dest='sw_crenel_angle',
    help="Set the angle position of the first crenel. Default: 0.0")
  r_parser.add_argument('--crenel_width','--cw', action='store', type=float, default=10.0, dest='sw_crenel_width',
    help="Set the width (tangential size) of a crenel. Default: 10.0")
  r_parser.add_argument('--crenel_height','--ch', action='store', type=float, default=5.0, dest='sw_crenel_height',
    help="Set the height (radial size) of a crenel. Default: 5.0")
  r_parser.add_argument('--crenel_router_bit_radius','--crbr', action='store', type=float, default=0.1, dest='sw_crenel_router_bit_radius',
    help="Set the router_bit radius for the crenel. Default: 0.1")
  ### wheel-hollow = legs
  r_parser.add_argument('--wheel_hollow_leg_number','--whln', action='store', type=int, default=0, dest='sw_wheel_hollow_leg_number',
    help="Set the number of legs for the wheel-hollow of the first gearwheel. The legs are uniform distributed. The first leg is centered on the leg_angle. 0 means no wheel-hollow. Default: 0")
  r_parser.add_argument('--wheel_hollow_leg_width','--whlw', action='store', type=float, default=10.0, dest='sw_wheel_hollow_leg_width',
    help="Set the wheel-hollow leg width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--wheel_hollow_leg_angle','--whla', action='store', type=float, default=0.0, dest='sw_wheel_hollow_leg_angle',
    help="Set the wheel-hollow leg-angle of the first gearwheel. Default: 0.0")
  r_parser.add_argument('--wheel_hollow_internal_diameter','--whid', action='store', type=float, default=0.0, dest='sw_wheel_hollow_internal_diameter',
    help="Set the wheel-hollow internal diameter of the first gearwheel. If equal to 0.0, it is set to twice the axle diameter. Default: 0.0")
  r_parser.add_argument('--wheel_hollow_external_diameter','--whed', action='store', type=float, default=0.0, dest='sw_wheel_hollow_external_diameter',
    help="Set the wheel-hollow external diameter of the first gearwheel. It must be bigger than the wheel_hollow_internal_diameter and smaller than the gear bottom diameter. If equal to 0.0 it is set to the gear-bottom-diameter minus the gear-module. Default: 0.0")
  r_parser.add_argument('--wheel_hollow_router_bit_radius','--whrr', action='store', type=float, default=0.0, dest='sw_wheel_hollow_router_bit_radius',
    help="Set the router_bit radius of the wheel-hollow of the first gearwheel. If equal to 0.0, it is set to a third of (wheel_hollow_external_diameter minus wheel_hollow_internal_diameter).Default: 0.0")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the first gearwheel. It increases gear_router_bit_radius, axle_router_bit_radius and wheel_hollow_router_bit_radius if needed. Default: 0.1")
  # return
  return(r_parser)

################################################################
# sub-funcitons
################################################################

def marked_circle_crenel(ai_x, ai_y, ai_radius, ai_orientation, ai_router_bit_radius, ai_mark_type=2):
  """ generate the B-outline of a marked circle-crenel, centered on (ai_x, ai_y) and with the orientation ai_orientation
  """
  if(ai_mark_type==0):
    r_mcc = (ai_x, ai_y, ai_radius)
  elif(ai_mark_type==1):
    A_mcc = []
    A_mcc.append((ai_x+ai_radius*math.cos(ai_orientation-math.pi/4), ai_y+ai_radius*math.sin(ai_orientation-math.pi/4), 0))
    A_mcc.append((ai_x+math.sqrt(2)*ai_radius*math.cos(ai_orientation-0*math.pi/4), ai_y+math.sqrt(2)*ai_radius*math.sin(ai_orientation-0*math.pi/4), ai_router_bit_radius))
    A_mcc.append((ai_x+ai_radius*math.cos(ai_orientation+math.pi/4), ai_y+ai_radius*math.sin(ai_orientation+math.pi/4), 0))
    A_mcc.append((ai_x+ai_radius*math.cos(ai_orientation+math.pi), ai_y+ai_radius*math.sin(ai_orientation+math.pi), ai_x+ai_radius*math.cos(ai_orientation-math.pi/4), ai_y+ai_radius*math.sin(ai_orientation-math.pi/4), 0))
    r_mcc = cnc25d_api.cnc_cut_outline(A_mcc, "marked_circle_crenel")
  elif(ai_mark_type==2):
    A_mcc = []
    A_mcc.append((ai_x+ai_radius*math.cos(-math.pi/2), ai_y+ai_radius*math.sin(-math.pi/2), 0))
    A_mcc.append((ai_x+(1+math.sqrt(2))*ai_radius, ai_y-ai_radius, ai_router_bit_radius))
    A_mcc.append((ai_x+ai_radius*math.cos(math.pi/4), ai_y+ai_radius*math.sin(math.pi/4), 0))
    A_mcc.append((ai_x+ai_radius*math.cos(math.pi), ai_y+ai_radius*math.sin(math.pi), A_mcc[0][0], A_mcc[0][1], 0))
    r_mcc = cnc25d_api.cnc_cut_outline(cnc25d_api.outline_rotate(A_mcc, ai_x, ai_y, ai_orientation), "marked_circle_crenel")
  else:
    print("ERR182: Error, ai_mark_type {:d} doesn't exist".format(ai_mark_type))
    sys.exit(2)
  return(r_mcc)
    
################################################################
# the most important function to be used in other scripts
################################################################

def gearwheel(ai_constraints):
  """
  The main function of the script.
  It generates a gearwheel according to the function arguments
  """
  ### check the dictionary-arguments ai_constraints
  gwdi = gearwheel_dictionary_init()
  gw_c = gwdi.copy()
  gw_c.update(ai_constraints)
  #print("dbg155: gw_c:", gw_c)
  if(len(gw_c.viewkeys() & gwdi.viewkeys()) != len(gw_c.viewkeys() | gwdi.viewkeys())): # check if the dictionary gw_c has exactly all the keys compare to gearwheel_dictionary_init()
    print("ERR157: Error, gw_c has too much entries as {:s} or missing entries as {:s}".format(gw_c.viewkeys() - gwdi.viewkeys(), gwdi.viewkeys() - gw_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new gearwheel constraints:")
  #for k in gw_c.viewkeys():
  #  if(gw_c[k] != gwdi[k]):
  #    print("dbg166: for k {:s}, gw_c[k] {:s} != gwdi[k] {:s}".format(k, str(gw_c[k]), str(gwdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  # get the router_bit_radius
  gear_router_bit_radius = gw_c['gear_router_bit_radius']
  if(gw_c['cnc_router_bit_radius']>gear_router_bit_radius):
    gear_router_bit_radius = gw_c['cnc_router_bit_radius']
  crenel_router_bit_radius = gw_c['crenel_router_bit_radius']
  if(gw_c['cnc_router_bit_radius']>crenel_router_bit_radius):
    crenel_router_bit_radius = gw_c['cnc_router_bit_radius']
  wheel_hollow_router_bit_radius = gw_c['wheel_hollow_router_bit_radius']
  if(gw_c['cnc_router_bit_radius']>wheel_hollow_router_bit_radius):
    wheel_hollow_router_bit_radius = gw_c['cnc_router_bit_radius']
  axle_router_bit_radius = gw_c['axle_router_bit_radius']
  if(gw_c['cnc_router_bit_radius']>axle_router_bit_radius):
    axle_router_bit_radius = gw_c['cnc_router_bit_radius']
  # gw_c['axle_type']
  if(not gw_c['axle_type'] in ('none', 'circle', 'rectangle')):
    print("ERR932: Error, axle_type {:s} is not valid!".format(gw_c['axle_type']))
    sys.exit(2)
  # gw_c['axle_x_width']
  axle_diameter = 0
  if(gw_c['axle_type'] in('circle','rectangle')):
    if(gw_c['axle_x_width']<2*axle_router_bit_radius+radian_epsilon):
      print("ERR663: Error, axle_x_width {:0.2f} is too small compare to axle_router_bit_radius {:0.2f}!".format(gw_c['axle_x_width'], axle_router_bit_radius))
      sys.exit(2)
    axle_diameter = gw_c['axle_x_width']
    # gw_c['axle_y_width']
    if(gw_c['axle_type']=='rectangle'):
      if(gw_c['axle_y_width']<2*axle_router_bit_radius+radian_epsilon):
        print("ERR664: Error, axle_y_width {:0.2f} is too small compare to axle_router_bit_radius {:0.2f}!".format(gw_c['axle_y_width'], axle_router_bit_radius))
        sys.exit(2)
      axle_diameter = math.sqrt(gw_c['axle_x_width']**2+gw_c['axle_y_width']**2)
  # crenel_type
  crenel_type = gw_c['crenel_type']
  if((crenel_type!='rectangle')and(crenel_type!='circle')):
    print("ERR213: Error, crenel_type {:s} is unknown".format(crenel_type))
    sys.exit(2)
  # crenel_mark_nb
  if((gw_c['crenel_mark_nb']<0)or(gw_c['crenel_mark_nb']>gw_c['crenel_number'])):
    print("ERR233: Error, crenel_mark_nb {:d} is out of the range 0..{:d}".format(gw_c['crenel_mark_nb'], gw_c['crenel_number']))
    sys.exit(2)
  # crenel_diameter
  crenel_diameter = gw_c['crenel_diameter']
  if(crenel_diameter==0):
    crenel_diameter = axle_diameter
  if(crenel_diameter<axle_diameter):
    print("ERR212: Error, crenel_diameter {:0.3f} is smaller than the axle_diameter {:0.3f}".format(crenel_diameter, axle_diameter))
    sys.exit(2)
  crenel_radius = crenel_diameter/2.0
  # gw_c['gear_tooth_nb']
  if(gw_c['gear_tooth_nb']>0): # create a gear_profile
    ### get the gear_profile
    gp_ci = gear_profile.gear_profile_dictionary_init()
    gp_c = dict([ (k, gw_c[k]) for k in gp_ci.keys() ]) # extract only the entries of the gear_profile
    gp_c['gear_type'] = 'e'
    gp_c['gear_router_bit_radius'] = gear_router_bit_radius
    gp_c['portion_tooth_nb'] = 0
    gp_c['portion_first_end'] = 0
    gp_c['portion_last_end'] = 0
    gp_c['output_file_basename'] = ''
    gp_c['args_in_txt'] = ''
    gp_c['return_type'] = 'figure_param_info'
    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile(gp_c)
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    minimal_gear_profile_radius = gear_profile_parameters['hollow_radius']
    g1_ix = gear_profile_parameters['center_ox']
    g1_iy = gear_profile_parameters['center_oy']
    g1_m = gear_profile_parameters['module']
  else: # no gear_profile, just a circle
    if(gw_c['gear_primitive_diameter']<radian_epsilon):
      print("ERR885: Error, the no-gear-profile circle outline diameter gear_primitive_diameter {:0.2f} is too small!".format(gw_c['gear_primitive_diameter']))
      sys.exit(2)
    g1_ix = gw_c['center_position_x']
    g1_iy = gw_c['center_position_y']
    gear_profile_B = (g1_ix, g1_iy, float(gw_c['gear_primitive_diameter'])/2)
    gear_profile_info = "\nSimple circle (no-gear-profile):\n"
    gear_profile_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(gw_c['gear_primitive_diameter']/2.0, gw_c['gear_primitive_diameter'])
    gear_profile_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(g1_ix, g1_iy)
    minimal_gear_profile_radius = float(gw_c['gear_primitive_diameter'])/2
    g1_m = 10.0
  ### default value for wheel_hollow
  axle_radius = axle_diameter/2.0
  if(axle_radius == 0): # if axle = none
    axle_radius = 1.0
  if(axle_radius>minimal_gear_profile_radius-radian_epsilon): # non sense case
    print("ERR218: Error, axle_radius {:0.3f} is bigger than minimal_gear_profile_radius {:0.3f}".format(axle_radius, minimal_gear_profile_radius))
    sys.exit(2)
  wheel_hollow_external_radius = gw_c['wheel_hollow_external_diameter']/2.0
  wheel_hollow_internal_radius = gw_c['wheel_hollow_internal_diameter']/2.0
  wheel_hollow_leg_number = gw_c['wheel_hollow_leg_number']
  if(wheel_hollow_leg_number>0):
    if(wheel_hollow_external_radius==0): # set the default value
      wheel_hollow_external_radius = minimal_gear_profile_radius - 2.5*g1_m
      if(wheel_hollow_external_radius<axle_radius+2.1*wheel_hollow_router_bit_radius): # remove the default value
        print("WARN224: Warning, the wheel_hollow_external_radius default value {:0.3f} can not be set!".format(wheel_hollow_external_radius))
        wheel_hollow_external_radius = 0
        wheel_hollow_leg_number = 0
    if(wheel_hollow_internal_radius==0): # set the default value
      #wheel_hollow_internal_radius = 2.0*axle_radius
      wheel_hollow_internal_radius = axle_radius + 1.0*gw_c['wheel_hollow_leg_width']
      if(wheel_hollow_internal_radius>wheel_hollow_external_radius-2.1*wheel_hollow_router_bit_radius): # remove the default value
        print("WARN228: Warning, the wheel_hollow_internal_radius default value {:0.3f} can not be set!".format(wheel_hollow_internal_radius))
        wheel_hollow_internal_radius = 0
        wheel_hollow_leg_number = 0
    if(gw_c['wheel_hollow_router_bit_radius']==0): # set the default value
      wheel_hollow_router_bit_radius = (wheel_hollow_external_radius-wheel_hollow_internal_radius)/5.0
      if(wheel_hollow_router_bit_radius<gw_c['cnc_router_bit_radius']):
        print("WARN233: Warning, the wheel_hollow_router_bit_radius default value {:0.3f} can not be set!".format(wheel_hollow_router_bit_radius))
        wheel_hollow_router_bit_radius = gw_c['cnc_router_bit_radius']
  ### check parameter coherence (part 2)
  if(wheel_hollow_leg_number>0):
    # wheel_hollow_external_diameter
    if(wheel_hollow_external_radius > minimal_gear_profile_radius-radian_epsilon):
      print("ERR733: Error, wheel_hollow_external_radius {:0.2f} is bigger than the gear_hollow_radius {:0.2f}!".format(wheel_hollow_external_radius, minimal_gear_profile_radius))
      sys.exit(2)
    if(wheel_hollow_external_radius < wheel_hollow_internal_radius+2*wheel_hollow_router_bit_radius+radian_epsilon):
      print("ERR734: Error, wheel_hollow_external_radius {:0.2f} is too small compare to wheel_hollow_internal_radius {:0.2f} and wheel_hollow_router_bit_radius {:0.2f}!".format(wheel_hollow_external_radius, wheel_hollow_internal_radius, wheel_hollow_router_bit_radius))
      sys.exit(2)
    # wheel_hollow_leg_width
    if(gw_c['wheel_hollow_leg_width']<radian_epsilon):
      print("ERR735: Error, wheel_hollow_leg_width {:0.2f} is too small!".format(gw_c['wheel_hollow_leg_width']))
      sys.exit(2)
    # wheel_hollow_internal_diameter
    if(wheel_hollow_internal_radius<axle_radius+radian_epsilon):
      print("ERR736: Error, wheel_hollow_internal_radius {:0.2f} is too small compare to axle_radius {:0.2f}!".format(wheel_hollow_internal_radius, axle_radius))
      sys.exit(2)
    if(2*wheel_hollow_internal_radius<gw_c['wheel_hollow_leg_width']+2*radian_epsilon):
      print("ERR736: Error, wheel_hollow_internal_radius {:0.2f} is too small compare to wheel_hollow_leg_width {:0.2f}!".format(wheel_hollow_internal_radius, gw_c['wheel_hollow_leg_width']))
      sys.exit(2)
  if(gw_c['crenel_number']>0):
    #print("dbg305: crenel_type {:s}".format(crenel_type))
    if(crenel_type=='rectangle'):
      if(math.sqrt((crenel_radius+gw_c['crenel_height'])**2+(gw_c['crenel_width']/2)**2)> minimal_gear_profile_radius-radian_epsilon):
        print("ERR298: Error, crenel_radius {:0.3f}, crenel_height {:0.3f} or crenel_width {:0.3f} are too big compare to minimal_gear_profile_radius {:0.3f}".format(crenel_radius, gw_c['crenel_height'], gw_c['crenel_width'], minimal_gear_profile_radius))
        sys.exit(2)
    elif(crenel_type=='circle'):
      if((crenel_radius+gw_c['crenel_width']/2)>minimal_gear_profile_radius-radian_epsilon):
        print("ERR311: Error, crenel_radius {:0.3f} or crenel_width {:0.3f} are too big compare to minimal_gear_profile_radius {:0.3f}".format(crenel_radius, gw_c['crenel_width'], minimal_gear_profile_radius))
        sys.exit(2)
    if(crenel_radius<radian_epsilon):
      print("ERR301: Error, the crenel_radius {:0.3f} is too small".format(crenel_radius))
      sys.exit(2)
    if(abs(gw_c['crenel_width'])>2*crenel_radius-radian_epsilon):
      print("ERR304: Error, crenel_width {:0.3f} is too big compare to crenel_radius {:0.3f}".format(gw_c['crenel_width'], crenel_radius))
      sys.exit(2)
    crenel_half_width_angle = math.asin(gw_c['crenel_width']/(2*crenel_radius))
    if(crenel_half_width_angle*2.2>2*math.pi/gw_c['crenel_number']):
      print("ERR305: Error, the crenel_number {:d} or crenel_width {:0.3f} are too big!".format(gw_c['crenel_number'], gw_c['crenel_width']))
      sys.exit(2)
    if(gw_c['crenel_width']<3.2*crenel_router_bit_radius):
      print("ERR308: Error, crenel_width {:0.3f} is too small compare to crenel_router_bit_radius {:0.3f}".format(gw_c['crenel_width'], crenel_router_bit_radius))
      sys.exit(2)

  ### crenel preparation
  crenel_axle_merge = False
  if((gw_c['crenel_number']>0)and(gw_c['axle_type']=='circle')and(gw_c['crenel_type']=='rectangle')and(crenel_radius==axle_radius)): # crenel and axle are merged in one outline
    crenel_axle_merge = True
  crenel_rectangle_type = 1
  if(gw_c['crenel_height']<3.0*crenel_router_bit_radius):
    crenel_rectangle_type = 2
  if(gw_c['crenel_number']>0):
    crenel_portion_angle = 2*math.pi/gw_c['crenel_number']
  # check for crenel_mark_nb: now, crenel-mark is implemented for configuration circle and merged-rectangle, but not for independant-rectangle
  #if((gw_c['crenel_mark_nb']>0)and(gw_c['crenel_type']!='circle')):
  #  print("WARN359: Warning, crenel_mark_nb {:d} is bigger than zero and crenel_type {:s} is not set to circle".format(gw_c['crenel_mark_nb'], gw_c['crenel_type']))

  ### axle
  axle_figure = []
  axle_figure_overlay = []
  if(gw_c['axle_type']=='circle'):
    if(not crenel_axle_merge):
      axle_figure.append([g1_ix, g1_iy, axle_radius])
    else:
      axle_A = [(g1_ix+axle_radius*math.cos(-1*crenel_half_width_angle), g1_iy+axle_radius*math.sin(-1*crenel_half_width_angle), 0)]
      if(crenel_rectangle_type==1):
        crenel_A = [
          (g1_ix+axle_radius+gw_c['crenel_height'], g1_iy-gw_c['crenel_width']/2.0, -1*crenel_router_bit_radius),
          (g1_ix+axle_radius+gw_c['crenel_height'], g1_iy+gw_c['crenel_width']/2.0, -1*crenel_router_bit_radius),
          (g1_ix+axle_radius*math.cos(1*crenel_half_width_angle), g1_iy+axle_radius*math.sin(1*crenel_half_width_angle), 0)]
        crenel_A_marked = crenel_A[:]
        crenel_A_marked[-1] = (crenel_A[-1][0], crenel_A[-1][1], gw_c['crenel_height']/2.0)
      elif(crenel_rectangle_type==2):
        tmp_l = crenel_router_bit_radius * (1+math.sqrt(2))
        crenel_A = [
          (g1_ix+axle_radius+gw_c['crenel_height']+1*tmp_l, g1_iy-gw_c['crenel_width']/2.0+0*tmp_l, 1*crenel_router_bit_radius),
          (g1_ix+axle_radius+gw_c['crenel_height']+0*tmp_l, g1_iy-gw_c['crenel_width']/2.0+1*tmp_l, 0*crenel_router_bit_radius),
          (g1_ix+axle_radius+gw_c['crenel_height']+0*tmp_l, g1_iy+gw_c['crenel_width']/2.0-1*tmp_l, 0*crenel_router_bit_radius),
          (g1_ix+axle_radius+gw_c['crenel_height']+1*tmp_l, g1_iy+gw_c['crenel_width']/2.0-0*tmp_l, 1*crenel_router_bit_radius),
          (g1_ix+axle_radius*math.cos(1*crenel_half_width_angle), g1_iy+axle_radius*math.sin(1*crenel_half_width_angle), 0)]
        crenel_A_marked = crenel_A[:]
        crenel_A_marked[-1] = (crenel_A[-1][0], crenel_A[-1][1], gw_c['crenel_height']/2.0)
      arc_half_angle = (crenel_portion_angle - 2*crenel_half_width_angle)/2.0
      arc_middle_a = crenel_half_width_angle + arc_half_angle
      arc_end_a = arc_middle_a + arc_half_angle
      crenel_A.append((g1_ix+axle_radius*math.cos(arc_middle_a), g1_iy+axle_radius*math.sin(arc_middle_a), g1_ix+axle_radius*math.cos(arc_end_a), g1_iy+axle_radius*math.sin(arc_end_a), 0))
      crenel_A_marked.append(crenel_A[-1])
      for i in range(gw_c['crenel_number']):
        if(i<gw_c['crenel_mark_nb']):
          crenel_A_selected = crenel_A_marked
        else:
          crenel_A_selected = crenel_A
        axle_A.extend(cnc25d_api.outline_rotate(crenel_A_selected, g1_ix, g1_iy, i*crenel_portion_angle))
      axle_A[-1] = (axle_A[-1][0], axle_A[-1][1], axle_A[0][0], axle_A[0][1], 0)
      axle_A_rotated = cnc25d_api.outline_rotate(axle_A, g1_ix, g1_iy, gw_c['crenel_angle'])
      axle_figure.append(cnc25d_api.cnc_cut_outline(axle_A_rotated, "axle_and_crenel"))
      axle_figure_overlay.append(cnc25d_api.ideal_outline(axle_A_rotated, "axle_and_crenel"))
  elif(gw_c['axle_type']=='rectangle'):
    axle_A = [
      [g1_ix-gw_c['axle_x_width']/2.0, g1_iy-gw_c['axle_y_width']/2.0, -1*axle_router_bit_radius],
      [g1_ix+gw_c['axle_x_width']/2.0, g1_iy-gw_c['axle_y_width']/2.0, -1*axle_router_bit_radius],
      [g1_ix+gw_c['axle_x_width']/2.0, g1_iy+gw_c['axle_y_width']/2.0, -1*axle_router_bit_radius],
      [g1_ix-gw_c['axle_x_width']/2.0, g1_iy+gw_c['axle_y_width']/2.0, -1*axle_router_bit_radius]]
    axle_A = cnc25d_api.outline_close(axle_A)
    axle_figure.append(cnc25d_api.cnc_cut_outline(axle_A, "axle_A"))
    axle_figure_overlay.append(cnc25d_api.ideal_outline(axle_A, "axle_A"))

  ### crenel
  #crenel_template
  if(gw_c['crenel_number']>0):
    if((crenel_type=='rectangle')and(not crenel_axle_merge)):
      if(crenel_rectangle_type==1):
        template_crenel = [
          (g1_ix+crenel_radius+0*gw_c['crenel_height'], g1_iy-1*gw_c['crenel_width']/2.0, -1*crenel_router_bit_radius),
          (g1_ix+crenel_radius+1*gw_c['crenel_height'], g1_iy-1*gw_c['crenel_width']/2.0, -1*crenel_router_bit_radius),
          (g1_ix+crenel_radius+1*gw_c['crenel_height'], g1_iy+1*gw_c['crenel_width']/2.0, -1*crenel_router_bit_radius),
          (g1_ix+crenel_radius+0*gw_c['crenel_height'], g1_iy+1*gw_c['crenel_width']/2.0, -1*crenel_router_bit_radius)]
      elif(crenel_rectangle_type==2):
        tmp_l = crenel_router_bit_radius * (1+math.sqrt(2))
        template_crenel = [
          (g1_ix+crenel_radius+0*gw_c['crenel_height']-1*tmp_l, g1_iy-1*gw_c['crenel_width']/2.0+0*tmp_l, 1*crenel_router_bit_radius),
          (g1_ix+crenel_radius+1*gw_c['crenel_height']+1*tmp_l, g1_iy-1*gw_c['crenel_width']/2.0+0*tmp_l, 1*crenel_router_bit_radius),
          (g1_ix+crenel_radius+1*gw_c['crenel_height']+0*tmp_l, g1_iy-1*gw_c['crenel_width']/2.0+1*tmp_l, 0*crenel_router_bit_radius),
          (g1_ix+crenel_radius+1*gw_c['crenel_height']+0*tmp_l, g1_iy+1*gw_c['crenel_width']/2.0-1*tmp_l, 0*crenel_router_bit_radius),
          (g1_ix+crenel_radius+1*gw_c['crenel_height']+1*tmp_l, g1_iy+1*gw_c['crenel_width']/2.0-0*tmp_l, 1*crenel_router_bit_radius),
          (g1_ix+crenel_radius+0*gw_c['crenel_height']-1*tmp_l, g1_iy+1*gw_c['crenel_width']/2.0-0*tmp_l, 1*crenel_router_bit_radius),
          (g1_ix+crenel_radius+0*gw_c['crenel_height']-0*tmp_l, g1_iy+1*gw_c['crenel_width']/2.0-1*tmp_l, 0*crenel_router_bit_radius),
          (g1_ix+crenel_radius+0*gw_c['crenel_height']-0*tmp_l, g1_iy-1*gw_c['crenel_width']/2.0+1*tmp_l, 0*crenel_router_bit_radius)]
      template_crenel = cnc25d_api.outline_close(template_crenel)
      for i in range(gw_c['crenel_number']):
        crenel_A = cnc25d_api.outline_rotate(template_crenel, g1_ix, g1_iy, gw_c['crenel_angle']+i*crenel_portion_angle)
        axle_figure.append(cnc25d_api.cnc_cut_outline(crenel_A, "crenel_A"))
        axle_figure_overlay.append(cnc25d_api.ideal_outline(crenel_A, "crenel_A"))
    elif(crenel_type=='circle'):
      for i in range(gw_c['crenel_number']):
        ta = gw_c['crenel_angle']+i*crenel_portion_angle
        if(i<gw_c['crenel_mark_nb']):
          axle_figure.append(marked_circle_crenel(g1_ix+crenel_radius*math.cos(ta), g1_iy++crenel_radius*math.sin(ta), gw_c['crenel_width']/2.0, ta+math.pi/2, crenel_router_bit_radius))
        else:
          axle_figure.append((g1_ix+crenel_radius*math.cos(ta), g1_iy++crenel_radius*math.sin(ta), gw_c['crenel_width']/2.0))
  #print("dbg435: axle_figure:", axle_figure)

  ### wheel hollow (a.k.a legs)
  wheel_hollow_figure = []
  wheel_hollow_figure_overlay = []
  if(wheel_hollow_leg_number>0):
    wh_angle = 2*math.pi/wheel_hollow_leg_number
    wh_leg_top_angle1 = math.asin(float(gw_c['wheel_hollow_leg_width']/2.0+wheel_hollow_router_bit_radius)/(wheel_hollow_external_radius-wheel_hollow_router_bit_radius))
    if(wh_angle<2*wh_leg_top_angle1+radian_epsilon):
      print("ERR664: Error, wh_angle {:0.2f} too small compare to wh_leg_top_angle1 {:0.2f}!".format(wh_angle, wh_leg_top_angle1))
      sys.exit(2)
    wh_leg_bottom_angle1 = math.asin(float(gw_c['wheel_hollow_leg_width']/2.0+wheel_hollow_router_bit_radius)/(wheel_hollow_internal_radius+wheel_hollow_router_bit_radius))
    #wh_leg_top_angle2 = math.asin((gw_c['wheel_hollow_leg_width']/2)/wheel_hollow_external_radius)
    wh_leg_top_angle2 = math.asin(float(gw_c['wheel_hollow_leg_width'])/(2*wheel_hollow_external_radius))
    #wh_leg_bottom_angle2 = math.asin((gw_c['wheel_hollow_leg_width']/2)/wheel_hollow_internal_radius)
    wh_leg_bottom_angle2 = math.asin(float(gw_c['wheel_hollow_leg_width'])/(2*wheel_hollow_internal_radius))
    # angular coordinates of the points
    wh_top1_a = gw_c['wheel_hollow_leg_angle']+wh_leg_top_angle2
    wh_top2_a = gw_c['wheel_hollow_leg_angle']+wh_angle/2.0
    wh_top3_a = gw_c['wheel_hollow_leg_angle']+wh_angle-wh_leg_top_angle2
    wh_bottom1_a = gw_c['wheel_hollow_leg_angle']+wh_leg_bottom_angle2
    wh_bottom2_a = gw_c['wheel_hollow_leg_angle']+wh_angle/2.0
    wh_bottom3_a = gw_c['wheel_hollow_leg_angle']+wh_angle-wh_leg_bottom_angle2
    # Cartesian coordinates of the points
    wh_top1_x = g1_ix + wheel_hollow_external_radius*math.cos(wh_top1_a)
    wh_top1_y = g1_iy + wheel_hollow_external_radius*math.sin(wh_top1_a)
    wh_top2_x = g1_ix + wheel_hollow_external_radius*math.cos(wh_top2_a)
    wh_top2_y = g1_iy + wheel_hollow_external_radius*math.sin(wh_top2_a)
    wh_top3_x = g1_ix + wheel_hollow_external_radius*math.cos(wh_top3_a)
    wh_top3_y = g1_iy + wheel_hollow_external_radius*math.sin(wh_top3_a)
    wh_bottom1_x = g1_ix + wheel_hollow_internal_radius*math.cos(wh_bottom1_a)
    wh_bottom1_y = g1_iy + wheel_hollow_internal_radius*math.sin(wh_bottom1_a)
    wh_bottom2_x = g1_ix + wheel_hollow_internal_radius*math.cos(wh_bottom2_a)
    wh_bottom2_y = g1_iy + wheel_hollow_internal_radius*math.sin(wh_bottom2_a)
    wh_bottom3_x = g1_ix + wheel_hollow_internal_radius*math.cos(wh_bottom3_a)
    wh_bottom3_y = g1_iy + wheel_hollow_internal_radius*math.sin(wh_bottom3_a)
    # create one outline
    if(wh_angle<2*wh_leg_bottom_angle1+radian_epsilon):
      wh_outline_A = [
        [wh_top1_x, wh_top1_y, wheel_hollow_router_bit_radius],
        [wh_top2_x, wh_top2_y, wh_top3_x, wh_top3_y, wheel_hollow_router_bit_radius],
        [wh_bottom2_x, wh_bottom2_y, wheel_hollow_router_bit_radius]]
    else:
      wh_outline_A = [
        [wh_top1_x, wh_top1_y, wheel_hollow_router_bit_radius],
        [wh_top2_x, wh_top2_y, wh_top3_x, wh_top3_y, wheel_hollow_router_bit_radius],
        [wh_bottom3_x, wh_bottom3_y, wheel_hollow_router_bit_radius],
        [wh_bottom2_x, wh_bottom2_y, wh_bottom1_x, wh_bottom1_y, wheel_hollow_router_bit_radius]]
    wh_outline_A = cnc25d_api.outline_close(wh_outline_A)
    wh_outline_B = cnc25d_api.cnc_cut_outline(wh_outline_A, "wheel_hollow")
    wh_outline_B_ideal = cnc25d_api.ideal_outline(wh_outline_A, "wheel_hollow")
    for i in range(wheel_hollow_leg_number):
      wheel_hollow_figure.append(cnc25d_api.outline_rotate(wh_outline_B, g1_ix, g1_iy, i*wh_angle))
      wheel_hollow_figure_overlay.append(cnc25d_api.outline_rotate(wh_outline_B_ideal, g1_ix, g1_iy, i*wh_angle))

  ### design output
  gw_figure = [gear_profile_B]
  gw_figure.extend(axle_figure)
  gw_figure.extend(wheel_hollow_figure)
  # ideal_outline in overlay
  gw_figure_overlay = []
  gw_figure_overlay.extend(axle_figure_overlay)
  gw_figure_overlay.extend(wheel_hollow_figure_overlay)
  # gearwheel_parameter_info
  gearwheel_parameter_info = "\nGearwheel parameter info:\n"
  gearwheel_parameter_info += "\n" + gw_c['args_in_txt'] + "\n\n"
  gearwheel_parameter_info += gear_profile_info
  gearwheel_parameter_info += """
axle_type:    \t{:s}
axle_x_width: \t{:0.3f}
axle_y_width: \t{:0.3f}
crenel_number:  \t{:d}
crenel_type:    \t{:s}
crenel_mark_nb: \t{:d}
crenel_diameter:\t{:0.3f}
""".format(gw_c['axle_type'], gw_c['axle_x_width'], gw_c['axle_y_width'], gw_c['crenel_number'], crenel_type, gw_c['crenel_mark_nb'], 2*crenel_radius)
  gearwheel_parameter_info += """
wheel_hollow_leg_number:        \t{:d}
wheel_hollow_leg_width:         \t{:0.3f}
wheel_hollow_external_radius:   \t{:0.3f}   \tdiameter: {:0.3f}
wheel_hollow_internal_radius:   \t{:0.3f}   \tdiameter: {:0.3f}
wheel_hollow_leg_angle:         \t{:0.3f}
""".format(wheel_hollow_leg_number, gw_c['wheel_hollow_leg_width'], wheel_hollow_external_radius, 2*wheel_hollow_external_radius, wheel_hollow_internal_radius, 2*wheel_hollow_internal_radius, gw_c['wheel_hollow_leg_angle'])
  gearwheel_parameter_info += """
gear_router_bit_radius:         \t{:0.3f}
wheel_hollow_router_bit_radius: \t{:0.3f}
axle_router_bit_radius:         \t{:0.3f}
cnc_router_bit_radius:          \t{:0.3f}
""".format(gear_router_bit_radius, wheel_hollow_router_bit_radius, axle_router_bit_radius, gw_c['cnc_router_bit_radius'])
  #print(gearwheel_parameter_info)

  # display with Tkinter
  if(gw_c['tkinter_view']):
    print(gearwheel_parameter_info)
    cnc25d_api.figure_simple_display(gw_figure, gw_figure_overlay, gearwheel_parameter_info)
  # generate output file
  cnc25d_api.generate_output_file(gw_figure, gw_c['output_file_basename'], gw_c['gear_profile_height'], gearwheel_parameter_info)

  ### return
  if(gw_c['return_type']=='int_status'):
    r_gw = 1
  elif(gw_c['return_type']=='cnc25d_figure'):
    r_gw = gw_figure
  elif(gw_c['return_type']=='freecad_object'):
    r_gw = cnc25d_api.figure_to_freecad_25d_part(gw_figure, gw_c['gear_profile_height'])
  else:
    print("ERR346: Error the return_type {:s} is unknown".format(gw_c['return_type']))
    sys.exit(2)
  return(r_gw)

################################################################
# gearwheel wrapper dance
################################################################

def gearwheel_argparse_to_dictionary(ai_gw_args):
  """ convert a gearwheel_argparse into a gearwheel_dictionary
  """
  r_gwd = {}
  r_gwd.update(gear_profile.gear_profile_argparse_to_dictionary(ai_gw_args, 1))
  ##### from gearwheel
  ### axle
  r_gwd['axle_type']                = ai_gw_args.sw_axle_type
  r_gwd['axle_x_width']             = ai_gw_args.sw_axle_x_width
  r_gwd['axle_y_width']             = ai_gw_args.sw_axle_y_width
  r_gwd['axle_router_bit_radius']   = ai_gw_args.sw_axle_router_bit_radius
  ### crenel
  r_gwd['crenel_number']       = ai_gw_args.sw_crenel_number
  r_gwd['crenel_type']         = ai_gw_args.sw_crenel_type
  r_gwd['crenel_mark_nb']      = ai_gw_args.sw_crenel_mark_nb
  r_gwd['crenel_diameter']     = ai_gw_args.sw_crenel_diameter
  r_gwd['crenel_angle']        = ai_gw_args.sw_crenel_angle
  r_gwd['crenel_width']        = ai_gw_args.sw_crenel_width
  r_gwd['crenel_height']       = ai_gw_args.sw_crenel_height
  r_gwd['crenel_router_bit_radius'] = ai_gw_args.sw_crenel_router_bit_radius
  ### wheel-hollow = legs
  r_gwd['wheel_hollow_leg_number']        = ai_gw_args.sw_wheel_hollow_leg_number
  r_gwd['wheel_hollow_leg_width']         = ai_gw_args.sw_wheel_hollow_leg_width
  r_gwd['wheel_hollow_leg_angle']         = ai_gw_args.sw_wheel_hollow_leg_angle
  r_gwd['wheel_hollow_internal_diameter'] = ai_gw_args.sw_wheel_hollow_internal_diameter
  r_gwd['wheel_hollow_external_diameter'] = ai_gw_args.sw_wheel_hollow_external_diameter
  r_gwd['wheel_hollow_router_bit_radius'] = ai_gw_args.sw_wheel_hollow_router_bit_radius
  ### cnc router_bit constraint
  r_gwd['cnc_router_bit_radius']          = ai_gw_args.sw_cnc_router_bit_radius
  ### design output : view the gearwheel with tkinter or write files
  #tkinter_view'] = tkinter_view
  r_gwd['output_file_basename'] = ai_gw_args.sw_output_file_basename
  r_gwd['return_type'] = ai_gw_args.sw_return_type
  ### optional
  #r_gwd['args_in_txt'] = ''
  #### return
  return(r_gwd)

def gearwheel_argparse_wrapper(ai_gw_args, ai_args_in_txt=""):
  """
  wrapper function of gearwheel() to call it using the gearwheel_parser.
  gearwheel_parser is mostly used for debug and non-regression tests.
  """
  # view the gearwheel with Tkinter as default action
  tkinter_view = True
  if(ai_gw_args.sw_simulation_enable or (ai_gw_args.sw_output_file_basename!='')):
    tkinter_view = False
  # wrapper
  gwd = gearwheel_argparse_to_dictionary(ai_gw_args)
  gwd['args_in_txt'] = ai_args_in_txt
  gwd['tkinter_view'] = tkinter_view
  #gwd['return_type'] = 'int_status'
  r_gw = gearwheel(gwd)
  return(r_gw)

################################################################
# self test
################################################################

def gearwheel_self_test():
  """
  This is the non-regression test of gearwheel.
  Look at the simulation Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"                  , "--gear_tooth_nb 21 --gear_module 10.0 --axle_type rectangle --axle_x_width 30 --axle_y_width 40 --axle_router_bit_radius 8.0 --cnc_router_bit_radius 3.0"],
    ["with gearwheel hollow 1 leg"    , "--gear_tooth_nb 25 --gear_module 10.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 20 --axle_router_bit_radius 4.0 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 20.0 --wheel_hollow_leg_angle 0.9 --wheel_hollow_internal_diameter 60.0 --wheel_hollow_external_diameter 200.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gearwheel hollow 3 legs"   , "--gear_tooth_nb 24 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 3 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 40.0 --wheel_hollow_external_diameter 180.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gearwheel hollow 7 legs"   , "--gear_tooth_nb 23 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 7 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 30.0 --wheel_hollow_external_diameter 160.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gear_profile simulation"   , "--gear_tooth_nb 23 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 7 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 60.0 --wheel_hollow_external_diameter 160.0 --wheel_hollow_router_bit_radius 15.0 --second_gear_tooth_nb 18 --simulation"],
    ["output files"   , "--gear_tooth_nb 23 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 7 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 60.0 --wheel_hollow_external_diameter 160.0 --wheel_hollow_router_bit_radius 15.0 --second_gear_tooth_nb 18 --output_file_basename test_output/gearwheel_self_test.dxf"],
    ["no tooth"                       , "--gear_tooth_nb 0 --gear_primitive_diameter 100.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 20 --axle_router_bit_radius 3.0 --wheel_hollow_leg_number 4 --wheel_hollow_leg_width 10.0 --wheel_hollow_internal_diameter 40.0  --wheel_hollow_external_diameter 80.0 --wheel_hollow_router_bit_radius 8.0"],
    ["default value with wheel_hollow"     , "--gear_tooth_nb 35 --gear_module 10.0 --axle_type circle --axle_x_width 30 --wheel_hollow_leg_number 6 --wheel_hollow_leg_width 10.0"],
    ["default value without wheel_hollow"  , "--gear_tooth_nb 35 --gear_module 10.0 --axle_type circle --axle_x_width 300 --wheel_hollow_leg_number 6 --wheel_hollow_leg_width 10.0"],
    ["crenel on axle with big crenel_height", "--gear_tooth_nb 25 --gear_module 10 --axle_type circle --axle_x_width 50 --crenel_number 1"],
    ["crenel on axle with small crenel_height", "--gear_tooth_nb 25 --gear_module 10 --axle_type circle --axle_x_width 50 --crenel_number 8 --crenel_router_bit_radius 3 --crenel_width 17"],
    ["crenel with big crenel_height", "--gear_tooth_nb 25 --gear_module 10 --axle_type circle --axle_x_width 50 --crenel_number 4 --crenel_router_bit_radius 3 --crenel_width 20 --crenel_diameter 70 --crenel_height 10 --crenel_angle 0.1"],
    ["crenel with small crenel_height", "--gear_tooth_nb 25 --gear_module 10 --axle_type circle --axle_x_width 50 --crenel_number 8 --crenel_router_bit_radius 3 --crenel_width 20 --crenel_diameter 70"],
    ["crenel circle", "--gear_tooth_nb 19 --gear_module 1 --axle_type circle --axle_x_width 8 --crenel_number 6 --crenel_type circle --crenel_width 1.9 --crenel_diameter 12"],
    ["crenel circle marked", "--gear_tooth_nb 13 --gear_module 10 --axle_type circle --axle_x_width 50 --crenel_number 6 --crenel_type circle --crenel_width 5 --crenel_diameter 70 --crenel_mark_nb 2"],
    ["crenel rectangle marked", "--gear_tooth_nb 13 --gear_module 1 --axle_type circle --axle_x_width 6 --crenel_number 4 --crenel_type rectangle --crenel_width 2  --crenel_height 1 --crenel_mark_nb 3"],
    ["last test"                      , "--gear_tooth_nb 30 --gear_module 10.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function gearwheel().')
  gearwheel_parser = gearwheel_add_argument(gearwheel_parser)
  gearwheel_parser = cnc25d_api.generate_output_file_add_argument(gearwheel_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = gearwheel_parser.parse_args(l_args)
    r_gwst = gearwheel_argparse_wrapper(st_args)
  return(r_gwst)

################################################################
# gearwheel command line interface
################################################################

def gearwheel_cli(ai_args=""):
  """ command line interface of gearwheel.py when it is used in standalone
  """
  # gearwheel parser
  gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function gearwheel().')
  gearwheel_parser = gearwheel_add_argument(gearwheel_parser)
  gearwheel_parser = cnc25d_api.generate_output_file_add_argument(gearwheel_parser, 1)
  # switch for self_test
  gearwheel_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
  help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "gearwheel arguments: " + ' '.join(effective_args)
  gw_args = gearwheel_parser.parse_args(effective_args)
  print("dbg111: start making gearwheel")
  if(gw_args.sw_run_self_test):
    r_gw = gearwheel_self_test()
  else:
    r_gw = gearwheel_argparse_wrapper(gw_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_gw)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearwheel.py says hello!\n")
  #my_gw = gearwheel_cli()
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --output_file_basename test_output/toto2")
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --axle_type rectangle --axle_x_width 20 --axle_y_width 30 --axle_router_bit_radius 5")
  #my_gw = gearwheel_cli("--gear_tooth_nb 25 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 15 --axle_router_bit_radius 2.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 10.0 --return_type freecad_object")
  #my_gw = gearwheel_cli("--gear_tooth_nb 25 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 15 --axle_router_bit_radius 2.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 10.0")
  my_gw = gearwheel_cli("--gear_tooth_nb 25 --gear_module 10 --axle_type circle --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 10.0 --axle_x_width 50")
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0")
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename test_output/gearwheel_hat")
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0")
  #my_gw = gearwheel_cli("--gear_primitive_diameter 140.0 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0")
  #Part.show(my_gw)
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw1.svg")
  #my_gw = gearwheel_cli("--gear_primitive_diameter 140.0 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 3 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw2.svg")
  #my_gw = gearwheel_cli("--gear_tooth_nb 23 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type circle --axle_x_width 20 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 180.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw3.svg")
  try: # depending on gw_c['return_type'] it might be or not a freecad_object
    Part.show(my_gw)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")

