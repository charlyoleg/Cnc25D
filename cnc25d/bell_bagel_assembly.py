# bell_bagel_assembly.py
# generates the bell and bagel assembly
# created by charlyoleg on 2013/12/02
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
bell_bagel_assembly.py generates the assembly of a bell with two bagels.
The main function displays in a Tk-interface the bell_bagel parts, or generates the design as files or returns the design as FreeCAD Part object.
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
import bell
import bagel

################################################################
# bell_bagel_assembly dictionary-arguments default values
################################################################

def bba_dictionary_init(ai_variant = 0):
  """ create and initiate a bell_bagel_assembly dictionary with the default value
  """
  r_bd = {}
  ### heritage from bell
  r_bd.update(bell.bell_dictionary_init(1))
  ### heritage from bagel
  r_bd.update(bagel.bagel_dictionary_init(1))
  ### output
  if(ai_variant != 1):
    r_bd['tkinter_view']           = False
    r_bd['output_file_basename']   = ''
    r_bd['args_in_txt'] = ""
    r_bd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_bd)

################################################################
# bell_bagel_assembly argparse
################################################################

def bba_add_argument(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the bell_bagel_assembly
  This function intends to be used by the bba_cli and bba_self_test
  """
  r_parser = ai_parser
  ### heritage from bell
  r_parser = bell.bell_add_argument(r_parser, 1)
  ### heritage from bagel
  r_parser = bagel.bagel_add_argument(r_parser, 1)
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def bba(ai_constraints):
  """
  The main function of the script.
  It generates a bell_bagel_assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  bbadi = bba_dictionary_init()
  bba_c = bbadi.copy()
  bba_c.update(ai_constraints)
  #print("dbg155: bba_c:", bba_c)
  if(len(bba_c.viewkeys() & bbadi.viewkeys()) != len(bba_c.viewkeys() | bbadi.viewkeys())): # check if the dictionary bba_c has exactly all the keys compare to bba_dictionary_init()
    print("ERR157: Error, bba_c has too much entries as {:s} or missing entries as {:s}".format(bba_c.viewkeys() - bbadi.viewkeys(), bbadi.viewkeys() - bba_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: bba constraints:")
  #for k in bba_c.viewkeys():
  #  if(bba_c[k] != bbadi[k]):
  #    print("dbg166: for k {:s}, bba_c[k] {:s} != bbadi[k] {:s}".format(k, str(bba_c[k]), str(bbadi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  # bagel_axle_diameter
  bba_c['bagel_axle_radius'] = bba_c['bagel_axle_diameter']/2.0
  if(bba_c['bagel_axle_radius']<radian_epsilon):
    print("ERR125: Error, bagel_axle_radius {:0.3f} is too small".format(bba_c['bagel_axle_radius']))
    sys.exit(2)
  bba_c['bagel_axle_diameter'] = 2*bba_c['bagel_axle_radius']
  # bagel_axle_internal_diameter
  bba_c['bagel_axle_internal_radius'] = bba_c['bagel_axle_internal_diameter']/2.0
  if(bba_c['bagel_axle_internal_radius']==0):
    bba_c['bagel_axle_internal_radius'] = 2*bba_c['bagel_axle_radius']
  if(bba_c['bagel_axle_internal_radius']<bba_c['bagel_axle_radius']):
    print("ERR132: Error, bagel_axle_internal_radius {:0.3f} must be bigger than bagel_axle_radius {:0.3f}".format(bba_c['bagel_axle_internal_radius'], bba_c['bagel_axle_radius']))
    sys.exit(2)
  bba_c['bagel_axle_internal_diameter'] = 2*bba_c['bagel_axle_internal_radius']
  # bagel_axle_external_diameter
  bba_c['bagel_axle_external_radius'] = bba_c['bagel_axle_external_diameter']/2.0
  if(bba_c['bagel_axle_external_radius']==0):
    bba_c['bagel_axle_external_radius'] = 2*bba_c['bagel_axle_internal_radius']
  if(bba_c['bagel_axle_external_radius']<bba_c['bagel_axle_internal_radius']+radian_epsilon):
    print("ERR139: Error, bagel_axle_external_radius {:0.3f} must be bigger than bagel_axle_internal_radius {:0.3f}".format(bba_c['bagel_axle_external_radius'], bba_c['bagel_axle_internal_radius']))
    sys.exit(2)
  bba_c['bagel_axle_external_diameter'] = 2*bba_c['bagel_axle_external_radius']
  # axle_internal_diameter
  bba_c['axle_internal_radius'] = bba_c['axle_internal_diameter']/2.0
  if(bba_c['axle_internal_radius']==0):
    bba_c['axle_internal_radius'] = bba_c['bagel_axle_internal_radius']
  if(bba_c['axle_internal_radius']<bba_c['bagel_axle_radius']):
    print("ERR146: Error, axle_internal_radius {:0.3f} must be bigger than bagel_axle_radius {:0.3f}".format(bba_c['axle_internal_radius'], bba_c['bagel_axle_radius']))
    sys.exit(2)
  bba_c['axle_internal_diameter'] = 2*bba_c['axle_internal_radius']
  # axle_external_diameter
  bba_c['axle_external_radius'] = bba_c['axle_external_diameter']/2.0
  if(bba_c['axle_external_radius']==0):
    bba_c['axle_external_radius'] = 2*bba_c['axle_internal_radius']
  if(bba_c['axle_external_radius']<bba_c['axle_internal_radius']+radian_epsilon):
    print("ERR139: Error, axle_external_radius {:0.3f} must be bigger than axle_internal_radius {:0.3f}".format(bba_c['axle_external_radius'], bba_c['axle_internal_radius']))
    sys.exit(2)
  bba_c['axle_external_diameter'] = 2*bba_c['axle_external_radius']

  ################################################################
  # outline construction
  ################################################################

  ################################################################
  # output
  ################################################################

  bell_ci = bell.bell_dictionary_init(1)
  bell_c = dict([ (k, bba_c[k]) for k in bell_ci.keys() ]) # extract only the entries of bell
  bell_c['tkinter_view']         = bba_c['tkinter_view']
  bell_c['output_file_basename'] = bba_c['output_file_basename']
  bell_c['args_in_txt']          = bba_c['args_in_txt']
  bell_c['return_type']          = 'figures_3dconf_info'
  (bell_part_list, bell_3d_conf, bell_param_info) = bell.bell(bell_c)

  bagel_ci = bagel.bagel_dictionary_init(1)
  bagel_c = dict([ (k, bba_c[k]) for k in bagel_ci.keys() ]) # extract only the entries of bagel
  bagel_c['middle_bagel_thickness'] = bba_c['face_thickness']
  bagel_c['axle_hole_nb'] = bba_c['axle_hole_nb']
  bagel_c['axle_hole_diameter'] = bba_c['axle_hole_diameter']
  bagel_c['axle_hole_position_diameter'] = bba_c['axle_hole_position_diameter']
  bagel_c['axle_hole_angle'] = bba_c['axle_hole_angle']
  bagel_c['tkinter_view']         = False #bba_c['tkinter_view']
  bagel_c['output_file_basename'] = bba_c['output_file_basename']
  bagel_c['args_in_txt']          = bba_c['args_in_txt']
  bagel_c['return_type']          = 'figures_3dconf_info'
  (bagel_part_list, bagel_3d_conf, bagel_param_info) = bagel.bagel(bagel_c)

  # parameter info
  bba_parameter_info = bell_param_info + bagel_param_info

  ### figures output
  # part_list
  part_list = []
  part_list.extend(bell_part_list)
  part_list.extend(bagel_part_list)
  # part_list_figure
  x_space = 2.1*bba_c['base_diameter'] 
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## bell_bagel_assembly
  bell_face_fig = part_list[0]
  bagel_external_fig = part_list[6]
  bagel_z = bba_c['base_thickness'] + bba_c['bell_face_height'] + bba_c['leg_length']
  bell_bagel_assembly_figure = []
  bell_bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(bell_face_fig, 0.0, 0.0, 0.0,      0, 0))
  bell_bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(bagel_external_fig, 0.0, 0.0, 0.0, 0, bagel_z))

  ### freecad-object assembly configuration
  # sub function
  def re_conf3d(ai_conf_line, ai_flip, ai_orientation, ai_tx, ai_ty, ai_tz):
    """ translate a figure of a 3D configuration
    """
    (figure, zero_x, zero_y, size_x, size_y, size_z, flip, orientation, tx, ty, tz) = ai_conf_line
    r_conf_line = (figure, zero_x, zero_y, size_x, size_y, size_z, ai_flip, ai_orientation, ai_tx, ai_ty, ai_tz)
    return(r_conf_line)
  # intermediate parameters
  bger = bba_c['bagel_axle_external_radius']
  bgir = bba_c['bagel_axle_internal_radius']
  bagel_y1 = bba_c['bell_face_width']/2.0
  bagel_y2 = -1*bba_c['bell_face_width']/2.0
  bget = bba_c['external_bagel_thickness']
  bgmt = bba_c['face_thickness']
  bgit = bba_c['internal_bagel_thickness']
  re_conf_bagel_1 = []
  re_conf_bagel_1.append(('i', 'xz', -1*bger, bagel_y1, bagel_z-bger))
  re_conf_bagel_1.append(('i', 'xz', -1*bgir, bagel_y1-bgmt, bagel_z-bgir))
  re_conf_bagel_1.append(('i', 'xz', -1*bger, bagel_y1-bgmt-bgit, bagel_z-bger))
  re_conf_bagel_1.append(('i', 'xz', -1*bger, bagel_y1-bgmt-bgit, bagel_z-bger))
  re_conf_bagel_2 = []
  re_conf_bagel_2.append(('i', 'xz', -1*bger, bagel_y2-bget, bagel_z-bger))
  re_conf_bagel_2.append(('i', 'xz', -1*bgir, bagel_y2, bagel_z-bgir))
  re_conf_bagel_2.append(('i', 'xz', -1*bger, bagel_y2+bgmt, bagel_z-bger))
  re_conf_bagel_2.append(('i', 'xz', -1*bger, bagel_y2+bgmt, bagel_z-bger))
  # conf1
  bell_bagel_assembly_conf1 = []
  bell_bagel_assembly_conf1.extend(bell_3d_conf)
  for i in range(len(bagel_3d_conf)):
    bell_bagel_assembly_conf1.append(re_conf3d(bagel_3d_conf[i], re_conf_bagel_1[i][0], re_conf_bagel_1[i][1], re_conf_bagel_1[i][2], re_conf_bagel_1[i][3], re_conf_bagel_1[i][4]))
  for i in range(len(bagel_3d_conf)):
    bell_bagel_assembly_conf1.append(re_conf3d(bagel_3d_conf[i], re_conf_bagel_2[i][0], re_conf_bagel_2[i][1], re_conf_bagel_2[i][2], re_conf_bagel_2[i][3], re_conf_bagel_2[i][4]))

  ### display with Tkinter
  if(bba_c['tkinter_view']):
    #print(bba_parameter_info)
    #print(bell_param_info)
    print(bagel_param_info)
    cnc25d_api.figure_simple_display(bell_bagel_assembly_figure, [], bba_parameter_info)

  ### generate output file
  if(bba_c['output_file_basename']!=''):
    (output_file_basename, output_file_suffix) = cnc25d_api.get_output_file_suffix(bba_c['output_file_basename'])
    # parts
    # assembly
    if((output_file_suffix=='.svg')or(output_file_suffix=='.dxf')):
      cnc25d_api.generate_output_file(part_list_figure, output_file_basename + "_bba_part_list" + output_file_suffix, 1.0, bba_parameter_info)
      cnc25d_api.generate_output_file(bell_bagel_assembly_figure, output_file_basename + "_bell_bagel_assembly" + output_file_suffix, 1.0, bba_parameter_info)
    else:
      #cnc25d_api.generate_3d_assembly_output_file(bell_bagel_assembly_conf1, output_file_basename + "_assembly", True, False, [])
      cnc25d_api.generate_3d_assembly_output_file(bell_bagel_assembly_conf1, output_file_basename + "_bell_bagel_assembly")


  #### return
  if(bba_c['return_type']=='int_status'):
    r_b = 1
  elif(bba_c['return_type']=='cnc25d_figure'):
    r_b = part_list
  elif(bba_c['return_type']=='freecad_object'):
    r_b = cnc25d_api.figures_to_freecad_assembly(bell_bagel_assembly_conf1)
  elif(bba_c['return_type']=='figures_3dconf_info'):
    r_b = (part_list, bell_bagel_assembly_conf1, bba_parameter_info)
  else:
    print("ERR277: Error the return_type {:s} is unknown".format(bba_c['return_type']))
    sys.exit(2)
  return(r_b)

################################################################
# bell_bagel_assembly wrapper dance
################################################################

def bba_argparse_to_dictionary(ai_b_args, ai_variant=0):
  """ convert a bba_argparse into a bba_dictionary
  """
  r_bd = {}
  ### heritage from bell
  r_bd.update(bell.bell_argparse_to_dictionary(ai_b_args, 1))
  ### heritage from bagel
  r_bd.update(bagel.bagel_argparse_to_dictionary(ai_b_args, 1))
  ### output
  #r_bd['tkinter_view']           = False
  r_bd['output_file_basename']   = ai_b_args.sw_output_file_basename
  #r_bd['args_in_txt'] = ""
  r_bd['return_type'] = ai_b_args.sw_return_type
  #### return
  return(r_bd)
  
def bba_argparse_wrapper(ai_b_args, ai_args_in_txt=""):
  """
  wrapper function of bba() to call it using the bba_parser.
  bba_parser is mostly used for debug and non-regression tests.
  """
  # view the bell_bagel_assembly with Tkinter as default action
  tkinter_view = True
  if(ai_b_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  bbad = bba_argparse_to_dictionary(ai_b_args)
  bbad['args_in_txt'] = ai_args_in_txt
  bbad['tkinter_view'] = tkinter_view
  #bbad['return_type'] = 'int_status'
  r_bba = bba(bbad)
  return(r_bba)

################################################################
# self test
################################################################

def bba_self_test():
  """
  This is the non-regression test of bba.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , ""],
    ["no axle_holes"        , "--axle_hole_nb 0"],
    ["odd number of axle_holes" , "--axle_hole_nb 5"],
    ["outputfile" , "--output_file_basename test_output/bba_self_test.dxf"],
    ["last test"            , "--bagel_axle_internal_diameter 25.0 --bagel_axle_external_diameter 40.0 --axle_hole_position_diameter 35.0 --axle_internal_diameter 28.0 --axle_external_diameter 42.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  bba_parser = argparse.ArgumentParser(description='Command line interface for the function bba().')
  bba_parser = bba_add_argument(bba_parser)
  bba_parser = cnc25d_api.generate_output_file_add_argument(bba_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = bba_parser.parse_args(l_args)
    r_bst = bba_argparse_wrapper(st_args)
  return(r_bst)

################################################################
# bell_bagel_assembly command line interface
################################################################

def bba_cli(ai_args=""):
  """ command line interface of bell_bagel_assembly.py when it is used in standalone
  """
  # bba parser
  bba_parser = argparse.ArgumentParser(description='Command line interface for the function bba().')
  bba_parser = bba_add_argument(bba_parser)
  bba_parser = cnc25d_api.generate_output_file_add_argument(bba_parser, 1)
  # switch for self_test
  bba_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "bell_bagel_assembly arguments: " + ' '.join(effective_args)
  bba_args = bba_parser.parse_args(effective_args)
  print("dbg111: start making bell_bagel_assembly")
  if(bba_args.sw_run_self_test):
    r_bba = bba_self_test()
  else:
    r_bba = bba_argparse_wrapper(bba_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_bba)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("bell_bagel_assembly.py says hello!\n")
  my_bba = bba_cli()
  #my_bba = bba_cli("--bell_extra_cut_thickness 1.0 --bagel_extra_cut_thickness 1.0 --return_type freecad_object")
  try: # depending on bba_c['return_type'] it might be or not a freecad_object
    Part.show(my_bba)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


