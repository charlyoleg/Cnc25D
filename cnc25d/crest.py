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
  r_cd.update(gear_profile.gear_profile_dictionary_init(2))
  ### outline
  r_cd['gear_module']         = 3.0
  r_cd['virtual_tooth_nb']    = 50
  r_cd['portion_tooth_nb']    = 25
  r_cd['free_mounting_width'] = 15.0
  ### gear_hollow
  r_cd['gear_hollow_leg_nb']  = 1 # possible values: 1(filled), 2(end-legs only), 3, 4 ...
  r_cd['end_leg_width']                     = 10.0
  r_cd['middle_leg_width']                  = 10.0
  r_cd['gear_hollow_external_diameter']     = 130.0
  r_cd['gear_hollow_internal_diameter']     = 80.0
  r_cd['floor_width']                       = 10.0
  r_cd['gear_hollow_smoothing_radius']      = 10.0
  ### gear_holes
  r_cd['fastening_hole_diameter']           = 5.0
  r_cd['fastening_hole_position']           = 0.0
  r_cd['centring_hole_diameter']            = 1.0
  r_cd['centring_hole_distance']            = 8.0
  r_cd['centring_hole_position']            = 4.0
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
  r_parser = gear_profile.gear_profile_add_argument(r_parser, 2)
  ### outline
  r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=3.0, dest='sw_gear_module',
    help="Set the gear-module of the crest. Default: 3.0")
  r_parser.add_argument('--virtual_tooth_nb','--vtn', action='store', type=int, default=50, dest='sw_virtual_tooth_nb',
    help="Set the virtual number of gear-teeth of the crest. Default: 50")
  r_parser.add_argument('--portion_tooth_nb','--ptn', action='store', type=int, default=25, dest='sw_portion_tooth_nb',
    help="Set the number of teeth of the gear-portion of the crest. Default: 25")
  r_parser.add_argument('--free_mounting_width','--fmw', action='store', type=float, default=15.0, dest='sw_free_mounting_width',
    help="Set the width that must be kept free to mount the crest in a cross_cube (minimum: face_B1_thickness + cnc_router_bit_radius). Default: 15.0")
  ### gear_hollow
  r_parser.add_argument('--gear_hollow_leg_nb','--ghln', action='store', type=int, default=1, dest='sw_gear_hollow_leg_nb',
    help="Set the number of gear-hollow_legs. Possible values: 1(filled), 2(end-legs only), 3, 4, etc. Default: 1")
  r_parser.add_argument('--end_leg_width','--elw', action='store', type=float, default=10.0, dest='sw_end_leg_width',
    help="Set the width of the two end-legs of the crest. Default: 10.0")
  r_parser.add_argument('--middle_leg_width','--mlw', action='store', type=float, default=10.0, dest='sw_middle_leg_width',
    help="Set the width of the middle-legs of the crest. Default: 10.0")
  r_parser.add_argument('--gear_hollow_external_diameter','--ghed', action='store', type=float, default=130.0, dest='sw_gear_hollow_external_diameter',
    help="Set the diameter of the gear-hollow-external circle. Default: 130.0")
  r_parser.add_argument('--gear_hollow_internal_diameter','--ghid', action='store', type=float, default=80.0, dest='sw_gear_hollow_internal_diameter',
    help="Set the diameter of the gear-hollow-internal circle. Default: 80.0")
  r_parser.add_argument('--floor_width','--fw', action='store', type=float, default=10.0, dest='sw_floor_width',
    help="Set the width between the cross_cube-top-holes and the crest-gear-hollow. Default: 10.0")
  r_parser.add_argument('--gear_hollow_smoothing_radius','--ghsr', action='store', type=float, default=10.0, dest='sw_gear_hollow_smoothing_radius',
    help="Set the smoothing radius for the crest-gear-hollow. Default: 10.0")
  ### gear_holes
  r_parser.add_argument('--fastening_hole_diameter','--fhd', action='store', type=float, default=5.0, dest='sw_fastening_hole_diameter',
    help="Set the diameter of the crest-gear-fastening-holes. Default: 5.0")
  r_parser.add_argument('--fastening_hole_position','--fhp', action='store', type=float, default=0.0, dest='sw_fastening_hole_position',
    help="Set the position relative to the gear-hollow-external circle of the crest-gear-fastening-holes. Default: 0.0")
  r_parser.add_argument('--centring_hole_diameter','--chd', action='store', type=float, default=1.0, dest='sw_centring_hole_diameter',
    help="Set the diameter of the crest-gear-centring-holes. Default: 1.0")
  r_parser.add_argument('--centring_hole_distance','--chdi', action='store', type=float, default=8.0, dest='sw_centring_hole_distance',
    help="Set the distance between a pair of crest-gear-centring-holes. Default: 8.0")
  r_parser.add_argument('--centring_hole_position','--chp', action='store', type=float, default=4.0, dest='sw_centring_hole_position',
    help="Set the position relative to the gear-hollow-external circle of the crest-gear-centring-holes. Default: 4.0")
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

  ################################################################
  # outline construction
  ################################################################
  

  ################################################################
  # output
  ################################################################

  # c_parameter_info
  c_parameter_info = "\ncrest parameter info:\n"
  c_parameter_info += "\n" + c_c['args_in_txt'] + "\n"


  #### return
  if(c_c['return_type']=='int_status'):
    r_c = 1
  elif(c_c['return_type']=='cnc25d_figure'):
    r_c = 1
  elif(c_c['return_type']=='freecad_object'):
    r_c = 1
  elif(c_c['return_type']=='figures_3dconf_info'):
    r_c = 1
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
  r_cd.update(gear_profile.gear_profile_argparse_to_dictionary(ai_c_args, 2))
  ### outline
  r_cd['gear_module']         = ai_c_args.sw_gear_module
  r_cd['virtual_tooth_nb']    = ai_c_args.sw_virtual_tooth_nb
  r_cd['portion_tooth_nb']    = ai_c_args.sw_portion_tooth_nb
  r_cd['free_mounting_width'] = ai_c_args.sw_free_mounting_width
  ### gear_hollow
  r_cd['gear_hollow_leg_nb']  = ai_c_args.sw_gear_hollow_leg_nb
  r_cd['end_leg_width']                     = ai_c_args.sw_end_leg_width
  r_cd['middle_leg_width']                  = ai_c_args.sw_middle_leg_width
  r_cd['gear_hollow_external_diameter']     = ai_c_args.sw_gear_hollow_external_diameter
  r_cd['gear_hollow_internal_diameter']     = ai_c_args.sw_gear_hollow_internal_diameter
  r_cd['floor_width']                       = ai_c_args.sw_floor_width
  r_cd['gear_hollow_smoothing_radius']      = ai_c_args.sw_gear_hollow_smoothing_radius
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
  if(ai_b_args.sw_output_file_basename!=''):
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
    ["extra cut" , "--cross_cube_extra_cut_thickness 1.0"],
    ["extra cut negative" , "--cross_cube_extra_cut_thickness -2.0"],
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


