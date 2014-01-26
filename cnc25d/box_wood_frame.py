# box_wood_frame.py
# a wood frame for building a shell or a straw house.
# created by charlyoleg on 2013/05/02
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
box_wood_frame is a parametric design for piece of furniture.
It's a rewrite of the script box_wood_frame_ng.py using bare_design.py
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

#import importing_freecad
#importing_freecad.importing_freecad()
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
#import os
#
from box_wood_frame_outline import *
#
import Part
#from FreeCAD import Base


################################################################
# box_wood_frame constraint_constructor
################################################################

def bwf_constraint_constructor(ai_parser):
  """ Add the argparse switches relative to the box_wood_frame
  """
  r_parser = ai_parser
  r_parser.add_argument('--box_width','--bw', action='store', type=float, default=400.0,
    help="It sets the width of the box of the grid.")
  r_parser.add_argument('--box_depth','--bd', action='store', type=float, default=400.0,
    help="It sets the depth of the box of the grid. Per default, it is set to box_width value.")
  r_parser.add_argument('--box_height','--bh', action='store', type=float, default=400.0,
    help="It sets the height of the box of the grid. Per default, it is set to box_width value.")
  r_parser.add_argument('--fitting_height','--fh', action='store', type=float, default=30.0,
    help="It sets the height of the fitting that pile up vertically two modules.")
  r_parser.add_argument('--h_plank_width','--hpw', action='store', type=float, default=50.0,
    help="It sets the width of the horizontal planks. Note that the total width of the horizontal plank is plank_width+fitting_height.")
  r_parser.add_argument('--v_plank_width','--vpw', action='store', type=float, default=30.0,
    help="It sets the width of the vertical planks.")
  r_parser.add_argument('--plank_height','--ph', action='store', type=float, default=20.0,
    help="It sets the height of the vertical and horizontal planks.")
  r_parser.add_argument('--d_plank_width','--dpw', action='store', type=float, default=30.0,
    help="It sets the width of the diagonal planks. Per default the value is set to v_plank_width.")
  r_parser.add_argument('--d_plank_height','--dph', action='store', type=float, default=10.0,
    help="It sets the height of the diagonal planks. If the vaue is zero, the plank_height value will be used. Set a lower value than plank_height to give space for the slab.")
  r_parser.add_argument('--crenel_depth','--cd', action='store', type=float, default=5.0,
    help="It sets the depth of the crenels of the coplanar planks.")
  r_parser.add_argument('--wall_diagonal_size','--wdz', action='store', type=float, default=50.0,
    help="It sets the size of the diagonal lining of the four vertical walls.")
  r_parser.add_argument('--tobo_diagonal_size','--tbdz', action='store', type=float, default=100.0,
    help="It sets the size of the diagonal lining of the top and bottom faces.")
  r_parser.add_argument('--diagonal_lining_top_height','--dlth', action='store', type=float, default=20.0,
    help="It sets the distance between the plank border and the holes for the horizontal top planks.")
  r_parser.add_argument('--diagonal_lining_bottom_height','--dlbh', action='store', type=float, default=20.0,
    help="It sets the distance between the plank border and the holes for the horizontal bottom planks.")
  #r_parser.add_argument('--tobo_diagonal_depth','--tdd', action='store', type=float, default=0.0,
  #  help="It sets the depth of the fitting between tobo_diagonal_lining_plank and horizontal_plank.")
  r_parser.add_argument('--module_width','--mw', action='store', type=int, default=1,
    help="It sets the width of the module in number of box_width.")
  #r_parser.add_argument('--module_depth','--md', action='store', type=int, default=1,
  #  help="It sets the depth of the module in number of box_depth.")
  #r_parser.add_argument('--module_height','--mh', action='store', type=int, default=1,
  #  help="It sets the height of the module in number of box_height.")
  r_parser.add_argument('--router_bit_radius','--rr', action='store', type=float, default=2.0,
    help="It sets the radius of the router_bit of the cnc.")
  r_parser.add_argument('--cutting_extra','--ce', action='store', type=float, default=2.0,
    help="It sets the cutting_extra used to see better the fitting in the assembly view.")
  r_parser.add_argument('--slab_thickness','--st', action='store', type=float, default=5.0,
    help="If not zero (the default value), it generates the slabs with this thickness.")
#  r_parser.add_argument('--output_file_basename','--ofb', action='store', default='',
#    help="If not set to the empty string (the default value), it generates a bunch of design files starting with this basename.")
#  r_parser.add_argument('--return_type','--rt', action='store', default='int_status',
#    help="Define the what the box_wood_frame() function should returns. Possible values: int_status, freecad_object. Set it to freecad_object to use it with FreeCAD. Default: int_status")
  return(r_parser)

################################################################
# box_wood_frame constraint_check
################################################################

def bwf_constraint_check(c):
  """ check the box_wood_frame constraint c and set the dynamic default values
  """
  #c['box_width']
  #c['box_depth']
  #c['box_height']
  #c['fitting_height']
  #c['h_plank_width']
  #c['v_plank_width']
  #c['plank_height']
  #c['d_plank_width']
  #c['d_plank_height']
  #c['crenel_depth']
  #c['wall_diagonal_size']
  #c['tobo_diagonal_size']
  #c['diagonal_lining_top_height']
  #c['diagonal_lining_bottom_height']
  #c['module_width']
  #c['router_bit_radius']
  #c['cutting_extra']
  #c['slab_thickness']
  ## check parameter coherence
  minimal_thickness = 5.0 # only used to check the parameter coherence
  if( (c['plank_height'] + c['v_plank_width'] + c['wall_diagonal_size'] + c['d_plank_height']*math.sqrt(2) + minimal_thickness) > c['box_width']/2 ):
    print("ERR601: Error of parameter coherence. Reduce wall_diagonal_size!\n")
    sys.exit(2)
  ## reassigned zero value minor parameters
  ai_tobo_diag_depth=0 # that was previously an argument
  if(ai_tobo_diag_depth==0):
    c['tobo_diag_depth'] = 1.0/2*c['plank_height']-0.5
  ### planks
  c['remove_skin_thickness'] = 1.0 # use during cut operation to avoid remaining skin
  ## plank dimension
  c['plank_xz_length'] = c['module_width']*c['box_width']
  c['plank_xz_width'] = c['h_plank_width']+c['fitting_height']
  c['plank_xz_height'] = c['plank_height']
  c['plank_yz_length'] = c['box_depth']
  c['plank_yz_width'] = c['plank_xz_width']
  c['plank_yz_height'] = c['plank_xz_height']
  c['plank_z_length'] = c['box_height'] - 2*c['h_plank_width'] - c['fitting_height'] + 2*c['crenel_depth']
  c['plank_z_width'] = c['v_plank_width']
  c['plank_z_height'] = c['plank_xz_height']
  c['plank_wall_diagonal_length'] = (c['wall_diagonal_size']+2*c['crenel_depth'])*math.sqrt(2)+2*(c['d_plank_width']-c['crenel_depth']*math.sqrt(2)/2)
  c['plank_wall_diagonal_width'] = c['d_plank_width']
  c['plank_wall_diagonal_height'] = c['d_plank_height']
  c['plank_tobo_diagonal_length'] = c['tobo_diagonal_size']*math.sqrt(2)+2*c['d_plank_width']+0*c['tobo_diag_depth']*math.sqrt(2)/2
  c['plank_tobo_diagonal_width'] = c['d_plank_width']
  c['plank_tobo_diagonal_height'] = c['plank_wall_diagonal_height']
  c['plank_hole_cover_length'] = (c['d_plank_width']*math.sqrt(2)-3*c['tobo_diag_depth'])
  c['plank_hole_cover_width'] = c['d_plank_height']
  c['plank_hole_cover_height'] = c['plank_height']-c['tobo_diag_depth']
  # rotated plank
  c['plank_wall_diagonal_in_cuboid_x_length'] = c['wall_diagonal_size']+c['d_plank_height']*math.sqrt(2)-c['crenel_depth']
  c['plank_wall_diagonal_in_cuboid_y_width'] = c['d_plank_width']*math.sqrt(2)
  c['plank_tobo_diagonal_in_cuboid_x_length'] = c['tobo_diagonal_size']+c['d_plank_width']*math.sqrt(2)-c['crenel_depth']
  c['plank_tobo_diagonal_in_cuboid_y_width'] = c['d_plank_width']*math.sqrt(2)
  ## slab dimension
  c['slab_top_bottom_single_length'] = c['box_width']-2*c['plank_height']
  c['slab_top_bottom_side_length'] = c['box_width']-1.5*c['plank_height']
  c['slab_top_bottom_middle_length'] = c['box_width']-1*c['plank_height']
  c['slab_top_bottom_width'] = c['box_depth']-2*c['plank_height']
  c['slab_top_bottom_height'] = c['slab_thickness']
  c['slab_side_length'] = c['box_height']-2*c['h_plank_width']-c['fitting_height']
  c['slab_side_left_right_width'] = c['box_depth']-2*(c['plank_height']+c['v_plank_width'])
  c['slab_side_rear_single_width'] = c['box_width']-2*c['v_plank_width']
  c['slab_side_rear_side_width'] = c['box_width']-1.5*c['v_plank_width']
  c['slab_side_rear_middle_width'] = c['box_width']-1*c['v_plank_width']
  c['slab_side_height'] = c['slab_thickness']
  c['slab_front_length'] = c['wall_diagonal_size']+c['d_plank_width']*math.sqrt(2)
  c['slab_front_width'] = c['slab_front_length']
  c['slab_front_height'] = c['slab_thickness']
  return(c)


################################################################
# box_wood_frame 2D-figures construction
################################################################

def bwf_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the box_wood_frame design
  """
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['plank_xz_top'] = plank_xz_top(c)
  r_height['plank_xz_top'] = c['plank_height']
  #
  r_figures['plank_xz_bottom'] = plank_xz_bottom(c)
  r_height['plank_xz_bottom'] = c['plank_height']
  #
  r_figures['plank_yz_top'] = plank_yz_top(c)
  r_height['plank_yz_top'] = c['plank_height']
  #
  r_figures['plank_yz_bottom'] = plank_yz_bottom(c)
  r_height['plank_yz_bottom'] = c['plank_height']
  #
  r_figures['plank_z_side'] = plank_z_side(c)
  r_height['plank_z_side'] = c['plank_height']
  #
  r_figures['plank_wall_diagonal'] = plank_wall_diagonal(c)
  r_height['plank_wall_diagonal'] = c['d_plank_height']
  #
  l = c['crenel_depth']*math.sqrt(2)/2 # crenel_depth * cos(pi/4)
  r_figures['plank_wall_diag_cuboid'] = cnc25d_api.rotate_and_translate_figure(plank_wall_diagonal(c), l,0,math.pi/4, -l,0)
  r_height['plank_wall_diag_cuboid'] = c['d_plank_height']
  #
  r_figures['plank_tobo_diagonal'] = plank_tobo_diagonal(c)
  r_height['plank_tobo_diagonal'] = c['d_plank_height']
  #
  r_figures['plank_tobo_diag_cuboid'] =  cnc25d_api.rotate_and_translate_figure(plank_tobo_diagonal(c), 0,0,math.pi/4, 0,0)
  r_height['plank_tobo_diag_cuboid'] = c['d_plank_height']
  #
  r_figures['plank_zx_middle'] = plank_zx_middle(c)
  r_height['plank_zx_middle'] = c['plank_height']
  #
  r_figures['plank_hole_cover'] = plank_hole_cover(c)
  r_height['plank_hole_cover'] = c['plank_height']-c['tobo_diag_depth']
  #
  r_figures['slab_top_bottom_single'] = slab_top_bottom(c, 'single')
  r_height['slab_top_bottom_single'] = c['slab_thickness']
  #
  r_figures['slab_top_bottom_side'] = slab_top_bottom(c, 'side')
  r_height['slab_top_bottom_side'] = c['slab_thickness']
  #
  r_figures['slab_top_bottom_middle'] = slab_top_bottom(c, 'middle')
  r_height['slab_top_bottom_middle'] = c['slab_thickness']
  #
  r_figures['slab_side_left_right'] = slab_side(c, 'left_right')
  r_height['slab_side_left_right'] = c['slab_thickness']
  #
  r_figures['slab_side_rear_single'] = slab_side(c, 'rear_single')
  r_height['slab_side_rear_single'] = c['slab_thickness']
  #
  r_figures['slab_side_rear_side'] = slab_side(c, 'rear_side')
  r_height['slab_side_rear_side'] = c['slab_thickness']
  #
  r_figures['slab_side_rear_middle'] = slab_side(c, 'rear_middle')
  r_height['slab_side_rear_middle'] = c['slab_thickness']
  #
  r_figures['slab_front'] = slab_front(c)
  r_height['slab_front'] = c['slab_thickness']
  ###
  bwf_face = []
  bwf_face.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_xz_top'], 0,0,0, 0, c['box_height']-c['h_plank_width']))
  bwf_face.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_xz_bottom'], 0,0,0, 0,0))
  bwf_face.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_z_side'], 0,0,-math.pi/2, 0.0, c['fitting_height']+c['h_plank_width']-c['crenel_depth']+c['plank_z_length']))
  bwf_face.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_z_side'], 0,0,math.pi/2, c['module_width']*c['box_width'], c['fitting_height']+c['h_plank_width']-c['crenel_depth']))
  bwf_face.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
    1, -1, 0.0, c['v_plank_width'], c['fitting_height']+c['h_plank_width']+c['wall_diagonal_size']))
  bwf_face.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
    1, 1, 0.0, c['v_plank_width'], c['box_height']-c['h_plank_width']-c['wall_diagonal_size']-c['plank_wall_diagonal_in_cuboid_y_width']))
  bwf_face.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
    -1, -1, 0.0, c['module_width']*c['box_width']-c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length'], c['fitting_height']+c['h_plank_width']+c['wall_diagonal_size']))
  bwf_face.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
    -1, 1, 0.0, c['module_width']*c['box_width']-c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length'], c['box_height']-c['h_plank_width']-c['wall_diagonal_size']-c['plank_wall_diagonal_in_cuboid_y_width']))
  for i in range(c['module_width']-1):
    bwf_face.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_zx_middle'], 0,0,math.pi/2, (i+1)*c['box_width']+0.5*c['v_plank_width'], c['fitting_height']+c['h_plank_width']-c['crenel_depth']))
    bwf_face.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
      1, -1, 0.0, (i+1)*c['box_width']+0.5*c['v_plank_width'], c['fitting_height']+c['h_plank_width']+c['wall_diagonal_size']))
    bwf_face.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
      1, 1, 0.0, (i+1)*c['box_width']+0.5*c['v_plank_width'], c['box_height']-c['h_plank_width']-c['wall_diagonal_size']-c['plank_wall_diagonal_in_cuboid_y_width']))
    bwf_face.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
      -1, -1, 0.0, (i+1)*c['box_width']-0.5*c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length'], c['fitting_height']+c['h_plank_width']+c['wall_diagonal_size']))
    bwf_face.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
      -1, 1, 0.0, (i+1)*c['box_width']-0.5*c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length'], c['box_height']-c['h_plank_width']-c['wall_diagonal_size']-c['plank_wall_diagonal_in_cuboid_y_width']))
  #
  bwf_side = []
  bwf_side.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_yz_top'], 0,0,0, 0, c['box_height']-c['h_plank_width']))
  bwf_side.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_yz_bottom'], 0,0,0, 0, 0))
  bwf_side.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_z_side'], 0,0,-math.pi/2, c['plank_height'], c['fitting_height']+c['h_plank_width']-c['crenel_depth']+c['plank_z_length']))
  bwf_side.extend(cnc25d_api.rotate_and_translate_figure(r_figures['plank_z_side'], 0,0,math.pi/2, c['box_depth']-c['plank_height'], c['fitting_height']+c['h_plank_width']-c['crenel_depth']))
  bwf_side.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
    1, -1, 0.0, c['plank_height']+c['v_plank_width'], c['fitting_height']+c['h_plank_width']+c['wall_diagonal_size']))
  bwf_side.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
    1, 1, 0.0, c['plank_height']+c['v_plank_width'], c['box_height']-c['h_plank_width']-c['wall_diagonal_size']-c['plank_wall_diagonal_in_cuboid_y_width']))
  bwf_side.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
    -1, -1, 0.0, c['box_depth']-c['plank_height']-c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length'], c['fitting_height']+c['h_plank_width']+c['wall_diagonal_size']))
  bwf_side.extend(cnc25d_api.flip_rotate_and_translate_figure(r_figures['plank_wall_diag_cuboid'], 0,0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'],
    -1, 1, 0.0, c['box_depth']-c['plank_height']-c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length'], c['box_height']-c['h_plank_width']-c['wall_diagonal_size']-c['plank_wall_diagonal_in_cuboid_y_width']))
  #
  bwf_overview = []
  bwf_overview.extend(cnc25d_api.rotate_and_translate_figure(bwf_face, 0,0,0, 0,0))
  bwf_overview.extend(cnc25d_api.rotate_and_translate_figure(bwf_side, 0,0,0, (c['module_width']+0.2)*c['box_width'],0))
  #
  r_figures['bwf_face'] = bwf_face
  r_height['bwf_face'] = 1.0
  #
  r_figures['bwf_side'] = bwf_side
  r_height['bwf_side'] = 1.0
  #
  r_figures['bwf_overview'] = bwf_overview
  r_height['bwf_overview'] = 1.0
  ###
  return((r_figures, r_height))

################################################################
# box_wood_frame 3D assembly-configuration construction
################################################################

def bwf_3d_construction(c):
  """ construct the 3D-assembly-configurations of the box_wood_frame
  """
  ### conf1: frame
  bwf_3dconf1 = []
  bwf_3dconf1.append(('plank_xz_top',     0.0, 0.0, c['plank_xz_length'], c['plank_xz_width'], c['plank_height'], 'i', 'xz', 0.0, 0.0, c['box_height']-c['h_plank_width']))
  bwf_3dconf1.append(('plank_xz_top',     0.0, 0.0, c['plank_xz_length'], c['plank_xz_width'], c['plank_height'], 'i', 'xz', 0.0, c['box_depth']-c['plank_height'], c['box_height']-c['h_plank_width']))
  bwf_3dconf1.append(('plank_xz_bottom',  0.0, 0.0, c['plank_xz_length'], c['plank_xz_width'], c['plank_height'], 'i', 'xz', 0.0, 0.0, 0.0))
  bwf_3dconf1.append(('plank_xz_bottom',  0.0, 0.0, c['plank_xz_length'], c['plank_xz_width'], c['plank_height'], 'i', 'xz', 0.0, c['box_depth']-c['plank_height'], 0.0))
  bwf_3dconf1.append(('plank_yz_top',     0.0, 0.0, c['plank_yz_length'], c['plank_yz_width'], c['plank_height'], 'i', 'yz', 0.0, 0.0, c['box_height']-c['h_plank_width']))
  bwf_3dconf1.append(('plank_yz_top',     0.0, 0.0, c['plank_yz_length'], c['plank_yz_width'], c['plank_height'], 'i', 'yz', c['module_width']*c['box_width']-c['plank_height'], 0.0, c['box_height']-c['h_plank_width']))
  for i in range(c['module_width']-1):
    bwf_3dconf1.append(('plank_yz_top',   0.0, 0.0, c['plank_yz_length'], c['plank_yz_width'], c['plank_height'], 'i', 'yz', (i+1)*c['box_width']-0.5*c['plank_height'], 0.0, c['box_height']-c['h_plank_width']))
  bwf_3dconf1.append(('plank_yz_bottom',  0.0, 0.0, c['plank_yz_length'], c['plank_yz_width'], c['plank_height'], 'i', 'yz', 0.0, 0.0, 0.0))
  bwf_3dconf1.append(('plank_yz_bottom',  0.0, 0.0, c['plank_yz_length'], c['plank_yz_width'], c['plank_height'], 'i', 'yz', c['module_width']*c['box_width']-c['plank_height'], 0.0, 0.0))
  for i in range(c['module_width']-1):
    bwf_3dconf1.append(('plank_yz_bottom',   0.0, 0.0, c['plank_yz_length'], c['plank_yz_width'], c['plank_height'], 'i', 'yz', (i+1)*c['box_width']-0.5*c['plank_height'], 0.0, 0.0))
  plank_z_position_z = c['h_plank_width']+c['fitting_height']-c['crenel_depth']
  bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'i', 'zx', 0.0, 0.0, plank_z_position_z))
  bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'x', 'zx', c['module_width']*c['box_width']-c['v_plank_width'], 0.0, plank_z_position_z))
  bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'i', 'zx', 0.0, c['box_depth']-c['plank_height'], plank_z_position_z))
  bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'x', 'zx', c['module_width']*c['box_width']-c['v_plank_width'], c['box_depth']-c['plank_height'], plank_z_position_z))
  for i in range(c['module_width']-1):
    bwf_3dconf1.append(('plank_zx_middle',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'i', 'zx', (i+1)*c['box_width']-0.5*c['v_plank_width'], 0.0, plank_z_position_z))
    bwf_3dconf1.append(('plank_zx_middle',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'x', 'zx', (i+1)*c['box_width']-0.5*c['v_plank_width'], c['box_depth']-c['plank_height'], plank_z_position_z))
  bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'i', 'zy', 0.0, c['plank_height'], plank_z_position_z))
  bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'x', 'zy', 0.0,  c['box_depth']-c['plank_height']-c['v_plank_width'],plank_z_position_z))
  bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'i', 'zy', c['module_width']*c['box_width']-c['plank_height'], c['plank_height'], plank_z_position_z))
  bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'x', 'zy', c['module_width']*c['box_width']-c['plank_height'],  c['box_depth']-c['plank_height']-c['v_plank_width'],plank_z_position_z))
  for i in range(c['module_width']-1):
    bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'i', 'zy', (i+1)*c['box_width']-0.5*c['plank_height'], c['plank_height'], plank_z_position_z))
    bwf_3dconf1.append(('plank_z_side',     0.0, 0.0, c['plank_z_length'], c['plank_z_width'], c['plank_height'], 'x', 'zy', (i+1)*c['box_width']-0.5*c['plank_height'], c['box_depth']-c['plank_height']-c['v_plank_width'],plank_z_position_z))
  # diagonal xz
  z1 = c['fitting_height']+c['h_plank_width']+c['wall_diagonal_size']
  z2 = c['box_height']-c['h_plank_width']-c['wall_diagonal_size']-c['d_plank_width']*math.sqrt(2)
  y1 = c['plank_height']-c['d_plank_height']
  y2 = c['box_depth']-c['plank_height']
  x1 = c['v_plank_width']
  x2 = c['module_width']*c['box_width']-c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length']
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'xz', x1, y1, z2))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'xz', x1, y1, z1))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'xz', x1, y2, z2))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'xz', x1, y2, z1))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'xz', x2, y1, z2))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'xz', x2, y1, z1))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'xz', x2, y2, z2))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'xz', x2, y2, z1))
  for i in range(c['module_width']-1):
    x1 = (i+1)*c['box_width']+0.5*c['v_plank_width']
    x2 = (i+1)*c['box_width']-0.5*c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length']
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'xz', x1, y1, z2))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'xz', x1, y1, z1))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'xz', x1, y2, z2))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'xz', x1, y2, z1))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'xz', x2, y1, z2))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'xz', x2, y1, z1))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'xz', x2, y2, z2))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'xz', x2, y2, z1))
  # diagonal yz
  y1 = c['plank_height']+c['v_plank_width']
  y2 = c['box_depth']-c['plank_height']-c['v_plank_width']-c['plank_wall_diagonal_in_cuboid_x_length']
  x1 = c['plank_height']-c['d_plank_height']
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'yz', x1, y1, z2))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'yz', x1, y1, z1))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'yz', x1, y2, z2))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'yz', x1, y2, z1))
  x1 = c['module_width']*c['box_width']-c['plank_height']
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'yz', x1, y1, z2))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'yz', x1, y1, z1))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'yz', x1, y2, z2))
  bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'yz', x1, y2, z1))
  for i in range(c['module_width']-1):
    x1 = (i+1)*c['box_width']-0.5*c['d_plank_height']
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'yz', x1, y1, z2))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'yz', x1, y1, z1))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'yz', x1, y2, z2))
    bwf_3dconf1.append(('plank_wall_diag_cuboid',     0.0, 0.0, c['plank_wall_diagonal_in_cuboid_x_length'], c['plank_wall_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'yz', x1, y2, z1))
  # diagonal xy
  x1 = c['plank_height']
  x2 = c['module_width']*c['box_width']-c['plank_height']-c['plank_tobo_diagonal_in_cuboid_x_length']
  y1 = c['plank_height']+c['tobo_diagonal_size']
  y2 = c['box_depth']-c['plank_height']-c['tobo_diagonal_size']-c['plank_tobo_diagonal_in_cuboid_y_width']
  z1 = c['fitting_height']+c['h_plank_width']-c['diagonal_lining_bottom_height']-c['d_plank_height']
  z2 = c['box_height']-c['h_plank_width']+c['diagonal_lining_top_height']
  bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'xy', x1, y1, z2))
  bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'xy', x1, y1, z1))
  bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'xy', x1, y2, z2))
  bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'xy', x1, y2, z1))
  bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'xy', x2, y1, z2))
  bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'xy', x2, y1, z1))
  bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'xy', x2, y2, z2))
  bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'xy', x2, y2, z1))
  for i in range(c['module_width']-1):
    x1 = (i+1)*c['box_width']+0.5*c['plank_height']
    x2 = (i+1)*c['box_width']-0.5*c['plank_height']-c['plank_tobo_diagonal_in_cuboid_x_length']
    bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'xy', x1, y1, z2))
    bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'x', 'xy', x1, y1, z1))
    bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'xy', x1, y2, z2))
    bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'i', 'xy', x1, y2, z1))
    bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'xy', x2, y1, z2))
    bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'z', 'xy', x2, y1, z1))
    bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'xy', x2, y2, z2))
    bwf_3dconf1.append(('plank_tobo_diag_cuboid',     0.0, 0.0, c['plank_tobo_diagonal_in_cuboid_x_length'], c['plank_tobo_diagonal_in_cuboid_y_width'], c['d_plank_height'], 'y', 'xy', x2, y2, z1))

  ### conf2: frame and walls
  bwf_3dconf2 = []
  bwf_3dconf2.extend(bwf_3dconf1)
  # slab side
  z1 = c['fitting_height'] + c['h_plank_width']
  y1 = c['plank_height'] + c['v_plank_width']
  x1 = c['plank_height'] - c['d_plank_height'] - c['slab_thickness']
  x2 = c['module_width']*c['box_width'] - c['plank_height'] + c['d_plank_height']
  bwf_3dconf2.append(('slab_side_left_right',     0.0, 0.0, c['slab_side_length'], c['slab_side_left_right_width'], c['slab_thickness'], 'i', 'zy', x1, y1, z1))
  bwf_3dconf2.append(('slab_side_left_right',     0.0, 0.0, c['slab_side_length'], c['slab_side_left_right_width'], c['slab_thickness'], 'i', 'zy', x2, y1, z1))
  # slab rear
  z1 = c['fitting_height'] + c['h_plank_width']
  z2 = c['box_height'] - c['h_plank_width'] - c['slab_front_length']
  y1 = c['plank_height'] - c['d_plank_height'] - c['slab_thickness']
  y2 = c['box_depth'] - c['plank_height'] + c['d_plank_height']
  x1 = c['v_plank_width']
  x2 = c['module_width']*c['box_width'] - c['v_plank_width']
  if(c['module_width']==1):
    bwf_3dconf2.append(('slab_side_rear_single',     0.0, 0.0, c['slab_side_length'], c['slab_side_rear_single_width'], c['slab_thickness'], 'i', 'zx', x1, y2, z1))
  else:
    bwf_3dconf2.append(('slab_side_rear_side',     0.0, 0.0, c['slab_side_length'], c['slab_side_rear_side_width'], c['slab_thickness'], 'i', 'zx', x1, y2, z1))
    bwf_3dconf2.append(('slab_side_rear_side',     0.0, 0.0, c['slab_side_length'], c['slab_side_rear_side_width'], c['slab_thickness'], 'i', 'zx', x2-c['slab_side_rear_side_width'], y2, z1))
    for i in range(c['module_width']-2):
      x3 = (i+1)*c['box_width'] + 0.5*c['v_plank_width']
      bwf_3dconf2.append(('slab_side_rear_middle',     0.0, 0.0, c['slab_side_length'], c['slab_side_rear_middle_width'], c['slab_thickness'], 'i', 'zx', x3, y2, z1))
  # slab front
  bwf_3dconf2.append(('slab_front',     0.0, 0.0, c['slab_front_length'], c['slab_front_width'], c['slab_thickness'], 'i', 'zx', x1, y1, z1))
  bwf_3dconf2.append(('slab_front',     0.0, 0.0, c['slab_front_length'], c['slab_front_width'], c['slab_thickness'], 'x', 'zx', x2-c['slab_front_width'], y1, z1))
  bwf_3dconf2.append(('slab_front',     0.0, 0.0, c['slab_front_length'], c['slab_front_width'], c['slab_thickness'], 'y', 'zx', x1, y1, z2))
  bwf_3dconf2.append(('slab_front',     0.0, 0.0, c['slab_front_length'], c['slab_front_width'], c['slab_thickness'], 'z', 'zx', x2-c['slab_front_width'], y1, z2))
  for i in range(c['module_width']-1):
    bwf_3dconf2.append(('slab_front',     0.0, 0.0, c['slab_front_length'], c['slab_front_width'], c['slab_thickness'], 'i', 'zx', (i+1)*c['box_width']+0.5*c['v_plank_width'], y1, z1))
    bwf_3dconf2.append(('slab_front',     0.0, 0.0, c['slab_front_length'], c['slab_front_width'], c['slab_thickness'], 'x', 'zx', (i+1)*c['box_width']-0.5*c['v_plank_width']-c['slab_front_width'], y1, z1))
    bwf_3dconf2.append(('slab_front',     0.0, 0.0, c['slab_front_length'], c['slab_front_width'], c['slab_thickness'], 'y', 'zx', (i+1)*c['box_width']+0.5*c['v_plank_width'], y1, z2))
    bwf_3dconf2.append(('slab_front',     0.0, 0.0, c['slab_front_length'], c['slab_front_width'], c['slab_thickness'], 'z', 'zx', (i+1)*c['box_width']-0.5*c['v_plank_width']-c['slab_front_width'], y1, z2))
  # slab top bottom
  x1 = c['plank_height']
  x2 = c['module_width']*c['box_width'] - c['plank_height'] - c['slab_top_bottom_side_length']
  y1 = c['plank_height']
  z1 = c['fitting_height']+c['h_plank_width']-c['diagonal_lining_bottom_height']
  z2 = c['box_height']-c['h_plank_width']+c['diagonal_lining_top_height']+c['d_plank_height']
  if(c['module_width']==1):
    bwf_3dconf2.append(('slab_top_bottom_single',     0.0, 0.0, c['slab_top_bottom_single_length'], c['slab_top_bottom_width'], c['slab_thickness'], 'i', 'xy', x1, y1, z1))
    bwf_3dconf2.append(('slab_top_bottom_single',     0.0, 0.0, c['slab_top_bottom_single_length'], c['slab_top_bottom_width'], c['slab_thickness'], 'i', 'xy', x1, y1, z2))
  else:
    bwf_3dconf2.append(('slab_top_bottom_side',     0.0, 0.0, c['slab_top_bottom_side_length'], c['slab_top_bottom_width'], c['slab_thickness'], 'i', 'xy', x1, y1, z1))
    bwf_3dconf2.append(('slab_top_bottom_side',     0.0, 0.0, c['slab_top_bottom_side_length'], c['slab_top_bottom_width'], c['slab_thickness'], 'i', 'xy', x1, y1, z2))
    bwf_3dconf2.append(('slab_top_bottom_side',     0.0, 0.0, c['slab_top_bottom_side_length'], c['slab_top_bottom_width'], c['slab_thickness'], 'i', 'xy', x2, y1, z1))
    bwf_3dconf2.append(('slab_top_bottom_side',     0.0, 0.0, c['slab_top_bottom_side_length'], c['slab_top_bottom_width'], c['slab_thickness'], 'i', 'xy', x2, y1, z2))
    for i in range(c['module_width']-2):
      x3 = (i+1)*c['box_width'] + 0.5*c['plank_height']
      bwf_3dconf2.append(('slab_top_bottom_middle',     0.0, 0.0, c['slab_top_bottom_middle_length'], c['slab_top_bottom_width'], c['slab_thickness'], 'i', 'xy', x3, y1, z1))
      bwf_3dconf2.append(('slab_top_bottom_middle',     0.0, 0.0, c['slab_top_bottom_middle_length'], c['slab_top_bottom_width'], c['slab_thickness'], 'i', 'xy', x3, y1, z2))
  #
  bwf_width = c['module_width']*c['box_width']
  bwf_height = c['box_height'] + c['fitting_height']
  slice_x = [ (i+1)/11.0*bwf_width for i in range(10) ]
  slice_y = [ (i+1)/11.0*c['box_depth'] for i in range(10) ]
  slice_z = [ (i+1)/11.0*bwf_height for i in range(10) ]
  slice_xyz = (bwf_width, c['box_depth'], bwf_height, 0.0, 0.0, 0.0, slice_z, slice_y, slice_x)
  #
  r_assembly = {}
  r_slice = {}

  r_assembly['bwf_frame_3dconf1'] = bwf_3dconf1
  r_slice['bwf_frame_3dconf1'] = slice_xyz
  #
  r_assembly['bwf_3dconf1'] = bwf_3dconf2
  r_slice['bwf_3dconf1'] = slice_xyz
  #
  return((r_assembly, r_slice))


################################################################
# box_wood_frame_info
################################################################

def bwf_info(c):
  """ create the text info related to the box_wood_frame
  """
  r_info = ""
  r_info += """
1. parameter values:
====================
box_width             : {:0.2f}
box_depth             : {:0.2f}
box_height            : {:0.2f}
module_width          : {:d} (in number of box)
fitting_height        : {:0.2f}
h_plank_width         : {:0.2f}
v_plank_width         : {:0.2f}
plank_height          : {:0.2f}
d_plank_width         : {:0.2f}
d_plank_height        : {:0.2f}
crenel_depth          : {:0.2f}
wall_diagonal_size    : {:0.2f}
tobo_diagonal_size    : {:0.2f}
diagonal_lining_top_height    : {:0.2f}
diagonal_lining_bottom_height : {:0.2f}
router_bit_radius         : {:0.2f}
cutting_extra         : {:0.2f}
slab_thickness        : {:0.2f}
""".format(c['box_width'], c['box_depth'], c['box_height'], c['module_width'],
        c['fitting_height'], c['h_plank_width'], c['v_plank_width'], c['plank_height'],
        c['d_plank_width'], c['d_plank_height'], c['crenel_depth'],
        c['wall_diagonal_size'], c['tobo_diagonal_size'],
        c['diagonal_lining_top_height'], c['diagonal_lining_bottom_height'],
        c['router_bit_radius'], c['cutting_extra'],
        c['slab_thickness'])
  return(r_info)

################################################################
# self test
################################################################

def bwf_self_test():
  """
  This is the non-regression test of box_wood_frame.
  """
  r_tests = [
    ("simple test", "--box_width 600.0"),
    ("just default value", ""),
    ("last test", "--box_height 600.0")]
  return(r_tests)

################################################################
# box_wood_frame design declaration
################################################################

class bwf(cnc25d_api.bare_design):
  """ box_wood_frame design
  """
  def __init__(self, constraint={}):
    """ configure the box_wood_frame design
    """
    self.design_setup(
      s_design_name             = "box_wood_frame_design",
      f_constraint_constructor  = bwf_constraint_constructor,
      f_constraint_check        = bwf_constraint_check,
      f_2d_constructor          = bwf_2d_construction,
      #d_2d_simulation           = {},
      f_3d_constructor          = bwf_3d_construction,
      #f_3d_freecad_constructor  = None,
      f_info                    = bwf_info,
      #l_display_figure_list     = None, # no figure is displey in Tk-window
      l_display_figure_list     = ['bwf_overview'],
      #s_default_simulation      = "",
      l_2d_figure_file_list     = [], # all figures
      l_3d_figure_file_list     = None, # no file
      l_3d_conf_file_list       = [], # all 3dconf
      #l_3d_freecad_file_list    = None,
      f_cli_return_type         = None,
      l_self_test_list          = bwf_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("box_wood_frame says hello!\n")
  my_bwf = bwf()
  #my_bwf.cli()
  #my_bwf.cli("--box_height 600.0")
  my_bwf.cli("--module_width 1")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_bwf.get_fc_obj_3dconf('bwf_3dconf1'))



