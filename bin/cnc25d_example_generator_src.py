#!/usr/bin/env python
#
# cnc25d_example_generator.py
# it generates examples of python scripts that use the cnc25d package
# created by charlyoleg on 2013/06/03
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
bwf_script_name="eg01_box_wood_frame_example.py"
# copy from ../cnc25d/tests/box_wood_frame_macro.py without the import stuff
bwf_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/box_wood_frame_macro.py
#
#include "../cnc25d/tests/box_wood_frame_macro.py"
'''

### cnc25d_api_example script
cgf_script_name="eg03_cnc25d_api_example.py"
# copy from ../cnc25d/tests/cnc25d_api_macro.py
cgf_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/cnc25d_api_macro.py
#
#include "../cnc25d/tests/cnc25d_api_macro.py"
'''

### simple_cnc25d_api_example script
sca_script_name="eg02_simple_cnc25d_api_example.py"
# copy from ../cnc25d/tests/simple_cnc25d_api_macro.py
sca_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/simple_cnc25d_api_macro.py
#
#include "../cnc25d/tests/simple_cnc25d_api_macro.py"
'''

### gear_profile script example
gp_script_name="eg04_gear_profile_example.py"
# copy from ../cnc25d/tests/gear_profile_macro.py
gp_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gear_profile_macro.py
#
#include "../cnc25d/tests/gear_profile_macro.py"
'''

### gearwheel script example
gw_script_name="eg05_gearwheel_example.py"
# copy from ../cnc25d/tests/gearwheel_macro.py
gw_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gearwheel_macro.py
#
#include "../cnc25d/tests/gearwheel_macro.py"
'''

### gearring script example
gr_script_name="eg06_gearring_example.py"
# copy from ../cnc25d/tests/gearring_macro.py
gr_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gearring_macro.py
#
#include "../cnc25d/tests/gearring_macro.py"
'''

### gearbar script example
gb_script_name="eg07_gearbar_example.py"
# copy from ../cnc25d/tests/gearbar_macro.py
gb_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/gearbar_macro.py
#
#include "../cnc25d/tests/gearbar_macro.py"
'''

### split_gearwheel script example
sgw_script_name="eg08_split_gearwheel_example.py"
# copy from ../cnc25d/tests/split_gearwheel_macro.py
sgw_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/split_gearwheel_macro.py
#
#include "../cnc25d/tests/split_gearwheel_macro.py"
'''

### epicyclic_gearing script example
eg_script_name="eg09_epicyclic_gearing_example.py"
# copy from ../cnc25d/tests/epicyclic_gearing_macro.py
eg_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/epicyclic_gearing_macro.py
#
#include "../cnc25d/tests/epicyclic_gearing_macro.py"
'''

### axle_lid script example
al_script_name="eg10_axle_lid_example.py"
# copy from ../cnc25d/tests/axle_lid_macro.py
al_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/axle_lid_macro.py
#
#include "../cnc25d/tests/axle_lid_macro.py"
'''

### motor_lid script example
ml_script_name="eg11_motor_lid_example.py"
# copy from ../cnc25d/tests/motor_lid_macro.py
ml_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/motor_lid_macro.py
#
#include "../cnc25d/tests/motor_lid_macro.py"
'''

### bell script example
bell_script_name="eg12_bell_example.py"
# copy from ../cnc25d/tests/bell_macro.py
bell_script_content='''#!/usr/bin/env python
#
# copy/paste of cnc25d/tests/bell_macro.py
#
#include "../cnc25d/tests/bell_macro.py"
'''

### Generating the script examples

ceg_example_list={
  bwf_script_name : bwf_script_content,
  cgf_script_name : cgf_script_content,
  sca_script_name : sca_script_content,
  gp_script_name : gp_script_content,
  gw_script_name : gw_script_content,
  gr_script_name : gr_script_content,
  gb_script_name : gb_script_content,
  sgw_script_name : sgw_script_content,
  eg_script_name : eg_script_content,
  al_script_name : al_script_content,
  ml_script_name : ml_script_content,
  bell_script_name : bell_script_content}

ceg_example_list_sorted_keys = sorted(ceg_example_list.keys())
print("\nThis executable helps you to generate the following cnc25d script examples in the current directory:")
for l_example in ceg_example_list_sorted_keys:
  print("  +  {:s}".format(l_example))
user_choice=raw_input("Do you want to generate all these upper files in the current directory? [yes/No] ")
if((user_choice=='yes')or(user_choice=='y')):
  for l_example in ceg_example_list_sorted_keys:
    fh_output = open(l_example, 'w')
    fh_output.write(ceg_example_list[l_example])
    fh_output.close()
  print("All cnc25d script examples have been created in the current directory :)")
else:
  print("Choose which cnc25d script example you want to generate in the current directory:")
  for l_example in ceg_example_list_sorted_keys:
    print("cnc25d script example : {:s}".format(l_example))
    user_choice=raw_input("Do you want to generate the file {:s} in the current directory? [yes/No] ".format(l_example))
    if((user_choice=='yes')or(user_choice=='y')):
      fh_output = open(l_example, 'w')
      fh_output.write(ceg_example_list[l_example])
      fh_output.close()
      print(ceg_instructions.format(l_example, l_example, l_example))
    else:
      print("The script example {:s} has not been created.".format(l_example))


