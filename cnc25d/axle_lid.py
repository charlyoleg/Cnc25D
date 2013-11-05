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
  ### general
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
  ### general
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
    annulus_holder_axle_hole_radius = axle_hole_radius
  if(cnc_router_bit_radius>axle_hole_radius):
    print("ERR141: Error, cnc_router_bit_radius {:0.3f} is bigger than axle_hole_radius {:0.3f}".format(cnc_router_bit_radius, axle_hole_radius))
    sys.exit(2)
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
  gr_c['holder_double_hole_length']   = al_c['holder_double_hole_length']
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
  (annulus_holder_figure, holder_parameters) = gearring.gearring(gr_c)
  ### middle_axle_lid
  middle_lid_outlines = []
  #
  ( holder_crenel_half_width, holder_crenel_half_angle, holder_smoothing_radius, holder_crenel_x_position, holder_maximal_height_plus,
    holder_crenel_router_bit_radius, holder_side_outer_smoothing_radius,
    holder_hole_position_radius, holder_hole_radius, holder_double_hole_length, holder_radius) = holder_parameters
  print("dbg204: holder_hole_radius {:0.3f}  holder_double_hole_length {:0.3f}".format(holder_hole_radius, holder_double_hole_length))
  g1_ix = 0.0
  g1_iy = 0.0
  angle_incr = crenel_portion_angle
  lid_router_bit_radius = holder_crenel_router_bit_radius
  for i in range(2):
    idx = middle_crenel_index[i]
    holder_A = []
    # first point
    first_angle = gr_c['holder_position_angle'] - holder_crenel_half_angle + idx*angle_incr
    holder_A.append([g1_ix+clearance_radius*math.cos(first_angle), g1_iy+clearance_radius*math.sin(first_angle), lid_router_bit_radius])
    # first line
    holder_A.append([g1_ix+holder_radius*math.cos(first_angle), g1_iy+holder_radius*math.sin(first_angle), lid_router_bit_radius])
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
    holder_A[-1] = (holder_A[-1][0], holder_A[-1][1], lid_router_bit_radius) # change the router_bit of the last point
    # second to last line
    last_angle = gr_c['holder_position_angle'] + holder_crenel_half_angle + (idx+1)*angle_incr
    holder_A.append([g1_ix+clearance_radius*math.cos(last_angle), g1_iy+clearance_radius*math.sin(last_angle), lid_router_bit_radius])
    # last arc
    holder_A.append([g1_ix+clearance_radius*math.cos(middle_angle), g1_iy+clearance_radius*math.sin(middle_angle),
                      g1_ix+clearance_radius*math.cos(first_angle), g1_iy+clearance_radius*math.sin(first_angle), 0])
    # save the portion of outline
    middle_lid_outlines.append(holder_A[:])
  ## overlay for check
  axle_lid_overlay_figure.append(cnc25d_api.ideal_outline(middle_lid_outlines[0], "middle_lid_outlines"))
  ## middle_axle_lid
  middle_lid_figures = []
  for i in range(2):
    one_middle_figure = []
    one_middle_figure.append(cnc25d_api.cnc_cut_outline(middle_lid_outlines[i], "middle_lid_outlines"))
    if(holder_hole_radius>0):
      tmp_a2 = math.atan(holder_double_hole_length/2.0/holder_hole_position_radius) # if double carrier-crenel-hole
      tmp_l2 = math.sqrt(holder_hole_position_radius**2+(holder_double_hole_length/2.0)**2)
      for j in range(2):
        hole_angle = gr_c['holder_position_angle']+((middle_crenel_index[i]+j)*angle_incr)
        if(holder_double_hole_length==0):
          one_middle_figure.append([g1_ix+holder_hole_position_radius*math.cos(hole_angle), g1_iy+holder_hole_position_radius*math.sin(hole_angle), holder_hole_radius])
        else:
          one_middle_figure.append([g1_ix+tmp_l2*math.cos(hole_angle-tmp_a2), g1_iy+tmp_l2*math.sin(hole_angle-tmp_a2), holder_hole_radius])
          one_middle_figure.append([g1_ix+tmp_l2*math.cos(hole_angle+tmp_a2), g1_iy+tmp_l2*math.sin(hole_angle+tmp_a2), holder_hole_radius])
          
    middle_lid_figures.append(one_middle_figure[:])

  ### top_lid
  # top_lid_outline
  middle_angle_1 = (middle_crenel_2 + (middle_crenel_1+1))/2.0*crenel_portion_angle + gr_c['holder_position_angle']
  middle_angle_2 = middle_angle_1 + math.pi
  top_lid_outline = []
  top_lid_outline.extend(middle_lid_outlines[0][:-1])
  top_lid_outline.append((g1_ix+central_radius*math.cos(middle_angle_1), g1_iy+central_radius*math.sin(middle_angle_1), holder_smoothing_radius))
  top_lid_outline.extend(middle_lid_outlines[1][:-1])
  top_lid_outline.append((g1_ix+central_radius*math.cos(middle_angle_2), g1_iy+central_radius*math.sin(middle_angle_2), holder_smoothing_radius))
  top_lid_outline.append((top_lid_outline[0][0], top_lid_outline[0][1], 0))
  # overlay debug
  axle_lid_overlay_figure.append(cnc25d_api.ideal_outline(top_lid_outline, "top_lid_outline"))
  # top_lid_figure
  top_lid_figure = []
  top_lid_figure.append(cnc25d_api.cnc_cut_outline(top_lid_outline, "top_lid_outline"))
  top_lid_figure.append((g1_ix, g1_iy, axle_hole_radius))
  if(holder_hole_radius>0):
    tmp_a2 = math.atan(holder_double_hole_length/2.0/holder_hole_position_radius) # if double carrier-crenel-hole
    tmp_l2 = math.sqrt(holder_hole_position_radius**2+(holder_double_hole_length/2.0)**2)
    for i in range(2):
      for j in range(2):
        hole_angle = gr_c['holder_position_angle']+((middle_crenel_index[i]+j)*angle_incr)
        if(holder_double_hole_length==0):
          top_lid_figure.append([g1_ix+holder_hole_position_radius*math.cos(hole_angle), g1_iy+holder_hole_position_radius*math.sin(hole_angle), holder_hole_radius])
        else:
          top_lid_figure.append([g1_ix+tmp_l2*math.cos(hole_angle-tmp_a2), g1_iy+tmp_l2*math.sin(hole_angle-tmp_a2), holder_hole_radius])
          top_lid_figure.append([g1_ix+tmp_l2*math.cos(hole_angle+tmp_a2), g1_iy+tmp_l2*math.sin(hole_angle+tmp_a2), holder_hole_radius])
  
  ### design output
  part_figure_list = []
  part_figure_list.append(annulus_holder_figure)
  part_figure_list.append(middle_lid_figures[0])
  part_figure_list.append(middle_lid_figures[1])
  part_figure_list.append(top_lid_figure)
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
cnc_router_bit_radius:    \t{:0.3f} diameter: \t{:0.3f}
""".format(holder_crenel_number, al_c['holder_hole_diameter']/2.0, al_c['holder_hole_diameter'], holder_radius, 2*holder_radius, clearance_radius, 2*clearance_radius, central_radius, 2*central_radius, axle_hole_radius, 2*axle_hole_radius, annulus_holder_axle_hole_radius, 2*annulus_holder_axle_hole_radius, cnc_router_bit_radius, 2*cnc_router_bit_radius)
  #print(al_parameter_info)

  ### display with Tkinter
  if(al_c['tkinter_view']):
    print(al_parameter_info)
    cnc25d_api.figure_simple_display(al_assembly_figure, axle_lid_overlay_figure, al_parameter_info)
      
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
  ### general
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
    ["double crenel-holes"  , "--holder_diameter 220.0 --clearance_diameter 200.0 --central_diameter 70.0 --axle_hole_diameter 22.0 --holder_crenel_number 8 --holder_double_hole_length 4.0 --holder_hole_diameter 3.0"],
    ["with initial angle"   , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 35.0 --axle_hole_diameter 22.0 --holder_position_angle 0.25"],
    ["with annulus-holder-axle-hole-diameter"   , "--holder_diameter 120.0 --clearance_diameter 100.0 --central_diameter 35.0 --axle_hole_diameter 22.0 --annulus_holder_axle_hole_diameter 80.0"],
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

