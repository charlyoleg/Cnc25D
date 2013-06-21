# gearwheel.py
# generates gearwheel and simulates gear.
# created by charlyoleg on 2013/06/19
# license: CC BY SA 3.0

"""
gearwheel.py is a parametric generator of gear-wheels.
It's actually a single function with the design parameters as input.
The function writes STL, DXF and SVG files if an output basename is given as argument.
The function can also display a small Tk windows for gear simulation.
Finally, the backends used are: FreeCAD (for GUI rendering, STL and DXF export), mozman dxfwrite, mozman svgwrite and Tkinter.
The function return the gear-wheel as FreeCAD Part object.
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

import math
import sys, argparse
from datetime import datetime
import os, errno
#
import cnc_cut_outline
import export_2d
#
import Part
from FreeCAD import Base

################################################################
# gearwheel_argparse
################################################################

"""
The gearwheel_parser defines and structures the arguments of gearwheel().
It's mostly used for debug and non-regression test.
Argument default values are defined here.
"""
gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function gearwheel().')
# first gearwheel parameters
gearwheel_parser.add_argument('--gear_type','--gt', action='store', default='ee', dest='sw_gear_type',
  help="Select the type of gear. Possible values: 'ee', 'ie', 'ce', 'ei' and 'ce'. Default: 'ee'")
gearwheel_parser.add_argument('--gear_tooth_nb','--gtn', action='store', type=int, default=17, dest='sw_gear_tooth_nb',
  help="Set the number of teeth of the first gearwheel.")
gearwheel_parser.add_argument('--gear_module','--gm', action='store', type=float, default=1.0, dest='sw_gear_module',
  help="Set the module of the gear. It influences the gearwheel diameters.")
gearwheel_parser.add_argument('--gear_primitive_diameter','--gpd', action='store', type=float, default=0.0, dest='sw_gear_primitive_diameter',
  help="If not set to zero, redefine the gear module to get this primitive diameter of the first gearwheel. Default: 0. If cremailliere, it redefines the length.")
gearwheel_parser.add_argument('--gear_base_diameter','--gbd', action='store', type=float, default=0.0, dest='sw_gear_base_diameter',
  help="If not set to zero, redefine the base diameter of the first gearwheel. Default: 0. If cremailliere, it redefines the tooth slope angle.")
gearwheel_parser.add_argument('--gear_tooth_half_height','--gthh', action='store', type=float, default=0.0, dest='sw_gear_tooth_half_height',
  help="If not set to zero, redefine the tooth half height of the first gearwheel. Default: 0.0")
gearwheel_parser.add_argument('--gear_addendum_dedendum_parity','--gadp', action='store', type=float, default=50.0, dest='sw_gear_addendum_dedendum_parity',
  help="Set the addendum / dedendum parity of the first gearwheel. Default: 50.0%%")
gearwheel_parser.add_argument('--gear_addendum_height_pourcentage','--gahp', action='store', type=float, default=100.0, dest='sw_gear_addendum_height_pourcentage',
  help="Set the addendum height of the first gearwheel in pourcentage of the tooth half height. Default: 100.0%%")
gearwheel_parser.add_argument('--gear_dedendum_height_pourcentage','--gdhp', action='store', type=float, default=100.0, dest='sw_gear_dedendum_height_pourcentage',
  help="Set the dedendum height of the first gearwheel in pourcentage of the tooth half height. Default: 100.0%%")
gearwheel_parser.add_argument('--gear_hollow_height_pourcentage','--ghhp', action='store', type=float, default=25.0, dest='sw_gear_hollow_height_pourcentage',
  help="Set the hollow height of the first gearwheel in pourcentage of the tooth half height. Default: 25.0%%")
gearwheel_parser.add_argument('--gear_reamer_radius','--grr', action='store', type=float, default=1.0, dest='sw_gear_reamer_radius',
  help="Set the reamer radius used to create the gear hollow of the first gearwheel. Default: 1.0")
gearwheel_parser.add_argument('--gear_initial_angle','--gia', action='store', type=float, default=0.0, dest='sw_gear_initial_angle',
  help="Set the gear reference angle (in Radian). Default: 0.0")
# gear contact parameters
gearwheel_parser.add_argument('--second_gear_position_angle','--sgpa', action='store', type=float, default=0.0, dest='sw_second_gear_position_angle',
  help="Angle in Radian that sets the postion on the second gearwheel. Default: 0.0")
gearwheel_parser.add_argument('--second_gear_additional_axe_length','--sgaal', action='store', type=float, default=0.0, dest='sw_second_gear_additional_axe_length',
  help="Set an additional value for the inter-axe length between the first and the second gearwheels. Default: 0.0")
gearwheel_parser.add_argument('--gear_force_angle','--gfa', action='store', type=float, default=0.0, dest='sw_gear_force_angle',
  help="If not set to zero, redefine the second_gear_additional_axe_length to get this force angle at the gear contact. Default: 0.0")
# second gearwheel parameters
gearwheel_parser.add_argument('--second_gear_tooth_nb','--sgtn', action='store', type=int, default=17, dest='sw_second_gear_tooth_nb',
  help="Set the number of teeth of the second gearwheel.")
gearwheel_parser.add_argument('--second_gear_primitive_diameter','--sgpd', action='store', type=float, default=0.0, dest='sw_second_gear_primitive_diameter',
  help="If not set to zero, redefine the gear module to get this primitive diameter of the second gearwheel. Default: 0.0. If cremailliere, it redefines the length.")
gearwheel_parser.add_argument('--second_gear_base_diameter','--sgbd', action='store', type=float, default=0.0, dest='sw_second_gear_base_diameter',
  help="If not set to zero, redefine the base diameter of the second gearwheel. Default: 0.0. If cremailliere, it redefines the tooth slope angle.")
gearwheel_parser.add_argument('--second_gear_tooth_half_height','--sgthh', action='store', type=float, default=0.0, dest='sw_second_gear_tooth_half_height',
  help="If not set to zero, redefine the tooth half height of the second gearwheel. Default: 0.0")
gearwheel_parser.add_argument('--second_gear_addendum_dedendum_parity','--sgadp', action='store', type=float, default=50.0, dest='sw_second_gear_addendum_dedendum_parity',
  help="Set the addendum / dedendum parity of the second gearwheel. Default: 50.0%%")
gearwheel_parser.add_argument('--second_gear_addendum_height_pourcentage','--sgahp', action='store', type=float, default=100.0, dest='sw_second_gear_addendum_height_pourcentage',
  help="Set the addendum height of the second gearwheel in pourcentage of the tooth half height. Default: 100.0%%")
gearwheel_parser.add_argument('--second_gear_dedendum_height_pourcentage','--sgdhp', action='store', type=float, default=100.0, dest='sw_second_gear_dedendum_height_pourcentage',
  help="Set the dedendum height of the second gearwheel in pourcentage of the tooth half height. Default: 100.0%%")
gearwheel_parser.add_argument('--second_gear_hollow_height_pourcentage','--sghhp', action='store', type=float, default=25.0, dest='sw_second_gear_hollow_height_pourcentage',
  help="Set the hollow height of the second gearwheel in pourcentage of the tooth half height. Default: 25.0%%")
gearwheel_parser.add_argument('--second_gear_reamer_radius','--sgrr', action='store', type=float, default=1.0, dest='sw_second_gear_reamer_radius',
  help="Set the reamer radius used to create the gear hollow of the second gearwheel. Default: 1.0")
# simulation
gearwheel_parser.add_argument('--simulation_enable','--se', action='store_true', default=False, dest='sw_simulation_enable',
  help='It display a Tk window where you can observe the gear running. Check with your eyes if the geometry is working.')
gearwheel_parser.add_argument('--simulation_zoom','--sz', action='store', type=float, default=4.0, dest='sw_simulation_zoom',
  help="Set the zoom factor for the zoom window. Usually you choose a value between 1.0 and 4.0 depending on your gearwheel diameters. Default: 4.0")
# axe parameters
gearwheel_parser.add_argument('--axe_type','--at', action='store', default='none', dest='sw_axe_type',
  help="Select the type of axe for the first gearwheel. Possible values: 'none', 'cylinder' and 'rectangle'. Default: 'none'")
gearwheel_parser.add_argument('--axe_size_1','--as1', action='store', type=float, default=10.0, dest='sw_axe_size_1',
  help="Set the axe cylinder diameter or the axe rectangle width of the first gearwheel. Default: 10.0")
gearwheel_parser.add_argument('--axe_size_2','--as2', action='store', type=float, default=10.0, dest='sw_axe_size_2',
  help="Set the axe rectangle height of the first gearwheel. Default: 10.0")
gearwheel_parser.add_argument('--axe_reamer_radius','--arr', action='store', type=float, default=1.0, dest='sw_axe_reamer_radius',
  help="Set the reamer radius of the first gearwheel rectangle axe. Default: 1.0")
# portion parameter
gearwheel_parser.add_argument('--portion_tooth_nb','--ptn', action='store', type=int, default=0, dest='sw_portion_tooth_nb',
  help="If not set to zero, cut a portion of the first gearwheel according to this portion tooth number. Default: 0")
# wheel hollow parameters
gearwheel_parser.add_argument('--wheel_hollow_internal_diameter','--whid', action='store', type=float, default=0.0, dest='sw_wheel_hollow_internal_diameter',
  help="If not set to zero, create wheel hollows of the first gearwheel with this internal diameter. Default: 0.0")
gearwheel_parser.add_argument('--wheel_hollow_external_diameter','--whed', action='store', type=float, default=0.0, dest='sw_wheel_hollow_external_diameter',
  help="Set the wheel hollow external diameter of the first gearwheel. It must be bigger than the wheel_hollow_internal_diameter and smaller than the gear bottom diameter. Default: 0.0")
gearwheel_parser.add_argument('--wheel_hollow_leg_number','--whln', action='store', type=int, default=1, dest='sw_wheel_hollow_leg_number',
  help="Set the number of legs for the wheel hollow of the first gearwheel. The legs are uniform distributed. The first leg is centered on the gear reference angle (gear_initial_angle). Default: 1")
gearwheel_parser.add_argument('--wheel_hollow_leg_width','--whlw', action='store', type=float, default=10.0, dest='sw_wheel_hollow_leg_width',
  help="Set the wheel hollow leg width of the first gearwheel. Default: 10.0")
gearwheel_parser.add_argument('--wheel_hollow_reamer_radius','--whrr', action='store', type=float, default=1.0, dest='sw_wheel_hollow_reamer_radius',
  help="Set the reamer radius of the wheel hollow of the first gearwheel. Default: 1.0")
# part split parameter
gearwheel_parser.add_argument('--part_split','--ps', action='store', type=int, default=1, dest='sw_part_split',
  help="Split the first gearwheel in N (=part_split) parts that can be glued together to create the gear wheel. Two series of N parts are created. N=1 doesn't split the gearwheel. Default: 1")
# center position parameters
gearwheel_parser.add_argument('--center_position_x','--cpx', action='store', type=float, default=0.0, dest='sw_center_position_x',
  help="Set the x-position of the first gearwheel center. Default: 0.0")
gearwheel_parser.add_argument('--center_position_y','--cpy', action='store', type=float, default=0.0, dest='sw_center_position_y',
  help="Set the y-position of the first gearwheel center. Default: 0.0")
# firt gearwheel extrusion (currently only linear extrusion is possible)
gearwheel_parser.add_argument('--gearwheel_height','--gwh', action='store', type=float, default=1.0, dest='sw_gearwheel_height',
  help="Set the height of the linear extrusion of the first gearwheel. Default: 1.0")
# cnc reamer constraint
gearwheel_parser.add_argument('--cnc_reamer_radius','--crr', action='store', type=float, default=1.0, dest='sw_cnc_reamer_radius',
  help="Set the minimum reamer radius of the first gearwheel. It increases gear_reamer_radius, axe_reamer_radius and wheel_hollow_reamer_radius if needed. Default: 1.0")
# tooth resolution
gearwheel_parser.add_argument('--gear_tooth_resolution','--gtr', action='store', type=int, default=3, dest='sw_gear_tooth_resolution',
  help="It sets the number of intermediate points of the tooth profile. Default: 3")
# output
gearwheel_parser.add_argument('--output_file_basename','--ofb', action='store', default='', dest='sw_output_file_basename',
  help="If not set to the empty string (the default value), it generates a bunch of design files starting with this basename.")
# self_test
gearwheel_parser.add_argument('--self_test_enable','--ste', action='store_true', default=False, dest='sw_self_test_enable',
  help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
    
################################################################
# the most important function to be used in other scripts
################################################################

def gearwheel(
      ai_gear_type,
      ai_gear_tooth_nb,
      ai_gear_module,
      ai_gear_primitive_diameter,
      ai_gear_base_diameter,
      ai_gear_tooth_half_height,
      ai_gear_addendum_dedendum_parity,
      ai_gear_addendum_height_pourcentage,
      ai_gear_dedendum_height_pourcentage,
      ai_gear_hollow_height_pourcentage,
      ai_gear_reamer_radius,
      ai_gear_initial_angle,
      ai_second_gear_position_angle,
      ai_second_gear_additional_axe_length,
      ai_gear_force_angle,
      ai_second_gear_tooth_nb,
      ai_second_gear_primitive_diameter,
      ai_second_gear_base_diameter,
      ai_second_gear_tooth_half_height,
      ai_second_gear_addendum_dedendum_parity,
      ai_second_gear_addendum_height_pourcentage,
      ai_second_gear_dedendum_height_pourcentage,
      ai_second_gear_hollow_height_pourcentage,
      ai_second_gear_reamer_radius,
      ai_simulation_enable,
      ai_simulation_zoom,
      ai_axe_type,
      ai_axe_size_1,
      ai_axe_size_2,
      ai_axe_reamer_radius,
      ai_portion_tooth_nb,
      ai_wheel_hollow_internal_diameter,
      ai_wheel_hollow_external_diameter,
      ai_wheel_hollow_leg_number,
      ai_wheel_hollow_leg_width,
      ai_wheel_hollow_reamer_radius,
      ai_part_split,
      ai_center_position_x,
      ai_center_position_y,
      ai_gearwheel_height,
      ai_cnc_reamer_radius,
      ai_gear_tooth_resolution,
      ai_output_file_basename):
  """
  The main function of the script.
  It generates a gearwheel according to the function arguments
  """
  ## check parameter coherence

  r_gw = 1
  return(r_gw)

################################################################
# gearwheel argparse_to_function
################################################################

def gearwheel_argparse(ai_gw_args):
  """
  wrapper function of gearwheel() to call it using the gearwheel_parser.
  gearwheel_parser is mostly used for debug and non-regression tests.
  """
  r_gw = gearwheel(
            ai_gw_args.sw_gear_type,
            ai_gw_args.sw_gear_tooth_nb,
            ai_gw_args.sw_gear_module,
            ai_gw_args.sw_gear_primitive_diameter,
            ai_gw_args.sw_gear_base_diameter,
            ai_gw_args.sw_gear_tooth_half_height,
            ai_gw_args.sw_gear_addendum_dedendum_parity,
            ai_gw_args.sw_gear_addendum_height_pourcentage,
            ai_gw_args.sw_gear_dedendum_height_pourcentage,
            ai_gw_args.sw_gear_hollow_height_pourcentage,
            ai_gw_args.sw_gear_reamer_radius,
            ai_gw_args.sw_gear_initial_angle,
            ai_gw_args.sw_second_gear_position_angle,
            ai_gw_args.sw_second_gear_additional_axe_length,
            ai_gw_args.sw_gear_force_angle,
            ai_gw_args.sw_second_gear_tooth_nb,
            ai_gw_args.sw_second_gear_primitive_diameter,
            ai_gw_args.sw_second_gear_base_diameter,
            ai_gw_args.sw_second_gear_tooth_half_height,
            ai_gw_args.sw_second_gear_addendum_dedendum_parity,
            ai_gw_args.sw_second_gear_addendum_height_pourcentage,
            ai_gw_args.sw_second_gear_dedendum_height_pourcentage,
            ai_gw_args.sw_second_gear_hollow_height_pourcentage,
            ai_gw_args.sw_second_gear_reamer_radius,
            ai_gw_args.sw_simulation_enable,
            ai_gw_args.sw_simulation_zoom,
            ai_gw_args.sw_axe_type,
            ai_gw_args.sw_axe_size_1,
            ai_gw_args.sw_axe_size_2,
            ai_gw_args.sw_axe_reamer_radius,
            ai_gw_args.sw_portion_tooth_nb,
            ai_gw_args.sw_wheel_hollow_internal_diameter,
            ai_gw_args.sw_wheel_hollow_external_diameter,
            ai_gw_args.sw_wheel_hollow_leg_number,
            ai_gw_args.sw_wheel_hollow_leg_width,
            ai_gw_args.sw_wheel_hollow_reamer_radius,
            ai_gw_args.sw_part_split,
            ai_gw_args.sw_center_position_x,
            ai_gw_args.sw_center_position_y,
            ai_gw_args.sw_gearwheel_height,
            ai_gw_args.sw_cnc_reamer_radius,
            ai_gw_args.sw_gear_tooth_resolution,
            ai_gw_args.sw_output_file_basename)
  return(r_gw)

################################################################
# self test
################################################################

def gearwheel_self_test():
  """
  This is the non-regression test of gearwheel.
  Look at the simulation Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"                                    , ""],
    ["simplest test with simulation"                    , "--simulation_enable"],
    ["simple reduction (ratio<1)"                       , "--second_gear_tooth_nb 21 --simulation_enable"],
    ["simple transmission (ratio=1)"                    , "--gear_tooth_nb 13 --second_gear_tooth_nb 13 --simulation_enable"],
    ["simple multiplication (ratio>1)"                  , "--gear_tooth_nb 19 --second_gear_tooth_nb 16 --simulation_enable"],
    ["big ratio and zoom"                               , "--gear_tooth_nb 19 --second_gear_tooth_nb 137 --simulation_zoom 4.0 --simulation_enable"],
    ["single gear with same primitive and base circle"  , "--gear_tooth_nb 17 --gear_base_diameter 17.0 --simulation_enable"],
    ["single gear with small base circle"               , "--gear_tooth_nb 27 --gear_base_diameter 23.5 --simulation_enable"],
    ["with first and second angle and inter-axe length" , "--second_gear_tooth_nb 21 --gear_initial_angle {:f} --second_gear_position_angle {:f} --second_gear_additional_axe_length 0.2 --simulation_enable".format(15*math.pi/180, 40.0*math.pi/180)],
    ["other with first and second angle"                , "--second_gear_tooth_nb 15 --gear_initial_angle  {:f} --second_gear_position_angle  {:f} --simulation_enable".format(-5*math.pi/180, 170.0*math.pi/180)],
    ["with force angle constraint"                      , "--gear_tooth_nb 17 --second_gear_tooth_nb 27 --gear_force_angle {:f} --simulation_enable".format(20*math.pi/180)],
    ["first base radius constraint"                     , "--gear_tooth_nb 26 --second_gear_tooth_nb 23 --gear_base_diameter 23.0 --simulation_enable"],
    ["second base radius constraint"                    , "--second_gear_tooth_nb 23 --second_gear_primitive_diameter 20.3 --simulation_enable"],
    ["fine draw resolution"                             , "--second_gear_tooth_nb 19 --gear_tooth_resolution 10 --simulation_enable"],
    ["ratio 1 and dedendum at 30%%"                     , "--second_gear_tooth_nb 17 --gear_dedendum_height_pourcentage 30.0 --second_gear_addendum_height_pourcentage 30.0 --simulation_enable"],
    ["ratio > 1 and dedendum at 40%%"                   , "--second_gear_tooth_nb 23 --gear_dedendum_height_pourcentage 40.0 --second_gear_addendum_height_pourcentage 40.0 --simulation_enable"],
    ["ratio > 1 and addendum at 80%%"                   , "--second_gear_tooth_nb 17 --gear_addendum_height_pourcentage 80.0 --second_gear_dedendum_height_pourcentage 80.0 --simulation_enable"],
    ["ratio > 1 and dedendum at 160%%"                  , "--second_gear_tooth_nb 21 --gear_dedendum_height_pourcentage 160.0 --simulation_enable"],
    ["ratio > 1 and small tooth height"                 , "--second_gear_tooth_nb 29 --gear_tooth_half_height 1.3 --second_gear_tooth_half_height 1.3 --simulation_enable"],
    ["ratio > 1 and big tooth height"                   , "--second_gear_tooth_nb 29 --gear_tooth_half_height 2.3 --second_gear_tooth_half_height 2.3 --simulation_enable"],
    ["ratio > 1 and addendum-dedendum parity"           , "--gear_tooth_nb 30 --second_gear_tooth_nb 37 --gear_addendum_dedendum_parity 60.0 --second_gear_addendum_dedendum_parity 40.0 --simulation_enable"],
    ["file generation"                                  , "--center_position_x 100 --center_position_y 50 --output_file_basename self_test_output/"],
    ["interior gear"                                    , "--second_gear_tooth_nb 14 --gear_type ie --simulation_enable"],
    ["interior gear"                                    , "--gear_tooth_nb 25 --second_gear_tooth_nb 17 --gear_type ie --second_gear_position_angle {:f} --simulation_enable".format(30.0*math.pi/180)],
    ["interior second gear"                             , "--second_gear_tooth_nb 29 --gear_type ei --simulation_enable"],
    ["interior second gear"                             , "--second_gear_tooth_nb 24 --gear_type ei --second_gear_position_angle {:f} --simulation_enable".format(-75*math.pi/180)],
    ["interior gear"                                    , "--second_gear_tooth_nb 14 --gear_type ie --gear_addendum_height_pourcentage 75.0 --simulation_enable"],
    ["cremailliere"                                     , "--gear_type ce --gear_tooth_nb 3 --second_gear_tooth_nb 20 --gear_primitive_diameter 15 --gear_base_diameter 20 --simulation_enable"],
    ["cremailliere with angle"                          , "--gear_type ce --gear_tooth_nb 12 --second_gear_tooth_nb 20 --gear_primitive_diameter 40 --gear_base_diameter 20 --gear_initial_angle {:f} --simulation_enable".format(40*math.pi/180)]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = gearwheel_parser.parse_args(l_args)
    r_gwst = gearwheel_argparse(st_args)
  return(r_gwst)

################################################################
# command line interface
################################################################

def gearwheel_cli():
  """ command line interface of gearwheel.py when it is used in standalone
  """
  # this ensure the possible to use the script with python and freecad
  # You can not use argparse and FreeCAD together, so it's actually useless !
  # Running this script, FreeCAD will just use the argparse default values
  arg_index_offset=0
  if(sys.argv[0]=='freecad'): # check if the script is used by freecad
    arg_index_offset=1
    if(len(sys.argv)>=2):
      if(sys.argv[1]=='-c'): # check if the script is used by freecad -c
        arg_index_offset=2
  effective_args = sys.argv[arg_index_offset+1:]
  #print("dbg115: effective_args:", str(effective_args))
  #FreeCAD.Console.PrintMessage("dbg116: effective_args: %s\n"%(str(effective_args)))
  gw_args = gearwheel_parser.parse_args(effective_args)
  print("dbg111: start making gearwheel")
  if(gw_args.sw_self_test_enable):
    r_gw = gearwheel_self_test()
  else:
    r_gw = gearwheel_argparse(gw_args)
  print("dbg999: end of script")
  return(r_gw)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearwheel.py says hello!\n")
  my_gw = gearwheel_cli()
  #Part.show(my_gw)


