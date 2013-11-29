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
# bell_face_side_holes
################################################################
# the common holes of the bell_face and side_face

def bell_face_side_holes(ai_c, ai_type):
  """ generate the commone hole outlines of the bell_face and side_face
  """
  # drawing in the xy space
  ### select the wall
  if(ai_type=='face'):
    wall_thickness = ai_c['side_thickness']
    axle_hole_radius = ai_c['y_hole_radius']
    axle_hole_y_position = ai_c['y_hole_z_position']
    axle_hole_x_position = ai_c['y_hole_x_position']
  elif(ai_type=='side'):
    wall_thickness = ai_c['face_thickness']
    axle_hole_radius = ai_c['x_hole_radius']
    axle_hole_y_position = ai_c['x_hole_z_position']
    axle_hole_x_position = ai_c['x_hole_y_position']
  else:
    print("ERR065: Error, ")
    sys.exit(2)
  ### intermediate parameters
  int_buttress_x1 = -1*ai_c['bell_face_width']/2.0 + wall_thickness + ai_c['int_buttress_x_position']
  int_buttress_x2 = -1*int_buttress_x1 - ai_c['int_buttress_x_length']
  int_buttress_y1 = ai_c['base_thickness'] + ai_c['int_buttress_z_position']
  int_buttress_y2 = int_buttress_y1 + ai_c['int_buttress_z_distance']
  axle_hole_x = -1*ai_c['bell_face_width']/2.0 + wall_thickness + axle_hole_x_position
  axle_hole_y1 = int_buttress_y1 + axle_hole_y_position
  axle_hole_y2 = int_buttress_y2 + axle_hole_y_position
  ext_buttress_x1 = -1*ai_c['ext_buttress_x_distance']/2.0 - ai_c['ext_buttress_x_width']
  ext_buttress_x2 = ai_c['ext_buttress_x_distance']/2.0
  ext_buttress_y = ai_c['base_thickness'] + ai_c['ext_buttress_z_position']
  ### figure construction
  r_f =[]
  # internal_buttress
  if(ai_c['int_buttress_x_length']>0):
    for px in (int_buttress_x1, int_buttress_x2):
      for py in (int_buttress_y1, int_buttress_y2):
        ib_ol = []
        ib_ol.append((px+0*ai_c['int_buttress_x_length'], py+0*ai_c['int_buttress_z_width'], -1*ai_c['cnc_router_bit_radius']))
        ib_ol.append((px+1*ai_c['int_buttress_x_length'], py+0*ai_c['int_buttress_z_width'], -1*ai_c['cnc_router_bit_radius']))
        ib_ol.append((px+1*ai_c['int_buttress_x_length'], py+1*ai_c['int_buttress_z_width'], -1*ai_c['cnc_router_bit_radius']))
        ib_ol.append((px+0*ai_c['int_buttress_x_length'], py+1*ai_c['int_buttress_z_width'], -1*ai_c['cnc_router_bit_radius']))
        ib_ol.append((px+0*ai_c['int_buttress_x_length'], py+0*ai_c['int_buttress_z_width'], 0))
        r_f.append(ib_ol[:])
  # axle_hole
  if(axle_hole_radius>0):
    for px in (axle_hole_x, -1*axle_hole_x):
      for py in (axle_hole_y1, axle_hole_y2):
        r_f.append((px, py, axle_hole_radius))
  # external_buttress
  if(ai_c['ext_buttress_z_length']>0):
    for px in (ext_buttress_x1, ext_buttress_x2):
      eb_ol = []
      eb_ol.append((px+0*ai_c['ext_buttress_x_width'], ext_buttress_y+0*ai_c['ext_buttress_z_length'], -1*ai_c['cnc_router_bit_radius']))
      eb_ol.append((px+1*ai_c['ext_buttress_x_width'], ext_buttress_y+0*ai_c['ext_buttress_z_length'], -1*ai_c['cnc_router_bit_radius']))
      eb_ol.append((px+1*ai_c['ext_buttress_x_width'], ext_buttress_y+1*ai_c['ext_buttress_z_length'], -1*ai_c['cnc_router_bit_radius']))
      eb_ol.append((px+0*ai_c['ext_buttress_x_width'], ext_buttress_y+1*ai_c['ext_buttress_z_length'], -1*ai_c['cnc_router_bit_radius']))
      eb_ol.append((px+0*ai_c['ext_buttress_x_width'], ext_buttress_y+0*ai_c['ext_buttress_z_length'], 0))
      r_f.append(eb_ol[:])
  ### return
  return(r_f)

################################################################
# bell_face
################################################################

def bell_face_outline(ai_c):
  """ generate the external-outline (type-a) of the bell_face part
  """
  ### precision
  radian_epsilon = math.pi/1000
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
  if(ai_c['leg_spare_width']>0):
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
    # coordinate of F: the point at the distance leg_smoothing_radius of AC an A
    (FX, FY, ACkF) = small_geometry.line_distance_point((Ax,Ay), (Dx,Dy), ai_c['leg_smoothing_radius'], "point_F")
    # coordinate of G: the intersection of the circle of center E and radius leg_smoothing_radius and the line parallet to AC passing through F
    (Gx, Gy, line_circle_intersection_status) = small_geometry.line_circle_intersection((AClx, ACly, ACkF), (Ex, Ey), ai_c['leg_smoothing_radius'], (Dx, Dy), math.pi/2, "point_G")
    # coordinate of H: projection of G on the line (AC)
    (Hx, Hy) = small_geometry.line_point_projection((AClx, ACly, ACk), (Gx, Gy), "point_H")
    # angle (Gx, GH)
    axGH = math.atan2(Hy-Gy, Hx-Gx)
    if(abs(axGH+leg_ext_axle_angle)>radian_epsilon): # check axGH
      print("ERR097: Error, axGH {:0.3f} is not equal to -1*leg_ext_axle_angle {:0.3f}".format(axGH, leg_ext_axle_angle))
      sys.exit(2)
    # angle (Gx, GE)
    axGE = math.atan2(Ey-Gy, Ex-Gx)
    # angle (Gx, GI)
    axGI = (axGH+axGE)/2.0
    # coordinate of I
    Ix = Gx + math.cos(axGI)*ai_c['leg_smoothing_radius']
    Iy = Gy + math.sin(axGI)*ai_c['leg_smoothing_radius']
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
  #r_ol.append((bell_face_width_2-ai_c['leg_spare_width'], ai_c['base_thickness']+ai_c['bell_face_height'], 0)) # leg
  if(ai_c['leg_spare_width']>0):
    r_ol.append((-1*Ix, Iy, -1*Hx, Hy, 0))
  r_ol.append((ai_c['axle_external_radius']*math.cos(leg_ext_axle_angle), axle_center_y+ai_c['axle_external_radius']*math.sin(leg_ext_axle_angle), 0)) # axle
  r_ol.append((0, axle_center_y+ai_c['axle_external_radius'], -1*ai_c['axle_external_radius']*math.cos(leg_ext_axle_angle), axle_center_y+ai_c['axle_external_radius']*math.sin(leg_ext_axle_angle), 0))
  #r_ol.append((-1*bell_face_width_2+ai_c['leg_spare_width'], ai_c['base_thickness']+ai_c['bell_face_height'], 0)) # leg
  if(ai_c['leg_spare_width']>0):
    r_ol.append((Hx, Hy, 0))
    r_ol.append((Ix, Iy, -1*bell_face_width_2, ai_c['base_thickness']+ai_c['bell_face_height'], 0))
  else:
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
  # intermediate parameters
  axle_y = ai_c['base_thickness']+ai_c['bell_face_height']+ai_c['leg_length']
  # axle_internal_hole
  if(ai_c['axle_internal_radius']>0):
    r_f.append((0, axle_y, ai_c['axle_internal_radius']))
  # axle_fastening_holes
  for i in  range(ai_c['axle_hole_nb']):
    a = i*2*math.pi/ai_c['axle_hole_nb']+ai_c['axle_hole_angle']
    r_f.append((ai_c['axle_hole_position_radius']*math.cos(a), axle_y+ai_c['axle_hole_position_radius']*math.sin(a), ai_c['axle_hole_radius']))
  # motor_fastening_holes
  if(ai_c['motor_hole_radius']>0):
    motor_x = ai_c['motor_hole_x_distance']/2.0
    motor_y1 = axle_y - ai_c['motor_hole_z_position']
    motor_y2 = motor_y1 - ai_c['motor_hole_z_distance']
    for px in [-motor_x, motor_x]:
      for py in [motor_y1, motor_y2]:
        r_f.append((px, py, ai_c['motor_hole_radius']))
  # int_buttress, ext_buttress, axis_fastening
  r_f.extend(bell_face_side_holes(ai_c, 'face'))
  # return
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
  ### figure construction
  r_f = []
  # base_fastening_holes
  for i in range(ai_c['base_hole_nb']):
    a = i*2*math.pi/ai_c['base_hole_nb']+ai_c['base_hole_angle']
    r_f.append((ai_c['base_hole_position_radius']*math.cos(a), ai_c['base_hole_position_radius']*math.sin(a), ai_c['base_hole_radius']))
  ### return
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


