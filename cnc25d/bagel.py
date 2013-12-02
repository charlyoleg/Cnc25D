# bagel.py
# generates the bagel, the axle-guidance of the bell piece
# created by charlyoleg on 2013/12/01
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
bagel.py generates the bagel parts, used as axle-guidance for the bell piece.
The main function displays in a Tk-interface the bagel parts, or generates the design as files or returns the design as FreeCAD Part object.
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
# bagel dictionary-arguments default values
################################################################

def bagel_dictionary_init():
  """ create and initiate a bagel_dictionary with the default value
  """
  r_bd = {}
  ## diameters
  r_bd['axle_diameter']                   = 10.0
  r_bd['axle_internal_diameter']          = 0.0
  r_bd['axle_external_diameter']          = 0.0
  ## axle_holes
  r_bd['axle_hole_nb']                    = 6
  r_bd['axle_hole_diameter']              = 4.0
  r_bd['axle_hole_position_diameter']     = 0.0
  r_bd['axle_hole_angle']                 = 0.0
  ## part thickness
  r_bd['external_bagel_thickness']        = 2.0
  r_bd['middle_bagel_thickness']          = 6.0
  r_bd['internal_bagel_thickness']        = 2.0
  ### output
  r_bd['tkinter_view']           = False
  r_bd['output_file_basename']   = ''
  r_bd['args_in_txt'] = ""
  r_bd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_bd)

################################################################
# bagel argparse
################################################################

def bagel_add_argument(ai_parser):
  """
  Add arguments relative to the bagel
  This function intends to be used by the bagel_cli and bagel_self_test
  """
  r_parser = ai_parser
  ## diameters
  r_parser.add_argument('--axle_diameter','--ad', action='store', type=float, default=10.0, dest='sw_axle_diameter',
    help="Set the axle_diameter. Default: 10.0")
  r_parser.add_argument('--axle_internal_diameter','--aid', action='store', type=float, default=20.0, dest='sw_axle_internal_diameter',
    help="Set the axle_internal_diameter. If equal to 0.0, set to 2*axle_diameter. Default: 0.0")
  r_parser.add_argument('--axle_external_diameter','--aed', action='store', type=float, default=0.0, dest='sw_axle_external_diameter',
    help="Set the axle_external_diameter. If equal to 0.0, set to 2*axle_internal_diameter. Default: 0.0")
  ## axle_holes
  r_parser.add_argument('--axle_hole_nb','--ahn', action='store', type=int, default=6, dest='sw_axle_hole_nb',
    help="Set the number of the axle-holes. If equal to 0, no axle-hole is created. Default: 6")
  r_parser.add_argument('--axle_hole_diameter','--ahd', action='store', type=float, default=4.0, dest='sw_axle_hole_diameter',
    help="Set the diameter of the axle-holes. Default: 4.0")
  r_parser.add_argument('--axle_hole_position_diameter','--ahpd', action='store', type=float, default=0.0, dest='sw_axle_hole_position_diameter',
    help="Set the diameter of the axle-hole position circle. If equal to 0.0, set to (axle_internal_diameter+axle_external_diameter)/2. Default: 0.0")
  r_parser.add_argument('--axle_hole_angle','--aha', action='store', type=float, default=0.0, dest='sw_axle_hole_angle',
    help="Set the position angle of the first axle-hole. Default: 0.0")
  ## part thickness
  r_parser.add_argument('--external_bagel_thickness','--ebt', action='store', type=float, default=2.0, dest='sw_external_bagel_thickness',
    help="Set the thickness (z-size) of the external_bagel part. Default: 2.0")
  r_parser.add_argument('--middle_bagel_thickness','--mbt', action='store', type=float, default=6.0, dest='sw_middle_bagel_thickness',
    help="Set the thickness (z-size) of the middle_bagel part. Default: 6.0")
  r_parser.add_argument('--internal_bagel_thickness','--ibt', action='store', type=float, default=2.0, dest='sw_internal_bagel_thickness',
    help="Set the thickness (z-size) of the internal_bagel part. Default: 2.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def bagel(ai_constraints):
  """
  The main function of the script.
  It generates a bagel assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  bdi = bagel_dictionary_init()
  b_c = bdi.copy()
  b_c.update(ai_constraints)
  #print("dbg155: b_c:", b_c)
  if(len(b_c.viewkeys() & bdi.viewkeys()) != len(b_c.viewkeys() | bdi.viewkeys())): # check if the dictionary b_c has exactly all the keys compare to bagel_dictionary_init()
    print("ERR157: Error, b_c has too much entries as {:s} or missing entries as {:s}".format(b_c.viewkeys() - bdi.viewkeys(), bdi.viewkeys() - b_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: bagel constraints:")
  #for k in b_c.viewkeys():
  #  if(b_c[k] != bdi[k]):
  #    print("dbg166: for k {:s}, b_c[k] {:s} != bdi[k] {:s}".format(k, str(b_c[k]), str(bdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  # axle_diameter
  b_c['axle_radius'] = b_c['axle_diameter']/2.0
  if(b_c['axle_radius']<radian_epsilon):
    print("ERR152: Error, axle_radius {:0.3f} is too small".format(b_c['axle_radius']))
    sys.exit(2)
  # axle_internal_diameter
  b_c['axle_internal_radius'] = b_c['axle_internal_diameter']/2.0
  if(b_c['axle_internal_radius']==0):
    b_c['axle_internal_radius'] = 2*b_c['axle_radius']
  if(b_c['axle_internal_radius']<b_c['axle_radius']):
    print("ERR159: Error, axle_internal_radius {:0.3f} must be bigger than axle_radius {:0.3f}".format(b_c['axle_internal_radius'], b_c['axle_radius']))
    sys.exit(2)
  # axle_external_diameter
  b_c['axle_external_radius'] = b_c['axle_external_diameter']/2.0
  if(b_c['axle_external_radius']==0):
    b_c['axle_external_radius'] = 2*b_c['axle_internal_radius']
  if(b_c['axle_external_radius']<b_c['axle_internal_radius']+radian_epsilon):
    print("ERR166: Error, axle_external_radius {:0.3f} must be bigger than axle_internal_radius {:0.3f}".format(b_c['axle_external_radius'], b_c['axle_internal_radius']))
    sys.exit(2)
  # axle_hole_nb
  b_c['axle_hole_radius'] = 0.0
  b_c['axle_hole_position_radius'] = 0.0
  if(b_c['axle_hole_nb']>0):
    # axle_hole_diameter
    b_c['axle_hole_radius'] = b_c['axle_hole_diameter']/2.0
    if(b_c['axle_hole_radius']<radian_epsilon):
      print("ERR173: Error, axle_hole_radius {:0.3f} must be strictly positive".format(b_c['axle_hole_radius']))
      sys.exit(2)
    # axle_hole_position_diameter
    b_c['axle_hole_position_radius'] = b_c['axle_hole_position_diameter']/2.0
    if(b_c['axle_hole_position_radius']==0.0):
      b_c['axle_hole_position_radius'] = (b_c['axle_internal_radius']+b_c['axle_external_radius'])/2.0
    if(b_c['axle_hole_position_radius'] < b_c['axle_internal_radius']+b_c['axle_hole_radius']+radian_epsilon):
      print("ERR180: Error: axle_hole_position_radius {:0.3f} is too small compare to axle_internal_radius {:0.3f} and axle_hole_radius {:0.3f}".format(b_c['axle_hole_position_radius'], b_c['axle_internal_radius'], b_c['axle_hole_radius']))
      sys.exit(2)
    if(b_c['axle_hole_position_radius'] > b_c['axle_external_radius']-b_c['axle_hole_radius']-radian_epsilon):
      print("ERR183: Error: axle_hole_position_radius {:0.3f} is too big compare to axle_external_radius {:0.3f} and axle_hole_radius {:0.3f}".format(b_c['axle_hole_position_radius'], b_c['axle_external_radius'], b_c['axle_hole_radius']))
      sys.exit(2)
    # axle_hole_angle
  # external_bagel_thickness
  if(b_c['external_bagel_thickness']<radian_epsilon):
    print("ERR188: Error, external_bagel_thickness {:0.3f} is too small".format(b_c['external_bagel_thickness']))
    sys.exit(2)
  # middle_bagel_thickness
  if(b_c['middle_bagel_thickness']<radian_epsilon):
    print("ERR192: Error, middle_bagel_thickness {:0.3f} is too small".format(b_c['middle_bagel_thickness']))
    sys.exit(2)
  # internal_bagel_thickness
  if(b_c['internal_bagel_thickness']<radian_epsilon):
    print("ERR196: Error, internal_bagel_thickness {:0.3f} is too small".format(b_c['internal_bagel_thickness']))
    sys.exit(2)

  ################################################################
  # outline construction
  ################################################################
  
  ### external_bagel
  external_bagel = []
  external_bagel.append((0.0, 0.0, b_c['axle_external_radius']))
  external_bagel.append((0.0, 0.0, b_c['axle_radius']))
  for i in range(b_c['axle_hole_nb']):
    a = i*2*math.pi/b_c['axle_hole_nb']+b_c['axle_hole_angle']
    external_bagel.append((0.0+b_c['axle_hole_position_radius']*math.cos(a), 0.0+b_c['axle_hole_position_radius']*math.sin(a), b_c['axle_hole_radius']))

  ### middle_bagel
  middle_bagel = []
  middle_bagel.append((0.0, 0.0, b_c['axle_internal_radius']))
  middle_bagel.append((0.0, 0.0, b_c['axle_radius']))

  ### internal_bagel
  ib_ol_A = []
  ib_ol_A.append((b_c['axle_external_radius'], 0.0, 0))
  ib_ol_A.append((0.0, b_c['axle_external_radius'], -1*b_c['axle_external_radius'], 0.0, 0))
  ib_ol_A.append((-1*b_c['axle_radius'], 0.0, 0))
  ib_ol_A.append((0.0, b_c['axle_radius'], b_c['axle_radius'], 0.0, 0))
  ib_ol_A.append((b_c['axle_external_radius'], 0.0, 0))
  ib_ol = cnc25d_api.cnc_cut_outline(ib_ol_A, "internal_bagel_ol")
  ib_figure = []
  ib_figure.append(ib_ol)
  ib_figure_2 = []
  ib_figure_2.append(ib_ol)
  if(b_c['axle_hole_nb']>0):
    a_step = math.pi/b_c['axle_hole_nb']
    for i in range(b_c['axle_hole_nb']/2):
      a = (2*i+1)*a_step
      ib_figure.append((0.0+b_c['axle_hole_position_radius']*math.cos(a), 0.0+b_c['axle_hole_position_radius']*math.sin(a), b_c['axle_hole_radius']))
    ib_figure = cnc25d_api.rotate_and_translate_figure(ib_figure, 0.0, 0.0, b_c['axle_hole_angle']-a_step, 0.0, 0.0)
    for i in range(b_c['axle_hole_nb']/2):
      a = (2*i+1+(b_c['axle_hole_nb']%2))*a_step
      ib_figure_2.append((0.0+b_c['axle_hole_position_radius']*math.cos(a), 0.0+b_c['axle_hole_position_radius']*math.sin(a), b_c['axle_hole_radius']))
    ib_figure_2 = cnc25d_api.rotate_and_translate_figure(ib_figure_2, 0.0, 0.0, b_c['axle_hole_angle']-a_step, 0.0, 0.0)
  internal_bagel = ib_figure
  internal_bagel_2 = cnc25d_api.rotate_and_translate_figure(ib_figure_2, 0.0, 0.0, math.pi, 0.0, 0.0)

  ################################################################
  # output
  ################################################################

  # b_parameter_info
  b_parameter_info = "\nbagel parameter info:\n"
  b_parameter_info += "\n" + b_c['args_in_txt'] + "\n"
  b_parameter_info += """
bagel diameters:
axle_radius:          {:0.3f}   diameter: {:0.3f}
axle_internal_radius: {:0.3f}   diameter: {:0.3f}
axle_external_radius: {:0.3f}   diameter: {:0.3f}
""".format(b_c['axle_radius'], 2*b_c['axle_radius'], b_c['axle_internal_radius'], 2*b_c['axle_internal_radius'], b_c['axle_external_radius'], 2*b_c['axle_external_radius'])
  b_parameter_info += """
axle_fastening_holes:
axle_hole_nb:               {:d}
axle_hole_radius:           {:0.3f}   diameter: {:0.3f}
axle_hole_position_radius:  {:0.3f}   diameter: {:0.3f}
axle_hole_angle:            {:0.3f} (radian)    {:0.3f} (degree)
""".format(b_c['axle_hole_nb'], b_c['axle_hole_radius'], 2*b_c['axle_hole_radius'], b_c['axle_hole_position_radius'], 2*b_c['axle_hole_position_radius'], b_c['axle_hole_angle'], b_c['axle_hole_angle']*180/math.pi)
  b_parameter_info += """
bagel tickness:
external_bagel_thickness: {:0.3f}
middle_bagel_thickness:   {:0.3f}
internal_bagel_thickness: {:0.3f}
""".format(b_c['external_bagel_thickness'], b_c['middle_bagel_thickness'], b_c['internal_bagel_thickness'])
  #print(b_parameter_info)

  ### figures output
  # part_list
  part_list = []
  part_list.append(external_bagel)
  part_list.append(middle_bagel)
  part_list.append(internal_bagel)
  part_list.append(internal_bagel_2)
  # part_list_figure
  x_space = 2.2*b_c['axle_external_radius'] 
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## bagel_part_overview
  bagel_assembly_figure = []
  bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(external_bagel, 0.0, 0.0, 0.0,   0, 0))
  bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(middle_bagel, 0.0, 0.0, 0.0,     0, 0))
  bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(internal_bagel, 0.0, 0.0, 0.0,   0, 0))
  bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(internal_bagel_2, 0.0, 0.0, 0.0, 0, 0))

  ### freecad-object assembly configuration
  # intermediate parameters
  aer = b_c['axle_external_radius']
  air = b_c['axle_internal_radius']
  ebt = b_c['external_bagel_thickness']
  mbt = b_c['middle_bagel_thickness']
  ibt = b_c['internal_bagel_thickness']
  # conf1
  bagel_assembly_conf1 = []
  bagel_assembly_conf1.append((external_bagel, -1*aer, -1*aer, 2*aer, 2*aer, ebt, 'i', 'xz', -1*aer, 0,         -1*aer))
  bagel_assembly_conf1.append((middle_bagel,   -1*air, -1*air, 2*air, 2*air, mbt, 'i', 'xz', -1*air, ebt,       -1*air))
  bagel_assembly_conf1.append((internal_bagel, -1*aer, -1*aer, 2*aer, 2*aer, ibt, 'i', 'xz', -1*aer, ebt+mbt,   -1*aer))
  bagel_assembly_conf1.append((internal_bagel_2, -1*aer, -1*aer, 2*aer, 2*aer, ibt, 'i', 'xz', -1*aer, ebt+mbt, -1*aer))

  ### display with Tkinter
  if(b_c['tkinter_view']):
    print(b_parameter_info)
    cnc25d_api.figure_simple_display(bagel_assembly_figure, part_list_figure, b_parameter_info)

  ### generate output file
  if(b_c['output_file_basename']!=''):
    (output_file_basename, output_file_suffix) = cnc25d_api.get_output_file_suffix(b_c['output_file_basename'])
    # parts
    cnc25d_api.generate_output_file(external_bagel, output_file_basename + "_external" + output_file_suffix, b_c['external_bagel_thickness'], b_parameter_info)
    cnc25d_api.generate_output_file(middle_bagel, output_file_basename + "_middle" + output_file_suffix, b_c['middle_bagel_thickness'], b_parameter_info)
    cnc25d_api.generate_output_file(internal_bagel, output_file_basename + "_internal" + output_file_suffix, b_c['internal_bagel_thickness'], b_parameter_info)
    # assembly
    if((output_file_suffix=='.svg')or(output_file_suffix=='.dxf')):
      cnc25d_api.generate_output_file(part_list_figure, output_file_basename + "_part_list" + output_file_suffix, 1.0, b_parameter_info)
      cnc25d_api.generate_output_file(bagel_assembly_figure, output_file_basename + "_part_overview" + output_file_suffix, 1.0, b_parameter_info)
    else:
      #cnc25d_api.generate_3d_assembly_output_file(bagel_assembly_conf1, output_file_basename + "_assembly", True, False, [])
      cnc25d_api.generate_3d_assembly_output_file(bagel_assembly_conf1, output_file_basename + "_assembly")


  #### return
  if(b_c['return_type']=='int_status'):
    r_b = 1
  elif(b_c['return_type']=='cnc25d_figure'):
    r_b = part_list
  elif(b_c['return_type']=='freecad_object'):
    r_b = cnc25d_api.figures_to_freecad_assembly(bagel_assembly_conf1)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(b_c['return_type']))
    sys.exit(2)
  return(r_b)

################################################################
# bagel wrapper dance
################################################################

def bagel_argparse_to_dictionary(ai_b_args):
  """ convert a bagel_argparse into a bagel_dictionary
  """
  r_bd = {}
  ## diameters
  r_bd['axle_diameter']                   = ai_b_args.sw_axle_diameter
  r_bd['axle_internal_diameter']          = ai_b_args.sw_axle_internal_diameter
  r_bd['axle_external_diameter']          = ai_b_args.sw_axle_external_diameter
  ## axle_holes
  r_bd['axle_hole_nb']                    = ai_b_args.sw_axle_hole_nb
  r_bd['axle_hole_diameter']              = ai_b_args.sw_axle_hole_diameter
  r_bd['axle_hole_position_diameter']     = ai_b_args.sw_axle_hole_position_diameter
  r_bd['axle_hole_angle']                 = ai_b_args.sw_axle_hole_angle
  ## part thickness
  r_bd['external_bagel_thickness']        = ai_b_args.sw_external_bagel_thickness
  r_bd['middle_bagel_thickness']          = ai_b_args.sw_middle_bagel_thickness
  r_bd['internal_bagel_thickness']        = ai_b_args.sw_internal_bagel_thickness
  ### output
  #r_bd['tkinter_view']           = False
  r_bd['output_file_basename']   = ai_b_args.sw_output_file_basename
  #r_bd['args_in_txt'] = ""
  r_bd['return_type'] = ai_b_args.sw_return_type
  #### return
  return(r_bd)
  
def bagel_argparse_wrapper(ai_b_args, ai_args_in_txt=""):
  """
  wrapper function of bagel() to call it using the bagel_parser.
  bagel_parser is mostly used for debug and non-regression tests.
  """
  # view the bagel with Tkinter as default action
  tkinter_view = True
  if(ai_b_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  bd = bagel_argparse_to_dictionary(ai_b_args)
  bd['args_in_txt'] = ai_args_in_txt
  bd['tkinter_view'] = tkinter_view
  #bd['return_type'] = 'int_status'
  r_b = bagel(bd)
  return(r_b)

################################################################
# self test
################################################################

def bagel_self_test():
  """
  This is the non-regression test of bagel.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , ""],
    ["no axle_holes"        , "--axle_hole_nb 0"],
    ["odd number of axle_holes" , "--axle_hole_nb 5"],
    ["outputfile" , "--output_file_basename test_output/bagel_self_test.dxf"],
    ["last test"            , "--axle_internal_diameter 25.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  bagel_parser = argparse.ArgumentParser(description='Command line interface for the function bagel().')
  bagel_parser = bagel_add_argument(bagel_parser)
  bagel_parser = cnc25d_api.generate_output_file_add_argument(bagel_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = bagel_parser.parse_args(l_args)
    r_bst = bagel_argparse_wrapper(st_args)
  return(r_bst)

################################################################
# bagel command line interface
################################################################

def bagel_cli(ai_args=""):
  """ command line interface of bagel.py when it is used in standalone
  """
  # bagel parser
  bagel_parser = argparse.ArgumentParser(description='Command line interface for the function bagel().')
  bagel_parser = bagel_add_argument(bagel_parser)
  bagel_parser = cnc25d_api.generate_output_file_add_argument(bagel_parser, 1)
  # switch for self_test
  bagel_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "bagel arguments: " + ' '.join(effective_args)
  b_args = bagel_parser.parse_args(effective_args)
  print("dbg111: start making bagel")
  if(b_args.sw_run_self_test):
    r_b = bagel_self_test()
  else:
    r_b = bagel_argparse_wrapper(b_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_b)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("bagel.py says hello!\n")
  my_b = bagel_cli()
  #my_b = bagel_cli("--return_type freecad_object")
  try: # depending on b_c['return_type'] it might be or not a freecad_object
    Part.show(my_b)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


