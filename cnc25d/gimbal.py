# gimbal.py
# generates the gimbal, a mechanism with the roll-pitch angles as degrees of freedom
# created by charlyoleg on 2013/12/10
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
gimbal.py generates the gimbal assembly, a mechanism with the roll-pitch angles as degrees of freedom.
The main function displays in a Tk-interface the gimbal parts, or generates the design as files or returns the design as FreeCAD Part object.
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
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import bell_bagel_assembly
import cross_cube
import angles


################################################################
# gimbal constraint_constructor
################################################################

def gimbal_constraint_constructor(ai_parser, ai_variant=0):
  """
  Add arguments relative to the gimbal
  """
  r_parser = ai_parser
  ### inheritance from bell_bagel_assembly
  i_bell_bagel_assembly = bell_bagel_assembly.bba()
  r_parser = i_bell_bagel_assembly.get_constraint_constructor()(r_parser, 1)
  ### inheritance from cross_cube
  i_cross_cube = cross_cube.cross_cube()
  r_parser = i_cross_cube.get_constraint_constructor()(r_parser, 1)
  ### roll-pitch angles
  r_parser.add_argument('--bottom_angle','--ba', action='store', type=float, default=0.0,
    help="Set the bottom angle (in radians). Default: 0.0")
  r_parser.add_argument('--top_angle','--ta', action='store', type=float, default=0.0,
    help="Set the top angle (in radians). Default: 0.0")
  ### pan_tilt angles # can be set only if roll-pitch angles are left to 0.0
  r_parser.add_argument('--pan_angle','--pan', action='store', type=float, default=0.0,
    help="Set the pan angle (in radians). Use the pan-tilt angles only if roll-pitch angles are left to 0.0. Default: 0.0")
  r_parser.add_argument('--tilt_angle','--tilt', action='store', type=float, default=0.0,
    help="Set the tilt angle (in radians). Default: 0.0")
  ### output
  # return
  return(r_parser)

    
################################################################
# constraint conversion
################################################################

def cross_cube_constraint(c):
  """ convert gimbal constraint into cross_cube constraint
  """
  cc_c = c.copy()
  cc_c['crest_cnc_router_bit_radius'] = c['cross_cube_cnc_router_bit_radius'] # crest_cnc_router_bit_radius must be removed because to similar to cross_cube_cnc_router_bit_radius
  return(cc_c)

################################################################
# gimbal constraint_check
################################################################

def gimbal_constraint_check(c):
  """ check the gimbal constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ###
  if((c['bottom_angle']!=0)or(c['top_angle']!=0)):
    if((c['pan_angle']!=0)or(c['tilt_angle']!=0)):
      print("ERR145: Error, roll-pitch angles {:0.3f} {:0.3f} and pan-tilt angles {:0.3f} {:0.3f} are set together".format(c['bottom_angle'], c['top_angle'], c['pan_angle'], c['tilt_angle']))
      sys.exit(2)
  if((c['pan_angle']!=0)or(c['tilt_angle']!=0)):
    (a1, a2) = angles.pan_tilt_to_roll_pitch(c['pan_angle'], c['tilt_angle'])
    c['bottom_angle'] = a1
    c['top_angle'] = a2
  (b1, b2) = angles.roll_pitch_to_pan_tilt(c['bottom_angle'], c['top_angle'])
  (a1, a2) = angles.pan_tilt_to_roll_pitch(b1, b2)
  if((abs(c['bottom_angle']-a1)>radian_epsilon)or(abs(c['top_angle']-a2)>radian_epsilon)):
    print("ERR154: Internal error in angle conversion: a1 {:0.3f} {:0.3f}  a2 {:0.3f} {:0.3f}".format(c['bottom_angle'], a1, c['top_angle'], a2))
    sys.exit(2)
  c['b3'] = angles.roll_pitch_pan_tilt_drift_angle(c['bottom_angle'], c['top_angle'])
  #
  if(abs(c['bottom_angle'])>0.7*math.pi):
    print("ERR133: Error, bottom_angle {:0.3f} absolute value is too big".format(c['bottom_angle']))
    sys.exit(2)
  if(abs(c['top_angle'])>0.7*math.pi):
    print("ERR136: Error, top_angle {:0.3f} absolute value is too big".format(c['top_angle']))
    sys.exit(2)
  if(abs(c['bottom_angle'])+abs(c['top_angle'])>1.1*math.pi):
    print("ERR139: Error, bottom_angle {:0.3f} and top_angle {:0.3f} absolute values can not be so large at the same time".format(c['bottom_angle'], c['top_angle']))
    sys.exit(2)
  # pan-tilt
  c['pan_angle'] = b1
  c['tilt_angle'] = b2
  if(c['tilt_angle']>0.6*math.pi):
    print("ERR147: Error, tilt_angle {:0.3f} is to big".format(c['tilt_angle']))
    sys.exit(2)
  return(c)

################################################################
# gimbal 2D-figures construction
################################################################

def gimbal_2d_construction(c):
  """ construct the 2D-figures with outlines at the A-format for the gimbal design
  """
  # bell_bagel_assembly
  i_bba = bell_bagel_assembly.bba()
  i_bba.apply_external_constraint(c)
  bell_face = i_bba.get_A_figure('bell_face')

  # cross_cube
  i_cross_cube = cross_cube.cross_cube()
  i_cross_cube.apply_external_constraint(cross_cube_constraint(c))
  crest_A = i_cross_cube.get_A_figure('crest_A_fig')
  crest_B = i_cross_cube.get_A_figure('crest_B_fig')

  ## gimbal 2D sketch
  # intermediate parameters
  bagel_z = c['base_thickness'] + c['bell_face_height'] + c['leg_length']
  crest_A_axle_z = c['top_thickness'] + c['height_margin'] + c['axle_diameter']/2.0
  crest_B_axle_z = crest_A_axle_z + c['inter_axle_length']
  #
  bottom_bell_face = cnc25d_api.rotate_and_translate_figure(bell_face, 0, bagel_z, 0.0, 0.0, 0.0)
  top_bell_face = cnc25d_api.rotate_and_translate_figure(bell_face, 0, bagel_z, math.pi+c['top_angle'], 0.0, crest_B_axle_z-bagel_z)
  bottom_crest_A = cnc25d_api.rotate_and_translate_figure(crest_A, c['cube_width']/2.0, crest_A_axle_z, c['bottom_angle'], -1*c['cube_width']/2.0, bagel_z-crest_A_axle_z)
  top_crest_B = cnc25d_api.rotate_and_translate_figure(crest_B, c['cube_width']/2.0, crest_B_axle_z, 0.0, -1*c['cube_width']/2.0, 0.0)

  ### figures output
  x_space = 1.2*max(c['gear_module']*c['virtual_tooth_nb'], c['base_diameter'])
  ## gimbal_sketch
  gimbal_sketch_figure = []
  gimbal_sketch_figure.extend(cnc25d_api.rotate_and_translate_figure(bottom_bell_face, 0.0, 0.0, 0.0,   0*x_space, 0))
  gimbal_sketch_figure.extend(cnc25d_api.rotate_and_translate_figure(bottom_crest_A, 0.0, 0.0, 0.0,     0*x_space, 0))
  gimbal_sketch_figure.extend(cnc25d_api.rotate_and_translate_figure(top_bell_face, 0.0, 0.0, 0.0,      1*x_space, 0))
  gimbal_sketch_figure.extend(cnc25d_api.rotate_and_translate_figure(top_crest_B, 0.0, 0.0, 0.0,        1*x_space, 0))
  ###
  r_figures = {}
  r_height = {}
  # get figures and heights from bell_bagel_assembly
  (bba_figs, bba_heights) = i_bba.apply_2d_constructor()
  r_figures.update(bba_figs)
  r_height.update(bba_heights)
  # get figures and heights from cross_cube
  (cc_figs, cc_heights) = i_cross_cube.apply_2d_constructor()
  r_figures.update(cc_figs)
  r_height.update(cc_heights)
  #
  r_figures['gimbal_sketch'] = gimbal_sketch_figure
  r_height['gimbal_sketch'] = 1.0
  ###
  return((r_figures, r_height))

################################################################
# gimbal simulation
################################################################

def crest_simulation_A(c):
  """ define the crest simulation
  """
  # inherit from gear_profile
  i_cross_cube = cross_cube.cross_cube()
  i_cross_cube.apply_external_constraint(c)
  i_cross_cube.run_simulation('crest_simulation_A')
  return(1)

def gimbal_2d_simulations():
  """ return the dictionary defining the available simulation for gimbal
  """
  r_sim = {}
  r_sim['crest_simulation_A'] = crest_simulation_A
  return(r_sim)

################################################################
# gimbal 3D FreeCAD construction
################################################################

### gimbal freecad construction
def sub_gimbal_freecad_construction(c, ai_bottom_angle, ai_top_angle):
  """ generate the the freecad-object gimbal
  """
  # intermediate parameters
  z1 = c['base_thickness'] + c['bell_face_height'] + c['leg_length']
  z2 = c['inter_axle_length']
  # make the freecad-objects from bell_bagel_assembly and cross_cube
  i_bba = bell_bagel_assembly.bba()
  i_bba.apply_external_constraint(c)
  fc_bb_bottom = i_bba.get_fc_obj_3dconf('bell_bagel_assembly_conf1')
  fc_bb_top = fc_bb_bottom.copy()
  i_cross_cube = cross_cube.cross_cube()
  i_cross_cube.apply_external_constraint(cross_cube_constraint(c))
  fc_cc = i_cross_cube.get_fc_obj_3dconf('cross_cube_assembly_with_rods_and_axles')
  # place
  fc_bb_bottom.rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),90)
  fc_bb_top.rotate(Base.Vector(0,0,z1),Base.Vector(0,1,0),180)
  fc_bb_top.translate(Base.Vector(0,0,z2))
  fc_cc.translate(Base.Vector(-1*c['cube_width']/2.0, -1*c['cube_width']/2.0, z1-(c['top_thickness'] + c['height_margin'] + c['axle_diameter']/2.0)))
  fc_cc.rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),90)
  # apply the rotation
  fc_bb_top.rotate(Base.Vector(0,0,z1+z2),Base.Vector(0,1,0),ai_top_angle*180/math.pi)
  fc_top = Part.makeCompound([fc_bb_top, fc_cc])
  fc_top.rotate(Base.Vector(0,0,z1),Base.Vector(1,0,0),ai_bottom_angle*180/math.pi)
  r_fc_gimbal = Part.makeCompound([fc_bb_bottom, fc_top])
  return(r_fc_gimbal)

def sub_gfc_gimbal(c):
  return(sub_gimbal_freecad_construction(c, c['bottom_angle'], c['top_angle']))

def sub_gfc_gimbal_00_00(c):
  return(sub_gimbal_freecad_construction(c, 0, 0))

def sub_gfc_gimbal_90_00(c):
  return(sub_gimbal_freecad_construction(c, math.pi/2, 0))

def sub_gfc_gimbal_00_90(c):
  return(sub_gimbal_freecad_construction(c, 0, math.pi/2))

def sub_gfc_gimbal_45_45(c):
  return(sub_gimbal_freecad_construction(c, math.pi/4, math.pi/4))

def sub_gfc_gimbal_15_30(c):
  return(sub_gimbal_freecad_construction(c, math.pi/12, math.pi/6))

def sub_gfc_gimbal_60_20(c):
  return(sub_gimbal_freecad_construction(c, math.pi/3, math.pi/9))

def gimbal_3d_freecad_construction(c):
  """ construct 3D-FreeCAD objects of the gimbal
  """
  ###
  r_fc_obj_f = {}
  r_slice = {}
  #
  r_fc_obj_f['gimbal'] = sub_gfc_gimbal
  r_slice['gimbal'] = []
  #
  r_fc_obj_f['gimbal_00_00'] = sub_gfc_gimbal_00_00
  r_slice['gimbal_00_00'] = []
  #
  r_fc_obj_f['gimbal_90_00'] = sub_gfc_gimbal_90_00
  r_slice['gimbal_90_00'] = []
  #
  r_fc_obj_f['gimbal_00_90'] = sub_gfc_gimbal_00_90
  r_slice['gimbal_00_90'] = []
  #
  r_fc_obj_f['gimbal_45_45'] = sub_gfc_gimbal_45_45
  r_slice['gimbal_45_45'] = []
  #
  r_fc_obj_f['gimbal_15_30'] = sub_gfc_gimbal_15_30
  r_slice['gimbal_15_30'] = []
  #
  r_fc_obj_f['gimbal_60_20'] = sub_gfc_gimbal_60_20
  r_slice['gimbal_60_20'] = []
  ###
  return((r_fc_obj_f, r_slice))


################################################################
# gimbal_info
################################################################

def gimbal_info(c):
  """ create the text info related to the bagel design
  """
  r_info = ""
  i_bell_bagel = bell_bagel_assembly.bba()
  i_bell_bagel.apply_external_constraint(c)
  r_info += i_bell_bagel.get_info()
  i_cross_cube = cross_cube.cross_cube()
  i_cross_cube.apply_external_constraint(c)
  r_info += i_cross_cube.get_info()
  r_info += """
roll-pitch angles:
bottom_angle:   {:0.3f} (radian)    {:0.3f} (degree)
top_angle:      {:0.3f} (radian)    {:0.3f} (degree)
pan-tilt conversion:
pan_angle:      {:0.3f} (radian)    {:0.3f} (degree)
tilt_angle:     {:0.3f} (radian)    {:0.3f} (degree)
roll-pitch pan-tilt drit angle: {:0.3f} (radian)    {:0.3f} (degree)
""".format(c['bottom_angle'], c['bottom_angle']*180/math.pi, c['top_angle'], c['top_angle']*180/math.pi, c['pan_angle'], c['pan_angle']*180/math.pi, c['tilt_angle'], c['tilt_angle']*180/math.pi, c['b3'], c['b3']*180/math.pi)
  #print(r_info)
  return(r_info)

################################################################
# self test
################################################################

def gimbal_self_test():
  """
  This is the non-regression test of gimbal.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , ""],
    ["bottom angle"        , "--bottom_angle 0.3"],
    ["top angle"        , "--top_angle -0.4"],
    ["both angle"        , "--bottom_angle -0.2 --top_angle 0.3"],
    ["pan-tilt"        , "--pan_angle 2.1 --tilt_angle 0.4"],
    ["outputfile" , "--output_file_basename test_output/gimbal_self_test.dxf"],
    ["last test"            , "--bottom_angle 0.1 --top_angle 0.2"]]
  return(r_tests)

################################################################
# gimbal design declaration
################################################################

class gimbal(cnc25d_api.bare_design):
  """ gimbal design
  """
  def __init__(self, constraint={}):
    """ configure the gimbal design
    """
    self.design_setup(
      s_design_name             = "gimbal_design",
      f_constraint_constructor  = gimbal_constraint_constructor,
      f_constraint_check        = gimbal_constraint_check,
      f_2d_constructor          = gimbal_2d_construction,
      d_2d_simulation           = gimbal_2d_simulations(),
      f_3d_constructor          = None,
      f_3d_freecad_constructor  = gimbal_3d_freecad_construction,
      f_info                    = gimbal_info,
      l_display_figure_list     = ['gimbal_sketch'],
      s_default_simulation      = "",
      l_2d_figure_file_list     = [], # all figures
      l_3d_figure_file_list     = None, # no file
      l_3d_conf_file_list       = None, # no file
      #l_3d_freecad_file_list    = [], # all freecad objects
      l_3d_freecad_file_list    = ['gimbal'],
      f_cli_return_type         = None,
      l_self_test_list          = gimbal_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gimbal.py says hello!\n")
  my_g = gimbal()
  #my_g.cli()
  #my_g.cli("--bagel_extra_cut_thickness 1.0")
  #my_g.cli("--bottom_angle 0.1 --top_angle 0.2")
  my_g.cli("--face_A1_crest --face_B1_crest --bottom_angle 0.1 --top_angle 0.2")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_g.get_fc_obj_function('gimbal'))


