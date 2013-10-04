# fablab_berlin_epicyclic_gearing.py
# the macro to generate an epicyclic-gearing
# created by charlyoleg on 2013/10/04
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
An epicyclic-gearing tested with the Zing laser-cutter
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
# sun and planet gearwheels
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
gw_constraint['gear_module']                    = 1.0 #5 #10.0
#gw_constraint['second_gear_type']                     = 'e'
gw_constraint['second_gear_tooth_nb']                 = 30
# first gear position
gw_constraint['center_position_x']                    = 0.0
gw_constraint['center_position_y']                    = 0.0
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
gw_constraint['wheel_hollow_leg_width']         = 5.0
#gw_constraint['wheel_hollow_leg_angle']         = 0.0
#gw_constraint['wheel_hollow_internal_diameter'] = 40.0
#gw_constraint['wheel_hollow_external_diameter'] = 125.0
#gw_constraint['wheel_hollow_router_bit_radius'] = 5.0
### cnc router_bit constraint
gw_constraint['cnc_router_bit_radius']          = 0.3 #1.6 #2.0
### design output : view the gearwheel with tkinter or write files
gw_constraint['tkinter_view'] = False
gw_constraint['output_file_basename'] = "" # set a not-empty string if you want to generate the output files
gw_constraint['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'

gw_sun = gw_constraint.copy()
gw_sun['gear_tooth_nb'] = 20
gw_sun['second_gear_tooth_nb'] = 20
gw_sun['wheel_hollow_leg_number'] = 4
gw_sun['axle_type']                = 'rectangle'
gw_sun['axle_x_width']             = 6.0
gw_sun['axle_y_width']             = gw_sun['axle_x_width']
# --axle_type circle --axle_x_width 6.0 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 40.0 --cnc_router_bit_radius 2.0 --gear_module 10 --gear_tooth_nb 19 --second_gear_tooth_nb 30 --wheel_hollow_leg_number 3 --output_file_basename test_output/luke1.dxf

gw_planet = gw_constraint.copy()
gw_planet['gear_tooth_nb'] = 20
gw_planet['second_gear_tooth_nb'] = 20
gw_planet['wheel_hollow_leg_number'] = 3
gw_planet['axle_type']                = 'circle'
gw_planet['axle_x_width']             = 6.0
# --axle_type circle --axle_x_width 6.0 --wheel_hollow_leg_width 20.0 --wheel_hollow_internal_diameter 40.0 --cnc_router_bit_radius 2.0 --gear_module 10 --gear_tooth_nb 30 --second_gear_tooth_nb 19 --wheel_hollow_leg_number 4 --output_file_basename test_output/luke2.dxf


gw_array = [gw_sun, gw_planet]

for i in range(len(gw_array)):
  if(sim):
    gw_array[i]['simulation_enable']    = True
  else:
    if(view):
      gw_array[i]['tkinter_view'] = True
    gw_array[i]['output_file_basename'] = "test_output/flb01_gw{:02d}.dxf".format(i+1)
  my_gw = cnc25d_design.gearwheel(gw_array[i])
  #Part.show(my_gw)
#Part.show(my_gw)


################################################################
# annulus gearring
################################################################

gr_constraint = {}
##### from gear_profile
### first gear
# general
gr_constraint['gear_tooth_nb']                  = 31
gr_constraint['gear_module']                    = gw_constraint['gear_module']
### second gear
# general
gr_constraint['second_gear_tooth_nb']                 = 19
##### from gearring
### holder
#gr_constraint['holder_diameter']            = 360.0
gr_constraint['holder_crenel_number']       = 6
gr_constraint['holder_position_angle']      = 0.0
### holder-hole
gr_constraint['holder_hole_position_radius']   = 0.0
gr_constraint['holder_hole_diameter']          = 2.0
### holder-crenel
gr_constraint['holder_crenel_position']        = 3.0
gr_constraint['holder_crenel_height']          = 2.0
gr_constraint['holder_crenel_width']           = 5.0
gr_constraint['holder_crenel_skin_width']      = 5.0
gr_constraint['holder_crenel_router_bit_radius']   = 1.0
gr_constraint['holder_smoothing_radius']       = 0.0
### cnc router_bit constraint
gr_constraint['cnc_router_bit_radius']          = 0.2


gr_annulus = gr_constraint.copy()
gr_annulus['gear_tooth_nb'] = 60
gr_annulus['second_gear_tooth_nb'] = 20
#gr_annulus['holder_diameter']            = (gr_annulus['gear_tooth_nb']+4) * gr_constraint['gear_module'] + gr_constraint['holder_hole_diameter']
# --gear_tooth_nb 60 --second_gear_tooth_nb 20 --holder_diameter 220 --cnc_router_bit_radius 0.5 --gear_module 3.0

gr_array = [gr_annulus]

for i in range(len(gr_array)):
  if(sim):
    gr_array[i]['simulation_enable']    = True
  else:
    if(view):
      gr_array[i]['tkinter_view'] = True
    gr_array[i]['output_file_basename'] = "test_output/flb01_gr{:02d}.dxf".format(i+1)
  my_gr = cnc25d_design.gearring(gr_array[i])
  #Part.show(my_gr)
#Part.show(my_gr)

################################################################
# triangle
################################################################

l_sun_planetary = (gw_sun['gear_tooth_nb'] + gw_planet['gear_tooth_nb'])*gw_constraint['gear_module']/2.0

smooth_triangle = 10.0
l_triangle = l_sun_planetary + 2.0*smooth_triangle
triangle_outline_A = (
  (l_triangle*math.cos(0*2*math.pi/3), l_triangle*math.sin(0*2*math.pi/3), smooth_triangle),
  (l_triangle*math.cos(1*2*math.pi/3), l_triangle*math.sin(1*2*math.pi/3), smooth_triangle),
  (l_triangle*math.cos(2*2*math.pi/3), l_triangle*math.sin(2*2*math.pi/3), smooth_triangle),
  (l_triangle*math.cos(0*2*math.pi/3), l_triangle*math.sin(0*2*math.pi/3), 0))
triangle_outline_B = cnc25d_api.cnc_cut_outline(triangle_outline_A, "triangle_outline_B")

s = gw_sun['axle_x_width']/2.0
c = -1*gw_constraint['cnc_router_bit_radius']
rectangle_axle_A = (
  (s, s, c),
  (-s, s, c),
  (-s, -s, c),
  (s, -s, c),
  (s, s, 0))
rectangle_axle_B = cnc25d_api.cnc_cut_outline(rectangle_axle_A, "rectangle_axle_A")

circle_axle_1 = (l_sun_planetary*math.cos(0*2*math.pi/3), l_sun_planetary*math.sin(0*2*math.pi/3), gw_planet['axle_x_width']/2.0)
circle_axle_2 = (l_sun_planetary*math.cos(1*2*math.pi/3), l_sun_planetary*math.sin(1*2*math.pi/3), gw_planet['axle_x_width']/2.0)
circle_axle_3 = (l_sun_planetary*math.cos(2*2*math.pi/3), l_sun_planetary*math.sin(2*2*math.pi/3), gw_planet['axle_x_width']/2.0)

triangle_figure = (triangle_outline_B, rectangle_axle_B, circle_axle_1, circle_axle_2, circle_axle_3)
cnc25d_api.generate_output_file(triangle_figure, "test_output/flb01_triangle.dxf", 10.0, "hello")


