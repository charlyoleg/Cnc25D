# box_wood_frame_macro.py
# the macro for a wood frame for building a shell or a straw house.
# created by charlyoleg on 2013/05/31
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
this piece of code is an example of how to use the parametric design box_wood_frame
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. box_wood_frame will use a default value
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

bwf_constraint = {} # This python-dictionary contains all the constraint-parameters to build the box_wood_frame
bwf_constraint['box_width'] = 400.0
bwf_constraint['box_depth'] = 400.0
bwf_constraint['box_height'] = 400.0
bwf_constraint['fitting_height'] = 30.0
bwf_constraint['h_plank_width'] = 50.0
bwf_constraint['v_plank_width'] = 30.0
bwf_constraint['plank_height'] = 20.0
bwf_constraint['d_plank_width'] = 30.0
bwf_constraint['d_plank_height'] = 10.0
bwf_constraint['crenel_depth'] = 5.0
bwf_constraint['wall_diagonal_size'] = 50.0
bwf_constraint['tobo_diagonal_size'] = 100.0
bwf_constraint['diagonal_lining_top_height'] = 20.0
bwf_constraint['diagonal_lining_bottom_height'] = 20.0
bwf_constraint['module_width'] = 1
bwf_constraint['router_bit_radius'] = 2.0
bwf_constraint['cutting_extra'] = 2.0 # doesn't affect the cnc cutting plan
bwf_constraint['slab_thickness'] = 5.0

################################################################
# action
################################################################

my_bwf = cnc25d_design.box_wood_frame(bwf_constraint)
my_bwf.outline_display()
my_bwf.write_info_txt("test_output/bwf_macro")
my_bwf.write_figure_svg("test_output/bwf_macro")
my_bwf.write_figure_dxf("test_output/bwf_macro")
my_bwf.write_figure_brep("test_output/bwf_macro")
my_bwf.write_assembly_brep("test_output/bwf_macro")
my_bwf.write_freecad_brep("test_output/bwf_macro")
#my_bwf.run_simulation("") # no simulation for box_wood_frame
my_bwf.view_design_configuration()
#my_bwf.run_self_test("")
#my_bwf.cli("--output_file_basename test_output/bwfm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_bwf.get_fc_obj_3dconf('bwf_3dconf1'))

