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
# inheritance from gear_profile
################################################################

def inherit_gear_profile(c={}):
  """ generate the gear_profile with the construct c
  """
  gp_c = c.copy()
  gp_c['gear_type'] = 'e'
  #gp_c['gear_router_bit_radius'] = c['gear_router_bit_radius']
  #gp_c['portion_tooth_nb'] = 0
  #gp_c['portion_first_end'] = 0
  #gp_c['portion_last_end'] = 0
  gp_c['cut_portion'] = [0, 0, 0]
  r_obj = gear_profile.gear_profile()
  r_obj.apply_external_constraint(gp_c)
  return(r_obj)

################################################################
# gearwheel constraint_constructor
################################################################

def gearwheel_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the gearwheel design
  """
  r_parser = ai_parser
  ### inherit arguments from gear_profile
  i_gear_profile = inherit_gear_profile()
  r_parser = i_gear_profile.get_constraint_constructor()(r_parser, 1)
  ### axle
  r_parser.add_argument('--axle_type','--at', action='store', default='none',
    help="Select the type of axle for the first gearwheel. Possible values: 'none', 'circle' and 'rectangle'. Default: 'none'")
  r_parser.add_argument('--axle_x_width','--axw', action='store', type=float, default=10.0,
    help="Set the axle cylinder diameter or the axle rectangle x-width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--axle_y_width','--ayw', action='store', type=float, default=10.0,
    help="Set the axle rectangle y-width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--axle_router_bit_radius','--arr', action='store', type=float, default=0.1,
    help="Set the router_bit radius of the first gearwheel rectangle axle. Default: 0.1")
  ### crenel
  r_parser.add_argument('--crenel_number','--cn', action='store', type=int, default=0,
    help="Set the number of crenels. The crenels are uniform distributed. The first crenel is centered on the crenel_angle. 0 means no crenel. Default: 0")
  r_parser.add_argument('--crenel_type','--ct', action='store', default='rectangle',
    help="Select the type of crenel for the first gearwheel. Possible values: 'rectangle' or 'circle'. Default: 'rectangle'")
  r_parser.add_argument('--crenel_mark_nb','--cmn', action='store', type=int, default=0,
    help="Set the number of crenels that must be marked. Default: 0")
  r_parser.add_argument('--crenel_diameter','--cd', action='store', type=float, default=0.0,
    help="Set the bottom diameter of the crenels. If equal to 0.0, it is set to the axle diameter. Default: 0.0")
  r_parser.add_argument('--crenel_angle','--ca', action='store', type=float, default=0.0,
    help="Set the angle position of the first crenel. Default: 0.0")
  r_parser.add_argument('--crenel_tooth_align','--cta', action='store', type=int, default=0,
    help="Set crenel aligned with teeth. Uncompatible with crenel_number and crenel_angle. Default: 0")
  r_parser.add_argument('--crenel_width','--cw', action='store', type=float, default=10.0,
    help="Set the width (tangential size) of a crenel. Default: 10.0")
  r_parser.add_argument('--crenel_height','--ch', action='store', type=float, default=5.0,
    help="Set the height (radial size) of a crenel. Default: 5.0")
  r_parser.add_argument('--crenel_router_bit_radius','--crbr', action='store', type=float, default=0.1,
    help="Set the router_bit radius for the crenel. Default: 0.1")
  ### wheel-hollow = legs
  r_parser.add_argument('--wheel_hollow_leg_number','--whln', action='store', type=int, default=0,
    help="Set the number of legs for the wheel-hollow of the first gearwheel. The legs are uniform distributed. The first leg is centered on the leg_angle. 0 means no wheel-hollow. Default: 0")
  r_parser.add_argument('--wheel_hollow_leg_width','--whlw', action='store', type=float, default=10.0,
    help="Set the wheel-hollow leg width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--wheel_hollow_leg_angle','--whla', action='store', type=float, default=0.0,
    help="Set the wheel-hollow leg-angle of the first gearwheel. Default: 0.0")
  r_parser.add_argument('--wheel_hollow_internal_diameter','--whid', action='store', type=float, default=0.0,
    help="Set the wheel-hollow internal diameter of the first gearwheel. If equal to 0.0, it is set to twice the axle diameter. Default: 0.0")
  r_parser.add_argument('--wheel_hollow_external_diameter','--whed', action='store', type=float, default=0.0,
    help="Set the wheel-hollow external diameter of the first gearwheel. It must be bigger than the wheel_hollow_internal_diameter and smaller than the gear bottom diameter. If equal to 0.0 it is set to the gear-bottom-diameter minus the gear-module. Default: 0.0")
  r_parser.add_argument('--wheel_hollow_router_bit_radius','--whrr', action='store', type=float, default=0.0,
    help="Set the router_bit radius of the wheel-hollow of the first gearwheel. If equal to 0.0, it is set to a third of (wheel_hollow_external_diameter minus wheel_hollow_internal_diameter).Default: 0.0")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1,
    help="Set the minimum router_bit radius of the first gearwheel. It increases gear_router_bit_radius, axle_router_bit_radius and wheel_hollow_router_bit_radius if needed. Default: 0.1")
  # return
  return(r_parser)

################################################################
# gearwheel constraint_check
################################################################

def gearwheel_constraint_check(c):
  """ check the gearwheel constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  # get the router_bit_radius
  c['gear_rbr'] = c['gear_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['gear_rbr']):
    c['gear_rbr'] = c['cnc_router_bit_radius']
  c['crenel_rbr'] = c['crenel_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['crenel_rbr']):
    c['crenel_rbr'] = c['cnc_router_bit_radius']
  c['wheel_hollow_rbr'] = c['wheel_hollow_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['wheel_hollow_rbr']):
    c['wheel_hollow_rbr'] = c['cnc_router_bit_radius']
  c['axle_rbr'] = c['axle_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['axle_rbr']):
    c['axle_rbr'] = c['cnc_router_bit_radius']
  # c['axle_type']
  if(not c['axle_type'] in ('none', 'circle', 'rectangle')):
    print("ERR932: Error, axle_type {:s} is not valid!".format(c['axle_type']))
    sys.exit(2)
  # c['axle_x_width']
  axle_diameter = 0
  if(c['axle_type'] in('circle','rectangle')):
    if(c['axle_x_width']<2*c['axle_rbr']+radian_epsilon):
      print("ERR663: Error, axle_x_width {:0.2f} is too small compare to axle_router_bit_radius {:0.2f}!".format(c['axle_x_width'], c['axle_rbr']))
      sys.exit(2)
    axle_diameter = c['axle_x_width']
    # c['axle_y_width']
    if(c['axle_type']=='rectangle'):
      if(c['axle_y_width']<2*c['axle_rbr']+radian_epsilon):
        print("ERR664: Error, axle_y_width {:0.2f} is too small compare to axle_router_bit_radius {:0.2f}!".format(c['axle_y_width'], c['axle_rbr']))
        sys.exit(2)
      axle_diameter = math.sqrt(c['axle_x_width']**2+c['axle_y_width']**2)
  # crenel_type
  if((c['crenel_type']!='rectangle')and(c['crenel_type']!='circle')):
    print("ERR213: Error, crenel_type {:s} is unknown".format(c['crenel_type']))
    sys.exit(2)
  # crenel_number
  crenel_increment_angle = 0.0
  if(c['crenel_number']>0):
    crenel_increment_angle = 2*math.pi/c['crenel_number']
  if(c['crenel_tooth_align']>0):
    if(c['crenel_number']>0):
      print("ERR255: Error, crenel_tooth_align {:d} and crenel_number {:d} are set together".format(c['crenel_tooth_align'], c['crenel_number']))
      sys.exit(2)
    if(c['crenel_angle']!=0):
      print("ERR258: Error, crenel_tooth_align {:d} and crenel_angle {:0.3f} are set together".format(c['crenel_tooth_align'], c['crenel_angle']))
      sys.exit(2)
    if(c['gear_tooth_nb']==0):
      print("ERR261: Error, crenel_tooth_align {:d} set and gear_tooth_nb {:d} is set to zero".format(c['crenel_tooth_align'], c['gear_tooth_nb']))
      sys.exit(2)
    c['crenel_number'] = int(c['gear_tooth_nb']/c['crenel_tooth_align'])
    c['crenel_angle'] = c['gear_initial_angle']
    crenel_increment_angle = c['crenel_tooth_align']*2*math.pi/c['gear_tooth_nb']
  #print("dbg266: crenel_number {:d}  crenel_angle {:0.3f}  crenel_increment_angle {:0.3f}".format(c['crenel_number'], c['crenel_angle'], crenel_increment_angle))
  # crenel_mark_nb
  if((c['crenel_mark_nb']<0)or(c['crenel_mark_nb']>c['crenel_number'])):
    print("ERR233: Error, crenel_mark_nb {:d} is out of the range 0..{:d}".format(c['crenel_mark_nb'], c['crenel_number']))
    sys.exit(2)
  # crenel_diameter
  crenel_diameter = c['crenel_diameter']
  if(crenel_diameter==0):
    crenel_diameter = axle_diameter
  if(crenel_diameter<axle_diameter):
    print("ERR212: Error, crenel_diameter {:0.3f} is smaller than the axle_diameter {:0.3f}".format(crenel_diameter, axle_diameter))
    sys.exit(2)
  c['crenel_radius'] = crenel_diameter/2.0
  # c['gear_tooth_nb']
  if(c['gear_tooth_nb']>0): # create a gear_profile
    ### inherit gear_profile
    i_gear_profile = inherit_gear_profile(c)
    gear_profile_parameters = i_gear_profile.get_constraint()
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    minimal_gear_profile_radius = gear_profile_parameters['g1_param']['hollow_radius']
    c['g1_ix'] = gear_profile_parameters['g1_param']['center_ox']
    c['g1_iy'] = gear_profile_parameters['g1_param']['center_oy']
    g1_m = gear_profile_parameters['g1_param']['module']
    c['addendum_radius'] = gear_profile_parameters['g1_param']['addendum_radius'] # for slice_xyz
  else: # no gear_profile, just a circle
    if(c['gear_primitive_diameter']<radian_epsilon):
      print("ERR885: Error, the no-gear-profile circle outline diameter gear_primitive_diameter {:0.2f} is too small!".format(c['gear_primitive_diameter']))
      sys.exit(2)
    c['g1_ix'] = c['center_position_x']
    c['g1_iy'] = c['center_position_y']
    minimal_gear_profile_radius = float(c['gear_primitive_diameter'])/2
    g1_m = 10.0
    c['addendum_radius'] = float(c['gear_primitive_diameter'])/2 # for slice_xyz
  ### default value for wheel_hollow
  c['axle_radius'] = axle_diameter/2.0
  if(c['axle_radius'] == 0): # if axle = none
    c['axle_radius'] = 1.0
  if(c['axle_radius']>minimal_gear_profile_radius-radian_epsilon): # non sense case
    print("ERR218: Error, axle_radius {:0.3f} is bigger than minimal_gear_profile_radius {:0.3f}".format(c['axle_radius'], minimal_gear_profile_radius))
    sys.exit(2)
  c['wheel_hollow_external_radius'] = c['wheel_hollow_external_diameter']/2.0
  c['wheel_hollow_internal_radius'] = c['wheel_hollow_internal_diameter']/2.0
  if(c['wheel_hollow_leg_number']>0):
    if(c['wheel_hollow_external_radius']==0): # set the default value
      c['wheel_hollow_external_radius'] = minimal_gear_profile_radius - 2.5*g1_m
      if(c['wheel_hollow_external_radius']<c['axle_radius']+2.1*c['wheel_hollow_rbr']): # remove the default value
        print("WARN224: Warning, the wheel_hollow_external_radius default value {:0.3f} can not be set!".format(c['wheel_hollow_external_radius']))
        c['wheel_hollow_external_radius'] = 0
        c['wheel_hollow_leg_number'] = 0
    if(c['wheel_hollow_internal_radius']==0): # set the default value
      #c['wheel_hollow_internal_radius'] = 2.0*c['axle_radius']
      c['wheel_hollow_internal_radius'] = c['axle_radius'] + 1.0*c['wheel_hollow_leg_width']
      if(c['wheel_hollow_internal_radius']>c['wheel_hollow_external_radius']-2.1*c['wheel_hollow_rbr']): # remove the default value
        print("WARN228: Warning, the wheel_hollow_internal_radius default value {:0.3f} can not be set!".format(c['wheel_hollow_internal_radius']))
        c['wheel_hollow_internal_radius'] = 0
        c['wheel_hollow_leg_number'] = 0
    if(c['wheel_hollow_router_bit_radius']==0): # set the default value
      c['wheel_hollow_rbr'] = (c['wheel_hollow_external_radius']-c['wheel_hollow_internal_radius'])/5.0
      if(c['wheel_hollow_rbr']<c['cnc_router_bit_radius']):
        print("WARN233: Warning, the wheel_hollow_router_bit_radius default value {:0.3f} can not be set!".format(c['wheel_hollow_rbr']))
        c['wheel_hollow_rbr'] = c['cnc_router_bit_radius']
  ### check parameter coherence (part 2)
  if(c['wheel_hollow_leg_number']>0):
    # wheel_hollow_external_diameter
    if(c['wheel_hollow_external_radius'] > minimal_gear_profile_radius-radian_epsilon):
      print("ERR733: Error, wheel_hollow_external_radius {:0.2f} is bigger than the gear_hollow_radius {:0.2f}!".format(c['wheel_hollow_external_radius'], minimal_gear_profile_radius))
      sys.exit(2)
    if(c['wheel_hollow_external_radius'] < c['wheel_hollow_internal_radius']+2*c['wheel_hollow_rbr']+radian_epsilon):
      print("ERR734: Error, wheel_hollow_external_radius {:0.2f} is too small compare to wheel_hollow_internal_radius {:0.2f} and wheel_hollow_router_bit_radius {:0.2f}!".format(c['wheel_hollow_external_radius'], c['wheel_hollow_internal_radius'], c['wheel_hollow_rbr']))
      sys.exit(2)
    # wheel_hollow_leg_width
    if(c['wheel_hollow_leg_width']<radian_epsilon):
      print("ERR735: Error, wheel_hollow_leg_width {:0.2f} is too small!".format(c['wheel_hollow_leg_width']))
      sys.exit(2)
    # wheel_hollow_internal_diameter
    if(c['wheel_hollow_internal_radius']<c['axle_radius']+radian_epsilon):
      print("ERR736: Error, wheel_hollow_internal_radius {:0.2f} is too small compare to axle_radius {:0.2f}!".format(c['wheel_hollow_internal_radius'], c['axle_radius']))
      sys.exit(2)
    if(2*c['wheel_hollow_internal_radius']<c['wheel_hollow_leg_width']+2*radian_epsilon):
      print("ERR736: Error, wheel_hollow_internal_radius {:0.2f} is too small compare to wheel_hollow_leg_width {:0.2f}!".format(c['wheel_hollow_internal_radius'], c['wheel_hollow_leg_width']))
      sys.exit(2)
  if(c['crenel_number']>0):
    #print("dbg305: crenel_type {:s}".format(c['crenel_type']))
    if(c['crenel_type']=='rectangle'):
      if(math.sqrt((c['crenel_radius']+c['crenel_height'])**2+(c['crenel_width']/2)**2)> minimal_gear_profile_radius-radian_epsilon):
        print("ERR298: Error, crenel_radius {:0.3f}, crenel_height {:0.3f} or crenel_width {:0.3f} are too big compare to minimal_gear_profile_radius {:0.3f}".format(c['crenel_radius'], c['crenel_height'], c['crenel_width'], minimal_gear_profile_radius))
        sys.exit(2)
    elif(c['crenel_type']=='circle'):
      if((c['crenel_radius']+c['crenel_width']/2)>minimal_gear_profile_radius-radian_epsilon):
        print("ERR311: Error, crenel_radius {:0.3f} or crenel_width {:0.3f} are too big compare to minimal_gear_profile_radius {:0.3f}".format(c['crenel_radius'], c['crenel_width'], minimal_gear_profile_radius))
        sys.exit(2)
    if(c['crenel_radius']<radian_epsilon):
      print("ERR301: Error, the crenel_radius {:0.3f} is too small".format(c['crenel_radius']))
      sys.exit(2)
    if(abs(c['crenel_width'])>2*c['crenel_radius']-radian_epsilon):
      print("ERR304: Error, crenel_width {:0.3f} is too big compare to crenel_radius {:0.3f}".format(c['crenel_width'], c['crenel_radius']))
      sys.exit(2)
    c['crenel_half_width_angle'] = math.asin(c['crenel_width']/(2*c['crenel_radius']))
    if(c['crenel_half_width_angle']*2.2>crenel_increment_angle):
      print("ERR305: Error, the crenel_increment_angle {:0.3f} or crenel_width {:0.3f} are too big!".format(crenel_increment_angle, c['crenel_width']))
      sys.exit(2)
    if(c['crenel_width']<3.2*c['crenel_rbr']):
      print("ERR308: Error, crenel_width {:0.3f} is too small compare to crenel_router_bit_radius {:0.3f}".format(c['crenel_width'], c['crenel_rbr']))
      sys.exit(2)

  ### crenel preparation
  c['crenel_axle_merge'] = False
  if((c['crenel_number']>0)and(c['axle_type']=='circle')and(c['crenel_type']=='rectangle')and(c['crenel_radius']==c['axle_radius'])): # crenel and axle are merged in one outline
    c['crenel_axle_merge'] = True
  c['crenel_rectangle_type'] = 1
  if(c['crenel_height']<3.0*c['crenel_rbr']):
    c['crenel_rectangle_type'] = 2
  if(c['crenel_number']>0):
    c['crenel_portion_angle'] = crenel_increment_angle
  # check for crenel_mark_nb: now, crenel-mark is implemented for configuration circle and merged-rectangle, but not for independant-rectangle
  #if((c['crenel_mark_nb']>0)and(c['crenel_type']!='circle')):
  #  print("WARN359: Warning, crenel_mark_nb {:d} is bigger than zero and crenel_type {:s} is not set to circle".format(c['crenel_mark_nb'], c['crenel_type']))
  ###
  return(c)

  
################################################################
# sub-funcitons
################################################################

def marked_circle_crenel(ai_x, ai_y, ai_radius, ai_orientation, ai_router_bit_radius, ai_mark_type=2):
  """ generate the A-outline of a marked circle-crenel, centered on (ai_x, ai_y) and with the orientation ai_orientation
  """
  if(ai_mark_type==0):
    r_mcc = (ai_x, ai_y, ai_radius)
  elif(ai_mark_type==1):
    A_mcc = []
    A_mcc.append((ai_x+ai_radius*math.cos(ai_orientation-math.pi/4), ai_y+ai_radius*math.sin(ai_orientation-math.pi/4), 0))
    A_mcc.append((ai_x+math.sqrt(2)*ai_radius*math.cos(ai_orientation-0*math.pi/4), ai_y+math.sqrt(2)*ai_radius*math.sin(ai_orientation-0*math.pi/4), ai_router_bit_radius))
    A_mcc.append((ai_x+ai_radius*math.cos(ai_orientation+math.pi/4), ai_y+ai_radius*math.sin(ai_orientation+math.pi/4), 0))
    A_mcc.append((ai_x+ai_radius*math.cos(ai_orientation+math.pi), ai_y+ai_radius*math.sin(ai_orientation+math.pi), ai_x+ai_radius*math.cos(ai_orientation-math.pi/4), ai_y+ai_radius*math.sin(ai_orientation-math.pi/4), 0))
    #r_mcc = cnc25d_api.cnc_cut_outline(A_mcc, "marked_circle_crenel")
    r_mcc = A_mcc
  elif(ai_mark_type==2):
    A_mcc = []
    A_mcc.append((ai_x+ai_radius*math.cos(-math.pi/2), ai_y+ai_radius*math.sin(-math.pi/2), 0))
    A_mcc.append((ai_x+(1+math.sqrt(2))*ai_radius, ai_y-ai_radius, ai_router_bit_radius))
    A_mcc.append((ai_x+ai_radius*math.cos(math.pi/4), ai_y+ai_radius*math.sin(math.pi/4), 0))
    A_mcc.append((ai_x+ai_radius*math.cos(math.pi), ai_y+ai_radius*math.sin(math.pi), A_mcc[0][0], A_mcc[0][1], 0))
    #r_mcc = cnc25d_api.cnc_cut_outline(cnc25d_api.outline_rotate(A_mcc, ai_x, ai_y, ai_orientation), "marked_circle_crenel")
    r_mcc = cnc25d_api.outline_rotate(A_mcc, ai_x, ai_y, ai_orientation)
  else:
    print("ERR182: Error, ai_mark_type {:d} doesn't exist".format(ai_mark_type))
    sys.exit(2)
  return(r_mcc)
    
################################################################
# gearwheel 2D-figures construction
################################################################

def gearwheel_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the gearwheel design
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### axle
  axle_figure = []
  if(c['axle_type']=='circle'):
    if(not c['crenel_axle_merge']):
      axle_figure.append([c['g1_ix'], c['g1_iy'], c['axle_radius']])
    else:
      axle_A = [(c['g1_ix']+c['axle_radius']*math.cos(-1*c['crenel_half_width_angle']), c['g1_iy']+c['axle_radius']*math.sin(-1*c['crenel_half_width_angle']), 0)]
      if(c['crenel_rectangle_type']==1):
        crenel_A = [
          (c['g1_ix']+c['axle_radius']+c['crenel_height'], c['g1_iy']-c['crenel_width']/2.0, -1*c['crenel_rbr']),
          (c['g1_ix']+c['axle_radius']+c['crenel_height'], c['g1_iy']+c['crenel_width']/2.0, -1*c['crenel_rbr']),
          (c['g1_ix']+c['axle_radius']*math.cos(1*c['crenel_half_width_angle']), c['g1_iy']+c['axle_radius']*math.sin(1*c['crenel_half_width_angle']), 0)]
        crenel_A_marked = crenel_A[:]
        crenel_A_marked[-1] = (crenel_A[-1][0], crenel_A[-1][1], 0.6*c['crenel_height'])
      elif(c['crenel_rectangle_type']==2):
        tmp_l = c['crenel_rbr'] * (1+math.sqrt(2))
        crenel_A = [
          (c['g1_ix']+c['axle_radius']+c['crenel_height']+1*tmp_l, c['g1_iy']-c['crenel_width']/2.0+0*tmp_l, 1*c['crenel_rbr']),
          (c['g1_ix']+c['axle_radius']+c['crenel_height']+0*tmp_l, c['g1_iy']-c['crenel_width']/2.0+1*tmp_l, 0*c['crenel_rbr']),
          (c['g1_ix']+c['axle_radius']+c['crenel_height']+0*tmp_l, c['g1_iy']+c['crenel_width']/2.0-1*tmp_l, 0*c['crenel_rbr']),
          (c['g1_ix']+c['axle_radius']+c['crenel_height']+1*tmp_l, c['g1_iy']+c['crenel_width']/2.0-0*tmp_l, 1*c['crenel_rbr']),
          (c['g1_ix']+c['axle_radius']*math.cos(1*c['crenel_half_width_angle']), c['g1_iy']+c['axle_radius']*math.sin(1*c['crenel_half_width_angle']), 0)]
        crenel_A_marked = crenel_A[:]
        crenel_A_marked[-1] = (crenel_A[-1][0], crenel_A[-1][1], 0.6*c['crenel_height'])
      arc_half_angle = (c['crenel_portion_angle'] - 2*c['crenel_half_width_angle'])/2.0
      arc_middle_a = c['crenel_half_width_angle'] + arc_half_angle
      arc_end_a = arc_middle_a + arc_half_angle
      crenel_A.append((c['g1_ix']+c['axle_radius']*math.cos(arc_middle_a), c['g1_iy']+c['axle_radius']*math.sin(arc_middle_a), c['g1_ix']+c['axle_radius']*math.cos(arc_end_a), c['g1_iy']+c['axle_radius']*math.sin(arc_end_a), 0))
      crenel_A_marked.append(crenel_A[-1])
      for i in range(c['crenel_number']):
        if(i<c['crenel_mark_nb']):
          crenel_A_selected = crenel_A_marked
        else:
          crenel_A_selected = crenel_A
        axle_A.extend(cnc25d_api.outline_rotate(crenel_A_selected, c['g1_ix'], c['g1_iy'], i*c['crenel_portion_angle']))
      axle_A[-1] = (axle_A[-1][0], axle_A[-1][1], axle_A[0][0], axle_A[0][1], 0)
      axle_A_rotated = cnc25d_api.outline_rotate(axle_A, c['g1_ix'], c['g1_iy'], c['crenel_angle'])
      axle_figure.append(axle_A_rotated)
  elif(c['axle_type']=='rectangle'):
    axle_A = [
      [c['g1_ix']-c['axle_x_width']/2.0, c['g1_iy']-c['axle_y_width']/2.0, -1*c['axle_rbr']],
      [c['g1_ix']+c['axle_x_width']/2.0, c['g1_iy']-c['axle_y_width']/2.0, -1*c['axle_rbr']],
      [c['g1_ix']+c['axle_x_width']/2.0, c['g1_iy']+c['axle_y_width']/2.0, -1*c['axle_rbr']],
      [c['g1_ix']-c['axle_x_width']/2.0, c['g1_iy']+c['axle_y_width']/2.0, -1*c['axle_rbr']]]
    axle_A = cnc25d_api.outline_close(axle_A)
    axle_figure.append(axle_A)

  ### crenel
  #crenel_template
  if(c['crenel_number']>0):
    if((c['crenel_type']=='rectangle')and(not c['crenel_axle_merge'])):
      if(c['crenel_rectangle_type']==1):
        template_crenel = [
          (c['g1_ix']+c['crenel_radius']+0*c['crenel_height'], c['g1_iy']-1*c['crenel_width']/2.0, -1*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+1*c['crenel_height'], c['g1_iy']-1*c['crenel_width']/2.0, -1*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+1*c['crenel_height'], c['g1_iy']+1*c['crenel_width']/2.0, -1*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+0*c['crenel_height'], c['g1_iy']+1*c['crenel_width']/2.0, -1*c['crenel_rbr'])]
      elif(c['crenel_rectangle_type']==2):
        tmp_l = c['crenel_rbr'] * (1+math.sqrt(2))
        template_crenel = [
          (c['g1_ix']+c['crenel_radius']+0*c['crenel_height']-1*tmp_l, c['g1_iy']-1*c['crenel_width']/2.0+0*tmp_l, 1*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+1*c['crenel_height']+1*tmp_l, c['g1_iy']-1*c['crenel_width']/2.0+0*tmp_l, 1*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+1*c['crenel_height']+0*tmp_l, c['g1_iy']-1*c['crenel_width']/2.0+1*tmp_l, 0*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+1*c['crenel_height']+0*tmp_l, c['g1_iy']+1*c['crenel_width']/2.0-1*tmp_l, 0*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+1*c['crenel_height']+1*tmp_l, c['g1_iy']+1*c['crenel_width']/2.0-0*tmp_l, 1*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+0*c['crenel_height']-1*tmp_l, c['g1_iy']+1*c['crenel_width']/2.0-0*tmp_l, 1*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+0*c['crenel_height']-0*tmp_l, c['g1_iy']+1*c['crenel_width']/2.0-1*tmp_l, 0*c['crenel_rbr']),
          (c['g1_ix']+c['crenel_radius']+0*c['crenel_height']-0*tmp_l, c['g1_iy']-1*c['crenel_width']/2.0+1*tmp_l, 0*c['crenel_rbr'])]
      template_crenel = cnc25d_api.outline_close(template_crenel)
      for i in range(c['crenel_number']):
        crenel_A = cnc25d_api.outline_rotate(template_crenel, c['g1_ix'], c['g1_iy'], c['crenel_angle']+i*c['crenel_portion_angle'])
        axle_figure.append(crenel_A)
    elif(c['crenel_type']=='circle'):
      for i in range(c['crenel_number']):
        ta = c['crenel_angle']+i*c['crenel_portion_angle']
        if(i<c['crenel_mark_nb']):
          axle_figure.append(marked_circle_crenel(c['g1_ix']+c['crenel_radius']*math.cos(ta), c['g1_iy']+c['crenel_radius']*math.sin(ta), c['crenel_width']/2.0, ta+math.pi/2, c['crenel_rbr']))
        else:
          axle_figure.append((c['g1_ix']+c['crenel_radius']*math.cos(ta), c['g1_iy']+c['crenel_radius']*math.sin(ta), c['crenel_width']/2.0))
  #print("dbg435: axle_figure:", axle_figure)

  ### wheel hollow (a.k.a legs)
  wheel_hollow_figure = []
  if(c['wheel_hollow_leg_number']>0):
    wh_angle = 2*math.pi/c['wheel_hollow_leg_number']
    wh_leg_top_angle1 = math.asin(float(c['wheel_hollow_leg_width']/2.0+c['wheel_hollow_rbr'])/(c['wheel_hollow_external_radius']-c['wheel_hollow_rbr']))
    if(wh_angle<2*wh_leg_top_angle1+radian_epsilon):
      print("ERR664: Error, wh_angle {:0.2f} too small compare to wh_leg_top_angle1 {:0.2f}!".format(wh_angle, wh_leg_top_angle1))
      sys.exit(2)
    wh_leg_bottom_angle1 = math.asin(float(c['wheel_hollow_leg_width']/2.0+c['wheel_hollow_rbr'])/(c['wheel_hollow_internal_radius']+c['wheel_hollow_rbr']))
    #wh_leg_top_angle2 = math.asin((c['wheel_hollow_leg_width']/2)/c['wheel_hollow_external_radius'])
    wh_leg_top_angle2 = math.asin(float(c['wheel_hollow_leg_width'])/(2*c['wheel_hollow_external_radius']))
    #wh_leg_bottom_angle2 = math.asin((c['wheel_hollow_leg_width']/2)/c['wheel_hollow_internal_radius'])
    wh_leg_bottom_angle2 = math.asin(float(c['wheel_hollow_leg_width'])/(2*c['wheel_hollow_internal_radius']))
    # angular coordinates of the points
    wh_top1_a = c['wheel_hollow_leg_angle']+wh_leg_top_angle2
    wh_top2_a = c['wheel_hollow_leg_angle']+wh_angle/2.0
    wh_top3_a = c['wheel_hollow_leg_angle']+wh_angle-wh_leg_top_angle2
    wh_bottom1_a = c['wheel_hollow_leg_angle']+wh_leg_bottom_angle2
    wh_bottom2_a = c['wheel_hollow_leg_angle']+wh_angle/2.0
    wh_bottom3_a = c['wheel_hollow_leg_angle']+wh_angle-wh_leg_bottom_angle2
    # Cartesian coordinates of the points
    wh_top1_x = c['g1_ix'] + c['wheel_hollow_external_radius']*math.cos(wh_top1_a)
    wh_top1_y = c['g1_iy'] + c['wheel_hollow_external_radius']*math.sin(wh_top1_a)
    wh_top2_x = c['g1_ix'] + c['wheel_hollow_external_radius']*math.cos(wh_top2_a)
    wh_top2_y = c['g1_iy'] + c['wheel_hollow_external_radius']*math.sin(wh_top2_a)
    wh_top3_x = c['g1_ix'] + c['wheel_hollow_external_radius']*math.cos(wh_top3_a)
    wh_top3_y = c['g1_iy'] + c['wheel_hollow_external_radius']*math.sin(wh_top3_a)
    wh_bottom1_x = c['g1_ix'] + c['wheel_hollow_internal_radius']*math.cos(wh_bottom1_a)
    wh_bottom1_y = c['g1_iy'] + c['wheel_hollow_internal_radius']*math.sin(wh_bottom1_a)
    wh_bottom2_x = c['g1_ix'] + c['wheel_hollow_internal_radius']*math.cos(wh_bottom2_a)
    wh_bottom2_y = c['g1_iy'] + c['wheel_hollow_internal_radius']*math.sin(wh_bottom2_a)
    wh_bottom3_x = c['g1_ix'] + c['wheel_hollow_internal_radius']*math.cos(wh_bottom3_a)
    wh_bottom3_y = c['g1_iy'] + c['wheel_hollow_internal_radius']*math.sin(wh_bottom3_a)
    # create one outline
    if(wh_angle<2*wh_leg_bottom_angle1+radian_epsilon):
      wh_outline_A = [
        [wh_top1_x, wh_top1_y, c['wheel_hollow_rbr']],
        [wh_top2_x, wh_top2_y, wh_top3_x, wh_top3_y, c['wheel_hollow_rbr']],
        [wh_bottom2_x, wh_bottom2_y, c['wheel_hollow_rbr']]]
    else:
      wh_outline_A = [
        [wh_top1_x, wh_top1_y, c['wheel_hollow_rbr']],
        [wh_top2_x, wh_top2_y, wh_top3_x, wh_top3_y, c['wheel_hollow_rbr']],
        [wh_bottom3_x, wh_bottom3_y, c['wheel_hollow_rbr']],
        [wh_bottom2_x, wh_bottom2_y, wh_bottom1_x, wh_bottom1_y, c['wheel_hollow_rbr']]]
    wh_outline_A = cnc25d_api.outline_close(wh_outline_A)
    for i in range(c['wheel_hollow_leg_number']):
      wheel_hollow_figure.append(cnc25d_api.outline_rotate(wh_outline_A, c['g1_ix'], c['g1_iy'], i*wh_angle))


  ### design output
  gw_figure = []
  if(c['gear_tooth_nb']>0):
    i_gear_profile = inherit_gear_profile(c) # inherit from gear_profile
    gw_figure.extend(i_gear_profile.get_A_figure('first_gear'))
  else:
    gw_figure.append((c['g1_ix'], c['g1_iy'], float(c['gear_primitive_diameter'])/2))
  gw_figure.extend(axle_figure)
  gw_figure.extend(wheel_hollow_figure)
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['gearwheel_fig'] = gw_figure
  r_height['gearwheel_fig'] = c['gear_profile_height']
  ###
  return((r_figures, r_height))

################################################################
# gearwheel simulation
################################################################

def gearwheel_simulation_A(c):
  """ define the gearwheel simulation
  """
  # inherit from gear_profile
  i_gear_profile = inherit_gear_profile(c)
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def gearwheel_2d_simulations():
  """ return the dictionary defining the available simulation for gearwheel
  """
  r_sim = {}
  r_sim['gearwheel_simulation_A'] = gearwheel_simulation_A
  return(r_sim)


################################################################
# gearwheel 3D assembly-configuration construction
################################################################

def gearwheel_3d_construction(c):
  """ construct the 3D-assembly-configurations of the gearwheel
  """
  # conf1
  gearwheel_3dconf1 = []
  gearwheel_3dconf1.append(('gearwheel_fig',  0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['gearwheel_3dconf1'] = gearwheel_3dconf1
  fgr = c['addendum_radius'] # first gear addendum radius
  hh = c['gear_profile_height']/2.0 # half-height
  r_slice['gearwheel_3dconf1'] = (2*fgr,2*fgr,c['gear_profile_height'], c['center_position_x']-fgr,c['center_position_y']-fgr,0.0, [hh], [], [])
  #
  return((r_assembly, r_slice))


################################################################
# gearwheel_info
################################################################

def gearwheel_info(c):
  """ create the text info related to the gearwheel
  """
  r_info = ''
  if(c['gear_tooth_nb']>0): # with gear-profile (normal case)
    i_gear_profile = inherit_gear_profile(c) # inherit from gear_profile
    r_info += i_gear_profile.get_info()
  else: # when no gear-profile
    r_info += "\nSimple circle (no-gear-profile):\n"
    r_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(c['gear_primitive_diameter']/2.0, c['gear_primitive_diameter'])
    r_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(c['g1_ix'], c['g1_iy'])
  #
  r_info += """
axle_type:    \t{:s}
axle_x_width: \t{:0.3f}
axle_y_width: \t{:0.3f}
crenel_number:  \t{:d}
crenel_type:    \t{:s}
crenel_mark_nb: \t{:d}
crenel_diameter:\t{:0.3f}
""".format(c['axle_type'], c['axle_x_width'], c['axle_y_width'], c['crenel_number'], c['crenel_type'], c['crenel_mark_nb'], 2*c['crenel_radius'])
  r_info += """
wheel_hollow_leg_number:        \t{:d}
wheel_hollow_leg_width:         \t{:0.3f}
wheel_hollow_external_radius:   \t{:0.3f}   \tdiameter: {:0.3f}
wheel_hollow_internal_radius:   \t{:0.3f}   \tdiameter: {:0.3f}
wheel_hollow_leg_angle:         \t{:0.3f}
""".format(c['wheel_hollow_leg_number'], c['wheel_hollow_leg_width'], c['wheel_hollow_external_radius'], 2*c['wheel_hollow_external_radius'], c['wheel_hollow_internal_radius'], 2*c['wheel_hollow_internal_radius'], c['wheel_hollow_leg_angle'])
  r_info += """
gear_router_bit_radius:         \t{:0.3f}
wheel_hollow_router_bit_radius: \t{:0.3f}
axle_router_bit_radius:         \t{:0.3f}
cnc_router_bit_radius:          \t{:0.3f}
""".format(c['gear_rbr'], c['wheel_hollow_rbr'], c['axle_rbr'], c['cnc_router_bit_radius'])
  #print(r_info)
  #
  return(r_info)




################################################################
# self test
################################################################

def gearwheel_self_test():
  """
  This is the non-regression test of gearwheel.
  Look at the simulation Tk window to check errors.
  """
  r_tests = [
    ["simplest test"                  , "--gear_tooth_nb 21 --gear_module 10.0 --axle_type rectangle --axle_x_width 30 --axle_y_width 40 --axle_router_bit_radius 8.0 --cnc_router_bit_radius 3.0"],
    ["with gearwheel hollow 1 leg"    , "--gear_tooth_nb 25 --gear_module 10.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 20 --axle_router_bit_radius 4.0 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 20.0 --wheel_hollow_leg_angle 0.9 --wheel_hollow_internal_diameter 60.0 --wheel_hollow_external_diameter 200.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gearwheel hollow 3 legs"   , "--gear_tooth_nb 24 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 3 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 40.0 --wheel_hollow_external_diameter 180.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gearwheel hollow 7 legs"   , "--gear_tooth_nb 23 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 7 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 30.0 --wheel_hollow_external_diameter 160.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gear_profile simulation"   , "--gear_tooth_nb 23 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 7 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 60.0 --wheel_hollow_external_diameter 160.0 --wheel_hollow_router_bit_radius 15.0 --second_gear_tooth_nb 18 --simulate_2d"],
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
    ["crenel aligned", "--gear_tooth_nb 13 --gear_module 1 --axle_type circle --axle_x_width 6 --crenel_tooth_align 3 --crenel_type circle --crenel_width 0.9 --crenel_mark_nb 0 --crenel_diameter 8.5"],
    ["last test"                      , "--gear_tooth_nb 30 --gear_module 10.0"]]
  return(r_tests)

################################################################
# gearwheel design declaration
################################################################

class gearwheel(cnc25d_api.bare_design):
  """ gearwheel design
  """
  def __init__(self, constraint={}):
    """ configure the gearwheel design
    """
    self.design_setup(
      s_design_name             = "gearwheel",
      f_constraint_constructor  = gearwheel_constraint_constructor,
      f_constraint_check        = gearwheel_constraint_check,
      f_2d_constructor          = gearwheel_2d_construction,
      d_2d_simulation           = gearwheel_2d_simulations(),
      f_3d_constructor          = gearwheel_3d_construction,
      f_info                    = gearwheel_info,
      l_display_figure_list     = ['gearwheel_fig'],
      s_default_simulation      = '',
      l_2d_figure_file_list     = ['gearwheel_fig'],
      l_3d_figure_file_list     = ['gearwheel_fig'],
      l_3d_conf_file_list       = ['gearwheel_3dconf1'],
      f_cli_return_type         = None,
      l_self_test_list          = gearwheel_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearwheel.py says hello!\n")
  my_gw = gearwheel()
  #my_gw.cli()
  #my_gw.cli("--gear_tooth_nb 17 --output_file_basename test_output/toto2")
  #my_gw.cli("--gear_tooth_nb 17 --gear_module 10 --axle_type rectangle --axle_x_width 20 --axle_y_width 30 --axle_router_bit_radius 5")
  #my_gw.cli("--gear_tooth_nb 25 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 15 --axle_router_bit_radius 2.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 10.0 --return_type freecad_object")
  #my_gw.cli("--gear_tooth_nb 25 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 15 --axle_router_bit_radius 2.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 10.0")
  my_gw.cli("--gear_tooth_nb 25 --gear_module 10 --axle_type circle --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 10.0 --axle_x_width 50")
  #my_gw.cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0")
  #my_gw.cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename test_output/gearwheel_hat")
  #my_gw.cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0")
  #my_gw.cli("--gear_primitive_diameter 140.0 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0")
  #my_gw.cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw1.svg")
  #my_gw.cli("--gear_primitive_diameter 140.0 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 3 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw2.svg")
  #my_gw.cli("--gear_tooth_nb 23 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type circle --axle_x_width 20 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 180.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw3.svg")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_gw.get_fc_obj_3dconf('gearwheel_3dconf1'))

