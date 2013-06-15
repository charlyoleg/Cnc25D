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

#print("dbg449: sys.path:", sys.path)

try:
  import cnc25d.importing_freecad
except:
  print("ERR058: Error, cnc25d package is not installed!")
  print("Please, install the cnc25d package with the command 'sudo pip install Cnc25D -U'")
  sys.exit(1)

cnc25d.importing_freecad.importing_freecad()

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
bwf_script_content='''#!/usr/bin/python
#
# copy/paste of cnc25d/tests/box_wood_frame_macro.py
#
#include "../cnc25d/tests/box_wood_frame_macro.py"
'''

### cnc25d_api_example script

cgf_script_name="cnc25d_api_example.py"

# copy from ../cnc25d/tests/cnc25d_api_macro.py without the import stuff
cgf_script_content='''#!/usr/bin/python
#
# copy/paste of cnc25d/tests/cnc25d_api_macro.py
#
#include "../cnc25d/tests/cnc25d_api_macro.py"
'''

### Generating the script examples

ceg_example_list={
  bwf_script_name : bwf_script_content,
  cgf_script_name : cgf_script_content}

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


