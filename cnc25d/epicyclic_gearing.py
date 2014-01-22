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
import gear_profile # to get the high-level parameter to find the angle position
import axle_lid

################################################################
# epicyclic_gearing constraint_constructor
################################################################

def epicyclic_gearing_constraint_constructor(ai_parser, ai_variant = 0):
  """
  Add arguments relative to the epicyclic_gearing design
  """
  r_parser = ai_parser
  ### structure
  r_parser.add_argument('--sun_gear_tooth_nb','--sgn', action='store', type=int, default=19,
    help="Set the number of gear-teeth of the sun-gear. Default: 19")
  r_parser.add_argument('--planet_gear_tooth_nb','--pgn', action='store', type=int, default=31,
    help="Set the number of gear-teeth of the planet-gear. Default: 31")
  r_parser.add_argument('--planet_nb','--pn', action='store', type=int, default=0,
    help="Set the number of planets. If equal to zero, the maximum possible number of planets is set. Default: 0")
  ### gear
  r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=1.0,
    help="Set the module of the sun, planet and annulus gear. Default: 1.0")
  r_parser.add_argument('--gear_router_bit_radius','--grr', action='store', type=float, default=0.1,
    help="Set the router_bit radius used to create the gear hollow of the first gear_profile. Default: 0.1")
  r_parser.add_argument('--gear_tooth_resolution','--gtr', action='store', type=int, default=2,
    help="It sets the number of segments of the gear involute. Default: 2")
  r_parser.add_argument('--gear_skin_thickness','--gst', action='store', type=float, default=0.0,
    help="Add or remove radial thickness on the gear involute to compensate the fabrication process. Default: 0.0")
  r_parser.add_argument('--gear_addendum_dedendum_parity_slack','--gadps', action='store', type=float, default=0.0,
    help="Decrease the gear_addendum_dedendum_parity to add some slack. Default: 0.0")
  r_parser.add_argument('--gearring_dedendum_to_hollow_pourcentage','--gdthp', action='store', type=float, default=0.0,
    help="Decrease the dedendum height pourcentage and increase the gear-hollow height pourcentage of the gearring. Use it with large gear_skin_thickness or gear_router_bit_radius. Default: 0.0")
  r_parser.add_argument('--gear_addendum_height_pourcentage','--gadhp', action='store', type=float, default=100.0,
    help="Set the gear_addendum_height_pourcentage of the sun-gear, planet-gear and annulus-gear. Use it to compensate gear_skin_thickness. Default: 100.0")
  ### sun-gear
  r_parser.add_argument('--sun_axle_type','--sat', action='store', default='circle',
    help="Select the type of axle for the sun-gear. Possible values: 'none', 'circle' and 'rectangle'. Default: 'circle'")
  r_parser.add_argument('--sun_axle_x_width','--saxw', action='store', type=float, default=3.0,
    help="Set the axle cylinder diameter or the axle rectangle x-width of the sun-gear. Default: 3.0")
  r_parser.add_argument('--sun_axle_y_width','--sayw', action='store', type=float, default=3.0,
    help="Set the axle rectangle y-width of the sun-gear. Default: 3.0")
  #r_parser.add_argument('--sun_axle_diameter','--sad', action='store', type=float, default=0.0,
  #  help="Set the diameter of the sun-gear cylindrical axle. Default: 0.0")
  r_parser.add_argument('--sun_crenel_nb','--scn', action='store', type=int, default=0,
    help="Set the number of sun-crenels. If equal to zero, no sun-crenel is created. Default: 0")
  r_parser.add_argument('--sun_crenel_tooth_align','--scta', action='store', type=int, default=0,
    help="Set sun-crenel aligned with teeth. Incompatible with sun_crenel_nb. Default: 0")
  r_parser.add_argument('--sun_crenel_type','--sct', action='store', default='rectangle',
    help="Select the type of crenel for the sun-gear. Possible values: 'rectangle' or 'circle'. Default: 'rectangle'")
  r_parser.add_argument('--sun_crenel_mark_nb','--scmn', action='store', type=int, default=0,
    help="Set the number of crenels that must be marked on the sun-gear. Default: 0")
  r_parser.add_argument('--sun_crenel_diameter','--scd', action='store', type=float, default=0.0,
    help="Set the diameter of the positioning circle for the sun-crenel. Default: 0.0")
  r_parser.add_argument('--sun_crenel_width','--scw', action='store', type=float, default=4.0,
    help="Set the width of the sun-crenel. Default: 4.0")
  r_parser.add_argument('--sun_crenel_height','--sch', action='store', type=float, default=2.0,
    help="Set the height of the sun-crenel. Default: 2.0")
  r_parser.add_argument('--sun_crenel_router_bit_radius','--scrbr', action='store', type=float, default=0.1,
    help="Set the router_bit radius for the sun-crenel. Default: 0.1")
  ### planet-gear
  r_parser.add_argument('--planet_axle_diameter','--pad', action='store', type=float, default=0.0,
    help="Set the diameter of the planet-gear cylindrical axle. Default: 0.0")
  r_parser.add_argument('--planet_crenel_nb','--pcn', action='store', type=int, default=0,
    help="Set the number of planet-crenels. If equal to zero, no planet-crenel is created. Default: 0")
  r_parser.add_argument('--planet_crenel_tooth_align','--pcta', action='store', type=int, default=0,
    help="Set planet-crenel aligned with teeth. Incompatible with planet_crenel_nb. Default: 0")
  r_parser.add_argument('--planet_crenel_type','--pct', action='store', default='rectangle',
    help="Select the type of crenel for the planet-gear. Possible values: 'rectangle' or 'circle'. Default: 'rectangle'")
  r_parser.add_argument('--planet_crenel_mark_nb','--pcmn', action='store', type=int, default=0,
    help="Set the number of crenels that must be marked on the planet-gear. Default: 0")
  r_parser.add_argument('--planet_crenel_diameter','--pcd', action='store', type=float, default=0.0,
    help="Set the diameter of the positioning circle for the planet-crenel. Default: 0.0")
  r_parser.add_argument('--planet_crenel_width','--pcw', action='store', type=float, default=4.0,
    help="Set the width of the planet-crenel. Default: 4.0")
  r_parser.add_argument('--planet_crenel_height','--pch', action='store', type=float, default=2.0,
    help="Set the height of the planet-crenel. Default: 2.0")
  r_parser.add_argument('--planet_crenel_router_bit_radius','--pcrbr', action='store', type=float, default=0.1,
    help="Set the router_bit radius for the planet-crenel. Default: 0.1")
  ### planet gear carrier
  r_parser.add_argument('--carrier_central_diameter','--ccd', action='store', type=float, default=0.0,
    help="Set the diameter of the outline of the central part of the planet-carrier. If equal to 0.0, set 1.1*sun_diameter. Default: 0.0")
  r_parser.add_argument('--carrier_leg_diameter','--cld', action='store', type=float, default=0.0,
    help="Set the diameter of the outline of the leg part of the planet-carrier. If equal to 0.0, set 0.7*planet_diameter. Default: 0.0")
  r_parser.add_argument('--carrier_peripheral_disable','--crd', action='store_true', default=False,
    help='Disable the planet-carrier paripheral ring and rear_planet_carrier. Default: False')
  r_parser.add_argument('--carrier_hollow_disable','--chd', action='store_true', default=False,
    help='Disable the carrier-hollow of the front_planet_carrier. Default: False')
  r_parser.add_argument('--carrier_peripheral_external_diameter','--cped', action='store', type=float, default=0.0,
    help="Set the diameter of the outline of the additional circle around the planet-carrier. If equal to 0, set sun_planet_length+0.5*carrier_leg_diameter. Default: 0.0")
  r_parser.add_argument('--carrier_peripheral_internal_diameter','--cpid', action='store', type=float, default=0.0,
    help="Set the internal diameter of the additional circle around the planet-carrier. If equal to 0, set sun_planet_length-0.25*carrier_leg_diameter. Default: 0.0")
  r_parser.add_argument('--carrier_leg_middle_diameter','--clmd', action='store', type=float, default=0.0,
    help="Set the diameter of the outline of the leg part of the planet-carrier. If equal to 0.0, set 1.2*planet_diameter. Default: 0.0")
  r_parser.add_argument('--carrier_smoothing_radius','--csr', action='store', type=float, default=0.0,
    help="Set the router_bit radius for the planet-carrier. If equal to 0, set 0.2*carrier_leg_diameter. Default: 0.0")
  #r_parser.add_argument('--carrier_central_hole_diameter','--cchd', action='store', type=float, default=10.0,
  #  help="Set the diameter of the central hole of the planet-carrier. Default: 10.0")
  r_parser.add_argument('--carrier_leg_hole_diameter','--clhd', action='store', type=float, default=10.0,
    help="Set the diameter of the leg hole of the planet-carrier. Default: 10.0")
  ## carrier peripheral crenel
  r_parser.add_argument('--carrier_crenel_width','--ccw', action='store', type=float, default=4.0,
    help="Set the width of the carrier-crenel. Default: 4.0")
  r_parser.add_argument('--carrier_crenel_height','--cch', action='store', type=float, default=2.0,
    help="Set the height of the carrier-crenel. Default: 2.0")
  r_parser.add_argument('--carrier_crenel_router_bit_radius','--ccrbr', action='store', type=float, default=0.1,
    help="Set the router_bit radius for the carrier-crenel. Default: 0.1")
  r_parser.add_argument('--carrier_hole_position_diameter','--cchpd', action='store', type=float, default=0.0,
    help="Set the diameter of the position circle of the carrier-crenel-holes. Default: 0.0")
  r_parser.add_argument('--carrier_hole_diameter','--cchd', action='store', type=float, default=0.0,
    help="Set the diameter of the carrier-crenel-holes. If equal zero, no carrier-crenel-hole are generated. Default: 0.0")
  r_parser.add_argument('--carrier_double_hole_length','--ccdhl', action='store', type=float, default=0.0,
    help="Set the length between of the double-carrier-crenel-holes. If equal zero, a single carrier-crenel-hole is generated. Default: 0.0")
  ## planet_carrier_angle
  r_parser.add_argument('--planet_carrier_angle','--pca', action='store', type=float, default=0.0,
    help="Set the initial angle of the planet carrier. It impacts the initial sun-gear angle. Default: 0.0")
  ### annulus: inherit dictionary entries from gearring
  i_gearring = gearring.gearring()
  r_parser = i_gearring.get_constraint_constructor()(r_parser, 1)
  #### side-cover
  ### input-gearwheel
  r_parser.add_argument('--input_gearwheel_tooth_nb','--igtn', action='store', type=int, default=0,
    help="Set the number of tooth to the input gearwheel. If equal to zero, no input side-cover is generated. Default: 0")
  r_parser.add_argument('--input_gearwheel_module','--igm', action='store', type=float, default=1.0,
    help="Set the gear-module of the input gearwheel. Default: 1.0")
  r_parser.add_argument('--input_gearwheel_axle_diameter','--igad', action='store', type=float, default=0.0,
    help="Set the axle diameter of the input gearwheel. If equal to zero, no axel is created. Default: 0.0")
  r_parser.add_argument('--input_gearwheel_crenel_number','--igcn', action='store', type=int, default=0,
    help="Set the number of circle-crenels of the input gearwheel. If equal to zero, no axel is created. Default: 0")
  r_parser.add_argument('--input_gearwheel_crenel_position_diameter','--igcpd', action='store', type=float, default=0.0,
    help="Set the diameter of the circle to place the circle-crenels of the input gearwheel. Default: 0.0")
  r_parser.add_argument('--input_gearwheel_crenel_diameter','--igcd', action='store', type=float, default=0.0,
    help="Set the diameter of the circle-crenels of the input gearwheel. Default: 0.0")
  r_parser.add_argument('--input_gearwheel_crenel_angle','--igca', action='store', type=float, default=0.0,
    help="Set the angle position of the first circle-crenels of the input gearwheel. Default: 0.0")
  r_parser.add_argument('--input_cover_extra_space','--ices', action='store', type=float, default=0.0,
    help="Set the extra-space between the radius of the annulus-holder and the input-shaft-cylinder. Default: 0.0")
  ### output-gearwheel
  r_parser.add_argument('--output_gearwheel_tooth_nb','--ogtn', action='store', type=int, default=0,
    help="Set the number of tooth to the output gearwheel. If equal to zero, no output side-cover is generated. Default: 0")
  r_parser.add_argument('--output_gearwheel_module','--ogm', action='store', type=float, default=1.0,
    help="Set the gear-module of the output gearwheel. Default: 1.0")
  r_parser.add_argument('--output_gearwheel_axle_diameter','--ogad', action='store', type=float, default=0.0,
    help="Set the axle diameter of the output gearwheel. If equal to zero, no axel is created. Default: 0.0")
  r_parser.add_argument('--output_gearwheel_crenel_number','--ogcn', action='store', type=int, default=0,
    help="Set the number of circle-crenels of the output gearwheel. If equal to zero, no axel is created. Default: 0")
  r_parser.add_argument('--output_gearwheel_crenel_position_diameter','--ogcpd', action='store', type=float, default=0.0,
    help="Set the diameter of the circle to place the circle-crenels of the output gearwheel. Default: 0.0")
  r_parser.add_argument('--output_gearwheel_crenel_diameter','--ogcd', action='store', type=float, default=0.0,
    help="Set the diameter of the circle-crenels of the output gearwheel. Default: 0.0")
  r_parser.add_argument('--output_gearwheel_crenel_angle','--ogca', action='store', type=float, default=0.0,
    help="Set the angle position of the first circle-crenels of the output gearwheel. Default: 0.0")
  r_parser.add_argument('--output_cover_extra_space','--oces', action='store', type=float, default=0.0,
    help="Set the extra-space between the radius of the annulus-holder and the output-shaft-cylinder. Default: 0.0")
  ### top : axle-lid
  r_parser.add_argument('--top_clearance_diameter','--tcld', action='store', type=float, default=0.0,
    help="Set the diameter of the clearence cylinder for the input and output gearwheel. If equal to 0.0, set to a bit more than the biggest gearwheel. Default: 0.0")
  r_parser.add_argument('--top_axle_hole_diameter','--tahd', action='store', type=float, default=0.0,
    help="Set the diameter of the axle hole of the top-axle-lid. If equal to 0.0, set to the sun-gear axle width. Default: 0.0")
  r_parser.add_argument('--top_central_diameter','--tced', action='store', type=float, default=0.0,
    help="Set the diameter of the central-circle of the top-axle-lid. If equal to 0.0, set to three times the sun-gear axle width. Default: 0.0")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1,
    help="Set the minimum router_bit radius of the epicyclic-gearing. Default: 0.1")
  r_parser.add_argument('--gear_profile_height','--gwh', action='store', type=float, default=10.0,
    help="Set the height of the linear extrusion of the first gear_profile. Default: 10.0")
  # return
  return(r_parser)

################################################################
# constraint conversion
################################################################

def annulus_gearring_constraint(c):
  """ convert the epicyclic_gearing constraint into gearring constraint
  """
  gr_c = {}
  gr_c['gear_tooth_nb']               = c['annulus_gear_tooth_nb']
  gr_c['second_gear_tooth_nb']        = c['planet_gear_tooth_nb']
  gr_c['gear_base_diameter']          = float((c['smallest_gear_tooth_nb']-2)*c['gear_module']*c['annulus_gear_tooth_nb'])/c['smallest_gear_tooth_nb']
  gr_c['gear_module']                 = c['gear_module']
  gr_c['gear_addendum_height_pourcentage']  = c['gear_addendum_height_pourcentage']
  gr_c['gear_dedendum_height_pourcentage']  = 100.0 - c['gearring_dedendum_to_hollow_pourcentage']
  gr_c['gear_hollow_height_pourcentage']    = 25.0 + c['gearring_dedendum_to_hollow_pourcentage']
  gr_c['gear_router_bit_radius']      = c['gear_router_bit_radius']
  gr_c['gear_tooth_resolution']       = c['gear_tooth_resolution']
  gr_c['gear_skin_thickness']         = c['gear_skin_thickness']
  gr_c['gear_addendum_dedendum_parity']         = c['addendum_dedendum_parity']
  gr_c['second_gear_addendum_dedendum_parity']  = c['addendum_dedendum_parity']
  gr_c['holder_diameter']             = c['holder_diameter']
  gr_c['holder_crenel_number']        = c['holder_crenel_number']
  gr_c['holder_position_angle']       = c['holder_position_angle']
  gr_c['holder_hole_position_radius'] = c['holder_hole_position_radius']
  gr_c['holder_hole_diameter']        = c['holder_hole_diameter']
  gr_c['holder_hole_mark_nb']         = c['holder_hole_mark_nb']
  gr_c['holder_double_hole_diameter'] = c['holder_double_hole_diameter']
  gr_c['holder_double_hole_length']   = c['holder_double_hole_length']
  gr_c['holder_double_hole_position'] = c['holder_double_hole_position']
  gr_c['holder_double_hole_mark_nb']  = c['holder_double_hole_mark_nb']
  gr_c['holder_crenel_position']      = c['holder_crenel_position']
  gr_c['holder_crenel_height']        = c['holder_crenel_height']
  gr_c['holder_crenel_width']         = c['holder_crenel_width']
  gr_c['holder_crenel_skin_width']    = c['holder_crenel_skin_width']
  gr_c['holder_hole_B_diameter']      = c['holder_hole_B_diameter']
  gr_c['holder_crenel_B_position']    = c['holder_crenel_B_position']
  gr_c['holder_hole_B_crenel_list']   = c['holder_hole_B_crenel_list']
  gr_c['holder_crenel_router_bit_radius'] = c['holder_crenel_router_bit_radius']
  gr_c['holder_smoothing_radius']     = c['holder_smoothing_radius']
  gr_c['cnc_router_bit_radius']       = c['cnc_router_bit_radius']
  gr_c['gear_profile_height']         = c['gear_profile_height']
  gr_c['center_position_x']                   = 0.0
  gr_c['center_position_y']                   = 0.0
  gr_c['gear_initial_angle']                  = 0.0
  gr_c['second_gear_position_angle']          = 0.0
  gr_c['second_gear_additional_axis_length']  = 0.0
  return(gr_c)

def planet_gearwheel_constraint(c):
  """ convert the epicyclic_gearing constraint into planet gearwheel_constraint
  """
  gw_c = {}
  gw_c['gear_tooth_nb']             = c['planet_gear_tooth_nb'] # gear-profile
  gw_c['second_gear_tooth_nb']      = c['sun_gear_tooth_nb']
  gw_c['gear_base_diameter']          = float((c['smallest_gear_tooth_nb']-2)*c['gear_module']*c['planet_gear_tooth_nb'])/c['smallest_gear_tooth_nb']
  gw_c['gear_addendum_height_pourcentage']  = c['gear_addendum_height_pourcentage']
  gw_c['gear_module']               = c['gear_module']
  gw_c['gear_router_bit_radius']    = c['gear_router_bit_radius']
  gw_c['gear_tooth_resolution']     = c['gear_tooth_resolution']
  gw_c['gear_skin_thickness']       = c['gear_skin_thickness']
  gw_c['gear_addendum_dedendum_parity']         = c['addendum_dedendum_parity']
  gw_c['second_gear_addendum_dedendum_parity']  = c['addendum_dedendum_parity']
  gw_c['axle_type']                 = 'none' # axle
  if(c['planet_axle_diameter']>0):
    gw_c['axle_type']               = 'circle'
  gw_c['axle_x_width']              = c['planet_axle_diameter']
  gw_c['axle_router_bit_radius']    = c['planet_crenel_rbr']
  gw_c['crenel_diameter']           = c['planet_crenel_diameter'] # crenel
  gw_c['crenel_number']             = c['planet_crenel_nb']
  gw_c['crenel_type']               = c['planet_crenel_type']
  gw_c['crenel_mark_nb']            = c['planet_crenel_mark_nb']
  gw_c['crenel_angle']              = 0
  gw_c['crenel_tooth_align']        = c['planet_crenel_tooth_align']
  gw_c['crenel_width']              = c['planet_crenel_width']
  gw_c['crenel_height']             = c['planet_crenel_height']
  gw_c['crenel_router_bit_radius']  = c['planet_crenel_router_bit_radius']
  gw_c['wheel_hollow_leg_number']   = 0 # wheel-hollow
  gw_c['cnc_router_bit_radius']     = c['cnc_router_bit_radius'] # general
  gw_c['gear_profile_height']       = c['gear_profile_height']
  planet_angle = 2*math.pi/c['planet_nb']
  gw_c_list = []
  for i in range(c['planet_nb']):
    gw_c['center_position_x']                   = 0.0 + c['sun_planet_length'] * math.cos(i*planet_angle + c['first_planet_position_angle'])
    gw_c['center_position_y']                   = 0.0 + c['sun_planet_length'] * math.sin(i*planet_angle + c['first_planet_position_angle'])
    gw_c['gear_initial_angle']                  = 0.0
    gw_c['second_gear_position_angle']          = i*planet_angle + c['first_planet_position_angle'] + math.pi
    gw_c['second_gear_additional_axis_length']  = 0.0
    gw_c_list.append(gw_c.copy())
  # compute the planet's gear_initial_angle
  i_gear_profile = gear_profile.gear_profile()
  gp_c = annulus_gearring_constraint(c)
  gp_c['gear_type'] = 'i'
  gp_c['second_gear_type'] = 'e'
  for i in range(c['planet_nb']):
    gp_c['second_gear_position_angle'] = i*planet_angle + c['first_planet_position_angle']
    i_gear_profile.apply_external_constraint(gp_c)
    gear_profile_parameters = i_gear_profile.get_constraint() # get the planet angle positions
    gw_c_list[i]['gear_initial_angle'] = gear_profile_parameters['second_positive_initial_angle']
  return(gw_c_list)

def sun_gearwheel_constraint(c):
  """ convert the epicyclic_gearing constraint into sun gearwheel_constraint
  """
  ### precision
  radian_epsilon = math.pi/1000
  gw_c = {}
  gw_c['gear_tooth_nb']             = c['sun_gear_tooth_nb'] # gear-profile
  gw_c['second_gear_tooth_nb']      = c['planet_gear_tooth_nb']
  gw_c['gear_base_diameter']          = float((c['smallest_gear_tooth_nb']-2)*c['gear_module']*c['sun_gear_tooth_nb'])/c['smallest_gear_tooth_nb']
  gw_c['gear_module']               = c['gear_module']
  gw_c['gear_addendum_height_pourcentage']  = c['gear_addendum_height_pourcentage']
  gw_c['gear_router_bit_radius']    = c['gear_router_bit_radius']
  gw_c['gear_tooth_resolution']     = c['gear_tooth_resolution']
  gw_c['gear_skin_thickness']       = c['gear_skin_thickness']
  gw_c['gear_addendum_dedendum_parity']         = c['addendum_dedendum_parity']
  gw_c['second_gear_addendum_dedendum_parity']  = c['addendum_dedendum_parity']
  gw_c['axle_type']                 = c['sun_axle_type'] # axle
  gw_c['axle_x_width']              = c['sun_axle_x_width']
  gw_c['axle_y_width']              = c['sun_axle_y_width']
  gw_c['axle_router_bit_radius']    = c['sun_crenel_rbr']
  gw_c['crenel_diameter']           = c['sun_crenel_diameter'] # crenel
  gw_c['crenel_number']             = c['sun_crenel_nb']
  gw_c['crenel_type']               = c['sun_crenel_type']
  gw_c['crenel_mark_nb']            = c['sun_crenel_mark_nb']
  gw_c['crenel_angle']              = 0
  gw_c['crenel_tooth_align']        = c['sun_crenel_tooth_align']
  gw_c['crenel_width']              = c['sun_crenel_width']
  gw_c['crenel_height']             = c['sun_crenel_height']
  gw_c['crenel_router_bit_radius']  = c['sun_crenel_rbr']
  gw_c['wheel_hollow_leg_number']   = 0 # wheel-hollow
  gw_c['cnc_router_bit_radius']     = c['cnc_router_bit_radius'] # general
  gw_c['gear_profile_height']       = c['gear_profile_height']
  gw_c['center_position_x']                   = 0.0
  gw_c['center_position_y']                   = 0.0
  gw_c['gear_initial_angle']                  = 0.0
  gw_c['second_gear_position_angle']          = 0.0
  gw_c['second_gear_additional_axis_length']  = 0.0
  # compute the sun angle position
  i_gear_profile = gear_profile.gear_profile()
  pg_c_list = planet_gearwheel_constraint(c)
  gp_c = {}
  gp_c['gear_type'] = 'e'
  gp_c['second_gear_type'] = 'e'
  sun_angle_position = []
  for i in range(c['planet_nb']):
    gp_c.update(pg_c_list[i])
    gear_profile_parameters = i_gear_profile.apply_external_constraint(gp_c) # get the sun angle positions
    sun_angle_position.append(gear_profile_parameters['second_positive_initial_angle'])
  g2_pi_module_angle = gear_profile_parameters['second_pi_module_angle']
  # check the sun angle position
  #tooth_check = (c['sun_gear_tooth_nb'] + c['annulus_gear_tooth_nb'])%c['planet_nb']
  tooth_check = (2*(c['sun_gear_tooth_nb'] + c['planet_gear_tooth_nb'])) % c['planet_nb']
  if(tooth_check!=0):
    print("WARN418: Warning, tooth_check {:d} is different from 0.".format(tooth_check))
    #print("tooth_check = (sun_nb {:d} + annulus_nb {:d}) % planet_nb {:d}".format(c['sun_gear_tooth_nb'], c['annulus_gear_tooth_nb'], c['planet_nb']))
    print("tooth_check = (2*(sun_nb {:d} + planet_nb {:d})) % planet_nb {:d}".format(c['sun_gear_tooth_nb'], c['planet_gear_tooth_nb'], c['planet_nb']))
  for i in range(c['planet_nb']):
    a0_ai_diff = math.fmod(sun_angle_position[i]-sun_angle_position[0]+5.5*g2_pi_module_angle, g2_pi_module_angle) - 0.5*g2_pi_module_angle
    if(abs(a0_ai_diff)>radian_epsilon):
      print("ERR414: Error, the i {:d} sun_angle_position {:0.5f} differ from the 0 sun_angle_position {:0.5f} with g2_pi_module_angle {:0.8f}".format(i, sun_angle_position[i], sun_angle_position[0], g2_pi_module_angle))
      print("dbg417: a0_ai_diff {:0.8f}".format(a0_ai_diff))
      sys.exit(2)
  gw_c['gear_initial_angle'] = sun_angle_position[0]
  return(gw_c)

################################################################
# epicyclic_gearing constraint_check
################################################################

def epicyclic_gearing_constraint_check(c):
  """ check the epicyclic_gearing constraint c and set the dynamic default values
  """
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  ## get the router_bit_radius
  if(c['cnc_router_bit_radius']>c['gear_router_bit_radius']):
    c['gear_router_bit_radius'] = c['cnc_router_bit_radius']
  c['sun_crenel_rbr'] = c['sun_crenel_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['sun_crenel_rbr']):
    c['sun_crenel_rbr'] = c['cnc_router_bit_radius']
  c['planet_crenel_rbr'] = c['planet_crenel_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['planet_crenel_rbr']):
    c['planet_crenel_rbr'] = c['cnc_router_bit_radius']
  c['carrier_sr'] = c['carrier_smoothing_radius']
  if(c['cnc_router_bit_radius']>c['carrier_sr']):
    c['carrier_sr'] = c['cnc_router_bit_radius']
  c['carrier_crenel_rbr'] = c['carrier_crenel_router_bit_radius']
  if(c['cnc_router_bit_radius']>c['carrier_crenel_rbr']):
    c['carrier_crenel_rbr'] = c['cnc_router_bit_radius']
  ## gearring_dedendum_to_hollow_pourcentage
  if((c['gearring_dedendum_to_hollow_pourcentage']>=100.0)or(c['gearring_dedendum_to_hollow_pourcentage']<0)):
    print("ERR277: Error, gearring_dedendum_to_hollow_pourcentage {:0.3f} must be set between 0.0% and 100.0%".format(c['gearring_dedendum_to_hollow_pourcentage']))
    sys.exit(2)
  ## tooth number
  c['annulus_gear_tooth_nb'] = c['sun_gear_tooth_nb'] + 2 * c['planet_gear_tooth_nb']
  c['smallest_gear_tooth_nb'] = min(c['sun_gear_tooth_nb'], c['planet_gear_tooth_nb'])
  ## maximal planet number
  # angle NOM
  NOM = 2*math.asin(1/(1+(float(c['sun_gear_tooth_nb'])/c['planet_gear_tooth_nb'])))
  security_coef = 1.1
  c['planet_number_max'] = int(2*math.pi/(NOM*security_coef))
  c['planet_nb'] = c['planet_nb']
  if(c['planet_nb']==0):
    c['planet_nb'] = c['planet_number_max']
  if(c['planet_nb']>c['planet_number_max']):
    print("ERR270: Error, planet_nb {:d} is bigger than planet_number_max {:d}".format(c['planet_nb'], c['planet_number_max']))
    sys.exit(2)
  c['epicyclic_gearing_ratio'] = float(c['sun_gear_tooth_nb'])/(c['sun_gear_tooth_nb']+c['annulus_gear_tooth_nb'])
  ## gear_addendum_dedendum_parity_slack
  if((c['gear_addendum_dedendum_parity_slack']<0)or(c['gear_addendum_dedendum_parity_slack']>30)):
    print("ERR274: Error, gear_addendum_dedendum_parity_slack {:0.3f} is out of the range 0..30".format(c['gear_addendum_dedendum_parity_slack']))
    sys.exit(2)
  c['addendum_dedendum_parity'] = 50.0-c['gear_addendum_dedendum_parity_slack']/2.0
  c['first_planet_position_angle'] = c['planet_carrier_angle']
  c['sun_planet_length'] = c['gear_module']*(c['sun_gear_tooth_nb']+c['planet_gear_tooth_nb'])/2.0
  #### gear parameter preparation
  c['gr_c'] = annulus_gearring_constraint(c)
  c['pg_c_list'] = planet_gearwheel_constraint(c)
  c['sg_c'] = sun_gearwheel_constraint(c)
  #print("dbg456: gr_c:", c['gr_c'])
  #print("dbg457: pg_c_list:", c['pg_c_list'])
  #print("dbg458: sg_c:", c['sg_c'])

  #### epicyclic_gearing construction
  i_annulus_gearring = gearring.gearring(c['gr_c'])
  holder_parameters = i_annulus_gearring.get_constraint()
  #holder_crenel_half_width = holder_parameters['holder_crenel_half_width']
  #holder_crenel_half_angle = holder_parameters['holder_crenel_half_angle']
  #holder_smoothing_radius = holder_parameters['holder_smoothing_radius']
  #holder_crenel_x_position = holder_parameters['holder_crenel_x_position']
  #holder_maximal_height_plus = holder_parameters['holder_maximal_height_plus']
  #holder_crenel_router_bit_radius = holder_parameters['holder_crenel_router_bit_radius']
  #holder_side_outer_smoothing_radius = holder_parameters['holder_side_outer_smoothing_radius']
  #holder_hole_position_radius = holder_parameters['holder_hole_position_radius']
  #holder_hole_radius = holder_parameters['holder_hole_radius']
  #holder_double_hole_diameter = holder_parameters['holder_double_hole_diameter']
  #holder_double_hole_length = holder_parameters['holder_double_hole_length']
  #holder_double_hole_position = holder_parameters['holder_double_hole_position']
  #holder_double_hole_mark_nb = holder_parameters['holder_double_hole_mark_nb']
  #holder_double_hole_position_radius = holder_parameters['holder_double_hole_position_radius']
  #holder_maximal_radius = holder_parameters['holder_maximal_radius']
  c['holder_radius'] = holder_parameters['holder_radius']

  ##### planet-carrier
  ## set the default value
  c['carrier_central_radius'] = c['carrier_central_diameter']/2.0
  if(c['carrier_central_radius']==0):
    c['carrier_central_radius'] = 1.1*(c['sun_gear_tooth_nb']+2)*c['gear_module']/2.0
  c['carrier_leg_radius'] =  c['carrier_leg_diameter']/2.0
  if(c['carrier_leg_radius']==0):
    c['carrier_leg_radius'] = 0.7*(c['planet_gear_tooth_nb']-2)*c['gear_module']/2.0
  c['carrier_peripheral_external_radius'] = c['carrier_peripheral_external_diameter']/2.0
  if(c['carrier_peripheral_external_radius']==0):
    c['carrier_peripheral_external_radius'] = c['sun_planet_length'] + c['carrier_leg_radius']
  c['carrier_peripheral_internal_radius'] = c['carrier_peripheral_internal_diameter']/2.0
  if(c['carrier_peripheral_internal_radius']==0):
    c['carrier_peripheral_internal_radius'] = c['sun_planet_length'] - 0.3 * c['carrier_leg_radius']
  c['carrier_leg_middle_radius'] = c['carrier_leg_middle_diameter']/2.0
  if(c['carrier_leg_middle_radius']==0):
    c['carrier_leg_middle_radius'] = 1.2*(c['planet_gear_tooth_nb']+2)*c['gear_module']/2.0
  c['carrier_sr'] = c['carrier_smoothing_radius'] # overwrite the previous check, so must be check again
  if(c['carrier_sr']==0):
    c['carrier_sr'] = 0.2*(c['planet_gear_tooth_nb']+2)*c['gear_module']/2.0
  c['carrier_leg_hole_radius'] = c['carrier_leg_hole_diameter']/2.0
  c['carrier_hole_position_radius'] = c['carrier_hole_position_diameter']/2.0
  if(c['carrier_hole_position_radius']==0):
    c['carrier_hole_position_radius'] = ((c['sun_planet_length']+c['carrier_leg_hole_radius'])+(c['carrier_peripheral_external_radius']-c['carrier_crenel_height']))/2.0
  c['carrier_hole_radius'] = c['carrier_hole_diameter']/2.0
  ## parameter check
  if(c['cnc_router_bit_radius']>c['carrier_sr']):
    c['carrier_sr'] = c['cnc_router_bit_radius']
  #if(c['carrier_central_hole_diameter']>c['carrier_central_diameter']):
  #  print("ERR443: Error, carrier_central_hole_diameter {:0.3f} is bigger than carrier_central_diameter {:0.3f}".format(c['carrier_central_hole_diameter'], c['carrier_central_diameter']))
  #  sys.exit(2)
  if(c['carrier_leg_hole_radius']>c['carrier_leg_radius']):
    print("ERR446: Error, carrier_leg_hole_radius {:0.3f} is bigger than carrier_leg_radius {:0.3f}".format(c['carrier_leg_hole_radius'], c['carrier_leg_radius']))
    sys.exit(2)
  if(c['carrier_peripheral_internal_radius']>c['sun_planet_length']):
    print("ERR448: Error, carrier_peripheral_internal_radius {:0.3f} is bigger than sun_planet_length {:0.3f}".format(c['carrier_peripheral_internal_radius'], c['sun_planet_length']))
    sys.exit(2)
  if(c['carrier_peripheral_internal_radius']<(c['carrier_central_radius']+3*c['carrier_sr'])):
    #print("WARN455: Warning, carrier_peripheral_internal_radius {:0.3f} is too small compare to  carrier_central_radius {:0.3f} and carrier_smoothing_radius {:0.3f}".format(c['carrier_peripheral_internal_radius'], c['carrier_central_radius'], c['carrier_sr']))
    c['carrier_hollow_disable'] = True
  if(c['carrier_peripheral_external_radius']<(c['sun_planet_length']+c['carrier_leg_radius'])):
    print("WARN461: Warning, carrier_peripheral_external_radius {:0.3f} is too small compare to sun_planet_length {:0.3f} and carrier_leg_radius {:0.3f}".format(c['carrier_peripheral_external_radius'], c['sun_planet_length'], c['carrier_leg_radius']))
    sys.exit(2)
  c['carrier_crenel'] = True
  if(c['carrier_crenel_height']==0):
    c['carrier_crenel'] = False
  if(c['carrier_crenel']):
    if(c['carrier_crenel_width']<7.0*c['carrier_crenel_rbr']):
      print("ERR468: Error, carrier_crenel_width {:0.3f} is too small compare to carrier_crenel_router_bit_radius {:0.3f}".format(c['carrier_crenel_width'], c['carrier_crenel_rbr']))
      sys.exit(2)
    if(c['carrier_crenel_height']<3*c['carrier_crenel_rbr']):
      c['carrier_crenel_type'] = 2
    else:
      c['carrier_crenel_type'] = 1
  #print("dbg509: carrier_crenel_router_bit_radius {:0.3f}  carrier_crenel_type {:d}".format(c['carrier_crenel_rbr'], c['carrier_crenel_type']))
  if(c['carrier_hole_radius']>0):
    if(c['carrier_hole_position_radius']<(c['sun_planet_length']+c['carrier_leg_hole_radius']+c['carrier_hole_radius']+radian_epsilon)):
      print("ERR544: Error, carrier_hole_position_radius {:0.3f} is too small compare to sun_planet_length {:0.3f}, carrier_leg_hole_radius {:0.3f} and carrier_hole_radius {:0.3f}".format(c['carrier_hole_position_radius'], c['sun_planet_length'], c['carrier_leg_hole_radius'], c['carrier_hole_radius']))
      sys.exit(2)
    if(c['carrier_hole_position_radius']>(c['carrier_peripheral_external_radius']-c['carrier_crenel_height']-c['carrier_hole_radius']-radian_epsilon)):
      print("ERR548: Error, carrier_hole_position_radius {:0.3f} is too big compare to carrier_peripheral_external_radius {:0.3f} carrier_crenel_height {:0.3f} and carrier_hole_radius {:0.3f}".format(c['carrier_hole_position_radius'], c['carrier_peripheral_external_radius'], c['carrier_crenel_height'], c['carrier_hole_radius']))
      sys.exit(2)
  if(c['carrier_double_hole_length']<0):
    print("ERR658: Error, carrier_double_hole_length {:0.3f} should be positive".format(c['carrier_double_hole_length']))
    sys.exit(2)
  elif(c['carrier_double_hole_length']>0):
    if(c['carrier_hole_radius']==0):
      print("ERR662: Error, carrier_double_hole_length {:0.3f} is positive whereas carrier_hole_radius is set to zero".format(c['carrier_double_hole_length']))
      sys.exit(2)
  ### top (axle-lid)
  c['top_clearance_radius'] = c['top_clearance_diameter']/2.0
  if(c['top_clearance_radius'] == 0):
    c['top_clearance_radius'] = (c['carrier_peripheral_external_radius'] + c['holder_radius'])/2.0 # default value
  if(c['top_clearance_radius'] < c['carrier_peripheral_external_radius']):
    print("ERR968: Error, top_clearance_radius {:0.3f} is smaller than carrier_peripheral_external_radius {:0.3f}".format(c['top_clearance_radius'], c['carrier_peripheral_external_radius']))
    sys.exit(2)
  if(c['top_clearance_radius'] > c['holder_radius']):
    print("ERR971: Error, top_clearance_radius {:0.3f} is bigger than holder_radius {:0.3f}".format(c['top_clearance_radius'], c['holder_radius']))
    sys.exit(2)
  c['top_axle_hole_radius'] = c['top_axle_hole_diameter']/2.0
  if(c['top_axle_hole_radius'] == 0):
    if(c['sun_axle_type'] != 'circle'):
      print("WARN978: Warning, sun_axle_type {:s} is not set to circle but sun_axle_x_width {:0.3f} is used to set the top_axle_hole_diameter".format(c['sun_axle_type'], c['sun_axle_x_width']))
    c['top_axle_hole_radius'] = c['sun_axle_x_width']/2.0
  c['top_central_radius'] = c['top_central_diameter']/2.0
  if(c['top_central_radius'] == 0):
    c['top_central_radius'] = 3*c['top_axle_hole_radius']
  if(c['top_central_radius']<c['top_axle_hole_radius']):
    print("ERR984: Error, top_central_radius {:0.3f} is smaller than top_axle_hole_radius {:0.3f}".format(c['top_central_radius'], c['top_axle_hole_radius']))
    sys.exit(2)
  if(c['top_central_radius']>c['holder_radius']):
    print("ERR987: Error, top_central_radius {:0.3f} is bigger than holder_radius {:0.3f}".format(c['top_central_radius'], c['holder_radius']))
    sys.exit(2)
  ### inout_in_hole_diameter
  #c['input_axle_shaft_radius'] = (c['input_gearwheel_tooth_nb']+2)*c['input_gearwheel_module']/2.0 # no, to avoid Z-axis issue, we don't want to make this radius as small as possible, but set it to carrier_peripheral_external_radius. Nice to have: input_axle_shaft_radius < (c['annulus_gear_tooth_nb']-2)*gear_module
  #c['input_axle_shaft_radius'] = c['carrier_peripheral_external_radius']
  c['input_axle_shaft_radius'] = max((c['input_gearwheel_tooth_nb']+2)*c['input_gearwheel_module']/2.0, c['carrier_peripheral_external_radius'])
  if(c['input_axle_shaft_radius']>(c['annulus_gear_tooth_nb']-2)*c['gear_module']/2.0-radian_epsilon):
    print("WARN910: Warning, input_axle_shaft_radius {:0.3f} is too big compare to annulus_gear_tooth_nb {:d} and gear_module {:0.3f}".format(c['input_axle_shaft_radius'], c['annulus_gear_tooth_nb'], c['gear_module']))
  c['inout_in_hole_diameter'] = 2*(c['input_axle_shaft_radius']+c['input_cover_extra_space'])
  ### inout_out_hole_diameter
  #output_axle_shaft_radius = (c['output_gearwheel_tooth_nb']+2)*c['output_gearwheel_module']/2.0 # no, it's not defined by the output gearwheel
  output_axle_shaft_radius = c['carrier_peripheral_external_radius']
  c['inout_out_hole_diameter'] = 2*(output_axle_shaft_radius+c['output_cover_extra_space'])
  return(c)

################################################################
# epicyclic_gearing 2D-figures construction
################################################################

def epicyclic_gearing_2d_construction(c):
  """
  construct the 2D-figures with outlines at the A-format for the epicyclic_gearing design
  """
  ### precision
  radian_epsilon = math.pi/1000
  ## carrier_crenel_outline function
  def carrier_crenel_outline(nai_radius):
    """ create the portion of outline for the carrier-crenel centered on Ox
    """
    crenel_width_half_angle = math.asin(c['carrier_crenel_width']/(2*nai_radius))
    if(c['carrier_crenel_type']==1):
      crenel_A = [
        (0.0+nai_radius-c['carrier_crenel_height'], 0.0-c['carrier_crenel_width']/2.0, -1*c['carrier_crenel_rbr']),
        (0.0+nai_radius-c['carrier_crenel_height'], 0.0+c['carrier_crenel_width']/2.0, -1*c['carrier_crenel_rbr']),
        (0.0+nai_radius*math.cos(1*crenel_width_half_angle), 0.0+nai_radius*math.sin(1*crenel_width_half_angle), 0)]
    elif(c['carrier_crenel_type']==2):
      tmp_l = c['carrier_crenel_rbr'] * (1+math.sqrt(2))
      crenel_A = [
        (0.0+nai_radius-c['carrier_crenel_height']-1*tmp_l, 0.0-c['carrier_crenel_width']/2.0+0*tmp_l, 1*c['carrier_crenel_rbr']),
        (0.0+nai_radius-c['carrier_crenel_height']-0*tmp_l, 0.0-c['carrier_crenel_width']/2.0+1*tmp_l, 0*c['carrier_crenel_rbr']),
        (0.0+nai_radius-c['carrier_crenel_height']-0*tmp_l, 0.0+c['carrier_crenel_width']/2.0-1*tmp_l, 0*c['carrier_crenel_rbr']),
        (0.0+nai_radius-c['carrier_crenel_height']-1*tmp_l, 0.0+c['carrier_crenel_width']/2.0-0*tmp_l, 1*c['carrier_crenel_rbr']),
        (0.0+nai_radius*math.cos(1*crenel_width_half_angle), 0.0+nai_radius*math.sin(1*crenel_width_half_angle), 0)]
    return(crenel_A, crenel_width_half_angle)

  # inheritance
  i_annulus_gearring = gearring.gearring(c['gr_c'])
  annulus_figure = i_annulus_gearring.get_A_figure('gearring_fig')
  planet_figures = []
  i_planet_gearwheel = gearwheel.gearwheel()
  for i in range(c['planet_nb']):
    i_planet_gearwheel.apply_constraint(c['pg_c_list'][i])
    planet_figures.append(i_planet_gearwheel.get_A_figure('gearwheel_fig'))
  #print("dbg512: sg_c:", c['sg_c'])
  i_sun_gearwheel = gearwheel.gearwheel(c['sg_c'])
  sun_figure = i_sun_gearwheel.get_A_figure('gearwheel_fig')

  ## planet-carrier external outline
  front_planet_carrier_figure = []
  if(not c['carrier_peripheral_disable']):
    cpe_radius = c['carrier_peripheral_external_radius']
    if(c['carrier_crenel']):
      (crenel_A, crenel_width_half_angle) = carrier_crenel_outline(cpe_radius)
      carrier_peripheral_portion_angle = 2*math.pi/(2*c['planet_nb'])
      carrier_peripheral_arc_half_angle = (carrier_peripheral_portion_angle - 2 * crenel_width_half_angle)/2.0
      if(carrier_peripheral_arc_half_angle<radian_epsilon):
        print("ERR493: Error, carrier_peripheral_arc_half_angle {:0.3f} is negative or too small".format(carrier_peripheral_arc_half_angle))
        sys.exit(2)
      cp_A = [(0.0+cpe_radius*math.cos(-1*crenel_width_half_angle), 0.0+cpe_radius*math.sin(-1*crenel_width_half_angle), 0)]
      arc_middle_a = crenel_width_half_angle + carrier_peripheral_arc_half_angle
      arc_end_a = arc_middle_a + carrier_peripheral_arc_half_angle
      crenel_A.append((0.0+cpe_radius*math.cos(arc_middle_a), 0.0+cpe_radius*math.sin(arc_middle_a), 0.0+cpe_radius*math.cos(arc_end_a), 0.0+cpe_radius*math.sin(arc_end_a), 0))
      for i in range(2*c['planet_nb']):
        cp_A.extend(cnc25d_api.outline_rotate(crenel_A, 0.0, 0.0, i*carrier_peripheral_portion_angle))
      cp_A[-1] = (cp_A[-1][0], cp_A[-1][1], cp_A[0][0], cp_A[0][1], 0)
      cp_A_rotated = cnc25d_api.outline_rotate(cp_A, 0.0, 0.0, c['first_planet_position_angle'])
      #print("dbg551: cp_A_rotated:", cp_A_rotated)
      #print("dbg552: len(cp_A_rotated) {:d}".format(len(cp_A_rotated)))
      front_planet_carrier_figure.append(cp_A_rotated)
    else: # not carrier_crenel
      cpe_circle = (0.0, 0.0, cpe_radius)
      front_planet_carrier_figure.append(cpe_circle)
  else: # carrier_peripheral_disable
    # get the length ONl and the angel (JAI) = LAOa
    OKl = c['carrier_central_radius']
    AIl = c['carrier_leg_radius']
    OAl = c['sun_planet_length']
    OLl = OKl - AIl
    LAOa = math.asin(OLl/OAl)
    MONa = 0.5*math.pi/c['planet_nb']
    KONa = MONa - LAOa
    ONl = OKl/math.cos(KONa)
    # half-leg angle
    hla = math.pi/c['planet_nb']
    # one leg
    leg_A = [(ONl*math.cos(-1*hla), ONl*math.sin(-1*hla), c['carrier_sr'])]
    ta1 = -1*math.pi/2+LAOa
    leg_A.append((OAl+AIl*math.cos(ta1), AIl*math.sin(ta1), 0))
    if(c['carrier_crenel']):
      (crenel_A, crenel_width_half_angle) = carrier_crenel_outline(AIl)
      arc_half_angle = (math.pi/2 - LAOa - crenel_width_half_angle)/2.0
      if(arc_half_angle<radian_epsilon):
        print("ERR596: Error, arc_half_angle {:0.3f} is negative or too small".format(arc_half_angle))
        sys.exit(2)
      leg_A.append((OAl+AIl*math.cos(ta1+1*arc_half_angle), AIl*math.sin(ta1+1*arc_half_angle), OAl+AIl*math.cos(ta1+2*arc_half_angle), AIl*math.sin(ta1+2*arc_half_angle), 0))
      leg_A.extend(cnc25d_api.outline_shift_x(crenel_A, OAl, 1))
      leg_A.append((OAl+AIl*math.cos(-1*ta1-1*arc_half_angle), AIl*math.sin(-1*ta1-1*arc_half_angle), OAl+AIl*math.cos(-1*ta1), AIl*math.sin(-1*ta1), 0))
    else:
      arc_half_angle = (math.pi - 2*LAOa)/2.0
      leg_A.append((OAl+AIl*math.cos(ta1+1*arc_half_angle), AIl*math.sin(ta1+1*arc_half_angle), OAl+AIl*math.cos(ta1+2*arc_half_angle), AIl*math.sin(ta1+2*arc_half_angle), 0))
    # carrier without peripheral
    cwop_A = []
    for i in range(c['planet_nb']):
      cwop_A.extend(cnc25d_api.outline_rotate(leg_A, 0.0, 0.0, i*2*hla))
    cwop_A.append((cwop_A[0][0], cwop_A[0][1], 0))
    cwop_A_rotated = cnc25d_api.outline_rotate(cwop_A, 0.0, 0.0, c['first_planet_position_angle'])
    front_planet_carrier_figure.append(cwop_A_rotated)
      
  ## front planet-carrier
  # carrier_leg_hole
  leg_hole_portion = 2*math.pi/c['planet_nb']
  carrier_hole_figure = []
  if(c['carrier_leg_hole_radius']>radian_epsilon):
    for i in range(c['planet_nb']):
      tmp_a = c['first_planet_position_angle'] + i * leg_hole_portion
      carrier_hole_figure.append((0.0+c['sun_planet_length']*math.cos(tmp_a), 0.0+c['sun_planet_length']*math.sin(tmp_a), c['carrier_leg_hole_radius']))
  carrier_hole_portion = 2*math.pi/(2*c['planet_nb'])
  tmp_a2 = math.atan(c['carrier_double_hole_length']/2.0/c['carrier_hole_position_radius']) # if double carrier-crenel-hole
  carrier_hole_position_radius2 = math.sqrt(c['carrier_hole_position_radius']**2+(c['carrier_double_hole_length']/2.0)**2)
  if(c['carrier_hole_radius']>0):
    for i in range(2*c['planet_nb']):
      tmp_a = c['first_planet_position_angle'] + i * carrier_hole_portion
      if(c['carrier_double_hole_length']==0): # single crenel hole
        carrier_hole_figure.append((0.0+c['carrier_hole_position_radius']*math.cos(tmp_a), 0.0+c['carrier_hole_position_radius']*math.sin(tmp_a), c['carrier_hole_radius']))
      else: # double crenel hole
        carrier_hole_figure.append((0.0+carrier_hole_position_radius2*math.cos(tmp_a-tmp_a2), 0.0+carrier_hole_position_radius2*math.sin(tmp_a-tmp_a2), c['carrier_hole_radius']))
        carrier_hole_figure.append((0.0+carrier_hole_position_radius2*math.cos(tmp_a+tmp_a2), 0.0+carrier_hole_position_radius2*math.sin(tmp_a+tmp_a2), c['carrier_hole_radius']))
  front_planet_carrier_figure.extend(carrier_hole_figure)
  # copy for the rear_planet_carrier_figure
  front_planet_carrier_figure_copy = front_planet_carrier_figure[:]
  #print("dbg573: len(front_planet_carrier_figure_copy[0]) {:d}".format(len(front_planet_carrier_figure_copy[0])))
  # sun axle and crenel
  front_planet_carrier_figure.extend(sun_figure[1:])
  # carrier_hollow
  if((not c['carrier_peripheral_disable']) and (not c['carrier_hollow_disable'])): #todo
    pass
    #print("WARN625: planet-carrier hollow is not implemented yet!")

  ## rear planet-carrier
  rear_planet_carrier_figure = []
  if(not c['carrier_peripheral_disable']):
    rear_planet_carrier_figure.extend(front_planet_carrier_figure_copy)
    # carrier_peripheral_internal
    cl_radius = c['carrier_leg_radius']
    cpi_radius = c['carrier_peripheral_internal_radius']
    if(cpi_radius<c['sun_planet_length']-cl_radius+radian_epsilon): # simple circle case
      rear_planet_carrier_figure.append((0.0, 0.0, cpi_radius))
    else: # complex case
      # circle_intersection_angle with cosines law
      cia = math.acos((c['sun_planet_length']**2+cpi_radius**2-cl_radius**2)/(2*c['sun_planet_length']*cpi_radius))
      cia_half = cia
      arc_half = (leg_hole_portion - 2*cia_half)/2.0
      if(arc_half<radian_epsilon):
        print("ERR551: Error, rear planet-carrier arc_half {:0.3f} is negative or too small".format(arc_half))
        sys.exit(2)
      cpi_A = [(0.0+cpi_radius*math.cos(-1*cia_half), 0.0+cpi_radius*math.sin(-1*cia_half), c['carrier_sr'])]
      short_radius = c['sun_planet_length'] - cl_radius
      for i in range(c['planet_nb']):
        a1_mid = i*leg_hole_portion
        a1_end = a1_mid + cia_half
        a2_mid = a1_end + arc_half
        a2_end = a2_mid + arc_half
        cpi_A.append((0.0+short_radius*math.cos(a1_mid), 0.0+short_radius*math.sin(a1_mid), 0.0+cpi_radius*math.cos(a1_end), 0.0+cpi_radius*math.sin(a1_end), c['carrier_sr']))
        cpi_A.append((0.0+cpi_radius*math.cos(a2_mid), 0.0+cpi_radius*math.sin(a2_mid), 0.0+cpi_radius*math.cos(a2_end), 0.0+cpi_radius*math.sin(a2_end), c['carrier_sr']))
      cpi_A[-1] = (cpi_A[-1][0], cpi_A[-1][1], cpi_A[0][0], cpi_A[0][1], 0)
      cpi_A_rotated = cnc25d_api.outline_rotate(cpi_A, 0.0, 0.0, c['first_planet_position_angle'])
      rear_planet_carrier_figure.append(cpi_A_rotated)

  ## middle planet-carrier
  middle_planet_carrier_figures = []
  if(not c['carrier_peripheral_disable']):
    # distance between the centers of two consecutive planets: law of cosines
    planet_planet_length = math.sqrt(2*c['sun_planet_length']**2 - 2*c['sun_planet_length']**2*math.cos(leg_hole_portion))
    # do the carrier_leg_middle_radius circle overlap or not?
    middle_radius_intersection = False
    if(2*c['carrier_leg_middle_radius']>planet_planet_length-radian_epsilon):
      middle_radius_intersection = True
    # intersection carrier_leg_middle_radius and carrier_peripheral_external_radius from planet
    if(c['sun_planet_length']+c['carrier_leg_middle_radius']<c['carrier_peripheral_external_radius']):
      print("ERR731: Error, carrier_leg_middle_radius {:0.3f} is too small compare to sun_planet_length {:0.3f} and carrier_peripheral_external_radius {:0.3f}".format(c['carrier_leg_middle_radius'], c['sun_planet_length'], c['carrier_peripheral_external_radius']))
      sys.exit(2)
    cos_imea = (c['carrier_leg_middle_radius']**2+c['sun_planet_length']**2-c['carrier_peripheral_external_radius']**2)/(2*c['carrier_leg_middle_radius']*c['sun_planet_length'])
    if((cos_imea<-1)or(cos_imea>1)):
      print("ERR730: Error, cos_imea {:0.3f} is out of the range -1,1".format(cos_imea))
      sys.exit(2)
    imea = math.acos(cos_imea)
    # intersection carrier_leg_middle_radius and carrier_peripheral_internal_radius from planet
    imia = math.acos((c['carrier_leg_middle_radius']**2+c['sun_planet_length']**2-c['carrier_peripheral_internal_radius']**2)/(2*c['carrier_leg_middle_radius']*c['sun_planet_length']))
    if(middle_radius_intersection):
      imia_0 = (math.pi - leg_hole_portion)/2.0
      if(2*c['carrier_leg_middle_radius']<planet_planet_length+radian_epsilon): # flat triangle
        imia = imia_0
      else: # normal case
        imia = imia_0 + math.acos((planet_planet_length**2+0*c['carrier_leg_middle_radius']**2)/(2*planet_planet_length*c['carrier_leg_middle_radius']))
    pla = (imea-imia)/2.0
    if(pla<radian_epsilon):
      print("ERR628: Error, imia {:0.3f} is larger than imea {:0.3f}".format(imia, imea))
      sys.exit(2)
    # intersection carrier_leg_middle_radius and carrier_peripheral_external_radius from sun
    imefsa = math.acos((c['sun_planet_length']**2+c['carrier_peripheral_external_radius']**2-c['carrier_leg_middle_radius']**2)/(2*c['sun_planet_length']*c['carrier_peripheral_external_radius']))
    p1x = c['sun_planet_length'] * math.cos(leg_hole_portion/2.0)
    p1y = c['sun_planet_length'] * math.sin(leg_hole_portion/2.0)
    p2x = p1x
    p2y = -1*p1y
    p1a_end = leg_hole_portion/2.0 + math.pi + imia
    p2a_first = -1*p1a_end #-1*leg_hole_portion/2.0 + math.pi - imia
    pl_radius = c['carrier_leg_middle_radius']
    mrbr = c['carrier_crenel_rbr']
    mcp_A = [ (p2x+pl_radius*math.cos(p2a_first-2*pla), p2y+pl_radius*math.sin(p2a_first-2*pla), mrbr) ]
    if(c['carrier_crenel']):
      (crenel_A, crenel_width_half_angle) = carrier_crenel_outline(cpe_radius)
      carrier_peripheral_arc_half_angle = (leg_hole_portion - 2 * imefsa - 2 * crenel_width_half_angle)/4.0
      if(carrier_peripheral_arc_half_angle<radian_epsilon):
        print("ERR635: Error, middle carrier_peripheral_arc_half_angle {:0.3f} is negative or too small".format(carrier_peripheral_arc_half_angle))
        sys.exit(2)
      arc_middle_a = crenel_width_half_angle + carrier_peripheral_arc_half_angle
      arc_end_a = arc_middle_a + carrier_peripheral_arc_half_angle
      mcp_A.append((0.0+cpe_radius*math.cos(-1*arc_middle_a), 0.0+cpe_radius*math.sin(-1*arc_middle_a), 0.0+cpe_radius*math.cos(-1*crenel_width_half_angle), 0.0+cpe_radius*math.sin(-1*crenel_width_half_angle), 0))
      mcp_A.extend(crenel_A)
      mcp_A.append((0.0+cpe_radius*math.cos(arc_middle_a), 0.0+cpe_radius*math.sin(arc_middle_a), 0.0+cpe_radius*math.cos(arc_end_a), 0.0+cpe_radius*math.sin(arc_end_a), mrbr))
    else:
      cp_arc_half_angle = (leg_hole_portion - 2 * imefsa)/2.0
      mcp_A.append((0.0+cpe_radius*math.cos(0*cp_arc_half_angle), 0.0+cpe_radius*math.sin(0*cp_arc_half_angle), 0.0+cpe_radius*math.cos(1*cp_arc_half_angle), 0.0+cpe_radius*math.sin(1*cp_arc_half_angle), mrbr))
    mcp_A.append((p1x+pl_radius*math.cos(p1a_end+pla), p1y+pl_radius*math.sin(p1a_end+pla), p1x+pl_radius*math.cos(p1a_end), p1y+pl_radius*math.sin(p1a_end), mrbr))
    if(not middle_radius_intersection): # additional arc when not middle_radius_intersection
      #print("dbg652: middle_radius_intersection True")
      mcp_A.append((c['carrier_peripheral_internal_radius'], 0, p2x+pl_radius*math.cos(p2a_first), p2y+pl_radius*math.sin(p2a_first), mrbr))
    mcp_A.append((p2x+pl_radius*math.cos(p2a_first-pla), p2y+pl_radius*math.sin(p2a_first-pla), mcp_A[0][0], mcp_A[0][1], 0))
    #mcp_A.append((p2x+pl_radius*math.cos(p2a_first-pla), p2y+pl_radius*math.sin(p2a_first-pla), 0))
    #mcp_A.append((p2x+pl_radius*math.cos(p2a_first-2*pla), p2y+pl_radius*math.sin(p2a_first-2*pla), 0))
    #mcp_A.append((0.0+cpe_radius*math.cos(-1*arc_middle_a), 0.0+cpe_radius*math.sin(-1*arc_middle_a), 0))
    #mcp_A.append((mcp_A[0][0], mcp_A[0][1], 0))
    #mcp_A[-1] = (mcp_A[-1][0], mcp_A[-1][1], mcp_A[0][0], mcp_A[0][1], 0)
    mcp_A_rotated = cnc25d_api.outline_rotate(mcp_A, 0.0, 0.0, c['first_planet_position_angle'])
    middle_planet_carrier_outline = mcp_A_rotated
    for i in range(c['planet_nb']):
      middle_planet_carrier_figures.append( [ cnc25d_api.outline_rotate(middle_planet_carrier_outline, 0.0, 0.0, (i+0.5)*leg_hole_portion) ] )
    ## add carrier-crenel-hole
    tmp_a2 = math.atan(c['carrier_double_hole_length']/2.0/c['carrier_hole_position_radius']) # if double carrier-crenel-hole
    carrier_hole_position_radius2 = math.sqrt(c['carrier_hole_position_radius']**2+(c['carrier_double_hole_length']/2.0)**2)
    if(c['carrier_hole_radius']>0):
      for i in range(c['planet_nb']):
        ta = (i+0.5)*leg_hole_portion + c['first_planet_position_angle']
        if(c['carrier_double_hole_length']==0): # single crenel hole
          middle_planet_carrier_figures[i].append((0.0+c['carrier_hole_position_radius']*math.cos(ta), 0.0+c['carrier_hole_position_radius']*math.sin(ta), c['carrier_hole_radius']))
        else: # double crenel hole
          middle_planet_carrier_figures[i].append((0.0+carrier_hole_position_radius2*math.cos(ta-tmp_a2), 0.0+carrier_hole_position_radius2*math.sin(ta-tmp_a2), c['carrier_hole_radius']))
          middle_planet_carrier_figures[i].append((0.0+carrier_hole_position_radius2*math.cos(ta+tmp_a2), 0.0+carrier_hole_position_radius2*math.sin(ta+tmp_a2), c['carrier_hole_radius']))
  ### input cover
  input_gearwheel_figure = []
  input_axle_shaft_figure = []
  input_cover_figure = []
  input_cover_shaft_merge_figure = []
  inout_in_axle_shaft_figure = []
  inout_in_cover_shaft_merge_figure = []
  if(c['input_gearwheel_tooth_nb']>0):
    ig_c = {} # input_gearwheel
    ig_c['gear_tooth_nb']             = c['input_gearwheel_tooth_nb']
    ig_c['gear_module']               = c['input_gearwheel_module']
    ig_c['gear_router_bit_radius']    = c['gear_router_bit_radius']
    ig_c['gear_tooth_resolution']     = c['gear_tooth_resolution']
    ig_c['gear_skin_thickness']       = c['gear_skin_thickness']
    if(c['input_gearwheel_axle_diameter']>0): # axle
      ig_c['axle_type']                 = 'circle'
    else:
      ig_c['axle_type']                 = 'none'
    ig_c['axle_x_width']              = c['input_gearwheel_axle_diameter']
    ig_c['crenel_diameter']           = c['input_gearwheel_crenel_position_diameter'] # crenel
    ig_c['crenel_number']             = c['input_gearwheel_crenel_number']
    ig_c['crenel_type']               = 'circle'
    ig_c['crenel_angle']              = c['input_gearwheel_crenel_angle']
    ig_c['crenel_width']              = c['input_gearwheel_crenel_diameter']
    ig_c['wheel_hollow_leg_number']   = 0 # wheel-hollow
    ig_c['cnc_router_bit_radius']     = c['cnc_router_bit_radius'] # general
    ig_c['gear_profile_height']       = c['gear_profile_height']
    ig_c['center_position_x']                   = 0.0
    ig_c['center_position_y']                   = 0.0
    ig_c['gear_initial_angle']                  = 0.0
    i_input_gearwheel = gearwheel.gearwheel(ig_c)
    input_gearwheel_figure = i_input_gearwheel.get_A_figure('gearwheel_fig')
    ic_c = c['gr_c'].copy() # input_cover
    ic_c['gear_tooth_nb'] = 0
    ic_c['gear_primitive_diameter'] = c['inout_in_hole_diameter']
    ic_c['holder_diameter'] = 2*c['holder_radius']
    i_input_cover_gearring = gearring.gearring(ic_c)
    input_cover_figure = i_input_cover_gearring.get_A_figure('gearring_fig')
    input_axle_shaft_figure.append((0.0, 0.0, c['input_axle_shaft_radius'])) # input_axle_shaft
    input_axle_shaft_figure.extend(sun_figure[1:]) # get the axle and the crenels
    if(c['input_gearwheel_axle_diameter']==0):
      input_axle_shaft_figure.extend(input_gearwheel_figure[1:]) # get the crenels only
    else:
      input_axle_shaft_figure.extend(input_gearwheel_figure[2:]) # get the crenels only
    input_cover_shaft_merge_figure.extend(input_cover_figure) # input_cover_shaft_merge_figure
    input_cover_shaft_merge_figure.extend(input_axle_shaft_figure)
    #input_cover_shaft_merge_figure.extend(input_gearwheel_figure) # just for debug
    inout_in_axle_shaft_figure = input_axle_shaft_figure[:] # inherit outline and holes from input_axle_shaft_figure
    inout_in_axle_shaft_figure.extend(carrier_hole_figure[:]) # get the holes from the planet-carrier
    inout_in_cover_shaft_merge_figure.extend(input_cover_figure) # input_cover_shaft_merge_figure
    inout_in_cover_shaft_merge_figure.extend(inout_in_axle_shaft_figure)
  ### output cover
  output_gearwheel_figure = []
  output_axle_shaft_figure = []
  output_cover_figure = []
  output_cover_shaft_merge_figure = []
  inout_out_axle_shaft_figure = []
  inout_out_cover_shaft_merge_figure = []
  if(c['output_gearwheel_tooth_nb']>0):
    og_c = {} # output_gearwheel
    og_c['gear_tooth_nb']             = c['output_gearwheel_tooth_nb']
    og_c['gear_module']               = c['output_gearwheel_module']
    og_c['gear_router_bit_radius']    = c['gear_router_bit_radius']
    og_c['gear_tooth_resolution']     = c['gear_tooth_resolution']
    og_c['gear_skin_thickness']       = c['gear_skin_thickness']
    if(c['output_gearwheel_axle_diameter']>0): # axle
      og_c['axle_type']                 = 'circle'
    else:
      og_c['axle_type']                 = 'none'
    og_c['axle_x_width']              = c['output_gearwheel_axle_diameter']
    og_c['crenel_diameter']           = c['output_gearwheel_crenel_position_diameter'] # crenel
    og_c['crenel_number']             = c['output_gearwheel_crenel_number']
    og_c['crenel_type']               = 'circle'
    og_c['crenel_angle']              = c['output_gearwheel_crenel_angle']
    og_c['crenel_width']              = c['output_gearwheel_crenel_diameter']
    og_c['wheel_hollow_leg_number']   = 0 # wheel-hollow
    og_c['cnc_router_bit_radius']     = c['cnc_router_bit_radius'] # general
    og_c['gear_profile_height']       = c['gear_profile_height']
    og_c['center_position_x']                   = 0.0
    og_c['center_position_y']                   = 0.0
    og_c['gear_initial_angle']                  = 0.0
    i_output_gearwheel = gearwheel.gearwheel(og_c)
    output_gearwheel_figure = i_output_gearwheel.get_A_figure('gearwheel_fig')
    oc_c = c['gr_c'].copy() # output_cover
    oc_c['gear_tooth_nb'] = 0
    oc_c['gear_primitive_diameter'] = c['inout_out_hole_diameter'] #2*(output_axle_shaft_radius+c['output_cover_extra_space'])
    oc_c['holder_diameter'] = 2*c['holder_radius']
    i_output_cover_gearring = gearring.gearring(oc_c)
    output_cover_figure = i_output_cover_gearring.get_A_figure('gearring_fig')
    output_axle_shaft_figure.extend(front_planet_carrier_figure_copy) # output_axle_shaft
    if(c['output_gearwheel_axle_diameter']>0):
      output_axle_shaft_figure.extend(output_gearwheel_figure[2:]) # get the crenels only without the axle
    else:
      output_axle_shaft_figure.extend(output_gearwheel_figure[1:])
    inout_out_axle_shaft_figure = output_axle_shaft_figure[:] # inherit outline and holes from output_axle_shaft_figure
    if(c['sun_axle_type']!='circle'):
      print("WARN945: Warning, sun_axle_type {:s} is not circle but sun_axle_x_width {:0.3f} is used as axle diameter for the output shaft".format(c['sun_axle_type'], c['sun_axle_x_width']))
    output_axle_shaft_figure.append((0.0, 0.0, c['sun_axle_x_width']/2.0))
    output_cover_shaft_merge_figure.extend(output_cover_figure) # output_cover_shaft_merge_figure
    output_cover_shaft_merge_figure.extend(output_axle_shaft_figure)
    #output_cover_shaft_merge_figure.extend(output_gearwheel_figure) # just for the debug
    inout_out_axle_shaft_figure.extend(sun_figure[1:]) # get the axle and the crenels
    inout_out_cover_shaft_merge_figure.extend(output_cover_figure) # output_cover_shaft_merge_figure
    inout_out_cover_shaft_merge_figure.extend(inout_out_axle_shaft_figure)
  ### top (axle-lid)
  al_c = annulus_gearring_constraint(c)
  al_c['holder_diameter']       = 2*c['holder_radius']
  al_c['clearance_diameter']     = 2*c['top_clearance_radius']
  al_c['central_diameter']       = 2*c['top_central_radius']
  al_c['axle_hole_diameter']     = 2*c['top_axle_hole_radius']
  al_c['annulus_holder_axle_hole_diameter'] = 0.0
  # general
  al_c['cnc_router_bit_radius']  = c['cnc_router_bit_radius']
  al_c['extrusion_height']       = c['gear_profile_height']
  ## generate the axle-lid-figures
  i_axle_lid = axle_lid.axle_lid()
  i_axle_lid.apply_external_constraint(al_c)
  top_lid_plate_figure = i_axle_lid.get_A_figure('middle_lid_0_fig')
  top_lid_arc_1_figure = i_axle_lid.get_A_figure('middle_lid_1_fig')
  top_lid_arc_2_figure = i_axle_lid.get_A_figure('main_top_lid_fig')
   
  ### design output
  part_figure_list = []
  part_figure_list.append(annulus_figure) # 0
  part_figure_list.append(sun_figure)
  part_figure_list.extend(planet_figures) # +planet_nb
  part_figure_list.append(front_planet_carrier_figure)
  part_figure_list.append(rear_planet_carrier_figure)
  part_figure_list.extend(middle_planet_carrier_figures) # +planet_nb
  part_figure_list.append(input_gearwheel_figure)
  part_figure_list.append(input_axle_shaft_figure) # 5+2*planet_nb
  part_figure_list.append(input_cover_figure)
  part_figure_list.append(output_gearwheel_figure)
  part_figure_list.append(output_axle_shaft_figure)
  part_figure_list.append(output_cover_figure)
  part_figure_list.append(inout_in_axle_shaft_figure) # 10+2*planet_nb
  part_figure_list.append(inout_out_axle_shaft_figure)
  part_figure_list.append(top_lid_arc_1_figure) # 12+2*planet_nb
  part_figure_list.append(top_lid_arc_2_figure)
  part_figure_list.append(top_lid_plate_figure)
  # eg_assembly_figure: assembly flatted in one figure
  eg_assembly_figure = []
  for i in range(len(part_figure_list)):
    eg_assembly_figure.extend(part_figure_list[i])
  # eg_gear_assembly_figure: assembly of the gear only flatted in one figure
  eg_gear_assembly_figure = []
  for i in range(2+c['planet_nb']):
    eg_gear_assembly_figure.extend(part_figure_list[i])
  # eg_list_of_parts: all parts aligned flatted in one figure
  x_space = 2.5*c['annulus_gear_tooth_nb']*c['gear_module']
  eg_list_of_parts = []
  for i in range(len(part_figure_list)):
    for j in range(len(part_figure_list[i])):
      eg_list_of_parts.append(cnc25d_api.outline_shift_x(part_figure_list[i][j], i*x_space, 1))
  # middle_planet_carrier_figure
  middle_planet_carrier_figure = []
  for i in range(len(middle_planet_carrier_figures)):
    middle_planet_carrier_figure.extend(middle_planet_carrier_figures[i])
  # planet_carrier_assembly_figure
  planet_carrier_assembly_figure = []
  planet_carrier_assembly_figure.extend(front_planet_carrier_figure)
  planet_carrier_assembly_figure.extend(middle_planet_carrier_figure)
  planet_carrier_assembly_figure.extend(rear_planet_carrier_figure)
  # planet_and_carrier_assembly_figure
  planet_and_carrier_assembly_figure = []
  for i in range(len(planet_figures)):
    planet_and_carrier_assembly_figure.extend(planet_figures[i])
  planet_and_carrier_assembly_figure.extend(middle_planet_carrier_figure)
  # planet_and_rear_carrier_assembly_figure
  planet_and_rear_carrier_assembly_figure = []
  for i in range(len(planet_figures)):
    planet_and_rear_carrier_assembly_figure.extend(planet_figures[i])
  planet_and_rear_carrier_assembly_figure.extend(rear_planet_carrier_figure)
  # input_top_assembly_figure
  input_top_assembly_figure = []
  input_top_assembly_figure.extend(input_gearwheel_figure)
  input_top_assembly_figure.extend(top_lid_arc_1_figure)
  input_top_assembly_figure.extend(top_lid_arc_2_figure)
  input_top_assembly_figure.extend(top_lid_plate_figure)
  # output_top_assembly_figure
  output_top_assembly_figure = []
  output_top_assembly_figure.extend(output_gearwheel_figure)
  output_top_assembly_figure.extend(top_lid_arc_1_figure)
  output_top_assembly_figure.extend(top_lid_arc_2_figure)
  output_top_assembly_figure.extend(top_lid_plate_figure)
  ###
  r_figures = {}
  r_height = {}
  #
  r_figures['annulus_fig'] = annulus_figure
  r_height['annulus_fig'] = c['gear_profile_height']
  #
  r_figures['sun_fig'] = sun_figure
  r_height['sun_fig'] = c['gear_profile_height']
  #
  for i in range(c['planet_nb']):
    fig_id = "planet_{:d}_fig".format(i)
    r_figures['fig_id'] = planet_figures[i]
    r_height['fig_id'] = c['gear_profile_height']
  #
  r_figures['front_planet_carrier_fig'] = front_planet_carrier_figure
  r_height['front_planet_carrier_fig'] = c['gear_profile_height']
  #
  r_figures['rear_planet_carrier_fig'] = rear_planet_carrier_figure
  r_height['rear_planet_carrier_fig'] = c['gear_profile_height']
  #
  for i in range(c['planet_nb']):
    fig_id = "middle_planet_carrier_{:d}_fig".format(i)
    r_figures['fig_id'] = middle_planet_carrier_figures
    r_height['fig_id'] = c['gear_profile_height']
  #
  r_figures['input_gearwheel_fig'] = input_gearwheel_figure
  r_height['input_gearwheel_fig'] = c['gear_profile_height']
  #
  r_figures['input_axle_shaft_fig'] = input_axle_shaft_figure
  r_height['input_axle_shaft_fig'] = c['gear_profile_height']
  #
  r_figures['input_cover_fig'] = input_cover_figure
  r_height['input_cover_fig'] = c['gear_profile_height']
  #
  r_figures['output_gearwheel_fig'] = output_gearwheel_figure
  r_height['output_gearwheel_fig'] = c['gear_profile_height']
  #
  r_figures['output_axle_shaft_fig'] = output_axle_shaft_figure
  r_height['output_axle_shaft_fig'] = c['gear_profile_height']
  #
  r_figures['output_cover_fig'] = output_cover_figure
  r_height['output_cover_fig'] = c['gear_profile_height']
  #
  r_figures['inout_in_axle_shaft_fig'] = inout_in_axle_shaft_figure
  r_height['inout_in_axle_shaft_fig'] = c['gear_profile_height']
  #
  r_figures['inout_out_axle_shaft_fig'] = inout_out_axle_shaft_figure
  r_height['inout_out_axle_shaft_fig'] = c['gear_profile_height']
  #
  r_figures['top_lid_arc_1_fig'] = top_lid_arc_1_figure
  r_height['top_lid_arc_1_fig'] = c['gear_profile_height']
  #
  r_figures['top_lid_arc_2_fig'] = top_lid_arc_2_figure
  r_height['top_lid_arc_2_fig'] = c['gear_profile_height']
  #
  r_figures['top_lid_plate_fig'] = top_lid_plate_figure
  r_height['top_lid_plate_fig'] = c['gear_profile_height']
  #
  r_figures['eg_assembly_fig'] = eg_assembly_figure
  r_height['eg_assembly_fig'] = c['gear_profile_height']
  #
  r_figures['eg_gear_assembly_fig'] = eg_gear_assembly_figure
  r_height['eg_gear_assembly_fig'] = c['gear_profile_height']
  #
  r_figures['part_list'] = eg_list_of_parts
  r_height['part_list'] = c['gear_profile_height']
  #
  r_figures['middle_planet_carrier_fig'] = middle_planet_carrier_figure
  r_height['middle_planet_carrier_fig'] = c['gear_profile_height']
  #
  r_figures['planet_carrier_assembly_fig'] = planet_carrier_assembly_figure
  r_height['planet_carrier_assembly_fig'] = c['gear_profile_height']
  #
  r_figures['planet_and_carrier_assembly_fig'] = planet_and_carrier_assembly_figure
  r_height['planet_and_carrier_assembly_fig'] = c['gear_profile_height']
  #
  r_figures['planet_and_rear_carrier_assembly_fig'] = planet_and_rear_carrier_assembly_figure
  r_height['planet_and_rear_carrier_assembly_fig'] = c['gear_profile_height']
  #
  r_figures['input_top_assembly_fig'] = input_top_assembly_figure
  r_height['input_top_assembly_fig'] = c['gear_profile_height']
  #
  r_figures['output_top_assembly_fig'] = output_top_assembly_figure
  r_height['output_top_assembly_fig'] = c['gear_profile_height']
  ###
  return((r_figures, r_height))

      
################################################################
# epicyclic_gearing 3D assembly-configuration construction
################################################################

def epicyclic_gearing_3d_construction(c):
  """ construct the 3D-assembly-configurations of the epicyclic_gearing
  """
  # conf1
  epicyclic_gearing_3dconf1 = []
  epicyclic_gearing_3dconf1.append(('annulus_fig',  0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  epicyclic_gearing_3dconf1.append(('sun_fig',      0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  for i in range(c['planet_nb']):
    fig_id = "planet_{:d}_fig".format(i)
    epicyclic_gearing_3dconf1.append((fig_id,  0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  epicyclic_gearing_3dconf1.append(('front_planet_carrier_fig',   0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 7.0*c['gear_profile_height']))
  epicyclic_gearing_3dconf1.append(('rear_planet_carrier_fig',    0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, -5.0*c['gear_profile_height']))
  for i in range(c['planet_nb']):
    fig_id = "middle_planet_carrier_{:d}_fig".format(i)
    epicyclic_gearing_3dconf1.append((fig_id,  0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 5.0*c['gear_profile_height']))
  #epicyclic_gearing_3dconf1.append(('input_gearwheel_fig',      0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('input_axle_shaft_fig',     0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('input_cover_fig',          0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('output_gearwheel_fig',     0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('output_axle_shaft_fig',    0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('output_cover_fig',         0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('inout_in_axle_shaft_fig',  0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('inout_out_axle_shaft_fig', 0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('top_lid_arc_1_fig',        0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('top_lid_arc_2_fig',        0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))
  #epicyclic_gearing_3dconf1.append(('top_lid_plate_fig',        0.0, 0.0, 0.0, 0.0, c['gear_profile_height'], 'i', 'xy', 0.0, 0.0, 0.0))

  #
  r_assembly = {}
  r_slice = {}

  r_assembly['epicyclic_gearing_3dconf1'] = epicyclic_gearing_3dconf1
  hr = c['holder_radius']
  hh = c['gear_profile_height']/2.0 # half-height
  r_slice['epicyclic_gearing_3dconf1'] = (2*hr,2*hr,c['gear_profile_height'], -hr,-hr,0.0, [hh], [], [])
  #
  return((r_assembly, r_slice))


################################################################
# epicyclic_gearing simulation
################################################################

def eg_sim_planet_sun(c):
  """ define the epicyclic_gearing first simulation: planet-sun
  """
  pg_c_list = planet_gearwheel_constraint(c)
  sg_c = pg_c_list[0]
  sg_c['gear_type'] = 'i'
  sg_c['second_gear_type'] = 'e'
  # gear_profile simulation
  i_gear_profile = gear_profile.gear_profile()
  i_gear_profile.apply_external_constraint(sg_c)
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def eg_sim_annulus_planet(c):
  """ define the epicyclic_gearing second simulation: annulus-planet
  """
  sg_c = annulus_gearring_constraint(c)
  sg_c['gear_type'] = 'i'
  sg_c['second_gear_type'] = 'e'
  # gear_profile gear_profile
  i_gear_profile = gear_profile.gear_profile()
  i_gear_profile.apply_external_constraint(sg_c)
  i_gear_profile.run_simulation('gear_profile_simulation_A')
  return(1)

def epicyclic_gearing_2d_simulations():
  """ return the dictionary defining the available simulation for epicyclic_gearing
  """
  r_sim = {}
  r_sim['eg_sim_planet_sun'] = eg_sim_planet_sun
  r_sim['eg_sim_annulus_planet'] = eg_sim_annulus_planet
  return(r_sim)


################################################################
# epicyclic_gearing_info
################################################################

def epicyclic_gearing_info(c):
  """ create the text info related to the epicyclic_gearing
  """
  r_info = ""
  # eg_parameter_info
  r_info += """
sun_gear_tooth_nb:        \t{:d}
planet_gear_tooth_nb:     \t{:d}
annulus_gear_tooth_nb:    \t{:d}
smallest_gear_tooth_nb:   \t{:d}
planet_nb:                \t{:d}
planet_number_max:        \t{:d}
epicyclic_gearing_ratio:  \t{:0.3f}  1/R: {:0.3f}  1/R2: {:0.3f}  1/R3: {:0.3f}  1/R4: {:0.3f}  1/R5: {:0.3f}
""".format(c['sun_gear_tooth_nb'], c['planet_gear_tooth_nb'], c['annulus_gear_tooth_nb'], c['smallest_gear_tooth_nb'], c['planet_nb'], c['planet_number_max'], c['epicyclic_gearing_ratio'], 1.0/c['epicyclic_gearing_ratio'], 1.0/c['epicyclic_gearing_ratio']**2, 1.0/c['epicyclic_gearing_ratio']**3, 1.0/c['epicyclic_gearing_ratio']**4, 1.0/c['epicyclic_gearing_ratio']**5)
  r_info += """
gear_module:              \t{:0.3f}
gear_router_bit_radius:   \t{:0.3f}
gear_tooth_resolution:    \t{:d}
gear_skin_thickness:      \t{:0.3f}
gear_addendum_dedendum_parity_slack: {:0.3f}
""".format(c['gear_module'], c['gear_router_bit_radius'], c['gear_tooth_resolution'], c['gear_skin_thickness'], c['gear_addendum_dedendum_parity_slack'])
  r_info += """
carrier_central radius: \t{:0.3f}  diameter: {:0.3f}
carrier_leg radius:     \t{:0.3f}  diameter: {:0.3f}
carrier_peripheral_disable: \t{:d}
carrier_hollow_disable:     \t{:d}
carrier_peripheral_external radius: \t{:0.3f}  diameter: {:0.3f}
carrier_peripheral_internal radius: \t{:0.3f}  diameter: {:0.3f}
carrier_leg_middle radius:  \t{:0.3f}  diameter: {:0.3f}
carrier_smoothing:          \t{:0.3f}  diameter: {:0.3f}
carrier_leg_hole:           \t{:0.3f}  diameter: {:0.3f}
""".format(c['carrier_central_radius'], 2*c['carrier_central_radius'], c['carrier_leg_radius'], 2*c['carrier_leg_radius'], c['carrier_peripheral_disable'], c['carrier_hollow_disable'], c['carrier_peripheral_external_radius'], 2*c['carrier_peripheral_external_radius'], c['carrier_peripheral_internal_radius'], 2*c['carrier_peripheral_internal_radius'], c['carrier_leg_middle_radius'], 2*c['carrier_leg_middle_radius'], c['carrier_sr'], 2*c['carrier_sr'], c['carrier_leg_hole_radius'], 2*c['carrier_leg_hole_radius'])
  r_info += """
sun_crenel_nb:      {:d}
sun_crenel_type:    {:s}
sun_crenel_mark_nb: {:d}
""".format(c['sun_crenel_nb'], c['sun_crenel_type'], c['sun_crenel_mark_nb'])
  r_info += """
planet_crenel_nb:      {:d}
planet_crenel_type:    {:s}
planet_crenel_mark_nb: {:d}
""".format(c['planet_crenel_nb'], c['planet_crenel_type'], c['planet_crenel_mark_nb'])
  r_info += """
holder radius:  {:0.3f}  diameter: {:0.3f}
holder_crenel_number: {:d}
holder_hole_mark_nb:  {:d}
""".format(c['holder_radius'], 2*c['holder_radius'], c['holder_crenel_number'], c['holder_hole_mark_nb'])
  r_info += """
planet_nb:                      {:d}
planet-carrier angle:           {:0.3f}
planet-axle radius:             {:0.3f}  diameter: {:0.3f}
planet-axle positioning radius: {:0.3f}  diameter: {:0.3f}
output-gearwheel-crenel nb:     {:d}
output-gearwheel-crenel angle:  {:0.3f}
output-gearwheel-crenel radius: {:0.3f}  diameter: {:0.3f}
output-gearwheel-crenel positioning radius: {:0.3f}  diameter: {:0.3f}
""".format(c['planet_nb'], c['first_planet_position_angle'], c['carrier_leg_hole_radius'], 2*c['carrier_leg_hole_radius'], c['carrier_hole_position_radius'], 2*c['carrier_hole_position_radius'], c['output_gearwheel_crenel_number'], c['output_gearwheel_crenel_angle'], c['output_gearwheel_crenel_diameter']/2.0, c['output_gearwheel_crenel_diameter'], c['output_gearwheel_crenel_position_diameter']/2.0, c['output_gearwheel_crenel_position_diameter'])
  r_info += """
top_clearance_radius: {:0.3f}  diameter: {:0.3}
top_axle_hole_radius: {:0.3f}  diameter: {:0.3}
top_central_radius:   {:0.3f}  diameter: {:0.3}
""".format(c['top_clearance_radius'], 2*c['top_clearance_radius'], c['top_axle_hole_radius'], 2*c['top_axle_hole_radius'], c['top_central_radius'], 2*c['top_central_radius'])
  #print(eg_parameter_info)
  return(r_info)


################################################################
# self test
################################################################

def epicyclic_gearing_self_test():
  """
  This is the non-regression test of epicyclic_gearing.
  Look at the Tk window to check errors.
  """
  r_tests = [
    ["simplest test"        , "--sun_gear_tooth_nb 20 --planet_gear_tooth_nb 31 --gear_module 1.0 --planet_nb 3"],
    ["sun crenel"           , "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --sun_axle_x_width 6 --sun_crenel_nb 2"],
    ["planet crenel"        , "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --planet_axle_diameter 8 --planet_crenel_nb 5"],
    ["gearring crenel"      , "--sun_gear_tooth_nb 23 --planet_gear_tooth_nb 31 --gear_module 1.0 --holder_crenel_number 4"],
    ["carrier with peripheral and crenel", "--sun_gear_tooth_nb 20 --planet_gear_tooth_nb 31 --gear_module 1.0 --planet_nb 3"],
    ["carrier with peripheral and without crenel", "--sun_gear_tooth_nb 20 --planet_gear_tooth_nb 31 --gear_module 1.0 --planet_nb 3 --carrier_crenel_height 0"],
    ["carrier without peripheral and with crenel", "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --carrier_peripheral_disable --carrier_central_diameter 30.0"],
    ["carrier without peripheral and crenel", "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --carrier_peripheral_disable --carrier_crenel_height 0 --carrier_central_diameter 30.0"],
    ["carrier without peripheral and small central circle", "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --carrier_peripheral_disable --carrier_central_diameter 20.0"],
    ["sun crenel circle"    , "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --sun_axle_x_width 8 --sun_crenel_nb 6 --sun_crenel_type circle --sun_crenel_width 1.9 --sun_crenel_diameter 12"],
    ["sun crenel circle marked", "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --sun_axle_x_width 8 --sun_crenel_nb 6 --sun_crenel_type circle --sun_crenel_width 1.9 --sun_crenel_diameter 12 --sun_crenel_mark_nb 1"],
    ["carrier crenel hole"  , "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --carrier_hole_diameter 1.9"],
    ["carrier crenel double hole"  , "--sun_gear_tooth_nb 17 --planet_gear_tooth_nb 31 --gear_module 1.0 --carrier_hole_diameter 1.0 --carrier_double_hole_length 2.0"],
    ["holder crenel double hole"  , "--sun_gear_tooth_nb 17 --planet_gear_tooth_nb 31 --gear_module 1.0 --holder_hole_diameter 5.0 --holder_double_hole_diameter 3.0 --holder_double_hole_length 10.0 --holder_crenel_skin_width 2.0 --holder_crenel_position 3.0 --holder_crenel_height 2.0"],
    ["gear simulation"      , "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 33 --gear_module 1.0 --gear_addendum_dedendum_parity_slack 1.5 --simulation_annulus_planet_gear"],
    ["output file"          , "--sun_gear_tooth_nb 21 --planet_gear_tooth_nb 31 --gear_module 1.0 --input_gearwheel_tooth_nb 29 --output_file_basename test_output/epicyclic_self_test.dxf"],
    ["output file2"         , "--sun_gear_tooth_nb 13 --planet_gear_tooth_nb 19 --gear_module 1.0 --holder_hole_diameter 1.0 --holder_crenel_position 2.0 --holder_crenel_height 2.0 --holder_crenel_width 6.0 --holder_crenel_skin_width 4.0 --input_gearwheel_tooth_nb 29 --input_gearwheel_module 1.0 --input_gearwheel_axle_diameter 19.0 --input_gearwheel_crenel_number 6 --input_gearwheel_crenel_position_diameter 24.0 --input_gearwheel_crenel_diameter 1.0 --input_cover_extra_space 0.5 --output_gearwheel_tooth_nb 13 --output_gearwheel_module 3.0 --output_gearwheel_axle_diameter 22.0 --output_gearwheel_crenel_number 6 --output_gearwheel_crenel_position_diameter 28.0 --output_gearwheel_crenel_diameter 3.0 --output_gearwheel_crenel_angle 0.3 --output_cover_extra_space 0.5 --output_file_basename test_output/epicyclic_self_test2.dxf"],
    ["output file3"         , "--sun_gear_tooth_nb 13 --planet_gear_tooth_nb 19 --gear_module 1.0 --holder_hole_diameter 1.0 --holder_crenel_position 2.0 --holder_crenel_height 2.0 --holder_crenel_width 6.0 --holder_crenel_skin_width 4.0 --input_gearwheel_tooth_nb 45 --input_gearwheel_module 1.0 --input_gearwheel_axle_diameter 22.0 --input_gearwheel_crenel_number 6 --input_gearwheel_crenel_position_diameter 26.0 --input_gearwheel_crenel_diameter 1.0 --input_cover_extra_space 0.5 --output_gearwheel_tooth_nb 13 --output_gearwheel_module 3.0 --sun_crenel_nb 5 --sun_crenel_type circle --sun_crenel_mark_nb 2 --sun_crenel_diameter 8.0 --sun_crenel_width 1.0 --carrier_hole_position_diameter 38.0 --carrier_hole_diameter 1.0 --carrier_double_hole_length 3.0 --carrier_leg_hole_diameter 3.0 --output_file_basename test_output/epicyclic_self_test3.dxf"],
    ["last test"            , "--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0"]]
  return(r_tests)

################################################################
# epicyclic_gearing design declaration
################################################################

class epicyclic_gearing(cnc25d_api.bare_design):
  """ epicyclic_gearing design
  """
  def __init__(self, constraint={}):
    """ configure the epicyclic_gearing design
    """
    self.set_design_name("epicyclic_gearing")
    self.set_constraint_constructor(epicyclic_gearing_constraint_constructor)
    self.set_constraint_check(epicyclic_gearing_constraint_check)
    self.set_2d_constructor(epicyclic_gearing_2d_construction)
    self.set_2d_simulation(epicyclic_gearing_2d_simulations())
    self.set_3d_constructor(epicyclic_gearing_3d_construction)
    self.set_info(epicyclic_gearing_info)
    self.set_display_figure_list(['eg_assembly_fig'])
    self.set_default_simulation()
    self.set_2d_figure_file_list([])
    self.set_3d_figure_file_list(['eg_gear_assembly_fig'])
    self.set_3d_conf_file_list(['epicyclic_gearing_3dconf1'])
    self.set_allinone_return_type()
    self.set_self_test(epicyclic_gearing_self_test())
    self.apply_constraint(constraint)


################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("epicyclic_gearing.py says hello!\n")
  my_eg = epicyclic_gearing()
  #my_eg.allinone()
  #my_eg.allinone("--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --return_type freecad_object")
  #my_eg.allinone("--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0")
  my_eg.allinone("--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0 --sun_axle_x_width 10 --sun_crenel_nb 4 --sun_crenel_height 1.0 --sun_crenel_width 3.0")
  if(cnc25d_api.interpretor_is_freecad()):
    Part.show(my_gb.get_fc_obj('epicyclic_gearing_3dconf1'))


