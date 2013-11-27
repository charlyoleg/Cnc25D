# bell_outline.py
# generates the bell-outline for bell.py
# created by charlyoleg on 2013/11/27
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
bell_outline.py generates the A-outlines for the bell-design. This is a sub-module for bell.py
It has been created to split the too large bell.py file into two smaller files, easier for editing.
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import cnc25d_api
#cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

import math
#import sys
#import Tkinter # to display the outline in a small GUI
#
#import Part
#from FreeCAD import Base

################################################################
# bell_face
################################################################

def bell_face_outline(ai_c):
  """ generate the external-outline (type-a) of the bell_face part
  """
  r_ol = []
  r_ol = (0.0, 0.0, ai_c['bell_face_width']/2.0)
  return(r_ol)

def bell_face_holes(ai_c):
  """ generate the hole-outlines (type-a) of the bell_face part
  """
  r_f = []
  return(r_f)

def bell_face(ai_c):
  """ generate the A-outline figure of the bell_face part
  """
  r_f = []
  r_f.append(bell_face_outline(ai_c))
  r_f.extend(bell_face_holes(ai_c))
  return(r_f)

################################################################
# bell_side
################################################################

def bell_side_outline(ai_c):
  """ generate the external-outline (type-a) of the bell_side part
  """
  r_ol = []
  r_ol = (0.0, 0.0, ai_c['bell_face_width']/2.0)
  return(r_ol)

def bell_side_holes(ai_c):
  """ generate the hole-outlines (type-a) of the bell_side part
  """
  r_f = []
  return(r_f)

def bell_side(ai_c):
  """ generate the A-outline figure of the bell_side part
  """
  r_f = []
  r_f.append(bell_side_outline(ai_c))
  r_f.extend(bell_side_holes(ai_c))
  return(r_f)

################################################################
# bell_base
################################################################

def bell_base_main_hole_outline(ai_c):
  """ generate the A-outline of the main hole of the bell_base part
  """
  r_ol = []
  r_ol = (0.0, 0.0, 10.0)
  return(r_ol)

def bell_base_holes(ai_c):
  """ generate the hole-outlines (type-a) of the bell_base part
  """
  r_f = []
  return(r_f)

def bell_base(ai_c):
  """ generate the A-outline figure of the bell_base part
  """
  r_f = []
  r_f.append((0.0, 0.0, ai_c['base_radius']))
  r_f.append(bell_base_main_hole_outline(ai_c))
  r_f.extend(bell_base_holes(ai_c))
  return(r_f)

################################################################
# bell_internal_buttress
################################################################

def bell_internal_buttress(ai_c):
  """ generate the A-outline figure of the bell_internal_buttress part
  """
  r_f = []
  r_f.append((0.0, 0.0, ai_c['int_buttress_x_length']))
  return(r_f)

################################################################
# bell_external_buttress
################################################################

def bell_external_buttress(ai_c):
  """ generate the A-outline figure of the bell_external_buttress part
  """
  r_f = []
  r_f.append((0.0, 0.0, ai_c['ext_buttress_z_length']))
  return(r_f)


