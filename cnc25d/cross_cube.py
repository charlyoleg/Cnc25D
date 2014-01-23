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
# cross_cube constraint_constructor
################################################################

def cross_cube_constraint_constructor(ai_parser, ai_variant=0):
  """
  Add arguments relative to the cross_cube
  """
  r_parser = ai_parser
  ### face A1, A2, B1 and B2 : inherited from crest
  i_crest = crest.crest()
  r_parser = i_crest.get_constraint_constructor()(r_parser, 1)
  ### top : inherited from cross_cube_sub
  r_parser = cross_cube_sub.cross_cube_sub_constraint_constructor(r_parser, 1)
  ### select crest on face
  r_parser.add_argument('--face_A1_crest','--fa1c', action='store_true', default=False,
    help="Replace the face_A1 with the crest. Default: False")
  r_parser.add_argument('--face_A2_crest','--fa2c', action='store_true', default=False,
    help="Replace the face_A2 with the crest. Default: False")
  r_parser.add_argument('--face_B1_crest','--fb1c', action='store_true', default=False,
    help="Replace the face_B1 with the crest. Default: False")
  r_parser.add_argument('--face_B2_crest','--fb2c', action='store_true', default=False,
    help="Replace the face_B2 with the crest. Default: False")
  ### output
  # return
  return(r_parser)

    
################################################################
# cross_cube constraint_check
################################################################

def cross_cube_constraint_check(c):
  """ check the cross_cube constraint c and set the dynamic default values
  """
  ### precision
  #radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  c = cross_cube_sub.cross_cube_sub_face_check(c)
  c = cross_cube_sub.cross_cube_sub_top_check(c)
  # rod stuff
  c['ftrr'] = 0.9*c['face_rod_hole_radius']
  c['ttrr'] = 0.9*c['top_rod_hole_radius']
  c['ar'] = 0.9*c['axle_radius']
  c['sr'] = c['spacer_radius']
  ###
  return(c)

################################################################
# cross_cube 2D-figures construction
################################################################

def cross_cube_2d_construction(c):
  """ construct the 2D-figures with outlines at the A-format for the cross_cube design
  """
  ### precision
  #radian_epsilon = math.pi/1000
  ###
  # alias
  fa1t = c['face_A1_thickness']
  fa2t = c['face_A2_thickness']
  fb1t = c['face_B1_thickness']
  fb2t = c['face_B2_thickness']
  ## face figure
  # face_A
  face_A = cnc25d_api.rotate_and_translate_figure(cross_cube_sub.cross_cube_face(c, fb1t, fb2t), c['cube_width']/2.0, c['cube_height']/2.0, 0.0, 0.0, 0.0)
  # face_B
  face_B = cnc25d_api.rotate_and_translate_figure(cross_cube_sub.cross_cube_face(c, fa2t, fa1t), c['cube_width']/2.0, c['cube_height']/2.0, math.pi, 0.0, 0.0)
  # crest
  i_crest = crest.crest()
  c_c = c.copy()
  c_c['face_B1_thickness'] = fb1t
  c_c['face_B2_thickness'] = fb2t
  i_crest.apply_external_constraint(c_c)
  crest_A = cnc25d_api.rotate_and_translate_figure(i_crest.get_A_figure('crest_fig'), c['cube_width']/2.0, c['cube_height']/2.0, math.pi, 0.0, 0.0)
  c_c['face_B1_thickness'] = fa2t
  c_c['face_B2_thickness'] = fa1t
  i_crest.apply_external_constraint(c_c)
  crest_B = cnc25d_api.rotate_and_translate_figure(i_crest.get_A_figure('crest_fig'), c['cube_width']/2.0, c['cube_height']/2.0, 0.0, 0.0, 0.0)

  ## top_figure
  top_figure = cross_cube_sub.cross_cube_top(c)


  ################################################################
  # output
  ################################################################


  ### figures output
  # part_list
  part_list = []
  part_list.append(face_A)
  part_list.append(crest_A)
  part_list.append(face_B)
  part_list.append(crest_B)
  part_list.append(top_figure)
  # part_list_figure
  x_space = 1.2*max(c['cube_width'], c['gear_module']*c['virtual_tooth_nb'])
  y_space = x_space
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## intermediate parameters
  ## sub-assembly
  ## cross_cube_part_overview
  cross_cube_part_overview_figure = []
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(face_A, 0.0, 0.0, 0.0, 1*x_space, 1*y_space))
  if(c['face_A1_crest'] or c['face_A2_crest']):
    cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(crest_A, 0.0, 0.0, 0.0, 1*x_space, 0*y_space))
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(face_B, 0.0, 0.0, 0.0, 0*x_space, 1*y_space))
  if(c['face_B1_crest'] or c['face_B2_crest']):
    cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(crest_B, 0.0, 0.0, 0.0, 0*x_space, 0*y_space))
  cross_cube_part_overview_figure.extend(cnc25d_api.rotate_and_translate_figure(top_figure, 0.0, 0.0, 0.0, 2*x_space, 1*y_space))
  ###
  face_threaded_rod = [(c['ftrr'], c['ftrr'], c['ftrr'])]
  top_threaded_rod = [(c['ttrr'], c['ttrr'], c['ttrr'])]
  axle = [(c['ar'], c['ar'], c['ar'])]
  spacer = [(c['sr'], c['sr'], c['sr'])]
  
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['face_A_fig'] = face_A
  r_height['face_A_fig'] = c['face_A1_thickness']
  #
  r_figures['crest_A_fig'] = crest_A
  r_height['crest_A_fig'] = c['face_A1_thickness']
  #
  r_figures['face_B_fig'] = face_B
  r_height['face_B_fig'] = c['face_B1_thickness']
  #
  r_figures['crest_B_fig'] = crest_B
  r_height['crest_B_fig'] = c['face_B1_thickness']
  #
  r_figures['top_fig'] = top_figure
  r_height['top_fig'] = c['top_thickness']
  #
  r_figures['cc_part_list'] = part_list_figure
  r_height['cc_part_list'] = 1.0
  #
  r_figures['cc_overview'] = cross_cube_part_overview_figure
  r_height['cc_overview'] = 1.0
  #
  r_figures['face_threaded_rod'] = face_threaded_rod
  r_height['face_threaded_rod'] = 1.0
  #
  r_figures['top_threaded_rod'] = top_threaded_rod
  r_height['top_threaded_rod'] = 1.0
  #
  r_figures['axle'] = axle
  r_height['axle'] = 1.0
  #
  r_figures['spacer'] = spacer
  r_height['spacer'] = 1.0
  ###
  return((r_figures, r_height))

################################################################
# cross_cube crest-gear simulation
################################################################

def crest_simulation_A(c):
  """ define the crest simulation
  """
  # inherit from gear_profile
  i_crest = crest.crest()
  i_crest.apply_external_constraint(c)
  i_crest.run_simulation('crest_simulation_A')
  return(1)

def cross_cube_2d_simulations():
  """ return the dictionary defining the available simulation for cross_cube
  """
  r_sim = {}
  r_sim['crest_simulation_A'] = crest_simulation_A
  return(r_sim)

################################################################
# cross_cube 3D assembly-configuration construction
################################################################

def cross_cube_3d_construction(c):
  """ construct the 3D-assembly-configurations of the cross_cube
  """
  ### freecad-object assembly configuration
  # intermediate parameters
  x1 = 0
  x2 = c['cube_width'] - c['face_B2_thickness']
  y1 = 0
  y2 = c['cube_width'] - c['face_A2_thickness']
  z1 = 0
  z2 = c['cube_height'] - c['top_thickness']
  # face selection
  if(c['face_A1_crest']):
    slot_A1 = 'crest_A_fig'
  else:
    slot_A1 = 'face_A_fig'
  if(c['face_A2_crest']):
    slot_A2 = 'crest_A_fig'
  else:
    slot_A2 = 'face_A_fig'
  if(c['face_B1_crest']):
    slot_B1 = 'crest_B_fig'
  else:
    slot_B1 = 'face_B_fig'
  if(c['face_B2_crest']):
    slot_B2 = 'crest_B_fig'
  else:
    slot_B2 = 'face_B_fig'
  # conf1a
  cross_cube_assembly_conf1a = []
  cross_cube_assembly_conf1a.append((slot_A1, 0, 0, c['cube_width'], c['cube_height'], c['face_A1_thickness'], 'i', 'xz', x1, y1, z1))
  cross_cube_assembly_conf1a.append((slot_B1, 0, 0, c['cube_width'], c['cube_height'], c['face_B1_thickness'], 'i', 'yz', x1, y1, z1))
  cross_cube_assembly_conf1a.append(('top_fig', 0, 0, c['cube_width'], c['cube_width'], c['top_thickness'], 'i', 'xy', x1, y1, z1))
  # conf1b
  cross_cube_assembly_conf1b = []
  cross_cube_assembly_conf1b.append((slot_A2, 0, 0, c['cube_width'], c['cube_height'], c['face_A2_thickness'], 'i', 'xz', x1, y2, z1))
  cross_cube_assembly_conf1b.append((slot_B2, 0, 0, c['cube_width'], c['cube_height'], c['face_B2_thickness'], 'i', 'yz', x2, y1, z1))
  cross_cube_assembly_conf1b.append(('top_fig', 0, 0, c['cube_width'], c['cube_width'], c['top_thickness'], 'i', 'xy', x1, y1, z2))
  # conf1
  cross_cube_assembly_conf1 = []
  cross_cube_assembly_conf1.extend(cross_cube_assembly_conf1a)
  cross_cube_assembly_conf1.extend(cross_cube_assembly_conf1b)
  # conf2a : threaded rod
  fatrx = (c['face_B1_thickness']+c['face_rod_hole_h_position']-c['ftrr'], c['cube_width']-(c['face_B2_thickness']+c['face_rod_hole_h_position'])-c['ftrr'])
  fatry = -0.1*c['cube_width']
  fatrz = (c['top_thickness']+c['face_rod_hole_v_position']+c['face_rod_hole_v_distance']-c['ftrr'], c['cube_height']-(c['top_thickness']+c['face_rod_hole_v_position'])-c['ftrr'])
  fbtrx = -0.1*c['cube_width']
  fbtry = (c['face_A1_thickness']+c['face_rod_hole_h_position']-c['ftrr'], c['cube_width']-(c['face_A2_thickness']+c['face_rod_hole_h_position'])-c['ftrr'])
  fbtrz = (c['top_thickness']+1*c['face_rod_hole_v_position']-c['ftrr'], c['cube_height']-(c['top_thickness']+c['face_rod_hole_v_position']+c['face_rod_hole_v_distance'])-c['ftrr'])
  ttrx = (c['face_B1_thickness']+c['top_rod_hole_h_position']-c['ttrr'], c['cube_width']-(c['face_B2_thickness']+c['top_rod_hole_h_position'])-c['ttrr'])
  ttry = (c['face_A1_thickness']+c['top_rod_hole_h_position']-c['ttrr'], c['cube_width']-(c['face_A2_thickness']+c['top_rod_hole_h_position'])-c['ttrr'])
  ttrz = -0.1*c['cube_height']
  cross_cube_assembly_conf2a = []
  if(c['face_rod_hole_radius']>0):
    cross_cube_assembly_conf2a.append(('face_threaded_rod', 0, 0, 2*c['ftrr'], 2*c['ftrr'], 1.2*c['cube_width'], 'i', 'xz', fatrx[0], fatry, fatrz[0])) # threaded rod on face_A
    cross_cube_assembly_conf2a.append(('face_threaded_rod', 0, 0, 2*c['ftrr'], 2*c['ftrr'], 1.2*c['cube_width'], 'i', 'xz', fatrx[1], fatry, fatrz[0]))
    cross_cube_assembly_conf2a.append(('face_threaded_rod', 0, 0, 2*c['ftrr'], 2*c['ftrr'], 1.2*c['cube_width'], 'i', 'xz', fatrx[1], fatry, fatrz[1]))
    cross_cube_assembly_conf2a.append(('face_threaded_rod', 0, 0, 2*c['ftrr'], 2*c['ftrr'], 1.2*c['cube_width'], 'i', 'xz', fatrx[0], fatry, fatrz[1]))
    cross_cube_assembly_conf2a.append(('face_threaded_rod', 0, 0, 2*c['ftrr'], 2*c['ftrr'], 1.2*c['cube_width'], 'i', 'yz', fbtrx, fbtry[0], fbtrz[0])) # threaded rod on face_B
    cross_cube_assembly_conf2a.append(('face_threaded_rod', 0, 0, 2*c['ftrr'], 2*c['ftrr'], 1.2*c['cube_width'], 'i', 'yz', fbtrx, fbtry[1], fbtrz[0]))
    cross_cube_assembly_conf2a.append(('face_threaded_rod', 0, 0, 2*c['ftrr'], 2*c['ftrr'], 1.2*c['cube_width'], 'i', 'yz', fbtrx, fbtry[1], fbtrz[1]))
    cross_cube_assembly_conf2a.append(('face_threaded_rod', 0, 0, 2*c['ftrr'], 2*c['ftrr'], 1.2*c['cube_width'], 'i', 'yz', fbtrx, fbtry[0], fbtrz[1]))
  if(c['top_rod_hole_radius']>0):
    cross_cube_assembly_conf2a.append(('top_threaded_rod', 0, 0, 2*c['ttrr'], 2*c['ttrr'], 1.2*c['cube_height'], 'i', 'xy', ttrx[0], ttry[0], ttrz)) # threaded rod on top
    cross_cube_assembly_conf2a.append(('top_threaded_rod', 0, 0, 2*c['ttrr'], 2*c['ttrr'], 1.2*c['cube_height'], 'i', 'xy', ttrx[1], ttry[0], ttrz))
    cross_cube_assembly_conf2a.append(('top_threaded_rod', 0, 0, 2*c['ttrr'], 2*c['ttrr'], 1.2*c['cube_height'], 'i', 'xy', ttrx[1], ttry[1], ttrz))
    cross_cube_assembly_conf2a.append(('top_threaded_rod', 0, 0, 2*c['ttrr'], 2*c['ttrr'], 1.2*c['cube_height'], 'i', 'xy', ttrx[0], ttry[1], ttrz))
  # conf2b : axles
  cross_cube_assembly_conf2b = []
  ax = c['cube_width']/2.0-c['ar']
  ay = -1*(c['axle_length']-c['cube_width'])/2.0
  az1 = c['top_thickness'] + c['height_margin'] + c['axle_radius']-c['ar']
  az2 = c['cube_height']-(c['top_thickness'] + c['height_margin'] + c['axle_radius'])-c['ar']
  sx = c['cube_width']/2.0-c['sr']
  sy1 = -1*c['spacer_length']
  sy2 = c['cube_width']
  sz1 = c['top_thickness'] + c['height_margin'] + c['axle_radius']-c['sr']
  sz2 = c['cube_height']-(c['top_thickness'] + c['height_margin'] + c['axle_radius'])-c['sr']
  if(c['axle_radius']>0):
    cross_cube_assembly_conf2b.append(('axle', 0, 0, 2*c['ar'], 2*c['ar'], c['axle_length'], 'i', 'xz', ax, ay, az1))
    cross_cube_assembly_conf2b.append(('axle', 0, 0, 2*c['ar'], 2*c['ar'], c['axle_length'], 'i', 'yz', ay, ax, az2))
  if(c['spacer_radius']>0):
    cross_cube_assembly_conf2b.append(('spacer', 0, 0, 2*c['sr'], 2*c['sr'], c['spacer_length'], 'i', 'xz', sx, sy1, sz1))
    cross_cube_assembly_conf2b.append(('spacer', 0, 0, 2*c['sr'], 2*c['sr'], c['spacer_length'], 'i', 'xz', sx, sy2, sz1))
    cross_cube_assembly_conf2b.append(('spacer', 0, 0, 2*c['sr'], 2*c['sr'], c['spacer_length'], 'i', 'yz', sy1, sx, sz2))
    cross_cube_assembly_conf2b.append(('spacer', 0, 0, 2*c['sr'], 2*c['sr'], c['spacer_length'], 'i', 'yz', sy2, sx, sz2))
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

  size_xyz = (c['axle_length'], c['axle_length'], c['cube_height'])
  zero_xyz = (-1*(c['axle_length']-c['cube_width'])/2.0, -1*(c['axle_length']-c['cube_width'])/2.0, 0)
  slice_x = [ (i+1)/11.0*size_xyz[0] for i in range(10) ]
  slice_y = [ (i+1)/11.0*size_xyz[1] for i in range(10) ]
  slice_z = [ (i+1)/11.0*size_xyz[2] for i in range(10) ]
  slice_xyz = (size_xyz[0], size_xyz[1], size_xyz[2], zero_xyz[0], zero_xyz[1], zero_xyz[2], slice_z, slice_y, slice_x)
  #
  #
  r_assembly = {}
  r_slice = {}
  #
  r_assembly['cross_cube_bare_assembly'] = cross_cube_assembly_conf1
  r_slice['cross_cube_bare_assembly'] = ()
  #
  r_assembly['cross_cube_open_assembly_with_rods_and_axles'] = cross_cube_assembly_conf2
  r_slice['cross_cube_open_assembly_with_rods_and_axles'] = ()
  #
  r_assembly['cross_cube_assembly_with_rods_and_axles'] = cross_cube_assembly_conf3
  r_slice['cross_cube_assembly_with_rods_and_axles'] = slice_xyz
  #
  return((r_assembly, r_slice))

################################################################
# cross_cube_info
################################################################

def cross_cube_info(c):
  """ create the text info related to the cross_cube design
  """
  r_info = ""
  i_crest = crest.crest()
  i_crest.apply_external_constraint(c)
  r_info += i_crest.get_info()
  r_info += cross_cube_sub.cross_cube_top_parameter_info(c)
  r_info += """
crest on faces:
face_A1_crest:      {:d}
face_A2_crest:      {:d}
face_B1_crest:      {:d}
face_B2_crest:      {:d}
""".format(c['face_A1_crest'], c['face_A2_crest'], c['face_B1_crest'], c['face_B2_crest'])
  #print("dbg552: r_info: {:s}".format(r_info))
  return(r_info)

################################################################
# self test
################################################################

def cross_cube_self_test():
  """
  This is the non-regression test of cross_cube.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , ""],
    ["extra cut" , "--cross_cube_extra_cut_thickness 1.0"],
    ["extra cut negative" , "--cross_cube_extra_cut_thickness -2.0"],
    ["one crest" , "--face_A1_crest"],
    ["two crests" , "--face_A1_crest --face_B1_crest"],
    ["double crests on A" , "--face_A1_crest --face_A2_crest"],
    ["outputfile" , "--output_file_basename test_output/cross_cube_self_test.dxf"],
    ["last test"            , ""]]
  return(r_tests)

################################################################
# cross_cube design declaration
################################################################

class cross_cube(cnc25d_api.bare_design):
  """ cross_cube design
  """
  def __init__(self, constraint={}):
    """ configure the cross_cube design
    """
    self.design_setup(
      s_design_name             = "cross_cube_design",
      f_constraint_constructor  = cross_cube_constraint_constructor,
      f_constraint_check        = cross_cube_constraint_check,
      f_2d_constructor          = cross_cube_2d_construction,
      d_2d_simulation           = cross_cube_2d_simulations(),
      f_3d_constructor          = cross_cube_3d_construction,
      f_info                    = cross_cube_info,
      l_display_figure_list     = ['cc_overview'],
      s_default_simulation      = "",
      l_2d_figure_file_list     = [], # all figures
      l_3d_figure_file_list     = ['face_A_fig', 'crest_A_fig', 'face_B_fig', 'crest_B_fig', 'top_fig'],
      l_3d_conf_file_list       = [], # all 3d-conf
      f_cli_return_type         = None,
      l_self_test_list          = cross_cube_self_test())
    self.apply_constraint(constraint)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("cross_cube.py says hello!\n")
  my_cc = cross_cube()
  #my_cc.cli()
  #my_cc.cli("--cross_cube_extra_cut_thickness 1.0")
  my_cc.cli("--cross_cube_extra_cut_thickness 1.0 --face_A1_crest --face_B1_crest")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_cc.get_fc_obj('cross_cube_bare_assembly'))


