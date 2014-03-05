# design_frontend.py
# functions for design scripts
# created by charlyoleg on 2014/02/24
#
# (C) Copyright 2014 charlyoleg
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
design_frontend.py is part of the Cnc25D API.
it provides functions that complete the bare_design class to create design scripts
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

#import importing_freecad
#importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

# Python standard library
import math
import sys
import re
#import argparse
#from datetime import datetime
#import os, errno
## cnc25d
#import outline_backends
#import export_2d


################################################################
# front-end functions and class
################################################################

################################################################
# function to check the constraint dictionary
################################################################

def check(constraint_dict={}, error_id="ERR000", error_msg='', constraint_dict_name='c', condition=None, warning_nerror=False):
  """ If the condition is False, print the error-message with the associated constraints and exit
      If the condition is set to None, the error_msg is evaluated
  """
  test_result = condition
  if(condition==None):
    #print("dbg068: eval(' {:s} ')".format(error_msg))
    eval_context = {constraint_dict_name:constraint_dict}
    test_result = eval(error_msg, eval_context)
    #print("dbg070: test_result {:d}".format(test_result))
  if(not test_result):
    msg_introduction = "Error on"
    if(warning_nerror):
      msg_introduction = "Warning on"
    #print("ERR073: Error on {:s} with:".format(error_msg))
    error_msg_without_dict = re.sub("'\]", " ", re.sub("{:s}\['".format(constraint_dict_name), " ", error_msg))
    print("{:s}: {:s} {:s} with:".format(error_id, msg_introduction, error_msg_without_dict))
    var_list = re.findall("{:s}\['\w+'\]".format(constraint_dict_name), error_msg)
    #print("dbg075: var_list:", var_list)
    for d_item in var_list:
      d_key = re.sub("'\].*$", "", re.sub("^.*\['", "", d_item))
      #d_key = re.sub("^.*\['(\w+)'\]$", "\1", d_item)
      #print("dbg078: d_key:", d_key)
      d_val = constraint_dict[d_key]
      print("{:s}['{:s}'] = {:s}".format(constraint_dict_name, d_key, str(d_val)))
    if(not warning_nerror):
      sys.exit(2)
    else:
      pass
      #print("Should exit with error status 2")
  return(0)

################################################################
# function and class to construct figures and outlines : move to draw_2d_frontend
################################################################
 


################################################################
# test-functions
################################################################

def test_check():
  """ test the API function check()
  """
  print("\nTest check()")
  c={'a':3, 'b':7.008, 'c1':15}
  check(c, "ERR104", "c['a']<c['b']", 'c', c['a']<c['b'])
  check(c, "ERR105", "c['a']>c['b']", 'c', c['a']>c['b'], warning_nerror=True)
  check(c, "ERR106", "c['a']>c['b']", warning_nerror=True)
  check(c, "ERR107", "c['a']>c['c1']", warning_nerror=True)


def design_frontend_self_test():
  """ check the design front-end fonctions
  """
  print("Non-regression tests of the design_frontend module")
  test_check()

################################################################
# main
################################################################

if __name__ == "__main__":
  design_frontend_self_test()



