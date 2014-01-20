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
#import re
#import Tkinter # to display the outline in a small GUI
#
import Part
#from FreeCAD import Base
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
  gp_c['gear_type'] = 'l'
  gp_c['second_gear_type'] = 'e'
  gp_c['gearbar_slope'] = 0.3
  #gp_c['gear_router_bit_radius'] = c['gear_router_bit_radius']
  r_obj = gear_profile.gear_profile()
  r_obj.apply_external_constraint(gp_c)
  return(r_obj)

################################################################
# gearbar constraint_constructor
################################################################

def gearbar_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the gearbar design
  """
  r_parser = ai_parser
  ### inherit arguments from gear_profile
  i_gear_profile = inherit_gear_profile()
  r_parser = i_gear_profile.get_constraint_constructor()(r_parser, 3)
  ### gearbar
  r_parser.add_argument('--gearbar_height','--gbh', action='store', type=float, default=20.0,
    help="Set the height of the gearbar (from the bottom to the gear-profile primitive line). Default: 20.0")
  ### gearbar-hole
  r_parser.add_argument('--gearbar_hole_height_position','--gbhhp', action='store', type=float, default=10.0,
    help="Set the height from the bottom of the gearbar to the center of the gearbar-hole. Default: 10.0")
  r_parser.add_argument('--gearbar_hole_diameter','--gbhd', action='store', type=float, default=10.0,
    help="Set the diameter of the gearbar-hole. If equal to 0.0, there are no gearbar-hole. Default: 10.0")
  r_parser.add_argument('--gearbar_hole_offset','--gbho', action='store', type=int, default=0,
    help="Set the initial number of teeth to position the first gearbar-hole. Default: 0")
  r_parser.add_argument('--gearbar_hole_increment','--gbhi', action='store', type=int, default=1,
    help="Set the number of teeth between two gearbar-holes. Default: 1")
  # return
  return(r_parser)

################################################################
# gearbar constraint_check
################################################################

def gearbar_constraint_check(c):
  """ check the gearbar constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  c['gearbar_hole_radius'] = float(c['gearbar_hole_diameter'])/2
  # c['gearbar_hole_height_position']
  if((c['gearbar_hole_height_position']+c['gearbar_hole_radius'])>c['gearbar_height']):
    print("ERR215: Error, gearbar_hole_height_position {:0.3} and gearbar_hole_radius {:0.3f} are too big compare to gearbar_height {:0.3f} !".format(c['gearbar_hole_height_position'], c['gearbar_hole_radius'], c['gearbar_height']))
    sys.exit(2)
  # c['gearbar_hole_increment']
  if(c['gearbar_hole_increment']==0):
    print("ERR183: Error gearbar_hole_increment must be bigger than zero!")
    sys.exit(2)
  # c['gear_tooth_nb']
  if(c['gear_tooth_nb']>0): # create a gear_profile
    i_gear_profile = inherit_gear_profile(c)
    gear_profile_parameters = i_gear_profile.get_constraint()
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    gear_profile_for_length = i_gear_profile.get_A_figure('first_gear')[0]
    c['gearbar_length'] = gear_profile_for_length[-1][0] - gear_profile_for_length[0][0]
    c['g1_ix'] = gear_profile_parameters['g1_param']['center_ox']
    c['g1_iy'] = gear_profile_parameters['g1_param']['center_oy']
    c['g1_inclination'] = gear_profile_parameters['g1_param']['gearbar_inclination']
    ## get some parameters
    c['minimal_gear_profile_height'] = c['gearbar_height'] - (gear_profile_parameters['g1_param']['hollow_height'] + gear_profile_parameters['g1_param']['dedendum_height'])
    c['pi_module'] = gear_profile_parameters['g1_param']['pi_module']
    pfe = gear_profile_parameters['g1_param']['portion_first_end']
    full_positive_slope = gear_profile_parameters['g1_param']['full_positive_slope']
    full_negative_slope = gear_profile_parameters['g1_param']['full_negative_slope']
    bottom_land = gear_profile_parameters['g1_param']['bottom_land']
    top_land = gear_profile_parameters['g1_param']['top_land']
    if((top_land + full_positive_slope + bottom_land + full_negative_slope)!=c['pi_module']):
      print("ERR269: Error with top_land {:0.3f}  full_positive_slope {:0.3f}  bottom_land {:0.3f}  full_negative_slope {:0.3f} and pi_module  {:0.3f}".format(top_land, full_positive_slope, bottom_land, full_negative_slope, c['pi_module']))
      sys.exit(2)
    if(pfe==0):
      c['first_tooth_position'] = full_positive_slope + bottom_land + full_negative_slope + float(top_land)/2
    elif(pfe==1):
      c['first_tooth_position'] = full_positive_slope + bottom_land + full_negative_slope + top_land
    elif(pfe==2):
      c['first_tooth_position'] = full_negative_slope + float(top_land)/2
    elif(pfe==3):
      c['first_tooth_position'] = float(bottom_land)/2 + full_negative_slope + float(top_land)/2
  else: # no gear_profile, just a circle
    if(c['gear_primitive_diameter']<radian_epsilon):
      print("ERR885: Error, the no-gear-profile line outline length gear_primitive_diameter {:0.2f} is too small!".format(c['gear_primitive_diameter']))
      sys.exit(2)
    #c['g1_ix'] = c['center_position_x
    #c['g1_iy'] = c['center_position_y
    c['gearbar_length'] = c['gear_primitive_diameter']
    c['minimal_gear_profile_height'] = c['gearbar_height']
    c['pi_module'] = c['gear_module'] * math.pi
    c['first_tooth_position'] = float(c['pi_module'])/2

  ### check parameter coherence (part 2)
  # minimal_gear_profile_height
  if(c['minimal_gear_profile_height']<radian_epsilon):
    print("ERR265: Error, minimal_gear_profile_height {:0.3f} is too small".format(c['minimal_gear_profile_height']))
    sys.exit(2)
  # gearbar_hole_diameter
  if((c['gearbar_hole_height_position']+c['gearbar_hole_radius'])>c['minimal_gear_profile_height']):
    print("ERR269: Error, gearbar_hole_height_position {:0.3f} and gearbar_hole_radius {:0.3f} are too big compare to minimal_gear_profile_height {:0.3f}".format(c['gearbar_hole_height_position'], c['gearbar_hole_radius'], c['minimal_gear_profile_height']))
    sys.exit(2)
  # pi_module
  if(c['gearbar_hole_radius']>0):
    if(c['pi_module']==0):
      print("ERR277: Error, pi_module is null. You might need to use --gear_module")
      sys.exit(2)
  ###
  return(c)

################################################################
# gearbar 2D-figures construction
################################################################

def gearbar_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the gearbar design
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### gearbar outline
  if(c['gear_tooth_nb']>0):
    i_gear_profile = inherit_gear_profile(c) # inherit from gear_profile
    gear_profile_A = i_gear_profile.get_A_figure('first_gear')[0] # Warning: gear_profile provide only B-format outline currently
    gear_profile_A = cnc25d_api.outline_rotate(gear_profile_A, c['g1_ix'], c['g1_iy'], -1*c['g1_inclination'] + math.pi/2)
    gear_profile_A = cnc25d_api.outline_shift_xy(gear_profile_A, -1*gear_profile_A[0][0], 1, -1*c['g1_iy'] + c['gearbar_height'], 1)
  else:
    gear_profile_A = [(0, c['gearbar_height']),(c['gearbar_length'], c['gearbar_height'])]
  gearbar_outline = gear_profile_A
  gearbar_outline.append((gearbar_outline[-1][0], 0))
  gearbar_outline.append((0, 0))
  gearbar_outline.append((0, gearbar_outline[0][1]))
  #print("dbg200: gearbar_outline:", gearbar_outline)
  ### gearbar-hole figure
  gearbar_hole_figure = []
  if((c['gearbar_hole_radius']>0)and(c['pi_module']>0)):
    hole_x = c['first_tooth_position'] + c['gearbar_hole_offset'] * c['pi_module']
    while(hole_x<(c['gearbar_length']-c['gearbar_hole_radius'])):
      #print("dbg312: hole_x {:0.3f}".format(hole_x))
      gearbar_hole_figure.append([hole_x, c['gearbar_hole_height_position'], c['gearbar_hole_radius']])
      hole_x += c['gearbar_hole_increment'] * c['pi_module']

  ### design output
  gb_figure = [gearbar_outline]
  gb_figure.extend(gearbar_hole_figure)
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['gearbar_fig'] = gb_figure
  r_height['gearbar_fig'] = c['gear_profile_height']
  ###
  return((r_figures, r_height))

################################################################
# gearbar simulation
################################################################

def gearbar_simulation_A(c):
  """ define the gearbar simulation
  """
  # inherit from gear_profile
  i_gear_profile = inherit_gear_profile(c)
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def gearbar_2d_simulations():
  """ return the dictionary defining the available simulation for gearbar
  """
  r_sim = {}
  r_sim['gearbar_simulation_A'] = gearbar_simulation_A
  return(r_sim)


################################################################
# gearbar 3D assembly-configuration construction
################################################################

def gearbar_3d_construction(c):
  """ construct the 3D-assembly-configurations of the gearbar
  """
  # conf1
  gearbar_3dconf1 = []
  gearbar_3dconf1.append(('gearbar_fig',  0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['gearbar_3dconf1'] = gearbar_3dconf1
  hh = c['gear_profile_height']/2.0 # half-height
  r_slice['gearbar_3dconf1'] = (c['gearbar_length'],c['gearbar_height'],c['gear_profile_height'], c['center_position_x'],c['center_position_y']-c['gearbar_height'],0.0, [hh], [], [])
  #
  return((r_assembly, r_slice))


################################################################
# gearbar_info
################################################################

def gearbar_info(c):
  """ create the text info related to the gearbar
  """
  r_info = ""
  if(c['gear_tooth_nb']>0): # with gear-profile (normal case)
    i_gear_profile = inherit_gear_profile(c) # inherit from gear_profile
    r_info += i_gear_profile.get_info()
  else: # when no gear-profile
    r_info += "\nSimple line (no-gear-profile):\n"
    r_info += "outline line length: \t{:0.3f}\n".format(c['gearbar_length'])
  r_info += """
gearbar_length: \t{:0.3f}
gearbar_height: \t{:0.3f}
minimal_gear_profile_height: \t{:0.3f}
""".format(c['gearbar_length'], c['gearbar_height'], c['minimal_gear_profile_height'])
  r_info += """
gearbar_hole_height_position: \t{:0.3f}
gearbar_hole_diameter: \t{:0.3f}
gearbar_hole_offset: \t{:d}
gearbar_hole_increment: \t{:d}
pi_module: \t{:0.3f}
""".format(c['gearbar_hole_height_position'], c['gearbar_hole_diameter'], c['gearbar_hole_offset'], c['gearbar_hole_increment'], c['pi_module'])
  #print(gearbar_parameter_info)
  return(r_info)


################################################################
# self test
################################################################

def gearbar_self_test():
  """
  This is the non-regression test of gearbar.
  Look at the simulation Tk window to check errors.
  """
  r_tests = [
    ["simplest test"    , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0"],
    ["no tooth"         , "--gear_tooth_nb 0 --gear_primitive_diameter 500.0 --gearbar_height 30.0 --gearbar_hole_height_position 15.0 --gear_module 10.0"],
    ["no gearbar-hole"  , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --gearbar_hole_diameter 0"],
    ["ends 3 3"         , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --cut_portion 20 3 3"],
    ["ends 2 1"         , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --cut_portion 19 2 1"],
    ["ends 1 3"         , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --cut_portion 18 1 3"],
    [" gearbar-hole"    , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --cut_portion 17 3 3 --gearbar_hole_offset 1 --gearbar_hole_increment 3"],
    ["output dxf"       , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --output_file_basename test_output/gearbar_self_test.dxf"],
    ["last test"        , "--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0"]]
  return(r_tests)

################################################################
# gearbar design declaration
################################################################

class gearbar(cnc25d_api.bare_design):
  """ gearbar design
  """
  def __init__(self, constraint={}):
    """ configure the gearbar design
    """
    self.set_design_name("gearbar")
    self.set_constraint_constructor(gearbar_constraint_constructor)
    self.set_constraint_check(gearbar_constraint_check)
    self.set_2d_constructor(gearbar_2d_construction)
    self.set_2d_simulation(gearbar_2d_simulations())
    self.set_3d_constructor(gearbar_3d_construction)
    self.set_info(gearbar_info)
    self.set_display_figure_list(['gearbar_fig'])
    self.set_default_simulation()
    self.set_2d_figure_file_list(['gearbar_fig'])
    self.set_3d_figure_file_list(['gearbar_fig'])
    self.set_3d_conf_file_list(['gearbar_3dconf1'])
    self.set_allinone_return_type()
    self.set_self_test(gearbar_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearbar.py says hello!\n")
  my_gb = gearbar()
  #my_gb.allinone()
  #my_gb.allinone("--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0 --return_type freecad_object")
  my_gb.allinone("--gear_tooth_nb 12 --gear_module 10 --gearbar_slope 0.3 --gear_router_bit_radius 3.0 --gearbar_height 40.0 --gearbar_hole_height_position 20.0")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_gb.get_fc_obj('gearbar_3dconf1'))
  

