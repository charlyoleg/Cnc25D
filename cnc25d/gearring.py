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

################################################################
# gearring argparse
################################################################

def gearring_add_argument(ai_parser):
  """
  Add arguments relative to the gearring in addition to the argument of gear_profile_add_argument()
  This function intends to be used by the gearring_cli and gearring_self_test
  """
  r_parser = ai_parser
  ### holder
  r_parser.add_argument('--holder_diameter','--hd', action='store', type=float, default=0.0, dest='sw_holder_diameter',
    help="Set the holder diameter of the gearring. This is a mandatory input.")
  r_parser.add_argument('--holder_crenel_number','--hcn', action='store', type=int, default=6, dest='sw_holder_crenel_number',
    help="Set the number of holder crenels (associated with a hole) arround the gearring holder. Default: 6")
  r_parser.add_argument('--holder_position_angle','--hpa', action='store', type=float, default=0.0, dest='sw_holder_position_angle',
    help="Set the holder position angle of the first holder-crenel (associated with a hole). Default: 0.0")
  ### holder-hole
  r_parser.add_argument('--holder_hole_position_radius','--hhpr', action='store', type=float, default=0.0, dest='sw_holder_hole_position_radius',
    help="Set the length between the center of the holder-hole and the center of the gearring. If it is equal to 0.0, the holder_diameter value is used. Default: 0.0")
  r_parser.add_argument('--holder_hole_diameter','--hhd', action='store', type=float, default=10.0, dest='sw_holder_hole_diameter',
    help="Set the diameter of the holder-hole. If equal to 0.0, there are no holder-hole. Default: 10.0")
  ### holder-crenel
  r_parser.add_argument('--holder_crenel_position','--hcp', action='store', type=float, default=10.0, dest='sw_holder_crenel_position',
    help="Set the length between the center of the holder-hole and the bottom of the holder-crenel. Default: 10.0")
  r_parser.add_argument('--holder_crenel_height','--hch', action='store', type=float, default=10.0, dest='sw_holder_crenel_height',
    help="Set the height (or depth) of the holder-crenel. If equal to 0.0, no holder-crenels are made. Default: 10.0")
  r_parser.add_argument('--holder_crenel_width','--hcw', action='store', type=float, default=10.0, dest='sw_holder_crenel_width',
    help="Set the width of the holder-crenel. The outline of the bottom of the holder-crenel depends on the relative value between holder_crenel_width and holder_crenel_router_bit_radius. Default: 10.0")
  r_parser.add_argument('--holder_crenel_skin_width','--hcsw', action='store', type=float, default=10.0, dest='sw_holder_crenel_skin_width',
    help="Set the width (or thickness) of the skin (or side-wall) of the holder-crenel. It must be bigger than 0.0. Default: 10.0")
  r_parser.add_argument('--holder_crenel_router_bit_radius','--hcrbr', action='store', type=float, default=1.0, dest='sw_holder_crenel_router_bit_radius',
    help="Set the router_bit radius to make the holder-crenel. Default: 1.0")
  r_parser.add_argument('--holder_smoothing_radius','--hsr', action='store', type=float, default=0.0, dest='sw_holder_smoothing_radius',
    help="Set the router_bit radius to smooth the inner corner between the holder cylinder and the holder-crenel side-wall. If equal to 0.0, the value of holder_crenel_position is used. Default: 0.0")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=1.0, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the gearring. It increases gear_router_bit_radius, holder_crenel_router_bit_radius and holder_smoothing_radius if needed. Default: 1.0")
  # return
  return(r_parser)

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
  #holder_crenel.append([x0, y12, ai_holder_smoothing_radius])
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
  return(r_holder_crenel)

################################################################
# the most important function to be used in other scripts
################################################################

def gearring(
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
      #ai_gearbar_slope = 0.0,
      #ai_gearbar_slope_n = 0.0,
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
      ##### from gearring
      ### holder
      ai_holder_diameter            = 0.0,
      ai_holder_crenel_number       = 6,
      ai_holder_position_angle      = 0.0,
      ### holder-hole
      ai_holder_hole_position_radius   = 0.0,
      ai_holder_hole_diameter          = 10.0,
      ### holder-crenel
      ai_holder_crenel_position        = 10.0,
      ai_holder_crenel_height          = 10.0,
      ai_holder_crenel_width           = 10.0,
      ai_holder_crenel_skin_width      = 10.0,
      ai_holder_crenel_router_bit_radius   = 1.0,
      ai_holder_smoothing_radius       = 0.0,
      ### cnc router_bit constraint
      ai_cnc_router_bit_radius          = '1.0',
      ### view the gearring with tkinter
      ai_tkinter_view = False,
      ai_output_file_basename = '',
      ### optional
      ai_args_in_txt = ""):
  """
  The main function of the script.
  It generates a gearring according to the function arguments
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  holder_radius = float(ai_holder_diameter)/2
  holder_hole_position_radius = ai_holder_hole_position_radius
  if(holder_hole_position_radius==0):
    holder_hole_position_radius = holder_radius
  holder_hole_radius = float(ai_holder_hole_diameter)/2
  holder_maximal_radius = holder_hole_position_radius + ai_holder_crenel_position + ai_holder_crenel_height
  holder_maximal_height = holder_maximal_radius - holder_radius
  holder_crenel_half_width = float(ai_holder_crenel_width)/2
  holder_crenel_with_wall_half_width = holder_crenel_half_width + ai_holder_crenel_skin_width
  holder_crenel_half_angle = math.asin(float(holder_crenel_with_wall_half_width)/holder_radius)
  holder_crenel_x_position = math.sqrt((holder_radius)**2 - (holder_crenel_with_wall_half_width)**2)
  additional_holder_maximal_height = holder_radius - holder_crenel_x_position
  holder_maximal_height_plus = holder_maximal_height + additional_holder_maximal_height
  holder_side_outer_smoothing_radius = min(0.8*ai_holder_crenel_skin_width, float(holder_maximal_height_plus)/4)
  holder_side_straigth_length = holder_maximal_height_plus - holder_side_outer_smoothing_radius
  # get the router_bit_radius
  gear_router_bit_radius = ai_gear_router_bit_radius
  if(ai_cnc_router_bit_radius>gear_router_bit_radius):
    gear_router_bit_radius = ai_cnc_router_bit_radius
  holder_crenel_router_bit_radius = ai_holder_crenel_router_bit_radius
  if(ai_cnc_router_bit_radius>holder_crenel_router_bit_radius):
    holder_crenel_router_bit_radius = ai_cnc_router_bit_radius
  holder_smoothing_radius = ai_holder_smoothing_radius
  if(holder_smoothing_radius==0):
    holder_smoothing_radius = 0.9*holder_side_straigth_length
  if(ai_cnc_router_bit_radius>holder_smoothing_radius):
    holder_smoothing_radius = ai_cnc_router_bit_radius
  # ai_holder_crenel_height
  if(ai_holder_crenel_number>0):
    if((0.9*holder_side_straigth_length)<holder_smoothing_radius):
      print("ERR218: Error, the holder-crenel-wall-side height is too small: holder_side_straigth_length {:0.3f}  holder_smoothing_radius {:0.3f}".format(holder_side_straigth_length, holder_smoothing_radius))
      sys.exit(2)
  # ai_holder_crenel_position
  if(ai_holder_crenel_position<holder_hole_radius):
    print("ERR211: Error, ai_holder_crenel_position {:0.3f} is too small compare to holder_hole_radius {:03f}".format(ai_holder_crenel_position, holder_hole_radius))
    sys.exit(2)
  # ai_holder_crenel_width
  if(ai_holder_crenel_width<2.1*ai_holder_crenel_router_bit_radius):
    print("ERR215: Error, ai_holder_crenel_width {:0.3} is too small compare to ai_holder_crenel_router_bit_radius {:0.3f}".format(ai_holder_crenel_width, ai_holder_crenel_router_bit_radius))
    sys.exit(2)
  # ai_gear_tooth_nb
  if(ai_gear_tooth_nb>0): # create a gear_profile
    ### get the gear_profile
    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile(
      ### first gear
      # general
      ai_gear_type                      = 'i',
      ai_gear_tooth_nb                  = ai_gear_tooth_nb,
      ai_gear_module                    = ai_gear_module,
      ai_gear_primitive_diameter        = ai_gear_primitive_diameter,
      ai_gear_addendum_dedendum_parity  = ai_gear_addendum_dedendum_parity,
      # tooth height
      ai_gear_tooth_half_height           = ai_gear_tooth_half_height,
      ai_gear_addendum_height_pourcentage = ai_gear_addendum_height_pourcentage,
      ai_gear_dedendum_height_pourcentage = ai_gear_dedendum_height_pourcentage,
      ai_gear_hollow_height_pourcentage   = ai_gear_hollow_height_pourcentage,
      ai_gear_router_bit_radius           = gear_router_bit_radius,
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
      #ai_gearbar_slope                  = ai_gearbar_slope,
      #ai_gearbar_slope_n                = ai_gearbar_slope_n,
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
    maximal_gear_profile_radius = gear_profile_parameters['hollow_radius']
    g1_ix = gear_profile_parameters['center_ox']
    g1_iy = gear_profile_parameters['center_oy']
  else: # no gear_profile, just a circle
    if(ai_gear_primitive_diameter<radian_epsilon):
      print("ERR885: Error, the no-gear-profile circle outline diameter ai_gear_primitive_diameter {:0.2f} is too small!".format(ai_gear_primitive_diameter))
      sys.exit(2)
    g1_ix = ai_center_position_x
    g1_iy = ai_center_position_y
    gear_profile_B = (g1_ix, g1_iy, float(ai_gear_primitive_diameter)/2)
    gear_profile_info = "\nSimple circle (no-gear-profile):\n"
    gear_profile_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(ai_gear_primitive_diameter/2.0, ai_gear_primitive_diameter)
    gear_profile_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(g1_ix, g1_iy)
    maximal_gear_profile_radius = float(ai_gear_primitive_diameter)/2
  ### check parameter coherence (part 2)
  # hollow_circle and holder-hole
  if(maximal_gear_profile_radius>(holder_hole_position_radius-holder_hole_radius)):
    print("ERR303: Error, holder-hole are too closed from the gear_hollow_circle: maximal_gear_profile_radius {:0.3f}  holder_hole_position_radius {:0.3f}  holder_hole_radius {:0.3f}".format(maximal_gear_profile_radius, holder_hole_position_radius, holder_hole_radius))
    sys.exit(2)
  ### holder outline
  holder_figure = []
  holder_figure_overlay = []
  if(ai_holder_crenel_number==0):
    holder_figure.append([g1_ix, g1_iy, holder_radius])
  elif(ai_holder_crenel_number>0):
    angle_incr = 2*math.pi/ai_holder_crenel_number
    if((angle_incr-2*holder_crenel_half_angle)<math.pi/10):
      print("ERR369: Error, no enough space between the crenel: angle_incr {:0.3f}  holder_crenel_half_angle {:0.3f}".format(angle_incr, holder_crenel_half_angle))
      sys.exit(2)
    holder_A = []
    first_angle = ai_holder_position_angle - holder_crenel_half_angle
    holder_A.append([g1_ix+holder_radius*math.cos(first_angle), g1_iy+holder_radius*math.sin(first_angle), holder_smoothing_radius])
    for i in range(ai_holder_crenel_number):
      holder_A .extend(make_holder_crenel(holder_maximal_height_plus, ai_holder_crenel_height, ai_holder_crenel_skin_width, holder_crenel_half_width, 
                                          holder_crenel_router_bit_radius, holder_side_outer_smoothing_radius, holder_smoothing_radius,
                                          holder_crenel_x_position, ai_holder_position_angle+i*angle_incr, g1_ix, g1_iy))
      middle_angle = ai_holder_position_angle + (i+0.5)*angle_incr
      end_angle = ai_holder_position_angle + (i+1)*angle_incr - holder_crenel_half_angle
      holder_A.append([g1_ix+holder_radius*math.cos(middle_angle), g1_iy+holder_radius*math.sin(middle_angle),
                        g1_ix+holder_radius*math.cos(end_angle), g1_iy+holder_radius*math.sin(end_angle), holder_smoothing_radius])
    holder_A[-1][-1] = 0
    holder_figure.append(cnc25d_api.cnc_cut_outline(holder_A, "holder_A"))
    holder_figure_overlay.append(cnc25d_api.ideal_outline(holder_A, "holder_A"))
  ### holder-hole outline
  holder_hole_figure = []
  if((ai_holder_crenel_number>0)and(holder_hole_radius>0)):
    for i in range(ai_holder_crenel_number):
      hole_angle = ai_holder_position_angle+i*angle_incr
      holder_hole_figure.append([g1_ix+holder_hole_position_radius*math.cos(hole_angle), g1_iy+holder_hole_position_radius*math.sin(hole_angle), holder_hole_radius])

  ### design output
  gr_figure = [gear_profile_B]
  gr_figure.extend(holder_figure)
  gr_figure.extend(holder_hole_figure)
  # ideal_outline in overlay
  gr_figure_overlay = []
  gr_figure_overlay.extend(holder_figure_overlay)
  # gearring_parameter_info
  gearring_parameter_info = "\nGearring parameter info:\n"
  gearring_parameter_info += "\n" + ai_args_in_txt + "\n\n"
  gearring_parameter_info += gear_profile_info
  gearring_parameter_info += """
holder_diameter: \t{:0.3f}
holder_crenel_number: \t{:d}
holder_position_angle: \t{:0.3f}
""".format(ai_holder_diameter, ai_holder_crenel_number, ai_holder_position_angle)
  gearring_parameter_info += """
holder_hole_position_radius: \t{:0.3f}
holder_hole_diameter: \t{:0.3f}
""".format(holder_hole_position_radius, ai_holder_hole_diameter)
  gearring_parameter_info += """
holder_crenel_position: \t{:0.3f}
holder_crenel_height: \t{:0.3f}
holder_crenel_width: \t{:0.3f}
holder_crenel_skin_width: \t{:0.3f}
""".format(ai_holder_crenel_position, ai_holder_crenel_height, ai_holder_crenel_width, ai_holder_crenel_skin_width)
  gearring_parameter_info += """
gear_router_bit_radius:           \t{:0.3f}
holder_crenel_router_bit_radius:  \t{:0.3f}
holder_smoothing_radius:          \t{:0.3f}
cnc_router_bit_radius:            \t{:0.3f}
""".format(gear_router_bit_radius, ai_holder_crenel_router_bit_radius, holder_smoothing_radius, ai_cnc_router_bit_radius)
  #print(gearring_parameter_info)

  # display with Tkinter
  if(ai_tkinter_view):
    print(gearring_parameter_info)
    cnc25d_api.figure_simple_display(gr_figure, gr_figure_overlay, gearring_parameter_info)
  # generate output file
  cnc25d_api.generate_output_file(gr_figure, ai_output_file_basename, ai_gear_profile_height, gearring_parameter_info)

  ### return the gearring as FreeCAD Part object
  #r_gr = cnc25d_api.figure_to_freecad_25d_part(gr_figure, ai_gear_profile_height)
  r_gr = 1 # this is to spare the freecad computation time during debuging
  return(r_gr)

################################################################
# gearring argparse_to_function
################################################################

def gearring_argparse_wrapper(ai_gr_args, ai_args_in_txt=""):
  """
  wrapper function of gearring() to call it using the gearring_parser.
  gearring_parser is mostly used for debug and non-regression tests.
  """
  # view the gearring with Tkinter as default action
  tkinter_view = True
  if(ai_gr_args.sw_simulation_enable or (ai_gr_args.sw_output_file_basename!='')):
    tkinter_view = False
  # wrapper
  r_gr = gearring(
           ##### from gear_profile
           ### first gear
           # general
           #ai_gear_type                      = ai_gr_args.sw_gear_type,
           ai_gear_tooth_nb                  = ai_gr_args.sw_gear_tooth_nb,
           ai_gear_module                    = ai_gr_args.sw_gear_module,
           ai_gear_primitive_diameter        = ai_gr_args.sw_gear_primitive_diameter,
           ai_gear_addendum_dedendum_parity  = ai_gr_args.sw_gear_addendum_dedendum_parity,
           # tooth height
           ai_gear_tooth_half_height           = ai_gr_args.sw_gear_tooth_half_height,
           ai_gear_addendum_height_pourcentage = ai_gr_args.sw_gear_addendum_height_pourcentage,
           ai_gear_dedendum_height_pourcentage = ai_gr_args.sw_gear_dedendum_height_pourcentage,
           ai_gear_hollow_height_pourcentage   = ai_gr_args.sw_gear_hollow_height_pourcentage,
           ai_gear_router_bit_radius           = ai_gr_args.sw_gear_router_bit_radius,
           # positive involute
           ai_gear_base_diameter       = ai_gr_args.sw_gear_base_diameter,
           ai_gear_force_angle         = ai_gr_args.sw_gear_force_angle,
           ai_gear_tooth_resolution    = ai_gr_args.sw_gear_tooth_resolution,
           ai_gear_skin_thickness      = ai_gr_args.sw_gear_skin_thickness,
           # negative involute (if zero, negative involute = positive involute)
           ai_gear_base_diameter_n     = ai_gr_args.sw_gear_base_diameter_n,
           ai_gear_force_angle_n       = ai_gr_args.sw_gear_force_angle_n,
           ai_gear_tooth_resolution_n  = ai_gr_args.sw_gear_tooth_resolution_n,
           ai_gear_skin_thickness_n    = ai_gr_args.sw_gear_skin_thickness_n,
           ### second gear
           # general
           #ai_second_gear_type                     = ai_gr_args.sw_second_gear_type,
           ai_second_gear_tooth_nb                 = ai_gr_args.sw_second_gear_tooth_nb,
           ai_second_gear_primitive_diameter       = ai_gr_args.sw_second_gear_primitive_diameter,
           ai_second_gear_addendum_dedendum_parity = ai_gr_args.sw_second_gear_addendum_dedendum_parity,
           # tooth height
           ai_second_gear_tooth_half_height            = ai_gr_args.sw_second_gear_tooth_half_height,
           ai_second_gear_addendum_height_pourcentage  = ai_gr_args.sw_second_gear_addendum_height_pourcentage,
           ai_second_gear_dedendum_height_pourcentage  = ai_gr_args.sw_second_gear_dedendum_height_pourcentage,
           ai_second_gear_hollow_height_pourcentage    = ai_gr_args.sw_second_gear_hollow_height_pourcentage,
           ai_second_gear_router_bit_radius            = ai_gr_args.sw_second_gear_router_bit_radius,
           # positive involute
           ai_second_gear_base_diameter      = ai_gr_args.sw_second_gear_base_diameter,
           ai_second_gear_tooth_resolution   = ai_gr_args.sw_second_gear_tooth_resolution,
           ai_second_gear_skin_thickness     = ai_gr_args.sw_second_gear_skin_thickness,
           # negative involute (if zero, negative involute = positive involute)
           ai_second_gear_base_diameter_n    = ai_gr_args.sw_second_gear_base_diameter_n,
           ai_second_gear_tooth_resolution_n = ai_gr_args.sw_second_gear_tooth_resolution_n,
           ai_second_gear_skin_thickness_n   = ai_gr_args.sw_second_gear_skin_thickness_n,
           ### gearbar specific
           #ai_gearbar_slope                  = ai_gr_args.sw_gearbar_slope,
           #ai_gearbar_slope_n                = ai_gr_args.sw_gearbar_slope_n,
           ### position
           # first gear position
           ai_center_position_x                    = ai_gr_args.sw_center_position_x,
           ai_center_position_y                    = ai_gr_args.sw_center_position_y,
           ai_gear_initial_angle                   = ai_gr_args.sw_gear_initial_angle,
           # second gear position
           ai_second_gear_position_angle           = ai_gr_args.sw_second_gear_position_angle,
           ai_second_gear_additional_axis_length   = ai_gr_args.sw_second_gear_additional_axis_length,
           ### portion
           #ai_portion_tooth_nb     = ai_gr_args.sw_cut_portion[0],
           #ai_portion_first_end    = ai_gr_args.sw_cut_portion[1],
           #ai_portion_last_end     = ai_gr_args.sw_cut_portion[2],
           ### output
           ai_gear_profile_height  = ai_gr_args.sw_gear_profile_height,
           ai_simulation_enable    = ai_gr_args.sw_simulation_enable,    # ai_gr_args.sw_simulation_enable,
           #ai_output_file_basename = ai_gr_args.sw_output_file_basename,
           ##### from gearring
           ### holder
           ai_holder_diameter            = ai_gr_args.sw_holder_diameter,
           ai_holder_crenel_number       = ai_gr_args.sw_holder_crenel_number,
           ai_holder_position_angle      = ai_gr_args.sw_holder_position_angle,
           ### holder-hole
           ai_holder_hole_position_radius   = ai_gr_args.sw_holder_hole_position_radius,
           ai_holder_hole_diameter          = ai_gr_args.sw_holder_hole_diameter,
           ### holder-crenel
           ai_holder_crenel_position        = ai_gr_args.sw_holder_crenel_position,
           ai_holder_crenel_height          = ai_gr_args.sw_holder_crenel_height,
           ai_holder_crenel_width           = ai_gr_args.sw_holder_crenel_width,
           ai_holder_crenel_skin_width      = ai_gr_args.sw_holder_crenel_skin_width,
           ai_holder_crenel_router_bit_radius   = ai_gr_args.sw_holder_crenel_router_bit_radius,
           ai_holder_smoothing_radius       = ai_gr_args.sw_holder_smoothing_radius,
           ### cnc router_bit constraint
           ai_cnc_router_bit_radius          = ai_gr_args.sw_cnc_router_bit_radius,
           ### design output : view the gearring with tkinter or write files
           ai_tkinter_view = tkinter_view,
           ai_output_file_basename = ai_gr_args.sw_output_file_basename,
           ### optional
           ai_args_in_txt = ai_args_in_txt)
  return(r_gr)

################################################################
# self test
################################################################

def gearring_self_test():
  """
  This is the non-regression test of gearring.
  Look at the simulation Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"                  , "--gear_tooth_nb 25 --gear_module 10 --holder_diameter 280.0 --cnc_router_bit_radius 3.0"],
    ["no tooth"                       , "--gear_tooth_nb 0 --gear_primitive_diameter 100.0 --holder_diameter 120.0 --cnc_router_bit_radius 3.0"],
    ["last test"                      , "--gear_tooth_nb 30 --gear_module 10.0 --holder_diameter 340.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  gearring_parser = argparse.ArgumentParser(description='Command line interface for the function gearring().')
  gearring_parser = gear_profile.gear_profile_add_argument(gearring_parser, 1)
  gearring_parser = gearring_add_argument(gearring_parser)
  gearring_parser = cnc25d_api.generate_output_file_add_argument(gearring_parser)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = gearring_parser.parse_args(l_args)
    r_grst = gearring_argparse_wrapper(st_args)
  return(r_grst)

################################################################
# gearring command line interface
################################################################

def gearring_cli(ai_args=None):
  """ command line interface of gearring.py when it is used in standalone
  """
  # gearring parser
  gearring_parser = argparse.ArgumentParser(description='Command line interface for the function gearring().')
  gearring_parser = gear_profile.gear_profile_add_argument(gearring_parser, 1)
  gearring_parser = gearring_add_argument(gearring_parser)
  gearring_parser = cnc25d_api.generate_output_file_add_argument(gearring_parser)
  # switch for self_test
  gearring_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
  help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "gearring arguments: " + ' '.join(effective_args)
  gr_args = gearring_parser.parse_args(effective_args)
  print("dbg111: start making gearring")
  if(gr_args.sw_run_self_test):
    r_gr = gearring_self_test()
  else:
    r_gr = gearring_argparse_wrapper(gr_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_gr)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearring.py says hello!\n")
  #my_gr = gearring_cli()
  my_gr = gearring_cli("--gear_tooth_nb 25 --gear_module 10 --holder_diameter 300.0 --holder_crenel_width 20.0 --holder_crenel_skin_width 10.0 --cnc_router_bit_radius 2.0".split())

