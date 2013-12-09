# crest.py
# generates the crest, an optional part for the cross_cube assembly
# created by charlyoleg on 2013/12/07
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
crest.py generates the crest part, an optional part for the cross_cube assembly.
The main function displays in a Tk-interface the crest part, or generates the design as files or returns the design as FreeCAD Part object.
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
#import re # to detect .dxf or .svg
#import Tkinter # to display the outline in a small GUI
#
import Part
#from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import cross_cube
import gear_profile

################################################################
# crest dictionary-arguments default values
################################################################

def crest_dictionary_init(ai_variant=0):
  """ create and initiate a crest_dictionary with the default value
  """
  r_cd = {}
  # parameter inheritance from cross_cube
  r_cd.update(cross_cube.cross_cube_dictionary_init(2))
  # parameter inheritance from gear_profile
  r_cd.update(gear_profile.gear_profile_dictionary_init(4))
  ### outline
  r_cd['gear_module']         = 3.0
  r_cd['virtual_tooth_nb']    = 60
  r_cd['portion_tooth_nb']    = 30
  r_cd['free_mounting_width'] = 15.0
  ### crest_hollow
  r_cd['crest_hollow_leg_nb']  = 4 # possible values: 1(filled), 2(end-legs only), 3, 4 ...
  r_cd['end_leg_width']                     = 10.0
  r_cd['middle_leg_width']                  = 0.0
  r_cd['crest_hollow_external_diameter']    = 0.0
  r_cd['crest_hollow_internal_diameter']    = 0.0
  r_cd['floor_width']                       = 0.0
  r_cd['crest_hollow_smoothing_radius']     = 0.0
  ### gear_holes
  r_cd['fastening_hole_diameter']           = 5.0
  r_cd['fastening_hole_position']           = 0.0
  r_cd['centring_hole_diameter']            = 1.0
  r_cd['centring_hole_distance']            = 8.0
  r_cd['centring_hole_position']            = 0.0
  ## part thickness
  r_cd['crest_thickness']                   = 5.0
  ### manufacturing
  r_cd['crest_cnc_router_bit_radius']       = 0.5
  ### output
  if(ai_variant!=1):
    r_cd['tkinter_view']           = False
    r_cd['output_file_basename']   = ''
    r_cd['args_in_txt'] = ""
    r_cd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_cd)

################################################################
# crest argparse
################################################################

def crest_add_argument(ai_parser, ai_variant=0):
  """
  Add arguments relative to the crest
  This function intends to be used by the crest_cli and crest_self_test
  """
  r_parser = ai_parser
  # parameter inheritance from cross_cube
  r_parser = cross_cube.cross_cube_add_argument(r_parser, 2)
  # parameter inheritance from gear_profile
  r_parser = gear_profile.gear_profile_add_argument(r_parser, 4)
  ### outline
  r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=3.0, dest='sw_gear_module',
    help="Set the gear-module of the crest. Default: 3.0")
  r_parser.add_argument('--virtual_tooth_nb','--vtn', action='store', type=int, default=60, dest='sw_virtual_tooth_nb',
    help="Set the virtual number of gear-teeth of the crest. Default: 60")
  r_parser.add_argument('--portion_tooth_nb','--ptn', action='store', type=int, default=30, dest='sw_portion_tooth_nb',
    help="Set the number of teeth of the gear-portion of the crest. Default: 30")
  r_parser.add_argument('--free_mounting_width','--fmw', action='store', type=float, default=15.0, dest='sw_free_mounting_width',
    help="Set the width that must be kept free to mount the crest in a cross_cube (minimum: face_B1_thickness + cnc_router_bit_radius). Default: 15.0")
  ### crest_hollow
  r_parser.add_argument('--crest_hollow_leg_nb','--chln', action='store', type=int, default=4, dest='sw_crest_hollow_leg_nb',
    help="Set the number of crest-hollow_legs. Possible values: 1(filled), 2(end-legs only), 3, 4, etc. Default: 4")
  r_parser.add_argument('--end_leg_width','--elw', action='store', type=float, default=10.0, dest='sw_end_leg_width',
    help="Set the width of the two end-legs of the crest. Default: 10.0")
  r_parser.add_argument('--middle_leg_width','--mlw', action='store', type=float, default=0.0, dest='sw_middle_leg_width',
    help="Set the width of the middle-legs of the crest. If equal to 0.0, set to end_leg_width. Default: 0.0")
  r_parser.add_argument('--crest_hollow_external_diameter','--ched', action='store', type=float, default=0.0, dest='sw_crest_hollow_external_diameter',
    help="Set the diameter of the crest-hollow-external circle. If equal to 0.0, set to gear_hollow_radius - delta. Default: 0.0")
  r_parser.add_argument('--crest_hollow_internal_diameter','--chid', action='store', type=float, default=0.0, dest='sw_crest_hollow_internal_diameter',
    help="Set the diameter of the crest-hollow-internal circle. If equal to 0.0, set to minimal_crest_hollow_internal_radius. Default: 0.0")
  r_parser.add_argument('--floor_width','--fw', action='store', type=float, default=0.0, dest='sw_floor_width',
    help="Set the width between the cross_cube-top-holes and the crest-gear-hollow. If equal to 0.0, set to end_leg_width. Default: 0.0")
  r_parser.add_argument('--crest_hollow_smoothing_radius','--chsr', action='store', type=float, default=0.0, dest='sw_crest_hollow_smoothing_radius',
    help="Set the smoothing radius for the crest-hollow. If equal to 0.0, set to 0.5*maximal_crest_hollow_smoothing_radius. Default: 0.0")
  ### gear_holes
  r_parser.add_argument('--fastening_hole_diameter','--fhd', action='store', type=float, default=5.0, dest='sw_fastening_hole_diameter',
    help="Set the diameter of the crest-gear-fastening-holes. Default: 5.0")
  r_parser.add_argument('--fastening_hole_position','--fhp', action='store', type=float, default=0.0, dest='sw_fastening_hole_position',
    help="Set the position relative to the gear-hollow-external circle of the crest-gear-fastening-holes. Default: 0.0")
  r_parser.add_argument('--centring_hole_diameter','--chd', action='store', type=float, default=1.0, dest='sw_centring_hole_diameter',
    help="Set the diameter of the crest-gear-centring-holes. Default: 1.0")
  r_parser.add_argument('--centring_hole_distance','--chdi', action='store', type=float, default=8.0, dest='sw_centring_hole_distance',
    help="Set the distance between a pair of crest-gear-centring-holes. Default: 8.0")
  r_parser.add_argument('--centring_hole_position','--chp', action='store', type=float, default=0.0, dest='sw_centring_hole_position',
    help="Set the position relative to the gear-hollow-external circle of the crest-gear-centring-holes. Default: 0.0")
  ## part thickness
  r_parser.add_argument('--crest_thickness','--ct', action='store', type=float, default=5.0, dest='sw_crest_thickness',
    help="Set the thickness (z-size) of the crest. Default: 5.0")
  ### manufacturing
  r_parser.add_argument('--crest_cnc_router_bit_radius','--ccrbr', action='store', type=float, default=0.5, dest='sw_crest_cnc_router_bit_radius',
    help="Set the minimal router_bit radius for the crest part. Default: 0.5")
  ### manufacturing
  r_parser.add_argument('--bagel_extra_cut_thickness','--bgect', action='store', type=float, default=0.0, dest='sw_bagel_extra_cut_thickness',
    help="Set the extra-cut-thickness for the internal-bagel cut. It can be used to compensate the manufacturing process or to check the 3D assembly with FreeCAD. Default: 0.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def crest(ai_constraints):
  """
  The main function of the script.
  It generates a crest assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  cdi = crest_dictionary_init()
  c_c = cdi.copy()
  c_c.update(ai_constraints)
  #print("dbg155: c_c:", c_c)
  if(len(c_c.viewkeys() & cdi.viewkeys()) != len(c_c.viewkeys() | cdi.viewkeys())): # check if the dictionary c_c has exactly all the keys compare to crest_dictionary_init()
    print("ERR148: Error, c_c has too much entries as {:s} or missing entries as {:s}".format(c_c.viewkeys() - cdi.viewkeys(), cdi.viewkeys() - c_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: crest constraints:")
  #for k in c_c.viewkeys():
  #  if(c_c[k] != cdi[k]):
  #    print("dbg166: for k {:s}, c_c[k] {:s} != cdi[k] {:s}".format(k, str(c_c[k]), str(cdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  ### outline
  #gear_module
  if(c_c['gear_module']<radian_epsilon):
    print("ERR194: Error, gear_module {:0.3f} must be strictly positive".format(c_c['gear_module']))
    sys.exit(2)
  #virtual_tooth_nb
  if((c_c['virtual_tooth_nb']-3)*c_c['gear_module']<0.9*c_c['cube_width']):
    print("ERR198: Error, virtual_tooth_nb {:d} is too small compare to gear_module {:0.3f} and cube_width {:0.3f}".format(c_c['virtual_tooth_nb'], c_c['gear_module'], c_c['cube_width']))
    sys.exit(2)
  gear_hollow_radius = (c_c['virtual_tooth_nb']-2)*c_c['gear_module']/2.0
  minimal_gear_portion_angle = 2*math.asin(c_c['cube_width']/(2.0*gear_hollow_radius))
  maximal_gear_portion_angle = 2*(math.pi-math.asin((c_c['cube_width']/2.0+c_c['free_mounting_width'])/gear_hollow_radius))
  #portion_tooth_nb
  gear_portion_angle = 2*math.pi*(c_c['portion_tooth_nb']+1)/c_c['virtual_tooth_nb']
  if(gear_portion_angle<minimal_gear_portion_angle):
    print("ERR205: Error, portion_tooth_nb {:d} is too small compare to gear_module {:0.3f}, virtual_tooth_nb {:d} and cube_width {:0.3f}".format(c_c['portion_tooth_nb'], c_c['gear_module'], c_c['virtual_tooth_nb'], c_c['cube_width']))
    sys.exit(2)
  if(gear_portion_angle>maximal_gear_portion_angle):
    print("ERR208: Error, portion_tooth_nb {:d} is too big compare to gear_module {:0.3f}, virtual_tooth_nb {:d}, free_mounting_width {:0.3f} and cube_width {:0.3f}".format(c_c['portion_tooth_nb'], c_c['gear_module'], c_c['virtual_tooth_nb'], c_c['free_mounting_width'], c_c['cube_width']))
    sys.exit(2)
  #free_mounting_width
  if(c_c['free_mounting_width']<max(c_c['face_B1_thickness'], c_c['face_B2_thickness'])+c_c['crest_cnc_router_bit_radius']):
    print("ERR212: Error, free_mounting_width {:0.3f} is too small compare to face_B1_thickness {:0.3f}, face_B2_thickness {:0.3f} and crest_cnc_router_bit_radius {:0.3f}".format(c_c['free_mounting_width'], c_c['face_B1_thickness'], c_c['face_B2_thickness'], c_c['crest_cnc_router_bit_radius']))
    sys.exit(2)
  if(c_c['free_mounting_width']+c_c['cube_width']/2.0>gear_hollow_radius):
    print("ERR215: Error, free_mounting_width {:0.3f} is too big compare to cube_width {:0.3f} and gear_hollow_radius {:0.3f}".format(c_c['free_mounting_width'], c_c['cube_width'], gear_hollow_radius))
    sys.exit(2)
  ### crest_hollow
  #crest_hollow_leg_nb # possible values: 1(filled), 2(end-legs only), 3, 4 ...
  if(c_c['crest_hollow_leg_nb']<1):
    print("ERR220: Error, crest_hollow_leg_nb {:d} must be bigger or equal to 1".format(c_c['crest_hollow_leg_nb']))
    sys.exit(2)
  #end_leg_width
  if(c_c['end_leg_width']<radian_epsilon):
    print("ERR224: Error, end_leg_width {:0.3f} must be strictly positive".format(c_c['end_leg_width']))
    sys.exit(2)
  if(c_c['end_leg_width']>0.7*2*math.pi*gear_hollow_radius*gear_portion_angle/c_c['crest_hollow_leg_nb']):
    print("ERR228: Error, end_leg_width {:0.3f} is too big compare to gear_hollow_radius {:0.3f}, gear_portion_angle {:0.3f} and crest_hollow_leg_nb {:d}".format(c_c['end_leg_width'], gear_hollow_radius, gear_portion_angle, c_c['crest_hollow_leg_nb']))
    sys.exit(2)
  #middle_leg_width
  if(c_c['middle_leg_width']==0):
    c_c['middle_leg_width'] = c_c['end_leg_width']
  if(c_c['middle_leg_width']<radian_epsilon):
    print("ERR232: Error, middle_leg_width {:0.3f} must be strictly positive".format(c_c['middle_leg_width']))
    sys.exit(2)
  if(c_c['middle_leg_width']>0.7*2*math.pi*gear_hollow_radius*gear_portion_angle/c_c['crest_hollow_leg_nb']):
    print("ERR235: Error, middle_leg_width {:0.3f} is too big compare to gear_hollow_radius {:0.3f}, gear_portion_angle {:0.3f} and crest_hollow_leg_nb {:d}".format(c_c['middle_leg_width'], gear_hollow_radius, gear_portion_angle, c_c['crest_hollow_leg_nb']))
    sys.exit(2)
  #crest_hollow_external_diameter
  c_c['crest_hollow_external_radius'] = c_c['crest_hollow_external_diameter']/2.0
  if(c_c['crest_hollow_external_radius']==0):
    c_c['crest_hollow_external_radius'] = gear_hollow_radius - 1.5*c_c['gear_module']
  if(c_c['crest_hollow_external_radius']>gear_hollow_radius):
    print("ERR244: Error, crest_hollow_external_radius {:0.3f} is too big compare to gear_hollow_radius {:0.3f}".format(c_c['crest_hollow_external_radius'], gear_hollow_radius))
    sys.exit(2)
  #crest_hollow_internal_diameter
  c_c['crest_hollow_internal_radius'] = c_c['crest_hollow_internal_diameter']/2.0
  minimal_crest_hollow_internal_radius = math.sqrt((c_c['cube_width']/2.0)**2+(c_c['top_thickness']+c_c['height_margin']+c_c['axle_diameter']/2.0)**2)
  if(c_c['crest_hollow_internal_radius']==0):
    c_c['crest_hollow_internal_radius'] = minimal_crest_hollow_internal_radius
  if(c_c['crest_hollow_internal_radius']<minimal_crest_hollow_internal_radius):
    print("ERR252: Error, crest_hollow_internal_radius {:0.3f} must be bigger than minimal_crest_hollow_internal_radius {:0.3f}".format(c_c['crest_hollow_internal_radius'], minimal_crest_hollow_internal_radius))
    sys.exit(2)
  #floor_width
  if(c_c['floor_width']==0):
    c_c['floor_width'] = c_c['end_leg_width']
  if(c_c['floor_width']<radian_epsilon):
    print("ERR257: Error, floor_width {:0.3f} must be strictly positive".format(c_c['floor_width']))
    sys.exit(2)
  if(c_c['floor_width']+c_c['top_thickness']+c_c['height_margin']+c_c['axle_diameter']/2.0>gear_hollow_radius):
    print("ERR260: Error, floor_width {:0.3f} is too big compare to top_thickness {:0.3f}, height_margin {:0.3f}, axle_diameter {:0.3f} and gear_hollow_radius {:0.3f}".format(c_c['floor_width'], c_c['top_thickness'], c_c['height_margin'], c_c['axle_diameter'], gear_hollow_radius))
    sys.exit(2)
  #crest_hollow_smoothing_radius
  max_leg_width = max(c_c['end_leg_width'], c_c['middle_leg_width'])
  maximal_crest_hollow_smoothing_radius = (c_c['crest_hollow_external_radius']*float(gear_portion_angle)/c_c['crest_hollow_leg_nb'] - max_leg_width)/3.0
  if(c_c['crest_hollow_smoothing_radius']==0):
    c_c['crest_hollow_smoothing_radius'] = min(0.5*maximal_crest_hollow_smoothing_radius, 0.2*abs(c_c['crest_hollow_external_radius']-c_c['crest_hollow_internal_radius']))
  if(c_c['crest_hollow_smoothing_radius']<c_c['crest_cnc_router_bit_radius']):
    print("ERR267: Error, crest_hollow_smoothing_radius {:0.3f} must be bigger than crest_cnc_router_bit_radius {:0.3f}".format(c_c['crest_hollow_smoothing_radius'], c_c['crest_cnc_router_bit_radius']))
    sys.exit(2)
  if(c_c['crest_hollow_smoothing_radius']>maximal_crest_hollow_smoothing_radius):
    print("ERR270: Error, crest_hollow_smoothing_radius {:0.3f} must be smaller than maximal_crest_hollow_smoothing_radius {:0.3f}".format(c_c['crest_hollow_smoothing_radius'], maximal_crest_hollow_smoothing_radius))
    sys.exit(2)
  if(c_c['crest_hollow_external_radius']<c_c['crest_hollow_internal_radius']+2.5*c_c['crest_hollow_smoothing_radius']):
    print("ERR265: Error, crest_hollow_external_radius {:0.3f} is too small compare to crest_hollow_internal_radius {:0.3f} and crest_hollow_smoothing_radius {:0.3f}".format(c_c['crest_hollow_external_radius'], c_c['crest_hollow_internal_radius'], c_c['crest_hollow_smoothing_radius']))
    sys.exit(2)
  ### gear_holes
  #fastening_hole_diameter
  c_c['fastening_hole_radius'] = c_c['fastening_hole_diameter']/2.0
  #fastening_hole_position
  if(c_c['crest_hollow_external_radius'] + c_c['fastening_hole_position'] + c_c['fastening_hole_radius']>gear_hollow_radius):
    print("ERR282: Error, fastening_hole_position {:0.3f} or fastening_hole_radius {:0.3f} are too big compare to crest_hollow_external_radius {:0.3f} and gear_hollow_radius {:0.3f}".format(c_c['fastening_hole_position'], c_c['fastening_hole_radius'], c_c['crest_hollow_external_radius'], gear_hollow_radius))
    sys.exit(2)
  #centring_hole_diameter
  c_c['centring_hole_radius'] = c_c['centring_hole_diameter']/2.0
  #centring_hole_distance
  if(c_c['centring_hole_distance']<2.1*c_c['centring_hole_radius']):
    print("ERR288: Error, centring_hole_distance {:0.3f} is too small compare to centring_hole_radius {:0.3f}".format(c_c['centring_hole_distance'], c_c['centring_hole_radius']))
    sys.exit(2)
  #centring_hole_position
  if(c_c['crest_hollow_external_radius'] + c_c['centring_hole_position'] + c_c['centring_hole_radius']>gear_hollow_radius):
    print("ERR292: Error, centring_hole_position {:0.3f} or centring_hole_radius {:0.3f} are too big compare to crest_hollow_external_radius {:0.3f} and gear_hollow_radius {:0.3f}".format(c_c['centring_hole_position'], c_c['centring_hole_radius'], c_c['crest_hollow_external_radius'], gear_hollow_radius))
    sys.exit(2)
  ## part thickness
  #crest_thickness
  if(c_c['crest_thickness']<radian_epsilon):
    print("ERR297: Error, crest_thickness {:0.3f} must be strictly positive".format(c_c['crest_thickness']))
    sys.exit(2)
  ### manufacturing
  #crest_cnc_router_bit_radius
  if(c_c['gear_router_bit_radius']<c_c['crest_cnc_router_bit_radius']):
    c_c['gear_router_bit_radius'] = c_c['crest_cnc_router_bit_radius']
  if(c_c['cross_cube_cnc_router_bit_radius']<c_c['crest_cnc_router_bit_radius']):
    c_c['cross_cube_cnc_router_bit_radius'] = c_c['crest_cnc_router_bit_radius']

  ################################################################
  # outline construction
  ################################################################
  
  cx = c_c['cube_width']/2.0
  cy = c_c['top_thickness']+c_c['height_margin']+c_c['axle_diameter']/2.0+c_c['inter_axle_length']

  # inheritance from cross_cube
  cc_ci = cross_cube.cross_cube_dictionary_init()
  cc_c = dict([ (k, c_c[k]) for k in cc_ci.viewkeys() & cdi.viewkeys() ]) # extract only the entries of the intersection of cross_cube and crest
  cc_c['tkinter_view'] = False
  cc_c['output_file_basename'] = ''
  cc_c['args_in_txt'] = "cross_cube for crest"
  cc_c['return_type'] = 'outlines_for_crest' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object', 'outlines_for_crest'
  (bottom_outline_A, cross_cube_hole_figure_A, cross_cube_info) = cross_cube.cross_cube(cc_c)

  # inheritance from gear_profile
  gp_ci = gear_profile.gear_profile_dictionary_init()
  gp_c = dict([ (k, c_c[k]) for k in gp_ci.viewkeys() & cdi.viewkeys() ]) # extract only the entries of the intersection of gear_profile and crest
  gp_c['gear_type'] = 'e'
  gp_c['gear_module'] = c_c['gear_module']
  gp_c['gear_tooth_nb'] = c_c['virtual_tooth_nb']
  gp_c['portion_tooth_nb'] = c_c['portion_tooth_nb']
  gp_c['portion_first_end'] = 2 # slope-bottom
  gp_c['portion_last_end'] = 2 # slope-bottom
  gp_c['center_position_x'] = cx
  gp_c['center_position_y'] = cy
  gp_c['gear_initial_angle'] = math.pi/2-math.pi*(c_c['portion_tooth_nb']-0)/c_c['virtual_tooth_nb']
  gp_c['output_file_basename'] = ''
  gp_c['args_in_txt'] = "gear_profile for crest"
  gp_c['return_type'] = 'figure_param_info' # 'int_status', 'cnc25d_figure', 'freecad_object', 'figure_param_info'
  (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile(gp_c)
  # gear_profile check
  if(abs(gear_profile_B[0][1]-gear_profile_B[-1][-1])>radian_epsilon):
    print("ERR335: Error, extremities of the gear_profile_B have different y-coordiante {:0.3f} {:0.3f}".format(gear_profile_B[0][1], gear_profile_B[-1][-1]))
    sys.exit(2)
  # gear_profile extremity angle
  crest_gear_angle = math.atan2(gear_profile_B[0][1]-cy, gear_profile_B[0][0]-cx)
 
  ## crest outline
  cube_height = 2*c_c['top_thickness']+2*c_c['height_margin']+c_c['axle_diameter']+c_c['inter_axle_length']
  crest_long_nshort = True
  free_mounting_width = c_c['free_mounting_width']
  if(gear_profile_B[0][1]>3*cube_height/4.0+radian_epsilon):
    crest_long_nshort = False
    free_mounting_width = c_c['crest_cnc_router_bit_radius']
  crest_outline_A = []
  crest_outline_A.append((gear_profile_B[-1][-2], gear_profile_B[-1][-1], 0))
  crest_outline_A.append((cx+c_c['crest_hollow_external_radius']*math.cos(math.pi-crest_gear_angle), cy+c_c['crest_hollow_external_radius']*math.sin(math.pi-crest_gear_angle), c_c['crest_cnc_router_bit_radius']))
  crest_outline_A.append((bottom_outline_A[0][0]-free_mounting_width, bottom_outline_A[0][1], c_c['crest_cnc_router_bit_radius']))
  crest_outline_A.extend(bottom_outline_A[1:-1])
  crest_outline_A.append((bottom_outline_A[-1][0]+free_mounting_width, bottom_outline_A[-1][1], c_c['crest_cnc_router_bit_radius']))
  crest_outline_A.append((cx+c_c['crest_hollow_external_radius']*math.cos(crest_gear_angle), cy+c_c['crest_hollow_external_radius']*math.sin(crest_gear_angle), c_c['crest_cnc_router_bit_radius']))
  crest_outline_A.append((gear_profile_B[0][0], gear_profile_B[0][1], 0))
  crest_outline_B = cnc25d_api.cnc_cut_outline(crest_outline_A, "crest_outline_A")
  crest_outline_B.extend(gear_profile_B[1:])
  crest_outline_B_overlay = cnc25d_api.ideal_outline(crest_outline_A, "crest_outline_A") # overlay
  crest_outline_B_overlay.extend(gear_profile_B[1:])
  ## crest holes
  crest_hole_A = []
  crest_hole_A.extend(cross_cube_hole_figure_A) 
  # cross_cube top holes
  ccthy = cy + c_c['axle_diameter']/2.0+c_c['height_margin']
  cw5 = c_c['cube_width']/5
  tt = c_c['top_thickness']
  ccect = c_c['cross_cube_extra_cut_thickness']
  cccrbr = c_c['cross_cube_cnc_router_bit_radius']
  cc_top_hole = []
  cc_top_hole.append((-1*ccect, -1*ccect, -1*cccrbr))
  cc_top_hole.append((cw5+1*ccect, -1*ccect, -1*cccrbr))
  cc_top_hole.append((cw5+1*ccect, tt+1*ccect, -1*cccrbr))
  cc_top_hole.append((-1*ccect, tt+1*ccect, -1*cccrbr))
  cc_top_hole.append((-1*ccect, -1*ccect, 0))
  crest_hole_A.append(cnc25d_api.outline_shift_xy(cc_top_hole, 1*cw5, 1, ccthy, 1))
  crest_hole_A.append(cnc25d_api.outline_shift_xy(cc_top_hole, 3*cw5, 1, ccthy, 1))
  # crest hollow
  cher = c_c['crest_hollow_external_radius']
  chir = c_c['crest_hollow_internal_radius']
  chln = c_c['crest_hollow_leg_nb']
  chsr = c_c['crest_hollow_smoothing_radius']
  if(crest_long_nshort):
    first_leg_ex_angle = math.asin((c_c['end_leg_width']+3*cube_height/4.0-cy)/cher)
    first_leg_in_angle = math.asin((c_c['end_leg_width']+3*cube_height/4.0-cy)/chir)
    first_leg_hole_angle = math.asin((c_c['end_leg_width']/2.0+3*cube_height/4.0-cy)/cher)
  else:
    first_leg_ex_angle = crest_gear_angle + 2*math.atan(c_c['end_leg_width']/(2.0*cher))
    first_leg_in_angle = crest_gear_angle + 2*math.atan(c_c['end_leg_width']/(2.0*chir))
    first_leg_hole_angle = crest_gear_angle + math.atan(c_c['end_leg_width']/(2.0*cher))
  if(c_c['crest_hollow_leg_nb']>1):
    leg_step_angle = 0
    if(chln>2):
      leg_step_angle = (math.pi-2*first_leg_ex_angle)/(chln-1)
    middle_leg_ex_half_angle = math.atan(c_c['middle_leg_width']/(2.0*cher))
    middle_leg_in_half_angle = math.atan(c_c['middle_leg_width']/(2.0*chir))
    smoothing_ex_half_angle = math.atan(float(chsr)/(cher-chsr))
    smoothing_in_half_angle = math.atan(float(chsr)/(chir+chsr))
    ex1_angles = []
    ex2_angles = []
    ex1_angles.append(first_leg_ex_angle)
    for i in range(chln-2):
      ex1_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle + middle_leg_ex_half_angle)
      ex2_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle - middle_leg_ex_half_angle)
    ex2_angles.append(math.pi-first_leg_ex_angle)
    in1_angles = []
    in2_angles = []
    in1_angles.append(first_leg_in_angle)
    for i in range(chln-2):
      in1_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle + middle_leg_in_half_angle)
      in2_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle - middle_leg_in_half_angle)
    in2_angles.append(math.pi-first_leg_in_angle)
    for i in range(chln-1):
      ea1 = ex1_angles[i]
      ea2 = ex2_angles[i]
      ma = (ex1_angles[i]+ex2_angles[i])/2.0
      ia1 = in1_angles[i]
      ia2 = in2_angles[i]
      if((ea2-ea1)<2.1*smoothing_ex_half_angle):
        print("ERR419: Error, crest_hollow_smoothing_radius {:0.3f} or crest_hollow_leg_nb {:d} are too big".format(chsr, chln))
        sys.exit(2)
      hollow = []
      hollow.append((cx+cher*math.cos(ea1), cy+cher*math.sin(ea1), chsr))
      hollow.append((cx+cher*math.cos(ma), cy+cher*math.sin(ma), cx+cher*math.cos(ea2), cy+cher*math.sin(ea2), chsr))
      if((ia2-ia1)<2.1*smoothing_in_half_angle):
        hollow.append((cx+chir*math.cos(ma), cy+chir*math.sin(ma), chsr))
      else:
        hollow.append((cx+chir*math.cos(ia2), cy+chir*math.sin(ia2), chsr))
        hollow.append((cx+chir*math.cos(ma), cy+chir*math.sin(ma), cx+chir*math.cos(ia1), cy+chir*math.sin(ia1), chsr))
      hollow.append((cx+cher*math.cos(ea1), cy+cher*math.sin(ea1), 0))
      crest_hole_A.append(hollow[:])
      #[todo] optimization with floor_width
  # crest gear holes
  hole_half_angle = math.atan(c_c['centring_hole_distance']/(2.0*(cher+c_c['centring_hole_position'])))
  hole_step_angle = 0
  if(chln>2):
    hole_step_angle = (math.pi-2*first_leg_hole_angle)/(chln-1)
  hole_angles = []
  hole_angles.append(first_leg_hole_angle)
  for i in range(chln-2):
    #hole_angles.append(first_leg_hole_angle + (i+1)*hole_step_angle)
    hole_angles.append(first_leg_ex_angle + (i+1)*leg_step_angle)
  hole_angles.append(math.pi-first_leg_hole_angle)
  for a in hole_angles:
    crest_hole_A.append((cx+(cher+c_c['fastening_hole_position'])*math.cos(a), cy+(cher+c_c['fastening_hole_position'])*math.sin(a), c_c['fastening_hole_radius']))
    crest_hole_A.append((cx+(cher+c_c['centring_hole_position'])*math.cos(a-hole_half_angle), cy+(cher+c_c['centring_hole_position'])*math.sin(a-hole_half_angle), c_c['centring_hole_radius']))
    crest_hole_A.append((cx+(cher+c_c['centring_hole_position'])*math.cos(a+hole_half_angle), cy+(cher+c_c['centring_hole_position'])*math.sin(a+hole_half_angle), c_c['centring_hole_radius']))
  ## crest figure
  crest_figure = []
  crest_figure.append(crest_outline_B)
  crest_figure.extend(cnc25d_api.cnc_cut_figure(crest_hole_A, "crest_hole_A"))
  crest_figure_overlay = []
  crest_figure_overlay.append(crest_outline_B_overlay)
  crest_figure_overlay.extend(cnc25d_api.ideal_figure(crest_hole_A, "crest_hole_A"))


  ################################################################
  # output
  ################################################################

  # c_parameter_info
  c_parameter_info = "\ncrest parameter info:\n"
  c_parameter_info += "\n" + c_c['args_in_txt'] + "\n"
  c_parameter_info += """
crest gear:
gear_module:          {:0.3f}
virtual_tooth_nb:     {:d}
portion_tooth_nb:     {:d}
free_mounting_width:  {:0.3f}
""".format(c_c['gear_module'], c_c['virtual_tooth_nb'], c_c['portion_tooth_nb'], c_c['free_mounting_width'])
  c_parameter_info += """
crest hollow:
crest_hollow_leg_nb:            {:d}
end_leg_width:                  {:0.3f}
middle_leg_width:               {:0.3f}
crest_hollow_external_radius:   {:0.3f}   diameter: {:0.3f}
crest_hollow_internal_radius:   {:0.3f}   diameter: {:0.3f}
floor_width:                    {:0.3f}
crest_hollow_smoothing_radius:  {:0.3f}
""".format(c_c['crest_hollow_leg_nb'], c_c['end_leg_width'], c_c['middle_leg_width'], c_c['crest_hollow_external_radius'], 2*c_c['crest_hollow_external_radius'], c_c['crest_hollow_internal_radius'], 2*c_c['crest_hollow_internal_radius'], c_c['floor_width'], c_c['crest_hollow_smoothing_radius'])
  c_parameter_info += """
gear holes:
fastening_hole_radius:    {:0.3f}   diameter: {:0.3f}
fastening_hole_position:  {:0.3f}
centring_hole_radius:     {:0.3f}   diameter: {:0.3f}
centring_hole_distance:   {:0.3f}
centring_hole_position:   {:0.3f}
""".format(c_c['fastening_hole_radius'], 2*c_c['fastening_hole_radius'], c_c['fastening_hole_position'], c_c['centring_hole_radius'], 2*c_c['centring_hole_radius'], c_c['centring_hole_distance'], c_c['centring_hole_position'])
  c_parameter_info += """
crest manufacturing:
crest_cnc_router_bit_radius: {:0.3f}
""".format(c_c['crest_cnc_router_bit_radius'])

  ### figures output
  # crest_figure
  # crest_figure_overlay

  ### display with Tkinter
  if(c_c['tkinter_view']):
    print(c_parameter_info)
    cnc25d_api.figure_simple_display(crest_figure, crest_figure_overlay, c_parameter_info)

  ### generate output file
  if(c_c['output_file_basename']!=''):
    (output_file_basename, output_file_suffix) = cnc25d_api.get_output_file_suffix(c_c['output_file_basename'])
    # parts
    cnc25d_api.generate_output_file(crest_figure, output_file_basename + "_crest" + output_file_suffix, c_c['crest_thickness'], c_parameter_info)

  #### return
  if(c_c['return_type']=='int_status'):
    r_c = 1
  elif(c_c['return_type']=='cnc25d_figure'):
    r_c = crest_figure
  elif(c_c['return_type']=='freecad_object'):
    r_c = cnc25d_api.figure_to_freecad_25d_part(crest_figure, c_c['crest_thickness'])
  elif(c_c['return_type']=='figures_3dconf_info'):
    r_c = ([crest_figure], [], c_parameter_info)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(c_c['return_type']))
    sys.exit(2)
  return(r_c)

################################################################
# crest wrapper dance
################################################################

def crest_argparse_to_dictionary(ai_c_args, ai_variant=0):
  """ convert a crest_argparse into a crest_dictionary
  """
  r_cd = {}
  # parameter inheritance from cross_cube
  r_cd.update(cross_cube.cross_cube_argparse_to_dictionary(ai_c_args, 2))
  # parameter inheritance from gear_profile
  r_cd.update(gear_profile.gear_profile_argparse_to_dictionary(ai_c_args, 4))
  ### outline
  r_cd['gear_module']         = ai_c_args.sw_gear_module
  r_cd['virtual_tooth_nb']    = ai_c_args.sw_virtual_tooth_nb
  r_cd['portion_tooth_nb']    = ai_c_args.sw_portion_tooth_nb
  r_cd['free_mounting_width'] = ai_c_args.sw_free_mounting_width
  ### crest_hollow
  r_cd['crest_hollow_leg_nb']  = ai_c_args.sw_crest_hollow_leg_nb
  r_cd['end_leg_width']                     = ai_c_args.sw_end_leg_width
  r_cd['middle_leg_width']                  = ai_c_args.sw_middle_leg_width
  r_cd['crest_hollow_external_diameter']    = ai_c_args.sw_crest_hollow_external_diameter
  r_cd['crest_hollow_internal_diameter']    = ai_c_args.sw_crest_hollow_internal_diameter
  r_cd['floor_width']                       = ai_c_args.sw_floor_width
  r_cd['crest_hollow_smoothing_radius']     = ai_c_args.sw_crest_hollow_smoothing_radius
  ### gear_holes
  r_cd['fastening_hole_diameter']           = ai_c_args.sw_fastening_hole_diameter
  r_cd['fastening_hole_position']           = ai_c_args.sw_fastening_hole_position
  r_cd['centring_hole_diameter']            = ai_c_args.sw_centring_hole_diameter
  r_cd['centring_hole_distance']            = ai_c_args.sw_centring_hole_distance
  r_cd['centring_hole_position']            = ai_c_args.sw_centring_hole_position
  ## part thickness
  r_cd['crest_thickness']                   = ai_c_args.sw_crest_thickness
  ### manufacturing
  r_cd['crest_cnc_router_bit_radius']       = ai_c_args.sw_crest_cnc_router_bit_radius
  ### output
  if(ai_variant!=1):
    #r_cd['tkinter_view']           = False
    r_cd['output_file_basename']   = ai_c_args.sw_output_file_basename
    #r_cd['args_in_txt'] = ""
    r_cd['return_type'] = ai_c_args.sw_return_type
  #### return
  return(r_cd)
  
def crest_argparse_wrapper(ai_c_args, ai_args_in_txt=""):
  """
  wrapper function of crest() to call it using the crest_parser.
  crest_parser is mostly used for debug and non-regression tests.
  """
  # view the crest with Tkinter as default action
  tkinter_view = True
  if(ai_c_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  cd = crest_argparse_to_dictionary(ai_c_args)
  cd['args_in_txt'] = ai_args_in_txt
  cd['tkinter_view'] = tkinter_view
  #cd['return_type'] = 'int_status'
  r_c = crest(cd)
  return(r_c)

################################################################
# self test
################################################################

def crest_self_test():
  """
  This is the non-regression test of crest.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , ""],
    ["short and no leg"  , "--portion_tooth_nb 20 --crest_hollow_leg_nb 1"],
    ["short and end-legs"  , "--portion_tooth_nb 20 --crest_hollow_leg_nb 2"],
    ["short and 3 legs"  , "--portion_tooth_nb 20 --crest_hollow_leg_nb 3"],
    ["short and 4 legs"  , "--portion_tooth_nb 20 --crest_hollow_leg_nb 4"],
    ["long and no leg"  , "--portion_tooth_nb 35 --crest_hollow_leg_nb 1"],
    ["long and end-legs"  , "--portion_tooth_nb 35 --crest_hollow_leg_nb 2"],
    ["long and 5 legs"  , "--portion_tooth_nb 35 --crest_hollow_leg_nb 5"],
    ["extra cut" , "--cross_cube_extra_cut_thickness 1.0"],
    ["extra cut negative" , "--cross_cube_extra_cut_thickness -0.5"],
    ["outputfile" , "--output_file_basename test_output/crest_self_test.dxf"],
    ["last test"            , ""]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  crest_parser = argparse.ArgumentParser(description='Command line interface for the function crest().')
  crest_parser = crest_add_argument(crest_parser)
  crest_parser = cnc25d_api.generate_output_file_add_argument(crest_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = crest_parser.parse_args(l_args)
    r_cst = crest_argparse_wrapper(st_args)
  return(r_cst)

################################################################
# crest command line interface
################################################################

def crest_cli(ai_args=""):
  """ command line interface of crest.py when it is used in standalone
  """
  # crest parser
  crest_parser = argparse.ArgumentParser(description='Command line interface for the function crest().')
  crest_parser = crest_add_argument(crest_parser)
  crest_parser = cnc25d_api.generate_output_file_add_argument(crest_parser, 1)
  # switch for self_test
  crest_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the result in a Tk window.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "crest arguments: " + ' '.join(effective_args)
  c_args = crest_parser.parse_args(effective_args)
  print("dbg111: start making crest")
  if(c_args.sw_run_self_test):
    r_c = crest_self_test()
  else:
    r_c = crest_argparse_wrapper(c_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_c)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("crest.py says hello!\n")
  my_c = crest_cli()
  #my_c = crest_cli("--cross_cube_extra_cut_thickness 1.0 --return_type freecad_object")
  try: # depending on c_c['return_type'] it might be or not a freecad_object
    Part.show(my_c)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


