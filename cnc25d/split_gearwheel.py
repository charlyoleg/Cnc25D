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
The main function return the split-gearwheel as FreeCAD Part object.
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
import re # to detect .dxf or .svg
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
  r_sgwd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
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
    help="Set the diameter of the high circle of the split-portion. If equal to 0.0, it is set to the minimal_gear_profile_radius - tooth_half_height. Default: 0.0")
  r_parser.add_argument('--high_split_type','--hst', action='store', default='h', dest='sw_high_split_type',
    help="Select the type of connection between the split-portion high-circle and the gear-profile. Possible values: 'h'=hollow_only , 'a'=addendum_too. Default: 'h'")
  ## split_router_bit_radius
  r_parser.add_argument('--split_router_bit_radius','--srbr', action='store', type=float, default=1.0, dest='sw_split_router_bit_radius',
    help="Set the split router_bit radius of the split-gearwheel (used at the high-circle corners). Default: 1.0")
  ### low-hole
  r_parser.add_argument('--low_hole_circle_diameter','--lhcd', action='store', type=float, default=0.0, dest='sw_low_hole_circle_diameter',
    help="Set the diameter of the low-hole circle. If equal to 0.0, it is set to low_split_diameter + low_hole_diameter. Default: 0.0")
  r_parser.add_argument('--low_hole_diameter','--lhd', action='store', type=float, default=10.0, dest='sw_low_hole_diameter',
    help="Set the diameter of the low-holes. Default: 10.0")
  r_parser.add_argument('--low_hole_nb','--lhn', action='store', type=int, default=1, dest='sw_low_hole_nb',
    help="Set the number of low-holes. Default: 1")
  ### high-hole
  r_parser.add_argument('--high_hole_circle_diameter','--hhcd', action='store', type=float, default=0.0, dest='sw_high_hole_circle_diameter',
    help="Set the diameter of the high-hole circle. If equal to 0.0, set to high_split_diameter - high_hole_diameter. Default: 0.0")
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
  ### check the dictionary-arguments ai_constraints
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
  # sg_c['split_nb']
  split_nb = sg_c['split_nb']
  if(split_nb<2):
    print("ERR188: Error, split_nb {:d} must be equal or bigger than 2".format(split_nb))
    sys.exit(2)
  #portion_angle = 2*math.pi/split_nb
  portion_angle = math.pi/split_nb
  #print("dbg190: sg_c['gear_tooth_nb']:", sg_c['gear_tooth_nb'])
  if(sg_c['gear_tooth_nb']>0): # create a gear_profile
    ### get the gear_profile
    gp_ci = gear_profile.gear_profile_dictionary_init()
    gp_c = dict([ (k, sg_c[k]) for k in gp_ci.keys() ]) # extract only the entries of the gear_profile
    gp_c['gear_type'] = 'e'
    gp_c['gear_router_bit_radius'] = gear_router_bit_radius
    gp_c['portion_tooth_nb'] = 0
    gp_c['portion_first_end'] = 0
    gp_c['portion_last_end'] = 0
    gp_c['output_file_basename'] = ''
    gp_c['args_in_txt'] = ''
    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile_dictionary_wrapper(gp_c)
    # extract some gear_profile high-level parameter
    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
    minimal_gear_profile_radius = gear_profile_parameters['hollow_radius']
    g1_ix = gear_profile_parameters['center_ox']
    g1_iy = gear_profile_parameters['center_oy']
    # high_split_radius
    g1_m = gear_profile_parameters['module']
    high_split_radius = sg_c['high_split_diameter']/2.0
    if(high_split_radius==0):
      high_split_radius = minimal_gear_profile_radius - g1_m
    ## gear_portion
    g1_pma = gear_profile_parameters['pi_module_angle']
    g1_hma = gear_profile_parameters['hollow_middle_angle']
    g1_ia = gear_profile_parameters['initial_angle']
    g1_tl = gear_profile_parameters['top_land']
    if(portion_angle<(1.1*g1_pma)):
      print("ERR219: Error, portion_angle {:0.3f} is too small compare to the pi_module_angle {:0.3f}".format(portion_angle, g1_pma))
      sys.exit(2)
    # pre common calculation
    absolute_angle = []
    relative_angle = []
    raw_tooth_nb = []
    a_start = g1_ia + g1_hma
    overhead = 2 # must be equal or bigger than 2 because of raw_tooth_nb[i-overhead+2]
    for i in range(2*split_nb+overhead):
      portion_start_angle = sg_c['split_initial_angle'] + (i+0.0) * portion_angle
      tooth_nb = 0
      while(abs(math.fmod(a_start-portion_start_angle+5*math.pi, 2*math.pi)-math.pi)>g1_pma/2.0):
        a_start += g1_pma
        tooth_nb += 1
      absolute_angle.append(a_start)
      relative_angle.append(math.fmod(a_start-portion_start_angle+5*math.pi, 2*math.pi)-math.pi)
      raw_tooth_nb.append(tooth_nb)
      #print("dbg238: i {:d} raw_tooth_nb {:0.3f}".format(i, raw_tooth_nb[i]))
    absolute_angle = absolute_angle[overhead:]
    relative_angle = relative_angle[overhead:]
    raw_tooth_nb = raw_tooth_nb[overhead:]
    # final low-parameters
    portion_gear_tooth_angle = []
    portion_gear_first_end = []
    portion_gear_last_end = []
    portion_gear_tooth_nb = []
    for i in range(2*split_nb):
      ii = i-overhead
      if(sg_c['high_split_type']=='h'):
        portion_gear_tooth_angle.append(absolute_angle[ii]-g1_hma+g1_pma)
        portion_gear_first_end.append(3)
        portion_gear_last_end.append(3)
        portion_gear_tooth_nb.append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1)
      elif(sg_c['high_split_type']=='a'):
        tooth_transfer = 0
        if(abs(relative_angle[ii])<=(g1_pma-g1_tl)/2.0):
          portion_gear_first_end.append(3)
          portion_gear_tooth_angle.append(absolute_angle[ii]-g1_hma+g1_pma)
        elif(relative_angle[ii]>=(g1_pma-g1_tl)/2.0):
          portion_gear_first_end.append(1)
          portion_gear_tooth_angle.append(absolute_angle[ii]-g1_hma)
          tooth_transfer = 1
        elif(relative_angle[ii]<=-1*(g1_pma-g1_tl)/2.0):
          portion_gear_first_end.append(1)
          portion_gear_tooth_angle.append(absolute_angle[ii]-g1_hma+g1_pma)
        if(abs(relative_angle[ii+2])<=(g1_pma-g1_tl)/2.0):
          portion_gear_tooth_nb.append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1+tooth_transfer)
          portion_gear_last_end.append(3)
        elif(relative_angle[ii+2]>=(g1_pma-g1_tl)/2.0):
          portion_gear_tooth_nb.append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1+tooth_transfer)
          portion_gear_last_end.append(1)
        elif(relative_angle[ii+2]<=-1*(g1_pma-g1_tl)/2.0):
          portion_gear_tooth_nb.append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-0+tooth_transfer)
          portion_gear_last_end.append(1)
    #print("dbg276: len(portion_gear_first_end) {:d}  len(portion_gear_last_end) {:d}".format(len(portion_gear_first_end), len(portion_gear_last_end)))
  else: # no gear_profile, just a circle
    if(sg_c['gear_primitive_diameter']<radian_epsilon):
      print("ERR885: Error, the no-gear-profile circle outline diameter sg_c['gear_primitive_diameter'] {:0.2f} is too small!".format(sg_c['gear_primitive_diameter']))
      sys.exit(2)
    #gear_profile_B = (g1_ix, g1_iy, float(sg_c['gear_primitive_diameter'])/2)
    minimal_gear_profile_radius = float(sg_c['gear_primitive_diameter'])/2
    g1_ix = sg_c['center_position_x']
    g1_iy = sg_c['center_position_y']
    gear_profile_info = "\nSimple circle (no-gear-profile):\n"
    gear_profile_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(sg_c['gear_primitive_diameter']/2.0, sg_c['gear_primitive_diameter'])
    gear_profile_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(g1_ix, g1_iy)
    if(sg_c['high_split_diameter']!=0):
      print("WARN221: Warning, the setting high_split_diameter {:0.3f} should not be used when gear_tooth_nb=0".format(sg_c['high_split_diameter']))
    high_split_radius = minimal_gear_profile_radius
  # set default value (if set to zero) for high_split_diameter, low_hole_circle_diameter, high_hole_circle_diameter
  low_split_radius = sg_c['low_split_diameter']/2.0
  low_hole_radius = sg_c['low_hole_diameter']/2.0
  low_hole_circle_radius = sg_c['low_hole_circle_diameter']/2.0
  high_hole_circle_radius = sg_c['high_hole_circle_diameter']/2.0
  high_hole_radius = sg_c['high_hole_diameter']/2.0
  if(low_hole_circle_radius==0):
    low_hole_circle_radius = low_split_radius + 2*low_hole_radius
  if(high_hole_circle_radius==0):
    high_hole_circle_radius = high_split_radius - 1.2*high_hole_radius
  #print("dbg292: high_hole_circle_radius {:0.3f}  high_split_radius {:0.3f}".format(high_hole_circle_radius, high_split_radius))
  ### check parameter coherence (part 2)
  # low_hole_nb and high_hole_nb
  if(sg_c['low_hole_nb']==0):
    low_hole_radius = 0
    sg_c['low_hole_nb']=1
  if(sg_c['high_hole_nb']==0):
    high_hole_radius = 0
    sg_c['high_hole_nb']=1
  # radial parameters
  if(low_hole_circle_radius<(low_split_radius + low_hole_radius)):
    print("ERR230: Error, low_hole_circle_radius {:0.3f} is too small compare to low_split_radius {:0.3f} and low_hole_radius {:0.3f}".format(low_hole_circle_radius, low_split_radius, low_hole_radius))
    sys.exit(2)
  if(high_hole_circle_radius<(low_hole_circle_radius + low_hole_radius + high_hole_radius)):
    print("ERR232: Error, high_hole_circle_radius {:0.3f} is too small compare to low_hole_circle_radius {:0.3f}, low_hole_radius {:0.3f} and high_hole_radius {:0.3f}".format(high_hole_circle_radius, low_hole_circle_radius, low_hole_radius, high_hole_radius))
    sys.exit(2)
  if(high_split_radius<(high_hole_circle_radius + high_hole_radius)):
    print("ERR236: Error, high_split_radius {:0.3f} is too small compare to high_hole_circle_radius {:0.3f} and high_hole_radius {:0.3f}".format(high_split_radius, high_hole_circle_radius, high_hole_radius))
    sys.exit(2)
  if(minimal_gear_profile_radius<high_split_radius):
    print("ERR239: Error, minimal_gear_profile_radius {:0.3f} is smaller than high_split_radius {:0.3f}".format(minimal_gear_profile_radius, high_split_radius))
    sys.exit(2)
  # angular (or circumference) parameters
  low_hole_diameter_angle = math.asin(float(low_hole_radius)/low_hole_circle_radius)
  low_hole_space_angle = portion_angle/float(sg_c['low_hole_nb'])
  high_hole_diameter_angle = math.asin(float(high_hole_radius)/high_hole_circle_radius)
  high_hole_space_angle = portion_angle/float(sg_c['high_hole_nb'])
  if(low_hole_space_angle<(2*low_hole_diameter_angle+radian_epsilon)):
    print("ERR253: Error, low_hole_nb {:d} or low_hole_diameter {:0.3f} are too big!".format(sg_c['low_hole_nb'], sg_c['low_hole_diameter']))
    sys.exit(2)
  if(high_hole_space_angle<(2*high_hole_diameter_angle+radian_epsilon)):
    print("ERR255: Error, high_hole_nb {:d} or high_hole_diameter {:0.3f} are too big!".format(sg_c['high_hole_nb'], sg_c['high_hole_diameter']))
    sys.exit(2)
  ### generate the portion outlines
  part_figure_list = []
  if(sg_c['gear_tooth_nb']>0): # create a gear_profile
    for i in range(2*split_nb):
      #print("dbg333:  portion_gear_tooth_nb[i]: {:0.3f}".format(portion_gear_tooth_nb[i]))
      #print("dbg334:  portion_gear_first_end[i]: {:0.3f}".format(portion_gear_first_end[i]))
      #print("dbg335:  portion_gear_last_end[i]: {:0.3f}".format(portion_gear_last_end[i]))
      #print("dbg336:  portion_gear_tooth_angle[i]: {:0.3f}".format(portion_gear_tooth_angle[i]))
      if(portion_gear_tooth_nb[i]<1):
        print("ERR338: Error, for i {:d} portion_gear_tooth_nb {:d} smaller than 1".format(i, portion_gear_tooth_nb[i]))
        sys.exit(2)
      gp_c['portion_tooth_nb']    = portion_gear_tooth_nb[i]
      gp_c['portion_first_end']   = portion_gear_first_end[i]
      gp_c['portion_last_end']    = portion_gear_last_end[i]
      gp_c['gear_initial_angle']  = portion_gear_tooth_angle[i]
      gp_c['simulation_enable'] = False
      #print("dbg342: gp_c:", gp_c)
      #print("dbg341: gp_c['portion_tooth_nb']: {:d}".format(gp_c['portion_tooth_nb']))
      (gear_profile_B, trash_gear_profile_parameters, trash_gear_profile_info) = gear_profile.gear_profile_dictionary_wrapper(gp_c)
      #print("dbg345: trash_gear_profile_parameters:", trash_gear_profile_parameters)
      #print("dbg346: trash_gear_profile_parameters['portion_tooth_nb']: {:d}".format(trash_gear_profile_parameters['portion_tooth_nb']))
      tmp_a = sg_c['split_initial_angle'] + (i+2.0)*portion_angle
      tmp_b = sg_c['split_initial_angle'] + (i+1.0)*portion_angle
      tmp_c = sg_c['split_initial_angle'] + (i+0.0)*portion_angle
      low_portion_A = []
      low_portion_A.append((gear_profile_B[-1][0], gear_profile_B[-1][1], 0))
      low_portion_A.append((g1_ix+high_split_radius*math.cos(tmp_a), g1_iy+high_split_radius*math.sin(tmp_a), split_router_bit_radius))
      low_portion_A.append((g1_ix+low_split_radius*math.cos(tmp_a), g1_iy+low_split_radius*math.sin(tmp_a), 0))
      if(sg_c['low_split_type']=='circle'):
        low_portion_A.append((g1_ix+low_split_radius*math.cos(tmp_b), g1_iy+low_split_radius*math.sin(tmp_b), g1_ix+low_split_radius*math.cos(tmp_c), g1_iy+low_split_radius*math.sin(tmp_c), 0))
      elif(sg_c['low_split_type']=='line'):
        low_portion_A.append((g1_ix+low_split_radius*math.cos(tmp_b), g1_iy+low_split_radius*math.sin(tmp_b), 0))
        low_portion_A.append((g1_ix+low_split_radius*math.cos(tmp_c), g1_iy+low_split_radius*math.sin(tmp_c), 0))
      low_portion_A.append((g1_ix+high_split_radius*math.cos(tmp_c), g1_iy+high_split_radius*math.sin(tmp_c), split_router_bit_radius))
      low_portion_A.append((gear_profile_B[0][0], gear_profile_B[0][1], 0))
      low_portion_B = cnc25d_api.cnc_cut_outline(low_portion_A, "portion_A")
      portion_B = gear_profile_B[:]
      portion_B.extend(low_portion_B[1:])
      #part_figure_list.append([portion_B])
      part_figure_list.append([portion_B[:]])
  else:
    for i in range(2*split_nb):
      tmp_a = sg_c['split_initial_angle'] + (i+2.0)*portion_angle
      tmp_b = sg_c['split_initial_angle'] + (i+1.0)*portion_angle
      tmp_c = sg_c['split_initial_angle'] + (i+0.0)*portion_angle
      portion_A = []
      portion_A.append((g1_ix+high_split_radius*math.cos(tmp_c), g1_iy+high_split_radius*math.sin(tmp_c), 0))
      portion_A.append((g1_ix+high_split_radius*math.cos(tmp_b), g1_iy+high_split_radius*math.sin(tmp_b), g1_ix+high_split_radius*math.cos(tmp_a), g1_iy+high_split_radius*math.sin(tmp_a), 0))
      portion_A.append((g1_ix+low_split_radius*math.cos(tmp_a), g1_iy+low_split_radius*math.sin(tmp_a), 0))
      if(sg_c['low_split_type']=='circle'):
        portion_A.append((g1_ix+low_split_radius*math.cos(tmp_b), g1_iy+low_split_radius*math.sin(tmp_b), g1_ix+low_split_radius*math.cos(tmp_c), g1_iy+low_split_radius*math.sin(tmp_c), 0))
      elif(sg_c['low_split_type']=='line'):
        portion_A.append((g1_ix+low_split_radius*math.cos(tmp_b), g1_iy+low_split_radius*math.sin(tmp_b), 0))
        portion_A.append((g1_ix+low_split_radius*math.cos(tmp_c), g1_iy+low_split_radius*math.sin(tmp_c), 0))
      portion_A.append((g1_ix+high_split_radius*math.cos(tmp_c), g1_iy+high_split_radius*math.sin(tmp_c), 0))
      portion_B = cnc25d_api.cnc_cut_outline(portion_A, "circle_portion_A")
      #part_figure_list.append([portion_B])
      part_figure_list.append([portion_B[:]])
  ### generate the hole outlines
  for i in range(len(part_figure_list)):
    hole_figure = []
    if(low_hole_radius>0):
      for j in range(2*sg_c['low_hole_nb']):
        tmp_a = sg_c['split_initial_angle'] + i*portion_angle + (j+0.5)*low_hole_space_angle
        hole_figure.append((g1_ix+low_hole_circle_radius*math.cos(tmp_a), g1_iy+low_hole_circle_radius*math.sin(tmp_a), low_hole_radius))
    if(high_hole_radius>0):
      for j in range(2*sg_c['high_hole_nb']):
        tmp_a = sg_c['split_initial_angle'] + i*portion_angle + (j+0.5)*high_hole_space_angle
        hole_figure.append((g1_ix+high_hole_circle_radius*math.cos(tmp_a), g1_iy+high_hole_circle_radius*math.sin(tmp_a), high_hole_radius))
    #part_figure_list[i].extend(hole_figure)
    part_figure_list[i].extend(hole_figure[:])

  ### design output
  sgw_assembly_figure = []
  sgw_assembly_A_figure = []
  sgw_assembly_B_figure = []
  aligned_part_figure_list = []
  sgw_list_of_parts = []
  for i in range(len(part_figure_list)):
    sgw_assembly_figure.extend(part_figure_list[i])
    if((i%2)==0):
      sgw_assembly_A_figure.extend(part_figure_list[i])
    else:
      sgw_assembly_B_figure.extend(part_figure_list[i])
    aligned_part_figure_list.append([])
    shift_x = 2.2 * (i%2) * minimal_gear_profile_radius
    shift_y = 2.2 * int(i/2) * minimal_gear_profile_radius
    for j in range(len(part_figure_list[i])):
      rotated_outline = cnc25d_api.outline_rotate(part_figure_list[i][j], g1_ix, g1_iy, -1*(sg_c['split_initial_angle'] + i*portion_angle))
      aligned_part_figure_list[i].append(rotated_outline)
      sgw_list_of_parts.append(cnc25d_api.outline_shift_xy(rotated_outline, shift_x, 1, shift_y, 1))
  # ideal_outline in overlay
  sgw_assembly_figure_overlay = part_figure_list[0]
  # sgw_parameter_info
  sgw_parameter_info = "\nSplit-Gearwheel parameter info:\n"
  sgw_parameter_info += "\n" + sg_c['args_in_txt'] + "\n\n"
  sgw_parameter_info += gear_profile_info
  sgw_parameter_info += """
split_nb:             \t{:d}
split_initial_angle:  \t{:0.3f} (radian)  \t{:0.3f} (degree)
high_split_radius:    \t{:0.3f} diameter: \t{:0.3f}
high_split_type:      \t{:s}
""".format(split_nb, sg_c['split_initial_angle'], sg_c['split_initial_angle']*180/math.pi, high_split_radius, 2*high_split_radius, sg_c['high_split_type'])
  sgw_parameter_info += """
low_split_radius:     \t{:0.3f} diameter: \t{:0.3f}
low_split_type:       \t{:s}
""".format(low_split_radius, 2*low_split_radius, sg_c['low_split_type'])
  sgw_parameter_info += """
low_hole_circle_radius:   \t{:0.3f} diameter: \t{:0.3f}
low_hole_radius:          \t{:0.3f} diameter: \t{:0.3f}
low_hole_nb:              \t{:d}
""".format(low_hole_circle_radius, 2*low_hole_circle_radius, low_hole_radius, 2*low_hole_radius, sg_c['low_hole_nb'])
  sgw_parameter_info += """
high_hole_circle_radius:  \t{:0.3f} diameter: \t{:0.3f}
high_hole_radius:         \t{:0.3f} diameter: \t{:0.3f}
high_hole_nb:             \t{:d}
""".format(high_hole_circle_radius, 2*high_hole_circle_radius, high_hole_radius, 2*high_hole_radius, sg_c['high_hole_nb'])
  sgw_parameter_info += """
gear_router_bit_radius:   \t{:0.3f}
split_router_bit_radius:  \t{:0.3f}
cnc_router_bit_radius:    \t{:0.3f}
""".format(gear_router_bit_radius, split_router_bit_radius, sg_c['cnc_router_bit_radius'])
  #print(sgw_parameter_info)

  ### display with Tkinter
  if(sg_c['tkinter_view']):
    print(sgw_parameter_info)
    #cnc25d_api.figure_simple_display(part_figure_list[0], sgw_assembly_figure_overlay, sgw_parameter_info) # for debug
    #cnc25d_api.figure_simple_display(sgw_assembly_A_figure, part_figure_list[0], sgw_parameter_info) # for debug
    cnc25d_api.figure_simple_display(sgw_assembly_figure, sgw_assembly_figure_overlay, sgw_parameter_info)
    cnc25d_api.figure_simple_display(sgw_assembly_A_figure, sgw_assembly_B_figure, sgw_parameter_info)
    #for i in range(len(part_figure_list)):
    #  #cnc25d_api.figure_simple_display(aligned_part_figure_list[i], part_figure_list[i], sgw_parameter_info)
    #  cnc25d_api.figure_simple_display(part_figure_list[i], part_figure_list[i-1], sgw_parameter_info)
    cnc25d_api.figure_simple_display(sgw_list_of_parts, [], sgw_parameter_info)
      
  ### generate output file
  output_file_suffix = ''
  if(sg_c['output_file_basename']!=''):
    output_file_suffix = 'brep'
    output_file_basename = sg_c['output_file_basename']
    if(re.search('\.dxf$', sg_c['output_file_basename'])):
      output_file_suffix = 'dxf'
      output_file_basename = re.sub('\.dxf$', '', sg_c['output_file_basename'])
    elif(re.search('\.svg$', sg_c['output_file_basename'])):
      output_file_suffix = 'svg'
      output_file_basename = re.sub('\.svg$', '', sg_c['output_file_basename'])
  if((output_file_suffix=='svg')or(output_file_suffix=='dxf')):
    cnc25d_api.generate_output_file(sgw_assembly_figure, output_file_basename + "_assembly." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
    cnc25d_api.generate_output_file(sgw_assembly_A_figure, output_file_basename + "_assembly_A." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
    cnc25d_api.generate_output_file(sgw_assembly_B_figure, output_file_basename + "_assembly_B." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
    cnc25d_api.generate_output_file(sgw_list_of_parts, output_file_basename + "_part_list." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
    for i in range(split_nb):
      cnc25d_api.generate_output_file(part_figure_list[2*i],    output_file_basename + "_part_A{:d}_placed.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
      cnc25d_api.generate_output_file(part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_placed.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i],    output_file_basename + "_part_A{:d}_aligned.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_aligned.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
  elif(output_file_suffix=='brep'):
    #cnc25d_api.generate_output_file(sgw_assembly_figure, output_file_basename + "_assembly", sg_c['gear_profile_height'], sgw_parameter_info)
    for i in range(split_nb):
      cnc25d_api.generate_output_file(part_figure_list[2*i],    output_file_basename + "_part_A{:d}_placed".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
      cnc25d_api.generate_output_file(part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_placed".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i],    output_file_basename + "_part_A{:d}_aligned".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_aligned".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)

  #### return
  if(sg_c['return_type']=='int_status'):
    r_sgw = 1
  elif(sg_c['return_type']=='cnc25d_figure'):
    r_sgw = sgw_assembly_A_figure
  elif(sg_c['return_type']=='freecad_object'):
    r_sgw = cnc25d_api.figure_to_freecad_25d_part(part_figure_list[0], sg_c['gear_profile_height'])
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(sg_c['return_type']))
    sys.exit(2)
  return(r_sgw)

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
    ["simplest test"        , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2"],
    ["split nb 2"           , "--gear_tooth_nb 27 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 2"],
    ["split nb 3"           , "--gear_tooth_nb 26 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 3"],
    ["split nb 4"           , "--gear_tooth_nb 23 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 4"],
    ["split nb 5"           , "--gear_tooth_nb 21 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 5"],
    ["split nb 6"           , "--gear_tooth_nb 29 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 6"],
    ["split nb 7"           , "--gear_tooth_nb 31 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 7"],
    ["split nb 8"           , "--gear_tooth_nb 33 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --split_nb 8"],
    ["portion and tooth nb" , "--gear_tooth_nb 17 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0"],
    ["no tooth"             , "--gear_tooth_nb 0 --gear_primitive_diameter 200.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 3"],
    ["no low hole"          , "--gear_tooth_nb 27 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --low_hole_nb 0"],
    ["no high hole"         , "--gear_tooth_nb 28 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 0"],
    ["split style line"     , "--gear_tooth_nb 30 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --low_split_type line --split_nb 2"],
    ["split style addendum" , "--gear_tooth_nb 41 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --high_split_type a --split_nb 10"],
    ["split initial angle"  , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --split_initial_angle 0.1 --gear_initial_angle 0.15"],
    ["gear simulation"      , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --simulation_enable --second_gear_tooth_nb 19"],
    ["output file"          , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --output_file_basename test_output/split_gearwheel_self_test.dxf"],
    ["last test"            , "--gear_tooth_nb 24 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0"]]
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
  my_sgw = split_gearwheel_cli("--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2".split())
  #my_sgw = split_gearwheel_cli("--gear_tooth_nb 17 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0".split())
  #Part.show(my_sgw)

