# small_geometry.py
# a help module for cnc_cut_outline.py, just to avoid to get too big files
# created by charlyoleg on 2013/07/30
# license: CC BY SA 3.0

"""
small_geometry.py provides sub functions for cnc_cut_outline.py related to the Euclid geometry
"""

################################################################
# python behavior
################################################################

from __future__ import division # to get float division


################################################################
# import
################################################################

#import outline_backends # for testing only
#
import math
import sys, argparse

################################################################
# functions to be used by cnc_cut_outline.py
################################################################

def rotate_point(ai_point, ai_ox, ai_oy, ai_rotation_angle):
  """ Rotation of the point ai_point of center (ai_ox, ai_oy) and angle ai_rotation_angle
  """
  ix = ai_point[0]-ai_ox
  iy = ai_point[1]-ai_oy
  pt_x = ai_ox+ix*math.cos(ai_rotation_angle)-iy*math.sin(ai_rotation_angle)
  pt_y = ai_oy+ix*math.sin(ai_rotation_angle)+iy*math.cos(ai_rotation_angle)
  r_point = [pt_x, pt_y]
  return(r_point)

def arc_center_radius(ai_arc_pt1, ai_arc_pt2, ai_arc_pt3, ai_error_msg_id):
  """ Compute the center of the arc defined by the three points A,B and C
  """
  #print("dbg197: ai_error_msg_id: {:s}".format(ai_error_msg_id))
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the arc three points A,B,C
  AX = ai_arc_pt1[0]
  AY = ai_arc_pt1[1]
  BX = ai_arc_pt2[0]
  BY = ai_arc_pt2[1]
  CX = ai_arc_pt3[0]
  CY = ai_arc_pt3[1]
  # check of the lenght AB, BC, AC
  AB = math.sqrt((BX-AX)**2+(BY-AY)**2)
  BC = math.sqrt((CX-BX)**2+(CY-BY)**2)
  AC = math.sqrt((CX-AX)**2+(CY-AY)**2)
  if((AB<radian_epsilon)or(BC<radian_epsilon)or(AC<radian_epsilon)):
    print("ERR682: Error in {:s}, the three arc points ABC are too closed: AB={:0.2f} BC={:0.2f} AC={:0.2f}".format(ai_error_msg_id, AB, BC, AC))
    sys.exit(2)
  # calculation of M and N
  MX = (AX+BX)/2
  MY = (AY+BY)/2
  NX = (BX+CX)/2
  NY = (BY+CY)/2
  # calculation of e and f
  cos_e = (BX-AX)/AB
  sin_e = (BY-AY)/AB
  cos_f = (CX-BX)/BC
  sin_f = (CY-BY)/BC
  # calculation de I
  #(cos(e)*sin(f)-cos(f)*sin(e))*x = sin(f)*(cos(e)*xM+sin(e)*yM)-sin(e)*(cos(f)*xN+sin(f)*yN)
  #(sin(e)*cos(f)-sin(f)*cos(e))*y = cos(f)*(cos(e)*xM+sin(e)*yM)-cos(e)*(cos(f)*xN+sin(f)*yN)
  # ixl = (cos(e)*sin(f)-cos(f)*sin(e))
  # iyl = (sin(e)*cos(f)-sin(f)*cos(e))
  # ixk = sin(f)*(cos(e)*xM+sin(e)*yM)-sin(e)*(cos(f)*xN+sin(f)*yN)
  # iyk = cos(f)*(cos(e)*xM+sin(e)*yM)-cos(e)*(cos(f)*xN+sin(f)*yN)
  ixl = cos_e*sin_f-cos_f*sin_e
  iyl = sin_e*cos_f-sin_f*cos_e
  ixk = sin_f*(cos_e*MX+sin_e*MY)-sin_e*(cos_f*NX+sin_f*NY)
  iyk = cos_f*(cos_e*MX+sin_e*MY)-cos_e*(cos_f*NX+sin_f*NY)
  if((abs(ixl)<radian_epsilon)or(abs(iyl)<radian_epsilon)):
    print("ERR947: Error in {:s}, ixl (= {:0.2f}) or iyl (= {:0.2f}) are too closed to zero!".format(ai_error_msg_id, ixl, iyl))
    sys.exit(2)
  IX=ixk/ixl
  IY=iyk/iyl
  # check than I is equidistant of A, B and C
  IA = math.sqrt((AX-IX)**2+(AY-IY)**2)
  IB = math.sqrt((BX-IX)**2+(BY-IY)**2)
  IC = math.sqrt((CX-IX)**2+(CY-IY)**2)
  if((abs(IB-IA)>radian_epsilon)or(abs(IC-IA)>radian_epsilon)):
    print("ERR748: Error in {:s}, the calculation of the center of the arc A,B,C is wrong! IA={:0.2f} IB={:0.2f} IC={:0.2f}".format(ai_error_msg_id, IA, IB, IC))
    print("dbg253: A= {:0.2f} {:0.2f}  B= {:0.2f} {:0.2f}  C= {:0.2f} {:0.2f}  I= {:0.2f} {:0.2f}".format(AX,AY,BX,BY,CX,CY,IX,IY))
    print("dbg764: cos_e={:0.2f}  sin_e={:0.2f}  cos_f={:0.2f}  sin_f={:0.2f}".format(cos_e, sin_e, cos_f, sin_f))
    print("dbg765: ixl={:0.2f} ixk={:0.2f} iyl={:0.2f} iyk={:0.2f}".format(ixl, ixk, iyl, iyk))
    print("dbg766: MX={:0.2f} MY={:0.2f} NX={:0.2f} NY={:0.2f}".format(MX,MY,NX,NY))
    sys.exit(2)
  # return
  r_arc_center_radius=(IX, IY, IA)
  return(r_arc_center_radius)

def arc_center_radius_angles(ai_arc_pt1, ai_arc_pt2, ai_arc_pt3, ai_error_msg_id):
  """ Compute the center, radius and angles of the arc defined by the three points A,B and C
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  AX = ai_arc_pt1[0]
  AY = ai_arc_pt1[1]
  BX = ai_arc_pt2[0]
  BY = ai_arc_pt2[1]
  CX = ai_arc_pt3[0]
  CY = ai_arc_pt3[1]
  # calculation of I
  (IX,IY, arc_radius) = arc_center_radius(ai_arc_pt1, ai_arc_pt2, ai_arc_pt3, ai_error_msg_id)
  # check I is equidistant of A,B,C,D,E
  IA = math.sqrt((AX-IX)**2+(AY-IY)**2)
  IB = math.sqrt((BX-IX)**2+(BY-IY)**2)
  IC = math.sqrt((CX-IX)**2+(CY-IY)**2)
  if((abs(IA-arc_radius)>radian_epsilon)or(abs(IB-arc_radius)>radian_epsilon)or(abs(IC-arc_radius)>radian_epsilon)):
    print("ERR841: Error, in {:s}, I is not equidistant from A,B,C. arc_radius={:0.2f} IA={:0.2f} IB={:0.2f} IC={:0.2f}".format(ai_error_msg_id, arc_radius, IA, IB, IC))
    sys.exit(2)
  # calculation of the angle u=(Ix, IA) , v=(Ix, IB), w=(Ix, IC), d=(Ix, ID) and e=(Ix, IE)
  u = math.atan2(AY-IY, AX-IX)
  v = math.atan2(BY-IY, BX-IX)
  w = math.atan2(CY-IY, CX-IX)
  # calculation of the angle uv=(IA, IB), uw=(IA, IC)
  uv = math.fmod(v-u+4*math.pi, 2*math.pi)
  uw = math.fmod(w-u+4*math.pi, 2*math.pi)
  # check arc direction
  ccw_ncw = True
  if(uw>uv):
    #print("dbg874: arc of circle direction: counter clock wise (CCW)")
    ccw_ncw = True
  else:
    #print("dbg875: arc of circle direction: clock wise (CW)")
    ccw_ncw = False
    uv = uv - 2*math.pi
    uw = uw - 2*math.pi
  # return
  r_arc_center_radius_angles=(IX, IY, IA, uw, u, w)
  return(r_arc_center_radius_angles)

def triangulation(ai_A, ai_AC, ai_B, ai_BC, ai_D, ai_D_direction, ai_error_msg_id):
  """ knowing the coordiantes of A and B and the lengths AC and BC, returns the coordinates of C
      C is placed on the same side as D compare to the line (AB)
      If D is too closed to the line (AB), the D_direction is used to identified the side to place C
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # code error
  r_status = 0
  # check the arguments
  if((ai_AC<radian_epsilon)or(ai_BC<radian_epsilon)):
    print("ERR965: Error in {:s}, the length ai_AC (={:0.2f}) or ai_BC (={:0.2f})".format(ai_error_msg_id, ai_AC, ai_BC))
    sys.exir(2)
  # interprete the arguments
  AX = ai_A[0]
  AY = ai_A[1]
  b = ai_AC
  BX = ai_B[0]
  BY = ai_B[1]
  a = ai_BC
  DX = ai_D[0]
  DY = ai_D[1]
  # calculation of the length c=AB
  c = math.sqrt((BX-AX)**2+(BY-AY)**2)
  if(c<radian_epsilon):
    print("ERR662: Error in {:s}, the length c (=AB={:0.2f}) is too small!".format(ai_error_msg_id, c))
    sys.exit(2)
  # calculation of the angle A with the law of cosines
  #BAC = math.acos((b**2+c**2-a**2)/(2*b*c))
  cos_BAC = (b**2+c**2-a**2)/(2*b*c)
  if(abs(cos_BAC)>1):
    print("ERR542: Error in {:s}, cos_BAC is out of [-1,1]! a={:0.2f} b={:0.2f} c={:0.2f} cos_BAC={:0.2f}".format(ai_error_msg_id, a, b, c, cos_BAC))
    print("dbg652: AX={:0.2f} AY={:0.2f} BX={:0.2f} BY={:0.2f}".format(AX,AY,BX,BY))
    #sys.exit(2)
    r_status=2
    return((0,0,r_status))
  BAC = math.acos(cos_BAC)
  # calculation of the angle xAB
  xAB = math.atan2(BY-AY, BX-AX)
  # calculation of the angle BAD
  xAD =  math.atan2(DY-AY, DX-AX) # atan2 avoid the problem of divided by zero
  BAD = math.fmod(xAD - xAB + 5*math.pi, 2*math.pi) - math.pi
  if(abs(BAD)<radian_epsilon):
    print("WARN546: Warning in {:s}, the side of the triangulation is not clear! Use the ai_D_direction".format(ai_error_msg_id))
    DX1 = DX+5*radian_epsilon*math.cos(ai_D_direction)
    DY1 = DY+5*radian_epsilon*math.sin(ai_D_direction)
    xAD =  math.atan2(DY1-AY, DX1-AX) # atan2 avoid the problem of divided by zero
    BAD = math.fmod(xAD - xAB + 5*math.pi, 2*math.pi) - math.pi
  # calculation of the angle xAC
  xAC = xAB + math.copysign(BAC, BAD)
  # calculation of the coordinates of C
  CX = AX+b*math.cos(xAC)
  CY = AY+b*math.sin(xAC)
  # for verification, duplication of the calculation via B
  ABC = math.acos((a**2+c**2-b**2)/(2*a*c))
  xBA = math.atan2(AY-BY, AX-BX) # = xAB+math.pi
  #BD = math.sqrt((DX-BX)**2+(DY-BY)**2)
  xBD = math.atan2(DY-BY, DX-BX)
  ABD = math.fmod(xBD - xBA + 5*math.pi, 2*math.pi) - math.pi
  if(abs(ABD)<radian_epsilon):
    print("WARN547: Warning in {:s}, the side of the triangulation is not clear! Use the ai_D_direction".format(ai_error_msg_id))
    DX1 = DX+5*radian_epsilon*math.cos(ai_D_direction)
    DY1 = DY+5*radian_epsilon*math.sin(ai_D_direction)
    xBD = math.atan2(DY1-BY, DX1-BX)
    ABD = math.fmod(xBD - xBA + 5*math.pi, 2*math.pi) - math.pi
  xBC = xBA + math.copysign(ABC, ABD)
  CX2 = BX+a*math.cos(xBC)
  CY2 = BY+a*math.sin(xBC)
  if((abs(CX2-CX)>radian_epsilon)or(abs(CY2-CY)>radian_epsilon)):
    print("ERR686: Error in {:s}, the coordinate of C seems wrong! CX={:0.2f} CX2={:0.2f} CY={:0.2f} CY2={:0.2f}".format(ai_error_msg_id, CX, CX2, CY, CY2))
    print("dbg545: D {:0.2f} {:0.2f}  ai_D_direction {:0.2f}".format(DX,DY, ai_D_direction))
    print("dbg512: BAC", BAC)
    print("dbg513: xAB", xAB)
    #print("dbg514: AD", AD)
    print("dbg515: BAD", BAD)
    print("dbg516: xAC", xAC)
    print("dbg517: AX {:0.2f}  AY {:0.2f}  b {:0.2f}".format(AX,AY, b))
    print("dbg522: ABC", ABC)
    print("dbg523: xBA", xBA)
    #print("dbg524: BD", BD)
    print("dbg525: ABD", ABD)
    print("dbg526: xBC", xBC)
    print("dbg527: BX {:0.2f}  BY {:0.2f}  a {:0.2f}".format(BX,BY, a))
    sys.exit(2)
  r_C = (CX,CY,r_status)
  return(r_C)



