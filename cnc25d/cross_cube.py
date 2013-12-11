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
import cross_cube_sub
import crest

################################################################
# cross_cube dictionary-arguments default values
################################################################

def cross_cube_dictionary_init(ai_variant=0):
  """ create and initiate a cross_cube dictionary with the default value
  """
  r_cc = {}
  ### face A1, A2, B1 and B2 : inherited from crest
  r_cc.update(crest.crest_dictionary_init(1))
  ### top : inherited from cross_cube_sub
  r_cc.update(cross_cube_sub.cross_cube_sub_dictionary_init(1))
  ### select crest on face
  r_cc['face_A1_crest'] = True
  r_cc['face_A2_crest'] = False
  r_cc['face_B1_crest'] = True
  r_cc['face_B2_crest'] = False
  ### output
  if(ai_variant==0):
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
  ### face A1, A2, B1 and B2 : inherited from crest
  r_parser = crest.crest_add_argument(r_parser, 1)
  ### top : inherited from cross_cube_sub
  r_parser = cross_cube_sub.cross_cube_sub_add_argument(r_parser, 1)
  ### select crest on face
  r_parser.add_argument('--face_A1_crest','--fa1c', action='store_true', default=False, dest='sw_face_A1_crest',
    help="Replace the face_A1 with the crest. Default: False")
  r_parser.add_argument('--face_A2_crest','--fa2c', action='store_true', default=False, dest='sw_face_A2_crest',
    help="Replace the face_A2 with the crest. Default: False")
  r_parser.add_argument('--face_B1_crest','--fb1c', action='store_true', default=False, dest='sw_face_B1_crest',
    help="Replace the face_B1 with the crest. Default: False")
  r_parser.add_argument('--face_B2_crest','--fb2c', action='store_true', default=False, dest='sw_face_B2_crest',
    help="Replace the face_B2 with the crest. Default: False")
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
    print("ERR127: Error, cc_c has too much entries as {:s} or missing entries as {:s}".format(cc_c.viewkeys() - ccdi.viewkeys(), ccdi.viewkeys() - cc_c.viewkeys()))
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
  cc_c = cross_cube_sub.check_cross_cube_face_parameters(cc_c)
  cc_c = cross_cube_sub.check_cross_cube_top_parameters(cc_c)

  ################################################################
  # outline construction
  ################################################################
  # alias
  fa1t = cc_c['face_A1_thickness']
  fa2t = cc_c['face_A2_thickness']
  fb1t = cc_c['face_B1_thickness']
  fb2t = cc_c['face_B2_thickness']
  ## face figure
  # face_A
  face_A_rotated = cnc25d_api.rotate_and_translate_figure(cross_cube_sub.cross_cube_face(cc_c, fb1t, fb2t), cc_c['cube_width']/2.0, cc_c['cube_height']/2.0, 0.0, 0.0, 0.0)
  face_A = cnc25d_api.cnc_cut_figure(face_A_rotated, "face_A")
  face_A_overlay = cnc25d_api.ideal_figure(face_A_rotated, "face_A")
  # face_B
  face_B_rotated = cnc25d_api.rotate_and_translate_figure(cross_cube_sub.cross_cube_face(cc_c, fa2t, fa1t), cc_c['cube_width']/2.0, cc_c['cube_height']/2.0, math.pi, 0.0, 0.0)
  face_B = cnc25d_api.cnc_cut_figure(face_B_rotated, "face_B")
  face_B_overlay = cnc25d_api.ideal_figure(face_B_rotated, "face_B")
  # crest
  c_ci = crest.crest_dictionary_init(1)
  c_c = dict([ (k, cc_c[k]) for k in c_ci.viewkeys() & ccdi.viewkeys() ]) # extract only the entries of the intersection of cross_cube and crest
  c_c['tkinter_view'] = False
  c_c['output_file_basename'] = ''
  c_c['args_in_txt'] = "crest for cross_cube"
  c_c['return_type'] = 'figures_3dconf_info' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  c_c['face_B1_thickness'] = fb1t
  c_c['face_B2_thickness'] = fb2t
  (crest_parts, crest_3d_conf,  crest_parameter_info1) = crest.crest(c_c)
  crest_A = cnc25d_api.rotate_and_translate_figure(crest_parts[0], cc_c['cube_width']/2.0, cc_c['cube_height']/2.0, math.pi, 0.0, 0.0)
  c_c['face_B1_thickness'] = fa2t
  c_c['face_B2_thickness'] = fa1t
  (crest_parts, crest_3d_conf,  crest_parameter_info2) = crest.crest(c_c)
  crest_B = cnc25d_api.rotate_and_translate_figure(crest_parts[0], cc_c['cube_width']/2.0, cc_c['cube_height']/2.0, 0.0, 0.0, 0.0)

  ## top_figure
  top_A = cross_cube_sub.cross_cube_top(cc_c)
  top_figure = cnc25d_api.cnc_cut_figure(top_A, "top_figure")
  top_figure_overlay = cnc25d_api.ideal_figure(top_A, "top_figure")


  ################################################################
  # output
  ################################################################

  # cc_parameter_info
  cc_parameter_info = "\ncross_cube parameter info:\n"
  cc_parameter_info += "\n" + cc_c['args_in_txt'] + "\n"
  cc_parameter_info += crest_parameter_info1
  cc_parameter_info += cross_cube_sub.cross_cube_top_parameter_info(cc_c)
  cc_parameter_info += """
crest on faces:
face_A1_crest:      {:d}
face_A2_crest:      {:d}
face_B1_crest:      {:d}
face_B2_crest:      {:d}
""".format(cc_c['face_A1_crest'], cc_c['face_A2_crest'], cc_c['face_B1_crest'], cc_c['face_B2_crest'])
  #print("dbg552: cc_parameter_info: {:s}".format(cc_parameter_info))

  ### figures output
  # part_list
  part_list = []
  part_list.append(face_A)
  part_list.append(crest_A)
  part_list.append(face_B)
  part_list.append(crest_B)
  part_list.append(top_figure)
  # part_list_figure
  x_space = 1.2*max(cc_c['cube_width'], cc_c['gear_module']*cc_c['virtual_tooth_nb'])
  y_space = x_space
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## intermediate parameters
  ## sub-assembly
  ## cross_cube_part_overview
  cross_cube_part_overview_figure = []
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(face_A, 0.0, 0.0, 0.0, 1*x_space, 1*y_space))
  if(cc_c['face_A1_crest'] or cc_c['face_A2_crest']):
    cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(crest_A, 0.0, 0.0, 0.0, 1*x_space, 0*y_space))
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(face_B, 0.0, 0.0, 0.0, 0*x_space, 1*y_space))
  if(cc_c['face_B1_crest'] or cc_c['face_B2_crest']):
    cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(crest_B, 0.0, 0.0, 0.0, 0*x_space, 0*y_space))
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(top_figure, 0.0, 0.0, 0.0, 2*x_space, 1*y_space))
  cross_cube_part_overview_figure_overlay = []
  cross_cube_part_overview_figure_overlay.extend(cnc25d_api.rotate_and_translate_figure(face_A_overlay, 0.0, 0.0, 0.0, 1*x_space, 1*y_space))
  cross_cube_part_overview_figure_overlay.extend(cnc25d_api.rotate_and_translate_figure(face_B_overlay, 0.0, 0.0, 0.0, 0*x_space, 1*y_space))
  cross_cube_part_overview_figure_overlay.extend(cnc25d_api.rotate_and_translate_figure(top_figure_overlay, 0.0, 0.0, 0.0, 2*x_space, 1*y_space))

  ### freecad-object assembly configuration
  # intermediate parameters
  x1 = 0
  x2 = cc_c['cube_width'] - cc_c['face_B2_thickness']
  y1 = 0
  y2 = cc_c['cube_width'] - cc_c['face_A2_thickness']
  z1 = 0
  z2 = cc_c['cube_height'] - cc_c['top_thickness']
  # face selection
  if(cc_c['face_A1_crest']):
    slot_A1 = crest_A
  else:
    slot_A1 = face_A
  if(cc_c['face_A2_crest']):
    slot_A2 = crest_A
  else:
    slot_A2 = face_A
  if(cc_c['face_B1_crest']):
    slot_B1 = crest_B
  else:
    slot_B1 = face_B
  if(cc_c['face_B2_crest']):
    slot_B2 = crest_B
  else:
    slot_B2 = face_B
  # conf1a
  cross_cube_assembly_conf1a = []
  cross_cube_assembly_conf1a.append((slot_A1, 0, 0, cc_c['cube_width'], cc_c['cube_height'], cc_c['face_A1_thickness'], 'i', 'xz', x1, y1, z1))
  cross_cube_assembly_conf1a.append((slot_B1, 0, 0, cc_c['cube_width'], cc_c['cube_height'], cc_c['face_B1_thickness'], 'i', 'yz', x1, y1, z1))
  cross_cube_assembly_conf1a.append((top_figure, 0, 0, cc_c['cube_width'], cc_c['cube_width'], cc_c['top_thickness'], 'i', 'xy', x1, y1, z1))
  # conf1b
  cross_cube_assembly_conf1b = []
  cross_cube_assembly_conf1b.append((slot_A2, 0, 0, cc_c['cube_width'], cc_c['cube_height'], cc_c['face_A2_thickness'], 'i', 'xz', x1, y2, z1))
  cross_cube_assembly_conf1b.append((slot_B2, 0, 0, cc_c['cube_width'], cc_c['cube_height'], cc_c['face_B2_thickness'], 'i', 'yz', x2, y1, z1))
  cross_cube_assembly_conf1b.append((top_figure, 0, 0, cc_c['cube_width'], cc_c['cube_width'], cc_c['top_thickness'], 'i', 'xy', x1, y1, z2))
  # conf1
  cross_cube_assembly_conf1 = []
  cross_cube_assembly_conf1.extend(cross_cube_assembly_conf1a)
  cross_cube_assembly_conf1.extend(cross_cube_assembly_conf1b)
  # conf2a : threaded rod
  ftrr = 0.9*cc_c['face_rod_hole_radius']
  face_threaded_rod = [(ftrr, ftrr, ftrr)]
  ttrr = 0.9*cc_c['top_rod_hole_radius']
  top_threaded_rod = [(ttrr, ttrr, ttrr)]
  fatrx = (cc_c['face_B1_thickness']+cc_c['face_rod_hole_h_distance']-ftrr, cc_c['cube_width']-(cc_c['face_B2_thickness']+cc_c['face_rod_hole_h_distance'])-ftrr)
  fatry = -0.1*cc_c['cube_width']
  fatrz = (cc_c['top_thickness']+2*cc_c['face_rod_hole_v_distance']-ftrr, cc_c['cube_height']-(cc_c['top_thickness']+cc_c['face_rod_hole_v_distance'])-ftrr)
  fbtrx = -0.1*cc_c['cube_width']
  fbtry = (cc_c['face_A1_thickness']+cc_c['face_rod_hole_h_distance']-ftrr, cc_c['cube_width']-(cc_c['face_A2_thickness']+cc_c['face_rod_hole_h_distance'])-ftrr)
  fbtrz = (cc_c['top_thickness']+1*cc_c['face_rod_hole_v_distance']-ftrr, cc_c['cube_height']-(cc_c['top_thickness']+2*cc_c['face_rod_hole_v_distance'])-ftrr)
  ttrx = (cc_c['face_B1_thickness']+cc_c['top_rod_hole_h_distance']-ttrr, cc_c['cube_width']-(cc_c['face_B2_thickness']+cc_c['top_rod_hole_h_distance'])-ttrr)
  ttry = (cc_c['face_A1_thickness']+cc_c['top_rod_hole_h_distance']-ttrr, cc_c['cube_width']-(cc_c['face_A2_thickness']+cc_c['top_rod_hole_h_distance'])-ttrr)
  ttrz = -0.1*cc_c['cube_height']
  cross_cube_assembly_conf2a = []
  if(cc_c['face_rod_hole_radius']>0):
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, 2*ftrr, 2*ftrr, 1.2*cc_c['cube_width'], 'i', 'xz', fatrx[0], fatry, fatrz[0])) # threaded rod on face_A
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, 2*ftrr, 2*ftrr, 1.2*cc_c['cube_width'], 'i', 'xz', fatrx[1], fatry, fatrz[0]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, 2*ftrr, 2*ftrr, 1.2*cc_c['cube_width'], 'i', 'xz', fatrx[1], fatry, fatrz[1]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, 2*ftrr, 2*ftrr, 1.2*cc_c['cube_width'], 'i', 'xz', fatrx[0], fatry, fatrz[1]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, 2*ftrr, 2*ftrr, 1.2*cc_c['cube_width'], 'i', 'yz', fbtrx, fbtry[0], fbtrz[0])) # threaded rod on face_B
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, 2*ftrr, 2*ftrr, 1.2*cc_c['cube_width'], 'i', 'yz', fbtrx, fbtry[1], fbtrz[0]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, 2*ftrr, 2*ftrr, 1.2*cc_c['cube_width'], 'i', 'yz', fbtrx, fbtry[1], fbtrz[1]))
    cross_cube_assembly_conf2a.append((face_threaded_rod, 0, 0, 2*ftrr, 2*ftrr, 1.2*cc_c['cube_width'], 'i', 'yz', fbtrx, fbtry[0], fbtrz[1]))
  if(cc_c['top_rod_hole_radius']>0):
    cross_cube_assembly_conf2a.append((top_threaded_rod, 0, 0, 2*ttrr, 2*ttrr, 1.2*cc_c['cube_height'], 'i', 'xy', ttrx[0], ttry[0], ttrz)) # threaded rod on top
    cross_cube_assembly_conf2a.append((top_threaded_rod, 0, 0, 2*ttrr, 2*ttrr, 1.2*cc_c['cube_height'], 'i', 'xy', ttrx[1], ttry[0], ttrz))
    cross_cube_assembly_conf2a.append((top_threaded_rod, 0, 0, 2*ttrr, 2*ttrr, 1.2*cc_c['cube_height'], 'i', 'xy', ttrx[1], ttry[1], ttrz))
    cross_cube_assembly_conf2a.append((top_threaded_rod, 0, 0, 2*ttrr, 2*ttrr, 1.2*cc_c['cube_height'], 'i', 'xy', ttrx[0], ttry[1], ttrz))
  # conf2b : axles
  cross_cube_assembly_conf2b = []
  ar = 0.9*cc_c['axle_radius']
  axle = [(ar, ar, ar)]
  sr = cc_c['spacer_radius']
  spacer = [(sr, sr, sr)]
  ax = cc_c['cube_width']/2.0-ar
  ay = -1*(cc_c['axle_length']-cc_c['cube_width'])/2.0
  az1 = cc_c['top_thickness'] + cc_c['height_margin'] + cc_c['axle_radius']-ar
  az2 = cc_c['cube_height']-(cc_c['top_thickness'] + cc_c['height_margin'] + cc_c['axle_radius'])-ar
  sx = cc_c['cube_width']/2.0-sr
  sy1 = -1*cc_c['spacer_length']
  sy2 = cc_c['cube_width']
  sz1 = cc_c['top_thickness'] + cc_c['height_margin'] + cc_c['axle_radius']-sr
  sz2 = cc_c['cube_height']-(cc_c['top_thickness'] + cc_c['height_margin'] + cc_c['axle_radius'])-sr
  if(cc_c['axle_radius']>0):
    cross_cube_assembly_conf2b.append((axle, 0, 0, 2*ar, 2*ar, cc_c['axle_length'], 'i', 'xz', ax, ay, az1))
    cross_cube_assembly_conf2b.append((axle, 0, 0, 2*ar, 2*ar, cc_c['axle_length'], 'i', 'yz', ay, ax, az2))
  if(cc_c['spacer_radius']>0):
    cross_cube_assembly_conf2b.append((spacer, 0, 0, 2*sr, 2*sr, cc_c['spacer_length'], 'i', 'xz', sx, sy1, sz1))
    cross_cube_assembly_conf2b.append((spacer, 0, 0, 2*sr, 2*sr, cc_c['spacer_length'], 'i', 'xz', sx, sy2, sz1))
    cross_cube_assembly_conf2b.append((spacer, 0, 0, 2*sr, 2*sr, cc_c['spacer_length'], 'i', 'yz', sy1, sx, sz2))
    cross_cube_assembly_conf2b.append((spacer, 0, 0, 2*sr, 2*sr, cc_c['spacer_length'], 'i', 'yz', sy2, sx, sz2))
  # conf2
  cross_cube_assembly_conf2 = []
  cross_cube_assembly_conf2.extend(cross_cube_assembly_conf1a)
  cross_cube_assembly_conf2.extend(cross_cube_assembly_conf2a)
  cross_cube_assembly_conf2.extend(cross_cube_assembly_conf2b)
  # conf3
  cross_cube_assembly_conf3 = []
  cross_cube_assembly_conf3.extend(cross_cube_assembly_conf2)
  cross_cube_assembly_conf3.extend(cross_cube_assembly_conf1b)
  #print("dbg635: cross_cube_assembly_conf3:", cross_cube_assembly_conf3)

  ### display with Tkinter
  if(cc_c['tkinter_view']):
    print(cc_parameter_info)
    cnc25d_api.figure_simple_display(cross_cube_part_overview_figure, cross_cube_part_overview_figure_overlay, cc_parameter_info)

  ### generate output file
  if(cc_c['output_file_basename']!=''):
    (output_file_basename, output_file_suffix) = cnc25d_api.get_output_file_suffix(cc_c['output_file_basename'])
    # parts
    cnc25d_api.generate_output_file(face_A, output_file_basename + "_face_A" + output_file_suffix, cc_c['face_A1_thickness'], cc_parameter_info)
    if(cc_c['face_A1_crest'] or cc_c['face_A2_crest']):
      cnc25d_api.generate_output_file(crest_A, output_file_basename + "_crest_A" + output_file_suffix, cc_c['face_A1_thickness'], cc_parameter_info)
    cnc25d_api.generate_output_file(face_B, output_file_basename + "_face_B" + output_file_suffix, cc_c['face_B1_thickness'], cc_parameter_info)
    if(cc_c['face_B1_crest'] or cc_c['face_B2_crest']):
      cnc25d_api.generate_output_file(crest_B, output_file_basename + "_crest_B" + output_file_suffix, cc_c['face_B1_thickness'], cc_parameter_info)
    cnc25d_api.generate_output_file(top_figure, output_file_basename + "_top" + output_file_suffix, cc_c['top_thickness'], cc_parameter_info)
    # assembly
    if((output_file_suffix=='.svg')or(output_file_suffix=='.dxf')):
      cnc25d_api.generate_output_file(part_list_figure, output_file_basename + "_part_list" + output_file_suffix, 1.0, cc_parameter_info)
      cnc25d_api.generate_output_file(cross_cube_part_overview_figure, output_file_basename + "_part_overview" + output_file_suffix, 1.0, cc_parameter_info)
    else:
      size_xyz = (cc_c['axle_length'], cc_c['axle_length'], cc_c['cube_height'])
      zero_xyz = (-1*(cc_c['axle_length']-cc_c['cube_width'])/2.0, -1*(cc_c['axle_length']-cc_c['cube_width'])/2.0, 0)
      slice_x = [ (i+1)/11.0*size_xyz[0] for i in range(10) ]
      slice_y = [ (i+1)/11.0*size_xyz[1] for i in range(10) ]
      slice_z = [ (i+1)/11.0*size_xyz[2] for i in range(10) ]
      slice_xyz = (size_xyz[0], size_xyz[1], size_xyz[2], zero_xyz[0], zero_xyz[1], zero_xyz[2], slice_z, slice_y, slice_x)
      cnc25d_api.generate_3d_assembly_output_file(cross_cube_assembly_conf1, output_file_basename + "_bare_assembly", True, False, [])
      cnc25d_api.generate_3d_assembly_output_file(cross_cube_assembly_conf2, output_file_basename + "_open_assembly_with_rods_and_axles", True, False, [])
      cnc25d_api.generate_3d_assembly_output_file(cross_cube_assembly_conf3, output_file_basename + "_assembly_with_rods_and_axles", True, False, slice_xyz)

  #### return
  if(cc_c['return_type']=='int_status'):
    r_cc = 1
  elif(cc_c['return_type']=='cnc25d_figure'):
    r_cc = part_list
  elif(cc_c['return_type']=='freecad_object'):
    r_cc = cnc25d_api.figures_to_freecad_assembly(cross_cube_assembly_conf3)
  elif(cc_c['return_type']=='freecad_object2'):
    r_cc = cnc25d_api.figures_to_freecad_assembly(cross_cube_assembly_conf2)
  elif(cc_c['return_type']=='figures_3dconf_info'):
    r_cc = (part_list, cross_cube_assembly_conf3, cc_parameter_info)
  #elif(cc_c['return_type']=='outlines_for_crest'): # vestige of before cross_cube_sub
  #  r_cc = (bottom_outline_A, cross_cube_hole_figure_A, cc_parameter_info)
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
  ### face A1, A2, B1 and B2 : inherited from crest
  r_ccd.update(crest.crest_argparse_to_dictionary(ai_cc_args, 1))
  ### top : inherited from cross_cube_sub
  r_ccd.update(cross_cube_sub.cross_cube_sub_argparse_to_dictionary(ai_cc_args, 1))
  ### select crest on face
  r_ccd['face_A1_crest']  = ai_cc_args.sw_face_A1_crest
  r_ccd['face_A2_crest']  = ai_cc_args.sw_face_A2_crest
  r_ccd['face_B1_crest']  = ai_cc_args.sw_face_B1_crest
  r_ccd['face_B2_crest']  = ai_cc_args.sw_face_B2_crest
  ### output
  if(ai_variant==0):
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
    ["one crest" , "--face_A1_crest"],
    ["two crests" , "--face_A1_crest --face_B1_crest"],
    ["double crests on A" , "--face_A1_crest --face_A2_crest"],
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
  my_cc = cross_cube_cli()
  #my_cc = cross_cube_cli("--cross_cube_extra_cut_thickness 1.0 --return_type freecad_object2")
  #my_cc = cross_cube_cli("--cross_cube_extra_cut_thickness 1.0 --return_type freecad_object --face_A1_crest --face_B1_crest")
  try: # depending on cc_c['return_type'] it might be or not a freecad_object
    Part.show(my_cc)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


