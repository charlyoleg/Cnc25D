# gimbal.py
# generates the gimbal, a mechanism with the roll-pitch angles as degrees of freedom
# created by charlyoleg on 2013/12/10
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
gimbal.py generates the gimbal assembly, a mechanism with the roll-pitch angles as degrees of freedom.
The main function displays in a Tk-interface the gimbal parts, or generates the design as files or returns the design as FreeCAD Part object.
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
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import bell_bagel_assembly
import cross_cube
import angles

################################################################
# gimbal dictionary-arguments default values
################################################################

def gimbal_dictionary_init(ai_variant=0):
  """ create and initiate a gimbal_dictionary with the default value
  """
  r_gd = {}
  ### inheritance from bell_bagel_assembly
  r_gd.update(bell_bagel_assembly.bba_dictionary_init(1))
  ### inheritance from cross_cube
  r_gd.update(cross_cube.cross_cube_dictionary_init(1))
  ### roll-pitch angles
  r_gd['bottom_angle']    = 0.0
  r_gd['top_angle']       = 0.0
  ### pan_tilt angles # can be set only if roll-pitch angles are left to 0.0
  r_gd['pan_angle']    = 0.0
  r_gd['tilt_angle']       = 0.0
  ### output
  if(ai_variant==0):
    r_gd['tkinter_view']           = False
    r_gd['output_file_basename']   = ''
    r_gd['args_in_txt'] = ""
    r_gd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_gd)

################################################################
# gimbal argparse
################################################################

def gimbal_add_argument(ai_parser, ai_variant=0):
  """
  Add arguments relative to the gimbal
  This function intends to be used by the gimbal_cli and gimbal_self_test
  """
  r_parser = ai_parser
  ### inheritance from bell_bagel_assembly
  r_parser = bell_bagel_assembly.bba_add_argument(r_parser, 1)
  ### inheritance from cross_cube
  r_parser = cross_cube.cross_cube_add_argument(r_parser, 1)
  ### roll-pitch angles
  r_parser.add_argument('--bottom_angle','--ba', action='store', type=float, default=0.0, dest='sw_bottom_angle',
    help="Set the bottom angle. Default: 0.0")
  r_parser.add_argument('--top_angle','--ta', action='store', type=float, default=0.0, dest='sw_top_angle',
    help="Set the top angle. Default: 0.0")
  ### pan_tilt angles # can be set only if roll-pitch angles are left to 0.0
  r_parser.add_argument('--pan_angle','--pan', action='store', type=float, default=0.0, dest='sw_pan_angle',
    help="Set the pan angle. Use the pan-tilt angles only if roll-pitch angles are left to 0.0. Default: 0.0")
  r_parser.add_argument('--tilt_angle','--tilt', action='store', type=float, default=0.0, dest='sw_tilt_angle',
    help="Set the tilt angle. Default: 0.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def gimbal(ai_constraints):
  """
  The main function of the script.
  It generates a gimbal assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  gdi = gimbal_dictionary_init()
  g_c = gdi.copy()
  g_c.update(ai_constraints)
  #print("dbg155: g_c:", g_c)
  if(len(g_c.viewkeys() & gdi.viewkeys()) != len(g_c.viewkeys() | gdi.viewkeys())): # check if the dictionary g_c has exactly all the keys compare to gimbal_dictionary_init()
    print("ERR148: Error, g_c has too much entries as {:s} or missing entries as {:s}".format(g_c.viewkeys() - gdi.viewkeys(), gdi.viewkeys() - g_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: gimbal constraints:")
  #for k in g_c.viewkeys():
  #  if(g_c[k] != gdi[k]):
  #    print("dbg166: for k {:s}, g_c[k] {:s} != gdi[k] {:s}".format(k, str(g_c[k]), str(gdi[k])))

  ### precision
  radian_epsilon = math.pi/1000

  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  if((g_c['bottom_angle']!=0)or(g_c['top_angle']!=0)):
    if((g_c['pan_angle']!=0)or(g_c['tilt_angle']!=0)):
      print("ERR145: Error, roll-pitch angles {:0.3f} {:0.3f} and pan-tilt angles {:0.3f} {:0.3f} are set together".format(g_c['bottom_angle'], g_c['top_angle'], g_c['pan_angle'], g_c['tilt_angle']))
      sys.exit(2)
  if((g_c['pan_angle']!=0)or(g_c['tilt_angle']!=0)):
    (a1, a2) = angles.pan_tilt_to_roll_pitch(g_c['pan_angle'], g_c['tilt_angle'])
    g_c['bottom_angle'] = a1
    g_c['top_angle'] = a2
  (b1, b2) = angles.roll_pitch_to_pan_tilt(g_c['bottom_angle'], g_c['top_angle'])
  (a1, a2) = angles.pan_tilt_to_roll_pitch(b1, b2)
  if((abs(g_c['bottom_angle']-a1)>radian_epsilon)or(abs(g_c['top_angle']-a2)>radian_epsilon)):
    print("ERR154: Internal error in angle conversion: a1 {:0.3f} {:0.3f}  a2 {:0.3f} {:0.3f}".format(g_c['bottom_angle'], a1, g_c['top_angle'], a2))
    sys.exit(2)
  b3 = angles.roll_pitch_pan_tilt_drift_angle(g_c['bottom_angle'], g_c['top_angle'])
  #
  if(abs(g_c['bottom_angle'])>0.7*math.pi):
    print("ERR133: Error, bottom_angle {:0.3f} absolute value is too big".format(g_c['bottom_angle']))
    sys.exit(2)
  if(abs(g_c['top_angle'])>0.7*math.pi):
    print("ERR136: Error, top_angle {:0.3f} absolute value is too big".format(g_c['top_angle']))
    sys.exit(2)
  if(abs(g_c['bottom_angle'])+abs(g_c['top_angle'])>1.1*math.pi):
    print("ERR139: Error, bottom_angle {:0.3f} and top_angle {:0.3f} absolute values can not be so large at the same time".format(g_c['bottom_angle'], g_c['top_angle']))
    sys.exit(2)
  # pan-tilt
  g_c['pan_angle'] = b1
  g_c['tilt_angle'] = b2
  if(g_c['tilt_angle']>0.6*math.pi):
    print("ERR147: Error, tilt_angle {:0.3f} is to big".format(g_c['tilt_angle']))
    sys.exit(2)

  ################################################################
  # outline construction
  ################################################################
  
  # bell_bagel_assembly
  bb_ci = bell_bagel_assembly.bba_dictionary_init(1)
  bb_c = dict([ (k, g_c[k]) for k in bb_ci.viewkeys() & gdi.viewkeys() ]) # extract only the entries of the intersection of bell_bagel_assembly and gimbal
  bb_c['tkinter_view'] = False
  bb_c['output_file_basename'] = ''
  bb_c['args_in_txt'] = "bell_bagel for gimbal"
  bb_c['return_type'] = 'figures_3dconf_info' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  (bell_bagel_parts, bell_bagel_3d_conf,  bell_bagel_parameter_info) = bell_bagel_assembly.bba(bb_c)
  bell_face = bell_bagel_parts[0]

  # cross_cube
  cc_ci = cross_cube.cross_cube_dictionary_init(1)
  cc_c = dict([ (k, g_c[k]) for k in cc_ci.viewkeys() & gdi.viewkeys() ]) # extract only the entries of the intersection of cross_cube and gimbal
  cc_c['tkinter_view'] = False
  cc_c['output_file_basename'] = ''
  cc_c['args_in_txt'] = "cross_cube for gimbal"
  cc_c['return_type'] = 'figures_3dconf_info' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  (cross_cube_parts, cross_cube_3d_conf,  cross_cube_parameter_info) = cross_cube.cross_cube(cc_c)
  crest_A = cross_cube_parts[1]
  crest_B = cross_cube_parts[3]

  ## gimbal 2D sketch
  # intermediate parameters
  bagel_z = g_c['base_thickness'] + g_c['bell_face_height'] + g_c['leg_length']
  crest_A_axle_z = g_c['top_thickness'] + g_c['height_margin'] + g_c['axle_diameter']/2.0
  crest_B_axle_z = crest_A_axle_z + g_c['inter_axle_length']
  #
  bottom_bell_face = cnc25d_api.rotate_and_translate_figure(bell_face, 0, bagel_z, 0.0, 0.0, 0.0)
  top_bell_face = cnc25d_api.rotate_and_translate_figure(bell_face, 0, bagel_z, math.pi+g_c['top_angle'], 0.0, crest_B_axle_z-bagel_z)
  bottom_crest_A = cnc25d_api.rotate_and_translate_figure(crest_A, g_c['cube_width']/2.0, crest_A_axle_z, g_c['bottom_angle'], -1*g_c['cube_width']/2.0, bagel_z-crest_A_axle_z)
  top_crest_B = cnc25d_api.rotate_and_translate_figure(crest_B, g_c['cube_width']/2.0, crest_B_axle_z, 0.0, -1*g_c['cube_width']/2.0, 0.0)

  ################################################################
  # output
  ################################################################

  # g_parameter_info
  g_parameter_info = "\ngimbal parameter info:\n"
  g_parameter_info += "\n" + g_c['args_in_txt'] + "\n"
  g_parameter_info += bell_bagel_parameter_info
  g_parameter_info += cross_cube_parameter_info
  g_parameter_info += """
roll-pitch angles:
bottom_angle:   {:0.3f} (radian)    {:0.3f} (degree)
top_angle:      {:0.3f} (radian)    {:0.3f} (degree)
pan-tilt conversion:
pan_angle:      {:0.3f} (radian)    {:0.3f} (degree)
tilt_angle:     {:0.3f} (radian)    {:0.3f} (degree)
roll-pitch pan-tilt drit angle: {:0.3f} (radian)    {:0.3f} (degree)
""".format(g_c['bottom_angle'], g_c['bottom_angle']*180/math.pi, g_c['top_angle'], g_c['top_angle']*180/math.pi, g_c['pan_angle'], g_c['pan_angle']*180/math.pi, g_c['tilt_angle'], g_c['tilt_angle']*180/math.pi, b3, b3*180/math.pi)
  #print(g_parameter_info)

  ### figures output
  # part_list
  part_list = []
  part_list.extend(bell_bagel_parts)
  part_list.extend(cross_cube_parts)
  # part_list_figure
  x_space = 1.2*max(g_c['gear_module']*g_c['virtual_tooth_nb'], g_c['base_diameter'])
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## gimbal_sketch
  gimbal_sketch_figure = []
  gimbal_sketch_figure.extend(cnc25d_api.rotate_and_translate_figure(bottom_bell_face, 0.0, 0.0, 0.0,   0*x_space, 0))
  gimbal_sketch_figure.extend(cnc25d_api.rotate_and_translate_figure(bottom_crest_A, 0.0, 0.0, 0.0,     0*x_space, 0))
  gimbal_sketch_figure.extend(cnc25d_api.rotate_and_translate_figure(top_bell_face, 0.0, 0.0, 0.0,      1*x_space, 0))
  gimbal_sketch_figure.extend(cnc25d_api.rotate_and_translate_figure(top_crest_B, 0.0, 0.0, 0.0,        1*x_space, 0))

  ### gimbal freecad construction
  def gimbal_freecad_construction(ai_bell_bagel_3d_conf, ai_cross_cube_3d_conf, ai_bottom_angle, ai_top_angle):
    """ generate the the freecad-object gimbal
    """
    # intermediate parameters
    z1 = g_c['base_thickness'] + g_c['bell_face_height'] + g_c['leg_length']
    z2 = g_c['inter_axle_length']
    # make the freecad-objects
    fc_bb_bottom = cnc25d_api.figures_to_freecad_assembly(ai_bell_bagel_3d_conf)
    fc_bb_top = fc_bb_bottom.copy()
    fc_cc = cnc25d_api.figures_to_freecad_assembly(ai_cross_cube_3d_conf)
    # place
    fc_bb_bottom.rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),90)
    fc_bb_top.rotate(Base.Vector(0,0,z1),Base.Vector(0,1,0),180)
    fc_bb_top.translate(Base.Vector(0,0,z2))
    fc_cc.translate(Base.Vector(-1*g_c['cube_width']/2.0, -1*g_c['cube_width']/2.0, z1-(g_c['top_thickness'] + g_c['height_margin'] + g_c['axle_diameter']/2.0)))
    fc_cc.rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),90)
    # apply the rotation
    fc_bb_top.rotate(Base.Vector(0,0,z1+z2),Base.Vector(0,1,0),ai_top_angle*180/math.pi)
    fc_top = Part.makeCompound([fc_bb_top, fc_cc])
    fc_top.rotate(Base.Vector(0,0,z1),Base.Vector(1,0,0),ai_bottom_angle*180/math.pi)
    r_fc_gimbal = Part.makeCompound([fc_bb_bottom, fc_top])
    return(r_fc_gimbal)

  ### display with Tkinter
  if(g_c['tkinter_view']):
    print(g_parameter_info)
    cnc25d_api.figure_simple_display(gimbal_sketch_figure, [], g_parameter_info)

  ### generate output file
  if(g_c['output_file_basename']!=''):
    (output_file_basename, output_file_suffix) = cnc25d_api.get_output_file_suffix(g_c['output_file_basename'])
    # bell_bagel parts 
    bb_c['output_file_basename'] = g_c['output_file_basename']
    bb_c['return_type'] = 'int_status'
    bell_bagel_assembly.bba(bb_c)
    # cross_cube parts 
    cc_c['output_file_basename'] = g_c['output_file_basename']
    cc_c['return_type'] = 'int_status'
    cross_cube.cross_cube(cc_c)
    # assembly
    if((output_file_suffix=='.svg')or(output_file_suffix=='.dxf')):
      cnc25d_api.generate_output_file(part_list_figure, output_file_basename + "_gimbal_part_list" + output_file_suffix, 1.0, g_parameter_info)
      cnc25d_api.generate_output_file(gimbal_sketch_figure, output_file_basename + "_gimbal_sketch" + output_file_suffix, 1.0, g_parameter_info)
    else:
      cnc25d_api.freecad_object_output_file(gimbal_freecad_construction(bell_bagel_3d_conf, cross_cube_3d_conf, g_c['bottom_angle'], g_c['top_angle']), output_file_basename + "_gimbal", True, False, [])
      cnc25d_api.freecad_object_output_file(gimbal_freecad_construction(bell_bagel_3d_conf, cross_cube_3d_conf, 0, 0), output_file_basename + "_gimbal_00_00", True, False, [])
      cnc25d_api.freecad_object_output_file(gimbal_freecad_construction(bell_bagel_3d_conf, cross_cube_3d_conf, math.pi/2, 0), output_file_basename + "_gimbal_90_00", True, False, [])
      cnc25d_api.freecad_object_output_file(gimbal_freecad_construction(bell_bagel_3d_conf, cross_cube_3d_conf, 0, math.pi/2), output_file_basename + "_gimbal_00_90", True, False, [])
      cnc25d_api.freecad_object_output_file(gimbal_freecad_construction(bell_bagel_3d_conf, cross_cube_3d_conf, math.pi/4, math.pi/4), output_file_basename + "_gimbal_45_45", True, False, [])
      cnc25d_api.freecad_object_output_file(gimbal_freecad_construction(bell_bagel_3d_conf, cross_cube_3d_conf, math.pi/12, math.pi/6), output_file_basename + "_gimbal_15_30", True, False, [])
      cnc25d_api.freecad_object_output_file(gimbal_freecad_construction(bell_bagel_3d_conf, cross_cube_3d_conf, math.pi/3, math.pi/9), output_file_basename + "_gimbal_60_20", True, False, [])

  #### return
  if(g_c['return_type']=='int_status'):
    r_g = 1
  elif(g_c['return_type']=='cnc25d_figure'):
    r_g = part_list
  elif(g_c['return_type']=='freecad_object'):
    r_g = gimbal_freecad_construction(bell_bagel_3d_conf, cross_cube_3d_conf, g_c['bottom_angle'], g_c['top_angle'])
  elif(g_c['return_type']=='figures_3dconf_info'):
    r_g = (part_list, [], g_parameter_info)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(g_c['return_type']))
    sys.exit(2)
  return(r_g)

################################################################
# gimbal wrapper dance
################################################################

def gimbal_argparse_to_dictionary(ai_g_args, ai_variant=0):
  """ convert a gimbal_argparse into a gimbal_dictionary
  """
  r_gd = {}
  ### inheritance from bell_bagel_assembly
  r_gd.update(bell_bagel_assembly.bba_argparse_to_dictionary(ai_g_args, 1))
  ### inheritance from cross_cube
  r_gd.update(cross_cube.cross_cube_argparse_to_dictionary(ai_g_args, 1))
  ### roll-pitch angles
  r_gd['bottom_angle']    = ai_g_args.sw_bottom_angle
  r_gd['top_angle']       = ai_g_args.sw_top_angle
  r_gd['pan_angle']       = ai_g_args.sw_pan_angle
  r_gd['tilt_angle']      = ai_g_args.sw_tilt_angle
  ### output
  if(ai_variant==0):
    #r_gd['tkinter_view']           = False
    r_gd['output_file_basename']   = ai_g_args.sw_output_file_basename
    #r_gd['args_in_txt'] = ""
    r_gd['return_type'] = ai_g_args.sw_return_type
  #### return
  return(r_gd)
  
def gimbal_argparse_wrapper(ai_g_args, ai_args_in_txt=""):
  """
  wrapper function of gimbal() to call it using the gimbal_parser.
  gimbal_parser is mostly used for debug and non-regression tests.
  """
  # view the gimbal with Tkinter as default action
  tkinter_view = True
  if(ai_g_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  gd = gimbal_argparse_to_dictionary(ai_g_args)
  gd['args_in_txt'] = ai_args_in_txt
  gd['tkinter_view'] = tkinter_view
  #gd['return_type'] = 'int_status'
  r_g = gimbal(gd)
  return(r_g)

################################################################
# self test
################################################################

def gimbal_self_test():
  """
  This is the non-regression test of gimbal.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , ""],
    ["bottom angle"        , "--bottom_angle 0.3"],
    ["top angle"        , "--top_angle -0.4"],
    ["both angle"        , "--bottom_angle -0.2 --top_angle 0.3"],
    ["pan-tilt"        , "--pan_angle 2.1 --tilt_angle 0.4"],
    ["outputfile" , "--output_file_basename test_output/gimbal_self_test.dxf"],
    ["last test"            , "--bottom_angle 0.1 --top_angle 0.2"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  gimbal_parser = argparse.ArgumentParser(description='Command line interface for the function gimbal().')
  gimbal_parser = gimbal_add_argument(gimbal_parser)
  gimbal_parser = cnc25d_api.generate_output_file_add_argument(gimbal_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = gimbal_parser.parse_args(l_args)
    r_gst = gimbal_argparse_wrapper(st_args)
  return(r_gst)

################################################################
# gimbal command line interface
################################################################

def gimbal_cli(ai_args=""):
  """ command line interface of gimbal.py when it is used in standalone
  """
  # gimbal parser
  gimbal_parser = argparse.ArgumentParser(description='Command line interface for the function gimbal().')
  gimbal_parser = gimbal_add_argument(gimbal_parser)
  gimbal_parser = cnc25d_api.generate_output_file_add_argument(gimbal_parser, 1)
  # switch for self_test
  gimbal_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display them in a Tk window.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "gimbal arguments: " + ' '.join(effective_args)
  g_args = gimbal_parser.parse_args(effective_args)
  print("dbg111: start making gimbal")
  if(g_args.sw_run_self_test):
    r_g = gimbal_self_test()
  else:
    r_g = gimbal_argparse_wrapper(g_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_g)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gimbal.py says hello!\n")
  my_g = gimbal_cli()
  #my_g = gimbal_cli("--bagel_extra_cut_thickness 1.0 --return_type freecad_object")
  #my_g = gimbal_cli("--bottom_angle 0.1 --top_angle 0.2 --return_type freecad_object")
  try: # depending on g_c['return_type'] it might be or not a freecad_object
    Part.show(my_g)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


