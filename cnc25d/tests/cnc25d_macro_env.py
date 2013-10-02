#!/usr/bin/env python
#
# cnc25d_macro_env.py
# Run a macro python script after importing the cnc25d package
# created by charlyoleg on 2013/09/28
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

# 

"""
cnc25d_macro_env.py lets run a macro python script with the appropriate sys.path
Usage:
> python cnc25d_macro_env.py my_script_macro.py
"""

### get the macro script path
import sys, os.path

if(len(sys.argv)!=2):
  print("ERR036: Error, cnc25d_macro_env.py requires one argument. Given {:d}".format(len(sys.argv)-1))
  sys.exit(2)
macro_path = sys.argv[1]
if(not os.path.isfile(macro_path)):
  print("ERR040: Error, {:s} is not a Python script!".format(macro_path))
  sys.exit(2)

### complete sys.path to access the cnc25d package
#import importing_cnc25d
#getcwd_dir = os.getcwd()
#print("dbg191: getcwd_dir:", getcwd_dir)
file_dir= os.path.dirname(__file__)
#print("dbg192: file_dir:", file_dir)
#argv_dir= os.path.dirname(sys.argv[0])
#print("dbg193: argv_dir:", argv_dir)

macro_script_dir=file_dir
if(macro_script_dir==''):
  macro_script_dir='.'
sys.path.append(macro_script_dir+'/../..')
#sys.path.append('./../..') # this work only if you launch the script from its own directory

### run the macro
#import macro_path # import statement doesn't accept path variable
execfile(macro_path)

