#!/usr/bin/python

# -*- coding:utf-8 -*-

# apply_license_on_python_script.py
# modify a python script to replace the inappropriate CC license with the LGPL license
# created by charlyoleg on 2013/08/12
#
# (C) Copyright 2013 charlyoleg
#
# This file is part of the Cnc25D Python package.
# 
# Cnc25D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cnc25D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Cnc25D.  If not, see <http://www.gnu.org/licenses/>.


"""
apply_license_on_python_script.py reads a script passed as argument, looks for the statement '# license: CC BY SA 3.0' and replaces it with the LGPL license.
"""

##########################################################################
# import and global function definiton
##########################################################################

import sys, re, os

apply_license_on_python_script_usage = """
apply_license_on_python_script_usage.py usage:
> apply_license_on_python_script_usage.py MyScript1.py MyScript2.py
"""

cc_license = '# license: CC BY SA 3.0'

lgpl_license = """#
# (C) Copyright 2013 charlyoleg
#
# This file is part of the Cnc25D Python package.
# 
# Cnc25D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cnc25D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Cnc25D.  If not, see <http://www.gnu.org/licenses/>.
"""

##########################################################################
# functions
##########################################################################

def replace_license_CC2LGPL(ai_txt, ai_filename):
  """
  Looks for the CC license and replace it with the LGPL license
  """
  r_out_txt = ''
  txt_per_line = ai_txt.splitlines()
  license_replaced = 0
  line_nb = 0
  for i_line in txt_per_line:
    line_nb += 1
    #print("dbg 101: {:d} : {:s}".format(line_nb, i_line))
    if(re.search(r'license', i_line)):
      if(i_line==cc_license):
        print("Info: Replace the CC license with a LGPL license at line {:d} in {:s}".format(line_nb, ai_filename))
        r_out_txt += lgpl_license
        license_replaced = 1
      else:
        print("WARN015: Warning, ambigous license statement at line {:d} in {:s}".format(line_nb, ai_filename))
        r_out_txt += i_line
    else:
      r_out_txt += i_line 
    r_out_txt += '\n'
  if(license_replaced==0):
    print("WARN417: Warning, No license has been replaced because no license CC has been found in {:s}!".format(ai_filename))
  return(r_out_txt)

##########################################################################
# main function
##########################################################################

def apply_license_on_python_script(ai_args):
  """
  main function of apply_license_on_python_script.py
  it takes as argument the list of the python scripts to be modified.
  """
  if(len(ai_args) < 1):
    print("ERR233: Error, apply_license_on_python_script takes at least one argument. %d arguments given!"%len(ai_args))
    print(apply_license_on_python_script_usage)
    sys.exit(1)
  input_filenames = ai_args
  for input_file in input_filenames:
    if(not os.path.exists(input_file)):
      print("ERR774: Error, the input file {:s} doesn't exist!".format(input_file))
      sys.exit(1)
    ifh = open(input_file, 'r')
    input_content = ifh.read()
    ifh.close()
    output_content = replace_license_CC2LGPL(input_content, input_file)
    ofh = open(input_file, 'w')
    ofh.write(output_content)
    ofh.close()
    print("The file {:s} has been modified :)".format(input_file))

##########################################################################
# main
##########################################################################

if __name__ == "__main__":
  apply_license_on_python_script(sys.argv[1:])

