# setup.py
# generates a Python package using setuptools
# created by charlyoleg on 2013/09/11
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

from setuptools import setup, find_packages

setup(
  name='Cnc25D',
  version='0.1.8',
  author='charlyoleg',
  author_email='charlyoleg@fabfolk.com',
  #packages=['cnc25d', 'cnc25d.tests'],
  packages=find_packages(),
  scripts=['bin/cnc25d_example_generator.py'],
  url='http://pypi.python.org/pypi/Cnc25D/',
  license='LICENSE.txt',
  description='CAD library for 2.5D parts (including gears) using svgwrite, dxfwrite or FreeCAD as backend',
  long_description=open('README.rst').read(),
  keywords="CNC 2.5D FreeCAD 3D gear",
  install_requires=[
    #"math >= 0.6.24",
    #"sys >= 0.1.6",
    "argparse >= 1.2.1",
    #"datetime >= 0.6.24", # datetime is a builtin module
    #"os >= 0.0.0",
    #"errno >= 0.0.0",
    #"Tkinter >= 0.0.0",
    #"tkMessageBox >= 0.0.0",
    "numpy >= 1.7.1",
    #"matplotlib >= 1.3.0",  # currently disable because of a bug in matplotlib setup.py about numpy dependency
    "svgwrite >= 1.1.2",
    "dxfwrite >= 1.2.0",
    #"timeit >= 0.0.0",
    #"cProfile >= 0.0.0",
    #"time >= 0.0.0",
  ],
)


