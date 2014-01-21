# split_gearwheel.py
# generates a split_gearwheel and simulates gear.
# created by charlyoleg on 2013/09/27
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
split_gearwheel.py is a parametric generator of split_gearwheels.
The main function return the split-gearwheel as FreeCAD Part object.
You can also simulate or view of the split-gearwheel and get a DXF, SVG or BRep file.
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
import re # to detect .dxf or .svg
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
# split_gearwheel constraint_constructor
################################################################

def split_gearwheel_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the split_gearwheel design
  """
  r_parser = ai_parser
  ### inherit arguments from gear_profile
  i_gear_profile = inherit_gear_profile()
  r_parser = i_gear_profile.get_constraint_constructor()(r_parser, 1)
  ### split
  ## general
  r_parser.add_argument('--split_nb','--snb', action='store', type=int, default=6,
    help="Set the number of portions to split the gearwheel. Default: 6")
  r_parser.add_argument('--split_initial_angle','--sia', action='store', type=float, default=0.0,
    help="Set the angle between the X-axis and the first split radius. Default: 0.0")
  ## low_split
  r_parser.add_argument('--low_split_diameter','--lsd', action='store', type=float, default=5.0,
    help="Set the diameter of the inner circle of the split-portion. Default: 5.0")
  r_parser.add_argument('--low_split_type','--lst', action='store', default='circle',
    help="Select the type of outline for the inner border of the split-portions. Possible values: 'circle', 'line'. Default: 'circle'")
  ## high_split
  r_parser.add_argument('--high_split_diameter','--hsd', action='store', type=float, default=0.0,
    help="Set the diameter of the high circle of the split-portion. If equal to 0.0, it is set to the minimal_gear_profile_radius - tooth_half_height. Default: 0.0")
  r_parser.add_argument('--high_split_type','--hst', action='store', default='h',
    help="Select the type of connection between the split-portion high-circle and the gear-profile. Possible values: 'h'=hollow_only , 'a'=addendum_too. Default: 'h'")
  ## split_router_bit_radius
  r_parser.add_argument('--split_router_bit_radius','--srbr', action='store', type=float, default=1.0,
    help="Set the split router_bit radius of the split-gearwheel (used at the high-circle corners). Default: 1.0")
  ### low-hole
  r_parser.add_argument('--low_hole_circle_diameter','--lhcd', action='store', type=float, default=0.0,
    help="Set the diameter of the low-hole circle. If equal to 0.0, it is set to low_split_diameter + low_hole_diameter. Default: 0.0")
  r_parser.add_argument('--low_hole_diameter','--lhd', action='store', type=float, default=1.0,
    help="Set the diameter of the low-holes. Default: 1.0")
  r_parser.add_argument('--low_hole_nb','--lhn', action='store', type=int, default=1,
    help="Set the number of low-holes. Default: 1")
  ### high-hole
  r_parser.add_argument('--high_hole_circle_diameter','--hhcd', action='store', type=float, default=0.0,
    help="Set the diameter of the high-hole circle. If equal to 0.0, set to high_split_diameter - high_hole_diameter. Default: 0.0")
  r_parser.add_argument('--high_hole_diameter','--hhd', action='store', type=float, default=1.0,
    help="Set the diameter of the high-holes. Default: 1.0")
  r_parser.add_argument('--high_hole_nb','--hhn', action='store', type=int, default=1,
    help="Set the number of high-holes. Default: 1")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=1.0,
    help="Set the minimum router_bit radius of the split-gearwheel. It increases gear_router_bit_radius and split_router_bit_radius if needed. Default: 1.0")
  # return
  return(r_parser)

    
################################################################
# split_gearwheel constraint_check
################################################################

def split_gearwheel_constraint_check(c):
  """ check the split_gearwheel constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  # get the router_bit_radius
  c['gear_rbr'] = c['gear_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['gear_rbr']):
    c['gear_rbr'] = c['cnc_router_bit_radius']
  c['split_rbr'] = c['split_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['split_rbr']):
    c['split_rbr'] = c['cnc_router_bit_radius']
  # c['low_split_type']
  if(not c['low_split_type'] in ('circle', 'line')):
    print("ERR216: Error, c['low_split_type'] {:s} is not valid!".format(c['low_split_type']))
    sys.exit(2)
  # c['high_split_type']
  if(not c['high_split_type'] in ('h', 'a')):
    print("ERR220: Error, c['high_split_type'] {:s} is not valid!".format(c['high_split_type']))
    sys.exit(2)
  if(c['split_nb']<2):
    print("ERR188: Error, split_nb {:d} must be equal or bigger than 2".format(c['split_nb']))
    sys.exit(2)
  #c['portion_angle'] = 2*math.pi/c['split_nb']
  c['portion_angle'] = math.pi/c['split_nb']
  #print("dbg190: c['gear_tooth_nb']:", c['gear_tooth_nb'])
  if(c['gear_tooth_nb']>0): # create a gear_profile
    i_gear_profile = inherit_gear_profile(c)
    gear_profile_parameters = i_gear_profile.get_constraint()
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    c['minimal_gear_profile_radius'] = gear_profile_parameters['g1_param']['hollow_radius']
    c['g1_ix'] = gear_profile_parameters['g1_param']['center_ox']
    c['g1_iy'] = gear_profile_parameters['g1_param']['center_oy']
    c['addendum_radius'] = gear_profile_parameters['g1_param']['addendum_radius'] # for slice_xyz
    # high_split_radius
    g1_m = gear_profile_parameters['g1_param']['module']
    c['high_split_radius'] = c['high_split_diameter']/2.0
    if(c['high_split_radius']==0):
      c['high_split_radius'] = c['minimal_gear_profile_radius'] - g1_m
    #print("dbg172: high_split_radius:", c['high_split_radius'])
    ## gear_portion
    g1_pma = gear_profile_parameters['g1_param']['pi_module_angle']
    g1_hma = gear_profile_parameters['g1_param']['hollow_middle_angle']
    g1_ia = gear_profile_parameters['g1_param']['initial_angle']
    g1_tl = gear_profile_parameters['g1_param']['top_land']
    if(c['portion_angle']<(1.1*g1_pma)):
      print("ERR219: Error, portion_angle {:0.3f} is too small compare to the pi_module_angle {:0.3f}".format(c['portion_angle'], g1_pma))
      sys.exit(2)
    # pre common calculation
    absolute_angle = []
    relative_angle = []
    raw_tooth_nb = []
    a_start = g1_ia + g1_hma
    overhead = 2 # must be equal or bigger than 2 because of raw_tooth_nb[i-overhead+2]
    for i in range(2*c['split_nb']+overhead):
      portion_start_angle = c['split_initial_angle'] + (i+0.0) * c['portion_angle']
      tooth_nb = 0
      while(abs(math.fmod(a_start-portion_start_angle+5*math.pi, 2*math.pi)-math.pi)>g1_pma/2.0):
        a_start += g1_pma
        tooth_nb += 1
      absolute_angle.append(a_start)
      relative_angle.append(math.fmod(a_start-portion_start_angle+5*math.pi, 2*math.pi)-math.pi)
      raw_tooth_nb.append(tooth_nb)
      #print("dbg238: i {:d} raw_tooth_nb {:0.3f}".format(i, raw_tooth_nb[i]))
    absolute_angle = absolute_angle[overhead:]
    relative_angle = relative_angle[overhead:]
    raw_tooth_nb = raw_tooth_nb[overhead:]
    # final low-parameters
    c['portion_gear_tooth_angle'] = []
    c['portion_gear_first_end'] = []
    c['portion_gear_last_end'] = []
    c['portion_gear_tooth_nb'] = []
    for i in range(2*c['split_nb']):
      ii = i-overhead
      if(c['high_split_type']=='h'):
        c['portion_gear_tooth_angle'].append(absolute_angle[ii]-g1_hma+g1_pma)
        c['portion_gear_first_end'].append(3)
        c['portion_gear_last_end'].append(3)
        c['portion_gear_tooth_nb'].append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1)
      elif(c['high_split_type']=='a'):
        tooth_transfer = 0
        if(abs(relative_angle[ii])<=(g1_pma-g1_tl)/2.0):
          c['portion_gear_first_end'].append(3)
          c['portion_gear_tooth_angle'].append(absolute_angle[ii]-g1_hma+g1_pma)
        elif(relative_angle[ii]>=(g1_pma-g1_tl)/2.0):
          c['portion_gear_first_end'].append(1)
          c['portion_gear_tooth_angle'].append(absolute_angle[ii]-g1_hma)
          tooth_transfer = 1
        elif(relative_angle[ii]<=-1*(g1_pma-g1_tl)/2.0):
          c['portion_gear_first_end'].append(1)
          c['portion_gear_tooth_angle'].append(absolute_angle[ii]-g1_hma+g1_pma)
        if(abs(relative_angle[ii+2])<=(g1_pma-g1_tl)/2.0):
          c['portion_gear_tooth_nb'].append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1+tooth_transfer)
          c['portion_gear_last_end'].append(3)
        elif(relative_angle[ii+2]>=(g1_pma-g1_tl)/2.0):
          c['portion_gear_tooth_nb'].append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1+tooth_transfer)
          c['portion_gear_last_end'].append(1)
        elif(relative_angle[ii+2]<=-1*(g1_pma-g1_tl)/2.0):
          c['portion_gear_tooth_nb'].append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-0+tooth_transfer)
          c['portion_gear_last_end'].append(1)
    #print("dbg276: len(portion_gear_first_end) {:d}  len(portion_gear_last_end) {:d}".format(len(c['portion_gear_first_end']), len(c['portion_gear_last_end'])))
  else: # no gear_profile, just a circle
    if(c['gear_primitive_diameter']<radian_epsilon):
      print("ERR885: Error, the no-gear-profile circle outline diameter c['gear_primitive_diameter'] {:0.2f} is too small!".format(c['gear_primitive_diameter']))
      sys.exit(2)
    #gear_profile_B = (c['g1_ix'], c['g1_iy'], float(c['gear_primitive_diameter'])/2)
    c['minimal_gear_profile_radius'] = float(c['gear_primitive_diameter'])/2
    c['g1_ix'] = c['center_position_x']
    c['g1_iy'] = c['center_position_y']
    c['addendum_radius'] = float(c['gear_primitive_diameter'])/2 # for slice_xyz
    if(c['high_split_diameter']!=0):
      print("WARN221: Warning, the setting high_split_diameter {:0.3f} should not be used when gear_tooth_nb=0".format(c['high_split_diameter']))
    c['high_split_radius'] = c['minimal_gear_profile_radius']
  # set default value (if set to zero) for high_split_diameter, low_hole_circle_diameter, high_hole_circle_diameter
  c['low_split_radius'] = c['low_split_diameter']/2.0
  c['low_hole_radius'] = c['low_hole_diameter']/2.0
  c['low_hole_circle_radius'] = c['low_hole_circle_diameter']/2.0
  c['high_hole_circle_radius'] = c['high_hole_circle_diameter']/2.0
  c['high_hole_radius'] = c['high_hole_diameter']/2.0
  if(c['low_hole_circle_radius']==0):
    c['low_hole_circle_radius'] = c['low_split_radius'] + 2*c['low_hole_radius']
  if(c['high_hole_circle_radius']==0):
    c['high_hole_circle_radius'] = c['high_split_radius'] - 1.2*c['high_hole_radius']
  #print("dbg292: high_hole_circle_radius {:0.3f}  high_split_radius {:0.3f}".format(c['high_hole_circle_radius'], c['high_split_radius']))
  ### check parameter coherence (part 2)
  # low_hole_nb and high_hole_nb
  if(c['low_hole_nb']==0):
    c['low_hole_radius'] = 0
    c['low_hole_nb']=1
  if(c['high_hole_nb']==0):
    c['high_hole_radius'] = 0
    c['high_hole_nb']=1
  # radial parameters
  if(c['low_hole_circle_radius']<(c['low_split_radius'] + c['low_hole_radius'])):
    print("ERR230: Error, low_hole_circle_radius {:0.3f} is too small compare to low_split_radius {:0.3f} and low_hole_radius {:0.3f}".format(c['low_hole_circle_radius'], c['low_split_radius'], c['low_hole_radius']))
    sys.exit(2)
  if(c['high_hole_circle_radius']<(c['low_hole_circle_radius'] + c['low_hole_radius'] + c['high_hole_radius'])):
    print("ERR232: Error, high_hole_circle_radius {:0.3f} is too small compare to low_hole_circle_radius {:0.3f}, low_hole_radius {:0.3f} and high_hole_radius {:0.3f}".format(c['high_hole_circle_radius'], c['low_hole_circle_radius'], c['low_hole_radius'], c['high_hole_radius']))
    sys.exit(2)
  if(c['high_split_radius']<(c['high_hole_circle_radius'] + c['high_hole_radius'])):
    print("ERR236: Error, high_split_radius {:0.3f} is too small compare to high_hole_circle_radius {:0.3f} and high_hole_radius {:0.3f}".format(c['high_split_radius'], c['high_hole_circle_radius'], c['high_hole_radius']))
    sys.exit(2)
  if(c['minimal_gear_profile_radius']<c['high_split_radius']):
    print("ERR239: Error, minimal_gear_profile_radius {:0.3f} is smaller than high_split_radius {:0.3f}".format(c['minimal_gear_profile_radius'], c['high_split_radius']))
    sys.exit(2)
  # angular (or circumference) parameters
  low_hole_diameter_angle = math.asin(float(c['low_hole_radius'])/c['low_hole_circle_radius'])
  c['low_hole_space_angle'] = c['portion_angle']/float(c['low_hole_nb'])
  high_hole_diameter_angle = math.asin(float(c['high_hole_radius'])/c['high_hole_circle_radius'])
  c['high_hole_space_angle'] = c['portion_angle']/float(c['high_hole_nb'])
  if(c['low_hole_space_angle']<(2*low_hole_diameter_angle+radian_epsilon)):
    print("ERR253: Error, low_hole_nb {:d} or low_hole_diameter {:0.3f} are too big!".format(c['low_hole_nb'], c['low_hole_diameter']))
    sys.exit(2)
  if(c['high_hole_space_angle']<(2*high_hole_diameter_angle+radian_epsilon)):
    print("ERR255: Error, high_hole_nb {:d} or high_hole_diameter {:0.3f} are too big!".format(c['high_hole_nb'], c['high_hole_diameter']))
    sys.exit(2)
  ###
  return(c)

################################################################
# split_gearwheel 2D-figures construction
################################################################

def split_gearwheel_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the split_gearwheel design
  """
  ### generate the portion outlines
  part_figure_list = []
  if(c['gear_tooth_nb']>0): # create a gear_profile
    for i in range(2*c['split_nb']):
      #print("dbg333:  portion_gear_tooth_nb[i]: {:0.3f}".format(c['portion_gear_tooth_nb'][i]))
      #print("dbg334:  portion_gear_first_end[i]: {:0.3f}".format(c['portion_gear_first_end'][i]))
      #print("dbg335:  portion_gear_last_end[i]: {:0.3f}".format(c['portion_gear_last_end'][i]))
      #print("dbg336:  portion_gear_tooth_angle[i]: {:0.3f}".format(c['portion_gear_tooth_angle'][i]))
      if(c['portion_gear_tooth_nb'][i]<1):
        print("ERR338: Error, for i {:d} portion_gear_tooth_nb {:d} smaller than 1".format(i, c['portion_gear_tooth_nb'][i]))
        sys.exit(2)
      gp_c = c.copy()
      gp_c['gear_type'] = 'e'
      #gp_c['portion_tooth_nb']    = c['portion_gear_tooth_nb'][i]
      #gp_c['portion_first_end']   = c['portion_gear_first_end'][i]
      #gp_c['portion_last_end']    = c['portion_gear_last_end'][i]
      gp_c['cut_portion'] = [c['portion_gear_tooth_nb'][i], c['portion_gear_first_end'][i], c['portion_gear_last_end'][i]]
      gp_c['gear_initial_angle']  = c['portion_gear_tooth_angle'][i]
      #print("dbg342: gp_c:", gp_c)
      #print("dbg341: gp_c['portion_tooth_nb']: {:d}".format(gp_c['portion_tooth_nb']))
      i_gear_profile = inherit_gear_profile()
      i_gear_profile.apply_external_constraint(gp_c)
      gear_profile_B = i_gear_profile.get_A_figure('first_gear')[0] # gear_profile always return figure at B-format
      #print("dbg321: gear_profile constraint:", i_gear_profile.get_constraint()['portion_tooth_nb'], c['portion_gear_tooth_nb'][i])
      #cnc25d_api.figure_simple_display([gear_profile_B], [], "debug gear_profile_B")
      #print("dbg345: trash_gear_profile_parameters:", trash_gear_profile_parameters)
      #print("dbg346: trash_gear_profile_parameters['portion_tooth_nb']: {:d}".format(trash_gear_profile_parameters['portion_tooth_nb']))
      tmp_a = c['split_initial_angle'] + (i+2.0)*c['portion_angle']
      tmp_b = c['split_initial_angle'] + (i+1.0)*c['portion_angle']
      tmp_c = c['split_initial_angle'] + (i+0.0)*c['portion_angle']
      low_portion_A = []
      low_portion_A.append((gear_profile_B[-1][0], gear_profile_B[-1][1], 0))
      low_portion_A.append((c['g1_ix']+c['high_split_radius']*math.cos(tmp_a), c['g1_iy']+c['high_split_radius']*math.sin(tmp_a), c['split_rbr']))
      low_portion_A.append((c['g1_ix']+c['low_split_radius']*math.cos(tmp_a), c['g1_iy']+c['low_split_radius']*math.sin(tmp_a), 0))
      if(c['low_split_type']=='circle'):
        low_portion_A.append((c['g1_ix']+c['low_split_radius']*math.cos(tmp_b), c['g1_iy']+c['low_split_radius']*math.sin(tmp_b), c['g1_ix']+c['low_split_radius']*math.cos(tmp_c), c['g1_iy']+c['low_split_radius']*math.sin(tmp_c), 0))
      elif(c['low_split_type']=='line'):
        low_portion_A.append((c['g1_ix']+c['low_split_radius']*math.cos(tmp_b), c['g1_iy']+c['low_split_radius']*math.sin(tmp_b), 0))
        low_portion_A.append((c['g1_ix']+c['low_split_radius']*math.cos(tmp_c), c['g1_iy']+c['low_split_radius']*math.sin(tmp_c), 0))
      low_portion_A.append((c['g1_ix']+c['high_split_radius']*math.cos(tmp_c), c['g1_iy']+c['high_split_radius']*math.sin(tmp_c), c['split_rbr']))
      low_portion_A.append((gear_profile_B[0][0], gear_profile_B[0][1], 0))
      #print("dbg337: low_portion_A:", low_portion_A)
      low_portion_B = cnc25d_api.cnc_cut_outline(low_portion_A, "portion_A")
      portion_B = gear_profile_B[:]
      portion_B.extend(low_portion_B[1:])
      #part_figure_list.append([portion_B])
      part_figure_list.append([portion_B[:]])
  else:
    for i in range(2*c['split_nb']):
      tmp_a = c['split_initial_angle'] + (i+2.0)*c['portion_angle']
      tmp_b = c['split_initial_angle'] + (i+1.0)*c['portion_angle']
      tmp_c = c['split_initial_angle'] + (i+0.0)*c['portion_angle']
      portion_A = []
      portion_A.append((c['g1_ix']+c['high_split_radius']*math.cos(tmp_c), c['g1_iy']+c['high_split_radius']*math.sin(tmp_c), 0))
      portion_A.append((c['g1_ix']+c['high_split_radius']*math.cos(tmp_b), c['g1_iy']+c['high_split_radius']*math.sin(tmp_b), c['g1_ix']+c['high_split_radius']*math.cos(tmp_a), c['g1_iy']+c['high_split_radius']*math.sin(tmp_a), 0))
      portion_A.append((c['g1_ix']+c['low_split_radius']*math.cos(tmp_a), c['g1_iy']+c['low_split_radius']*math.sin(tmp_a), 0))
      if(c['low_split_type']=='circle'):
        portion_A.append((c['g1_ix']+c['low_split_radius']*math.cos(tmp_b), c['g1_iy']+c['low_split_radius']*math.sin(tmp_b), c['g1_ix']+c['low_split_radius']*math.cos(tmp_c), c['g1_iy']+c['low_split_radius']*math.sin(tmp_c), 0))
      elif(c['low_split_type']=='line'):
        portion_A.append((c['g1_ix']+c['low_split_radius']*math.cos(tmp_b), c['g1_iy']+c['low_split_radius']*math.sin(tmp_b), 0))
        portion_A.append((c['g1_ix']+c['low_split_radius']*math.cos(tmp_c), c['g1_iy']+c['low_split_radius']*math.sin(tmp_c), 0))
      portion_A.append((c['g1_ix']+c['high_split_radius']*math.cos(tmp_c), c['g1_iy']+c['high_split_radius']*math.sin(tmp_c), 0))
      portion_B = cnc25d_api.cnc_cut_outline(portion_A, "circle_portion_A")
      #part_figure_list.append([portion_B])
      part_figure_list.append([portion_B[:]])
  ### generate the hole outlines
  for i in range(len(part_figure_list)):
    hole_figure = []
    if(c['low_hole_radius']>0):
      for j in range(2*c['low_hole_nb']):
        tmp_a = c['split_initial_angle'] + i*c['portion_angle'] + (j+0.5)*c['low_hole_space_angle']
        hole_figure.append((c['g1_ix']+c['low_hole_circle_radius']*math.cos(tmp_a), c['g1_iy']+c['low_hole_circle_radius']*math.sin(tmp_a), c['low_hole_radius']))
    if(c['high_hole_radius']>0):
      for j in range(2*c['high_hole_nb']):
        tmp_a = c['split_initial_angle'] + i*c['portion_angle'] + (j+0.5)*c['high_hole_space_angle']
        hole_figure.append((c['g1_ix']+c['high_hole_circle_radius']*math.cos(tmp_a), c['g1_iy']+c['high_hole_circle_radius']*math.sin(tmp_a), c['high_hole_radius']))
    #part_figure_list[i].extend(hole_figure)
    part_figure_list[i].extend(hole_figure[:])

  ### design output
  sgw_assembly_figure = []
  sgw_assembly_A_figure = []
  sgw_assembly_B_figure = []
  aligned_part_figure_list = []
  sgw_list_of_parts = []
  for i in range(2*c['split_nb']):
    sgw_assembly_figure.extend(part_figure_list[i])
    if((i%2)==0):
      sgw_assembly_A_figure.extend(part_figure_list[i])
    else:
      sgw_assembly_B_figure.extend(part_figure_list[i])
    shift_x = 2.2 * (i%2) * c['minimal_gear_profile_radius']
    shift_y = 2.2 * int(i/2) * c['minimal_gear_profile_radius']
    rotated_fig = cnc25d_api.rotate_and_translate_figure(part_figure_list[i], c['g1_ix'], c['g1_iy'], -1*(c['split_initial_angle'] + i*c['portion_angle']), 0.0, 0.0)
    aligned_part_figure_list.append(rotated_fig)
    sgw_list_of_parts.extend(cnc25d_api.rotate_and_translate_figure(rotated_fig, 0.0, 0.0, 0.0, shift_x, shift_y))
  ###
  r_figures = {}
  r_height = {}
  #
  for i in range(2*c['split_nb']):
    r_figures['sgw_part_{:02d}'.format(i)] = part_figure_list[i]
    r_height['sgw_part_{:02d}'.format(i)] = c['gear_profile_height']
  #
  r_figures['sgw_assembly_fig'] = sgw_assembly_figure
  r_height['sgw_assembly_fig'] = c['gear_profile_height']
  #
  r_figures['sgw_even_assembly_fig'] = sgw_assembly_A_figure
  r_height['sgw_even_assembly_fig'] = c['gear_profile_height']
  #
  r_figures['sgw_odd_assembly_fig'] = sgw_assembly_B_figure
  r_height['sgw_odd_assembly_fig'] = c['gear_profile_height']
  #
  for i in range(2*c['split_nb']):
    r_figures['sgw_aligned_part_{:02d}'.format(i)] = aligned_part_figure_list[i]
    r_height['sgw_aligned_part_{:02d}'.format(i)] = c['gear_profile_height']
  #
  r_figures['sgw_list_of_parts'] = sgw_list_of_parts
  r_height['sgw_list_of_parts'] = c['gear_profile_height']
  #
  ###
  return((r_figures, r_height))

################################################################
# split_gearwheel simulation
################################################################

def split_gearwheel_simulation_A(c):
  """ define the split_gearwheel simulation
  """
  # inherit from gear_profile
  i_gear_profile = inherit_gear_profile(c)
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def split_gearwheel_2d_simulations():
  """ return the dictionary defining the available simulation for split_gearwheel
  """
  r_sim = {}
  r_sim['split_gearwheel_simulation_A'] = split_gearwheel_simulation_A
  return(r_sim)


################################################################
# split_gearwheel 3D assembly-configuration construction
################################################################

def split_gearwheel_3d_construction(c):
  """ construct the 3D-assembly-configurations of the split_gearwheel
  """
  # conf1
  split_gearwheel_3dconf1 = []
  for i in range(2*c['split_nb']):
    split_gearwheel_3dconf1.append(('sgw_part_{:02d}'.format(i),  0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, (i%2)*c['gear_profile_height']))
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['split_gearwheel_3dconf1'] = split_gearwheel_3dconf1
  hr = c['addendum_radius']
  hh = c['gear_profile_height']/2.0 # half-height
  r_slice['split_gearwheel_3dconf1'] = (2*hr,2*hr,4*hh, c['center_position_x']-hr,c['center_position_y']-hr,0.0, [hh, 3*hh], [], [])
  #
  return((r_assembly, r_slice))


################################################################
# split_gearwheel_info
################################################################

def split_gearwheel_info(c):
  """ create the text info related to the split_gearwheel
  """
  r_info = ""
  if(c['gear_tooth_nb']>0): # with gear-profile (normal case)
    i_gear_profile = inherit_gear_profile(c) # inherit from gear_profile
    r_info += i_gear_profile.get_info()
  else: # when no gear-profile
    r_info += "\nSimple circle (no-gear-profile):\n"
    r_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(c['gear_primitive_diameter']/2.0, c['gear_primitive_diameter'])
    r_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(c['g1_ix'], c['g1_iy'])
  r_info += """
split_nb:             \t{:d}
split_initial_angle:  \t{:0.3f} (radian)  \t{:0.3f} (degree)
high_split_radius:    \t{:0.3f} diameter: \t{:0.3f}
high_split_type:      \t{:s}
""".format(c['split_nb'], c['split_initial_angle'], c['split_initial_angle']*180/math.pi, c['high_split_radius'], 2*c['high_split_radius'], c['high_split_type'])
  r_info += """
low_split_radius:     \t{:0.3f} diameter: \t{:0.3f}
low_split_type:       \t{:s}
""".format(c['low_split_radius'], 2*c['low_split_radius'], c['low_split_type'])
  r_info += """
low_hole_circle_radius:   \t{:0.3f} diameter: \t{:0.3f}
low_hole_radius:          \t{:0.3f} diameter: \t{:0.3f}
low_hole_nb:              \t{:d}
""".format(c['low_hole_circle_radius'], 2*c['low_hole_circle_radius'], c['low_hole_radius'], 2*c['low_hole_radius'], c['low_hole_nb'])
  r_info += """
high_hole_circle_radius:  \t{:0.3f} diameter: \t{:0.3f}
high_hole_radius:         \t{:0.3f} diameter: \t{:0.3f}
high_hole_nb:             \t{:d}
""".format(c['high_hole_circle_radius'], 2*c['high_hole_circle_radius'], c['high_hole_radius'], 2*c['high_hole_radius'], c['high_hole_nb'])
  r_info += """
gear_router_bit_radius:   \t{:0.3f}
split_router_bit_radius:  \t{:0.3f}
cnc_router_bit_radius:    \t{:0.3f}
""".format(c['gear_rbr'], c['split_rbr'], c['cnc_router_bit_radius'])
  #print(r_info)
  return(r_info)


################################################################
# self test
################################################################

def split_gearwheel_self_test():
  """
  This is the non-regression test of split_gearwheel.
  Look at the simulation Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2"],
    ["split nb 2"           , "--gear_tooth_nb 27 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 2"],
    ["split nb 3"           , "--gear_tooth_nb 26 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 3"],
    ["split nb 4"           , "--gear_tooth_nb 23 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 4"],
    ["split nb 5"           , "--gear_tooth_nb 21 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 5"],
    ["split nb 6"           , "--gear_tooth_nb 29 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 6"],
    ["split nb 7"           , "--gear_tooth_nb 31 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 7"],
    ["split nb 8"           , "--gear_tooth_nb 33 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 8"],
    ["portion and tooth nb" , "--gear_tooth_nb 17 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0"],
    ["no tooth"             , "--gear_tooth_nb 0 --gear_primitive_diameter 200.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 3"],
    ["no low hole"          , "--gear_tooth_nb 27 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --low_hole_nb 0"],
    ["no high hole"         , "--gear_tooth_nb 28 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 0"],
    ["split style line"     , "--gear_tooth_nb 30 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --low_split_type line --split_nb 2"],
    ["split style addendum" , "--gear_tooth_nb 41 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --high_split_type a --split_nb 10"],
    ["split initial angle"  , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --split_initial_angle 0.1 --gear_initial_angle 0.15"],
    ["gear simulation"      , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --simulate_2d --second_gear_tooth_nb 19"],
    ["output file"          , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --output_file_basename test_output/split_gearwheel_self_test.dxf"],
    ["last test"            , "--gear_tooth_nb 24 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0"]]
  return(r_tests)

################################################################
# split_gearwheel design declaration
################################################################

class split_gearwheel(cnc25d_api.bare_design):
  """ split_gearwheel design
  """
  def __init__(self, constraint={}):
    """ configure the split_gearwheel design
    """
    self.set_design_name("split_gearwheel")
    self.set_constraint_constructor(split_gearwheel_constraint_constructor)
    self.set_constraint_check(split_gearwheel_constraint_check)
    self.set_2d_constructor(split_gearwheel_2d_construction)
    self.set_2d_simulation(split_gearwheel_2d_simulations())
    self.set_3d_constructor(split_gearwheel_3d_construction)
    self.set_info(split_gearwheel_info)
    self.set_display_figure_list(['sgw_assembly_fig', 'sgw_even_assembly_fig', 'sgw_odd_assembly_fig', 'sgw_list_of_parts'])
    self.set_default_simulation()
    self.set_2d_figure_file_list([]) # all figures
    self.set_3d_figure_file_list(['sgw_even_assembly_fig', 'sgw_odd_assembly_fig'])
    self.set_3d_conf_file_list(['split_gearwheel_3dconf1'])
    self.set_allinone_return_type()
    self.set_self_test(split_gearwheel_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("split_gearwheel.py says hello!\n")
  my_sgw = split_gearwheel()
  #my_sgw.allinone()
  my_sgw.allinone("--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2")
  #my_sgw.allinone("--gear_tooth_nb 17 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_sgw.get_fc_obj('split_gearwheel_3dconf1'))

