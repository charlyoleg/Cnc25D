# positioning.py
# to place 3D parts in an assembly
# created by charlyoleg on 2013/07/17
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
positioning.py provides help functions to place 3D parts in an assembly
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import importing_freecad
importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

import Part
from FreeCAD import Base
import math
import sys, argparse
import design_output # just for get_effective_args()

################################################################
# Positioning API
################################################################

def place_plank(ai_plank_solid, ai_x_length, ai_y_width, ai_z_height, ai_flip, ai_orientation, ai_translate_x, ai_translate_y, ai_translate_z):
  """ After creating a plank, use this function to place it in a cuboid construction
  """
  r_placed_plank = ai_plank_solid
  #r_placed_plank = ai_plank_solid.copy()
  # flip
  flip_center_x = ai_x_length/2
  flip_center_y = ai_y_width/2
  flip_center_z = ai_z_height/2
  if(ai_flip=='i'):
    r_placed_plank.rotate(Base.Vector(flip_center_x, flip_center_y, flip_center_z),Base.Vector(0,0,1),0)
  elif(ai_flip=='x'):
    r_placed_plank.rotate(Base.Vector(flip_center_x, flip_center_y, flip_center_z),Base.Vector(1,0,0),180)
  elif(ai_flip=='y'):
    r_placed_plank.rotate(Base.Vector(flip_center_x, flip_center_y, flip_center_z),Base.Vector(0,1,0),180)
  elif(ai_flip=='z'):
    r_placed_plank.rotate(Base.Vector(flip_center_x, flip_center_y, flip_center_z),Base.Vector(0,0,1),180)
  else:
    print("ERR505: Error, the flip value %s doesn't exist! Use only: i,x,y,z."%ai_flip)
    sys.exit(2)
  # orientation
  if(ai_orientation=='xy'):
    r_placed_plank.rotate(Base.Vector(0, 0, 0),Base.Vector(0,0,1),0)
    r_placed_plank.translate(Base.Vector(0, 0, 0))
  elif(ai_orientation=='xz'):
    r_placed_plank.rotate(Base.Vector(0, 0, 0),Base.Vector(1,0,0),90)
    r_placed_plank.translate(Base.Vector(0, ai_z_height, 0))
  elif(ai_orientation=='yx'):
    r_placed_plank.rotate(Base.Vector(0, 0, 0),Base.Vector(0,0,1),90)
    r_placed_plank.translate(Base.Vector(ai_y_width, 0, 0))
  elif(ai_orientation=='yz'):
    r_placed_plank.rotate(Base.Vector(0, 0, 0),Base.Vector(0,0,1),90)
    r_placed_plank.rotate(Base.Vector(0, 0, 0),Base.Vector(0,1,0),90)
    r_placed_plank.translate(Base.Vector(0, 0, 0))
  elif(ai_orientation=='zx'):
    r_placed_plank.rotate(Base.Vector(0, 0, 0),Base.Vector(0,1,0),-90)
    r_placed_plank.rotate(Base.Vector(0, 0, 0),Base.Vector(0,0,1),-90)
    r_placed_plank.translate(Base.Vector(0, 0, 0))
  elif(ai_orientation=='zy'):
    r_placed_plank.rotate(Base.Vector(0, 0, 0),Base.Vector(0,1,0),-90)
    r_placed_plank.translate(Base.Vector(ai_z_height, 0, 0))
  else:
    print("ERR506: Error, the orientation value %s doesn't exist! Use only: xz,xy,yx,yz,zx,zy."%ai_orientation)
    sys.exit(2)
  # translation
  r_placed_plank.translate(Base.Vector(ai_translate_x, ai_translate_y, ai_translate_z))
  return(r_placed_plank)

################################################################
# API testing
################################################################

def test_plank():
  """ Plank example to test the place_plank function
  """
  r_plank = Part.makeBox(20,4,2)
  r_plank = r_plank.cut(Part.makeBox(5,3,4, Base.Vector(16,-1,-1), Base.Vector(0,0,1)))
  r_plank = r_plank.cut(Part.makeBox(3,6,2, Base.Vector(18,-1,1), Base.Vector(0,0,1)))
  #Part.show(r_plank)
  return(r_plank)

def positioning_test1():
  """ test the place_plank function
  """
  # test place_plank()
  #pp0 = test_plank()
  #Part.show(pp0)
  pp1 = place_plank(test_plank(), 20,4,2, 'i', 'xy', 300,0,0)
  Part.show(pp1)
  pp2 = place_plank(test_plank(), 20,4,2, 'x', 'xy', 300,30,0)
  Part.show(pp2)
  pp3 = place_plank(test_plank(), 20,4,2, 'y', 'xy', 300,60,0)
  Part.show(pp3)
  pp4 = place_plank(test_plank(), 20,4,2, 'z', 'xy', 300,90,0)
  Part.show(pp4)
  #pp4 = place_plank(test_plank(), 20,4,2, 'u', 'xy', 300,30,0)
  pp21 = place_plank(test_plank(), 20,4,2, 'i', 'xy', 350,0,0)
  Part.show(pp21)
  pp22 = place_plank(test_plank(), 20,4,2, 'i', 'xz', 350,30,0)
  Part.show(pp22)
  pp23 = place_plank(test_plank(), 20,4,2, 'i', 'yx', 350,60,0)
  Part.show(pp23)
  pp24 = place_plank(test_plank(), 20,4,2, 'i', 'yz', 350,90,0)
  Part.show(pp24)
  pp25 = place_plank(test_plank(), 20,4,2, 'i', 'zx', 350,120,0)
  Part.show(pp25)
  pp26 = place_plank(test_plank(), 20,4,2, 'i', 'zy', 350,150,0)
  Part.show(pp26)
  #pp27 = place_plank(test_plank(), 20,4,2, 'i', 'xx', 350,180,0)
  ##Part.show(pp1)
  r_test = 1
  return(r_test)

################################################################
# positioning command line interface
################################################################

def positioning_cli(ai_args=None):
  """ it is the command line interface of positioning.py when it is used in standalone
  """
  posi_parser = argparse.ArgumentParser(description='Test the positioning API')
  posi_parser.add_argument('--test1','--t1', action='store_true', default=False, dest='sw_test1',
    help='First test to check place_plank.')
  effective_args = design_output.get_effective_args(ai_args)
  posi_args = posi_parser.parse_args(effective_args)
  print("dbg111: start testing positioning.py")
  if(posi_args.sw_test1):
    positioning_test1()
  print("dbg999: end of script")
  
    

################################################################
# main
################################################################

# with freecad, the script is also main :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("dbg109: I'm main\n")
  #positioning_cli()
  positioning_cli("--test1".split())

