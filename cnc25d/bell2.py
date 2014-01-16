# bell.py
# generates the bell, assembled piece, that is part of the motorised gimbal assembly
# created by charlyoleg on 2013/11/22
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
bell.py generates the bell piece of the motorised gimbal. The bell piece is composed by several flat parts.
The main function displays in a Tk-interface the bell piece, or generates the design as files or returns the design as FreeCAD Part object.
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
import bell_outline


################################################################
# bell constraint_constructor
################################################################

def bell_constraint_constructor(ai_parser, ai_variant=0):
  """
  Add arguments relative to the bell
  This function intends to be used by the bell_cli and bell_self_test
  """
  r_parser = ai_parser
  ### bell_face
  ## bulk
  r_parser.add_argument('--axle_internal_diameter','--aid', action='store', type=float, default=20.0,
    help="Set the internal diameter of the bell-axle. Default: 20.0")
  r_parser.add_argument('--axle_external_diameter','--aed', action='store', type=float, default=0.0,
    help="Set the external diameter of the bell-axle. If equal to 0.0, set to 2*axle_internal_diameter. Default: 0.0")
  r_parser.add_argument('--leg_length','--ll', action='store', type=float, default=40.0,
    help="Set the length of the bell_leg. Default: 40.0")
  r_parser.add_argument('--bell_face_height','--bfh', action='store', type=float, default=80.0,
    help="Set the height of the bell-face and bell-side. Default: 80.0")
  r_parser.add_argument('--bell_face_width','--bfw', action='store', type=float, default=80.0,
    help="Set the width of the bell-face and bell-side. Default: 80.0")
  ### bell_base_disc
  r_parser.add_argument('--base_diameter','--bd', action='store', type=float, default=160.0,
    help="Set the diameter of the base-disc. Default: 160.0")
  ## wall_thickness
  r_parser.add_argument('--face_thickness','--ft', action='store', type=float, default=6.0,
    help="Set the thickness of the bell-face. Default: 6.0")
  r_parser.add_argument('--side_thickness','--st', action='store', type=float, default=4.0,
    help="Set the thickness of the bell-side. If equal to 0.0, set to face_thickness. Default: 4.0")
  r_parser.add_argument('--base_thickness','--bt', action='store', type=float, default=8.0,
    help="Set the thickness of the bell-base. If equal to 0.0, set to face_thickness. Default: 8.0")
  ## axle_hole
  r_parser.add_argument('--axle_hole_nb','--ahn', action='store', type=int, default=6,
    help="Set the number of the axle-holes. If equal to 0, no axle-hole is created. Default: 6")
  r_parser.add_argument('--axle_hole_diameter','--ahd', action='store', type=float, default=4.0,
    help="Set the diameter of the axle-holes. Default: 4.0")
  r_parser.add_argument('--axle_hole_position_diameter','--ahpd', action='store', type=float, default=0.0,
    help="Set the diameter of the axle-hole position circle. If equal to 0.0, set to (axle_internal_diameter+axle_external_diameter)/2. Default: 0.0")
  r_parser.add_argument('--axle_hole_angle','--aha', action='store', type=float, default=0.0,
    help="Set the position angle of the first axle-hole. Default: 0.0")
  ## leg
  r_parser.add_argument('--leg_spare_width','--lsw', action='store', type=float, default=10.0,
    help="Set the left and right spare_width of the bell-leg. Default: 10.0")
  r_parser.add_argument('--leg_smoothing_radius','--lsr', action='store', type=float, default=30.0,
    help="Set the smoothing radius of the bell-leg. Default: 30.0")
  ## motor_hole
  r_parser.add_argument('--motor_hole_diameter','--mhd', action='store', type=float, default=4.0,
    help="Set the diameter of the motor-holes. If equal to 0.0, no motor-hole is created. Default: 4.0")
  r_parser.add_argument('--motor_hole_x_distance','--mhxd', action='store', type=float, default=40.0,
    help="Set the x-distance of the motor-hole. Make it fit the motor_lid parameters. Default: 40.0")
  r_parser.add_argument('--motor_hole_z_distance','--mhzd', action='store', type=float, default=50.0,
    help="Set the z-distance of the motor-hole. Make it fit the motor_lid parameters. Default: 50.0")
  r_parser.add_argument('--motor_hole_z_position','--mhzp', action='store', type=float, default=40.0,
    help="Set the z-position of the motor-hole. Make it fit the gearwheel diameters. Default: 40.0")
  ## internal_buttress
  r_parser.add_argument('--int_buttress_x_length','--ibxl', action='store', type=float, default=10.0,
    help="Set the x-length of the internal-buttress-hole. If equal to 0.0, no internal-buttress hole is created. Default: 10.0")
  r_parser.add_argument('--int_buttress_z_width','--ibzw', action='store', type=float, default=5.0,
    help="Set the z-width of the internal-buttress-hole. Default: 5.0")
  r_parser.add_argument('--int_buttress_z_distance','--ibzd', action='store', type=float, default=50.0,
    help="Set the z-distance between a pair of internal-buttress. Default: 50.0")
  r_parser.add_argument('--int_buttress_x_position','--ibxp', action='store', type=float, default=10.0,
    help="Set the x-position of the internal-buttress-hole. Default: 10.0")
  r_parser.add_argument('--int_buttress_z_position','--ibzp', action='store', type=float, default=10.0,
    help="Set the z-position of the first internal-buttress. Default: 10.0")
  r_parser.add_argument('--int_buttress_int_corner_length','--ibicl', action='store', type=float, default=5.0,
    help="Set the internal-corner-length of the internal-buttress. Default: 5.0")
  r_parser.add_argument('--int_buttress_ext_corner_length','--ibecl', action='store', type=float, default=5.0,
    help="Set the external-corner-length of the internal-buttress. Default: 5.0")
  r_parser.add_argument('--int_buttress_bump_length','--ibbl', action='store', type=float, default=10.0,
    help="Set the bump-length of the internal-buttress. Default: 10.0")
  r_parser.add_argument('--int_buttress_arc_height','--ibah', action='store', type=float, default=-2.0,
    help="Set the arc-height of the internal-buttress. If equal to 0.0, a line is created instead of an arc. Default: -2.0")
  r_parser.add_argument('--int_buttress_smoothing_radius','--ibsr', action='store', type=float, default=10.0,
    help="Set the smoothing-radius of the internal-buttress. Default: 10.0")
  ## external_buttress
  r_parser.add_argument('--ext_buttress_z_length','--ebzl', action='store', type=float, default=10.0,
    help="Set the z-length of the external-buttress-hole. If equal to 0.0, no hole is generated on the face and side wall. Default: 10.0")
  r_parser.add_argument('--ext_buttress_x_width','--ebxw', action='store', type=float, default=5.0,
    help="Set the x-width of the external-buttress-hole. Default: 5.0")
  r_parser.add_argument('--ext_buttress_x_distance','--ebxd', action='store', type=float, default=20.0,
    help="Set the x-distance between a pair of the external-buttress. Default: 20.0")
  r_parser.add_argument('--ext_buttress_z_position','--ebzp', action='store', type=float, default=40.0,
    help="Set the z-position of the external-buttress-hole on the face and side wall. Default: 40.0")
  r_parser.add_argument('--ext_buttress_y_length','--ebyl', action='store', type=float, default=10.0,
    help="Set the y-length of the external-buttress-hole. If equal to 0.0, no hole is generated on the base wall. Default: 10.0")
  r_parser.add_argument('--ext_buttress_y_position','--ebyp', action='store', type=float, default=20.0,
    help="Set the y-position of the external-buttress-hole on the base wall. Default: 20.0")
  r_parser.add_argument('--ext_buttress_face_int_corner_length','--ebficl', action='store', type=float, default=5.0,
    help="Set the internal-corner-length of the external-buttress for the face and side crenel. Default: 5.0")
  r_parser.add_argument('--ext_buttress_face_ext_corner_length','--ebfecl', action='store', type=float, default=5.0,
    help="Set the external-corner-length of the external-buttress for the face and side crenel. Default: 5.0")
  r_parser.add_argument('--ext_buttress_face_bump_length','--ebfbl', action='store', type=float, default=10.0,
    help="Set the bump-length of the external-buttress for the face and side crenel. Default: 10.0")
  r_parser.add_argument('--ext_buttress_base_int_corner_length','--ebbicl', action='store', type=float, default=5.0,
    help="Set the internal-corner-length of the external-buttress for the base crenel. Default: 5.0")
  r_parser.add_argument('--ext_buttress_base_ext_corner_length','--ebbecl', action='store', type=float, default=5.0,
    help="Set the external-corner-length of the external-buttress for the base crenel. Default: 5.0")
  r_parser.add_argument('--ext_buttress_base_bump_length','--ebbbl', action='store', type=float, default=10.0,
    help="Set the bump-length of the external-buttress for the base crenel. Default: 10.0")
  r_parser.add_argument('--ext_buttress_arc_height','--ebah', action='store', type=float, default=-5.0,
    help="Set the arc-height of the external-buttress. If equal to 0.0, a line is created instead of an arc. Default: -5.0")
  r_parser.add_argument('--ext_buttress_smoothing_radius','--ebsr', action='store', type=float, default=10.0,
    help="Set the smoothing radius of the external-buttress. Default: 10.0")
  ### bell_side
  ## hollow
  r_parser.add_argument('--hollow_z_height','--hzh', action='store', type=float, default=10.0,
    help="Set the z-height of the bell-side-hollow. Default: 10.0")
  r_parser.add_argument('--hollow_y_width','--hyw', action='store', type=float, default=20.0,
    help="Set the y-width of the bell-side-hollow. Default: 20.0")
  r_parser.add_argument('--hollow_spare_width','--hsw', action='store', type=float, default=10.0,
    help="Set the spare_width of the bell-side-hollow. Default: 10.0")
  ## base_hole
  r_parser.add_argument('--base_hole_nb','--bhn', action='store', type=int, default=8,
    help="Set the number of base-holes. If equal to 0, no base-hole is created. Default: 8")
  r_parser.add_argument('--base_hole_diameter','--bhd', action='store', type=float, default=4.0,
    help="Set the diameter of the base-holes. Default: 4.0")
  r_parser.add_argument('--base_hole_position_diameter','--bhpd', action='store', type=float, default=0.0,
    help="Set the diameter of the base-hole position circle. If equal to 0.0, set to base_diameter-2*base_hole_diameter. Default: 0.0")
  r_parser.add_argument('--base_hole_angle','--bha', action='store', type=float, default=0.0,
    help="Set the position-angle of the first base-hole. Default: 0.0")
  ### xyz-axles
  ## y_hole
  r_parser.add_argument('--y_hole_diameter','--yhd', action='store', type=float, default=4.0,
    help="Set the diameter of the y-holes. If equal to 0.0, no y-hole is created. Default: 4.0")
  r_parser.add_argument('--y_hole_z_top_position','--yhztp', action='store', type=float, default=10.0,
    help="Set the z-position of the top y-holes. Default: 10.0")
  r_parser.add_argument('--y_hole_z_bottom_position','--yhzbp', action='store', type=float, default=10.0,
    help="Set the z-position of the bottom y-holes. Default: 10.0")
  r_parser.add_argument('--y_hole_x_position','--yhxp', action='store', type=float, default=6.0,
    help="Set the x-position of the y-holes. Default: 6.0")
  ## x_hole
  r_parser.add_argument('--x_hole_diameter','--xhd', action='store', type=float, default=4.0,
    help="Set the diameter of the x-holes. If equal to 0.0, no x-hole is created. Default: 4.0")
  r_parser.add_argument('--x_hole_z_top_position','--xhztp', action='store', type=float, default=-6.0,
    help="Set the z-position of the top y-holes. Default: -6.0")
  r_parser.add_argument('--x_hole_z_bottom_position','--xhzbp', action='store', type=float, default=-6.0,
    help="Set the z-position of the bottom y-holes. Default: -6.0")
  r_parser.add_argument('--x_hole_y_position','--xhyp', action='store', type=float, default=6.0,
    help="Set the y-position of the x-holes. Default: 6.0")
  ## z_hole
  r_parser.add_argument('--z_hole_diameter','--zhd', action='store', type=float, default=4.0,
    help="Set the diameter of the z-holes. If equal to 0.0, no z-hole is created. Default: 4.0")
  r_parser.add_argument('--z_hole_external_diameter','--zhed', action='store', type=float, default=0.0,
    help="Set the external-diameter of the z-holes. If equal to 0.0, set to 2*z_hole_diameter. Default: 4.0")
  r_parser.add_argument('--z_hole_position_length','--zhpl', action='store', type=float, default=15.0,
    help="Set the position-length of the z-holes. Default: 15.0")
  ### manufacturing
  r_parser.add_argument('--bell_cnc_router_bit_radius','--crbr', action='store', type=float, default=1.0,
    help="Set the minimal router_bit_radius for the whole design. Default: 1.0")
  r_parser.add_argument('--bell_extra_cut_thickness','--ect', action='store', type=float, default=0.0,
    help="Set the extra-cut-thickness for the rectangular-crenels. It can be used to compensate the manufacturing process or to check the 3D assembly with FreeCAD. Default: 0.0")
  ### output
  # return
  return(r_parser)

################################################################
# bell constraint_check
################################################################

def bell_constraint_check(c):
  """ check the bell constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  # axle_internal_diameter
  if(c['axle_internal_diameter']<radian_epsilon):
    print("ERR333: Error, axle_internal_diameter {:0.3f} is too small".format(c['axle_internal_diameter']))
    sys.exit(2)
  c['axle_internal_radius'] = c['axle_internal_diameter']/2.0
  # axle_external_diameter
  c['axle_external_radius'] = c['axle_external_diameter']/2.0
  if(c['axle_external_radius']==0):
    c['axle_external_radius'] = 2*c['axle_internal_radius']
  if(c['axle_external_radius']<c['axle_internal_radius']+radian_epsilon):
    print("ERR340: Error, axle_external_radius {:0.3f} must be bigger than axle_internal_radius {:0.3f}".format(c['axle_external_radius'], c['axle_internal_radius']))
    sys.exit(2)
  # leg_length
  if(c['leg_length']<c['axle_internal_radius']):
    print("ERR346: Error, leg_length {:0.3f} must be bigger than axle_internal_radius {:0.3f}".format(c['leg_length'], c['axle_internal_radius']))
    sys.exit(2)
  # bell_face_height
  if(c['bell_face_height']<radian_epsilon):
    print("ERR350: Error, bell_face_height {:0.3f} must be strictly positive".format(c['bell_face_height']))
    sys.exit(2)
  # bell_face_width
  if(c['bell_face_width']<2*c['axle_external_radius']):
    print("ERR354: Error, bell_face_width {:0.3f} is too small compare too axle_external_radius {:0.3f}".format(c['bell_face_width'], c['axle_external_radius']))
    sys.exit(2)
  # base_diameter
  c['base_radius'] = c['base_diameter']/2.0
  if(c['base_radius']<c['bell_face_width']/10.0*math.sqrt(5**2+1.5**2)):
    print("ERR357: Error, base_radius {:0.3f} is too small compare to bell_face_width {:0.3f}".format(c['base_radius'], c['bell_face_width']))
    sys.exit(2)
  # face_thickness
  if(c['face_thickness']<radian_epsilon):
    print("ERR358: Error, face_thickness {:0.3f} must be strictly positive".format(c['face_thickness']))
    sys.exit(2)
  if(c['face_thickness']>c['bell_face_width']/5.0):
    print("ERR361: Error, face_thickness {:0.3f} is too big compare to bell_face_width {:0.3f}".format(c['face_thickness'], c['bell_face_width']))
    sys.exit(2)
  # side_thickness
  if(c['side_thickness']==0.0):
    c['side_thickness'] = c['face_thickness']
  if(c['side_thickness']>c['bell_face_width']/5.0):
    print("ERR367: Error, side_thickness {:0.3f} is too big compare to bell_face_width {:0.3f}".format(c['side_thickness'], c['bell_face_width']))
    sys.exit(2)
  # base_thickness
  if(c['base_thickness']==0.0):
    c['base_thickness'] = c['face_thickness']
  # axle_hole_nb
  c['axle_hole_radius'] = 0.0
  c['axle_hole_position_radius'] = 0.0
  if(c['axle_hole_nb']>0):
    # axle_hole_diameter
    c['axle_hole_radius'] = c['axle_hole_diameter']/2.0
    if(c['axle_hole_radius']<radian_epsilon):
      print("ERR370: Error, axle_hole_radius {:0.3f} must be strictly positive".format(c['axle_hole_radius']))
      sys.exit(2)
    # axle_hole_position_diameter
    c['axle_hole_position_radius'] = c['axle_hole_position_diameter']/2.0
    if(c['axle_hole_position_radius']==0.0):
      c['axle_hole_position_radius'] = (c['axle_internal_radius']+c['axle_external_radius'])/2.0
    if(c['axle_hole_position_radius'] < c['axle_internal_radius']+c['axle_hole_radius']+radian_epsilon):
      print("ERR378: Error: axle_hole_position_radius {:0.3f} is too small compare to axle_internal_radius {:0.3f} and axle_hole_radius {:0.3f}".format(c['axle_hole_position_radius'], c['axle_internal_radius'], c['axle_hole_radius']))
      sys.exit(2)
    if(c['axle_hole_position_radius'] > c['axle_external_radius']-c['axle_hole_radius']-radian_epsilon):
      print("ERR381: Error: axle_hole_position_radius {:0.3f} is too big compare to axle_external_radius {:0.3f} and axle_hole_radius {:0.3f}".format(c['axle_hole_position_radius'], c['axle_external_radius'], c['axle_hole_radius']))
      sys.exit(2)
    # axle_hole_angle
  # leg_spare_width
  if(c['leg_spare_width'] > (c['bell_face_width']-2*c['axle_external_radius'])/2.0+radian_epsilon):
    print("ERR385: Error, leg_spare_width {:0.3f} is too big compare to bell_face_width {:0.3f} and axle_external_radius {:0.3f}".format(c['leg_spare_width'], c['bell_face_width'], c['axle_external_radius']))
    sys.exit(2)
  # leg_smoothing_radius
  if(c['leg_smoothing_radius']<c['bell_cnc_router_bit_radius']):
    print("ERR389: Error, leg_smoothing_radius {:0.3f} must be bigger than bell_cnc_router_bit_radius {:0.3f}".format(c['leg_smoothing_radius'], c['bell_cnc_router_bit_radius']))
    sys.exit(2)
  if(c['leg_smoothing_radius']<c['leg_spare_width']):
    print("ERR403: Error, leg_smoothing_radius {:0.3f} must be bigger than leg_spare_width {:0.3f}".format(c['leg_smoothing_radius'], c['leg_spare_width']))
    sys.exit(2)
  if(c['leg_smoothing_radius']>c['leg_length']):
    print("ERR392: Error, leg_smoothing_radius {:0.3f} must be bigger than leg_length {:0.3f}".format(c['leg_smoothing_radius'], c['leg_length']))
    sys.exit(2)
  # motor_hole_diameter
  c['motor_hole_radius'] = c['motor_hole_diameter']/2.0
  if(c['motor_hole_radius']>0.0):
    # motor_hole_x_distance
    if(c['motor_hole_x_distance']<2*c['motor_hole_radius']+radian_epsilon):
      print("ERR399: Error, motor_hole_x_distance {:0.3f} is too small compare to motor_hole_radius {:0.3f}".format(c['motor_hole_x_distance'], c['motor_hole_radius']))
      sys.exit(2)
    if(c['motor_hole_x_distance']>c['bell_face_width']-2*c['side_thickness']-2*c['motor_hole_radius']-radian_epsilon):
      print("ERR402: Error, motor_hole_x_distance {:0.3f} is too big compare to bell_face_width {:0.3f}, side_thickness {:0.3f} and motor_hole_radius {:0.3f}".format(c['motor_hole_x_distance'], c['bell_face_width'], c['side_thickness'], c['motor_hole_radius']))
      sys.exit(2)
    # motor_hole_z_distance
    if(c['motor_hole_z_distance']<2*c['motor_hole_radius']+radian_epsilon):
      print("ERR406: Error, motor_hole_z_distance {:0.3f} is too small compare to motor_hole_radius {:0.3f}".format(c['motor_hole_z_distance'], c['motor_hole_radius']))
      sys.exit(2)
    if(c['motor_hole_z_distance']>c['bell_face_height']+c['leg_length']-2*c['motor_hole_radius']-radian_epsilon):
      print("ERR409: Error, motor_hole_z_distance {:0.3f} is too big compare to bell_face_height {:0.3f}, leg_length {:0.3f} and motor_hole_radius {:0.3f}".format(c['motor_hole_z_distance'], c['bell_face_height'], c['leg_length'], c['motor_hole_radius']))
      sys.exit(2)
    # motor_hole_z_position
    if(c['motor_hole_z_position']<c['motor_hole_radius']+radian_epsilon):
      print("ERR413: Error, motor_hole_z_position {:0.3f} is too small compare to motor_hole_radius {:0.3f}".format(c['motor_hole_z_position'], c['motor_hole_radius']))
      sys.exit(2)
    if(c['motor_hole_z_position']>c['bell_face_height']+c['leg_length']-c['motor_hole_z_distance']-2*c['motor_hole_radius']-radian_epsilon):
      print("ERR416: Error, motor_hole_z_distance {:0.3f} is too big compare to bell_face_height {:0.3f}, leg_length {:0.3f}, motor_hole_z_distance {:0.3f} and motor_hole_radius {:0.3f}".format(c['motor_hole_z_distance'], c['bell_face_height'], c['leg_length'], c['motor_hole_z_distance'], c['motor_hole_radius']))
      sys.exit(2)
  # int_buttress_x_length
  if(c['int_buttress_x_length']>(c['bell_face_width']-2*c['side_thickness'])/3.0):
    print("ERR426: Error, int_buttress_x_length {:0.3f} is too big compare to bell_face_width {:0.3f} and side_thickness {:0.3f}".format(c['int_buttress_x_length'], c['bell_face_width'], c['side_thickness']))
    sys.exit(2)
  if(c['int_buttress_x_length']>0):
    # int_buttress_z_width
    if(c['int_buttress_z_width']<3*c['bell_cnc_router_bit_radius']):
      print("ERR431: Error, int_buttress_z_width {:0.3f} is too small compare to bell_cnc_router_bit_radius {:0.3f}".format(c['int_buttress_z_width'], c['bell_cnc_router_bit_radius']))
      sys.exit(2)
    if(c['int_buttress_z_width']>c['bell_face_height']/5.0):
      print("ERR434: Error, int_buttress_z_width {:0.3f} is too big compare to bell_face_height {:0.3f}".format(c['int_buttress_z_width'], c['bell_face_height']))
      sys.exit(2)
    # int_buttress_z_distance
    if(c['int_buttress_z_distance']<c['int_buttress_z_width']+radian_epsilon):
      print("ERR438: Error, int_buttress_z_distance {:0.3f} must be bigger than int_buttress_z_width {:0.3f}".format(c['int_buttress_z_distance'], c['int_buttress_z_width']))
      sys.exit(2)
    if(c['int_buttress_z_distance']>c['bell_face_height']-2*c['int_buttress_z_width']-radian_epsilon):
      print("ERR441: Error, int_buttress_z_distance {:0.3f} is too big compare to bell_face_height {:0.3f} and int_buttress_z_width {:0.3f}".format(c['int_buttress_z_distance'], c['bell_face_height'], c['int_buttress_z_width']))
      sys.exit(2)
    # int_buttress_x_position
    if(c['int_buttress_x_position']>c['bell_face_width']/2.0-c['face_thickness']-c['int_buttress_x_length']):
      print("ERR445: Error, int_buttress_x_position {:0.3f} is too big compare to bell_face_width {:0.3f}, face_thickness {:0.3f} and int_buttress_x_length {:0.3f}".format(c['int_buttress_x_position'], c['bell_face_width'], c['face_thickness'], c['int_buttress_x_length']))
      sys.exit(2)
    # int_buttress_z_position
    if(c['int_buttress_z_position']>c['bell_face_height']-c['int_buttress_z_distance']-c['int_buttress_z_width']-radian_epsilon):
      print("ERR448: int_buttress_z_position {:0.3f} is too big compare to bell_face_height {:0.3f}, int_buttress_z_distance {:0.3f} and int_buttress_z_width {:0.3f}".format(c['int_buttress_z_position'], c['bell_face_height'], c['int_buttress_z_distance'], c['int_buttress_z_width']))
      sys.exit(2)
    # int_buttress_int_corner_length
    if(c['int_buttress_int_corner_length']>c['int_buttress_x_position']):
      print("ERR453: Error, int_buttress_int_corner_length {:0.3f} must be smaller than int_buttress_x_position {:0.3f}".format(c['int_buttress_int_corner_length'], c['int_buttress_x_position']))
      sys.exit(2)
    # int_buttress_ext_corner_length
    if(c['int_buttress_ext_corner_length']>c['bell_face_width']/2.0-c['face_thickness']-c['int_buttress_x_length']-c['int_buttress_x_position']):
      print("ERR457: Error, int_buttress_ext_corner_length {:0.3f} is too big comapre to bell_face_width {:0.3f}, face_thickness {:0.3f}, int_buttress_x_length {:0.3f} and int_buttress_x_position {:0.3f}".format(c['int_buttress_ext_corner_length'], c['bell_face_width'], c['face_thickness'], c['int_buttress_x_length'], c['int_buttress_x_position']))
      sys.exit(2)
    # int_buttress_bump_length
    if(c['int_buttress_bump_length']>c['int_buttress_x_position']+c['int_buttress_x_length']):
      print("ERR461: Error, int_buttress_bump_length {:0.3f} is too big compare to int_buttress_x_position {:0.3f} and int_buttress_x_length {:0.3f}".format(c['int_buttress_bump_length'], c['int_buttress_x_position'], c['int_buttress_x_length']))
      sys.exit(2)
    # int_buttress_arc_height
    if(abs(c['int_buttress_arc_height'])>c['int_buttress_x_length']):
      print("ERR465: Error, int_buttress_arc_height {:0.3f} absolute value must be smaller than int_buttress_x_length {:0.3f}".format(c['int_buttress_arc_height'], c['int_buttress_x_length']))
      sys.exit(2)
    # int_buttress_smoothing_radius
    if(c['int_buttress_smoothing_radius']>c['int_buttress_bump_length']):
      print("ERR469: Error, int_buttress_smoothing_radius {:0.3f} must be smaller than int_buttress_bump_length {:0.3f}".format(c['int_buttress_smoothing_radius'], c['int_buttress_bump_length']))
      sys.exit(2)
  # ext_buttress_z_length
  if(c['ext_buttress_z_length']>c['bell_face_height']/3.0):
    print("ERR473: Error, ext_buttress_z_length {:0.3f} is too big compare to bell_face_height {:0.3f}".format(c['ext_buttress_z_length'], c['bell_face_height']))
    sys.exit(2)
  if(c['ext_buttress_z_length']>0):
    # ext_buttress_x_width
    if(c['ext_buttress_x_width']<3*c['bell_cnc_router_bit_radius']):
      print("ERR478: Error, ext_buttress_x_width {:0.3f} is too small compare to bell_cnc_router_bit_radius {:0.3f}".format(c['ext_buttress_x_width'], c['bell_cnc_router_bit_radius']))
      sys.exit(2)
    if(c['ext_buttress_x_width']>c['bell_face_width']/5.0):
      print("ERR481: Error, ext_buttress_x_width {:0.3f} is too big compare to bell_face_width {:0.3f}".format(c['ext_buttress_x_width'], c['bell_face_width']))
      sys.exit(2)
    # ext_buttress_x_distance
    if(c['ext_buttress_x_distance']<radian_epsilon):
      print("ERR485: Error, ext_buttress_x_distance {:0.3f} must be strictly positive".format(c['ext_buttress_x_distance']))
      sys.exit(2)
    if(c['ext_buttress_x_distance']>c['bell_face_width']-2*c['ext_buttress_x_width']-2*c['face_thickness']):
      print("ERR488: Error, ext_buttress_x_distance {:0.3f} is too big compare to bell_face_width {:0.3f} ext_buttress_x_width {:0.3f} and face_thickness {:0.3f}".format(c['ext_buttress_x_distance'], c['bell_face_width'], c['ext_buttress_x_width'], c['face_thickness']))
      sys.exit(2)
    # ext_buttress_z_position
    if(c['ext_buttress_z_position']>c['bell_face_height']+c['leg_length']-c['ext_buttress_z_length']):
      print("ERR490: Error, ext_buttress_z_position {:0.3f} is too big compare to bell_face_height {:0.3f}, leg_length {:0.3f} and ext_buttress_z_length {:0.3f}".format(c['ext_buttress_z_position'], c['bell_face_height'], c['leg_length'], c['ext_buttress_z_length']))
      sys.exit(2)
    # ext_buttress_y_length
    if(c['ext_buttress_y_length']>c['base_radius']-c['bell_face_width']/2.0):
      print("ERR499: Error, ext_buttress_y_length {:0.3f} is too big compare to base_radius {:0.3f} and bell_face_width {:0.3f}".format(c['ext_buttress_y_length'], c['base_radius'], c['bell_face_width']))
      sys.exit(2)
    # ext_buttress_y_position
    if(math.sqrt((c['ext_buttress_x_distance']/2.0+c['ext_buttress_x_width'])**2+(c['bell_face_width']/2.0+c['ext_buttress_y_position']+c['ext_buttress_y_length'])**2)>c['base_radius']):
      print("ERR502: Error, ext_buttress_y_position {:0.3f} is too big compare to ext_buttress_x_distance {:0.3f}, ext_buttress_x_width {:0.3f}, bell_face_width {:0.3f}, ext_buttress_y_length {:0.3f} and base_radius {:0.3f}".format(c['ext_buttress_y_position'], c['ext_buttress_x_distance'], c['ext_buttress_x_width'], c['bell_face_width'], c['ext_buttress_y_length'], c['base_radius']))
      sys.exit(2)
    # ext_buttress_face_int_corner_length
    if(c['ext_buttress_face_int_corner_length']>c['ext_buttress_z_position']):
      print("ERR507: Error, ext_buttress_face_int_corner_length {:0.3f} must be smaller than ext_buttress_z_position {:0.3f}".format(c['ext_buttress_face_int_corner_length'], c['ext_buttress_z_position']))
      sys.exit(2)
    # ext_buttress_face_ext_corner_length
    if(c['ext_buttress_face_ext_corner_length']>c['bell_face_height']+c['leg_length']-c['ext_buttress_z_length']):
      print("ext_buttress_face_ext_corner_length {:0.3f} is too big compare to bell_face_height {:0.3f}, leg_length {:0.3f} and ext_buttress_z_length {:0.3f}".format(c['ext_buttress_face_ext_corner_length'], c['bell_face_height'], c['leg_length'], c['ext_buttress_z_length']))
      sys.exit(2)
    # ext_buttress_face_bump_length
    if(c['ext_buttress_face_bump_length']>c['ext_buttress_y_position']+c['ext_buttress_y_length']):
      print("ERR515: Error, ext_buttress_face_bump_length {:0.3f} is too big compare to ext_buttress_y_position {:0.3f} and ext_buttress_y_length {:0.3f}".format(c['ext_buttress_face_bump_length'], c['ext_buttress_y_position'], c['ext_buttress_y_length']))
      sys.exit(2)
    # ext_buttress_base_int_corner_length
    if(c['ext_buttress_base_int_corner_length']>c['ext_buttress_y_position']):
      print("ERR519: Error, ext_buttress_base_int_corner_length {:0.3f} must be smaller than ext_buttress_y_position {:0.3f}".format(c['ext_buttress_base_int_corner_length'], c['ext_buttress_y_position']))
      sys.exit(2)
    # ext_buttress_base_ext_corner_length
    if(c['ext_buttress_base_ext_corner_length']>c['base_radius']-(c['bell_face_width']/2.0+c['ext_buttress_y_position']+c['ext_buttress_y_length'])):
      print("ERR523: Error, ext_buttress_base_ext_corner_length {:0.3f} is too big compare to base_radius {:0.3f}, bell_face_width {:0.3f}, ext_buttress_y_position {:0.3f} and ext_buttress_y_length {:0.3f}".format(c['ext_buttress_base_ext_corner_length'], c['base_radius'], c['bell_face_width'], c['ext_buttress_y_position'], c['ext_buttress_y_length']))
      sys.exit(2)
    # ext_buttress_base_bump_length
    if(c['ext_buttress_base_bump_length']>c['ext_buttress_z_position']+c['ext_buttress_z_length']):
      print("ERR527: Error, ext_buttress_base_bump_length {:0.3f} is too big compare to ext_buttress_z_position {:0.3f} and ext_buttress_z_length {:0.3f}".format(c['ext_buttress_base_bump_length'], c['ext_buttress_z_position'], c['ext_buttress_z_length']))
      sys.exit(2)
    # ext_buttress_arc_height
    if(abs(c['ext_buttress_arc_height'])>max(c['ext_buttress_z_length'], c['ext_buttress_y_length'])):
      print("ERR531: Error, ext_buttress_arc_height {:0.3f} absolute value is too big compare to ext_buttress_z_length {:0.3f} and ext_buttress_y_length {:0.3f}".format(c['ext_buttress_arc_height'], c['ext_buttress_z_length'], c['ext_buttress_y_length']))
      sys.exit(2)
    # ext_buttress_smoothing_radius
    if(c['ext_buttress_smoothing_radius']>max(c['ext_buttress_face_bump_length'], c['ext_buttress_base_bump_length'])):
      print("ERR535: Error, ext_buttress_smoothing_radius {:0.3f} is too big compare to ext_buttress_face_bump_length {:0.3f} and ext_buttress_base_bump_length {:0.3f}".format(c['ext_buttress_smoothing_radius'], c['ext_buttress_face_bump_length'], c['ext_buttress_base_bump_length']))
      sys.exit(2)
  # hollow_z_height
  if(c['hollow_z_height']>c['bell_face_height']):
    print("ERR539: Error, hollow_z_height {:0.3f} must be smaller than bell_face_height {:0.3f}".format(c['hollow_z_height'], c['bell_face_height']))
    sys.exit(2)
  # hollow_y_width
  if(c['hollow_y_width']<2*c['bell_cnc_router_bit_radius']):
    print("ERR543: Error, hollow_y_width {:0.3f} is too small compare to bell_cnc_router_bit_radius {:0.3f}".format(c['hollow_y_width'], c['bell_cnc_router_bit_radius']))
    sys.exit(2)
  if(c['hollow_y_width']>c['bell_face_width']-2*c['face_thickness']):
    print("ERR546: Error, hollow_y_width {:0.3f} is too big compare to bell_face_width {:0.3f} and face_thickness {:0.3f}".format(c['hollow_y_width'], c['bell_face_width'], c['face_thickness']))
    sys.exit(2)
  # hollow_spare_width
  if(c['hollow_spare_width']>c['bell_face_width']/2-c['face_thickness']-c['hollow_y_width']/2.0):
    print("ERR550: Error, hollow_spare_width {:0.3f} is too big compare to bell_face_width {:0.3f}, face_thickness {:0.3f} and hollow_y_width {:0.3f}".format(c['hollow_spare_width'], c['bell_face_width'], c['face_thickness'], c['hollow_y_width']))
    sys.exit(2)
  # base_hole_nb
  if(c['base_hole_nb']>0):
    # base_hole_diameter
    c['base_hole_radius'] = c['base_hole_diameter']/2.0
    if(c['base_hole_radius']<radian_epsilon):
      print("ERR556: Error, base_hole_radius {:0.3f} must be strictly positive".format(c['base_hole_radius']))
      sys.exit(2)
    # base_hole_position_diameter
    c['base_hole_position_radius'] = c['base_hole_position_diameter']/2.0
    if(c['base_hole_position_radius']==0):
      c['base_hole_position_radius'] = c['base_radius'] - 2*c['base_hole_radius']
    if(c['base_hole_position_radius']<c['bell_face_width']/2.0):
      print("ERR564: Error, base_hole_position_radius {:0.3f} is too small compare to bell_face_width {:0.3f}".format(c['base_hole_position_radius'], c['bell_face_width']))
      sys.exit(2)
    if(c['base_hole_position_radius']>c['base_radius']-c['base_hole_radius']):
      print("ERR567: Error, base_hole_position_radius {:0.3f} is too big compare to base_radius {:0.3f} and base_hole_radius {:0.3f}".format(c['base_hole_position_radius'], c['base_radius'], c['base_hole_radius']))
      sys.exit(2)
    # base_hole_angle
  # y_hole_diameter
  c['y_hole_radius'] = c['y_hole_diameter']/2.0
  if(c['y_hole_radius']>0):
    # y_hole_z_top_position
    if(abs(c['y_hole_z_top_position'])>c['bell_face_height']):
      print("ERR575: Error, y_hole_z_top_position {:0.3f} absolute value is too big compare to bell_face_height {:0.3f}".format(c['y_hole_z_top_position'], c['bell_face_height']))
      sys.exit(2)
    if(c['y_hole_z_top_position']>0):
      if(c['y_hole_z_top_position']<c['int_buttress_z_width']+c['y_hole_radius']):
        print("ERR580: Error, positive y_hole_z_top_position {:0.3f} is too small compare to int_buttress_z_width {:0.3f} and y_hole_radius {:0.3f}".format(c['y_hole_z_top_position'], c['int_buttress_z_width'], c['y_hole_radius']))
        sys.exit(2)
    else:
      if(c['y_hole_z_top_position']>-1*c['y_hole_radius']):
        print("ERR584: Error, negative y_hole_z_top_position {:0.3f} must be smaller than y_hole_radius {:0.3f}".format(c['y_hole_z_top_position'], -1*c['y_hole_radius']))
        sys.exit(2)
    # y_hole_z_bottom_position
    if(abs(c['y_hole_z_bottom_position'])>c['bell_face_height']):
      print("ERR575: Error, y_hole_z_bottom_position {:0.3f} absolute value is too big compare to bell_face_height {:0.3f}".format(c['y_hole_z_bottom_position'], c['bell_face_height']))
      sys.exit(2)
    if(c['y_hole_z_bottom_position']>0):
      if(c['y_hole_z_bottom_position']<c['int_buttress_z_width']+c['y_hole_radius']):
        print("ERR580: Error, positive y_hole_z_bottom_position {:0.3f} is too small compare to int_buttress_z_width {:0.3f} and y_hole_radius {:0.3f}".format(c['y_hole_z_bottom_position'], c['int_buttress_z_width'], c['y_hole_radius']))
        sys.exit(2)
    else:
      if(c['y_hole_z_bottom_position']>-1*c['y_hole_radius']):
        print("ERR584: Error, negative y_hole_z_bottom_position {:0.3f} must be smaller than y_hole_radius {:0.3f}".format(c['y_hole_z_bottom_position'], -1*c['y_hole_radius']))
        sys.exit(2)
    # y_hole_x_position
    if(c['y_hole_x_position']<c['y_hole_radius']):
      print("ERR588: Error, y_hole_x_position {:0.3f} is too small compare to y_hole_radius {:0.3f}".format(c['y_hole_x_position'], c['y_hole_radius']))
      sys.exit(2)
    if(c['y_hole_x_position']>c['bell_face_width']/2.0-c['side_thickness']):
      print("ERR591: Error, y_hole_x_position {:0.3f} is too big compare to bell_face_width {:0.3f} and side_thickness {:0.3f}".format(c['y_hole_x_position'], c['bell_face_width'], c['side_thickness']))
      sys.exit(2)
  # x_hole_diameter
  c['x_hole_radius'] = c['x_hole_diameter']/2.0
  if(c['x_hole_radius']>0):
    # x_hole_z_top_position
    if(abs(c['x_hole_z_top_position'])>c['bell_face_height']):
      print("ERR598: Error, x_hole_z_top_position {:0.3f} absolute value is too big compare to bell_face_height {:0.3f}".format(c['x_hole_z_top_position'], c['bell_face_height']))
      sys.exit(2)
    if(c['x_hole_z_top_position']>0):
      if(c['x_hole_z_top_position']<c['int_buttress_z_width']+c['x_hole_radius']):
        print("ERR580: Error, positive x_hole_z_top_position {:0.3f} is too small compare to int_buttress_z_width {:0.3f} and x_hole_radius {:0.3f}".format(c['x_hole_z_top_position'], c['int_buttress_z_width'], c['x_hole_radius']))
        sys.exit(2)
    else:
      if(c['x_hole_z_top_position']>-1*c['x_hole_radius']):
        print("ERR584: Error, negative x_hole_z_top_position {:0.3f} must be smaller than x_hole_radius {:0.3f}".format(c['x_hole_z_top_position'], -1*c['x_hole_radius']))
        sys.exit(2)
    # x_hole_z_bottom_position
    if(abs(c['x_hole_z_bottom_position'])>c['bell_face_height']):
      print("ERR598: Error, x_hole_z_bottom_position {:0.3f} absolute value is too big compare to bell_face_height {:0.3f}".format(c['x_hole_z_bottom_position'], c['bell_face_height']))
      sys.exit(2)
    if(c['x_hole_z_bottom_position']>0):
      if(c['x_hole_z_bottom_position']<c['int_buttress_z_width']+c['x_hole_radius']):
        print("ERR580: Error, positive x_hole_z_bottom_position {:0.3f} is too small compare to int_buttress_z_width {:0.3f} and x_hole_radius {:0.3f}".format(c['x_hole_z_bottom_position'], c['int_buttress_z_width'], c['x_hole_radius']))
        sys.exit(2)
    else:
      if(c['x_hole_z_bottom_position']>-1*c['x_hole_radius']):
        print("ERR584: Error, negative x_hole_z_bottom_position {:0.3f} must be smaller than x_hole_radius {:0.3f}".format(c['x_hole_z_bottom_position'], -1*c['x_hole_radius']))
        sys.exit(2)
    # x_hole_y_position
    if(c['x_hole_y_position']<c['x_hole_radius']):
      print("ERR588: Error, x_hole_y_position {:0.3f} is too small compare to x_hole_radius {:0.3f}".format(c['x_hole_y_position'], c['x_hole_radius']))
      sys.exit(2)
    if(c['x_hole_y_position']>c['bell_face_width']/2.0-c['side_thickness']):
      print("ERR591: Error, x_hole_y_position {:0.3f} is too big compare to bell_face_width {:0.3f} and side_thickness {:0.3f}".format(c['x_hole_y_position'], c['bell_face_width'], c['side_thickness']))
      sys.exit(2)
  # z_hole_diameter
  c['z_hole_radius'] = c['z_hole_diameter']/2.0
  # z_hole_external_diameter
  c['z_hole_external_radius'] = c['z_hole_external_diameter']/2.0
  if(c['z_hole_external_radius']==0):
    c['z_hole_external_radius'] = 2*c['z_hole_radius']
  # z_hole_position_length
  if(c['z_hole_position_length']<math.sqrt(2)*c['z_hole_radius']):
    print("ERR623: Error, z_hole_position_length {:0.3f} is too small compare to z_hole_radius {:0.3f}".format(c['z_hole_position_length'], c['z_hole_radius']))
    sys.exit(2)
  if(c['z_hole_position_length']>c['bell_face_width']/2.0):
    print("ERR626: Error, z_hole_position_length {:0.3f} is too big compare to bell_face_width {:0.3f}".format(c['z_hole_position_length'], c['bell_face_width']))
    sys.exit(2)
  # bell_cnc_router_bit_radius
  if(c['bell_cnc_router_bit_radius']>min(c['face_thickness'], c['side_thickness'], c['base_thickness'])/2.0):
    print("ERR634: Error, bell_cnc_router_bit_radius {:0.3f} is too big compare to face_thickness {:0.3f}, side_thickness {:0.3f} or base_thickness {:0.3f}".format(c['bell_cnc_router_bit_radius'], c['face_thickness'], c['side_thickness'], c['base_thickness']))
    sys.exit(2)
  # bell_extra_cut_thickness
  if(c['bell_extra_cut_thickness']>min(c['bell_face_width'], c['bell_face_height'])/10.0):
    print("ERR630: Error, bell_extra_cut_thickness {:0.3f} is too big compare to bell_face_width {:0.3f} and bell_face_height {:0.3f}".format(c['bell_extra_cut_thickness'], c['bell_face_width'], c['bell_face_height']))
    sys.exit(2)
  ## intermediate parameters
  c['f_w2'] = c['bell_face_width']/2.0
  c['ib_x_zero'] = c['int_buttress_ext_corner_length']
  c['ib_x_size'] = c['int_buttress_x_length']
  c['ib_y_size'] = c['face_thickness']
  c['eb_x_zero'] = c['ext_buttress_base_ext_corner_length']
  c['eb_x_size'] = c['ext_buttress_y_length']
  c['eb_y_size'] = c['base_thickness']
  c['ib_abs_x1_position'] = -1*c['bell_face_width']/2.0 + c['side_thickness'] + c['int_buttress_x_position']
  c['ib_abs_x2_position'] = c['bell_face_width']/2.0 - c['side_thickness'] - c['int_buttress_x_position'] - c['int_buttress_x_length']
  c['eb_abs_x1_position'] = -1*c['f_w2'] - c['ext_buttress_y_position'] - c['ext_buttress_y_length']
  c['eb_abs_x2_position'] = c['f_w2'] + c['ext_buttress_y_position']
  return(c)

    
################################################################
# bell 2D-figures construction
################################################################

def bell_2d_construction(c):
  """ construct the 2D-figures with outlines at the A-format for the bell design
  """
  r_figures = {}
  r_height = {}
  ### base-figures
  r_figures['bell_face'] = bell_outline.bell_face(c)
  r_height['bell_face'] = c['face_thickness']

  r_figures['bell_side'] = bell_outline.bell_side(c)
  r_height['bell_side'] = c['side_thickness']

  r_figures['bell_base'] = bell_outline.bell_base(c)
  r_height['bell_base'] = c['base_thickness']

  r_figures['bell_internal_buttress'] = bell_outline.bell_internal_buttress(c)
  r_height['bell_internal_buttress'] = c['int_buttress_z_width']

  r_figures['bell_external_face_buttress'] = bell_outline.bell_external_buttress(c, 'face')
  r_height['bell_external_face_buttress'] = c['ext_buttress_x_width']

  r_figures['bell_external_side_buttress'] = bell_outline.bell_external_buttress(c, 'side')
  r_height['bell_external_side_buttress'] = c['ext_buttress_x_width']
  #
  ### output-figures
  # part_list
  part_list = []
  part_list.append(r_figures['bell_face'])
  part_list.append(r_figures['bell_side'])
  part_list.append(r_figures['bell_base'])
  part_list.append(r_figures['bell_internal_buttress'])
  part_list.append(r_figures['bell_external_face_buttress'])
  part_list.append(r_figures['bell_external_side_buttress'])
  # part_list_figure
  x_space = 1.2*c['base_radius'] 
  y_space = 1.2*c['base_radius'] 
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## sub-assembly
  # internal_buttress_assembly
  internal_buttress_assembly = []
  internal_buttress_assembly.extend(cnc25d_api.rotate_and_translate_figure(r_figures['bell_base'], 0.0, 0.0, 0.0, 0.0, 0.0))
  internal_buttress_assembly.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['bell_internal_buttress'], c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], -1,  1, 0.0, c['ib_abs_x1_position'], -1*c['f_w2']))
  internal_buttress_assembly.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['bell_internal_buttress'], c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], -1, -1, 0.0, c['ib_abs_x1_position'],  1*c['f_w2']-c['ib_y_size']))
  internal_buttress_assembly.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['bell_internal_buttress'], c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'],  1,  1, 0.0, c['ib_abs_x2_position'], -1*c['f_w2']))
  internal_buttress_assembly.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['bell_internal_buttress'], c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'],  1, -1, 0.0, c['ib_abs_x2_position'],  1*c['f_w2']-c['ib_y_size']))
  # external_buttress_assembly
  external_buttress_assembly = []
  external_buttress_assembly.extend(cnc25d_api.rotate_and_translate_figure(r_figures['bell_face'], 0.0, 0.0, 0.0, 0.0, 0.0))
  external_buttress_assembly.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['bell_external_side_buttress'], c['eb_x_zero'], 0.0, c['eb_x_size'], c['eb_y_size'],  1, 1, 0.0, c['eb_abs_x1_position'], 0.0))
  external_buttress_assembly.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['bell_external_side_buttress'], c['eb_x_zero'], 0.0, c['eb_x_size'], c['eb_y_size'], -1, 1, 0.0, c['eb_abs_x2_position'], 0.0))
  ## bell_part_overview
  bell_part_overview_figure = []
  bell_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(r_figures['bell_face'], 0.0, 0.0, 0.0, 0*x_space, 1*y_space))
  bell_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(r_figures['bell_side'], 0.0, 0.0, 0.0, 1*x_space, 1*y_space))
  bell_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(r_figures['bell_base'], 0.0, 0.0, 0.0, 0*x_space, 0*y_space))
  bell_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(r_figures['bell_internal_buttress'], 0.0, 0.0, 0.0, 1*x_space, 0*y_space))
  bell_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(r_figures['bell_external_face_buttress'], 0.0, 0.0, 0.0, 1.5*x_space, 0*y_space))
  bell_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(r_figures['bell_external_side_buttress'], 0.0, 0.0, 0.0, 1.5*x_space, -0.8*y_space))
  #
  r_figures['part_list'] = part_list_figure
  r_height['part_list'] = 1.0

  r_figures['internal_buttress_assembly'] = internal_buttress_assembly
  r_height['internal_buttress_assembly'] = 1.0

  r_figures['external_buttress_assembly'] = external_buttress_assembly
  r_height['external_buttress_assembly'] = 1.0

  r_figures['bell_part_overview'] = bell_part_overview_figure
  r_height['bell_part_overview'] = 1.0
  ### addition threaded rods
  r_figures['z_rod'] = [(0, 0, 0.9*c['z_hole_radius'])]
  r_height['z_rod'] = c['base_thickness']+c['bell_face_height']

  r_figures['x_rod'] = [(0, 0, 0.9*c['x_hole_radius'])]
  r_height['x_rod'] = c['bell_face_height']+2*c['x_hole_radius']

  r_figures['y_rod'] = [(0, 0, 0.9*c['y_hole_radius'])]
  r_height['y_rod'] = c['bell_face_height']+2*c['x_hole_radius']
  ###
  return((r_figures, r_height))

################################################################
# bell 3D assembly-configuration construction
################################################################

def bell_3d_construction(c):
  """ construct the 3D-assembly-configurations of the bell design
  """
  ### freecad-object assembly configuration
  # intermediate parameters
  #int_buttress_y_size = c['face_thickness'] + c['int_buttress_x_position'] + c['int_buttress_int_corner_length'] + c['int_buttress_x_length'] + c['int_buttress_ext_corner_length']
  int_butt_abs_z1_position = c['base_thickness'] + c['int_buttress_z_position']
  int_butt_abs_z2_position = int_butt_abs_z1_position + c['int_buttress_z_distance']
  #c['ib_x_zero'] =  c['int_buttress_ext_corner_length']
  #c['ib_x_size'] = c['int_buttress_x_length']
  #c['ib_y_size'] = c['face_thickness']
  ib_z_size = c['int_buttress_z_width']
  f_w2b = c['f_w2'] - c['face_thickness']
  #c['eb_x_zero'] = c['ext_buttress_base_ext_corner_length']
  #c['eb_x_size'] = c['ext_buttress_y_length']
  #c['eb_y_size'] = c['base_thickness']
  eb_z_size = c['ext_buttress_x_width']
  ext_side_butt_abs_x1_position = c['eb_abs_x1_position']
  ext_side_butt_abs_x2_position = c['eb_abs_x2_position']
  ext_side_butt_abs_y1_position = -1*(c['ext_buttress_x_distance']/2.0 + 1*c['ext_buttress_x_width'])
  ext_side_butt_abs_y2_position =  1*(c['ext_buttress_x_distance']/2.0 + 0*c['ext_buttress_x_width'])
  ext_face_butt_abs_x1_position = ext_side_butt_abs_y1_position
  ext_face_butt_abs_x2_position = ext_side_butt_abs_y2_position
  ext_face_butt_abs_y1_position = ext_side_butt_abs_x1_position
  ext_face_butt_abs_y2_position = ext_side_butt_abs_x2_position
  # conf1
  bell_assembly_conf1 = []
  bell_assembly_conf1.append(('bell_base', 0, 0, c['base_radius'], c['base_radius'], c['base_thickness'], 'i', 'xy', 0, 0, 0))
  bell_assembly_conf1.append(('bell_face', -c['f_w2'], 0, 2*c['f_w2'], c['bell_face_height'], c['face_thickness'], 'i', 'xz', -c['f_w2'], c['f_w2']-c['face_thickness'], 0))
  bell_assembly_conf1.append(('bell_face', -c['f_w2'], 0, 2*c['f_w2'], c['bell_face_height'], c['face_thickness'], 'i', 'xz', -c['f_w2'], -c['f_w2'], 0))
  bell_assembly_conf1.append(('bell_side', -c['f_w2'], 0, 2*c['f_w2'], c['bell_face_height'], c['side_thickness'], 'i', 'yz', c['f_w2']-c['side_thickness'], -c['f_w2'], 0))
  bell_assembly_conf1.append(('bell_side', -c['f_w2'], 0, 2*c['f_w2'], c['bell_face_height'], c['side_thickness'], 'i', 'yz', -c['f_w2'], -c['f_w2'], 0))
  bell_assembly_conf1.append(('bell_internal_buttress', c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], ib_z_size, 'y', 'xy', c['ib_abs_x1_position'], -c['f_w2'], int_butt_abs_z2_position))
  bell_assembly_conf1.append(('bell_internal_buttress', c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], ib_z_size, 'i', 'xy', c['ib_abs_x2_position'], -c['f_w2'], int_butt_abs_z2_position))
  bell_assembly_conf1.append(('bell_internal_buttress', c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], ib_z_size, 'z', 'xy', c['ib_abs_x1_position'], f_w2b, int_butt_abs_z2_position))
  bell_assembly_conf1.append(('bell_internal_buttress', c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], ib_z_size, 'x', 'xy', c['ib_abs_x2_position'], f_w2b, int_butt_abs_z2_position))
  bell_assembly_conf1.append(('bell_internal_buttress', c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], ib_z_size, 'y', 'xy', c['ib_abs_x1_position'], -c['f_w2'], int_butt_abs_z1_position))
  bell_assembly_conf1.append(('bell_internal_buttress', c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], ib_z_size, 'i', 'xy', c['ib_abs_x2_position'], -c['f_w2'], int_butt_abs_z1_position))
  bell_assembly_conf1.append(('bell_internal_buttress', c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], ib_z_size, 'z', 'xy', c['ib_abs_x1_position'], f_w2b, int_butt_abs_z1_position))
  bell_assembly_conf1.append(('bell_internal_buttress', c['ib_x_zero'], 0, c['ib_x_size'], c['ib_y_size'], ib_z_size, 'x', 'xy', c['ib_abs_x2_position'], f_w2b, int_butt_abs_z1_position))
  bell_assembly_conf1.append(('bell_external_side_buttress', c['eb_x_zero'], 0, c['eb_x_size'], c['eb_y_size'], eb_z_size, 'i', 'xz', ext_side_butt_abs_x1_position, ext_side_butt_abs_y1_position, 0))
  bell_assembly_conf1.append(('bell_external_side_buttress', c['eb_x_zero'], 0, c['eb_x_size'], c['eb_y_size'], eb_z_size, 'i', 'xz', ext_side_butt_abs_x1_position, ext_side_butt_abs_y2_position, 0))
  bell_assembly_conf1.append(('bell_external_side_buttress', c['eb_x_zero'], 0, c['eb_x_size'], c['eb_y_size'], eb_z_size, 'y', 'xz', ext_side_butt_abs_x2_position, ext_side_butt_abs_y1_position, 0))
  bell_assembly_conf1.append(('bell_external_side_buttress', c['eb_x_zero'], 0, c['eb_x_size'], c['eb_y_size'], eb_z_size, 'y', 'xz', ext_side_butt_abs_x2_position, ext_side_butt_abs_y2_position, 0))
  bell_assembly_conf1.append(('bell_external_face_buttress', c['eb_x_zero'], 0, c['eb_x_size'], c['eb_y_size'], eb_z_size, 'i', 'yz', ext_face_butt_abs_x1_position, ext_face_butt_abs_y1_position, 0))
  bell_assembly_conf1.append(('bell_external_face_buttress', c['eb_x_zero'], 0, c['eb_x_size'], c['eb_y_size'], eb_z_size, 'i', 'yz', ext_face_butt_abs_x2_position, ext_face_butt_abs_y1_position, 0))
  bell_assembly_conf1.append(('bell_external_face_buttress', c['eb_x_zero'], 0, c['eb_x_size'], c['eb_y_size'], eb_z_size, 'y', 'yz', ext_face_butt_abs_x1_position, ext_face_butt_abs_y2_position, 0))
  bell_assembly_conf1.append(('bell_external_face_buttress', c['eb_x_zero'], 0, c['eb_x_size'], c['eb_y_size'], eb_z_size, 'y', 'yz', ext_face_butt_abs_x2_position, ext_face_butt_abs_y2_position, 0))
  # conf2
  z_hole_abs_position = c['f_w2'] - max(c['face_thickness'], c['side_thickness']) - c['z_hole_position_length']*math.sqrt(2)/2
  x_hole_abs_y_position = c['f_w2'] - c['face_thickness'] - c['x_hole_y_position']
  x_hole_abs_z1_position = int_butt_abs_z1_position + c['x_hole_z_bottom_position']
  x_hole_abs_z2_position = int_butt_abs_z2_position + c['x_hole_z_top_position']
  y_hole_abs_x_position = c['f_w2'] - c['side_thickness'] - c['y_hole_x_position']
  y_hole_abs_z1_position = int_butt_abs_z1_position + c['y_hole_z_bottom_position']
  y_hole_abs_z2_position = int_butt_abs_z2_position + c['y_hole_z_top_position']
  bell_assembly_conf2 = []
  bell_assembly_conf2.extend(bell_assembly_conf1)
  if(c['z_hole_radius']>0):
    bell_assembly_conf2.append(('z_rod', 0, 0, 0, 0, c['base_thickness']+c['bell_face_height'], 'i', 'xy',  1*z_hole_abs_position,  1*z_hole_abs_position, -1*c['z_hole_radius']))
    bell_assembly_conf2.append(('z_rod', 0, 0, 0, 0, c['base_thickness']+c['bell_face_height'], 'i', 'xy', -1*z_hole_abs_position,  1*z_hole_abs_position, -1*c['z_hole_radius']))
    bell_assembly_conf2.append(('z_rod', 0, 0, 0, 0, c['base_thickness']+c['bell_face_height'], 'i', 'xy', -1*z_hole_abs_position, -1*z_hole_abs_position, -1*c['z_hole_radius']))
    bell_assembly_conf2.append(('z_rod', 0, 0, 0, 0, c['base_thickness']+c['bell_face_height'], 'i', 'xy',  1*z_hole_abs_position, -1*z_hole_abs_position, -1*c['z_hole_radius']))
  if(c['x_hole_radius']>0):
    bell_assembly_conf2.append(('x_rod', 0, 0, 0, 0, c['bell_face_height']+2*c['x_hole_radius'], 'i', 'yz', -1*c['f_w2']-c['x_hole_radius'],  1*x_hole_abs_y_position, x_hole_abs_z1_position))
    bell_assembly_conf2.append(('x_rod', 0, 0, 0, 0, c['bell_face_height']+2*c['x_hole_radius'], 'i', 'yz', -1*c['f_w2']-c['x_hole_radius'], -1*x_hole_abs_y_position, x_hole_abs_z1_position))
    bell_assembly_conf2.append(('x_rod', 0, 0, 0, 0, c['bell_face_height']+2*c['x_hole_radius'], 'i', 'yz', -1*c['f_w2']-c['x_hole_radius'],  1*x_hole_abs_y_position, x_hole_abs_z2_position))
    bell_assembly_conf2.append(('x_rod', 0, 0, 0, 0, c['bell_face_height']+2*c['x_hole_radius'], 'i', 'yz', -1*c['f_w2']-c['x_hole_radius'], -1*x_hole_abs_y_position, x_hole_abs_z2_position))
  if(c['y_hole_radius']>0):
    bell_assembly_conf2.append(('y_rod', 0, 0, 0, 0, c['bell_face_height']+2*c['x_hole_radius'], 'i', 'xz',  1*y_hole_abs_x_position, -1*c['f_w2']-c['y_hole_radius'], y_hole_abs_z1_position))
    bell_assembly_conf2.append(('y_rod', 0, 0, 0, 0, c['bell_face_height']+2*c['x_hole_radius'], 'i', 'xz', -1*y_hole_abs_x_position, -1*c['f_w2']-c['y_hole_radius'], y_hole_abs_z1_position))
    bell_assembly_conf2.append(('y_rod', 0, 0, 0, 0, c['bell_face_height']+2*c['x_hole_radius'], 'i', 'xz',  1*y_hole_abs_x_position, -1*c['f_w2']-c['y_hole_radius'], y_hole_abs_z2_position))
    bell_assembly_conf2.append(('y_rod', 0, 0, 0, 0, c['bell_face_height']+2*c['x_hole_radius'], 'i', 'xz', -1*y_hole_abs_x_position, -1*c['f_w2']-c['y_hole_radius'], y_hole_abs_z2_position))
  #
  size_xyz = (2*c['base_radius'], 2*c['base_radius'], c['base_thickness']+c['bell_face_height']+c['leg_length']+c['axle_external_radius'])
  zero_xyz = (-1*c['base_radius'], -1*c['base_radius'], 0)
  slice_x = [ (i+1)/12.0*size_xyz[0] for i in range(10) ]
  slice_y = [ (i+1)/12.0*size_xyz[1] for i in range(10) ]
  slice_z = [ (i+0.1)/12.0*size_xyz[2] for i in range(10) ]
  slice_xyz = (size_xyz[0], size_xyz[1], size_xyz[2], zero_xyz[0], zero_xyz[1], zero_xyz[2], slice_z, slice_y, slice_x)
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['bell_assembly_conf1'] = bell_assembly_conf1
  r_slice['bell_assembly_conf1'] = slice_xyz

  r_assembly['bell_assembly_conf2'] = bell_assembly_conf2
  r_slice['bell_assembly_conf2'] = ()
  #
  return((r_assembly, r_slice))


################################################################
# bell_info
################################################################

def bell_info(c):
  """ create the text info related to the bell design
  """
  # b_parameter_info
  b_parameter_info = """
bell bulk:
axle_internal_radius: {:0.3f}   diameter: {:0.3f}
axle_external_radius: {:0.3f}   diameter: {:0.3f}
leg_length:           {:0.3f}
bell_face_height:     {:0.3f}
bell_face_width:      {:0.3f}
base_diameter:        {:0.3f}
""".format(c['axle_internal_radius'], 2*c['axle_internal_radius'], c['axle_external_radius'], 2*c['axle_external_radius'], c['leg_length'], c['bell_face_height'], c['bell_face_width'], c['base_radius'], 2*c['base_radius'])
  b_parameter_info += """
wall tickness:
face_thickness: {:0.3f}
side_thickness: {:0.3f}
base_thickness: {:0.3f}
""".format(c['face_thickness'], c['side_thickness'], c['base_thickness'])
  b_parameter_info += """
axle_fastening_holes:
axle_hole_nb:               {:d}
axle_hole_radius:           {:0.3f}   diameter: {:0.3f}
axle_hole_position_radius:  {:0.3f}   diameter: {:0.3f}
axle_hole_angle:            {:0.3f} (radian)    {:0.3f} (degree)
""".format(c['axle_hole_nb'], c['axle_hole_radius'], 2*c['axle_hole_radius'], c['axle_hole_position_radius'], 2*c['axle_hole_position_radius'], c['axle_hole_angle'], c['axle_hole_angle']*180/math.pi)
  b_parameter_info += """
leg:
leg_spare_width:      {:0.3f}
leg_smoothing_radius: {:0.3f}
""".format(c['leg_spare_width'], c['leg_smoothing_radius'])
  b_parameter_info += """
motor_fastening_holes:
motor_hole_radius:      {:0.3f}   diameter: {:0.3f}
motor_hole_x_distance:  {:0.3f}
motor_hole_z_distance:  {:0.3f}
motor_hole_z_position:  {:0.3f}
""".format(c['motor_hole_radius'], 2*c['motor_hole_radius'], c['motor_hole_x_distance'], c['motor_hole_z_distance'], c['motor_hole_z_position'])
  b_parameter_info += """
internal_buttress:
int_buttress_x_length:            {:0.3f}
int_buttress_z_width:             {:0.3f}
int_buttress_z_distance:          {:0.3f}
int_buttress_x_position:          {:0.3f}
int_buttress_z_position:          {:0.3f}
int_buttress_int_corner_length:   {:0.3f}
int_buttress_ext_corner_length:   {:0.3f}
int_buttress_bump_length:         {:0.3f}
int_buttress_arc_height:          {:0.3f}
int_buttress_smoothing_radius:    {:0.3f}
""".format(c['int_buttress_x_length'], c['int_buttress_z_width'], c['int_buttress_z_distance'], c['int_buttress_x_position'], c['int_buttress_z_position'], c['int_buttress_int_corner_length'], c['int_buttress_ext_corner_length'], c['int_buttress_bump_length'], c['int_buttress_arc_height'], c['int_buttress_smoothing_radius'])
  b_parameter_info += """
external_buttress:
ext_buttress_z_length:                {:0.3f}
ext_buttress_x_width:                 {:0.3f}
ext_buttress_x_distance:              {:0.3f}
ext_buttress_z_position:              {:0.3f}
ext_buttress_y_length:                {:0.3f}
ext_buttress_y_position:              {:0.3f}
ext_buttress_face_int_corner_length:  {:0.3f}
ext_buttress_face_ext_corner_length:  {:0.3f}
ext_buttress_face_bump_length:        {:0.3f}
ext_buttress_base_int_corner_length:  {:0.3f}
ext_buttress_base_ext_corner_length:  {:0.3f}
ext_buttress_base_bump_length:        {:0.3f}
ext_buttress_arc_height:              {:0.3f}
ext_buttress_smoothing_radius:        {:0.3f}
""".format(c['ext_buttress_z_length'], c['ext_buttress_x_width'], c['ext_buttress_x_distance'], c['ext_buttress_z_position'], c['ext_buttress_y_length'], c['ext_buttress_y_position'], c['ext_buttress_face_int_corner_length'], c['ext_buttress_face_ext_corner_length'], c['ext_buttress_face_bump_length'], c['ext_buttress_base_int_corner_length'], c['ext_buttress_base_ext_corner_length'], c['ext_buttress_base_bump_length'], c['ext_buttress_arc_height'], c['ext_buttress_smoothing_radius'])
  b_parameter_info += """
bell_side_hollow:
hollow_z_height:      {:0.3f}
hollow_y_width:       {:0.3f}
hollow_spare_width:   {:0.3f}
""".format(c['hollow_z_height'], c['hollow_y_width'], c['hollow_spare_width'])
  b_parameter_info += """
base_fastening_holes:
base_hole_nb:               {:d}
base_hole_radius:           {:0.3f}   diameter: {:0.3f}
base_hole_position_radius:  {:0.3f}   diameter: {:0.3f}
base_hole_angle:            {:0.3f} (radian)    {:0.3f} (degree)
""".format(c['base_hole_nb'], c['base_hole_radius'], 2*c['base_hole_radius'], c['base_hole_position_radius'], 2*c['base_hole_position_radius'], c['base_hole_angle'], c['base_hole_angle']*180/math.pi)
  b_parameter_info += """
y_fastening_holes:
y_hole_radius:              {:0.3f}    diameter: {:0.3f}
y_hole_z_top_position:      {:0.3f}
y_hole_z_bottom_position:   {:0.3f}
y_hole_x_position:          {:0.3f}
""".format(c['y_hole_radius'], 2*c['y_hole_radius'], c['y_hole_z_top_position'], c['y_hole_z_bottom_position'], c['y_hole_x_position'])
  b_parameter_info += """
x_fastening_holes:
x_hole_radius:              {:0.3f}   diameter: {:0.3f}
x_hole_z_top_position:      {:0.3f}
x_hole_z_bottom_position:   {:0.3f}
x_hole_y_position:          {:0.3f}
""".format(c['x_hole_radius'], 2*c['x_hole_radius'], c['x_hole_z_top_position'], c['x_hole_z_bottom_position'], c['x_hole_y_position'])
  b_parameter_info += """
z_fastening_holes:
z_hole_radius:          {:0.3f}   diameter: {:0.3f}
z_hole_external_radius: {:0.3f}   diameter: {:0.3f}
z_hole_position_length: {:0.3f}
""".format(c['z_hole_radius'], 2*c['z_hole_radius'], c['z_hole_external_radius'], 2*c['z_hole_external_radius'], c['z_hole_position_length'])
  b_parameter_info += """
manufacturing:
bell_cnc_router_bit_radius:  {:0.3f}
bell_extra_cut_thickness:    {:0.3f}
""".format(c['bell_cnc_router_bit_radius'], c['bell_extra_cut_thickness'])
  #print(b_parameter_info)
  return(b_parameter_info)

################################################################
# bell allinone_return_type
################################################################

def bell_allinone_return_type(return_type, c):
  """ generate the allinone return value of the bell design
  """
  (figures, height) = bell_2d_construction(c)
  (assembly_conf, slice_xyz) = bell_3d_construction(c)
  b_info = bell_info(c)
  #
  if(return_type=='int_status'):
    r_b = 1
  elif(return_type=='cnc25d_figure'):
    r_b = figures['part_list']
  elif(return_type=='freecad_object'):
    partial_conf = assembly_conf['bell_assembly_conf2']
    complete_assembly_conf = []
    for i in range(len(partial_conf)):
      one_figure_conf = list(partial_conf[i])
      fig_name = one_figure_conf[0]
      fig_B = cnc25d_api.cnc_cut_figure(figures[fig_name], "complete_assembly_conf_{:s}".format(fig_name))
      one_figure_conf[0] = fig_B
      complete_assembly_conf.append(one_figure_conf)
    r_b = cnc25d_api.figures_to_freecad_assembly(complete_assembly_conf)
  elif(return_type=='figures_3dconf_info'):
    r_b = (figures['part_list'], assembly_conf['bell_assembly_conf1'], b_info)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(return_type))
    sys.exit(2)
  return(r_b)

################################################################
# self test
################################################################

def bell_self_test():
  """
  This is the non-regression test of bell.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , ""],
    ["no internal buttress" , "--int_buttress_x_length 0.0 --int_buttress_ext_corner_length 25.0 --int_buttress_bump_length 0.0"],
    ["no external buttress" , "--ext_buttress_z_length 0.0 --ext_buttress_y_length 0.0 --ext_buttress_base_ext_corner_length 25.0 --ext_buttress_face_ext_corner_length 25.0 --ext_buttress_face_bump_length 0.0 --ext_buttress_base_bump_length 0.0"],
    ["straight leg"         , "--leg_spare_width 0.0"],
    ["smallest leg smoothing radius" , "--leg_spare_width 10.0 --leg_smoothing_radius 10.0"],
    ["leg square"         , "--leg_spare_width 20.0 --axle_external_diameter 40.0"],
    ["no side hollow"       , "--hollow_z_height 0.0"],
    ["external_buttress without int_corner" , "--ext_buttress_base_int_corner_length 0.0 --ext_buttress_smoothing_radius 0.0"],
    ["external_buttress without bump" , "--ext_buttress_base_bump_length 0.0"],
    ["external_buttress without arc" , "--ext_buttress_arc_height 0.0"],
    ["no xyz holes"         , "--x_hole_diameter 0.0 --y_hole_diameter 0.0 --z_hole_diameter 0.0"],
    ["compute 3d assembly"  , "--bell_extra_cut_thickness 1.0 --return_type freecad_object"],
    ["output files"         , "--output_file_basename test_output/bell_self_test.dxf"],
    ["last test"            , "--motor_hole_diameter 0.0"]]
  return(r_tests)


################################################################
# bell design declaration
################################################################

class bell(cnc25d_api.bare_design):
  """ bell design
  """
  def __init__(self, constraint={}):
    """ configure the bell design
    """
    self.set_design_name("bell_design")
    self.set_constraint_constructor(bell_constraint_constructor)
    self.set_constraint_check(bell_constraint_check)
    self.set_2d_constructor(bell_2d_construction)
    self.set_2d_simulation()
    self.set_3d_constructor(bell_3d_construction)
    self.set_info(bell_info)
    self.set_display_figure_list(['bell_part_overview', 'external_buttress_assembly', 'internal_buttress_assembly'])
    figs = ['bell_face', 'bell_side', 'bell_base', 'bell_internal_buttress', 'bell_external_face_buttress', 'bell_external_side_buttress', 'part_list', 'internal_buttress_assembly', 'external_buttress_assembly', 'bell_part_overview']
    #self.set_2d_figure_file_list()
    self.set_2d_figure_file_list(figs)
    self.set_3d_figure_file_list(figs)
    self.set_3d_conf_file_list(['bell_assembly_conf1'])
    self.set_allinone_return_type(bell_allinone_return_type)
    self.set_self_test(bell_self_test())
    self.apply_constraint(constraint)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("bell.py says hello!\n")
  my_b = bell()
  my_b.allinone()
  #b_value = my_b.allinone("--bell_extra_cut_thickness 1.0 --return_type freecad_object")
  try: # depending on c['return_type'] it might be or not a freecad_object
    Part.show(b_value)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


