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
You can also simulate or view of the gearwheel and get a DXF, SVG or BRep or the gearwheel
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
# gearwheel argparse
################################################################

def gearwheel_add_argument(ai_parser):
  """
  Add arguments relative to the gearwheel in addition to the argument of gear_profile_add_argument()
  This function intends to be used by the gearwheel_cli, gearwheel_self_test
  """
  r_parser = ai_parser
  ### axle
  r_parser.add_argument('--axle_type','--at', action='store', default='none', dest='sw_axle_type',
    help="Select the type of axle for the first gearwheel. Possible values: 'none', 'circle' and 'rectangle'. Default: 'none'")
  r_parser.add_argument('--axle_x_width','--axw', action='store', type=float, default=10.0, dest='sw_axle_x_width',
    help="Set the axle cylinder diameter or the axle rectangle x-width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--axle_y_width','--ayw', action='store', type=float, default=10.0, dest='sw_axle_y_width',
    help="Set the axle rectangle y-width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--axle_router_bit_radius','--arr', action='store', type=float, default=1.0, dest='sw_axle_router_bit_radius',
    help="Set the router_bit radius of the first gearwheel rectangle axle. Default: 1.0")
  ### wheel-hollow = legs
  r_parser.add_argument('--wheel_hollow_leg_number','--whln', action='store', type=int, default=0, dest='sw_wheel_hollow_leg_number',
    help="Set the number of legs for the wheel-hollow of the first gearwheel. The legs are uniform distributed. The first leg is centered on the leg_angle. 0 means no wheel-hollow  Default: 0")
  r_parser.add_argument('--wheel_hollow_leg_width','--whlw', action='store', type=float, default=10.0, dest='sw_wheel_hollow_leg_width',
    help="Set the wheel-hollow leg width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--wheel_hollow_leg_angle','--whla', action='store', type=float, default=0.0, dest='sw_wheel_hollow_leg_angle',
    help="Set the wheel-hollow leg-angle of the first gearwheel. Default: 0.0")
  r_parser.add_argument('--wheel_hollow_internal_diameter','--whid', action='store', type=float, default=20.0, dest='sw_wheel_hollow_internal_diameter',
    help="Set the wheel-hollow internal diameter of the first gearwheel. Default: 20.0")
  r_parser.add_argument('--wheel_hollow_external_diameter','--whed', action='store', type=float, default=30.0, dest='sw_wheel_hollow_external_diameter',
    help="Set the wheel-hollow external diameter of the first gearwheel. It must be bigger than the wheel_hollow_internal_diameter and smaller than the gear bottom diameter. Default: 30.0")
  r_parser.add_argument('--wheel_hollow_router_bit_radius','--whrr', action='store', type=float, default=1.0, dest='sw_wheel_hollow_router_bit_radius',
    help="Set the router_bit radius of the wheel-hollow of the first gearwheel. Default: 1.0")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=1.0, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the first gearwheel. It increases gear_router_bit_radius, axle_router_bit_radius and wheel_hollow_router_bit_radius if needed. Default: 1.0")
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def gearwheel(
      ##### from gear_profile
      ### first gear
      # general
      #ai_gear_type = 'e',
      ai_gear_tooth_nb = 0,
      ai_gear_module = 0.0,
      ai_gear_primitive_diameter = 0.0,
      ai_gear_addendum_dedendum_parity = 50.0,
      # tooth height
      ai_gear_tooth_half_height = 0.0,
      ai_gear_addendum_height_pourcentage = 100.0,
      ai_gear_dedendum_height_pourcentage = 100.0,
      ai_gear_hollow_height_pourcentage = 25.0,
      ai_gear_router_bit_radius = 0.1,
      # positive involute
      ai_gear_base_diameter = 0.0,
      ai_gear_force_angle = 0.0,
      ai_gear_tooth_resolution = 3,
      ai_gear_skin_thickness = 0.0,
      # negative involute (if zero, negative involute = positive involute)
      ai_gear_base_diameter_n = 0.0,
      ai_gear_force_angle_n = 0.0,
      ai_gear_tooth_resolution_n = 0,
      ai_gear_skin_thickness_n = 0.0,
      ### second gear
      # general
      ai_second_gear_type = 'e',
      ai_second_gear_tooth_nb = 0,
      ai_second_gear_primitive_diameter = 0.0,
      ai_second_gear_addendum_dedendum_parity = 0.0,
      # tooth height
      ai_second_gear_tooth_half_height = 0.0,
      ai_second_gear_addendum_height_pourcentage = 100.0,
      ai_second_gear_dedendum_height_pourcentage = 100.0,
      ai_second_gear_hollow_height_pourcentage = 25.0,
      ai_second_gear_router_bit_radius = 0.0,
      # positive involute
      ai_second_gear_base_diameter = 0.0,
      ai_second_gear_tooth_resolution = 0,
      ai_second_gear_skin_thickness = 0.0,
      # negative involute (if zero, negative involute = positive involute)
      ai_second_gear_base_diameter_n = 0.0,
      ai_second_gear_tooth_resolution_n = 0,
      ai_second_gear_skin_thickness_n = 0.0,
      ### gearbar specific
      ai_gearbar_slope = 0.0,
      ai_gearbar_slope_n = 0.0,
      ### position
      # first gear position
      ai_center_position_x = 0.0,
      ai_center_position_y = 0.0,
      ai_gear_initial_angle = 0.0,
      # second gear position
      ai_second_gear_position_angle = 0.0,
      ai_second_gear_additional_axis_length = 0.0,
      ### portion
      #ai_portion_tooth_nb = 0,
      #ai_portion_first_end = 0,
      #ai_portion_last_end =0,
      ### output
      ai_gear_profile_height = 1.0,
      ai_simulation_enable = False,
      #ai_output_file_basename = '',
      ##### from gearwheel
      ### axle
      ai_axle_type                = 'circle',
      ai_axle_x_width             = 10.0,
      ai_axle_y_width             = 10.0,
      ai_axle_router_bit_radius   = 1.0,
      ### wheel-hollow = legs
      ai_wheel_hollow_leg_number        = 0,
      ai_wheel_hollow_leg_width         = 10.0,
      ai_wheel_hollow_leg_angle         = 0.0,
      ai_wheel_hollow_internal_diameter = 20.0,
      ai_wheel_hollow_external_diameter = 30.0,
      ai_wheel_hollow_router_bit_radius = 1.0,
      ### cnc router_bit constraint
      ai_cnc_router_bit_radius          = '1.0',
      ### view the gearwheel with tkinter
      ai_tkinter_view = False,
      ai_output_file_basename = ''):
  """
  The main function of the script.
  It generates a gearwheel according to the function arguments
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  # get the router_bit_radius
  gear_router_bit_radius = ai_gear_router_bit_radius
  if(ai_cnc_router_bit_radius>gear_router_bit_radius):
    gear_router_bit_radius = ai_cnc_router_bit_radius
  wheel_hollow_router_bit_radius = ai_wheel_hollow_router_bit_radius
  if(ai_cnc_router_bit_radius>wheel_hollow_router_bit_radius):
    wheel_hollow_router_bit_radius = ai_cnc_router_bit_radius
  axle_router_bit_radius = ai_axle_router_bit_radius
  if(ai_cnc_router_bit_radius>axle_router_bit_radius):
    axle_router_bit_radius = ai_cnc_router_bit_radius
  # ai_axle_type
  if(not ai_axle_type in ('none', 'circle', 'rectangle')):
    print("ERR932: Error, ai_axle_type {:s} is not valid!".format(ai_axle_type))
    sys.exit(2)
  # ai_axle_x_width
  axle_diameter = 0
  if(ai_axle_type in('circle','rectangle')):
    if(ai_axle_x_width<2*axle_router_bit_radius+radian_epsilon):
      print("ERR663: Error, ai_axle_x_width {:0.2f} is too small compare to axle_router_bit_radius {:0.2f}!".format(ai_axle_x_width, axle_router_bit_radius))
      sys.exit(2)
    axle_diameter = ai_axle_x_width
    # ai_axle_y_width
    if(ai_axle_type=='rectangle'):
      if(ai_axle_y_width<2*axle_router_bit_radius+radian_epsilon):
        print("ERR664: Error, ai_axle_y_width {:0.2f} is too small compare to axle_router_bit_radius {:0.2f}!".format(ai_axle_y_width, axle_router_bit_radius))
        sys.exit(2)
      axle_diameter = math.sqrt(ai_axle_x_width**2+ai_axle_y_width**2)
  # ai_gear_tooth_nb
  if(ai_gear_tooth_nb>0): # create a gear_profile
    ### get the gear_profile
    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile(
      ### first gear
      # general
      ai_gear_type                      = 'e',
      ai_gear_tooth_nb                  = ai_gear_tooth_nb,
      ai_gear_module                    = ai_gear_module,
      ai_gear_primitive_diameter        = ai_gear_primitive_diameter,
      ai_gear_addendum_dedendum_parity  = ai_gear_addendum_dedendum_parity,
      # tooth height
      ai_gear_tooth_half_height           = ai_gear_tooth_half_height,
      ai_gear_addendum_height_pourcentage = ai_gear_addendum_height_pourcentage,
      ai_gear_dedendum_height_pourcentage = ai_gear_dedendum_height_pourcentage,
      ai_gear_hollow_height_pourcentage   = ai_gear_hollow_height_pourcentage,
      ai_gear_router_bit_radius           = ai_gear_router_bit_radius,
      # positive involute
      ai_gear_base_diameter       = ai_gear_base_diameter,
      ai_gear_force_angle         = ai_gear_force_angle,
      ai_gear_tooth_resolution    = ai_gear_tooth_resolution,
      ai_gear_skin_thickness      = ai_gear_skin_thickness,
      # negative involute (if zero, negative involute = positive involute)
      ai_gear_base_diameter_n     = ai_gear_base_diameter_n,
      ai_gear_force_angle_n       = ai_gear_force_angle_n,
      ai_gear_tooth_resolution_n  = ai_gear_tooth_resolution_n,
      ai_gear_skin_thickness_n    = ai_gear_skin_thickness_n,
      ### second gear
      # general
      ai_second_gear_type                     = ai_second_gear_type,
      ai_second_gear_tooth_nb                 = ai_second_gear_tooth_nb,
      ai_second_gear_primitive_diameter       = ai_second_gear_primitive_diameter,
      ai_second_gear_addendum_dedendum_parity = ai_second_gear_addendum_dedendum_parity,
      # tooth height
      ai_second_gear_tooth_half_height            = ai_second_gear_tooth_half_height,
      ai_second_gear_addendum_height_pourcentage  = ai_second_gear_addendum_height_pourcentage,
      ai_second_gear_dedendum_height_pourcentage  = ai_second_gear_dedendum_height_pourcentage,
      ai_second_gear_hollow_height_pourcentage    = ai_second_gear_hollow_height_pourcentage,
      ai_second_gear_router_bit_radius            = ai_second_gear_router_bit_radius,
      # positive involute
      ai_second_gear_base_diameter      = ai_second_gear_base_diameter,
      ai_second_gear_tooth_resolution   = ai_second_gear_tooth_resolution,
      ai_second_gear_skin_thickness     = ai_second_gear_skin_thickness,
      # negative involute (if zero, negative involute = positive involute)
      ai_second_gear_base_diameter_n    = ai_second_gear_base_diameter_n,
      ai_second_gear_tooth_resolution_n = ai_second_gear_tooth_resolution_n,
      ai_second_gear_skin_thickness_n   = ai_second_gear_skin_thickness_n,
      ### gearbar specific
      ai_gearbar_slope                  = ai_gearbar_slope,
      ai_gearbar_slope_n                = ai_gearbar_slope_n,
      ### position
      # first gear position
      ai_center_position_x                    = ai_center_position_x,
      ai_center_position_y                    = ai_center_position_y,
      ai_gear_initial_angle                   = ai_gear_initial_angle,
      # second gear position
      ai_second_gear_position_angle           = ai_second_gear_position_angle,
      ai_second_gear_additional_axis_length   = ai_second_gear_additional_axis_length,
      ### portion
      ai_portion_tooth_nb     = 0,
      ai_portion_first_end    = 0,
      ai_portion_last_end     = 0,
      ### output
      ai_gear_profile_height  = ai_gear_profile_height,
      ai_simulation_enable    = ai_simulation_enable,    # ai_simulation_enable,
      ai_output_file_basename = '')
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    minimal_gear_profile_radius = gear_profile_parameters['hollow_radius']
    g1_ix = gear_profile_parameters['center_ox']
    g1_iy = gear_profile_parameters['center_oy']
  else: # no gear_profile, just a circle
    if(ai_gear_primitive_diameter<radian_epsilon):
      print("ERR885: Error, the no-gear-profile circle outline diameter ai_gear_primitive_diameter {:0.2f} is too small!".format(ai_gear_primitive_diameter))
      sys.exit(2)
    g1_ix = ai_center_position_x
    g1_iy = ai_center_position_y
    gear_profile_B = (g1_ix, g1_iy, ai_gear_primitive_diameter/2)
    gear_profile_info = "\nSimple circle (no-gear-profile):\n"
    gear_profile_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(ai_gear_primitive_diameter/2, ai_gear_primitive_diameter)
    gear_profile_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(g1_ix, g1_iy)
    minimal_gear_profile_radius = ai_gear_primitive_diameter/2
  ### check parameter coherence (part 2)
  if(ai_wheel_hollow_leg_number>0):
    # wheel_hollow_external_diameter
    if(ai_wheel_hollow_external_diameter > 2*minimal_gear_profile_radius-radian_epsilon):
      print("ERR733: Error, ai_wheel_hollow_external_diameter {:0.2f} is bigger than the gear_hollow_radius {:0.2f}!".format(ai_wheel_hollow_external_diameter, minimal_gear_profile_radius))
      sys.exit(2)
    if(ai_wheel_hollow_external_diameter < ai_wheel_hollow_internal_diameter+4*wheel_hollow_router_bit_radius):
      print("ERR734: Error, ai_wheel_hollow_external_diameter {:0.2f} is too small compare to ai_wheel_hollow_internal_diameter {:0.2f} and wheel_hollow_router_bit_radius {:0.2f}!".format(ai_wheel_hollow_external_diameter, ai_wheel_hollow_internal_diameter, wheel_hollow_router_bit_radius))
      sys.exit(2)
    # wheel_hollow_leg_width
    if(ai_wheel_hollow_leg_width<radian_epsilon):
      print("ERR735: Error, ai_wheel_hollow_leg_width {:0.2f} is too small!".format(ai_wheel_hollow_leg_width))
      sys.exit(2)
    # wheel_hollow_internal_diameter
    if(ai_wheel_hollow_internal_diameter<axle_diameter+radian_epsilon):
      print("ERR736: Error, ai_wheel_hollow_internal_diameter {:0.2f} is too small compare to axle_diameter {:0.2f}!".format(ai_wheel_hollow_internal_diameter, axle_diameter))
      sys.exit(2)
    if(ai_wheel_hollow_internal_diameter<ai_wheel_hollow_leg_width+2*radian_epsilon):
      print("ERR736: Error, ai_wheel_hollow_internal_diameter {:0.2f} is too small compare to ai_wheel_hollow_leg_width {:0.2f}!".format(ai_wheel_hollow_internal_diameter, ai_wheel_hollow_leg_width))
      sys.exit(2)
  # 

  ### axle
  axle_figure = []
  axle_figure_overlay = []
  if(ai_axle_type=='circle'):
    axle_figure.append([g1_ix, g1_iy, axle_diameter/2])
  elif(ai_axle_type=='rectangle'):
    axle_A = [
      [g1_ix-ai_axle_x_width/2, g1_iy-ai_axle_y_width/2, -1*axle_router_bit_radius],
      [g1_ix+ai_axle_x_width/2, g1_iy-ai_axle_y_width/2, -1*axle_router_bit_radius],
      [g1_ix+ai_axle_x_width/2, g1_iy+ai_axle_y_width/2, -1*axle_router_bit_radius],
      [g1_ix-ai_axle_x_width/2, g1_iy+ai_axle_y_width/2, -1*axle_router_bit_radius]]
    axle_A = cnc25d_api.outline_close(axle_A)
    axle_figure.append(cnc25d_api.cnc_cut_outline(axle_A, "axle_A"))
    axle_figure_overlay.append(cnc25d_api.ideal_outline(axle_A, "axle_A"))

  ### wheel hollow (a.k.a legs)
  wheel_hollow_figure = []
  wheel_hollow_figure_overlay = []
  if(ai_wheel_hollow_leg_number>0):
    wh_angle = 2*math.pi/ai_wheel_hollow_leg_number
    wh_leg_top_angle1 = math.asin((ai_wheel_hollow_leg_width/2+wheel_hollow_router_bit_radius)/(ai_wheel_hollow_external_diameter/2-wheel_hollow_router_bit_radius))
    if(wh_angle<2*wh_leg_top_angle1+radian_epsilon):
      print("ERR664: Error, wh_angle {:0.2f} too small compare to wh_leg_top_angle {:0.2f}!".format(wh_angle, wh_leg_top_angle))
      sys.exit(2)
    wh_leg_bottom_angle1 = math.asin((ai_wheel_hollow_leg_width/2+wheel_hollow_router_bit_radius)/(ai_wheel_hollow_internal_diameter/2+wheel_hollow_router_bit_radius))
    #wh_leg_top_angle2 = math.asin((ai_wheel_hollow_leg_width/2)/(ai_wheel_hollow_external_diameter/2))
    wh_leg_top_angle2 = math.asin(ai_wheel_hollow_leg_width/ai_wheel_hollow_external_diameter)
    #wh_leg_bottom_angle2 = math.asin((ai_wheel_hollow_leg_width/2)/(ai_wheel_hollow_internal_diameter/2))
    wh_leg_bottom_angle2 = math.asin(ai_wheel_hollow_leg_width/ai_wheel_hollow_internal_diameter)
    # angular coordinates of the points
    wh_top1_a = ai_wheel_hollow_leg_angle+wh_leg_top_angle2
    wh_top2_a = ai_wheel_hollow_leg_angle+wh_angle/2
    wh_top3_a = ai_wheel_hollow_leg_angle+wh_angle-wh_leg_top_angle2
    wh_bottom1_a = ai_wheel_hollow_leg_angle+wh_leg_bottom_angle2
    wh_bottom2_a = ai_wheel_hollow_leg_angle+wh_angle/2
    wh_bottom3_a = ai_wheel_hollow_leg_angle+wh_angle-wh_leg_bottom_angle2
    # Cartesian coordinates of the points
    wh_top1_x = g1_ix + ai_wheel_hollow_external_diameter/2*math.cos(wh_top1_a)
    wh_top1_y = g1_iy + ai_wheel_hollow_external_diameter/2*math.sin(wh_top1_a)
    wh_top2_x = g1_ix + ai_wheel_hollow_external_diameter/2*math.cos(wh_top2_a)
    wh_top2_y = g1_iy + ai_wheel_hollow_external_diameter/2*math.sin(wh_top2_a)
    wh_top3_x = g1_ix + ai_wheel_hollow_external_diameter/2*math.cos(wh_top3_a)
    wh_top3_y = g1_iy + ai_wheel_hollow_external_diameter/2*math.sin(wh_top3_a)
    wh_bottom1_x = g1_ix + ai_wheel_hollow_internal_diameter/2*math.cos(wh_bottom1_a)
    wh_bottom1_y = g1_iy + ai_wheel_hollow_internal_diameter/2*math.sin(wh_bottom1_a)
    wh_bottom2_x = g1_ix + ai_wheel_hollow_internal_diameter/2*math.cos(wh_bottom2_a)
    wh_bottom2_y = g1_iy + ai_wheel_hollow_internal_diameter/2*math.sin(wh_bottom2_a)
    wh_bottom3_x = g1_ix + ai_wheel_hollow_internal_diameter/2*math.cos(wh_bottom3_a)
    wh_bottom3_y = g1_iy + ai_wheel_hollow_internal_diameter/2*math.sin(wh_bottom3_a)
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
    for i in range(ai_wheel_hollow_leg_number):
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
  gearwheel_parameter_info += gear_profile_info
  gearwheel_parameter_info += """
axle_type:    \t{:s}
axle_x_width: \t{:0.3f}
axle_y_width: \t{:0.3f}
""".format(ai_axle_type, ai_axle_x_width, ai_axle_y_width)
  gearwheel_parameter_info += """
wheel_hollow_leg_number:          \t{:d}
wheel_hollow_leg_width:           \t{:0.3f}
wheel_hollow_external_diameter:   \t{:0.3f}
wheel_hollow_internal_diameter:   \t{:0.3f}
wheel_hollow_leg_angle:           \t{:0.3f}
""".format(ai_wheel_hollow_leg_number, ai_wheel_hollow_leg_width, ai_wheel_hollow_external_diameter, ai_wheel_hollow_internal_diameter, ai_wheel_hollow_leg_angle)
  gearwheel_parameter_info += """
gear_router_bit_radius:         \t{:0.3f}
wheel_hollow_router_bit_radius: \t{:0.3f}
axle_router_bit_radius:         \t{:0.3f}
cnc_router_bit_radius:          \t{:0.3f}
""".format(gear_router_bit_radius, wheel_hollow_router_bit_radius, axle_router_bit_radius, ai_gear_router_bit_radius)
  #print(gearwheel_parameter_info)

  # display with Tkinter
  if(ai_tkinter_view):
    print(gearwheel_parameter_info)
    cnc25d_api.figure_simple_display(gw_figure, gw_figure_overlay, gearwheel_parameter_info)
  # generate output file
  cnc25d_api.generate_output_file(gw_figure, ai_output_file_basename, ai_gear_profile_height, gearwheel_parameter_info)

  ### return the gearwheel as FreeCAD Part object
  #r_gw = cnc25d_api.figure_to_freecad_25d_part(gw_figure, ai_gear_profile_height)
  r_gw = 1 # this is to spare the freecad computation time during debuging
  return(r_gw)

################################################################
# gearwheel argparse_to_function
################################################################

def gearwheel_argparse_wrapper(ai_gw_args):
  """
  wrapper function of gearwheel() to call it using the gearwheel_parser.
  gearwheel_parser is mostly used for debug and non-regression tests.
  """
  # view the gearwheel with Tkinter as default action
  tkinter_view = True
  if(ai_gw_args.sw_simulation_enable or (ai_gw_args.sw_output_file_basename!='')):
    tkinter_view = False
  # wrapper
  r_gw = gearwheel(
           ##### from gear_profile
           ### first gear
           # general
           #ai_gear_type                      = ai_gw_args.sw_gear_type,
           ai_gear_tooth_nb                  = ai_gw_args.sw_gear_tooth_nb,
           ai_gear_module                    = ai_gw_args.sw_gear_module,
           ai_gear_primitive_diameter        = ai_gw_args.sw_gear_primitive_diameter,
           ai_gear_addendum_dedendum_parity  = ai_gw_args.sw_gear_addendum_dedendum_parity,
           # tooth height
           ai_gear_tooth_half_height           = ai_gw_args.sw_gear_tooth_half_height,
           ai_gear_addendum_height_pourcentage = ai_gw_args.sw_gear_addendum_height_pourcentage,
           ai_gear_dedendum_height_pourcentage = ai_gw_args.sw_gear_dedendum_height_pourcentage,
           ai_gear_hollow_height_pourcentage   = ai_gw_args.sw_gear_hollow_height_pourcentage,
           ai_gear_router_bit_radius           = ai_gw_args.sw_gear_router_bit_radius,
           # positive involute
           ai_gear_base_diameter       = ai_gw_args.sw_gear_base_diameter,
           ai_gear_force_angle         = ai_gw_args.sw_gear_force_angle,
           ai_gear_tooth_resolution    = ai_gw_args.sw_gear_tooth_resolution,
           ai_gear_skin_thickness      = ai_gw_args.sw_gear_skin_thickness,
           # negative involute (if zero, negative involute = positive involute)
           ai_gear_base_diameter_n     = ai_gw_args.sw_gear_base_diameter_n,
           ai_gear_force_angle_n       = ai_gw_args.sw_gear_force_angle_n,
           ai_gear_tooth_resolution_n  = ai_gw_args.sw_gear_tooth_resolution_n,
           ai_gear_skin_thickness_n    = ai_gw_args.sw_gear_skin_thickness_n,
           ### second gear
           # general
           ai_second_gear_type                     = ai_gw_args.sw_second_gear_type,
           ai_second_gear_tooth_nb                 = ai_gw_args.sw_second_gear_tooth_nb,
           ai_second_gear_primitive_diameter       = ai_gw_args.sw_second_gear_primitive_diameter,
           ai_second_gear_addendum_dedendum_parity = ai_gw_args.sw_second_gear_addendum_dedendum_parity,
           # tooth height
           ai_second_gear_tooth_half_height            = ai_gw_args.sw_second_gear_tooth_half_height,
           ai_second_gear_addendum_height_pourcentage  = ai_gw_args.sw_second_gear_addendum_height_pourcentage,
           ai_second_gear_dedendum_height_pourcentage  = ai_gw_args.sw_second_gear_dedendum_height_pourcentage,
           ai_second_gear_hollow_height_pourcentage    = ai_gw_args.sw_second_gear_hollow_height_pourcentage,
           ai_second_gear_router_bit_radius            = ai_gw_args.sw_second_gear_router_bit_radius,
           # positive involute
           ai_second_gear_base_diameter      = ai_gw_args.sw_second_gear_base_diameter,
           ai_second_gear_tooth_resolution   = ai_gw_args.sw_second_gear_tooth_resolution,
           ai_second_gear_skin_thickness     = ai_gw_args.sw_second_gear_skin_thickness,
           # negative involute (if zero, negative involute = positive involute)
           ai_second_gear_base_diameter_n    = ai_gw_args.sw_second_gear_base_diameter_n,
           ai_second_gear_tooth_resolution_n = ai_gw_args.sw_second_gear_tooth_resolution_n,
           ai_second_gear_skin_thickness_n   = ai_gw_args.sw_second_gear_skin_thickness_n,
           ### gearbar specific
           ai_gearbar_slope                  = ai_gw_args.sw_gearbar_slope,
           ai_gearbar_slope_n                = ai_gw_args.sw_gearbar_slope_n,
           ### position
           # first gear position
           ai_center_position_x                    = ai_gw_args.sw_center_position_x,
           ai_center_position_y                    = ai_gw_args.sw_center_position_y,
           ai_gear_initial_angle                   = ai_gw_args.sw_gear_initial_angle,
           # second gear position
           ai_second_gear_position_angle           = ai_gw_args.sw_second_gear_position_angle,
           ai_second_gear_additional_axis_length   = ai_gw_args.sw_second_gear_additional_axis_length,
           ### portion
           #ai_portion_tooth_nb     = ai_gw_args.sw_cut_portion[0],
           #ai_portion_first_end    = ai_gw_args.sw_cut_portion[1],
           #ai_portion_last_end     = ai_gw_args.sw_cut_portion[2],
           ### output
           ai_gear_profile_height  = ai_gw_args.sw_gear_profile_height,
           ai_simulation_enable    = ai_gw_args.sw_simulation_enable,    # ai_gw_args.sw_simulation_enable,
           #ai_output_file_basename = ai_gw_args.sw_output_file_basename,
           ##### from gearwheel
           ### axle
           ai_axle_type                = ai_gw_args.sw_axle_type,
           ai_axle_x_width             = ai_gw_args.sw_axle_x_width,
           ai_axle_y_width             = ai_gw_args.sw_axle_y_width,
           ai_axle_router_bit_radius   = ai_gw_args.sw_axle_router_bit_radius,
           ### wheel-hollow = legs
           ai_wheel_hollow_leg_number        = ai_gw_args.sw_wheel_hollow_leg_number,
           ai_wheel_hollow_leg_width         = ai_gw_args.sw_wheel_hollow_leg_width,
           ai_wheel_hollow_leg_angle         = ai_gw_args.sw_wheel_hollow_leg_angle,
           ai_wheel_hollow_internal_diameter = ai_gw_args.sw_wheel_hollow_internal_diameter,
           ai_wheel_hollow_external_diameter = ai_gw_args.sw_wheel_hollow_external_diameter,
           ai_wheel_hollow_router_bit_radius = ai_gw_args.sw_wheel_hollow_router_bit_radius,
           ### cnc router_bit constraint
           ai_cnc_router_bit_radius          = ai_gw_args.sw_cnc_router_bit_radius,
           ### design output : view the gearwheel with tkinter or write files
           ai_tkinter_view = tkinter_view,
           ai_output_file_basename = ai_gw_args.sw_output_file_basename)
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
    ["simplest test"                                    , ""],
    ["simplest test with simulation"                    , "--simulation_enable"],
    ["simple reduction (ratio<1)"                       , "--second_gear_tooth_nb 21 --simulation_enable"],
    ["simple transmission (ratio=1)"                    , "--gear_tooth_nb 13 --second_gear_tooth_nb 13 --simulation_enable"],
    ["simple multiplication (ratio>1)"                  , "--gear_tooth_nb 19 --second_gear_tooth_nb 16 --simulation_enable"],
    ["big ratio and zoom"                               , "--gear_tooth_nb 19 --second_gear_tooth_nb 137 --simulation_zoom 4.0 --simulation_enable"],
    ["single gear with same primitive and base circle"  , "--gear_tooth_nb 17 --gear_base_diameter 17.0 --simulation_enable"],
    ["single gear with small base circle"               , "--gear_tooth_nb 27 --gear_base_diameter 23.5 --simulation_enable"],
    ["with first and second angle and inter-axis length" , "--second_gear_tooth_nb 21 --gear_initial_angle {:f} --second_gear_position_angle {:f} --second_gear_additional_axis_length 0.2 --simulation_enable".format(15*math.pi/180, 40.0*math.pi/180)],
    ["other with first and second angle"                , "--second_gear_tooth_nb 15 --gear_initial_angle  {:f} --second_gear_position_angle  {:f} --simulation_enable".format(-5*math.pi/180, 170.0*math.pi/180)],
    ["with force angle constraint"                      , "--gear_tooth_nb 17 --second_gear_tooth_nb 27 --gear_force_angle {:f} --simulation_enable".format(20*math.pi/180)],
    ["first base radius constraint"                     , "--gear_tooth_nb 26 --second_gear_tooth_nb 23 --gear_base_diameter 23.0 --simulation_enable"],
    ["second base radius constraint"                    , "--second_gear_tooth_nb 23 --second_gear_primitive_diameter 20.3 --simulation_enable"],
    ["fine draw resolution"                             , "--second_gear_tooth_nb 19 --gear_tooth_resolution 10 --simulation_enable"],
    ["ratio 1 and dedendum at 30%%"                     , "--second_gear_tooth_nb 17 --gear_dedendum_height_pourcentage 30.0 --second_gear_addendum_height_pourcentage 30.0 --simulation_enable"],
    ["ratio > 1 and dedendum at 40%%"                   , "--second_gear_tooth_nb 23 --gear_dedendum_height_pourcentage 40.0 --second_gear_addendum_height_pourcentage 40.0 --simulation_enable"],
    ["ratio > 1 and addendum at 80%%"                   , "--second_gear_tooth_nb 17 --gear_addendum_height_pourcentage 80.0 --second_gear_dedendum_height_pourcentage 80.0 --simulation_enable"],
    ["ratio > 1 and dedendum at 160%%"                  , "--second_gear_tooth_nb 21 --gear_dedendum_height_pourcentage 160.0 --simulation_enable"],
    ["ratio > 1 and small tooth height"                 , "--second_gear_tooth_nb 29 --gear_tooth_half_height 1.3 --second_gear_tooth_half_height 1.3 --simulation_enable"],
    ["ratio > 1 and big tooth height"                   , "--second_gear_tooth_nb 29 --gear_tooth_half_height 2.3 --second_gear_tooth_half_height 2.3 --simulation_enable"],
    ["ratio > 1 and addendum-dedendum parity"           , "--gear_tooth_nb 30 --second_gear_tooth_nb 37 --gear_addendum_dedendum_parity 60.0 --second_gear_addendum_dedendum_parity 40.0 --simulation_enable"],
    ["file generation"                                  , "--center_position_x 100 --center_position_y 50 --output_file_basename self_test_output/"],
    ["interior gear"                                    , "--second_gear_tooth_nb 14 --gear_type ie --simulation_enable"],
    ["interior gear"                                    , "--gear_tooth_nb 25 --second_gear_tooth_nb 17 --gear_type ie --second_gear_position_angle {:f} --simulation_enable".format(30.0*math.pi/180)],
    ["interior second gear"                             , "--second_gear_tooth_nb 29 --gear_type ei --simulation_enable"],
    ["interior second gear"                             , "--second_gear_tooth_nb 24 --gear_type ei --second_gear_position_angle {:f} --simulation_enable".format(-75*math.pi/180)],
    ["interior gear"                                    , "--second_gear_tooth_nb 14 --gear_type ie --gear_addendum_height_pourcentage 75.0 --simulation_enable"],
    ["cremailliere"                                     , "--gear_type ce --gear_tooth_nb 3 --second_gear_tooth_nb 20 --gear_primitive_diameter 15 --gear_base_diameter 20 --simulation_enable"],
    ["cremailliere with angle"                          , "--gear_type ce --gear_tooth_nb 12 --second_gear_tooth_nb 20 --gear_primitive_diameter 40 --gear_base_diameter 20 --gear_initial_angle {:f} --simulation_enable".format(40*math.pi/180)]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function gear_profile().')
  gearwheel_parser = gear_profile.gear_profile_add_argument(gearwheel_parser, 1)
  gearwheel_parser = gearwheel_add_argument(gearwheel_parser)
  gearwheel_parser = cnc25d_api.generate_output_file_add_argument(gearwheel_parser)
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

def gearwheel_cli(ai_args=None):
  """ command line interface of gearwheel.py when it is used in standalone
  """
  # gearwheel parser
  gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function gearwheel().')
  gearwheel_parser = gear_profile.gear_profile_add_argument(gearwheel_parser, 1)
  gearwheel_parser = gearwheel_add_argument(gearwheel_parser)
  gearwheel_parser = cnc25d_api.generate_output_file_add_argument(gearwheel_parser)
  # switch for self_test
  gearwheel_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
  help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  gw_args = gearwheel_parser.parse_args(effective_args)
  print("dbg111: start making gearwheel")
  if(gw_args.sw_run_self_test):
    r_gw = gearwheel_self_test()
  else:
    r_gw = gearwheel_argparse_wrapper(gw_args)
  print("dbg999: end of script")
  return(r_gw)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearwheel.py says hello!\n")
  #my_gw = gearwheel_cli()
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --output_file_basename test_output/toto2".split())
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --axle_type rectangle --axle_x_width 20 --axle_y_width 30 --axle_router_bit_radius 5".split())
  my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0".split())
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename test_output/gearwheel_hat".split())
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0".split())
  #my_gw = gearwheel_cli("--gear_primitive_diameter 140.0 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0".split())
  #Part.show(my_gw)
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 5 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw1.svg".split())
  #my_gw = gearwheel_cli("--gear_primitive_diameter 140.0 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type rectangle --axle_x_width 20 --axle_y_width 25 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 3 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 120.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw2.svg".split())
  #my_gw = gearwheel_cli("--gear_tooth_nb 23 --gear_module 10 --gear_router_bit_radius 3.0 --axle_type circle --axle_x_width 20 --axle_router_bit_radius 5.0 --wheel_hollow_leg_number 1 --wheel_hollow_leg_width 8.0 --wheel_hollow_leg_angle 0.0 --wheel_hollow_internal_diameter 50.0 --wheel_hollow_external_diameter 180.0 --wheel_hollow_router_bit_radius 10.0 --gear_profile_height 15.0 --output_file_basename gw3.svg".split())


