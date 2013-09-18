#!/usr/bin/env python
#
# cnc25d_api_test.py
# test the cnc25d_api_macro.py which is included in bin/cnc25d_example_generator.py
# created by charlyoleg on 2013/06/13
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
cnc25d_api_test.py lets run the script cnc25d_api_macro.py with the appropriate sys.path
Running this script is a quick test to check that the package cnc25d code is running.
"""

# complete sys.path to access the cnc25d package
import importing_cnc25d

# run the macro
import cnc25d_api_macro


