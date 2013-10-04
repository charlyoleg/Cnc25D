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
# gearring dictionary-constraint-arguments default values
################################################################

def gearring_dictionary_init():
  """ create and initiate a gearring_dictionary with the default value
  """
  r_grd = {}
  #### inherit dictionary entries from gear_profile
  r_grd.update(gear_profile.gear_profile_dictionary_init())
  #### gearring dictionary entries
  ### holder
  r_grd['holder_diameter']            = 0.0
  r_grd['holder_crenel_number']       = 6
  r_grd['holder_position_angle']      = 0.0
  ### holder-hole
  r_grd['holder_hole_position_radius']   = 0.0
  r_grd['holder_hole_diameter']          = 10.0
  ### holder-crenel
  r_grd['holder_crenel_position']        = 10.0
  r_grd['holder_crenel_height']          = 10.0
  r_grd['holder_crenel_width']           = 10.0
  r_grd['holder_crenel_skin_width']      = 10.0
  r_grd['holder_crenel_router_bit_radius']   = 1.0
  r_grd['holder_smoothing_radius']       = 0.0
  ### cnc router_bit constraint
  r_grd['cnc_router_bit_radius']          = 1.0
  ### view the gearring with tkinter
  r_grd['tkinter_view'] = False
  r_grd['output_file_basename'] = ''
  ### optional
  r_grd['args_in_txt'] = ''
  r_grd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_grd)

################################################################
# gearring argparse
################################################################

def gearring_add_argument(ai_parser):
  """
  Add arguments relative to the gearring in addition to the argument of gear_profile_add_argument()
  This function intends to be used by the gearring_cli and gearring_self_test
  """
  r_parser = ai_parser
  ### inherit arguments from gear_profile
  r_parser = gear_profile.gear_profile_add_argument(r_parser, 2)
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

def gearring(ai_constraints):
  """
  The main function of the script.
  It generates a gearring according to the function arguments
  """
  ### check the dictionary-arguments ai_constraints
  grdi = gearring_dictionary_init()
  gr_c = grdi.copy()
  gr_c.update(ai_constraints)
  #print("dbg155: gr_c:", gr_c)
  if(len(gr_c.viewkeys() & grdi.viewkeys()) != len(gr_c.viewkeys() | grdi.viewkeys())): # check if the dictionary gr_c has exactly all the keys compare to gearring_dictionary_init()
    print("ERR157: Error, gr_c has too much entries as {:s} or missing entries as {:s}".format(gr_c.viewkeys() - grdi.viewkeys(), grdi.viewkeys() - gr_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new gearring constraints:")
  #for k in gr_c.viewkeys():
  #  if(gr_c[k] != grdi[k]):
  #    print("dbg166: for k {:s}, gr_c[k] {:s} != grdi[k] {:s}".format(k, str(gr_c[k]), str(grdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  holder_radius = float(gr_c['holder_diameter'])/2
  if(holder_radius<radian_epsilon):
    print("ERR202: Error, holder_radius {:0.3f} must be set with a larger value".format(holder_radius))
    sys.exit(2)
  holder_hole_position_radius = gr_c['holder_hole_position_radius']
  if(holder_hole_position_radius==0):
    holder_hole_position_radius = holder_radius
  holder_hole_radius = float(gr_c['holder_hole_diameter'])/2
  holder_maximal_radius = holder_hole_position_radius + gr_c['holder_crenel_position'] + gr_c['holder_crenel_height']
  holder_maximal_height = holder_maximal_radius - holder_radius
  holder_crenel_half_width = float(gr_c['holder_crenel_width'])/2
  holder_crenel_with_wall_half_width = holder_crenel_half_width + gr_c['holder_crenel_skin_width']
  if(holder_radius<holder_crenel_with_wall_half_width):
    print("ERR213: Error, holder_radius {:0.3f} must be bigger than holder_crenel_with_wall_half_width {:0.3f}".format(holder_radius, holder_crenel_with_wall_half_width))
    sys.exit(2)
  holder_crenel_half_angle = math.asin(float(holder_crenel_with_wall_half_width)/holder_radius)
  holder_crenel_x_position = math.sqrt((holder_radius)**2 - (holder_crenel_with_wall_half_width)**2)
  additional_holder_maximal_height = holder_radius - holder_crenel_x_position
  holder_maximal_height_plus = holder_maximal_height + additional_holder_maximal_height
  holder_side_outer_smoothing_radius = min(0.8*gr_c['holder_crenel_skin_width'], float(holder_maximal_height_plus)/4)
  holder_side_straigth_length = holder_maximal_height_plus - holder_side_outer_smoothing_radius
  # get the router_bit_radius
  gear_router_bit_radius = gr_c['gear_router_bit_radius']
  if(gr_c['cnc_router_bit_radius']>gear_router_bit_radius):
    gear_router_bit_radius = gr_c['cnc_router_bit_radius']
  holder_crenel_router_bit_radius = gr_c['holder_crenel_router_bit_radius']
  if(gr_c['cnc_router_bit_radius']>holder_crenel_router_bit_radius):
    holder_crenel_router_bit_radius = gr_c['cnc_router_bit_radius']
  holder_smoothing_radius = gr_c['holder_smoothing_radius']
  if(holder_smoothing_radius==0):
    holder_smoothing_radius = 0.9*holder_side_straigth_length
  if(gr_c['cnc_router_bit_radius']>holder_smoothing_radius):
    holder_smoothing_radius = gr_c['cnc_router_bit_radius']
  # gr_c['holder_crenel_height
  if(gr_c['holder_crenel_number']>0):
    if((0.9*holder_side_straigth_length)<holder_smoothing_radius):
      print("ERR218: Error, the holder-crenel-wall-side height is too small: holder_side_straigth_length {:0.3f}  holder_smoothing_radius {:0.3f}".format(holder_side_straigth_length, holder_smoothing_radius))
      sys.exit(2)
  # gr_c['holder_crenel_position']
  if(gr_c['holder_crenel_position']<holder_hole_radius):
    print("ERR211: Error, holder_crenel_position {:0.3f} is too small compare to holder_hole_radius {:03f}".format(gr_c['holder_crenel_position'], holder_hole_radius))
    sys.exit(2)
  # gr_c['holder_crenel_width']
  if(gr_c['holder_crenel_width']<2.1*holder_crenel_router_bit_radius):
    print("ERR215: Error, holder_crenel_width {:0.3} is too small compare to holder_crenel_router_bit_radius {:0.3f}".format(gr_c['holder_crenel_width'], holder_crenel_router_bit_radius))
    sys.exit(2)
  # gr_c['gear_tooth_nb']
  if(gr_c['gear_tooth_nb']>0): # create a gear_profile
    ### get the gear_profile
    gp_ci = gear_profile.gear_profile_dictionary_init()
    gp_c = dict([ (k, gr_c[k]) for k in gp_ci.keys() ]) # extract only the entries of the gear_profile
    gp_c['gear_type'] = 'i'
    gp_c['second_gear_type'] = 'e'
    gp_c['gear_router_bit_radius'] = gear_router_bit_radius
    gp_c['gearbar_slope'] = 0
    gp_c['gearbar_slope_n'] = 0
    gp_c['portion_tooth_nb'] = 0
    gp_c['portion_first_end'] = 0
    gp_c['portion_last_end'] = 0
    gp_c['output_file_basename'] = ''
    gp_c['args_in_txt'] = ''
    gp_c['return_type'] = 'figure_param_info'
    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile(gp_c)
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    maximal_gear_profile_radius = gear_profile_parameters['hollow_radius']
    g1_ix = gear_profile_parameters['center_ox']
    g1_iy = gear_profile_parameters['center_oy']
  else: # no gear_profile, just a circle
    if(gr_c['gear_primitive_diameter']<radian_epsilon):
      print("ERR885: Error, the no-gear-profile circle outline diameter gear_primitive_diameter {:0.2f} is too small!".format(gr_c['gear_primitive_diameter']))
      sys.exit(2)
    g1_ix = gr_c['center_position_x']
    g1_iy = gr_c['center_position_y']
    gear_profile_B = (g1_ix, g1_iy, float(gr_c['gear_primitive_diameter'])/2)
    gear_profile_info = "\nSimple circle (no-gear-profile):\n"
    gear_profile_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(gr_c['gear_primitive_diameter']/2.0, gr_c['gear_primitive_diameter'])
    gear_profile_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(g1_ix, g1_iy)
    maximal_gear_profile_radius = float(gr_c['gear_primitive_diameter'])/2
  ### check parameter coherence (part 2)
  # hollow_circle and holder-hole
  if(maximal_gear_profile_radius>(holder_hole_position_radius-holder_hole_radius)):
    print("ERR303: Error, holder-hole are too closed from the gear_hollow_circle: maximal_gear_profile_radius {:0.3f}  holder_hole_position_radius {:0.3f}  holder_hole_radius {:0.3f}".format(maximal_gear_profile_radius, holder_hole_position_radius, holder_hole_radius))
    sys.exit(2)
  ### holder outline
  holder_figure_overlay = []
  if(gr_c['holder_crenel_number']==0):
    holder_outline = (g1_ix, g1_iy, holder_radius)
  elif(gr_c['holder_crenel_number']>0):
    angle_incr = 2*math.pi/gr_c['holder_crenel_number']
    if((angle_incr-2*holder_crenel_half_angle)<math.pi/10):
      print("ERR369: Error, no enough space between the crenel: angle_incr {:0.3f}  holder_crenel_half_angle {:0.3f}".format(angle_incr, holder_crenel_half_angle))
      sys.exit(2)
    holder_A = []
    first_angle = gr_c['holder_position_angle'] - holder_crenel_half_angle
    holder_A.append([g1_ix+holder_radius*math.cos(first_angle), g1_iy+holder_radius*math.sin(first_angle), holder_smoothing_radius])
    for i in range(gr_c['holder_crenel_number']):
      holder_A .extend(make_holder_crenel(holder_maximal_height_plus, gr_c['holder_crenel_height'], gr_c['holder_crenel_skin_width'], holder_crenel_half_width, 
                                          holder_crenel_router_bit_radius, holder_side_outer_smoothing_radius, holder_smoothing_radius,
                                          holder_crenel_x_position, gr_c['holder_position_angle']+i*angle_incr, g1_ix, g1_iy))
      middle_angle = gr_c['holder_position_angle'] + (i+0.5)*angle_incr
      end_angle = gr_c['holder_position_angle'] + (i+1)*angle_incr - holder_crenel_half_angle
      holder_A.append([g1_ix+holder_radius*math.cos(middle_angle), g1_iy+holder_radius*math.sin(middle_angle),
                        g1_ix+holder_radius*math.cos(end_angle), g1_iy+holder_radius*math.sin(end_angle), holder_smoothing_radius])
    holder_A[-1] = [holder_A[-1][0], holder_A[-1][1], holder_A[0][0], holder_A[0][1], 0]
    holder_outline = cnc25d_api.cnc_cut_outline(holder_A, "holder_A")
    holder_figure_overlay.append(cnc25d_api.ideal_outline(holder_A, "holder_A"))
  ### holder-hole outline
  holder_hole_figure = []
  if((gr_c['holder_crenel_number']>0)and(holder_hole_radius>0)):
    for i in range(gr_c['holder_crenel_number']):
      hole_angle = gr_c['holder_position_angle']+i*angle_incr
      holder_hole_figure.append([g1_ix+holder_hole_position_radius*math.cos(hole_angle), g1_iy+holder_hole_position_radius*math.sin(hole_angle), holder_hole_radius])

  ### design output
  gr_figure = []
  gr_figure.append(holder_outline) # largest outline first for freecad
  gr_figure.append(gear_profile_B)
  gr_figure.extend(holder_hole_figure)
  # ideal_outline in overlay
  gr_figure_overlay = []
  gr_figure_overlay.extend(holder_figure_overlay)
  # gearring_parameter_info
  gearring_parameter_info = "\nGearring parameter info:\n"
  gearring_parameter_info += "\n" + gr_c['args_in_txt'] + "\n\n"
  gearring_parameter_info += gear_profile_info
  gearring_parameter_info += """
holder_diameter: \t{:0.3f}
holder_crenel_number: \t{:d}
holder_position_angle: \t{:0.3f}
""".format(gr_c['holder_diameter'], gr_c['holder_crenel_number'], gr_c['holder_position_angle'])
  gearring_parameter_info += """
holder_hole_position_radius: \t{:0.3f}
holder_hole_diameter: \t{:0.3f}
""".format(holder_hole_position_radius, gr_c['holder_hole_diameter'])
  gearring_parameter_info += """
holder_crenel_position: \t{:0.3f}
holder_crenel_height: \t{:0.3f}
holder_crenel_width: \t{:0.3f}
holder_crenel_skin_width: \t{:0.3f}
""".format(gr_c['holder_crenel_position'], gr_c['holder_crenel_height'], gr_c['holder_crenel_width'], gr_c['holder_crenel_skin_width'])
  gearring_parameter_info += """
gear_router_bit_radius:           \t{:0.3f}
holder_crenel_router_bit_radius:  \t{:0.3f}
holder_smoothing_radius:          \t{:0.3f}
cnc_router_bit_radius:            \t{:0.3f}
""".format(gear_router_bit_radius, holder_crenel_router_bit_radius, holder_smoothing_radius, gr_c['cnc_router_bit_radius'])
  #print(gearring_parameter_info)

  # display with Tkinter
  if(gr_c['tkinter_view']):
    print(gearring_parameter_info)
    cnc25d_api.figure_simple_display(gr_figure, gr_figure_overlay, gearring_parameter_info)
  # generate output file
  cnc25d_api.generate_output_file(gr_figure, gr_c['output_file_basename'], gr_c['gear_profile_height'], gearring_parameter_info)

  ### return
  if(gr_c['return_type']=='int_status'):
    r_gr = 1
  elif(gr_c['return_type']=='cnc25d_figure'):
    r_gr = gr_figure
  elif(gr_c['return_type']=='freecad_object'):
    r_gr = cnc25d_api.figure_to_freecad_25d_part(gr_figure, gr_c['gear_profile_height'])
  else:
    print("ERR346: Error the return_type {:s} is unknown".format(gr_c['return_type']))
    sys.exit(2)
  return(r_gr)

################################################################
# gearring wrapper dance
################################################################

def gearring_argparse_to_dictionary(ai_gr_args):
  """ convert a gearring_argparse into a gearring_dictionary
  """
  r_grd = {}
  r_grd.update(gear_profile.gear_profile_argparse_to_dictionary(ai_gr_args, 2))
  ##### from gearring
  ### holder
  r_grd['holder_diameter']            = ai_gr_args.sw_holder_diameter
  r_grd['holder_crenel_number']       = ai_gr_args.sw_holder_crenel_number
  r_grd['holder_position_angle']      = ai_gr_args.sw_holder_position_angle
  ### holder-hole
  r_grd['holder_hole_position_radius']   = ai_gr_args.sw_holder_hole_position_radius
  r_grd['holder_hole_diameter']          = ai_gr_args.sw_holder_hole_diameter
  ### holder-crenel
  r_grd['holder_crenel_position']        = ai_gr_args.sw_holder_crenel_position
  r_grd['holder_crenel_height']          = ai_gr_args.sw_holder_crenel_height
  r_grd['holder_crenel_width']           = ai_gr_args.sw_holder_crenel_width
  r_grd['holder_crenel_skin_width']      = ai_gr_args.sw_holder_crenel_skin_width
  r_grd['holder_crenel_router_bit_radius']   = ai_gr_args.sw_holder_crenel_router_bit_radius
  r_grd['holder_smoothing_radius']       = ai_gr_args.sw_holder_smoothing_radius
  ### cnc router_bit constraint
  r_grd['cnc_router_bit_radius']          = ai_gr_args.sw_cnc_router_bit_radius
  ### design output : view the gearring with tkinter or write files
  #r_grd['tkinter_view'] = tkinter_view
  r_grd['output_file_basename'] = ai_gr_args.sw_output_file_basename
  r_grd['return_type'] = ai_gr_args.sw_return_type
  ### optional
  #r_grd['args_in_txt'] = ''
  #### return
  return(r_grd)

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
  grd = gearring_argparse_to_dictionary(ai_gr_args)
  #grd['gear_type'] = 'i'
  #grd['second_gear_type'] = 'e'
  #grd['gearbar_slope'] = 0
  #grd['gearbar_slope_n'] = 0
  #grd['portion_tooth_nb'] = 0
  #grd['portion_first_end'] = 0
  #grd['portion_last_end'] = 0
  grd['args_in_txt'] = ai_args_in_txt
  grd['tkinter_view'] = tkinter_view
  #grd['return_type'] = 'int_status'
  r_gr = gearring(grd)
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
    ["simplest test"    , "--gear_tooth_nb 25 --gear_module 10 --holder_diameter 300.0 --cnc_router_bit_radius 2.0"],
    ["no tooth"         , "--gear_tooth_nb 0 --gear_primitive_diameter 100.0 --holder_diameter 120.0 --cnc_router_bit_radius 2.0 --holder_crenel_number 7"],
    ["no holder-hole"   , "--gear_tooth_nb 30 --gear_module 10 --holder_diameter 360.0 --holder_crenel_width 20.0 --holder_crenel_skin_width 20.0 --cnc_router_bit_radius 2.0 --holder_hole_diameter 0.0"],
    ["no crenel"        , "--gear_tooth_nb 29 --gear_module 10 --holder_diameter 340.0 --holder_crenel_width 20.0 --holder_crenel_number 0"],
    ["small crenel"     , "--gear_tooth_nb 30 --gear_module 10 --holder_diameter 360.0 --holder_crenel_width 20.0 --holder_crenel_number 1 --holder_hole_diameter 0.0 --holder_crenel_position 0.0 --holder_crenel_height 5.0"],
    ["narrow crenel"    , "--gear_tooth_nb 30 --gear_module 10 --holder_diameter 360.0 --holder_crenel_width 20.0 --holder_crenel_number 4 --holder_position_angle 0.785 --holder_hole_diameter 0.0 --holder_crenel_position 0.0 --holder_crenel_height 5.0"],
    ["output dxf"    , "--gear_tooth_nb 30 --gear_module 10 --holder_diameter 360.0 --holder_crenel_width 20.0 --holder_crenel_number 2 --holder_position_angle 0.785 --holder_hole_diameter 0.0 --holder_crenel_position 0.0 --holder_crenel_height 5.0 --output_file_basename test_output/gearring_self_test.dxf"],
    ["last test"        , "--gear_tooth_nb 30 --gear_module 10.0 --holder_diameter 340.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  gearring_parser = argparse.ArgumentParser(description='Command line interface for the function gearring().')
  gearring_parser = gearring_add_argument(gearring_parser)
  gearring_parser = cnc25d_api.generate_output_file_add_argument(gearring_parser, 1)
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
  gearring_parser = gearring_add_argument(gearring_parser)
  gearring_parser = cnc25d_api.generate_output_file_add_argument(gearring_parser, 1)
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
  #my_gr = gearring_cli("--gear_tooth_nb 25 --gear_module 10 --holder_diameter 300.0 --holder_crenel_width 20.0 --holder_crenel_skin_width 10.0 --cnc_router_bit_radius 2.0 --return_type freecad_object".split())
  my_gr = gearring_cli("--gear_tooth_nb 25 --gear_module 10 --holder_diameter 300.0 --holder_crenel_width 20.0 --holder_crenel_skin_width 10.0 --cnc_router_bit_radius 2.0".split())
  try: # depending on gr_c['return_type'] it might be or not a freecad_object
    Part.show(my_gr)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")

