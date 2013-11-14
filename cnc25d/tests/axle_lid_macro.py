# axle_lid_macro.py
# the macro to generate an axle_lid.
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design axle_lid
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

al_constraint = {}
### annulus-holder: inherit dictionary entries from gearring
### holder
al_constraint['holder_diameter']            = 120.0
al_constraint['holder_crenel_number']       = 6
al_constraint['holder_position_angle']      = 0.0
### holder-hole
al_constraint['holder_hole_position_radius']   = 0.0
al_constraint['holder_hole_diameter']          = 5.0
al_constraint['holder_double_hole_diameter']   = 0.0
al_constraint['holder_double_hole_length']     = 0.0
al_constraint['holder_double_hole_position']   = 0.0
### holder-crenel
al_constraint['holder_crenel_position']        = 4.0
al_constraint['holder_crenel_height']          = 2.0
al_constraint['holder_crenel_width']           = 10.0
al_constraint['holder_crenel_skin_width']      = 5.0
al_constraint['holder_crenel_router_bit_radius']   = 1.0
al_constraint['holder_smoothing_radius']       = 0.0
#### axle_lid
al_constraint['clearance_diameter']           = 100.0
al_constraint['central_diameter']             = 40.0
al_constraint['axle_hole_diameter']           = 22.0
al_constraint['annulus_holder_axle_hole_diameter'] = 0.0
### axle-B
al_constraint['output_axle_B_place']              = 'none' # 'none', 'small' or 'large' # useful when the gearring has an odd number of crenels
al_constraint['output_axle_distance']             = 0.0
al_constraint['output_axle_angle']                = 0.0
al_constraint['output_axle_B_internal_diameter']  = 0.0
al_constraint['output_axle_B_external_diameter']  = 0.0
al_constraint['output_axle_B_crenel_number']              = 0
al_constraint['output_axle_B_crenel_diameter']            = 0.0
al_constraint['output_axle_B_crenel_position_diameter']   = 0.0
al_constraint['output_axle_B_crenel_angle']               = 0.0
al_constraint['input_axle_B_enable']                      = False
### leg
al_constraint['leg_type']             = 'none' # 'none', 'rear' or 'side'
al_constraint['leg_length']           = 0.0
al_constraint['foot_length']          = 0.0
al_constraint['toe_length']           = 0.0
al_constraint['leg_hole_diameter']    = 0.0
al_constraint['leg_hole_distance']    = 0.0
al_constraint['leg_hole_length']      = 0.0
al_constraint['leg_border_length']    = 0.0
al_constraint['leg_shift_length']     = 0.0
### general
al_constraint['smoothing_radius']       = 0.0
al_constraint['cnc_router_bit_radius']  = 0.1
al_constraint['extrusion_height']     = 10.0
### design output : view the gearring with tkinter or write files
al_constraint['tkinter_view']                    = True
al_constraint['output_file_basename'] = "" # set a not-empty string if you want to generate the output files
#al_constraint['output_file_basename'] = "test_output/axle_lid_macro.svg"  # to generate the SVG file with mozman svgwrite
#al_constraint['output_file_basename'] = "test_output/axle_lid_macro.dxf"  # to generate the DXF file with mozman svgwrite
#al_constraint['output_file_basename'] = "test_output/axle_lid_macro"      # to generate the Brep and DXF file with FreeCAD
al_constraint['return_type'] = 'int_status' #'freecad_object' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'

################################################################
# action
################################################################

my_al = cnc25d_design.axle_lid(al_constraint)

try: # display if a freecad object
  Part.show(my_al)
except:
  pass

