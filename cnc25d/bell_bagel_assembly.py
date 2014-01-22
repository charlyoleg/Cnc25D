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
# inheritance from designs bell and bagel
################################################################

def inherit_bell(c={}):
  """ generate the design bell with the construct c
  """
  r_obj = bell.bell()
  r_obj.apply_external_constraint(c)
  return(r_obj)

def inherit_bagel(c={}):
  """ generate the design bagel with the construct c
  """
  lc = c.copy()
  if(len(c)>0):
    lc['middle_bagel_thickness'] = c['face_thickness']
    lc['axle_hole_nb'] = c['axle_hole_nb']
    lc['axle_hole_diameter'] = c['axle_hole_diameter']
    lc['axle_hole_position_diameter'] = c['axle_hole_position_diameter']
    lc['axle_hole_angle'] = c['axle_hole_angle']
  r_obj = bagel.bagel()
  r_obj.apply_external_constraint(c)
  return(r_obj)

################################################################
# bell_bagel_assembly constraint_constructor
################################################################

def bba_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the bell_bagel_assembly
  """
  r_parser = ai_parser
  ### heritage from bell
  i_bell = inherit_bell()
  r_parser = i_bell.get_constraint_constructor()(r_parser, 1)
  #r_parser = bell.bell_constraint_constructor(r_parser, 1) # alternative using directly the design_constraint_constructor() function
  ### heritage from bagel
  i_bagel = inherit_bagel()
  r_parser = i_bagel.get_constraint_constructor()(r_parser, 1)
  #r_parser = bagel.bagel_constraint_constructor(r_parser, 1) # alternative
  ### output
  # return
  return(r_parser)

    
################################################################
# bell_bagel_assembly constraint_check
################################################################

def bba_constraint_check(c):
  """ check the bell_bagel_assembly constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  # bagel_axle_diameter
  c['bagel_axle_radius'] = c['bagel_axle_diameter']/2.0
  if(c['bagel_axle_radius']<radian_epsilon):
    print("ERR125: Error, bagel_axle_radius {:0.3f} is too small".format(c['bagel_axle_radius']))
    sys.exit(2)
  c['bagel_axle_diameter'] = 2*c['bagel_axle_radius']
  # bagel_axle_internal_diameter
  c['bagel_axle_internal_radius'] = c['bagel_axle_internal_diameter']/2.0
  if(c['bagel_axle_internal_radius']==0):
    c['bagel_axle_internal_radius'] = 2*c['bagel_axle_radius']
  if(c['bagel_axle_internal_radius']<c['bagel_axle_radius']):
    print("ERR132: Error, bagel_axle_internal_radius {:0.3f} must be bigger than bagel_axle_radius {:0.3f}".format(c['bagel_axle_internal_radius'], c['bagel_axle_radius']))
    sys.exit(2)
  c['bagel_axle_internal_diameter'] = 2*c['bagel_axle_internal_radius']
  # bagel_axle_external_diameter
  c['bagel_axle_external_radius'] = c['bagel_axle_external_diameter']/2.0
  if(c['bagel_axle_external_radius']==0):
    c['bagel_axle_external_radius'] = 2*c['bagel_axle_internal_radius']
  if(c['bagel_axle_external_radius']<c['bagel_axle_internal_radius']+radian_epsilon):
    print("ERR139: Error, bagel_axle_external_radius {:0.3f} must be bigger than bagel_axle_internal_radius {:0.3f}".format(c['bagel_axle_external_radius'], c['bagel_axle_internal_radius']))
    sys.exit(2)
  c['bagel_axle_external_diameter'] = 2*c['bagel_axle_external_radius']
  # axle_internal_diameter
  c['axle_internal_radius'] = c['axle_internal_diameter']/2.0
  if(c['axle_internal_radius']==0):
    c['axle_internal_radius'] = c['bagel_axle_internal_radius']
  if(c['axle_internal_radius']<c['bagel_axle_radius']):
    print("ERR146: Error, axle_internal_radius {:0.3f} must be bigger than bagel_axle_radius {:0.3f}".format(c['axle_internal_radius'], c['bagel_axle_radius']))
    sys.exit(2)
  c['axle_internal_diameter'] = 2*c['axle_internal_radius']
  # axle_external_diameter
  c['axle_external_radius'] = c['axle_external_diameter']/2.0
  if(c['axle_external_radius']==0):
    c['axle_external_radius'] = 2*c['axle_internal_radius']
  if(c['axle_external_radius']<c['axle_internal_radius']+radian_epsilon):
    print("ERR139: Error, axle_external_radius {:0.3f} must be bigger than axle_internal_radius {:0.3f}".format(c['axle_external_radius'], c['axle_internal_radius']))
    sys.exit(2)
  c['axle_external_diameter'] = 2*c['axle_external_radius']
  ### sub-design check
  #i_bell = inherit_bell(c)
  #c.update(i_bell.apply_external_constraint(c))
  #i_bagel = inherit_bagel(c)
  #c.update(i_bagel.apply_external_constraint(c))
  ### additional internal contraint/parameters
  c['bagel_z'] = c['base_thickness'] + c['bell_face_height'] + c['leg_length']
  return(c)

################################################################
# bell_bagel_assembly 2D-figures construction
################################################################

def bba_2d_construction(c):
  """ construct the 2D-figures with outlines at the A-format for the bell_bagel_assembly design
  """
  # inherit from bell
  i_bell = inherit_bell(c)
  (bell_figs, bell_height) = i_bell.apply_2d_constructor()
  # inherit from bagel
  i_bagel = inherit_bagel(c)
  (bagel_figs, bagel_height) = i_bagel.apply_2d_constructor()
  ### figures output
  # part_list
  part_list = []
  part_list.extend(bell_figs.values())
  part_list.extend(bagel_figs.values())
  # part_list_figure
  x_space = 2.1*c['base_diameter'] 
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## bell_bagel_assembly
  bell_face_fig = bell_figs['bell_face']
  bagel_external_fig = bagel_figs['external_bagel']
  bell_bagel_assembly_figure = []
  bell_bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(bell_face_fig, 0.0, 0.0, 0.0,      0, 0))
  bell_bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(bagel_external_fig, 0.0, 0.0, 0.0, 0, c['bagel_z']))
  ###
  r_figures = {}
  r_height = {}

  r_figures.update(bell_figs)
  r_height.update(bell_height)

  r_figures.update(bagel_figs)
  r_height.update(bagel_height)

  r_figures['part_list'] = part_list_figure
  r_height['part_list'] = 1.0

  r_figures['bell_bagel_assembly'] = bell_bagel_assembly_figure
  r_height['bell_bagel_assembly'] = 1.0
  ###
  return((r_figures, r_height))

################################################################
# bell_bagel_assembly 3D assembly-configuration construction
################################################################

def bba_3d_construction(c):
  """ construct the 3D-assembly-configurations of the bell_bagel_assembly
  """
  # inherit from bell
  i_bell = inherit_bell(c)
  (bell_3dconf, bell_slice) = i_bell.apply_3d_constructor()
  # inherit from bagel
  i_bagel = inherit_bagel(c)
  (bagel_3dconf, bagel_slice) = i_bagel.apply_3d_constructor()
  ### freecad-object assembly configuration
  # sub function
  def re_conf3d(ai_conf_line, ai_flip, ai_orientation, ai_tx, ai_ty, ai_tz):
    """ translate a figure of a 3D configuration
    """
    (figure, zero_x, zero_y, size_x, size_y, size_z, flip, orientation, tx, ty, tz) = ai_conf_line
    r_conf_line = (figure, zero_x, zero_y, size_x, size_y, size_z, ai_flip, ai_orientation, ai_tx, ai_ty, ai_tz)
    return(r_conf_line)
  # intermediate parameters
  bger = c['bagel_axle_external_radius']
  bgir = c['bagel_axle_internal_radius']
  bagel_y1 = c['bell_face_width']/2.0
  bagel_y2 = -1*c['bell_face_width']/2.0
  bget = c['external_bagel_thickness']
  bgmt = c['face_thickness']
  bgit = c['internal_bagel_thickness']
  re_conf_bagel_1 = []
  re_conf_bagel_1.append(('i', 'xz', -1*bger, bagel_y1, c['bagel_z']-bger))
  re_conf_bagel_1.append(('i', 'xz', -1*bgir, bagel_y1-bgmt, c['bagel_z']-bgir))
  re_conf_bagel_1.append(('i', 'xz', -1*bger, bagel_y1-bgmt-bgit, c['bagel_z']-bger))
  re_conf_bagel_1.append(('i', 'xz', -1*bger, bagel_y1-bgmt-bgit, c['bagel_z']-bger))
  re_conf_bagel_2 = []
  re_conf_bagel_2.append(('i', 'xz', -1*bger, bagel_y2-bget, c['bagel_z']-bger))
  re_conf_bagel_2.append(('i', 'xz', -1*bgir, bagel_y2, c['bagel_z']-bgir))
  re_conf_bagel_2.append(('i', 'xz', -1*bger, bagel_y2+bgmt, c['bagel_z']-bger))
  re_conf_bagel_2.append(('i', 'xz', -1*bger, bagel_y2+bgmt, c['bagel_z']-bger))
  # conf1
  bell_bagel_assembly_conf1 = []
  bell_bagel_assembly_conf1.extend(bell_3dconf['bell_assembly_conf2'])
  for i in range(len(bagel_3dconf['bagel_assembly_conf1'])):
    bell_bagel_assembly_conf1.append(re_conf3d(bagel_3dconf['bagel_assembly_conf1'][i], re_conf_bagel_1[i][0], re_conf_bagel_1[i][1], re_conf_bagel_1[i][2], re_conf_bagel_1[i][3], re_conf_bagel_1[i][4]))
  for i in range(len(bagel_3dconf['bagel_assembly_conf1'])):
    bell_bagel_assembly_conf1.append(re_conf3d(bagel_3dconf['bagel_assembly_conf1'][i], re_conf_bagel_2[i][0], re_conf_bagel_2[i][1], re_conf_bagel_2[i][2], re_conf_bagel_2[i][3], re_conf_bagel_2[i][4]))
  ###
  r_assembly = {}
  r_slice = {}

  r_assembly['bell_bagel_assembly_conf1'] = bell_bagel_assembly_conf1
  r_slice['bell_bagel_assembly_conf1'] = bell_slice['bell_assembly_conf2']
  #
  return((r_assembly, r_slice))

################################################################
# bell_bagel_assembly_info
################################################################

def bba_info(c):
  """ create the text info related to the bell_bagel_assembly
  """
  r_info = ""
  # inherit from bell
  i_bell = inherit_bell(c)
  r_info += i_bell.get_info()
  # inherit from bagel
  i_bagel = inherit_bagel(c)
  r_info += i_bagel.get_info()
  #
  return(r_info)

################################################################
# self test
################################################################

def bba_self_test():
  """
  This is the non-regression test of bell_bagel_assembly.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , ""],
    ["no axle_holes"        , "--axle_hole_nb 0"],
    ["odd number of axle_holes" , "--axle_hole_nb 5"],
    ["outputfile" , "--output_file_basename test_output/bba_self_test.dxf"],
    ["last test"            , "--bagel_axle_internal_diameter 25.0 --bagel_axle_external_diameter 40.0 --axle_hole_position_diameter 35.0 --axle_internal_diameter 28.0 --axle_external_diameter 42.0"]]
  return(r_tests)

################################################################
# bell_bagel_assembly declaration
################################################################

class bba(cnc25d_api.bare_design):
  """ bell_bagel_assembly
  """
  def __init__(self, constraint={}):
    """ configure the bell_bagel_assembly
    """
    figs = []
    self.design_setup(
      s_design_name             = "bell_bagel_design",
      f_constraint_constructor  = bba_constraint_constructor,
      f_constraint_check        = bba_constraint_check,
      f_2d_constructor          = bba_2d_construction,
      d_2d_simulation           = {},
      f_3d_constructor          = bba_3d_construction,
      f_info                    = bba_info,
      l_display_figure_list     = ['bell_bagel_assembly'],
      s_default_simulation      = "",
      #l_2d_figure_file_list     = [],
      l_2d_figure_file_list     = figs,
      l_3d_figure_file_list     = figs,
      l_3d_conf_file_list       = ['bell_bagel_assembly_conf1'],
      f_cli_return_type         = None,
      l_self_test_list          = bba_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("bell_bagel_assembly.py says hello!\n")
  my_bba = bba()
  #my_bba.cli()
  my_bba.cli("--bell_extra_cut_thickness 1.0 --bagel_extra_cut_thickness 1.0")
  if(cnc25d_api.interpretor_is_freecad()):
    #my_bba.apply_cli("--bell_extra_cut_thickness 1.0 --bagel_extra_cut_thickness 1.0")
    #my_bba.outline_display()
    Part.show(my_bba.get_fc_obj('bell_bagel_assembly_conf1'))


