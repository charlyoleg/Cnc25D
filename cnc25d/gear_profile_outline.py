# gear_profile_outline.py
# sub-module of gear_profile
# created by charlyoleg on 2013/09/07
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
gear_profile_outline.py is a sub-module of gear_profile.py
It has been created to split the too large gear_profile.py file into two smaller files, easier for editing.
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

# Python standard library
import math
#import sys, argparse
import sys
#from datetime import datetime
#import os, errno
#import re
#import Tkinter # to display the outline in a small GUI
# FreeCAD
#import Part
#from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import small_geometry # use some well-tested functions from the internal of the cnc25d_api

################################################################
# module variable
################################################################
gpo_radian_epsilon_1000 = math.pi/1000 #0.003
#gpo_radian_epsilon_10000 = gpo_radian_epsilon_1000/10 #0.0003
gpo_radian_epsilon_100000 = gpo_radian_epsilon_1000/100 #0.0003
gpo_radian_epsilon_100 = gpo_radian_epsilon_1000*10 # 0.03
gpo_radian_epsilon_10 = gpo_radian_epsilon_1000*100 # 0.3
#gpo_radian_big_epsilon = math.pi/5 # almost 1 mm !

################################################################
# gear_profile help functions (including involute_to_circle)
################################################################

#############################################################################
# make gear_profile_outline
#############################################################################

def involute_to_circle(ai_center, ai_base_radius, ai_initial_angle, ai_orientation, ai_parameter):
  """ Compute the Cartesian coordinates of P a point of an involute_to_circle curve with the parameter u
      ai_center: center of the base circle (O)
      ai_base_radius: radius of the base circle (B)
      ai_initial_angle : angle (xOS) with (S) start of of the involute_to_circle
      ai_orientation: orienation of the involute_to_circle: 1=CCW -1=CW
      it returns: the Cartesian coordinates of (P) and the tangent inclination (xPt)
  """
  # use notation of the documentation
  OX = ai_center[0]
  OY = ai_center[1]
  B = ai_base_radius
  s = ai_initial_angle
  rd = ai_orientation
  u = ai_parameter
  # check the parameter
  if(u<0):
    print("ERR099: Error, the parameter of the involute_to_circle must be positive {:0.8f}".format(u))
    print("dbg887: ai_center {:0.2f} {:0.2f}  ai_base_radius {:0.2f}  ai_initial_angle {:0.2f}  ai_orientation {:d}  ai_parameter {:0.2f}".format(ai_center[0], ai_center[1], ai_base_radius, ai_initial_angle, ai_orientation, ai_parameter))
    sys.exit(2)
  # involute_to_circle of center (0,0), radius 1 and initial_angle = 0 with the parameter u
  px0 = math.cos(u)+u*math.sin(u)
  py0 = rd*(math.sin(u)-u*math.cos(u))
  ti0 = math.fmod(rd*u+math.pi, 2*math.pi) - math.pi # =u translated in [-pi,pi[
  # involute_to_circle of center (OX,OY), radius B and initial_angle = s with the parameter u
  px = OX+math.cos(s)*B*px0-math.sin(s)*B*py0
  py = OY+math.sin(s)*B*px0+math.cos(s)*B*py0
  ti = math.fmod(ti0+s+3*math.pi, 2*math.pi) - math.pi #=u+s translated in [-pi,pi[
  # return
  r_itc=(px, py, ti)
  return(r_itc)

def search_point_of_involute_to_circle(ai_center, ai_base_radius, ai_initial_angle, ai_orientation, ai_altitude, ai_step, ai_precision):
  """ Compute the coordinates of the intersection (P) of an involute_to_circle curve and a circle of raidus ai_altitude
      ai_center: center of the base circle and of the other circle (O)
      ai_base_radius: radius of the base circle (B)
      ai_initial_angle : angle (xOS) with (S) start of of the involute_to_circle
      ai_orientation: orienation of the involute_to_circle: 1=CCW -1=CW
      ai_altitude: radius of the other circle
      ai_step: initial increment of the parameter to converge to (P)
      ai_precision: required precision to get closer to ai_altitude
      it returns: the paramter u, the angle (xOP), the Cartesian coordinates of (P), the tangent inclination (xPt)
  """
  #print("dbg974: ai_center:", ai_center)
  #print("dbg975: ai_base_radius:", ai_base_radius)
  #print("dbg976: ai_initial_angle:", ai_initial_angle)
  #print("dbg977: ai_orientation:", ai_orientation)
  #print("dbg978: ai_altitude:", ai_altitude)
  #print("dbg979: ai_step:", ai_step)
  #print("dbg980: ai_precision:", ai_precision)
  # use notation of the documentation
  OX = ai_center[0]
  OY = ai_center[1]
  B = ai_base_radius
  s = ai_initial_angle
  rd = ai_orientation
  R = ai_altitude
  # check the paramter
  if(R<B):
    print("ERR098: Error, the altitude {:0.2f} is smaller than the base_diameter {:0.2f}".format(R, B))
    sys.exit(2)
  ### method 1
  ## converge to P
  #u = 0
  #step = ai_step
  #error = -2*ai_precision
  #iteration_cnt = 0
  #while(abs(error)>ai_precision):
  #  iteration_cnt += 1
  #  #print("dbg351: iteration_cnt: {:d}  u: {:0.6f}  step: {:0.6f}  error: {:0.6f}".format(iteration_cnt, u, step, error))
  #  (px, py, ti) = involute_to_circle((OX,OY), B, s, rd, u)
  #  OP = math.sqrt((px-OX)**2+(py-OY)**2)
  #  sign_old_error = math.copysign(1, error)
  #  error = OP-R
  #  sign_new_error = math.copysign(1, error)
  #  if(sign_old_error*sign_new_error<0):
  #    step = step/2
  #  if(sign_new_error<0):
  #    u=u+step
  #  else:
  #    u=u-step
  ## we get u, px, py and ti
  ## calcultation of a = angle (xOP)
  #a = math.atan2((py-OY)/OP, (px-OX)/OP)
  #r_spoitc = (u, a, px, py, ti)
  ### method 2
  u2 = math.sqrt((R/B)**2-1)
  a2 = s+rd*(u2-math.atan(u2))
  ## compare the result of the two methods
  #if(abs(u2-u)>2*ai_precision)2:
  #  print("ERR877: Error in the calculation of u {:0.3f} or u2 {:0.3f}".format(u, u2))
  #  sys.exit(2)
  #if(abs(a2-a)>2*ai_precision):
  #  print("ERR878: Error in the calculation of a {:0.3f} or a2 {:0.3f}".format(a, a2))
  #  sys.exit(2)
  (px2, py2, ti2) = involute_to_circle((OX,OY), B, s, rd, u2)
  # return
  r_spoitc = (u2, a2, px2, py2, ti2)
  return(r_spoitc)

def sample_of_gear_tooth_profile(ai_center, ai_base_radius, ai_initial_angle, ai_orientation, ai_thickness_offset, ai_parameter):
  """ Compute the Cartesian coordinates of Q a point of a gear_tooth_profile with the parameter u
      ai_center: center of the base circle (O)
      ai_base_radius: radius of the base circle (B)
      ai_initial_angle : angle (xOS) with (S) start of of the involute_to_circle
      ai_orientation: orienation of the involute_to_circle: 1=CCW -1=CW
      ai_thickness_offset: translation apply to P. The translation is perpendicular to the tangent. Positive if move away from (O). Negative if move closer to (O)
      it returns: the Cartesian coordinates of (Q) and the tangent inclination (xPt)
  """
  (px, py, ti) = involute_to_circle(ai_center, ai_base_radius, ai_initial_angle, ai_orientation, ai_parameter)
  #rd = ai_orientation
  #qx = px + ai_thickness_offset*math.cos(ti-rd*math.pi/2) # cos(a-pi/2)=sin(a)   cos(a+pi/2)=-sin(a)
  #qy = py + ai_thickness_offset*math.sin(ti-rd*math.pi/2) # sin(a-pi/2)=-cos(a)  sin(a+pi/2)=cos(a)
  qx = px + ai_orientation*ai_thickness_offset*math.sin(ti)
  qy = py - ai_orientation*ai_thickness_offset*math.cos(ti)
  # return
  r_sogtp = (qx, qy, ti)
  return(r_sogtp)

def calc_low_level_gear_parameters(ai_param):
  """ From the hight level parameters relative to a gearwheel (or gearbar) and returns the low level parameters required to compute the gearwheel outline
      It also adds some parameters to the high-level parameter dictionary ai_param. So this function must be called before calling pre_g2_position_calculation()
  """
  # get the hight level parameters
  g_type  = ai_param['gear_type']
  g_n     = ai_param['full_tooth_nb']
  g_m     = ai_param['module']
  g_pr    = ai_param['primitive_radius']
  g_adp   = ai_param['addendum_dedendum_parity']
  #g_thh   = ai_param['tooth_half_height']
  g_ar    = ai_param['addendum_radius']
  g_dr    = ai_param['dedendum_radius']
  g_brp   = ai_param['positive_base_radius']
  g_brn   = ai_param['negative_base_radius']
  g_ox    = ai_param['center_ox']
  g_oy    = ai_param['center_oy']
  g_rbr   = ai_param['gear_router_bit_radius']
  g_hr    = ai_param['hollow_radius']
  g_irp   = ai_param['positive_involute_resolution']
  g_irn   = ai_param['negative_involute_resolution']
  g_stp   = ai_param['positive_skin_thickness']
  g_stn   = ai_param['negative_skin_thickness']
  g_ptn   = ai_param['portion_tooth_nb']
  g_pfe   = ai_param['portion_first_end']
  g_ple   = ai_param['portion_last_end']
  g_bi    = ai_param['gearbar_inclination']
  g_sp    = ai_param['positive_slope_angle']
  g_sn    = ai_param['negative_slope_angle']
  g_ah    = ai_param['addendum_height']
  g_dh    = ai_param['dedendum_height']
  g_hh    = ai_param['hollow_height']
  g_ks    = ai_param['gear_sign']
  # precision
  radian_epsilon = math.pi/1000
  radian_epsilon_2 = math.pi/10000
  ### check
  #print("dbg233: g_ptn: {:d}".format(g_ptn))
  # tooth height check
  #
  if(g_ks*(g_pr-g_dr)<0):
    print("ERR985: Error, g_pr {:0.2f} and g_dr {:0.2f} are not in the correct order!".format(g_pr, g_dr))
    sys.exit(2)
  if(g_ks*(g_ar-g_pr)<0):
    print("ERR986: Error, g_pr {:0.2f} and g_ar {:0.2f} are not in the correct order!".format(g_pr, g_ar))
    sys.exit(2)
  # involute resolution check
  if(g_irp<1):
    print("ERR786: Error, g_irp {:d} must be equal or bigger than 1!".format(g_irp))
    sys.exit(2)
  if(g_irn<1):
    print("ERR787: Error, g_irn {:d} must be equal or bigger than 1!".format(g_irn))
    sys.exit(2)
  ### calculation of the low level parameters
  r_low_parameters = ()
  if((g_type=='e')or(g_type=='i')):
    ### search points
    initial_step = float(g_ar-g_dr)/4
    #pi_module_angle = 2*math.pi/g_n
    pi_module_angle = ai_param['pi_module_angle']
    # intersection of positive involute and the primitive circle
    if(g_brp>g_pr-radian_epsilon):
      print("ERR987: Error, g_brp {:0.2f} is bigger than g_pr {:0.2f}!".format(g_brp, g_pr))
      sys.exit(2)
    (ippu, ippa, ippx, ippy, ippti) = search_point_of_involute_to_circle((g_ox, g_oy), g_brp, 0, 1, g_pr, initial_step, radian_epsilon_2)
    #ai_param['low_positive_primitive_angle'] = ippa
    # intersection of negative involute and the primitive circle
    if(g_brn>g_pr-radian_epsilon):
      print("ERR988: Error, g_brn {:0.2f} is bigger than g_pr {:0.2f}!".format(g_brp, g_pr))
      sys.exit(2)
    (inpu, inpa, inpx, inpy, inpti) = search_point_of_involute_to_circle((g_ox, g_oy), g_brn, 0, -1, g_pr, initial_step, radian_epsilon_2)
    #ai_param['low_negative_primitive_angle'] = inpa
    # intersection of positive involute and the addendum circle
    ipau=0; ipaa=0;
    if(g_brp<g_ar): # check for internal gear
      (ipau, ipaa, ipax, ipay, ipati) = search_point_of_involute_to_circle((g_ox, g_oy), g_brp, 0, 1, g_ar, initial_step, radian_epsilon_2)
    ai_param['low_positive_addendum_angle'] = ipaa
    # intersection of negative involute and the addendum circle
    inau=0; inaa=0;
    if(g_brn<g_ar): # check for internal gear
      (inau, inaa, inax, inay, inati) = search_point_of_involute_to_circle((g_ox, g_oy), g_brn, 0, -1, g_ar, initial_step, radian_epsilon_2)
    ai_param['low_negative_addendum_angle'] = inaa
    # intersection of positive involute and the dedendum circle
    ipdu=0; ipda=0; ipdti=0;
    if(g_brp<g_dr): # check for external gear
      (ipdu, ipda, ipdx, ipdy, ipdti) = search_point_of_involute_to_circle((g_ox, g_oy), g_brp, 0, 1, g_dr, initial_step, radian_epsilon_2)
    #ai_param['low_positive_dedendum_angle'] = ipda
    # intersection of negative involute and the dedendum circle
    indu=0; inda=0; indti=0;
    if(g_brn<g_dr): # check for external gear
      (indu, inda, indx, indy, indti) = search_point_of_involute_to_circle((g_ox, g_oy), g_brn, 0, -1, g_dr, initial_step, radian_epsilon_2)
    #ai_param['low_negative_dedendum_angle'] = inda
    #
    full_positive_involute = g_ks*(ipaa-ipda)
    full_negative_involute = -1*g_ks*(inaa-inda)
    addendum_positive_involute = g_ks*(ipaa-ippa)
    addendum_negative_involute = -1*g_ks*(inaa-inpa)
    dedendum_positive_involute = g_ks*(ippa-ipda)
    dedendum_negative_involute = -1*g_ks*(inpa-inda)
    #print("dbg646: full_positive_involute: {:0.3f}  full_negative_involute: {:0.3f}  addendum_positive_involute: {:0.3f}  addendum_negative_involute: {:0.3f}  dedendum_positive_involute: {:0.3f}  dedendum_negative_involute: {:0.3f}".format(full_positive_involute, full_negative_involute, addendum_positive_involute, addendum_negative_involute, dedendum_positive_involute, dedendum_negative_involute))
    top_land = pi_module_angle*g_adp-(addendum_positive_involute+addendum_negative_involute)
    if(top_land*g_ar<radian_epsilon): # a bit stricter than 0
      print("ERR989: Error, the top_land {:0.2f} is negative or too small!".format(top_land))
      print("dbg553: g_pr {:0.3f}  g_brp {:0.3f}  g_brn {:0.3f}".format(g_pr, g_brp, g_brn))
      sys.exit(2)
    bottom_land = pi_module_angle*(1-g_adp)-(dedendum_positive_involute+dedendum_negative_involute)
    if(bottom_land*g_dr<2.1*g_rbr): # a bit stricter than router_bit_radius
      print("ERR990: Error, the bottom_land {:0.2f} is negative or too small compare to the router_bit_radius {:0.2f} ({:0.2f} < {:0.2f})!".format(bottom_land, g_rbr, bottom_land*g_dr, 2*g_rbr))
      sys.exit(2)
    ai_param['top_land'] = top_land
    ai_param['bottom_land'] = bottom_land
    ai_param['addendum_positive_involute'] = addendum_positive_involute
    ai_param['addendum_negative_involute'] = addendum_negative_involute
    ai_param['dedendum_positive_involute'] = dedendum_positive_involute
    ai_param['dedendum_negative_involute'] = dedendum_negative_involute
    ai_param['full_positive_involute'] = full_positive_involute
    ai_param['full_negative_involute'] = full_negative_involute
    ai_param['positive_primitive_offset'] = -1*g_ks*(float(top_land)/2 + addendum_positive_involute)
    ai_param['negative_primitive_offset'] =  1*g_ks*(float(top_land)/2 + addendum_negative_involute)
    ai_param['positive_location_offset'] = -1*g_ks*(float(top_land)/2 + g_ks*ipaa)
    ai_param['negative_location_offset'] =  1*g_ks*(float(top_land)/2 - g_ks*inaa)
    #print("dbg223: g_ks {:d}  top_land {:0.3f}  ipaa {:0.3f}  inaa {:0.3f}  positive_location_offset {:0.3f}  negative_location_offset {:0.3f}".format(g_ks, top_land, ipaa, inaa, ai_param['positive_location_offset'],  ai_param['negative_location_offset']))
    if(g_type=='e'): # negative > hollow > positive
      # low1: to create the gear-profile outline
      i1_base = g_brn
      i1_offset = float(top_land)/2-inaa
      i1_sign = -1
      i1u_nb = g_irn
      i1u_ini = inau
      i1u_inc = float(indu-inau)/i1u_nb # <0
      i1_dtri = math.fmod(indti-inda+5*math.pi, 2*math.pi) - math.pi # dedendum tangent relative inclination
      i1_dsl = max(0, g_brn-g_dr) + g_stn*math.tan(i1_dtri) # dedendum_slope_length
      i1_hsl = float(g_hh)/math.cos(i1_dtri)  # hollow slope length
      i1_thickness = g_stn
      i2_base = g_brp
      i2_offset = pi_module_angle-float(top_land)/2-ipaa
      i2_sign = 1
      i2u_nb = g_irp
      i2u_ini = ipdu
      i2u_inc = float(ipau-ipdu)/i2u_nb # >0
      i2_dtri = math.fmod(ipdti-ipda+5*math.pi, 2*math.pi) - math.pi # dedendum tangent relative inclination
      i2_dsl = max(0, g_brp-g_dr) + g_stp*math.tan(i2_dtri) # dedendum_slope_length
      i2_hsl = float(g_hh)/math.cos(i2_dtri) # hollow slope length
      i2_thickness = g_stp
      ha1 = top_land/2 + full_negative_involute
    elif(g_type=='i'): # positive > hollow > negative
      # low1
      i1_base = g_brp
      i1_offset = float(top_land)/2-ipaa
      i1_sign = 1
      i1u_nb = g_irp
      i1u_ini = ipau
      i1u_inc = float(ipdu-ipau)/i1u_nb # >0
      i1_dtri = math.fmod(ipdti-ipda+5*math.pi, 2*math.pi) - math.pi # dedendum tangent relative inclination
      i1_dsl = g_stp*math.tan(i1_dtri)
      i1_hsl = float(g_hh)/math.cos(i1_dtri) # hollow slope length
      i1_thickness = g_stp
      i2_base = g_brn
      i2_offset = pi_module_angle-float(top_land)/2-inaa
      i2_sign = -1
      i2u_nb = g_irn
      i2u_ini = indu
      i2u_inc = float(inau-indu)/i2u_nb # >0
      i2_dtri = math.fmod(indti-inda+5*math.pi, 2*math.pi) - math.pi # dedendum tangent relative inclination
      i2_dsl = g_stn*math.tan(i2_dtri)
      i2_hsl = float(g_hh)/math.cos(i2_dtri)  # hollow slope length
      i2_thickness = g_stn
      ha1 = top_land/2 + full_positive_involute
      #print("dbg663: ipaa {:0.3f}".format(ipaa))
    #print("dbg553: i1_hsl {:0.3f}  i2_hsl {:0.3f}  g_rbr {:0.3f} g_hh  {:0.3f}".format(i1_hsl, i2_hsl, g_rbr, g_hh))
    ### optimization of i1_hsl and i2_hsl
    #bottom_land_length = bottom_land * g_dr
    bottom_land_length = 2 * g_dr * math.sin(bottom_land/2)
    if((g_ks*i1_dtri>0)or(g_ks*i2_dtri<0)):
      print("ERR234: Error, i1_dtri {:0.3f} >0 or i2_dtri {:0.3f} < 0".format(g_ks*i1_dtri, g_ks*i2_dtri))
      sys.exit(2)
    cos_i1_dtri = math.cos(i1_dtri)
    cos_i2_dtri = math.cos(i2_dtri)
    if((cos_i1_dtri<radian_epsilon)or(cos_i1_dtri<radian_epsilon)):
      print("ERR632: Error, i1_dtri {:0.3f} or i2_dtri {:0.3f} are too closed to pi/2 or even bigger!".format(i1_dtri, i2_dtri))
      sys.exit(2)
    ABh = bottom_land_length-i1_thickness/cos_i1_dtri-i2_thickness/cos_i2_dtri # see documentation graphic of hollow optimization
    a = math.pi/2-abs(i1_dtri) - g_ks * bottom_land/2
    b = math.pi/2-abs(i2_dtri) - g_ks * bottom_land/2
    AIB = math.pi - (a + b)
    ho = False # hollow_optimization
    if(AIB>radian_epsilon):
      ### AI, BI (this method has too much imprecision when a=pi/2 or b=pi/2)
      tan_a = math.tan(a)
      tan_b = math.tan(b)
      tan_a_plus_tan_b = tan_a+tan_b
      xi = 0
      yi = 0
      if(tan_a_plus_tan_b>radian_epsilon):
        xi = tan_b*ABh/tan_a_plus_tan_b
        yi = tan_a*xi
      AI = math.sqrt(xi**2+yi**2)
      BI = math.sqrt((ABh-xi)**2+yi**2)
      ## alternative with the law of sine: BI/sin(a) = AI/sin(b) = ABh/sin(AIB)
      AI2 = ABh*math.sin(b)/math.sin(AIB)
      BI2 = ABh*math.sin(a)/math.sin(AIB)
      if(abs(AI2-AI)>radian_epsilon):
        print("ERR972: Error, AI {:0.3f} and AI2 {:0.3f} are not equal".format(AI, AI2))
        print("dbg647: a {:0.3f}  b {:0.3f}  AIB {:0.3f}  ABh {:0.3f}".format(a, b, AIB, ABh))
        sys.exit(2)
      if(abs(BI2-BI)>radian_epsilon):
        print("ERR973: Error, BI {:0.3f} and BI2 {:0.3f} are not equal".format(BI, BI2))
        sys.exit(2)
      # select the method for AI and BI
      AI = AI2
      BI = BI2
      AIO = float(AIB)/2
      IO = g_rbr / math.sin(AIO)
      AIF = math.pi/2-a
      OIF = abs(AIF-AIO)
      IFl = IO * math.cos(OIF)
      IHl = AI * math.sin(a)
      Xh = g_hh - (IHl-IFl)
      #print("dbg974: IO {:0.3f}  IFl {:0.3f}  IHl {:0.3f}  g_hh {:0.3f}  g_rbr {:0.3f}  Xh {:0.3f}".format(IO, IFl, IHl, g_hh, g_rbr, Xh))
      if(Xh>(0.9*g_rbr)): # in this case the hollow is optmized
        ho = True
        i1_hsl = AI
        i2_hsl = BI
    ### portion
    #hlm = g_hr*math.cos(bottom_land/2) # this is to ensure nice junction of split gearwheel
    ham = ha1 + float(bottom_land)/2
    tlm = g_ar*math.cos(top_land/2) # this is to ensure nice junction of split gearwheel
    if(g_ptn==0):
      portion_tooth_nb = g_n
      closed = True
    else:
      portion_tooth_nb = g_ptn
      closed = False
    ai_param['hollow_middle_angle'] = ham
    # return
    make_low_parameters = (g_type, pi_module_angle,
      i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_dsl, i1_hsl, i1_thickness,
      i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_dsl, i2_hsl, i2_thickness,
      ho, g_rbr, ham, tlm,
      g_ox, g_oy, portion_tooth_nb, g_pfe, g_ple, closed)
    # info
    info_txt = "Gear profile details: hollow with {:d} corner\n".format(1 if(ho) else 2)
    info_txt += "positive involute: \t{:0.3f} (radian)  \t{:0.3f} (mm)  \t{:0.2f} %\n".format(full_positive_involute, g_pr*full_positive_involute, 100*full_positive_involute/pi_module_angle)
    info_txt += "negative involute: \t{:0.3f} (radian)  \t{:0.3f} (mm)  \t{:0.2f} %\n".format(full_negative_involute, g_pr*full_negative_involute, 100*full_negative_involute/pi_module_angle)
    info_txt += "top land:          \t{:0.3f} (radian)  \t{:0.3f} (mm)  \t{:0.2f} %\n".format(top_land, g_ar*top_land, 100*top_land/pi_module_angle)
    info_txt += "bottom land:       \t{:0.3f} (radian)  \t{:0.3f} (mm)  \t{:0.2f} %\n".format(bottom_land, g_dr*bottom_land, 100*bottom_land/pi_module_angle)
  elif(g_type=='l'):
    # linear gear make low parameters
    pi_module = g_m * math.pi
    positive_addendum = g_ah*math.tan(g_sp)
    positive_dedendum = abs(g_dh)*math.tan(g_sp)
    negative_addendum = g_ah*math.tan(g_sn)
    negative_dedendum = abs(g_dh)*math.tan(g_sn)
    full_positive_slope = positive_addendum + positive_dedendum
    full_negative_slope = negative_addendum + negative_dedendum
    top_land = pi_module*g_adp-(positive_addendum+negative_addendum)
    bottom_land = pi_module*(1-g_adp)-(positive_dedendum+negative_dedendum)
    if(top_land<radian_epsilon):
      print("ERR858: Error, the linear gear top-land {:0.3f} is negative or too small!".format(top_land))
      print("dbg455: g_sp {:0.3f}  g_sn {:0.3f}".format(g_sp, g_sn))
      sys.exit(2)
    if(bottom_land<2*g_rbr+radian_epsilon):
      print("ERR859: Error, the linear gear bottom-land {:0.3f} is too small compare to the gear_router_bit_radius {:0.3f}".format(bottom_land, g_rbr))
      sys.exit(2)
    ai_param['top_land'] = top_land
    ai_param['bottom_land'] = bottom_land
    ai_param['addendum_positive_slope'] = positive_addendum
    ai_param['addendum_negative_slope'] = negative_addendum
    ai_param['dedendum_positive_slope'] = positive_dedendum
    ai_param['dedendum_negative_slope'] = negative_dedendum
    ai_param['full_positive_slope'] = full_positive_slope
    ai_param['full_negative_slope'] = full_negative_slope
    ai_param['positive_primitive_offset'] =  1*(float(top_land)/2 + positive_addendum)
    ai_param['negative_primitive_offset'] = -1*(float(top_land)/2 + negative_addendum)
    ai_param['positive_location_offset'] = ai_param['positive_primitive_offset']
    ai_param['negative_location_offset'] = ai_param['negative_primitive_offset']
    bar_tooth_nb = g_n
    if(g_ptn>0):
      bar_tooth_nb = g_ptn
    middle_tooth = int(bar_tooth_nb/2)+1
    tlh = g_ah
    blh = g_dh + g_hh
    blx = top_land/2 + negative_addendum + negative_dedendum + bottom_land/2
    g_alp = g_ah/math.cos(g_sp)
    g_dlp = g_dh/math.cos(g_sp)
    g_hlp = g_hh/math.cos(g_sp) + g_stp*math.tan(g_sp)
    g_aln = g_ah/math.cos(g_sn)
    g_dln = g_dh/math.cos(g_sn)
    g_hln = g_hh/math.cos(g_sn) + g_stn*math.tan(g_sn)
    gb_p_offset = top_land/2+positive_addendum
    gb_n_offset = -1*(top_land/2+negative_addendum)
    ## hollow optimization
    ho = False
    cos_p = math.cos(g_sp)
    cos_n = math.cos(g_sn)
    if((cos_p<radian_epsilon)or(cos_n<radian_epsilon)):
      print("ERR334: Error, g_sp {:0.3f}  or g_sn {:0.3f} are too closed to pi/2 or even bigger!".format(cos_p, cos_n))
      sys.exit(2)
    ABh = bottom_land - g_stp/cos_p - g_stn/cos_n
    a = math.pi/2-abs(g_sp)
    b = math.pi/2-abs(g_sn)
    AIB = math.pi - (a + b)
    if(AIB>radian_epsilon):
      AI = ABh*math.sin(b)/math.sin(AIB)
      BI = ABh*math.sin(a)/math.sin(AIB)
      AIO = float(AIB)/2
      IO = g_rbr / math.sin(AIO)
      AIF = math.pi/2-a
      OIF = abs(AIF-AIO)
      IFl = IO * math.cos(OIF)
      IHl = AI * math.sin(a)
      Xh = g_hh - (IHl-IFl)
      if(Xh>(0.9*g_rbr)): # in this case the hollow is optmized
        ho = True
        g_hlp = AI
        g_hln = BI
    # return
    make_low_parameters = (g_type, pi_module, g_ox, g_oy, g_bi, bar_tooth_nb, middle_tooth, g_pfe, g_ple, tlh, blh, blx, ho,
                            g_sp, g_sn, g_alp, g_dlp, g_hlp, g_aln, g_dln, g_hln, g_rbr, g_stp, g_stn, gb_p_offset, gb_n_offset)
    # info
    info_txt = "Gearbar profile details: hollow with {:d} corner\n".format(1 if(ho) else 2)
    info_txt += "positive slope: \t{:0.3f} (mm)  \t{:0.2f} %\n".format(full_positive_slope, 100*full_positive_slope/pi_module)
    info_txt += "negative slope: \t{:0.3f} (mm)  \t{:0.2f} %\n".format(full_negative_slope, 100*full_negative_slope/pi_module)
    info_txt += "top land:          \t{:0.3f} (mm)  \t{:0.2f} %\n".format(top_land, 100*top_land/pi_module)
    info_txt += "bottom land:       \t{:0.3f} (mm)  \t{:0.2f} %\n".format(bottom_land, 100*bottom_land/pi_module)
  else:
    print("ERR740: Error, the gear_type {:s} doesn't exist!".format(g_type))
    sys.exit(2)
  #return
  r_cllgp = (make_low_parameters, info_txt)
  return(r_cllgp)

def involute_outline(ai_ox, ai_oy, ai_base_radius, ai_offset, ai_sign, ai_u_nb, ai_u_ini, ai_u_inc, ai_thickness, ai_g_type, ai_he, ai_dsl, ai_hsl, ai_rbr, ai_tooth_angle):
  """ from subset of low-level parameter, generates an involute_to_circle format B outline
  """
  # precision
  #radian_epsilon=math.pi/1000 # unefficient because this function is used often
  radian_epsilon = gpo_radian_epsilon_1000
  #
  u = ai_u_ini
  involute_C = []
  for sampling in range(ai_u_nb+1):
    #print("dbg443: u:", u)
    if(abs(u)<radian_epsilon): # for rounding error
      u=0
    (qx, qy, ti) = sample_of_gear_tooth_profile((ai_ox,ai_oy), ai_base_radius, ai_tooth_angle+ai_offset, ai_sign, ai_thickness, u)
    involute_C.append((qx, qy, ti-(ai_sign-1)/2*math.pi))
    u += ai_u_inc
  #print("dbg444: involute_C:", involute_C)
  r_involute_B = cnc25d_api.smooth_outline_c_curve(involute_C, radian_epsilon, 0, "involute_outline")
  # hollow slope
  r_hollow_slope_A = ()
  inv_tangent = (1 + math.copysign(1, ai_u_inc) * ai_g_type)/2
  if(ai_he==1):
    p2x = involute_C[0][0]
    p2y = involute_C[0][1]
    p2t = involute_C[0][2] + inv_tangent * math.pi
    p1x = p2x + (ai_dsl + ai_hsl) * math.cos(p2t)
    p1y = p2y + (ai_dsl + ai_hsl) * math.sin(p2t)
    r_hollow_slope_A = ((p1x, p1y, ai_rbr), (p2x, p2y, 0))
    r_ti = p2t
  elif(ai_he==-1):
    p1x = involute_C[-1][0]
    p1y = involute_C[-1][1]
    p1t = involute_C[-1][2] + inv_tangent * math.pi
    p2x = p1x + (ai_dsl + ai_hsl) * math.cos(p1t)
    p2y = p1y + (ai_dsl + ai_hsl) * math.sin(p1t)
    r_hollow_slope_A = ((p1x, p1y, 0), (p2x, p2y, ai_rbr))
    r_ti = p1t
  else:
    print("ERR563: Error, the hollow end {:d} can only be 1 or -1".format(ai_he))
    sys.exit(2)
  return(r_involute_B, r_hollow_slope_A, r_ti)

def half_hollow_outline(ai_tooth_angle, ai_sx, ai_sy, ai_si, ai_hrbr, ai_ham, ai_first_nlast, ai_ox, ai_oy):
  """ generate the half-hollow outline for the end_type 3
  """
  # rename variable
  fnl = ai_first_nlast
  # center of the half-hollow arc
  csx = ai_si+fnl*math.pi/2
  cx = ai_sx + ai_hrbr*math.cos(csx)
  cy = ai_sy + ai_hrbr*math.sin(csx)
  # angle (SOC)
  osl = math.sqrt((ai_sx-ai_ox)**2+(ai_sy-ai_oy)**2)
  ocl = math.sqrt((cx-ai_ox)**2+(cy-ai_oy)**2)
  sox = math.atan2((ai_sy-ai_oy)/osl, (ai_sx-ai_ox)/osl)
  cox = math.atan2((cy-ai_oy)/ocl, (cx-ai_ox)/ocl)
  soc = math.fmod(fnl*(sox-cox)+5*math.pi, 2*math.pi) - math.pi
  #print("dbg581: cox {:0.3f}  soc {:0.3f}".format(cox, soc))
  if(soc<ai_ham):
    #print("dbg731: large half-hollow {:d}".format(fnl))
    ## P
    pcx = cox+math.pi
    px = cx + ai_hrbr*math.cos(pcx)
    py = cy + ai_hrbr*math.sin(pcx)
    ## T
    otl = ocl - ai_hrbr
    tox = ai_tooth_angle - fnl * ai_ham
    tx = ai_ox + otl * math.cos(tox)
    ty = ai_oy + otl * math.sin(tox)
  else: # this case is very rare (maybe impossible because of the restriction on hrbr). So this code has not been tested yet!
    print("dbg732: narrow half-hollow {:d}".format(fnl))
    ## P (identical with T)
    # angle poc
    pox = ai_tooth_angle - fnl * ai_ham
    poc = math.fmod(fnl*(pox-cox)+5*math.pi, 2*math.pi) - math.pi
    # angle opc with the law of sines
    pcl = ai_hrbr
    opc = math.asin(ocl*math.sin(poc)/pcl)
    # angle ocp
    ocp = math.pi - opc - poc
    # angle pcx
    pcx = math.fmod(cox + math.pi + ocp + 5*math.pi, 2*math.pi) - math.pi
    # px, py
    px = cx + ai_hrbr*math.cos(pcx)
    py = cy + ai_hrbr*math.sin(pcx)
  ## Q
  # angle scp = scx - pcx = csx+pi - pcx
  scx = csx + math.pi
  scp = math.fmod(pcx - scx +5*math.pi, 2*math.pi) - math.pi
  qsx = scx + scp/2
  qx = cx + ai_hrbr*math.cos(qsx)
  qy = cy + ai_hrbr*math.sin(qsx)
  # half-hollow outline
  if(soc<ai_ham):
    r_hho = [(tx,ty), (px,py), (qx,qy, ai_sx,ai_sy)]
  else:
    r_hho = [(px,py), (qx,qy, ai_sx,ai_sy)]
  if(fnl==-1):
    r_hho = cnc25d_api.outline_reverse(r_hho)
  return(r_hho)

def gearwheel_profile_outline(ai_low_parameters, ai_angle_position):
  """ create the outline of a gear definied by ai_low_parameters
      The reference of a gearwheel is the middle of its first tooth.
      ai_angle_position sets the reference of the gearwheel.
  """
  # get ai_low_parameters
  (gear_type, pi_module_angle,
    i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_dsl, i1_hsl, i1_thickness,
    i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_dsl, i2_hsl, i2_thickness,
    ho, hrbr, ham, tlm,
    ox, oy, portion_tooth_nb, first_end, last_end, closed) = ai_low_parameters
  # precision
  #radian_epsilon = math.pi/1000
  radian_epsilon = gpo_radian_epsilon_1000
  #radian_big_epsilon =  gpo_radian_big_epsilon
  # hollow_gear_type
  if(gear_type=='e'):
    hgt = 1
  elif(gear_type=='i'):
    hgt = -1
  else:
    print("ERR556: gear_type {:s} must be 'e' or 'i'".format(gear_type))
    sys.exit(2)
  # construct the final_outline
  r_final_outline = []
  tooth_angle = ai_angle_position
  ### start of the gearwheel_portion
  if(first_end>0):
    half_hollow = []
    start_of_profile_B = []
    if(first_end==1):
      start_of_profile_B = [(ox+tlm*math.cos(tooth_angle), oy+tlm*math.sin(tooth_angle))]
    elif(first_end==2):
      (start_of_profile_B, tooth_slope_A, s_ti) = involute_outline(ox, oy, i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_thickness, hgt, 1, i2_dsl, 0, 0, tooth_angle-pi_module_angle)
      if(i2_dsl>0):
        half_hollow =  cnc25d_api.cnc_cut_outline(tooth_slope_A, "dedendum_base_line")
    elif(first_end==3):
      (start_of_profile_B, tooth_slope_A, s_ti) = involute_outline(ox, oy, i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_thickness, hgt, 1, i2_dsl, 0.3*hrbr, 0, tooth_angle-pi_module_angle)
      half_hollow = half_hollow_outline(tooth_angle, tooth_slope_A[0][0], tooth_slope_A[0][1], s_ti, hrbr, ham, 1, ox, oy)
    # assembly
    r_final_outline.extend(half_hollow)
    r_final_outline.extend(start_of_profile_B)
  ### bulk of the gearwheel_portion
  for tooth in range(portion_tooth_nb):
    # first involute
    (first_involute_B, first_hollow_slope_A, s_ti) = involute_outline(ox, oy, i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_thickness, hgt, -1, i1_dsl, i1_hsl, hrbr, tooth_angle)
    # second involute
    (second_involute_B, second_hollow_slope_A, s_ti) = involute_outline(ox, oy, i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_thickness, hgt, 1, i2_dsl, i2_hsl, hrbr, tooth_angle)
    # gearwheel hollow
    hollow_A = []
    hollow_A.extend(first_hollow_slope_A)
    if(ho):
      hollow_A.append(second_hollow_slope_A[1])
    else:
      hollow_A.extend(second_hollow_slope_A)
    # check the optimization
    if(ho):
      if((abs(first_hollow_slope_A[1][0]-second_hollow_slope_A[0][0])>radian_epsilon)or(abs(first_hollow_slope_A[1][1]-second_hollow_slope_A[0][1])>radian_epsilon)):
        print("ERR582: the hollow optimization intersection is wrong: x1 {:0.3f}   x2 {:0.3f}  y1 {:0.3f}   y2 {:0.3f}".format(first_hollow_slope_A[1][0], second_hollow_slope_A[0][0], first_hollow_slope_A[1][1], second_hollow_slope_A[0][1]))
        #hollow_A = []
        #hollow_A.extend(first_hollow_slope_A)
        #hollow_A.extend(second_hollow_slope_A)
        sys.exit(2)
    hollow_B = cnc25d_api.cnc_cut_outline(hollow_A, "hollow")
    # assembly
    r_final_outline.extend(first_involute_B)
    r_final_outline.extend(hollow_B[1:-1])
    r_final_outline.extend(second_involute_B)
    # prepare the next tooth
    tooth_angle += pi_module_angle
  ### end of bulk
  if(last_end>0):
    half_hollow = []
    end_of_profile_B = []
    if(last_end==1):
      end_of_profile_B = [(ox+tlm*math.cos(tooth_angle), oy+tlm*math.sin(tooth_angle))]
    elif(last_end==2):
      (end_of_profile_B, tooth_slope_A, s_ti) = involute_outline(ox, oy, i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_thickness, hgt, -1, i1_dsl, 0, 0, tooth_angle)
      if(i1_dsl>0):
        half_hollow = cnc25d_api.cnc_cut_outline(tooth_slope_A, "base_dedendum_line")
    # gearwheel hollow
    elif(last_end==3):
      (end_of_profile_B, tooth_slope_A, s_ti) = involute_outline(ox, oy, i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_thickness, hgt, -1, i1_dsl, 0.3*hrbr, 0, tooth_angle)
      half_hollow.extend(half_hollow_outline(tooth_angle, tooth_slope_A[1][0], tooth_slope_A[1][1], s_ti, hrbr, ham, -1, ox, oy))
    # assembly
    r_final_outline.extend(end_of_profile_B)
    r_final_outline.extend(half_hollow)
  if(closed):
    r_final_outline.append(r_final_outline[0]) # closed the outline in case of full gearwheel
  #return
  return(r_final_outline)

def ideal_involute_tooth_outline(ai_low_parameters, ai_angle_position, ai_thickness_coeff):
  """ create the ideal tooth_profile over the first tooth of an intern or extern gearwheel
  """
  # precision
  #radian_epsilon=math.pi/1000 # unefficient because this function is used often
  radian_epsilon = gpo_radian_epsilon_1000
  # get ai_low_parameters
  (gear_type, pi_module_angle,
    i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_dsl, i1_hsl, i1_thickness,
    i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_dsl, i2_hsl, i2_thickness,
    ho, hrbr, ham, tlm,
    ox, oy, portion_tooth_nb, first_end, last_end, closed) = ai_low_parameters
  # precision
  ideal = 8 # additional_sampling_for_ideal_curve. it's a multiplicator
  # initialization
  tooth_angle = ai_angle_position
  # construct the ideal_tooth_outline over the first tooth
  # first_involute
  first_involute = []
  u = i2u_ini
  ideal_i2u_inc = float(i2u_inc)/ideal
  for sampling in range(ideal*i2u_nb+1):
    if(abs(u)<radian_epsilon): # for rounding error
      u=0
    (qx, qy, ti) = sample_of_gear_tooth_profile((ox,oy), i2_base, tooth_angle-pi_module_angle+i2_offset, i2_sign, ai_thickness_coeff*i2_thickness, u)
    first_involute.append((qx, qy))
    u += ideal_i2u_inc
  # second_involute
  second_involute = []
  u = i1u_ini
  ideal_i1u_inc = float(i1u_inc)/ideal
  for sampling in range(ideal*i1u_nb+1):
    if(abs(u)<radian_epsilon): # for rounding error
      u=0
    (qx, qy, ti) = sample_of_gear_tooth_profile((ox,oy), i1_base, tooth_angle+i1_offset, i1_sign, ai_thickness_coeff*i1_thickness, u)
    second_involute.append((qx, qy))
    u += ideal_i1u_inc
  # assembly
  r_ideal_tooth_outline = []
  r_ideal_tooth_outline.extend(first_involute)
  r_ideal_tooth_outline.extend(second_involute)
  #return
  return(r_ideal_tooth_outline)

def slope_outline(ai_ox, ai_oy, ai_bi, ai_offset, ai_slope_angle, ai_sign, ai_top_length, ai_bottom_length, ai_hollow_length, ai_thickness, ai_bottom_router_bit, ai_tooth_position):
  """ from subset of low-level parameter, generates a gearbear_tooth_slope format B outline
  """
  # precision
  #radian_epsilon=math.pi/1000 # unefficient because this function is used often
  radian_epsilon = gpo_radian_epsilon_1000
  #
  slope_angle = ai_bi + ai_sign*ai_slope_angle
  thickness_angle = slope_angle - ai_sign*math.pi/2
  #top_height = ai_top_height/math.cos(ai_slope_angle)
  #bottom_height = ai_bottom_height/math.cos(ai_slope_angle)
  top_length = ai_top_length
  bottom_length = ai_bottom_length + ai_hollow_length
  #
  top_x = ai_ox + (ai_tooth_position+ai_offset)*math.cos(ai_bi-math.pi/2) + top_length*math.cos(slope_angle) + ai_thickness*math.cos(thickness_angle)
  top_y = ai_oy + (ai_tooth_position+ai_offset)*math.sin(ai_bi-math.pi/2) + top_length*math.sin(slope_angle) + ai_thickness*math.sin(thickness_angle)
  bottom_x = ai_ox + (ai_tooth_position+ai_offset)*math.cos(ai_bi-math.pi/2) - bottom_length*math.cos(slope_angle) + ai_thickness*math.cos(thickness_angle)
  bottom_y = ai_oy + (ai_tooth_position+ai_offset)*math.sin(ai_bi-math.pi/2) - bottom_length*math.sin(slope_angle) + ai_thickness*math.sin(thickness_angle)
  #
  if(ai_sign==1):
    r_slope_B = ((top_x, top_y, 0),(bottom_x, bottom_y, ai_bottom_router_bit))
  elif(ai_sign==-1):
    r_slope_B = ((bottom_x, bottom_y, ai_bottom_router_bit),(top_x, top_y, 0))
  # return
  return(r_slope_B)

def gearbar_profile_outline(ai_low_parameters, ai_tangential_position):
  """ create the outline of a gearbar definied by ai_low_parameters
      The reference of a gearbar is the middle of the middle tooth.
      ai_tangential_position sets the reference of the gearbar.
  """
  # precision
  #radian_epsilon = math.pi/1000
  radian_epsilon = gpo_radian_epsilon_1000
  #radian_big_epsilon =  gpo_radian_big_epsilon
  # get ai_low_parameters
  #(g_type, pi_module, g_ox, g_oy, g_bi, bar_tooth_nb, g_pfe, g_ple, g_sp, g_sn, g_ah, g_dh, g_hh, g_rbr, g_stp, g_stn, gb_p_offset, gb_n_offset) = ai_low_parameters
  (g_type, pi_module, g_ox, g_oy, g_bi, bar_tooth_nb, middle_tooth, g_pfe, g_ple, tlh, blh, blx, ho,
    g_sp, g_sn, g_alp, g_dlp, g_hlp, g_aln, g_dln, g_hln, g_rbr, g_stp, g_stn, gb_p_offset, gb_n_offset) = ai_low_parameters
  # construct the final_outline
  r_final_outline = []
  cyclic_tangential_position = math.fmod(ai_tangential_position, (middle_tooth-1)*pi_module) # to avoid the gearbar move away from its gearwheel
  tangential_position = cyclic_tangential_position - middle_tooth*pi_module # the position reference is the middle of the middle tooth
  # start of the gearbar
  gearbar_A = []
  if(g_pfe==3): # start on hollow_middle
    hollow_middle_x = g_ox + (tangential_position-pi_module+blx)*math.cos(g_bi-math.pi/2) + blh*math.cos(g_bi+math.pi)
    hollow_middle_y = g_oy + (tangential_position-pi_module+blx)*math.sin(g_bi-math.pi/2) + blh*math.sin(g_bi+math.pi)
    gearbar_A.append((hollow_middle_x, hollow_middle_y, 0)) # hollow middle
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_n_offset, g_sn, -1, g_aln, g_dln, g_hln, g_stn, g_rbr, tangential_position)) # negative slope
  elif(g_pfe==2): # start on the negative slope
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_n_offset, g_sn, -1, g_aln, g_dln, 0, g_stn, 0, tangential_position)) # negative slope
  elif(g_pfe==1): # start on the top middle
    top_middle_x = g_ox + tangential_position*math.cos(g_bi-math.pi/2) + tlh*math.cos(g_bi)
    top_middle_y = g_oy + tangential_position*math.sin(g_bi-math.pi/2) + tlh*math.sin(g_bi)
    gearbar_A.append((top_middle_x, top_middle_y, 0)) # top middle
  if(len(gearbar_A)>1):
    gearbar_B = cnc25d_api.cnc_cut_outline(gearbar_A, "start of gearbar")
    r_final_outline.extend(gearbar_B)
  elif(len(gearbar_A)==1):
    r_final_outline.append((gearbar_A[0][0], gearbar_A[0][1]))
  # bulk of the gearbar
  for tooth in range(bar_tooth_nb):
    gearbar_A = []
    l_positive_slope = slope_outline(g_ox, g_oy, g_bi, gb_p_offset, g_sp,  1, g_alp, g_dlp, g_hlp, g_stp, g_rbr, tangential_position) # positive slope
    l_negative_slope = slope_outline(g_ox, g_oy, g_bi, gb_n_offset, g_sn, -1, g_aln, g_dln, g_hln, g_stn, g_rbr, tangential_position+pi_module) # negative slope
    if(ho):
      if((abs(l_negative_slope[0][0]-l_positive_slope[1][0])>radian_epsilon)or(abs(l_negative_slope[0][1]-l_positive_slope[1][1])>radian_epsilon)):
        print("ERR583: the gearbar hollow optimization intersection is wrong: x1 {:0.3f}   x2 {:0.3f}  y1 {:0.3f}   y2 {:0.3f}".format(l_positive_slope[1][0], l_negative_slope[0][0], l_positive_slope[1][1], l_negative_slope[0][1]))
        sys.exit(2)
    gearbar_A.extend(l_positive_slope)
    if(ho):
      gearbar_A.append(l_negative_slope[1])
    else:
      gearbar_A.extend(l_negative_slope)
    #print("dbg745: gearbar_A:", gearbar_A)
    gearbar_B = cnc25d_api.cnc_cut_outline(gearbar_A, "bulk of gearbar")
    r_final_outline.extend(gearbar_B)
    # prepare the next tooth
    tangential_position += pi_module
  # end of the gearbar
  gearbar_A = []
  if(g_ple==3): # stop on hollow_middle
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_p_offset, g_sp,  1, g_alp, g_dlp, g_hlp, g_stp, g_rbr, tangential_position)) # positive slope
    hollow_middle_x = g_ox + (tangential_position+blx)*math.cos(g_bi-math.pi/2) + blh*math.cos(g_bi+math.pi)
    hollow_middle_y = g_oy + (tangential_position+blx)*math.sin(g_bi-math.pi/2) + blh*math.sin(g_bi+math.pi)
    gearbar_A.append((hollow_middle_x, hollow_middle_y, 0)) # hollow middle
  elif(g_ple==2): # stop on the positive slope
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_p_offset, g_sp,  1, g_alp, g_dlp, 0, g_stp, 0, tangential_position)) # positive slope
  elif(g_ple==1): # stop on the top middle
    top_middle_x = g_ox + tangential_position*math.cos(g_bi-math.pi/2) + tlh*math.cos(g_bi)
    top_middle_y = g_oy + tangential_position*math.sin(g_bi-math.pi/2) + tlh*math.sin(g_bi)
    gearbar_A.append((top_middle_x, top_middle_y, 0)) # top middle
  if(len(gearbar_A)>1):
    gearbar_B = cnc25d_api.cnc_cut_outline(gearbar_A, "end of gearbar")
    r_final_outline.extend(gearbar_B)
  elif(len(gearbar_A)==1):
    r_final_outline.append((gearbar_A[0][0], gearbar_A[0][1]))
  #return
  return(r_final_outline)

def ideal_linear_tooth_outline(ai_low_parameters, ai_tangential_position, ai_thickness_coeff):
  """ create the ideal tooth_profile over the first tooth of a gearbar
  """
  # get ai_low_parameters
  (g_type, pi_module, g_ox, g_oy, g_bi, bar_tooth_nb, middle_tooth, g_pfe, g_ple, tlh, blh, blx, ho,
    g_sp, g_sn, g_alp, g_dlp, g_hlp, g_aln, g_dln, g_hln, g_rbr, g_stp, g_stn, gb_p_offset, gb_n_offset) = ai_low_parameters
  cyclic_tangential_position = math.fmod(ai_tangential_position, (middle_tooth-1)*pi_module) # to avoid the gearbar move away from its gearwheel
  #tangential_position = cyclic_tangential_position - middle_tooth*pi_module # the position reference is the middle of the middle tooth
  tangential_position = cyclic_tangential_position
  # tooth
  tooth_A = []
  tooth_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_n_offset, g_sn, -1, g_aln, g_dln, 0, ai_thickness_coeff*g_stn, 0, tangential_position))
  tooth_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_p_offset, g_sp,  1, g_alp, g_dlp, 0, ai_thickness_coeff*g_stp, 0, tangential_position))
  r_ideal_tooth_outline_B = cnc25d_api.cnc_cut_outline(tooth_A, "bulk of gearbar")
  #return
  return(r_ideal_tooth_outline_B)

def gear_profile_outline(ai_low_parameters, ai_angle_position):
  """ create the format B outline of a gear definied by ai_low_parameters
      ai_angle_position sets the gear position.
  """
  r_gear_profile_outline_B = []
  g_type = ai_low_parameters[0]
  if((g_type=='e')or(g_type=='i')):
    r_gear_profile_outline_B = gearwheel_profile_outline(ai_low_parameters, ai_angle_position)
  elif(g_type=='l'):
    r_gear_profile_outline_B = gearbar_profile_outline(ai_low_parameters, ai_angle_position)
  #return
  return(r_gear_profile_outline_B)

def ideal_tooth_outline(ai_low_parameters, ai_angle_position, ai_thickness_coeff):
  """ create the ideal tooth_profile over the first tooth of a gear (i, e or l)
  """
  r_ideal_tooth_outline = []
  g_type = ai_low_parameters[0]
  if((g_type=='e')or(g_type=='i')):
    r_ideal_tooth_outline = ideal_involute_tooth_outline(ai_low_parameters, ai_angle_position, ai_thickness_coeff)
  elif(g_type=='l'):
    r_ideal_tooth_outline = ideal_linear_tooth_outline(ai_low_parameters, ai_angle_position, ai_thickness_coeff)
  #return
  return(r_ideal_tooth_outline)

#############################################################################
# positioning help-function
#############################################################################

def calc_real_force_angle(ai_g1_type, ai_g1_pr, ai_g1_br, ai_g2_type, ai_g2_pr, ai_g2_br, ai_aal, ai_g1_sa, ai_g2_sa):
  """ calculate the real_force_angle depending also on the additional inter-axis length
  """
  if((ai_g1_type=='e')and(ai_g2_type=='e')):# depending on gear_type
    r_real_force_angle = math.acos(float(ai_g1_br+ai_g2_br)/(ai_g1_pr+ai_g2_pr+ai_aal))
  elif((ai_g1_type=='i')and(ai_g2_type=='e')): # i-e
    if(ai_g2_pr>ai_g1_pr):
      print("ERR546: Error, the gearring radius {:0.3f} must be bigger gearwheel radius {:0.3f}".format(ai_g1_pr, ai_g2_pr))
      sys.exit(2)
    r_real_force_angle = math.acos(float(ai_g1_br-ai_g2_br)/(ai_g1_pr-(ai_g2_pr+ai_aal)))
  elif((ai_g1_type=='e')and(ai_g2_type=='i')): # e-i
    if(ai_g1_pr>ai_g2_pr):
      print("ERR547: Error, the gearring radius {:0.3f} must be bigger gearwheel radius {:0.3f}".format(ai_g2_pr, ai_g1_pr))
      sys.exit(2)
    r_real_force_angle = math.acos(float(ai_g2_br-ai_g1_br)/(ai_g2_pr-(ai_g1_pr+ai_aal)))
  elif((ai_g1_type=='l')and(ai_g2_type=='e')): # l-e
    r_real_force_angle = ai_g1_sa
  elif((ai_g1_type=='e')and(ai_g2_type=='l')): # e-l
    r_real_force_angle = ai_g2_sa
  else:
    print("ERR221: Error, the gear type combination {:s}-{:s} does not exist!".format(ai_g1_type, ai_g2_type))
    sys.exit(2)
  return(r_real_force_angle)

#############################################################################
# positioning
#############################################################################

def linear_gear_geometry(ai_g_sa, ai_br, ai_AB):
  """ calculation of the geometry relative to a e-l or l-e gear
  """
  KD = ai_br*math.tan(ai_g_sa)
  AD = ai_br/math.cos(ai_g_sa)
  BD = ai_AB-AD
  DE = BD/math.sin(ai_g_sa)
  KE = KD+DE
  BE = BD/math.tan(ai_g_sa)
  #if(BD<0):
  #  print("ERR853: Error, BD {:0.3f} is negative".format(BD))
  #  print("dbg553: ai_g_sa {:0.3f}  ai_br {:0.3f}  ai_AB {:0.3f}".format(ai_g_sa, ai_br, ai_AB))
  #  sys.exit(2)
  return(KE, BE, BD)

def pre_g2_position_calculation(ai_g1_param, ai_g2_param, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale):
  """ Initial calcultation for getting the g2_position from the high-level parameters of g1 anf g2.
      The goal of this function is to speed-up the function g2_position_calcultion by factoring some of the processing
  """
  # precision
  radian_epsilon = math.pi/1000
  ### place_low_parameters
  # get g1 high-level parameters
  g1_type  = ai_g1_param['gear_type']
  if((g1_type=='e')or(g1_type=='i')): # g1_tl and g1_gc are used to find out the current tooth involved
    g1_tl    = ai_g1_param['pi_module_angle'] # tooth length
    g1_gc    = ai_g1g2_a # gear center
  elif(g1_type=='l'):
    g1_tl    = ai_g1_param['pi_module'] # tooth length
    g1_gc    = 0 # gear center
  g1_n     = ai_g1_param['full_tooth_nb']
  g1_pr    = ai_g1_param['primitive_radius']
  g1_adp   = ai_g1_param['addendum_dedendum_parity']
  g1_brp   = ai_g1_param['positive_base_radius']
  g1_brn   = ai_g1_param['negative_base_radius']
  g1_ox    = ai_g1_param['center_ox']
  g1_oy    = ai_g1_param['center_oy']
  g1_bi    = ai_g1_param['gearbar_inclination']
  g1_sp    = ai_g1_param['positive_slope_angle']
  g1_sn    = ai_g1_param['negative_slope_angle']
  g1_ks    = ai_g1_param['gear_sign']
  g1_pc    = ai_g1_param['position_coefficient']
  g1_pop   = ai_g1_param['positive_primitive_offset']
  g1_pon   = ai_g1_param['negative_primitive_offset']
  g1_lop   = ai_g1_param['positive_location_offset']
  g1_lon   = ai_g1_param['negative_location_offset']
  # get g2 high-level parameters
  g2_type  = ai_g2_param['gear_type']
  g2_tl    = ai_g2_param['pi_module']
  g2_n     = ai_g2_param['full_tooth_nb']
  g2_pr    = ai_g2_param['primitive_radius']
  g2_adp   = ai_g2_param['addendum_dedendum_parity']
  g2_brp   = ai_g2_param['positive_base_radius']
  g2_brn   = ai_g2_param['negative_base_radius']
  g2_ox    = ai_g2_param['center_ox']
  g2_oy    = ai_g2_param['center_oy']
  g2_bi    = ai_g2_param['gearbar_inclination']
  g2_sp    = ai_g2_param['positive_slope_angle']
  g2_sn    = ai_g2_param['negative_slope_angle']
  g2_ks    = ai_g2_param['gear_sign']
  g2_pc    = ai_g2_param['position_coefficient']
  g2_pop   = ai_g2_param['positive_primitive_offset']
  g2_pon   = ai_g2_param['negative_primitive_offset']
  g2_lop   = ai_g2_param['positive_location_offset']
  g2_lon   = ai_g2_param['negative_location_offset']
  ### g1 driving - g2 driven
  ## positive rotation
  # e-e : negative involute - negative involute
  # e-i : negative involute - negative involute
  # e-l : negative involute - negative slope
  # i-e : positive involute - positive involute
  # l-e : negative slope - negative involute
  gear_param_positive = (g1_brp, g1_sp, g1_pop, g1_lop, g2_brp, g2_sp, g2_pop, g2_lop)
  gear_param_negative = (g1_brn, g1_sn, g1_pon, g1_lon, g2_brn, g2_sn, g2_pon, g2_lon)
  if(g1_type=='i'): # i-e
    place_low_param_positive = gear_param_positive
    place_low_param_negative = gear_param_negative
  else: # e-e, e-i, e-l, l-e
    place_low_param_positive = gear_param_negative
    place_low_param_negative = gear_param_positive
  (g1_br_rp, g1_sa_rp, g1_po_rp, g1_lo_rp, g2_br_rp, g2_sa_rp, g2_po_rp, g2_lo_rp) = place_low_param_positive # positive rotation
  (g1_br_rn, g1_sa_rn, g1_po_rn, g1_lo_rn, g2_br_rn, g2_sa_rn, g2_po_rn, g2_lo_rn) = place_low_param_negative # negative rotation
  ### some calculation in advance
  # real_force_angle
  rfa_rp = calc_real_force_angle(g1_type, g1_pr, g1_br_rp, g2_type, g2_pr, g2_br_rp, ai_aal, g1_sa_rp, g2_sa_rp)
  rfa_rn = calc_real_force_angle(g1_type, g1_pr, g1_br_rn, g2_type, g2_pr, g2_br_rn, ai_aal, g1_sa_rn, g2_sa_rn)
  # AB = g1_pr+g2_pr+ai_aal
  AB = abs(g1_ks*g1_pc*g1_pr+g2_ks*g2_pc*g2_pr+ai_aal)
  # alternative for AB
  AB2 = math.sqrt((g2_ox-g1_ox)**2+(g2_oy-g1_oy)**2)
  if(abs(AB2-AB)>radian_epsilon):
    print("ERR414: Error with the calculation of AB {:0.3f} or {:0.3f}".format(AB, AB2))
    sys.exit(2)
  # KL (see documentation  graphic gear_position.svg), used only with e-e, e-i and i-e
  KL_rp = math.sin(rfa_rp)*AB
  KL_rn = math.sin(rfa_rn)*AB
  if((g1_type!='l')and(g2_type!='l')):
    KL_rp2 = math.sqrt(AB**2 - (g1_ks*g1_br_rp+g2_ks*g2_br_rp)**2) # kind of pythagor
    KL_rn2 = math.sqrt(AB**2 - (g1_ks*g1_br_rn+g2_ks*g2_br_rn)**2) # kind of pythagor
    if(abs(KL_rp2-KL_rp)>radian_epsilon):
      print("ERR815: Error, KL_rp {:0.3f} and KL_rp2 {:0.3f} are too different!".format(KL_rp, KL_rp2))
      sys.exit(2)
    if(abs(KL_rn2-KL_rn)>radian_epsilon):
      print("ERR876: Error, KL_rn {:0.3f} and KL_rn2 {:0.3f} are too different!".format(KL_rn, KL_rn2))
      sys.exit(2)
  # KE, BE, BD
  KE1_rp = 0 # default value for g_type = 'e' or 'i'
  BE1_rp = 0
  BD1_rp = 0
  KE1_rn = 0
  BE1_rn = 0
  BD1_rn = 0
  if(g1_type=='l'):
    (KE1_rp, BE1_rp, BD1_rp) = linear_gear_geometry(g1_sa_rp, g2_br_rp, AB)
    (KE1_rn, BE1_rn, BD1_rn) = linear_gear_geometry(g1_sa_rn, g2_br_rn, AB)
  KE2_rp = 0 # default value for g_type = 'e' or 'i'
  BE2_rp = 0
  BD2_rp = 0
  KE2_rn = 0
  BE2_rn = 0
  BD2_rn = 0
  if(g2_type=='l'):
    (KE2_rp, BE2_rp, BD2_rp) = linear_gear_geometry(g2_sa_rp, g1_br_rp, AB)
    (KE2_rn, BE2_rn, BD2_rn) = linear_gear_geometry(g2_sa_rn, g1_br_rn, AB)
  ### pack the place_low_param
  place_low_param_common = (g1_type, g1_pr, g1_ox, g1_oy, g1_bi, g1_ks, g1_pc,
                            g2_type, g2_pr, g2_ox, g2_oy, g2_bi, g2_ks, g2_pc,
                            ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale,
                            g1_tl, g1_gc, AB)
  place_low_param_positive2 = (g1_br_rp, g1_sa_rp, g1_po_rp, g1_lo_rp, g2_br_rp, g2_sa_rp, g2_po_rp, g2_lo_rp, rfa_rp, KL_rp, KE1_rp, BE1_rp, KE2_rp, BE2_rp)
  place_low_param_negative2 = (g1_br_rn, g1_sa_rn, g1_po_rn, g1_lo_rn, g2_br_rn, g2_sa_rn, g2_po_rn, g2_lo_rn, rfa_rn, KL_rn, KE1_rn, BE1_rn, KE2_rn, BE2_rn)
  place_low_param = (place_low_param_common, place_low_param_positive2, place_low_param_negative2)
  #print("dbg964: g1_sa_rp {:0.3f}  g1_sa_rn {:0.3f}".format(g1_sa_rp, g1_sa_rn))
  ### info_txt
  ## check if the primitive circle are matching (in order than addendum_dedendum_parity makes sense)
  info_txt = ""
  if((g1_type!='l')and(g2_type!='l')): # e-e, e-i or i-e
    if(abs(g2_pr*g1_n-g1_pr*g2_n)>radian_epsilon):
      info_txt += "WARN701: Warning, the primitive diameter ratio is different from N2/N1: g1_pr {:0.3f}  g2_pr {:0.3f}  g1_n {:d}  g2_n {:d}\n".format(g1_pr, g2_pr, g1_n, g2_n)
    if(abs(g2_brp*g1_n-g1_brp*g2_n)>radian_epsilon):
      info_txt += "WARN702: Warning, the positive base diameter ratio is different from N2/N1: g1_brp {:0.3f}  g2_brp {:0.3f}  g1_n {:d}  g2_n {:d}\n".format(g1_brp, g2_brp, g1_n, g2_n)
    if(abs(g2_brn*g1_n-g1_brn*g2_n)>radian_epsilon):
      info_txt += "WARN703: Warning, the negative base diameter ratio is different from N2/N1: g1_brn {:0.3f}  g2_brn {:0.3f}  g1_n {:d}  g2_n {:d}\n".format(g1_brn, g2_brn, g1_n, g2_n)
  elif((g1_type=='l')or(g2_type=='l')): # e-l or l-e
    if(g1_type=='l'):
      g_tl = g1_tl
      g_sp = g1_sp
      g_sn = g1_sn
      g_n = g2_n
      g_pr = g2_pr
      g_brp = g2_brp
      g_brn = g2_brn
    elif(g2_type=='l'):
      g_tl = g2_tl
      g_sp = g2_sp
      g_sn = g2_sn
      g_n = g1_n
      g_pr = g1_pr
      g_brp = g1_brp
      g_brn = g1_brn
    if(abs(g_tl-2*math.pi*g_pr/g_n)>radian_epsilon):
      info_txt += "WARN711: Warning, the tooth pitch of gearwheel and the gearbar are different! g_tl {:0.3f}  g_pr {:0.3f}  g_n {:d}\n".format(g_tl, g_pr, g_n)
    if(abs(g_pr*math.cos(g_sp)-g_brp)>radian_epsilon):
      info_txt += "WARN712: Warning, the positive base diameter and the gearbar slope angle are not coherent! g_pr {:0.3f}  g_sp {:0.3f}  g_brp {:0.3f}\n".format(g_pr, g_sp, g_brp)
    if(abs(g_pr*math.cos(g_sn)-g_brn)>radian_epsilon):
      info_txt += "WARN713: Warning, the negative base diameter and the gearbar slope angle are not coherent! g_pr {:0.3f}  g_sn {:0.3f}  g_brn {:0.3f}\n".format(g_pr, g_sn, g_brn)
  if(ai_aal!=0):
    info_txt += "WARN704: Warning, the additional inter-axis length {:0.3f} is not null. The addendum_dedendum_parity can not be checked\n".format(ai_aal)
  elif(abs(g1_adp+g2_adp-1)>radian_epsilon):
    info_txt += "WARN05: Warning, the addendum_dedendum_parity are not complementary. g1_adp {:0.3f}  g2_adp {:0.3f}\n".format(g1_adp, g2_adp)
  #print("{:s}".format(info_txt))
  # return
  r_ppc = (place_low_param, info_txt)
  return(r_ppc)

#def g2_position_calculation(ai_g1_param, ai_g2_param, ai_rotation_direction, ai_g1_position, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale):
def g2_position_calculation(ai_place_low_param, ai_rotation_direction, ai_g1_position):
  """ calculation of the angle position of the second gear and other related parameters (speed, friction)
  """
  # precision
  #radian_epsilon = math.pi/1000
  radian_epsilon_1000 = gpo_radian_epsilon_1000
  radian_epsilon_100000 = gpo_radian_epsilon_100000
  radian_epsilon_100 = gpo_radian_epsilon_100
  radian_epsilon_10 = gpo_radian_epsilon_10
  # rotation_direction alias
  rd = ai_rotation_direction
  # unpack place_low_param
  #(place_low_param, tmp_info) = pre_g2_position_calculation(ai_g1_param, ai_g2_param, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale)
  (place_low_param_common, place_low_param_positive2, place_low_param_negative2) = ai_place_low_param
  if(rd==1):
    place_low_param_oriented = place_low_param_positive2
  elif(rd==-1):
    place_low_param_oriented = place_low_param_negative2
  #() = place_low_param_common
  (g1_type, g1_pr, g1_ox, g1_oy, g1_bi, g1_ks, g1_pc,
    g2_type, g2_pr, g2_ox, g2_oy, g2_bi, g2_ks, g2_pc,
    aal, g1g2_a, g1_rotation_speed, speed_scale,
    g1_tl, g1_gc, AB) = place_low_param_common
  #() = place_low_param_oriented
  (g1_br, g1_sa, g1_po, g1_lo, g2_br, g2_sa, g2_po, g2_lo, rfa, KL, KE1, BE1, KE2, BE2) = place_low_param_oriented
  ## gear system related
  ## real_force_angle
  #rfa = calc_real_force_angle(g1_type, g1_pr, g1_br, g2_type, g2_pr, g2_br, aal, g1_sa, g2_sa)
  ## AB = g1_pr+g2_pr+aal
  #AB = abs(g1_ks*g1_pc*g1_pr+g2_ks*g2_pc*g2_pr+aal)
  ## g1 related
  if((g1_type=='e')or(g1_type=='i')):
    # get the angle of the closest middle of addendum to the contact point
    aa = ai_g1_position + g1_po - g1g2_a
    while(abs(aa)>g1_tl/2+radian_epsilon_1000):
      if(aa>0):
        aa = aa - g1_tl
      else:
        aa = aa + g1_tl
    contact_g1_tooth_angle = aa - g1_po + g1g2_a
    contact_g1_tooth_relative_angle = aa - g1_po # relative to the inter-axis
    # g1_contact_u : involute parameter for g1 of the contact point
    g1_contact_u = rfa + rd * g1_ks * (contact_g1_tooth_relative_angle + g1_lo)
    #print("dbg558: g1_lo {:0.3f}  contact_g1_tooth_relative_angle {:0.3f}  rfa {:0.3f}".format(g1_lo, contact_g1_tooth_relative_angle, rfa))
    # contact point coordinates (method 1)
    (cx, cy, ti) = sample_of_gear_tooth_profile((g1_ox, g1_oy), g1_br, contact_g1_tooth_angle+g1_lo, -1*g1_ks*rd, 0, g1_contact_u)
    #print("dbg858: contact point (method1): cx: {:0.2f}  cy: {:0.2f}  ti: {:0.2f}".format(cx, cy, ti))
    #print("dbg325: contact_g1_tooth_angle {:0.3f}  g1_lo {:0.3f}  g1_contact_u {:0.3f}  ti {:0.3f}".format(contact_g1_tooth_angle, g1_lo, g1_contact_u, ti))
  elif(g1_type=='l'): # linear-gear (aka gearbar)
    # some geometry
    #(KE1, BE1, BD1) = linear_gear_geometry(g1_sa, g2_br, AB)
    # contact_g1_tooth_position
    aa = ai_g1_position + g1_po
    while(abs(aa)>g1_tl/2+radian_epsilon_1000):
      if(aa>0):
        aa = aa - g1_tl
      else:
        aa = aa + g1_tl
    contact_g1_tooth_position = aa - g1_po
    g1_contact_u = (contact_g1_tooth_position+g1_lo-rd*BE1)*math.cos(g1_sa)
    g1_position2 = rd*BE1 + g1_contact_u/math.cos(g1_sa) - g1_lo
    ec = (g1_position2+g1_lo-rd*BE1)*math.cos(g1_sa)
    cx = g1_ox + rd*BE1*math.cos(g1_bi-math.pi/2) + ec*math.cos(g1_bi-math.pi/2-rd*g1_sa)
    cy = g1_oy + rd*BE1*math.sin(g1_bi-math.pi/2) + ec*math.sin(g1_bi-math.pi/2-rd*g1_sa)
    #print("dbg989: g2_position {:0.3f}   ec {:0.3f}".format(g2_position, ec))
    #print("dbg753: rd {:d}  g1_bi {:0.3f}  BE1 {:0.3f}  ec {:0.3f}".format(rd, g1_bi, BE1, ec))
    # ti
    ti = g1_bi-rd*g1_sa
  ## triangle ABC
  # length of AC
  AC = math.sqrt((cx-g1_ox)**2+(cy-g1_oy)**2)
  # length of BC
  BC = math.sqrt((cx-g2_ox)**2+(cy-g2_oy)**2)
  # angle CBA
  max_ABC = max(AB,AC, BC)
  min_ABC = min(AB,AC, BC)
  med_ABC = AB+AC+BC-max_ABC-min_ABC
  #if(AC+BC==AB):
  #if(abs(AC+BC-AB)<radian_epsilon_1000):
  #if(min_ABC+med_ABC==max_ABC):
  #if((max_ABC>=min_ABC+med_ABC-radian_epsilon_1000)and(max_ABC<min_ABC+med_ABC+radian_epsilon_1000)):
  if(abs(min_ABC+med_ABC-max_ABC)<radian_epsilon_100000):
    #print("WARN468: Warning, the triangle ABC is flat") # it happens from time to time, don't worry :O
    BAC = 0
    ABC = 0
  elif(min_ABC+med_ABC<max_ABC):
    print("ERR478: Error of length in the triangle ABC")
    print("dbg637: AB {:0.3f}  AC {:0.3f}  BC {:0.3f}".format(AB, AC, BC))
    sys.exit(20)
  else:
    # law of cosine (Al-Kashi) in ABC
    BAC = math.acos(float(AB**2+AC**2-BC**2)/(2*AB*AC))
    ABC = math.acos(float(AB**2+BC**2-AC**2)/(2*AB*BC))
    #print("dbg569: BAC {:0.3f}   ABC {:0.3f}".format(BAC, ABC))
    BAC = math.fmod(BAC+5*math.pi/2, math.pi)-math.pi/2
    ABC = math.fmod(ABC+5*math.pi/2, math.pi)-math.pi/2
    # alternative
    xAB = math.atan2(g2_oy-g1_oy, g2_ox-g1_ox)
    xAC = math.atan2(cy-g1_oy, cx-g1_ox)
    BAC2 = math.fmod(xAC-xAB+9*math.pi/2, math.pi)-math.pi/2
    xBA = math.atan2(g1_oy-g2_oy, g1_ox-g2_ox)
    xBC = math.atan2(cy-g2_oy, cx-g2_ox)
    ABC2 = math.fmod(xBC-xBA+9*math.pi/2, math.pi)-math.pi/2
    #print("dbg557: xBA {:0.3f}  xBC {:0.3f}".format(xBA, xBC))
    # sign BAC, ABC
    BAC = math.copysign(BAC, BAC2)
    ABC = math.copysign(ABC, ABC2)
    # check BAC and BAC2
    if(abs(BAC2-BAC)>radian_epsilon_1000):
      print("ERR689: Error in the calculation of BAC {:0.3f} or BAC2 {:0.3f} !".format(BAC, BAC2))
      sys.exit(2)
    # check ABC and ABC2
    if(abs(ABC2-ABC)>radian_epsilon_1000):
      print("ERR688: Error in the calculation of ABC {:0.3f} or ABC2 {:0.3f} !".format(ABC, ABC2))
      sys.exit(2)
  #print("dbg334: BAC: {:0.3f}".format(BAC))
  #print("dbg335: ABC: {:0.3f}".format(ABC))
  ## speed / radial angle
  g1_sra = rd*g1_ks*rfa+BAC
  # alternative
  if((g1_type=='e')or(g1_type=='i')):
    g1_sra2 = rd*g1_ks*math.atan(g1_contact_u)
    if(abs(g1_sra2-g1_sra)>radian_epsilon_100):
      print("ERR417: Error in calculation of g1_sra {:0.3f} or g1_sra2 {:0.3f}".format(g1_sra, g1_sra2))
      sys.exit(2)
  ## speed of c1 (contact point of g1)
  # c1 speed
  if((g1_type=='e')or(g1_type=='i')):
    c1_speed = AC*g1_rotation_speed
    c1_speed_radial = c1_speed*math.cos(g1_sra)
    c1_speed_tangential = c1_speed*math.sin(g1_sra)
  elif(g1_type=='l'): # linear-gear (aka gearbar)
    c1_speed = g1_rotation_speed * g1_tl * 5 # * g1_tl * 5 to scale it to make it visible
    c1_speed_radial = c1_speed*math.cos(g1_sa)
    c1_speed_tangential = rd*c1_speed*math.sin(g1_sa)
  ### g2_position, g2_contact_u, c2x, c2y, c2_speed_radial, c2_speed, c2_speed_tangential, g2_rotation_speed
  if((g2_type=='e')or(g2_type=='i')):
    ## g2_contact_u : involute parameter for g2 of the contact point
    # several mathods:
    g2_sra = rd*g1_ks*rfa+ABC
    # length KL (see documentation  graphic gear_position.svg)
    #KL = math.sin(rfa)*AB
    g2_contact_u2 = math.tan(abs(g2_sra))
    g2_contact_u3 = math.sqrt((float(BC)/g2_br)**2-1)
    if((g1_type=='e')or(g1_type=='i')):
      g2_contact_u1 = g1_ks*float(KL - g2_ks*g1_contact_u*g1_br)/g2_br
      if(abs(g2_contact_u2-g2_contact_u1)>radian_epsilon_10):
        print("ERR331: Error in the calculation of g2_contact_u1 {:0.3f} or g2_contact_u2 {:0.3f}".format(g2_contact_u1, g2_contact_u2))
        sys.exit(2)
      if(abs(g2_contact_u3-g2_contact_u1)>radian_epsilon_10):
        print("ERR332: Error in the calculation of g2_contact_u1 {:0.3f} or g2_contact_u3 {:0.3f}".format(g2_contact_u1, g2_contact_u3))
        sys.exit(2)
    g2_contact_u = g2_contact_u3 # select the method for g2_contact_u
    ## c2_position
    g2_position = g1g2_a + (1+g1_ks*g2_ks)/2*math.pi - rd*g1_ks*(rfa - g2_contact_u) - g2_lo
    # c2 coordinates
    (c2x, c2y, t2i) = sample_of_gear_tooth_profile((g2_ox, g2_oy), g2_br, g2_position+g2_lo, -1*rd*g1_ks, 0, g2_contact_u)
    #print("dbg326: g2_position {:0.3f}  g2_lo {:0.3f}  g2_contact_u {:0.3f}  t2i {:0.3f}".format(g2_position, g2_lo, g2_contact_u, t2i))
    if(abs(math.fmod(ti-t2i+4.5*math.pi, math.pi) - 0.5*math.pi)>radian_epsilon_1000):
      print("ERR874: Error, the tangents ti {:0.3f} and t2i {:0.3f} are not equal (modulo pi)".format(ti, t2i))
      sys.exit(2)
    #print("dbg632: g2_ox {:0.3f}  g2_oy {:0.3f}  g2_br {:0.3f}".format(g2_ox, g2_oy, g2_br))
    ## speed of c2 (contact point of g2)
    c2_speed_radial = c1_speed_radial
    c2_speed = float(c2_speed_radial)/math.cos(g2_sra)
    c2_speed_tangential = c2_speed*math.sin(g2_sra)
    # alternative
    c2_speed_tangential2 = rd*g1_ks*c2_speed_radial*g2_contact_u
    if(abs(c2_speed_tangential2-c2_speed_tangential)>radian_epsilon_10):
      print("ERR336: Error in the calculation of c2_speed_tangential {:0.3f} or c2_speed_tangential2 {:0.3f}".format(c2_speed_tangential, c2_speed_tangential2))
      print("dbg967: radian_epsilon_1000 {:0.6f}  radian_epsilon_100000 {:0.6f}".format(radian_epsilon_1000, radian_epsilon_100000))
      sys.exit(2)
    g2_rotation_speed = float(c2_speed)/BC
  elif(g2_type=='l'): # linear-gear (aka gearbar)
    #(KE2, BE2, BD2) = linear_gear_geometry(g2_sa, g1_br, AB)
    g2_contact_u = rd*(g1_contact_u*g1_br-KE2)
    g2_position = rd*BE2 + g2_contact_u/math.cos(g2_sa) - g2_lo
    dc = (g2_position+g2_lo-rd*BE2)*math.cos(g2_sa)
    c2x = g2_ox + rd*BE2*math.cos(g2_bi-math.pi/2) + dc*math.cos(g2_bi-math.pi/2-rd*g2_sa)
    c2y = g2_oy + rd*BE2*math.sin(g2_bi-math.pi/2) + dc*math.sin(g2_bi-math.pi/2-rd*g2_sa)
    #print("dbg989: g2_position {:0.3f}   dc {:0.3f}".format(g2_position, dc))
    if(abs(math.fmod(ti - (g2_bi-1*rd*g2_sa)+4.5*math.pi, math.pi)-0.5*math.pi)>radian_epsilon_1000):
      print("ERR875: Error, the tangents ti {:0.3f} and slope g2_sa {:0.3f} are not equal (modulo pi)".format(ti, g2_sa))
      sys.exit(2)
    c2_speed_radial = c1_speed_radial
    c2_speed = float(c2_speed_radial)/math.cos(g2_sa)
    c2_speed_tangential = rd*c2_speed*math.sin(g2_sa)
    g2_rotation_speed = c2_speed
  # friction between g1 and g2
  tangential_friction = c2_speed_tangential - c1_speed_tangential
  ## speed outline
  # scale the outline
  scaled_c1_speed_radial = c1_speed_radial*speed_scale # *g1_module *g1_pr ???
  scaled_c1_speed_tangential = c1_speed_tangential*speed_scale
  scaled_c2_speed_radial = c2_speed_radial*speed_scale # *g2_module *g2_pr ???
  scaled_c2_speed_tangential = c2_speed_tangential*speed_scale
  # normal-tangential reference frame
  nxa = ti+rd*math.pi/2
  txa = nxa+math.pi/2
  #
  c1rx = cx+scaled_c1_speed_radial*math.cos(nxa)
  c1ry = cy+scaled_c1_speed_radial*math.sin(nxa)
  c1_speed_outline = ((cx, cy), # contact point
    (c1rx, c1ry), # c1 radial speed
    (c1rx+scaled_c1_speed_tangential*math.cos(txa), c1ry+scaled_c1_speed_tangential*math.sin(txa)), # c1 tangential speed
    (cx, cy)) # close
  c2rx = c2x+scaled_c2_speed_radial*math.cos(nxa)
  c2ry = c2y+scaled_c2_speed_radial*math.sin(nxa)
  c2_speed_outline = ((c2x, c2y),
    (c2rx, c2ry), # c2 radial speed
    (c2rx+scaled_c2_speed_tangential*math.cos(txa), c2ry+scaled_c2_speed_tangential*math.sin(txa)), # c2 tangential speed
    (c2x, c2y)) # close
  # return
  r_position = (g2_position, g2_rotation_speed, tangential_friction, c1_speed_outline, c2_speed_outline)
  return(r_position)

#############################################################################
# analytic calculation of the real_force_angle
#############################################################################

def info_on_real_force_angle(ai_g1_param, ai_g2_param, ai_sys_param, ai_rotation_direction):
  """ Analytic calculation to check the real_force_angle (including the additional_inter_axis_length) and the force_path_length
  """
  ### positive_rotation
  # external / external : negative_involute / negative_involute
  # external / internal : negative_involute / negative_involute
  # internal / external : positive_involute / positive_involute # exception !
  # external / linear   : negative_involute / negative_involute
  # linear   / external : negative_involute / negative_involute
  if(ai_rotation_direction==1):
    rotation_name = 'Positive'
  elif(ai_rotation_direction==-1):
    rotation_name = 'Negative'
  else:
    print("ERR663: Error, ai_rotation_direction {:d} can only be 1 or -1!".format(ai_rotation_direction))
    sys.exit(2)
  # get the interesting high-level parameters
  rd = ai_rotation_direction
  g1_type = ai_g1_param['gear_type']
  g1_sign = ai_g1_param['gear_sign']
  g1_n    = ai_g1_param['full_tooth_nb']
  g1_pr   = ai_g1_param['primitive_radius']
  g1_ar   = ai_g1_param['addendum_radius']
  g1_ah   = ai_g1_param['addendum_height']
  g1_bl   = ai_g1_param['gearbar_length']
  g1_ox   = ai_g1_param['center_ox']
  g1_oy   = ai_g1_param['center_oy']
  g2_type = ai_g2_param['gear_type']
  g2_sign = ai_g2_param['gear_sign']
  g2_n    = ai_g2_param['full_tooth_nb']
  g2_pr   = ai_g2_param['primitive_radius']
  g2_ar   = ai_g2_param['addendum_radius']
  g2_ah   = ai_g2_param['addendum_height']
  g2_bl   = ai_g2_param['gearbar_length']
  g2_ox   = ai_g2_param['center_ox']
  g2_oy   = ai_g2_param['center_oy']
  g1g2_a  = ai_sys_param['g1g2_angle']
  aal     = ai_sys_param['additional_inter_axis_length']
  if(rd*g1_sign==1):
    involute_name = 'Negative'
    g1_br = ai_g1_param['negative_base_radius']
    g2_br = ai_g2_param['negative_base_radius']
    g1_sa = ai_g1_param['negative_slope_angle']
    g2_sa = ai_g2_param['negative_slope_angle']
  else:
    involute_name = 'Positive'
    g1_br = ai_g1_param['positive_base_radius']
    g2_br = ai_g2_param['positive_base_radius']
    g1_sa = ai_g1_param['positive_slope_angle']
    g2_sa = ai_g2_param['positive_slope_angle']
  # start creating the info text
  r_info = ""
  #r_info += "Info on Real Force Angle {:s}:\n".format(rotation_name)
  #print("dbg311: ai_g1_br:", ai_g1_br)
  # depending on gear_type
  #real_force_angle = math.acos(float(ai_g1_br*(ai_g1_n+ai_g2_n))/((ai_g1_pr+ai_g2_pr+aal)*ai_g1_n))
  real_force_angle = calc_real_force_angle(g1_type, g1_pr, g1_br, g2_type, g2_pr, g2_br, aal, g1_sa, g2_sa)
  #r_info += "{:s} Real Force Angle = {:0.2f} radian ({:0.2f} degree)\n".format(rotation_name, real_force_angle, real_force_angle*180/math.pi)
  # coordinate of C (intersection of axis-line and force-line)
  #AC = float((ai_g1_pr+ai_g2_pr+aal)*ai_g1_n)/(ai_g1_n+ai_g2_n)
  if((g1_type=='e')or(g1_type=='i')):
    AC = g1_br/math.cos(real_force_angle)
  elif(g1_type=='l'):
    AC = aal
  CX = g1_ox + math.cos(g1g2_a)*AC
  CY = g1_oy + math.sin(g1g2_a)*AC
  # force line equation
  real_force_inclination = g1g2_a + rd*(math.pi/2 - g1_sign*real_force_angle) # angle (Ox, force)
  Flx = math.sin(real_force_inclination)
  Fly = -1*math.cos(real_force_inclination)
  Fk = -1*(Flx*CX+Fly*CY)
  # F2: intersection of the force line and the addendum_circle_1
  if((g1_type=='e')or(g1_type=='i')):
    S2X = CX + g1_pr/g1_n*math.cos(g1g2_a+rd*math.pi/2) # S2: define the side of the intersection line-circle
    S2Y = CY + g1_pr/g1_n*math.sin(g1g2_a+rd*math.pi/2)
    (F2X,F2Y, line_circle_intersection_status) = small_geometry.line_circle_intersection((Flx, Fly, Fk), (g1_ox, g1_oy), g1_ar, (S2X,S2Y), real_force_inclination, "F2 calcultation")
    if(line_circle_intersection_status==2):
      print("ERR125: Error with the intersection of the force line and the addendum_circle_1")
      sys.exit(2)
  elif(g1_type=='l'):
    LX = g1_ox+g1_ah*math.cos(g1g2_a)
    LY = g1_oy+g1_ah*math.sin(g1g2_a)
    Blx = math.sin(g1g2_a+math.pi/2)
    Bly = -1*math.cos(g1g2_a+math.pi/2)
    Bk = -1*(Blx*LX+Bly*LY)
    (F2X, F2Y, line_line_intersection_status) = small_geometry.line_line_intersection((Flx, Fly, Fk), (Blx, Bly, Bk), "F2 calcultation with gearbar")
    if(line_line_intersection_status==2):
      print("ERR127: Error with the intersection of the force line and the gearbar addendum line")
      sys.exit(2)
  # F1: intersection of the force line and the addendum_circle_2
  if((g2_type=='e')or(g2_type=='i')):
    S1X = CX + g2_pr/g2_n*math.cos(g1g2_a-rd*math.pi/2) # S1: define the side of the intersection line-circle
    S1Y = CY + g2_pr/g2_n*math.sin(g1g2_a-rd*math.pi/2)
    (F1X,F1Y, line_circle_intersection_status) = small_geometry.line_circle_intersection((Flx, Fly, Fk), (g2_ox, g2_oy), g2_ar, (S1X,S1Y), real_force_inclination+math.pi, "F1 calcultation")
    if(line_circle_intersection_status==2):
      print("ERR126: Error with the intersection of the force line and the addendum_circle_2")
      sys.exit(2)
  elif(g2_type=='l'):
    LX = g2_ox+g1_ah*math.cos(g1g2_a+math.pi)
    LY = g2_oy+g1_ah*math.sin(g1g2_a+math.pi)
    Blx = math.sin(g1g2_a+math.pi/2)
    Bly = -1*math.cos(g1g2_a+math.pi/2)
    Bk = -1*(Blx*LX+Bly*LY)
    (F1X, F1Y, line_line_intersection_status) = small_geometry.line_line_intersection((Flx, Fly, Fk), (Blx, Bly, Bk), "F1 calcultation with gearbar")
    if(line_line_intersection_status==2):
      print("ERR129: Error with the intersection of the force line and the gearbar addendum line")
      sys.exit(2)
  ### action_line_outline
  r_action_line_outline = ((F1X, F1Y), (F2X, F2Y))
  # length of F1F2
  F1F2 = math.sqrt((F2X-F1X)**2+(F2Y-F1Y)**2)
  #r_info += "length of the tooth {:s} contact path: {:0.2f}\n".format(involute_name, F1F2)
  r_info += "{:s} rotation, {:s}-{:s} involute {:s}. Real Force Angle = {:0.2f} radian ({:0.2f} degree). Contact path length: {:0.2f}\n".format(rotation_name, g1_type, g2_type, involute_name, real_force_angle, real_force_angle*180/math.pi, F1F2)
  # angle (F1AF2)
  if((g1_type=='e')or(g1_type=='i')):
    AF1 = float(math.sqrt((F1X-g1_ox)**2+(F1Y-g1_oy)**2))
    xAF1 = math.atan2((F1Y-g1_oy)/AF1, (F1X-g1_ox)/AF1)
    AF2 = float(g1_ar)
    xAF2 = math.atan2((F2Y-g1_oy)/AF2, (F2X-g1_ox)/AF2)
    F1AF2 = abs(math.fmod(xAF2-xAF1+5*math.pi, 2*math.pi)-math.pi)
    F1AF2p = F1AF2*g1_n/(2*math.pi)
    r_info += "tooth {:s} contact path angle from gearwheel1: {:0.2f} radian ({:0.2f} degree) {:0.2f}% of tooth length\n".format(involute_name, F1AF2, F1AF2*180/math.pi, F1AF2p*100)
  elif(g1_type=='l'):
    F1F2t = F1F2*math.cos(g1_sa)
    F1F2p = float(F1F2t)*g1_n/g1_bl
    r_info += "tooth {:s} contact path from gearbar1 tangential length {:0.2f} (mm) {:0.2f}% of tooth length\n".format(involute_name, F1F2t, F1F2p*100)
  # angle (F1EF2)
  if((g2_type=='e')or(g2_type=='i')):
    EF2 = float(math.sqrt((F2X-g2_ox)**2+(F2Y-g2_oy)**2))
    xEF2 = math.atan2((F2Y-g2_oy)/EF2, (F2X-g2_ox)/EF2)
    EF1 = float(g2_ar)
    xEF1 = math.atan2((F1Y-g2_oy)/EF1, (F1X-g2_ox)/EF1)
    F1EF2 = abs(math.fmod(xEF2-xEF1+5*math.pi, 2*math.pi)-math.pi)
    F1EF2p = F1EF2*g2_n/(2*math.pi)
    r_info += "tooth {:s} contact path angle from gearwheel2: {:0.2f} radian ({:0.2f} degree) {:0.2f}% of tooth length\n".format(involute_name, F1EF2, F1EF2*180/math.pi, F1EF2p*100)
  elif(g2_type=='l'):
    F1F2t = F1F2*math.cos(g2_sa)
    F1F2p = float(F1F2t)*g2_n/g2_bl
    r_info += "tooth {:s} contact path from gearbar2 tangential length {:0.2f} (mm) {:0.2f}% of tooth length\n".format(involute_name, F1F2t, F1F2p*100)
  # return
  r_iorfa = (r_info, r_action_line_outline)
  return(r_iorfa)

