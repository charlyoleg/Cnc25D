# design_help.py
# small help functions for design scripts
# created by charlyoleg on 2013/08/27
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
design_help.py is part of the Cnc25D API.
it provides macros that are commonly used in design scripts
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
#import math
import sys, argparse
#from datetime import datetime
import os, errno
#import re
#import Tkinter # to display the outline in a small GUI
# FreeCAD
#import Part
#from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
#import outline_backends
#import export_2d


################################################################
# help functions
################################################################

################################################################
# functions to be reused
################################################################

def mkdir_p(ai_directory):
  """ Create the directory if needed and possible
  """
  r_status = 2
  if(ai_directory!=''):
    #print("dbg448: ai_directory:", ai_directory)
    # mkdir -p directory if needed
    print("dbg450: try to create the output directory: {:s}".format(ai_directory))
    try:
      os.makedirs(ai_directory)
      r_status = 0
    except OSError as exc:
      if exc.errno == errno.EEXIST and os.path.isdir(ai_directory):
        pass
      else:
        raise
  return(r_status)

def get_effective_args(ai_default_args):
  """ Find the args to be processed by the parser.
      Use sys.argv, but if empty then use ai_default_args
      let run your script with python and freecad
  """
  # this ensure the possible to use the script with python and freecad
  # You can not use argparse and FreeCAD together, so it's actually useless !
  # Running this script, FreeCAD will just use the argparse default values
  arg_index_offset=0
  if(sys.argv[0]=='freecad'): # check if the script is used by freecad
    arg_index_offset=1
    if(len(sys.argv)>=2):
      if(sys.argv[1]=='-c'): # check if the script is used by freecad -c
        arg_index_offset=2
  r_effective_args = sys.argv[arg_index_offset+1:]
  if(len(r_effective_args)==0):
    r_effective_args = ai_default_args
  #print("dbg115: r_effective_args:", str(r_effective_args))
  #FreeCAD.Console.PrintMessage("dbg116: r_effective_args: %s\n"%(str(r_effective_args)))
  return(r_effective_args)

################################################################
# test-functions
################################################################


