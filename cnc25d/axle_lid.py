# axle_lid.py
# generates an axle_lid assembly that can complete a epicyclic-gearing.
# created by charlyoleg on 2013/10/15
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
axle_lid.py is a parametric generator of an assembly that completes the epicyclic-gearing system.
The main function displays in a Tk-interface the axle-lid assembly, or generates the design as files or returns the design as FreeCAD Part object.
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
import re # to detect .dxf or .svg
#import Tkinter # to display the outline in a small GUI
#
import Part
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import gearring

################################################################
# axle_lid dictionary-arguments default values
################################################################

def axle_lid_dictionary_init():
  """ create and initiate an axle_lid_dictionary with the default value
  """
  r_ald = {}
  ### annulus-holder: inherit dictionary entries from gearring
  r_ald.update(gearring.gearring_dictionary_init(1))
  #### axle_lid dictionary entries
  r_ald['clearance_diameter']     = 50.0
  r_ald['central_diameter']       = 30.0
  r_ald['axle_hole_diameter']     = 22.0
  r_ald['annulus_holder_axle_hole_diameter'] = 0.0
  ### axle-B
  r_ald['output_axle_B_place']              = 'none' # 'none', 'small' or 'large' # useful when the gearring has an odd number of crenels
  r_ald['output_axle_distance']             = 0.0
  r_ald['output_axle_angle']             = 0.0
  r_ald['output_axle_B_internal_diameter']  = 0.0
  r_ald['output_axle_B_external_diameter']  = 0.0
  r_ald['output_axle_B_crenel_number']              = 0
  r_ald['output_axle_B_crenel_diameter']            = 0.0
  r_ald['output_axle_B_crenel_position_diameter']   = 0.0
  r_ald['output_axle_B_crenel_angle']               = 0.0
  ### leg
  r_ald['leg_type']             = 'none' # 'none', 'rear' or 'side'
  r_ald['leg_length']           = 0.0
  r_ald['foot_length']          = 0.0
  r_ald['toe_length']           = 0.0
  r_ald['leg_hole_diameter']    = 0.0
  r_ald['leg_hole_distance']    = 0.0
  r_ald['leg_hole_length']      = 0.0
  r_ald['leg_border_length']    = 0.0
  r_ald['leg_shift_length']     = 0.0
  ### general
  r_ald['smoothing_radius']       = 0.0
  r_ald['cnc_router_bit_radius']  = 0.1
  r_ald['extrusion_height']       = 10.0
  ### output
  r_ald['tkinter_view']           = False
  r_ald['output_file_basename']   = ''
  ### optional
  r_ald['args_in_txt'] = ""
  r_ald['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_ald)

################################################################
# axle_lid argparse
################################################################

def axle_lid_add_argument(ai_parser):
  """
  Add arguments relative to the axle-lid in addition to the argument of gearring(variant=1)
  This function intends to be used by the axle_lid_cli and axle_lid_self_test
  """
  r_parser = ai_parser
  ### annulus-holder: inherit dictionary entries from gearring
  r_parser = gearring.gearring_add_argument(r_parser, 1)
  ### axle_lid stuff
  r_parser.add_argument('--clearance_diameter','--cld', action='store', type=float, default=50.0, dest='sw_clearance_diameter',
    help="Set the diameter of the clearance circle. Default: 50.0")
  r_parser.add_argument('--central_diameter','--ced', action='store', type=float, default=50.0, dest='sw_central_diameter',
    help="Set the diameter of the central circle. Default: 30.0")
  r_parser.add_argument('--axle_hole_diameter','--ahd', action='store', type=float, default=22.0, dest='sw_axle_hole_diameter',
    help="Set the diameter of the axle-hole. Default: 22.0")
  r_parser.add_argument('--annulus_holder_axle_hole_diameter','--ahahd', action='store', type=float, default=0.0, dest='sw_annulus_holder_axle_hole_diameter',
    help="Set the diameter of the axle-hole on the annulus-holder side. If equal to 0.0, it is set to axle_hole_diameter. Default: 0.0")
  ### axle-B
  r_parser.add_argument('--output_axle_B_place','--oabp', action='store', default='none', dest='sw_output_axle_B_place',
    help="Set the side to generate the axle_B. Possible values: 'none', 'small', 'large'. Default: 'none'")
  r_parser.add_argument('--output_axle_distance','--oad', action='store', type=float, default=0.0, dest='sw_output_axle_distance',
    help="Set the distance between the output_axle and output_axle_B. Default: 0.0")
  r_parser.add_argument('--output_axle_angle','--oaa', action='store', type=float, default=0.0, dest='sw_output_axle_angle',
    help="Set the angle between the output_axle and output_axle_B. Default: 0.0")
  r_parser.add_argument('--output_axle_B_internal_diameter','--oabid', action='store', type=float, default=0.0, dest='sw_output_axle_B_internal_diameter',
    help="Set the internal diameter of the axle_B. Default: 0.0")
  r_parser.add_argument('--output_axle_B_external_diameter','--oabed', action='store', type=float, default=0.0, dest='sw_output_axle_B_external_diameter',
    help="Set the external diameter of the axle_B. If equal to 0.0, it is set to 2*output_axle_B_internal_diameter. Default: 0.0")
  r_parser.add_argument('--output_axle_B_crenel_number','--oabcn', action='store', type=int, default=0, dest='sw_output_axle_B_crenel_number',
    help="Set the number of crenels around the axle_B. If equal to 0, no crenel for the axle_B is generated. Default: 0")
  r_parser.add_argument('--output_axle_B_crenel_diameter','--oabcd', action='store', type=float, default=0.0, dest='sw_output_axle_B_crenel_diameter',
    help="Set the diameter of the crenels placed around the axle_B. Default: 0.0")
  r_parser.add_argument('--output_axle_B_crenel_position_diameter','--oabcpd', action='store', type=float, default=0.0, dest='sw_output_axle_B_crenel_position_diameter',
    help="Set the diameter of the position circle of the axle_B crenels. If equal to 0.0, it is set to the mean of the axle_B external and internal diameters. Default: 0.0")
  r_parser.add_argument('--output_axle_B_crenel_angle','--oabca', action='store', type=float, default=0.0, dest='sw_output_axle_B_crenel_angle',
    help="Set the position angle of the first crenel placed around the axle_B. Default: 0.0")
  ### leg
  r_parser.add_argument('--leg_type','--lt', action='store', default='none', dest='sw_leg_type',
    help="Set the type of leg. Possible values: 'none', 'rear', 'side'. Default: 'none'")
  r_parser.add_argument('--leg_length','--ll', action='store', type=float, default=0.0, dest='sw_leg_length',
    help="Set the length between the center of the gearring and the end of the leg. Default: 0.0")
  r_parser.add_argument('--foot_length','--fl', action='store', type=float, default=0.0, dest='sw_foot_length',
    help="Set the length between the end of the leg and the center of the holes. If equal to 0.0, set to leg_hole_diameter. Default: 0.0")
  r_parser.add_argument('--toe_length','--tl', action='store', type=float, default=0.0, dest='sw_toe_length',
    help="Set the length between the center of the holes and the end of the leg-foot-toe. If equal to 0.0, set to leg_hole_diameter. Default: 0.0")
  r_parser.add_argument('--leg_hole_diameter','--lhd', action='store', type=float, default=0.0, dest='sw_leg_hole_diameter',
    help="Set the diameter of the leg-holes. If equal to 0.0, no holes is generated. Default: 0.0")
  r_parser.add_argument('--leg_hole_distance','--lhdis', action='store', type=float, default=0.0, dest='sw_leg_hole_distance',
    help="Set the distance between a pair of leg-holes. If equal to 0.0, it is set to 2*leg_hole_diameter. Default: 0.0")
  r_parser.add_argument('--leg_hole_length','--lhl', action='store', type=float, default=0.0, dest='sw_leg_hole_length',
    help="Set the length of the leg-holes. Default: 0.0")
  r_parser.add_argument('--leg_border_length','--lbl', action='store', type=float, default=0.0, dest='sw_leg_border_length',
    help="Set the width of the leg-borders. If equal to 0.0, it is set to leg_hole_diameter. Default: 0.0")
  r_parser.add_argument('--leg_shift_length','--lsl', action='store', type=float, default=0.0, dest='sw_leg_shift_length',
    help="Set the length between middle axe of the gearring and the middle of the pair of leg-holes. Default: 0.0")
  ### general
  r_parser.add_argument('--smoothing_radius','--sr', action='store', type=float, default=0.0, dest='sw_smoothing_radius',
    help="Set the smoothing radius for the axle-lid. If equal to 0.0, it is set to cnc_router_bit_radius. Default: 0.0")
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the axle-lid. Default: 0.1")
  r_parser.add_argument('--extrusion_height','--eh', action='store', type=float, default=10.0, dest='sw_extrusion_height',
    help="Set the height of the linear extrusion of each part of the axle_lid assembly. Default: 10.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def axle_lid(ai_constraints):
  """
  The main function of the script.
  It generates an axle-lid assembly according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  aldi = axle_lid_dictionary_init()
  al_c = aldi.copy()
  al_c.update(ai_constraints)
  #print("dbg155: al_c:", al_c)
  if(len(al_c.viewkeys() & aldi.viewkeys()) != len(al_c.viewkeys() | aldi.viewkeys())): # check if the dictionary al_c has exactly all the keys compare to axle_lid_dictionary_init()
    print("ERR157: Error, al_c has too much entries as {:s} or missing entries as {:s}".format(al_c.viewkeys() - aldi.viewkeys(), aldi.viewkeys() - al_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new axle_lid constraints:")
  #for k in al_c.viewkeys():
  #  if(al_c[k] != aldi[k]):
  #    print("dbg166: for k {:s}, al_c[k] {:s} != aldi[k] {:s}".format(k, str(al_c[k]), str(aldi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  cnc_router_bit_radius = al_c['cnc_router_bit_radius']
  axle_hole_radius = al_c['axle_hole_diameter']/2.0
  central_radius = al_c['central_diameter']/2.0
  clearance_radius = al_c['clearance_diameter']/2.0
  holder_radius = al_c['holder_diameter']/2.0
  annulus_holder_axle_hole_radius = al_c['annulus_holder_axle_hole_diameter']/2.0
  if(annulus_holder_axle_hole_radius==0):
    if(axle_hole_radius>radian_epsilon):
      annulus_holder_axle_hole_radius = axle_hole_radius
    else:
      annulus_holder_axle_hole_radius = clearance_radius #holder_radius/2.0 # rare case not really usefull
  #if(cnc_router_bit_radius>axle_hole_radius):
  #  print("ERR141: Error, cnc_router_bit_radius {:0.3f} is bigger than axle_hole_radius {:0.3f}".format(cnc_router_bit_radius, axle_hole_radius))
  #  sys.exit(2)
  if(axle_hole_radius>central_radius-radian_epsilon):
    print("ERR144: Error, axle_hole_radius {:0.3f} is bigger than central_radius {:0.3f}".format(axle_hole_radius, central_radius))
    sys.exit(2)
  if(central_radius>clearance_radius-radian_epsilon):
    print("ERR147: Error, central_radius {:0.3f} is bigger than clearance_radius {:0.3f}".format(central_radius, clearance_radius))
    sys.exit(2)
  if(clearance_radius>holder_radius-radian_epsilon):
    print("ERR151: Error, clearance_radius {:0.3f} is bigger than the holder_radius {:0.3f}".format(clearance_radius, holder_radius))
    sys.exit(2)
  if(annulus_holder_axle_hole_radius>clearance_radius):
    print("ERR159: Error, annulus_holder_axle_hole_radius {:0.3f} is bigger than clearance_radius {:0.3f}".format(annulus_holder_axle_hole_radius, clearance_radius))
    sys.exit(2)
  holder_crenel_number = al_c['holder_crenel_number']
  if(holder_crenel_number<4):
    print("ERR154: Error, holder_crenel_number {:d} is smaller than 4".format(holder_crenel_number))
    sys.exit(2)
  middle_crenel_1 = 0
  middle_crenel_2 = int(holder_crenel_number/2)
  if(al_c['output_axle_B_place'] == 'large'):
    middle_crenel_2 = int((holder_crenel_number+1)/2)
  middle_crenel_index = [middle_crenel_1, middle_crenel_2]
  crenel_portion_angle = 2*math.pi/holder_crenel_number
  ### axle_lid_overlay_figure: add stuff on it when you want
  axle_lid_overlay_figure = []
  ### gearring-holder
  gr_c = {}
  gr_c['gear_tooth_nb']               = 0
  gr_c['gear_primitive_diameter']     = 2.0*annulus_holder_axle_hole_radius
  gr_c['holder_diameter']             = 2.0*holder_radius
  gr_c['holder_crenel_number']        = holder_crenel_number
  gr_c['holder_position_angle']       = al_c['holder_position_angle']
  gr_c['holder_hole_position_radius'] = al_c['holder_hole_position_radius']
  gr_c['holder_hole_diameter']        = al_c['holder_hole_diameter']
  gr_c['holder_double_hole_diameter'] = al_c['holder_double_hole_diameter']
  gr_c['holder_double_hole_length']   = al_c['holder_double_hole_length']
  gr_c['holder_double_hole_position'] = al_c['holder_double_hole_position']
  gr_c['holder_double_hole_mark_nb']  = al_c['holder_double_hole_mark_nb']
  gr_c['holder_crenel_position']      = al_c['holder_crenel_position']
  gr_c['holder_crenel_height']        = al_c['holder_crenel_height']
  gr_c['holder_crenel_width']         = al_c['holder_crenel_width']
  gr_c['holder_crenel_skin_width']    = al_c['holder_crenel_skin_width']
  gr_c['holder_crenel_router_bit_radius'] = al_c['holder_crenel_router_bit_radius']
  gr_c['holder_smoothing_radius']     = al_c['holder_smoothing_radius']
  gr_c['cnc_router_bit_radius']       = cnc_router_bit_radius
  gr_c['gear_profile_height']         = al_c['extrusion_height']
  gr_c['center_position_x']           = 0.0
  gr_c['center_position_y']           = 0.0
  gr_c['gear_initial_angle']          = 0.0
  gr_c['tkinter_view']                = False
  gr_c['simulation_enable']           = False
  gr_c['output_file_basename']        = ""
  gr_c['args_in_txt']                 = "gearring for axle_lid"
  gr_c['return_type']                 = 'cnc25d_figure_and_parameters'
  (annulus_holder_figure_not_used, holder_parameters) = gearring.gearring(gr_c)
  ### holder_cut_outlines
  holder_cut_side_outlines = []
  holder_cut_face_outlines = []
  #
  ( holder_crenel_half_width, holder_crenel_half_angle, holder_smoothing_radius, holder_crenel_x_position, holder_maximal_height_plus,
    holder_crenel_router_bit_radius, holder_side_outer_smoothing_radius,
    holder_hole_position_radius, holder_hole_radius,
    holder_double_hole_radius, holder_double_hole_length, holder_double_hole_position, holder_double_hole_mark_nb, holder_double_hole_position_radius,
    holder_radius, holder_maximal_radius) = holder_parameters
  #print("dbg204: holder_hole_radius {:0.3f}  holder_double_hole_length {:0.3f}".format(holder_hole_radius, holder_double_hole_length))
  g1_ix = 0.0
  g1_iy = 0.0
  middle_angle_1 = (middle_crenel_1 + 1 + middle_crenel_2)/2.0*crenel_portion_angle + gr_c['holder_position_angle']
  middle_angle_2 = middle_angle_1 + math.pi
  middle_angles = (middle_angle_1, middle_angle_2)
  angle_incr = crenel_portion_angle
  lid_router_bit_radius = holder_crenel_router_bit_radius
  lid_smoothing_router_bit_radius = al_c['smoothing_radius']
  if(lid_smoothing_router_bit_radius==0):
    lid_smoothing_router_bit_radius = lid_router_bit_radius
  ## holder_cut_side_outlines
  for i in range(len(middle_crenel_index)):
    idx = middle_crenel_index[i]
    holder_A = []
    # first crenel
    holder_A .extend(gearring.make_holder_crenel(holder_maximal_height_plus, gr_c['holder_crenel_height'], gr_c['holder_crenel_skin_width'], holder_crenel_half_width, 
                                        holder_crenel_router_bit_radius, holder_side_outer_smoothing_radius, holder_smoothing_radius,
                                        holder_crenel_x_position, gr_c['holder_position_angle']+idx*angle_incr, g1_ix, g1_iy))
    # external arc
    middle_angle = gr_c['holder_position_angle'] + (idx+0.5)*angle_incr
    end_angle = gr_c['holder_position_angle'] + (idx+1)*angle_incr - holder_crenel_half_angle
    holder_A.append([g1_ix+holder_radius*math.cos(middle_angle), g1_iy+holder_radius*math.sin(middle_angle),
                      g1_ix+holder_radius*math.cos(end_angle), g1_iy+holder_radius*math.sin(end_angle), holder_smoothing_radius])
    # second crenel
    holder_A .extend(gearring.make_holder_crenel(holder_maximal_height_plus, gr_c['holder_crenel_height'], gr_c['holder_crenel_skin_width'], holder_crenel_half_width, 
                                        holder_crenel_router_bit_radius, holder_side_outer_smoothing_radius, holder_smoothing_radius,
                                        holder_crenel_x_position, gr_c['holder_position_angle']+(idx+1)*angle_incr, g1_ix, g1_iy))
    #holder_A[-1] = (holder_A[-1][0], holder_A[-1][1], lid_router_bit_radius) # change the router_bit of the last point # this point must be removed
    # save the portion of outline
    holder_cut_side_outlines.append(holder_A[:-1]) # remove the last point
  holder_cut_first_point = holder_cut_side_outlines[0][0]
  ## holder_cut_face_outlines
  for i in range(len(middle_crenel_index)):
    idx = middle_crenel_index[i] + 1
    cut_length = (middle_crenel_index[i-1] - (middle_crenel_index[i-2] + 1) + holder_crenel_number) % holder_crenel_number - 1
    #print("dbg296: idx {:d}  cut_length {:d}   middle_crenel_index_i_-1 {:d}   middle_crenel_index_i_-2 {:d}".format(idx, cut_length, middle_crenel_index[i-1], middle_crenel_index[i-2]))
    holder_A = []
    # first point
    first_angle = gr_c['holder_position_angle'] + (idx+0.0)*angle_incr + holder_crenel_half_angle
    holder_A.append([g1_ix+holder_radius*math.cos(first_angle), g1_iy+holder_radius*math.sin(first_angle), holder_smoothing_radius])
    # first arc
    middle_angle = gr_c['holder_position_angle'] + (idx+0.5)*angle_incr
    end_angle = gr_c['holder_position_angle'] + (idx+1)*angle_incr - holder_crenel_half_angle
    holder_A.append([g1_ix+holder_radius*math.cos(middle_angle), g1_iy+holder_radius*math.sin(middle_angle),
                      g1_ix+holder_radius*math.cos(end_angle), g1_iy+holder_radius*math.sin(end_angle), holder_smoothing_radius])
    for j in range(cut_length):
      # crenel
      holder_A .extend(gearring.make_holder_crenel(holder_maximal_height_plus, gr_c['holder_crenel_height'], gr_c['holder_crenel_skin_width'], holder_crenel_half_width, 
                                          holder_crenel_router_bit_radius, holder_side_outer_smoothing_radius, holder_smoothing_radius,
                                          holder_crenel_x_position, gr_c['holder_position_angle']+(idx+j+1)*angle_incr, g1_ix, g1_iy))
      # external arc
      middle_angle = gr_c['holder_position_angle'] + (idx+j+1.5)*angle_incr
      end_angle = gr_c['holder_position_angle'] + (idx+j+2)*angle_incr - holder_crenel_half_angle
      holder_A.append([g1_ix+holder_radius*math.cos(middle_angle), g1_iy+holder_radius*math.sin(middle_angle),
                        g1_ix+holder_radius*math.cos(end_angle), g1_iy+holder_radius*math.sin(end_angle), holder_smoothing_radius])
    # save the portion of outline
    holder_cut_face_outlines.append(holder_A[:]) # small and large faces
  ### middle_axle_lid
  middle_lid_outlines = []
  for i in range(2):
    idx = middle_crenel_index[i]
    holder_A = []
    # first point
    first_angle = gr_c['holder_position_angle'] - holder_crenel_half_angle + idx*angle_incr
    holder_A.append([g1_ix+clearance_radius*math.cos(first_angle), g1_iy+clearance_radius*math.sin(first_angle), lid_router_bit_radius])
    # first line
    holder_A.append([g1_ix+holder_radius*math.cos(first_angle), g1_iy+holder_radius*math.sin(first_angle), lid_router_bit_radius])
    # holder_cut_side_outlines
    holder_A.extend(holder_cut_side_outlines[i])
    # second to last line
    last_angle = gr_c['holder_position_angle'] + holder_crenel_half_angle + (idx+1)*angle_incr
    holder_A.append([g1_ix+holder_radius*math.cos(last_angle), g1_iy+holder_radius*math.sin(last_angle), lid_router_bit_radius])
    holder_A.append([g1_ix+clearance_radius*math.cos(last_angle), g1_iy+clearance_radius*math.sin(last_angle), lid_router_bit_radius])
    # last arc
    middle_angle = gr_c['holder_position_angle'] + (idx+0.5)*angle_incr
    holder_A.append([g1_ix+clearance_radius*math.cos(middle_angle), g1_iy+clearance_radius*math.sin(middle_angle),
                      g1_ix+clearance_radius*math.cos(first_angle), g1_iy+clearance_radius*math.sin(first_angle), 0])
    # save the portion of outline
    middle_lid_outlines.append(holder_A[:])
  ## overlay for check
  axle_lid_overlay_figure.append(cnc25d_api.ideal_outline(middle_lid_outlines[0], "middle_lid_outlines"))
  ### holes
  ## side_hole_figures
  side_hole_figures = []
  for i in range(2):
    idx = middle_crenel_index[i]
    hole_figure = []
    if(holder_hole_radius>0):
      for j in range(2):
        hole_angle = gr_c['holder_position_angle']+((idx+j)*angle_incr)
        hole_figure.append([g1_ix+holder_hole_position_radius*math.cos(hole_angle), g1_iy+holder_hole_position_radius*math.sin(hole_angle), holder_hole_radius])
    if(holder_double_hole_radius>0):
      tmp_a2 = math.atan(holder_double_hole_length/2.0/holder_double_hole_position_radius) # if double carrier-crenel-hole
      tmp_l2 = math.sqrt(holder_double_hole_position_radius**2+(holder_double_hole_length/2.0)**2)
      for j in range(2):
        hole_angle = gr_c['holder_position_angle']+((idx+j)*angle_incr)
        hole_figure.append([g1_ix+tmp_l2*math.cos(hole_angle-tmp_a2), g1_iy+tmp_l2*math.sin(hole_angle-tmp_a2), holder_double_hole_radius])
        hole_figure.append([g1_ix+tmp_l2*math.cos(hole_angle+tmp_a2), g1_iy+tmp_l2*math.sin(hole_angle+tmp_a2), holder_double_hole_radius])
    side_hole_figures.append(hole_figure[:])
  ## face_hole_figures
  face_hole_figures = []
  for i in range(2):
    idx = middle_crenel_index[i] + 2
    cut_length = (middle_crenel_index[i-1] - (middle_crenel_index[i-2] + 1) + holder_crenel_number) % holder_crenel_number - 1
    hole_figure = []
    if(holder_hole_radius>0):
      for j in range(cut_length):
        hole_angle = gr_c['holder_position_angle']+((idx+j)*angle_incr)
        hole_figure.append([g1_ix+holder_hole_position_radius*math.cos(hole_angle), g1_iy+holder_hole_position_radius*math.sin(hole_angle), holder_hole_radius])
    if(holder_double_hole_radius>0):
      tmp_a2 = math.atan(holder_double_hole_length/2.0/holder_double_hole_position_radius) # if double carrier-crenel-hole
      tmp_l2 = math.sqrt(holder_double_hole_position_radius**2+(holder_double_hole_length/2.0)**2)
      for j in range(cut_length):
        hole_angle = gr_c['holder_position_angle']+((idx+j)*angle_incr)
        hole_figure.append([g1_ix+tmp_l2*math.cos(hole_angle-tmp_a2), g1_iy+tmp_l2*math.sin(hole_angle-tmp_a2), holder_double_hole_radius])
        hole_figure.append([g1_ix+tmp_l2*math.cos(hole_angle+tmp_a2), g1_iy+tmp_l2*math.sin(hole_angle+tmp_a2), holder_double_hole_radius])
    face_hole_figures.append(hole_figure[:])

  ## middle_axle_lid
  middle_lid_figures = []
  for i in range(2):
    one_middle_figure = []
    one_middle_figure.append(cnc25d_api.cnc_cut_outline(middle_lid_outlines[i], "middle_lid_outlines"))
    one_middle_figure.extend(side_hole_figures[i]) 
    middle_lid_figures.append(one_middle_figure[:])

  ### face_top_lid_outlines
  face_top_lid_outlines = []
  for i in range(2):
    idx_1 = middle_crenel_index[i]+1
    idx_2 = middle_crenel_index[i-1]
    first_angle = gr_c['holder_position_angle'] + holder_crenel_half_angle + idx_1*angle_incr
    last_angle = gr_c['holder_position_angle'] - holder_crenel_half_angle + idx_2*angle_incr
    holder_A = []
    holder_A.append([g1_ix+holder_radius*math.cos(first_angle), g1_iy+holder_radius*math.sin(first_angle), lid_router_bit_radius])
    holder_A.append([g1_ix+clearance_radius*math.cos(first_angle), g1_iy+clearance_radius*math.sin(first_angle), lid_router_bit_radius])
    holder_A.append((g1_ix+central_radius*math.cos(middle_angles[i]), g1_iy+central_radius*math.sin(middle_angles[i]), holder_smoothing_radius))
    holder_A.append([g1_ix+clearance_radius*math.cos(last_angle), g1_iy+clearance_radius*math.sin(last_angle), lid_router_bit_radius])
    holder_A.append([g1_ix+holder_radius*math.cos(last_angle), g1_iy+holder_radius*math.sin(last_angle), lid_router_bit_radius])
    # save the portion of outline
    face_top_lid_outlines.append(holder_A[:])

  ### axle_B
  output_axle_B_internal_radius = al_c['output_axle_B_internal_diameter']/2.0
  output_axle_B_external_radius = al_c['output_axle_B_external_diameter']/2.0
  output_axle_B_crenel_radius = al_c['output_axle_B_crenel_diameter']/2.0
  output_axle_B_crenel_position_radius = al_c['output_axle_B_crenel_position_diameter']/2.0
  output_axle_B_angle = middle_angle_1 + al_c['output_axle_angle']
  if(al_c['output_axle_B_place'] != 'none'):
    if((al_c['output_axle_B_place'] != 'small')and(al_c['output_axle_B_place'] != 'large')):
      print("ERR442: Error, output_axle_B_place {:s} is unknown. Possible values: 'none', 'small' or 'large'".format(al_c['output_axle_B_place']))
      sys.exit(2)
    if(al_c['output_axle_distance']<=0.0):
      print("ERR445: Error, output_axle_distance {:0.3f} must be positive".format(al_c['output_axle_distance']))
      sys.exit(2)
    if(output_axle_B_external_radius == 0):
      output_axle_B_external_radius = 2*output_axle_B_internal_radius
    if(output_axle_B_external_radius<=output_axle_B_internal_radius):
      print("ERR452: Error, output_axle_B_external_radius {:0.3f} is null or smaller than output_axle_B_internal_radius {:0.3f}".format(output_axle_B_external_radius, output_axle_B_internal_radius))
      sys.exit(2)
    if(al_c['output_axle_B_crenel_number']>0):
      if(output_axle_B_crenel_radius<radian_epsilon):
        print("ERR460: Error, output_axle_B_crenel_radius {:0.3f} is too small".format(output_axle_B_crenel_radius))
        sys.exit(2)
      if(output_axle_B_crenel_position_radius == 0):
        output_axle_B_crenel_position_radius = (output_axle_B_internal_radius + output_axle_B_external_radius)/2.0
      if(output_axle_B_crenel_position_radius<(output_axle_B_internal_radius+output_axle_B_crenel_radius)):
        print("ERR460: Error, output_axle_B_crenel_position_radius {:0.3f} is too small compare to output_axle_B_internal_radius {:0.3f} and output_axle_B_crenel_radius {:0.3f}".format(output_axle_B_crenel_position_radius, output_axle_B_internal_radius, output_axle_B_crenel_radius))
        sys.exit(2)
      if(output_axle_B_crenel_position_radius>(output_axle_B_external_radius-output_axle_B_crenel_radius)):
        print("ERR463: Error, output_axle_B_crenel_position_radius {:0.3f} is too big compare to output_axle_B_external_radius {:0.3f} and output_axle_B_crenel_radius {:0.3f}".format(output_axle_B_crenel_position_radius, output_axle_B_external_radius, output_axle_B_crenel_radius))
        sys.exit(2)
    ## calculation of the angle (DCE)
    ABC = (middle_crenel_2 - middle_crenel_1 - 1) * crenel_portion_angle / 2.0 - holder_crenel_half_angle
    ABC1 = ABC + al_c['output_axle_angle']
    AB = holder_maximal_radius
    BC = al_c['output_axle_distance']
    # law of cosines to get AC and (ACB)
    AC1 = math.sqrt(AB**2 + BC**2 - 2*AB*BC*math.cos(ABC1))
    cos_ACB1 = ((AC1**2+BC**2-AB**2)/(2*AC1*BC))
    if((cos_ACB1<radian_epsilon)or(cos_ACB1>1-radian_epsilon)):
      print("ERR474: Error, cos_ACB1 {:0.3f} is out of the range 0..1".format(cos_ACB1))
      sys.exit(2)
    ACB1 = math.acos(cos_ACB1)
    DC = output_axle_B_external_radius
    cos_ACD1 = float(DC)/AC1
    ACD1 = math.acos(cos_ACD1)
    DCE1 = math.pi - ACD1 - ACB1
    ABC2 = ABC - al_c['output_axle_angle']
    AC2 = math.sqrt(AB**2 + BC**2 - 2*AB*BC*math.cos(ABC2))
    cos_ACB2 = ((AC2**2+BC**2-AB**2)/(2*AC2*BC))
    ACB2 = math.acos(cos_ACB2)
    cos_ACD2 = float(DC)/AC2
    ACD2 = math.acos(cos_ACD2)
    DCE2 = math.pi - ACD2 - ACB2
    #print("dbg486: ACD {:0.3f}  ACB {:0.3f}  DC {:0.3f}  AC {:0.3f}".format(ACD, ACB, DC, AC))
    #print("dbg483: DCE {:0.3f}  middle_angle_1 {:0.3f}".format(DCE, middle_angle_1))
    ## axle_B_outline
    axle_B_outline = []
    axle_B_outline.append((g1_ix+BC*math.cos(output_axle_B_angle)+DC*math.cos(output_axle_B_angle-DCE1), g1_iy+BC*math.sin(output_axle_B_angle)+DC*math.sin(output_axle_B_angle-DCE1), 0))
    axle_B_outline.append((g1_ix+BC*math.cos(output_axle_B_angle)+DC*math.cos(output_axle_B_angle+(DCE2-DCE1)/2.0), g1_iy+BC*math.sin(output_axle_B_angle)+DC*math.sin(output_axle_B_angle+(DCE2-DCE1)/2.0),
                           g1_ix+BC*math.cos(output_axle_B_angle)+DC*math.cos(output_axle_B_angle+DCE2), g1_iy+BC*math.sin(output_axle_B_angle)+DC*math.sin(output_axle_B_angle+DCE2), 0))
    ## axle_B_hole_figure
    axle_B_hole_figure = []
    if(output_axle_B_internal_radius>radian_epsilon):
      axle_B_hole_figure.append((g1_ix+BC*math.cos(output_axle_B_angle), g1_iy+BC*math.sin(output_axle_B_angle), output_axle_B_internal_radius))
    if(al_c['output_axle_B_crenel_number']>0):
      crenel_B_angle = 2*math.pi/al_c['output_axle_B_crenel_number']
      for i in range(al_c['output_axle_B_crenel_number']):
        axle_B_hole_figure.append((g1_ix+BC*math.cos(output_axle_B_angle)+output_axle_B_crenel_position_radius*math.cos(output_axle_B_angle+i*crenel_B_angle+al_c['output_axle_B_crenel_angle']),
                              g1_iy+BC*math.sin(output_axle_B_angle)+output_axle_B_crenel_position_radius*math.sin(output_axle_B_angle+i*crenel_B_angle+al_c['output_axle_B_crenel_angle']),
                              output_axle_B_crenel_radius))

  ### leg_outline
  # default values
  leg_hole_radius = al_c['leg_hole_diameter']/2.0
  foot_length = al_c['foot_length']
  if(foot_length==0):
    foot_length = 2*leg_hole_radius
  toe_length = al_c['toe_length']
  if(toe_length==0):
    toe_length = 2*leg_hole_radius
  leg_border_length = al_c['leg_border_length']
  if(leg_border_length==0):
    leg_border_length = 2*leg_hole_radius
  leg_hole_distance = al_c['leg_hole_distance']
  if(leg_hole_distance==0):
    leg_hole_distance = 2*(2*leg_hole_radius + al_c['leg_hole_length'])
  if(al_c['leg_type'] != 'none'):
    if((al_c['leg_type'] != 'rear') and (al_c['leg_type'] != 'side')):
      print("ERR536: Error, leg_type {:s} set to an unknow value. Possible values: 'none', 'rear' or 'side'".format(al_c['leg_type']))
      sys.exit(2)
    if(al_c['leg_length']<=0):
      print("ERR539: Error, leg_length {:0.3f} must be strictly positive".format(al_c['leg_length']))
      sys.exit(2)
    if(toe_length<leg_hole_radius):
      print("ERR543: Error, toe_length {:0.3f} is smaller than leg_hole_radius {:0.3f}".format(toe_length, leg_hole_radius))
      sys.exit(2)
    #if(foot_length<leg_hole_radius):
    #  print("ERR543: Error, foot_length {:0.3f} is smaller than leg_hole_radius {:0.3f}".format(foot_length, leg_hole_radius))
    #  sys.exit(2)
    if(leg_hole_distance<2*leg_hole_radius+al_c['leg_hole_length']):
      print("ERR549: Error, leg_hole_distance {:0.3f} is too small compare to leg_hole_radius {:0.3f} and leg_hole_length {:0.3f}".format(leg_hole_distance, leg_hole_radius, al_c['leg_hole_length']))
      sys.exit(2)
    if(leg_border_length<leg_hole_radius):
      print("ERR552: Error, leg_border_length {:0.3f} is smaller than leg_hole_radius {:0.3f}".format(leg_border_length, leg_hole_radius))
      sys.exit(2)

  def leg_outline(ai_direction, ai_shift_coef):
    """ It generates the outline of a leg. It can be used to generate the left-side, right-side and rear leg.
        ai_shift_coef lets invert the leg_shift_length parameter if needed
    """
    r_leg_outline = []
    leg_width = leg_hole_distance + al_c['leg_hole_length'] + 2 * leg_border_length
    tx = g1_ix + al_c['leg_length'] * math.cos(ai_direction)
    ty = g1_iy + al_c['leg_length'] * math.sin(ai_direction)
    tx += (leg_width/2.0 + ai_shift_coef * al_c['leg_shift_length']) * math.cos(ai_direction-math.pi/2)
    ty += (leg_width/2.0 + ai_shift_coef * al_c['leg_shift_length']) * math.sin(ai_direction-math.pi/2)
    r_leg_outline.append((tx, ty, lid_smoothing_router_bit_radius))
    tx += (foot_length + toe_length) * math.cos(ai_direction)
    ty += (foot_length + toe_length) * math.sin(ai_direction)
    r_leg_outline.append((tx, ty, lid_smoothing_router_bit_radius))
    tx += leg_width * math.cos(ai_direction + math.pi/2)
    ty += leg_width * math.sin(ai_direction + math.pi/2)
    r_leg_outline.append((tx, ty, lid_smoothing_router_bit_radius))
    tx += (foot_length + toe_length) * math.cos(ai_direction + math.pi)
    ty += (foot_length + toe_length) * math.sin(ai_direction + math.pi)
    r_leg_outline.append((tx, ty, lid_smoothing_router_bit_radius))
    return(r_leg_outline)

  def leg_hole_figure(ai_direction, ai_shift_coef):
    """ It generates the holes of a leg. It can be used to generate the holes of the left-side, right-side and rear leg.
        ai_shift_coef lets invert the leg_shift_length parameter if needed
    """
    r_leg_hole_figure = []
    cx = g1_ix + (al_c['leg_length'] + foot_length) * math.cos(ai_direction)
    cy = g1_iy + (al_c['leg_length'] + foot_length) * math.sin(ai_direction)
    hd = (leg_hole_distance - al_c['leg_hole_length'])/2.0 + ai_shift_coef * al_c['leg_shift_length']
    cx += hd * math.cos(ai_direction - math.pi/2)
    cy += hd * math.sin(ai_direction - math.pi/2)
    if(leg_hole_radius>0):
      for i in range(2):
        hole_outline = []
        c1x = cx + i * leg_hole_distance * math.cos(ai_direction+math.pi/2)
        c1y = cy + i * leg_hole_distance * math.sin(ai_direction+math.pi/2)
        s1x = c1x + leg_hole_radius * math.cos(ai_direction)
        s1y = c1y + leg_hole_radius * math.sin(ai_direction)
        m1x = c1x + leg_hole_radius * math.cos(ai_direction+math.pi/2)
        m1y = c1y + leg_hole_radius * math.sin(ai_direction+math.pi/2)
        e1x = c1x + leg_hole_radius * math.cos(ai_direction+math.pi)
        e1y = c1y + leg_hole_radius * math.sin(ai_direction+math.pi)
        c2x = c1x + al_c['leg_hole_length'] * math.cos(ai_direction-math.pi/2)
        c2y = c1y + al_c['leg_hole_length'] * math.sin(ai_direction-math.pi/2)
        s2x = c2x +  leg_hole_radius * math.cos(ai_direction-math.pi)
        s2y = c2y +  leg_hole_radius * math.sin(ai_direction-math.pi)
        m2x = c2x +  leg_hole_radius * math.cos(ai_direction-math.pi/2)
        m2y = c2y +  leg_hole_radius * math.sin(ai_direction-math.pi/2)
        e2x = c2x +  leg_hole_radius * math.cos(ai_direction)
        e2y = c2y +  leg_hole_radius * math.sin(ai_direction)
        hole_outline.append((e1x, e1y))
        if(al_c['leg_hole_length']>0):
          hole_outline.append((s2x, s2y))
        hole_outline.append((m2x, m2y, e2x, e2y))
        if(al_c['leg_hole_length']>0):
          hole_outline.append((s1x, s1y))
        hole_outline.append((m1x, m1y, e1x, e1y))
        r_leg_hole_figure.append(hole_outline[:])
    return(r_leg_hole_figure)

  ## annulus_holder_figure
  def f_annulus_holder_figure(ai_axle_B_type, ai_leg_type):
    """ generate the annulus_holder_figure
    """
    annulus_holder_outline = []
    if(ai_leg_type == 'side'):
      annulus_holder_outline.append((holder_cut_first_point[0], holder_cut_first_point[1], lid_smoothing_router_bit_radius))
      annulus_holder_outline.extend(leg_outline(middle_angle_1-math.pi/2, 1))
      annulus_holder_outline.append((holder_cut_side_outlines[0][-1][0], holder_cut_side_outlines[0][-1][1], lid_smoothing_router_bit_radius))
    else:
      annulus_holder_outline.extend(holder_cut_side_outlines[0])
    if(ai_axle_B_type != 'none'):
      annulus_holder_outline.extend(axle_B_outline)
    else:
      annulus_holder_outline.extend(holder_cut_face_outlines[0])
    if(ai_leg_type == 'side'):
      annulus_holder_outline.append((holder_cut_side_outlines[1][0][0], holder_cut_side_outlines[1][0][1], lid_smoothing_router_bit_radius))
      annulus_holder_outline.extend(leg_outline(middle_angle_1+math.pi/2, -1))
      annulus_holder_outline.append((holder_cut_side_outlines[1][-1][0], holder_cut_side_outlines[1][-1][1], lid_smoothing_router_bit_radius))
    else:
      annulus_holder_outline.extend(holder_cut_side_outlines[1])
    if(ai_leg_type == 'rear'):
      annulus_holder_outline.extend(leg_outline(middle_angle_1+math.pi, 1))
    else:
      annulus_holder_outline.extend(holder_cut_face_outlines[1])
    annulus_holder_outline.append((holder_cut_first_point[0], holder_cut_first_point[1], 0))
    r_annulus_holder_figure = []
    r_annulus_holder_figure.append(cnc25d_api.cnc_cut_outline(annulus_holder_outline, "annulus_holder_outline"))
    r_annulus_holder_figure.append((g1_ix, g1_iy, annulus_holder_axle_hole_radius))
    r_annulus_holder_figure.extend(side_hole_figures[0])
    if(ai_axle_B_type != 'none'):
      r_annulus_holder_figure.extend(axle_B_hole_figure)
    else:
      r_annulus_holder_figure.extend(face_hole_figures[0])
    r_annulus_holder_figure.extend(side_hole_figures[1])
    r_annulus_holder_figure.extend(face_hole_figures[1])
    if(ai_leg_type == 'side'):
      r_annulus_holder_figure.extend(leg_hole_figure(middle_angle_1-math.pi/2, 1))
      r_annulus_holder_figure.extend(leg_hole_figure(middle_angle_1+math.pi/2, -1))
    elif(ai_leg_type == 'rear'):
      r_annulus_holder_figure.extend(leg_hole_figure(middle_angle_1+math.pi, 1))
    return(r_annulus_holder_figure)

    # top_lid_figure
  def f_top_lid_figure(ai_axle_B_type, ai_leg_type):
    """ generate the top_lid_figure
    """
    top_lid_outline = []
    if(ai_leg_type == 'side'):
      top_lid_outline.append((holder_cut_first_point[0], holder_cut_first_point[1], lid_smoothing_router_bit_radius))
      top_lid_outline.extend(leg_outline(middle_angle_1-math.pi/2, 1))
      top_lid_outline.append((holder_cut_side_outlines[0][-1][0], holder_cut_side_outlines[0][-1][1], lid_smoothing_router_bit_radius))
    else:
      top_lid_outline.extend(holder_cut_side_outlines[0])
    if(ai_axle_B_type != 'none'):
      top_lid_outline.extend(axle_B_outline)
    else:
      top_lid_outline.extend(face_top_lid_outlines[0])
    if(ai_leg_type == 'side'):
      top_lid_outline.append((holder_cut_side_outlines[1][0][0], holder_cut_side_outlines[1][0][1], lid_smoothing_router_bit_radius))
      top_lid_outline.extend(leg_outline(middle_angle_1+math.pi/2, -1))
      top_lid_outline.append((holder_cut_side_outlines[1][-1][0], holder_cut_side_outlines[1][-1][1], lid_smoothing_router_bit_radius))
    else:
      top_lid_outline.extend(holder_cut_side_outlines[1])
    if(ai_leg_type == 'rear'):
      top_lid_outline.extend(leg_outline(middle_angle_1+math.pi, 1))
    else:
      top_lid_outline.extend(face_top_lid_outlines[1])
    top_lid_outline.append((holder_cut_first_point[0], holder_cut_first_point[1], 0))
    r_top_lid_figure = []
    r_top_lid_figure.append(cnc25d_api.cnc_cut_outline(top_lid_outline, "top_lid_outline"))
    if(axle_hole_radius>radian_epsilon):
      r_top_lid_figure.append((g1_ix, g1_iy, axle_hole_radius))
    r_top_lid_figure.extend(side_hole_figures[0])
    if(ai_axle_B_type != 'none'):
      r_top_lid_figure.extend(axle_B_hole_figure)
    r_top_lid_figure.extend(side_hole_figures[1])
    if(ai_leg_type == 'side'):
      r_top_lid_figure.extend(leg_hole_figure(middle_angle_1-math.pi/2, 1))
      r_top_lid_figure.extend(leg_hole_figure(middle_angle_1+math.pi/2, -1))
    elif(ai_leg_type == 'rear'):
      r_top_lid_figure.extend(leg_hole_figure(middle_angle_1+math.pi, 1))
    return(r_top_lid_figure)

  ## figure generation
  annulus_holder_figure = f_annulus_holder_figure(al_c['output_axle_B_place'], al_c['leg_type'])
  top_lid_figure = f_top_lid_figure(al_c['output_axle_B_place'], al_c['leg_type'])
  annulus_holder_simple_figure = f_annulus_holder_figure('none', 'none')
  top_lid_simple_figure = f_top_lid_figure('none', 'none')
  annulus_holder_with_axle_B_figure = f_annulus_holder_figure(al_c['output_axle_B_place'], 'none')
  top_lid_with_axle_B_figure = f_top_lid_figure(al_c['output_axle_B_place'], 'none')
  annulus_holder_with_leg_figure = f_annulus_holder_figure('none', al_c['leg_type'])
  top_lid_with_leg_figure = f_top_lid_figure('none', al_c['leg_type'])
  # selection
  main_annulus_holder_figure = annulus_holder_figure[:]
  main_top_lid_figure = top_lid_figure[:]

  # overlay debug
  #axle_lid_overlay_figure.append(cnc25d_api.ideal_outline(top_lid_outline, "top_lid_outline"))

  ### design output
  part_figure_list = []
  #part_figure_list.append(annulus_holder_figure)
  part_figure_list.append(main_annulus_holder_figure)
  part_figure_list.append(middle_lid_figures[0])
  part_figure_list.append(middle_lid_figures[1])
  #part_figure_list.append(top_lid_figure)
  part_figure_list.append(main_top_lid_figure)
  # al_assembly_figure: assembly flatted in one figure
  al_assembly_figure = []
  for i in range(len(part_figure_list)):
    al_assembly_figure.extend(part_figure_list[i])
  # ideal_outline in overlay
  al_assembly_figure_overlay = []
  # al_list_of_parts: all parts aligned flatted in one figure
  x_space = 3.1*holder_radius
  al_list_of_parts = []
  for i in range(len(part_figure_list)):
    for j in range(len(part_figure_list[i])):
      al_list_of_parts.append(cnc25d_api.outline_shift_x(part_figure_list[i][j], i*x_space, 1))

  # al_parameter_info
  al_parameter_info = "\naxle_lid parameter info:\n"
  al_parameter_info += "\n" + al_c['args_in_txt'] + "\n\n"
  al_parameter_info += """
holder crenel number:     \t{:d}
holder hole radius:       \t{:0.3f} diameter: \t{:0.3f}
holder external radius:   \t{:0.3f} diameter: \t{:0.3f}
clearance radius:         \t{:0.3f} diameter: \t{:0.3f}
central radius:           \t{:0.3f} diameter: \t{:0.3f}
axle-hole radius:         \t{:0.3f} diameter: \t{:0.3f}
annulus-holder-axle-hole radius: \t{:0.3f} diameter: \t{:0.3f}
holder_crenel_router_bit_radius:  \t{:0.3f} diameter: \t{:0.3f}
holder_smoothing_radius:          \t{:0.3f} diameter: \t{:0.3f}
cnc_router_bit_radius:    \t{:0.3f} diameter: \t{:0.3f}
""".format(holder_crenel_number, al_c['holder_hole_diameter']/2.0, al_c['holder_hole_diameter'], holder_radius, 2*holder_radius, clearance_radius, 2*clearance_radius, central_radius, 2*central_radius, axle_hole_radius, 2*axle_hole_radius, annulus_holder_axle_hole_radius, 2*annulus_holder_axle_hole_radius, holder_crenel_router_bit_radius, 2*holder_crenel_router_bit_radius, holder_smoothing_radius, 2*holder_smoothing_radius, cnc_router_bit_radius, 2*cnc_router_bit_radius)
  al_parameter_info += """
output_axle_B_place:  \t{:s}
output_axle_distance: \t{:0.3f}
output_axle_angle: \t{:0.3f} (radian) \t{:0.3f} (degree)
output_axle_B_internal_radius: \t{:0.3f}  diameter: \t{:0.3f}
output_axle_B_external_radius: \t{:0.3f}  diameter: \t{:0.3f}
output_axle_B_crenel_number: \t{:d}
output_axle_B_crenel_radius: \t{:0.3f}  diameter: \t{:0.3f}
output_axle_B_crenel_position_radius: \t{:0.3f}  diameter: \t{:0.3f}
output_axle_B_crenel_angle: \t{:0.3f}
""".format(al_c['output_axle_B_place'], al_c['output_axle_distance'], al_c['output_axle_angle'], al_c['output_axle_angle']*180/math.pi,  output_axle_B_internal_radius, 2*output_axle_B_internal_radius, output_axle_B_external_radius, 2*output_axle_B_external_radius, al_c['output_axle_B_crenel_number'], output_axle_B_crenel_radius, 2*output_axle_B_crenel_radius, output_axle_B_crenel_position_radius, 2*output_axle_B_crenel_position_radius, al_c['output_axle_B_crenel_angle'])
  al_parameter_info += """
leg_type:     \t{:s}
leg_length:   \t{:0.3f}
foot_length:  \t{:0.3f}
toe_length:   \t{:0.3f}
leg_hole_radius:    \t{:0.3f}  \tdiameter: {:0.3f}
leg_hole_distance:  \t{:0.3f}
leg_hole_length:    \t{:0.3f}
leg_border_length:  \t{:0.3f}
leg_shift_length:   \t{:0.3f}
""".format(al_c['leg_type'], al_c['leg_length'], foot_length, toe_length, leg_hole_radius, 2*leg_hole_radius, leg_hole_distance, al_c['leg_hole_length'], leg_border_length, al_c['leg_shift_length'])
  #print(al_parameter_info)

  ### display with Tkinter
  if(al_c['tkinter_view']):
    print(al_parameter_info)
    cnc25d_api.figure_simple_display(al_assembly_figure, axle_lid_overlay_figure, al_parameter_info)
    #cnc25d_api.figure_simple_display(main_annulus_holder_figure, axle_lid_overlay_figure, al_parameter_info)
    #cnc25d_api.figure_simple_display(main_top_lid_figure, axle_lid_overlay_figure, al_parameter_info)
      
  ### sub-function to create the freecad-object
  def freecad_axle_lid(nai_part_figure_list):
    fc_obj = []
    for i in range(len(nai_part_figure_list)):
      fc_obj.append(cnc25d_api.figure_to_freecad_25d_part(nai_part_figure_list[i], al_c['extrusion_height']))
      if((i==1)or(i==2)): # front planet-carrier
        fc_obj[i].translate(Base.Vector(0,0,5.0*al_c['extrusion_height']))
      if(i==3): # rear planet-carrier
        fc_obj[i].translate(Base.Vector(0,0,10.0*al_c['extrusion_height']))
    r_fal = Part.makeCompound(fc_obj)
    return(r_fal)

  ### generate output file
  output_file_suffix = ''
  if(al_c['output_file_basename']!=''):
    output_file_suffix = '' # .brep
    output_file_basename = al_c['output_file_basename']
    if(re.search('\.dxf$', al_c['output_file_basename'])):
      output_file_suffix = '.dxf'
      output_file_basename = re.sub('\.dxf$', '', al_c['output_file_basename'])
    elif(re.search('\.svg$', al_c['output_file_basename'])):
      output_file_suffix = '.svg'
      output_file_basename = re.sub('\.svg$', '', al_c['output_file_basename'])
  if(al_c['output_file_basename']!=''):
    # parts
    cnc25d_api.generate_output_file(annulus_holder_figure, output_file_basename + "_annulus_holder" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(middle_lid_figures[0], output_file_basename + "_middle_lid1" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(middle_lid_figures[1], output_file_basename + "_middle_lid2" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(top_lid_figure, output_file_basename + "_top_lid" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(annulus_holder_simple_figure, output_file_basename + "_annulus_holder_simple" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(top_lid_simple_figure, output_file_basename + "_top_lid_simple" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(annulus_holder_with_axle_B_figure, output_file_basename + "_annulus_holder_with_axle_B" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(top_lid_with_axle_B_figure, output_file_basename + "_top_lid_with_axle_B" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(annulus_holder_with_leg_figure, output_file_basename + "_annulus_holder_with_leg" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    cnc25d_api.generate_output_file(top_lid_with_leg_figure, output_file_basename + "_top_lid_with_leg" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    # assembly
    if((output_file_suffix=='.svg')or(output_file_suffix=='.dxf')):
      cnc25d_api.generate_output_file(al_assembly_figure, output_file_basename + "_assembly" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
      cnc25d_api.generate_output_file(al_list_of_parts, output_file_basename + "_part_list" + output_file_suffix, al_c['extrusion_height'], al_parameter_info)
    else:
      fc_assembly_filename = "{:s}_assembly.brep".format(output_file_basename)
      print("Generate with FreeCAD the BRep file {:s}".format(fc_assembly_filename))
      fc_assembly = freecad_axle_lid(part_figure_list)
      fc_assembly.exportBrep(fc_assembly_filename)

  #### return
  if(al_c['return_type']=='int_status'):
    r_al = 1
  elif(al_c['return_type']=='cnc25d_figure'):
    r_al = part_figure_list
  elif(al_c['return_type']=='freecad_object'):
    r_al = freecad_axle_lid(part_figure_list)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(al_c['return_type']))
    sys.exit(2)
  return(r_al)

################################################################
# axle-lid wrapper dance
################################################################

def axle_lid_argparse_to_dictionary(ai_al_args):
  """ convert a axle_lid_argparse into a axle_lid_dictionary
  """
  r_ald = {}
  ### annulus-holder: inherit dictionary entries from gearring
  r_ald.update(gearring.gearring_argparse_to_dictionary(ai_al_args, 1))
  #### axle_lid dictionary entries
  r_ald['clearance_diameter']     = ai_al_args.sw_clearance_diameter
  r_ald['central_diameter']       = ai_al_args.sw_central_diameter
  r_ald['axle_hole_diameter']     = ai_al_args.sw_axle_hole_diameter
  r_ald['annulus_holder_axle_hole_diameter']     = ai_al_args.sw_annulus_holder_axle_hole_diameter
  ### axle-B
  r_ald['output_axle_B_place']              = ai_al_args.sw_output_axle_B_place
  r_ald['output_axle_distance']             = ai_al_args.sw_output_axle_distance
  r_ald['output_axle_angle']                = ai_al_args.sw_output_axle_angle
  r_ald['output_axle_B_internal_diameter']  = ai_al_args.sw_output_axle_B_internal_diameter
  r_ald['output_axle_B_external_diameter']  = ai_al_args.sw_output_axle_B_external_diameter
  r_ald['output_axle_B_crenel_number']              = ai_al_args.sw_output_axle_B_crenel_number
  r_ald['output_axle_B_crenel_diameter']            = ai_al_args.sw_output_axle_B_crenel_diameter
  r_ald['output_axle_B_crenel_position_diameter']   = ai_al_args.sw_output_axle_B_crenel_position_diameter
  r_ald['output_axle_B_crenel_angle']               = ai_al_args.sw_output_axle_B_crenel_angle
  ### leg
  r_ald['leg_type']             = ai_al_args.sw_leg_type
  r_ald['leg_length']           = ai_al_args.sw_leg_length
  r_ald['foot_length']          = ai_al_args.sw_foot_length
  r_ald['toe_length']           = ai_al_args.sw_toe_length
  r_ald['leg_hole_diameter']    = ai_al_args.sw_leg_hole_diameter
  r_ald['leg_hole_distance']    = ai_al_args.sw_leg_hole_distance
  r_ald['leg_hole_length']      = ai_al_args.sw_leg_hole_length
  r_ald['leg_border_length']    = ai_al_args.sw_leg_border_length
  r_ald['leg_shift_length']     = ai_al_args.sw_leg_shift_length
  ### general
  r_ald['smoothing_radius']       = ai_al_args.sw_smoothing_radius
  r_ald['cnc_router_bit_radius']  = ai_al_args.sw_cnc_router_bit_radius
  r_ald['extrusion_height']       = ai_al_args.sw_extrusion_height
  ### output
  #r_ald['tkinter_view']           = False
  r_ald['output_file_basename']   = ai_al_args.sw_output_file_basename
  ### optional
  #r_ald['args_in_txt'] = ""
  r_ald['return_type'] = ai_al_args.sw_return_type
  #### return
  return(r_ald)
  
def axle_lid_argparse_wrapper(ai_al_args, ai_args_in_txt=""):
  """
  wrapper function of axle_lid() to call it using the axle_lid_parser.
  axle_lid_parser is mostly used for debug and non-regression tests.
  """
  # view the axle_lid with Tkinter as default action
  tkinter_view = True
  if(ai_al_args.sw_output_file_basename!=''):
    tkinter_view = False
  # wrapper
  ald = axle_lid_argparse_to_dictionary(ai_al_args)
  ald['args_in_txt'] = ai_args_in_txt
  ald['tkinter_view'] = tkinter_view
  #ald['return_type'] = 'int_status'
  r_al = axle_lid(ald)
  return(r_al)

################################################################
# self test
################################################################

def axle_lid_self_test():
  """
  This is the non-regression test of axle_lid.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 79.0 --axle_hole_diameter 22.0 --holder_crenel_number 6"],
    ["odd number of crenel" , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 5"],
    ["four crenels"         , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 4"],
    ["double-holes only"  , "--holder_diameter 220.0 --clearance_diameter 200.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 8 --holder_double_hole_length 4.0 --holder_double_hole_diameter 3.0 --holder_hole_diameter 0.0"],
    ["single and double holes"  , "--holder_diameter 220.0 --clearance_diameter 200.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 8 --holder_double_hole_length 16.0 --holder_double_hole_diameter 3.0 --holder_hole_diameter 5.0"],
    ["with initial angle"   , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 35.0 --axle_hole_diameter 22.0 --holder_position_angle 0.25"],
    ["with annulus-holder-axle-hole-diameter"   , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 35.0 --axle_hole_diameter 22.0 --annulus_holder_axle_hole_diameter 80.0"],
    ["axle_B with even crenel", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --output_axle_B_place small --output_axle_distance 130.0 --output_axle_B_internal_diameter 20.0 --output_axle_B_external_diameter 40.0"],
    ["axle_B small side", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place small --output_axle_distance 100.0 --output_axle_B_internal_diameter 30.0 --output_axle_B_external_diameter 65.0"],
    ["axle_B large side with crenels", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 170.0 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0 --output_axle_B_crenel_number 7 --output_axle_B_crenel_diameter 1.0"],
    ["axle_B large side angle", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 90.0  --output_axle_angle 0.3 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0"],
    ["axle_B large side angle and no axle_B_hole", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --output_axle_B_place large --output_axle_distance 70.0  --output_axle_angle -0.4 --output_axle_B_internal_diameter 0.0 --output_axle_B_external_diameter 50.0"],
    ["no axle hole", "--holder_diameter 150.0 --clearance_diameter 120.0 --central_diameter 30.0 --axle_hole_diameter 0.0 --holder_crenel_number 7"],
    ["with side leg", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --leg_type side --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0"],
    ["with rear leg", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --leg_type rear --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length -20.0"],
    ["complete with rear leg", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --leg_type rear --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0 --output_axle_B_place large --output_axle_distance 170.0 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0 --output_axle_B_crenel_number 7 --output_axle_B_crenel_diameter 1.0"],
    ["complete with side leg", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --leg_type side --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0 --output_axle_B_place large --output_axle_distance 170.0 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0 --output_axle_B_crenel_number 7 --output_axle_B_crenel_diameter 1.0"],
    ["complete with side leg into file", "--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 5 --leg_type side --leg_length 100.0 --foot_length 20.0 --leg_hole_diameter 10.0 --leg_hole_distance 60.0 --leg_hole_length 20.0 --leg_shift_length 30.0 --output_axle_B_place large --output_axle_distance 170.0 --output_axle_B_internal_diameter 40.0 --output_axle_B_external_diameter 50.0 --output_axle_B_crenel_number 7 --output_axle_B_crenel_diameter 1.0 --output_file_basename test_output/axle_lid_self_test2.dxf"],
    ["output file"          , "--holder_diameter 130.0 --clearance_diameter 115.0 --central_diameter 100.0 --axle_hole_diameter 22.0 --output_file_basename test_output/axle_lid_self_test.dxf"],
    ["last test"            , "--holder_diameter 160.0 --clearance_diameter 140.0 --central_diameter 80.0 --axle_hole_diameter 22.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  axle_lid_parser = argparse.ArgumentParser(description='Command line interface for the function axle_lid().')
  axle_lid_parser = axle_lid_add_argument(axle_lid_parser)
  axle_lid_parser = cnc25d_api.generate_output_file_add_argument(axle_lid_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = axle_lid_parser.parse_args(l_args)
    r_alst = axle_lid_argparse_wrapper(st_args)
  return(r_alst)

################################################################
# axle_lid command line interface
################################################################

def axle_lid_cli(ai_args=""):
  """ command line interface of axle_lid.py when it is used in standalone
  """
  # axle_lid parser
  axle_lid_parser = argparse.ArgumentParser(description='Command line interface for the function axle_lid().')
  axle_lid_parser = axle_lid_add_argument(axle_lid_parser)
  axle_lid_parser = cnc25d_api.generate_output_file_add_argument(axle_lid_parser, 1)
  # switch for self_test
  axle_lid_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "axle_lid arguments: " + ' '.join(effective_args)
  al_args = axle_lid_parser.parse_args(effective_args)
  print("dbg111: start making axle_lid")
  if(al_args.sw_run_self_test):
    r_al = axle_lid_self_test()
  else:
    r_al = axle_lid_argparse_wrapper(al_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_al)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("axle_lid.py says hello!\n")
  #my_al = axle_lid_cli()
  #my_al = axle_lid_cli("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6 --return_type freecad_object")
  my_al = axle_lid_cli("--holder_diameter 100.0 --clearance_diameter 80.0 --central_diameter 30.0 --axle_hole_diameter 22.0 --holder_crenel_number 6")
  #Part.show(my_al)
  try: # depending on al_c['return_type'] it might be or not a freecad_object
    Part.show(my_al)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")

