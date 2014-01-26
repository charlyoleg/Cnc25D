# box_wood_frame_outline.py
# a sub module for the box_wood_frame design.
# created by charlyoleg on 2014/01/24
#
# (C) Copyright 2014 charlyoleg
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
sub-module of box_wood_frame.py
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
import sys

################################################################
# 2D-figures
################################################################

# jonction_plank_xz_with_zx
def jonction_plank_xz_with_zx(c):
  nr = [
    #[1.0/2*c['v_plank_width']-1*c['cutting_extra'], 0*c['crenel_depth']+0*c['cutting_extra'], 1*c['router_bit_radius']],
    [1.0/2*c['v_plank_width']-1*c['cutting_extra'], 0*c['crenel_depth']+0*c['cutting_extra'], 0*c['router_bit_radius']],
    [1.0/2*c['v_plank_width']-1*c['cutting_extra'], 1*c['crenel_depth']+1*c['cutting_extra'], 1*c['router_bit_radius']],
    [2.0/2*c['v_plank_width']+1*c['cutting_extra'], 1*c['crenel_depth']+1*c['cutting_extra'], 1*c['router_bit_radius']],
    [2.0/2*c['v_plank_width']+1*c['cutting_extra'], 0*c['crenel_depth']+0*c['cutting_extra'], 0*c['router_bit_radius']]]
  return(nr)

# jonction_plank_xz_with_middle_zx
def jonction_plank_xz_with_middle_zx(c):
  nr = [
    [-1.0/2*c['v_plank_width']-1*c['cutting_extra'], 0*c['crenel_depth']+0*c['cutting_extra'], 0*c['router_bit_radius']],
    [-1.0/2*c['v_plank_width']-1*c['cutting_extra'], 1*c['crenel_depth']+1*c['cutting_extra'], 1*c['router_bit_radius']],
    [ 1.0/2*c['v_plank_width']+1*c['cutting_extra'], 1*c['crenel_depth']+1*c['cutting_extra'], 1*c['router_bit_radius']],
    [ 1.0/2*c['v_plank_width']+1*c['cutting_extra'], 0*c['crenel_depth']+0*c['cutting_extra'], 0*c['router_bit_radius']]]
  return(nr)

#   jonction_plank_xz_with_wall_diagonal
def jonction_plank_xz_with_wall_diagonal(c):
  nr = [
    [c['v_plank_width']+c['wall_diagonal_size']+0*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)-2*c['cutting_extra'], 0*c['crenel_depth']+0*c['cutting_extra'], 0*c['router_bit_radius']],
    [c['v_plank_width']+c['wall_diagonal_size']+1*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)-1*c['cutting_extra'], 1*c['crenel_depth']+1*c['cutting_extra'], 1*c['router_bit_radius']],
    [c['v_plank_width']+c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+1*c['cutting_extra'], 1*c['crenel_depth']+1*c['cutting_extra'], 1*c['router_bit_radius']],
    [c['v_plank_width']+c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+1*c['cutting_extra'], 0*c['crenel_depth']+0*c['cutting_extra'], 0*c['router_bit_radius']]]
  return(nr)

# jonction_plank_top_xz_with_yz
def jonction_plank_top_xz_with_yz(c):
  nr = [
    [0*c['plank_height']+0*c['cutting_extra'], c['crenel_depth']+2.0/3*(c['h_plank_width']-c['crenel_depth'])+1*c['cutting_extra'], 0*c['router_bit_radius']],
    [1*c['plank_height']+1*c['cutting_extra'], c['crenel_depth']+2.0/3*(c['h_plank_width']-c['crenel_depth'])+1*c['cutting_extra'],-1*c['router_bit_radius']],
    [1*c['plank_height']+1*c['cutting_extra'], c['crenel_depth']+1.0/3*(c['h_plank_width']-c['crenel_depth'])-1*c['cutting_extra'],-1*c['router_bit_radius']],
    [0*c['plank_height']+0*c['cutting_extra'], c['crenel_depth']+1.0/3*(c['h_plank_width']-c['crenel_depth'])-1*c['cutting_extra'], 0*c['router_bit_radius']]]
  return(nr)

def hole_in_plank_top_xz_for_yz(c, nai_x_offset):
  l_outline = [
    [nai_x_offset-1.0/2*c['plank_height']-1*c['cutting_extra'], c['crenel_depth']+2.0/3*(c['h_plank_width']-c['crenel_depth'])+1*c['cutting_extra'],-1*c['router_bit_radius']],
    [nai_x_offset+1.0/2*c['plank_height']+1*c['cutting_extra'], c['crenel_depth']+2.0/3*(c['h_plank_width']-c['crenel_depth'])+1*c['cutting_extra'],-1*c['router_bit_radius']],
    [nai_x_offset+1.0/2*c['plank_height']+1*c['cutting_extra'], c['crenel_depth']+1.0/3*(c['h_plank_width']-c['crenel_depth'])-1*c['cutting_extra'],-1*c['router_bit_radius']],
    [nai_x_offset-1.0/2*c['plank_height']-1*c['cutting_extra'], c['crenel_depth']+1.0/3*(c['h_plank_width']-c['crenel_depth'])-1*c['cutting_extra'],-1*c['router_bit_radius']]]
  #l_outline.append([l_outline[0][0], l_outline[0][1], 0]) # close the outline
  l_outline_A = cnc25d_api.outline_close(l_outline)
  r_fig = [l_outline_A]
  return(r_fig)

# jonction_plank_bot_xz_with_yz
def jonction_plank_bot_xz_with_yz(c):
  nr = [
    [0*c['plank_height']+0*c['cutting_extra'], 2.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth'])+1*c['cutting_extra'], 0*c['router_bit_radius']],
    [1*c['plank_height']+1*c['cutting_extra'], 2.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth'])+1*c['cutting_extra'],-1*c['router_bit_radius']],
    [1*c['plank_height']+1*c['cutting_extra'], 1.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth'])-1*c['cutting_extra'],-1*c['router_bit_radius']],
    [0*c['plank_height']+0*c['cutting_extra'], 1.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth'])-1*c['cutting_extra'], 0*c['router_bit_radius']]]
  return(nr)

def hole_in_plank_bot_xz_for_yz(c, nai_x_offset):
  l_outline = [
    [nai_x_offset-1.0/2*c['plank_height']-1*c['cutting_extra'], 2.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth'])+1*c['cutting_extra'],-1*c['router_bit_radius']],
    [nai_x_offset+1.0/2*c['plank_height']+1*c['cutting_extra'], 2.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth'])+1*c['cutting_extra'],-1*c['router_bit_radius']],
    [nai_x_offset+1.0/2*c['plank_height']+1*c['cutting_extra'], 1.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth'])-1*c['cutting_extra'],-1*c['router_bit_radius']],
    [nai_x_offset-1.0/2*c['plank_height']-1*c['cutting_extra'], 1.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth'])-1*c['cutting_extra'],-1*c['router_bit_radius']]]
  #l_outline.append([l_outline[0][0], l_outline[0][1], 0]) # close the outline
  l_outline_A = cnc25d_api.outline_close(l_outline)
  r_fig = [l_outline_A]
  return(r_fig)

# jonction_plank_top_yz_with_xz
def jonction_plank_top_yz_with_xz(c):
  nr = [
    [1*c['plank_height'], c['crenel_depth']+2.0/3*(c['h_plank_width']-c['crenel_depth']),-1*c['router_bit_radius']],
    [0*c['plank_height'], c['crenel_depth']+2.0/3*(c['h_plank_width']-c['crenel_depth']), 0*c['router_bit_radius']],
    [0*c['plank_height'], c['crenel_depth']+1.0/3*(c['h_plank_width']-c['crenel_depth']), 0*c['router_bit_radius']],
    [1*c['plank_height'], c['crenel_depth']+1.0/3*(c['h_plank_width']-c['crenel_depth']),-1*c['router_bit_radius']]]
  return(nr)

# jonction_plank_bot_yz_with_xz
def jonction_plank_bot_yz_with_xz(c):
  nr = [
    [1*c['plank_height'], 2.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth']),-1*c['router_bit_radius']],
    [0*c['plank_height'], 2.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth']), 0*c['router_bit_radius']],
    [0*c['plank_height'], 1.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth']), 0*c['router_bit_radius']],
    [1*c['plank_height'], 1.0/3*(c['h_plank_width']+c['fitting_height']-c['crenel_depth']),-1*c['router_bit_radius']]]
  return(nr)

# jonction_plank_xz_fitting
def jonction_plank_xz_fitting(c):
  nr = [
    [1.0/4*c['box_width']-1.0/2*c['fitting_height'], 0*c['fitting_height'], 1.0/2*c['fitting_height']],
    [1.0/4*c['box_width']-0.0/2*c['fitting_height'], 1*c['fitting_height'], 1.0/2*c['fitting_height']]]
  return(nr)

# jonction_plank_z_side_with_xz
def jonction_plank_z_side_with_xz(c):
  act = (1+math.sqrt(2))*c['router_bit_radius']
  nr = [
    [0*c['crenel_depth'],     2.0/2*c['v_plank_width'],     1*c['router_bit_radius']],
    [0*c['crenel_depth'],     1.0/2*c['v_plank_width'],     1*c['router_bit_radius']],
    #[1*c['crenel_depth'],    1.0/2*c['v_plank_width'],     1*c['router_bit_radius']],
    [1*c['crenel_depth']+act, 1.0/2*c['v_plank_width'],     1*c['router_bit_radius']],
    [1*c['crenel_depth'],     1.0/2*c['v_plank_width']-act, 0*c['router_bit_radius']],
    [1*c['crenel_depth'],     0.0/2*c['v_plank_width'],     0*c['router_bit_radius']]]
  return(nr)

# jonction_plank_z_with_wall_diagonal
def jonction_plank_z_with_wall_diagonal(c):
  nr = cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(c), -1*c['v_plank_width']+1*c['crenel_depth'], 1, c['v_plank_width'], -1)
  return(nr)

# jonction_plank_wall_diagonal
def jonction_plank_wall_diagonal(c):
  nr = [
    [1*c['d_plank_width']-1*c['crenel_depth']*math.sqrt(2)/2, 1*c['d_plank_width']+0*c['crenel_depth']*math.sqrt(2)/2, 1*c['router_bit_radius']],
    [0*c['d_plank_width']-0*c['crenel_depth']*math.sqrt(2)/2, 0*c['d_plank_width']+1*c['crenel_depth']*math.sqrt(2)/2, 1*c['router_bit_radius']],
    [0*c['d_plank_width']+1*c['crenel_depth']*math.sqrt(2)/2, 0*c['d_plank_width']+0*c['crenel_depth']*math.sqrt(2)/2, 0*c['router_bit_radius']]]
  return(nr)

# jonction_plank_tobo_diagonal
def jonction_plank_tobo_diagonal(c):
  #l_soft_external = c['tobo_diag_depth']/2
  l_soft_external = 0
  nr = [
    [1*c['d_plank_width']+0*c['tobo_diag_depth']*math.sqrt(2)/2, 1*c['d_plank_width']+0*c['tobo_diag_depth']*math.sqrt(2)/2, 1*l_soft_external],
    [1*c['d_plank_width']-1*c['tobo_diag_depth']*math.sqrt(2)/2, 1*c['d_plank_width']-1*c['tobo_diag_depth']*math.sqrt(2)/2,-1*c['router_bit_radius']],
    [1*c['d_plank_width']-2*c['tobo_diag_depth']*math.sqrt(2)/2, 1*c['d_plank_width']-0*c['tobo_diag_depth']*math.sqrt(2)/2, 1*l_soft_external],
    [0*c['d_plank_width']+(1.5-1)*c['tobo_diag_depth']*math.sqrt(2)/2, 0*c['d_plank_width']+(1.5+1)*c['tobo_diag_depth']*math.sqrt(2)/2, 1*l_soft_external],
    [0*c['d_plank_width']+1.5*c['tobo_diag_depth']*math.sqrt(2)/2,     0*c['d_plank_width']+1.5*c['tobo_diag_depth']*math.sqrt(2)/2,-1*c['router_bit_radius']],
    [0*c['d_plank_width']+0*c['tobo_diag_depth']*math.sqrt(2)/2,       0*c['d_plank_width']+0*c['tobo_diag_depth']*math.sqrt(2)/2, 1*l_soft_external]]
  return(nr)

#print("dbg412: jonction_plank_tobo_diagonal", jonction_plank_tobo_diagonal)
# jonction_plank_zx_with_wall_diagonal
def jonction_plank_zx_with_wall_diagonal(c):
  nr = cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(c), -1*c['v_plank_width']+1*c['crenel_depth'], 1, 0*c['v_plank_width'], 1)
  return(nr)

# jonction_plank_zx_with_xz
def jonction_plank_zx_with_xz(c):
  nr = [
    [0, 1*c['v_plank_width'], 1*c['router_bit_radius']],
    [0, 0*c['v_plank_width'], 1*c['router_bit_radius']]]
  return(nr)

#   jonction_slab_side_with_wall_diagonal_horizontal
def jonction_slab_side_with_wall_diagonal_horizontal(c):
  act = (1+math.sqrt(2))*c['router_bit_radius']
  nr = [
    [c['wall_diagonal_size']+0*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)-1*c['cutting_extra'],  0*c['crenel_depth']+1*c['cutting_extra'], -1*c['router_bit_radius']],
    [c['wall_diagonal_size']+1*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'], -1*c['crenel_depth']+0*c['cutting_extra'], 1*c['router_bit_radius']],
    [c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'], -1*c['crenel_depth']+0*c['cutting_extra'], 1*c['router_bit_radius']],
    #[c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'],  0*c['crenel_depth']+1*c['cutting_extra'],-1*c['router_bit_radius']]]
    [c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'],  0*c['crenel_depth']+act+1*c['cutting_extra'], 1*c['router_bit_radius']],
    [c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+act+0*c['cutting_extra'],  0*c['crenel_depth']+1*c['cutting_extra'], 0*c['router_bit_radius']]]
  return(nr)

#   jonction_slab_side_with_wall_diagonal_vertical
def jonction_slab_side_with_wall_diagonal_vertical(c):
  act = (1+math.sqrt(2))*c['router_bit_radius']
  nr = [
    #[ 0*c['crenel_depth']+1*c['cutting_extra'], c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'], -1*c['router_bit_radius']],
    [ 0*c['crenel_depth']+1*c['cutting_extra'], c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+act+0*c['cutting_extra'],  0*c['router_bit_radius']],
    [ 0*c['crenel_depth']+act+1*c['cutting_extra'], c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'],  1*c['router_bit_radius']],
    [-1*c['crenel_depth']+0*c['cutting_extra'], c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'],  1*c['router_bit_radius']],
    [-1*c['crenel_depth']+0*c['cutting_extra'], c['wall_diagonal_size']+1*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'],  1*c['router_bit_radius']],
    [ 0*c['crenel_depth']+1*c['cutting_extra'], c['wall_diagonal_size']+0*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)-1*c['cutting_extra'], -1*c['router_bit_radius']]]
  return(nr)

## hole sub   
# plank_xz_hole plank_yz_hole
def plank_xz_yz_hole(c, nai_box_size, nai_module_width):
  hdx = (c['d_plank_width']*math.sqrt(2)-(1+1.5)*c['tobo_diag_depth'])
  hdy = c['d_plank_height']
  hpx = c['tobo_diagonal_size'] + c['tobo_diag_depth'] + 0*c['plank_height']
  #hpy = ai_diagonal_lining_height
  act = (1+math.sqrt(2))*c['router_bit_radius']
  plank_xz_hole_outline = [ # the y position is not set yet for an easier re-use for other planks
    [hpx+0*hdx-1*c['cutting_extra'], 0*hdy-act-1*c['cutting_extra'], 1*c['router_bit_radius']],
    [hpx+0*hdx+act-1*c['cutting_extra'], 0*hdy-1*c['cutting_extra'], 0*c['router_bit_radius']],
    [hpx+1*hdx-act+1*c['cutting_extra'], 0*hdy-1*c['cutting_extra'], 0*c['router_bit_radius']],
    [hpx+1*hdx+1*c['cutting_extra'], 0*hdy-act-1*c['cutting_extra'], 1*c['router_bit_radius']],
    [hpx+1*hdx+1*c['cutting_extra'], 1*hdy+act+1*c['cutting_extra'], 1*c['router_bit_radius']],
    [hpx+1*hdx-act+1*c['cutting_extra'], 1*hdy+1*c['cutting_extra'], 0*c['router_bit_radius']],
    [hpx+0*hdx+act-1*c['cutting_extra'], 1*hdy+1*c['cutting_extra'], 0*c['router_bit_radius']],
    [hpx+0*hdx-1*c['cutting_extra'], 1*hdy+act+1*c['cutting_extra'], 1*c['router_bit_radius']]]
  plank_xz_hole_A = cnc25d_api.outline_close(plank_xz_hole_outline)
  ## array of holes
  r_plank_xz_hole_fig = []
  ## place the holes
  r_plank_xz_hole_fig.append(cnc25d_api.outline_shift_x(plank_xz_hole_A, 0*nai_box_size+c['plank_height'], 1))
  for i in range(nai_module_width-1):
    r_plank_xz_hole_fig.append(cnc25d_api.outline_shift_x(plank_xz_hole_A, (i+1)*nai_box_size-1.0/2*c['plank_height']-hdx-2*hpx, 1))
    r_plank_xz_hole_fig.append(cnc25d_api.outline_shift_x(plank_xz_hole_A, (i+1)*nai_box_size+1.0/2*c['plank_height'], 1))
  r_plank_xz_hole_fig.append(cnc25d_api.outline_shift_x(plank_xz_hole_A, nai_module_width*nai_box_size-c['plank_height']-hdx-2*hpx, 1))
  return(r_plank_xz_hole_fig)

def plank_xz_top_hole(c):
  r_fig = []
  r_fig.extend(cnc25d_api.rotate_and_translate_figure(plank_xz_yz_hole(c, c['box_width'], c['module_width']), 0,0,0, 0, c['diagonal_lining_top_height']))
  for i in range(c['module_width']-1):
    r_fig.extend(hole_in_plank_top_xz_for_yz(c, (i+1)*c['box_width']))
  return(r_fig)

def plank_xz_bottom_hole(c):
  r_fig = []
  r_fig.extend(cnc25d_api.rotate_and_translate_figure(plank_xz_yz_hole(c, c['box_width'], c['module_width']), 0,0,0, 0, c['h_plank_width']+c['fitting_height']-c['d_plank_height']-c['diagonal_lining_bottom_height']))
  for i in range(c['module_width']-1):
    r_fig.extend(hole_in_plank_bot_xz_for_yz(c, (i+1)*c['box_width']))
  return(r_fig)

def plank_yz_top_hole(c):
  r_fig = []
  r_fig.extend(cnc25d_api.rotate_and_translate_figure(plank_xz_yz_hole(c, c['box_depth'], 1), 0,0,0, 0, c['diagonal_lining_top_height']))
  return(r_fig)

def plank_yz_bottom_hole(c):
  r_fig = []
  r_fig.extend(cnc25d_api.rotate_and_translate_figure(plank_xz_yz_hole(c, c['box_depth'], 1), 0,0,0, 0, c['h_plank_width']+c['fitting_height']-c['d_plank_height']-c['diagonal_lining_bottom_height']))
  return(r_fig)

##
## plank_xz_top
def plank_xz_top(c):
  """ Create the FreeCAD Part Object plank_xz_top
  """
  # plank_xz_top_outline
  plank_xz_top_outline = []
  plank_xz_top_outline.append([0*c['box_width'], 0*c['h_plank_width'], 0*c['router_bit_radius']]) #0
  plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_zx(c),             0*c['box_width'], 1)) #1-4
  plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(c),  0*c['box_width'], 1)) #5-8
  for i in range(c['module_width']-1):
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(c),  (i+1)*c['box_width']+1.0/2*c['v_plank_width'], -1))
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_middle_zx(c),      (i+1)*c['box_width'],  1))
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(c),  (i+1)*c['box_width']-1.0/2*c['v_plank_width'], 1))
  plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(c),  c['module_width']*c['box_width'], -1)) #9-12
  plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_zx(c),             c['module_width']*c['box_width'], -1)) #13-16
  plank_xz_top_outline.append([c['module_width']*c['box_width'], 0*c['plank_height'], 0*c['router_bit_radius']]) #17
  plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_top_xz_with_yz(c),         c['module_width']*c['box_width'], -1)) #18-21
  plank_xz_top_outline.append([c['module_width']*c['box_width'], 1*c['h_plank_width'], 0*c['router_bit_radius']]) #22
  for i in range(c['module_width']):
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_fitting(c)[::-1],    (c['module_width']-i)*c['box_width'], -1, c['h_plank_width'], 1)) #23-24
    plank_xz_top_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_fitting(c)[::-1],  (c['module_width']-1-i)*c['box_width'],  1, c['h_plank_width'], 1)) #25-26
  plank_xz_top_outline.append([0*c['box_width'], 1*c['h_plank_width'], 0*c['router_bit_radius']]) #27
  plank_xz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_top_xz_with_yz(c),         0*c['box_width'],  1)) #28-31
  plank_xz_top_A = cnc25d_api.outline_close(plank_xz_top_outline)
  # final build of  the plank plank_xz_top
  r_fig = [plank_xz_top_A]
  r_fig.extend(plank_xz_top_hole(c))
  return(r_fig)

## plank_xz_bottom
def plank_xz_bottom(c):
  """ Create the FreeCAD Part Object plank_xz_bottom
  """
  # plank_xz_bottom_outline
  plank_xz_bottom_outline = []
  plank_xz_bottom_outline.append([0*c['box_width'], 0*(c['h_plank_width']+c['fitting_height']), 0*c['router_bit_radius']]) #0
  for i in range(c['module_width']):
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_fitting(c),              i*c['box_width'], 1)) #1-2
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_fitting(c),          (i+1)*c['box_width'],-1))
  plank_xz_bottom_outline.append([c['module_width']*c['box_width'], 0*(c['h_plank_width']+c['fitting_height']), 0*c['router_bit_radius']])
  plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_bot_xz_with_yz(c),          c['module_width']*c['box_width'], -1))
  plank_xz_bottom_outline.append([c['module_width']*c['box_width'], 1*(c['h_plank_width']+c['fitting_height']), 0*c['router_bit_radius']])
  plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_zx(c),             c['module_width']*c['box_width'], -1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(c),  c['module_width']*c['box_width'], -1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  for i in range(c['module_width']-1):
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(c),  (c['module_width']-i-1)*c['box_width']-1.0/2*c['v_plank_width'],  1, 1*(c['h_plank_width']+c['fitting_height']), -1))
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_middle_zx(c),      (c['module_width']-i-1)*c['box_width'], 1, 1*(c['h_plank_width']+c['fitting_height']), -1))
    plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(c),  (c['module_width']-i-1)*c['box_width']+1.0/2*c['v_plank_width'], -1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(c),  0*c['box_width'],  1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_zx(c),             0*c['box_width'],  1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  plank_xz_bottom_outline.append([0*c['box_width'], 1*(c['h_plank_width']+c['fitting_height']), 0*c['router_bit_radius']])
  plank_xz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_bot_xz_with_yz(c),          0*c['box_width'],  1))
  plank_xz_bottom_A = cnc25d_api.outline_close(plank_xz_bottom_outline)
  r_fig = [plank_xz_bottom_A]
  r_fig.extend(plank_xz_bottom_hole(c))
  return(r_fig)

## plank_yz_top
def plank_yz_top(c):
  """ Create the FreeCAD Part Object plank_yz_top
  """
  # plank_yz_top_outline
  plank_yz_top_outline = []
  plank_yz_top_outline.append([0*c['box_depth']+1*c['plank_height'], 0*c['h_plank_width'], 0*c['router_bit_radius']]) #0
  plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_zx(c),            0*c['box_depth']+1*c['plank_height'], 1)) #1-4
  plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(c), 0*c['box_depth']+1*c['plank_height'], 1)) #5-8
  plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_wall_diagonal(c), 1*c['box_depth']-1*c['plank_height'], -1)) #9-12
  plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_with_zx(c),            1*c['box_depth']-1*c['plank_height'], -1)) #13-16
  plank_yz_top_outline.append([1*c['box_depth']-1*c['plank_height'], 0*c['plank_height'], 0*c['router_bit_radius']]) #17
  plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_top_yz_with_xz(c),            1*c['box_depth'], -1)) #18-21
  plank_yz_top_outline.append([1*c['box_depth']-1*c['plank_height'], 1*c['h_plank_width'], 0*c['router_bit_radius']]) #22
  plank_yz_top_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_fitting(c)[::-1], 1*c['box_depth'], -1, c['h_plank_width'], 1)) #23-24
  plank_yz_top_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_fitting(c)[::-1], 0*c['box_depth'],  1, c['h_plank_width'], 1)) #25-26
  plank_yz_top_outline.append([0*c['box_depth']+1*c['plank_height'], 1*c['h_plank_width'], 0*c['router_bit_radius']]) #27
  plank_yz_top_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_top_yz_with_xz(c),            0*c['box_depth'],  1)) #28-31
  plank_yz_top_A = cnc25d_api.outline_close(plank_yz_top_outline)
  r_fig = [plank_yz_top_A]
  r_fig.extend(plank_yz_top_hole(c))
  return(r_fig)

## plank_yz_bottom
def plank_yz_bottom(c):
  """ Create the FreeCAD Part Object plank_yz_bottom
  """
  # plank_yz_bottom_outline
  plank_yz_bottom_outline = []
  plank_yz_bottom_outline.append([0*c['box_depth']+1*c['plank_height'], 0*(c['h_plank_width']+c['fitting_height']), 0*c['router_bit_radius']]) #0
  plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_fitting(c), 0*c['box_depth'], 1)) #1-2
  plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_xz_fitting(c), 1*c['box_depth'],-1))
  plank_yz_bottom_outline.append([1*c['box_depth']-1*c['plank_height'], 0*(c['h_plank_width']+c['fitting_height']), 0*c['router_bit_radius']])
  plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_bot_yz_with_xz(c),  1*c['box_depth'], -1))
  plank_yz_bottom_outline.append([1*c['box_depth']-1*c['plank_height'], 1*(c['h_plank_width']+c['fitting_height']), 0*c['router_bit_radius']])
  plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_zx(c),
    1*c['box_depth']-1*c['plank_height'], -1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(c),
    1*c['box_depth']-1*c['plank_height'], -1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_wall_diagonal(c),
    0*c['box_depth']+1*c['plank_height'],  1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_xz_with_zx(c),
    0*c['box_depth']+1*c['plank_height'],  1, 1*(c['h_plank_width']+c['fitting_height']), -1))
  plank_yz_bottom_outline.append([0*c['box_depth']+1*c['plank_height'], 1*(c['h_plank_width']+c['fitting_height']), 0*c['router_bit_radius']])
  plank_yz_bottom_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_bot_yz_with_xz(c),  0*c['box_depth'],  1))
  plank_yz_bottom_A = cnc25d_api.outline_close(plank_yz_bottom_outline)
  r_fig = [plank_yz_bottom_A]
  r_fig.extend(plank_yz_bottom_hole(c))
  return(r_fig)

## plank_z_side
def plank_z_side(c):
  """ Create the FreeCAD Part Object plank_z_side
  """
  # plank_z_side_outline
  #plank_z_side_length = c['box_height'] - 2*c['h_plank_width'] - c['fitting_height'] + 2*c['crenel_depth']
  plank_z_side_length = c['plank_z_length']
  plank_z_side_outline = []
  plank_z_side_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_z_side_with_xz(c), 0*plank_z_side_length, 1))
  plank_z_side_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_z_side_with_xz(c), 1*plank_z_side_length,-1))
  plank_z_side_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_z_with_wall_diagonal(c), 1*plank_z_side_length,-1))
  plank_z_side_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_z_with_wall_diagonal(c), 0*plank_z_side_length, 1))
  plank_z_side_A = cnc25d_api.outline_close(plank_z_side_outline)
  r_fig = [plank_z_side_A]
  return(r_fig)

## plank_wall_diagonal
def plank_wall_diagonal(c):
  """ Create the FreeCAD Part Object plank_wall_diagonal
  """
  #c['plank_wall_diagonal_length'] = (c['wall_diagonal_size']+2*c['crenel_depth'])*math.sqrt(2)+2*(c['d_plank_width']-c['crenel_depth']*math.sqrt(2)/2)
  #print("dbg825: c['plank_wall_diagonal_length']:", c['plank_wall_diagonal_length'])
  plank_wall_diagonal_outline = []
  plank_wall_diagonal_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_wall_diagonal(c), 1*c['plank_wall_diagonal_length'], -1))
  plank_wall_diagonal_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_wall_diagonal(c), 0*c['plank_wall_diagonal_length'],  1))
  plank_wall_diagonal_A = cnc25d_api.outline_close(plank_wall_diagonal_outline)
  r_fig = [plank_wall_diagonal_A]
  return(r_fig)

## plank_tobo_diagonal
def plank_tobo_diagonal(c):
  """ Create the FreeCAD Part Object plank_tobo_diagonal
  """
  #c['plank_tobo_diagonal_length'] = c['tobo_diagonal_size']*math.sqrt(2)+2*c['d_plank_width']+0*c['tobo_diag_depth']*math.sqrt(2)/2
  plank_tobo_diagonal_outline = []
  plank_tobo_diagonal_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_tobo_diagonal(c), 1*c['plank_tobo_diagonal_length'], -1))
  plank_tobo_diagonal_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_tobo_diagonal(c), 0*c['plank_tobo_diagonal_length'],  1))
  plank_tobo_diagonal_A = cnc25d_api.outline_close(plank_tobo_diagonal_outline)
  r_fig = [plank_tobo_diagonal_A]
  return(r_fig)

## plank_zx_middle
def plank_zx_middle(c):
  """ Create the FreeCAD Part Object plank_zx_middle
  """
  #plank_z_side_length = c['box_height'] - 2*c['h_plank_width'] - c['fitting_height'] + 2*c['crenel_depth']
  plank_z_side_length = c['plank_z_length']
  plank_zx_middle_outline = []
  plank_zx_middle_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_zx_with_wall_diagonal(c), 0*plank_z_side_length, 1, 0*c['v_plank_width'], 1))
  plank_zx_middle_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_zx_with_wall_diagonal(c), 1*plank_z_side_length,-1, 0*c['v_plank_width'], 1))
  plank_zx_middle_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_zx_with_xz(c), 1*plank_z_side_length,-1))
  plank_zx_middle_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_zx_with_wall_diagonal(c), 1*plank_z_side_length,-1, 1*c['v_plank_width'], -1))
  plank_zx_middle_outline.extend(cnc25d_api.outline_shift_xy(jonction_plank_zx_with_wall_diagonal(c), 0*plank_z_side_length, 1, 1*c['v_plank_width'], -1))
  plank_zx_middle_outline.extend(cnc25d_api.outline_shift_x(jonction_plank_zx_with_xz(c), 0*plank_z_side_length, 1))
  plank_zx_middle_A = cnc25d_api.outline_close(plank_zx_middle_outline)
  r_fig = [plank_zx_middle_A]
  return(r_fig)

## plank_hole_cover
def plank_hole_cover(c):
  """ Create the FreeCAD Part Object plank_hole_cover
  """
  hdx = c['plank_hole_cover_length']
  hdy = c['plank_hole_cover_width']
  hdz = c['plank_hole_cover_height']
  plank_hole_cover_outline = []
  plank_hole_cover_outline.append([0*hdx, 0*hdy, 0])
  plank_hole_cover_outline.append([1*hdx, 0*hdy, 0])
  plank_hole_cover_outline.append([1*hdx, 1*hdy, 0])
  plank_hole_cover_outline.append([0*hdx, 1*hdy, 0])
  #plank_hole_cover_outline.append([plank_hole_cover_outline[0][0], plank_hole_cover_outline[0][1], 0]) # close the outline
  plank_hole_cover_A = cnc25d_api.outline_close(plank_hole_cover_outline)
  r_fig = [plank_hole_cover_A]
  return(r_fig)

## slab_top_bottom
def slab_top_bottom(c, nai_type):
  """ Create the FreeCAD Part Object slab_top_bottom
  """
  if(nai_type=='single'):
    slab_length = c['slab_top_bottom_single_length']
  elif(nai_type=='side'):
    slab_length = c['slab_top_bottom_side_length']
  elif(nai_type=='middle'):
    slab_length = c['slab_top_bottom_middle_length']
  slab_width = c['slab_top_bottom_width']
  slab_top_bottom_outline = []
  slab_top_bottom_outline.append([0*slab_length+1*c['cutting_extra'], 0*slab_width+1*c['cutting_extra'], 0])
  slab_top_bottom_outline.append([1*slab_length-1*c['cutting_extra'], 0*slab_width+1*c['cutting_extra'], 0])
  slab_top_bottom_outline.append([1*slab_length-1*c['cutting_extra'], 1*slab_width-1*c['cutting_extra'], 0])
  slab_top_bottom_outline.append([0*slab_length+1*c['cutting_extra'], 1*slab_width-1*c['cutting_extra'], 0])
  slab_top_bottom_A = cnc25d_api.outline_close(slab_top_bottom_outline)
  r_fig = [slab_top_bottom_A]
  return(r_fig)

## slab_left_right and slab_rear
def slab_side(c, nai_type):
  """ Create the FreeCAD Part Object slab_side
  """
  slab_length = c['slab_side_length']
  if(nai_type=='left_right'):
    slab_width = c['slab_side_left_right_width']
  elif(nai_type=='rear_single'):
    slab_width = c['slab_side_rear_single_width']
  elif(nai_type=='rear_side'):
    slab_width = c['slab_side_rear_side_width']
  elif(nai_type=='rear_middle'):
    slab_width = c['slab_side_rear_middle_width']
  slab_side_outline = []
  slab_side_outline.append([0*slab_length+1*c['cutting_extra'], 0*slab_width+1*c['cutting_extra'], 0])
  slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_horizontal(c), 0*slab_length, 1, 0*slab_width, 1))
  slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_horizontal(c), 1*slab_length,-1, 0*slab_width, 1))
  slab_side_outline.append([1*slab_length-1*c['cutting_extra'], 0*slab_width+1*c['cutting_extra'], 0])
  slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_vertical(c), 1*slab_length,-1, 0*slab_width, 1))
  slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_vertical(c), 1*slab_length,-1, 1*slab_width,-1))
  slab_side_outline.append([1*slab_length-1*c['cutting_extra'], 1*slab_width-1*c['cutting_extra'], 0])
  slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_horizontal(c), 1*slab_length, -1, 1*slab_width,-1))
  slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_horizontal(c), 0*slab_length,  1, 1*slab_width,-1))
  slab_side_outline.append([0*slab_length+1*c['cutting_extra'], 1*slab_width-1*c['cutting_extra'], 0])
  slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_vertical(c), 0*slab_length, 1, 1*slab_width,-1))
  slab_side_outline.extend(cnc25d_api.outline_shift_xy(jonction_slab_side_with_wall_diagonal_vertical(c), 0*slab_length, 1, 0*slab_width, 1))
  slab_side_A = cnc25d_api.outline_close(slab_side_outline)
  r_fig = [slab_side_A]
  return(r_fig)

## slab_front
def slab_front(c):
  """ Create the FreeCAD Part Object slab_front
  """
  slab_front_outline = []
  slab_front_outline.append([0+1*c['cutting_extra'], 0+1*c['cutting_extra'], 0])
  slab_front_outline.append([c['wall_diagonal_size']+0*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)-1*c['cutting_extra'], 0*c['crenel_depth']+1*c['cutting_extra'], -1*c['router_bit_radius']])
  slab_front_outline.append([c['wall_diagonal_size']+1*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'], -1*c['crenel_depth']+0*c['cutting_extra'], 1*c['router_bit_radius']])
  slab_front_outline.append([c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'], -1*c['crenel_depth']+0*c['cutting_extra'], 1*c['router_bit_radius']])
  slab_front_outline.append([c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'],  0*c['crenel_depth']+0*c['cutting_extra'], 0*c['router_bit_radius']])
  slab_front_outline.append([ 0*c['crenel_depth']+0*c['cutting_extra'], c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'], 0*c['router_bit_radius']])
  slab_front_outline.append([-1*c['crenel_depth']+0*c['cutting_extra'], c['wall_diagonal_size']+0*c['crenel_depth']+1*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'], 1*c['router_bit_radius']])
  slab_front_outline.append([-1*c['crenel_depth']+0*c['cutting_extra'], c['wall_diagonal_size']+1*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)+0*c['cutting_extra'], 1*c['router_bit_radius']])
  slab_front_outline.append([ 0*c['crenel_depth']+1*c['cutting_extra'], c['wall_diagonal_size']+0*c['crenel_depth']+0*c['d_plank_width']*math.sqrt(2)-1*c['cutting_extra'], -1*c['router_bit_radius']])
  slab_front_A = cnc25d_api.outline_close(slab_front_outline)
  r_fig = [slab_front_A]
  return(r_fig)



