# bagel_macro.py
# the macro to generate a bagel, the axle-guidance of the bell piece
# created by charlyoleg on 2013/12/02
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
this piece of code is an example of how to use the parametric design bagel
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it.  Default value is used, if you don't set a constraint explicitly.
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
from cnc25d import cnc25d_design
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

bagel_constraint = {} # This python-dictionary contains all the constraint-parameters to build the bagel piece (part of a gimbal)
### bagel_face
## bulk
bagel_constraint['bagel_axle_diameter']                   = 10.0
bagel_constraint['bagel_axle_internal_diameter']          = 0.0
bagel_constraint['bagel_axle_external_diameter']          = 0.0
## axle_hole
bagel_constraint['axle_hole_nb']                    = 6
bagel_constraint['axle_hole_diameter']              = 4.0
bagel_constraint['axle_hole_position_diameter']     = 0.0
bagel_constraint['axle_hole_angle']                 = 0.0
## wall_thickness
bagel_constraint['external_bagel_thickness']        = 2.0
bagel_constraint['middle_bagel_thickness']          = 6.0
bagel_constraint['internal_bagel_thickness']        = 2.0
### manufacturing
bagel_constraint['bagel_extra_cut_thickness']       = 0.0

################################################################
# action
################################################################

my_bagel = cnc25d_design.bagel(bagel_constraint)
my_bagel.outline_display()
my_bagel.write_info_txt("test_output/bagel_macro")
my_bagel.write_figure_svg("test_output/bagel_macro")
my_bagel.write_figure_dxf("test_output/bagel_macro")
my_bagel.write_figure_brep("test_output/bagel_macro")
my_bagel.write_assembly_brep("test_output/bagel_macro")
my_bagel.write_freecad_brep("test_output/bagel_macro")
#my_bagel.run_simulation("") # no simulation for bagel
my_bagel.view_design_configuration()
#my_bagel.run_self_test("")
#my_bagel.cli("--output_file_basename test_output/bm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_bagel.get_fc_obj_3dconf('bagel_assembly_conf1'))


