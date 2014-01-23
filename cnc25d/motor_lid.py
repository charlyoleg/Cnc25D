# motor_lid.py
# generates a motor_lid assembly that can complete a epicyclic-gearing.
# created by charlyoleg on 2013/11/13
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
motor_lid.py is a parametric generator of an assembly that completes the epicyclic-gearing system to mount an electric motor.
The main function displays in a Tk-interface the motor-lid assembly, or generates the design as files or returns the design as FreeCAD Part object.
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
import axle_lid


################################################################
# motor_lid constraint_constructor
################################################################

def motor_lid_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the motor_lid design
  """
  r_parser = ai_parser
  ### holder-A and holder-B : inherit dictionary entries from axle_lid
  i_axle_lid = axle_lid.axle_lid()
  r_parser = i_axle_lid.get_constraint_constructor()(r_parser, 1)
  ### input axle-B
  r_parser.add_argument('--axle_B_place','--abp', action='store', default='small',
    help="Set the side to generate the input axle_B. Possible values: 'small' or 'large'. Default: 'small'")
  r_parser.add_argument('--axle_B_distance','--abdis', action='store', type=float, default=0.0,
    help="Set the distance between the input axle-A and input axle-B. Default: 0.0")
  r_parser.add_argument('--axle_B_angle','--aba', action='store', type=float, default=0.0,
    help="Set the angle between the symmetric axis and the intput_axle_B. Default: 0.0")
  r_parser.add_argument('--axle_B_diameter','--abd', action='store', type=float, default=0.0,
    help="Set the diameter of the input_axle_B. If equal to 0.0, no hole for the axle_B is generated. Default: 0.0")
  r_parser.add_argument('--axle_B_external_diameter','--abed', action='store', type=float, default=0.0,
    help="Set the external diameter of the input_axle_B. If equal to 0.0, it is set to 2*axle_B_diameter. Default: 0.0")
  r_parser.add_argument('--axle_B_hole_diameter','--abhd', action='store', type=float, default=0.0,
    help="Set the diameter of the hole in the holder-B for the axle_B. If equal to 0.0, no hole in the holder-B for the axle_B is generated. Default: 0.0")
  r_parser.add_argument('--axle_B_central_diameter','--abcd', action='store', type=float, default=0.0,
    help="Set the central diameter of the axle_B for the holder-C. If equal to 0.0, it is set to 2*axle_B_diameter. Default: 0.0")
  ### input axle-C
  r_parser.add_argument('--axle_C_distance','--acdis', action='store', type=float, default=0.0,
    help="Set the distance between the input axle-B and input axle-C. Default: 0.0")
  r_parser.add_argument('--axle_C_angle','--aca', action='store', type=float, default=0.0,
    help="Set the angle between the AB-axis and the BC-axis. Default: 0.0")
  r_parser.add_argument('--axle_C_hole_diameter','--achd', action='store', type=float, default=0.0,
    help="Set the diameter of the hole of the axle_C. If equal to 0.0, no hole for the axle_C is generated. Default: 0.0")
  r_parser.add_argument('--axle_C_external_diameter','--aced', action='store', type=float, default=0.0,
    help="Set the external diameter of the input_axle_C. If equal to 0.0, it is set to 2*axle_C_hole_diameter. Default: 0.0")
  ### motor screws
  # screw 1
  r_parser.add_argument('--motor_screw1_diameter','--ms1d', action='store', type=float, default=0.0,
    help="Set the diameter of the screw1 holes for an electric motor. If equal to 0.0, no screw1 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw1_angle','--ms1a', action='store', type=float, default=0.0,
    help="Set the angle between the BC-axis and the screw1-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw1_x_length','--ms1xl', action='store', type=float, default=0.0,
    help="Set the length between the screw1-y-axis and the screw1-hole (ie: half of the length between the two screw1-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw1_y_length','--ms1yl', action='store', type=float, default=0.0,
    help="Set the length between the axle_C and the screw-x-axis. Default: 0.0")
  # screw 2
  r_parser.add_argument('--motor_screw2_diameter','--ms2d', action='store', type=float, default=0.0,
    help="Set the diameter of the screw2 holes for an electric motor. If equal to 0.0, no screw1 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw2_angle','--ms2a', action='store', type=float, default=0.0,
    help="Set the angle between the BC-axis and the screw2-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw2_x_length','--ms2xl', action='store', type=float, default=0.0,
    help="Set the length between the screw2-y-axis and the screw2-hole (ie: half of the length between the two screw1-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw2_y_length','--ms2yl', action='store', type=float, default=0.0,
    help="Set the length between the axle_C and the screw2-x-axis. Default: 0.0")
  # screw 3
  r_parser.add_argument('--motor_screw3_diameter','--ms3d', action='store', type=float, default=0.0,
    help="Set the diameter of the screw3 holes for an electric motor. If equal to 0.0, no screw3 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw3_angle','--ms3a', action='store', type=float, default=0.0,
    help="Set the angle between the BC-axis and the screw3-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw3_x_length','--ms3xl', action='store', type=float, default=0.0,
    help="Set the length between the screw3-y-axis and the screw3-hole (ie: half of the length between the two screw3-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw3_y_length','--ms3yl', action='store', type=float, default=0.0,
    help="Set the length between the axle_C and the screw3-x-axis. Default: 0.0")
  ### holder-C
  r_parser.add_argument('--fastening_BC_hole_diameter','--fbchd', action='store', type=float, default=0.0,
    help="Set the diameter of the holder B and C fastening holes. If equal to 0.0, no fastening holes are generated. Default: 0.0")
  r_parser.add_argument('--fastening_BC_external_diameter','--fbced', action='store', type=float, default=0.0,
    help="Set the external diameter of the holder B and C fastening extremities. If equal to 0.0, it is set to 2*fastening_BC_hole_diameter. Default: 0.0")
  r_parser.add_argument('--fastening_BC_bottom_position_diameter','--fbcbpd', action='store', type=float, default=0.0,
    help="Set the diameter of the position circle for the bottom fastening holes. Default: 0.0")
  r_parser.add_argument('--fastening_BC_bottom_angle','--fbcba', action='store', type=float, default=0.0,
    help="Set the angle between the AB-axis and the bottom fastening hole. Default: 0.0")
  r_parser.add_argument('--fastening_BC_top_position_diameter','--fbctpd', action='store', type=float, default=0.0,
    help="Set the diameter of the position circle for the top fastening holes. Default: 0.0")
  r_parser.add_argument('--fastening_BC_top_angle','--fbcta', action='store', type=float, default=0.0,
    help="Set the angle between the AB-axis and the top fastening hole. Default: 0.0")
  ### general
  r_parser.add_argument('--smoothing_radius','--sr', action='store', type=float, default=0.0,
    help="Set the smoothing radius for the motor-lid. If equal to 0.0, it is set to cnc_router_bit_radius. Default: 0.0")
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1,
    help="Set the minimum router_bit radius of the motor-lid. Default: 0.1")
  r_parser.add_argument('--extrusion_height','--eh', action='store', type=float, default=10.0,
    help="Set the height of the linear extrusion of each part of the motor_lid assembly. Default: 10.0")
  ### output
  # return
  return(r_parser)

################################################################
# constraint converstion
################################################################

def holder_A_al2ml(c):
  """ set the axle_lid constraint to generate holder_A
  """
  al_c = c.copy()
  al_c['output_axle_B_place'] = c['holder_A_axle_B_place']
  al_c['output_axle_distance'] = c['axle_B_distance']
  al_c['output_axle_angle'] = c['axle_B_angle']
  al_c['output_axle_B_external_diameter'] = 2*c['axle_B_external_radius']
  al_c['output_axle_B_internal_diameter'] = 2*c['axle_B_radius']
  al_c['input_axle_B_enable'] = True
  al_c['smoothing_radius'] = c['smoothing_radius']
  al_c['cnc_router_bit_radius'] = c['cnc_router_bit_radius']
  al_c['extrusion_height'] = c['extrusion_height']
  return(al_c)
    
def holder_B_al2ml(c):
  """ set the axle_lid constraint to generate holder_A
  """
  al_c = c.copy()
  al_c['output_axle_B_place'] = c['holder_B_axle_B_place']
  al_c['output_axle_distance'] = c['AC_length']
  al_c['output_axle_angle'] = c['AC_angle']
  al_c['output_axle_B_external_diameter'] = 2*c['axle_C_external_radius']
  al_c['output_axle_B_internal_diameter'] = 2*c['axle_C_hole_radius']
  al_c['input_axle_B_enable'] = False
  al_c['smoothing_radius'] = c['smoothing_radius']
  al_c['cnc_router_bit_radius'] = c['cnc_router_bit_radius']
  al_c['extrusion_height'] = c['extrusion_height']
  return(al_c)
    
################################################################
# motor_lid constraint_check
################################################################

def motor_lid_constraint_check(c):
  """ check the motor_lid constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ## router_bit
  if(c['smoothing_radius']==0):
    c['smoothing_radius'] = c['cnc_router_bit_radius']
  if(c['smoothing_radius']<c['cnc_router_bit_radius']):
    print("ERR232: Error, smoothing_radius {:0.3f} is smaller than cnc_router_bit_radius {:0.3f}".format(c['smoothing_radius'], c['cnc_router_bit_radius']))
    sys.exit(2)
  ## holder-axis
  if((c['axle_B_place']!='small')and(c['axle_B_place']!='large')):
    print("ERR236: Error, axle_B_place {:s} accept only 'small' or 'large'".format(c['axle_B_place']))
    sys.exit(2)
  c['holder_crenel_number'] = c['holder_crenel_number']
  middle_crenel_1 = 0
  middle_crenel_2 = int(c['holder_crenel_number']/2)
  if(c['axle_B_place'] == 'large'):
    middle_crenel_2 = int((c['holder_crenel_number']+1)/2)
  #middle_crenel_index = [middle_crenel_1, middle_crenel_2]
  crenel_portion_angle = 2*math.pi/c['holder_crenel_number']
  c['holder_axis_angle'] = c['holder_position_angle'] + (middle_crenel_1 + 1 + middle_crenel_2)*crenel_portion_angle/2.0
  # axle_C
  c['holder_radius'] = c['holder_diameter']/2.0
  l_AC = 0.0
  a_AC = 0.0
  #if(c['axle_C_distance']<radian_epsilon):
  #  print("ERR237: Error, axle_C_distance {:0.3f} is too small".format(c['axle_C_distance']))
  #  sys.exit(2)
  if(c['axle_C_distance']>radian_epsilon):
    a_abc = math.pi-abs(c['axle_C_angle']) # angle (ABC)
    l_AC = math.sqrt( c['axle_B_distance']**2 + c['axle_C_distance']**2 - 2 *  c['axle_B_distance'] * c['axle_C_distance'] * math.cos(a_abc)) # length (AC): law of cosines
    sin_a = math.sin(a_abc) * c['axle_C_distance'] / l_AC # angle (CAB): law of sines
    a_cab = math.asin(sin_a)
    a_AC = c['axle_B_angle'] + math.copysign(a_cab, c['axle_C_angle']) # angle (holder-axis, AC)
    if(l_AC<c['holder_radius']):
      print("ERR245: l_AC {:0.3} is smaller than the holder_radius {:0.3f}".format(l_AC, c['holder_radius']))
      sys.exit(2)
  ### holder_A
  c['holder_A_axle_B_place'] = c['axle_B_place']
  if(c['axle_B_distance']<radian_epsilon):
    c['holder_A_axle_B_place'] = 'none'
  c['axle_B_radius'] = c['axle_B_diameter']/2.0
  c['axle_B_external_radius'] = c['axle_B_external_diameter']/2.0
  if(c['axle_B_external_radius']==0):
    c['axle_B_external_radius'] = 2*c['axle_B_radius']
  if(c['holder_A_axle_B_place'] != 'none'):
    if(c['axle_B_external_radius']<c['axle_B_radius']+radian_epsilon):
      print("ERR262: Error, axle_B_external_radius {:0.3f} is smaller than axle_B_radius {:0.3f}".format(c['axle_B_external_radius'], c['axle_B_radius']))
      sys.exit(2)
  i_axle_lid = axle_lid.axle_lid()
  i_axle_lid.apply_external_constraint(holder_A_al2ml(c))
  holder_parameters = i_axle_lid.get_constraint()
  c['holder_radius'] = holder_parameters['holder_radius']
  ### holder_B
  c['holder_B_axle_B_place'] = c['axle_B_place']
  if(l_AC<radian_epsilon):
    c['holder_B_axle_B_place'] = 'none'
  c['axle_C_hole_radius'] = c['axle_C_hole_diameter']/2.0
  c['axle_C_external_radius'] = c['axle_C_external_diameter']/2.0
  if(c['axle_C_external_radius']==0):
    c['axle_C_external_radius'] = 2*c['axle_C_hole_radius']
  if(c['holder_B_axle_B_place'] != 'none'):
    if(c['axle_C_external_radius']<c['axle_C_hole_radius']+radian_epsilon):
      print("ERR280: Error, axle_C_external_radius {:0.3f} is too small compare to axle_C_hole_radius {:0.3f}".format(c['axle_C_external_radius'], c['axle_C_hole_radius']))
      sys.exit(2)
  c['AC_length'] = l_AC
  c['AC_angle'] = a_AC
  ###
  c['axle_B_hole_radius'] = c['axle_B_hole_diameter']/2.0
  c['fastening_BC_hole_radius'] = c['fastening_BC_hole_diameter']/2.0
  c['fastening_BC_bottom_position_radius'] = c['fastening_BC_bottom_position_diameter']/2.0
  c['fastening_BC_top_position_radius'] = c['fastening_BC_top_position_diameter']/2.0
  c['motor_screw_diameter'] = [c['motor_screw1_diameter'], c['motor_screw2_diameter'], c['motor_screw3_diameter']]
  c['motor_screw_angle'] = [c['motor_screw1_angle'], c['motor_screw2_angle'], c['motor_screw3_angle']]
  c['motor_screw_x_length'] = [c['motor_screw1_x_length'], c['motor_screw2_x_length'], c['motor_screw3_x_length']]
  c['motor_screw_y_length'] = [c['motor_screw1_y_length'], c['motor_screw2_y_length'], c['motor_screw3_y_length']]
  c['axle_B_central_radius'] = c['axle_B_central_diameter']/2.0
  if(c['axle_B_central_radius']==0):
    c['axle_B_central_radius'] = 2*c['axle_B_radius']
  c['fastening_BC_external_radius'] = c['fastening_BC_external_diameter']/2.0
  if(c['fastening_BC_external_radius']==0):
    c['fastening_BC_external_radius'] = 2*c['fastening_BC_hole_radius']
  if(c['fastening_BC_external_radius']>0):
    if(c['fastening_BC_external_radius']<c['fastening_BC_hole_radius']+radian_epsilon):
      print("ERR367: Error, fastening_BC_external_radius {:0.3f} is too small compare to fastening_BC_hole_radius {:0.3f}".format(c['fastening_BC_external_radius'], c['fastening_BC_hole_radius']))
      sys.exit(2)
    if(c['axle_B_central_radius']<c['axle_B_radius']+radian_epsilon):
      print("ERR355: Error, axle_B_central_radius {:0.3f} is too small compare to axle_B_radius {:0.3f}".format(c['axle_B_central_radius'], c['axle_B_radius']))
      sys.exit(2)
    if(c['fastening_BC_hole_radius']<radian_epsilon):
      print("ERR324: Error, fastening_BC_hole_radius {:0.3f} is too small".format(c['fastening_BC_hole_radius']))
      sys.exit(2)
    if((c['fastening_BC_external_radius']+c['fastening_BC_hole_radius'])>c['fastening_BC_bottom_position_radius']):
      print("ERR327: Error, fastening_BC_bottom_position_radius {:0.3f} is too small compare to fastening_BC_external_radius {:0.3f} and fastening_BC_hole_radius {:0.3f}".format(c['fastening_BC_bottom_position_radius'], c['fastening_BC_external_radius'], c['fastening_BC_hole_radius']))
      sys.exit(2)
    if((c['fastening_BC_external_radius']+c['fastening_BC_hole_radius'])>c['fastening_BC_top_position_radius']):
      print("ERR330: Error, fastening_BC_top_position_radius {:0.3f} is too small compare to fastening_BC_external_radius {:0.3f} and fastening_BC_hole_radius {:0.3f}".format(c['fastening_BC_top_position_radius'], c['fastening_BC_external_radius'], c['fastening_BC_hole_radius']))
      sys.exit(2)
  ###
  return(c)

################################################################
# motor_lid 2D-figures construction
################################################################

def motor_lid_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the motor_lid design
  """
  # holder_A from axle_lid
  i1_axle_lid = axle_lid.axle_lid()
  i1_axle_lid.apply_external_constraint(holder_A_al2ml(c))
  holder_A_figure = i1_axle_lid.get_A_figure('annulus_holder_fig')
  holder_A_simple_figure = i1_axle_lid.get_A_figure('annulus_holder_simple_fig')
  holder_A_with_motor_lid_figure = i1_axle_lid.get_A_figure('annulus_holder_with_axle_B_fig')
  holder_A_with_leg_figure = i1_axle_lid.get_A_figure('annulus_holder_with_leg_fig')
  # holder_B from axle_lid
  i2_axle_lid = axle_lid.axle_lid()
  i2_axle_lid.apply_external_constraint(holder_B_al2ml(c))
  holder_B_figure = i2_axle_lid.get_A_figure('top_lid_fig')
  holder_B_simple_figure = i2_axle_lid.get_A_figure('top_lid_simple_fig')
  holder_B_with_motor_lid_figure = i2_axle_lid.get_A_figure('top_lid_with_axle_B_fig')
  holder_B_with_leg_figure = i2_axle_lid.get_A_figure('top_lid_with_leg_fig')
  middle_lid_0_figure = i2_axle_lid.get_A_figure('middle_lid_0_fig')
  middle_lid_1_figure = i2_axle_lid.get_A_figure('middle_lid_1_fig')
  ## holder_B_hole_figure
  g1_ix = 0.0
  g1_iy = 0.0
  holder_B_hole_figure = []
  # axle_B_hole_diameter
  a_AB = c['holder_axis_angle'] + c['axle_B_angle']
  a_BC = a_AB + c['axle_C_angle']
  bx = g1_ix+c['axle_B_distance']*math.cos(a_AB)
  by = g1_iy+c['axle_B_distance']*math.sin(a_AB)
  if(c['axle_B_hole_radius']>0):
    holder_B_hole_figure.append((bx, by, c['axle_B_hole_radius']))
  # fastening_BC_hole_figure
  fastening_BC_hole_figure = []
  if(c['fastening_BC_hole_radius']>0):
    for s in [-1, 1]:
      a_bottom = a_AB + math.pi + s * c['fastening_BC_bottom_angle']
      fastening_BC_hole_figure.append((bx+c['fastening_BC_bottom_position_radius']*math.cos(a_bottom), by+c['fastening_BC_bottom_position_radius']*math.sin(a_bottom), c['fastening_BC_hole_radius']))
      a_top = a_BC + s * c['fastening_BC_top_angle']
      fastening_BC_hole_figure.append((bx+c['fastening_BC_top_position_radius']*math.cos(a_top), by+c['fastening_BC_top_position_radius']*math.sin(a_top), c['fastening_BC_hole_radius']))
  holder_B_hole_figure.extend(fastening_BC_hole_figure)
  # motor_screw
  cx = bx + c['axle_C_distance']*math.cos(a_BC)
  cy = by + c['axle_C_distance']*math.sin(a_BC)
  for i in range(len(c['motor_screw_diameter'])):
    if(c['motor_screw_diameter'][i]>0):
      for s in [-1, 1]:
        a_h = a_BC + c['motor_screw_angle'][i]
        hx = cx + c['motor_screw_y_length'][i] * math.cos(a_h) + c['motor_screw_x_length'][i] * math.cos(a_h+s*math.pi/2)
        hy = cy + c['motor_screw_y_length'][i] * math.sin(a_h) + c['motor_screw_x_length'][i] * math.sin(a_h+s*math.pi/2)
        holder_B_hole_figure.append((hx, hy, c['motor_screw_diameter'][i]/2.0))
  # holder_B
  holder_B_figure.extend(holder_B_hole_figure)
  holder_B_with_motor_lid_figure.extend(holder_B_hole_figure)
  ### holder_C
  holder_C_figure = []
  if(c['fastening_BC_external_radius']>0):
    # holder_C_outline_A
    holder_C_outline_A = []
    hca = ((a_AB + math.pi - c['fastening_BC_bottom_angle'], c['fastening_BC_bottom_position_radius']),
           (a_AB + math.pi + c['fastening_BC_bottom_angle'], c['fastening_BC_bottom_position_radius']),
           (a_BC - c['fastening_BC_top_angle'], c['fastening_BC_top_position_radius']),
           (a_BC + c['fastening_BC_top_angle'], c['fastening_BC_top_position_radius']))
    for i in range(len(hca)):
      ea = hca[i][0]
      ma = hca[i-1][0] + (math.fmod(hca[i][0] - hca[i-1][0] + 4*math.pi, 2*math.pi) - 0*math.pi)/2.0 # we always want the angle positive because we always turn CCW
      dl = math.sqrt(hca[i][1]**2 + c['fastening_BC_external_radius']**2)
      da = math.atan(float(c['fastening_BC_external_radius'])/hca[i][1])
      sl = hca[i][1] + c['fastening_BC_external_radius']
      holder_C_outline_A.append((bx+c['axle_B_central_radius']*math.cos(ma), by+c['axle_B_central_radius']*math.sin(ma), c['smoothing_radius']))
      holder_C_outline_A.append((bx+dl*math.cos(ea-da), by+dl*math.sin(ea-da), 0))
      holder_C_outline_A.append((bx+sl*math.cos(ea), by+sl*math.sin(ea), bx+dl*math.cos(ea+da), by+dl*math.sin(ea+da), 0))
    holder_C_outline_A.append((holder_C_outline_A[0][0], holder_C_outline_A[0][1], 0))
    # holder_C_figure
    holder_C_figure.append(holder_C_outline_A)
    if(c['axle_B_radius']>0):
      holder_C_figure.append((bx, by, c['axle_B_radius']))
    holder_C_figure.extend(fastening_BC_hole_figure)

  ### design output
  # part_figure_list
  part_figure_list = []
  part_figure_list.append(holder_A_figure)
  part_figure_list.append(middle_lid_0_figure)
  part_figure_list.append(middle_lid_1_figure)
  part_figure_list.append(holder_B_figure)
  part_figure_list.append(holder_C_figure)
  part_figure_list.append(holder_A_with_motor_lid_figure)
  # assembly
  ml_assembly_figure = []
  for i in range(len(part_figure_list)):
    ml_assembly_figure.extend(part_figure_list[i])
  # ml_list_of_parts
  x_space = 3.1*c['holder_radius']
  ml_list_of_parts = []
  for i in range(len(part_figure_list)):
    for j in range(len(part_figure_list[i])):
      ml_list_of_parts.append(cnc25d_api.outline_shift_x(part_figure_list[i][j], i*x_space, 1))
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['holder_A_fig'] = holder_A_figure
  r_height['holder_A_fig'] = c['extrusion_height']
  #
  r_figures['middle_lid_0_fig'] = middle_lid_0_figure
  r_height['middle_lid_0_fig'] = c['extrusion_height']
  #
  r_figures['middle_lid_1_fig'] = middle_lid_1_figure
  r_height['middle_lid_1_fig'] = c['extrusion_height']
  #
  r_figures['holder_B_fig'] = holder_B_figure
  r_height['holder_B_fig'] = c['extrusion_height']
  #
  r_figures['holder_C_fig'] = holder_C_figure
  r_height['holder_C_fig'] = c['extrusion_height']
  #
  r_figures['holder_A_with_motor_lid_fig'] = holder_A_with_motor_lid_figure
  r_height['holder_A_with_motor_lid_fig'] = c['extrusion_height']
  #
  r_figures['ml_assembly_fig'] = ml_assembly_figure
  r_height['ml_assembly_fig'] = 1.0
  #
  r_figures['ml_part_list'] = ml_list_of_parts
  r_height['ml_part_list'] = 1.0
  #
  r_figures['holder_A_simple_fig'] = holder_A_simple_figure
  r_height['holder_A_simple_fig'] = c['extrusion_height']
  #
  r_figures['holder_B_simple_fig'] = holder_B_simple_figure
  r_height['holder_B_simple_fig'] = c['extrusion_height']
  #
  r_figures['holder_A_with_leg_fig'] = holder_A_with_leg_figure
  r_height['holder_A_with_leg_fig'] = c['extrusion_height']
  #
  r_figures['holder_B_with_leg_fig'] = holder_B_with_leg_figure
  r_height['holder_B_with_leg_fig'] = c['extrusion_height']
  ###
  return((r_figures, r_height))

################################################################
# motor_lid 3D assembly-configuration construction
################################################################

def motor_lid_3d_construction(c):
  """ construct the 3D-assembly-configurations of the motor_lid
  """
  hr = c['holder_radius']
  eh = c['extrusion_height']/2.0 # half-height
  #print("dbg435: hr:", hr, " eh:", eh)
  # conf1
  motor_lid_3dconf1 = []
  motor_lid_3dconf1.append(('holder_A_fig',                 0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0,  0*eh))
  motor_lid_3dconf1.append(('middle_lid_0_fig',             0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0,  5*eh))
  motor_lid_3dconf1.append(('middle_lid_1_fig',             0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0,  5*eh))
  motor_lid_3dconf1.append(('holder_B_fig',                 0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0, 10*eh))
  if(c['fastening_BC_external_radius']>0):
    motor_lid_3dconf1.append(('holder_C_fig',                 0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0, 15*eh))
  motor_lid_3dconf1.append(('holder_A_with_motor_lid_fig',  0.0, 0.0, 0.0, 0.0, c['extrusion_height'], 'i', 'xy', 0.0, 0.0,  0*eh))
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['motor_lid_3dconf1'] = motor_lid_3dconf1
  r_slice['motor_lid_3dconf1'] = (2*hr,2*hr,6*eh, -hr,-hr,0.0, [eh], [], [])
  #
  return((r_assembly, r_slice))

################################################################
# motor_lid_info
################################################################

def motor_lid_info(c):
  """ create the text info related to the motor_lid
  """
  r_info = ""
  # inheritance from axle_lid
  i_axle_lid = axle_lid.axle_lid()
  i_axle_lid.apply_external_constraint(c)
  r_info += i_axle_lid.get_info()
  r_info += """
axle_B_place:  \t{:s}
axle_B_distance: \t{:0.3f}
axle_B_angle: \t{:0.3f} (radian) \t{:0.3f} (degree)
axle_B_radius: \t{:0.3f}  diameter: \t{:0.3f}
axle_B_external_radius: \t{:0.3f}  diameter: \t{:0.3f}
axle_B_hole_radius: \t{:0.3f}  diameter: \t{:0.3f}
axle_B_central_radius: \t{:0.3f}  diameter: \t{:0.3f}
""".format(c['axle_B_place'], c['axle_B_distance'], c['axle_B_angle'], c['axle_B_angle']*180/math.pi, c['axle_B_radius'], 2*c['axle_B_radius'], c['axle_B_external_radius'], 2*c['axle_B_external_radius'], c['axle_B_hole_radius'], 2*c['axle_B_hole_radius'], c['axle_B_central_radius'], 2*c['axle_B_central_radius'])
  r_info += """
axle_C_distance:  \t{:0.3f}
axle_C_angle: \t{:0.3f} (radian) \t{:0.3f} (degree)
axle_C_hole_radius: \t{:0.3f}  diameter: \t{:0.3f}
axle_C_external_radius: \t{:0.3f}  diameter: \t{:0.3f}
""".format(c['axle_C_distance'], c['axle_C_angle'], c['axle_C_angle']*180/math.pi, c['axle_C_hole_radius'], 2*c['axle_C_hole_radius'], c['axle_C_external_radius'], 2*c['axle_C_external_radius'])
  for i in range(len(c['motor_screw_diameter'])):
    r_info += """
motor_screw{:d}_radius {:0.3f}  diameter {:0.3f}
motor_screw{:d}_angle {:0.3f} (radian) \t{:0.3f} (degree)
motor_screw{:d}_x_length {:0.3f}  2x_length {:0.3f}
motor_screw{:d}_y_length {:0.3f}  2y_length {:0.3f}
""".format(i, c['motor_screw_diameter'][i]/2.0, c['motor_screw_diameter'][i], i, c['motor_screw_angle'][i], c['motor_screw_angle'][i]*180/math.pi, i, c['motor_screw_x_length'][i], 2* c['motor_screw_x_length'][i], i, c['motor_screw_y_length'][i], 2* c['motor_screw_y_length'][i])
  r_info += """
fastening_BC_hole_radius {:0.3f}  diameter {:0.3f}
fastening_BC_external_radius {:0.3f}  diameter {:0.3f}
fastening_BC_bottom_position_radius {:0.3f}  diameter {:0.3f}
fastening_BC_bottom_angle {:0.3f} (radian) \t{:0.3f} (degree)
fastening_BC_top_position_radius {:0.3f}  diameter {:0.3f}
fastening_BC_top_angle {:0.3f} (radian) \t{:0.3f} (degree)
smoothing_radius {:0.3f}  diameter {:0.3f}
cnc_router_bit_radius {:0.3f}  diameter {:0.3f}
""".format(c['fastening_BC_hole_radius'], 2*c['fastening_BC_hole_radius'], c['fastening_BC_external_radius'], 2*c['fastening_BC_external_radius'], c['fastening_BC_bottom_position_radius'], 2*c['fastening_BC_bottom_position_radius'], c['fastening_BC_bottom_angle'], c['fastening_BC_bottom_angle']*180/math.pi, c['fastening_BC_top_position_radius'], 2*c['fastening_BC_top_position_radius'], c['fastening_BC_top_angle'], c['fastening_BC_top_angle']*180/math.pi, c['smoothing_radius'], 2*c['smoothing_radius'], c['cnc_router_bit_radius'], 2*c['cnc_router_bit_radius'])
  #print(r_info)
  return(r_info)

################################################################
# self test
################################################################

def motor_lid_self_test():
  """
  This is the non-regression test of motor_lid.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , "--holder_diameter 160.0 --clearance_diameter 140.0 --central_diameter 80.0 --axle_hole_diameter 22.0"],
    ["small side"            , "--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place small --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_external_diameter 15.0"],
    ["large side with side leg" , "--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place large --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_external_diameter 15.0 --leg_type side --leg_length 120.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0"],
    ["seven holder", "--holder_diameter 59.0 --holder_hole_position_radius 30.5 --holder_hole_diameter 4.1 --holder_double_hole_diameter 0.9 --holder_double_hole_length 8.0 --holder_double_hole_position -1.0 --holder_double_hole_mark_nb 1 --holder_crenel_position 3.5 --holder_crenel_height 0.5 --holder_crenel_width 6.0 --holder_crenel_skin_width 3.0 --holder_crenel_router_bit_radius 0.1 --holder_smoothing_radius 0.0 --clearance_diameter 53.0 --axle_hole_diameter 5.9 --central_diameter 30.0 --axle_B_distance 0.0 --axle_B_external_diameter 0.0 --axle_C_distance 53.0 --axle_C_external_diameter 38.0 --holder_crenel_number 7"],
    ["output files" , "--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place large --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_external_diameter 15.0 --leg_type side --leg_length 120.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0 --axle_B_hole_diameter 20.0 --output_file_basename test_output/motor_lid_self_test.dxf"],
    ["last test"            , "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0  --holder_crenel_number 6 --axle_B_distance 52.0 --axle_C_distance 40.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0"]]
  return(r_tests)

################################################################
# motor_lid design declaration
################################################################

class motor_lid(cnc25d_api.bare_design):
  """ motor_lid design
  """
  def __init__(self, constraint={}):
    """ configure the motor_lid design
    """
    self.design_setup(
      s_design_name             = "motor_lid",
      f_constraint_constructor  = motor_lid_constraint_constructor,
      f_constraint_check        = motor_lid_constraint_check,
      f_2d_constructor          = motor_lid_2d_construction,
      #d_2d_simulation           = {},
      f_3d_constructor          = motor_lid_3d_construction,
      f_info                    = motor_lid_info,
      l_display_figure_list     = ['ml_assembly_fig'],
      #s_default_simulation      = '',
      l_2d_figure_file_list     = [], # all figures
      l_3d_figure_file_list     = ['holder_A_fig', 'holder_B_fig'],
      l_3d_conf_file_list       = ['motor_lid_3dconf1'],
      f_cli_return_type         = None,
      l_self_test_list          = motor_lid_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("motor_lid.py says hello!\n")
  my_ml = motor_lid()
  #my_ml.cli()
  #my_ml.cli("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --return_type freecad_object")
  #my_ml.cli("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --axle_B_distance 52.0 --axle_C_distance 40.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0")
  my_ml.cli("--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place small --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_hole_diameter 20.0 --axle_B_external_diameter 15.0")
  #my_ml.cli("--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place small --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_hole_diameter 20.0 --axle_B_external_diameter 15.0 --return_type freecad_object")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_ml.get_fc_obj('motor_lid_3dconf1'))


