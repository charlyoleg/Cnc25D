# gearbar.py
# generates gearbar and simulates gear.
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
gearbar.py is a parametric generator of gearbars.
The main function return the gear-bar as FreeCAD Part object.
You can also simulate or view of the gearbar and get a DXF, SVG or BRep file.
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
# gearbar argparse
################################################################

def gearbar_add_argument(ai_parser):
  """
  Add arguments relative to the gearbar in addition to the argument of gear_profile_add_argument()
  This function intends to be used by the gearbar_cli and gearbar_self_test
  """
  r_parser = ai_parser
  ### gearbar
  r_parser.add_argument('--gearbar_height','--gbh', action='store', type=float, default=20.0, dest='sw_gearbar_height',
    help="Set the height of the gearbar (from the bottom to the gear-profile primitive line). Default: 20.0")
  ### gearbar-hole
  r_parser.add_argument('--gearbar_hole_height_position','--gbhhp', action='store', type=float, default=10.0, dest='sw_gearbar_hole_height_position',
    help="Set the height from the bottom of the gearbar to the center of the gearbar-hole. Default: 10.0")
  r_parser.add_argument('--gearbar_hole_diameter','--gbhd', action='store', type=float, default=10.0, dest='sw_gearbar_hole_diameter',
    help="Set the diameter of the gearbar-hole. If equal to 0.0, there are no gearbar-hole. Default: 10.0")
  r_parser.add_argument('--gearbar_hole_offset','--gbho', action='store', type=int, default=0, dest='sw_gearbar_hole_offset',
    help="Set the initial number of teeth to position the first gearbar-hole. Default: 0")
  r_parser.add_argument('--gearbar_hole_increment','--gbhi', action='store', type=int, default=1, dest='sw_gearbar_hole_increment',
    help="Set the number of teeth between two gearbar-holes. Default: 1")
  # return
  return(r_parser)

################################################################
# sub-function
################################################################


################################################################
# the most important function to be used in other scripts
################################################################

def gearbar(
      ##### from gear_profile
      ### first gear
      # general
      #ai_gear_type = 'i',
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
      #ai_second_gear_type = 'e',
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
      ai_portion_tooth_nb = 0,
      ai_portion_first_end = 0,
      ai_portion_last_end =0,
      ### output
      ai_gear_profile_height = 1.0,
      ai_simulation_enable = False,
      #ai_output_file_basename = '',
      ##### from gearbar
      ### gearbar
      ai_gearbar_height                 = 20.0,
      ### gearbar-hole
      ai_gearbar_hole_height_position   = 10.0,
      ai_gearbar_hole_diameter          = 10.0,
      ai_gearbar_hole_offset            = 0,
      ai_gearbar_hole_increment         = 1,
      ### view the gearbar with tkinter
      ai_tkinter_view = False,
      ai_output_file_basename = '',
      ### optional
      ai_args_in_txt = ""):
  """
  The main function of the script.
  It generates a gearbar according to the function arguments
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  gearbar_hole_radius = float(ai_gearbar_hole_diameter)/2
  # ai_gearbar_hole_height_position
  if((ai_gearbar_hole_height_position+gearbar_hole_radius)>ai_gearbar_height):
    print("ERR215: Error, ai_gearbar_hole_height_position {:0.3} and gearbar_hole_radius {:0.3f} are too big compare to ai_gearbar_height {:0.3f} !".format(ai_gearbar_hole_height_position, gearbar_hole_radius, ai_gearbar_height))
    sys.exit(2)
  # ai_gear_tooth_nb
  if(ai_gear_tooth_nb>0): # create a gear_profile
    ### get the gear_profile
    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile(
      ### first gear
      # general
      ai_gear_type                      = 'l',
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
      ai_second_gear_type                     = 'e',
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
      ai_portion_tooth_nb     = ai_portion_tooth_nb,
      ai_portion_first_end    = ai_portion_first_end,
      ai_portion_last_end     = ai_portion_last_end,
      ### output
      ai_gear_profile_height  = ai_gear_profile_height,
      ai_simulation_enable    = ai_simulation_enable,    # ai_simulation_enable,
      ai_output_file_basename = '')
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    ## gear_profile_B rotation / translation transformation
    g1_ix = gear_profile_parameters['center_ox']
    g1_iy = gear_profile_parameters['center_oy']
    g1_inclination = gear_profile_parameters['gearbar_inclination']
    gear_profile_B = cnc25d_api.outline_rotate(gear_profile_B, g1_ix, g1_iy, -1*g1_inclination + math.pi/2)
    gear_profile_B = cnc25d_api.outline_shift_xy(gear_profile_B, -1*gear_profile_B[0][0], 1, -1*g1_iy + ai_gearbar_height, 1)
    ## get some parameters
    minimal_gear_profile_height = ai_gearbar_height - (gear_profile_parameters['hollow_height'] + gear_profile_parameters['dedendum_height'])
    gearbar_length = gear_profile_B[-1][0] - gear_profile_B[0][0]
    pi_module = gear_profile_parameters['pi_module']
    pfe = gear_profile_parameters['portion_first_end']
    full_positive_slope = gear_profile_parameters['full_positive_slope']
    full_negative_slope = gear_profile_parameters['full_negative_slope']
    bottom_land = gear_profile_parameters['bottom_land']
    top_land = gear_profile_parameters['top_land']
    if((top_land + full_positive_slope + bottom_land + full_negative_slope)!=pi_module):
      print("ERR269: Error with top_land {:0.3f}  full_positive_slope {:0.3f}  bottom_land {:0.3f}  full_negative_slope {:0.3f} and pi_module  {:0.3f}".format(top_land, full_positive_slope, bottom_land, full_negative_slope, pi_module))
      sys.exit(2)
    if(pfe==0):
      first_tooth_position = full_positive_slope + bottom_land + full_negative_slope + float(top_land)/2
    elif(pfe==1):
      first_tooth_position = full_positive_slope + bottom_land + full_negative_slope + top_land
    elif(pfe==2):
      first_tooth_position = full_negative_slope + float(top_land)/2
    elif(pfe==3):
      first_tooth_position = float(bottom_land)/2 + full_negative_slope + float(top_land)/2
  else: # no gear_profile, just a circle
    if(ai_gear_primitive_diameter<radian_epsilon):
      print("ERR885: Error, the no-gear-profile line outline length ai_gear_primitive_diameter {:0.2f} is too small!".format(ai_gear_primitive_diameter))
      sys.exit(2)
    #g1_ix = ai_center_position_x
    #g1_iy = ai_center_position_y
    gearbar_length = ai_gear_primitive_diameter
    gear_profile_B = [(0, ai_gearbar_height),(gearbar_length, ai_gearbar_height)]
    gear_profile_info = "\nSimple line (no-gear-profile):\n"
    gear_profile_info += "outline line length: \t{:0.3f}\n".format(gearbar_length)
    minimal_gear_profile_height = ai_gearbar_height
    pi_module = ai_gear_module * math.pi
    first_tooth_position = float(pi_module)/2

  ### check parameter coherence (part 2)
  # minimal_gear_profile_height
  if(minimal_gear_profile_height<radian_epsilon):
    print("ERR265: Error, minimal_gear_profile_height {:0.3f} is too small".format(minimal_gear_profile_height))
    sys.exit(2)
  # gearbar_hole_diameter
  if((ai_gearbar_hole_height_position+gearbar_hole_radius)>minimal_gear_profile_height):
    print("ERR269: Error, ai_gearbar_hole_height_position {:0.3f} and gearbar_hole_radius {:0.3f} are too big compare to minimal_gear_profile_height {:0.3f}".format(ai_gearbar_hole_height_position, gearbar_hole_radius, minimal_gear_profile_height))
    sys.exit(2)
  # pi_module
  if(gearbar_hole_radius>0):
    if(pi_module==0):
      print("ERR277: Error, pi_module is null. You might need to use --gear_module")
      sys.exit(2)

  ### gearbar outline
  gearbar_outline = gear_profile_B
  gearbar_outline.append((gearbar_outline[-1][0], 0))
  gearbar_outline.append((0, 0))
  gearbar_outline.append((0, gearbar_outline[0][1]))
  ### gearbar-hole figure
  gearbar_hole_figure = []
  if((gearbar_hole_radius>0)and(pi_module>0)):
    hole_x = first_tooth_position + ai_gearbar_hole_offset * pi_module
    while(hole_x<(gearbar_length-gearbar_hole_radius)):
      #print("dbg312: hole_x {:0.3f}".format(hole_x))
      gearbar_hole_figure.append([hole_x, ai_gearbar_hole_height_position, gearbar_hole_radius])
      hole_x += ai_gearbar_hole_increment * pi_module

  ### design output
  gb_figure = [gearbar_outline]
  gb_figure.extend(gearbar_hole_figure)
  # ideal_outline in overlay
  gb_figure_overlay = []
  # gearbar_parameter_info
  gearbar_parameter_info = "\nGearbar parameter info:\n"
  gearbar_parameter_info += "\n" + ai_args_in_txt + "\n\n"
  gearbar_parameter_info += gear_profile_info
  gearbar_parameter_info += """
gearbar_length: \t{:0.3f}
gearbar_height: \t{:0.3f}
minimal_gear_profile_height: \t{:0.3f}
""".format(gearbar_length, ai_gearbar_height, minimal_gear_profile_height)
  gearbar_parameter_info += """
gearbar_hole_height_position: \t{:0.3f}
gearbar_hole_diameter: \t{:0.3f}
gearbar_hole_offset: \t{:d}
gearbar_hole_increment: \t{:d}
pi_module: \t{:0.3f}
""".format(ai_gearbar_hole_height_position, ai_gearbar_hole_diameter, ai_gearbar_hole_offset, ai_gearbar_hole_increment, pi_module)
  #print(gearbar_parameter_info)

  # display with Tkinter
  if(ai_tkinter_view):
    print(gearbar_parameter_info)
    cnc25d_api.figure_simple_display(gb_figure, gb_figure_overlay, gearbar_parameter_info)
  # generate output file
  cnc25d_api.generate_output_file(gb_figure, ai_output_file_basename, ai_gear_profile_height, gearbar_parameter_info)

  ### return the gearbar as FreeCAD Part object
  #r_gb = cnc25d_api.figure_to_freecad_25d_part(gb_figure, ai_gear_profile_height)
  r_gb = 1 # this is to spare the freecad computation time during debuging
  return(r_gb)

################################################################
# gearbar argparse_to_function
################################################################

def gearbar_argparse_wrapper(ai_gb_args, ai_args_in_txt=""):
  """
  wrapper function of gearbar() to call it using the gearbar_parser.
  gearbar_parser is mostly used for debug and non-regression tests.
  """
  # view the gearbar with Tkinter as default action
  tkinter_view = True
  if(ai_gb_args.sw_simulation_enable or (ai_gb_args.sw_output_file_basename!='')):
    tkinter_view = False
  # wrapper
  r_gb = gearbar(
           ##### from gear_profile
           ### first gear
           # general
           #ai_gear_type                      = ai_gb_args.sw_gear_type,
           ai_gear_tooth_nb                  = ai_gb_args.sw_gear_tooth_nb,
           ai_gear_module                    = ai_gb_args.sw_gear_module,
           ai_gear_primitive_diameter        = ai_gb_args.sw_gear_primitive_diameter,
           ai_gear_addendum_dedendum_parity  = ai_gb_args.sw_gear_addendum_dedendum_parity,
           # tooth height
           ai_gear_tooth_half_height           = ai_gb_args.sw_gear_tooth_half_height,
           ai_gear_addendum_height_pourcentage = ai_gb_args.sw_gear_addendum_height_pourcentage,
           ai_gear_dedendum_height_pourcentage = ai_gb_args.sw_gear_dedendum_height_pourcentage,
           ai_gear_hollow_height_pourcentage   = ai_gb_args.sw_gear_hollow_height_pourcentage,
           ai_gear_router_bit_radius           = ai_gb_args.sw_gear_router_bit_radius,
           # positive involute
           ai_gear_base_diameter       = ai_gb_args.sw_gear_base_diameter,
           ai_gear_force_angle         = ai_gb_args.sw_gear_force_angle,
           ai_gear_tooth_resolution    = ai_gb_args.sw_gear_tooth_resolution,
           ai_gear_skin_thickness      = ai_gb_args.sw_gear_skin_thickness,
           # negative involute (if zero, negative involute = positive involute)
           ai_gear_base_diameter_n     = ai_gb_args.sw_gear_base_diameter_n,
           ai_gear_force_angle_n       = ai_gb_args.sw_gear_force_angle_n,
           ai_gear_tooth_resolution_n  = ai_gb_args.sw_gear_tooth_resolution_n,
           ai_gear_skin_thickness_n    = ai_gb_args.sw_gear_skin_thickness_n,
           ### second gear
           # general
           #ai_second_gear_type                     = ai_gb_args.sw_second_gear_type,
           ai_second_gear_tooth_nb                 = ai_gb_args.sw_second_gear_tooth_nb,
           ai_second_gear_primitive_diameter       = ai_gb_args.sw_second_gear_primitive_diameter,
           ai_second_gear_addendum_dedendum_parity = ai_gb_args.sw_second_gear_addendum_dedendum_parity,
           # tooth height
           ai_second_gear_tooth_half_height            = ai_gb_args.sw_second_gear_tooth_half_height,
           ai_second_gear_addendum_height_pourcentage  = ai_gb_args.sw_second_gear_addendum_height_pourcentage,
           ai_second_gear_dedendum_height_pourcentage  = ai_gb_args.sw_second_gear_dedendum_height_pourcentage,
           ai_second_gear_hollow_height_pourcentage    = ai_gb_args.sw_second_gear_hollow_height_pourcentage,
           ai_second_gear_router_bit_radius            = ai_gb_args.sw_second_gear_router_bit_radius,
           # positive involute
           ai_second_gear_base_diameter      = ai_gb_args.sw_second_gear_base_diameter,
           ai_second_gear_tooth_resolution   = ai_gb_args.sw_second_gear_tooth_resolution,
           ai_second_gear_skin_thickness     = ai_gb_args.sw_second_gear_skin_thickness,
           # negative involute (if zero, negative involute = positive involute)
           ai_second_gear_base_diameter_n    = ai_gb_args.sw_second_gear_base_diameter_n,
           ai_second_gear_tooth_resolution_n = ai_gb_args.sw_second_gear_tooth_resolution_n,
           ai_second_gear_skin_thickness_n   = ai_gb_args.sw_second_gear_skin_thickness_n,
           ### gearbar specific
           ai_gearbar_slope                  = ai_gb_args.sw_gearbar_slope,
           ai_gearbar_slope_n                = ai_gb_args.sw_gearbar_slope_n,
           ### position
           # first gear position
           ai_center_position_x                    = ai_gb_args.sw_center_position_x,
           ai_center_position_y                    = ai_gb_args.sw_center_position_y,
           ai_gear_initial_angle                   = ai_gb_args.sw_gear_initial_angle,
           # second gear position
           ai_second_gear_position_angle           = ai_gb_args.sw_second_gear_position_angle,
           ai_second_gear_additional_axis_length   = ai_gb_args.sw_second_gear_additional_axis_length,
           ### portion
           ai_portion_tooth_nb     = ai_gb_args.sw_cut_portion[0],
           ai_portion_first_end    = ai_gb_args.sw_cut_portion[1],
           ai_portion_last_end     = ai_gb_args.sw_cut_portion[2],
           ### output
           ai_gear_profile_height  = ai_gb_args.sw_gear_profile_height,
           ai_simulation_enable    = ai_gb_args.sw_simulation_enable,    # ai_gb_args.sw_simulation_enable,
           #ai_output_file_basename = ai_gb_args.sw_output_file_basename,
           ##### from gearbar
           ### gearbar
           ai_gearbar_height                = ai_gb_args.sw_gearbar_height,
           ### gearbar-hole
           ai_gearbar_hole_height_position  = ai_gb_args.sw_gearbar_hole_height_position,
           ai_gearbar_hole_diameter         = ai_gb_args.sw_gearbar_hole_diameter,
           ai_gearbar_hole_offset           = ai_gb_args.sw_gearbar_hole_offset,
           ai_gearbar_hole_increment        = ai_gb_args.sw_gearbar_hole_increment,
           ### design output : view the gearbar with tkinter or write files
           ai_tkinter_view = tkinter_view,
           ai_output_file_basename = ai_gb_args.sw_output_file_basename,
           ### optional
           ai_args_in_txt = ai_args_in_txt)
  return(r_gb)

################################################################
# self test
################################################################

def gearbar_self_test():
  """
  This is the non-regression test of gearbar.
  Look at the simulation Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"    , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0"],
    ["no tooth"         , "--gear_tooth_nb 0 --gear_primitive_diameter 500.0 --gearbar_height 30.0 --gearbar_hole_height_position 15.0 --gear_module 10.0"],
    ["no gearbar-hole"  , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --gearbar_hole_diameter 0"],
    ["ends 3 3"         , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --cut_portion 20 3 3"],
    ["ends 2 1"         , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --cut_portion 19 2 1"],
    ["ends 1 3"         , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --cut_portion 18 1 3"],
    [" gearbar-hole"    , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --cut_portion 17 3 3 --gearbar_hole_offset 1 --gearbar_hole_increment 3"],
    ["output dxf"       , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --output_file_basename test_output/gearbar_self_test.dxf"],
    ["last test"        , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  gearbar_parser = argparse.ArgumentParser(description='Command line interface for the function gearbar().')
  gearbar_parser = gear_profile.gear_profile_add_argument(gearbar_parser, 3)
  gearbar_parser = gearbar_add_argument(gearbar_parser)
  gearbar_parser = cnc25d_api.generate_output_file_add_argument(gearbar_parser)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = gearbar_parser.parse_args(l_args)
    r_gbst = gearbar_argparse_wrapper(st_args)
  return(r_gbst)

################################################################
# gearbar command line interface
################################################################

def gearbar_cli(ai_args=None):
  """ command line interface of gearbar.py when it is used in standalone
  """
  # gearbar parser
  gearbar_parser = argparse.ArgumentParser(description='Command line interface for the function gearbar().')
  gearbar_parser = gear_profile.gear_profile_add_argument(gearbar_parser, 3)
  gearbar_parser = gearbar_add_argument(gearbar_parser)
  gearbar_parser = cnc25d_api.generate_output_file_add_argument(gearbar_parser)
  # switch for self_test
  gearbar_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
  help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "gearbar arguments: " + ' '.join(effective_args)
  gb_args = gearbar_parser.parse_args(effective_args)
  print("dbg111: start making gearbar")
  if(gb_args.sw_run_self_test):
    r_gb = gearbar_self_test()
  else:
    r_gb = gearbar_argparse_wrapper(gb_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_gb)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearbar.py says hello!\n")
  #my_gb = gearbar_cli()
  my_gb = gearbar_cli("--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0".split())

