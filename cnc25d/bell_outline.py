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
  ect = ai_c['bell_extra_cut_thickness']
  ### figure construction
  r_f =[]
  # internal_buttress
  if(ai_c['int_buttress_x_length']>0):
    for px in (int_buttress_x1, int_buttress_x2):
      for py in (int_buttress_y1, int_buttress_y2):
        ib_ol = []
        ib_ol.append((px+0*ai_c['int_buttress_x_length']-ect, py+0*ai_c['int_buttress_z_width']-ect, -1*ai_c['bell_cnc_router_bit_radius']))
        ib_ol.append((px+1*ai_c['int_buttress_x_length']+ect, py+0*ai_c['int_buttress_z_width']-ect, -1*ai_c['bell_cnc_router_bit_radius']))
        ib_ol.append((px+1*ai_c['int_buttress_x_length']+ect, py+1*ai_c['int_buttress_z_width']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
        ib_ol.append((px+0*ai_c['int_buttress_x_length']-ect, py+1*ai_c['int_buttress_z_width']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
        ib_ol.append((px+0*ai_c['int_buttress_x_length']-ect, py+0*ai_c['int_buttress_z_width']-ect, 0))
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
      eb_ol.append((px+0*ai_c['ext_buttress_x_width']-ect, ext_buttress_y+0*ai_c['ext_buttress_z_length']-ect, -1*ai_c['bell_cnc_router_bit_radius']))
      eb_ol.append((px+1*ai_c['ext_buttress_x_width']+ect, ext_buttress_y+0*ai_c['ext_buttress_z_length']-ect, -1*ai_c['bell_cnc_router_bit_radius']))
      eb_ol.append((px+1*ai_c['ext_buttress_x_width']+ect, ext_buttress_y+1*ai_c['ext_buttress_z_length']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
      eb_ol.append((px+0*ai_c['ext_buttress_x_width']-ect, ext_buttress_y+1*ai_c['ext_buttress_z_length']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
      eb_ol.append((px+0*ai_c['ext_buttress_x_width']-ect, ext_buttress_y+0*ai_c['ext_buttress_z_length']-ect, 0))
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
  ect = ai_c['bell_extra_cut_thickness']
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
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+4*bell_face_height_5+ect, 0))
  r_ol.append((-1*bell_face_width_2+st+ect, ai_c['base_thickness']+4*bell_face_height_5+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-1*bell_face_width_2+st+ect, ai_c['base_thickness']+3*bell_face_height_5-ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+3*bell_face_height_5-ect, 0))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+2*bell_face_height_5+ect, 0))
  r_ol.append((-1*bell_face_width_2+st+ect, ai_c['base_thickness']+2*bell_face_height_5+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-1*bell_face_width_2+st+ect, ai_c['base_thickness']+1*bell_face_height_5-ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+1*bell_face_height_5-ect, 0))
  r_ol.append((-1*bell_face_width_2, ai_c['base_thickness']+ect, 0)) # bottom
  r_ol.append((-3*bell_face_width_10+ect, ai_c['base_thickness']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-3*bell_face_width_10+ect, 0, 0))
  r_ol.append((-1*bell_face_width_10-ect, 0, 0))
  r_ol.append((-1*bell_face_width_10-ect, ai_c['base_thickness']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((1*bell_face_width_10+ect, ai_c['base_thickness']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((1*bell_face_width_10+ect, 0, 0))
  r_ol.append((3*bell_face_width_10-ect, 0, 0))
  r_ol.append((3*bell_face_width_10-ect, ai_c['base_thickness']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+ect, 0)) # right-side
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+1*bell_face_height_5-ect, 0))
  r_ol.append((bell_face_width_2-(st+ect), ai_c['base_thickness']+1*bell_face_height_5-ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2-(st+ect), ai_c['base_thickness']+2*bell_face_height_5+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+2*bell_face_height_5+ect, 0))
  r_ol.append((bell_face_width_2, ai_c['base_thickness']+3*bell_face_height_5-ect, 0))
  r_ol.append((bell_face_width_2-(st+ect), ai_c['base_thickness']+3*bell_face_height_5-ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((bell_face_width_2-(st+ect), ai_c['base_thickness']+4*bell_face_height_5+ect, -1*ai_c['bell_cnc_router_bit_radius']))
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
  ### intermediate parameters
  bell_face_height_5 = ai_c['bell_face_height']/5.0
  bell_face_width_10 = ai_c['bell_face_width']/10.0
  ect = ai_c['bell_extra_cut_thickness']
  hollow_slope_length = math.sqrt((ai_c['bell_face_width']/2.0-ai_c['face_thickness']-ai_c['hollow_spare_width']-ai_c['hollow_y_width']/2.0)**2+ai_c['hollow_z_height']**2)
  smoothing_hollow_int_radius = max(ai_c['bell_cnc_router_bit_radius'], hollow_slope_length*3/4.0) # verification against hollow_y_width is difficult
  smoothing_hollow_ext_radius = max(0, (hollow_slope_length - smoothing_hollow_int_radius)*2/3.0)
  ### outline construction
  r_ol = []
  r_ol.append((-5*bell_face_width_10+ai_c['face_thickness']+ect, ai_c['base_thickness']+5*bell_face_height_5, 0)) # left-side
  r_ol.append((-5*bell_face_width_10+ai_c['face_thickness']+ect, ai_c['base_thickness']+4*bell_face_height_5, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-5*bell_face_width_10, ai_c['base_thickness']+4*bell_face_height_5, 0))
  r_ol.append((-5*bell_face_width_10, ai_c['base_thickness']+3*bell_face_height_5, 0))
  r_ol.append((-5*bell_face_width_10+ai_c['face_thickness']+ect, ai_c['base_thickness']+3*bell_face_height_5, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-5*bell_face_width_10+ai_c['face_thickness']+ect, ai_c['base_thickness']+2*bell_face_height_5, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-5*bell_face_width_10, ai_c['base_thickness']+2*bell_face_height_5, 0))
  r_ol.append((-5*bell_face_width_10, ai_c['base_thickness']+1*bell_face_height_5, 0))
  r_ol.append((-5*bell_face_width_10+ai_c['face_thickness']+ect, ai_c['base_thickness']+1*bell_face_height_5, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-5*bell_face_width_10+ai_c['face_thickness']+ect, ai_c['base_thickness']+ect, 0)) # bottom-side
  r_ol.append((-3*bell_face_width_10+ect, ai_c['base_thickness']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((-3*bell_face_width_10+ect, 0, 0))
  r_ol.append((-1*bell_face_width_10-ect, 0, 0))
  r_ol.append((-1*bell_face_width_10-ect, ai_c['base_thickness']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((1*bell_face_width_10+ect, ai_c['base_thickness']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((1*bell_face_width_10+ect, 0, 0))
  r_ol.append((3*bell_face_width_10-ect, 0, 0))
  r_ol.append((3*bell_face_width_10-ect, ai_c['base_thickness']+ect, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((5*bell_face_width_10-ai_c['face_thickness']-ect, ai_c['base_thickness']+ect, 0)) # right-side
  r_ol.append((5*bell_face_width_10-ai_c['face_thickness']-ect, ai_c['base_thickness']+1*bell_face_height_5, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((5*bell_face_width_10, ai_c['base_thickness']+1*bell_face_height_5, 0))
  r_ol.append((5*bell_face_width_10, ai_c['base_thickness']+2*bell_face_height_5, 0))
  r_ol.append((5*bell_face_width_10-ai_c['face_thickness']-ect, ai_c['base_thickness']+2*bell_face_height_5, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((5*bell_face_width_10-ai_c['face_thickness']-ect, ai_c['base_thickness']+3*bell_face_height_5, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((5*bell_face_width_10, ai_c['base_thickness']+3*bell_face_height_5, 0))
  r_ol.append((5*bell_face_width_10, ai_c['base_thickness']+4*bell_face_height_5, 0))
  r_ol.append((5*bell_face_width_10-ai_c['face_thickness']-ect, ai_c['base_thickness']+4*bell_face_height_5, -1*ai_c['bell_cnc_router_bit_radius']))
  r_ol.append((5*bell_face_width_10-ai_c['face_thickness']-ect, ai_c['base_thickness']+5*bell_face_height_5, 0))
  if(ai_c['hollow_z_height']>0): # top-side
    r_ol.append((5*bell_face_width_10-ai_c['face_thickness']-ai_c['hollow_spare_width'], ai_c['base_thickness']+5*bell_face_height_5, smoothing_hollow_ext_radius))
    r_ol.append((ai_c['hollow_y_width']/2.0, ai_c['base_thickness']+5*bell_face_height_5-ai_c['hollow_z_height'], smoothing_hollow_int_radius))
    r_ol.append((-1*ai_c['hollow_y_width']/2.0, ai_c['base_thickness']+5*bell_face_height_5-ai_c['hollow_z_height'], smoothing_hollow_int_radius))
    r_ol.append((-5*bell_face_width_10+ai_c['face_thickness']+ai_c['hollow_spare_width'], ai_c['base_thickness']+5*bell_face_height_5, smoothing_hollow_ext_radius))
  r_ol.append((-5*bell_face_width_10+ai_c['face_thickness']+ect, ai_c['base_thickness']+5*bell_face_height_5, 0)) # close
  return(r_ol)

def bell_side_holes(ai_c):
  """ generate the hole-outlines (type-a) of the bell_side part
  """
  r_f = []
  # int_buttress, ext_buttress, axis_fastening
  r_f.extend(bell_face_side_holes(ai_c, 'side'))
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
  ### constant
  radian_epsilon = math.pi/1000
  ### intermediate parameters
  bell_face_width_10 = ai_c['bell_face_width']/10.0
  wall_thickness = max(ai_c['face_thickness'], ai_c['side_thickness'])
  ect = ai_c['bell_extra_cut_thickness']
  ### sub-outline construction
  sol = []
  sol.append((-3*bell_face_width_10, -5*bell_face_width_10+1.5*wall_thickness, ai_c['bell_cnc_router_bit_radius']))
  sol.append((-3*bell_face_width_10, -5*bell_face_width_10-ect, -1*ai_c['bell_cnc_router_bit_radius']))
  sol.append((-1*bell_face_width_10, -5*bell_face_width_10-ect, -1*ai_c['bell_cnc_router_bit_radius']))
  sol.append((-1*bell_face_width_10, -5*bell_face_width_10+wall_thickness, 0))
  sol.append((1*bell_face_width_10, -5*bell_face_width_10+wall_thickness, 0))
  sol.append((1*bell_face_width_10, -5*bell_face_width_10-ect, -1*ai_c['bell_cnc_router_bit_radius']))
  sol.append((3*bell_face_width_10, -5*bell_face_width_10-ect, -1*ai_c['bell_cnc_router_bit_radius']))
  sol.append((3*bell_face_width_10, -5*bell_face_width_10+1.5*wall_thickness, ai_c['bell_cnc_router_bit_radius']))
  if(ai_c['z_hole_radius']>0):
    lAB = 2*bell_face_width_10 - wall_thickness
    lAC = ai_c['z_hole_position_length']
    lCD = ai_c['z_hole_external_radius']
    aBAC = math.pi/4
    lCB = math.sqrt(lAB**2+lAC**2-2*lAB*lAC*math.cos(aBAC)) # law of cosines in the triangle ABC
    cos_aACB = (lCB**2+lAC**2-lAB**2)/(2*lCB*lAC)
    if(abs(cos_aACB)>1):
      print("ERR359: Error, cos_aACB {:0.3f} is out of the range -1..1".format(cos_aACB))
      sys.exit(2)
    aACB = math.acos(cos_aACB)
    cos_aBCD = lCD/lCB
    if(abs(cos_aBCD)>1):
      print("ERR364: Error, cos_aBCD {:0.3f} is out of the range -1..1".format(cos_aBCD))
      sys.exit(2)
    aBCD = math.acos(cos_aBCD)
    aACD = aACB + aBCD
    #print("dbg370: aACB {:0.3f}  aBCD {:0.3f}  aACD {:0.3f}".format(aACB, aBCD, aACD))
    lEC = math.sqrt(2)*wall_thickness + lAC
    Cx = 5*bell_face_width_10 - lEC * math.cos(math.pi/4) # sqrt(2)/2
    Cy = -5*bell_face_width_10 + lEC * math.sin(math.pi/4)
    Fx = Cx - ai_c['z_hole_external_radius']*math.cos(math.pi/4)
    Fy = Cy + ai_c['z_hole_external_radius']*math.sin(math.pi/4)
    Dx = Cx + ai_c['z_hole_external_radius']*math.cos(-math.pi/4-aACD)
    Dy = Cy + ai_c['z_hole_external_radius']*math.sin(-math.pi/4-aACD)
    Gx = Cx + ai_c['z_hole_external_radius']*math.cos(-math.pi/4+aACD)
    Gy = Cy + ai_c['z_hole_external_radius']*math.sin(-math.pi/4+aACD)
    if(aACD>math.pi-radian_epsilon):
      sol.append((Fx, Fy, ai_c['bell_cnc_router_bit_radius']))
    else:
      sol.append((Dx, Dy, 0))
      sol.append((Fx, Fy, Gx, Gy, 0))
  #print("dbg351: sol:", sol)
  ### outline construction
  r_ol = []
  for i in range(4):
    r_ol.extend(cnc25d_api.outline_rotate(sol, 0.0, 0.0, i*math.pi/2))
  r_ol = cnc25d_api.outline_close(r_ol)
  ### return
  return(r_ol)
  
def bell_base_holes(ai_c):
  """ generate the hole-outlines (type-a) of the bell_base part
  """
  ### intermediate parameters
  wall_thickness = max(ai_c['face_thickness'], ai_c['side_thickness'])
  ect = ai_c['bell_extra_cut_thickness']
  ### figure construction
  r_f = []
  # z_axle_hole
  if(ai_c['z_hole_radius']>0):
    z_axle_hole_position = math.sqrt(2)*(ai_c['bell_face_width']/2.0-wall_thickness) - ai_c['z_hole_position_length']
    for i in range(4):
      a = i*math.pi/2+math.pi/4
      r_f.append((z_axle_hole_position*math.cos(a), z_axle_hole_position*math.sin(a), ai_c['z_hole_radius']))
  # base_fastening_holes
  for i in range(ai_c['base_hole_nb']):
    a = i*2*math.pi/ai_c['base_hole_nb']+ai_c['base_hole_angle']
    r_f.append((ai_c['base_hole_position_radius']*math.cos(a), ai_c['base_hole_position_radius']*math.sin(a), ai_c['base_hole_radius']))
  # external_buttress
  if(ai_c['ext_buttress_y_length']>0):
    py = -1*ai_c['bell_face_width']/2.0 - ai_c['ext_buttress_y_position']
    px1 = -1*ai_c['ext_buttress_x_distance']/2.0 - ai_c['ext_buttress_x_width']
    px2 = ai_c['ext_buttress_x_distance']/2.0
    for i in range(4):
      for px in (px1, px2):
        hol = []
        hol.append((px-ect, py+ect, -1*ai_c['bell_cnc_router_bit_radius']))
        hol.append((px-ect, py-ai_c['ext_buttress_y_length']-ect, -1*ai_c['bell_cnc_router_bit_radius']))
        hol.append((px+ai_c['ext_buttress_x_width']+ect, py-ai_c['ext_buttress_y_length']-ect, -1*ai_c['bell_cnc_router_bit_radius']))
        hol.append((px+ai_c['ext_buttress_x_width']+ect, py+ect, -1*ai_c['bell_cnc_router_bit_radius']))
        hol.append((px-ect, py+ect, 0))
        r_f.append(cnc25d_api.outline_rotate(hol, 0.0, 0.0, i*math.pi/2))
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
  ### intermediate parameters
  x1 = 0
  x2 = x1 + ai_c['int_buttress_ext_corner_length']
  x3 = x2 + ai_c['int_buttress_x_length']
  x4 = x3 + ai_c['int_buttress_int_corner_length']
  x5 = x3 + ai_c['int_buttress_x_position']
  x6 = x5 + ai_c['side_thickness']
  x7 = x5 - ai_c['int_buttress_bump_length']
  if(ai_c['int_buttress_bump_length']>0):
    x8 = (x2+x7)/2.0
  else:
    x8 = (x1+x5)/2.0
  x9 = x8 - ai_c['int_buttress_arc_height']*math.sqrt(2)/2
  x10 = x5 - ai_c['z_hole_position_length']*math.sqrt(2)/2
  y1 = 0
  y2 = y1 + ai_c['face_thickness']
  y4 = y2 + ai_c['int_buttress_x_position']
  y3 = y4 - ai_c['int_buttress_int_corner_length']
  y5 = y4 + ai_c['int_buttress_x_length']
  y6 = y5 + ai_c['int_buttress_ext_corner_length']
  y7 = y2 + ai_c['int_buttress_bump_length']
  if(ai_c['int_buttress_bump_length']>0):
    y8 = (y5+y7)/2.0
  else:
    y8 = (y2+y6)/2.0
  y9 = y8 + ai_c['int_buttress_arc_height']*math.sqrt(2)/2
  y10 = y2 + ai_c['z_hole_position_length']*math.sqrt(2)/2
  ### outline construction
  ib_ol = []
  ib_ol.append((x1, y2, 0))
  if((ai_c['int_buttress_ext_corner_length']>0)and(ai_c['int_buttress_x_length']>0)):
    ib_ol.append((x2, y2, -1*ai_c['bell_cnc_router_bit_radius']))
  if(ai_c['int_buttress_x_length']>0):
    ib_ol.append((x2, y1, 0))
    ib_ol.append((x3, y1, 0))
  if((ai_c['int_buttress_int_corner_length']>0)and(ai_c['int_buttress_x_length']>0)):
    ib_ol.append((x3, y2, -1*ai_c['bell_cnc_router_bit_radius']))
  if((ai_c['int_buttress_x_length']>0)and(ai_c['int_buttress_int_corner_length']==0)): # two branch because of the router_bit_radius
    ib_ol.append((x4, y2, -1*ai_c['bell_cnc_router_bit_radius']))
    ib_ol.append((x5, y3, -1*ai_c['bell_cnc_router_bit_radius']))
  else:
    ib_ol.append((x4, y2, 0))
    ib_ol.append((x5, y3, 0))
  if((ai_c['int_buttress_int_corner_length']>0)and(ai_c['int_buttress_x_length']>0)):
    ib_ol.append((x5, y4, -1*ai_c['bell_cnc_router_bit_radius']))
  if(ai_c['int_buttress_x_length']>0):
    ib_ol.append((x6, y4, 0))
    ib_ol.append((x6, y5, 0))
  if((ai_c['int_buttress_ext_corner_length']>0)and(ai_c['int_buttress_x_length']>0)):
    ib_ol.append((x5, y5, -1*ai_c['bell_cnc_router_bit_radius']))
  ib_ol.append((x5, y6, 0))
  if(ai_c['int_buttress_bump_length']>0):
    ib_ol.append((x7, y5, ai_c['int_buttress_smoothing_radius']))
  if(ai_c['int_buttress_arc_height']==0):
    if(ai_c['int_buttress_bump_length']>0):
      ib_ol.append((x2, y7, ai_c['int_buttress_smoothing_radius']))
    ib_ol.append((x1, y2, 0))
  else:
    if(ai_c['int_buttress_bump_length']>0):
      ib_ol.append((x9, y9, x2, y7, ai_c['int_buttress_smoothing_radius']))
      ib_ol.append((x1, y2, 0))
    else:
      ib_ol.append((x9, y9, x1, y2, 0))
  ### figure construction
  r_f = []
  r_f.append(ib_ol)
  if(ai_c['z_hole_radius']>0):
    r_f.append((x10, y10, ai_c['z_hole_radius']))
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


