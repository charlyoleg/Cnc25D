#!/usr/bin/python
#
# gearwheel_test.py
# test the gearwheel_macro.py which is included in bin/cnc25d_example_generator.py
# created by charlyoleg on 2013/06/19
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

# 

"""
gearwheel_test.py lets run the script gearwheel_macro.py with the appropriate sys.path
Running this script is a quick test to check that the package cnc25d code is running.
"""

# complete sys.path to access the cnc25d package
import importing_cnc25d

# run the macro
import gearwheel_macro

