#!/usr/bin/python
#
# cnc25d_example_generator.py
# it generates examples of python scripts that use the cnc25d package
# created by charlyoleg on 2013/06/03
# license: CC BY SA 3.0

"""
cnc25d_example_generator.py is the unique binary delivered with the Cnc25D distribution. It aims at generating script examples that use the cnc25d package.
In addition, it checks if FreeCAD is correctly installed on the host computer.
"""

##############################################################################
# import
##############################################################################

import os, re, sys
import subprocess

##############################################################################
# Checking FreeCAD installation
##############################################################################

### check if FreeCAD exists and checks the version number

# create a tempory script that checks the FreeCAD versions
checking_freecad_version_script = """
import sys
freecad_version = FreeCAD.Version()
FreeCAD.Console.PrintMessage("FREECAD_VERSION_START{:s}FREECAD_VERSION_STOP".format(freecad_version))
sys.exit(0)
"""
# We don't use the /tmp directory for an easier compatibility with windows
checking_freecad_version_script_name = "tmp_checking_freecad_version.py"
fh_output = open(checking_freecad_version_script_name, 'w')
fh_output.write(checking_freecad_version_script)
fh_output.close()
l_cmdline = "freecad -c {:s}".format(checking_freecad_version_script_name)
#print("dbg226: l_cmdline:", l_cmdline)
try:
  #freecad_return_code = subprocess.call(l_cmdline.split(' '), stdin=None, stdout=None, stderr=None, shell=False)
  freecad_output = subprocess.check_output(l_cmdline.split(' '), stdin=None, stderr=None, shell=False)
except:
  print("ERR054: Error, FreeCAD is not installed on your system!")
  print("Please, install the latest FreeCAD version on your system and re-run this script.")
  sys.exit(1)
# remove the tempory script
os.remove(checking_freecad_version_script_name)
#print("dbg111: freecad_return_code:", freecad_return_code)
#print("dbg112: freecad_output:", freecad_output)
# extract the verion from the freecad_output
freecad_verion = re.sub(r'\n', '', freecad_output, re.DOTALL)
freecad_verion = re.sub(r'^.*FREECAD_VERSION_START\[', '', freecad_verion, re.DOTALL) 
freecad_verion = re.sub(r'\]FREECAD_VERSION_STOP.*$', '', freecad_verion, re.DOTALL)
freecad_verion = re.sub(r",\s+'", ",'", freecad_verion, re.DOTALL)
freecad_verion = re.sub(r"'", "", freecad_verion, re.DOTALL)
freecad_verion = freecad_verion.split(',')
#print("dbg113: freecad_verion:", freecad_verion)
freecad_verion_major = int(freecad_verion[0])
freecad_verion_minor = int(freecad_verion[1])
if((freecad_verion_major==0)and(freecad_verion_minor<13)):
  print("ERR056: Error, Your FreeCAD version is too old! You have {:d}.{:d} and 0.13 or newer is needed.".format(freecad_verion_major, freecad_verion_minor))
  print("Please, install the latest FreeCAD version on your system and re-run this script.")
  sys.exit(1)
#info
print("The FreeCAD version {:d}.{:d} is installed on your system.".format(freecad_verion_major, freecad_verion_minor))

### check if the FreeCAD Library can be imported

try:
  import importing_freecad
except:
  print("ERR058: Error, cnc25d package is not installed!")
  print("Please, install the cnc25d package with the command 'sudo pip install Cnc25D -U'")
  sys.exit(1)

importing_freecad.importing_freecad()

try:
  FreeCAD.Console.PrintMessage("FreeCAD run from Cnc25D :)\n")
except:
  print("ERR060: Error, the package cnc25d can not use the FreeCAD library")
  sys.exit(1)

##############################################################################
# Creating the script example
##############################################################################
ceg_instructions="""
The example script {:s} has been created :)
To use it, just run the following command:
> python {:s}
You can rename, move, copy and edit the script {:s}
"""

### box_wood_frame script example

bwf_script_name="box_wood_frame_example.py"

# copy from ../cnc25d/tests/box_wood_frame_example.py without the import stuff
bwf_script_content="""
#!/usr/bin/python
#
# box_wood_frame_macro.py
# the macro for a wood frame for building a shell or a straw house.
# created by charlyoleg on 2013/05/31
# license: CC BY SA 3.0

################################################################
# Installation
################################################################
# This script needs freecad (http://www.freecadweb.org/) installed on your system
# With Ubuntu, run the following command
# > sudo apt-get install freecad
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# add to sys.path path to the cnc25d package
################################################################

import importing_cnc25d

#import sys, os
##getcwd_dir = os.getcwd()
##print("dbg191: getcwd_dir:", getcwd_dir)
#file_dir= os.path.dirname(__file__)
##print("dbg192: file_dir:", file_dir)
##argv_dir= os.path.dirname(sys.argv[0])
##print("dbg193: argv_dir:", argv_dir)
#
#test_script_dir=file_dir
#if(test_script_dir==''):
#  test_script_dir='.'
#sys.path.append(test_script_dir+'/../..')

################################################################
# header for Python / FreeCAD compatibility
################################################################

from cnc25d import importing_freecad
importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

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

### Generating the script example

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
    print("The script example {:s} has not been created.".format(l_example))


