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
import re # to detect .dxf or .svg
#import Tkinter # to display the outline in a small GUI
#
import Part
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d

################################################################
# bell dictionary-arguments default values
################################################################

def bell_dictionary_init():
  """ create and initiate a bell_dictionary with the default value
  """
  r_bd = {}
  ### bell_face
  ## bulk
  r_bd['axle_internal_diameter']          = 20.0
  r_bd['axle_external_diameter']          = 0.0
  r_bd['leg_length']                      = 50.0
  r_bd['bell_face_height']                = 50.0
  r_bd['bell_face_width']                 = 50.0
  ## wall_thickness
  r_bd['face_thickness']                  = 5.0
  r_bd['side_thickness']                  = 5.0
  r_bd['base_thickness']                  = 5.0
  ## axle_hole
  r_bd['axle_hole_nb']                    = 6
  r_bd['axle_hole_diameter']              = 4.0
  r_bd['axle_hole_position_diameter']     = 0.0
  r_bd['axle_hole_angle']                 = 0.0
  ## leg
  r_bd['leg_spare_width']                 = 10.0
  r_bd['leg_smoothing_radius']            = 30.0
  ## motor_hole
  r_bd['motor_hole_diameter']             = 4.0
  r_bd['motor_hole_x_distance']           = 30.0
  r_bd['motor_hole_z_distance']           = 30.0
  r_bd['motor_hole_z_position']           = 60.0
  ## internal_buttress
  r_bd['int_buttress_x_length']           = 10.0
  r_bd['int_buttress_z_width']            = 5.0
  r_bd['int_buttress_z_distance']         = 20.0
  r_bd['int_buttress_x_position']         = 10.0
  r_bd['int_buttress_z_position']         = 10.0
  r_bd['int_buttress_int_corner_length']  = 5.0
  r_bd['int_buttress_ext_corner_length']  = 5.0
  r_bd['int_buttress_bump_length']        = 10.0
  r_bd['int_buttress_arc_height']         = 5.0
  r_bd['int_buttress_smoothing_radius']   = 10.0
  ## external_buttress
  r_bd['ext_buttress_z_length']           = 10.0
  r_bd['ext_buttress_x_width']            = 5.0
  r_bd['ext_buttress_x_distance']         = 20.0
  r_bd['ext_buttress_z_position']         = 20.0
  r_bd['ext_buttress_y_length']           = 10.0
  r_bd['ext_buttress_y_position']         = 5.0
  r_bd['ext_buttress_face_int_corner_length']   = 5.0
  r_bd['ext_buttress_face_ext_corner_length']   = 5.0
  r_bd['ext_buttress_face_bump_length']         = 10.0
  r_bd['ext_buttress_base_int_corner_length']   = 5.0
  r_bd['ext_buttress_base_ext_corner_length']   = 5.0
  r_bd['ext_buttress_base_bump_length']         = 10.0
  r_bd['ext_buttress_arc_height']               = 5.0
  r_bd['ext_buttress_smoothing_radius']         = 10.0
  ### bell_side
  ## hollow
  r_bd['hollow_z_height']                 = 10.0
  r_bd['hollow_y_width']                  = 20.0
  r_bd['hollow_spare_width']              = 10.0
  ### bell_base
  ## base_disc
  r_bd['base_diameter']                   = 120.0
  ## base_hole
  r_bd['base_hole_nb']                    = 8
  r_bd['base_hole_diameter']              = 4.0
  r_bd['base_hole_position_diameter']     = 0.0
  r_bd['base_hole_angle']                 = 0.0
  ### xyz-axles
  ## y_hole
  r_bd['y_hole_diameter']                 = 4.0
  r_bd['y_hole_z_position']               = 10.0
  r_bd['y_hole_x_position']               = 10.0
  ## x_hole
  r_bd['x_hole_diameter']                 = 4.0
  r_bd['x_hole_z_position']               = -6.0
  r_bd['x_hole_y_position']               = 10.0
  ## z_hole
  r_bd['z_hole_diameter']                 = 4.0
  r_bd['z_hole_external_diameter']        = 0.0
  r_bd['z_hole_position_length']          = 10.0
  ### manufacturing
  r_bd['cnc_router_bit_radius']           = 2.0
  r_bd['extra_cut_thickness']             = 2.0
  ### output
  r_bd['tkinter_view']           = False
  r_bd['output_file_basename']   = ''
  r_bd['args_in_txt'] = ""
  r_bd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_bd)

################################################################
# bell argparse
################################################################

def bell_add_argument(ai_parser):
  """
  Add arguments relative to the bell
  This function intends to be used by the bell_cli and bell_self_test
  """
  r_parser = ai_parser
  ### bell_face
  ## bulk
  r_parser.add_argument('--axle_internal_diameter','--aid', action='store', type=float, default=20.0, dest='sw_axle_internal_diameter',
    help="Set the internal diameter of the bell-axle. Default: 20.0")
  r_parser.add_argument('--axle_external_diameter','--aed', action='store', type=float, default=0.0, dest='sw_axle_external_diameter',
    help="Set the external diameter of the bell-axle. If equal to 0.0, set to 2*axle_internal_diameter. Default: 0.0")
  r_parser.add_argument('--leg_length','--ll', action='store', type=float, default=50.0, dest='sw_leg_length',
    help="Set the length of the bell_leg. Default: 50.0")
  r_parser.add_argument('--bell_face_height','--bfh', action='store', type=float, default=50.0, dest='sw_bell_face_height',
    help="Set the height of the bell-face and bell-side. Default: 50.0")
  r_parser.add_argument('--bell_face_width','--bfw', action='store', type=float, default=50.0, dest='sw_bell_face_width',
    help="Set the width of the bell-face and bell-side. Default: 50.0")
  ## wall_thickness
  r_parser.add_argument('--face_thickness','--ft', action='store', type=float, default=5.0, dest='sw_face_thickness',
    help="Set the thickness of the bell-face. Default: 5.0")
  r_parser.add_argument('--side_thickness','--st', action='store', type=float, default=5.0, dest='sw_side_thickness',
    help="Set the thickness of the bell-side. Default: 5.0")
  r_parser.add_argument('--base_thickness','--bt', action='store', type=float, default=5.0, dest='sw_base_thickness',
    help="Set the thickness of the bell-base. Default: 5.0")
  ## axle_hole
  r_parser.add_argument('--axle_hole_nb','--ahn', action='store', type=int, default=6.0, dest='sw_axle_hole_nb',
    help="Set the number of the axle-holes. If equal to 0, no axle-hole is created. Default: 6.0")
  r_parser.add_argument('--axle_hole_diameter','--ahd', action='store', type=float, default=4.0, dest='sw_axle_hole_diameter',
    help="Set the diameter of the axle-holes. Default: 4.0")
  r_parser.add_argument('--axle_hole_position_diameter','--ahpd', action='store', type=float, default=0.0, dest='sw_axle_hole_position_diameter',
    help="Set the diameter of the axle-hole position circle. If equal to 0.0, set to (axle_internal_diameter+axle_external_diameter)/2.Default: 4.0")
  r_parser.add_argument('--axle_hole_angle','--aha', action='store', type=float, default=0.0, dest='sw_axle_hole_angle',
    help="Set the position angle of the first axle-hole. Default: 0.0")
  ## leg
  r_parser.add_argument('--leg_spare_width','--lsw', action='store', type=float, default=10.0, dest='sw_leg_spare_width',
    help="Set the left and right spare_width of the bell-leg. Default: 10.0")
  r_parser.add_argument('--leg_smoothing_radius','--lsr', action='store', type=float, default=30.0, dest='sw_leg_smoothing_radius',
    help="Set the smoothing radius of the bell-leg. Default: 30.0")
  ## motor_hole
  r_parser.add_argument('--motor_hole_diameter','--mhd', action='store', type=float, default=4.0, dest='sw_motor_hole_diameter',
    help="Set the diameter of the motor-holes. If equal to 0.0, no motor-hole is created. Default: 4.0")
  r_parser.add_argument('--motor_hole_x_distance','--mhxd', action='store', type=float, default=30.0, dest='sw_motor_hole_x_distance',
    help="Set the x-distance of the motor-hole. Make it fit the motor_lid parameters. Default: 30.0")
  r_parser.add_argument('--motor_hole_z_distance','--mhzd', action='store', type=float, default=30.0, dest='sw_motor_hole_z_distance',
    help="Set the z-distance of the motor-hole. Make it fit the motor_lid parameters. Default: 30.0")
  r_parser.add_argument('--motor_hole_z_position','--mhzp', action='store', type=float, default=60.0, dest='sw_motor_hole_z_position',
    help="Set the z-position of the motor-hole. Make it fit the gearwheel diameters. Default: 60.0")
  ## internal_buttress
  r_parser.add_argument('--int_buttress_x_length','--ibxl', action='store', type=float, default=10.0, dest='sw_int_buttress_x_length',
    help="Set the x-length of the internal-buttress-hole. If equal to 0.0, no internal-buttress hole is created. Default: 10.0")
  r_parser.add_argument('--int_buttress_z_width','--ibzw', action='store', type=float, default=5.0, dest='sw_int_buttress_z_width',
    help="Set the z-width of the internal-buttress-hole. Default: 5.0")
  r_parser.add_argument('--int_buttress_z_distance','--ibzd', action='store', type=float, default=20.0, dest='sw_int_buttress_z_distance',
    help="Set the z-distance between a pair of internal-buttress. Default: 20.0")
  r_parser.add_argument('--int_buttress_x_position','--ibxp', action='store', type=float, default=10.0, dest='sw_int_buttress_x_position',
    help="Set the x-position of the internal-buttress-hole. Default: 10.0")
  r_parser.add_argument('--int_buttress_z_position','--ibzp', action='store', type=float, default=10.0, dest='sw_int_buttress_z_position',
    help="Set the z-position of the first internal-buttress. Default: 10.0")
  r_parser.add_argument('--int_buttress_int_corner_length','--ibicl', action='store', type=float, default=5.0, dest='sw_int_buttress_int_corner_length',
    help="Set the internal-corner-length of the internal-buttress. Default: 5.0")
  r_parser.add_argument('--int_buttress_ext_corner_length','--ibecl', action='store', type=float, default=5.0, dest='sw_int_buttress_ext_corner_length',
    help="Set the external-corner-length of the internal-buttress. Default: 5.0")
  r_parser.add_argument('--int_buttress_bump_length','--ibbl', action='store', type=float, default=10.0, dest='sw_int_buttress_bump_length',
    help="Set the bump-length of the internal-buttress. Default: 10.0")
  r_parser.add_argument('--int_buttress_arc_height','--ibah', action='store', type=float, default=5.0, dest='sw_int_buttress_arc_height',
    help="Set the arc-height of the internal-buttress. If equal to 0.0, a line is created instead of an arc. Default: 5.0")
  r_parser.add_argument('--int_buttress_smoothing_radius','--ibsr', action='store', type=float, default=10.0, dest='sw_int_buttress_smoothing_radius',
    help="Set the smoothing-radius of the internal-buttress. Default: 10.0")
  ## external_buttress
  r_parser.add_argument('--ext_buttress_z_length','--ebzl', action='store', type=float, default=10.0, dest='sw_ext_buttress_z_length',
    help="Set the z-length of the external-buttress-hole. If equal to 0.0, no hole is generated on the face and side wall. Default: 10.0")
  r_parser.add_argument('--ext_buttress_x_width','--ebxw', action='store', type=float, default=5.0, dest='sw_ext_buttress_x_width',
    help="Set the x-width of the external-buttress-hole. Default: 5.0")
  r_parser.add_argument('--ext_buttress_x_distance','--ebxd', action='store', type=float, default=20.0, dest='sw_ext_buttress_x_distance',
    help="Set the x-distance between a pair of the external-buttress. Default: 20.0")
  r_parser.add_argument('--ext_buttress_z_position','--ebzp', action='store', type=float, default=20.0, dest='sw_ext_buttress_z_position',
    help="Set the z-position of the external-buttress-hole on the face and side wall. Default: 20.0")
  r_parser.add_argument('--ext_buttress_y_length','--ebyl', action='store', type=float, default=10.0, dest='sw_ext_buttress_y_length',
    help="Set the y-length of the external-buttress-hole. If equal to 0.0, no hole is generated on the base wall. Default: 10.0")
  r_parser.add_argument('--ext_buttress_y_position','--ebyp', action='store', type=float, default=5.0, dest='sw_ext_buttress_y_position',
    help="Set the y-position of the external-buttress-hole on the base wall. Default: 5.0")
  r_parser.add_argument('--ext_buttress_face_int_corner_length','--ebficl', action='store', type=float, default=5.0, dest='sw_ext_buttress_face_int_corner_length',
    help="Set the internal-corner-length of the external-buttress for the face and side crenel. Default: 5.0")
  r_parser.add_argument('--ext_buttress_face_ext_corner_length','--ebfecl', action='store', type=float, default=5.0, dest='sw_ext_buttress_face_ext_corner_length',
    help="Set the external-corner-length of the external-buttress for the face and side crenel. Default: 5.0")
  r_parser.add_argument('--ext_buttress_face_bump_length','--ebfbl', action='store', type=float, default=10.0, dest='sw_ext_buttress_face_bump_length',
    help="Set the bump-length of the external-buttress for the face and side crenel. Default: 10.0")
  r_parser.add_argument('--ext_buttress_base_int_corner_length','--ebbicl', action='store', type=float, default=5.0, dest='sw_ext_buttress_base_int_corner_length',
    help="Set the internal-corner-length of the external-buttress for the base crenel. Default: 5.0")
  r_parser.add_argument('--ext_buttress_base_ext_corner_length','--ebbecl', action='store', type=float, default=5.0, dest='sw_ext_buttress_base_ext_corner_length',
    help="Set the external-corner-length of the external-buttress for the base crenel. Default: 5.0")
  r_parser.add_argument('--ext_buttress_base_bump_length','--ebbbl', action='store', type=float, default=10.0, dest='sw_ext_buttress_base_bump_length',
    help="Set the bump-length of the external-buttress for the base crenel. Default: 10.0")
  r_parser.add_argument('--ext_buttress_arc_height','--ebah', action='store', type=float, default=5.0, dest='sw_ext_buttress_arc_height',
    help="Set the arc-height of the external-buttress. If equal to 0.0, a line is created instead of an arc. Default: 5.0")
  r_parser.add_argument('--ext_buttress_smoothing_radius','--ebsr', action='store', type=float, default=10.0, dest='sw_ext_buttress_smoothing_radius',
    help="Set the smoothing radius of the external-buttress. Default: 10.0")
  ### bell_side
  ## hollow
  r_parser.add_argument('--hollow_z_height','--hzh', action='store', type=float, default=10.0, dest='sw_hollow_z_height',
    help="Set the z-height of the bell-side-hollow. Default: 10.0")
  r_parser.add_argument('--hollow_y_width','--hyw', action='store', type=float, default=20.0, dest='sw_hollow_y_width',
    help="Set the y-width of the bell-side-hollow. Default: 20.0")
  r_parser.add_argument('--hollow_spare_width','--hsw', action='store', type=float, default=10.0, dest='sw_hollow_spare_width',
    help="Set the spare_width of the bell-side-hollow. Default: 10.0")
  ### bell_base
  ## base_disc
  r_parser.add_argument('--base_diameter','--bd', action='store', type=float, default=120.0, dest='sw_base_diameter',
    help="Set the diameter of the base-disc. Default: 120.0")
  ## base_hole
  r_parser.add_argument('--base_hole_nb','--bhn', action='store', type=int, default=8.0, dest='sw_base_hole_nb',
    help="Set the number of base-holes. If equal to 0, no base-hole is created. Default: 8.0")
  r_parser.add_argument('--base_hole_diameter','--bhd', action='store', type=float, default=4.0, dest='sw_base_hole_diameter',
    help="Set the diameter of the base-holes. Default: 4.0")
  r_parser.add_argument('--base_hole_position_diameter','--bhpd', action='store', type=float, default=0.0, dest='sw_base_hole_position_diameter',
    help="Set the diameter of the base-hole position circle. If equal to 0.0, set to base_diameter-2*base_hole_diameter. Default: 0.0")
  r_parser.add_argument('--base_hole_angle','--bha', action='store', type=float, default=0.0, dest='sw_base_hole_angle',
    help="Set the position-angle of the first base-hole. Default: 0.0")
  ### xyz-axles
  ## y_hole
  r_parser.add_argument('--y_hole_diameter','--yhd', action='store', type=float, default=4.0, dest='sw_y_hole_diameter',
    help="Set the diameter of the y-holes. If equal to 0.0, no y-hole is created. Default: 4.0")
  r_parser.add_argument('--y_hole_z_position','--yhzp', action='store', type=float, default=10.0, dest='sw_y_hole_z_position',
    help="Set the z-position of the y-holes. Default: 10.0")
  r_parser.add_argument('--y_hole_x_position','--yhxp', action='store', type=float, default=10.0, dest='sw_y_hole_x_position',
    help="Set the x-position of the y-holes. Default: 10.0")
  ## x_hole
  r_parser.add_argument('--x_hole_diameter','--xhd', action='store', type=float, default=4.0, dest='sw_x_hole_diameter',
    help="Set the diameter of the x-holes. If equal to 0.0, no x-hole is created. Default: 4.0")
  r_parser.add_argument('--x_hole_z_position','--xhzp', action='store', type=float, default=10.0, dest='sw_x_hole_z_position',
    help="Set the z-position of the y-holes. Default: 10.0")
  r_parser.add_argument('--x_hole_y_position','--xhyp', action='store', type=float, default=10.0, dest='sw_x_hole_y_position',
    help="Set the y-position of the x-holes. Default: 10.0")
  ## z_hole
  r_parser.add_argument('--z_hole_diameter','--zhd', action='store', type=float, default=4.0, dest='sw_z_hole_diameter',
    help="Set the diameter of the z-holes. If equal to 0.0, no z-hole is created. Default: 4.0")
  r_parser.add_argument('--z_hole_external_diameter','--zhed', action='store', type=float, default=0.0, dest='sw_z_hole_external_diameter',
    help="Set the external-diameter of the z-holes. If equal to 0.0, set to 2*z_hole_diameter. Default: 4.0")
  r_parser.add_argument('--z_hole_position_length','--zhpl', action='store', type=float, default=10.0, dest='sw_z_hole_position_length',
    help="Set the position-length of the z-holes. Default: 10.0")
  ### manufacturing
  r_parser.add_argument('--cnc_router_bit_radius','--crbr', action='store', type=float, default=2.0, dest='sw_cnc_router_bit_radius',
    help="Set the minimal router_bit_radius for the whole design. Default: 2.0")
  r_parser.add_argument('--extra_cut_thickness','--ect', action='store', type=float, default=2.0, dest='sw_extra_cut_thickness',
    help="Set the extra-cut-thickness for the holes and crenels. Default: 2.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def bell(ai_constraints):
  """
  The main function of the script.
  It generates a bell assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  bdi = bell_dictionary_init()
  b_c = bdi.copy()
  b_c.update(ai_constraints)
  #print("dbg155: b_c:", b_c)
  if(len(b_c.viewkeys() & bdi.viewkeys()) != len(b_c.viewkeys() | bdi.viewkeys())): # check if the dictionary b_c has exactly all the keys compare to bell_dictionary_init()
    print("ERR157: Error, b_c has too much entries as {:s} or missing entries as {:s}".format(b_c.viewkeys() - bdi.viewkeys(), bdi.viewkeys() - b_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: bell constraints:")
  #for k in b_c.viewkeys():
  #  if(b_c[k] != bdi[k]):
  #    print("dbg166: for k {:s}, b_c[k] {:s} != bdi[k] {:s}".format(k, str(b_c[k]), str(bdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################


  #### return
  if(b_c['return_type']=='int_status'):
    r_b = 1
  elif(b_c['return_type']=='cnc25d_figure'):
    r_b = 1
  elif(b_c['return_type']=='freecad_object'):
    r_b = 1
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(b_c['return_type']))
    sys.exit(2)
  return(r_b)

################################################################
# bell wrapper dance
################################################################

def bell_argparse_to_dictionary(ai_b_args):
  """ convert a bell_argparse into a bell_dictionary
  """
  r_bd = {}
  ### bell_face
  ## bulk
  r_bd['axle_internal_diameter']          = ai_b_args.sw_axle_internal_diameter 
  r_bd['axle_external_diameter']          = ai_b_args.sw_axle_external_diameter
  r_bd['leg_length']                      = ai_b_args.sw_leg_length
  r_bd['bell_face_height']                = ai_b_args.sw_bell_face_height
  r_bd['bell_face_width']                 = ai_b_args.sw_bell_face_width
  ## wall_thickness
  r_bd['face_thickness']                  = ai_b_args.sw_face_thickness
  r_bd['side_thickness']                  = ai_b_args.sw_side_thickness
  r_bd['base_thickness']                  = ai_b_args.sw_base_thickness
  ## axle_hole
  r_bd['axle_hole_nb']                    = ai_b_args.sw_axle_hole_nb
  r_bd['axle_hole_diameter']              = ai_b_args.sw_axle_hole_diameter
  r_bd['axle_hole_position_diameter']     = ai_b_args.sw_axle_hole_position_diameter
  r_bd['axle_hole_angle']                 = ai_b_args.sw_axle_hole_angle
  ## leg
  r_bd['leg_spare_width']                 = ai_b_args.sw_leg_spare_width
  r_bd['leg_smoothing_radius']            = ai_b_args.sw_leg_smoothing_radius
  ## motor_hole
  r_bd['motor_hole_diameter']             = ai_b_args.sw_motor_hole_diameter
  r_bd['motor_hole_x_distance']           = ai_b_args.sw_motor_hole_x_distance
  r_bd['motor_hole_z_distance']           = ai_b_args.sw_motor_hole_z_distance
  r_bd['motor_hole_z_position']           = ai_b_args.sw_motor_hole_z_position
  ## internal_buttress
  r_bd['int_buttress_x_length']           = ai_b_args.sw_int_buttress_x_length
  r_bd['int_buttress_z_width']            = ai_b_args.sw_int_buttress_z_width
  r_bd['int_buttress_z_distance']         = ai_b_args.sw_int_buttress_z_distance
  r_bd['int_buttress_x_position']         = ai_b_args.sw_int_buttress_x_position
  r_bd['int_buttress_z_position']         = ai_b_args.sw_int_buttress_z_position
  r_bd['int_buttress_int_corner_length']  = ai_b_args.sw_int_buttress_int_corner_length
  r_bd['int_buttress_ext_corner_length']  = ai_b_args.sw_int_buttress_ext_corner_length
  r_bd['int_buttress_bump_length']        = ai_b_args.sw_int_buttress_bump_length
  r_bd['int_buttress_arc_height']         = ai_b_args.sw_int_buttress_arc_height
  r_bd['int_buttress_smoothing_radius']   = ai_b_args.sw_int_buttress_smoothing_radius
  ## external_buttress
  r_bd['ext_buttress_z_length']                 = ai_b_args.sw_ext_buttress_z_length
  r_bd['ext_buttress_x_width']                  = ai_b_args.sw_ext_buttress_x_width
  r_bd['ext_buttress_x_distance']               = ai_b_args.sw_ext_buttress_x_distance
  r_bd['ext_buttress_z_position']               = ai_b_args.sw_ext_buttress_z_position
  r_bd['ext_buttress_y_length']                 = ai_b_args.sw_ext_buttress_y_length
  r_bd['ext_buttress_y_position']               = ai_b_args.sw_ext_buttress_y_position
  r_bd['ext_buttress_face_int_corner_length']   = ai_b_args.sw_ext_buttress_face_int_corner_length
  r_bd['ext_buttress_face_ext_corner_length']   = ai_b_args.sw_ext_buttress_face_ext_corner_length
  r_bd['ext_buttress_face_bump_length']         = ai_b_args.sw_ext_buttress_face_bump_length
  r_bd['ext_buttress_base_int_corner_length']   = ai_b_args.sw_ext_buttress_base_int_corner_length
  r_bd['ext_buttress_base_ext_corner_length']   = ai_b_args.sw_ext_buttress_base_ext_corner_length
  r_bd['ext_buttress_base_bump_length']         = ai_b_args.sw_ext_buttress_base_bump_length
  r_bd['ext_buttress_arc_height']               = ai_b_args.sw_ext_buttress_arc_height
  r_bd['ext_buttress_smoothing_radius']         = ai_b_args.sw_ext_buttress_smoothing_radius
  ### bell_side
  ## hollow
  r_bd['hollow_z_height']                 = ai_b_args.sw_hollow_z_height
  r_bd['hollow_y_width']                  = ai_b_args.sw_hollow_y_width
  r_bd['hollow_spare_width']              = ai_b_args.sw_hollow_spare_width
  ### bell_base
  ## base_disc
  r_bd['base_diameter']                   = ai_b_args.sw_base_diameter
  ## base_hole
  r_bd['base_hole_nb']                    = ai_b_args.sw_base_hole_nb
  r_bd['base_hole_diameter']              = ai_b_args.sw_base_hole_diameter
  r_bd['base_hole_position_diameter']     = ai_b_args.sw_base_hole_position_diameter
  r_bd['base_hole_angle']                 = ai_b_args.sw_base_hole_angle
  ### xyz-axles
  ## y_hole
  r_bd['y_hole_diameter']                 = ai_b_args.sw_y_hole_diameter
  r_bd['y_hole_z_position']               = ai_b_args.sw_y_hole_z_position
  r_bd['y_hole_x_position']               = ai_b_args.sw_y_hole_x_position
  ## x_hole
  r_bd['x_hole_diameter']                 = ai_b_args.sw_x_hole_diameter
  r_bd['x_hole_z_position']               = ai_b_args.sw_x_hole_z_position
  r_bd['x_hole_y_position']               = ai_b_args.sw_x_hole_y_position
  ## z_hole
  r_bd['z_hole_diameter']                 = ai_b_args.sw_z_hole_diameter
  r_bd['z_hole_external_diameter']        = ai_b_args.sw_z_hole_external_diameter
  r_bd['z_hole_position_length']          = ai_b_args.sw_z_hole_position_length
  ### manufacturing
  r_bd['cnc_router_bit_radius']           = ai_b_args.sw_cnc_router_bit_radius
  r_bd['extra_cut_thickness']             = ai_b_args.sw_extra_cut_thickness
  ### output
  #r_bd['tkinter_view']           = False
  r_bd['output_file_basename']   = ai_b_args.sw_output_file_basename
  #r_bd['args_in_txt'] = ""
  r_bd['return_type'] = ai_b_args.sw_return_type
  #### return
  return(r_bd)
  
def bell_argparse_wrapper(ai_b_args, ai_args_in_txt=""):
  """
  wrapper function of bell() to call it using the bell_parser.
  bell_parser is mostly used for debug and non-regression tests.
  """
  # view the bell with Tkinter as default action
  tkinter_view = True
  if(ai_b_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  bd = bell_argparse_to_dictionary(ai_b_args)
  bd['args_in_txt'] = ai_args_in_txt
  bd['tkinter_view'] = tkinter_view
  #bd['return_type'] = 'int_status'
  r_b = bell(bd)
  return(r_b)

################################################################
# self test
################################################################

def bell_self_test():
  """
  This is the non-regression test of bell.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , ""],
    ["last test"            , ""]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  bell_parser = argparse.ArgumentParser(description='Command line interface for the function bell().')
  bell_parser = bell_add_argument(bell_parser)
  bell_parser = cnc25d_api.generate_output_file_add_argument(bell_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = bell_parser.parse_args(l_args)
    r_bst = bell_argparse_wrapper(st_args)
  return(r_bst)

################################################################
# bell command line interface
################################################################

def bell_cli(ai_args=""):
  """ command line interface of bell.py when it is used in standalone
  """
  # bell parser
  bell_parser = argparse.ArgumentParser(description='Command line interface for the function bell().')
  bell_parser = bell_add_argument(bell_parser)
  bell_parser = cnc25d_api.generate_output_file_add_argument(bell_parser, 1)
  # switch for self_test
  bell_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "bell arguments: " + ' '.join(effective_args)
  b_args = bell_parser.parse_args(effective_args)
  print("dbg111: start making bell")
  if(b_args.sw_run_self_test):
    r_b = bell_self_test()
  else:
    r_b = bell_argparse_wrapper(b_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_b)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("bell.py says hello!\n")
  my_b = bell_cli()
  try: # depending on b_c['return_type'] it might be or not a freecad_object
    Part.show(my_b)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


