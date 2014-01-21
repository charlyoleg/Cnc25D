# axle_lid.py
# generates an axle_lid assembly that can complete a epicyclic-gearing.
# created by charlyoleg on 2013/10/15
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
axle_lid.py is a parametric generator of an assembly that completes the epicyclic-gearing system.
The main function displays in a Tk-interface the axle-lid assembly, or generates the design as files or returns the design as FreeCAD Part object.
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
import gearring

################################################################
# inheritance from gearring
################################################################

def inherit_gearring(c={}):
  """ generate the gearring with the construct c
  """
  gr_c = c.copy()
  gr_c['gear_tooth_nb']               = 0
  gr_c['gear_primitive_diameter']     = 100.0 # temporary fictive value
  gr_c['center_position_x']           = 0.0
  gr_c['center_position_y']           = 0.0
  gr_c['gear_initial_angle']          = 0.0
  r_obj = gearring.gearring()
  r_obj.apply_external_constraint(gr_c)
  return(r_obj)

################################################################
# axle_lid constraint_constructor
################################################################

def axle_lid_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the axle_lid design
  """
  r_parser = ai_parser
  ### annulus-holder: inherit dictionary entries from gearring
  i_gearring = inherit_gearring()
  r_parser = i_gearring.get_constraint_constructor()(r_parser, 1)
  ### axle_lid stuff
  r_parser.add_argument('--clearance_diameter','--cld', action='store', type=float, default=50.0,
    help="Set the diameter of the clearance circle. Default: 50.0")
  r_parser.add_argument('--central_diameter','--ced', action='store', type=float, default=30.0,
    help="Set the diameter of the central circle. Default: 30.0")
  r_parser.add_argument('--axle_hole_diameter','--ahd', action='store', type=float, default=22.0,
    help="Set the diameter of the axle-hole. Default: 22.0")
  r_parser.add_argument('--annulus_holder_axle_hole_diameter','--ahahd', action='store', type=float, default=0.0,
    help="Set the diameter of the axle-hole on the annulus-holder side. If equal to 0.0, it is set to axle_hole_diameter. Default: 0.0")
  if(ai_variant!=1):
    ### axle-B
    r_parser.add_argument('--output_axle_B_place','--oabp', action='store', default='none',
      help="Set the side to generate the axle_B. Possible values: 'none', 'small', 'large'. Default: 'none'")
    r_parser.add_argument('--output_axle_distance','--oad', action='store', type=float, default=0.0,
      help="Set the distance between the output_axle and output_axle_B. Default: 0.0")
    r_parser.add_argument('--output_axle_angle','--oaa', action='store', type=float, default=0.0,
      help="Set the angle between the output_axle and output_axle_B. Default: 0.0")
    r_parser.add_argument('--output_axle_B_internal_diameter','--oabid', action='store', type=float, default=0.0,
      help="Set the internal diameter of the axle_B. Default: 0.0")
    r_parser.add_argument('--output_axle_B_external_diameter','--oabed', action='store', type=float, default=0.0,
      help="Set the external diameter of the axle_B. If equal to 0.0, it is set to 2*output_axle_B_internal_diameter. Default: 0.0")
    r_parser.add_argument('--output_axle_B_crenel_number','--oabcn', action='store', type=int, default=0,
      help="Set the number of crenels around the axle_B. If equal to 0, no crenel for the axle_B is generated. Default: 0")
    r_parser.add_argument('--output_axle_B_crenel_diameter','--oabcd', action='store', type=float, default=0.0,
      help="Set the diameter of the crenels placed around the axle_B. Default: 0.0")
    r_parser.add_argument('--output_axle_B_crenel_position_diameter','--oabcpd', action='store', type=float, default=0.0,
      help="Set the diameter of the position circle of the axle_B crenels. If equal to 0.0, it is set to the mean of the axle_B external and internal diameters. Default: 0.0")
    r_parser.add_argument('--output_axle_B_crenel_angle','--oabca', action='store', type=float, default=0.0,
      help="Set the position angle of the first crenel placed around the axle_B. Default: 0.0")
    r_parser.add_argument('--input_axle_B_enable','--iabe', action='store_true', default=False,
      help="Enable the generation of the annulus-holder-input-axle-B. Default: False")
  ### leg
  r_parser.add_argument('--leg_type','--lt', action='store', default='none',
    help="Set the type of leg. Possible values: 'none', 'rear', 'side'. Default: 'none'")
  r_parser.add_argument('--leg_length','--ll', action='store', type=float, default=0.0,
    help="Set the length between the center of the gearring and the end of the leg. Default: 0.0")
  r_parser.add_argument('--foot_length','--fl', action='store', type=float, default=0.0,
    help="Set the length between the end of the leg and the center of the holes. If equal to 0.0, set to leg_hole_diameter. Default: 0.0")
  r_parser.add_argument('--toe_length','--tl', action='store', type=float, default=0.0,
    help="Set the length between the center of the holes and the end of the leg-foot-toe. If equal to 0.0, set to leg_hole_diameter. Default: 0.0")
  r_parser.add_argument('--leg_hole_diameter','--lhd', action='store', type=float, default=0.0,
    help="Set the diameter of the leg-holes. If equal to 0.0, no holes is generated. Default: 0.0")
  r_parser.add_argument('--leg_hole_distance','--lhdis', action='store', type=float, default=0.0,
    help="Set the distance between a pair of leg-holes. If equal to 0.0, it is set to 2*leg_hole_diameter. Default: 0.0")
  r_parser.add_argument('--leg_hole_length','--lhl', action='store', type=float, default=0.0,
    help="Set the length of the leg-holes. Default: 0.0")
  r_parser.add_argument('--leg_border_length','--lbl', action='store', type=float, default=0.0,
    help="Set the width of the leg-borders. If equal to 0.0, it is set to leg_hole_diameter. Default: 0.0")
  r_parser.add_argument('--leg_shift_length','--lsl', action='store', type=float, default=0.0,
    help="Set the length between middle axe of the gearring and the middle of the pair of leg-holes. Default: 0.0")
  if(ai_variant!=1):
    ### general
    r_parser.add_argument('--smoothing_radius','--sr', action='store', type=float, default=0.0,
      help="Set the smoothing radius for the axle-lid. If equal to 0.0, it is set to cnc_router_bit_radius. Default: 0.0")
    r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1,
      help="Set the minimum router_bit radius of the axle-lid. Default: 0.1")
    r_parser.add_argument('--extrusion_height','--eh', action='store', type=float, default=10.0,
      help="Set the height of the linear extrusion of each part of the axle_lid assembly. Default: 10.0")
  ### output
  # return
  return(r_parser)

################################################################
# constraint conversion
################################################################

def gearring_constraint(c):
  """ convert the axle_lid constraint into gearring constraint
  """
  #print("dbg155: holder_radius:", c['holder_radius'], "annulus_holder_axle_hole_radius:", c['annulus_holder_axle_hole_radius'], "holder_hole_diameter:", c['holder_hole_diameter'])
  gr_c = {}
  gr_c['gear_tooth_nb']               = 0
  gr_c['gear_primitive_diameter']     = 2.0*c['clearance_radius']
  gr_c['holder_diameter']             = 2.0*c['holder_radius']
  gr_c['holder_crenel_number']        = c['holder_crenel_number']
  gr_c['holder_position_angle']       = c['holder_position_angle']
  gr_c['holder_hole_position_radius'] = c['holder_hole_position_radius']
  gr_c['holder_hole_diameter']        = c['holder_hole_diameter']
  gr_c['holder_double_hole_diameter'] = c['holder_double_hole_diameter']
  gr_c['holder_double_hole_length']   = c['holder_double_hole_length']
  gr_c['holder_double_hole_position'] = c['holder_double_hole_position']
  gr_c['holder_double_hole_mark_nb']  = c['holder_double_hole_mark_nb']
  gr_c['holder_crenel_position']      = c['holder_crenel_position']
  gr_c['holder_crenel_height']        = c['holder_crenel_height']
  gr_c['holder_crenel_width']         = c['holder_crenel_width']
  gr_c['holder_crenel_skin_width']    = c['holder_crenel_skin_width']
  gr_c['holder_crenel_router_bit_radius'] = c['holder_crenel_router_bit_radius']
  gr_c['holder_smoothing_radius']     = c['holder_smoothing_radius']
  gr_c['cnc_router_bit_radius']       = c['cnc_router_bit_radius']
  gr_c['gear_profile_height']         = c['extrusion_height']
  gr_c['center_position_x']           = 0.0
  gr_c['center_position_y']           = 0.0
  gr_c['gear_initial_angle']          = 0.0
  return(gr_c)

################################################################
# axle_lid constraint_check
################################################################

def axle_lid_constraint_check(c):
  """ check the axle_lid constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  c['axle_hole_radius'] = c['axle_hole_diameter']/2.0
  c['central_radius'] = c['central_diameter']/2.0
  c['clearance_radius'] = c['clearance_diameter']/2.0
  c['holder_radius'] = c['holder_diameter']/2.0
  c['annulus_holder_axle_hole_radius'] = c['annulus_holder_axle_hole_diameter']/2.0
  if(c['annulus_holder_axle_hole_radius']==0):
    if(c['axle_hole_radius']>radian_epsilon):
      c['annulus_holder_axle_hole_radius'] = c['axle_hole_radius']
    else:
      c['annulus_holder_axle_hole_radius'] = c['clearance_radius'] #c['holder_radius']/2.0 # rare case not really usefull
  ### gearring-holder
  i_gearring = inherit_gearring()
  c['gr_c'] = gearring_constraint(c)
  i_gearring.apply_constraint(c['gr_c'])
  holder_parameters = i_gearring.get_constraint()
  c['holder_crenel_half_width'] = holder_parameters['holder_crenel_half_width']
  c['holder_crenel_half_angle'] = holder_parameters['holder_crenel_half_angle']
  c['holder_smoothing_radius'] = holder_parameters['holder_smoothing_radius']
  c['holder_crenel_x_position'] = holder_parameters['holder_crenel_x_position']
  c['holder_maximal_height_plus'] = holder_parameters['holder_maximal_height_plus']
  c['holder_crenel_router_bit_radius'] = holder_parameters['holder_crenel_router_bit_radius']
  c['holder_side_outer_smoothing_radius'] = holder_parameters['holder_side_outer_smoothing_radius']
  c['holder_hole_position_radius'] = holder_parameters['holder_hole_position_radius']
  c['holder_hole_radius'] = holder_parameters['holder_hole_radius']
  c['holder_double_hole_radius'] = holder_parameters['holder_double_hole_radius']
  c['holder_double_hole_length'] = holder_parameters['holder_double_hole_length']
  c['holder_double_hole_position'] = holder_parameters['holder_double_hole_position']
  c['holder_double_hole_mark_nb'] = holder_parameters['holder_double_hole_mark_nb']
  c['holder_double_hole_position_radius'] = holder_parameters['holder_double_hole_position_radius']
  c['holder_radius'] = holder_parameters['holder_radius']
  c['holder_maximal_radius'] = holder_parameters['holder_maximal_radius']
  #print("dbg220: holder_radius:", c['holder_radius'])
  #print("dbg204: holder_hole_radius {:0.3f}  holder_double_hole_length {:0.3f}".format(c['holder_hole_radius'], c['holder_double_hole_length']))
  #if(c['cnc_router_bit_radius']>c['axle_hole_radius']):
  #  print("ERR141: Error, cnc_router_bit_radius {:0.3f} is bigger than axle_hole_radius {:0.3f}".format(c['cnc_router_bit_radius'], c['axle_hole_radius']))
  #  sys.exit(2)
  if(c['axle_hole_radius']>c['central_radius']-radian_epsilon):
    print("ERR144: Error, axle_hole_radius {:0.3f} is bigger than central_radius {:0.3f}".format(c['axle_hole_radius'], c['central_radius']))
    sys.exit(2)
  if(c['central_radius']>c['clearance_radius']-radian_epsilon):
    print("ERR147: Error, central_radius {:0.3f} is bigger than clearance_radius {:0.3f}".format(c['central_radius'], c['clearance_radius']))
    sys.exit(2)
  if(c['clearance_radius']>c['holder_radius']-radian_epsilon):
    print("ERR151: Error, clearance_radius {:0.3f} is bigger than the holder_radius {:0.3f}".format(c['clearance_radius'], c['holder_radius']))
    sys.exit(2)
  if(c['annulus_holder_axle_hole_radius']>c['clearance_radius']):
    print("ERR159: Error, annulus_holder_axle_hole_radius {:0.3f} is bigger than clearance_radius {:0.3f}".format(c['annulus_holder_axle_hole_radius'], c['clearance_radius']))
    sys.exit(2)
  if(c['holder_crenel_number']<4):
    print("ERR154: Error, holder_crenel_number {:d} is smaller than 4".format(c['holder_crenel_number']))
    sys.exit(2)
  c['middle_crenel_1'] = 0
  c['middle_crenel_2'] = int(c['holder_crenel_number']/2)
  if(c['output_axle_B_place'] == 'large'):
    c['middle_crenel_2'] = int((c['holder_crenel_number']+1)/2)
  c['middle_crenel_index'] = [c['middle_crenel_1'], c['middle_crenel_2']]
  c['crenel_portion_angle'] = 2*math.pi/c['holder_crenel_number']
  c['g1_ix'] = 0.0
  c['g1_iy'] = 0.0
  c['middle_angle_1'] = (c['middle_crenel_1'] + 1 + c['middle_crenel_2'])/2.0*c['crenel_portion_angle'] + c['gr_c']['holder_position_angle']
  middle_angle_2 = c['middle_angle_1'] + math.pi
  c['middle_angles'] = (c['middle_angle_1'], middle_angle_2)
  c['angle_incr'] = c['crenel_portion_angle']
  c['lid_router_bit_radius'] = c['holder_crenel_router_bit_radius']
  c['lid_smoothing_router_bit_radius'] = c['smoothing_radius']
  if(c['lid_smoothing_router_bit_radius']==0):
    c['lid_smoothing_router_bit_radius'] = c['lid_router_bit_radius']
  # leg default values
  c['leg_hole_radius'] = c['leg_hole_diameter']/2.0
  if(c['foot_length']==0):
    c['foot_length'] = 2*c['leg_hole_radius']
  if(c['toe_length']==0):
    c['toe_length'] = 2*c['leg_hole_radius']
  if(c['leg_border_length']==0):
    c['leg_border_length'] = 2*c['leg_hole_radius']
  if(c['leg_hole_distance']==0):
    c['leg_hole_distance'] = 2*(2*c['leg_hole_radius'] + c['leg_hole_length'])
  if(c['leg_type'] != 'none'):
    if((c['leg_type'] != 'rear') and (c['leg_type'] != 'side')):
      print("ERR536: Error, leg_type {:s} set to an unknow value. Possible values: 'none', 'rear' or 'side'".format(c['leg_type']))
      sys.exit(2)
    if(c['leg_length']<=0):
      print("ERR539: Error, leg_length {:0.3f} must be strictly positive".format(c['leg_length']))
      sys.exit(2)
    if(c['toe_length']<c['leg_hole_radius']):
      print("ERR543: Error, toe_length {:0.3f} is smaller than leg_hole_radius {:0.3f}".format(c['toe_length'], c['leg_hole_radius']))
      sys.exit(2)
    #if(c['foot_length']<c['leg_hole_radius']):
    #  print("ERR543: Error, foot_length {:0.3f} is smaller than leg_hole_radius {:0.3f}".format(c['foot_length'], c['leg_hole_radius']))
    #  sys.exit(2)
    if(c['leg_hole_distance']<2*c['leg_hole_radius']+c['leg_hole_length']):
      print("ERR549: Error, leg_hole_distance {:0.3f} is too small compare to leg_hole_radius {:0.3f} and leg_hole_length {:0.3f}".format(c['leg_hole_distance'], c['leg_hole_radius'], c['leg_hole_length']))
      sys.exit(2)
    if(c['leg_border_length']<c['leg_hole_radius']):
      print("ERR552: Error, leg_border_length {:0.3f} is smaller than leg_hole_radius {:0.3f}".format(c['leg_border_length'], c['leg_hole_radius']))
      sys.exit(2)
  ### axle_B
  c['output_axle_B_internal_radius'] = c['output_axle_B_internal_diameter']/2.0
  c['output_axle_B_external_radius'] = c['output_axle_B_external_diameter']/2.0
  c['output_axle_B_crenel_radius'] = c['output_axle_B_crenel_diameter']/2.0
  c['output_axle_B_crenel_position_radius'] = c['output_axle_B_crenel_position_diameter']/2.0
  c['output_axle_B_angle'] = c['middle_angle_1'] + c['output_axle_angle']
  ### constraint info preparation
  c['holder_parameter_info'] = """
holder crenel number:     \t{:d}
holder hole radius:       \t{:0.3f} diameter: \t{:0.3f}
holder external radius:   \t{:0.3f} diameter: \t{:0.3f}
clearance radius:         \t{:0.3f} diameter: \t{:0.3f}
central radius:           \t{:0.3f} diameter: \t{:0.3f}
axle-hole radius:         \t{:0.3f} diameter: \t{:0.3f}
annulus-holder-axle-hole radius: \t{:0.3f} diameter: \t{:0.3f}
holder_crenel_router_bit_radius:  \t{:0.3f} diameter: \t{:0.3f}
holder_smoothing_radius:          \t{:0.3f} diameter: \t{:0.3f}
cnc_router_bit_radius:    \t{:0.3f} diameter: \t{:0.3f}
""".format(c['holder_crenel_number'], c['holder_hole_diameter']/2.0, c['holder_hole_diameter'], c['holder_radius'], 2*c['holder_radius'], c['clearance_radius'], 2*c['clearance_radius'], c['central_radius'], 2*c['central_radius'], c['axle_hole_radius'], 2*c['axle_hole_radius'], c['annulus_holder_axle_hole_radius'], 2*c['annulus_holder_axle_hole_radius'], c['holder_crenel_router_bit_radius'], 2*c['holder_crenel_router_bit_radius'], c['holder_smoothing_radius'], 2*c['holder_smoothing_radius'], c['cnc_router_bit_radius'], 2*c['cnc_router_bit_radius'])
  c['leg_parameter_info'] = """
leg_type:     \t{:s}
leg_length:   \t{:0.3f}
foot_length:  \t{:0.3f}
toe_length:   \t{:0.3f}
leg_hole_radius:    \t{:0.3f}  \tdiameter: {:0.3f}
leg_hole_distance:  \t{:0.3f}
leg_hole_length:    \t{:0.3f}
leg_border_length:  \t{:0.3f}
leg_shift_length:   \t{:0.3f}
""".format(c['leg_type'], c['leg_length'], c['foot_length'], c['toe_length'], c['leg_hole_radius'], 2*c['leg_hole_radius'], c['leg_hole_distance'], c['leg_hole_length'], c['leg_border_length'], c['leg_shift_length'])
  c['parameter_info_for_motor_lid'] = c['holder_parameter_info'] + c['leg_parameter_info']
  ###
  return(c)

################################################################
# axle_lid 2D-figures construction
################################################################

def axle_lid_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the axle_lid design
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### holder_cut_outlines
  holder_cut_side_outlines = []
  holder_cut_face_outlines = []
  ## holder_cut_side_outlines
  for i in range(len(c['middle_crenel_index'])):
    idx = c['middle_crenel_index'][i]
    holder_A = []
    # first crenel
    holder_A .extend(gearring.make_holder_crenel(c['holder_maximal_height_plus'], c['gr_c']['holder_crenel_height'], c['gr_c']['holder_crenel_skin_width'], c['holder_crenel_half_width'], 
                                        c['holder_crenel_router_bit_radius'], c['holder_side_outer_smoothing_radius'], c['holder_smoothing_radius'],
                                        c['holder_crenel_x_position'], c['gr_c']['holder_position_angle']+idx*c['angle_incr'], c['g1_ix'], c['g1_iy']))
    # external arc
    middle_angle = c['gr_c']['holder_position_angle'] + (idx+0.5)*c['angle_incr']
    end_angle = c['gr_c']['holder_position_angle'] + (idx+1)*c['angle_incr'] - c['holder_crenel_half_angle']
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(middle_angle), c['g1_iy']+c['holder_radius']*math.sin(middle_angle),
                      c['g1_ix']+c['holder_radius']*math.cos(end_angle), c['g1_iy']+c['holder_radius']*math.sin(end_angle), c['holder_smoothing_radius']])
    # second crenel
    holder_A .extend(gearring.make_holder_crenel(c['holder_maximal_height_plus'], c['gr_c']['holder_crenel_height'], c['gr_c']['holder_crenel_skin_width'], c['holder_crenel_half_width'], 
                                        c['holder_crenel_router_bit_radius'], c['holder_side_outer_smoothing_radius'], c['holder_smoothing_radius'],
                                        c['holder_crenel_x_position'], c['gr_c']['holder_position_angle']+(idx+1)*c['angle_incr'], c['g1_ix'], c['g1_iy']))
    #holder_A[-1] = (holder_A[-1][0], holder_A[-1][1], c['lid_router_bit_radius']) # change the router_bit of the last point # this point must be removed
    # save the portion of outline
    holder_cut_side_outlines.append(holder_A[:-1]) # remove the last point
  holder_cut_first_point = holder_cut_side_outlines[0][0]
  ## holder_cut_face_outlines
  for i in range(len(c['middle_crenel_index'])):
    idx = c['middle_crenel_index'][i] + 1
    cut_length = (c['middle_crenel_index'][i-1] - (c['middle_crenel_index'][i-2] + 1) + c['holder_crenel_number']) % c['holder_crenel_number'] - 1
    #print("dbg296: idx {:d}  cut_length {:d}   middle_crenel_index_i_-1 {:d}   middle_crenel_index_i_-2 {:d}".format(idx, cut_length, c['middle_crenel_index'][i-1], c['middle_crenel_index'][i-2]))
    holder_A = []
    # first point
    first_angle = c['gr_c']['holder_position_angle'] + (idx+0.0)*c['angle_incr'] + c['holder_crenel_half_angle']
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(first_angle), c['g1_iy']+c['holder_radius']*math.sin(first_angle), c['holder_smoothing_radius']])
    # first arc
    middle_angle = c['gr_c']['holder_position_angle'] + (idx+0.5)*c['angle_incr']
    end_angle = c['gr_c']['holder_position_angle'] + (idx+1)*c['angle_incr'] - c['holder_crenel_half_angle']
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(middle_angle), c['g1_iy']+c['holder_radius']*math.sin(middle_angle),
                      c['g1_ix']+c['holder_radius']*math.cos(end_angle), c['g1_iy']+c['holder_radius']*math.sin(end_angle), c['holder_smoothing_radius']])
    for j in range(cut_length):
      # crenel
      holder_A .extend(gearring.make_holder_crenel(c['holder_maximal_height_plus'], c['gr_c']['holder_crenel_height'], c['gr_c']['holder_crenel_skin_width'], c['holder_crenel_half_width'], 
                                          c['holder_crenel_router_bit_radius'], c['holder_side_outer_smoothing_radius'], c['holder_smoothing_radius'],
                                          c['holder_crenel_x_position'], c['gr_c']['holder_position_angle']+(idx+j+1)*c['angle_incr'], c['g1_ix'], c['g1_iy']))
      # external arc
      middle_angle = c['gr_c']['holder_position_angle'] + (idx+j+1.5)*c['angle_incr']
      end_angle = c['gr_c']['holder_position_angle'] + (idx+j+2)*c['angle_incr'] - c['holder_crenel_half_angle']
      holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(middle_angle), c['g1_iy']+c['holder_radius']*math.sin(middle_angle),
                        c['g1_ix']+c['holder_radius']*math.cos(end_angle), c['g1_iy']+c['holder_radius']*math.sin(end_angle), c['holder_smoothing_radius']])
    # save the portion of outline
    holder_cut_face_outlines.append(holder_A[:]) # small and large faces
  ### middle_axle_lid
  middle_lid_outlines = []
  for i in range(2):
    idx = c['middle_crenel_index'][i]
    holder_A = []
    # first point
    first_angle = c['gr_c']['holder_position_angle'] - c['holder_crenel_half_angle'] + idx*c['angle_incr']
    holder_A.append([c['g1_ix']+c['clearance_radius']*math.cos(first_angle), c['g1_iy']+c['clearance_radius']*math.sin(first_angle), c['lid_router_bit_radius']])
    # first line
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(first_angle), c['g1_iy']+c['holder_radius']*math.sin(first_angle), c['lid_router_bit_radius']])
    # holder_cut_side_outlines
    holder_A.extend(holder_cut_side_outlines[i])
    # second to last line
    last_angle = c['gr_c']['holder_position_angle'] + c['holder_crenel_half_angle'] + (idx+1)*c['angle_incr']
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(last_angle), c['g1_iy']+c['holder_radius']*math.sin(last_angle), c['lid_router_bit_radius']])
    holder_A.append([c['g1_ix']+c['clearance_radius']*math.cos(last_angle), c['g1_iy']+c['clearance_radius']*math.sin(last_angle), c['lid_router_bit_radius']])
    # last arc
    middle_angle = c['gr_c']['holder_position_angle'] + (idx+0.5)*c['angle_incr']
    holder_A.append([c['g1_ix']+c['clearance_radius']*math.cos(middle_angle), c['g1_iy']+c['clearance_radius']*math.sin(middle_angle),
                      c['g1_ix']+c['clearance_radius']*math.cos(first_angle), c['g1_iy']+c['clearance_radius']*math.sin(first_angle), 0])
    # save the portion of outline
    middle_lid_outlines.append(holder_A[:])
  ### holes
  ## side_hole_figures
  side_hole_figures = []
  for i in range(2):
    idx = c['middle_crenel_index'][i]
    hole_figure = []
    if(c['holder_hole_radius']>0):
      for j in range(2):
        hole_angle = c['gr_c']['holder_position_angle']+((idx+j)*c['angle_incr'])
        hole_figure.append([c['g1_ix']+c['holder_hole_position_radius']*math.cos(hole_angle), c['g1_iy']+c['holder_hole_position_radius']*math.sin(hole_angle), c['holder_hole_radius']])
    if(c['holder_double_hole_radius']>0):
      tmp_a2 = math.atan(c['holder_double_hole_length']/2.0/c['holder_double_hole_position_radius']) # if double carrier-crenel-hole
      tmp_l2 = math.sqrt(c['holder_double_hole_position_radius']**2+(c['holder_double_hole_length']/2.0)**2)
      for j in range(2):
        hole_angle = c['gr_c']['holder_position_angle']+((idx+j)*c['angle_incr'])
        hole_figure.append([c['g1_ix']+tmp_l2*math.cos(hole_angle-tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle-tmp_a2), c['holder_double_hole_radius']])
        hole_figure.append([c['g1_ix']+tmp_l2*math.cos(hole_angle+tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle+tmp_a2), c['holder_double_hole_radius']])
    side_hole_figures.append(hole_figure[:])
  ## face_hole_figures
  face_hole_figures = []
  for i in range(2):
    idx = c['middle_crenel_index'][i] + 2
    cut_length = (c['middle_crenel_index'][i-1] - (c['middle_crenel_index'][i-2] + 1) + c['holder_crenel_number']) % c['holder_crenel_number'] - 1
    hole_figure = []
    if(c['holder_hole_radius']>0):
      for j in range(cut_length):
        hole_angle = c['gr_c']['holder_position_angle']+((idx+j)*c['angle_incr'])
        hole_figure.append([c['g1_ix']+c['holder_hole_position_radius']*math.cos(hole_angle), c['g1_iy']+c['holder_hole_position_radius']*math.sin(hole_angle), c['holder_hole_radius']])
    if(c['holder_double_hole_radius']>0):
      tmp_a2 = math.atan(c['holder_double_hole_length']/2.0/c['holder_double_hole_position_radius']) # if double carrier-crenel-hole
      tmp_l2 = math.sqrt(c['holder_double_hole_position_radius']**2+(c['holder_double_hole_length']/2.0)**2)
      for j in range(cut_length):
        hole_angle = c['gr_c']['holder_position_angle']+((idx+j)*c['angle_incr'])
        hole_figure.append([c['g1_ix']+tmp_l2*math.cos(hole_angle-tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle-tmp_a2), c['holder_double_hole_radius']])
        hole_figure.append([c['g1_ix']+tmp_l2*math.cos(hole_angle+tmp_a2), c['g1_iy']+tmp_l2*math.sin(hole_angle+tmp_a2), c['holder_double_hole_radius']])
    face_hole_figures.append(hole_figure[:])

  ## middle_axle_lid
  middle_lid_figures = []
  for i in range(2):
    one_middle_figure = []
    one_middle_figure.append(middle_lid_outlines[i])
    one_middle_figure.extend(side_hole_figures[i]) 
    middle_lid_figures.append(one_middle_figure[:])

  ### face_top_lid_outlines
  face_top_lid_outlines = []
  for i in range(2):
    idx_1 = c['middle_crenel_index'][i]+1
    idx_2 = c['middle_crenel_index'][i-1]
    first_angle = c['gr_c']['holder_position_angle'] + c['holder_crenel_half_angle'] + idx_1*c['angle_incr']
    last_angle = c['gr_c']['holder_position_angle'] - c['holder_crenel_half_angle'] + idx_2*c['angle_incr']
    holder_A = []
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(first_angle), c['g1_iy']+c['holder_radius']*math.sin(first_angle), c['lid_router_bit_radius']])
    holder_A.append([c['g1_ix']+c['clearance_radius']*math.cos(first_angle), c['g1_iy']+c['clearance_radius']*math.sin(first_angle), c['lid_router_bit_radius']])
    holder_A.append((c['g1_ix']+c['central_radius']*math.cos(c['middle_angles'][i]), c['g1_iy']+c['central_radius']*math.sin(c['middle_angles'][i]), c['holder_smoothing_radius']))
    holder_A.append([c['g1_ix']+c['clearance_radius']*math.cos(last_angle), c['g1_iy']+c['clearance_radius']*math.sin(last_angle), c['lid_router_bit_radius']])
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(last_angle), c['g1_iy']+c['holder_radius']*math.sin(last_angle), c['lid_router_bit_radius']])
    # save the portion of outline
    face_top_lid_outlines.append(holder_A[:])

  ### axle_B
  if(c['output_axle_B_place'] != 'none'):
    if((c['output_axle_B_place'] != 'small')and(c['output_axle_B_place'] != 'large')):
      print("ERR442: Error, output_axle_B_place {:s} is unknown. Possible values: 'none', 'small' or 'large'".format(c['output_axle_B_place']))
      sys.exit(2)
    if(c['output_axle_distance']<=0.0):
      print("ERR445: Error, output_axle_distance {:0.3f} must be positive".format(c['output_axle_distance']))
      sys.exit(2)
    if(c['output_axle_B_external_radius'] == 0):
      c['output_axle_B_external_radius'] = 2*c['output_axle_B_internal_radius']
    if(c['output_axle_B_external_radius']<=c['output_axle_B_internal_radius']):
      print("ERR452: Error, output_axle_B_external_radius {:0.3f} is null or smaller than output_axle_B_internal_radius {:0.3f}".format(c['output_axle_B_external_radius'], c['output_axle_B_internal_radius']))
      sys.exit(2)
    if(c['output_axle_B_crenel_number']>0):
      if(c['output_axle_B_crenel_radius']<radian_epsilon):
        print("ERR460: Error, output_axle_B_crenel_radius {:0.3f} is too small".format(c['output_axle_B_crenel_radius']))
        sys.exit(2)
      if(c['output_axle_B_crenel_position_radius'] == 0):
        c['output_axle_B_crenel_position_radius'] = (c['output_axle_B_internal_radius'] + c['output_axle_B_external_radius'])/2.0
      if(c['output_axle_B_crenel_position_radius']<(c['output_axle_B_internal_radius']+c['output_axle_B_crenel_radius'])):
        print("ERR460: Error, output_axle_B_crenel_position_radius {:0.3f} is too small compare to output_axle_B_internal_radius {:0.3f} and output_axle_B_crenel_radius {:0.3f}".format(c['output_axle_B_crenel_position_radius'], c['output_axle_B_internal_radius'], c['output_axle_B_crenel_radius']))
        sys.exit(2)
      if(c['output_axle_B_crenel_position_radius']>(c['output_axle_B_external_radius']-c['output_axle_B_crenel_radius'])):
        print("ERR463: Error, output_axle_B_crenel_position_radius {:0.3f} is too big compare to output_axle_B_external_radius {:0.3f} and output_axle_B_crenel_radius {:0.3f}".format(c['output_axle_B_crenel_position_radius'], c['output_axle_B_external_radius'], c['output_axle_B_crenel_radius']))
        sys.exit(2)
    ## calculation of the angle (DCE)
    ABC = (c['middle_crenel_2'] - c['middle_crenel_1'] - 1) * c['crenel_portion_angle'] / 2.0 - c['holder_crenel_half_angle']
    ABC1 = ABC + c['output_axle_angle']
    AB = c['holder_maximal_radius']
    BC = c['output_axle_distance']
    # law of cosines to get AC and (ACB)
    AC1 = math.sqrt(AB**2 + BC**2 - 2*AB*BC*math.cos(ABC1))
    cos_ACB1 = ((AC1**2+BC**2-AB**2)/(2*AC1*BC))
    if((cos_ACB1<radian_epsilon)or(cos_ACB1>1-radian_epsilon)):
      print("ERR474: Error, cos_ACB1 {:0.3f} is out of the range 0..1".format(cos_ACB1))
      sys.exit(2)
    ACB1 = math.acos(cos_ACB1)
    DC = c['output_axle_B_external_radius']
    cos_ACD1 = float(DC)/AC1
    ACD1 = math.acos(cos_ACD1)
    DCE1 = math.pi - ACD1 - ACB1
    ABC2 = ABC - c['output_axle_angle']
    AC2 = math.sqrt(AB**2 + BC**2 - 2*AB*BC*math.cos(ABC2))
    cos_ACB2 = ((AC2**2+BC**2-AB**2)/(2*AC2*BC))
    ACB2 = math.acos(cos_ACB2)
    cos_ACD2 = float(DC)/AC2
    ACD2 = math.acos(cos_ACD2)
    DCE2 = math.pi - ACD2 - ACB2
    #print("dbg486: ACD {:0.3f}  ACB {:0.3f}  DC {:0.3f}  AC {:0.3f}".format(ACD, ACB, DC, AC))
    #print("dbg483: DCE {:0.3f}  middle_angle_1 {:0.3f}".format(DCE, c['middle_angle_1']))
    ## axle_B_outline
    axle_B_outline = []
    axle_B_outline.append((c['g1_ix']+BC*math.cos(c['output_axle_B_angle'])+DC*math.cos(c['output_axle_B_angle']-DCE1), c['g1_iy']+BC*math.sin(c['output_axle_B_angle'])+DC*math.sin(c['output_axle_B_angle']-DCE1), 0))
    axle_B_outline.append((c['g1_ix']+BC*math.cos(c['output_axle_B_angle'])+DC*math.cos(c['output_axle_B_angle']+(DCE2-DCE1)/2.0), c['g1_iy']+BC*math.sin(c['output_axle_B_angle'])+DC*math.sin(c['output_axle_B_angle']+(DCE2-DCE1)/2.0),
                           c['g1_ix']+BC*math.cos(c['output_axle_B_angle'])+DC*math.cos(c['output_axle_B_angle']+DCE2), c['g1_iy']+BC*math.sin(c['output_axle_B_angle'])+DC*math.sin(c['output_axle_B_angle']+DCE2), 0))
    ## axle_B_hole_figure
    axle_B_hole_figure = []
    if(c['output_axle_B_internal_radius']>radian_epsilon):
      axle_B_hole_figure.append((c['g1_ix']+BC*math.cos(c['output_axle_B_angle']), c['g1_iy']+BC*math.sin(c['output_axle_B_angle']), c['output_axle_B_internal_radius']))
    if(c['output_axle_B_crenel_number']>0):
      crenel_B_angle = 2*math.pi/c['output_axle_B_crenel_number']
      for i in range(c['output_axle_B_crenel_number']):
        axle_B_hole_figure.append((c['g1_ix']+BC*math.cos(c['output_axle_B_angle'])+c['output_axle_B_crenel_position_radius']*math.cos(c['output_axle_B_angle']+i*crenel_B_angle+c['output_axle_B_crenel_angle']),
                              c['g1_iy']+BC*math.sin(c['output_axle_B_angle'])+c['output_axle_B_crenel_position_radius']*math.sin(c['output_axle_B_angle']+i*crenel_B_angle+c['output_axle_B_crenel_angle']),
                              c['output_axle_B_crenel_radius']))

  ### input_axle_B_outline and input_axle_B_hole_figure for motor_lid
  if(c['input_axle_B_enable']):
    #if(c['output_axle_B_place']=='none'):
    #  print("ERR501: Error, output_axle_B_place set to 'none' and input_axle_B_enable set to True!")
    #  sys.exit(2)
    input_axle_B_external_radius = c['output_axle_B_external_radius']
    input_axle_B_internal_radius = c['output_axle_B_internal_radius']
    first_angle = c['gr_c']['holder_position_angle'] + (c['middle_crenel_1']+1.0)*c['angle_incr'] + c['holder_crenel_half_angle']
    last_angle = c['gr_c']['holder_position_angle'] + (c['middle_crenel_2']+0.0)*c['angle_incr'] - c['holder_crenel_half_angle']
    # external_axle_B_half_angle
    external_axle_B_half_angle = math.atan(float(input_axle_B_external_radius)/c['holder_radius'])
    if(first_angle>c['output_axle_B_angle']-external_axle_B_half_angle):
      print("ERR500: Error, first_angle {:0.3f} too big compare to output_axle_B_angle {:0.3f} and external_axle_B_half_angle {:0.3f}".format(first_angle, c['output_axle_B_angle'], external_axle_B_half_angle))
      sys.exit(2)
    if(last_angle<c['output_axle_B_angle']+external_axle_B_half_angle):
      print("ERR503: Error, last_angle {:0.3f} too small compare to output_axle_B_angle {:0.3f} and external_axle_B_half_angle {:0.3f}".format(last_angle, c['output_axle_B_angle'], external_axle_B_half_angle))
      sys.exit(2)
    holder_A = []
    # first point
    holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(first_angle), c['g1_iy']+c['holder_radius']*math.sin(first_angle), c['holder_smoothing_radius']])
    if(c['holder_radius']>c['output_axle_distance']+0.9*input_axle_B_external_radius):
      middle_angle = (first_angle + last_angle)/2.0
      holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(middle_angle), c['g1_iy']+c['holder_radius']*math.sin(middle_angle),
                      c['g1_ix']+c['holder_radius']*math.cos(last_angle), c['g1_iy']+c['holder_radius']*math.sin(last_angle), c['holder_smoothing_radius']])
    elif(c['holder_radius']>c['output_axle_distance']-0.75*input_axle_B_external_radius):
      # intersection of the external_axle_B and holder_radius: law of cosines
      cos_ia = (c['holder_radius']**2 + c['output_axle_distance']**2 - input_axle_B_external_radius**2)/(2*c['holder_radius']*c['output_axle_distance'])
      intersection_a = math.acos(cos_ia)
      a3 = c['output_axle_B_angle'] - intersection_a
      a2 = (a3+first_angle)/2.0
      a4 = c['output_axle_B_angle']
      a5 = c['output_axle_B_angle'] + intersection_a
      a6 = (a5+last_angle)/2.0
      holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(a2), c['g1_iy']+c['holder_radius']*math.sin(a2),
                      c['g1_ix']+c['holder_radius']*math.cos(a3), c['g1_iy']+c['holder_radius']*math.sin(a3), c['holder_smoothing_radius']])
      holder_A.append([c['g1_ix']+(c['output_axle_distance']+input_axle_B_external_radius)*math.cos(a4), c['g1_iy']+(c['output_axle_distance']+input_axle_B_external_radius)*math.sin(a4),
                      c['g1_ix']+c['holder_radius']*math.cos(a5), c['g1_iy']+c['holder_radius']*math.sin(a5), c['holder_smoothing_radius']])
      holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(a6), c['g1_iy']+c['holder_radius']*math.sin(a6),
                      c['g1_ix']+c['holder_radius']*math.cos(last_angle), c['g1_iy']+c['holder_radius']*math.sin(last_angle), c['holder_smoothing_radius']])
    else:
      a3 = c['output_axle_B_angle'] - external_axle_B_half_angle
      a2 = (a3+first_angle)/2.0
      a4 = c['output_axle_B_angle'] - math.pi/2
      a5 = c['output_axle_B_angle']
      a6 = c['output_axle_B_angle'] + math.pi/2
      a7 = c['output_axle_B_angle'] + external_axle_B_half_angle
      a8 = (a7+last_angle)/2.0
      holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(a2), c['g1_iy']+c['holder_radius']*math.sin(a2),
                      c['g1_ix']+c['holder_radius']*math.cos(a3), c['g1_iy']+c['holder_radius']*math.sin(a3), c['holder_smoothing_radius']])
      holder_A.append([c['g1_ix']+c['output_axle_distance']*math.cos(a5)+input_axle_B_external_radius*math.cos(a4), c['g1_iy']+c['output_axle_distance']*math.sin(a5)+input_axle_B_external_radius*math.sin(a4), 0])
      holder_A.append([c['g1_ix']+(c['output_axle_distance']+input_axle_B_external_radius)*math.cos(a5), c['g1_iy']+(c['output_axle_distance']+input_axle_B_external_radius)*math.sin(a5),
                      c['g1_ix']+c['output_axle_distance']*math.cos(a5)+input_axle_B_external_radius*math.cos(a6), c['g1_iy']+c['output_axle_distance']*math.sin(a5)+input_axle_B_external_radius*math.sin(a6), 0])
      holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(a7), c['g1_iy']+c['holder_radius']*math.sin(a7), c['holder_smoothing_radius']])
      holder_A.append([c['g1_ix']+c['holder_radius']*math.cos(a8), c['g1_iy']+c['holder_radius']*math.sin(a8),
                      c['g1_ix']+c['holder_radius']*math.cos(last_angle), c['g1_iy']+c['holder_radius']*math.sin(last_angle), c['holder_smoothing_radius']])
    input_axle_B_outline = holder_A[:]
    #print("dbg554: input_axle_B_outline:", input_axle_B_outline)
    
    input_axle_B_hole_figure = []
    if(input_axle_B_internal_radius>radian_epsilon):
      input_axle_B_hole_figure.append((c['g1_ix']+c['output_axle_distance']*math.cos(c['output_axle_B_angle']), c['g1_ix']+c['output_axle_distance']*math.sin(c['output_axle_B_angle']), input_axle_B_internal_radius))

  ### leg_outline
  def leg_outline(ai_direction, ai_shift_coef):
    """ It generates the outline of a leg. It can be used to generate the left-side, right-side and rear leg.
        ai_shift_coef lets invert the leg_shift_length parameter if needed
    """
    r_leg_outline = []
    leg_width = c['leg_hole_distance'] + c['leg_hole_length'] + 2 * c['leg_border_length']
    tx = c['g1_ix'] + c['leg_length'] * math.cos(ai_direction)
    ty = c['g1_iy'] + c['leg_length'] * math.sin(ai_direction)
    tx += (leg_width/2.0 + ai_shift_coef * c['leg_shift_length']) * math.cos(ai_direction-math.pi/2)
    ty += (leg_width/2.0 + ai_shift_coef * c['leg_shift_length']) * math.sin(ai_direction-math.pi/2)
    r_leg_outline.append((tx, ty, c['lid_smoothing_router_bit_radius']))
    tx += (c['foot_length'] + c['toe_length']) * math.cos(ai_direction)
    ty += (c['foot_length'] + c['toe_length']) * math.sin(ai_direction)
    r_leg_outline.append((tx, ty, c['lid_smoothing_router_bit_radius']))
    tx += leg_width * math.cos(ai_direction + math.pi/2)
    ty += leg_width * math.sin(ai_direction + math.pi/2)
    r_leg_outline.append((tx, ty, c['lid_smoothing_router_bit_radius']))
    tx += (c['foot_length'] + c['toe_length']) * math.cos(ai_direction + math.pi)
    ty += (c['foot_length'] + c['toe_length']) * math.sin(ai_direction + math.pi)
    r_leg_outline.append((tx, ty, c['lid_smoothing_router_bit_radius']))
    return(r_leg_outline)

  def leg_hole_figure(ai_direction, ai_shift_coef):
    """ It generates the holes of a leg. It can be used to generate the holes of the left-side, right-side and rear leg.
        ai_shift_coef lets invert the leg_shift_length parameter if needed
    """
    r_leg_hole_figure = []
    cx = c['g1_ix'] + (c['leg_length'] + c['foot_length']) * math.cos(ai_direction)
    cy = c['g1_iy'] + (c['leg_length'] + c['foot_length']) * math.sin(ai_direction)
    hd = (c['leg_hole_distance'] - c['leg_hole_length'])/2.0 + ai_shift_coef * c['leg_shift_length']
    cx += hd * math.cos(ai_direction - math.pi/2)
    cy += hd * math.sin(ai_direction - math.pi/2)
    if(c['leg_hole_radius']>0):
      for i in range(2):
        hole_outline = []
        c1x = cx + i * c['leg_hole_distance'] * math.cos(ai_direction+math.pi/2)
        c1y = cy + i * c['leg_hole_distance'] * math.sin(ai_direction+math.pi/2)
        s1x = c1x + c['leg_hole_radius'] * math.cos(ai_direction)
        s1y = c1y + c['leg_hole_radius'] * math.sin(ai_direction)
        m1x = c1x + c['leg_hole_radius'] * math.cos(ai_direction+math.pi/2)
        m1y = c1y + c['leg_hole_radius'] * math.sin(ai_direction+math.pi/2)
        e1x = c1x + c['leg_hole_radius'] * math.cos(ai_direction+math.pi)
        e1y = c1y + c['leg_hole_radius'] * math.sin(ai_direction+math.pi)
        c2x = c1x + c['leg_hole_length'] * math.cos(ai_direction-math.pi/2)
        c2y = c1y + c['leg_hole_length'] * math.sin(ai_direction-math.pi/2)
        s2x = c2x +  c['leg_hole_radius'] * math.cos(ai_direction-math.pi)
        s2y = c2y +  c['leg_hole_radius'] * math.sin(ai_direction-math.pi)
        m2x = c2x +  c['leg_hole_radius'] * math.cos(ai_direction-math.pi/2)
        m2y = c2y +  c['leg_hole_radius'] * math.sin(ai_direction-math.pi/2)
        e2x = c2x +  c['leg_hole_radius'] * math.cos(ai_direction)
        e2y = c2y +  c['leg_hole_radius'] * math.sin(ai_direction)
        hole_outline.append((e1x, e1y))
        if(c['leg_hole_length']>0):
          hole_outline.append((s2x, s2y))
        hole_outline.append((m2x, m2y, e2x, e2y))
        if(c['leg_hole_length']>0):
          hole_outline.append((s1x, s1y))
        hole_outline.append((m1x, m1y, e1x, e1y))
        r_leg_hole_figure.append(hole_outline[:])
    return(r_leg_hole_figure)

  ## annulus_holder_figure
  def f_annulus_holder_figure(ai_axle_B_type, ai_leg_type, ai_input_axle_B_enable):
    """ generate the annulus_holder_figure
    """
    annulus_holder_outline = []
    if(ai_leg_type == 'side'):
      annulus_holder_outline.append((holder_cut_first_point[0], holder_cut_first_point[1], c['lid_smoothing_router_bit_radius']))
      annulus_holder_outline.extend(leg_outline(c['middle_angle_1']-math.pi/2, 1))
      annulus_holder_outline.append((holder_cut_side_outlines[0][-1][0], holder_cut_side_outlines[0][-1][1], c['lid_smoothing_router_bit_radius']))
    else:
      annulus_holder_outline.extend(holder_cut_side_outlines[0])
    if(ai_axle_B_type != 'none'):
      if(ai_input_axle_B_enable):
        annulus_holder_outline.extend(input_axle_B_outline)
      else:
        annulus_holder_outline.extend(axle_B_outline)
    else:
      annulus_holder_outline.extend(holder_cut_face_outlines[0])
    if(ai_leg_type == 'side'):
      annulus_holder_outline.append((holder_cut_side_outlines[1][0][0], holder_cut_side_outlines[1][0][1], c['lid_smoothing_router_bit_radius']))
      annulus_holder_outline.extend(leg_outline(c['middle_angle_1']+math.pi/2, -1))
      annulus_holder_outline.append((holder_cut_side_outlines[1][-1][0], holder_cut_side_outlines[1][-1][1], c['lid_smoothing_router_bit_radius']))
    else:
      annulus_holder_outline.extend(holder_cut_side_outlines[1])
    if(ai_leg_type == 'rear'):
      annulus_holder_outline.extend(leg_outline(c['middle_angle_1']+math.pi, 1))
    else:
      annulus_holder_outline.extend(holder_cut_face_outlines[1])
    annulus_holder_outline.append((holder_cut_first_point[0], holder_cut_first_point[1], 0))
    r_annulus_holder_figure = []
    r_annulus_holder_figure.append(annulus_holder_outline)
    r_annulus_holder_figure.append((c['g1_ix'], c['g1_iy'], c['annulus_holder_axle_hole_radius']))
    r_annulus_holder_figure.extend(side_hole_figures[0])
    if(ai_axle_B_type != 'none'):
      if(ai_input_axle_B_enable):
        r_annulus_holder_figure.extend(input_axle_B_hole_figure)
      else:
        r_annulus_holder_figure.extend(axle_B_hole_figure)
    else:
      r_annulus_holder_figure.extend(face_hole_figures[0])
    r_annulus_holder_figure.extend(side_hole_figures[1])
    r_annulus_holder_figure.extend(face_hole_figures[1])
    if(ai_leg_type == 'side'):
      r_annulus_holder_figure.extend(leg_hole_figure(c['middle_angle_1']-math.pi/2, 1))
      r_annulus_holder_figure.extend(leg_hole_figure(c['middle_angle_1']+math.pi/2, -1))
    elif(ai_leg_type == 'rear'):
      r_annulus_holder_figure.extend(leg_hole_figure(c['middle_angle_1']+math.pi, 1))
    return(r_annulus_holder_figure)

    # top_lid_figure
  def f_top_lid_figure(ai_axle_B_type, ai_leg_type):
    """ generate the top_lid_figure
    """
    top_lid_outline = []
    if(ai_leg_type == 'side'):
      top_lid_outline.append((holder_cut_first_point[0], holder_cut_first_point[1], c['lid_smoothing_router_bit_radius']))
      top_lid_outline.extend(leg_outline(c['middle_angle_1']-math.pi/2, 1))
      top_lid_outline.append((holder_cut_side_outlines[0][-1][0], holder_cut_side_outlines[0][-1][1], c['lid_smoothing_router_bit_radius']))
    else:
      top_lid_outline.extend(holder_cut_side_outlines[0])
    if(ai_axle_B_type != 'none'):
      top_lid_outline.extend(axle_B_outline)
    else:
      top_lid_outline.extend(face_top_lid_outlines[0])
    if(ai_leg_type == 'side'):
      top_lid_outline.append((holder_cut_side_outlines[1][0][0], holder_cut_side_outlines[1][0][1], c['lid_smoothing_router_bit_radius']))
      top_lid_outline.extend(leg_outline(c['middle_angle_1']+math.pi/2, -1))
      top_lid_outline.append((holder_cut_side_outlines[1][-1][0], holder_cut_side_outlines[1][-1][1], c['lid_smoothing_router_bit_radius']))
    else:
      top_lid_outline.extend(holder_cut_side_outlines[1])
    if(ai_leg_type == 'rear'):
      top_lid_outline.extend(leg_outline(c['middle_angle_1']+math.pi, 1))
    else:
      top_lid_outline.extend(face_top_lid_outlines[1])
    top_lid_outline.append((holder_cut_first_point[0], holder_cut_first_point[1], 0))
    r_top_lid_figure = []
    r_top_lid_figure.append(top_lid_outline)
    if(c['axle_hole_radius']>radian_epsilon):
      r_top_lid_figure.append((c['g1_ix'], c['g1_iy'], c['axle_hole_radius']))
    r_top_lid_figure.extend(side_hole_figures[0])
    if(ai_axle_B_type != 'none'):
      r_top_lid_figure.extend(axle_B_hole_figure)
    r_top_lid_figure.extend(side_hole_figures[1])
    if(ai_leg_type == 'side'):
      r_top_lid_figure.extend(leg_hole_figure(c['middle_angle_1']-math.pi/2, 1))
      r_top_lid_figure.extend(leg_hole_figure(c['middle_angle_1']+math.pi/2, -1))
    elif(ai_leg_type == 'rear'):
      r_top_lid_figure.extend(leg_hole_figure(c['middle_angle_1']+math.pi, 1))
    return(r_top_lid_figure)

  ## figure generation
  annulus_holder_figure = f_annulus_holder_figure(c['output_axle_B_place'], c['leg_type'], c['input_axle_B_enable'])
  top_lid_figure = f_top_lid_figure(c['output_axle_B_place'], c['leg_type'])
  annulus_holder_simple_figure = f_annulus_holder_figure('none', 'none', c['input_axle_B_enable'])
  top_lid_simple_figure = f_top_lid_figure('none', 'none')
  annulus_holder_with_axle_B_figure = f_annulus_holder_figure(c['output_axle_B_place'], 'none', c['input_axle_B_enable'])
  top_lid_with_axle_B_figure = f_top_lid_figure(c['output_axle_B_place'], 'none')
  annulus_holder_with_leg_figure = f_annulus_holder_figure('none', c['leg_type'], c['input_axle_B_enable'])
  top_lid_with_leg_figure = f_top_lid_figure('none', c['leg_type'])
  # selection
  main_annulus_holder_figure = annulus_holder_figure[:]
  main_top_lid_figure = top_lid_figure[:]
  annulus_holder_with_axle_B_overlay_figure = f_annulus_holder_figure(c['output_axle_B_place'], 'none', c['input_axle_B_enable'])

  ### design output
  part_figure_list = []
  #part_figure_list.append(annulus_holder_figure)
  part_figure_list.append(main_annulus_holder_figure)
  part_figure_list.append(middle_lid_figures[0])
  part_figure_list.append(middle_lid_figures[1])
  #part_figure_list.append(top_lid_figure)
  part_figure_list.append(main_top_lid_figure)
  # al_assembly_figure: assembly flatted in one figure
  al_assembly_figure = []
  for i in range(len(part_figure_list)):
    al_assembly_figure.extend(part_figure_list[i])
  # al_list_of_parts: all parts aligned flatted in one figure
  x_space = 3.1*c['holder_radius']
  al_list_of_parts = []
  for i in range(len(part_figure_list)):
    for j in range(len(part_figure_list[i])):
      al_list_of_parts.append(cnc25d_api.outline_shift_x(part_figure_list[i][j], i*x_space, 1))
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['main_annulus_holder_fig'] = main_annulus_holder_figure
  r_height['main_annulus_holder_fig'] = c['extrusion_height']
  #
  r_figures['middle_lid_0_fig'] = middle_lid_figures[0]
  r_height['middle_lid_0_fig'] = c['extrusion_height']
  #
  r_figures['middle_lid_1_fig'] = middle_lid_figures[1]
  r_height['middle_lid_1_fig'] = c['extrusion_height']
  #
  r_figures['main_top_lid_fig'] = main_top_lid_figure
  r_height['main_top_lid_fig'] = c['extrusion_height']
  #
  r_figures['al_assembly_fig'] = al_assembly_figure
  r_height['al_assembly_fig'] = 1.0
  #
  r_figures['part_list_fig'] = al_list_of_parts
  r_height['part_list_fig'] = 1.0
  #
  r_figures['annulus_holder_figure'] = annulus_holder_figure
  r_height['annulus_holder_figure'] = c['extrusion_height']
  #
  r_figures['top_lid_figure'] = top_lid_figure
  r_height['top_lid_figure'] = c['extrusion_height']
  #
  r_figures['annulus_holder_simple_figure'] = annulus_holder_simple_figure
  r_height['annulus_holder_simple_figure'] = c['extrusion_height']
  #
  r_figures['top_lid_simple_figure'] = top_lid_simple_figure
  r_height['top_lid_simple_figure'] = c['extrusion_height']
  #
  r_figures['annulus_holder_with_axle_B_figure'] = annulus_holder_with_axle_B_figure
  r_height['annulus_holder_with_axle_B_figure'] = c['extrusion_height']
  #
  r_figures['top_lid_with_axle_B_figure'] = top_lid_with_axle_B_figure
  r_height['top_lid_with_axle_B_figure'] = c['extrusion_height']
  #
  r_figures['annulus_holder_with_leg_figure'] = annulus_holder_with_leg_figure
  r_height['annulus_holder_with_leg_figure'] = c['extrusion_height']
  #
  r_figures['top_lid_with_leg_figure'] = top_lid_with_leg_figure
  r_height['top_lid_with_leg_figure'] = c['extrusion_height']
  ###
  return((r_figures, r_height))

################################################################
# axle_lid 3D assembly-configuration construction
################################################################

def axle_lid_3d_construction(c):
  """ construct the 3D-assembly-configurations of the axle_lid
  """
  #
  hr = c['holder_radius']
  eh = c['extrusion_height']/2.0 # half-height
  # conf1
  axle_lid_3dconf1 = []
  axle_lid_3dconf1.append(('main_annulus_holder_fig',  0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  axle_lid_3dconf1.append(('middle_lid_0_fig',  0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0, 4*eh))
  axle_lid_3dconf1.append(('middle_lid_1_fig',  0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0, 4*eh))
  axle_lid_3dconf1.append(('main_top_lid_fig',  0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0, 8*eh))
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['axle_lid_3dconf1'] = axle_lid_3dconf1
  r_slice['axle_lid_3dconf1'] = (2*hr,2*hr,6*eh, -hr,-hr,0.0, [1*eh, 5*eh, 9*eh], [0.5*hr, 1*hr, 1.5*hr], [0.5*hr, 1*hr, 1.5*hr])
  #
  return((r_assembly, r_slice))


################################################################
# axle_lid_info
################################################################

def axle_lid_info(c):
  """ create the text info related to the axle_lid
  """
  r_info = ""
  r_info += c['holder_parameter_info']
  r_info += """
output_axle_B_place:  \t{:s}
output_axle_distance: \t{:0.3f}
output_axle_angle: \t{:0.3f} (radian) \t{:0.3f} (degree)
output_axle_B_internal_radius: \t{:0.3f}  diameter: \t{:0.3f}
output_axle_B_external_radius: \t{:0.3f}  diameter: \t{:0.3f}
output_axle_B_crenel_number: \t{:d}
output_axle_B_crenel_radius: \t{:0.3f}  diameter: \t{:0.3f}
output_axle_B_crenel_position_radius: \t{:0.3f}  diameter: \t{:0.3f}
output_axle_B_crenel_angle: \t{:0.3f}
""".format(c['output_axle_B_place'], c['output_axle_distance'], c['output_axle_angle'], c['output_axle_angle']*180/math.pi,  c['output_axle_B_internal_radius'], 2*c['output_axle_B_internal_radius'], c['output_axle_B_external_radius'], 2*c['output_axle_B_external_radius'], c['output_axle_B_crenel_number'], c['output_axle_B_crenel_radius'], 2*c['output_axle_B_crenel_radius'], c['output_axle_B_crenel_position_radius'], 2*c['output_axle_B_crenel_position_radius'], c['output_axle_B_crenel_angle'])
  r_info += c['leg_parameter_info']
  #print(r_info)
  return(r_info)

#    r_al = (annulus_holder_figure, annulus_holder_simple_figure, annulus_holder_with_axle_B_figure, annulus_holder_with_leg_figure, annulus_holder_with_axle_B_overlay_figure)
#    r_al = (top_lid_figure, top_lid_simple_figure, top_lid_with_axle_B_figure, top_lid_with_leg_figure)

################################################################
# self test
################################################################

def axle_lid_self_test():
  """
  This is the non-regression test of axle_lid.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 79.0 --axle_hole_diameter 22.0 --holder_crenel_number 6"],
    ["odd number of crenel" , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 5"],
    ["four crenels"         , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 4"],
    ["double-holes only"  , "--holder_diameter 220.0 --clearance_diameter 200.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 8 --holder_double_hole_length 4.0 --holder_double_hole_diameter 3.0 --holder_hole_diameter 0.0"],
    ["single and double holes"  , "--holder_diameter 220.0 --clearance_diameter 200.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 8 --holder_double_hole_length 16.0 --holder_double_hole_diameter 3.0 --holder_hole_diameter 5.0"],
    ["with initial angle"   , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 35.0 --axle_hole_diameter 22.0 --holder_position_angle 0.25"],
    ["with annulus-holder-axle-hole-diameter"   , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 35.0 --axle_hole_diameter 22.0 --annulus_holder_axle_hole_diameter 80.0"],
    ["axle_B with even crenel", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --output_axle_B_place small --output_axle_distance 130.0 --output_axle_B_internal_diameter 20.0 --output_axle_B_external_diameter 40.0"],
    ["axle_B small side", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place small --output_axle_distance 100.0 --output_axle_B_internal_diameter 30.0 --output_axle_B_external_diameter 65.0"],
    ["axle_B large side with crenels", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 170.0 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0 --output_axle_B_crenel_number 7 --output_axle_B_crenel_diameter 1.0"],
    ["axle_B large side angle", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 90.0  --output_axle_angle 0.3 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0"],
    ["axle_B large side angle and no axle_B_hole", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 70.0  --output_axle_angle -0.4 --output_axle_B_internal_diameter 0.0 --output_axle_B_external_diameter 50.0"],
    ["no axle hole", "--holder_diameter 150.0 --clearance_diameter 120.0 --central_diameter 30.0 --axle_hole_diameter 0.0 --holder_crenel_number 7"],
    ["with side leg", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --leg_type side --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0"],
    ["with rear leg", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --leg_type rear --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length -20.0"],
    ["complete with rear leg", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --leg_type rear --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0 --output_axle_B_place large --output_axle_distance 170.0 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0 --output_axle_B_crenel_number 7 --output_axle_B_crenel_diameter 1.0"],
    ["complete with side leg", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --leg_type side --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0 --output_axle_B_place large --output_axle_distance 170.0 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0 --output_axle_B_crenel_number 7 --output_axle_B_crenel_diameter 1.0"],
    ["complete with side leg into file", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --leg_type side --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0 --output_axle_B_place large --output_axle_distance 170.0 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0 --output_axle_B_crenel_number 7 --output_axle_B_crenel_diameter 1.0 --output_file_basename test_output/axle_lid_self_test2.dxf"],
    ["input_axle_B_enable small", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 46.0 --output_axle_B_internal_diameter 3.0 --output_axle_B_external_diameter 8.0 --input_axle_B_enable"],
    ["input_axle_B_enable medium", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 52.0 --output_axle_B_internal_diameter 3.0 --output_axle_B_external_diameter 20.0 --input_axle_B_enable --output_axle_angle 0.1"],
    ["input_axle_B_enable large", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 62.0 --output_axle_B_internal_diameter 3.0 --output_axle_B_external_diameter 10.0 --input_axle_B_enable --output_axle_angle -0.2"],
    ["output file"          , "--holder_diameter 130.0 --clearance_diameter 115.0 --central_diameter 100.0 --axle_hole_diameter 22.0 --output_file_basename test_output/axle_lid_self_test.dxf"],
    ["last test"            , "--holder_diameter 160.0 --clearance_diameter 140.0 --central_diameter 80.0 --axle_hole_diameter 22.0"]]
  return(r_tests)

################################################################
# axle_lid design declaration
################################################################

class axle_lid(cnc25d_api.bare_design):
  """ axle_lid design
  """
  def __init__(self, constraint={}):
    """ configure the axle_lid design
    """
    self.set_design_name("axle_lid")
    self.set_constraint_constructor(axle_lid_constraint_constructor)
    self.set_constraint_check(axle_lid_constraint_check)
    self.set_2d_constructor(axle_lid_2d_construction)
    self.set_2d_simulation()
    self.set_3d_constructor(axle_lid_3d_construction)
    self.set_info(axle_lid_info)
    self.set_display_figure_list(['al_assembly_fig'])
    self.set_default_simulation()
    self.set_2d_figure_file_list([]) # all figures
    self.set_3d_figure_file_list(['main_annulus_holder_fig', 'main_top_lid_fig'])
    self.set_3d_conf_file_list(['axle_lid_3dconf1'])
    self.set_allinone_return_type()
    self.set_self_test(axle_lid_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("axle_lid.py says hello!\n")
  my_al = axle_lid()
  #my_al.allinone()
  #my_al.allinone("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --return_type freecad_object")
  my_al.allinone("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_al.get_fc_obj('axle_lid_3dconf1'))
  


