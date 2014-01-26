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
# bagel constraint_constructor
################################################################

def bagel_constraint_constructor(ai_parser, ai_variant=0):
  """
  Add arguments relative to the bagel
  """
  r_parser = ai_parser
  ## diameters
  r_parser.add_argument('--bagel_axle_diameter','--bgad', action='store', type=float, default=10.0,
    help="Set the axle_diameter. Default: 10.0")
  r_parser.add_argument('--bagel_axle_internal_diameter','--bgaid', action='store', type=float, default=20.0,
    help="Set the axle_internal_diameter. If equal to 0.0, set to 2*bagel_axle_diameter. Default: 0.0")
  r_parser.add_argument('--bagel_axle_external_diameter','--bgaed', action='store', type=float, default=0.0,
    help="Set the axle_external_diameter. If equal to 0.0, set to 2*bagel_axle_internal_diameter. Default: 0.0")
  ## axle_holes
  if(ai_variant!=1):
    r_parser.add_argument('--axle_hole_nb','--ahn', action='store', type=int, default=6,
      help="Set the number of the axle-holes. If equal to 0, no axle-hole is created. Default: 6")
    r_parser.add_argument('--axle_hole_diameter','--ahd', action='store', type=float, default=4.0,
      help="Set the diameter of the axle-holes. Default: 4.0")
    r_parser.add_argument('--axle_hole_position_diameter','--ahpd', action='store', type=float, default=0.0,
      help="Set the diameter of the axle-hole position circle. If equal to 0.0, set to (axle_internal_diameter+axle_external_diameter)/2. Default: 0.0")
    r_parser.add_argument('--axle_hole_angle','--aha', action='store', type=float, default=0.0,
      help="Set the position angle of the first axle-hole. Default: 0.0")
  ## part thickness
  r_parser.add_argument('--external_bagel_thickness','--ebt', action='store', type=float, default=2.0,
    help="Set the thickness (z-size) of the external_bagel part. Default: 2.0")
  if(ai_variant!=1):
    r_parser.add_argument('--middle_bagel_thickness','--mbt', action='store', type=float, default=6.0,
      help="Set the thickness (z-size) of the middle_bagel part. Default: 6.0")
  r_parser.add_argument('--internal_bagel_thickness','--ibt', action='store', type=float, default=2.0,
    help="Set the thickness (z-size) of the internal_bagel part. Default: 2.0")
  ### manufacturing
  r_parser.add_argument('--bagel_extra_cut_thickness','--bgect', action='store', type=float, default=0.0,
    help="Set the extra-cut-thickness for the internal-bagel cut. It can be used to compensate the manufacturing process or to check the 3D assembly with FreeCAD. Default: 0.0")
  ### output
  # return
  return(r_parser)

################################################################
# bagel constraint_check
################################################################

def bagel_constraint_check(c):
  """ check the bagel constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ################################################################
  # parameter check and dynamic-default values
  ################################################################
  # bagel_axle_diameter
  c['bagel_axle_radius'] = c['bagel_axle_diameter']/2.0
  if(c['bagel_axle_radius']<radian_epsilon):
    print("ERR152: Error, bagel_axle_radius {:0.3f} is too small".format(c['bagel_axle_radius']))
    sys.exit(2)
  # bagel_axle_internal_diameter
  c['bagel_axle_internal_radius'] = c['bagel_axle_internal_diameter']/2.0
  if(c['bagel_axle_internal_radius']==0):
    c['bagel_axle_internal_radius'] = 2*c['bagel_axle_radius']
  if(c['bagel_axle_internal_radius']<c['bagel_axle_radius']):
    print("ERR159: Error, bagel_axle_internal_radius {:0.3f} must be bigger than bagel_axle_radius {:0.3f}".format(c['bagel_axle_internal_radius'], c['bagel_axle_radius']))
    sys.exit(2)
  # bagel_axle_external_diameter
  c['bagel_axle_external_radius'] = c['bagel_axle_external_diameter']/2.0
  if(c['bagel_axle_external_radius']==0):
    c['bagel_axle_external_radius'] = 2*c['bagel_axle_internal_radius']
  if(c['bagel_axle_external_radius']<c['bagel_axle_internal_radius']+radian_epsilon):
    print("ERR166: Error, bagel_axle_external_radius {:0.3f} must be bigger than bagel_axle_internal_radius {:0.3f}".format(c['bagel_axle_external_radius'], c['bagel_axle_internal_radius']))
    sys.exit(2)
  # axle_hole_nb
  c['axle_hole_radius'] = 0.0
  c['axle_hole_position_radius'] = 0.0
  if(c['axle_hole_nb']>0):
    # axle_hole_diameter
    c['axle_hole_radius'] = c['axle_hole_diameter']/2.0
    if(c['axle_hole_radius']<radian_epsilon):
      print("ERR173: Error, axle_hole_radius {:0.3f} must be strictly positive".format(c['axle_hole_radius']))
      sys.exit(2)
    # axle_hole_position_diameter
    c['axle_hole_position_radius'] = c['axle_hole_position_diameter']/2.0
    if(c['axle_hole_position_radius']==0.0):
      c['axle_hole_position_radius'] = (c['bagel_axle_internal_radius']+c['bagel_axle_external_radius'])/2.0
    if(c['axle_hole_position_radius'] < c['bagel_axle_internal_radius']+c['axle_hole_radius']+radian_epsilon):
      print("ERR180: Error: axle_hole_position_radius {:0.3f} is too small compare to bagel_axle_internal_radius {:0.3f} and axle_hole_radius {:0.3f}".format(c['axle_hole_position_radius'], c['bagel_axle_internal_radius'], c['axle_hole_radius']))
      sys.exit(2)
    if(c['axle_hole_position_radius'] > c['bagel_axle_external_radius']-c['axle_hole_radius']-radian_epsilon):
      print("ERR183: Error: axle_hole_position_radius {:0.3f} is too big compare to bagel_axle_external_radius {:0.3f} and axle_hole_radius {:0.3f}".format(c['axle_hole_position_radius'], c['bagel_axle_external_radius'], c['axle_hole_radius']))
      sys.exit(2)
    # axle_hole_angle
  # external_bagel_thickness
  if(c['external_bagel_thickness']<radian_epsilon):
    print("ERR188: Error, external_bagel_thickness {:0.3f} is too small".format(c['external_bagel_thickness']))
    sys.exit(2)
  # middle_bagel_thickness
  if(c['middle_bagel_thickness']<radian_epsilon):
    print("ERR192: Error, middle_bagel_thickness {:0.3f} is too small".format(c['middle_bagel_thickness']))
    sys.exit(2)
  # internal_bagel_thickness
  if(c['internal_bagel_thickness']<radian_epsilon):
    print("ERR196: Error, internal_bagel_thickness {:0.3f} is too small".format(c['internal_bagel_thickness']))
    sys.exit(2)
  # bagel_extra_cut_thickness
  if(abs(c['bagel_extra_cut_thickness'])>c['bagel_axle_radius']/2.0):
    print("ERR212: Error, bagel_extra_cut_thickness {:0.3f} is too big compare to bagel_axle_radius {:0.3f}".format(c['bagel_extra_cut_thickness'], c['bagel_axle_radius']))
    sys.exit(2)
  return(c)

################################################################
# bagel 2D-figures construction
################################################################

def bagel_2d_construction(c):
  """ construct the 2D-figures with outlines at the A-format for the bagel design
  """
  ### external_bagel
  external_bagel = []
  external_bagel.append((0.0, 0.0, c['bagel_axle_external_radius']))
  external_bagel.append((0.0, 0.0, c['bagel_axle_radius']))
  for i in range(c['axle_hole_nb']):
    a = i*2*math.pi/c['axle_hole_nb']+c['axle_hole_angle']
    external_bagel.append((0.0+c['axle_hole_position_radius']*math.cos(a), 0.0+c['axle_hole_position_radius']*math.sin(a), c['axle_hole_radius']))

  ### middle_bagel
  middle_bagel = []
  middle_bagel.append((0.0, 0.0, c['bagel_axle_internal_radius']))
  middle_bagel.append((0.0, 0.0, c['bagel_axle_radius']))

  ### internal_bagel
  # intermediate parameters
  cut_y = c['bagel_extra_cut_thickness']
  cut_x1 = math.sqrt(c['bagel_axle_radius']**2+cut_y**2)
  cut_x2 = math.sqrt(c['bagel_axle_external_radius']**2+cut_y**2)
  # outline construction
  ib_ol_A = []
  ib_ol_A.append((cut_x2, cut_y, 0))
  ib_ol_A.append((0.0, c['bagel_axle_external_radius'], -1*cut_x2, cut_y, 0))
  ib_ol_A.append((-1*cut_x1, cut_y, 0))
  ib_ol_A.append((0.0, c['bagel_axle_radius'], cut_x1, cut_y, 0))
  ib_ol_A.append((cut_x2, cut_y, 0))
  #ib_ol = cnc25d_api.cnc_cut_outline(ib_ol_A, "internal_bagel_ol")
  # figure construction
  ib_figure = []
  ib_figure.append(ib_ol_A)
  ib_figure_2 = []
  ib_figure_2.append(ib_ol_A)
  if(c['axle_hole_nb']>0):
    a_step = math.pi/c['axle_hole_nb']
    for i in range(c['axle_hole_nb']/2):
      a = (2*i+1)*a_step
      ib_figure.append((0.0+c['axle_hole_position_radius']*math.cos(a), 0.0+c['axle_hole_position_radius']*math.sin(a), c['axle_hole_radius']))
    ib_figure = cnc25d_api.rotate_and_translate_figure(ib_figure, 0.0, 0.0, c['axle_hole_angle']-a_step, 0.0, 0.0)
    for i in range(c['axle_hole_nb']/2):
      a = (2*i+1+(c['axle_hole_nb']%2))*a_step
      ib_figure_2.append((0.0+c['axle_hole_position_radius']*math.cos(a), 0.0+c['axle_hole_position_radius']*math.sin(a), c['axle_hole_radius']))
    ib_figure_2 = cnc25d_api.rotate_and_translate_figure(ib_figure_2, 0.0, 0.0, c['axle_hole_angle']-a_step, 0.0, 0.0)
  internal_bagel = ib_figure
  internal_bagel_2 = cnc25d_api.rotate_and_translate_figure(ib_figure_2, 0.0, 0.0, math.pi, 0.0, 0.0)
  ### figures output
  # part_list
  part_list = []
  part_list.append(external_bagel)
  part_list.append(middle_bagel)
  part_list.append(internal_bagel)
  part_list.append(internal_bagel_2)
  # part_list_figure
  x_space = 2.2*c['bagel_axle_external_radius'] 
  part_list_figure = []
  for i in range(len(part_list)):
    part_list_figure.extend(cnc25d_api.rotate_and_translate_figure(part_list[i], 0.0, 0.0, 0.0, i*x_space, 0.0))
  ## bagel_part_overview
  bagel_assembly_figure = []
  bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(external_bagel, 0.0, 0.0, 0.0,   0, 0))
  bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(middle_bagel, 0.0, 0.0, 0.0,     0, 0))
  bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(internal_bagel, 0.0, 0.0, 0.0,   0, 0))
  bagel_assembly_figure.extend(cnc25d_api.rotate_and_translate_figure(internal_bagel_2, 0.0, 0.0, 0.0, 0, 0))
  ###
  r_figures = {}
  r_height = {}

  r_figures['external_bagel'] = external_bagel
  r_height['external_bagel'] = c['external_bagel_thickness']

  r_figures['middle_bagel'] = middle_bagel
  r_height['middle_bagel'] = c['middle_bagel_thickness']

  r_figures['internal_bagel'] = internal_bagel
  r_height['internal_bagel'] = c['internal_bagel_thickness']

  r_figures['internal_bagel_2'] = internal_bagel_2
  r_height['internal_bagel_2'] = c['internal_bagel_thickness']

  r_figures['part_list'] = part_list_figure
  r_height['part_list'] = 1.0

  r_figures['bagel_assembly'] = bagel_assembly_figure
  r_height['bagel_assembly'] = 1.0
  ###
  return((r_figures, r_height))
  
################################################################
# bagel 3D assembly-configuration construction
################################################################

def bagel_3d_construction(c):
  """ construct the 3D-assembly-configurations of the bagel design
  """
  ### freecad-object assembly configuration
  # intermediate parameters
  aer = c['bagel_axle_external_radius']
  air = c['bagel_axle_internal_radius']
  ebt = c['external_bagel_thickness']
  mbt = c['middle_bagel_thickness']
  ibt = c['internal_bagel_thickness']
  # conf1
  bagel_assembly_conf1 = []
  bagel_assembly_conf1.append(('external_bagel', -1*aer, -1*aer, 2*aer, 2*aer, ebt, 'i', 'xz', -1*aer, 0,         -1*aer))
  bagel_assembly_conf1.append(('middle_bagel',   -1*air, -1*air, 2*air, 2*air, mbt, 'i', 'xz', -1*air, ebt,       -1*air))
  bagel_assembly_conf1.append(('internal_bagel', -1*aer, -1*aer, 2*aer, 2*aer, ibt, 'i', 'xz', -1*aer, ebt+mbt,   -1*aer))
  bagel_assembly_conf1.append(('internal_bagel_2', -1*aer, -1*aer, 2*aer, 2*aer, ibt, 'i', 'xz', -1*aer, ebt+mbt, -1*aer))
  ###
  r_assembly = {}
  r_slice = {}

  r_assembly['bagel_assembly_conf1'] = bagel_assembly_conf1
  r_slice['bagel_assembly_conf1'] = ()
  #
  return((r_assembly, r_slice))

################################################################
# bagel_info
################################################################

def bagel_info(c):
  """ create the text info related to the bagel design
  """
  # b_parameter_info
  b_parameter_info = """
bagel diameters:
bagel_axle_radius:          {:0.3f}   diameter: {:0.3f}
bagel_axle_internal_radius: {:0.3f}   diameter: {:0.3f}
bagel_axle_external_radius: {:0.3f}   diameter: {:0.3f}
""".format(c['bagel_axle_radius'], 2*c['bagel_axle_radius'], c['bagel_axle_internal_radius'], 2*c['bagel_axle_internal_radius'], c['bagel_axle_external_radius'], 2*c['bagel_axle_external_radius'])
  b_parameter_info += """
axle_fastening_holes:
axle_hole_nb:               {:d}
axle_hole_radius:           {:0.3f}   diameter: {:0.3f}
axle_hole_position_radius:  {:0.3f}   diameter: {:0.3f}
axle_hole_angle:            {:0.3f} (radian)    {:0.3f} (degree)
""".format(c['axle_hole_nb'], c['axle_hole_radius'], 2*c['axle_hole_radius'], c['axle_hole_position_radius'], 2*c['axle_hole_position_radius'], c['axle_hole_angle'], c['axle_hole_angle']*180/math.pi)
  b_parameter_info += """
bagel tickness:
external_bagel_thickness: {:0.3f}
middle_bagel_thickness:   {:0.3f}
internal_bagel_thickness: {:0.3f}
""".format(c['external_bagel_thickness'], c['middle_bagel_thickness'], c['internal_bagel_thickness'])
  b_parameter_info += """
manufacturing:
bagel_extra_cut_thickness:  {:0.3f}
""".format(c['bagel_extra_cut_thickness'])
  #print(b_parameter_info)
  return(b_parameter_info)

################################################################
# self test
################################################################

def bagel_self_test():
  """
  This is the non-regression test of bagel.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , ""],
    ["no axle_holes"        , "--axle_hole_nb 0"],
    ["odd number of axle_holes" , "--axle_hole_nb 5"],
    ["extra cut" , "--bagel_extra_cut_thickness 1.0"],
    ["extra cut negative" , "--bagel_extra_cut_thickness -2.0"],
    ["outputfile" , "--output_file_basename test_output/bagel_self_test.dxf"],
    ["last test"            , "--bagel_axle_internal_diameter 25.0"]]
  return(r_tests)

################################################################
# bagel design declaration
################################################################

class bagel(cnc25d_api.bare_design):
  """ bagel design
  """
  def __init__(self, constraint={}):
    """ configure the bagel design
    """
    figs = []
    self.design_setup(
      s_design_name             = "bagel_design",
      f_constraint_constructor  = bagel_constraint_constructor,
      f_constraint_check        = bagel_constraint_check,
      f_2d_constructor          = bagel_2d_construction,
      d_2d_simulation           = {},
      f_3d_constructor          = bagel_3d_construction,
      f_info                    = bagel_info,
      l_display_figure_list     = ['bagel_assembly'],
      s_default_simulation      = "",
      #l_2d_figure_file_list     = [],
      l_2d_figure_file_list     = figs,
      l_3d_figure_file_list     = figs,
      l_3d_conf_file_list       = ['bagel_assembly_conf1'],
      f_cli_return_type         = None,
      l_self_test_list          = bagel_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("bagel.py says hello!\n")
  my_bagel = bagel()
  my_bagel.cli()
  if(cnc25d_api.interpretor_is_freecad()):
    my_bagel.apply_cli("--bagel_extra_cut_thickness 1.0")
    #my_bagel.outline_display()
    Part.show(my_bagel.get_fc_obj_3dconf('bagel_assembly_conf1'))


