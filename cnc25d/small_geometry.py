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

# aka circle_circle_intersection
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

def line_equation(ai_A, ai_B, ai_error_msg_id):
  """ Given the coordinates of two points, it returns the three coefficient of the line equation, the length of the segment and the inclination
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  AX = ai_A[0]
  AY = ai_A[1]
  BX = ai_B[0]
  BY = ai_B[1]
  # calculation of the length AB
  lAB = math.sqrt((BX-AX)**2+(BY-AY)**2)
  # calculation of the inclination of AB
  xAB = math.atan2(BY-AY, BX-AX)
  cos_xAB = (BX-AX)/lAB
  sin_xAB = (BY-AY)/lAB
  # calculation of the line equation coefficient : ABlx * x + ABly * y + ABk = 0
  # ABlx = sin(xAB)
  ABlx = sin_xAB
  # ABly = -cos(xAB)
  ABly = -cos_xAB
  # ABk = -(ABlx*AX+ABly*AY)
  ABk = -(ABlx*AX+ABly*AY)
  # return
  r_line_equation = (ABlx, ABly, ABk, lAB, xAB)
  return(r_line_equation)

def line_distance_point(ai_A, ai_B, ai_q, ai_error_msg_id):
  """ Given the two points A and B and the distance q, what are the coordinates of Q, distance of q from A and AB
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  AX = ai_A[0]
  AY = ai_A[1]
  BX = ai_B[0]
  BY = ai_B[1]
  # line equation of AB
  #(ABlx, ABly, ABkA, lAB, xAB) = line_equation(ai_A, ai_B, ai_error_msg_id)
  lAB = math.sqrt((BX-AX)**2+(BY-AY)**2)
  cos_xAB = (BX-AX)/lAB
  sin_xAB = (BY-AY)/lAB
  ABlx = sin_xAB
  ABly = -cos_xAB
  # calculation of Q
  # QX = AX+q*cos(xAB+pi/2) = AX-q*sin(xAB)
  # QY = AX+q*sin(xAB+pi/2) = AX+q*cos(xAB)
  QX = AX-ai_q*sin_xAB
  QY = AY+ai_q*cos_xAB
  ABkQ = -(ABlx*QX+ABly*QY)
  # return
  r_Q = (QX, QY, ABkQ)
  return(r_Q)

def line_point_projection(ai_AB, ai_M, ai_error_msg_id):
  """ Given the line equation of AB (ABlx, AVly, ABk) and the coordinates of M (MX,MY), returns the coordinates of P, projection of M on AB
  """
  # use to check is angle is smaller than pi/2
  #radian_epsilon = math.pi/1000
  # interpretation of the input points
  a = ai_AB[0] # ABlx
  b = ai_AB[1] # ABly
  c = ai_AB[2] # ABk
  MX = ai_M[0]
  MY = ai_M[1]
  # calculation of d (MPk, coefficient of the line equation of PM)
  d = -(b*MX-a*MY) # MPk
  # calculation of the coordinates of P
  PX = -(c*a+d*b)
  PY = d*a-c*b
  # return
  r_P = (PX, PY)
  return(r_P)

def line_circle_intersection(ai_AB, ai_I, ai_R, ai_C, ai_D_direction, ai_error_msg_id):
  """ Given the line equation (a*x+b*y+c=0) and the circle of center I and radius R, returns the intersection M
      C define the side of the intersection
      D_direction is used if C is too closed to the border. Set it to zero if you don't know how to set it.
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # status for error forward
  line_circle_intersection_status = 0
  r_line_circle_intersection = (0, 0, line_circle_intersection_status)
  # interpretation of the input points
  a = ai_AB[0] # ABlx
  b = ai_AB[1] # ABly
  c = ai_AB[2] # ABk
  IX = ai_I[0]
  IY = ai_I[1]
  CX = ai_C[0]
  CY = ai_C[1]
  # calculation of the coordinates of P, projection of M on AB
  (PX, PY) = line_point_projection(ai_AB, ai_I, ai_error_msg_id)
  # calculation of the coordinates of C2, projection of C on AB
  (C2X, C2Y) = line_point_projection(ai_AB, ai_C, ai_error_msg_id)
  # calculation of the length IP
  #IP = math.sqrt((PX-IX)**2+(PY-IY)**2)
  IP2 = (PX-IX)**2+(PY-IY)**2
  IP = math.sqrt(IP2)
  if(IP>ai_R):
    # This error might occur when the sign of the tangent is wrong because of calculation impression.
    # That's why, we need to report the error instead of stopping on this error
    print("ERR672: Error in {:s}, the line and the circle have no intersection! IP={:0.2f}  ai_R={:0.2f}".format(ai_error_msg_id, IP, ai_R))
    print("dbg611: ai_AB:", ai_AB)
    print("dbg612: ai_I:", ai_I)
    print("dbg613: ai_R:", ai_R)
    print("dbg614: ai_C:", ai_C)
    #sys.exit(2)
    line_circle_intersection_status=2
    r_line_circle_intersection = (0, 0, line_circle_intersection_status)
  else:
    # calculation of the length PM
    PM = math.sqrt(ai_R**2-IP2)
    # calculation of the length C2P
    C2P = math.sqrt((PX-C2X)**2+(PY-C2Y)**2)
    cos_i = (C2X-PX)/C2P
    sin_i = (C2Y-PY)/C2P
    if(C2P<radian_epsilon):
      print("WARN348: Warning in {:s}, C is too closed from the board to find the line_circle_intersection!".format(ai_error_msg_id))
      xAB = math.atan2(a, -b)
      direction_correlation = math.fmod(ai_D_direction-xAB+5*math.pi, 2*math.pi)-math.pi
      direction_AB = math.copysign(1, direction_correlation)
      norm_ab = math.sqrt(a**2+b**2)
      cos_i = direction_AB * -b / norm_ab
      sin_i = direction_AB * a / norm_ab
    # calculation of the coordinates of M
    MX = PX+cos_i*PM
    MY = PY+sin_i*PM
    r_line_circle_intersection = (MX, MY, line_circle_intersection_status)
  # return
  return(r_line_circle_intersection)

def sub_smooth_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ compute the corner center of a smoothed line-arc corner
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  #AX = ai_pre_point[0]
  #AY = ai_pre_point[1]
  CX = ai_current_point[0]
  CY = ai_current_point[1]
  #DX = ai_post_middle[0]
  #DY = ai_post_middle[1]
  #EX = ai_post_point[0]
  #EY = ai_post_point[1]
  # calculation of the AC line equation and J
  (AClx, ACly, ACkA, lAC, xAC) = line_equation(ai_pre_point, ai_current_point, ai_error_msg_id)
  (JX,JY, R2, uw2, u2, w2) = arc_center_radius_angles(ai_current_point, ai_post_middle, ai_post_point, ai_error_msg_id)
  # arc orientation
  #o1 = math.copysign(1, uw1)
  o2 = math.copysign(1, uw2)
  # sign of the tangent angle
  tangent_angle = math.fmod( u2+o2*math.pi/2-xAC+7*math.pi, 2*math.pi) - math.pi
  #r_outline = []
  smooth_status = 0
  if(abs(tangent_angle)<radian_epsilon):
    print("WARN942: Warning in {:s}, the tangent_angle is too flat! the corner doesn't need to be smoothed.".format(ai_error_msg_id))
    #r_outline = [(ai_current_point[0], ai_current_point[1])]
    smooth_status = 2
  #elif(abs(tangent_angle)>math.pi-radian_epsilon):
  #  print("WARN943: Warning in {:s}, the tangent_angle is too sharp! the corner cannot be smoothed.".format(ai_error_msg_id))
  #  r_outline = [(ai_current_point[0], ai_current_point[1])]
  else:
    o3 = math.copysign(1, tangent_angle)
    # calculation of IS and JS
    Q1_plus = o3 # = -1 if the router below the line, else 1
    R2_plus = o2*o3 # = -1 if the router is outer the arc, else 1
    (QX,QY, ACkQ) = line_distance_point(ai_pre_point, ai_current_point, Q1_plus*ai_router_bit_request, ai_error_msg_id)
    JS = R2-R2_plus*ai_router_bit_request
    #print("dbg147: ai_pre_point", ai_pre_point)
    #print("dbg347: ai_current_point", ai_current_point)
    #print("dbg447: ai_post_middle", ai_post_middle)
    #print("dbg547: ai_post_point", ai_post_point)
    #print("dbg647: ai_router_bit_request", ai_router_bit_request)
    #print("dbg123: AClx={:0.2f} ACly={:0.2f} ACkA={:0.2f} lAC={:0.2f} xAC={:0.2f}".format(AClx, ACly, ACkA, lAC, xAC))
    #print("dbg124: JX={:0.2f} JY={:0.2f} R2={:0.2f} uw2={:0.2f} u2={:0.2f}  w2={:0.2f}".format(JX, JY, R2, uw2, u2, w2))
    #print("dbg125: o2={:0.2f} o3={:0.2f}".format(o2,o3))
    #print("dbg127: tangent_angle", tangent_angle)
    #print("dbg126: QS={:0.2f} JS={:0.2f}".format(QS,JS))
    #print("dbg532: in {:s}, xAC={:0.2f} R2={:0.2f} ai_router_bit_request={:0.2f}".format(ai_error_msg_id, xAC, R2, ai_router_bit_request))
    # calculation of the coordiantes of S, the center of the router_bit in the smooth corner
    bisector_angle = math.fmod(u2+o2*math.pi/2-(xAC+math.pi) + 7*math.pi, 2*math.pi) - math.pi
    D_direction = xAC + bisector_angle/2
    #print("dbg693: bisector_angle {:0.2f}  D_direction {:0.2f}".format(bisector_angle, D_direction))
    (SX,SY, line_circle_intersection_status) = line_circle_intersection((AClx, ACly, ACkQ), (JX,JY),JS, (CX,CY), D_direction, ai_error_msg_id)
    # when the angle is too sharp, the sign of the tangeant angle might be wrong because of calculation imprecition.
    # in this case, we use the method of try and retry
    if((line_circle_intersection_status==2)and(abs(tangent_angle)>math.pi-10*radian_epsilon)): # error then retry with -Q1_plus instead of Q1_plus
      print("WARN682: Warning in {:s}, line_arc corner is smoothed with the other side because of a line_circle_intersection error!".format(ai_error_msg_id))
      (QX,QY, ACkQ) = line_distance_point(ai_pre_point, ai_current_point, -Q1_plus*ai_router_bit_request, ai_error_msg_id)
      tmpCX = CX + JS*math.cos(xAC+math.pi)
      tmpCY = CY + JS*math.sin(xAC+math.pi)
      (SX,SY, line_circle_intersection_status) = line_circle_intersection((AClx, ACly, ACkQ), (JX,JY),JS, (tmpCX,tmpCY), D_direction, ai_error_msg_id)
    # end of the retry. Continue the normal calculation recipe
    if(line_circle_intersection_status==2):
      print("WARN684: Warning in {:s}, corner is not smoothed because of a line_circle_intersection error!".format(ai_error_msg_id))
      print("dbg681: ai_pre_point", ai_pre_point)
      print("dbg683: ai_current_point", ai_current_point)
      print("dbg684: ai_post_middle", ai_post_middle)
      print("dbg685: ai_post_point", ai_post_point)
      print("dbg686: ai_router_bit_request", ai_router_bit_request)
      print("dbg623: AClx={:0.2f} ACly={:0.2f} ACkA={:0.2f} lAC={:0.2f} xAC={:0.2f}".format(AClx, ACly, ACkA, lAC, xAC))
      print("dbg688: JX={:0.2f} JY={:0.2f} R2={:0.2f} uw2={:0.2f} u2={:0.2f}  w2={:0.2f}".format(JX, JY, R2, uw2, u2, w2))
      print("dbg689: o2={:0.2f} o3={:0.2f}".format(o2,o3))
      print("dbg691: tangent_angle", tangent_angle)
      print("dbg692: JS={:0.2f}".format(JS))
      print("dbg711: QX={:0.2f} QY={:0.2f} ACkQ={:0.2f}".format(QX,QY,ACkQ))
      print("dbg693: in {:s}, xAC={:0.2f} R2={:0.2f} ai_router_bit_request={:0.2f}".format(ai_error_msg_id, xAC, R2, ai_router_bit_request))
      #r_outline = [(ai_current_point[0], ai_current_point[1])]
      smooth_status = 2
      sys.exit(2)
    else:
      # calculation of U, the projection of S on AC
      (UX, UY) = line_point_projection((AClx, ACly, ACkA), (SX,SY), ai_error_msg_id)
      # calculation of the angles xSU and xSJ
      #xSU = math.atan2(UY-SY, UX-SX)+(1+Q1_plus)/2*math.pi
      xSU = math.atan2(UY-SY, UX-SX)
      xSJ = math.atan2(JY-SY, JX-SX)+(1+R2_plus)/2*math.pi
      router_bit_arc_uw = math.fmod(xSJ-xSU+4*math.pi, 2*math.pi)
      if(o3<0):
        router_bit_arc_uw = router_bit_arc_uw - 2*math.pi
      #print("dbg337: SX {:0.2f}  SY {:0.2f}".format(SX,SY))
      #print("dbg994: xSI {:0.2f}  xSJ {:0.2f}".format(xSI, xSJ))
      #print("dbg773: router_bit_arc_uw", router_bit_arc_uw)
      smooth_status = 1
  # return
  r_sub_smooth_corner_line_arc = (SX, SY, UX, UY, xSU, xSJ, router_bit_arc_uw, smooth_status)
  return(r_sub_smooth_corner_line_arc)

def sub_smooth_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Compute the smooth corner center for a arc-arc corner
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  #AX = ai_pre_point[0]
  #AY = ai_pre_point[1]
  #BX = ai_pre_middle[0]
  #BY = ai_pre_middle[1]
  CX = ai_current_point[0]
  CY = ai_current_point[1]
  #DX = ai_post_middle[0]
  #DY = ai_post_middle[1]
  #EX = ai_post_point[0]
  #EY = ai_post_point[1]
  # calculation of I and J
  (IX,IY, R1, uw1, u1, w1) = arc_center_radius_angles(ai_pre_point, ai_pre_middle, ai_current_point, ai_error_msg_id)
  (JX,JY, R2, uw2, u2, w2) = arc_center_radius_angles(ai_current_point, ai_post_middle, ai_post_point, ai_error_msg_id)
  # arc orientation
  o1 = math.copysign(1, uw1)
  o2 = math.copysign(1, uw2)
  # sign of the tangent angle
  #tangent_angle = math.fmod( (u2+o2*path.pi/2)-(w1+o1*path.pi/2)+8*math.pi, 2*math.pi) - math.pi
  tangent_angle = math.fmod( u2-w1+(o2-o1)*math.pi/2+9*math.pi, 2*math.pi) - math.pi
  #r_outline = []
  smooth_status = 0
  if(abs(tangent_angle)<radian_epsilon):
    print("WARN932: Warning in {:s}, the tangent_angle is too flat! the corner doesn't need to be smoothed.".format(ai_error_msg_id))
    #r_outline = [(ai_current_point[0], ai_current_point[1])]
    smooth_status = 2
  elif(abs(tangent_angle)>math.pi-radian_epsilon):
    print("WARN933: Warning in {:s}, the tangent_angle is too sharp! the corner cannot be smoothed.".format(ai_error_msg_id))
    #r_outline = [(ai_current_point[0], ai_current_point[1])]
    smooth_status = 2
  else:
    o3 = math.copysign(1, tangent_angle)
    # calculation of IS and JS
    R1_plus = o1*o3 # = -1 if the router is outer the arc, else 1
    R2_plus = o2*o3 # = -1 if the router is outer the arc, else 1
    IS = R1-R1_plus*ai_router_bit_request
    JS = R2-R2_plus*ai_router_bit_request
    #print("dbg147: ai_pre_point", ai_pre_point)
    #print("dbg247: ai_pre_middle", ai_pre_middle)
    #print("dbg347: ai_current_point", ai_current_point)
    #print("dbg447: ai_post_middle", ai_post_middle)
    #print("dbg547: ai_post_point", ai_post_point)
    #print("dbg647: ai_router_bit_request", ai_router_bit_request)
    #print("dbg123: IX={:0.2f} IY={:0.2f} R1={:0.2f} uw1={:0.2f} u1={:0.2f}  w1={:0.2f}".format(IX, IY, R1, uw1, u1, w1))
    #print("dbg124: JX={:0.2f} JY={:0.2f} R2={:0.2f} uw2={:0.2f} u2={:0.2f}  w2={:0.2f}".format(JX, JY, R2, uw2, u2, w2))
    #print("dbg125: o1={:0.2f} o2={:0.2f} o3={:0.2f}".format(o1,o2,o3))
    #print("dbg127: tangent_angle", tangent_angle)
    #print("dbg126: IS={:0.2f} JS={:0.2f}".format(IS,JS))
    #print("dbg532: in {:s}, R1={:0.2f} R2={:0.2f} ai_router_bit_request={:0.2f}".format(ai_error_msg_id, R1, R2, ai_router_bit_request))
    # calculation of the coordiantes of S, the center of the router_bit in the smooth corner
    bisector_angle = math.fmod(u2-w1+(o2+o1)*math.pi/2 + 9*math.pi, 2*math.pi) - math.pi #(u2+o2*math.pi/2)-(w1-o1*math.pi/2)
    D_direction = w1 + bisector_angle/2
    #print("dbg693: bisector_angle {:0.2f}  D_direction {:0.2f}".format(bisector_angle, D_direction))
    (SX,SY, triangulation_status) = triangulation((IX,IY),IS,(JX,JY),JS,(CX,CY), D_direction, ai_error_msg_id)
    if(triangulation_status==2):
      print("WARN693: Warning in {:s}, corner is not smoothed because of a triangulation error!".format(ai_error_msg_id))
      #print("dbg681: ai_pre_point", ai_pre_point)
      #print("dbg682: ai_pre_middle", ai_pre_middle)
      #print("dbg683: ai_current_point", ai_current_point)
      #print("dbg684: ai_post_middle", ai_post_middle)
      #print("dbg685: ai_post_point", ai_post_point)
      #print("dbg686: ai_router_bit_request", ai_router_bit_request)
      #print("dbg687: IX={:0.2f} IY={:0.2f} R1={:0.2f} uw1={:0.2f} u1={:0.2f}  w1={:0.2f}".format(IX, IY, R1, uw1, u1, w1))
      #print("dbg688: JX={:0.2f} JY={:0.2f} R2={:0.2f} uw2={:0.2f} u2={:0.2f}  w2={:0.2f}".format(JX, JY, R2, uw2, u2, w2))
      #print("dbg689: o1={:0.2f} o2={:0.2f} o3={:0.2f}".format(o1,o2,o3))
      #print("dbg691: tangent_angle", tangent_angle)
      #print("dbg692: IS={:0.2f} JS={:0.2f}".format(IS,JS))
      #print("dbg693: in {:s}, R1={:0.2f} R2={:0.2f} ai_router_bit_request={:0.2f}".format(ai_error_msg_id, R1, R2, ai_router_bit_request))
      #r_outline = [(ai_current_point[0], ai_current_point[1])]
      smooth_status = 2
    else:
      # calculation of the angles xSI and xSJ
      xSI = math.atan2(IY-SY, IX-SX)+(1+R1_plus)/2*math.pi
      xSJ = math.atan2(JY-SY, JX-SX)+(1+R2_plus)/2*math.pi
      router_bit_arc_uw = math.fmod(xSJ-xSI+4*math.pi, 2*math.pi)
      if(o3<0):
        router_bit_arc_uw = router_bit_arc_uw - 2*math.pi
      #print("dbg337: SX {:0.2f}  SY {:0.2f}".format(SX,SY))
      #print("dbg994: xSI {:0.2f}  xSJ {:0.2f}".format(xSI, xSJ))
      #print("dbg773: router_bit_arc_uw", router_bit_arc_uw)
      smooth_status = 1
  #return
  r_sub_smooth_corner_arc_arc = (SX, SY, xSI, xSJ, router_bit_arc_uw, smooth_status)
  return(r_sub_smooth_corner_arc_arc)

def sub_enlarge_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Compute the points related to an enlarged arc-arc corner
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  #AX = ai_pre_point[0]
  #AY = ai_pre_point[1]
  #BX = ai_pre_middle[0]
  #BY = ai_pre_middle[1]
  CX = ai_current_point[0]
  CY = ai_current_point[1]
  #DX = ai_post_middle[0]
  #DY = ai_post_middle[1]
  #EX = ai_post_point[0]
  #EY = ai_post_point[1]
  (SX, SY, xSI, xSJ, router_bit_arc_uw, smooth_status) = sub_smooth_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id)
  if(abs(router_bit_arc_uw)>math.pi):
    print("ERR887: Error in {:s}, the sub smooth corner is englobed!".format(ai_error_msg_id))
    sys.exit(2)
  #print("dbg553: router_bit_arc_uw:", router_bit_arc_uw)
  corner_orientation = math.copysign(1, router_bit_arc_uw)
  enlarge_status = 0
  if(smooth_status==1):
    enlarge_status = 1
    (SClx, SCly, SCkS, lSC, xSC) = line_equation((SX,SY), (CX,CY), ai_error_msg_id)
    (FX,FY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkS), (CX,CY),ai_router_bit_request, (SX,SY), xSC+math.pi, ai_error_msg_id)
    if(line_circle_intersection_status==2):
      print("ERR639: Error in {:s} with the line_circle_intersection_status!".format(ai_error_msg_id))
      sys.exit(2)
    (GX,GY, SCkG) = line_distance_point((FX,FY), (CX,CY), -1*corner_orientation*ai_router_bit_request, ai_error_msg_id)
    (HX,HY, SCkH) = line_distance_point((FX,FY), (CX,CY),  1*corner_orientation*ai_router_bit_request, ai_error_msg_id)
    (IX,IY, R1, uw1, u1, w1) = arc_center_radius_angles(ai_pre_point, ai_pre_middle, ai_current_point, ai_error_msg_id)
    (JX,JY, R2, uw2, u2, w2) = arc_center_radius_angles(ai_current_point, ai_post_middle, ai_post_point, ai_error_msg_id)
    (MX,MY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkG), (IX,IY),R1, ((GX+SX)/2,(GY+SY)/2), xSC+math.pi, ai_error_msg_id)
    #print("dbg321: MX={:0.2f}  MY={:0.2f}  line_circle_intersection={:0.2f}".format(MX, MY, line_circle_intersection_status))
    if(line_circle_intersection_status==2):
      print("ERR636: Error in {:s} with the line_circle_intersection_status!".format(ai_error_msg_id))
      sys.exit(2)
    (NX,NY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkH), (JX,JY),R2, ((HX+SX)/2,(HY+SY)/2), xSC+math.pi, ai_error_msg_id)
    #print("dbg322: NX={:0.2f}  NY={:0.2f}  line_circle_intersection={:0.2f}".format(NX, NY, line_circle_intersection_status))
    if(line_circle_intersection_status==2):
      print("ERR633: Error in {:s} with the line_circle_intersection_status!".format(ai_error_msg_id))
      #print("dbg513: G={:0.2f} {:0.2f}  H={:0.2f} {:0.2f}".format(GX, GY, HX, HY))
      #sys.exit(2)
      enlarge_status = 2
    # check if arc-arc intersection must be calculated
    tmp_MG_deep_x = (MX-GX)*(CX-FX)
    tmp_MG_deep_y = (MY-GY)*(CY-FY)
    #print("dbg301: tmp_MG_deep_x:", tmp_MG_deep_x)
    #print("dbg302: tmp_MG_deep_y:", tmp_MG_deep_y)
    MG_deep = math.copysign(1, tmp_MG_deep_x)
    if(abs(tmp_MG_deep_x)<abs(tmp_MG_deep_y)):
      MG_deep = math.copysign(1, tmp_MG_deep_y)
      #print("dbg303: use Y to get MG_deep")
    tmp_NH_deep_x = (NX-HX)*(CX-FX)
    tmp_NH_deep_y = (NY-HY)*(CY-FY)
    #print("dbg311: tmp_NH_deep_x:", tmp_NH_deep_x)
    #print("dbg312: tmp_NH_deep_y:", tmp_NH_deep_y)
    NH_deep = math.copysign(1, tmp_NH_deep_x)
    if(abs(tmp_NH_deep_x)<abs(tmp_NH_deep_y)):
      NH_deep = math.copysign(1, tmp_NH_deep_y)
      #print("dbg313: use Y to get NH_deep")
    MKX = MX
    MKY = MY
    NLX = NX
    NLY = NY
    enlarge_type_request_1 = 3
    enlarge_type_request_2 = 3
    # compute the arc-arc intersection
    if(MG_deep>0):
      (KX,KY, triangulation_status) = triangulation((IX,IY),R1,(FX,FY),ai_router_bit_request,(GX,GY), xSC+math.pi, ai_error_msg_id)
      if(triangulation_status==2):
        print("ERR536: Error in {:s} with the triangulation_status!".format(ai_error_msg_id))
        sys.exit(2)
      MKX = KX
      MKY = KY
      enlarge_type_request_1 = 2
    if(NH_deep>0):
      (LX,LY, triangulation_status) = triangulation((JX,JY),R2,(FX,FY),ai_router_bit_request,(HX,HY), xSC+math.pi, ai_error_msg_id)
      if(triangulation_status==2):
        print("ERR533: Error in {:s} with the triangulation_status!".format(ai_error_msg_id))
        sys.exit(2)
      NLX = LX
      NLY = LY
      enlarge_type_request_2 = 2
    lMN=math.sqrt((NLX-MKX)**2+(NLY-MKY)**2)
    if(lMN<radian_epsilon):
      print("WARN667: Warning in {:s}, the angle is too flat to be enlarged!".format(ai_error_msg_id))
      enlarge_type_request_1 = 1
      enlarge_type_request_2 = 1
  # return
  r_sub_enlarge_corner_arc_arc = ((MKX,MKY), (GX,GY), (CX,CY), (HX,HY), (NLX,NLY), enlarge_type_request_1, enlarge_type_request_2, enlarge_status)
  return(r_sub_enlarge_corner_arc_arc)

