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
The main function return the split-gear-wheel as FreeCAD Part object.
You can also simulate or view of the split-gearwheel and get a DXF, SVG or BRep file.
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
# split_gearwheel dictionary-arguments default values
################################################################

def split_gearwheel_dictionary_init():
  """ create and initiate a split_gearwheel_dictionary with the default value
  """
  r_sgwd = {}
  #### inherit dictionary entries from gear_profile
  r_sgwd.update(gear_profile.gear_profile_dictionary_init())
  #### split_gearwheel dictionary entries
  ### split
  r_sgwd['split_nb']                 = 6
  r_sgwd['split_initial_angle']      = 0.0
  r_sgwd['low_split_diameter']       = 0.0
  r_sgwd['low_split_type']           = 'circle'
  r_sgwd['high_split_diameter']      = 0.0
  r_sgwd['high_split_type']          = 'h'
  r_sgwd['split_router_bit_radius']  = 1.0
  ### low-holes
  r_sgwd['low_hole_circle_diameter']   = 0.0
  r_sgwd['low_hole_diameter']          = 10.0
  r_sgwd['low_hole_nb']                = 1
  ### high-holes
  r_sgwd['high_hole_circle_diameter']  = 0.0
  r_sgwd['high_hole_diameter']         = 10.0
  r_sgwd['high_hole_nb']               = 2
  ### cnc router_bit constraint
  r_sgwd['cnc_router_bit_radius']      = 1.0
  ### view the split_gearwheel with tkinter
  r_sgwd['tkinter_view'] = False
  r_sgwd['output_file_basename'] = ''
  ### optional
  r_sgwd['args_in_txt'] = ""
  #### return
  return(r_sgwd)

################################################################
# split_gearwheel argparse
################################################################

def split_gearwheel_add_argument(ai_parser):
  """
  Add arguments relative to the split-gearwheel in addition to the argument of gear_profile_add_argument()
  This function intends to be used by the split_gearwheel_cli, split_gearwheel_self_test
  """
  r_parser = ai_parser
  ### inherit arguments from gear_profile
  r_parser = gear_profile.gear_profile_add_argument(r_parser, 1)
  ### split
  ## general
  r_parser.add_argument('--split_nb','--snb', action='store', type=int, default=6, dest='sw_split_nb',
    help="Set the number of portions to split the gearwheel. Default: 6")
  r_parser.add_argument('--split_initial_angle','--sia', action='store', type=float, default=0.0, dest='sw_split_initial_angle',
    help="Set the angle between the X-axis and the first split radius. Default: 0.0")
  ## low_split
  r_parser.add_argument('--low_split_diameter','--lsd', action='store', type=float, default=0.0, dest='sw_low_split_diameter',
    help="Set the diameter of the inner circle of the split-portion. Default: 0.0")
  r_parser.add_argument('--low_split_type','--lst', action='store', default='circle', dest='sw_low_split_type',
    help="Select the type of outline for the inner border of the split-portions. Possible values: 'circle', 'line'. Default: 'circle'")
  ## high_split
  r_parser.add_argument('--high_split_diameter','--hsd', action='store', type=float, default=0.0, dest='sw_high_split_diameter',
    help="Set the diameter of the high circle of the split-portion. If equal to 0.0, it is set to the dedendum diameter minus tooth_half_height. Default: 0.0")
  r_parser.add_argument('--high_split_type','--hst', action='store', default='h', dest='sw_high_split_type',
    help="Select the type of connection between the split-portion high-circle and the gear-profile. Possible values: 'h'=hollow_only , 'a'=addendum_too. Default: 'h'")
  ## split_router_bit_radius
  r_parser.add_argument('--split_router_bit_radius','--srbr', action='store', type=float, default=1.0, dest='sw_split_router_bit_radius',
    help="Set the split router_bit radius of the split-gearwheel (used at the high-circle corners). Default: 1.0")
  ### low-hole
  r_parser.add_argument('--low_hole_circle_diameter','--lhcd', action='store', type=float, default=0.0, dest='sw_low_hole_circle_diameter',
    help="Set the diameter of the low-hole circle. Default: 0.0")
  r_parser.add_argument('--low_hole_diameter','--lhd', action='store', type=float, default=10.0, dest='sw_low_hole_diameter',
    help="Set the diameter of the low-holes. Default: 10.0")
  r_parser.add_argument('--low_hole_nb','--lhn', action='store', type=int, default=1, dest='sw_low_hole_nb',
    help="Set the number of low-holes. Default: 1")
  ### high-hole
  r_parser.add_argument('--high_hole_circle_diameter','--hhcd', action='store', type=float, default=0.0, dest='sw_high_hole_circle_diameter',
    help="Set the diameter of the high-hole circle. If equal to 0.0, set to high_split_diameter minus high_hole_diameter. Default: 0.0")
  r_parser.add_argument('--high_hole_diameter','--hhd', action='store', type=float, default=10.0, dest='sw_high_hole_diameter',
    help="Set the diameter of the high-holes. Default: 10.0")
  r_parser.add_argument('--high_hole_nb','--hhn', action='store', type=int, default=1, dest='sw_high_hole_nb',
    help="Set the number of high-holes. Default: 1")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=1.0, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the split-gearwheel. It increases gear_router_bit_radius and split_router_bit_radius if needed. Default: 1.0")
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def split_gearwheel(ai_constraints):
  """
  The main function of the script.
  It generates a split-gearwheel according to the function arguments
  """
  # check the dictionary-arguments ai_constraints
  sgdi = split_gearwheel_dictionary_init()
  sg_c = sgdi.copy()
  sg_c.update(ai_constraints)
  #print("dbg155: sg_c:", sg_c)
  if(len(sg_c.viewkeys() & sgdi.viewkeys()) != len(sg_c.viewkeys() | sgdi.viewkeys())): # check if the dictionary sg_c has exactly all the keys compare to split_gearwheel_dictionary_init()
    print("ERR157: Error, sg_c has too much entries as {:s} or missing entries as {:s}".format(sg_c.viewkeys() - sgdi.viewkeys(), sgdi.viewkeys() - sg_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new split_gearwheel constraints:")
  #for k in sg_c.viewkeys():
  #  if(sg_c[k] != sgdi[k]):
  #    print("dbg166: for k {:s}, sg_c[k] {:s} != sgdi[k] {:s}".format(k, str(sg_c[k]), str(sgdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  # get the router_bit_radius
  gear_router_bit_radius = sg_c['gear_router_bit_radius']
  if(sg_c['cnc_router_bit_radius']>gear_router_bit_radius):
    gear_router_bit_radius = sg_c['cnc_router_bit_radius']
  split_router_bit_radius = sg_c['split_router_bit_radius']
  if(sg_c['cnc_router_bit_radius']>split_router_bit_radius):
    split_router_bit_radius = sg_c['cnc_router_bit_radius']
  # sg_c['low_split_type']
  if(not sg_c['low_split_type'] in ('circle', 'line')):
    print("ERR216: Error, sg_c['low_split_type'] {:s} is not valid!".format(sg_c['low_split_type']))
    sys.exit(2)
  # sg_c['high_split_type']
  if(not sg_c['high_split_type'] in ('h', 'a')):
    print("ERR220: Error, sg_c['high_split_type'] {:s} is not valid!".format(sg_c['high_split_type']))
    sys.exit(2)
  # pre_minimal_gear_profile_radius
  #pre_minimal_gear_profile_radius = 
#  # ai_axle_x_width
#  axle_diameter = 0
#  if(ai_axle_type in('circle','rectangle')):
#    if(ai_axle_x_width<2*axle_router_bit_radius+radian_epsilon):
#      print("ERR663: Error, ai_axle_x_width {:0.2f} is too small compare to axle_router_bit_radius {:0.2f}!".format(ai_axle_x_width, axle_router_bit_radius))
#      sys.exit(2)
#    axle_diameter = ai_axle_x_width
#    # ai_axle_y_width
#    if(ai_axle_type=='rectangle'):
#      if(ai_axle_y_width<2*axle_router_bit_radius+radian_epsilon):
#        print("ERR664: Error, ai_axle_y_width {:0.2f} is too small compare to axle_router_bit_radius {:0.2f}!".format(ai_axle_y_width, axle_router_bit_radius))
#        sys.exit(2)
#      axle_diameter = math.sqrt(ai_axle_x_width**2+ai_axle_y_width**2)
  # sg_c['gear_tooth_nb']
  #print("dbg190: sg_c['gear_tooth_nb']:", sg_c['gear_tooth_nb'])
  if(sg_c['gear_tooth_nb']>0): # create a gear_profile
    ### get the gear_profile
    gpdi = gear_profile.gear_profile_dictionary_init()
    gpd = dict([ (k, sg_c[k]) for k in gpdi.keys() ]) # extract only the entries of the gear_profile
    gpd['gear_type'] = 'e'
    gpd['portion_tooth_nb'] = 0
    gpd['portion_first_end'] = 0
    gpd['portion_last_end'] = 0
    gpd['output_file_basename'] = ''
    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile_dictionary_wrapper(gpd)
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    minimal_gear_profile_radius = gear_profile_parameters['hollow_radius']
    g1_ix = gear_profile_parameters['center_ox']
    g1_iy = gear_profile_parameters['center_oy']
  else: # no gear_profile, just a circle
    if(sg_c['gear_primitive_diameter']<radian_epsilon):
      print("ERR885: Error, the no-gear-profile circle outline diameter sg_c['gear_primitive_diameter'] {:0.2f} is too small!".format(sg_c['gear_primitive_diameter']))
      sys.exit(2)
    g1_ix = sg_c['center_position_x']
    g1_iy = sg_c['center_position_y']
    gear_profile_B = (g1_ix, g1_iy, float(sg_c['gear_primitive_diameter'])/2)
    gear_profile_info = "\nSimple circle (no-gear-profile):\n"
    gear_profile_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(sg_c['gear_primitive_diameter']/2.0, sg_c['gear_primitive_diameter'])
    gear_profile_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(g1_ix, g1_iy)
    minimal_gear_profile_radius = float(sg_c['gear_primitive_diameter'])/2
#  ### check parameter coherence (part 2)
#  if(ai_wheel_hollow_leg_number>0):
#    # wheel_hollow_external_diameter
#    if(ai_wheel_hollow_external_diameter > 2*minimal_gear_profile_radius-radian_epsilon):
#      print("ERR733: Error, ai_wheel_hollow_external_diameter {:0.2f} is bigger than the gear_hollow_radius {:0.2f}!".format(ai_wheel_hollow_external_diameter, minimal_gear_profile_radius))
#      sys.exit(2)
#    if(ai_wheel_hollow_external_diameter < ai_wheel_hollow_internal_diameter+4*wheel_hollow_router_bit_radius):
#      print("ERR734: Error, ai_wheel_hollow_external_diameter {:0.2f} is too small compare to ai_wheel_hollow_internal_diameter {:0.2f} and wheel_hollow_router_bit_radius {:0.2f}!".format(ai_wheel_hollow_external_diameter, ai_wheel_hollow_internal_diameter, wheel_hollow_router_bit_radius))
#      sys.exit(2)
#    # wheel_hollow_leg_width
#    if(ai_wheel_hollow_leg_width<radian_epsilon):
#      print("ERR735: Error, ai_wheel_hollow_leg_width {:0.2f} is too small!".format(ai_wheel_hollow_leg_width))
#      sys.exit(2)
#    # wheel_hollow_internal_diameter
#    if(ai_wheel_hollow_internal_diameter<axle_diameter+radian_epsilon):
#      print("ERR736: Error, ai_wheel_hollow_internal_diameter {:0.2f} is too small compare to axle_diameter {:0.2f}!".format(ai_wheel_hollow_internal_diameter, axle_diameter))
#      sys.exit(2)
#    if(ai_wheel_hollow_internal_diameter<ai_wheel_hollow_leg_width+2*radian_epsilon):
#      print("ERR736: Error, ai_wheel_hollow_internal_diameter {:0.2f} is too small compare to ai_wheel_hollow_leg_width {:0.2f}!".format(ai_wheel_hollow_internal_diameter, ai_wheel_hollow_leg_width))
#      sys.exit(2)
#  # 
#
#  ### axle
#  axle_figure = []
#  axle_figure_overlay = []
#  if(ai_axle_type=='circle'):
#    axle_figure.append([g1_ix, g1_iy, axle_diameter/2.0])
#  elif(ai_axle_type=='rectangle'):
#    axle_A = [
#      [g1_ix-ai_axle_x_width/2.0, g1_iy-ai_axle_y_width/2.0, -1*axle_router_bit_radius],
#      [g1_ix+ai_axle_x_width/2.0, g1_iy-ai_axle_y_width/2.0, -1*axle_router_bit_radius],
#      [g1_ix+ai_axle_x_width/2.0, g1_iy+ai_axle_y_width/2.0, -1*axle_router_bit_radius],
#      [g1_ix-ai_axle_x_width/2.0, g1_iy+ai_axle_y_width/2.0, -1*axle_router_bit_radius]]
#    axle_A = cnc25d_api.outline_close(axle_A)
#    axle_figure.append(cnc25d_api.cnc_cut_outline(axle_A, "axle_A"))
#    axle_figure_overlay.append(cnc25d_api.ideal_outline(axle_A, "axle_A"))
#
#  ### wheel hollow (a.k.a legs)
#  wheel_hollow_figure = []
#  wheel_hollow_figure_overlay = []
#  if(ai_wheel_hollow_leg_number>0):
#    wh_angle = 2*math.pi/ai_wheel_hollow_leg_number
#    wh_leg_top_angle1 = math.asin(float(ai_wheel_hollow_leg_width/2.0+wheel_hollow_router_bit_radius)/(ai_wheel_hollow_external_diameter/2.0-wheel_hollow_router_bit_radius))
#    if(wh_angle<2*wh_leg_top_angle1+radian_epsilon):
#      print("ERR664: Error, wh_angle {:0.2f} too small compare to wh_leg_top_angle {:0.2f}!".format(wh_angle, wh_leg_top_angle))
#      sys.exit(2)
#    wh_leg_bottom_angle1 = math.asin(float(ai_wheel_hollow_leg_width/2.0+wheel_hollow_router_bit_radius)/(ai_wheel_hollow_internal_diameter/2.0+wheel_hollow_router_bit_radius))
#    #wh_leg_top_angle2 = math.asin((ai_wheel_hollow_leg_width/2)/(ai_wheel_hollow_external_diameter/2))
#    wh_leg_top_angle2 = math.asin(float(ai_wheel_hollow_leg_width)/ai_wheel_hollow_external_diameter)
#    #wh_leg_bottom_angle2 = math.asin((ai_wheel_hollow_leg_width/2)/(ai_wheel_hollow_internal_diameter/2))
#    wh_leg_bottom_angle2 = math.asin(float(ai_wheel_hollow_leg_width)/ai_wheel_hollow_internal_diameter)
#    # angular coordinates of the points
#    wh_top1_a = ai_wheel_hollow_leg_angle+wh_leg_top_angle2
#    wh_top2_a = ai_wheel_hollow_leg_angle+wh_angle/2.0
#    wh_top3_a = ai_wheel_hollow_leg_angle+wh_angle-wh_leg_top_angle2
#    wh_bottom1_a = ai_wheel_hollow_leg_angle+wh_leg_bottom_angle2
#    wh_bottom2_a = ai_wheel_hollow_leg_angle+wh_angle/2.0
#    wh_bottom3_a = ai_wheel_hollow_leg_angle+wh_angle-wh_leg_bottom_angle2
#    # Cartesian coordinates of the points
#    wh_top1_x = g1_ix + ai_wheel_hollow_external_diameter/2.0*math.cos(wh_top1_a)
#    wh_top1_y = g1_iy + ai_wheel_hollow_external_diameter/2.0*math.sin(wh_top1_a)
#    wh_top2_x = g1_ix + ai_wheel_hollow_external_diameter/2.0*math.cos(wh_top2_a)
#    wh_top2_y = g1_iy + ai_wheel_hollow_external_diameter/2.0*math.sin(wh_top2_a)
#    wh_top3_x = g1_ix + ai_wheel_hollow_external_diameter/2.0*math.cos(wh_top3_a)
#    wh_top3_y = g1_iy + ai_wheel_hollow_external_diameter/2.0*math.sin(wh_top3_a)
#    wh_bottom1_x = g1_ix + ai_wheel_hollow_internal_diameter/2.0*math.cos(wh_bottom1_a)
#    wh_bottom1_y = g1_iy + ai_wheel_hollow_internal_diameter/2.0*math.sin(wh_bottom1_a)
#    wh_bottom2_x = g1_ix + ai_wheel_hollow_internal_diameter/2.0*math.cos(wh_bottom2_a)
#    wh_bottom2_y = g1_iy + ai_wheel_hollow_internal_diameter/2.0*math.sin(wh_bottom2_a)
#    wh_bottom3_x = g1_ix + ai_wheel_hollow_internal_diameter/2.0*math.cos(wh_bottom3_a)
#    wh_bottom3_y = g1_iy + ai_wheel_hollow_internal_diameter/2.0*math.sin(wh_bottom3_a)
#    # create one outline
#    if(wh_angle<2*wh_leg_bottom_angle1+radian_epsilon):
#      wh_outline_A = [
#        [wh_top1_x, wh_top1_y, wheel_hollow_router_bit_radius],
#        [wh_top2_x, wh_top2_y, wh_top3_x, wh_top3_y, wheel_hollow_router_bit_radius],
#        [wh_bottom2_x, wh_bottom2_y, wheel_hollow_router_bit_radius]]
#    else:
#      wh_outline_A = [
#        [wh_top1_x, wh_top1_y, wheel_hollow_router_bit_radius],
#        [wh_top2_x, wh_top2_y, wh_top3_x, wh_top3_y, wheel_hollow_router_bit_radius],
#        [wh_bottom3_x, wh_bottom3_y, wheel_hollow_router_bit_radius],
#        [wh_bottom2_x, wh_bottom2_y, wh_bottom1_x, wh_bottom1_y, wheel_hollow_router_bit_radius]]
#    wh_outline_A = cnc25d_api.outline_close(wh_outline_A)
#    wh_outline_B = cnc25d_api.cnc_cut_outline(wh_outline_A, "wheel_hollow")
#    wh_outline_B_ideal = cnc25d_api.ideal_outline(wh_outline_A, "wheel_hollow")
#    for i in range(ai_wheel_hollow_leg_number):
#      wheel_hollow_figure.append(cnc25d_api.outline_rotate(wh_outline_B, g1_ix, g1_iy, i*wh_angle))
#      wheel_hollow_figure_overlay.append(cnc25d_api.outline_rotate(wh_outline_B_ideal, g1_ix, g1_iy, i*wh_angle))
#
#  ### design output
#  gw_figure = [gear_profile_B]
#  gw_figure.extend(axle_figure)
#  gw_figure.extend(wheel_hollow_figure)
#  # ideal_outline in overlay
#  gw_figure_overlay = []
#  gw_figure_overlay.extend(axle_figure_overlay)
#  gw_figure_overlay.extend(wheel_hollow_figure_overlay)
#  # gearwheel_parameter_info
#  gearwheel_parameter_info = "\nGearwheel parameter info:\n"
#  gearwheel_parameter_info += "\n" + ai_args_in_txt + "\n\n"
#  gearwheel_parameter_info += gear_profile_info
#  gearwheel_parameter_info += """
#axle_type:    \t{:s}
#axle_x_width: \t{:0.3f}
#axle_y_width: \t{:0.3f}
#""".format(ai_axle_type, ai_axle_x_width, ai_axle_y_width)
#  gearwheel_parameter_info += """
#wheel_hollow_leg_number:          \t{:d}
#wheel_hollow_leg_width:           \t{:0.3f}
#wheel_hollow_external_diameter:   \t{:0.3f}
#wheel_hollow_internal_diameter:   \t{:0.3f}
#wheel_hollow_leg_angle:           \t{:0.3f}
#""".format(ai_wheel_hollow_leg_number, ai_wheel_hollow_leg_width, ai_wheel_hollow_external_diameter, ai_wheel_hollow_internal_diameter, ai_wheel_hollow_leg_angle)
#  gearwheel_parameter_info += """
#gear_router_bit_radius:         \t{:0.3f}
#wheel_hollow_router_bit_radius: \t{:0.3f}
#axle_router_bit_radius:         \t{:0.3f}
#cnc_router_bit_radius:          \t{:0.3f}
#""".format(gear_router_bit_radius, wheel_hollow_router_bit_radius, axle_router_bit_radius, ai_cnc_router_bit_radius)
#  #print(gearwheel_parameter_info)
#
#  # display with Tkinter
#  if(ai_tkinter_view):
#    print(gearwheel_parameter_info)
#    cnc25d_api.figure_simple_display(gw_figure, gw_figure_overlay, gearwheel_parameter_info)
#  # generate output file
#  cnc25d_api.generate_output_file(gw_figure, ai_output_file_basename, ai_gear_profile_height, gearwheel_parameter_info)

  ### return the gearwheel as FreeCAD Part object
  #r_gw = cnc25d_api.figure_to_freecad_25d_part(gw_figure, ai_gear_profile_height)
  r_gw = 1 # this is to spare the freecad computation time during debuging
  return(r_gw)

################################################################
# split_gearwheel wrapper dance
################################################################

def split_gearwheel_argparse_to_dictionary(ai_sgw_args):
  """ convert a split_gearwheel_argparse into a split_gearwheel_dictionary
  """
  r_sgwd = {}
  r_sgwd.update(gear_profile.gear_profile_argparse_to_dictionary(ai_sgw_args, 1))
  ### split
  r_sgwd['split_nb']                 = ai_sgw_args.sw_split_nb
  r_sgwd['split_initial_angle']      = ai_sgw_args.sw_split_initial_angle
  r_sgwd['low_split_diameter']       = ai_sgw_args.sw_low_split_diameter
  r_sgwd['low_split_type']           = ai_sgw_args.sw_low_split_type
  r_sgwd['high_split_diameter']      = ai_sgw_args.sw_high_split_diameter
  r_sgwd['high_split_type']          = ai_sgw_args.sw_high_split_type
  r_sgwd['split_router_bit_radius']  = ai_sgw_args.sw_split_router_bit_radius
  ### low-holes
  r_sgwd['low_hole_circle_diameter']   = ai_sgw_args.sw_low_hole_circle_diameter
  r_sgwd['low_hole_diameter']          = ai_sgw_args.sw_low_hole_diameter
  r_sgwd['low_hole_nb']                = ai_sgw_args.sw_low_hole_nb
  ### high-holes
  r_sgwd['high_hole_circle_diameter']  = ai_sgw_args.sw_high_hole_circle_diameter
  r_sgwd['high_hole_diameter']         = ai_sgw_args.sw_high_hole_diameter
  r_sgwd['high_hole_nb']               = ai_sgw_args.sw_high_hole_nb
  ### cnc router_bit constraint
  r_sgwd['cnc_router_bit_radius']      = ai_sgw_args.sw_cnc_router_bit_radius
  ### view the split_gearwheel with tkinter
  #r_sgwd['tkinter_view'] = tkinter_view
  r_sgwd['output_file_basename'] = ai_sgw_args.sw_output_file_basename
  ### optional
  #r_sgwd['args_in_txt'] = ai_args_in_txt
  #### return
  return(r_sgwd)
  
def split_gearwheel_argparse_wrapper(ai_sgw_args, ai_args_in_txt=""):
  """
  wrapper function of split_gearwheel() to call it using the split_gearwheel_parser.
  split_gearwheel_parser is mostly used for debug and non-regression tests.
  """
  # view the split_gearwheel with Tkinter as default action
  tkinter_view = True
  if(ai_sgw_args.sw_simulation_enable or (ai_sgw_args.sw_output_file_basename!='')):
    tkinter_view = False
  # wrapper
  sgwd = split_gearwheel_argparse_to_dictionary(ai_sgw_args)
  sgwd['args_in_txt'] = ai_args_in_txt
  sgwd['tkinter_view'] = tkinter_view

  r_sgw = split_gearwheel(sgwd)
  return(r_sgw)

################################################################
# self test
################################################################

def split_gearwheel_self_test():
  """
  This is the non-regression test of split_gearwheel.
  Look at the simulation Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"                  , "--gear_tooth_nb 21 --gear_module 10.0 --axle_type rectangle --axle_x_width 30 --axle_y_width 40 --axle_router_bit_radius 8.0 --cnc_router_bit_radius 3.0"],
    ["with gearwheel hollow 1 leg"    , "--gear_tooth_nb 25 --gear_module 10.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 20 --axle_router_bit_radius 4.0 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 20.0 --wheel_hollow_leg_angle 0.9 --wheel_hollow_internal_diameter 60.0 --wheel_hollow_external_diameter 200.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gearwheel hollow 3 legs"   , "--gear_tooth_nb 24 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 3 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 40.0 --wheel_hollow_external_diameter 180.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gearwheel hollow 7 legs"   , "--gear_tooth_nb 23 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 7 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 30.0 --wheel_hollow_external_diameter 160.0 --wheel_hollow_router_bit_radius 15.0"],
    ["with gear_profile simulation"   , "--gear_tooth_nb 23 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 7 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 60.0 --wheel_hollow_external_diameter 160.0 --wheel_hollow_router_bit_radius 15.0 --second_gear_tooth_nb 18 --simulation"],
    ["with gear_profile simulation"   , "--gear_tooth_nb 23 --gear_module 10.0 --axle_type circle --axle_x_width 20 --cnc_router_bit_radius 3.0 --wheel_hollow_leg_number 7 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 60.0 --wheel_hollow_external_diameter 160.0 --wheel_hollow_router_bit_radius 15.0 --second_gear_tooth_nb 18 --output_file_basename test_output/gearwheel_self_test.dxf"],
    ["no tooth"                       , "--gear_tooth_nb 0 --gear_primitive_diameter 100.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 20 --axle_router_bit_radius 3.0 --wheel_hollow_leg_number 4 --wheel_hollow_leg_width 10.0 --wheel_hollow_internal_diameter 40.0  --wheel_hollow_external_diameter 80.0 --wheel_hollow_router_bit_radius 8.0"],
    ["last test"                      , "--gear_tooth_nb 30 --gear_module 10.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  split_gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function split_gearwheel().')
  split_gearwheel_parser = split_gearwheel_add_argument(split_gearwheel_parser)
  split_gearwheel_parser = cnc25d_api.generate_output_file_add_argument(split_gearwheel_parser)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = split_gearwheel_parser.parse_args(l_args)
    r_sgwst = split_gearwheel_argparse_wrapper(st_args)
  return(r_sgwst)

################################################################
# split_gearwheel command line interface
################################################################

def split_gearwheel_cli(ai_args=None):
  """ command line interface of split_gearwheel.py when it is used in standalone
  """
  # split_gearwheel parser
  split_gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function split_gearwheel().')
  split_gearwheel_parser = split_gearwheel_add_argument(split_gearwheel_parser)
  split_gearwheel_parser = cnc25d_api.generate_output_file_add_argument(split_gearwheel_parser)
  # switch for self_test
  split_gearwheel_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
  help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "split_gearwheel arguments: " + ' '.join(effective_args)
  sgw_args = split_gearwheel_parser.parse_args(effective_args)
  print("dbg111: start making split_gearwheel")
  if(sgw_args.sw_run_self_test):
    r_sgw = split_gearwheel_self_test()
  else:
    r_sgw = split_gearwheel_argparse_wrapper(sgw_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_sgw)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("split_gearwheel.py says hello!\n")
  #my_sgw = split_gearwheel_cli()
  my_sgw = split_gearwheel_cli("--gear_tooth_nb 17 --output_file_basename test_output/toto2".split())

