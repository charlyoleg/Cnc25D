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
# motor_lid dictionary-arguments default values
################################################################

def motor_lid_dictionary_init():
  """ create and initiate a motor_lid_dictionary with the default value
  """
  r_mld = {}
  ### holder-A and holder-B: inherit dictionary entries from axle_lid
  r_mld.update(axle_lid.axle_lid_dictionary_init(1))
  #### motor_lid dictionary entries
  ### input axle-B
  r_mld['axle_B_place']             = 'small' # 'small' or 'large' # useful when the gearring has an odd number of crenels
  r_mld['axle_B_distance']          = 0.0
  r_mld['axle_B_angle']             = 0.0
  r_mld['axle_B_diameter']          = 0.0
  r_mld['axle_B_external_diameter'] = 0.0
  r_mld['axle_B_hole_diameter']     = 0.0
  r_mld['axle_B_central_diameter']  = 0.0
  ### input axle-C
  r_mld['axle_C_distance']          = 0.0
  r_mld['axle_C_angle']             = 0.0
  r_mld['axle_C_hole_diameter']     = 0.0
  r_mld['axle_C_external_diameter'] = 0.0
  ### motor screws
  r_mld['motor_screw1_diameter']    = 0.0
  r_mld['motor_screw1_angle']       = 0.0
  r_mld['motor_screw1_x_length']    = 0.0
  r_mld['motor_screw1_y_length']    = 0.0
  r_mld['motor_screw2_diameter']    = 0.0
  r_mld['motor_screw2_angle']       = 0.0
  r_mld['motor_screw2_x_length']    = 0.0
  r_mld['motor_screw2_y_length']    = 0.0
  r_mld['motor_screw3_diameter']    = 0.0
  r_mld['motor_screw3_angle']       = 0.0
  r_mld['motor_screw3_x_length']    = 0.0
  r_mld['motor_screw3_y_length']    = 0.0
  ### holder-C
  r_mld['fastening_BC_hole_diameter']     = 0.0
  r_mld['fastening_BC_external_diameter'] = 0.0
  r_mld['fastening_BC_bottom_position_diameter']  = 0.0
  r_mld['fastening_BC_bottom_angle']              = 0.0
  r_mld['fastening_BC_top_position_diameter']     = 0.0
  r_mld['fastening_BC_top_angle']                 = 0.0
  ### general
  r_mld['smoothing_radius']       = 0.0
  r_mld['cnc_router_bit_radius']  = 0.1
  r_mld['extrusion_height']       = 10.0
  ### output
  r_mld['tkinter_view']           = False
  r_mld['output_file_basename']   = ''
  ### optional
  r_mld['args_in_txt'] = ""
  r_mld['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_mld)

################################################################
# motor_lid argparse
################################################################

def motor_lid_add_argument(ai_parser):
  """
  Add arguments relative to the motor-lid in addition to the argument of axle_lid(variant=1)
  This function intends to be used by the motor_lid_cli and motor_lid_self_test
  """
  r_parser = ai_parser
  ### holder-A and holder-B : inherit dictionary entries from axle_lid
  r_parser = axle_lid.axle_lid_add_argument(r_parser, 1)
  ### input axle-B
  r_parser.add_argument('--axle_B_place','--abp', action='store', default='small', dest='sw_axle_B_place',
    help="Set the side to generate the input axle_B. Possible values: 'small' or 'large'. Default: 'small'")
  r_parser.add_argument('--axle_B_distance','--abdis', action='store', type=float, default=0.0, dest='sw_axle_B_distance',
    help="Set the distance between the input axle-A and input axle-B. Default: 0.0")
  r_parser.add_argument('--axle_B_angle','--aba', action='store', type=float, default=0.0, dest='sw_axle_B_angle',
    help="Set the angle between the symmetric axis and the intput_axle_B. Default: 0.0")
  r_parser.add_argument('--axle_B_diameter','--abd', action='store', type=float, default=0.0, dest='sw_axle_B_diameter',
    help="Set the diameter of the input_axle_B. If equal to 0.0, no hole for the axle_B is generated. Default: 0.0")
  r_parser.add_argument('--axle_B_external_diameter','--abed', action='store', type=float, default=0.0, dest='sw_axle_B_external_diameter',
    help="Set the external diameter of the input_axle_B. If equal to 0.0, it is set to 2*axle_B_diameter. Default: 0.0")
  r_parser.add_argument('--axle_B_hole_diameter','--abhd', action='store', type=float, default=0.0, dest='sw_axle_B_hole_diameter',
    help="Set the diameter of the hole in the holder-B for the axle_B. If equal to 0.0, no hole in the holder-B for the axle_B is generated. Default: 0.0")
  r_parser.add_argument('--axle_B_central_diameter','--abcd', action='store', type=float, default=0.0, dest='sw_axle_B_central_diameter',
    help="Set the central diameter of the axle_B for the holder-C. If equal to 0.0, it is set to 2*axle_B_diameter. Default: 0.0")
  ### input axle-C
  r_parser.add_argument('--axle_C_distance','--acdis', action='store', type=float, default=0.0, dest='sw_axle_C_distance',
    help="Set the distance between the input axle-B and input axle-C. Default: 0.0")
  r_parser.add_argument('--axle_C_angle','--aca', action='store', type=float, default=0.0, dest='sw_axle_C_angle',
    help="Set the angle between the AB-axis and the BC-axis. Default: 0.0")
  r_parser.add_argument('--axle_C_hole_diameter','--achd', action='store', type=float, default=0.0, dest='sw_axle_C_hole_diameter',
    help="Set the diameter of the hole of the axle_C. If equal to 0.0, no hole for the axle_C is generated. Default: 0.0")
  r_parser.add_argument('--axle_C_external_diameter','--aced', action='store', type=float, default=0.0, dest='sw_axle_C_external_diameter',
    help="Set the external diameter of the input_axle_C. If equal to 0.0, it is set to 2*axle_C_hole_diameter. Default: 0.0")
  ### motor screws
  # screw 1
  r_parser.add_argument('--motor_screw1_diameter','--ms1d', action='store', type=float, default=0.0, dest='sw_motor_screw1_diameter',
    help="Set the diameter of the screw1 holes for an electric motor. If equal to 0.0, no screw1 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw1_angle','--ms1a', action='store', type=float, default=0.0, dest='sw_motor_screw1_angle',
    help="Set the angle between the BC-axis and the screw1-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw1_x_length','--ms1xl', action='store', type=float, default=0.0, dest='sw_motor_screw1_x_length',
    help="Set the length between the screw1-y-axis and the screw1-hole (ie: half of the length between the two screw1-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw1_y_length','--ms1yl', action='store', type=float, default=0.0, dest='sw_motor_screw1_y_length',
    help="Set the length between the axle_C and the screw-x-axis. Default: 0.0")
  # screw 2
  r_parser.add_argument('--motor_screw2_diameter','--ms2d', action='store', type=float, default=0.0, dest='sw_motor_screw2_diameter',
    help="Set the diameter of the screw2 holes for an electric motor. If equal to 0.0, no screw1 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw2_angle','--ms2a', action='store', type=float, default=0.0, dest='sw_motor_screw2_angle',
    help="Set the angle between the BC-axis and the screw2-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw2_x_length','--ms2xl', action='store', type=float, default=0.0, dest='sw_motor_screw2_x_length',
    help="Set the length between the screw2-y-axis and the screw2-hole (ie: half of the length between the two screw1-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw2_y_length','--ms2yl', action='store', type=float, default=0.0, dest='sw_motor_screw2_y_length',
    help="Set the length between the axle_C and the screw2-x-axis. Default: 0.0")
  # screw 3
  r_parser.add_argument('--motor_screw3_diameter','--ms3d', action='store', type=float, default=0.0, dest='sw_motor_screw3_diameter',
    help="Set the diameter of the screw3 holes for an electric motor. If equal to 0.0, no screw3 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw3_angle','--ms3a', action='store', type=float, default=0.0, dest='sw_motor_screw3_angle',
    help="Set the angle between the BC-axis and the screw3-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw3_x_length','--ms3xl', action='store', type=float, default=0.0, dest='sw_motor_screw3_x_length',
    help="Set the length between the screw3-y-axis and the screw3-hole (ie: half of the length between the two screw3-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw3_y_length','--ms3yl', action='store', type=float, default=0.0, dest='sw_motor_screw3_y_length',
    help="Set the length between the axle_C and the screw3-x-axis. Default: 0.0")
  ### holder-C
  r_parser.add_argument('--fastening_BC_hole_diameter','--fbchd', action='store', type=float, default=0.0, dest='sw_fastening_BC_hole_diameter',
    help="Set the diameter of the holder B and C fastening holes. If equal to 0.0, no fastening holes are generated. Default: 0.0")
  r_parser.add_argument('--fastening_BC_external_diameter','--fbced', action='store', type=float, default=0.0, dest='sw_fastening_BC_external_diameter',
    help="Set the external diameter of the holder B and C fastening extremities. If equal to 0.0, it is set to 2*fastening_BC_hole_diameter. Default: 0.0")
  r_parser.add_argument('--fastening_BC_bottom_position_diameter','--fbcbpd', action='store', type=float, default=0.0, dest='sw_fastening_BC_bottom_position_diameter',
    help="Set the diameter of the position circle for the bottom fastening holes. Default: 0.0")
  r_parser.add_argument('--fastening_BC_bottom_angle','--fbcba', action='store', type=float, default=0.0, dest='sw_fastening_BC_bottom_angle',
    help="Set the angle between the AB-axis and the bottom fastening hole. Default: 0.0")
  r_parser.add_argument('--fastening_BC_top_position_diameter','--fbctpd', action='store', type=float, default=0.0, dest='sw_fastening_BC_top_position_diameter',
    help="Set the diameter of the position circle for the top fastening holes. Default: 0.0")
  r_parser.add_argument('--fastening_BC_top_angle','--fbcta', action='store', type=float, default=0.0, dest='sw_fastening_BC_top_angle',
    help="Set the angle between the AB-axis and the top fastening hole. Default: 0.0")
  ### general
  r_parser.add_argument('--smoothing_radius','--sr', action='store', type=float, default=0.0, dest='sw_smoothing_radius',
    help="Set the smoothing radius for the motor-lid. If equal to 0.0, it is set to cnc_router_bit_radius. Default: 0.0")
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the motor-lid. Default: 0.1")
  r_parser.add_argument('--extrusion_height','--eh', action='store', type=float, default=10.0, dest='sw_extrusion_height',
    help="Set the height of the linear extrusion of each part of the motor_lid assembly. Default: 10.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def motor_lid(ai_constraints):
  """
  The main function of the script.
  It generates a motor-lid assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  mldi = motor_lid_dictionary_init()
  ml_c = mldi.copy()
  ml_c.update(ai_constraints)
  #print("dbg155: ml_c:", ml_c)
  if(len(ml_c.viewkeys() & mldi.viewkeys()) != len(ml_c.viewkeys() | mldi.viewkeys())): # check if the dictionary ml_c has exactly all the keys compare to motor_lid_dictionary_init()
    print("ERR157: Error, ml_c has too much entries as {:s} or missing entries as {:s}".format(ml_c.viewkeys() - mldi.viewkeys(), mldi.viewkeys() - ml_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new motor_lid constraints:")
  #for k in ml_c.viewkeys():
  #  if(ml_c[k] != mldi[k]):
  #    print("dbg166: for k {:s}, ml_c[k] {:s} != mldi[k] {:s}".format(k, str(ml_c[k]), str(mldi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ## router_bit
  smoothing_radius = ml_c['smoothing_radius']
  cnc_router_bit_radius = ml_c['cnc_router_bit_radius']
  if(smoothing_radius==0):
    smoothing_radius = cnc_router_bit_radius
  if(smoothing_radius<cnc_router_bit_radius):
    print("ERR232: Error, smoothing_radius {:0.3f} is smaller than cnc_router_bit_radius {:0.3f}".format(smoothing_radius, cnc_router_bit_radius))
    sys.exit(2)
  ## holder-axis
  if((ml_c['axle_B_place']!='small')and(ml_c['axle_B_place']!='large')):
    print("ERR236: Error, axle_B_place {:s} accept only 'small' or 'large'".format(ml_c['axle_B_place']))
    sys.exit(2)
  holder_crenel_number = ml_c['holder_crenel_number']
  middle_crenel_1 = 0
  middle_crenel_2 = int(holder_crenel_number/2)
  if(ml_c['axle_B_place'] == 'large'):
    middle_crenel_2 = int((holder_crenel_number+1)/2)
  middle_crenel_index = [middle_crenel_1, middle_crenel_2]
  crenel_portion_angle = 2*math.pi/holder_crenel_number
  holder_axis_angle = ml_c['holder_position_angle'] + (middle_crenel_1 + 1 + middle_crenel_2)*crenel_portion_angle/2.0
  # axle_C
  holder_radius = ml_c['holder_diameter']/2.0
  l_AC = 0.0
  a_AC = 0.0
  #if(ml_c['axle_C_distance']<radian_epsilon):
  #  print("ERR237: Error, axle_C_distance {:0.3f} is too small".format(ml_c['axle_C_distance']))
  #  sys.exit(2)
  if(ml_c['axle_C_distance']>radian_epsilon):
    a_abc = math.pi-abs(ml_c['axle_C_angle']) # angle (ABC)
    l_AC = math.sqrt( ml_c['axle_B_distance']**2 + ml_c['axle_C_distance']**2 - 2 *  ml_c['axle_B_distance'] * ml_c['axle_C_distance'] * math.cos(a_abc)) # length (AC): law of cosines
    sin_a = math.sin(a_abc) * ml_c['axle_C_distance'] / l_AC # angle (CAB): law of sines
    a_cab = math.asin(sin_a)
    a_AC = ml_c['axle_B_angle'] + math.copysign(a_cab, ml_c['axle_C_angle']) # angle (holder-axis, AC)
    if(l_AC<holder_radius):
      print("ERR245: l_AC {:0.3} is smaller than the holder_radius {:0.3f}".format(l_AC, holder_radius))
      sys.exit(2)
  ### holder_A
  holder_A_axle_B_place = ml_c['axle_B_place']
  if(ml_c['axle_B_distance']<radian_epsilon):
    holder_A_axle_B_place = 'none'
  axle_B_radius = ml_c['axle_B_diameter']/2.0
  axle_B_external_radius = ml_c['axle_B_external_diameter']/2.0
  if(axle_B_external_radius==0):
    axle_B_external_radius = 2*axle_B_radius
  if(holder_A_axle_B_place != 'none'):
    if(axle_B_external_radius<axle_B_radius+radian_epsilon):
      print("ERR262: Error, axle_B_external_radius {:0.3f} is smaller than axle_B_radius {:0.3f}".format(axle_B_external_radius, axle_B_radius))
      sys.exit(2)
  alml_ci_keys = axle_lid.axle_lid_dictionary_init(1).viewkeys() & motor_lid_dictionary_init().viewkeys()
  al_c = dict([ (k, ml_c[k]) for k in alml_ci_keys ]) # extract only the entries of the axle_lid
  al_c['output_axle_B_place'] = holder_A_axle_B_place
  al_c['output_axle_distance'] = ml_c['axle_B_distance']
  al_c['output_axle_angle'] = ml_c['axle_B_angle']
  al_c['output_axle_B_external_diameter'] = 2*axle_B_external_radius
  al_c['output_axle_B_internal_diameter'] = 2*axle_B_radius
  al_c['input_axle_B_enable'] = True
  al_c['smoothing_radius'] = smoothing_radius
  al_c['cnc_router_bit_radius'] = ml_c['cnc_router_bit_radius']
  al_c['extrusion_height'] = ml_c['extrusion_height']
  al_c['tkinter_view'] = False
  al_c['output_file_basename'] = ""
  al_c['return_type'] = 'figures_for_motor_lid_holder_A'
  (holder_A_figure, holder_A_simple_figure, holder_A_with_motor_lid_figure, holder_A_with_leg_figure, holder_A_with_motor_lid_overlay_figure) = axle_lid.axle_lid(al_c)
  ### holder_B
  holder_B_axle_B_place = ml_c['axle_B_place']
  if(l_AC<radian_epsilon):
    holder_B_axle_B_place = 'none'
  axle_C_hole_radius = ml_c['axle_C_hole_diameter']/2.0
  axle_C_external_radius = ml_c['axle_C_external_diameter']/2.0
  if(axle_C_external_radius==0):
    axle_C_external_radius = 2*axle_C_hole_radius
  if(holder_B_axle_B_place != 'none'):
    if(axle_C_external_radius<axle_C_hole_radius+radian_epsilon):
      print("ERR280: Error, axle_C_external_radius {:0.3f} is too small compare to axle_C_hole_radius {:0.3f}".format(axle_C_external_radius, axle_C_hole_radius))
      sys.exit(2)
  al_c = dict([ (k, ml_c[k]) for k in alml_ci_keys ]) # extract only the entries of the axle_lid
  al_c['output_axle_B_place'] = holder_B_axle_B_place
  al_c['output_axle_distance'] = l_AC
  al_c['output_axle_angle'] = a_AC
  al_c['output_axle_B_external_diameter'] = 2*axle_C_external_radius
  al_c['output_axle_B_internal_diameter'] = 2*axle_C_hole_radius
  al_c['input_axle_B_enable'] = False
  al_c['smoothing_radius'] = smoothing_radius
  al_c['cnc_router_bit_radius'] = ml_c['cnc_router_bit_radius']
  al_c['extrusion_height'] = ml_c['extrusion_height']
  al_c['tkinter_view'] = False
  al_c['output_file_basename'] = ""
  al_c['return_type'] = 'figures_for_motor_lid_holder_B'
  (holder_B_figure, holder_B_simple_figure, holder_B_with_motor_lid_figure, holder_B_with_leg_figure) = axle_lid.axle_lid(al_c)
  ## middle_lid_figures
  al_c['return_type'] = 'figures_for_motor_lid_middle_lid'
  middle_lid_figures = axle_lid.axle_lid(al_c)
  ## axle_lid parameter info
  al_c['return_type'] = 'figures_for_motor_lid_parameter_info'
  al_parameter_info = axle_lid.axle_lid(al_c)
  ## holder_B_hole_figure
  g1_ix = 0.0
  g1_iy = 0.0
  holder_B_hole_figure = []
  # axle_B_hole_diameter
  axle_B_hole_radius = ml_c['axle_B_hole_diameter']/2.0
  a_AB = holder_axis_angle + ml_c['axle_B_angle']
  a_BC = a_AB + ml_c['axle_C_angle']
  bx = g1_ix+ml_c['axle_B_distance']*math.cos(a_AB)
  by = g1_iy+ml_c['axle_B_distance']*math.sin(a_AB)
  if(axle_B_hole_radius>0):
    holder_B_hole_figure.append((bx, by, axle_B_hole_radius))
  # fastening_BC_hole_figure
  fastening_BC_hole_figure = []
  fastening_BC_hole_radius = ml_c['fastening_BC_hole_diameter']/2.0
  fastening_BC_bottom_position_radius = ml_c['fastening_BC_bottom_position_diameter']/2.0
  fastening_BC_top_position_radius = ml_c['fastening_BC_top_position_diameter']/2.0
  if(fastening_BC_hole_radius>0):
    for s in [-1, 1]:
      a_bottom = a_AB + math.pi + s * ml_c['fastening_BC_bottom_angle']
      fastening_BC_hole_figure.append((bx+fastening_BC_bottom_position_radius*math.cos(a_bottom), by+fastening_BC_bottom_position_radius*math.sin(a_bottom), fastening_BC_hole_radius))
      a_top = a_BC + s * ml_c['fastening_BC_top_angle']
      fastening_BC_hole_figure.append((bx+fastening_BC_top_position_radius*math.cos(a_top), by+fastening_BC_top_position_radius*math.sin(a_top), fastening_BC_hole_radius))
  holder_B_hole_figure.extend(fastening_BC_hole_figure)
  # motor_screw
  motor_screw_diameter = [ml_c['motor_screw1_diameter'], ml_c['motor_screw2_diameter'], ml_c['motor_screw3_diameter']]
  motor_screw_angle = [ml_c['motor_screw1_angle'], ml_c['motor_screw2_angle'], ml_c['motor_screw3_angle']]
  motor_screw_x_length = [ml_c['motor_screw1_x_length'], ml_c['motor_screw2_x_length'], ml_c['motor_screw3_x_length']]
  motor_screw_y_length = [ml_c['motor_screw1_y_length'], ml_c['motor_screw2_y_length'], ml_c['motor_screw3_y_length']]
  cx = bx + ml_c['axle_C_distance']*math.cos(a_BC)
  cy = by + ml_c['axle_C_distance']*math.sin(a_BC)
  for i in range(len(motor_screw_diameter)):
    if(motor_screw_diameter[i]>0):
      for s in [-1, 1]:
        a_h = a_BC + motor_screw_angle[i]
        hx = cx + motor_screw_y_length[i] * math.cos(a_h) + motor_screw_x_length[i] * math.cos(a_h+s*math.pi/2)
        hy = cy + motor_screw_y_length[i] * math.sin(a_h) + motor_screw_x_length[i] * math.sin(a_h+s*math.pi/2)
        holder_B_hole_figure.append((hx, hy, motor_screw_diameter[i]/2.0))
  # holder_B
  holder_B_figure.extend(holder_B_hole_figure)
  holder_B_with_motor_lid_figure.extend(holder_B_hole_figure)
  ### holder_C
  fastening_BC_external_radius = ml_c['fastening_BC_external_diameter']/2.0
  if(fastening_BC_external_radius==0):
    fastening_BC_external_radius = 2*fastening_BC_hole_radius
  axle_B_central_radius = ml_c['axle_B_central_diameter']/2.0
  if(axle_B_central_radius==0):
    axle_B_central_radius = 2*axle_B_radius
  holder_C_figure = []
  if(fastening_BC_external_radius>0):
    if(fastening_BC_external_radius<fastening_BC_hole_radius+radian_epsilon):
      print("ERR367: Error, fastening_BC_external_radius {:0.3f} is too small compare to fastening_BC_hole_radius {:0.3f}".format(fastening_BC_external_radius, fastening_BC_hole_radius))
      sys.exit(2)
    if(axle_B_central_radius<axle_B_radius+radian_epsilon):
      print("ERR355: Error, axle_B_central_radius {:0.3f} is too small compare to axle_B_radius {:0.3f}".format(axle_B_central_radius, axle_B_radius))
      sys.exit(2)
    if(fastening_BC_hole_radius<radian_epsilon):
      print("ERR324: Error, fastening_BC_hole_radius {:0.3f} is too small".format(fastening_BC_hole_radius))
      sys.exit(2)
    if((fastening_BC_external_radius+fastening_BC_hole_radius)>fastening_BC_bottom_position_radius):
      print("ERR327: Error, fastening_BC_bottom_position_radius {:0.3f} is too small compare to fastening_BC_external_radius {:0.3f} and fastening_BC_hole_radius {:0.3f}".format(fastening_BC_bottom_position_radius, fastening_BC_external_radius, fastening_BC_hole_radius))
      sys.exit(2)
    if((fastening_BC_external_radius+fastening_BC_hole_radius)>fastening_BC_top_position_radius):
      print("ERR330: Error, fastening_BC_top_position_radius {:0.3f} is too small compare to fastening_BC_external_radius {:0.3f} and fastening_BC_hole_radius {:0.3f}".format(fastening_BC_top_position_radius, fastening_BC_external_radius, fastening_BC_hole_radius))
      sys.exit(2)
    # holder_C_outline_A
    holder_C_outline_A = []
    hca = ((a_AB + math.pi - ml_c['fastening_BC_bottom_angle'], fastening_BC_bottom_position_radius),
           (a_AB + math.pi + ml_c['fastening_BC_bottom_angle'], fastening_BC_bottom_position_radius),
           (a_BC - ml_c['fastening_BC_top_angle'], fastening_BC_top_position_radius),
           (a_BC + ml_c['fastening_BC_top_angle'], fastening_BC_top_position_radius))
    for i in range(len(hca)):
      ea = hca[i][0]
      ma = hca[i-1][0] + (math.fmod(hca[i][0] - hca[i-1][0] + 4*math.pi, 2*math.pi) - 0*math.pi)/2.0 # we always want the angle positive because we always turn CCW
      dl = math.sqrt(hca[i][1]**2 + fastening_BC_external_radius**2)
      da = math.atan(float(fastening_BC_external_radius)/hca[i][1])
      sl = hca[i][1] + fastening_BC_external_radius
      holder_C_outline_A.append((bx+axle_B_central_radius*math.cos(ma), by+axle_B_central_radius*math.sin(ma), smoothing_radius))
      holder_C_outline_A.append((bx+dl*math.cos(ea-da), by+dl*math.sin(ea-da), 0))
      holder_C_outline_A.append((bx+sl*math.cos(ea), by+sl*math.sin(ea), bx+dl*math.cos(ea+da), by+dl*math.sin(ea+da), 0))
    holder_C_outline_A.append((holder_C_outline_A[0][0], holder_C_outline_A[0][1], 0))
    # holder_C_figure
    holder_C_figure.append(cnc25d_api.cnc_cut_outline(holder_C_outline_A, "holder_C_outline_A"))
    if(axle_B_radius>0):
      holder_C_figure.append((bx, by, axle_B_radius))
    holder_C_figure.extend(fastening_BC_hole_figure)

  ### design output
  # part_figure_list
  part_figure_list = []
  part_figure_list.append(holder_A_figure)
  part_figure_list.append(middle_lid_figures[0])
  part_figure_list.append(middle_lid_figures[1])
  part_figure_list.append(holder_B_figure)
  part_figure_list.append(holder_C_figure)
  part_figure_list.append(holder_A_with_motor_lid_figure)
  # assembly
  ml_assembly_figure = []
  for i in range(len(part_figure_list)):
    ml_assembly_figure.extend(part_figure_list[i])
  ml_assembly_figure_overlay = []
  ml_assembly_figure_overlay.extend(holder_A_with_motor_lid_overlay_figure)
  # ml_list_of_parts
  x_space = 3.1*holder_radius
  ml_list_of_parts = []
  for i in range(len(part_figure_list)):
    for j in range(len(part_figure_list[i])):
      ml_list_of_parts.append(cnc25d_api.outline_shift_x(part_figure_list[i][j], i*x_space, 1))

  # ml_parameter_info
  ml_parameter_info = "\nmotor_lid parameter info:\n"
  ml_parameter_info += "\n" + ml_c['args_in_txt'] + "\n\n"
  ml_parameter_info += al_parameter_info
  ml_parameter_info += """
axle_B_place:  \t{:s}
axle_B_distance: \t{:0.3f}
axle_B_angle: \t{:0.3f} (radian) \t{:0.3f} (degree)
axle_B_radius: \t{:0.3f}  diameter: \t{:0.3f}
axle_B_external_radius: \t{:0.3f}  diameter: \t{:0.3f}
axle_B_hole_radius: \t{:0.3f}  diameter: \t{:0.3f}
axle_B_central_radius: \t{:0.3f}  diameter: \t{:0.3f}
""".format(ml_c['axle_B_place'], ml_c['axle_B_distance'], ml_c['axle_B_angle'], ml_c['axle_B_angle']*180/math.pi, axle_B_radius, 2*axle_B_radius, axle_B_external_radius, 2*axle_B_external_radius, axle_B_hole_radius, 2*axle_B_hole_radius, axle_B_central_radius, 2*axle_B_central_radius)
  ml_parameter_info += """
axle_C_distance:  \t{:0.3f}
axle_C_angle: \t{:0.3f} (radian) \t{:0.3f} (degree)
axle_C_hole_radius: \t{:0.3f}  diameter: \t{:0.3f}
axle_C_external_radius: \t{:0.3f}  diameter: \t{:0.3f}
""".format(ml_c['axle_C_distance'], ml_c['axle_C_angle'], ml_c['axle_C_angle']*180/math.pi, axle_C_hole_radius, 2*axle_C_hole_radius, axle_C_external_radius, 2*axle_C_external_radius)
  for i in range(len(motor_screw_diameter)):
    ml_parameter_info += """
motor_screw{:d}_radius {:0.3f}  diameter {:0.3f}
motor_screw{:d}_angle {:0.3f} (radian) \t{:0.3f} (degree)
motor_screw{:d}_x_length {:0.3f}  2x_length {:0.3f}
motor_screw{:d}_y_length {:0.3f}  2y_length {:0.3f}
""".format(i, motor_screw_diameter[i]/2.0, motor_screw_diameter[i], i, motor_screw_angle[i], motor_screw_angle[i]*180/math.pi, i, motor_screw_x_length[i], 2* motor_screw_x_length[i], i, motor_screw_y_length[i], 2* motor_screw_y_length[i])
  ml_parameter_info += """
fastening_BC_hole_radius {:0.3f}  diameter {:0.3f}
fastening_BC_external_radius {:0.3f}  diameter {:0.3f}
fastening_BC_bottom_position_radius {:0.3f}  diameter {:0.3f}
fastening_BC_bottom_angle {:0.3f} (radian) \t{:0.3f} (degree)
fastening_BC_top_position_radius {:0.3f}  diameter {:0.3f}
fastening_BC_top_angle {:0.3f} (radian) \t{:0.3f} (degree)
smoothing_radius {:0.3f}  diameter {:0.3f}
cnc_router_bit_radius {:0.3f}  diameter {:0.3f}
""".format(fastening_BC_hole_radius, 2*fastening_BC_hole_radius, fastening_BC_external_radius, 2*fastening_BC_external_radius, fastening_BC_bottom_position_radius, 2*fastening_BC_bottom_position_radius, ml_c['fastening_BC_bottom_angle'], ml_c['fastening_BC_bottom_angle']*180/math.pi, fastening_BC_top_position_radius, 2*fastening_BC_top_position_radius, ml_c['fastening_BC_top_angle'], ml_c['fastening_BC_top_angle']*180/math.pi, smoothing_radius, 2*smoothing_radius, cnc_router_bit_radius, 2*cnc_router_bit_radius)
  #print(ml_parameter_info)

  ### display with Tkinter
  if(ml_c['tkinter_view']):
    print(ml_parameter_info)
    cnc25d_api.figure_simple_display(ml_assembly_figure, ml_assembly_figure_overlay, ml_parameter_info)
    #cnc25d_api.figure_simple_display(holder_A_figure, ml_assembly_figure_overlay, ml_parameter_info)
    #cnc25d_api.figure_simple_display(holder_B_figure, ml_assembly_figure_overlay, ml_parameter_info)
    #cnc25d_api.figure_simple_display(holder_C_figure, ml_assembly_figure_overlay, ml_parameter_info)
      
  ### sub-function to create the freecad-object
  def freecad_motor_lid(nai_part_figure_list):
    fc_obj = []
    for i in range(len(nai_part_figure_list)):
      fc_obj.append(cnc25d_api.figure_to_freecad_25d_part(nai_part_figure_list[i], ml_c['extrusion_height']))
      if((i==1)or(i==2)): # middle_lid
        fc_obj[i].translate(Base.Vector(0,0,5.0*ml_c['extrusion_height']))
      if(i==3): # holder_B
        fc_obj[i].translate(Base.Vector(0,0,10.0*ml_c['extrusion_height']))
      if(i==4): # holder_C
        fc_obj[i].translate(Base.Vector(0,0,15.0*ml_c['extrusion_height']))
    r_fal = Part.makeCompound(fc_obj)
    return(r_fal)

  ### generate output file
  output_file_suffix = ''
  if(ml_c['output_file_basename']!=''):
    output_file_suffix = '' # .brep
    output_file_basename = ml_c['output_file_basename']
    if(re.search('\.dxf$', ml_c['output_file_basename'])):
      output_file_suffix = '.dxf'
      output_file_basename = re.sub('\.dxf$', '', ml_c['output_file_basename'])
    elif(re.search('\.svg$', ml_c['output_file_basename'])):
      output_file_suffix = '.svg'
      output_file_basename = re.sub('\.svg$', '', ml_c['output_file_basename'])
  if(ml_c['output_file_basename']!=''):
    # parts
    cnc25d_api.generate_output_file(holder_A_figure, output_file_basename + "_holder_A" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(middle_lid_figures[0], output_file_basename + "_middle_lid1" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(middle_lid_figures[1], output_file_basename + "_middle_lid2" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(holder_B_figure, output_file_basename + "_holder_B" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(holder_C_figure, output_file_basename + "_holder_C" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(holder_A_simple_figure, output_file_basename + "_holder_A_simple" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(holder_B_simple_figure, output_file_basename + "_holder_B_simple" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(holder_A_with_motor_lid_figure, output_file_basename + "_holder_A_with_motor_lid" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(holder_B_with_motor_lid_figure, output_file_basename + "_holder_B_with_motor_lid" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(holder_A_with_leg_figure, output_file_basename + "_holder_A_with_leg" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    cnc25d_api.generate_output_file(holder_B_with_leg_figure, output_file_basename + "_holder_B_with_leg" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    # assembly
    if((output_file_suffix=='.svg')or(output_file_suffix=='.dxf')):
      cnc25d_api.generate_output_file(ml_assembly_figure, output_file_basename + "_assembly" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
      cnc25d_api.generate_output_file(ml_list_of_parts, output_file_basename + "_part_list" + output_file_suffix, ml_c['extrusion_height'], ml_parameter_info)
    else:
      fc_assembly_filename = "{:s}_assembly.brep".format(output_file_basename)
      print("Generate with FreeCAD the BRep file {:s}".format(fc_assembly_filename))
      fc_assembly = freecad_motor_lid(part_figure_list)
      fc_assembly.exportBrep(fc_assembly_filename)

  #### return
  if(ml_c['return_type']=='int_status'):
    r_ml = 1
  elif(ml_c['return_type']=='cnc25d_figure'):
    r_ml = part_figure_list
  elif(ml_c['return_type']=='freecad_object'):
    r_ml = freecad_motor_lid(part_figure_list)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(ml_c['return_type']))
    sys.exit(2)
  return(r_ml)

################################################################
# motor-lid wrapper dance
################################################################

def motor_lid_argparse_to_dictionary(ai_ml_args):
  """ convert a motor_lid_argparse into a motor_lid_dictionary
  """
  r_mld = {}
  ### annulus-holder: inherit dictionary entries from axle_lid
  r_mld.update(axle_lid.axle_lid_argparse_to_dictionary(ai_ml_args, 1))
  #### motor_lid dictionary entries
  ### input axle-B
  r_mld['axle_B_place']             = ai_ml_args.sw_axle_B_place
  r_mld['axle_B_distance']          = ai_ml_args.sw_axle_B_distance
  r_mld['axle_B_angle']             = ai_ml_args.sw_axle_B_angle
  r_mld['axle_B_diameter']          = ai_ml_args.sw_axle_B_diameter
  r_mld['axle_B_external_diameter'] = ai_ml_args.sw_axle_B_external_diameter
  r_mld['axle_B_hole_diameter']     = ai_ml_args.sw_axle_B_hole_diameter
  r_mld['axle_B_central_diameter']  = ai_ml_args.sw_axle_B_central_diameter
  ### input axle-C
  r_mld['axle_C_distance']          = ai_ml_args.sw_axle_C_distance
  r_mld['axle_C_angle']             = ai_ml_args.sw_axle_C_angle
  r_mld['axle_C_hole_diameter']     = ai_ml_args.sw_axle_C_hole_diameter
  r_mld['axle_C_external_diameter'] = ai_ml_args.sw_axle_C_external_diameter
  ### motor screws
  r_mld['motor_screw1_diameter']    = ai_ml_args.sw_motor_screw1_diameter
  r_mld['motor_screw1_angle']       = ai_ml_args.sw_motor_screw1_angle
  r_mld['motor_screw1_x_length']    = ai_ml_args.sw_motor_screw1_x_length
  r_mld['motor_screw1_y_length']    = ai_ml_args.sw_motor_screw1_y_length
  r_mld['motor_screw2_diameter']    = ai_ml_args.sw_motor_screw2_diameter
  r_mld['motor_screw2_angle']       = ai_ml_args.sw_motor_screw2_angle
  r_mld['motor_screw2_x_length']    = ai_ml_args.sw_motor_screw2_x_length
  r_mld['motor_screw2_y_length']    = ai_ml_args.sw_motor_screw2_y_length
  r_mld['motor_screw3_diameter']    = ai_ml_args.sw_motor_screw3_diameter
  r_mld['motor_screw3_angle']       = ai_ml_args.sw_motor_screw3_angle
  r_mld['motor_screw3_x_length']    = ai_ml_args.sw_motor_screw3_x_length
  r_mld['motor_screw3_y_length']    = ai_ml_args.sw_motor_screw3_y_length
  ### holder-C
  r_mld['fastening_BC_hole_diameter']             = ai_ml_args.sw_fastening_BC_hole_diameter
  r_mld['fastening_BC_external_diameter']         = ai_ml_args.sw_fastening_BC_external_diameter
  r_mld['fastening_BC_bottom_position_diameter']  = ai_ml_args.sw_fastening_BC_bottom_position_diameter
  r_mld['fastening_BC_bottom_angle']              = ai_ml_args.sw_fastening_BC_bottom_angle
  r_mld['fastening_BC_top_position_diameter']     = ai_ml_args.sw_fastening_BC_top_position_diameter
  r_mld['fastening_BC_top_angle']                 = ai_ml_args.sw_fastening_BC_top_angle
  ### general
  r_mld['smoothing_radius']       = ai_ml_args.sw_smoothing_radius
  r_mld['cnc_router_bit_radius']  = ai_ml_args.sw_cnc_router_bit_radius
  r_mld['extrusion_height']       = ai_ml_args.sw_extrusion_height
  ### output
  #r_mld['tkinter_view']           = False
  r_mld['output_file_basename']   = ai_ml_args.sw_output_file_basename
  ### optional
  #r_mld['args_in_txt'] = ""
  r_mld['return_type'] = ai_ml_args.sw_return_type
  #### return
  return(r_mld)
  
def motor_lid_argparse_wrapper(ai_ml_args, ai_args_in_txt=""):
  """
  wrapper function of motor_lid() to call it using the motor_lid_parser.
  motor_lid_parser is mostly used for debug and non-regression tests.
  """
  # view the motor_lid with Tkinter as default action
  tkinter_view = True
  if(ai_ml_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  mld = motor_lid_argparse_to_dictionary(ai_ml_args)
  mld['args_in_txt'] = ai_args_in_txt
  mld['tkinter_view'] = tkinter_view
  #mld['return_type'] = 'int_status'
  r_ml = motor_lid(mld)
  return(r_ml)

################################################################
# self test
################################################################

def motor_lid_self_test():
  """
  This is the non-regression test of motor_lid.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , "--holder_diameter 160.0 --clearance_diameter 140.0 --central_diameter 80.0 --axle_hole_diameter 22.0"],
    ["small side"            , "--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place small --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_external_diameter 15.0"],
    ["large side with side leg" , "--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place large --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_external_diameter 15.0 --leg_type side --leg_length 120.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0"],
    ["seven holder", "--holder_diameter 59.0 --holder_hole_position_radius 30.5 --holder_hole_diameter 4.1 --holder_double_hole_diameter 0.9 --holder_double_hole_length 8.0 --holder_double_hole_position -1.0 --holder_double_hole_mark_nb 1 --holder_crenel_position 3.5 --holder_crenel_height 0.5 --holder_crenel_width 6.0 --holder_crenel_skin_width 3.0 --holder_crenel_router_bit_radius 0.1 --holder_smoothing_radius 0.0 --clearance_diameter 53.0 --axle_hole_diameter 5.9 --central_diameter 30.0 --axle_B_distance 0.0 --axle_B_external_diameter 0.0 --axle_C_distance 53.0 --axle_C_external_diameter 38.0 --holder_crenel_number 7"],
    ["output files" , "--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place large --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_external_diameter 15.0 --leg_type side --leg_length 120.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0 --axle_B_hole_diameter 20.0 --output_file_basename test_output/motor_lid_self_test.dxf"],
    ["last test"            , "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0  --holder_crenel_number 6 --axle_B_distance 52.0 --axle_C_distance 40.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  motor_lid_parser = argparse.ArgumentParser(description='Command line interface for the function motor_lid().')
  motor_lid_parser = motor_lid_add_argument(motor_lid_parser)
  motor_lid_parser = cnc25d_api.generate_output_file_add_argument(motor_lid_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = motor_lid_parser.parse_args(l_args)
    r_mlst = motor_lid_argparse_wrapper(st_args)
  return(r_mlst)

################################################################
# motor_lid command line interface
################################################################

def motor_lid_cli(ai_args=""):
  """ command line interface of motor_lid.py when it is used in standalone
  """
  # motor_lid parser
  motor_lid_parser = argparse.ArgumentParser(description='Command line interface for the function motor_lid().')
  motor_lid_parser = motor_lid_add_argument(motor_lid_parser)
  motor_lid_parser = cnc25d_api.generate_output_file_add_argument(motor_lid_parser, 1)
  # switch for self_test
  motor_lid_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "motor_lid arguments: " + ' '.join(effective_args)
  ml_args = motor_lid_parser.parse_args(effective_args)
  print("dbg111: start making motor_lid")
  if(ml_args.sw_run_self_test):
    r_ml = motor_lid_self_test()
  else:
    r_ml = motor_lid_argparse_wrapper(ml_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_ml)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("motor_lid.py says hello!\n")
  #my_ml = motor_lid_cli()
  #my_ml = motor_lid_cli("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --return_type freecad_object")
  #my_ml = motor_lid_cli("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --axle_B_distance 52.0 --axle_C_distance 40.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0")
  my_ml = motor_lid_cli("--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place small --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_hole_diameter 20.0 --axle_B_external_diameter 15.0")
  #my_ml = motor_lid_cli("--holder_diameter 140.0 --clearance_diameter 110.0 --central_diameter 30.0 --axle_hole_diameter 6.0  --holder_crenel_number 7 --axle_B_distance 75.0 --axle_C_distance 30.0 --axle_C_hole_diameter 10.0 --axle_B_diameter 3.0 --axle_B_place small --axle_B_angle 0.2 --axle_C_angle -0.4 --motor_screw1_diameter 2.0 --motor_screw1_x_length 10.0 --fastening_BC_hole_diameter 2.0 --fastening_BC_bottom_position_diameter 50.0 --fastening_BC_bottom_angle 0.5 --fastening_BC_top_position_diameter 45.0 --fastening_BC_top_angle 0.3 --smoothing_radius 3.0 --axle_B_hole_diameter 20.0 --axle_B_external_diameter 15.0 --return_type freecad_object")
  #Part.show(my_ml)
  try: # depending on ml_c['return_type'] it might be or not a freecad_object
    Part.show(my_ml)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


