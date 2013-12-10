# cross_cubes_sub.py
# sub-module of the cross-cube design
# created by charlyoleg on 2013/12/09
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
cross_cube_sub.py is a sub-module of cross_cube.py.
The functions of the cross_cube design have been split into the two modules cross_cube_sub.py and cross_cube.py to enable the inheritance to and from crest.py
inheritance chain: cross_cube_sub.py > crest.py > cross_cube.py
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

################################################################
# cross_cube dictionary-arguments default values
################################################################

def cross_cube_sub_dictionary_init(ai_variant=0):
  """ create and initiate a cross_cube_sub dictionary with the default value
  ai_variant = 1 : for cross_cube directly
  ai_variant = 2 : for crest and then cross_cube
  """
  r_cc = {}
  ### face A1, A2, B1 and B2
  # height
  if(ai_variant==2):
    r_cc['axle_diameter']       = 10.0
    r_cc['inter_axle_length']   = 15.0
    r_cc['height_margin']       = 10.0
    r_cc['top_thickness']       = 5.0
  # width
  if(ai_variant==2):
    r_cc['cube_width']          = 60.0
  if(ai_variant==2): # not used by crest, but anyway already settable to simplify the parameter check
    r_cc['face_A1_thickness']   = 9.0
    r_cc['face_A2_thickness']   = 7.0
  if(ai_variant==2):
    r_cc['face_B1_thickness']   = 8.0
    r_cc['face_B2_thickness']   = 6.0
  ### threaded rod
  # face
  if(ai_variant==2):
    r_cc['face_rod_hole_diameter']    = 4.0
    r_cc['face_rod_hole_h_distance']  = 5.0
    r_cc['face_rod_hole_v_distance']  = 5.0
  # top
  if(ai_variant==1):
    r_cc['top_rod_hole_diameter']     = 4.0
    r_cc['top_rod_hole_h_distance']   = 10.0
  ### hollow
  # face hollow
  if(ai_variant==2):
    r_cc['face_hollow_leg_nb']            = 1 # possible values: 1 (filled), 4, 8
    r_cc['face_hollow_border_width']      = 0.0
    r_cc['face_hollow_axle_width']        = 0.0
    r_cc['face_hollow_leg_width']         = 0.0
    r_cc['face_hollow_smoothing_radius']  = 0.0
  # top hollow
  if(ai_variant==1):
    r_cc['top_hollow_leg_nb']             = 0 # possible values: 0 (empty), 1 (filled), 4, 8
    r_cc['top_hollow_border_width']       = 0.0
    r_cc['top_hollow_leg_width']          = 0.0
    r_cc['top_hollow_smoothing_radius']   = 0.0
  ### axle
  if(ai_variant==1):
    r_cc['axle_length']                   = 0.0
    r_cc['spacer_diameter']               = 0.0
    r_cc['spacer_length']                 = 0.0
  ### manufacturing
  if(ai_variant==2):
    r_cc['cross_cube_cnc_router_bit_radius']  = 1.0
    r_cc['cross_cube_extra_cut_thickness']  = 0.0
  ### output
  #### return
  return(r_cc)

################################################################
# cross_cube_sub argparse
################################################################

def cross_cube_sub_add_argument(ai_parser, ai_variant=0):
  """
  Add arguments relative to the cross_cube_sub
  This function intends to be inherited by crest.py and cross_cube.py
  ai_variant = 1 : for cross_cube directly
  ai_variant = 2 : for crest and then cross_cube
  """
  r_parser = ai_parser
  ### face A1, A2, B1 and B2
  # height
  if(ai_variant==2):
    r_parser.add_argument('--axle_diameter','--ad', action='store', type=float, default=10.0, dest='sw_axle_diameter',
      help="Set the diameter of the two axles. Default: 10.0")
    r_parser.add_argument('--inter_axle_length','--ial', action='store', type=float, default=15.0, dest='sw_inter_axle_length',
      help="Set the length length betwen the two axle centers. Default: 15.0")
    r_parser.add_argument('--height_margin','--hm', action='store', type=float, default=10.0, dest='sw_height_margin',
      help="Set the length betwen the axle peripheral and the inner edge of the top. Default: 10.0")
    r_parser.add_argument('--top_thickness','--tt', action='store', type=float, default=5.0, dest='sw_top_thickness',
      help="Set the thickness of the top part. Default: 5.0")
  # width
  if(ai_variant==2):
    r_parser.add_argument('--cube_width','--cw', action='store', type=float, default=60.0, dest='sw_cube_width',
      help="Set the outer width of the cube (for x and y). Default: 60.0")
  if(ai_variant==2):
    r_parser.add_argument('--face_A1_thickness','--fa1t', action='store', type=float, default=9.0, dest='sw_face_A1_thickness',
      help="Set the thickness of the face_A1 part. If equal to 0.0, set to top_thickness. Default: 9.0")
    r_parser.add_argument('--face_A2_thickness','--fa2t', action='store', type=float, default=7.0, dest='sw_face_A2_thickness',
      help="Set the thickness of the face_A2 part. If equal to 0.0, set to top_thickness. Default: 7.0")
  if(ai_variant==2):
    r_parser.add_argument('--face_B1_thickness','--fb1t', action='store', type=float, default=8.0, dest='sw_face_B1_thickness',
      help="Set the thickness of the face_B1 part. If equal to 0.0, set to top_thickness. Default: 8.0")
    r_parser.add_argument('--face_B2_thickness','--fb2t', action='store', type=float, default=6.0, dest='sw_face_B2_thickness',
      help="Set the thickness of the face_B2 part. If equal to 0.0, set to top_thickness. Default: 6.0")
  ### threaded rod
  # face
  if(ai_variant==2):
    r_parser.add_argument('--face_rod_hole_diameter','--frhd', action='store', type=float, default=4.0, dest='sw_face_rod_hole_diameter',
      help="Set the diameter of the holes for threaded rod on the faces. Default: 4.0")
    r_parser.add_argument('--face_rod_hole_h_distance','--frhhd', action='store', type=float, default=5.0, dest='sw_face_rod_hole_h_distance',
      help="Set the horizontal position of the threaded rod center from the inner edge. Default: 5.0")
    r_parser.add_argument('--face_rod_hole_v_distance','--frhvd', action='store', type=float, default=5.0, dest='sw_face_rod_hole_v_distance',
      help="Set the vertical position of the threaded rod center from the inner edge. Default: 5.0")
  # top
  if(ai_variant==1):
    r_parser.add_argument('--top_rod_hole_diameter','--trhd', action='store', type=float, default=4.0, dest='sw_top_rod_hole_diameter',
      help="Set the diameter of the holes for the vertical threaded rods. Default: 4.0")
    r_parser.add_argument('--top_rod_hole_h_distance','--trhhd', action='store', type=float, default=10.0, dest='sw_top_rod_hole_h_distance',
      help="Set the horizontal position of the vertical threaded rod center from the inner edge. Default: 10.0")
  ### hollow
  # face hollow
  if(ai_variant==2):
    r_parser.add_argument('--face_hollow_leg_nb','--fhln', action='store', type=int, default=1, dest='sw_face_hollow_leg_nb',
      help="Set the number of legs (equivalent number of hollows) on the faces. Possible values: 1 (filled), 4, 8. Default: 1")
    r_parser.add_argument('--face_hollow_border_width','--fhbw', action='store', type=float, default=0.0, dest='sw_face_hollow_border_width',
      help="Set the width around the face-inner-border. If equal to 0.0, set to max_face_top_thickness. Default: 0.0")
    r_parser.add_argument('--face_hollow_axle_width','--fhaw', action='store', type=float, default=0.0, dest='sw_face_hollow_axle_width',
      help="Set the width around the axle. If equal to 0.0, set to axle_radius. Default: 0.0")
    r_parser.add_argument('--face_hollow_leg_width','--fhlw', action='store', type=float, default=0.0, dest='sw_face_hollow_leg_width',
      help="Set the width of the legs. If equal to 0.0, set to max(max_face_top_thickness, axle_radius). Default: 0.0")
    r_parser.add_argument('--face_hollow_smoothing_radius','--fhsr', action='store', type=float, default=0.0, dest='sw_face_hollow_smoothing_radius',
      help="Set the radius for smoothing the face-hollow corners. If equal to 0.0, set to cube_width/10. Default: 0.0")
  # top hollow
  if(ai_variant==1):
    r_parser.add_argument('--top_hollow_leg_nb','--thln', action='store', type=int, default=0, dest='sw_top_hollow_leg_nb',
      help="Set the number of legs (equivalent number of hollows) on the top. Possible values: 0 (empty), 1 (filled), 4, 8. Default: 0")
    r_parser.add_argument('--top_hollow_border_width','--thbw', action='store', type=float, default=0.0, dest='sw_top_hollow_border_width',
      help="Set the width around the top-inner-border. If equal to 0.0, set to max_face_thickness. Default: 0.0")
    r_parser.add_argument('--top_hollow_leg_width','--thlw', action='store', type=float, default=0.0, dest='sw_top_hollow_leg_width',
      help="Set the width of the legs. If equal to 0.0, set to max_face_thickness. Default: 0.0")
    r_parser.add_argument('--top_hollow_smoothing_radius','--thsr', action='store', type=float, default=0.0, dest='sw_top_hollow_smoothing_radius',
      help="Set the radius for smoothing the top-hollow corners. If equal to 0.0, set to cube_width/10. Default: 0.0")
  ### axle
  if(ai_variant==1):
    r_parser.add_argument('--axle_length','--al', action='store', type=float, default=0.0, dest='sw_axle_length',
      help="Set the total length of the axles. If equal to 0.0, set to 2*cube_width. Default: 0.0")
    r_parser.add_argument('--spacer_diameter','--sd', action='store', type=float, default=0.0, dest='sw_spacer_diameter',
      help="Set the external diameter of the spacer. If equal to 0.0, set to 1.2*axle_diameter. Default: 0.0")
    r_parser.add_argument('--spacer_length','--sl', action='store', type=float, default=0.0, dest='sw_spacer_length',
      help="Set the length of the spacers. If equal to 0.0, set to (axle_length-cube_width)/4. Default: 0.0")
  ### manufacturing
  if(ai_variant==2):
    r_parser.add_argument('--cross_cube_cnc_router_bit_radius','--cccrbr', action='store', type=float, default=1.0, dest='sw_cross_cube_cnc_router_bit_radius',
      help="Set the minimal cnc_router_bit radius of the design. Default: 1.0")
    r_parser.add_argument('--cross_cube_extra_cut_thickness','--ccect', action='store', type=float, default=0.0, dest='sw_cross_cube_extra_cut_thickness',
      help="Set the extra-cut-thickness for the internal cross_cube cuts. It can be used to compensate the manufacturing process or to check the 3D assembly with FreeCAD. Default: 0.0")
  ### output
  # return
  return(r_parser)

################################################################
# parameter check functions
################################################################

def check_cross_cube_face_parameters(ai_constraints):
  """ check and complete the parameters relative to the cross_cube-face
  """
  cc_c = ai_constraints
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  ### face A1, A2, B1 and B2
  ## height
  # axle_diameter
  cc_c['axle_radius'] = cc_c['axle_diameter']/2.0
  if(cc_c['axle_radius']<radian_epsilon):
    print("ERR220: Error, axle_radius {:0.3f} must be strictly positive".format(cc_c['axle_radius']))
    sys.exit(2)
  # inter_axle_length
  if(cc_c['inter_axle_length']<0):
    print("ERR224: Error, inter_axle_length {:0.3f} must be positive".format(cc_c['inter_axle_length']))
    sys.exit(2)
  if(cc_c['inter_axle_length']<2*cc_c['axle_radius']):
    print("WARN227: Warning, inter_axle_length {:0.3f} is smaller than the axle_diameter {:0.3f}".format(cc_c['inter_axle_length'], 2*cc_c['axle_radius']))
  # height_margin
  if(cc_c['height_margin']<radian_epsilon):
    print("ERR229: Error, height_margin {:0.3f} must be strictly positive".format(cc_c['height_margin']))
    sys.exit(2)
  # top_thickness
  if(cc_c['top_thickness']<2*cc_c['cross_cube_cnc_router_bit_radius']):
    print("ERR232: Error, top_thickness {:0.3f} is too small compare to cross_cube_cnc_router_bit_radius {:0.3f}".format(cc_c['top_thickness'], cc_c['cross_cube_cnc_router_bit_radius']))
    sys.exit(2)
  if(cc_c['top_thickness']>(cc_c['inter_axle_length']+2*cc_c['axle_radius']+2*cc_c['height_margin'])/4.0):
    print("ERR235: top_thickness {:0.3f} is too small compare to inter_axle_length {:0.3}, axle_radius {:0.3}, height_margin {:0.3}".format(cc_c['top_thickness'], cc_c['inter_axle_length'], cc_c['axle_radius'], cc_c['height_margin']))
    sys.exit(2)
  cc_c['cube_height'] = cc_c['inter_axle_length'] + 2*cc_c['axle_radius'] + 2*cc_c['height_margin'] + 2*cc_c['top_thickness']
  ## width
  # cube_width
  if(cc_c['cube_width']<3*cc_c['axle_radius']):
    print("ERR239: Error, cube_width {:0.3f} is too small compare to axle_radius {:0.3f}".format(cc_c['cube_width'], cc_c['axle_radius']))
    sys.exit(2)
  # face_A1_thickness, face_A2_thickness, face_B1_thickness, face_B2_thickness
  face_thickness = [cc_c['face_A1_thickness'], cc_c['face_A2_thickness'], cc_c['face_B1_thickness'], cc_c['face_B2_thickness']]
  cc_c['max_face_thickness'] = max(face_thickness)
  cc_c['max_face_top_thickness'] = max(cc_c['max_face_thickness'], cc_c['top_thickness'])
  for i in range(len(face_thickness)):
    if(face_thickness[i]==0):
      face_thickness[i] = cc_c['top_thickness']
    if(face_thickness[i]<2*cc_c['cross_cube_cnc_router_bit_radius']):
      print("ERR244: Error, face_thickness[{:d}] {:0.3f} is too small compare to cross_cube_cnc_router_bit_radius {:0.3f}".format(i, face_thickness[i], cc_c['cross_cube_cnc_router_bit_radius']))
      sys.exit(2)
    if(face_thickness[i]>cc_c['cube_width']/2.0-cc_c['axle_radius']):
      print("ERR247: Error, face_thickness[{:d}] {:0.3f} is too big compare to cube_width {:0.3f} and axle_radius {:0.3f}".format(i, face_thickness[i], cc_c['cube_width'], cc_c['axle_radius']))
      sys.exit(2)
    if(face_thickness[i]>cc_c['cube_width']/6.0):
      print("ERR250: Error, face_thickness[{:d}] {:0.3f} is too big compare to cube_width {:0.3f}".format(i, face_thickness[i], cc_c['cube_width']))
      sys.exit(2)
  cc_c['face_A1_thickness'] = face_thickness[0]
  cc_c['face_A2_thickness'] = face_thickness[1]
  cc_c['face_B1_thickness'] = face_thickness[2]
  cc_c['face_B2_thickness'] = face_thickness[3]
  ### threaded rod
  ## face
  # face_rod_hole_diameter
  cc_c['face_rod_hole_radius'] = cc_c['face_rod_hole_diameter']/2.0
  if(cc_c['face_rod_hole_radius']>0):
    # face_rod_hole_h_distance
    if(cc_c['face_rod_hole_h_distance']<cc_c['face_rod_hole_radius']):
      print("ERR257: Error, face_rod_hole_h_distance {:0.3f} must be biggert than face_rod_hole_radius {:0.3f}".format(cc_c['face_rod_hole_h_distance'], cc_c['face_rod_hole_radius']))
      sys.exit(2)
    if(cc_c['max_face_thickness']+cc_c['face_rod_hole_h_distance']+cc_c['face_rod_hole_radius']>cc_c['cube_width']/2.0-cc_c['axle_radius']):
      print("ERR261: Error, face_rod_hole_h_distance {:0.3f} is too big compare to max_face_thickness {:0.3f}, face_rod_hole_radius {:0.3f}, cube_width {:0.3f}, axle_radius {:0.3f}".format(cc_c['face_rod_hole_h_distance'], cc_c['max_face_thickness'], cc_c['face_rod_hole_radius'], cc_c['cube_width'], cc_c['axle_radius']))
      sys.exit(2)
    # face_rod_hole_v_distance
    if(cc_c['face_rod_hole_v_distance']<cc_c['face_rod_hole_radius']):
      print("ERR264: Error, face_rod_hole_v_distance {:0.3f} must be bigger than face_rod_hole_radius {:0.3f}".format(cc_c['face_rod_hole_v_distance'], cc_c['face_rod_hole_radius']))
      sys.exit(2)
    if(cc_c['face_rod_hole_v_distance']+cc_c['face_rod_hole_radius']>cc_c['height_margin']):
      print("ERR267: Error, face_rod_hole_v_distance {:0.3f} is too big compare to face_rod_hole_radius {:0.3f} and height_margin {:0.3f}".format(cc_c['face_rod_hole_v_distance'], cc_c['face_rod_hole_radius'], cc_c['height_margin']))
      sys.exit(2)
  ## top
  ### hollow
  ## face hollow
  # face_hollow_leg_nb
  if(not(cc_c['face_hollow_leg_nb'] in [1, 4, 8])):
    print("ERR281: Error, face_hollow_leg_nb {:d} accepts only the values: 1, 4 or 8".format(cc_c['face_hollow_leg_nb']))
    sys.exit(2)
  # face_hollow_border_width
  if(cc_c['face_hollow_border_width']==0):
    cc_c['face_hollow_border_width'] = cc_c['max_face_top_thickness']
  if(cc_c['face_hollow_border_width']<radian_epsilon):
    print("ERR283: Error, face_hollow_border_width {:0.3f} must be strictly positive".format(cc_c['face_hollow_border_width']))
    sys.exit(2)
  # face_hollow_axle_width
  if(cc_c['face_hollow_axle_width']==0):
    cc_c['face_hollow_axle_width'] = cc_c['axle_radius']
  if(cc_c['face_hollow_axle_width']<radian_epsilon):
    print("ERR292: Error, face_hollow_axle_width {:0.3f} must be strictly positive".format(cc_c['face_hollow_axle_width']))
    sys.exit(2)
  # face_hollow_leg_width
  if(cc_c['face_hollow_leg_width']==0):
    cc_c['face_hollow_leg_width'] = max(cc_c['face_hollow_border_width'], cc_c['face_hollow_axle_width'])
  if(cc_c['face_hollow_leg_width']<radian_epsilon):
    print("ERR297: Error, face_hollow_leg_width {:0.3f} must be strictly positive".format(cc_c['face_hollow_leg_width']))
    sys.exit(2)
  # face_hollow_smoothing_radius
  if(cc_c['face_hollow_smoothing_radius']==0):
    cc_c['face_hollow_smoothing_radius'] = cc_c['cube_width']/10.0
  if(cc_c['face_hollow_smoothing_radius']<cc_c['cross_cube_cnc_router_bit_radius']):
    print("ERR302: Error, face_hollow_smoothing_radius {:0.3f} must be bigger than cross_cube_cnc_router_bit_radius {:0.3f}".format(cc_c['face_hollow_smoothing_radius'], cc_c['cross_cube_cnc_router_bit_radius']))
    sys.exit(2)
  ### manufacturing
  # cross_cube_cnc_router_bit_radius
  # cross_cube_extra_cut_thickness
  if(abs(cc_c['cross_cube_extra_cut_thickness'])>min(cc_c['cube_width']/5.0, cc_c['cube_height']/4.0)/3.0):
    print("ERR369: Error, cross_cube_extra_cut_thickness {:0.3} absolute value is too big compare to cube_width {:0.3f} and cube_height {:0.3f}".format(cc_c['cross_cube_extra_cut_thickness'], cc_c['cube_width'], cc_c['cube_height']))
    sys.exit(2)
  # return
  return(cc_c)

def check_cross_cube_top_parameters(ai_constraints):
  """ check and complete the parameters relative to the cross_cube-top
  """
  cc_c = ai_constraints
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  ### face A1, A2, B1 and B2
  ## top
  # top_rod_hole_diameter
  cc_c['top_rod_hole_radius'] = cc_c['top_rod_hole_diameter']/2.0
  if(cc_c['top_rod_hole_radius']>0):
    # top_rod_hole_h_distance
    if(cc_c['top_rod_hole_h_distance']<cc_c['face_rod_hole_h_distance']+cc_c['face_rod_hole_radius']+cc_c['top_rod_hole_radius']):
      print("ERR273: Error, top_rod_hole_h_distance {:0.3f} is too small compare to face_rod_hole_h_distance {:0.3f}, face_rod_hole_radius {:0.3f} and top_rod_hole_radius {:0.3f}".format(cc_c['top_rod_hole_h_distance'], cc_c['face_rod_hole_h_distance'], cc_c['face_rod_hole_radius'], cc_c['top_rod_hole_radius']))
      sys.exit(2)
    if(cc_c['max_face_thickness']+cc_c['top_rod_hole_h_distance']+cc_c['top_rod_hole_radius']>cc_c['cube_width']/2.0-cc_c['axle_radius']):
      print("ERR276: Error, top_rod_hole_h_distance {:0.3f} is too big compare to max_face_thickness {:0.3f}, top_rod_hole_radius {:0.3f}, cube_width {:0.3f} and axle_radius {:0.3f}".format(cc_c['top_rod_hole_h_distance'], cc_c['max_face_thickness'], cc_c['top_rod_hole_radius'], cc_c['cube_width'], cc_c['axle_radius']))
      sys.exit(2)
  ## top hollow
  # top_hollow_leg_nb
  if(not(cc_c['top_hollow_leg_nb'] in [0, 1, 4, 8])):
    print("ERR325: Error, top_hollow_leg_nb {:d} accepts only the values: 0, 1, 4, 8".format(cc_c['top_hollow_leg_nb']))
    sys.exit(2)
  # top_hollow_border_width
  if(cc_c['top_hollow_border_width']==0):
    cc_c['top_hollow_border_width'] = cc_c['max_face_thickness']
  if(cc_c['top_hollow_border_width']<radian_epsilon):
    print("ERR332: Error, top_hollow_border_width {:0.3f} must be strictly positive".format(cc_c['top_hollow_border_width']))
    sys.exit(2)
  # top_hollow_leg_width
  if(cc_c['top_hollow_leg_width']==0):
    cc_c['top_hollow_leg_width'] = cc_c['top_hollow_border_width']
  if(cc_c['top_hollow_leg_width']<radian_epsilon):
    print("ERR338: Error, top_hollow_leg_width {:0.3f} must be strictly positive".format(cc_c['top_hollow_leg_width']))
    sys.exit(2)
  # top_hollow_smoothing_radius
  if(cc_c['top_hollow_smoothing_radius']==0):
    cc_c['top_hollow_smoothing_radius'] = cc_c['cube_width']/10.0
  if(cc_c['top_hollow_smoothing_radius']<cc_c['cross_cube_cnc_router_bit_radius']):
    print("ERR344: Error, top_hollow_smoothing_radius {:0.3f} must be bigger than cross_cube_cnc_router_bit_radius {:0.3f}".format(cc_c['top_hollow_smoothing_radius'], cc_c['cross_cube_cnc_router_bit_radius']))
    sys.exit(2)
  ### axle
  # axle_length
  if(cc_c['axle_length']==0):
    cc_c['axle_length'] = 2*cc_c['cube_width']
  if(cc_c['axle_length']<cc_c['cube_width']):
    print("ERR349: Error, axle_length {:0.3f} must be bigger than cube_width {:0.3f}".format(cc_c['axle_length'], cc_c['cube_width']))
    sys.exit(2)
  # spacer_diameter
  cc_c['spacer_radius'] = cc_c['spacer_diameter']/2.0
  if(cc_c['spacer_radius']==0):
    cc_c['spacer_radius'] = 1.2*cc_c['axle_radius']
  if(cc_c['spacer_radius']<cc_c['axle_radius']+radian_epsilon):
    print("ERR357: Error, spacer_radius {:0.3f} must be bigger than axle_radius {:0.3f}".format(cc_c['spacer_radius'], cc_c['axle_radius']))
    sys.exit(2)
  if(cc_c['spacer_length']==0):
    cc_c['spacer_length'] = (cc_c['axle_length']-cc_c['cube_width'])/4.0
  if(cc_c['spacer_length']<radian_epsilon):
    print("ERR360: Error, spacer_length {:0.3f} must be strictly positive".format(cc_c['spacer_length']))
    sys.exit(2)
  if(cc_c['spacer_length']>(cc_c['axle_length']-cc_c['cube_width'])/2.0):
    print("ERR363: Error, spacer_length {:0.3f} is too big compare to axle_length {:0.3f} and cube_width {:0.3f}".format(cc_c['spacer_length'], cc_c['axle_length'], cc_c['cube_width']))
    sys.exit(2)
  # return
  return(cc_c)
    
    
################################################################
# construction functions
################################################################

def cross_cube_face_bottom_outline(ai_constraints, ai_left_thickness, ai_right_thickness):
  """ Generate the bottom-portion of the face external-outline
  """
  # alias
  cc_c = check_cross_cube_face_parameters(ai_constraints)
  lt = ai_left_thickness
  rt = ai_right_thickness
  cccrbr = cc_c['cross_cube_cnc_router_bit_radius']
  ccect = cc_c['cross_cube_extra_cut_thickness']
  cw5 = cc_c['cube_width']/5.0
  tt = cc_c['top_thickness']
  #mlrt = max(lt, rt)
  face_bottom_ol = []
  face_bottom_ol.append((0*cw5, 0, 0)) # bottom side
  face_bottom_ol.append((1*cw5-ccect, 0, 0))
  face_bottom_ol.append((1*cw5-ccect, tt+ccect, -1*cccrbr))
  face_bottom_ol.append((2*cw5+ccect, tt+ccect, -1*cccrbr))
  face_bottom_ol.append((2*cw5+ccect, 0, 0))
  face_bottom_ol.append((3*cw5-ccect, 0, 0))
  face_bottom_ol.append((3*cw5-ccect, tt+ccect, -1*cccrbr))
  face_bottom_ol.append((4*cw5+ccect, tt+ccect, -1*cccrbr))
  face_bottom_ol.append((4*cw5+ccect, 0, 0))
  face_bottom_ol.append((5*cw5, 0, 0))
  return(face_bottom_ol)

def cross_cube_face_top_outline(ai_constraints, ai_left_thickness, ai_right_thickness):
  """ Generate the top-portion of the face external-outline
  """
  # alias
  cc_c = check_cross_cube_face_parameters(ai_constraints)
  lt = ai_left_thickness
  rt = ai_right_thickness
  cccrbr = cc_c['cross_cube_cnc_router_bit_radius']
  ccect = cc_c['cross_cube_extra_cut_thickness']
  cw5 = cc_c['cube_width']/5.0
  ch4 = cc_c['cube_height']/4.0
  tt = cc_c['top_thickness']
  #
  face_top_ol = []
  #face_top_ol.append((5*cw5, 0, 0)) # face A1 right side
  face_top_ol.append((5*cw5, 1*ch4-ccect/2.0, 0))
  face_top_ol.append((5*cw5-rt-ccect, 1*ch4-ccect/2.0, -1*cccrbr))
  face_top_ol.append((5*cw5-rt-ccect, 2*ch4+ccect/2.0, -1*cccrbr))
  face_top_ol.append((5*cw5, 2*ch4+ccect/2.0, 0))
  face_top_ol.append((5*cw5, 3*ch4-ccect/2.0, 0))
  face_top_ol.append((5*cw5-rt-ccect, 3*ch4-ccect/2.0, -1*cccrbr))
  face_top_ol.append((5*cw5-rt-ccect, 4*ch4, 0)) # top side
  face_top_ol.append((4*cw5+ccect, 4*ch4, 0))
  face_top_ol.append((4*cw5+ccect, 4*ch4-tt-ccect, -1*cccrbr))
  face_top_ol.append((3*cw5-ccect, 4*ch4-tt-ccect, -1*cccrbr))
  face_top_ol.append((3*cw5-ccect, 4*ch4, 0))
  face_top_ol.append((2*cw5+ccect, 4*ch4, 0))
  face_top_ol.append((2*cw5+ccect, 4*ch4-tt-ccect, -1*cccrbr))
  face_top_ol.append((1*cw5-ccect, 4*ch4-tt-ccect, -1*cccrbr))
  face_top_ol.append((1*cw5-ccect, 4*ch4, 0))
  face_top_ol.append((0*cw5+lt+ccect, 4*ch4, 0)) # left side
  face_top_ol.append((0*cw5+lt+ccect, 3*ch4-ccect/2.0, -1*cccrbr))
  face_top_ol.append((0*cw5, 3*ch4-ccect/2.0, 0))
  face_top_ol.append((0*cw5, 2*ch4+ccect/2.0, 0))
  face_top_ol.append((0*cw5+lt+ccect, 2*ch4+ccect/2.0, -1*cccrbr))
  face_top_ol.append((0*cw5+lt+ccect, 1*ch4-ccect/2.0, -1*cccrbr))
  face_top_ol.append((0*cw5, 1*ch4-ccect/2.0, 0))
  #face_top_ol.append((0*cw5, 0*ch4, 0))
  return(face_top_ol)

def cross_cube_face_holes(ai_constraints, ai_left_thickness, ai_right_thickness):
  """ Generate the hole-outlines of the face figures
  """
  # alias
  cc_c = check_cross_cube_face_parameters(ai_constraints)
  lt = ai_left_thickness
  rt = ai_right_thickness
  tt = cc_c['top_thickness']
  #
  r_face_hole_figure = []
  # alias
  lt = ai_left_thickness
  rt = ai_right_thickness
  # holes
  if(cc_c['axle_radius']>0):
    r_face_hole_figure.append((cc_c['cube_width']/2.0, tt+cc_c['height_margin']+cc_c['axle_radius'], cc_c['axle_radius']))
  if(cc_c['face_rod_hole_radius']>0):
    r_face_hole_figure.append((lt+cc_c['face_rod_hole_h_distance'], tt+2*cc_c['face_rod_hole_v_distance'], cc_c['face_rod_hole_radius']))
    r_face_hole_figure.append((cc_c['cube_width']-(rt+cc_c['face_rod_hole_h_distance']), tt+2*cc_c['face_rod_hole_v_distance'], cc_c['face_rod_hole_radius']))
    r_face_hole_figure.append((lt+cc_c['face_rod_hole_h_distance'], cc_c['cube_height']-(tt+cc_c['face_rod_hole_v_distance']), cc_c['face_rod_hole_radius']))
    r_face_hole_figure.append((cc_c['cube_width']-(rt+cc_c['face_rod_hole_h_distance']), cc_c['cube_height']-(tt+cc_c['face_rod_hole_v_distance']), cc_c['face_rod_hole_radius']))
  # face-hollow
  # [todo]

  # return
  return(r_face_hole_figure)


def cross_cube_face(ai_constraints, ai_left_thickness, ai_right_thickness):
  """ Generate the whole face figure
  """
  face_ol = []
  face_ol.extend(cross_cube_face_bottom_outline(ai_constraints, ai_left_thickness, ai_right_thickness))
  face_ol.extend(cross_cube_face_top_outline(ai_constraints, ai_left_thickness, ai_right_thickness))
  face_ol = cnc25d_api.outline_close(face_ol)
  r_face_figure = []
  r_face_figure.append(face_ol)
  r_face_figure.extend(cross_cube_face_holes(ai_constraints, ai_left_thickness, ai_right_thickness))
  return(r_face_figure)

def cross_cube_top(ai_constraints):
  """ Generate the whole top figure
  """
  # alias
  cc_c = check_cross_cube_top_parameters(ai_constraints)
  cccrbr = cc_c['cross_cube_cnc_router_bit_radius']
  ccect = cc_c['cross_cube_extra_cut_thickness']
  cw5 = cc_c['cube_width']/5.0
  fa1t = cc_c['face_A1_thickness']
  fa2t = cc_c['face_A2_thickness']
  fb1t = cc_c['face_B1_thickness']
  fb2t = cc_c['face_B2_thickness']
  #
  # top_sub_outline
  def top_sub_outline(ai_previous_face_thickness, ai_current_face_thickness, ai_post_face_thickness):
    """ Generate a sub-outline of the top_outline
    """
    #
    pre_ft = ai_previous_face_thickness
    cur_ft = ai_current_face_thickness
    post_ft = ai_post_face_thickness
    #
    r_top_sub_ol = []
    r_top_sub_ol.append((pre_ft+ccect, cur_ft+ccect, 0))
    r_top_sub_ol.append((1*cw5, cur_ft+ccect, -1*cccrbr))
    r_top_sub_ol.append((1*cw5, 0, 0))
    r_top_sub_ol.append((2*cw5, 0, 0))
    r_top_sub_ol.append((2*cw5, cur_ft+ccect, -1*cccrbr))
    r_top_sub_ol.append((3*cw5, cur_ft+ccect, -1*cccrbr))
    r_top_sub_ol.append((3*cw5, 0, 0))
    r_top_sub_ol.append((4*cw5, 0, 0))
    r_top_sub_ol.append((4*cw5, cur_ft+ccect, -1*cccrbr))
    r_top_sub_ol.append((5*cw5-post_ft-ccect, cur_ft+ccect, 0))
    #
    return(r_top_sub_ol)
  # top_outline
  top_ol = []
  top_ol.extend(cnc25d_api.outline_rotate(top_sub_outline(fb1t, fa1t, fb2t)[:-1], cc_c['cube_width']/2.0, cc_c['cube_width']/2.0, 0*math.pi/2))
  top_ol.extend(cnc25d_api.outline_rotate(top_sub_outline(fa1t, fb2t, fa2t)[:-1], cc_c['cube_width']/2.0, cc_c['cube_width']/2.0, 1*math.pi/2))
  top_ol.extend(cnc25d_api.outline_rotate(top_sub_outline(fb2t, fa2t, fb1t)[:-1], cc_c['cube_width']/2.0, cc_c['cube_width']/2.0, 2*math.pi/2))
  top_ol.extend(cnc25d_api.outline_rotate(top_sub_outline(fa2t, fb1t, fa1t)[:-1], cc_c['cube_width']/2.0, cc_c['cube_width']/2.0, 3*math.pi/2))
  top_ol = cnc25d_api.outline_close(top_ol)
  top_A = []
  top_A.append(top_ol)
  # holes
  if(cc_c['top_rod_hole_radius']>0):
    top_A.append((fb1t+cc_c['top_rod_hole_h_distance'], fa1t+cc_c['top_rod_hole_h_distance'], cc_c['top_rod_hole_radius']))
    top_A.append((cc_c['cube_width']-(fb2t+cc_c['top_rod_hole_h_distance']), fa1t+cc_c['top_rod_hole_h_distance'], cc_c['top_rod_hole_radius']))
    top_A.append((cc_c['cube_width']-(fb2t+cc_c['top_rod_hole_h_distance']), cc_c['cube_width']-(fa2t+cc_c['top_rod_hole_h_distance']), cc_c['top_rod_hole_radius']))
    top_A.append((fb1t+cc_c['top_rod_hole_h_distance'], cc_c['cube_width']-(fa2t+cc_c['top_rod_hole_h_distance']), cc_c['top_rod_hole_radius']))
  # top-hollow
  # [todo]
  # return
  return(top_A)

################################################################
# parameter info
################################################################

def cross_cube_face_parameter_info(ai_constraints):
  """ generate a text string parameter_info for crest
  """
  cc_c = check_cross_cube_face_parameters(ai_constraints)
  # cc_parameter_info
  cc_parameter_info = "cross_cube parameter info for crest:"
  cc_parameter_info += """
cube height:
axle_radius:        {:0.3f}    diameter: {:0.3f}
inter_axle_length:  {:0.3f}
height_margin:      {:0.3f}
top_thickness:      {:0.3f}
cube_height:        {:0.3f}
""".format(cc_c['axle_radius'], 2*cc_c['axle_radius'], cc_c['inter_axle_length'], cc_c['height_margin'], cc_c['top_thickness'], cc_c['cube_height'])
  cc_parameter_info += """
cube width:
cube_width:         {:0.3f}
face_A1_thickness:  {:0.3f}
face_A2_thickness:  {:0.3f}
face_B1_thickness:  {:0.3f}
face_B2_thickness:  {:0.3f}
""".format(cc_c['cube_width'], cc_c['face_A1_thickness'], cc_c['face_A2_thickness'], cc_c['face_B1_thickness'], cc_c['face_B2_thickness'])
  cc_parameter_info += """
threaded rod holes:
face_rod_hole_radius:     {:0.3f}   diameter: {:0.3f}
face_rod_hole_h_distance: {:0.3f}
face_rod_hole_v_distance: {:0.3f}
""".format(cc_c['face_rod_hole_radius'], 2*cc_c['face_rod_hole_radius'], cc_c['face_rod_hole_h_distance'], cc_c['face_rod_hole_v_distance'])
  cc_parameter_info += """
face-hollow:
face_hollow_leg_nb:             {:d}
face_hollow_border_width:       {:0.3f}
face_hollow_axle_width:         {:0.3f}parameter info
face_hollow_leg_width:          {:0.3f}
face_hollow_smoothing_radius:   {:0.3f}
""".format(cc_c['face_hollow_leg_nb'], cc_c['face_hollow_border_width'], cc_c['face_hollow_axle_width'], cc_c['face_hollow_leg_width'], cc_c['face_hollow_smoothing_radius'])
  cc_parameter_info += """
manufacturing:
cross_cube_cnc_router_bit_radius: {:0.3f}
cross_cube_extra_cut_thickness:   {:0.3f}
""".format(cc_c['cross_cube_cnc_router_bit_radius'], cc_c['cross_cube_extra_cut_thickness'])
  #print("dbg552: cc_parameter_info: {:s}".format(cc_parameter_info))
  return(cc_parameter_info)

def cross_cube_top_parameter_info(ai_constraints):
  """ generate a text string parameter_info for the rest of cross_cube
  """
  cc_c = check_cross_cube_top_parameters(ai_constraints)
  # cc_parameter_info
  cc_parameter_info = "cross_cube parameter info for top:"
  cc_parameter_info += """
threaded rod holes:
top_rod_hole_radius:      {:0.3f}   diameter: {:0.3f}
top_rod_hole_h_distance:  {:0.3f}
""".format(cc_c['top_rod_hole_radius'], 2*cc_c['top_rod_hole_radius'], cc_c['top_rod_hole_h_distance'])
  cc_parameter_info += """
top-hollow:
top_hollow_leg_nb:            {:d}
top_hollow_border_width:      {:0.3f}
top_hollow_leg_width:         {:0.3f}
top_hollow_smoothing_radius:  {:0.3f}
""".format(cc_c['top_hollow_leg_nb'], cc_c['top_hollow_border_width'], cc_c['top_hollow_leg_width'], cc_c['top_hollow_smoothing_radius'])
  cc_parameter_info += """
axles:
axle_length:    {:0.3f}
spacer_radius:  {:0.3f}    spacer_diameter: {:0.3f}
spacer_length:  {:0.3f}
""".format(cc_c['axle_length'], cc_c['spacer_radius'], 2*cc_c['spacer_radius'], cc_c['spacer_length'])
  #print("dbg552: cc_parameter_info: {:s}".format(cc_parameter_info))
  return(cc_parameter_info)

################################################################
# cross_cube wrapper dance
################################################################

def cross_cube_sub_argparse_to_dictionary(ai_cc_args, ai_variant=0):
  """ convert a cross_cube_sub_argparse into a cross_cube_sub_dictionary
  """
  r_ccd = {}
  ### face A1, A2, B1 and B2
  # height
  if(ai_variant==2):
    r_ccd['axle_diameter']       = ai_cc_args.sw_axle_diameter
    r_ccd['inter_axle_length']   = ai_cc_args.sw_inter_axle_length
    r_ccd['height_margin']       = ai_cc_args.sw_height_margin
    r_ccd['top_thickness']       = ai_cc_args.sw_top_thickness
  # width
  if(ai_variant==2):
    r_ccd['cube_width']          = ai_cc_args.sw_cube_width
  if(ai_variant==2):
    r_ccd['face_A1_thickness']   = ai_cc_args.sw_face_A1_thickness
    r_ccd['face_A2_thickness']   = ai_cc_args.sw_face_A2_thickness
  if(ai_variant==2):
    r_ccd['face_B1_thickness']   = ai_cc_args.sw_face_B1_thickness
    r_ccd['face_B2_thickness']   = ai_cc_args.sw_face_B2_thickness
  ### threaded rod
  # face
  if(ai_variant==2):
    r_ccd['face_rod_hole_diameter']    = ai_cc_args.sw_face_rod_hole_diameter
    r_ccd['face_rod_hole_h_distance']  = ai_cc_args.sw_face_rod_hole_h_distance
    r_ccd['face_rod_hole_v_distance']  = ai_cc_args.sw_face_rod_hole_v_distance
  # top
  if(ai_variant==1):
    r_ccd['top_rod_hole_diameter']     = ai_cc_args.sw_top_rod_hole_diameter
    r_ccd['top_rod_hole_h_distance']   = ai_cc_args.sw_top_rod_hole_h_distance
  ### hollow
  # face hollow
  if(ai_variant==2):
    r_ccd['face_hollow_leg_nb']            = ai_cc_args.sw_face_hollow_leg_nb
    r_ccd['face_hollow_border_width']      = ai_cc_args.sw_face_hollow_border_width
    r_ccd['face_hollow_axle_width']        = ai_cc_args.sw_face_hollow_axle_width
    r_ccd['face_hollow_leg_width']         = ai_cc_args.sw_face_hollow_leg_width
    r_ccd['face_hollow_smoothing_radius']  = ai_cc_args.sw_face_hollow_smoothing_radius
  # top hollow
  if(ai_variant==1):
    r_ccd['top_hollow_leg_nb']             = ai_cc_args.sw_top_hollow_leg_nb
    r_ccd['top_hollow_border_width']       = ai_cc_args.sw_top_hollow_border_width
    r_ccd['top_hollow_leg_width']          = ai_cc_args.sw_top_hollow_leg_width
    r_ccd['top_hollow_smoothing_radius']   = ai_cc_args.sw_top_hollow_smoothing_radius
  ### axle
  if(ai_variant==1):
    r_ccd['axle_length']                   = ai_cc_args.sw_axle_length
    r_ccd['spacer_diameter']               = ai_cc_args.sw_spacer_diameter
    r_ccd['spacer_length']                 = ai_cc_args.sw_spacer_length
  ### manufacturing
  if(ai_variant==2):
    r_ccd['cross_cube_cnc_router_bit_radius']  = ai_cc_args.sw_cross_cube_cnc_router_bit_radius
    r_ccd['cross_cube_extra_cut_thickness']  = ai_cc_args.sw_cross_cube_extra_cut_thickness
  ### output
  #### return
  return(r_ccd)
  
