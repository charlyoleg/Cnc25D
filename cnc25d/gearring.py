# gearring.py
# generates gearring and simulates gear.
# created by charlyoleg on 2013/09/26
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
gearring.py is a parametric generator of gearrings.
The main function return the gear-ring as FreeCAD Part object.
You can also simulate or view of the gearring and get a DXF, SVG or BRep file.
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
import gearwheel # gearwheel.marked_circle_crenel()


################################################################
# inheritance from gear_profile
################################################################

def inherit_gear_profile(c={}):
  """ generate the gear_profile with the construct c
  """
  gp_c = c.copy()
  gp_c['gear_type'] = 'i'
  gp_c['second_gear_type'] = 'e'
  #gp_c['gear_router_bit_radius'] = c['gear_router_bit_radius']
  gp_c['gearbar_slope'] = 0
  gp_c['gearbar_slope_n'] = 0
  #gp_c['portion_tooth_nb'] = 0
  #gp_c['portion_first_end'] = 0
  #gp_c['portion_last_end'] = 0
  gp_c['cut_portion'] = [0, 0, 0]
  r_obj = gear_profile.gear_profile()
  r_obj.apply_external_constraint(gp_c)
  return(r_obj)

################################################################
# gearring constraint_constructor
################################################################

def gearring_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the gearring design
  """
  r_parser = ai_parser
  ### inherit arguments from gear_profile
  if(ai_variant!=1):
    i_gear_profile = inherit_gear_profile()
    r_parser = i_gear_profile.get_constraint_constructor()(r_parser, 2)
  ### holder
  r_parser.add_argument('--holder_diameter','--hd', action='store', type=float, default=0.0,
    help="Set the holder diameter of the gearring. This is a mandatory input.")
  r_parser.add_argument('--holder_crenel_number','--hcn', action='store', type=int, default=4,
    help="Set the number of holder crenels (associated with a hole) arround the gearring holder. Default: 4")
  r_parser.add_argument('--holder_position_angle','--hpa', action='store', type=float, default=0.0,
    help="Set the holder position angle of the first holder-crenel (associated with a hole). Default: 0.0")
  if(ai_variant!=1):
    r_parser.add_argument('--holder_crenel_number_cut','--hcnc', action='store', type=int, default=0,
      help="Set the number of holder crenels to be cut for input/ouput holder. If set to 0, no cut is created. Default: 0")
  ### holder-hole
  r_parser.add_argument('--holder_hole_position_radius','--hhpr', action='store', type=float, default=0.0,
    help="Set the length between the center of the holder-hole and the center of the gearring. If it is equal to 0.0, the holder_diameter value is used. Default: 0.0")
  r_parser.add_argument('--holder_hole_diameter','--hhd', action='store', type=float, default=5.0,
    help="Set the diameter of the holder-hole. If equal to 0.0, there are no holder-hole. Default: 5.0")
  r_parser.add_argument('--holder_hole_mark_nb','--hhmn', action='store', type=int, default=0,
    help="Set the number of holder-hole that must be marked. Default: 0")
  r_parser.add_argument('--holder_double_hole_diameter','--hdhd', action='store', type=float, default=0.0,
    help="Set the diameter of the double-holes. If equal to 0.0, no double-holes is generated. Default: 0.0")
  r_parser.add_argument('--holder_double_hole_length','--hdhl', action='store', type=float, default=0.0,
    help="Set the length between the double-holes. If holder_double_hole_diameter is positive, holder_double_hole_length must be positive too. Default: 0.0")
  r_parser.add_argument('--holder_double_hole_position','--hdhp', action='store', type=float, default=0.0,
    help="Set radius position of the double-holes relative to the holder_hole. holder_double_hole_position can position or negative. Default: 0.0")
  r_parser.add_argument('--holder_double_hole_mark_nb','--hdhmn', action='store', type=int, default=0,
    help="Set the number of holder-double-hole that must be marked. Default: 0")
  ### holder-crenel
  r_parser.add_argument('--holder_crenel_position','--hcp', action='store', type=float, default=5.0,
    help="Set the length between the center of the holder-hole and the bottom of the holder-crenel. Default: 5.0")
  r_parser.add_argument('--holder_crenel_height','--hch', action='store', type=float, default=5.0,
    help="Set the height (or depth) of the holder-crenel. If equal to 0.0, no holder-crenels are made. Default: 5.0")
  r_parser.add_argument('--holder_crenel_width','--hcw', action='store', type=float, default=5.0,
    help="Set the width of the holder-crenel. The outline of the bottom of the holder-crenel depends on the relative value between holder_crenel_width and holder_crenel_router_bit_radius. Default: 5.0")
  r_parser.add_argument('--holder_crenel_skin_width','--hcsw', action='store', type=float, default=5.0,
    help="Set the width (or thickness) of the skin (or side-wall) of the holder-crenel. It must be bigger than 0.0. Default: 5.0")
  r_parser.add_argument('--holder_crenel_router_bit_radius','--hcrbr', action='store', type=float, default=1.0,
    help="Set the router_bit radius to make the holder-crenel. Default: 1.0")
  r_parser.add_argument('--holder_smoothing_radius','--hsr', action='store', type=float, default=0.0,
    help="Set the router_bit radius to smooth the inner corner between the holder cylinder and the holder-crenel side-wall. If equal to 0.0, the value of holder_crenel_position is used. Default: 0.0")
  ### holder-hole-B
  r_parser.add_argument('--holder_hole_B_diameter','--hhbd', action='store', type=float, default=5.0,
    help="Set the diameter of the holder-hole-B. If equal to 0.0, there are no holder-hole. Default: 5.0")
  r_parser.add_argument('--holder_crenel_B_position','--hcbp', action='store', type=float, default=5.0,
    help="Set the length between the center of the holder-hole-B and the bottom of the holder-crenel-B. Default: 5.0")
  r_parser.add_argument('--holder_hole_B_crenel_list','--hhbcl', action='store', nargs='*', default=[],
    help="Select the crenel that uses the parameter holder_hole_B_diameter instead to holder_hole_diameter")
  ### cnc router_bit constraint
  if(ai_variant!=1):
    r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=1.0,
      help="Set the minimum router_bit radius of the gearring. It increases gear_router_bit_radius, holder_crenel_router_bit_radius and holder_smoothing_radius if needed. Default: 1.0")
  # return
  return(r_parser)

################################################################
# gearring constraint_check
################################################################

def gearring_constraint_check(c):
  """ check the gearring constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  # get the router_bit_radius
  c['gear_rbr'] = c['gear_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['gear_rbr']):
    c['gear_rbr'] = c['cnc_router_bit_radius']
  c['holder_crenel_rbr'] = c['holder_crenel_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['holder_crenel_rbr']):
    c['holder_crenel_rbr'] = c['cnc_router_bit_radius']
  c['holder_sr'] = c['holder_smoothing_radius']
  if(c['cnc_router_bit_radius']>c['holder_sr']):
    c['holder_sr'] = c['cnc_router_bit_radius']
  # c['gear_tooth_nb']
  if(c['gear_tooth_nb']>0): # create a gear_profile
    ### inherit gear_profile
    i_gear_profile = inherit_gear_profile(c)
    gear_profile_parameters = i_gear_profile.get_constraint()
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    c['maximal_gear_profile_radius'] = gear_profile_parameters['g1_param']['hollow_radius']
    c['g1_ix'] = gear_profile_parameters['g1_param']['center_ox']
    c['g1_iy'] = gear_profile_parameters['g1_param']['center_oy']
    gear_module = gear_profile_parameters['g1_param']['module']
  else: # no gear_profile, just a circle
    if(c['gear_primitive_diameter']<radian_epsilon):
      print("ERR176: Error, the no-gear-profile circle outline diameter gear_primitive_diameter {:0.2f} is too small!".format(c['gear_primitive_diameter']))
      sys.exit(2)
    c['g1_ix'] = c['center_position_x']
    c['g1_iy'] = c['center_position_y']
    c['maximal_gear_profile_radius'] = float(c['gear_primitive_diameter'])/2
    gear_module = 0
  ### check parameter coherence (part 2)
  c['holder_radius'] = float(c['holder_diameter'])/2
  if(c['holder_radius']==0): # dynamic default value
    c['holder_radius'] = c['maximal_gear_profile_radius'] + 2.0*gear_module + c['holder_hole_diameter']/2.0
  if(c['holder_hole_position_radius']==0):
    c['holder_hole_position_radius'] = c['holder_radius']
  c['holder_hole_radius'] = float(c['holder_hole_diameter'])/2
  c['holder_maximal_radius'] = c['holder_hole_position_radius'] + c['holder_crenel_position'] + c['holder_crenel_height']
  holder_maximal_height = c['holder_maximal_radius'] - c['holder_radius']
  c['holder_crenel_half_width'] = float(c['holder_crenel_width'])/2
  holder_crenel_with_wall_half_width = c['holder_crenel_half_width'] + c['holder_crenel_skin_width']
  if(c['holder_radius']<holder_crenel_with_wall_half_width):
    print("ERR213: Error, holder_radius {:0.3f} must be bigger than holder_crenel_with_wall_half_width {:0.3f}".format(c['holder_radius'], holder_crenel_with_wall_half_width))
    sys.exit(2)
  c['holder_crenel_half_angle'] = math.asin(float(holder_crenel_with_wall_half_width)/c['holder_radius'])
  c['holder_crenel_x_position'] = math.sqrt((c['holder_radius'])**2 - (holder_crenel_with_wall_half_width)**2)
  additional_holder_maximal_height = c['holder_radius'] - c['holder_crenel_x_position']
  c['holder_maximal_height_plus'] = holder_maximal_height + additional_holder_maximal_height
  c['holder_side_outer_smoothing_radius'] = min(0.8*c['holder_crenel_skin_width'], float(c['holder_maximal_height_plus'])/4)
  holder_side_straigth_length = c['holder_maximal_height_plus'] - c['holder_side_outer_smoothing_radius']
  # check
  if(c['holder_smoothing_radius']==0):
    c['holder_sr'] = 0.9*holder_side_straigth_length
  if(c['cnc_router_bit_radius']>c['holder_sr']):
    c['holder_sr'] = c['cnc_router_bit_radius']
  # c['holder_crenel_height
  if(c['holder_crenel_number']>0):
    if((0.9*holder_side_straigth_length)<c['holder_sr']):
      print("ERR218: Error, the holder-crenel-wall-side height is too small: holder_side_straigth_length {:0.3f}  holder_smoothing_radius {:0.3f}".format(holder_side_straigth_length, c['holder_sr']))
      sys.exit(2)
  # c['holder_crenel_position']
  if(c['holder_crenel_position']<c['holder_hole_radius']):
    print("ERR211: Error, holder_crenel_position {:0.3f} is too small compare to holder_hole_radius {:0.3f}".format(c['holder_crenel_position'], c['holder_hole_radius']))
    sys.exit(2)
  # c['holder_crenel_width']
  if(c['holder_crenel_width']<2.1*c['holder_crenel_rbr']):
    print("ERR215: Error, holder_crenel_width {:0.3} is too small compare to holder_crenel_router_bit_radius {:0.3f}".format(c['holder_crenel_width'], c['holder_crenel_rbr']))
    sys.exit(2)
  # hollow_circle and holder-hole
  if(c['maximal_gear_profile_radius']>(c['holder_hole_position_radius']-c['holder_hole_radius'])):
    print("ERR303: Error, holder-hole are too closed from the gear_hollow_circle: maximal_gear_profile_radius {:0.3f}  holder_hole_position_radius {:0.3f}  holder_hole_radius {:0.3f}".format(c['maximal_gear_profile_radius'], c['holder_hole_position_radius'], c['holder_hole_radius']))
    sys.exit(2)
  # holder_hole_mark_nb
  if((c['holder_hole_mark_nb']<0)or(c['holder_hole_mark_nb']>c['holder_crenel_number'])):
    print("ERR294: Error, holder_hole_mark_nb {:d} is out of its range 0..{:d}".format(c['holder_hole_mark_nb'], c['holder_crenel_number']))
    sys.exit(2)
  # holder_double_hole
  c['holder_double_hole_radius'] = c['holder_double_hole_diameter']/2.0
  c['holder_double_hole_position_radius'] = c['holder_hole_position_radius'] + c['holder_double_hole_position']
  if(c['holder_double_hole_length']<0):
    print("ERR304: Error, holder_double_hole_length {:0.3f} should be positive".format(c['holder_double_hole_length']))
    sys.exit(2)
  elif(c['holder_double_hole_length']>0):
    if(c['holder_double_hole_radius']==0):
      print("ERR308: Error, holder_double_hole_length {:0.3f} is positive whereas holder_double_hole_radius is set to zero".format(c['holder_double_hole_length']))
      sys.exit(2)
  if(c['holder_double_hole_position']!=0):
    if(c['holder_double_hole_radius']==0):
      print("ERR319: Error, holder_double_hole_position {:0.3f} is set whereas holder_double_hole_radius is still set to zero".format(c['holder_double_hole_position']))
      sys.exit(2)
  if(c['holder_double_hole_radius']<0):
    print("ERR322: Error, holder_double_hole_radius {:0.3f} must be positive or null".format(c['holder_double_hole_radius']))
    sys.exit(2)
  elif(c['holder_double_hole_radius']>0):
    if(c['holder_double_hole_length']==0):
      print("ERR326: Error, holder_double_hole_length must be positive when holder_double_hole_radius {:0.3f} is positive".format(c['holder_double_hole_radius']))
      sys.exit(2)
  # holder_double_hole_mark_nb
  if((c['holder_double_hole_mark_nb']<0)or(c['holder_double_hole_mark_nb']>c['holder_crenel_number'])):
    print("ERR333: Error, holder_double_hole_mark_nb {:d} is out of its range 0..{:d}".format(c['holder_double_hole_mark_nb'], c['holder_crenel_number']))
    sys.exit(2)
  ## holder_hole_B
  holder_hole_B_radius = float(c['holder_hole_B_diameter'])/2
  # holder_hole_B_crenel_list_bis
  c['holder_hole_B_crenel_list_bis'] = [ 0 for i in range(c['holder_crenel_number']) ]
  for i in range(len(c['holder_hole_B_crenel_list'])):
    if((int(c['holder_hole_B_crenel_list'][i])<0)or(int(c['holder_hole_B_crenel_list'][i])>=c['holder_crenel_number'])):
      print("ERR286: Error, the holder_hole_B_crenel_list index {:s} is out of the range 0..{:d}".format(c['holder_hole_B_crenel_list'][i], c['holder_crenel_number']))
      sys.exit(2)
    c['holder_hole_B_crenel_list_bis'][int(c['holder_hole_B_crenel_list'][i])] = 1
  #print("dbg358: holder_hole_B_crenel_list_bis:", c['holder_hole_B_crenel_list_bis'])
  c['holder_maximal_height_plus_B'] = c['holder_hole_position_radius'] + c['holder_crenel_B_position'] + c['holder_crenel_height'] - c['holder_radius'] + additional_holder_maximal_height
  #print("dbg305: holder_maximal_height_plus {:0.3f}  holder_maximal_height_plus_B {:0.3f}".format(c['holder_maximal_height_plus'], c['holder_maximal_height_plus_B']))
  #print("dbg306: holder_crenel_position {:0.3f}   holder_crenel_B_position {:0.3f}".format(c['holder_crenel_position'], c['holder_crenel_B_position']))
  holder_side_outer_smoothing_radius_B = min(0.8*c['holder_crenel_skin_width'], float(c['holder_maximal_height_plus_B'])/4)
  holder_side_straigth_length_B = c['holder_maximal_height_plus_B'] - holder_side_outer_smoothing_radius_B
  holder_smoothing_radius_B = c['holder_sr']
  if(c['holder_smoothing_radius']==0):
    holder_smoothing_radius_B = 0.9*holder_side_straigth_length_B
  if(c['cnc_router_bit_radius']>holder_smoothing_radius_B):
    holder_smoothing_radius_B = c['cnc_router_bit_radius']
  #
  c['holder_hole_radius_list'] = [ c['holder_hole_radius'] for i in range(len(c['holder_hole_B_crenel_list_bis'])) ]
  c['holder_side_outer_smoothing_radius_list'] = [ c['holder_side_outer_smoothing_radius'] for i in range(len(c['holder_hole_B_crenel_list_bis'])) ]
  c['holder_smoothing_radius_list'] = [ c['holder_sr'] for i in range(len(c['holder_hole_B_crenel_list_bis'])+1) ] # generate n+1 values to simplify code in the loop
  for i in range(len(c['holder_hole_B_crenel_list_bis'])):
    if(c['holder_hole_B_crenel_list_bis'][i]==1):
      c['holder_hole_radius_list'][i] = holder_hole_B_radius
      c['holder_side_outer_smoothing_radius_list'][i] = holder_side_outer_smoothing_radius_B
      c['holder_smoothing_radius_list'][i] = holder_smoothing_radius_B
  #print("dbg377: holder_side_outer_smoothing_radius_list:", c['holder_side_outer_smoothing_radius_list'])
  #print("dbg378: holder_smoothing_radius_list:", c['holder_smoothing_radius_list'])
  #
  if(c['holder_crenel_number_cut']>c['holder_crenel_number']):
    print("ERR288: Error, holder_crenel_number_cut {:d} must be smaller than holder_crenel_number {:d}".format(c['holder_crenel_number_cut'], c['holder_crenel_number']))
    sys.exit(2)
  ###
  return(c)

################################################################
# sub-function
################################################################

def make_holder_crenel(ai_holder_maximal_height_plus, ai_holder_crenel_height, ai_holder_crenel_skin_width, ai_holder_crenel_half_width, 
                       ai_holder_crenel_router_bit_radius, ai_holder_side_outer_smoothing_radius, ai_holder_smoothing_radius, ai_holder_crenel_x_position, ai_angle, ai_ox, ai_oy):
  """ generate the A-outline of the holder-crenel
  """
  x0 = ai_holder_crenel_x_position
  x1 = x0 + ai_holder_maximal_height_plus
  x2 = x1 - ai_holder_crenel_height
  y22 = ai_holder_crenel_half_width+ai_holder_crenel_skin_width
  y21 = ai_holder_crenel_half_width
  y12 = -1*y22
  y11 = -1*y21
  dx3 = (1+math.sqrt(2))*ai_holder_crenel_router_bit_radius
  x3 = x2 - dx3
  y23 = y21 - dx3
  y13 = -1*y23
  holder_crenel = []
  holder_crenel.append([x0, y12, ai_holder_smoothing_radius]) # it will be removed at the end of the function
  holder_crenel.append([x1, y12, ai_holder_side_outer_smoothing_radius])
  holder_crenel.append([x1, y11, 0])
  if(y23>ai_holder_crenel_half_width*0.1):
    holder_crenel.append([x3, y11, ai_holder_crenel_router_bit_radius])
    holder_crenel.append([x2, y13, 0])
    holder_crenel.append([x2, y23, 0])
    holder_crenel.append([x3, y21, ai_holder_crenel_router_bit_radius])
  else:
    holder_crenel.append([x2, y11, ai_holder_crenel_router_bit_radius])
    holder_crenel.append([x2, y21, ai_holder_crenel_router_bit_radius])
  holder_crenel.append([x1, y21, 0])
  holder_crenel.append([x1, y22, ai_holder_side_outer_smoothing_radius])
  holder_crenel.append([x0, y22, ai_holder_smoothing_radius])
  #
  r_holder_crenel = cnc25d_api.outline_rotate(holder_crenel, ai_ox, ai_oy, ai_angle)
  #first_point = r_holder_crenel[1]
  return(r_holder_crenel[1:])

################################################################
# gearring 2D-figures construction
################################################################

def gearring_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the gearring design
  """
  ### holder outline
  if(c['holder_crenel_number']==0):
    holder_outline = (c['g1_ix'], c['g1_iy'], c['holder_radius'])
  elif(c['holder_crenel_number']>0):
    angle_incr = 2*math.pi/c['holder_crenel_number']
    if((angle_incr-2*c['holder_crenel_half_angle'])<math.pi/10):
      print("ERR369: Error, no enough space between the crenel: angle_incr {:0.3f}  holder_crenel_half_angle {:0.3f}".format(angle_incr, c['holder_crenel_half_angle']))
      sys.exit(2)
    holder_A = []
    first_angle = c['holder_position_angle'] - c['holder_crenel_half_angle']
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(first_angle), c['g1_iy']+c['holder_radius']*math.sin(first_angle), c['holder_smoothing_radius_list'][-1]])
    for i in range(c['holder_crenel_number']):
      holder_maximal_height_plus_sel = c['holder_maximal_height_plus']
      if(c['holder_hole_B_crenel_list_bis'][i]==1):
        holder_maximal_height_plus_sel = c['holder_maximal_height_plus_B']
      holder_A .extend(make_holder_crenel(holder_maximal_height_plus_sel, c['holder_crenel_height'], c['holder_crenel_skin_width'], c['holder_crenel_half_width'], 
                                          c['holder_crenel_rbr'], c['holder_side_outer_smoothing_radius_list'][i], c['holder_smoothing_radius_list'][i],
                                          c['holder_crenel_x_position'], c['holder_position_angle']+i*angle_incr, c['g1_ix'], c['g1_iy']))
      middle_angle = c['holder_position_angle'] + (i+0.5)*angle_incr
      end_angle = c['holder_position_angle'] + (i+1)*angle_incr - c['holder_crenel_half_angle']
      holder_A.append((c['g1_ix']+c['holder_radius']*math.cos(middle_angle), c['g1_iy']+c['holder_radius']*math.sin(middle_angle),
                        c['g1_ix']+c['holder_radius']*math.cos(end_angle), c['g1_iy']+c['holder_radius']*math.sin(end_angle), c['holder_smoothing_radius_list'][i+1]))
    holder_A[-1] = (holder_A[-1][0], holder_A[-1][1], holder_A[0][0], holder_A[0][1], 0)
    holder_outline = holder_A
  ### holder-hole outline
  holder_hole_figure = []
  for i in range(c['holder_crenel_number']):
    hole_angle = c['holder_position_angle']+i*angle_incr
    if(c['holder_hole_radius_list'][i]>0):
      if(i<c['holder_hole_mark_nb']):
        holder_hole_figure.append(gearwheel.marked_circle_crenel(c['g1_ix']+c['holder_hole_position_radius']*math.cos(hole_angle), c['g1_iy']+c['holder_hole_position_radius']*math.sin(hole_angle), c['holder_hole_radius_list'][i], hole_angle+math.pi/2, c['holder_crenel_rbr']))
      else:
        holder_hole_figure.append([c['g1_ix']+c['holder_hole_position_radius']*math.cos(hole_angle), c['g1_iy']+c['holder_hole_position_radius']*math.sin(hole_angle), c['holder_hole_radius_list'][i]])
  if((c['holder_crenel_number']>0)and(c['holder_double_hole_radius']>0)):
    tmp_a2 = math.atan(c['holder_double_hole_length']/2.0/c['holder_double_hole_position_radius']) # if double carrier-crenel-hole
    tmp_l2 = math.sqrt(c['holder_double_hole_position_radius']**2+(c['holder_double_hole_length']/2.0)**2)
    for i in range(c['holder_crenel_number']):
      hole_angle = c['holder_position_angle']+i*angle_incr
      holder_hole_figure.append([c['g1_ix']+tmp_l2*math.cos(hole_angle-tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle-tmp_a2), c['holder_double_hole_radius']])
      if(i<c['holder_double_hole_mark_nb']):
        holder_hole_figure.append(gearwheel.marked_circle_crenel(c['g1_ix']+tmp_l2*math.cos(hole_angle+tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle+tmp_a2), c['holder_double_hole_radius'], hole_angle+math.pi/2, c['holder_crenel_rbr']))
        #holder_hole_figure.append(gearwheel.marked_circle_crenel(c['g1_ix']+tmp_l2*math.cos(hole_angle+tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle+tmp_a2), c['holder_double_hole_radius'], hole_angle+tmp_a2+math.pi/2, c['holder_crenel_rbr']))
      else:
        holder_hole_figure.append([c['g1_ix']+tmp_l2*math.cos(hole_angle+tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle+tmp_a2), c['holder_double_hole_radius']])
  ### design output
  gr_figure = []
  gr_figure.append(holder_outline) # largest outline first for freecad
  if(c['gear_tooth_nb']>0):
    i_gear_profile = inherit_gear_profile(c) # inherit from gear_profile
    gr_figure.extend(i_gear_profile.get_A_figure('first_gear'))
  else:
    gr_figure.append((c['g1_ix'], c['g1_iy'], float(c['gear_primitive_diameter'])/2))
  gr_figure.extend(holder_hole_figure)
  #
  gr_wo_hole_fig = []
  gr_wo_hole_fig.append(holder_outline)
  gr_wo_hole_fig.extend(holder_hole_figure)
  # gearring_cut : added for low_torque_transmission
  gearring_cut_fig = []
  if(c['holder_crenel_number_cut']>0):
    #print("dbg400: holder_crenel_number_cut:", c['holder_crenel_number_cut'])
    holder_A = []
    li = c['maximal_gear_profile_radius'] # alias
    angle_incr = 2*math.pi/c['holder_crenel_number']
    first_angle = c['holder_position_angle'] - c['holder_crenel_half_angle']
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(first_angle), c['g1_iy']+c['holder_radius']*math.sin(first_angle), c['holder_smoothing_radius_list'][-1]])
    for i in range(c['holder_crenel_number_cut']):
      holder_maximal_height_plus_sel = c['holder_maximal_height_plus']
      if(c['holder_hole_B_crenel_list_bis'][i]==1):
        holder_maximal_height_plus_sel = c['holder_maximal_height_plus_B']
      holder_A .extend(make_holder_crenel(holder_maximal_height_plus_sel, c['holder_crenel_height'], c['holder_crenel_skin_width'], c['holder_crenel_half_width'], 
                                          c['holder_crenel_rbr'], c['holder_side_outer_smoothing_radius_list'][i], c['holder_smoothing_radius_list'][i],
                                          c['holder_crenel_x_position'], c['holder_position_angle']+i*angle_incr, c['g1_ix'], c['g1_iy']))
      if(i!=c['holder_crenel_number_cut']-1):
        middle_angle = c['holder_position_angle'] + (i+0.5)*angle_incr
        end_angle = c['holder_position_angle'] + (i+1)*angle_incr - c['holder_crenel_half_angle']
        holder_A.append((c['g1_ix']+c['holder_radius']*math.cos(middle_angle), c['g1_iy']+c['holder_radius']*math.sin(middle_angle),
                        c['g1_ix']+c['holder_radius']*math.cos(end_angle), c['g1_iy']+c['holder_radius']*math.sin(end_angle), c['holder_smoothing_radius_list'][i+1]))
    end_angle = c['holder_position_angle'] + (c['holder_crenel_number_cut']-1)*angle_incr + c['holder_crenel_half_angle']
    holder_A.append((c['g1_ix']+li*math.cos(end_angle), c['g1_iy']+li*math.sin(end_angle), 0))
    middle_angle = c['holder_position_angle'] + (c['holder_crenel_number_cut']-1)*angle_incr/2.0
    #print("dbg421: end_angle middle_angle first_angle:", end_angle, middle_angle, first_angle)
    holder_A.append((c['g1_ix']+li*math.cos(middle_angle), c['g1_iy']+li*math.sin(middle_angle), c['g1_ix']+li*math.cos(first_angle), c['g1_iy']+li*math.sin(first_angle), 0))
    holder_A.append((holder_A[0][0], holder_A[0][1], 0))
    gearring_cut_fig.append(holder_A) # external outline
    for i in range(c['holder_crenel_number_cut']):
      hole_angle = c['holder_position_angle']+i*angle_incr
      if(c['holder_hole_radius_list'][i]>0):
        if(i<c['holder_hole_mark_nb']):
          gearring_cut_fig.append(gearwheel.marked_circle_crenel(c['g1_ix']+c['holder_hole_position_radius']*math.cos(hole_angle), c['g1_iy']+c['holder_hole_position_radius']*math.sin(hole_angle), c['holder_hole_radius_list'][i], hole_angle+math.pi/2, c['holder_crenel_rbr']))
        else:
          gearring_cut_fig.append([c['g1_ix']+c['holder_hole_position_radius']*math.cos(hole_angle), c['g1_iy']+c['holder_hole_position_radius']*math.sin(hole_angle), c['holder_hole_radius_list'][i]])
    if((c['holder_crenel_number']>0)and(c['holder_double_hole_radius']>0)):
      tmp_a2 = math.atan(c['holder_double_hole_length']/2.0/c['holder_double_hole_position_radius']) # if double carrier-crenel-hole
      tmp_l2 = math.sqrt(c['holder_double_hole_position_radius']**2+(c['holder_double_hole_length']/2.0)**2)
      for i in range(c['holder_crenel_number']):
        hole_angle = c['holder_position_angle']+i*angle_incr
        gearring_cut_fig.append([c['g1_ix']+tmp_l2*math.cos(hole_angle-tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle-tmp_a2), c['holder_double_hole_radius']])
        if(i<c['holder_double_hole_mark_nb']):
          gearring_cut_fig.append(gearwheel.marked_circle_crenel(c['g1_ix']+tmp_l2*math.cos(hole_angle+tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle+tmp_a2), c['holder_double_hole_radius'], hole_angle+math.pi/2, c['holder_crenel_rbr']))
          #gearring_cut_fig.append(gearwheel.marked_circle_crenel(c['g1_ix']+tmp_l2*math.cos(hole_angle+tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle+tmp_a2), c['holder_double_hole_radius'], hole_angle+tmp_a2+math.pi/2, c['holder_crenel_rbr']))
        else:
          gearring_cut_fig.append([c['g1_ix']+tmp_l2*math.cos(hole_angle+tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle+tmp_a2), c['holder_double_hole_radius']])
    
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['gearring_fig'] = gr_figure
  r_height['gearring_fig'] = c['gear_profile_height']
  #
  r_figures['gearring_without_hole_fig'] = gr_wo_hole_fig
  r_height['gearring_without_hole_fig'] = c['gear_profile_height']
  #
  r_figures['gearring_cut'] = gearring_cut_fig
  r_height['gearring_cut'] = c['gear_profile_height']
  ###
  return((r_figures, r_height))

################################################################
# gearring simulation
################################################################

def gearring_simulation_A(c):
  """ define the gearring simulation
  """
  # inherit from gear_profile
  i_gear_profile = inherit_gear_profile(c)
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def gearring_2d_simulations():
  """ return the dictionary defining the available simulation for gearring
  """
  r_sim = {}
  r_sim['gearring_simulation_A'] = gearring_simulation_A
  return(r_sim)


################################################################
# gearring 3D assembly-configuration construction
################################################################

def gearring_3d_construction(c):
  """ construct the 3D-assembly-configurations of the gearring
  """
  # conf1
  gearring_3dconf1 = []
  gearring_3dconf1.append(('gearring_fig',  0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['gearring_3dconf1'] = gearring_3dconf1
  hr = c['holder_radius']
  hh = c['gear_profile_height']/2.0 # half-height
  r_slice['gearring_3dconf1'] = (2*hr,2*hr,c['gear_profile_height'], c['center_position_x']-hr,c['center_position_y']-hr,0.0, [hh], [], [])
  #
  return((r_assembly, r_slice))


################################################################
# gearring_info
################################################################

def gearring_info(c):
  """ create the text info related to the gearring
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
holder_radius: \t{:0.3f}  diameter: \t{:0.3f}
holder_crenel_number: \t{:d}
holder_position_angle: \t{:0.3f}
""".format(c['holder_radius'], 2*c['holder_radius'], c['holder_crenel_number'], c['holder_position_angle'])
  r_info += """
holder_hole_position_radius: \t{:0.3f}
holder_hole_diameter: \t{:0.3f}
holder_hole_mark_nb:  \t{:d}
holder_double_hole_diameter: \t{:0.3f}  radius: \t{:0.3f}
holder_double_hole_length: \t{:0.3f}
holder_double_hole_position: \t{:0.3f}
holder_double_hole_mark_nb:  \t{:d}
""".format(c['holder_hole_position_radius'], c['holder_hole_diameter'], c['holder_hole_mark_nb'], c['holder_double_hole_diameter'], c['holder_double_hole_diameter']/2.0, c['holder_double_hole_length'], c['holder_double_hole_position'], c['holder_double_hole_mark_nb'])
  r_info += """
holder_crenel_position: \t{:0.3f}
holder_crenel_height: \t{:0.3f}
holder_crenel_width: \t{:0.3f}
holder_crenel_skin_width: \t{:0.3f}
""".format(c['holder_crenel_position'], c['holder_crenel_height'], c['holder_crenel_width'], c['holder_crenel_skin_width'])
  r_info += """
holder_hole_B_diameter: \t{:0.3f}
holder_crenel_B_position: \t{:0.3f}
""".format(c['holder_hole_B_diameter'], c['holder_crenel_B_position'])
  r_info += """
gear_router_bit_radius:           \t{:0.3f}
holder_crenel_router_bit_radius:  \t{:0.3f}
holder_smoothing_radius:          \t{:0.3f}
cnc_router_bit_radius:            \t{:0.3f}
""".format(c['gear_rbr'], c['holder_crenel_rbr'], c['holder_sr'], c['cnc_router_bit_radius'])
  #print(r_info)
  return(r_info)


################################################################
# self test
################################################################

def gearring_self_test():
  """
  This is the non-regression test of gearring.
  Look at the simulation Tk window to check errors.
  """
  r_tests = [
    ["simplest test"    , "--gear_tooth_nb 25 --gear_module 10 --holder_diameter 300.0 --cnc_router_bit_radius 2.0"],
    ["no tooth"         , "--gear_tooth_nb 0 --gear_primitive_diameter 100.0 --holder_diameter 120.0 --cnc_router_bit_radius 2.0 --holder_crenel_number 7"],
    ["no holder-hole"   , "--gear_tooth_nb 30 --gear_module 10 --holder_diameter 360.0 --holder_crenel_width 20.0 --holder_crenel_skin_width 20.0 --cnc_router_bit_radius 2.0 --holder_hole_diameter 0.0"],
    ["no crenel"        , "--gear_tooth_nb 29 --gear_module 10 --holder_diameter 340.0 --holder_crenel_width 20.0 --holder_crenel_number 0"],
    ["marked holder-hole" , "--gear_tooth_nb 33 --gear_module 10 --holder_crenel_number 8 --holder_hole_mark_nb 1 --holder_hole_diameter 14.0 --holder_crenel_position 10.0"],
    ["double hole only" , "--gear_tooth_nb 37 --gear_module 10 --holder_crenel_number 8 --holder_double_hole_mark_nb 2 --holder_double_hole_diameter 6.0 --holder_double_hole_length 12.0 --holder_hole_diameter 0.0"],
    ["single and double hole" , "--gear_tooth_nb 37 --gear_module 10 --holder_crenel_number 8 --holder_double_hole_mark_nb 3 --holder_double_hole_diameter 4.0 --holder_double_hole_length 20.0 --holder_hole_diameter 8.0 --holder_double_hole_position 4.0"],
    ["small crenel"     , "--gear_tooth_nb 30 --gear_module 10 --holder_diameter 360.0 --holder_crenel_width 20.0 --holder_crenel_number 1 --holder_hole_diameter 0.0 --holder_crenel_position 0.0 --holder_crenel_height 5.0"],
    ["narrow crenel"    , "--gear_tooth_nb 30 --gear_module 10 --holder_diameter 360.0 --holder_crenel_width 20.0 --holder_crenel_number 4 --holder_position_angle 0.785 --holder_hole_diameter 0.0 --holder_crenel_position 0.0 --holder_crenel_height 5.0"],
    ["crenel-B"    , "--gear_tooth_nb 51 --gear_module 1.0 --holder_diameter 59.0 --holder_crenel_width 2.0 --holder_crenel_number 6 --holder_hole_diameter 4.1 --holder_hole_B_diameter 1.1 --holder_crenel_position 30.5 --holder_crenel_height 0.5 --holder_crenel_position 3.5 --holder_crenel_B_position 1.0 --holder_hole_B_crenel_list 2 5 --cnc_router_bit_radius 0.05 --gear_router_bit_radius 0.05 --holder_crenel_router_bit_radius 0.1 --holder_crenel_skin_width 3.0"],
    ["output dxf"    , "--gear_tooth_nb 30 --gear_module 10 --holder_diameter 360.0 --holder_crenel_width 20.0 --holder_crenel_number 2 --holder_position_angle 0.785 --holder_hole_diameter 0.0 --holder_crenel_position 0.0 --holder_crenel_height 5.0 --output_file_basename test_output/gearring_self_test.dxf"],
    ["last test"        , "--gear_tooth_nb 30 --gear_module 10.0 --holder_diameter 340.0"]]
  return(r_tests)

################################################################
# gearring design declaration
################################################################

class gearring(cnc25d_api.bare_design):
  """ gearring design
  """
  def __init__(self, constraint={}):
    """ configure the gearring design
    """
    self.design_setup(
      s_design_name             = "gearring",
      f_constraint_constructor  = gearring_constraint_constructor,
      f_constraint_check        = gearring_constraint_check,
      f_2d_constructor          = gearring_2d_construction,
      d_2d_simulation           = gearring_2d_simulations(),
      f_3d_constructor          = gearring_3d_construction,
      f_info                    = gearring_info,
      l_display_figure_list     = ['gearring_fig'],
      s_default_simulation      = '',
      l_2d_figure_file_list     = ['gearring_fig'],
      l_3d_figure_file_list     = ['gearring_fig'],
      l_3d_conf_file_list       = ['gearring_3dconf1'],
      f_cli_return_type         = None,
      l_self_test_list          = gearring_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearring.py says hello!\n")
  my_gr = gearring()
  #my_gr.cli()
  #my_gr.cli("--gear_tooth_nb 25 --gear_module 10 --holder_diameter 300.0 --holder_crenel_width 20.0 --holder_crenel_skin_width 10.0 --cnc_router_bit_radius 2.0")
  my_gr.cli("--gear_tooth_nb 25 --gear_module 10 --holder_crenel_width 20.0 --holder_crenel_skin_width 10.0 --cnc_router_bit_radius 2.0")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_gr.get_fc_obj_3dconf('gearring_3dconf1'))


