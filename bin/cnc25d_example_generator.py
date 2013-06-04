#!/usr/bin/python
#
# cnc25d_example_generator.py
# it generates examples of python scripts that use the cnc25d package
# created by charlyoleg on 2013/06/03
# license: CC BY SA 3.0

ceg_instructions="""
The example script {:s} has been generated!
To use it, just run the following command:
> python {:s}
You can rename, move, copy and edit the script {:s}
"""


bwf_script_name="box_wood_frame_example.py"

bwf_script_content="""
#!/usr/bin/python
#
# box_wood_frame_example.py
# This script example generates a box_wood_frame with the cnc25d library.
# rename, move, copy and edit this script.
# created by charlyoleg on 2013/06/03
# license: CC BY SA 3.0

################################################################
# Installation request
################################################################
# This script needs freecad (http://www.freecadweb.org/) installed on your system
# With Ubuntu, run the following command
# > sudo apt-get install freecad


################################################################
# add to sys.path path to the cnc25d package
################################################################

#import sys, os
#current_dir = os.getcwd()
##print("dbg109: current_dir:", current_dir)
#sys.path.append(current_dir+'/..')

################################################################
# header for Python / FreeCAD compatibility
################################################################

from cnc25d import importing_freecad
importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

#
from cnc25d import box_wood_frame
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edite those parameter values

bwf_box_width = 400.0
bwf_box_depth = 400.0 # recommendation: keep bwf_box_depth = bwf_box_width to get more pile up possibilities
bwf_box_height = 400.0
bwf_fitting_height = 30.0
bwf_h_plank_width = 50.0
bwf_v_plank_width = 30.0
bwf_plank_height = 20.0
bwf_d_plank_width = 30.0
bwf_d_plank_height = 10.0
bwf_crenel_depth = 5.0
bwf_wall_diagonal_size = 50.0
bwf_tobo_diagonal_size = 100.0
bwf_diagonal_lining_top_height = 20.0
bwf_diagonal_lining_bottom_height = 20.0
bwf_module_width = 1
bwf_reamer_radius = 2.0
bwf_cutting_extra = 2.0 # doesn't affect the cnc cutting plan
bwf_slab_thickness = 0.0 # set it bigger than 0 if you want to get the slab too
bwf_output_file_basename = "" # set a not-empty string if you want to generate the output files
#bwf_output_file_basename = "my_output_dir/" 
#bwf_output_file_basename = "my_output_dir/my_output_basename" 
#bwf_output_file_basename = "my_output_basename" 



################################################################
# action
################################################################

bwf_assembly = box_wood_frame.box_wood_frame(bwf_box_width, bwf_box_depth, bwf_box_height,
                                              bwf_fitting_height, bwf_h_plank_width, bwf_v_plank_width, bwf_plank_height,
                                              bwf_d_plank_width, bwf_d_plank_height, bwf_crenel_depth,
                                              bwf_wall_diagonal_size, bwf_tobo_diagonal_size,
                                              bwf_diagonal_lining_top_height, bwf_diagonal_lining_bottom_height,
                                              bwf_module_width, bwf_reamer_radius, bwf_cutting_extra,
                                              bwf_slab_thickness, bwf_output_file_basename)
Part.show(bwf_assembly)
"""

ceg_example_list={
  bwf_script_name : bwf_script_content
}

for l_example in ceg_example_list.keys():
  print("cnc25d script example : {:s}".format(l_example))
  user_choice=raw_input("Do you want to generate the file {:s} in the current directory? [yes/No] ".format(l_example))
  if((user_choice=='yes')or(user_choice=='y')):
    fh_output = open(l_example, 'w')
    fh_output.write(ceg_example_list[l_example])
    fh_output.close()
    print(ceg_instructions.format(l_example, l_example, l_example))
  else:
    print("Nothing done.")


