# cross_cube.py
# generates the cross_cube, the gimbal axle holder
# created by charlyoleg on 2013/12/05
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
cross_cube.py generates the cross_cube piece, used in a gimbal to hold the two axles.
The main function displays in a Tk-interface the cross_cube piece, or generates the design as files or returns the design as FreeCAD Part object.
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

def cross_cube_dictionary_init(ai_variant=0):
  """ create and initiate a cross_cube dictionary with the default value
  """
  r_cc = {}
  ### face A1, A2, B1 and B2
  # height
  r_cc['axle_diameter']       = 10.0
  r_cc['inter_axle_length']   = 15.0
  r_cc['height_margin']       = 10.0
  r_cc['top_thickness']       = 5.0
  # width
  r_cc['cube_width']          = 60.0
  r_cc['face_A1_thickness']   = 9.0
  r_cc['face_A2_thickness']   = 7.0
  r_cc['face_B1_thickness']   = 8.0
  r_cc['face_B2_thickness']   = 6.0
  ### threaded rod
  # face
  r_cc['face_rod_hole_diameter']    = 4.0
  r_cc['face_rod_hole_h_distance']  = 5.0
  r_cc['face_rod_hole_v_distance']  = 5.0
  # top
  r_cc['top_rod_hole_diameter']     = 4.0
  r_cc['top_rod_hole_h_distance']   = 10.0
  ### hollow
  # face hollow
  r_cc['face_hollow_leg_nb']            = 1 # possible values: 1 (filled), 4, 8
  r_cc['face_hollow_border_width']      = 0.0
  r_cc['face_hollow_axle_width']        = 0.0
  r_cc['face_hollow_leg_width']         = 0.0
  r_cc['face_hollow_smoothing_radius']  = 0.0
  # top hollow
  r_cc['top_hollow_leg_nb']             = 0 # possible values: 0 (empty), 1 (filled), 4, 8
  r_cc['top_hollow_border_width']       = 0.0
  r_cc['top_hollow_leg_width']          = 0.0
  r_cc['top_hollow_smoothing_radius']   = 0.0
  ### axle
  r_cc['axle_length']                   = 0.0
  r_cc['spacer_diameter']               = 0.0
  r_cc['spacer_length']                 = 0.0
  ### manufacturing
  r_cc['cross_cube_cnc_router_bit_radius']  = 1.0
  r_cc['cross_cube_extra_cut_thickness']  = 0.0
  ### output
  if(ai_variant!=1):
    r_cc['tkinter_view']           = False
    r_cc['output_file_basename']   = ''
    r_cc['args_in_txt'] = ""
    r_cc['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_cc)

################################################################
# cross_cube argparse
################################################################

def cross_cube_add_argument(ai_parser, ai_variant=0):
  """
  Add arguments relative to the cross_cube
  This function intends to be used by the cross_cube_cli and cross_cube_self_test
  """
  r_parser = ai_parser
  ### face A1, A2, B1 and B2
  # height
  r_parser.add_argument('--axle_diameter','--ad', action='store', type=float, default=10.0, dest='sw_axle_diameter',
    help="Set the diameter of the two axles. Default: 10.0")
  r_parser.add_argument('--inter_axle_length','--ial', action='store', type=float, default=15.0, dest='sw_inter_axle_length',
    help="Set the length length betwen the two axle centers. Default: 15.0")
  r_parser.add_argument('--height_margin','--hm', action='store', type=float, default=10.0, dest='sw_height_margin',
    help="Set the length betwen the axle peripheral and the inner edge of the top. Default: 10.0")
  r_parser.add_argument('--top_thickness','--tt', action='store', type=float, default=5.0, dest='sw_top_thickness',
    help="Set the thickness of the top part. Default: 5.0")
  # width
  r_parser.add_argument('--cube_width','--cw', action='store', type=float, default=60.0, dest='sw_cube_width',
    help="Set the outer width of the cube (for x and y). Default: 60.0")
  r_parser.add_argument('--face_A1_thickness','--fa1t', action='store', type=float, default=9.0, dest='sw_face_A1_thickness',
    help="Set the thickness of the face_A1 part. If equal to 0.0, set to top_thickness. Default: 9.0")
  r_parser.add_argument('--face_A2_thickness','--fa2t', action='store', type=float, default=7.0, dest='sw_face_A2_thickness',
    help="Set the thickness of the face_A2 part. If equal to 0.0, set to top_thickness. Default: 7.0")
  r_parser.add_argument('--face_B1_thickness','--fb1t', action='store', type=float, default=8.0, dest='sw_face_B1_thickness',
    help="Set the thickness of the face_B1 part. If equal to 0.0, set to top_thickness. Default: 8.0")
  r_parser.add_argument('--face_B2_thickness','--fb2t', action='store', type=float, default=6.0, dest='sw_face_B2_thickness',
    help="Set the thickness of the face_B2 part. If equal to 0.0, set to top_thickness. Default: 6.0")
  ### threaded rod
  # face
  r_parser.add_argument('--face_rod_hole_diameter','--frhd', action='store', type=float, default=4.0, dest='sw_face_rod_hole_diameter',
    help="Set the diameter of the holes for threaded rod on the faces. Default: 4.0")
  r_parser.add_argument('--face_rod_hole_h_distance','--frhhd', action='store', type=float, default=5.0, dest='sw_face_rod_hole_h_distance',
    help="Set the horizontal position of the threaded rod center from the inner edge. Default: 5.0")
  r_parser.add_argument('--face_rod_hole_v_distance','--frhvd', action='store', type=float, default=5.0, dest='sw_face_rod_hole_v_distance',
    help="Set the vertical position of the threaded rod center from the inner edge. Default: 5.0")
  # top
  r_parser.add_argument('--top_rod_hole_diameter','--trhd', action='store', type=float, default=4.0, dest='sw_top_rod_hole_diameter',
    help="Set the diameter of the holes for the vertical threaded rods. Default: 4.0")
  r_parser.add_argument('--top_rod_hole_h_distance','--trhhd', action='store', type=float, default=10.0, dest='sw_top_rod_hole_h_distance',
    help="Set the horizontal position of the vertical threaded rod center from the inner edge. Default: 10.0")
  ### hollow
  # face hollow
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
  r_parser.add_argument('--top_hollow_leg_nb','--thln', action='store', type=int, default=0, dest='sw_top_hollow_leg_nb',
    help="Set the number of legs (equivalent number of hollows) on the top. Possible values: 0 (empty), 1 (filled), 4, 8. Default: 0")
  r_parser.add_argument('--top_hollow_border_width','--thbw', action='store', type=float, default=0.0, dest='sw_top_hollow_border_width',
    help="Set the width around the top-inner-border. If equal to 0.0, set to max_face_thickness. Default: 0.0")
  r_parser.add_argument('--top_hollow_leg_width','--thlw', action='store', type=float, default=0.0, dest='sw_top_hollow_leg_width',
    help="Set the width of the legs. If equal to 0.0, set to max_face_thickness. Default: 0.0")
  r_parser.add_argument('--top_hollow_smoothing_radius','--thsr', action='store', type=float, default=0.0, dest='sw_top_hollow_smoothing_radius',
    help="Set the radius for smoothing the top-hollow corners. If equal to 0.0, set to cube_width/10. Default: 0.0")
  ### axle
  r_parser.add_argument('--axle_length','--al', action='store', type=float, default=0.0, dest='sw_axle_length',
    help="Set the total length of the axles. If equal to 0.0, set to 2*cube_width. Default: 0.0")
  r_parser.add_argument('--spacer_diameter','--sd', action='store', type=float, default=0.0, dest='sw_spacer_diameter',
    help="Set the external diameter of the spacer. If equal to 0.0, set to 1.2*axle_diameter. Default: 0.0")
  r_parser.add_argument('--spacer_length','--sl', action='store', type=float, default=0.0, dest='sw_spacer_length',
    help="Set the length of the spacers. If equal to 0.0, set to (axle_length-cube_width)/4. Default: 0.0")
  ### manufacturing
  r_parser.add_argument('--cross_cube_cnc_router_bit_radius','--cccrbr', action='store', type=float, default=1.0, dest='sw_cross_cube_cnc_router_bit_radius',
    help="Set the minimal cnc_router_bit radius of the design. Default: 1.0")
  r_parser.add_argument('--cross_cube_extra_cut_thickness','--ccect', action='store', type=float, default=0.0, dest='sw_cross_cube_extra_cut_thickness',
    help="Set the extra-cut-thickness for the internal cross_cube cuts. It can be used to compensate the manufacturing process or to check the 3D assembly with FreeCAD. Default: 0.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def cross_cube(ai_constraints):
  """
  The main function of the script.
  It generates a cross_cube assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  ccdi = cross_cube_dictionary_init()
  cc_c = ccdi.copy()
  cc_c.update(ai_constraints)
  #print("dbg155: cc_c:", cc_c)
  if(len(cc_c.viewkeys() & ccdi.viewkeys()) != len(cc_c.viewkeys() | ccdi.viewkeys())): # check if the dictionary cc_c has exactly all the keys compare to cross_cube_dictionary_init()
    print("ERR2060: Error, cc_c has too much entries as {:s} or missing entries as {:s}".format(cc_c.viewkeys() - ccdi.viewkeys(), ccdi.viewkeys() - cc_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: cross_cube constraints:")
  #for k in cc_c.viewkeys():
  #  if(cc_c[k] != ccdi[k]):
  #    print("dbg211: for k {:s}, cc_c[k] {:s} != ccdi[k] {:s}".format(k, str(cc_c[k]), str(ccdi[k])))
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
  cube_height = cc_c['inter_axle_length'] + 2*cc_c['axle_radius'] + 2*cc_c['height_margin'] + 2*cc_c['top_thickness']
  ## width
  # cube_width
  if(cc_c['cube_width']<3*cc_c['axle_radius']):
    print("ERR239: Error, cube_width {:0.3f} is too small compare to axle_radius {:0.3f}".format(cc_c['cube_width'], cc_c['axle_radius']))
    sys.exit(2)
  # face_A1_thickness, face_A2_thickness, face_B1_thickness, face_B2_thickness
  face_thickness = [cc_c['face_A1_thickness'], cc_c['face_A2_thickness'], cc_c['face_B1_thickness'], cc_c['face_B2_thickness']]
  max_face_thickness = max(face_thickness)
  max_face_top_thickness = max(max_face_thickness, cc_c['top_thickness'])
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
    if(max_face_thickness+cc_c['face_rod_hole_h_distance']+cc_c['face_rod_hole_radius']>cc_c['cube_width']/2.0-cc_c['axle_radius']):
      print("ERR261: Error, face_rod_hole_h_distance {:0.3f} is too big compare to max_face_thickness {:0.3f}, face_rod_hole_radius {:0.3f}, cube_width {:0.3f}, axle_radius {:0.3f}".format(cc_c['face_rod_hole_h_distance'], max_face_thickness, cc_c['face_rod_hole_radius'], cc_c['cube_width'], cc_c['axle_radius']))
      sys.exit(2)
    # face_rod_hole_v_distance
    if(cc_c['face_rod_hole_v_distance']<cc_c['face_rod_hole_radius']):
      print("ERR264: Error, face_rod_hole_v_distance {:0.3f} must be bigger than face_rod_hole_radius {:0.3f}".format(cc_c['face_rod_hole_v_distance'], cc_c['face_rod_hole_radius']))
      sys.exit(2)
    if(cc_c['face_rod_hole_v_distance']+cc_c['face_rod_hole_radius']>cc_c['height_margin']):
      print("ERR267: Error, face_rod_hole_v_distance {:0.3f} is too big compare to face_rod_hole_radius {:0.3f} and height_margin {:0.3f}".format(cc_c['face_rod_hole_v_distance'], cc_c['face_rod_hole_radius'], cc_c['height_margin']))
      sys.exit(2)
  ## top
  # top_rod_hole_diameter
  cc_c['top_rod_hole_radius'] = cc_c['top_rod_hole_diameter']/2.0
  if(cc_c['top_rod_hole_radius']>0):
    # top_rod_hole_h_distance
    if(cc_c['top_rod_hole_h_distance']<cc_c['face_rod_hole_h_distance']+cc_c['face_rod_hole_radius']+cc_c['top_rod_hole_radius']):
      print("ERR273: Error, top_rod_hole_h_distance {:0.3f} is too small compare to face_rod_hole_h_distance {:0.3f}, face_rod_hole_radius {:0.3f} and top_rod_hole_radius {:0.3f}".format(cc_c['top_rod_hole_h_distance'], cc_c['face_rod_hole_h_distance'], cc_c['face_rod_hole_radius'], cc_c['top_rod_hole_radius']))
      sys.exit(2)
    if(max_face_thickness+cc_c['top_rod_hole_h_distance']+cc_c['top_rod_hole_radius']>cc_c['cube_width']/2.0-cc_c['axle_radius']):
      print("ERR276: Error, top_rod_hole_h_distance {:0.3f} is too big compare to max_face_thickness {:0.3f}, top_rod_hole_radius {:0.3f}, cube_width {:0.3f} and axle_radius {:0.3f}".format(cc_c['top_rod_hole_h_distance'], max_face_thickness, cc_c['top_rod_hole_radius'], cc_c['cube_width'], cc_c['axle_radius']))
      sys.exit(2)
  ### hollow
  ## face hollow
  # face_hollow_leg_nb
  if(not(cc_c['face_hollow_leg_nb'] in [1, 4, 8])):
    print("ERR281: Error, face_hollow_leg_nb {:d} accepts only the values: 1, 4 or 8".format(cc_c['face_hollow_leg_nb']))
    sys.exit(2)
  # face_hollow_border_width
  if(cc_c['face_hollow_border_width']==0):
    cc_c['face_hollow_border_width'] = max_face_top_thickness
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
  ## top hollow
  # top_hollow_leg_nb
  if(not(cc_c['top_hollow_leg_nb'] in [0, 1, 4, 8])):
    print("ERR325: Error, top_hollow_leg_nb {:d} accepts only the values: 0, 1, 4, 8".format(cc_c['top_hollow_leg_nb']))
    sys.exit(2)
  # top_hollow_border_width
  if(cc_c['top_hollow_border_width']==0):
    cc_c['top_hollow_border_width'] = max_face_thickness
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
  if(cc_c['spacer_radius']>0):
    if(cc_c['spacer_radius']==0):
      cc_c['spacer_radius'] = 2.4*cc_c['axle_radius']
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
  ### manufacturing
  # cross_cube_cnc_router_bit_radius
  # cross_cube_extra_cut_thickness
  if(abs(cc_c['cross_cube_extra_cut_thickness'])>min(cc_c['cube_width']/5.0, cube_height/4.0)/3.0):
    print("ERR369: Error, cross_cube_extra_cut_thickness {:0.3} absolute value is too big compare to cube_width {:0.3f} and cube_height {:0.3f}".format(cc_c['cross_cube_extra_cut_thickness'], cc_c['cube_width'], cube_height))
    sys.exit(2)

  ################################################################
  # outline construction
  ################################################################
  # intermediate parameters
  cccrbr = cc_c['cross_cube_cnc_router_bit_radius']
  ccect = cc_c['cross_cube_extra_cut_thickness']
  cw5 = cc_c['cube_width']/5.0
  ch4 = cube_height/4.0
  tt = cc_c['top_thickness']
  fa1t = cc_c['face_A1_thickness']
  fa2t = cc_c['face_A2_thickness']
  fb1t = cc_c['face_B1_thickness']
  fb2t = cc_c['face_B2_thickness']
  ## face figure
  def face_figure(ai_left_thickness, ai_right_thickness):
    """ generate the face-figure for face_A and face_B
    """
    r_face_figure = []
    # alias
    lt = ai_left_thickness
    rt = ai_right_thickness
    #mlrt = max(lt, rt)
    # face_outline
    face_ol = []
    face_ol.append((0*cw5, 0, 0)) # bottom side
    face_ol.append((1*cw5-ccect, 0, 0))
    face_ol.append((1*cw5-ccect, tt+ccect, -1*cccrbr))
    face_ol.append((2*cw5+ccect, tt+ccect, -1*cccrbr))
    face_ol.append((2*cw5+ccect, 0, 0))
    face_ol.append((3*cw5-ccect, 0, 0))
    face_ol.append((3*cw5-ccect, tt+ccect, -1*cccrbr))
    face_ol.append((4*cw5+ccect, tt+ccect, -1*cccrbr))
    face_ol.append((4*cw5+ccect, 0, 0))
    face_ol.append((5*cw5, 0, 0)) # face A1 right side
    face_ol.append((5*cw5, 1*ch4-ccect/2.0, 0))
    face_ol.append((5*cw5-rt-ccect, 1*ch4-ccect/2.0, -1*cccrbr))
    face_ol.append((5*cw5-rt-ccect, 2*ch4+ccect/2.0, -1*cccrbr))
    face_ol.append((5*cw5, 2*ch4+ccect/2.0, 0))
    face_ol.append((5*cw5, 3*ch4-ccect/2.0, 0))
    face_ol.append((5*cw5-rt-ccect, 3*ch4-ccect/2.0, -1*cccrbr))
    face_ol.append((5*cw5-rt-ccect, 4*ch4, 0)) # top side
    face_ol.append((4*cw5+ccect, 4*ch4, 0))
    face_ol.append((4*cw5+ccect, 4*ch4-tt-ccect, -1*cccrbr))
    face_ol.append((3*cw5-ccect, 4*ch4-tt-ccect, -1*cccrbr))
    face_ol.append((3*cw5-ccect, 4*ch4, 0))
    face_ol.append((2*cw5+ccect, 4*ch4, 0))
    face_ol.append((2*cw5+ccect, 4*ch4-tt-ccect, -1*cccrbr))
    face_ol.append((1*cw5-ccect, 4*ch4-tt-ccect, -1*cccrbr))
    face_ol.append((1*cw5-ccect, 4*ch4, 0))
    face_ol.append((0*cw5+lt+ccect, 4*ch4, 0)) # left side
    face_ol.append((0*cw5+lt+ccect, 3*ch4-ccect/2.0, -1*cccrbr))
    face_ol.append((0*cw5, 3*ch4-ccect/2.0, 0))
    face_ol.append((0*cw5, 2*ch4+ccect/2.0, 0))
    face_ol.append((0*cw5+lt+ccect, 2*ch4+ccect/2.0, -1*cccrbr))
    face_ol.append((0*cw5+lt+ccect, 1*ch4-ccect/2.0, -1*cccrbr))
    face_ol.append((0*cw5, 1*ch4-ccect/2.0, 0))
    face_ol.append((0*cw5, 0*ch4, 0))
    r_face_figure.append(face_ol)
    # holes
    if(cc_c['axle_radius']>0):
      r_face_figure.append((cc_c['cube_width']/2.0, tt+cc_c['height_margin']+cc_c['axle_radius'], cc_c['axle_radius']))
    if(cc_c['face_rod_hole_radius']>0):
      r_face_figure.append((lt+cc_c['face_rod_hole_h_distance'], tt+2*cc_c['face_rod_hole_v_distance'], cc_c['face_rod_hole_radius']))
      r_face_figure.append((cc_c['cube_width']-(rt+cc_c['face_rod_hole_h_distance']), tt+2*cc_c['face_rod_hole_v_distance'], cc_c['face_rod_hole_radius']))
      r_face_figure.append((lt+cc_c['face_rod_hole_h_distance'], cube_height-(tt+cc_c['face_rod_hole_v_distance']), cc_c['face_rod_hole_radius']))
      r_face_figure.append((cc_c['cube_width']-(rt+cc_c['face_rod_hole_h_distance']), cube_height-(tt+cc_c['face_rod_hole_v_distance']), cc_c['face_rod_hole_radius']))
    # face-hollow

    # return
    return(r_face_figure)
  # face_A
  face_A_rotated = cnc25d_api.rotate_and_translate_figure(face_figure(fb1t, fb2t), cc_c['cube_width']/2.0, cube_height/2.0, 0.0, 0.0, 0.0)
  face_A = cnc25d_api.cnc_cut_figure(face_A_rotated, "face_A")
  face_A_overlay = cnc25d_api.ideal_figure(face_A_rotated, "face_A")
  # face_B
  face_B_rotated = cnc25d_api.rotate_and_translate_figure(face_figure(fa2t, fa1t), cc_c['cube_width']/2.0, cube_height/2.0, math.pi, 0.0, 0.0)
  face_B = cnc25d_api.cnc_cut_figure(face_B_rotated, "face_B")
  face_B_overlay = cnc25d_api.ideal_figure(face_B_rotated, "face_B")

  ## top_figure
  top_A = []
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
  top_A.append(top_ol)
  # holes
  if(cc_c['top_rod_hole_radius']>0):
    top_A.append((fb1t+cc_c['top_rod_hole_h_distance'], fa1t+cc_c['top_rod_hole_h_distance'], cc_c['top_rod_hole_radius']))
    top_A.append((cc_c['cube_width']-(fb2t+cc_c['top_rod_hole_h_distance']), fa1t+cc_c['top_rod_hole_h_distance'], cc_c['top_rod_hole_radius']))
    top_A.append((cc_c['cube_width']-(fb2t+cc_c['top_rod_hole_h_distance']), cc_c['cube_width']-(fa2t+cc_c['top_rod_hole_h_distance']), cc_c['top_rod_hole_radius']))
    top_A.append((fb1t+cc_c['top_rod_hole_h_distance'], cc_c['cube_width']-(fa2t+cc_c['top_rod_hole_h_distance']), cc_c['top_rod_hole_radius']))
  # top-hollow

  # top_figure
  top_figure = cnc25d_api.cnc_cut_figure(top_A, "top_figure")
  top_figure_overlay = cnc25d_api.ideal_figure(top_A, "top_figure")


  ################################################################
  # output
  ################################################################

  # cc_parameter_info
  cc_parameter_info = "\ncross_cube parameter info:\n"
  cc_parameter_info += "\n" + cc_c['args_in_txt'] + "\n"
  cc_parameter_info += """
cube height:
axle_radius:        {:0.3f}    diameter: {:0.3f}
inter_axle_length:  {:0.3f}
height_margin:      {:0.3f}
top_thickness:      {:0.3f}
cube_height:        {:0.3f}
""".format(cc_c['axle_radius'], 2*cc_c['axle_radius'], cc_c['inter_axle_length'], cc_c['height_margin'], cc_c['top_thickness'], cube_height)
  cc_parameter_info += """
cube width:
cube_width:         {:0.3f}
face_A1_thickness:  {:0.3f}
face_A1_thickness:  {:0.3f}
face_B1_thickness:  {:0.3f}
face_B2_thickness:  {:0.3f}
""".format(cc_c['cube_width'], cc_c['face_A1_thickness'], cc_c['face_A2_thickness'], cc_c['face_B1_thickness'], cc_c['face_B2_thickness'])
  cc_parameter_info += """
threaded rod holes:
face_rod_hole_radius:     {:0.3f}   diameter: {:0.3f}
face_rod_hole_h_distance: {:0.3f}
face_rod_hole_v_distance: {:0.3f}
top_rod_hole_radius:      {:0.3f}   diameter: {:0.3f}
top_rod_hole_h_distance:  {:0.3f}
""".format(cc_c['face_rod_hole_radius'], 2*cc_c['face_rod_hole_radius'], cc_c['face_rod_hole_h_distance'], cc_c['face_rod_hole_v_distance'], cc_c['top_rod_hole_radius'], 2*cc_c['top_rod_hole_radius'], cc_c['top_rod_hole_h_distance'])
  cc_parameter_info += """
face-hollow:
face_hollow_leg_nb:             {:d}
face_hollow_border_width:       {:0.3f}
face_hollow_axle_width:         {:0.3f}
face_hollow_leg_width:          {:0.3f}
face_hollow_smoothing_radius:   {:0.3f}
""".format(cc_c['face_hollow_leg_nb'], cc_c['face_hollow_border_width'], cc_c['face_hollow_axle_width'], cc_c['face_hollow_leg_width'], cc_c['face_hollow_smoothing_radius'])
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
  cc_parameter_info += """
manufacturing:
cross_cube_cnc_router_bit_radius: {:0.3f}
cross_cube_extra_cut_thickness:   {:0.3f}
""".format(cc_c['cross_cube_cnc_router_bit_radius'], cc_c['cross_cube_extra_cut_thickness'])
  #print("dbg552: cc_parameter_info: {:s}".format(cc_parameter_info))

  ### figures output
  # part_list
  part_list = []
  part_list.append(face_A)
  part_list.append(face_B)
  part_list.append(top_figure)
  # part_list_figure
  x_space = 1.2*cc_c['cube_width'] 
  y_space = 1.2*max(cube_height, cc_c['cube_width'])
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## intermediate parameters
  ## sub-assembly
  ## cross_cube_part_overview
  cross_cube_part_overview_figure = []
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(face_A, 0.0, 0.0, 0.0, 1*x_space, 1*y_space))
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(face_B, 0.0, 0.0, 0.0, 0*x_space, 1*y_space))
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(top_figure, 0.0, 0.0, 0.0, 1*x_space, 0*y_space))
  cross_cube_part_overview_figure_overlay = []
  cross_cube_part_overview_figure_overlay.extend(cnc25d_api.rotate_and_translate_figure(face_A_overlay, 0.0, 0.0, 0.0, 1*x_space, 1*y_space))
  cross_cube_part_overview_figure_overlay.extend(cnc25d_api.rotate_and_translate_figure(face_B_overlay, 0.0, 0.0, 0.0, 0*x_space, 1*y_space))
  cross_cube_part_overview_figure_overlay.extend(cnc25d_api.rotate_and_translate_figure(top_figure_overlay, 0.0, 0.0, 0.0, 1*x_space, 0*y_space))

  ### freecad-object assembly configuration
  # intermediate parameters
  x1 = 0
  x2 = cc_c['cube_width'] - cc_c['face_B2_thickness']
  y1 = 0
  y2 = cc_c['cube_width'] - cc_c['face_A2_thickness']
  z1 = 0
  z2 = cube_height - cc_c['top_thickness']
  # conf1a
  cross_cube_assembly_conf1a = []
  cross_cube_assembly_conf1a.append((face_A, 0, 0, cc_c['cube_width'], cube_height, cc_c['face_A1_thickness'], 'i', 'xz', x1, y1, z1))
  cross_cube_assembly_conf1a.append((face_B, 0, 0, cc_c['cube_width'], cube_height, cc_c['face_B1_thickness'], 'i', 'yz', x1, y1, z1))
  cross_cube_assembly_conf1a.append((top_figure, 0, 0, cc_c['cube_width'], cc_c['cube_width'], cc_c['top_thickness'], 'i', 'xy', x1, y1, z1))
  # conf1b
  cross_cube_assembly_conf1b = []
  cross_cube_assembly_conf1b.append((face_A, 0, 0, cc_c['cube_width'], cube_height, cc_c['face_A2_thickness'], 'i', 'xz', x1, y2, z1))
  cross_cube_assembly_conf1b.append((face_B, 0, 0, cc_c['cube_width'], cube_height, cc_c['face_B2_thickness'], 'i', 'yz', x2, y1, z1))
  cross_cube_assembly_conf1b.append((top_figure, 0, 0, cc_c['cube_width'], cc_c['cube_width'], cc_c['top_thickness'], 'i', 'xy', x1, y1, z2))
  # conf1
  cross_cube_assembly_conf1 = []
  cross_cube_assembly_conf1.extend(cross_cube_assembly_conf1a)
  cross_cube_assembly_conf1.extend(cross_cube_assembly_conf1b)
  # conf2a : threaded rod
  ftrr = 0.9*cc_c['face_rod_hole_radius']
  face_threaded_rod = (ftrr, ftrr, ftrr)
  ttrr = 0.9*cc_c['top_rod_hole_radius']
  top_threaded_rod = (ttrr, ttrr, ttrr)
  fatrx = (cc_c['face_B1_thickness']+cc_c['face_rod_hole_h_distance'], cc_c['cube_width']-(cc_c['face_B2_thickness']+cc_c['face_rod_hole_h_distance']))
  fatry = -0.1*cc_c['cube_width']
  fatrz = (cc_c['top_thickness']+2*cc_c['face_rod_hole_v_distance'], cc_c['cube_width']-(cc_c['top_thickness']+cc_c['face_rod_hole_v_distance']))
  fbtrx = -0.1*cc_c['cube_width']
  fbtry = (cc_c['face_A1_thickness']+cc_c['face_rod_hole_h_distance'], cc_c['cube_width']-(cc_c['face_A2_thickness']+cc_c['face_rod_hole_h_distance']))
  fbtrz = (cc_c['top_thickness']+1*cc_c['face_rod_hole_v_distance'], cc_c['cube_width']-(cc_c['top_thickness']+2*cc_c['face_rod_hole_v_distance']))
  ttrx = (max_face_thickness+cc_c['top_rod_hole_h_distance'], cc_c['cube_width']-(max_face_thickness+cc_c['top_rod_hole_h_distance']))
  ttry = ttrx
  ttrz = -0.1*cube_height
  cross_cube_assembly_conf2a = []
  if(cc_c['face_rod_hole_radius']>0):
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, ftrr, ftrr, 1.2*cc_c['cube_width'], 'i', 'xz', fatrx[0], fatry, fatrz[0])) # threaded rod on face_A
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, ftrr, ftrr, 1.2*cc_c['cube_width'], 'i', 'xz', fatrx[1], fatry, fatrz[0]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, ftrr, ftrr, 1.2*cc_c['cube_width'], 'i', 'xz', fatrx[1], fatry, fatrz[1]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, ftrr, ftrr, 1.2*cc_c['cube_width'], 'i', 'xz', fatrx[0], fatry, fatrz[1]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, ftrr, ftrr, 1.2*cc_c['cube_width'], 'i', 'yz', fbtrx, fbtry[0], fbtrz[0])) # threaded rod on face_B
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, ftrr, ftrr, 1.2*cc_c['cube_width'], 'i', 'yz', fbtrx, fbtry[1], fbtrz[0]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, ftrr, ftrr, 1.2*cc_c['cube_width'], 'i', 'yz', fbtrx, fbtry[1], fbtrz[1]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, ftrr, ftrr, 1.2*cc_c['cube_width'], 'i', 'yz', fbtrx, fbtry[0], fbtrz[1]))
  if(cc_c['top_rod_hole_radius']>0):
    cross_cube_assembly_conf2a.append((top_threaded_rod, 0, 0, ttrr, ttrr, 1.2*cube_height, 'i', 'xy', ttrx[0], ttry[0], ttrz)) # threaded rod on top
    cross_cube_assembly_conf2a.append((top_threaded_rod, 0, 0, ttrr, ttrr, 1.2*cube_height, 'i', 'xy', ttrx[1], ttry[0], ttrz))
    cross_cube_assembly_conf2a.append((top_threaded_rod, 0, 0, ttrr, ttrr, 1.2*cube_height, 'i', 'xy', ttrx[1], ttry[1], ttrz))
    cross_cube_assembly_conf2a.append((top_threaded_rod, 0, 0, ttrr, ttrr, 1.2*cube_height, 'i', 'xy', ttrx[0], ttry[1], ttrz))
  # conf2b : axles
  cross_cube_assembly_conf2b = []

  # conf2
  cross_cube_assembly_conf2 = []
  cross_cube_assembly_conf2.extend(cross_cube_assembly_conf1a)
  cross_cube_assembly_conf2.extend(cross_cube_assembly_conf2a)
  cross_cube_assembly_conf2.extend(cross_cube_assembly_conf2b)
  # conf3
  cross_cube_assembly_conf3 = []
  cross_cube_assembly_conf3.extend(cross_cube_assembly_conf2)
  cross_cube_assembly_conf3.extend(cross_cube_assembly_conf1b)

  ### display with Tkinter
  if(cc_c['tkinter_view']):
    print(cc_parameter_info)
    cnc25d_api.figure_simple_display(cross_cube_part_overview_figure, cross_cube_part_overview_figure_overlay, cc_parameter_info)

  ### generate output file
  if(cc_c['output_file_basename']!=''):
    (output_file_basename, output_file_suffix) = cnc25d_api.get_output_file_suffix(cc_c['output_file_basename'])
    # parts
    cnc25d_api.generate_output_file(face_A, output_file_basename + "_face_A" + output_file_suffix, cc_c['face_A1_thickness'], cc_parameter_info)
    cnc25d_api.generate_output_file(face_B, output_file_basename + "_face_B" + output_file_suffix, cc_c['face_B1_thickness'], cc_parameter_info)
    cnc25d_api.generate_output_file(top_figure, output_file_basename + "_top" + output_file_suffix, cc_c['top_thickness'], cc_parameter_info)
    # assembly
    if((output_file_suffix=='.svg')or(output_file_suffix=='.dxf')):
      cnc25d_api.generate_output_file(part_list_figure, output_file_basename + "_part_list" + output_file_suffix, 1.0, cc_parameter_info)
      cnc25d_api.generate_output_file(cross_cube_part_overview_figure, output_file_basename + "_part_overview" + output_file_suffix, 1.0, cc_parameter_info)
    else:
      size_xyz = (cc_c['axle_length'], cc_c['axle_length'], cube_height)
      zero_xyz = ((cc_c['axle_length']-cc_c['cube_width'])/2.0, (cc_c['axle_length']-cc_c['cube_width'])/2.0, 0)
      slice_x = [ (i+1)/12.0*size_xyz[0] for i in range(10) ]
      slice_y = [ (i+1)/12.0*size_xyz[1] for i in range(10) ]
      slice_z = [ (i+0.1)/12.0*size_xyz[2] for i in range(10) ]
      slice_xyz = (size_xyz[0], size_xyz[1], size_xyz[2], zero_xyz[0], zero_xyz[1], zero_xyz[2], slice_z, slice_y, slice_x)
      cnc25d_api.generate_3d_assembly_output_file(cross_cube_assembly_conf1, output_file_basename + "_bare_assembly", True, False, slice_xyz)
      cnc25d_api.generate_3d_assembly_output_file(cross_cube_assembly_conf2, output_file_basename + "_open_assembly_with_rods_and_axles", True, True, [])
      cnc25d_api.generate_3d_assembly_output_file(cross_cube_assembly_conf3, output_file_basename + "_assembly_with_rods_and_axles", True, True, [])

  #### return
  if(cc_c['return_type']=='int_status'):
    r_cc = 1
  elif(cc_c['return_type']=='cnc25d_figure'):
    r_cc = part_list
  elif(cc_c['return_type']=='freecad_object'):
    r_cc = cnc25d_api.figures_to_freecad_assembly(cross_cube_assembly_conf2)
  elif(cc_c['return_type']=='figures_3dconf_info'):
    r_cc = (part_list, cross_cube_assembly_conf3, cc_parameter_info)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(cc_c['return_type']))
    sys.exit(2)
  return(r_cc)

################################################################
# cross_cube wrapper dance
################################################################

def cross_cube_argparse_to_dictionary(ai_cc_args, ai_variant=0):
  """ convert a cross_cube_argparse into a cross_cube_dictionary
  """
  r_ccd = {}
  ### face A1, A2, B1 and B2
  # height
  r_ccd['axle_diameter']       = ai_cc_args.sw_axle_diameter
  r_ccd['inter_axle_length']   = ai_cc_args.sw_inter_axle_length
  r_ccd['height_margin']       = ai_cc_args.sw_height_margin
  r_ccd['top_thickness']       = ai_cc_args.sw_top_thickness
  # width
  r_ccd['cube_width']          = ai_cc_args.sw_cube_width
  r_ccd['face_A1_thickness']   = ai_cc_args.sw_face_A1_thickness
  r_ccd['face_A2_thickness']   = ai_cc_args.sw_face_A2_thickness
  r_ccd['face_B1_thickness']   = ai_cc_args.sw_face_B1_thickness
  r_ccd['face_B2_thickness']   = ai_cc_args.sw_face_B2_thickness
  ### threaded rod
  # face
  r_ccd['face_rod_hole_diameter']    = ai_cc_args.sw_face_rod_hole_diameter
  r_ccd['face_rod_hole_h_distance']  = ai_cc_args.sw_face_rod_hole_h_distance
  r_ccd['face_rod_hole_v_distance']  = ai_cc_args.sw_face_rod_hole_v_distance
  # top
  r_ccd['top_rod_hole_diameter']     = ai_cc_args.sw_top_rod_hole_diameter
  r_ccd['top_rod_hole_h_distance']   = ai_cc_args.sw_top_rod_hole_h_distance
  ### hollow
  # face hollow
  r_ccd['face_hollow_leg_nb']            = ai_cc_args.sw_face_hollow_leg_nb
  r_ccd['face_hollow_border_width']      = ai_cc_args.sw_face_hollow_border_width
  r_ccd['face_hollow_axle_width']        = ai_cc_args.sw_face_hollow_axle_width
  r_ccd['face_hollow_leg_width']         = ai_cc_args.sw_face_hollow_leg_width
  r_ccd['face_hollow_smoothing_radius']  = ai_cc_args.sw_face_hollow_smoothing_radius
  # top hollow
  r_ccd['top_hollow_leg_nb']             = ai_cc_args.sw_top_hollow_leg_nb
  r_ccd['top_hollow_border_width']       = ai_cc_args.sw_top_hollow_border_width
  r_ccd['top_hollow_leg_width']          = ai_cc_args.sw_top_hollow_leg_width
  r_ccd['top_hollow_smoothing_radius']   = ai_cc_args.sw_top_hollow_smoothing_radius
  ### axle
  r_ccd['axle_length']                   = ai_cc_args.sw_axle_length
  r_ccd['spacer_diameter']               = ai_cc_args.sw_spacer_diameter
  r_ccd['spacer_length']                 = ai_cc_args.sw_spacer_length
  ### manufacturing
  r_ccd['cross_cube_extra_cut_thickness']  = ai_cc_args.sw_cross_cube_extra_cut_thickness
  ### output
  if(ai_variant!=1):
    #r_ccd['tkinter_view']           = False
    r_ccd['output_file_basename']   = ai_cc_args.sw_output_file_basename
    #r_ccd['args_in_txt'] = ""
    r_ccd['return_type'] = ai_cc_args.sw_return_type
  #### return
  return(r_ccd)
  
def cross_cube_argparse_wrapper(ai_cc_args, ai_args_in_txt=""):
  """
  wrapper function of cross_cube() to call it using the cross_cube_parser.
  cross_cube_parser is mostly used for debug and non-regression tests.
  """
  # view the cross_cube with Tkinter as default action
  tkinter_view = True
  if(ai_cc_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  ccd = cross_cube_argparse_to_dictionary(ai_cc_args)
  ccd['args_in_txt'] = ai_args_in_txt
  ccd['tkinter_view'] = tkinter_view
  #ccd['return_type'] = 'int_status'
  r_cc = cross_cube(ccd)
  return(r_cc)

################################################################
# self test
################################################################

def cross_cube_self_test():
  """
  This is the non-regression test of cross_cube.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , ""],
    ["extra cut" , "--cross_cube_extra_cut_thickness 1.0"],
    ["extra cut negative" , "--cross_cube_extra_cut_thickness -2.0"],
    ["outputfile" , "--output_file_basename test_output/cross_cube_self_test.dxf"],
    ["last test"            , ""]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  cc_parser = argparse.ArgumentParser(description='Command line interface for the function cross_cube().')
  cc_parser = cross_cube_add_argument(cc_parser)
  cc_parser = cnc25d_api.generate_output_file_add_argument(cc_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = cc_parser.parse_args(l_args)
    r_ccst = cross_cube_argparse_wrapper(st_args)
  return(r_ccst)

################################################################
# cross_cube command line interface
################################################################

def cross_cube_cli(ai_args=""):
  """ command line interface of cross_cube.py when it is used in standalone
  """
  # cross_cube parser
  cc_parser = argparse.ArgumentParser(description='Command line interface for the function cross_cube().')
  cc_parser = cross_cube_add_argument(cc_parser)
  cc_parser = cnc25d_api.generate_output_file_add_argument(cc_parser, 1)
  # switch for self_test
  cc_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "cross_cube arguments: " + ' '.join(effective_args)
  cc_args = cc_parser.parse_args(effective_args)
  print("dbg111: start making cross_cube")
  if(cc_args.sw_run_self_test):
    r_cc = cross_cube_self_test()
  else:
    r_cc = cross_cube_argparse_wrapper(cc_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_cc)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("cross_cube.py says hello!\n")
  #my_cc = cross_cube_cli()
  my_cc = cross_cube_cli("--cross_cube_extra_cut_thickness 1.0 --return_type freecad_object")
  try: # depending on cc_c['return_type'] it might be or not a freecad_object
    Part.show(my_cc)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


