#!/usr/bin/python
#
# gearwheel_test.py
# test the gearwheel_macro.py which is included in bin/cnc25d_example_generator.py
# created by charlyoleg on 2013/06/19
# license: CC BY SA 3.0
# 

"""
gearwheel_test.py lets run the script gearwheel_macro.py with the appropriate sys.path
Running this script is a quick test to check that the package cnc25d code is running.
"""

# complete sys.path to access the cnc25d package
import importing_cnc25d

# run the macro
import gearwheel_macro

