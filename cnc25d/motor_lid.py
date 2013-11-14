# motor_lid.py
# generates a motor_lid assembly that can complete a epicyclic-gearing.
# created by charlyoleg on 2013/11/13
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
motor_lid.py is a parametric generator of an assembly that completes the epicyclic-gearing system to mount an electric motor.
The main function displays in a Tk-interface the motor-lid assembly, or generates the design as files or returns the design as FreeCAD Part object.
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
import axle_lid

################################################################
# motor_lid dictionary-arguments default values
################################################################

def motor_lid_dictionary_init():
  """ create and initiate a motor_lid_dictionary with the default value
  """
  r_mld = {}
  ### holder-A and holder-B: inherit dictionary entries from axle_lid
  r_mld.update(axle_lid.axle_lid_dictionary_init(1))
  #### motor_lid dictionary entries
  ### input axle-B
  r_mld['axle_B_place']             = 'small' # 'small' or 'large' # useful when the gearring has an odd number of crenels
  r_mld['axle_B_distance']          = 0.0
  r_mld['axle_B_angle']             = 0.0
  r_mld['axle_B_diameter']          = 0.0
  r_mld['axle_B_external_diameter'] = 0.0
  r_mld['axle_B_hole_diameter']     = 0.0
  r_mld['axle_B_central_diameter']  = 0.0
  ### input axle-C
  r_mld['axle_C_distance']          = 0.0
  r_mld['axle_C_angle']             = 0.0
  r_mld['axle_C_hole_diameter']     = 0.0
  r_mld['axle_C_external_diameter'] = 0.0
  ### motor screws
  r_mld['motor_screw1_diameter']    = 0.0
  r_mld['motor_screw1_angle']       = 0.0
  r_mld['motor_screw1_x_length']    = 0.0
  r_mld['motor_screw1_y_length']    = 0.0
  r_mld['motor_screw2_diameter']    = 0.0
  r_mld['motor_screw2_angle']       = 0.0
  r_mld['motor_screw2_x_length']    = 0.0
  r_mld['motor_screw2_y_length']    = 0.0
  r_mld['motor_screw3_diameter']    = 0.0
  r_mld['motor_screw3_angle']       = 0.0
  r_mld['motor_screw3_x_length']    = 0.0
  r_mld['motor_screw3_y_length']    = 0.0
  ### holder-C
  r_mld['fastening_BC_hole_diameter']     = 0.0
  r_mld['fastening_BC_external_diameter'] = 0.0
  r_mld['fastening_BC_bottom_position_diameter']  = 0.0
  r_mld['fastening_BC_bottom_angle']              = 0.0
  r_mld['fastening_BC_top_position_diameter']     = 0.0
  r_mld['fastening_BC_top_angle']                 = 0.0
  ### general
  r_mld['smoothing_radius']       = 0.0
  r_mld['cnc_router_bit_radius']  = 0.1
  r_mld['extrusion_height']       = 10.0
  ### output
  r_mld['tkinter_view']           = False
  r_mld['output_file_basename']   = ''
  ### optional
  r_mld['args_in_txt'] = ""
  r_mld['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_mld)

################################################################
# motor_lid argparse
################################################################

def motor_lid_add_argument(ai_parser):
  """
  Add arguments relative to the motor-lid in addition to the argument of axle_lid(variant=1)
  This function intends to be used by the motor_lid_cli and motor_lid_self_test
  """
  r_parser = ai_parser
  ### holder-A and holder-B : inherit dictionary entries from axle_lid
  r_parser = axle_lid.axle_lid_add_argument(r_parser, 1)
  ### input axle-B
  r_parser.add_argument('--axle_B_place','--abp', action='store', default='small', dest='sw_axle_B_place',
    help="Set the side to generate the input axle_B. Possible values: 'small' or 'large'. Default: 'small'")
  r_parser.add_argument('--axle_B_distance','--abdis', action='store', type=float, default=0.0, dest='sw_axle_B_distance',
    help="Set the distance between the input axle-A and input axle-B. Default: 0.0")
  r_parser.add_argument('--axle_B_angle','--aba', action='store', type=float, default=0.0, dest='sw_axle_B_angle',
    help="Set the angle between the symmetric axis and the intput_axle_B. Default: 0.0")
  r_parser.add_argument('--axle_B_diameter','--abd', action='store', type=float, default=0.0, dest='sw_axle_B_diameter',
    help="Set the diameter of the input_axle_B. If equal to 0.0, no hole for the axle_B is generated. Default: 0.0")
  r_parser.add_argument('--axle_B_external_diameter','--abed', action='store', type=float, default=0.0, dest='sw_axle_B_external_diameter',
    help="Set the external diameter of the input_axle_B. If equal to 0.0, it is set to 2*axle_B_diameter. Default: 0.0")
  r_parser.add_argument('--axle_B_hole_diameter','--abhd', action='store', type=float, default=0.0, dest='sw_axle_B_hole_diameter',
    help="Set the diameter of the hole in the holder-B for the axle_B. If equal to 0.0, no hole in the holder-B for the axle_B is generated. Default: 0.0")
  r_parser.add_argument('--axle_B_central_diameter','--abcd', action='store', type=float, default=0.0, dest='sw_axle_B_central_diameter',
    help="Set the central diameter of the axle_B for the holder-C. If equal to 0.0, it is set to 2*axle_B_diameter. Default: 0.0")
  ### input axle-C
  r_parser.add_argument('--axle_C_distance','--acdis', action='store', type=float, default=0.0, dest='sw_axle_C_distance',
    help="Set the distance between the input axle-B and input axle-C. Default: 0.0")
  r_parser.add_argument('--axle_C_angle','--aca', action='store', type=float, default=0.0, dest='sw_axle_C_angle',
    help="Set the angle between the AB-axis and the BC-axis. Default: 0.0")
  r_parser.add_argument('--axle_C_hole_diameter','--achd', action='store', type=float, default=0.0, dest='sw_axle_C_hole_diameter',
    help="Set the diameter of the hole of the axle_C. If equal to 0.0, no hole for the axle_C is generated. Default: 0.0")
  r_parser.add_argument('--axle_C_external_diameter','--aced', action='store', type=float, default=0.0, dest='sw_axle_C_external_diameter',
    help="Set the external diameter of the input_axle_C. If equal to 0.0, it is set to 2*axle_C_hole_diameter. Default: 0.0")
  ### motor screws
  # screw 1
  r_parser.add_argument('--motor_screw1_diameter','--ms1d', action='store', type=float, default=0.0, dest='sw_motor_screw1_diameter',
    help="Set the diameter of the screw1 holes for an electric motor. If equal to 0.0, no screw1 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw1_angle','--ms1a', action='store', type=float, default=0.0, dest='sw_motor_screw1_angle',
    help="Set the angle between the BC-axis and the screw1-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw1_x_length','--ms1xl', action='store', type=float, default=0.0, dest='sw_motor_screw1_x_length',
    help="Set the length between the screw1-y-axis and the screw1-hole (ie: half of the length between the two screw1-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw1_y_length','--ms1yl', action='store', type=float, default=0.0, dest='sw_motor_screw1_y_length',
    help="Set the length between the axle_C and the screw-x-axis. Default: 0.0")
  # screw 2
  r_parser.add_argument('--motor_screw2_diameter','--ms2d', action='store', type=float, default=0.0, dest='sw_motor_screw2_diameter',
    help="Set the diameter of the screw2 holes for an electric motor. If equal to 0.0, no screw1 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw2_angle','--ms2a', action='store', type=float, default=0.0, dest='sw_motor_screw2_angle',
    help="Set the angle between the BC-axis and the screw2-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw2_x_length','--ms2xl', action='store', type=float, default=0.0, dest='sw_motor_screw2_x_length',
    help="Set the length between the screw2-y-axis and the screw2-hole (ie: half of the length between the two screw1-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw2_y_length','--ms2yl', action='store', type=float, default=0.0, dest='sw_motor_screw2_y_length',
    help="Set the length between the axle_C and the screw2-x-axis. Default: 0.0")
  # screw 3
  r_parser.add_argument('--motor_screw3_diameter','--ms3d', action='store', type=float, default=0.0, dest='sw_motor_screw3_diameter',
    help="Set the diameter of the screw3 holes for an electric motor. If equal to 0.0, no screw3 hole is generated. Default: 0.0")
  r_parser.add_argument('--motor_screw3_angle','--ms3a', action='store', type=float, default=0.0, dest='sw_motor_screw3_angle',
    help="Set the angle between the BC-axis and the screw3-y-axis. Default: 0.0")
  r_parser.add_argument('--motor_screw3_x_length','--ms3xl', action='store', type=float, default=0.0, dest='sw_motor_screw3_x_length',
    help="Set the length between the screw3-y-axis and the screw3-hole (ie: half of the length between the two screw3-holes). Default: 0.0")
  r_parser.add_argument('--motor_screw3_y_length','--ms3yl', action='store', type=float, default=0.0, dest='sw_motor_screw3_y_length',
    help="Set the length between the axle_C and the screw3-x-axis. Default: 0.0")
  ### holder-C
  r_parser.add_argument('--fastening_BC_hole_diameter','--fbchd', action='store', type=float, default=0.0, dest='sw_fastening_BC_hole_diameter',
    help="Set the diameter of the holder B and C fastening holes. If equal to 0.0, no fastening holes are generated. Default: 0.0")
  r_parser.add_argument('--fastening_BC_external_diameter','--fbced', action='store', type=float, default=0.0, dest='sw_fastening_BC_external_diameter',
    help="Set the external diameter of the holder B and C fastening extremities. If equal to 0.0, it is set to 2*fastening_BC_hole_diameter. Default: 0.0")
  r_parser.add_argument('--fastening_BC_bottom_position_diameter','--fbcbpd', action='store', type=float, default=0.0, dest='sw_fastening_BC_bottom_position_diameter',
    help="Set the diameter of the position circle for the bottom fastening holes. Default: 0.0")
  r_parser.add_argument('--fastening_BC_bottom_angle','--fbcba', action='store', type=float, default=0.0, dest='sw_fastening_BC_bottom_angle',
    help="Set the angle between the AB-axis and the bottom fastening hole. Default: 0.0")
  r_parser.add_argument('--fastening_BC_top_position_diameter','--fbctpd', action='store', type=float, default=0.0, dest='sw_fastening_BC_top_position_diameter',
    help="Set the diameter of the position circle for the top fastening holes. Default: 0.0")
  r_parser.add_argument('--fastening_BC_top_angle','--fbcta', action='store', type=float, default=0.0, dest='sw_fastening_BC_top_angle',
    help="Set the angle between the AB-axis and the top fastening hole. Default: 0.0")
  ### general
  r_parser.add_argument('--smoothing_radius','--sr', action='store', type=float, default=0.0, dest='sw_smoothing_radius',
    help="Set the smoothing radius for the motor-lid. If equal to 0.0, it is set to cnc_router_bit_radius. Default: 0.0")
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the motor-lid. Default: 0.1")
  r_parser.add_argument('--extrusion_height','--eh', action='store', type=float, default=10.0, dest='sw_extrusion_height',
    help="Set the height of the linear extrusion of each part of the motor_lid assembly. Default: 10.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def motor_lid(ai_constraints):
  """
  The main function of the script.
  It generates a motor-lid assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  mldi = motor_lid_dictionary_init()
  ml_c = mldi.copy()
  ml_c.update(ai_constraints)
  #print("dbg155: ml_c:", ml_c)
  if(len(ml_c.viewkeys() & mldi.viewkeys()) != len(ml_c.viewkeys() | mldi.viewkeys())): # check if the dictionary ml_c has exactly all the keys compare to motor_lid_dictionary_init()
    print("ERR157: Error, ml_c has too much entries as {:s} or missing entries as {:s}".format(ml_c.viewkeys() - mldi.viewkeys(), mldi.viewkeys() - ml_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new motor_lid constraints:")
  #for k in ml_c.viewkeys():
  #  if(ml_c[k] != mldi[k]):
  #    print("dbg166: for k {:s}, ml_c[k] {:s} != mldi[k] {:s}".format(k, str(ml_c[k]), str(mldi[k])))
  ### precision
  radian_epsilon = math.pi/1000



  #### return
  if(ml_c['return_type']=='int_status'):
    r_ml = 1
  elif(ml_c['return_type']=='cnc25d_figure'):
    r_ml = part_figure_list
  elif(ml_c['return_type']=='freecad_object'):
    r_ml = 1 #freecad_motor_lid(part_figure_list)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(ml_c['return_type']))
    sys.exit(2)
  return(r_ml)

################################################################
# motor-lid wrapper dance
################################################################

def motor_lid_argparse_to_dictionary(ai_ml_args):
  """ convert a motor_lid_argparse into a motor_lid_dictionary
  """
  r_mld = {}
  ### annulus-holder: inherit dictionary entries from axle_lid
  r_mld.update(axle_lid.axle_lid_argparse_to_dictionary(ai_ml_args, 1))
  #### motor_lid dictionary entries
  ### input axle-B
  r_mld['axle_B_place']             = ai_ml_args.sw_axle_B_place
  r_mld['axle_B_distance']          = ai_ml_args.sw_axle_B_distance
  r_mld['axle_B_angle']             = ai_ml_args.sw_axle_B_angle
  r_mld['axle_B_diameter']          = ai_ml_args.sw_axle_B_diameter
  r_mld['axle_B_external_diameter'] = ai_ml_args.sw_axle_B_external_diameter
  r_mld['axle_B_hole_diameter']     = ai_ml_args.sw_axle_B_hole_diameter
  r_mld['axle_B_central_diameter']  = ai_ml_args.sw_axle_B_central_diameter
  ### input axle-C
  r_mld['axle_C_distance']          = ai_ml_args.sw_axle_C_distance
  r_mld['axle_C_angle']             = ai_ml_args.sw_axle_C_angle
  r_mld['axle_C_hole_diameter']     = ai_ml_args.sw_axle_C_hole_diameter
  r_mld['axle_C_external_diameter'] = ai_ml_args.sw_axle_C_external_diameter
  ### motor screws
  r_mld['motor_screw1_diameter']    = ai_ml_args.sw_motor_screw1_diameter
  r_mld['motor_screw1_angle']       = ai_ml_args.sw_motor_screw1_angle
  r_mld['motor_screw1_x_length']    = ai_ml_args.sw_motor_screw1_x_length
  r_mld['motor_screw1_y_length']    = ai_ml_args.sw_motor_screw1_y_length
  r_mld['motor_screw2_diameter']    = ai_ml_args.sw_motor_screw2_diameter
  r_mld['motor_screw2_angle']       = ai_ml_args.sw_motor_screw2_angle
  r_mld['motor_screw2_x_length']    = ai_ml_args.sw_motor_screw2_x_length
  r_mld['motor_screw2_y_length']    = ai_ml_args.sw_motor_screw2_y_length
  r_mld['motor_screw3_diameter']    = ai_ml_args.sw_motor_screw3_diameter
  r_mld['motor_screw3_angle']       = ai_ml_args.sw_motor_screw3_angle
  r_mld['motor_screw3_x_length']    = ai_ml_args.sw_motor_screw3_x_length
  r_mld['motor_screw3_y_length']    = ai_ml_args.sw_motor_screw3_y_length
  ### holder-C
  r_mld['fastening_BC_hole_diameter']             = ai_ml_args.sw_fastening_BC_hole_diameter
  r_mld['fastening_BC_external_diameter']         = ai_ml_args.sw_fastening_BC_external_diameter
  r_mld['fastening_BC_bottom_position_diameter']  = ai_ml_args.sw_fastening_BC_bottom_position_diameter
  r_mld['fastening_BC_bottom_angle']              = ai_ml_args.sw_fastening_BC_bottom_angle
  r_mld['fastening_BC_top_position_diameter']     = ai_ml_args.sw_fastening_BC_top_position_diameter
  r_mld['fastening_BC_top_angle']                 = ai_ml_args.sw_fastening_BC_top_angle
  ### general
  r_mld['smoothing_radius']       = ai_ml_args.sw_smoothing_radius
  r_mld['cnc_router_bit_radius']  = ai_ml_args.sw_cnc_router_bit_radius
  r_mld['extrusion_height']       = ai_ml_args.sw_extrusion_height
  ### output
  #r_mld['tkinter_view']           = False
  r_mld['output_file_basename']   = ai_ml_args.sw_output_file_basename
  ### optional
  #r_mld['args_in_txt'] = ""
  r_mld['return_type'] = ai_ml_args.sw_return_type
  #### return
  return(r_mld)
  
def motor_lid_argparse_wrapper(ai_ml_args, ai_args_in_txt=""):
  """
  wrapper function of motor_lid() to call it using the motor_lid_parser.
  motor_lid_parser is mostly used for debug and non-regression tests.
  """
  # view the motor_lid with Tkinter as default action
  tkinter_view = True
  if(ai_ml_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  mld = motor_lid_argparse_to_dictionary(ai_ml_args)
  mld['args_in_txt'] = ai_args_in_txt
  mld['tkinter_view'] = tkinter_view
  #mld['return_type'] = 'int_status'
  r_ml = motor_lid(mld)
  return(r_ml)

################################################################
# self test
################################################################

def motor_lid_self_test():
  """
  This is the non-regression test of motor_lid.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 79.0 --axle_hole_diameter 22.0 --holder_crenel_number 6"],
    ["last test"            , "--holder_diameter 160.0 --clearance_diameter 140.0 --central_diameter 80.0 --axle_hole_diameter 22.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  motor_lid_parser = argparse.ArgumentParser(description='Command line interface for the function motor_lid().')
  motor_lid_parser = motor_lid_add_argument(motor_lid_parser)
  motor_lid_parser = cnc25d_api.generate_output_file_add_argument(motor_lid_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = motor_lid_parser.parse_args(l_args)
    r_mlst = motor_lid_argparse_wrapper(st_args)
  return(r_mlst)

################################################################
# motor_lid command line interface
################################################################

def motor_lid_cli(ai_args=""):
  """ command line interface of motor_lid.py when it is used in standalone
  """
  # motor_lid parser
  motor_lid_parser = argparse.ArgumentParser(description='Command line interface for the function motor_lid().')
  motor_lid_parser = motor_lid_add_argument(motor_lid_parser)
  motor_lid_parser = cnc25d_api.generate_output_file_add_argument(motor_lid_parser, 1)
  # switch for self_test
  motor_lid_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "motor_lid arguments: " + ' '.join(effective_args)
  ml_args = motor_lid_parser.parse_args(effective_args)
  print("dbg111: start making motor_lid")
  if(ml_args.sw_run_self_test):
    r_ml = motor_lid_self_test()
  else:
    r_ml = motor_lid_argparse_wrapper(ml_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_ml)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("motor_lid.py says hello!\n")
  #my_ml = motor_lid_cli()
  #my_ml = motor_lid_cli("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --return_type freecad_object")
  my_ml = motor_lid_cli("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6")
  #Part.show(my_ml)
  try: # depending on ml_c['return_type'] it might be or not a freecad_object
    Part.show(my_ml)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


