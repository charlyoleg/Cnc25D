# box_wood_frame.py
# a wood frame for building a shell or a straw house.
# created by charlyoleg on 2013/05/02
# license: CC BY SA 3.0

"""
box_wood_frame is a parametric design for piece if furniture.
It's actually a single function with the design parameters as input.
The function writes STL and DXF files if an output basename is given as argument.
The function return a FreeCAD Part object of the assembled object.
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
from datetime import datetime
import os, errno
#
# replaced by cnc25d_api
#import cnc_cut_outline
#import export_2d
#
import Part
from FreeCAD import Base

    
################################################################
# the main function to be re-used
################################################################

def box_wood_frame(ai_box_width, ai_box_depth, ai_box_height,
    ai_fitting_height, ai_h_plank_width, ai_v_plank_width, ai_plank_height,
    ai_d_plank_width, ai_d_plank_height, ai_crenel_depth,
    ai_wall_diagonal_size, ai_tobo_diagonal_size,
    ai_diagonal_lining_top_height, ai_diagonal_lining_bottom_height,
    ai_module_width, ai_router_bit_radius, ai_cutting_extra,
    ai_slab_thickness, ai_output_file_basename):
  """
  The main function of the script.
  It generates the pilable box modules according to design parameters
  """
  ## check parameter coherence
  minimal_thickness = 5.0 # only used to check the parameter coherence
  if( (ai_plank_height + ai_v_plank_width + ai_wall_diagonal_size + ai_d_plank_height*math.sqrt(2) + minimal_thickness) > ai_box_width/2 ):
    print("ERR601: Error of parameter coherence. Reduce wall_diagonal_size!\n")
    return(2)
  ## reassigned zero value minor parameters
  ai_tobo_diag_depth=0 # that was previously an argument
  if(ai_tobo_diag_depth==0):
    cai_tobo_diag_depth = 1.0/2*ai_plank_height-0.5
  ### planks
  remove_skin_thickness = 1.0 # use during cut operation to avoid remaining skin
  ## plank dimension
  plank_xz_length = ai_module_width*ai_box_width
  plank_xz_width = ai_h_plank_width+ai_fitting_height
  plank_xz_height = ai_plank_height
  plank_yz_length = ai_box_depth
  plank_yz_width = plank_xz_width
  plank_yz_height = plank_xz_height
  plank_z_length = ai_box_height - 2*ai_h_plank_width - ai_fitting_height + 2*ai_crenel_depth
  plank_z_width = ai_v_plank_width
  plank_z_height = plank_xz_height
  plank_wall_diagonal_length = (ai_wall_diagonal_size+2*ai_crenel_depth)*math.sqrt(2)+2*(ai_d_plank_width-ai_crenel_depth*math.sqrt(2)/2)
  plank_wall_diagonal_width = ai_d_plank_width
  plank_wall_diagonal_height = ai_d_plank_height
  plank_tobo_diagonal_length = ai_tobo_diagonal_size*math.sqrt(2)+2*ai_d_plank_width+0*cai_tobo_diag_depth*math.sqrt(2)/2
  plank_tobo_diagonal_width = ai_d_plank_width
  plank_tobo_diagonal_height = plank_wall_diagonal_height
  plank_hole_cover_length = (ai_d_plank_width*math.sqrt(2)-3*cai_tobo_diag_depth)
  plank_hole_cover_width = ai_d_plank_height
  plank_hole_cover_height = ai_plank_height-cai_tobo_diag_depth
  # rotated plank
  plank_wall_diagonal_in_cuboid_x_length = ai_wall_diagonal_size+ai_d_plank_height*math.sqrt(2)-ai_crenel_depth
  plank_wall_diagonal_in_cuboid_y_width = ai_d_plank_width*math.sqrt(2)
  plank_tobo_diagonal_in_cuboid_x_length = ai_tobo_diagonal_size+ai_d_plank_width*math.sqrt(2)-ai_crenel_depth
  plank_tobo_diagonal_in_cuboid_y_width = ai_d_plank_width*math.sqrt(2)
  ## slab dimension
  slab_top_bottom_single_length = ai_box_width-2*ai_plank_height
  slab_top_bottom_side_length = ai_box_width-1.5*ai_plank_height
  slab_top_bottom_middle_length = ai_box_width-1*ai_plank_height
  slab_top_bottom_width = ai_box_depth-2*ai_plank_height
  slab_top_bottom_height = ai_slab_thickness
  slab_side_length = ai_box_height-2*ai_h_plank_width-ai_fitting_height
  slab_side_left_right_width = ai_box_depth-2*(ai_plank_height+ai_v_plank_width)
  slab_side_rear_single_width = ai_box_width-2*ai_v_plank_width
  slab_side_rear_side_width = ai_box_width-1.5*ai_v_plank_width
  slab_side_rear_middle_width = ai_box_width-1*ai_v_plank_width
  slab_side_height = ai_slab_thickness
  slab_front_length = ai_wall_diagonal_size+ai_d_plank_width*math.sqrt(2)
  slab_front_width = slab_front_length
  slab_front_height = ai_slab_thickness
  ## plank dimension and count
  def plank_description(nai_module_width):
    """
    Depending on the module_width, provides the size (length_x, width_y, height_z) of each plank and their count in the final assembly.
    """
    l_plank_xz_length = nai_module_width*ai_box_width
    r_plank_description = {
      'plank01_xz_bottom'       : [l_plank_xz_length, plank_xz_width,                       plank_xz_height,              2],
      'plank02_xz_top'          : [l_plank_xz_length, plank_xz_width,                       plank_xz_height,              2],
      'plank03_yz_bottom'       : [plank_yz_length, plank_yz_width,                         plank_yz_height,              1+nai_module_width],
      'plank04_yz_top'          : [plank_yz_length, plank_yz_width,                         plank_yz_height,              1+nai_module_width],
      'plank05_z_side'          : [plank_z_length, plank_z_width,                           plank_z_height,               4+2*(1+nai_module_width)],
      'plank06_zx_middle'       : [plank_z_length, plank_z_width,                           plank_z_height,               2*(nai_module_width-1)],
      'plank07_wall_diagonal'   : [plank_wall_diagonal_length, plank_wall_diagonal_width,   plank_wall_diagonal_height,   4*(1+3*nai_module_width)],
      'plank08_tobo_diagonal'   : [plank_tobo_diagonal_length, plank_tobo_diagonal_width,   plank_tobo_diagonal_height,   8*nai_module_width],
      'plank09_hole_cover'      : [plank_hole_cover_length, plank_hole_cover_width,         plank_hole_cover_height,      8+8*nai_module_width],
      'plank21_wall_diag_rot'   : [plank_wall_diagonal_in_cuboid_x_length, plank_wall_diagonal_in_cuboid_y_width, plank_wall_diagonal_height, 0],
      'plank22_tobo_diag_rot'   : [plank_tobo_diagonal_in_cuboid_x_length, plank_tobo_diagonal_in_cuboid_y_width, plank_tobo_diagonal_height, 0],
      'slab51_tobo_single'      : [slab_top_bottom_single_length, slab_top_bottom_width, slab_top_bottom_height, 2 if (nai_module_width==1) else 0],
      'slab52_tobo_side'        : [slab_top_bottom_side_length, slab_top_bottom_width, slab_top_bottom_height, 4 if (nai_module_width>1) else 0],
      'slab53_tobo_middle'      : [slab_top_bottom_middle_length, slab_top_bottom_width, slab_top_bottom_height, 2*(nai_module_width-2) if (nai_module_width>2) else 0],
      'slab54_side_left_right'  : [slab_side_length, slab_side_left_right_width, slab_side_height, 2],
      'slab55_side_rear_single' : [slab_side_length, slab_side_rear_single_width, slab_side_height, 1 if (nai_module_width==1) else 0],
      'slab56_side_rear_side'   : [slab_side_length, slab_side_rear_side_width, slab_side_height, 2 if (nai_module_width>1) else 0],
      'slab57_side_rear_middle' : [slab_side_length, slab_side_rear_middle_width, slab_side_height, nai_module_width-2 if (nai_module_width>2) else 0],
      'slab58_front'            : [slab_front_length, slab_front_width, slab_front_height, 4*nai_module_width]}
    return(r_plank_description)
  def plank_per_height(nai_module_width):
    """
    Create a dictionary with the plank's height as entry and the according plank list for each height
    """
    l_plank_desc = plank_description(nai_module_width)
    l_plank_list = sorted(l_plank_desc.keys())
    r_plank_per_height = {}
    for lp in l_plank_list:
      l_height = l_plank_desc[lp][2]
      l_q = l_plank_desc[lp][3]
      if(l_q>0):
        if(l_height in r_plank_per_height):
          r_plank_per_height[l_height].append(lp)
        else:
          r_plank_per_height[l_height] = [lp]
    return(r_plank_per_height)
  def plank_per_height_and_width(nai_module_width):
    """
    Create a dictionary with the plank's width and height as entry and the according plank list for each width_x_height
    """
    l_plank_desc = plank_description(nai_module_width)
    l_plank_list = sorted(l_plank_desc.keys())
    r_plank_per_height_and_width = {}
    for lp in l_plank_list:
      l_hxw = "{:05.02f}x{:05.02f}".format(l_plank_desc[lp][2], l_plank_desc[lp][1])
      l_q = l_plank_desc[lp][3]
      if(l_q>0):
        if(l_hxw in r_plank_per_height_and_width):
          r_plank_per_height_and_width[l_hxw].append(lp)
        else:
          r_plank_per_height_and_width[l_hxw] = [lp]
    return(r_plank_per_height_and_width)
  ## sub path
  # we use nested functions to reduce the list of arguments. Most of arguments of the mother function are reused there.
  # jonction_plank_xz_with_zx
  def jonction_plank_xz_with_zx(nai_cutting_extra):
    nr = [
      #[1.0/2*ai_v_plank_width-1*nai_cutting_extra, 0*ai_crenel_depth+0*nai_cutting_extra, 1*ai_router_bit_radius],
      [1.0/2*ai_v_plank_width-1*nai_cutting_extra, 0*ai_crenel_depth+0*nai_cutting_extra, 0*ai_router_bit_radius],
      [1.0/2*ai_v_plank_width-1*nai_cutting_extra, 1*ai_crenel_depth+1*nai_cutting_extra, 1*ai_router_bit_radius],
      [2.0/2*ai_v_plank_width+1*nai_cutting_extra, 1*ai_crenel_depth+1*nai_cutting_extra, 1*ai_router_bit_radius],
      [2.0/2*ai_v_plank_width+1*nai_cutting_extra, 0*ai_crenel_depth+0*nai_cutting_extra, 0*ai_router_bit_radius]]
    return(nr)
  # jonction_plank_xz_with_middle_zx
  def jonction_plank_xz_with_middle_zx(nai_cutting_extra):
    nr = [
      [-1.0/2*ai_v_plank_width-1*nai_cutting_extra, 0*ai_crenel_depth+0*nai_cutting_extra, 0*ai_router_bit_radius],
      [-1.0/2*ai_v_plank_width-1*nai_cutting_extra, 1*ai_crenel_depth+1*nai_cutting_extra, 1*ai_router_bit_radius],
      [ 1.0/2*ai_v_plank_width+1*nai_cutting_extra, 1*ai_crenel_depth+1*nai_cutting_extra, 1*ai_router_bit_radius],
      [ 1.0/2*ai_v_plank_width+1*nai_cutting_extra, 0*ai_crenel_depth+0*nai_cutting_extra, 0*ai_router_bit_radius]]
    return(nr)
  #   jonction_plank_xz_with_wall_diagonal
  def jonction_plank_xz_with_wall_diagonal(nai_cutting_extra):
    nr = [
      [ai_v_plank_width+ai_wall_diagonal_size+0*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)-2*nai_cutting_extra, 0*ai_crenel_depth+0*nai_cutting_extra, 0*ai_router_bit_radius],
      [ai_v_plank_width+ai_wall_diagonal_size+1*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)-1*nai_cutting_extra, 1*ai_crenel_depth+1*nai_cutting_extra, 1*ai_router_bit_radius],
      [ai_v_plank_width+ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+1*nai_cutting_extra, 1*ai_crenel_depth+1*nai_cutting_extra, 1*ai_router_bit_radius],
      [ai_v_plank_width+ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+1*nai_cutting_extra, 0*ai_crenel_depth+0*nai_cutting_extra, 0*ai_router_bit_radius]]
    return(nr)
  # jonction_plank_top_xz_with_yz
  def jonction_plank_top_xz_with_yz(nai_cutting_extra):
    nr = [
      [0*ai_plank_height+0*nai_cutting_extra, ai_crenel_depth+2.0/3*(ai_h_plank_width-ai_crenel_depth)+1*nai_cutting_extra, 0*ai_router_bit_radius],
      [1*ai_plank_height+1*nai_cutting_extra, ai_crenel_depth+2.0/3*(ai_h_plank_width-ai_crenel_depth)+1*nai_cutting_extra,-1*ai_router_bit_radius],
      [1*ai_plank_height+1*nai_cutting_extra, ai_crenel_depth+1.0/3*(ai_h_plank_width-ai_crenel_depth)-1*nai_cutting_extra,-1*ai_router_bit_radius],
      [0*ai_plank_height+0*nai_cutting_extra, ai_crenel_depth+1.0/3*(ai_h_plank_width-ai_crenel_depth)-1*nai_cutting_extra, 0*ai_router_bit_radius]]
    return(nr)
  def hole_in_plank_top_xz_for_yz(nai_x_offset, nai_cutting_extra):
    l_outline = [
      [nai_x_offset-1.0/2*ai_plank_height-1*nai_cutting_extra, ai_crenel_depth+2.0/3*(ai_h_plank_width-ai_crenel_depth)+1*nai_cutting_extra,-1*ai_router_bit_radius],
      [nai_x_offset+1.0/2*ai_plank_height+1*nai_cutting_extra, ai_crenel_depth+2.0/3*(ai_h_plank_width-ai_crenel_depth)+1*nai_cutting_extra,-1*ai_router_bit_radius],
      [nai_x_offset+1.0/2*ai_plank_height+1*nai_cutting_extra, ai_crenel_depth+1.0/3*(ai_h_plank_width-ai_crenel_depth)-1*nai_cutting_extra,-1*ai_router_bit_radius],
      [nai_x_offset-1.0/2*ai_plank_height-1*nai_cutting_extra, ai_crenel_depth+1.0/3*(ai_h_plank_width-ai_crenel_depth)-1*nai_cutting_extra,-1*ai_router_bit_radius]]
    l_outline.append([l_outline[0][0], l_outline[0][1], 0]) # close the outline
    l_hole_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(l_outline, 'hole_in_plank_top_xz_for_yz').Edges))
    r_hole_solid = l_hole_face.extrude(Base.Vector(0,0,ai_plank_height+2*remove_skin_thickness)) # straight linear extrusion
    return(r_hole_solid)
  # jonction_plank_bot_xz_with_yz
  def jonction_plank_bot_xz_with_yz(nai_cutting_extra):
    nr = [
      [0*ai_plank_height+0*nai_cutting_extra, 2.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth)+1*nai_cutting_extra, 0*ai_router_bit_radius],
      [1*ai_plank_height+1*nai_cutting_extra, 2.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth)+1*nai_cutting_extra,-1*ai_router_bit_radius],
      [1*ai_plank_height+1*nai_cutting_extra, 1.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth)-1*nai_cutting_extra,-1*ai_router_bit_radius],
      [0*ai_plank_height+0*nai_cutting_extra, 1.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth)-1*nai_cutting_extra, 0*ai_router_bit_radius]]
    return(nr)
  def hole_in_plank_bot_xz_for_yz(nai_x_offset, nai_cutting_extra):
    l_outline = [
      [nai_x_offset-1.0/2*ai_plank_height-1*nai_cutting_extra, 2.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth)+1*nai_cutting_extra,-1*ai_router_bit_radius],
      [nai_x_offset+1.0/2*ai_plank_height+1*nai_cutting_extra, 2.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth)+1*nai_cutting_extra,-1*ai_router_bit_radius],
      [nai_x_offset+1.0/2*ai_plank_height+1*nai_cutting_extra, 1.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth)-1*nai_cutting_extra,-1*ai_router_bit_radius],
      [nai_x_offset-1.0/2*ai_plank_height-1*nai_cutting_extra, 1.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth)-1*nai_cutting_extra,-1*ai_router_bit_radius]]
    l_outline.append([l_outline[0][0], l_outline[0][1], 0]) # close the outline
    l_hole_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(l_outline, 'hole_in_plank_bot_xz_for_yz').Edges))
    r_hole_solid = l_hole_face.extrude(Base.Vector(0,0,ai_plank_height+2*remove_skin_thickness)) # straight linear extrusion
    return(r_hole_solid)
  # jonction_plank_top_yz_with_xz
  def jonction_plank_top_yz_with_xz(nai_cutting_extra):
    nr = [
      [1*ai_plank_height, ai_crenel_depth+2.0/3*(ai_h_plank_width-ai_crenel_depth),-1*ai_router_bit_radius],
      [0*ai_plank_height, ai_crenel_depth+2.0/3*(ai_h_plank_width-ai_crenel_depth), 0*ai_router_bit_radius],
      [0*ai_plank_height, ai_crenel_depth+1.0/3*(ai_h_plank_width-ai_crenel_depth), 0*ai_router_bit_radius],
      [1*ai_plank_height, ai_crenel_depth+1.0/3*(ai_h_plank_width-ai_crenel_depth),-1*ai_router_bit_radius]]
    return(nr)
  # jonction_plank_bot_yz_with_xz
  def jonction_plank_bot_yz_with_xz(nai_cutting_extra):
    nr = [
      [1*ai_plank_height, 2.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth),-1*ai_router_bit_radius],
      [0*ai_plank_height, 2.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth), 0*ai_router_bit_radius],
      [0*ai_plank_height, 1.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth), 0*ai_router_bit_radius],
      [1*ai_plank_height, 1.0/3*(ai_h_plank_width+ai_fitting_height-ai_crenel_depth),-1*ai_router_bit_radius]]
    return(nr)
  # jonction_plank_xz_fitting
  def jonction_plank_xz_fitting(nai_cutting_extra):
    nr = [
      [1.0/4*ai_box_width-1.0/2*ai_fitting_height, 0*ai_fitting_height, 1.0/2*ai_fitting_height],
      [1.0/4*ai_box_width-0.0/2*ai_fitting_height, 1*ai_fitting_height, 1.0/2*ai_fitting_height]]
    return(nr)
  # jonction_plank_z_side_with_xz
  def jonction_plank_z_side_with_xz(nai_cutting_extra):
    act = (1+math.sqrt(2))*ai_router_bit_radius
    nr = [
      [0*ai_crenel_depth,     2.0/2*ai_v_plank_width,     1*ai_router_bit_radius],
      [0*ai_crenel_depth,     1.0/2*ai_v_plank_width,     1*ai_router_bit_radius],
      #[1*ai_crenel_depth,    1.0/2*ai_v_plank_width,     1*ai_router_bit_radius],
      [1*ai_crenel_depth+act, 1.0/2*ai_v_plank_width,     1*ai_router_bit_radius],
      [1*ai_crenel_depth,     1.0/2*ai_v_plank_width-act, 0*ai_router_bit_radius],
      [1*ai_crenel_depth,     0.0/2*ai_v_plank_width,     0*ai_router_bit_radius]]
    return(nr)
  # jonction_plank_z_with_wall_diagonal
  def jonction_plank_z_with_wall_diagonal(nai_cutting_extra):
    nr = cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra), -1*ai_v_plank_width+1*ai_crenel_depth, 1, ai_v_plank_width, -1)
    return(nr)
  # jonction_plank_wall_diagonal
  def jonction_plank_wall_diagonal(nai_cutting_extra):
    nr = [
      [1*ai_d_plank_width-1*ai_crenel_depth*math.sqrt(2)/2, 1*ai_d_plank_width+0*ai_crenel_depth*math.sqrt(2)/2, 1*ai_router_bit_radius],
      [0*ai_d_plank_width-0*ai_crenel_depth*math.sqrt(2)/2, 0*ai_d_plank_width+1*ai_crenel_depth*math.sqrt(2)/2, 1*ai_router_bit_radius],
      [0*ai_d_plank_width+1*ai_crenel_depth*math.sqrt(2)/2, 0*ai_d_plank_width+0*ai_crenel_depth*math.sqrt(2)/2, 0*ai_router_bit_radius]]
    return(nr)
  # jonction_plank_tobo_diagonal
  def jonction_plank_tobo_diagonal(nai_cutting_extra):
    #l_soft_external = cai_tobo_diag_depth/2
    l_soft_external = 0
    nr = [
      [1*ai_d_plank_width+0*cai_tobo_diag_depth*math.sqrt(2)/2, 1*ai_d_plank_width+0*cai_tobo_diag_depth*math.sqrt(2)/2, 1*l_soft_external],
      [1*ai_d_plank_width-1*cai_tobo_diag_depth*math.sqrt(2)/2, 1*ai_d_plank_width-1*cai_tobo_diag_depth*math.sqrt(2)/2,-1*ai_router_bit_radius],
      [1*ai_d_plank_width-2*cai_tobo_diag_depth*math.sqrt(2)/2, 1*ai_d_plank_width-0*cai_tobo_diag_depth*math.sqrt(2)/2, 1*l_soft_external],
      [0*ai_d_plank_width+(1.5-1)*cai_tobo_diag_depth*math.sqrt(2)/2, 0*ai_d_plank_width+(1.5+1)*cai_tobo_diag_depth*math.sqrt(2)/2, 1*l_soft_external],
      [0*ai_d_plank_width+1.5*cai_tobo_diag_depth*math.sqrt(2)/2,     0*ai_d_plank_width+1.5*cai_tobo_diag_depth*math.sqrt(2)/2,-1*ai_router_bit_radius],
      [0*ai_d_plank_width+0*cai_tobo_diag_depth*math.sqrt(2)/2,       0*ai_d_plank_width+0*cai_tobo_diag_depth*math.sqrt(2)/2, 1*l_soft_external]]
    return(nr)
  #print("dbg412: jonction_plank_tobo_diagonal", jonction_plank_tobo_diagonal)
  # jonction_plank_zx_with_wall_diagonal
  def jonction_plank_zx_with_wall_diagonal(nai_cutting_extra):
    nr = cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra), -1*ai_v_plank_width+1*ai_crenel_depth, 1, 0*ai_v_plank_width, 1)
    return(nr)
  # jonction_plank_zx_with_xz
  def jonction_plank_zx_with_xz(nai_cutting_extra):
    nr = [
      [0, 1*ai_v_plank_width, 1*ai_router_bit_radius],
      [0, 0*ai_v_plank_width, 1*ai_router_bit_radius]]
    return(nr)
  #   jonction_slab_side_with_wall_diagonal_horizontal
  def jonction_slab_side_with_wall_diagonal_horizontal(nai_cutting_extra):
    act = (1+math.sqrt(2))*ai_router_bit_radius
    nr = [
      [ai_wall_diagonal_size+0*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)-1*nai_cutting_extra,  0*ai_crenel_depth+1*nai_cutting_extra, -1*ai_router_bit_radius],
      [ai_wall_diagonal_size+1*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra, -1*ai_crenel_depth+0*nai_cutting_extra, 1*ai_router_bit_radius],
      [ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra, -1*ai_crenel_depth+0*nai_cutting_extra, 1*ai_router_bit_radius],
      #[ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra,  0*ai_crenel_depth+1*nai_cutting_extra,-1*ai_router_bit_radius]]
      [ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra,  0*ai_crenel_depth+act+1*nai_cutting_extra, 1*ai_router_bit_radius],
      [ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+act+0*nai_cutting_extra,  0*ai_crenel_depth+1*nai_cutting_extra, 0*ai_router_bit_radius]]
    return(nr)
  #   jonction_slab_side_with_wall_diagonal_vertical
  def jonction_slab_side_with_wall_diagonal_vertical(nai_cutting_extra):
    act = (1+math.sqrt(2))*ai_router_bit_radius
    nr = [
      #[ 0*ai_crenel_depth+1*nai_cutting_extra, ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra, -1*ai_router_bit_radius],
      [ 0*ai_crenel_depth+1*nai_cutting_extra, ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+act+0*nai_cutting_extra,  0*ai_router_bit_radius],
      [ 0*ai_crenel_depth+act+1*nai_cutting_extra, ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra,  1*ai_router_bit_radius],
      [-1*ai_crenel_depth+0*nai_cutting_extra, ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra,  1*ai_router_bit_radius],
      [-1*ai_crenel_depth+0*nai_cutting_extra, ai_wall_diagonal_size+1*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra,  1*ai_router_bit_radius],
      [ 0*ai_crenel_depth+1*nai_cutting_extra, ai_wall_diagonal_size+0*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)-1*nai_cutting_extra, -1*ai_router_bit_radius]]
    return(nr)

  ## hole sub   
  # plank_xz_hole plank_yz_hole
  def plank_xz_yz_hole(nai_box_nb, nai_cutting_extra, nai_box_size):
    hdx = (ai_d_plank_width*math.sqrt(2)-(1+1.5)*cai_tobo_diag_depth)
    hdy = ai_d_plank_height
    hpx = ai_tobo_diagonal_size + cai_tobo_diag_depth + 0*ai_plank_height
    #hpy = ai_diagonal_lining_height
    act = (1+math.sqrt(2))*ai_router_bit_radius
    plank_xz_hole_outline = [ # the y position is not set yet for an easier re-use for other planks
      [hpx+0*hdx-1*nai_cutting_extra, 0*hdy-act-1*nai_cutting_extra, 1*ai_router_bit_radius],
      [hpx+0*hdx+act-1*nai_cutting_extra, 0*hdy-1*nai_cutting_extra, 0*ai_router_bit_radius],
      [hpx+1*hdx-act+1*nai_cutting_extra, 0*hdy-1*nai_cutting_extra, 0*ai_router_bit_radius],
      [hpx+1*hdx+1*nai_cutting_extra, 0*hdy-act-1*nai_cutting_extra, 1*ai_router_bit_radius],
      [hpx+1*hdx+1*nai_cutting_extra, 1*hdy+act+1*nai_cutting_extra, 1*ai_router_bit_radius],
      [hpx+1*hdx-act+1*nai_cutting_extra, 1*hdy+1*nai_cutting_extra, 0*ai_router_bit_radius],
      [hpx+0*hdx+act-1*nai_cutting_extra, 1*hdy+1*nai_cutting_extra, 0*ai_router_bit_radius],
      [hpx+0*hdx-1*nai_cutting_extra, 1*hdy+act+1*nai_cutting_extra, 1*ai_router_bit_radius]]
    plank_xz_hole_outline.append([plank_xz_hole_outline[0][0], plank_xz_hole_outline[0][1], 0]) # close the outline
    plank_xz_hole_shape = cnc25d_api.cnc_cut_outline_fc(plank_xz_hole_outline, 'plank_xz_yz_hole')
    plank_xz_hole_wire = Part.Wire(plank_xz_hole_shape.Edges)
    plank_xz_hole_face = Part.Face(plank_xz_hole_wire)
    plank_xz_hole_face.translate(Base.Vector(0,0,-remove_skin_thickness))
    plank_xz_hole_solid = plank_xz_hole_face.extrude(Base.Vector(0,0,ai_plank_height+2*remove_skin_thickness)) # straight linear extrusion
    ## array of holes
    # duplicate the holes
    l_hole_array = []
    for i in range(2*nai_box_nb):
      l_hole_array.append(plank_xz_hole_solid.copy())
    ## place the holes
    l_hole_array[0].translate(Base.Vector(0*nai_box_size+ai_plank_height,0,0))
    for i in range(nai_box_nb-1):
      l_hole_array[2*i+1].translate(Base.Vector((i+1)*nai_box_size-1.0/2*ai_plank_height-hdx-2*hpx,0,0))
      l_hole_array[2*i+2].translate(Base.Vector((i+1)*nai_box_size+1.0/2*ai_plank_height,0,0))
    l_hole_array[2*nai_box_nb-1].translate(Base.Vector(nai_box_nb*nai_box_size-ai_plank_height-hdx-2*hpx,0,0))
    r_plank_xz_hole_solid = Part.makeCompound(l_hole_array)
    return(r_plank_xz_hole_solid)
  #Part.show(plank_xz_yz_hole(1,0, ai_box_width))
  def plank_xz_top_hole(nai_box_nb, nai_cutting_extra):
    plank_xz_top_hole_solid =  plank_xz_yz_hole(nai_box_nb, nai_cutting_extra, ai_box_width)
    plank_xz_top_hole_solid.translate(Base.Vector(0,ai_diagonal_lining_top_height,0))
    for i in range(nai_box_nb-1):
      plank_xz_top_hole_solid = plank_xz_top_hole_solid.fuse(hole_in_plank_top_xz_for_yz((i+1)*ai_box_width, nai_cutting_extra))
    return(plank_xz_top_hole_solid)
  def plank_xz_bottom_hole(nai_box_nb, nai_cutting_extra):
    #plank_xz_bottom_hole_solid = plank_xz_top_hole_solid(nai_cutting_extra).copy()
    plank_xz_bottom_hole_solid = plank_xz_yz_hole(nai_box_nb, nai_cutting_extra, ai_box_width)
    plank_xz_bottom_hole_solid.translate(Base.Vector(0,ai_h_plank_width+ai_fitting_height-ai_d_plank_height-ai_diagonal_lining_bottom_height,0))
    for i in range(nai_box_nb-1):
      plank_xz_bottom_hole_solid = plank_xz_bottom_hole_solid.fuse(hole_in_plank_bot_xz_for_yz((i+1)*ai_box_width, nai_cutting_extra))
    return(plank_xz_bottom_hole_solid)
  #Part.show(plank_xz_top_hole(2,0))
  def plank_yz_top_hole(nai_box_nb, nai_cutting_extra):
    plank_xz_top_hole_solid =  plank_xz_yz_hole(nai_box_nb, nai_cutting_extra, ai_box_depth)
    plank_xz_top_hole_solid.translate(Base.Vector(0,ai_diagonal_lining_top_height,0))
    for i in range(nai_box_nb-1):
      plank_xz_top_hole_solid = plank_xz_top_hole_solid.fuse(hole_in_plank_top_xz_for_yz((i+1)*ai_box_width, nai_cutting_extra))
    return(plank_xz_top_hole_solid)
  def plank_yz_bottom_hole(nai_box_nb, nai_cutting_extra):
    #plank_xz_bottom_hole_solid = plank_xz_top_hole_solid(nai_cutting_extra).copy()
    plank_xz_bottom_hole_solid = plank_xz_yz_hole(nai_box_nb, nai_cutting_extra, ai_box_depth)
    plank_xz_bottom_hole_solid.translate(Base.Vector(0,ai_h_plank_width+ai_fitting_height-ai_d_plank_height-ai_diagonal_lining_bottom_height,0))
    for i in range(nai_box_nb-1):
      plank_xz_bottom_hole_solid = plank_xz_bottom_hole_solid.fuse(hole_in_plank_bot_xz_for_yz((i+1)*ai_box_width, nai_cutting_extra))
    return(plank_xz_bottom_hole_solid)
  #Part.show(plank_yz_top_hole(2,0))
  ##
  ## plank_xz_top
  def plank_xz_top(nai_module_width, nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_xz_top
    """
    # plank_xz_top_outline
    plank_xz_top_outline = []
    plank_xz_top_outline.append([0*ai_box_width, 0*ai_h_plank_width, 0*ai_router_bit_radius]) #0
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_zx(nai_cutting_extra),             0*ai_box_width, 1)) #1-4
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),  0*ai_box_width, 1)) #5-8
    for i in range(nai_module_width-1):
      plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),  (i+1)*ai_box_width+1.0/2*ai_v_plank_width, -1))
      plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_middle_zx(nai_cutting_extra),      (i+1)*ai_box_width,  1))
      plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),  (i+1)*ai_box_width-1.0/2*ai_v_plank_width, 1))
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),  nai_module_width*ai_box_width, -1)) #9-12
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_zx(nai_cutting_extra),             nai_module_width*ai_box_width, -1)) #13-16
    plank_xz_top_outline.append([nai_module_width*ai_box_width, 0*ai_plank_height, 0*ai_router_bit_radius]) #17
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_top_xz_with_yz(nai_cutting_extra),         nai_module_width*ai_box_width, -1)) #18-21
    plank_xz_top_outline.append([nai_module_width*ai_box_width, 1*ai_h_plank_width, 0*ai_router_bit_radius]) #22
    for i in range(nai_module_width):
      plank_xz_top_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_fitting(nai_cutting_extra)[::-1],    (nai_module_width-i)*ai_box_width, -1, ai_h_plank_width, 1)) #23-24
      plank_xz_top_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_fitting(nai_cutting_extra)[::-1],  (nai_module_width-1-i)*ai_box_width,  1, ai_h_plank_width, 1)) #25-26
    plank_xz_top_outline.append([0*ai_box_width, 1*ai_h_plank_width, 0*ai_router_bit_radius]) #27
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_top_xz_with_yz(nai_cutting_extra),         0*ai_box_width,  1)) #28-31
    plank_xz_top_outline.append([plank_xz_top_outline[0][0], plank_xz_top_outline[0][1], 0]) # close the outline
    # extrusion
    plank_xz_top_shape = cnc25d_api.cnc_cut_outline_fc(plank_xz_top_outline, 'plank_xz_top')
    plank_xz_top_wire = Part.Wire(plank_xz_top_shape.Edges)
    plank_xz_top_face = Part.Face(plank_xz_top_wire)
    plank_xz_top_solid = plank_xz_top_face.extrude(Base.Vector(0,0,ai_plank_height)) # straight linear extrusion
    # final build of  the plank plank_xz_top
    plank_xz_top_solid = plank_xz_top_solid.cut(plank_xz_top_hole(nai_module_width, nai_cutting_extra))
    return(plank_xz_top_solid)
  # visualize
  #Part.show(plank_xz_top(3,0)) # works only with FreeCAD GUI, ignore otherwise
  ## plank_xz_bottom
  def plank_xz_bottom(nai_module_width, nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_xz_bottom
    """
    # plank_xz_bottom_outline
    plank_xz_bottom_outline = []
    plank_xz_bottom_outline.append([0*ai_box_width, 0*(ai_h_plank_width+ai_fitting_height), 0*ai_router_bit_radius]) #0
    for i in range(nai_module_width):
      plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_fitting(nai_cutting_extra),              i*ai_box_width, 1)) #1-2
      plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_fitting(nai_cutting_extra),          (i+1)*ai_box_width,-1))
    plank_xz_bottom_outline.append([nai_module_width*ai_box_width, 0*(ai_h_plank_width+ai_fitting_height), 0*ai_router_bit_radius])
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_bot_xz_with_yz(nai_cutting_extra),          nai_module_width*ai_box_width, -1))
    plank_xz_bottom_outline.append([nai_module_width*ai_box_width, 1*(ai_h_plank_width+ai_fitting_height), 0*ai_router_bit_radius])
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_zx(nai_cutting_extra),             nai_module_width*ai_box_width, -1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),  nai_module_width*ai_box_width, -1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    for i in range(nai_module_width-1):
      plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),  (nai_module_width-i-1)*ai_box_width-1.0/2*ai_v_plank_width,  1, 1*(ai_h_plank_width+ai_fitting_height), -1))
      plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_middle_zx(nai_cutting_extra),      (nai_module_width-i-1)*ai_box_width, 1, 1*(ai_h_plank_width+ai_fitting_height), -1))
      plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),  (nai_module_width-i-1)*ai_box_width+1.0/2*ai_v_plank_width, -1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),  0*ai_box_width,  1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_zx(nai_cutting_extra),             0*ai_box_width,  1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    plank_xz_bottom_outline.append([0*ai_box_width, 1*(ai_h_plank_width+ai_fitting_height), 0*ai_router_bit_radius])
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_bot_xz_with_yz(nai_cutting_extra),          0*ai_box_width,  1))
    plank_xz_bottom_outline.append([plank_xz_bottom_outline[0][0], plank_xz_bottom_outline[0][1], 0]) # close the outline
    # extrusion
    #plank_xz_bottom_shape = cnc25d_api.cnc_cut_outline_fc(plank_xz_bottom_outline, 'plank_xz_bottom')
    #plank_xz_bottom_wire = Part.Wire(plank_xz_bottom_shape.Edges)
    #plank_xz_bottom_face = Part.Face(plank_xz_bottom_wire)
    #plank_xz_bottom_face = Part.Face(Part.Wire(plank_xz_bottom_shape.Edges))
    plank_xz_bottom_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(plank_xz_bottom_outline, 'plank_xz_bottom').Edges))
    plank_xz_bottom_solid = plank_xz_bottom_face.extrude(Base.Vector(0,0,ai_plank_height)) # straight linear extrusion
    #print("dbg601: ai_h_plank_width+ai_fitting_height-hdy-ai_diagonal_lining_bottom_height:", ai_h_plank_width, ai_fitting_height, hdy, ai_diagonal_lining_bottom_height)
    plank_xz_bottom_solid = plank_xz_bottom_solid.cut(plank_xz_bottom_hole(nai_module_width, nai_cutting_extra))
    return(plank_xz_bottom_solid)
  # visualize
  #Part.show(plank_xz_bottom(3, 0)) # works only with FreeCAD GUI, ignore otherwise
  ## plank_yz_top
  def plank_yz_top(nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_yz_top
    """
    # plank_yz_top_outline
    plank_yz_top_outline = []
    plank_yz_top_outline.append([0*ai_box_depth+1*ai_plank_height, 0*ai_h_plank_width, 0*ai_router_bit_radius]) #0
    plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_zx(nai_cutting_extra),            0*ai_box_depth+1*ai_plank_height, 1)) #1-4
    plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra), 0*ai_box_depth+1*ai_plank_height, 1)) #5-8
    plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra), 1*ai_box_depth-1*ai_plank_height, -1)) #9-12
    plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_zx(nai_cutting_extra),            1*ai_box_depth-1*ai_plank_height, -1)) #13-16
    plank_yz_top_outline.append([1*ai_box_depth-1*ai_plank_height, 0*ai_plank_height, 0*ai_router_bit_radius]) #17
    plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_top_yz_with_xz(nai_cutting_extra),            1*ai_box_depth, -1)) #18-21
    plank_yz_top_outline.append([1*ai_box_depth-1*ai_plank_height, 1*ai_h_plank_width, 0*ai_router_bit_radius]) #22
    plank_yz_top_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_fitting(nai_cutting_extra)[::-1], 1*ai_box_depth, -1, ai_h_plank_width, 1)) #23-24
    plank_yz_top_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_fitting(nai_cutting_extra)[::-1], 0*ai_box_depth,  1, ai_h_plank_width, 1)) #25-26
    plank_yz_top_outline.append([0*ai_box_depth+1*ai_plank_height, 1*ai_h_plank_width, 0*ai_router_bit_radius]) #27
    plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_top_yz_with_xz(nai_cutting_extra),            0*ai_box_depth,  1)) #28-31
    plank_yz_top_outline.append([plank_yz_top_outline[0][0], plank_yz_top_outline[0][1], 0]) # close the outline
    # extrusion
    plank_yz_top_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(plank_yz_top_outline, 'plank_yz_top').Edges))
    plank_yz_top_solid = plank_yz_top_face.extrude(Base.Vector(0,0,ai_plank_height)) # straight linear extrusion
    plank_yz_top_solid = plank_yz_top_solid.cut(plank_yz_top_hole(1, nai_cutting_extra))
    return(plank_yz_top_solid)
  #Part.show(plank_yz_top(0))
  ## plank_yz_bottom
  def plank_yz_bottom(nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_yz_bottom
    """
    # plank_yz_bottom_outline
    plank_yz_bottom_outline = []
    plank_yz_bottom_outline.append([0*ai_box_depth+1*ai_plank_height, 0*(ai_h_plank_width+ai_fitting_height), 0*ai_router_bit_radius]) #0
    plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_fitting(nai_cutting_extra), 0*ai_box_depth, 1)) #1-2
    plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_fitting(nai_cutting_extra), 1*ai_box_depth,-1))
    plank_yz_bottom_outline.append([1*ai_box_depth-1*ai_plank_height, 0*(ai_h_plank_width+ai_fitting_height), 0*ai_router_bit_radius])
    plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_bot_yz_with_xz(nai_cutting_extra),  1*ai_box_depth, -1))
    plank_yz_bottom_outline.append([1*ai_box_depth-1*ai_plank_height, 1*(ai_h_plank_width+ai_fitting_height), 0*ai_router_bit_radius])
    plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_zx(nai_cutting_extra),
      1*ai_box_depth-1*ai_plank_height, -1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),
      1*ai_box_depth-1*ai_plank_height, -1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(nai_cutting_extra),
      0*ai_box_depth+1*ai_plank_height,  1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_zx(nai_cutting_extra),
      0*ai_box_depth+1*ai_plank_height,  1, 1*(ai_h_plank_width+ai_fitting_height), -1))
    plank_yz_bottom_outline.append([0*ai_box_depth+1*ai_plank_height, 1*(ai_h_plank_width+ai_fitting_height), 0*ai_router_bit_radius])
    plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_bot_yz_with_xz(nai_cutting_extra),  0*ai_box_depth,  1))
    plank_yz_bottom_outline.append([plank_yz_bottom_outline[0][0], plank_yz_bottom_outline[0][1], 0]) # close the outline
    # extrusion
    plank_yz_bottom_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(plank_yz_bottom_outline, 'plank_yz_bottom').Edges))
    plank_yz_bottom_solid = plank_yz_bottom_face.extrude(Base.Vector(0,0,ai_plank_height)) # straight linear extrusion
    #plank_xz_bottom_hole_solid.translate(Base.Vector(0,ai_h_plank_width+ai_fitting_height-hdy-ai_diagonal_lining_bottom_height,0))
    plank_yz_bottom_solid = plank_yz_bottom_solid.cut(plank_yz_bottom_hole(1, nai_cutting_extra))
    return(plank_yz_bottom_solid)
  # visualize
  #Part.show(plank_yz_bottom(0)) # works only with FreeCAD GUI, ignore otherwise
  ## plank_z_side
  def plank_z_side(nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_z_side
    """
    # plank_z_side_outline
    #plank_z_side_length = ai_box_height - 2*ai_h_plank_width - ai_fitting_height + 2*ai_crenel_depth
    plank_z_side_length = plank_z_length
    plank_z_side_outline = []
    plank_z_side_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_z_side_with_xz(nai_cutting_extra), 0*plank_z_side_length, 1))
    plank_z_side_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_z_side_with_xz(nai_cutting_extra), 1*plank_z_side_length,-1))
    plank_z_side_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_z_with_wall_diagonal(nai_cutting_extra), 1*plank_z_side_length,-1))
    plank_z_side_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_z_with_wall_diagonal(nai_cutting_extra), 0*plank_z_side_length, 1))
    plank_z_side_outline.append([plank_z_side_outline[0][0], plank_z_side_outline[0][1], 0]) # close the outline
    # extrusion
    plank_z_side_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(plank_z_side_outline, 'plank_z_side').Edges))
    plank_z_side_solid = plank_z_side_face.extrude(Base.Vector(0,0,ai_plank_height))
    return(plank_z_side_solid)
  #Part.show(plank_z_side(0))
  ## plank_wall_diagonal
  def plank_wall_diagonal(nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_wall_diagonal
    """
    #plank_wall_diagonal_length = (ai_wall_diagonal_size+2*ai_crenel_depth)*math.sqrt(2)+2*(ai_d_plank_width-ai_crenel_depth*math.sqrt(2)/2)
    #print("dbg825: plank_wall_diagonal_length:", plank_wall_diagonal_length)
    plank_wall_diagonal_outline = []
    plank_wall_diagonal_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_wall_diagonal(nai_cutting_extra), 1*plank_wall_diagonal_length, -1))
    plank_wall_diagonal_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_wall_diagonal(nai_cutting_extra), 0*plank_wall_diagonal_length,  1))
    plank_wall_diagonal_outline.append([plank_wall_diagonal_outline[0][0], plank_wall_diagonal_outline[0][1], 0]) # close the outline
    plank_wall_diagonal_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(plank_wall_diagonal_outline, 'plank_wall_diagonal').Edges))
    plank_wall_diagonal_solid = plank_wall_diagonal_face.extrude(Base.Vector(0,0,ai_d_plank_height))
    return(plank_wall_diagonal_solid)
  #Part.show(plank_wall_diagonal(0))
  def plank_wall_diagonal_in_cuboid(nai_cutting_extra):
    """ rotate plank_wall_diagonal from a convenient cnc orientation to a convenient assembly orientation
    """
    r_plank = plank_wall_diagonal(nai_cutting_extra)
    r_plank.rotate(Base.Vector(0,ai_crenel_depth*math.sqrt(2)/2,0), Base.Vector(0,0,1),45)
    r_plank.translate(Base.Vector(-ai_crenel_depth,-ai_crenel_depth*math.sqrt(2)/2,0))
    return(r_plank)
  #Part.show(plank_wall_diagonal_in_cuboid(0))
  ## plank_tobo_diagonal
  def plank_tobo_diagonal(nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_tobo_diagonal
    """
    #plank_tobo_diagonal_length = ai_tobo_diagonal_size*math.sqrt(2)+2*ai_d_plank_width+0*cai_tobo_diag_depth*math.sqrt(2)/2
    plank_tobo_diagonal_outline = []
    plank_tobo_diagonal_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_tobo_diagonal(nai_cutting_extra), 1*plank_tobo_diagonal_length, -1))
    plank_tobo_diagonal_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_tobo_diagonal(nai_cutting_extra), 0*plank_tobo_diagonal_length,  1))
    plank_tobo_diagonal_outline.append([plank_tobo_diagonal_outline[0][0], plank_tobo_diagonal_outline[0][1], 0]) # close the outline
    plank_tobo_diagonal_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(plank_tobo_diagonal_outline, 'plank_tobo_diagonal').Edges))
    plank_tobo_diagonal_solid = plank_tobo_diagonal_face.extrude(Base.Vector(0,0,ai_d_plank_height))
    return(plank_tobo_diagonal_solid)
  #Part.show(plank_tobo_diagonal(0))
  def plank_tobo_diagonal_in_cuboid(nai_cutting_extra):
    """ rotate plank_tobo_diagonal from a convenient cnc orientation to a convenient assembly orientation
    """
    r_plank = plank_tobo_diagonal(nai_cutting_extra)
    r_plank.rotate(Base.Vector(0*cai_tobo_diag_depth*math.sqrt(2)/2,0,0), Base.Vector(0,0,1),45)
    #r_plank.translate(Base.Vector(-cai_tobo_diag_depth*math.sqrt(2)/2,0,0))
    return(r_plank)
  #Part.show(plank_tobo_diagonal_in_cuboid(0))
  ## plank_zx_middle
  def plank_zx_middle(nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_zx_middle
    """
    #plank_z_side_length = ai_box_height - 2*ai_h_plank_width - ai_fitting_height + 2*ai_crenel_depth
    plank_z_side_length = plank_z_length
    plank_zx_middle_outline = []
    plank_zx_middle_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_zx_with_wall_diagonal(nai_cutting_extra), 0*plank_z_side_length, 1, 0*ai_v_plank_width, 1))
    plank_zx_middle_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_zx_with_wall_diagonal(nai_cutting_extra), 1*plank_z_side_length,-1, 0*ai_v_plank_width, 1))
    plank_zx_middle_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_zx_with_xz(nai_cutting_extra), 1*plank_z_side_length,-1))
    plank_zx_middle_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_zx_with_wall_diagonal(nai_cutting_extra), 1*plank_z_side_length,-1, 1*ai_v_plank_width, -1))
    plank_zx_middle_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_zx_with_wall_diagonal(nai_cutting_extra), 0*plank_z_side_length, 1, 1*ai_v_plank_width, -1))
    plank_zx_middle_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_zx_with_xz(nai_cutting_extra), 0*plank_z_side_length, 1))
    plank_zx_middle_outline.append([plank_zx_middle_outline[0][0], plank_zx_middle_outline[0][1], 0]) # close the outline
    plank_zx_middle_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(plank_zx_middle_outline, 'plank_zx_middle').Edges))
    plank_zx_middle_solid = plank_zx_middle_face.extrude(Base.Vector(0,0,ai_plank_height))
    return(plank_zx_middle_solid)
  #Part.show(plank_zx_middle(0))
  ## plank_hole_cover
  def plank_hole_cover(nai_cutting_extra):
    """ Create the FreeCAD Part Object plank_hole_cover
    """
    hdx = plank_hole_cover_length
    hdy = plank_hole_cover_width
    hdz = plank_hole_cover_height
    plank_hole_cover_outline = []
    plank_hole_cover_outline.append([0*hdx, 0*hdy, 0])
    plank_hole_cover_outline.append([1*hdx, 0*hdy, 0])
    plank_hole_cover_outline.append([1*hdx, 1*hdy, 0])
    plank_hole_cover_outline.append([0*hdx, 1*hdy, 0])
    plank_hole_cover_outline.append([plank_hole_cover_outline[0][0], plank_hole_cover_outline[0][1], 0]) # close the outline
    plank_hole_cover_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(plank_hole_cover_outline, 'plank_hole_cover').Edges))
    r_plank_hole_cover_solid = plank_hole_cover_face.extrude(Base.Vector(0,0,hdz))
    return(r_plank_hole_cover_solid)
  #Part.show(plank_hole_cover(0))
  ## slab_top_bottom
  def slab_top_bottom(nai_type, nai_cutting_extra):
    """ Create the FreeCAD Part Object slab_top_bottom
    """
    if(nai_type=='single'):
      slab_length = slab_top_bottom_single_length
    elif(nai_type=='side'):
      slab_length = slab_top_bottom_side_length
    elif(nai_type=='middle'):
      slab_length = slab_top_bottom_middle_length
    slab_width = slab_top_bottom_width
    slab_top_bottom_outline = []
    slab_top_bottom_outline.append([0*slab_length+1*nai_cutting_extra, 0*slab_width+1*nai_cutting_extra, 0])
    slab_top_bottom_outline.append([1*slab_length-1*nai_cutting_extra, 0*slab_width+1*nai_cutting_extra, 0])
    slab_top_bottom_outline.append([1*slab_length-1*nai_cutting_extra, 1*slab_width-1*nai_cutting_extra, 0])
    slab_top_bottom_outline.append([0*slab_length+1*nai_cutting_extra, 1*slab_width-1*nai_cutting_extra, 0])
    slab_top_bottom_outline.append([slab_top_bottom_outline[0][0], slab_top_bottom_outline[0][1], 0]) # close the outline
    slab_top_bottom_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(slab_top_bottom_outline, 'slab_top_bottom').Edges))
    r_slab_top_bottom_solid = slab_top_bottom_face.extrude(Base.Vector(0,0,slab_top_bottom_height))
    return(r_slab_top_bottom_solid)
  #Part.show(slab_top_bottom('single',0))
  ## slab_left_right and slab_rear
  def slab_side(nai_type, nai_cutting_extra):
    """ Create the FreeCAD Part Object slab_side
    """
    slab_length = slab_side_length
    if(nai_type=='left_right'):
      slab_width = slab_side_left_right_width
    elif(nai_type=='rear_single'):
      slab_width = slab_side_rear_single_width
    elif(nai_type=='rear_side'):
      slab_width = slab_side_rear_side_width
    elif(nai_type=='rear_middle'):
      slab_width = slab_side_rear_middle_width
    slab_side_outline = []
    slab_side_outline.append([0*slab_length+1*nai_cutting_extra, 0*slab_width+1*nai_cutting_extra, 0])
    slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_horizontal(nai_cutting_extra), 0*slab_length, 1, 0*slab_width, 1))
    slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_horizontal(nai_cutting_extra), 1*slab_length,-1, 0*slab_width, 1))
    slab_side_outline.append([1*slab_length-1*nai_cutting_extra, 0*slab_width+1*nai_cutting_extra, 0])
    slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_vertical(nai_cutting_extra), 1*slab_length,-1, 0*slab_width, 1))
    slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_vertical(nai_cutting_extra), 1*slab_length,-1, 1*slab_width,-1))
    slab_side_outline.append([1*slab_length-1*nai_cutting_extra, 1*slab_width-1*nai_cutting_extra, 0])
    slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_horizontal(nai_cutting_extra), 1*slab_length, -1, 1*slab_width,-1))
    slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_horizontal(nai_cutting_extra), 0*slab_length,  1, 1*slab_width,-1))
    slab_side_outline.append([0*slab_length+1*nai_cutting_extra, 1*slab_width-1*nai_cutting_extra, 0])
    slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_vertical(nai_cutting_extra), 0*slab_length, 1, 1*slab_width,-1))
    slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_vertical(nai_cutting_extra), 0*slab_length, 1, 0*slab_width, 1))
    slab_side_outline.append([slab_side_outline[0][0], slab_side_outline[0][1], 0]) # close the outline
    slab_side_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(slab_side_outline, 'slab_side').Edges))
    r_slab_side_solid = slab_side_face.extrude(Base.Vector(0,0,ai_slab_thickness))
    return(r_slab_side_solid)
  #Part.show(slab_side('left_right', 0))
  ## slab_front
  def slab_front(nai_cutting_extra):
    """ Create the FreeCAD Part Object slab_front
    """
    slab_front_outline = []
    slab_front_outline.append([0+1*nai_cutting_extra, 0+1*nai_cutting_extra, 0])
    slab_front_outline.append([ai_wall_diagonal_size+0*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)-1*nai_cutting_extra, 0*ai_crenel_depth+1*nai_cutting_extra, -1*ai_router_bit_radius])
    slab_front_outline.append([ai_wall_diagonal_size+1*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra, -1*ai_crenel_depth+0*nai_cutting_extra, 1*ai_router_bit_radius])
    slab_front_outline.append([ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra, -1*ai_crenel_depth+0*nai_cutting_extra, 1*ai_router_bit_radius])
    slab_front_outline.append([ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra,  0*ai_crenel_depth+0*nai_cutting_extra, 0*ai_router_bit_radius])
    slab_front_outline.append([ 0*ai_crenel_depth+0*nai_cutting_extra, ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra, 0*ai_router_bit_radius])
    slab_front_outline.append([-1*ai_crenel_depth+0*nai_cutting_extra, ai_wall_diagonal_size+0*ai_crenel_depth+1*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra, 1*ai_router_bit_radius])
    slab_front_outline.append([-1*ai_crenel_depth+0*nai_cutting_extra, ai_wall_diagonal_size+1*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)+0*nai_cutting_extra, 1*ai_router_bit_radius])
    slab_front_outline.append([ 0*ai_crenel_depth+1*nai_cutting_extra, ai_wall_diagonal_size+0*ai_crenel_depth+0*ai_d_plank_width*math.sqrt(2)-1*nai_cutting_extra, -1*ai_router_bit_radius])
    slab_front_outline.append([slab_front_outline[0][0], slab_front_outline[0][1], 0]) # close the outline
    slab_front_face = Part.Face(Part.Wire(cnc25d_api.cnc_cut_outline_fc(slab_front_outline, 'slab_front').Edges))
    r_slab_front_solid = slab_front_face.extrude(Base.Vector(0,0,ai_slab_thickness))
    return(r_slab_front_solid)
  #Part.show(slab_front(0))

  ## plank_generic
  # to help some reporting function
  def plank_generic(nai_plank_name, nai_module_width, nai_cutting_extra):
    """ Wrapper function to call any planks from a single function
    """
    if(nai_plank_name=="plank01_xz_bottom"):
      r_plank = plank_xz_bottom(nai_module_width, nai_cutting_extra)
    elif(nai_plank_name=="plank02_xz_top"):
      r_plank = plank_xz_top(nai_module_width, nai_cutting_extra)
    elif(nai_plank_name=="plank03_yz_bottom"):
      r_plank = plank_yz_bottom(nai_cutting_extra)
    elif(nai_plank_name=="plank04_yz_top"):
      r_plank = plank_yz_top(nai_cutting_extra)
    elif(nai_plank_name=="plank05_z_side"):
      r_plank = plank_z_side(nai_cutting_extra)
    elif(nai_plank_name=="plank06_zx_middle"):
      r_plank = plank_zx_middle(nai_cutting_extra)
    elif(nai_plank_name=="plank07_wall_diagonal"):
      r_plank = plank_wall_diagonal(nai_cutting_extra)
    elif(nai_plank_name=="plank08_tobo_diagonal"):
      r_plank = plank_tobo_diagonal(nai_cutting_extra)
    elif(nai_plank_name=="plank09_hole_cover"):
      r_plank = plank_hole_cover(nai_cutting_extra)
    elif(nai_plank_name=="plank21_wall_diag_rot"):
      r_plank = plank_wall_diagonal_in_cuboid(nai_cutting_extra)
    elif(nai_plank_name=="plank22_tobo_diag_rot"):
      r_plank = plank_tobo_diagonal_in_cuboid(nai_cutting_extra)
    elif(nai_plank_name=="slab51_tobo_single"):
      r_plank = slab_top_bottom("single", nai_cutting_extra)
    elif(nai_plank_name=="slab52_tobo_side"):
      r_plank = slab_top_bottom("side", nai_cutting_extra)
    elif(nai_plank_name=="slab53_tobo_middle"):
      r_plank = slab_top_bottom("middle", nai_cutting_extra)
    elif(nai_plank_name=="slab54_side_left_right"):
      r_plank = slab_side("left_right", nai_cutting_extra)
    elif(nai_plank_name=="slab55_side_rear_single"):
      r_plank = slab_side("rear_single", nai_cutting_extra)
    elif(nai_plank_name=="slab56_side_rear_side"):
      r_plank = slab_side("rear_side", nai_cutting_extra)
    elif(nai_plank_name=="slab57_side_rear_middle"):
      r_plank = slab_side("rear_middle", nai_cutting_extra)
    elif(nai_plank_name=="slab58_front"):
      r_plank = slab_front(nai_cutting_extra)
    else:
      print("ERR115: Error, the plank_name %s doesn't exist" % nai_plank_name)
      sys.exit(2)
    return(r_plank)
  def place_plank_generic(nai_plank_name, nai_module_width, nai_cutting_extra, ai_flip, ai_orientation, ai_position_x, ai_position_y, ai_position_z):
    """ Wrapper function to place any planks in a cuboid construction
    """
    l_plank_desc = plank_description(nai_module_width)
    r_placed_plank = cnc25d_api.place_plank(plank_generic(nai_plank_name, nai_module_width, nai_cutting_extra),
      l_plank_desc[nai_plank_name][0], l_plank_desc[nai_plank_name][1], l_plank_desc[nai_plank_name][2],
      ai_flip, ai_orientation, ai_position_x, ai_position_y, ai_position_z)
    return(r_placed_plank)

  ## assembly
  ## optional plank_hole_cover assembly
  def hole_cover_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view):
    """ optional sub-assembly of the hole_cover
    """
    #print("dbg202: nai_module_width:", nai_module_width)
    # initialization of the list of plank_hole_cover
    l_assembly = []
    # position of the plank_hole_cover
    lx_for_xz = [ai_plank_height+ai_tobo_diagonal_size+cai_tobo_diag_depth]
    for li in range(nai_module_width-1):
      lx_for_xz.append((li+1)*ai_box_width-1.0/2*ai_plank_height-ai_tobo_diagonal_size-cai_tobo_diag_depth-1*plank_hole_cover_length)
      lx_for_xz.append((li+1)*ai_box_width+1.0/2*ai_plank_height+ai_tobo_diagonal_size+cai_tobo_diag_depth-0*plank_hole_cover_length)
    lx_for_xz.append(nai_module_width*ai_box_width-ai_plank_height-ai_tobo_diagonal_size-cai_tobo_diag_depth-plank_hole_cover_length+nai_exploded_view)
    ly_for_xz = [0, ai_box_depth - plank_hole_cover_height + nai_exploded_view]
    lz_for_xz = [ai_fitting_height + ai_h_plank_width - ai_diagonal_lining_bottom_height - ai_d_plank_height,
                  ai_box_height - ai_h_plank_width + ai_diagonal_lining_top_height + nai_exploded_view]
    lx_for_yz = [0, nai_module_width*ai_box_width - plank_hole_cover_height + nai_exploded_view]
    ly_for_yz = [ai_plank_height + ai_tobo_diagonal_size + cai_tobo_diag_depth,
                  ai_box_depth - ai_plank_height - ai_tobo_diagonal_size - cai_tobo_diag_depth - plank_hole_cover_length + nai_exploded_view]
    lz_for_yz = lz_for_xz
    # positioning
    for lx in lx_for_xz:
      for ly in ly_for_xz:
        for lz in lz_for_xz:
          l_assembly.append(place_plank_generic('plank09_hole_cover', nai_module_width, nai_cutting_extra, 'i', 'xz', lx, ly, lz))
    for lx in lx_for_yz:
      for ly in ly_for_yz:
        for lz in lz_for_yz:
          l_assembly.append(place_plank_generic('plank09_hole_cover', nai_module_width, nai_cutting_extra, 'i', 'yz', lx, ly, lz))
    return(l_assembly)
    # make one Part.compound
    r_hole_cover_assembly_solid = Part.makeCompound(l_assembly)
    return(r_hole_cover_assembly_solid)
  #Part.show(hole_cover_assembly(1,0,0))
  #Part.show(Part.makeCompound(hole_cover_assembly(1,0,0)))

  ## optional slab assembly
  def slab_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view):
    """ optional sub-assembly of the slabs
    """
    # pre-computing of x coordinates
    lx_for_tobo_single = []
    if(nai_module_width==1):
      lx_for_tobo_single.append(ai_plank_height)
    lx_for_tobo_side = []
    if(nai_module_width>1):
      lx_for_tobo_side.append(ai_plank_height)
      lx_for_tobo_side.append(nai_module_width*ai_box_width-ai_plank_height-slab_top_bottom_side_length+nai_exploded_view)
    lx_for_tobo_middle = []
    for li in range(nai_module_width-2):
      lx_for_tobo_middle.append(ai_plank_height/2+(1+li)*ai_box_width)
    lx_for_left_right = []
    lx_for_left_right.append(0*(nai_module_width*ai_box_width)+(ai_plank_height-ai_d_plank_height-1*ai_slab_thickness))
    lx_for_left_right.append(1*(nai_module_width*ai_box_width)-(ai_plank_height-ai_d_plank_height-0*ai_slab_thickness)+nai_exploded_view)
    lx_for_rear_single = []
    if(nai_module_width==1):
      lx_for_rear_single.append(ai_v_plank_width)
    lx_for_rear_side = []
    if(nai_module_width>1):
      lx_for_rear_side.append(0*(nai_module_width*ai_box_width)+ai_v_plank_width)
      lx_for_rear_side.append(1*(nai_module_width*ai_box_width)-ai_v_plank_width-slab_side_rear_side_width+nai_exploded_view)
    lx_for_rear_middle = []
    for li in range(nai_module_width-2):
      lx_for_rear_middle.append(ai_v_plank_width/2+(1+li)*ai_box_width)
    lx_for_front_left = []
    lx_for_front_left.append(ai_v_plank_width)
    for li in range(nai_module_width-1):
      lx_for_front_left.append(ai_v_plank_width/2+(1+li)*ai_box_width)
    lx_for_front_right = []
    for lx in lx_for_front_left:
      lx_for_front_right.append(nai_module_width*ai_box_width-lx-slab_front_width)
    lz_for_tobo = []
    lz_for_tobo.append(ai_fitting_height+ai_h_plank_width-ai_diagonal_lining_bottom_height)
    lz_for_tobo.append(ai_box_height-ai_h_plank_width+ai_diagonal_lining_top_height+ai_d_plank_height+nai_exploded_view)
    lz_for_front = []
    lz_for_front.append(ai_fitting_height+ai_h_plank_width)
    lz_for_front.append(ai_box_height-ai_h_plank_width-slab_front_length+nai_exploded_view)
    # initialization of the list of slabs
    l_assembly = []
    # positioning
    for lz in lz_for_tobo:
      for lx in lx_for_tobo_single:
        l_assembly.append(place_plank_generic('slab51_tobo_single', nai_module_width, nai_cutting_extra, 'i', 'xy', lx, ai_plank_height, lz))
      for lx in lx_for_tobo_side:
        l_assembly.append(place_plank_generic('slab52_tobo_side', nai_module_width, nai_cutting_extra, 'i', 'xy', lx, ai_plank_height, lz))
      for lx in lx_for_tobo_middle:
        l_assembly.append(place_plank_generic('slab53_tobo_middle', nai_module_width, nai_cutting_extra, 'i', 'xy', lx, ai_plank_height, lz))
    for lx in lx_for_left_right:
      l_assembly.append(place_plank_generic('slab54_side_left_right', nai_module_width, nai_cutting_extra, 'i', 'zy', lx, ai_plank_height+ai_v_plank_width, ai_fitting_height+ai_h_plank_width))
    for lx in lx_for_rear_single:
      l_assembly.append(place_plank_generic('slab55_side_rear_single', nai_module_width, nai_cutting_extra, 'i', 'zx', lx, ai_box_depth-ai_plank_height+ai_d_plank_height+nai_exploded_view, ai_fitting_height+ai_h_plank_width))
    for lx in lx_for_rear_side:
      l_assembly.append(place_plank_generic('slab56_side_rear_side', nai_module_width, nai_cutting_extra, 'i', 'zx', lx, ai_box_depth-ai_plank_height+ai_d_plank_height+nai_exploded_view, ai_fitting_height+ai_h_plank_width))
    for lx in lx_for_rear_middle:
      l_assembly.append(place_plank_generic('slab57_side_rear_middle', nai_module_width, nai_cutting_extra, 'i', 'zx', lx, ai_box_depth-ai_plank_height+ai_d_plank_height+nai_exploded_view, ai_fitting_height+ai_h_plank_width))
    for lx in lx_for_front_left:
      l_assembly.append(place_plank_generic('slab58_front',  nai_module_width, nai_cutting_extra, 'i', 'zx', lx, ai_plank_height-ai_d_plank_height-ai_slab_thickness, lz_for_front[0]))
      l_assembly.append(place_plank_generic('slab58_front',  nai_module_width, nai_cutting_extra, 'y', 'zx', lx, ai_plank_height-ai_d_plank_height-ai_slab_thickness, lz_for_front[1]))
    for lx in lx_for_front_right:
      l_assembly.append(place_plank_generic('slab58_front',  nai_module_width, nai_cutting_extra, 'x', 'zx', lx, ai_plank_height-ai_d_plank_height-ai_slab_thickness, lz_for_front[0]))
      l_assembly.append(place_plank_generic('slab58_front',  nai_module_width, nai_cutting_extra, 'z', 'zx', lx, ai_plank_height-ai_d_plank_height-ai_slab_thickness, lz_for_front[1]))
    r_assembly = Part.makeCompound(l_assembly)
    return(r_assembly)
  #Part.show(slab_assembly(1,0,0))

  ## module assembly
  def frame_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view):
    """ assembly of the frame as a FreeCAD Part Object
    """
    # cuboid assembly
    l_assembly = []
    for ly in [0, ai_box_depth-ai_plank_height+nai_exploded_view]:
      l_assembly.append(place_plank_generic('plank02_xz_top', nai_module_width, nai_cutting_extra, 'i', 'xz', 0, ly, ai_box_height-ai_h_plank_width+nai_exploded_view))
      l_assembly.append(place_plank_generic('plank01_xz_bottom', nai_module_width, nai_cutting_extra, 'i', 'xz', 0, ly, 0))
    lx_for_yz = [0]
    lx_for_yz.extend([ (li+1)*ai_box_width-1.0/2*ai_plank_height for li in range(nai_module_width-1) ])
    lx_for_yz.append(nai_module_width*ai_box_width-ai_plank_height+nai_exploded_view)
    for lx in lx_for_yz:
      l_assembly.append(place_plank_generic('plank04_yz_top', nai_module_width, nai_cutting_extra, 'i', 'yz', lx, 0, ai_box_height-ai_h_plank_width+nai_exploded_view))
      l_assembly.append(place_plank_generic('plank03_yz_bottom', nai_module_width, nai_cutting_extra, 'i', 'yz', lx, 0, 0))
      l_assembly.append(place_plank_generic('plank05_z_side', nai_module_width, nai_cutting_extra,
        'i', 'zy', lx, ai_plank_height, ai_h_plank_width+ai_fitting_height-ai_crenel_depth))
      l_assembly.append(place_plank_generic('plank05_z_side', nai_module_width, nai_cutting_extra,
        'x', 'zy', lx,  ai_box_depth-ai_plank_height-ai_v_plank_width+nai_exploded_view, ai_h_plank_width+ai_fitting_height-ai_crenel_depth))
    ly_for_zx = [0, ai_box_depth-ai_plank_height+nai_exploded_view]
    for ly in ly_for_zx:
      l_assembly.append(place_plank_generic('plank05_z_side', nai_module_width, nai_cutting_extra,
        'i', 'zx', 0, ly, ai_h_plank_width+ai_fitting_height-ai_crenel_depth))
      l_assembly.append(place_plank_generic('plank05_z_side', nai_module_width, nai_cutting_extra,
        'x', 'zx', nai_module_width*ai_box_width-ai_v_plank_width+nai_exploded_view, ly, ai_h_plank_width+ai_fitting_height-ai_crenel_depth))
      for li in range(nai_module_width-1):
        l_assembly.append(place_plank_generic('plank06_zx_middle', nai_module_width, nai_cutting_extra,
          'i', 'zx', (li+1)*ai_box_width-1.0/2*ai_v_plank_width, ly, ai_h_plank_width+ai_fitting_height-ai_crenel_depth))
    # wall_diagonal assembly
#    l_assembly = []
    lx_for_wall_diag_xz1 = [ai_v_plank_width+ai_wall_diagonal_size]
    lx_for_wall_diag_xz1.extend([ (li+1)*ai_box_width+1.0/2*ai_v_plank_width+ai_wall_diagonal_size for li in range(nai_module_width-1) ])
    lx_for_wall_diag_xz2 = [ (li+1)*ai_box_width-1.0/2*ai_v_plank_width-ai_wall_diagonal_size-plank_wall_diagonal_in_cuboid_y_width for li in range(nai_module_width-1) ]
    lx_for_wall_diag_xz2.append(nai_module_width*ai_box_width-ai_v_plank_width-ai_wall_diagonal_size-plank_wall_diagonal_in_cuboid_y_width)
    lx_for_wall_diag_yz = [ai_plank_height-ai_d_plank_height]
    lx_for_wall_diag_yz.extend([ (li+1)*ai_box_width-1.0/2*ai_d_plank_height for li in range(nai_module_width-1) ])
    lx_for_wall_diag_yz.append(nai_module_width*ai_box_width-ai_plank_height+nai_exploded_view)
    ly_for_wall_diag_xz = [0*ai_box_depth+1*ai_plank_height-1*ai_d_plank_height, 1*ai_box_depth-1*ai_plank_height+0*ai_d_plank_height+nai_exploded_view]
    ly_for_wall_diag_yz = [0*ai_box_depth+1*ai_plank_height+1*ai_v_plank_width+1*ai_wall_diagonal_size,
                          1*ai_box_depth-1*ai_plank_height-1*ai_v_plank_width-1*ai_wall_diagonal_size-plank_wall_diagonal_in_cuboid_y_width]
    lz_for_wall_diag = [ai_h_plank_width+ai_fitting_height, ai_box_height-ai_h_plank_width-plank_wall_diagonal_in_cuboid_x_length]
    for lx in lx_for_wall_diag_xz1:
      for ly in ly_for_wall_diag_xz:
        l_assembly.append(place_plank_generic('plank21_wall_diag_rot', nai_module_width, nai_cutting_extra, 'x', 'zx', lx, ly, lz_for_wall_diag[0]))
        l_assembly.append(place_plank_generic('plank21_wall_diag_rot', nai_module_width, nai_cutting_extra, 'z', 'zx', lx, ly, lz_for_wall_diag[1]))
    for lx in lx_for_wall_diag_xz2:
      for ly in ly_for_wall_diag_xz:
        l_assembly.append(place_plank_generic('plank21_wall_diag_rot', nai_module_width, nai_cutting_extra, 'i', 'zx', lx, ly, lz_for_wall_diag[0]))
        l_assembly.append(place_plank_generic('plank21_wall_diag_rot', nai_module_width, nai_cutting_extra, 'y', 'zx', lx, ly, lz_for_wall_diag[1]))
    for lx in lx_for_wall_diag_yz:
        l_assembly.append(place_plank_generic('plank21_wall_diag_rot', nai_module_width, nai_cutting_extra, 'x', 'zy', lx, ly_for_wall_diag_yz[0], lz_for_wall_diag[0]))
        l_assembly.append(place_plank_generic('plank21_wall_diag_rot', nai_module_width, nai_cutting_extra, 'z', 'zy', lx, ly_for_wall_diag_yz[0], lz_for_wall_diag[1]))
        l_assembly.append(place_plank_generic('plank21_wall_diag_rot', nai_module_width, nai_cutting_extra, 'y', 'zy', lx, ly_for_wall_diag_yz[1], lz_for_wall_diag[1]))
        l_assembly.append(place_plank_generic('plank21_wall_diag_rot', nai_module_width, nai_cutting_extra, 'i', 'zy', lx, ly_for_wall_diag_yz[1], lz_for_wall_diag[0]))
    # tobo_diag assembly
    lx_for_tobo_diag_1 = [ai_plank_height]
    lx_for_tobo_diag_1.extend([ai_box_width*(li+1)+1.0/2*ai_plank_height for li in range(nai_module_width-1) ])
    lx_for_tobo_diag_2 = [ai_box_width*(li+1)-1.0/2*ai_plank_height-plank_tobo_diagonal_in_cuboid_x_length for li in range(nai_module_width-1) ]
    lx_for_tobo_diag_2.append(nai_module_width*ai_box_width-ai_plank_height-plank_tobo_diagonal_in_cuboid_x_length)
    ly_for_tobo_diag = [ai_plank_height+ai_tobo_diagonal_size, ai_box_depth-ai_plank_height-ai_tobo_diagonal_size-plank_wall_diagonal_in_cuboid_y_width]
    lz_for_tobo_diag = [ai_fitting_height+ai_h_plank_width-ai_diagonal_lining_bottom_height-ai_d_plank_height,
                        ai_box_height-ai_h_plank_width+ai_diagonal_lining_top_height+nai_exploded_view]
    for lx in lx_for_tobo_diag_1:
      for lz in lz_for_tobo_diag:
        l_assembly.append(place_plank_generic('plank22_tobo_diag_rot', nai_module_width, nai_cutting_extra, 'x', 'xy', lx, ly_for_tobo_diag[0], lz))
        l_assembly.append(place_plank_generic('plank22_tobo_diag_rot', nai_module_width, nai_cutting_extra, 'i', 'xy', lx, ly_for_tobo_diag[1], lz))
    #print("dbg441: lx_for_tobo_diag_2:", lx_for_tobo_diag_2)
    for lx in lx_for_tobo_diag_2:
      for lz in lz_for_tobo_diag:
        l_assembly.append(place_plank_generic('plank22_tobo_diag_rot', nai_module_width, nai_cutting_extra, 'z', 'xy', lx, ly_for_tobo_diag[0], lz))
        l_assembly.append(place_plank_generic('plank22_tobo_diag_rot', nai_module_width, nai_cutting_extra, 'y', 'xy', lx, ly_for_tobo_diag[1], lz))
    # hole cover  
    # comment this line if you don't want the hole_cover
    #l_assembly.extend(hole_cover_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view))
    #l_assembly.extend(slab_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view))
    r_assembly = Part.makeCompound(l_assembly)
    # comment this line if you don't want the hole_cover
    #r_assembly = r_assembly.fuse(hole_cover_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view)) # fuse of two makeCompound seems bugy!
    return(r_assembly)
  #Part.show(frame_assembly(1,2,200))
  #Part.show(frame_assembly(1,2,0))

  def box_wood_frame_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view):
    """ complete assembly of the box_wood_frame as a FreeCAD Part Object
    """
    l_assembly = []
    l_assembly.append(frame_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view))
    l_assembly.append(hole_cover_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view))
    l_assembly.append(slab_assembly(nai_module_width, nai_cutting_extra, nai_exploded_view))
    r_assembly = Part.makeCompound(l_assembly)
    return(r_assembly)
  #Part.show(box_wood_frame_assembly(1,2,200))
  #Part.show(box_wood_frame_assembly(1,2,0))
  #Part.show(box_wood_frame_assembly(1,0,0))

  def place_plank_list(nai_module_width, nai_cutting_extra, nai_count):
    # plank count
    l_plank_desc = plank_description(nai_module_width)
    l_plank_list = sorted(l_plank_desc.keys())
    # position
    place_x = 0
    place_y = 0
    place_z = 0
    place_step_x = 200
    place_step_y = 200
    # batch
    l_batch = []
    for lp in l_plank_list:
      l_count = l_plank_desc[lp][3]
      if(l_count>0):
        if(nai_count==0):
          l_count = 1
        for li in range(l_count):
          l_batch.append(place_plank_generic(lp, nai_module_width, nai_cutting_extra, 'i', 'xy', place_x+li*(place_step_x+l_plank_desc[lp][0]), place_y, place_z))
        place_y = place_y + place_step_y + l_plank_desc[lp][1]
    #
    r_batch = Part.makeCompound(l_batch)
    return(r_batch)

  def box_wood_frame_plank_definition_list(nai_module_width, nai_cutting_extra):
    """ Generate the list of all plank designs required for the box_wood_frame
        Each plank design appears only once
    """
    r_batch = place_plank_list(nai_module_width, nai_cutting_extra, 0)
    return(r_batch)
  #Part.show(box_wood_frame_plank_definition_list(3,0))
  def box_wood_frame_plank_count_list(nai_module_width, nai_cutting_extra):
    """ Generate the list of all planks required for the box_wood_frame
        Each plank design appears as much as their required count for the box_wood_frame assembly
    """
    r_batch = place_plank_list(nai_module_width, nai_cutting_extra, 1)
    return(r_batch)
  #Part.show(box_wood_frame_plank_count_list(1,0))

  ## cnc plan organization
  def plank_serie_place(ai_plank_list, nai_module_width, nai_cutting_extra, ai_ini_x, ai_ini_y, ai_ini_z, ai_step_x, ai_step_y):
    l_plank_desc = plank_description(nai_module_width)
    l_pos_x = ai_ini_x
    l_pos_y = ai_ini_y
    r_batch = []
    for lp in sorted(ai_plank_list.keys()):
      l_orientation = ai_plank_list[lp][0]
      l_increment_y = ai_plank_list[lp][1]
      l_inc_x = 0
      l_inc_y = 0
      if(l_orientation=='xy'):
        l_inc_y = 1
      elif(l_orientation=='yx'):
        l_inc_x = 1
      else:
        print("ERR564: the l_orientation %s doesn't exist!" % l_orientation)
        sys.exit(2)
      for li in range(l_plank_desc[lp][3]):
        r_batch.append(place_plank_generic(lp, nai_module_width, nai_cutting_extra, 'i', l_orientation, l_pos_x, l_pos_y, ai_ini_z))
        l_pos_x = l_pos_x + l_inc_x*(l_plank_desc[lp][1]+ai_step_x)
        l_pos_y = l_pos_y + l_inc_y*(l_plank_desc[lp][1]+ai_step_y)
      if((l_orientation=='yx') and (l_increment_y==1)):
        l_pos_x = ai_ini_x
        l_pos_y += l_plank_desc[lp][0]+ai_step_y
    return(r_batch)

  def box_wood_frame_plank_cutting_plan_cuboid(nai_module_width, nai_cutting_extra):
    """ Attempt to place all planks of height plank_height in a compact way for CNC cutting
    """
    l_plank_list = {  # set here the plank of tha batch and their wished orientation and position [orientation, increment_y]
      'plank01_xz_bottom' : ['xy', 0],
      'plank02_xz_top'    : ['xy', 0],
      'plank03_yz_bottom' : ['yx', 0],
      'plank04_yz_top'    : ['yx', 1],
      'plank05_z_side'    : ['yx', 0],
      'plank06_zx_middle' : ['yx', 1]}
    # space between plank
    place_step_x = 10
    place_step_y = 10
    # position
    place_x = 0
    place_y = 0
    place_z = 0
    # batch
    l_batch = plank_serie_place(l_plank_list, nai_module_width, nai_cutting_extra, place_x, place_y, place_z, place_step_x, place_step_y)
    r_batch = Part.makeCompound(l_batch)
    return(r_batch)

  def box_wood_frame_plank_cutting_plan_diagonal(nai_module_width, nai_cutting_extra):
    """ Attempt to place all planks of height plank_diagonal_height in a compact way for CNC cutting
    """
    l_plank_list = {  # set here the plank of tha batch and their wished orientation and position [orientation, increment_y]
      'plank07_wall_diagonal' : ['yx', 1],
      'plank08_tobo_diagonal' : ['yx', 0]}
    # space between plank
    place_step_x = 10
    place_step_y = 10
    # position
    place_x = 0
    place_y = 0
    place_z = 0
    # batch
    l_batch = plank_serie_place(l_plank_list, nai_module_width, nai_cutting_extra, place_x, place_y, place_z, place_step_x, place_step_y)
    r_batch = Part.makeCompound(l_batch)
    return(r_batch)

  def box_wood_frame_plank_cutting_plan_hole_cover(nai_module_width, nai_cutting_extra):
    """ Attempt to place all planks of height hole_cover_height in a compact way for CNC cutting
    """
    l_plank_list = {  # set here the plank of tha batch and their wished orientation and position [orientation, increment_y]
      'plank09_hole_cover' : ['yx', 1]}
    # space between plank
    place_step_x = 10
    place_step_y = 10
    # position
    place_x = 0
    place_y = 0
    place_z = 0
    # batch
    l_batch = plank_serie_place(l_plank_list, nai_module_width, nai_cutting_extra, place_x, place_y, place_z, place_step_x, place_step_y)
    r_batch = Part.makeCompound(l_batch)
    return(r_batch)

  def box_wood_frame_slab_cutting_plan(nai_module_width, nai_cutting_extra):
    """ Attempt to place all slabs in a compact way for CNC cutting
    """
    l_plank_list = {  # set here the plank of tha batch and their wished orientation and position [orientation, increment_y]
      'slab51_tobo_single'      : ['yx', 0],
      'slab52_tobo_side'        : ['yx', 0],
      'slab53_tobo_middle'      : ['yx', 1],
      'slab54_side_left_right'  : ['yx', 1],
      'slab55_side_rear_single' : ['yx', 0],
      'slab56_side_rear_side'   : ['yx', 0],
      'slab57_side_rear_middle' : ['yx', 1],
      'slab58_front'            : ['yx', 1]}
    # space between plank
    place_step_x = 10+ai_crenel_depth
    place_step_y = 10+ai_crenel_depth
    # position
    place_x = 0
    place_y = 0
    place_z = 0
    # batch
    l_batch = plank_serie_place(l_plank_list, nai_module_width, nai_cutting_extra, place_x, place_y, place_z, place_step_x, place_step_y)
    r_batch = Part.makeCompound(l_batch)
    return(r_batch)

  #Part.show(box_wood_frame_plank_cutting_plan_cuboid(1,0))
  #Part.show(box_wood_frame_plank_cutting_plan_diagonal(2,0))
  #Part.show(box_wood_frame_plank_cutting_plan_hole_cover(2,0))
  #Part.show(box_wood_frame_slab_cutting_plan(2,0))

  def box_wood_frame_plank_cutting_plan(nai_module_width, nai_cutting_extra):
    """ Overview of the three attempts to place all planks in a compact way for CNC cutting
    """
    l_plank_desc = plank_description(nai_module_width)
    place_step_x = 10
    place_step_y = 10
    place_y_plan_diagonal = ((l_plank_desc['plank01_xz_bottom'][3]+l_plank_desc['plank02_xz_top'][3])*(plank_xz_width+place_step_y)
                            + (plank_yz_length+place_step_y) + (plank_z_length+place_step_y))
    place_y_plan_hole_cover = place_y_plan_diagonal + (plank_wall_diagonal_length+place_step_y) + (plank_tobo_diagonal_length+place_step_y)
    place_y_plan_slab = place_y_plan_hole_cover + (plank_hole_cover_length + place_step_y)
    l_batch = []
    l_batch.append(box_wood_frame_plank_cutting_plan_cuboid(nai_module_width, nai_cutting_extra))
    l_batch.append(box_wood_frame_plank_cutting_plan_diagonal(nai_module_width, nai_cutting_extra))
    l_batch.append(box_wood_frame_plank_cutting_plan_hole_cover(nai_module_width, nai_cutting_extra))
    l_batch.append(box_wood_frame_slab_cutting_plan(nai_module_width, nai_cutting_extra))
    # translate batch plan_diagonal and _plan_hole_cover
    l_batch[1].translate(Base.Vector(0,place_y_plan_diagonal,0))
    l_batch[2].translate(Base.Vector(0,place_y_plan_hole_cover,0))
    l_batch[3].translate(Base.Vector(0,place_y_plan_slab,0))
    r_batch = Part.makeCompound(l_batch)
    return(r_batch)
  #Part.show(box_wood_frame_plank_cutting_plan(2,0))

  #def box_wood_frame_construction_step_01():
  #def box_wood_frame_construction_step_02():

  def box_wood_frame_text_report(nai_module_width):
    """ Generates the text report to provide all additional information to the STL and DXF files
    """
    r_text_report = ""
    r_text_report += """
box_wood_frame design
piece of furniture for building pile-up shell or straw house
created by charlyoleg on %s
license: CC BY SA 3.0
"""  % (datetime.now().isoformat())
    r_text_report += """
1. parameter values:
====================
box_width             : %0.2f
box_depth             : %0.2f
box_height            : %0.2f
module_width          : %d (in number of box)
fitting_height        : %0.2f
h_plank_width         : %0.2f
v_plank_width         : %0.2f
plank_height          : %0.2f
d_plank_width         : %0.2f
d_plank_height        : %0.2f
crenel_depth          : %0.2f
wall_diagonal_size    : %0.2f
tobo_diagonal_size    : %0.2f
diagonal_lining_top_height    : %0.2f
diagonal_lining_bottom_height : %0.2f
router_bit_radius         : %0.2f
cutting_extra         : %0.2f
slab_thickness        : %0.2f
output_file_basename  : %s
""" % (ai_box_width, ai_box_depth, ai_box_height, nai_module_width,
        ai_fitting_height, ai_h_plank_width, ai_v_plank_width, ai_plank_height,
        ai_d_plank_width, ai_d_plank_height, ai_crenel_depth,
        ai_wall_diagonal_size, ai_tobo_diagonal_size,
        ai_diagonal_lining_top_height, ai_diagonal_lining_bottom_height,
        ai_router_bit_radius, ai_cutting_extra,
        ai_slab_thickness, ai_output_file_basename)
    wood_density_fir_tree = 450 #kg/m3
    wood_density_oak_tree = 980 #kg/m3
    r_text_report += """
2. wood density:
================
fir tree density  :   %0.2f (kg/m3)
oak tree density  :   %0.2f (kg/m3)
""" % (wood_density_fir_tree, wood_density_oak_tree)
    r_text_report += """
3. plank height and section list:
=================================
"""
    # plank list per height
    l_plank_desc = plank_description(nai_module_width)
    l_plank_per_height = plank_per_height(nai_module_width)
    # Oops, if you don't convert it in list, it will be empty at the second read access (could be read only once!)
    possible_plank_height = list(reversed(sorted(l_plank_per_height.keys()))) 
    #print("dbg873: possible_plank_height:", possible_plank_height)
    possible_plank_height_str = [ "{: 3.02f}".format(lh) for lh in  possible_plank_height]
    r_text_report += "plank height list: %s\n" % (" ".join(possible_plank_height_str))
    l_plank_per_height_and_width = plank_per_height_and_width(nai_module_width)
    possible_plank_height_and_width = list(reversed(sorted(l_plank_per_height_and_width.keys())))
    r_text_report += "plank width and height list: %s\n" % ("   ".join(possible_plank_height_and_width))
    r_text_report += """
4.1. plank list:
================
"""
    per_height_q = {}
    per_height_volume = {}
    l_plank_idx = 0
    #print("dbg874: possible_plank_height:", possible_plank_height)
    for lpph in possible_plank_height:
      r_text_report += "list of planks of height : %0.02f\n" % (lpph)
      per_height_q[lpph] = 0
      per_height_volume[lpph] = 0.0
      for lp in l_plank_per_height[lpph]:
        l_plank_idx += 1
        lq = l_plank_desc[lp][3]
        lv = l_plank_desc[lp][0]*l_plank_desc[lp][1]*l_plank_desc[lp][2]/1000
        per_height_q[lpph] += lq
        per_height_volume[lpph] += lq*lv
        r_text_report += "{:02d}: {:<26s} L*W*H= {: 3.02f} x{: 3.02f} x{: 3.02f} (mm)  V={: 4.02f} (cm3)  M(min)={: 4.03f}  M(max)={: 4.03f} (kg)  Q={: 2d}\n".format(
          l_plank_idx, lp, l_plank_desc[lp][0], l_plank_desc[lp][1], l_plank_desc[lp][2], lv, lv*wood_density_fir_tree*10**-6, lv*wood_density_oak_tree*10**-6, lq)
    r_text_report += """
4.2. summary per plank height:
==============================
"""
    total_type_nb = 0
    total_q = 0
    total_volume = 0.0
    #print("dbg875: possible_plank_height:", possible_plank_height)
    for lpph in possible_plank_height:
      total_type_nb += len(l_plank_per_height[lpph])
      total_q += per_height_q[lpph]
      total_volume += per_height_volume[lpph]
      r_text_report += "for plank height {: 6.02f}: plank_type_nb: {: 2d}  plank_nb: {: 2d}  V={: 4.02f} (cm3)  M(min)={: 4.03f}  M(max)={: 4.03f} (kg)\n".format(
        lpph, len(l_plank_per_height[lpph]), per_height_q[lpph], per_height_volume[lpph],
        per_height_volume[lpph]*wood_density_fir_tree*10**-6, per_height_volume[lpph]*wood_density_oak_tree*10**-6)
    r_text_report += """
4.3. plank total:
=================
"""
    r_text_report += "in total: plank_type_nb: {: 2d}  plank_nb: {: 2d}  V={: 4.02f} (cm3)  M(min)={: 4.03f}  M(max)={: 4.03f} (kg)\n".format(
      total_type_nb, total_q, total_volume, total_volume*wood_density_fir_tree*10**-6, total_volume*wood_density_oak_tree*10**-6)
    r_text_report += """
5. cnc plan requirement:
========================
"""
    # space between plank
    l_space_x = 10
    l_space_y = 10
    # cuboid plan
    l_h1_dx = max(plank_xz_length,
      l_plank_desc['plank03_yz_bottom'][3]*(l_plank_desc['plank03_yz_bottom'][1]+l_space_y)+l_plank_desc['plank04_yz_top'][3]*(l_plank_desc['plank04_yz_top'][1]+l_space_y),
      l_plank_desc['plank05_z_side'][3]*(l_plank_desc['plank05_z_side'][1]+l_space_y)+l_plank_desc['plank06_zx_middle'][3]*(l_plank_desc['plank06_zx_middle'][1]+l_space_y))
    l_h1_dy = 4*(plank_xz_width+l_space_y)+(plank_yz_length+l_space_y)+(plank_z_length+l_space_y)
    l_h1_v = l_h1_dx*l_h1_dy*ai_plank_height/1000
    r_text_report += "cnc plank height {: 6.02f} :  x_size={: 3.02f}  y_size={: 3.02f}  V={: 4.02f} (cm3)  M(min)={: 4.03f}  M(max)={: 4.03f} (kg)\n".format(
      ai_plank_height, l_h1_dx, l_h1_dy, l_h1_v, l_h1_v*wood_density_fir_tree*10**-6, l_h1_v*wood_density_oak_tree*10**-6)
    # diagonal plan
    l_h2_dx = max(l_plank_desc['plank07_wall_diagonal'][3]*(l_plank_desc['plank07_wall_diagonal'][1]+l_space_y),
                  l_plank_desc['plank08_tobo_diagonal'][3]*(l_plank_desc['plank08_tobo_diagonal'][1]+l_space_y))
    l_h2_dy = l_plank_desc['plank06_zx_middle'][0] + l_plank_desc['plank07_wall_diagonal'][0] + 2*l_space_y
    l_h2_v = l_h2_dx*l_h2_dy*ai_d_plank_height/1000
    r_text_report += "cnc plank height {: 6.02f} :  x_size={: 3.02f}  y_size={: 3.02f}  V={: 4.02f} (cm3)  M(min)={: 4.03f}  M(max)={: 4.03f} (kg)\n".format(
      ai_d_plank_height, l_h2_dx, l_h2_dy, l_h2_v, l_h2_v*wood_density_fir_tree*10**-6, l_h2_v*wood_density_oak_tree*10**-6)
    # hole_cover plan
    l_h3_dx = l_plank_desc['plank09_hole_cover'][3]*(l_plank_desc['plank09_hole_cover'][1]+l_space_y)
    l_h3_dy = l_plank_desc['plank09_hole_cover'][0] + 2*l_space_y
    l_h3_v = l_h3_dx*l_h3_dy*plank_hole_cover_height/1000
    r_text_report += "cnc plank height {: 6.02f} :  x_size={: 3.02f}  y_size={: 3.02f}  V={: 4.02f} (cm3)  M(min)={: 4.03f}  M(max)={: 4.03f} (kg)\n".format(
      plank_hole_cover_height, l_h3_dx, l_h3_dy, l_h3_v, l_h3_v*wood_density_fir_tree*10**-6, l_h3_v*wood_density_oak_tree*10**-6)
    # slab plan
    l_h4_dx = max((l_plank_desc['slab51_tobo_single'][3] + l_plank_desc['slab52_tobo_side'][3] + l_plank_desc['slab53_tobo_middle'][3])*(l_plank_desc['slab53_tobo_middle'][1]+l_space_y),
                  l_plank_desc['slab54_side_left_right'][3]*(l_plank_desc['slab54_side_left_right'][1]+l_space_y),
                  (l_plank_desc['slab55_side_rear_single'][3] + l_plank_desc['slab56_side_rear_side'][3] + l_plank_desc['slab57_side_rear_middle'][3])*(l_plank_desc['slab57_side_rear_middle'][1]+l_space_y),
                  l_plank_desc['slab58_front'][3]*(l_plank_desc['slab58_front'][1]+l_space_y))
    l_h4_dy = l_plank_desc['slab53_tobo_middle'][0] + l_plank_desc['slab54_side_left_right'][0] + l_plank_desc['slab57_side_rear_middle'][0] + l_plank_desc['slab58_front'][0] + 5*l_space_y
    l_h4_v = l_h4_dx*l_h4_dy*slab_top_bottom_height/1000
    r_text_report += "cnc slab height {: 6.02f} :  x_size={: 3.02f}  y_size={: 3.02f}  V={: 4.02f} (cm3)  M(min)={: 4.03f}  M(max)={: 4.03f} (kg)\n".format(
      slab_top_bottom_height, l_h4_dx, l_h4_dy, l_h4_v, l_h4_v*wood_density_fir_tree*10**-6, l_h4_v*wood_density_oak_tree*10**-6)
    r_text_report += """
6.1. plank requirement:
=======================
"""
    per_wxh_q = {}
    per_wxh_length = {}
    for lppwh in possible_plank_height_and_width:
      r_text_report += "plank section width_x_height: %s\n"%lppwh
      per_wxh_q[lppwh] = 0
      per_wxh_length[lppwh] = 0.0
      for lp in l_plank_per_height_and_width[lppwh]:
        lq = l_plank_desc[lp][3]
        l_length = l_plank_desc[lp][0]
        l_total_length = lq*l_length
        per_wxh_q[lppwh] += lq
        per_wxh_length[lppwh] += l_total_length
        r_text_report += "plank {:<15s} {:<26s} : length: {: 3.02f}  Q={: 2d}  total_length: {: 5.02f}\n".format(lppwh, lp, l_length, lq, l_total_length)
    r_text_report += """
6.2. summary per plank section width x height:
==============================================
for plank section : plank_type_nb plank_nb total_length  : Accumulation: plank_type_nb plank_nb total_length
"""
    total_type_nb = 0
    total_q = 0
    total_length = 0
    for lppwh in possible_plank_height_and_width:
      total_type_nb += len(l_plank_per_height_and_width[lppwh])
      total_q += per_wxh_q[lppwh]
      total_length += per_wxh_length[lppwh]
      #r_text_report += "for plank section {:<15s} : plank_type_nb: {: 2d}  plank_nb: {: 2d} total_length: {: 5.02f}".format(
      r_text_report += "for {:<15s} : type_nb: {: 3d}  nb: {: 3d}  length: {: 8.02f}".format(
                          lppwh, len(l_plank_per_height_and_width[lppwh]), per_wxh_q[lppwh], per_wxh_length[lppwh])
      #r_text_report += "  Accumulation: plank_type_nb: {: 2d}  plank_nb: {: 2d}  total_length: {: 5.02f}\n".format(total_type_nb, total_q, total_length)
      r_text_report += "  : Accumulation: type_nb: {: 4d}  nb: {: 4d}  length: {: 10.02f}\n".format(total_type_nb, total_q, total_length)
#    r_text_report += """
#6.3. plank section total:
#=========================
#"""
#    r_text_report += "in total: plank_type_nb: {: 2d}  plank_nb: {: 2d}  total_length: {: 5.02f}\n".format(total_type_nb, total_q, total_length)

    r_text_report += """
7. output file list:
====================
"""
    return(r_text_report)
  #print("box_wood_frame text report:\n%s"%(box_wood_frame_text_report(1)))

  def fg_file_path(ai_output_dir, ai_file_name):
    r_file_path = "{:s}/{:s}".format(ai_output_dir, ai_file_name)
    print("Generate the output file: {:s}".format(r_file_path))
    return(r_file_path)

  def fg_text_report(ai_file_idx, ai_file_name, ai_file_description, ai_size):
    r_txt = "{:2d} : {:s}\n{:s}\nsize (in byte): {:,d}\n\n".format(ai_file_idx, ai_file_name, ai_file_description, ai_size)
    return(r_txt)

  def fg_stl(ai_solid, ai_file_idx, ai_text_report, ai_output_dir, ai_output_basename, ai_file_basename2, ai_file_description):
    l_file_idx = ai_file_idx + 1
    l_file_name = "{:s}bwf{:02d}_{:s}".format(ai_output_basename, l_file_idx, ai_file_basename2)
    l_file_description = "{:s}. STL format (3D).".format(ai_file_description)
    l_file_path = fg_file_path(ai_output_dir, l_file_name) 
    ai_solid.exportStl(l_file_path)
    l_text_report = ai_text_report + fg_text_report(l_file_idx, l_file_name, l_file_description, os.path.getsize(l_file_path))
    r_fg = (l_file_idx, l_text_report)
    return(r_fg)

  def fg_step(ai_solid, ai_file_idx, ai_text_report, ai_output_dir, ai_output_basename, ai_file_basename2, ai_file_description):
    l_file_idx = ai_file_idx + 1
    l_file_name = "{:s}bwf{:02d}_{:s}".format(ai_output_basename, l_file_idx, ai_file_basename2)
    l_file_description = "{:s}. ISO standard STEP format (3D).".format(ai_file_description)
    l_file_path = fg_file_path(ai_output_dir, l_file_name) 
    ai_solid.exportStep(l_file_path)
    l_text_report = ai_text_report + fg_text_report(l_file_idx, l_file_name, l_file_description, os.path.getsize(l_file_path))
    r_fg = (l_file_idx, l_text_report)
    return(r_fg)

  def fg_brep(ai_solid, ai_file_idx, ai_text_report, ai_output_dir, ai_output_basename, ai_file_basename2, ai_file_description):
    l_file_idx = ai_file_idx + 1
    l_file_name = "{:s}bwf{:02d}_{:s}".format(ai_output_basename, l_file_idx, ai_file_basename2)
    l_file_description = "{:s}. Native OpenCasCade BRep format (3D).".format(ai_file_description)
    l_file_path = fg_file_path(ai_output_dir, l_file_name) 
    ai_solid.exportBrep(l_file_path)
    l_text_report = ai_text_report + fg_text_report(l_file_idx, l_file_name, l_file_description, os.path.getsize(l_file_path))
    r_fg = (l_file_idx, l_text_report)
    return(r_fg)

  def fg_3d(ai_solid, ai_file_idx, ai_text_report, ai_output_dir, ai_output_basename, ai_file_basename2, ai_file_description):
    l_file_idx = ai_file_idx
    l_text_report = ai_text_report
    # stl to be viewed with meshlab or freecad
    (l_file_idx, l_text_report) = fg_stl(ai_solid, l_file_idx, l_text_report, ai_output_dir, ai_output_basename, "{:s}.stl".format(ai_file_basename2), ai_file_description) 
    # STEP (iso standard) to be viewed with freecad. Warning: largest file size!
    #(l_file_idx, l_text_report) = fg_step(ai_solid, l_file_idx, l_text_report, ai_output_dir, ai_output_basename, "{:s}.step".format(ai_file_basename2), ai_file_description) 
    # BRep (OpenCascade Native) to be viewed with freecad
    (l_file_idx, l_text_report) = fg_brep(ai_solid, l_file_idx, l_text_report, ai_output_dir, ai_output_basename, "{:s}.brep".format(ai_file_basename2), ai_file_description) 
    r_fg = (l_file_idx, l_text_report)
    return(r_fg)

  def fg_dxf(ai_solid, ai_file_idx, ai_text_report, ai_output_dir, ai_output_basename, ai_file_basename2, ai_file_description):
    l_file_idx = ai_file_idx + 1
    l_file_name = "{:s}bwf{:02d}_{:s}".format(ai_output_basename, l_file_idx, ai_file_basename2)
    l_file_description = "{:s}. DXF format (2D).".format(ai_file_description)
    l_file_path = fg_file_path(ai_output_dir, l_file_name) 
    cnc25d_api.export_to_dxf(ai_solid, Base.Vector(0,0,1), 1.0, l_file_path) # slice the plank in the XY plan at a height of 1.0
    l_text_report = ai_text_report + fg_text_report(l_file_idx, l_file_name, l_file_description, os.path.getsize(l_file_path))
    r_fg = (l_file_idx, l_text_report)
    return(r_fg)

  def fg_svg(ai_solid, ai_file_idx, ai_text_report, ai_output_dir, ai_output_basename, ai_file_basename2, ai_file_description):
    l_file_idx = ai_file_idx + 1
    l_file_name = "{:s}bwf{:02d}_{:s}".format(ai_output_basename, l_file_idx, ai_file_basename2)
    l_file_description = "{:s}. SVG format (2D).".format(ai_file_description)
    l_file_path = fg_file_path(ai_output_dir, l_file_name) 
    cnc25d_api.export_to_svg(ai_solid, Base.Vector(0,0,1), 1.0, l_file_path) # slice the plank in the XY plan at a height of 1.0
    l_text_report = ai_text_report + fg_text_report(l_file_idx, l_file_name, l_file_description, os.path.getsize(l_file_path))
    r_fg = (l_file_idx, l_text_report)
    return(r_fg)

  def fg_xyz_dxf(ai_solid, ai_file_idx, ai_text_report, ai_output_dir, ai_output_basename, ai_file_basename2, ai_file_description):
    l_file_idx = ai_file_idx + 1
    l_file_name = "{:s}bwf{:02d}_{:s}".format(ai_output_basename, l_file_idx, ai_file_basename2)
    l_file_description = "{:s}. DXF format (2D).".format(ai_file_description)
    l_file_path = fg_file_path(ai_output_dir, l_file_name)
    lepsilon = 1.0
    l_xy_slice_list = [lepsilon,
                        ai_fitting_height-lepsilon,
                        ai_fitting_height+lepsilon,
                        ai_fitting_height+ai_h_plank_width/2,
                        ai_fitting_height+ai_h_plank_width+lepsilon,
                        (ai_box_height-(ai_fitting_height+2*ai_h_plank_width))/4+(ai_fitting_height+ai_h_plank_width),
                        ai_box_height/2,
                        ai_box_height-((ai_box_height-(ai_fitting_height+2*ai_h_plank_width))/4+(ai_fitting_height+ai_h_plank_width)),
                        ai_box_height-(ai_h_plank_width+lepsilon),
                        ai_box_height-(ai_h_plank_width/2),
                        ai_box_height-lepsilon,
                        ai_box_height+lepsilon,
                        ai_box_height+ai_fitting_height-lepsilon]
    l_xz_slice_list = [lepsilon,
                        ai_plank_height-lepsilon,
                        ai_plank_height+lepsilon,
                        ai_plank_height+(ai_box_depth-2*ai_plank_height)/4,
                        ai_box_depth/2,
                        ai_box_depth-(ai_plank_height+(ai_box_depth-2*ai_plank_height)/4),
                        ai_box_depth-(ai_plank_height+lepsilon),
                        ai_box_depth-(ai_plank_height-lepsilon),
                        ai_box_depth-lepsilon]
    l_yz_slice_list = [lepsilon,
                        ai_plank_height-lepsilon,
                        ai_plank_height+lepsilon,
                        ai_plank_height+(ai_box_width-2*ai_plank_height)/4,
                        ai_box_width/2,
                        ai_box_width-(ai_plank_height+(ai_box_width-2*ai_plank_height)/4),
                        ai_box_width-(ai_plank_height+lepsilon),
                        ai_box_width-(ai_plank_height-lepsilon),
                        ai_box_width-lepsilon]
    cnc25d_api.export_xyz_to_dxf(ai_solid, ai_module_width*ai_box_width, ai_box_depth, ai_box_height, l_xy_slice_list, l_xz_slice_list, l_yz_slice_list, l_file_path)
    l_text_report = ai_text_report + fg_text_report(l_file_idx, l_file_name, l_file_description, os.path.getsize(l_file_path))
    r_fg = (l_file_idx, l_text_report)
    return(r_fg)

  def box_wood_frame_file_generator(nai_output_file_basename):
    """ this function generates the DXF and STL files if the parameter output_file_basename is not empty.
        It returns a string that contains the file name list and their description.
    """
    bwf_log = box_wood_frame_text_report(ai_module_width)
    print("{:s}".format(bwf_log))
    l_text_report = bwf_log
    #print("dbg747: nai_output_file_basename:", nai_output_file_basename)
    if(nai_output_file_basename==""):
      print("No output_basename! No file generated!\n")
    else:
      l_output_dir = os.path.dirname(nai_output_file_basename)
      if(l_output_dir==''):
        l_output_dir='.'
      #print("dbg448: l_output_dir:", l_output_dir)
      l_output_basename = os.path.basename(nai_output_file_basename)
      #print("dbg449: l_output_basename:", l_output_basename)
      # mkdir -p directory if needed
      print("dbg450: try to create the output directory: {:s}".format(l_output_dir))
      try:
        os.makedirs(l_output_dir)
      except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(l_output_dir):
          pass
        else:
          raise
      #
      l_file_idx = 0

      # plank definition
      l_plank_desc = plank_description(ai_module_width)
      l_plank_list = sorted(l_plank_desc.keys())
      for lp in l_plank_list:
        if(l_plank_desc[lp][3]>0):
          l_plank = plank_generic(lp, ai_module_width, 0)
          (l_file_idx, l_text_report) = fg_3d(l_plank, l_file_idx, l_text_report, l_output_dir, l_output_basename,
            "{:s}_definition".format(lp), "Definition of the plank: {:s}".format(lp)) 
          (l_file_idx, l_text_report) = fg_dxf(l_plank, l_file_idx, l_text_report, l_output_dir, l_output_basename,
            "{:s}_definition.dxf".format(lp), "Definition of the plank: {:s}".format(lp)) 
          #(l_file_idx, l_text_report) = fg_svg(l_plank, l_file_idx, l_text_report, l_output_dir, l_output_basename,
          #  "{:s}_definition.svg".format(lp), "Definition of the plank: {:s}".format(lp))

      # plank type batch
      l_batch = box_wood_frame_plank_definition_list(ai_module_width, 0)
      (l_file_idx, l_text_report) = fg_3d(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "plank_type_batch", "Batch of each plank type") 
      (l_file_idx, l_text_report) = fg_dxf(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "plank_type_batch.dxf", "Batch of each plank type") 

      # plank count batch
      l_batch = box_wood_frame_plank_count_list(ai_module_width, 0)
      (l_file_idx, l_text_report) = fg_3d(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "plank_count_batch", "Batch of all required planks") 
      (l_file_idx, l_text_report) = fg_dxf(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "plank_count_batch.dxf", "Batch of all required planks") 

      # frame assembly
      l_assembly = frame_assembly(ai_module_width, 0, 0)
      (l_file_idx, l_text_report) = fg_3d(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "frame_assembly", "Assembly of the frame") 
      (l_file_idx, l_text_report) = fg_xyz_dxf(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "frame_assembly.dxf", "Assembly of the frame") 

      # frame assembly with amplified_cut
      l_assembly = frame_assembly(ai_module_width, ai_cutting_extra, 0)
      (l_file_idx, l_text_report) = fg_3d(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "frame_assembly_with_amplified_cut", "Assembly of the frame with amplified cut") 
      (l_file_idx, l_text_report) = fg_xyz_dxf(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "frame_assembly_with_amplified_cut.dxf", "Assembly of the frame with amplified cut") 

      # frame explosed assembly with amplified_cut
      l_assembly = frame_assembly(ai_module_width, ai_cutting_extra, 200)
      (l_file_idx, l_text_report) = fg_3d(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "explosed_frame_assembly_with_amplified_cut", "Explosed assembly of the frame with amplified cut") 

      # assembly
      l_assembly = box_wood_frame_assembly(ai_module_width, 0, 0)
      (l_file_idx, l_text_report) = fg_3d(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "assembly", "Assembly of the box_wood_frame") 
      (l_file_idx, l_text_report) = fg_xyz_dxf(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "assembly.dxf", "Assembly of the box_wood_frame") 

      # assembly with amplified_cut
      l_assembly = box_wood_frame_assembly(ai_module_width, ai_cutting_extra, 0)
      (l_file_idx, l_text_report) = fg_3d(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "assembly_with_amplified_cut", "Assembly of the box_wood_frame with amplified cut") 
      (l_file_idx, l_text_report) = fg_xyz_dxf(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "assembly_with_amplified_cut.dxf", "Assembly of the box_wood_frame with amplified cut") 

      # explosed assembly with amplified_cut
      l_assembly = box_wood_frame_assembly(ai_module_width, ai_cutting_extra, 200)
      (l_file_idx, l_text_report) = fg_3d(l_assembly, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "explosed_assembly_with_amplified_cut", "Explosed assembly of the box_wood_frame with amplified cut") 

      # cnc plan for cuboid plank
      l_batch = box_wood_frame_plank_cutting_plan_cuboid(ai_module_width, 0)
      (l_file_idx, l_text_report) = fg_3d(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "cuboid_cnc_plan", "Batch of the cuboid planks gathered on a plan to be cut by cnc") 
      (l_file_idx, l_text_report) = fg_dxf(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "cuboid_cnc_plan.dxf", "Batch of the cuboid planks gathered on a plan to be cut by cnc")

      # cnc plan for diagonal plank
      l_batch = box_wood_frame_plank_cutting_plan_diagonal(ai_module_width, 0)
      (l_file_idx, l_text_report) = fg_3d(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "diagonal_cnc_plan", "Batch of the diagonal planks gathered on a plan to be cut by cnc") 
      (l_file_idx, l_text_report) = fg_dxf(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "diagonal_cnc_plan.dxf", "Batch of the diagonal planks gathered on a plan to be cut by cnc")

      # cnc plan for hole_cover plank
      l_batch = box_wood_frame_plank_cutting_plan_hole_cover(ai_module_width, 0)
      (l_file_idx, l_text_report) = fg_3d(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "hole_cover_cnc_plan", "Batch of the hole_cover planks gathered on a plan to be cut by cnc") 
      (l_file_idx, l_text_report) = fg_dxf(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "hole_cover_cnc_plan.dxf", "Batch of the hole_cover planks gathered on a plan to be cut by cnc")

      # cnc plan for slabs
      l_batch = box_wood_frame_slab_cutting_plan(ai_module_width, 0)
      (l_file_idx, l_text_report) = fg_3d(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "slab_cnc_plan", "Batch of the slabs gathered on a plan to be cut by cnc") 
      (l_file_idx, l_text_report) = fg_dxf(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "slab_cnc_plan.dxf", "Batch of the slabs gathered on a plan to be cut by cnc")

      # cnc plan overview
      l_batch = box_wood_frame_plank_cutting_plan(ai_module_width, 0)
      (l_file_idx, l_text_report) = fg_3d(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "cnc_plan_overview", "Batch of all planks gathered on a cnc plan for checking. Don't use it for cnc!") 
      (l_file_idx, l_text_report) = fg_dxf(l_batch, l_file_idx, l_text_report, l_output_dir, l_output_basename,
        "cnc_plan_overview.dxf", "Batch of all planks gathered on a cnc plan for checking. Don't use it for cnc!")

      l_file_idx += 1
      l_file_name = "{:s}bwf{:02d}_text_report.txt".format(l_output_basename, l_file_idx)
      l_file_description = "this text report"
      l_file_path = fg_file_path(l_output_dir, l_file_name)
      l_text_report += fg_text_report(l_file_idx, l_file_name, l_file_description, -1)
      fh_output = open(l_file_path, 'w')
      fh_output.write(l_text_report)
      fh_output.close()

    r_generator = 1
    return(r_generator)
  #print("dbg553: box_wood_frame_file_generator: %d" % box_wood_frame_file_generator('aaa'))
  #print("dbg554: box_wood_frame_file_generator: %d" % box_wood_frame_file_generator(''))
  
  # action = sub main
  box_wood_frame_file_generator(ai_output_file_basename)
  #box_wood_frame_file_generator('ttt/')
  #Part.show(box_wood_frame_assembly(1,2,0))

  ## select what you want to return
  #r_bwf = 1
  r_bwf = box_wood_frame_assembly(ai_module_width,ai_cutting_extra,0)
  #r_bwf = box_wood_frame_assembly(ai_module_width,ai_cutting_extra,200)
  #r_bwf = frame_assembly(ai_module_width,ai_cutting_extra,0)
  #r_bwf.exportStl("bwf_assembly.stl")
  #r_bwf = plank_tobo_diagonal(0)
  #r_bwf.exportBrep("plank_tobo_diagonal.brep")
  return(r_bwf)

################################################################
# box_wood_frame command line interface
################################################################

def box_wood_frame_cli():
  """ it is the command line interface of box_wood_frame.py when it is used in standalone
  """
  bwf_parser = argparse.ArgumentParser(description='Command line interface for the function box_wood_frame().')
  bwf_parser.add_argument('--box_width','--bw', action='store', type=float, default=400.0, dest='sw_box_width',
    help="It sets the width of the box of the grid.")
  bwf_parser.add_argument('--box_depth','--bd', action='store', type=float, default=400.0, dest='sw_box_depth',
    help="It sets the depth of the box of the grid. Per default, it is set to box_width value.")
  bwf_parser.add_argument('--box_height','--bh', action='store', type=float, default=400.0, dest='sw_box_height',
    help="It sets the height of the box of the grid. Per default, it is set to box_width value.")
  bwf_parser.add_argument('--fitting_height','--fh', action='store', type=float, default=30.0, dest='sw_fitting_height',
    help="It sets the height of the fitting that pile up vertically two modules.")
  bwf_parser.add_argument('--h_plank_width','--hpw', action='store', type=float, default=50.0, dest='sw_h_plank_width',
    help="It sets the width of the horizontal planks. Note that the total width of the horizontal plank is plank_width+fitting_height.")
  bwf_parser.add_argument('--v_plank_width','--vpw', action='store', type=float, default=30.0, dest='sw_v_plank_width',
    help="It sets the width of the vertical planks.")
  bwf_parser.add_argument('--plank_height','--ph', action='store', type=float, default=20.0, dest='sw_plank_height',
    help="It sets the height of the vertical and horizontal planks.")
  bwf_parser.add_argument('--d_plank_width','--dpw', action='store', type=float, default=30.0, dest='sw_d_plank_width',
    help="It sets the width of the diagonal planks. Per default the value is set to v_plank_width.")
  bwf_parser.add_argument('--d_plank_height','--dph', action='store', type=float, default=10.0, dest='sw_d_plank_height',
    help="It sets the height of the diagonal planks. If the vaue is zero, the plank_height value will be used. Set a lower value than plank_height to give space for the slab.")
  bwf_parser.add_argument('--crenel_depth','--cd', action='store', type=float, default=5.0, dest='sw_crenel_depth',
    help="It sets the depth of the crenels of the coplanar planks.")
  bwf_parser.add_argument('--wall_diagonal_size','--wdz', action='store', type=float, default=50.0, dest='sw_wall_diagonal_size',
    help="It sets the size of the diagonal lining of the four vertical walls.")
  bwf_parser.add_argument('--tobo_diagonal_size','--tbdz', action='store', type=float, default=100.0, dest='sw_tobo_diagonal_size',
    help="It sets the size of the diagonal lining of the top and bottom faces.")
  bwf_parser.add_argument('--diagonal_lining_top_height','--dlth', action='store', type=float, default=20.0, dest='sw_diagonal_lining_top_height',
    help="It sets the distance between the plank border and the holes for the horizontal top planks.")
  bwf_parser.add_argument('--diagonal_lining_bottom_height','--dlbh', action='store', type=float, default=20.0, dest='sw_diagonal_lining_bottom_height',
    help="It sets the distance between the plank border and the holes for the horizontal bottom planks.")
  #bwf_parser.add_argument('--tobo_diagonal_depth','--tdd', action='store', type=float, default=0.0, dest='sw_tobo_diagonal_depth',
  #  help="It sets the depth of the fitting between tobo_diagonal_lining_plank and horizontal_plank.")
  bwf_parser.add_argument('--module_width','--mw', action='store', type=int, default=1, dest='sw_module_width',
    help="It sets the width of the module in number of box_width.")
  #bwf_parser.add_argument('--module_depth','--md', action='store', type=int, default=1, dest='sw_module_depth',
  #  help="It sets the depth of the module in number of box_depth.")
  #bwf_parser.add_argument('--module_height','--mh', action='store', type=int, default=1, dest='sw_module_height',
  #  help="It sets the height of the module in number of box_height.")
  bwf_parser.add_argument('--router_bit_radius','--rr', action='store', type=float, default=2.0, dest='sw_router_bit_radius',
    help="It sets the radius of the router_bit of the cnc.")
  bwf_parser.add_argument('--cutting_extra','--ce', action='store', type=float, default=2.0, dest='sw_cutting_extra',
    help="It sets the cutting_extra used to see better the fitting in the assembly view.")
  bwf_parser.add_argument('--slab_thickness','--st', action='store', type=float, default=5.0, dest='sw_slab_thickness',
    help="If not zero (the default value), it generates the slabs with this thickness.")
  bwf_parser.add_argument('--output_file_basename','--ofb', action='store', default='', dest='sw_output_file_basename',
    help="If not set to the empty string (the default value), it generates a bunch of design files starting with this basename.")
  # this ensure the possible to use the script with python and freecad
  arg_index_offset=0
  if(sys.argv[0]=='freecad'): # check if the script is used by freecad
    arg_index_offset=1
    if(len(sys.argv)>=2):
      if(sys.argv[1]=='-c'): # check if the script is used by freecad -c
        arg_index_offset=2
  bwf_args = bwf_parser.parse_args(sys.argv[arg_index_offset+1:])
  print("dbg111: start building the 3D part")
  r_bwf = box_wood_frame(bwf_args.sw_box_width, bwf_args.sw_box_depth, bwf_args.sw_box_height,
    bwf_args.sw_fitting_height, bwf_args.sw_h_plank_width, bwf_args.sw_v_plank_width, bwf_args.sw_plank_height,
    bwf_args.sw_d_plank_width, bwf_args.sw_d_plank_height, bwf_args.sw_crenel_depth,
    bwf_args.sw_wall_diagonal_size, bwf_args.sw_tobo_diagonal_size,
    bwf_args.sw_diagonal_lining_top_height, bwf_args.sw_diagonal_lining_bottom_height,
    bwf_args.sw_module_width, bwf_args.sw_router_bit_radius, bwf_args.sw_cutting_extra,
    bwf_args.sw_slab_thickness, bwf_args.sw_output_file_basename)
  print("dbg999: end of script")
  return(r_bwf)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("box_wood_frame says hello!\n")
  my_bwf = box_wood_frame_cli()
  Part.show(my_bwf)



