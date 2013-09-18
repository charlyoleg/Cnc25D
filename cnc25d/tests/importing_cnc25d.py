# importing_cnc25d.py
# it helps to let the test scripts find the cnc25d package
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
importing_cnc25d completes sys.path to give access to the cnc25d package
"""

import sys, os
#getcwd_dir = os.getcwd()
#print("dbg191: getcwd_dir:", getcwd_dir)
file_dir= os.path.dirname(__file__)
#print("dbg192: file_dir:", file_dir)
#argv_dir= os.path.dirname(sys.argv[0])
#print("dbg193: argv_dir:", argv_dir)

test_script_dir=file_dir
if(test_script_dir==''):
  test_script_dir='.'
sys.path.append(test_script_dir+'/../..')
#sys.path.append('./../..') # this work only if you launch the script from its own directory

