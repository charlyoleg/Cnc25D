# juergen_four_gearwheel_test.py
# the macro to generate test-system with Juergen
# created by charlyoleg on 2013/10/02
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
Gear test-system with Juergen
4 gearwheels in a circular-chain
"""

################################################################
# import
################################################################

try:    # when working on the source files
  from cnc25d import cnc25d_api
except: # when working with an installed Cnc25D package
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
#cnc25d_api.importing_freecad()
#print("FreeCAD.Version:", FreeCAD.Version())

import math
import sys
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# gearwheels
################################################################

sim = False
view = False
if(len(sys.argv)>1):
  if(sys.argv[1]=='sim'):
    sim = True
  elif(sys.argv[1]=='view'):
    view = True

gw_constraint = {}
##### from gear_profile
#gw_constraint['gear_type']                      = 'e'
gw_constraint['gear_tooth_nb']                  = 19
gw_constraint['gear_module']                    = 10.0 #5 #10.0
#gw_constraint['second_gear_type']                     = 'e'
gw_constraint['second_gear_tooth_nb']                 = 30
# first gear position
gw_constraint['center_position_x']                    = 200.0
gw_constraint['center_position_y']                    = 200.0
## second gear position
additional_axis_length = 1.0
#gw_constraint['second_gear_position_angle']           = 0.0
#gw_constraint['second_gear_additional_axis_length']   = additional_axis_length
###### from gearwheel
#### axle
gw_constraint['axle_type']                = 'circle'
gw_constraint['axle_x_width']             = 6.0
#gw_constraint['axle_y_width']             = 15.0
#gw_constraint['axle_router_bit_radius']   = 3.0
#### wheel-hollow = legs
gw_constraint['wheel_hollow_leg_number']        = 3
gw_constraint['wheel_hollow_leg_width']         = 20.0
#gw_constraint['wheel_hollow_leg_angle']         = 0.0
gw_constraint['wheel_hollow_internal_diameter'] = 40.0
#gw_constraint['wheel_hollow_external_diameter'] = 125.0
#gw_constraint['wheel_hollow_router_bit_radius'] = 5.0
### cnc router_bit constraint
gw_constraint['cnc_router_bit_radius']          = 2.0 #1.6 #2.0
### design output : view the gearwheel with tkinter or write files
gw_constraint['tkinter_view'] = False
gw_constraint['output_file_basename'] = "" # set a not-empty string if you want to generate the output files
gw_constraint['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'

gw_c1 = gw_constraint.copy()
gw_c1['gear_tooth_nb'] = 19
gw_c1['second_gear_tooth_nb'] = 30
gw_c1['wheel_hollow_leg_number'] = 3
# --axle_type circle --axle_x_width 6.0 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 40.0 --cnc_router_bit_radius 2.0 --gear_module 10 --gear_tooth_nb 19 --second_gear_tooth_nb 30 --wheel_hollow_leg_number 3 --output_file_basename test_output/luke1.dxf

gw_c2 = gw_constraint.copy()
gw_c2['gear_tooth_nb'] = 30
gw_c2['second_gear_tooth_nb'] = 19
gw_c2['wheel_hollow_leg_number'] = 4
# --axle_type circle --axle_x_width 6.0 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 40.0 --cnc_router_bit_radius 2.0 --gear_module 10 --gear_tooth_nb 30 --second_gear_tooth_nb 19 --wheel_hollow_leg_number 4 --output_file_basename test_output/luke2.dxf

gw_c3 = gw_constraint.copy()
gw_c3['gear_tooth_nb'] = 25
gw_c3['second_gear_tooth_nb'] = 19
gw_c3['wheel_hollow_leg_number'] = 5

gw_c4 = gw_constraint.copy()
gw_c4['gear_tooth_nb'] = 33
gw_c4['second_gear_tooth_nb'] = 19
gw_c4['wheel_hollow_leg_number'] = 6

gw_c_array = [gw_c1, gw_c2, gw_c3, gw_c4]

for i in range(len(gw_c_array)):
  if(sim):
    gw_c_array[i]['simulation_enable']    = True
  else:
    if(view):
      gw_c_array[i]['tkinter_view'] = True
    gw_c_array[i]['output_file_basename'] = "test_output/jh01_{:02d}.dxf".format(i+1)
  my_gw = cnc25d_design.gearwheel(gw_c_array[i])
  #Part.show(my_gw)
#Part.show(my_gw)

################################################################
# center-plank
################################################################

import math

m = gw_constraint['gear_module']
n1 = gw_c1['gear_tooth_nb']
n2 = gw_c2['gear_tooth_nb']
n3 = gw_c3['gear_tooth_nb']
n4 = gw_c4['gear_tooth_nb']

center_diameter = gw_constraint['axle_x_width']

pd1 = n1 * m
pd2 = n2 * m
pd3 = n3 * m
pd4 = n4 * m

def center_position(ai_center_diameter, ai_pd1, ai_pd2, ai_pd3, ai_pd4, ai_optional_additional_axis_length):
  """ compute the four axis center
  """
  # inter-axis length
  l12 = (ai_pd1+ai_pd2)/2.0 + ai_optional_additional_axis_length
  l23 = (ai_pd2+ai_pd3)/2.0 + ai_optional_additional_axis_length
  l34 = (ai_pd3+ai_pd4)/2.0 + ai_optional_additional_axis_length
  l41 = (ai_pd4+ai_pd1)/2.0 + ai_optional_additional_axis_length
  # l13 arbitrary
  l13_min = max(l12, l23, l34, l41)
  l13_max = min(l12+l23, l34+l41)
  l13 = (l13_min+l13_max)/2.0
  print("l13: min {:0.3f}  max {:0.3f} l13 {:0.3f}".format(l13_min, l13_max, l13))
  # c1
  c1x = 0.0
  c1y = 0.0
  # c3
  c3x = c1x + 0.0
  c3y = c1y + l13
  # c2
  # law of cosines: BAC = math.acos((b**2+c**2-a**2)/(2*b*c))
  a213 = math.acos((l12**2+l13**2-l23**2)/(2*l12*l13))
  c2a = math.pi/2-a213
  c2x = c1x + l12*math.cos(c2a)
  c2y = c1y + l12*math.sin(c2a)
  # c4
  a314 = math.acos((l41**2+l13**2-l34**2)/(2*l41*l13))
  c4a = math.pi/2+a314
  c4x = c1x + l41*math.cos(c4a)
  c4y = c1y + l41*math.sin(c4a)
  # info_txt
  info_txt = """
  center coordiantes:
  c1: x {:0.3f}  y {:0.3f}
  c2: x {:0.3f}  y {:0.3f}
  c3: x {:0.3f}  y {:0.3f}
  c4: x {:0.3f}  y {:0.3f}
  """.format(c1x, c1y, c2x, c2y, c3x, c3y, c4x, c4y)
  print("{:s}".format(info_txt))
  ### dxf
  # plank outline 
  smooth_radius = 40
  center_plank_A = [
    (c1x,               c1y-smooth_radius,  smooth_radius),
    (c2x+smooth_radius, c2y,                smooth_radius),
    (c3x,               c3y+smooth_radius,  smooth_radius),
    (c4x-smooth_radius, c4y,                smooth_radius),
    (c1x,               c1y-smooth_radius,  0)]
  center_plank_B = cnc25d_api.cnc_cut_outline(center_plank_A, "center_plank_A")
  # figure
  center_figure = [
    center_plank_B,
    (c1x, c1y, ai_center_diameter/2.0),
    (c2x, c2y, ai_center_diameter/2.0),
    (c3x, c3y, ai_center_diameter/2.0),
    (c4x, c4y, ai_center_diameter/2.0)]
  if(not sim):
    cnc25d_api.generate_output_file(center_figure, "test_output/jh01_zahnrad_center_{:0.2f}.dxf".format(ai_optional_additional_axis_length), 10.0, "hello")

center_position(center_diameter, pd1, pd2, pd3, pd4, 0)
center_position(center_diameter, pd1, pd2, pd3, pd4, additional_axis_length)


