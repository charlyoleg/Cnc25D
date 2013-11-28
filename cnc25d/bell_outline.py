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
#
# cnc25d
import small_geometry

################################################################
# bell_face
################################################################

def bell_face_outline(ai_c):
  """ generate the external-outline (type-a) of the bell_face part
  """
  ### leg slope inclination angle
  lAB = ai_c['bell_face_width']/2.0 - ai_c['leg_spare_width']
  lBC = ai_c['leg_length']
  lCD = ai_c['axle_external_radius']
  lAC = math.sqrt(lAB**2+lBC**2)
  cos_aBAC = float(lAB)/lAC
  if(abs(cos_aBAC)>1):
    print("ERR063: Error, cos_aBAC {:0.3f} is out of the range -1..1".format(cos_aBAC))
    print("dbg064: lAC {:0.3f}  lAB {:0.3f}".format(lAC, lAB))
    sys.exit(2)
  aBAC = math.acos(cos_aBAC)
  #lAD = math.sqrt(lAC**2-lCD**2)
  aCAD = math.asin(float(lCD)/lAC)
  leg_inclination_angle = aBAC + aCAD # aBAD
  leg_ext_axle_angle = math.pi/2 - leg_inclination_angle
  #print("dbg072: leg_inclination_angle {:0.3f}  leg_ext_axle_angle {:0.3f}".format(leg_inclination_angle, leg_ext_axle_angle))
  #print("dbg073: aBAC {:0.3f}  aCAD {:0.3f}  lAC {:0.3f}".format(aBAC, aCAD, lAC))
  ### smoothing leg
  # coordiante of A
  Ax = -1*ai_c['bell_face_width']/2.0 + ai_c['leg_spare_width']
  Ay = ai_c['base_thickness'] + ai_c['bell_face_height']
  # coordiante of C
  Dx = -1*ai_c['axle_external_radius']*math.cos(leg_ext_axle_angle)
  Dy = ai_c['base_thickness'] + ai_c['bell_face_height'] + ai_c['leg_length'] + ai_c['axle_external_radius']*math.sin(leg_ext_axle_angle)
  # coordiante of E
  Ex = -1*ai_c['bell_face_width']/2.0
  Ey = ai_c['base_thickness'] + ai_c['bell_face_height']
  # equation of the line AC
  (AClx, ACly, ACk, lAC, xAC) = small_geometry.line_equation((Ax,Ay), (Dx,Dy), "line_AC")
  # coordinate of F
  (FX, FY, ACkF) = small_geometry.line_distance_point((Ax,Ay), (Dx,Dy), ai_c['leg_smoothing_radius'], "point_F")
  # coordinate of G
  (Gx, Gy, line_circle_intersection_status) = small_geometry.line_circle_intersection((AClx, ACly, ACkF), (Ex, Ey), ai_c['leg_smoothing_radius'], (Dx, Dy), math.pi/2, "point_G")
  ### intermediate parameters
  axle_center_y = ai_c['base_thickness']+ai_c['bell_face_height']+ai_c['leg_length']
  bell_face_height_5 = ai_c['bell_face_height']/5.0
  bell_face_width_10 = ai_c['bell_face_width']/10.0
  bell_face_width_2 = ai_c['bell_face_width']/2.0
  ect = ai_c['extra_cut_thickness']
  st = ai_c['side_thickness']
  bt = ai_c['base_thickness']
  ### bell_face_outline
  r_ol = []
  r_ol.append((bell_face_width_2,                        ai_c['base_thickness']+ai_c['bell_face_height'], 0)) # top-right, CCW
  r_ol.append((bell_face_width_2-ai_c['leg_spare_width'], ai_c['base_thickness']+ai_c['bell_face_height'], 0)) # leg
  r_ol.append((ai_c['axle_external_radius']*math.cos(leg_ext_axle_angle), axle_center_y+ai_c['axle_external_radius']*math.sin(leg_ext_axle_angle), 0)) # axle
  r_ol.append((0, axle_center_y+ai_c['axle_external_radius'], -1*ai_c['axle_external_radius']*math.cos(leg_ext_axle_angle), axle_center_y+ai_c['axle_external_radius']*math.sin(leg_ext_axle_angle), 0))
  r_ol.append((-1*bell_face_width_2+ai_c['leg_spare_width'], ai_c['base_thickness']+ai_c['bell_face_height'], 0)) # leg
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+ai_c['bell_face_height'], 0)) # left-side
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+ai_c['bell_face_height'], 0))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+4*bell_face_height_5+ect, 0))
  r_ol.append((-1*bell_face_width_2+st+ect, ai_c['base_thickness']+4*bell_face_height_5+ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((-1*bell_face_width_2+st+ect, ai_c['base_thickness']+3*bell_face_height_5-ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+3*bell_face_height_5-ect, 0))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+2*bell_face_height_5+ect, 0))
  r_ol.append((-1*bell_face_width_2+st+ect, ai_c['base_thickness']+2*bell_face_height_5+ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((-1*bell_face_width_2+st+ect, ai_c['base_thickness']+1*bell_face_height_5-ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+1*bell_face_height_5-ect, 0))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+ect, 0)) # bottom
  r_ol.append((-3*bell_face_width_10+ect, ai_c['base_thickness']+ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((-3*bell_face_width_10+ect, 0, 0))
  r_ol.append((-1*bell_face_width_10-ect, 0, 0))
  r_ol.append((-1*bell_face_width_10-ect, ai_c['base_thickness']+ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((1*bell_face_width_10+ect, ai_c['base_thickness']+ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((1*bell_face_width_10+ect, 0, 0))
  r_ol.append((3*bell_face_width_10-ect, 0, 0))
  r_ol.append((3*bell_face_width_10-ect, ai_c['base_thickness']+ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+ect, 0)) # right-side
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+1*bell_face_height_5-ect, 0))
  r_ol.append((bell_face_width_2-(st+ect), ai_c['base_thickness']+1*bell_face_height_5-ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2-(st+ect), ai_c['base_thickness']+2*bell_face_height_5+ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+2*bell_face_height_5+ect, 0))
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+3*bell_face_height_5-ect, 0))
  r_ol.append((bell_face_width_2-(st+ect), ai_c['base_thickness']+3*bell_face_height_5-ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2-(st+ect), ai_c['base_thickness']+4*bell_face_height_5+ect, -1*ai_c['cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+4*bell_face_height_5+ect, 0))
  r_ol.append((r_ol[0][0], r_ol[0][1], 0)) # close
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


