# epicyclic_gearing.py
# generates an epicyclic_gearing and simulates the sun/planet gear or the planet/annulus gear.
# created by charlyoleg on 2013/10/07
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
epicyclic_gearing.py is a parametric generator of epicylic gearing.
The main function displays in a Tk-interface the epicyclic gearing, or generate the design as files or returns the design as FreeCAD Part object.
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
import gearwheel

################################################################
# epicyclic_gearing dictionary-arguments default values
################################################################

def epicyclic_gearing_dictionary_init():
  """ create and initiate an epicyclic_gearing_dictionary with the default value
  """
  r_egd = {}
  #### epicyclic_gearing dictionary entries
  ### structure
  r_egd['sun_gear_tooth_nb']       = 19
  r_egd['planet_gear_tooth_nb']    = 31
  r_egd['planet_nb']               = 3
  ### gear
  r_egd['gear_module']             = 1.0
  r_egd['gear_router_bit_radius']  = 0.1
  r_egd['gear_tooth_resolution']   = 2
  r_egd['gear_skin_thickness']     = 0.0
  r_egd['gear_addendum_dedendum_parity_slack'] = 0.0
  ### sun-gear
  r_egd['sun_axle_diameter']       = 3.0
  r_egd['sun_crenel_diameter']     = 0.0
  r_egd['sun_crenel_nb']           = 8
  r_egd['sun_crenel_width']        = 4.0
  r_egd['sun_crenel_height']       = 2.0
  r_egd['sun_crenel_router_bit_radius']   = 1.0
  ### planet-gear
  r_egd['planet_axle_diameter']      = 3.0
  r_egd['planet_crenel_diameter']    = 0.0
  r_egd['planet_crenel_nb']          = 8
  r_egd['planet_crenel_width']       = 4.0
  r_egd['planet_crenel_height']      = 2.0
  r_egd['planet_crenel_router_bit_radius']  = 1.0
  ### planet gear carrier
  r_egd['carrier_central_diameter']              = 20.0
  r_egd['carrier_leg_diameter']                  = 20.0
  r_egd['carrier_peripheral_external_diameter']  = 0.0
  r_egd['carrier_peripheral_internal_diameter']  = 0.0
  r_egd['carrier_router_bit_radius']             = 10.0
  r_egd['carrier_central_hole_diameter']   = 10.0
  r_egd['carrier_leg_hole_diameter']       = 10.0
  ## carrier central crenel: inherit from sun-gear
  #r_egd['carrier_central_crenel_diameter']     = r_egd['sun_crenel_diameter']     
  #r_egd['carrier_central_crenel_nb']           = r_egd['sun_crenel_nb']           
  #r_egd['carrier_central_crenel_width']        = r_egd['sun_crenel_width']        
  #r_egd['carrier_central_crenel_height']       = r_egd['sun_crenel_height']       
  #r_egd['carrier_central_router_bit_radius']   = r_egd['sun_crenel_router_bit_radius']   
  ## carrier peripheral crenel
  r_egd['carrier_crenel_width']                = 4.0
  r_egd['carrier_crenel_height']               = 2.0
  r_egd['carrier_crenel_router_bit_radius']    = 0.1
  ### annulus: inherit dictionary entries from gearring
  r_egd.update(gearring.gearring_dictionary_init(1))
  ### general
  r_egd['cnc_router_bit_radius']   = 1.0
  r_egd['gear_profile_height']     = 10.0
  ### output
  r_egd['tkinter_view']                    = False
  r_egd['simulation_sun_planet_gear']      = False
  r_egd['simulation_planet_annulus_gear']  = False
  r_egd['output_file_basename']            = ''
  ### optional
  r_egd['args_in_txt'] = ""
  r_egd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_egd)

################################################################
# epicyclic_gearing argparse
################################################################

def epicyclic_gearing_add_argument(ai_parser):
  """
  Add arguments relative to the epicyclic-gearing in addition to the argument of gearring(variant=1)
  This function intends to be used by the epicyclic_gearing_cli, epicyclic_gearing_self_test
  """
  r_parser = ai_parser
  ### structure
  r_parser.add_argument('--sun_gear_tooth_nb','--sgn', action='store', type=int, default=19, dest='sw_sun_gear_tooth_nb',
    help="Set the number of gear-teeth of the sun-gear. Default: 19")
  r_parser.add_argument('--planet_gear_tooth_nb','--pgn', action='store', type=int, default=31, dest='sw_planet_gear_tooth_nb',
    help="Set the number of gear-teeth of the planet-gear. Default: 31")
  r_parser.add_argument('--planet_nb','--pn', action='store', type=int, default=0, dest='sw_planet_nb',
    help="Set the number of planets. If equal to zero, the maximum possible number of planets is set. Default: 0")
  ### gear
  r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=1.0, dest='sw_gear_module',
    help="Set the module of the sun, planet and annulus gear. Default: 1.0")
  r_parser.add_argument('--gear_router_bit_radius','--grr', action='store', type=float, default=0.1, dest='sw_gear_router_bit_radius',
    help="Set the router_bit radius used to create the gear hollow of the first gear_profile. Default: 0.1")
  r_parser.add_argument('--gear_tooth_resolution','--gtr', action='store', type=int, default=2, dest='sw_gear_tooth_resolution',
    help="It sets the number of segments of the gear involute. Default: 2")
  r_parser.add_argument('--gear_skin_thickness','--gst', action='store', type=float, default=0.0, dest='sw_gear_skin_thickness',
    help="Add or remove radial thickness on the gear involute to compensate the fabrication process. Default: 0.0")
  r_parser.add_argument('--gear_addendum_dedendum_parity_slack','--gadps', action='store', type=float, default=0.0, dest='sw_gear_addendum_dedendum_parity_slack',
    help="Decrease the gear_addendum_dedendum_parity to add some slack. Default: 0.0")
  ### sun-gear
  r_parser.add_argument('--sun_axle_diameter','--sad', action='store', type=float, default=0.0, dest='sw_sun_axle_diameter',
    help="Set the diameter of the sun-gear cylindrical axle. Default: 0.0")
  r_parser.add_argument('--sun_crenel_diameter','--scd', action='store', type=float, default=0.0, dest='sw_sun_crenel_diameter',
    help="Set the diameter of the positioning circle for the sun-crenel. Default: 0.0")
  r_parser.add_argument('--sun_crenel_nb','--scn', action='store', type=int, default=0, dest='sw_sun_crenel_nb',
    help="Set the number of sun-crenels. If equal to zero, no sun-crenel is created. Default: 0")
  r_parser.add_argument('--sun_crenel_width','--scw', action='store', type=float, default=4.0, dest='sw_sun_crenel_width',
    help="Set the width of the sun-crenel. Default: 4.0")
  r_parser.add_argument('--sun_crenel_height','--sch', action='store', type=float, default=2.0, dest='sw_sun_crenel_height',
    help="Set the height of the sun-crenel. Default: 2.0")
  r_parser.add_argument('--sun_crenel_router_bit_radius','--scrbr', action='store', type=float, default=0.1, dest='sw_sun_crenel_router_bit_radius',
    help="Set the router_bit radius for the sun-crenel. Default: 0.1")
  ### planet-gear
  r_parser.add_argument('--planet_axle_diameter','--pad', action='store', type=float, default=0.0, dest='sw_planet_axle_diameter',
    help="Set the diameter of the planet-gear cylindrical axle. Default: 0.0")
  r_parser.add_argument('--planet_crenel_diameter','--pcd', action='store', type=float, default=0.0, dest='sw_planet_crenel_diameter',
    help="Set the diameter of the positioning circle for the planet-crenel. Default: 0.0")
  r_parser.add_argument('--planet_crenel_nb','--pcn', action='store', type=int, default=0, dest='sw_planet_crenel_nb',
    help="Set the number of planet-crenels. If equal to zero, no planet-crenel is created. Default: 0")
  r_parser.add_argument('--planet_crenel_width','--pcw', action='store', type=float, default=4.0, dest='sw_planet_crenel_width',
    help="Set the width of the planet-crenel. Default: 4.0")
  r_parser.add_argument('--planet_crenel_height','--pch', action='store', type=float, default=2.0, dest='sw_planet_crenel_height',
    help="Set the height of the planet-crenel. Default: 2.0")
  r_parser.add_argument('--planet_crenel_router_bit_radius','--pcrbr', action='store', type=float, default=0.1, dest='sw_planet_crenel_router_bit_radius',
    help="Set the router_bit radius for the planet-crenel. Default: 0.1")
  ### planet gear carrier
  r_parser.add_argument('--carrier_central_diameter','--ccd', action='store', type=float, default=20.0, dest='sw_carrier_central_diameter',
    help="Set the diameter of the outline of the central part of the planet-carrier. Default: 20.0")
  r_parser.add_argument('--carrier_leg_diameter','--cld', action='store', type=float, default=20.0, dest='sw_carrier_leg_diameter',
    help="Set the diameter of the outline of the leg part of the planet-carrier. Default: 20.0")
  r_parser.add_argument('--carrier_peripheral_external_diameter','--cped', action='store', type=float, default=0.0, dest='sw_carrier_peripheral_external_diameter',
    help="Set the diameter of the outline of the additional circle around the planet-carrier. If equal to 0, no additional circle is generated. Default: 0.0")
  r_parser.add_argument('--carrier_peripheral_internal_diameter','--cpid', action='store', type=float, default=0.0, dest='sw_carrier_peripheral_internal_diameter',
    help="Set the internal diameter of the additional circle around the planet-carrier. If equal to 0, the planet-carrier is filled (no hollow). Default: 0.0")
  r_parser.add_argument('--carrier_router_bit_radius','--crbr', action='store', type=float, default=10, dest='sw_carrier_router_bit_radius',
    help="Set the router_bit radius for the planet-carrier. Default: 10")
  r_parser.add_argument('--carrier_central_hole_diameter','--cchd', action='store', type=float, default=10.0, dest='sw_carrier_central_hole_diameter',
    help="Set the diameter of the central hole of the planet-carrier. Default: 10.0")
  r_parser.add_argument('--carrier_leg_hole_diameter','--clhd', action='store', type=float, default=10.0, dest='sw_carrier_leg_hole_diameter',
    help="Set the diameter of the leg hole of the planet-carrier. Default: 10.0")
  ## carrier peripheral crenel
  r_parser.add_argument('--carrier_crenel_width','--ccw', action='store', type=float, default=4.0, dest='sw_carrier_crenel_width',
    help="Set the width of the carrier-crenel. Default: 4.0")
  r_parser.add_argument('--carrier_crenel_height','--cch', action='store', type=float, default=2.0, dest='sw_carrier_crenel_height',
    help="Set the height of the carrier-crenel. Default: 2.0")
  r_parser.add_argument('--carrier_crenel_router_bit_radius','--ccrbr', action='store', type=float, default=0.1, dest='sw_carrier_crenel_router_bit_radius',
    help="Set the router_bit radius for the carrier-crenel. Default: 0.1")
  ### annulus: inherit dictionary entries from gearring
  r_parser = gearring.gearring_add_argument(r_parser, 1)
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the epicyclic-gearing. Default: 0.1")
  r_parser.add_argument('--gear_profile_height','--gwh', action='store', type=float, default=10.0, dest='sw_gear_profile_height',
    help="Set the height of the linear extrusion of the first gear_profile. Default: 10.0")
  ### output
  r_parser.add_argument('--simulation_sun_planet_gear','--sspg', action='store_true', default=False, dest='sw_simulation_sun_planet_gear',
    help='Simulate the sun-planet gear with gear_profile.py')
  r_parser.add_argument('--simulation_planet_annulus_gear','--spag', action='store_true', default=False, dest='sw_simulation_planet_annulus_gear',
    help='Simulate the planet-annulus gear with gear_profile.py')
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def epicyclic_gearing(ai_constraints):
  """
  The main function of the script.
  It generates a epicyclic-gearing according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  egdi = epicyclic_gearing_dictionary_init()
  eg_c = egdi.copy()
  eg_c.update(ai_constraints)
  #print("dbg155: eg_c:", eg_c)
  if(len(eg_c.viewkeys() & egdi.viewkeys()) != len(eg_c.viewkeys() | egdi.viewkeys())): # check if the dictionary eg_c has exactly all the keys compare to epicyclic_gearing_dictionary_init()
    print("ERR157: Error, eg_c has too much entries as {:s} or missing entries as {:s}".format(eg_c.viewkeys() - egdi.viewkeys(), egdi.viewkeys() - eg_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new epicyclic_gearing constraints:")
  #for k in eg_c.viewkeys():
  #  if(eg_c[k] != egdi[k]):
  #    print("dbg166: for k {:s}, eg_c[k] {:s} != egdi[k] {:s}".format(k, str(eg_c[k]), str(egdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
#  ### check parameter coherence (part 1)
#  # get the router_bit_radius
#  gear_router_bit_radius = sg_c['gear_router_bit_radius']
#  if(sg_c['cnc_router_bit_radius']>gear_router_bit_radius):
#    gear_router_bit_radius = sg_c['cnc_router_bit_radius']
#  split_router_bit_radius = sg_c['split_router_bit_radius']
#  if(sg_c['cnc_router_bit_radius']>split_router_bit_radius):
#    split_router_bit_radius = sg_c['cnc_router_bit_radius']
#  # sg_c['low_split_type']
#  if(not sg_c['low_split_type'] in ('circle', 'line')):
#    print("ERR216: Error, sg_c['low_split_type'] {:s} is not valid!".format(sg_c['low_split_type']))
#    sys.exit(2)
#  # sg_c['high_split_type']
#  if(not sg_c['high_split_type'] in ('h', 'a')):
#    print("ERR220: Error, sg_c['high_split_type'] {:s} is not valid!".format(sg_c['high_split_type']))
#    sys.exit(2)
#  # sg_c['split_nb']
#  split_nb = sg_c['split_nb']
#  if(split_nb<2):
#    print("ERR188: Error, split_nb {:d} must be equal or bigger than 2".format(split_nb))
#    sys.exit(2)
#  #portion_angle = 2*math.pi/split_nb
#  portion_angle = math.pi/split_nb
#  #print("dbg190: sg_c['gear_tooth_nb']:", sg_c['gear_tooth_nb'])
#  if(sg_c['gear_tooth_nb']>0): # create a gear_profile
#    ### get the gear_profile
#    gp_ci = gear_profile.gear_profile_dictionary_init()
#    gp_c = dict([ (k, sg_c[k]) for k in gp_ci.keys() ]) # extract only the entries of the gear_profile
#    gp_c['gear_type'] = 'e'
#    gp_c['gear_router_bit_radius'] = gear_router_bit_radius
#    gp_c['portion_tooth_nb'] = 0
#    gp_c['portion_first_end'] = 0
#    gp_c['portion_last_end'] = 0
#    gp_c['output_file_basename'] = ''
#    gp_c['args_in_txt'] = ''
#    gp_c['return_type'] = 'figure_param_info'
#    (gear_profile_B, gear_profile_parameters, gear_profile_info) = gear_profile.gear_profile(gp_c)
#    # extract some gear_profile high-level parameter
#    #print('dbg556: gear_profile_parameters:', gear_profile_parameters)
#    minimal_gear_profile_radius = gear_profile_parameters['hollow_radius']
#    g1_ix = gear_profile_parameters['center_ox']
#    g1_iy = gear_profile_parameters['center_oy']
#    # high_split_radius
#    g1_m = gear_profile_parameters['module']
#    high_split_radius = sg_c['high_split_diameter']/2.0
#    if(high_split_radius==0):
#      high_split_radius = minimal_gear_profile_radius - g1_m
#    ## gear_portion
#    g1_pma = gear_profile_parameters['pi_module_angle']
#    g1_hma = gear_profile_parameters['hollow_middle_angle']
#    g1_ia = gear_profile_parameters['initial_angle']
#    g1_tl = gear_profile_parameters['top_land']
#    if(portion_angle<(1.1*g1_pma)):
#      print("ERR219: Error, portion_angle {:0.3f} is too small compare to the pi_module_angle {:0.3f}".format(portion_angle, g1_pma))
#      sys.exit(2)
#    # pre common calculation
#    absolute_angle = []
#    relative_angle = []
#    raw_tooth_nb = []
#    a_start = g1_ia + g1_hma
#    overhead = 2 # must be equal or bigger than 2 because of raw_tooth_nb[i-overhead+2]
#    for i in range(2*split_nb+overhead):
#      portion_start_angle = sg_c['split_initial_angle'] + (i+0.0) * portion_angle
#      tooth_nb = 0
#      while(abs(math.fmod(a_start-portion_start_angle+5*math.pi, 2*math.pi)-math.pi)>g1_pma/2.0):
#        a_start += g1_pma
#        tooth_nb += 1
#      absolute_angle.append(a_start)
#      relative_angle.append(math.fmod(a_start-portion_start_angle+5*math.pi, 2*math.pi)-math.pi)
#      raw_tooth_nb.append(tooth_nb)
#      #print("dbg238: i {:d} raw_tooth_nb {:0.3f}".format(i, raw_tooth_nb[i]))
#    absolute_angle = absolute_angle[overhead:]
#    relative_angle = relative_angle[overhead:]
#    raw_tooth_nb = raw_tooth_nb[overhead:]
#    # final low-parameters
#    portion_gear_tooth_angle = []
#    portion_gear_first_end = []
#    portion_gear_last_end = []
#    portion_gear_tooth_nb = []
#    for i in range(2*split_nb):
#      ii = i-overhead
#      if(sg_c['high_split_type']=='h'):
#        portion_gear_tooth_angle.append(absolute_angle[ii]-g1_hma+g1_pma)
#        portion_gear_first_end.append(3)
#        portion_gear_last_end.append(3)
#        portion_gear_tooth_nb.append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1)
#      elif(sg_c['high_split_type']=='a'):
#        tooth_transfer = 0
#        if(abs(relative_angle[ii])<=(g1_pma-g1_tl)/2.0):
#          portion_gear_first_end.append(3)
#          portion_gear_tooth_angle.append(absolute_angle[ii]-g1_hma+g1_pma)
#        elif(relative_angle[ii]>=(g1_pma-g1_tl)/2.0):
#          portion_gear_first_end.append(1)
#          portion_gear_tooth_angle.append(absolute_angle[ii]-g1_hma)
#          tooth_transfer = 1
#        elif(relative_angle[ii]<=-1*(g1_pma-g1_tl)/2.0):
#          portion_gear_first_end.append(1)
#          portion_gear_tooth_angle.append(absolute_angle[ii]-g1_hma+g1_pma)
#        if(abs(relative_angle[ii+2])<=(g1_pma-g1_tl)/2.0):
#          portion_gear_tooth_nb.append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1+tooth_transfer)
#          portion_gear_last_end.append(3)
#        elif(relative_angle[ii+2]>=(g1_pma-g1_tl)/2.0):
#          portion_gear_tooth_nb.append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-1+tooth_transfer)
#          portion_gear_last_end.append(1)
#        elif(relative_angle[ii+2]<=-1*(g1_pma-g1_tl)/2.0):
#          portion_gear_tooth_nb.append(raw_tooth_nb[ii+2]+raw_tooth_nb[ii+1]-0+tooth_transfer)
#          portion_gear_last_end.append(1)
#    #print("dbg276: len(portion_gear_first_end) {:d}  len(portion_gear_last_end) {:d}".format(len(portion_gear_first_end), len(portion_gear_last_end)))
#  else: # no gear_profile, just a circle
#    if(sg_c['gear_primitive_diameter']<radian_epsilon):
#      print("ERR885: Error, the no-gear-profile circle outline diameter sg_c['gear_primitive_diameter'] {:0.2f} is too small!".format(sg_c['gear_primitive_diameter']))
#      sys.exit(2)
#    #gear_profile_B = (g1_ix, g1_iy, float(sg_c['gear_primitive_diameter'])/2)
#    minimal_gear_profile_radius = float(sg_c['gear_primitive_diameter'])/2
#    g1_ix = sg_c['center_position_x']
#    g1_iy = sg_c['center_position_y']
#    gear_profile_info = "\nSimple circle (no-gear-profile):\n"
#    gear_profile_info += "outline circle radius: \t{:0.3f}  \tdiameter: {:0.3f}\n".format(sg_c['gear_primitive_diameter']/2.0, sg_c['gear_primitive_diameter'])
#    gear_profile_info += "gear center (x, y):   \t{:0.3f}  \t{:0.3f}\n".format(g1_ix, g1_iy)
#    if(sg_c['high_split_diameter']!=0):
#      print("WARN221: Warning, the setting high_split_diameter {:0.3f} should not be used when gear_tooth_nb=0".format(sg_c['high_split_diameter']))
#    high_split_radius = minimal_gear_profile_radius
#  # set default value (if set to zero) for high_split_diameter, low_hole_circle_diameter, high_hole_circle_diameter
#  low_split_radius = sg_c['low_split_diameter']/2.0
#  low_hole_radius = sg_c['low_hole_diameter']/2.0
#  low_hole_circle_radius = sg_c['low_hole_circle_diameter']/2.0
#  high_hole_circle_radius = sg_c['high_hole_circle_diameter']/2.0
#  high_hole_radius = sg_c['high_hole_diameter']/2.0
#  if(low_hole_circle_radius==0):
#    low_hole_circle_radius = low_split_radius + 2*low_hole_radius
#  if(high_hole_circle_radius==0):
#    high_hole_circle_radius = high_split_radius - 1.2*high_hole_radius
#  #print("dbg292: high_hole_circle_radius {:0.3f}  high_split_radius {:0.3f}".format(high_hole_circle_radius, high_split_radius))
#  ### check parameter coherence (part 2)
#  # low_hole_nb and high_hole_nb
#  if(sg_c['low_hole_nb']==0):
#    low_hole_radius = 0
#    sg_c['low_hole_nb']=1
#  if(sg_c['high_hole_nb']==0):
#    high_hole_radius = 0
#    sg_c['high_hole_nb']=1
#  # radial parameters
#  if(low_hole_circle_radius<(low_split_radius + low_hole_radius)):
#    print("ERR230: Error, low_hole_circle_radius {:0.3f} is too small compare to low_split_radius {:0.3f} and low_hole_radius {:0.3f}".format(low_hole_circle_radius, low_split_radius, low_hole_radius))
#    sys.exit(2)
#  if(high_hole_circle_radius<(low_hole_circle_radius + low_hole_radius + high_hole_radius)):
#    print("ERR232: Error, high_hole_circle_radius {:0.3f} is too small compare to low_hole_circle_radius {:0.3f}, low_hole_radius {:0.3f} and high_hole_radius {:0.3f}".format(high_hole_circle_radius, low_hole_circle_radius, low_hole_radius, high_hole_radius))
#    sys.exit(2)
#  if(high_split_radius<(high_hole_circle_radius + high_hole_radius)):
#    print("ERR236: Error, high_split_radius {:0.3f} is too small compare to high_hole_circle_radius {:0.3f} and high_hole_radius {:0.3f}".format(high_split_radius, high_hole_circle_radius, high_hole_radius))
#    sys.exit(2)
#  if(minimal_gear_profile_radius<high_split_radius):
#    print("ERR239: Error, minimal_gear_profile_radius {:0.3f} is smaller than high_split_radius {:0.3f}".format(minimal_gear_profile_radius, high_split_radius))
#    sys.exit(2)
#  # angular (or circumference) parameters
#  low_hole_diameter_angle = math.asin(float(low_hole_radius)/low_hole_circle_radius)
#  low_hole_space_angle = portion_angle/float(sg_c['low_hole_nb'])
#  high_hole_diameter_angle = math.asin(float(high_hole_radius)/high_hole_circle_radius)
#  high_hole_space_angle = portion_angle/float(sg_c['high_hole_nb'])
#  if(low_hole_space_angle<(2*low_hole_diameter_angle+radian_epsilon)):
#    print("ERR253: Error, low_hole_nb {:d} or low_hole_diameter {:0.3f} are too big!".format(sg_c['low_hole_nb'], sg_c['low_hole_diameter']))
#    sys.exit(2)
#  if(high_hole_space_angle<(2*high_hole_diameter_angle+radian_epsilon)):
#    print("ERR255: Error, high_hole_nb {:d} or high_hole_diameter {:0.3f} are too big!".format(sg_c['high_hole_nb'], sg_c['high_hole_diameter']))
#    sys.exit(2)
#  ### generate the portion outlines
#  part_figure_list = []
#  if(sg_c['gear_tooth_nb']>0): # create a gear_profile
#    for i in range(2*split_nb):
#      #print("dbg333:  portion_gear_tooth_nb[i]: {:0.3f}".format(portion_gear_tooth_nb[i]))
#      #print("dbg334:  portion_gear_first_end[i]: {:0.3f}".format(portion_gear_first_end[i]))
#      #print("dbg335:  portion_gear_last_end[i]: {:0.3f}".format(portion_gear_last_end[i]))
#      #print("dbg336:  portion_gear_tooth_angle[i]: {:0.3f}".format(portion_gear_tooth_angle[i]))
#      if(portion_gear_tooth_nb[i]<1):
#        print("ERR338: Error, for i {:d} portion_gear_tooth_nb {:d} smaller than 1".format(i, portion_gear_tooth_nb[i]))
#        sys.exit(2)
#      gp_c['portion_tooth_nb']    = portion_gear_tooth_nb[i]
#      gp_c['portion_first_end']   = portion_gear_first_end[i]
#      gp_c['portion_last_end']    = portion_gear_last_end[i]
#      gp_c['gear_initial_angle']  = portion_gear_tooth_angle[i]
#      gp_c['simulation_enable'] = False
#      gp_c['return_type'] = 'figure_param_info'
#      #print("dbg342: gp_c:", gp_c)
#      #print("dbg341: gp_c['portion_tooth_nb']: {:d}".format(gp_c['portion_tooth_nb']))
#      (gear_profile_B, trash_gear_profile_parameters, trash_gear_profile_info) = gear_profile.gear_profile(gp_c)
#      #print("dbg345: trash_gear_profile_parameters:", trash_gear_profile_parameters)
#      #print("dbg346: trash_gear_profile_parameters['portion_tooth_nb']: {:d}".format(trash_gear_profile_parameters['portion_tooth_nb']))
#      tmp_a = sg_c['split_initial_angle'] + (i+2.0)*portion_angle
#      tmp_b = sg_c['split_initial_angle'] + (i+1.0)*portion_angle
#      tmp_c = sg_c['split_initial_angle'] + (i+0.0)*portion_angle
#      low_portion_A = []
#      low_portion_A.append((gear_profile_B[-1][0], gear_profile_B[-1][1], 0))
#      low_portion_A.append((g1_ix+high_split_radius*math.cos(tmp_a), g1_iy+high_split_radius*math.sin(tmp_a), split_router_bit_radius))
#      low_portion_A.append((g1_ix+low_split_radius*math.cos(tmp_a), g1_iy+low_split_radius*math.sin(tmp_a), 0))
#      if(sg_c['low_split_type']=='circle'):
#        low_portion_A.append((g1_ix+low_split_radius*math.cos(tmp_b), g1_iy+low_split_radius*math.sin(tmp_b), g1_ix+low_split_radius*math.cos(tmp_c), g1_iy+low_split_radius*math.sin(tmp_c), 0))
#      elif(sg_c['low_split_type']=='line'):
#        low_portion_A.append((g1_ix+low_split_radius*math.cos(tmp_b), g1_iy+low_split_radius*math.sin(tmp_b), 0))
#        low_portion_A.append((g1_ix+low_split_radius*math.cos(tmp_c), g1_iy+low_split_radius*math.sin(tmp_c), 0))
#      low_portion_A.append((g1_ix+high_split_radius*math.cos(tmp_c), g1_iy+high_split_radius*math.sin(tmp_c), split_router_bit_radius))
#      low_portion_A.append((gear_profile_B[0][0], gear_profile_B[0][1], 0))
#      low_portion_B = cnc25d_api.cnc_cut_outline(low_portion_A, "portion_A")
#      portion_B = gear_profile_B[:]
#      portion_B.extend(low_portion_B[1:])
#      #part_figure_list.append([portion_B])
#      part_figure_list.append([portion_B[:]])
#  else:
#    for i in range(2*split_nb):
#      tmp_a = sg_c['split_initial_angle'] + (i+2.0)*portion_angle
#      tmp_b = sg_c['split_initial_angle'] + (i+1.0)*portion_angle
#      tmp_c = sg_c['split_initial_angle'] + (i+0.0)*portion_angle
#      portion_A = []
#      portion_A.append((g1_ix+high_split_radius*math.cos(tmp_c), g1_iy+high_split_radius*math.sin(tmp_c), 0))
#      portion_A.append((g1_ix+high_split_radius*math.cos(tmp_b), g1_iy+high_split_radius*math.sin(tmp_b), g1_ix+high_split_radius*math.cos(tmp_a), g1_iy+high_split_radius*math.sin(tmp_a), 0))
#      portion_A.append((g1_ix+low_split_radius*math.cos(tmp_a), g1_iy+low_split_radius*math.sin(tmp_a), 0))
#      if(sg_c['low_split_type']=='circle'):
#        portion_A.append((g1_ix+low_split_radius*math.cos(tmp_b), g1_iy+low_split_radius*math.sin(tmp_b), g1_ix+low_split_radius*math.cos(tmp_c), g1_iy+low_split_radius*math.sin(tmp_c), 0))
#      elif(sg_c['low_split_type']=='line'):
#        portion_A.append((g1_ix+low_split_radius*math.cos(tmp_b), g1_iy+low_split_radius*math.sin(tmp_b), 0))
#        portion_A.append((g1_ix+low_split_radius*math.cos(tmp_c), g1_iy+low_split_radius*math.sin(tmp_c), 0))
#      portion_A.append((g1_ix+high_split_radius*math.cos(tmp_c), g1_iy+high_split_radius*math.sin(tmp_c), 0))
#      portion_B = cnc25d_api.cnc_cut_outline(portion_A, "circle_portion_A")
#      #part_figure_list.append([portion_B])
#      part_figure_list.append([portion_B[:]])
#  ### generate the hole outlines
#  for i in range(len(part_figure_list)):
#    hole_figure = []
#    if(low_hole_radius>0):
#      for j in range(2*sg_c['low_hole_nb']):
#        tmp_a = sg_c['split_initial_angle'] + i*portion_angle + (j+0.5)*low_hole_space_angle
#        hole_figure.append((g1_ix+low_hole_circle_radius*math.cos(tmp_a), g1_iy+low_hole_circle_radius*math.sin(tmp_a), low_hole_radius))
#    if(high_hole_radius>0):
#      for j in range(2*sg_c['high_hole_nb']):
#        tmp_a = sg_c['split_initial_angle'] + i*portion_angle + (j+0.5)*high_hole_space_angle
#        hole_figure.append((g1_ix+high_hole_circle_radius*math.cos(tmp_a), g1_iy+high_hole_circle_radius*math.sin(tmp_a), high_hole_radius))
#    #part_figure_list[i].extend(hole_figure)
#    part_figure_list[i].extend(hole_figure[:])
#
#  ### design output
#  sgw_assembly_figure = []
#  sgw_assembly_A_figure = []
#  sgw_assembly_B_figure = []
#  aligned_part_figure_list = []
#  sgw_list_of_parts = []
#  for i in range(len(part_figure_list)):
#    sgw_assembly_figure.extend(part_figure_list[i])
#    if((i%2)==0):
#      sgw_assembly_A_figure.extend(part_figure_list[i])
#    else:
#      sgw_assembly_B_figure.extend(part_figure_list[i])
#    aligned_part_figure_list.append([])
#    shift_x = 2.2 * (i%2) * minimal_gear_profile_radius
#    shift_y = 2.2 * int(i/2) * minimal_gear_profile_radius
#    for j in range(len(part_figure_list[i])):
#      rotated_outline = cnc25d_api.outline_rotate(part_figure_list[i][j], g1_ix, g1_iy, -1*(sg_c['split_initial_angle'] + i*portion_angle))
#      aligned_part_figure_list[i].append(rotated_outline)
#      sgw_list_of_parts.append(cnc25d_api.outline_shift_xy(rotated_outline, shift_x, 1, shift_y, 1))
#  # ideal_outline in overlay
#  sgw_assembly_figure_overlay = part_figure_list[0]
#  # sgw_parameter_info
#  sgw_parameter_info = "\nSplit-Gearwheel parameter info:\n"
#  sgw_parameter_info += "\n" + sg_c['args_in_txt'] + "\n\n"
#  sgw_parameter_info += gear_profile_info
#  sgw_parameter_info += """
#split_nb:             \t{:d}
#split_initial_angle:  \t{:0.3f} (radian)  \t{:0.3f} (degree)
#high_split_radius:    \t{:0.3f} diameter: \t{:0.3f}
#high_split_type:      \t{:s}
#""".format(split_nb, sg_c['split_initial_angle'], sg_c['split_initial_angle']*180/math.pi, high_split_radius, 2*high_split_radius, sg_c['high_split_type'])
#  sgw_parameter_info += """
#low_split_radius:     \t{:0.3f} diameter: \t{:0.3f}
#low_split_type:       \t{:s}
#""".format(low_split_radius, 2*low_split_radius, sg_c['low_split_type'])
#  sgw_parameter_info += """
#low_hole_circle_radius:   \t{:0.3f} diameter: \t{:0.3f}
#low_hole_radius:          \t{:0.3f} diameter: \t{:0.3f}
#low_hole_nb:              \t{:d}
#""".format(low_hole_circle_radius, 2*low_hole_circle_radius, low_hole_radius, 2*low_hole_radius, sg_c['low_hole_nb'])
#  sgw_parameter_info += """
#high_hole_circle_radius:  \t{:0.3f} diameter: \t{:0.3f}
#high_hole_radius:         \t{:0.3f} diameter: \t{:0.3f}
#high_hole_nb:             \t{:d}
#""".format(high_hole_circle_radius, 2*high_hole_circle_radius, high_hole_radius, 2*high_hole_radius, sg_c['high_hole_nb'])
#  sgw_parameter_info += """
#gear_router_bit_radius:   \t{:0.3f}
#split_router_bit_radius:  \t{:0.3f}
#cnc_router_bit_radius:    \t{:0.3f}
#""".format(gear_router_bit_radius, split_router_bit_radius, sg_c['cnc_router_bit_radius'])
#  #print(sgw_parameter_info)
#
#  ### display with Tkinter
#  if(sg_c['tkinter_view']):
#    print(sgw_parameter_info)
#    #cnc25d_api.figure_simple_display(part_figure_list[0], sgw_assembly_figure_overlay, sgw_parameter_info) # for debug
#    #cnc25d_api.figure_simple_display(sgw_assembly_A_figure, part_figure_list[0], sgw_parameter_info) # for debug
#    cnc25d_api.figure_simple_display(sgw_assembly_figure, sgw_assembly_figure_overlay, sgw_parameter_info)
#    cnc25d_api.figure_simple_display(sgw_assembly_A_figure, sgw_assembly_B_figure, sgw_parameter_info)
#    #for i in range(len(part_figure_list)):
#    #  #cnc25d_api.figure_simple_display(aligned_part_figure_list[i], part_figure_list[i], sgw_parameter_info)
#    #  cnc25d_api.figure_simple_display(part_figure_list[i], part_figure_list[i-1], sgw_parameter_info)
#    cnc25d_api.figure_simple_display(sgw_list_of_parts, [], sgw_parameter_info)
#      
#  ### generate output file
#  output_file_suffix = ''
#  if(sg_c['output_file_basename']!=''):
#    output_file_suffix = 'brep'
#    output_file_basename = sg_c['output_file_basename']
#    if(re.search('\.dxf$', sg_c['output_file_basename'])):
#      output_file_suffix = 'dxf'
#      output_file_basename = re.sub('\.dxf$', '', sg_c['output_file_basename'])
#    elif(re.search('\.svg$', sg_c['output_file_basename'])):
#      output_file_suffix = 'svg'
#      output_file_basename = re.sub('\.svg$', '', sg_c['output_file_basename'])
#  if((output_file_suffix=='svg')or(output_file_suffix=='dxf')):
#    cnc25d_api.generate_output_file(sgw_assembly_figure, output_file_basename + "_assembly." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#    cnc25d_api.generate_output_file(sgw_assembly_A_figure, output_file_basename + "_assembly_A." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#    cnc25d_api.generate_output_file(sgw_assembly_B_figure, output_file_basename + "_assembly_B." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#    cnc25d_api.generate_output_file(sgw_list_of_parts, output_file_basename + "_part_list." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#    for i in range(split_nb):
#      cnc25d_api.generate_output_file(part_figure_list[2*i],    output_file_basename + "_part_A{:d}_placed.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_placed.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i],    output_file_basename + "_part_A{:d}_aligned.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_aligned.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#  elif(output_file_suffix=='brep'):
#    #cnc25d_api.generate_output_file(sgw_assembly_figure, output_file_basename + "_assembly", sg_c['gear_profile_height'], sgw_parameter_info)
#    for i in range(split_nb):
#      cnc25d_api.generate_output_file(part_figure_list[2*i],    output_file_basename + "_part_A{:d}_placed".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_placed".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i],    output_file_basename + "_part_A{:d}_aligned".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_aligned".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
#
#  #### return
#  if(sg_c['return_type']=='int_status'):
#    r_sgw = 1
#  elif(sg_c['return_type']=='cnc25d_figure'):
#    r_sgw = sgw_assembly_A_figure
#  elif(sg_c['return_type']=='freecad_object'):
#    fc_obj = []
#    for i in range(len(part_figure_list)):
#      fc_obj.append(cnc25d_api.figure_to_freecad_25d_part(part_figure_list[i], sg_c['gear_profile_height']))
#      if((i%2)==1):
#        fc_obj[i].translate(Base.Vector(0,0,sg_c['gear_profile_height']))
#    r_sgw = Part.makeCompound(fc_obj)
#  else:
#    print("ERR508: Error the return_type {:s} is unknown".format(sg_c['return_type']))
#    sys.exit(2)
  r_eg = 1
  return(r_eg)

################################################################
# epicyclic_gearing wrapper dance
################################################################

def epicyclic_gearing_argparse_to_dictionary(ai_eg_args):
  """ convert a epicyclic_gearing_argparse into a epicyclic_gearing_dictionary
  """
  r_egd = {}
  #### epicyclic_gearing dictionary entries
  ### structure
  r_egd['sun_gear_tooth_nb']       = ai_eg_args.sw_sun_gear_tooth_nb
  r_egd['planet_gear_tooth_nb']    = ai_eg_args.sw_planet_gear_tooth_nb
  r_egd['planet_nb']               = ai_eg_args.sw_planet_nb
  ### gear
  r_egd['gear_module']             = ai_eg_args.sw_gear_module
  r_egd['gear_router_bit_radius']  = ai_eg_args.sw_gear_router_bit_radius
  r_egd['gear_tooth_resolution']   = ai_eg_args.sw_gear_tooth_resolution
  r_egd['gear_skin_thickness']     = ai_eg_args.sw_gear_skin_thickness
  r_egd['gear_addendum_dedendum_parity_slack'] = ai_eg_args.sw_gear_addendum_dedendum_parity_slack
  ### sun-gear
  r_egd['sun_axle_diameter']       = ai_eg_args.sw_sun_axle_diameter
  r_egd['sun_crenel_diameter']     = ai_eg_args.sw_sun_crenel_diameter
  r_egd['sun_crenel_nb']           = ai_eg_args.sw_sun_crenel_nb
  r_egd['sun_crenel_width']        = ai_eg_args.sw_sun_crenel_width
  r_egd['sun_crenel_height']       = ai_eg_args.sw_sun_crenel_height
  r_egd['sun_crenel_router_bit_radius']   = ai_eg_args.sw_sun_crenel_router_bit_radius
  ### planet-gear
  r_egd['planet_axle_diameter']      = ai_eg_args.sw_planet_axle_diameter
  r_egd['planet_crenel_diameter']    = ai_eg_args.sw_planet_crenel_diameter
  r_egd['planet_crenel_nb']          = ai_eg_args.sw_planet_crenel_nb
  r_egd['planet_crenel_width']       = ai_eg_args.sw_planet_crenel_width
  r_egd['planet_crenel_height']      = ai_eg_args.sw_planet_crenel_height
  r_egd['planet_crenel_router_bit_radius']  = ai_eg_args.sw_planet_crenel_router_bit_radius
  ### planet gear carrier
  r_egd['carrier_central_diameter']              = ai_eg_args.sw_carrier_central_diameter
  r_egd['carrier_leg_diameter']                  = ai_eg_args.sw_carrier_leg_diameter
  r_egd['carrier_peripheral_external_diameter']  = ai_eg_args.sw_carrier_peripheral_external_diameter
  r_egd['carrier_peripheral_internal_diameter']  = ai_eg_args.sw_carrier_peripheral_internal_diameter
  r_egd['carrier_router_bit_radius']             = ai_eg_args.sw_carrier_router_bit_radius
  r_egd['carrier_central_hole_diameter']   = ai_eg_args.sw_carrier_central_hole_diameter
  r_egd['carrier_leg_hole_diameter']       = ai_eg_args.sw_carrier_leg_hole_diameter
  ## carrier peripheral crenel
  r_egd['carrier_crenel_width']                = ai_eg_args.sw_carrier_crenel_width
  r_egd['carrier_crenel_height']               = ai_eg_args.sw_carrier_crenel_height
  r_egd['carrier_crenel_router_bit_radius']    = ai_eg_args.sw_carrier_crenel_router_bit_radius
  ### annulus: inherit dictionary entries from gearring
  r_egd.update(gearring.gearring_argparse_to_dictionary(ai_eg_args, 1))
  ### general
  r_egd['cnc_router_bit_radius']   = ai_eg_args.sw_cnc_router_bit_radius
  r_egd['gear_profile_height']     = ai_eg_args.sw_gear_profile_height
  ### output
  #r_egd['tkinter_view']                    = False
  r_egd['simulation_sun_planet_gear']      = ai_eg_args.sw_simulation_sun_planet_gear
  r_egd['simulation_planet_annulus_gear']  = ai_eg_args.sw_simulation_planet_annulus_gear
  r_egd['output_file_basename']            = ai_eg_args.sw_output_file_basename
  ### optional
  #r_egd['args_in_txt'] = ""
  r_egd['return_type'] = ai_eg_args.sw_return_type
  #### return
  return(r_egd)
  
def epicyclic_gearing_argparse_wrapper(ai_eg_args, ai_args_in_txt=""):
  """
  wrapper function of epicyclic_gearing() to call it using the epicyclic_gearing_parser.
  epicyclic_gearing_parser is mostly used for debug and non-regression tests.
  """
  # view the epicyclic_gearing with Tkinter as default action
  tkinter_view = True
  if(ai_eg_args.sw_simulation_sun_planet_gear or ai_eg_args.sw_simulation_planet_annulus_gear or (ai_eg_args.sw_output_file_basename!='')):
    tkinter_view = False
  # wrapper
  egd = epicyclic_gearing_argparse_to_dictionary(ai_eg_args)
  egd['args_in_txt'] = ai_args_in_txt
  egd['tkinter_view'] = tkinter_view
  #egd['return_type'] = 'int_status'
  r_eg = epicyclic_gearing(egd)
  return(r_eg)

################################################################
# self test
################################################################

def epicyclic_gearing_self_test():
  """
  This is the non-regression test of epicyclic_gearing.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2"],
    ["gear simulation"      , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --simulation_enable --second_gear_tooth_nb 19"],
    ["output file"          , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --output_file_basename test_output/split_gearwheel_self_test.dxf"],
    ["last test"            , "--gear_tooth_nb 24 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  epicyclic_gearing_parser = argparse.ArgumentParser(description='Command line interface for the function epicyclic_gearing().')
  epicyclic_gearing_parser = epicyclic_gearing_add_argument(epicyclic_gearing_parser)
  epicyclic_gearing_parser = cnc25d_api.generate_output_file_add_argument(epicyclic_gearing_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = epicyclic_gearing_parser.parse_args(l_args)
    r_egst = epicyclic_gearing_argparse_wrapper(st_args)
  return(r_egst)

################################################################
# epicyclic_gearing command line interface
################################################################

def epicyclic_gearing_cli(ai_args=None):
  """ command line interface of epicyclic_gearing.py when it is used in standalone
  """
  # epicyclic_gearing parser
  epicyclic_gearing_parser = argparse.ArgumentParser(description='Command line interface for the function epicyclic_gearing().')
  epicyclic_gearing_parser = epicyclic_gearing_add_argument(epicyclic_gearing_parser)
  epicyclic_gearing_parser = cnc25d_api.generate_output_file_add_argument(epicyclic_gearing_parser, 1)
  # switch for self_test
  epicyclic_gearing_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "epicyclic_gearing arguments: " + ' '.join(effective_args)
  eg_args = epicyclic_gearing_parser.parse_args(effective_args)
  print("dbg111: start making epicyclic_gearing")
  if(eg_args.sw_run_self_test):
    r_eg = epicyclic_gearing_self_test()
  else:
    r_eg = epicyclic_gearing_argparse_wrapper(eg_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_eg)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("epicyclic_gearing.py says hello!\n")
  #my_eg = epicyclic_gearing_cli()
  #my_eg = epicyclic_gearing_cli("--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --return_type freecad_object".split())
  my_eg = epicyclic_gearing_cli("--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31".split())
  #Part.show(my_eg)
  try: # depending on eg_c['return_type'] it might be or not a freecad_object
    Part.show(my_eg)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")

