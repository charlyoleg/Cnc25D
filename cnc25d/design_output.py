# design_output.py
# generates output design files from a figure
# created by charlyoleg on 2013/08/27
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
design_output.py is part of the Cnc25D API.
it provide macro that are commonly used to generate the output files of a design
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import importing_freecad
importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

# Python standard library
import math
import sys, argparse
from datetime import datetime
#import os, errno
import os
import re
#import Tkinter # to display the outline in a small GUI
# FreeCAD
import Part
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import outline_backends
import export_2d
import design_help
import cnc_outline
import positioning


################################################################
# help functions
################################################################

################################################################
# functions to be reused
################################################################

def generate_output_file_add_argument(ai_parser, ai_variant=0):
  """ Add the argparse switch --output_file_basename
  """
  r_parser = ai_parser
  r_parser.add_argument('--output_file_basename','--ofb', action='store', default='', dest='sw_output_file_basename',
    help="If not  the empty_string (the default value), it outputs the (first) gear in file(s) depending on your argument file_extension: .dxf uses mozman dxfwrite, .svg uses mozman svgwrite, no-extension uses FreeCAD and you get .brep and .dxf")
  if(ai_variant==1):
    r_parser.add_argument('--return_type','--rt', action='store', default='int_status', dest='sw_return_type',
      help="Define the what the main function should returns. Possible values: int_status, cnc25d_figure, freecad_object. Set it to freecad_object to use it with FreeCAD. Default: int_status")
  # return
  return(r_parser)
  
def get_output_file_suffix(ai_output_file_basename):
  """ detect the output-file-suffix .dxf and .svg and return the basename and suffix
  """
  output_file_suffix = '' # .brep
  output_file_basename = ai_output_file_basename
  if(re.search('\.dxf$', ai_output_file_basename)):
    output_file_suffix = '.dxf'
    output_file_basename = re.sub('\.dxf$', '', ai_output_file_basename)
  elif(re.search('\.svg$', ai_output_file_basename)):
    output_file_suffix = '.svg'
    output_file_basename = re.sub('\.svg$', '', ai_output_file_basename)
  r_bs = (output_file_basename, output_file_suffix)
  return(r_bs)

def generate_output_file(ai_figure, ai_output_filename, ai_height, ai_info_txt=''):
  """ implement the swith --output_file_basename for 2D figure
  """
  if(ai_output_filename!=''):
    # create the output directory if needed
    l_output_dir = os.path.dirname(ai_output_filename)
    design_help.mkdir_p(l_output_dir)
    #l_output_basename = os.path.basename(ai_output_filename)
    #print("dbg449: l_output_basename:", l_output_basename)
    # mozman dxfwrite
    if(re.search('\.dxf$', ai_output_filename)):
      #print("Generate {:s} with mozman dxfwrite".format(ai_output_filename))
      outline_backends.write_figure_in_dxf(ai_figure, ai_output_filename)
    # mozman svgwrite
    elif(re.search('\.svg$', ai_output_filename)):
      #print("Generate {:s} with mozman svgwrite".format(ai_output_filename))
      outline_backends.write_figure_in_svg(ai_figure, ai_output_filename)
    # FreeCAD
    else:
      print("Generate with FreeCAD the BRep file {:s}.brep".format(ai_output_filename))
      freecad_part = outline_backends.figure_to_freecad_25d_part(ai_figure, ai_height)
      freecad_part.exportBrep("{:s}.brep".format(ai_output_filename))
      print("Generate with FreeCAD the DXF file {:s}.dxf".format(ai_output_filename))
      # slice freecad_part  in the XY plan at a height of ai_height/2
      export_2d.export_to_dxf(freecad_part, Base.Vector(0,0,1), ai_height/2, "{:s}.dxf".format(ai_output_filename))
    # info_txt
    if(ai_info_txt!=''):
      output_basename = re.sub('(\.dxf$)|(\.svg$)', '', ai_output_filename)
      info_txt_filename = "{:s}.txt".format(output_basename)
      print("Generate the text info file {:s}".format(info_txt_filename))
      ofh = open(info_txt_filename, 'w')
      ofh.write("{:s} generated by Cnc25D on {:s}\n\n".format(info_txt_filename, datetime.now().isoformat()))
      ofh.write(ai_info_txt)
      ofh.close()
  # return
  return(0)

def generate_3d_assembly_output_file(ai_3d_conf, ai_output_filename, ai_brep=True, ai_stl=False, ai_slice_xyz=[]):
  """ implement the swith --output_file_basename for 3D assembly
  """
  print("Compute with FreeCAD the 3D assembly {:s}".format(ai_output_filename))
  fc_assembly = figures_to_freecad_assembly(ai_3d_conf)
  if(ai_brep):
    brep_output_filename = "{:s}.brep".format(ai_output_filename)
    print("Generate with FreeCAD the BRep file {:s}".format(brep_output_filename))
    fc_assembly.exportBrep(brep_output_filename)
  if(ai_stl):
    stl_output_filename = "{:s}.stl".format(ai_output_filename)
    print("Generate with FreeCAD the STL file {:s}".format(stl_output_filename))
    fc_assembly.exportStl(stl_output_filename)
  if(len(ai_slice_xyz)>0):
    if(len(ai_slice_xyz)!=9):
      print("ERR150: Error, len(ai_slice_xyz) {:d} must be 9".format(len(ai_slice_xyz)))
      sys.exit(2)
    size_x = ai_slice_xyz[0]
    size_y = ai_slice_xyz[1]
    size_z = ai_slice_xyz[2]
    zero_x = ai_slice_xyz[3]
    zero_y = ai_slice_xyz[4]
    zero_z = ai_slice_xyz[5]
    slice_x = ai_slice_xyz[6]
    slice_y = ai_slice_xyz[7]
    slice_z = ai_slice_xyz[8]
    dxf_output_filename = "{:s}_xyz_slices.dxf".format(ai_output_filename)
    print("Slice with FreeCAD the 3D into the DXF file {:s}".format(dxf_output_filename))
    fc_assembly.translate(Base.Vector(-1*zero_x, -1*zero_y, -1*zero_z))
    export_2d.export_xyz_to_dxf(fc_assembly, size_x, size_y, size_z, slice_x, slice_y, slice_z, dxf_output_filename)
  return(0)

def flip_rotate_and_translate_figure(ai_figure, ai_zero_x, ai_zero_y, ai_size_x, ai_size_y, ai_x_flip, ai_y_flip, ai_rotation_angle, ai_translate_x, ai_translate_y):
  """ flip, rotate and translate a figure (list of outlines). Usually used to agglomerate figures to create a cut-set.
  """
  r_figure = []
  for i in range(len(ai_figure)):
    centered_ol = cnc_outline.outline_shift_xy(ai_figure[i], -1*(ai_zero_x+ai_size_x/2.0), 1, -1*(ai_zero_y+ai_size_y/2.0), 1)
    flipped_ol = cnc_outline.outline_shift_xy(centered_ol, 0.0, ai_x_flip, 0.0, ai_y_flip)
    #flipped_ol = cnc_outline.outline_shift_xy(centered_ol, 0, ai_x_flip, 0, ai_y_flip) # what makes the most sense? re-shift or not?
    rotated_ol = cnc_outline.outline_rotate(flipped_ol, 0.0, 0.0, ai_rotation_angle)
    translated_ol = cnc_outline.outline_shift_xy(rotated_ol, ai_size_x/2.0+ai_translate_x, 1, ai_size_y/2.0+ai_translate_y, 1)
    r_figure.append(translated_ol[:])
  return(r_figure)

def rotate_and_translate_figure(ai_figure, ai_rotation_center_x, ai_rotation_center_y, ai_rotation_angle, ai_translate_x, ai_translate_y):
  """ rotate and translate a figure (list of outlines). Usually used to agglomerate figures to create a cut-set.
  """
  #r_figure = []
  #for i in range(len(ai_figure)):
  #  r_figure.append(cnc_outline.outline_shift_xy(cnc_outline.outline_rotate(ai_figure[i], ai_rotation_center_x, ai_rotation_center_y, ai_rotation_angle), ai_translate_x, 1, ai_translate_y, 1))
  r_figure = flip_rotate_and_translate_figure(ai_figure, ai_rotation_center_x, ai_rotation_center_y, 0.0, 0.0, 1, 1, ai_rotation_angle, ai_rotation_center_x+ai_translate_x, ai_rotation_center_y+ai_translate_y)
  return(r_figure)

def cnc_cut_figure(ai_figure, ai_error_msg_id):
  """ apply the cnc_cut_outline function to all outlines of the input figure
  """
  r_figure = []
  for i in range(len(ai_figure)):
    #print("dbg133:", ai_figure[i])
    if(cnc_outline.check_outline_format(ai_figure[i])==2):
      r_figure.append(cnc_outline.cnc_cut_outline(ai_figure[i], "{:s}.ol{:d}".format(ai_error_msg_id, i)))
    else: # circle of format-B
      r_figure.append(ai_figure[i])
  return(r_figure)

def ideal_figure(ai_figure, ai_error_msg_id):
  """ apply the ideal_outline function to all outlines of the input figure
  """
  r_figure = []
  for i in range(len(ai_figure)):
    #print("dbg145:", ai_figure[i])
    if(cnc_outline.check_outline_format(ai_figure[i])==2):
      r_figure.append(cnc_outline.ideal_outline(ai_figure[i], "{:s}.ol{:d}".format(ai_error_msg_id, i)))
    else: # circle of format-B
      r_figure.append(ai_figure[i])
  return(r_figure)

def figures_to_freecad_assembly(ai_figure_assembly):
  """ Extrude figures and place them from a list of figures and 3D positioning instructions
  """
  fc_obj = []
  for i in range(len(ai_figure_assembly)):
    (part_figure, zero_x, zero_y, size_x, size_y, size_z, flip, orientation, translate_x, translate_y, translate_z) = ai_figure_assembly[i]
    part_figure_zero = rotate_and_translate_figure(part_figure, 0, 0, 0, -1*zero_x, -1*zero_y)
    part_extruded = outline_backends.figure_to_freecad_25d_part(part_figure_zero, size_z)
    part_placed = positioning.place_plank(part_extruded, size_x, size_y, size_z, flip, orientation, translate_x, translate_y, translate_z)
    fc_obj.append(part_placed.copy())
  r_assembly = Part.makeCompound(fc_obj)
  return(r_assembly)

################################################################
# test-functions
################################################################


