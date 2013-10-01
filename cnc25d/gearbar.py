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
# gearbar dictionary-constraint-arguments default values
################################################################

def gearbar_dictionary_init():
  """ create and initiate a gearbar_dictionary with the default value
  """
  r_gbd = {}
  #### inherit dictionary entries from gear_profile
  r_gbd.update(gear_profile.gear_profile_dictionary_init())
  #### gearbar dictionary entries
  ### gearbar
  r_gbd['gearbar_height']                 = 20.0
  ### gearbar-hole
  r_gbd['gearbar_hole_height_position']   = 10.0
  r_gbd['gearbar_hole_diameter']          = 10.0
  r_gbd['gearbar_hole_offset']            = 0
  r_gbd['gearbar_hole_increment']         = 1
  ### view the gearbar with tkinter
  r_gbd['tkinter_view'] = False
  r_gbd['output_file_basename'] = ''
  ### optional
  r_gbd['args_in_txt'] = ''
  r_gbd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_gbd)

################################################################
# gearbar argparse
################################################################

def gearbar_add_argument(ai_parser):
  """
  Add arguments relative to the gearbar in addition to the argument of gear_profile_add_argument()
  This function intends to be used by the gearbar_cli and gearbar_self_test
  """
  r_parser = ai_parser
  ### inherit arguments from gear_profile
  r_parser = gear_profile.gear_profile_add_argument(r_parser, 3)
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

def gearbar(ai_constraints):
  """
  The main function of the script.
  It generates a gearbar according to the function arguments
  """
  ### check the dictionary-arguments ai_constraints
  gbdi = gearbar_dictionary_init()
  gb_c = gbdi.copy()
  gb_c.update(ai_constraints)
  #print("dbg155: gb_c:", gb_c)
  if(len(gb_c.viewkeys() & gbdi.viewkeys()) != len(gb_c.viewkeys() | gbdi.viewkeys())): # check if the dictionary gb_c has exactly all the keys compare to gearbar_dictionary_init()
    print("ERR157: Error, gb_c has too much entries as {:s} or missing entries as {:s}".format(gb_c.viewkeys() - gbdi.viewkeys(), gbdi.viewkeys() - gb_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new gearbar constraints:")
  #for k in gb_c.viewkeys():
  #  if(gb_c[k] != gbdi[k]):
  #    print("dbg166: for k {:s}, gb_c[k] {:s} != gbdi[k] {:s}".format(k, str(gb_c[k]), str(gbdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  gearbar_hole_radius = float(gb_c['gearbar_hole_diameter'])/2
  # gb_c['gearbar_hole_height_position']
  if((gb_c['gearbar_hole_height_position']+gearbar_hole_radius)>gb_c['gearbar_height']):
    print("ERR215: Error, gearbar_hole_height_position {:0.3} and gearbar_hole_radius {:0.3f} are too big compare to gearbar_height {:0.3f} !".format(gb_c['gearbar_hole_height_position'], gearbar_hole_radius, gb_c['gearbar_height']))
    sys.exit(2)
  # gb_c['gearbar_hole_increment']
  if(gb_c['gearbar_hole_increment']==0):
    print("ERR183: Error gearbar_hole_increment must be bigger than zero!")
    sys.exit(2)
  # gb_c['gear_tooth_nb']
  if(gb_c['gear_tooth_nb']>0): # create a gear_profile
    ### get the gear_profile
    gp_ci = gear_profile.gear_profile_dictionary_init()
    gp_c = dict([ (k, gb_c[k]) for k in gp_ci.keys() ]) # extract only the entries of the gear_profile
    gp_c['gear_type'] = 'l'
    gp_c['second_gear_type'] = 'e'
    gp_c['output_file_basename'] = ''
    gp_c['args_in_txt'] = ''
    gp_c['return_type'] = 'figure_param_info'
    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile(gp_c)
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    ## gear_profile_B rotation / translation transformation
    g1_ix = gear_profile_parameters['center_ox']
    g1_iy = gear_profile_parameters['center_oy']
    g1_inclination = gear_profile_parameters['gearbar_inclination']
    gear_profile_B = cnc25d_api.outline_rotate(gear_profile_B, g1_ix, g1_iy, -1*g1_inclination + math.pi/2)
    gear_profile_B = cnc25d_api.outline_shift_xy(gear_profile_B, -1*gear_profile_B[0][0], 1, -1*g1_iy + gb_c['gearbar_height'], 1)
    ## get some parameters
    minimal_gear_profile_height = gb_c['gearbar_height'] - (gear_profile_parameters['hollow_height'] + gear_profile_parameters['dedendum_height'])
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
    if(gb_c['gear_primitive_diameter']<radian_epsilon):
      print("ERR885: Error, the no-gear-profile line outline length gear_primitive_diameter {:0.2f} is too small!".format(gb_c['gear_primitive_diameter']))
      sys.exit(2)
    #g1_ix = gb_c['center_position_x
    #g1_iy = gb_c['center_position_y
    gearbar_length = gb_c['gear_primitive_diameter']
    gear_profile_B = [(0, gb_c['gearbar_height']),(gearbar_length, gb_c['gearbar_height'])]
    gear_profile_info = "\nSimple line (no-gear-profile):\n"
    gear_profile_info += "outline line length: \t{:0.3f}\n".format(gearbar_length)
    minimal_gear_profile_height = gb_c['gearbar_height']
    pi_module = gb_c['gear_module'] * math.pi
    first_tooth_position = float(pi_module)/2

  ### check parameter coherence (part 2)
  # minimal_gear_profile_height
  if(minimal_gear_profile_height<radian_epsilon):
    print("ERR265: Error, minimal_gear_profile_height {:0.3f} is too small".format(minimal_gear_profile_height))
    sys.exit(2)
  # gearbar_hole_diameter
  if((gb_c['gearbar_hole_height_position']+gearbar_hole_radius)>minimal_gear_profile_height):
    print("ERR269: Error, gearbar_hole_height_position {:0.3f} and gearbar_hole_radius {:0.3f} are too big compare to minimal_gear_profile_height {:0.3f}".format(gb_c['gearbar_hole_height_position'], gearbar_hole_radius, minimal_gear_profile_height))
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
    hole_x = first_tooth_position + gb_c['gearbar_hole_offset'] * pi_module
    while(hole_x<(gearbar_length-gearbar_hole_radius)):
      #print("dbg312: hole_x {:0.3f}".format(hole_x))
      gearbar_hole_figure.append([hole_x, gb_c['gearbar_hole_height_position'], gearbar_hole_radius])
      hole_x += gb_c['gearbar_hole_increment'] * pi_module

  ### design output
  gb_figure = [gearbar_outline]
  gb_figure.extend(gearbar_hole_figure)
  # ideal_outline in overlay
  gb_figure_overlay = []
  # gearbar_parameter_info
  gearbar_parameter_info = "\nGearbar parameter info:\n"
  gearbar_parameter_info += "\n" + gb_c['args_in_txt'] + "\n\n"
  gearbar_parameter_info += gear_profile_info
  gearbar_parameter_info += """
gearbar_length: \t{:0.3f}
gearbar_height: \t{:0.3f}
minimal_gear_profile_height: \t{:0.3f}
""".format(gearbar_length, gb_c['gearbar_height'], minimal_gear_profile_height)
  gearbar_parameter_info += """
gearbar_hole_height_position: \t{:0.3f}
gearbar_hole_diameter: \t{:0.3f}
gearbar_hole_offset: \t{:d}
gearbar_hole_increment: \t{:d}
pi_module: \t{:0.3f}
""".format(gb_c['gearbar_hole_height_position'], gb_c['gearbar_hole_diameter'], gb_c['gearbar_hole_offset'], gb_c['gearbar_hole_increment'], pi_module)
  #print(gearbar_parameter_info)

  # display with Tkinter
  if(gb_c['tkinter_view']):
    print(gearbar_parameter_info)
    cnc25d_api.figure_simple_display(gb_figure, gb_figure_overlay, gearbar_parameter_info)
  # generate output file
  cnc25d_api.generate_output_file(gb_figure, gb_c['output_file_basename'], gb_c['gear_profile_height'], gearbar_parameter_info)

  ### return the gearbar as FreeCAD Part object
  #r_gb = cnc25d_api.figure_to_freecad_25d_part(gb_figure, gb_c['gear_profile_height'])
  r_gb = 1 # this is to spare the freecad computation time during debuging
  #### return
  if(gb_c['return_type']=='int_status'):
    r_gb = 1
  elif(gb_c['return_type']=='cnc25d_figure'):
    r_gb = gb_figure
  elif(gb_c['return_type']=='freecad_object'):
    r_gb = cnc25d_api.figure_to_freecad_25d_part(gb_figure, gb_c['gear_profile_height'])
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(gb_c['return_type']))
    sys.exit(2)
  return(r_gb)

################################################################
# gearbar wrapper dance
################################################################

def gearbar_argparse_to_dictionary(ai_gb_args):
  """ convert a gearbar_argparse into a gearbar_dictionary
  """
  r_gbd = {}
  r_gbd.update(gear_profile.gear_profile_argparse_to_dictionary(ai_gb_args, 3))
  ##### from gearbar
  ### gearbar
  r_gbd['gearbar_height']                = ai_gb_args.sw_gearbar_height
  ### gearbar-hole
  r_gbd['gearbar_hole_height_position']  = ai_gb_args.sw_gearbar_hole_height_position
  r_gbd['gearbar_hole_diameter']         = ai_gb_args.sw_gearbar_hole_diameter
  r_gbd['gearbar_hole_offset']           = ai_gb_args.sw_gearbar_hole_offset
  r_gbd['gearbar_hole_increment']        = ai_gb_args.sw_gearbar_hole_increment
  ### design output : view the gearbar with tkinter or write files
  #r_gbd['tkinter_view'] = tkinter_view
  r_gbd['output_file_basename'] = ai_gb_args.sw_output_file_basename
  ### optional
  #r_gbd['args_in_txt'] = ''
  #r_gbd['return_type'] = 'int_status'
  #### return
  return(r_gbd)

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
  gbd = gearbar_argparse_to_dictionary(ai_gb_args)
  gbd['args_in_txt'] = ai_args_in_txt
  gbd['tkinter_view'] = tkinter_view
  gbd['return_type'] = 'int_status'
  r_gb = gearbar(gbd)
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

