# importing_cnc25d.py
# it helps to let the test scripts find the cnc25d package
# created by charlyoleg on 2013/06/03
# license: CC BY SA 3.0

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

