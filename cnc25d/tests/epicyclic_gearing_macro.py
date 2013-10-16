# epicyclic_gearing_macro.py
# the macro to generate an epicyclic_gearing.
# created by charlyoleg on 2013/10/03
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design epicyclic_gearing
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################

eg_constraint = {}
#### epicyclic_gearing dictionary entries
### structure
eg_constraint['sun_gear_tooth_nb']       = 20
eg_constraint['planet_gear_tooth_nb']    = 31
eg_constraint['planet_nb']               = 3
### gear
eg_constraint['gear_module']             = 1.0
eg_constraint['gear_router_bit_radius']  = 0.1
eg_constraint['gear_tooth_resolution']   = 2
eg_constraint['gear_skin_thickness']     = 0.0
eg_constraint['gear_addendum_dedendum_parity_slack']      = 0.0
eg_constraint['gearring_dedendum_to_hollow_pourcentage']  = 0.0
eg_constraint['gear_addendum_height_pourcentage']         = 100.0
### sun-gear
eg_constraint['sun_axle_diameter']       = 12.0
eg_constraint['sun_crenel_nb']           = 4
eg_constraint['sun_crenel_type']         = 'rectangle' # 'rectangle' or 'circle'
eg_constraint['sun_crenel_diameter']     = 0.0
eg_constraint['sun_crenel_width']        = 3.0
eg_constraint['sun_crenel_height']       = 1.0
eg_constraint['sun_crenel_router_bit_radius']   = 0.1
### planet-gear
eg_constraint['planet_axle_diameter']      = 10.0
eg_constraint['planet_crenel_nb']          = 0
eg_constraint['planet_crenel_type']        = 'rectangle' # 'rectangle' or 'circle'
eg_constraint['planet_crenel_diameter']    = 0.0
eg_constraint['planet_crenel_width']       = 4.0
eg_constraint['planet_crenel_height']      = 2.0
eg_constraint['planet_crenel_router_bit_radius']  = 0.1
### planet gear carrier
eg_constraint['carrier_central_diameter']               = 0.0
eg_constraint['carrier_leg_diameter']                   = 0.0
eg_constraint['carrier_peripheral_disable']             = False
eg_constraint['carrier_hollow_disable']                 = False
eg_constraint['carrier_peripheral_external_diameter']   = 0.0
eg_constraint['carrier_peripheral_internal_diameter']   = 0.0
eg_constraint['carrier_leg_middle_diameter']            = 0.0
eg_constraint['carrier_smoothing_radius']               = 0.0
eg_constraint['carrier_leg_hole_diameter']              = 10.0
## carrier peripheral crenel
eg_constraint['carrier_crenel_width']                = 4.0
eg_constraint['carrier_crenel_height']               = 2.0
eg_constraint['carrier_crenel_router_bit_radius']    = 0.1
eg_constraint['carrier_hole_position_diameter']      = 0.0
eg_constraint['carrier_hole_diameter']               = 0.0
### annulus: inherit dictionary entries from gearring
### holder
eg_constraint['holder_diameter']            = 0.0
eg_constraint['holder_crenel_number']       = 6
eg_constraint['holder_position_angle']      = 0.0
### holder-hole
eg_constraint['holder_hole_position_radius']   = 0.0
eg_constraint['holder_hole_diameter']          = 5.0
### holder-crenel
eg_constraint['holder_crenel_position']        = 4.0
eg_constraint['holder_crenel_height']          = 2.0
eg_constraint['holder_crenel_width']           = 10.0
eg_constraint['holder_crenel_skin_width']      = 5.0
eg_constraint['holder_crenel_router_bit_radius']   = 1.0
eg_constraint['holder_smoothing_radius']       = 0.0
### general
eg_constraint['cnc_router_bit_radius']   = 0.1
eg_constraint['gear_profile_height']     = 10.0
### design output : view the gearring with tkinter or write files
eg_constraint['tkinter_view']                    = True
eg_constraint['simulation_sun_planet_gear']      = False
eg_constraint['simulation_annulus_planet_gear']  = False
eg_constraint['output_file_basename'] = "" # set a not-empty string if you want to generate the output files
#eg_constraint['output_file_basename'] = "test_output/epicyclic_gearing_macro.svg"  # to generate the SVG file with mozman svgwrite
#eg_constraint['output_file_basename'] = "test_output/epicyclic_gearing_macro.dxf"  # to generate the DXF file with mozman svgwrite
#eg_constraint['output_file_basename'] = "test_output/epicyclic_gearing_macro"      # to generate the Brep and DXF file with FreeCAD
eg_constraint['return_type'] = 'int_status' #'freecad_object' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'

################################################################
# action
################################################################

my_eg = cnc25d_design.epicyclic_gearing(eg_constraint)

try: # display if a freecad object
  Part.show(my_eg)
except:
  pass

