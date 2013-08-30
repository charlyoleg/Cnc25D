# cnc_cut_outline.py
# a function that converts a polygon into a curve trimable with 2.5D cnc
# created by charlyoleg on 2013/05/13
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
cnc_cut_outline.py provides API functions to design 2.5D parts and create cuboid assembly
"""

################################################################
# python behavior
################################################################

from __future__ import division # to get float division

################################################################
# header for Python / FreeCAD compatibility
################################################################

# cnc_cut_outline must not rely on FreeCAD any more. outline_backends.py makes the junction with FreeCAD
# freecad is only used to test the cnc_cut_outline api
#import importing_freecad # for testing only
#importing_freecad.importing_freecad() # for testing only

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

#import Part # for testing only
#from FreeCAD import Base # for testing only
#
#import outline_backends # for testing only
#
import math
import sys, argparse
#
import design_help # just for get_effective_args()
from small_geometry import *

################################################################
# ******** Sub-functions for the API ***********
################################################################

def check_outline_format(ai_outline):
  """ check the input format and return the outline_type with the code:
      0: format-B circle,  1: format-B general outline (all outline except circle), 2: format-A
  """
  r_outline_type = -1
  # check if it is a format-B circle
  if(not isinstance(ai_outline, (tuple, list))):
    print("ERR937: Error, ai_outline must be a list or a tuple")
    sys.exit(2)
  # check if the outline is a circle or a general outline
  if(isinstance(ai_outline[0], (tuple, list))): # general outline
    # checks on ai_outline for general outline
    if(len(ai_outline)<2):
      print("ERR402: Error, the segment list must contain at least 2 elements. Currently, len(ai_outline) = {:d}".format(len(ai_outline)))
      sys.exit(2)
    # check the first point
    len_first_point = len(ai_outline[0])
    if(len_first_point==2):
      r_outline_type = 1
    elif(len_first_point==3):
      r_outline_type = 2
    else:
      print("ERR457: Error, the first point has an unexpected number of items {:d}".format(len_first_point))
      sys.exit(2)
  else: # circle outline
    if(len(ai_outline)!=3):
      print("ERR758: Error, circle outline must be a list of 3 floats (or int)! Current len: {:d}".format(len(ai_outline)))
      sys.exit(2)
    r_outline_type = 0
  return(r_outline_type)

def reverse_outline(ai_outline):
  """ reverse an outline
      ai_outline can be list of segments with the input format of cnc_cut_outline.cnc_cut_outline() or with the input format of outline_backends.outline_arc_line()
      the output format is the input format
  """
  # check the ai_outline format
  outline_type = check_outline_format(ai_outline)
  #print("dbg553: outline_type:", outline_type)
  # check if the outline is closed
  outline_closed = False
  if((ai_outline[0][0]==ai_outline[-1][-outline_type-1])and(ai_outline[0][1]==ai_outline[-1][-outline_type])):
    outline_closed = True
  # outline data extraction
  l_end_point = []
  l_mid_point = []
  l_router_bit_request = []
  for p in ai_outline:
    len_p = len(p)
    # check segment
    is_arc = False
    if(outline_type==1):
      if(len_p==2):
        is_arc = False
      elif(len_p==4):
        is_arc = True
      else:
        print("ERR257: Error, the segment has an unxepected number of items {:d}".format(len_p))
        sys.exit(2)
    elif(outline_type==2):
      if(len_p==3):
        is_arc = False
      elif(len_p==5):
        is_arc = True
      else:
        print("ERR258: Error, the segment has an unxepected number of items {:d}".format(len_p))
        sys.exit(2)
    #else:
    #  print("ERR557: Error, the outline_type is unexpected {:d}".format(outline_type))
    #  sys.exit(2)
    # extract segments
    middle_point = None
    end_point = ()
    end_point_router_bit = None
    if(is_arc):
      middle_point = (p[0], p[1])
      end_point = (p[2], p[3])
    else:
      end_point = (p[0], p[1])
    if(outline_type==2):
      if(is_arc):
        end_point_router_bit = p[4]
      else:
        end_point_router_bit = p[2]
      l_router_bit_request.append(end_point_router_bit)
    l_mid_point.append(middle_point)
    l_end_point.append(end_point)
  # outline construction
  r_outline = []
  # start point
  if(outline_type==2):
    r_outline.append((l_end_point[-1][0], l_end_point[-1][1], l_router_bit_request[-1]))
  else:
    r_outline.append((l_end_point[-1][0], l_end_point[-1][1]))
  # segments
  point_nb = len(l_end_point)
  for i in range(point_nb-1):
    if(outline_type==2):
      if(l_mid_point[point_nb-1-i]==None):
        r_outline.append((l_end_point[point_nb-2-i][0], l_end_point[point_nb-2-i][1], l_router_bit_request[point_nb-2-i]))
      else:
        r_outline.append((l_mid_point[point_nb-1-i][0], l_mid_point[point_nb-1-i][1], l_end_point[point_nb-2-i][0], l_end_point[point_nb-2-i][1], l_router_bit_request[point_nb-2-i]))
    else:
      if(l_mid_point[point_nb-1-i]==None):
        r_outline.append((l_end_point[point_nb-2-i][0], l_end_point[point_nb-2-i][1]))
      else:
        r_outline.append((l_mid_point[point_nb-1-i][0], l_mid_point[point_nb-1-i][1], l_end_point[point_nb-2-i][0], l_end_point[point_nb-2-i][1]))
  # move the router_bit request if the outline is closed
  if(outline_closed):
    if(outline_type==2):
      if(r_outline[0][2]!=0):
        print("WARN567: Warning, the last router_bit request of the closed outline is not set to zero: {:0.2f}".format(r_outline[0][2]))
      r_outline[0]=(r_outline[0][0], r_outline[0][1], r_outline[-1][-1])
      last_segment =  list(r_outline[-1])
      last_segment[-1] = 0
      r_outline[-1] = tuple(last_segment)
  return(r_outline)

def smooth_corner_line_line(ai_pre_point, ai_current_point, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Generate the corner outline for a smoothed line-line corner
  """
  r_outline = []
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # to understand the notation, chech the documentation
  (AX,AY)=ai_current_point
  (GX,GY)=ai_pre_point
  (HX,HY)=ai_post_point
  # segment length
  AG=math.sqrt((GX-AX)**2+(GY-AY)**2)
  AH=math.sqrt((HX-AX)**2+(HY-AY)**2)
  GH=math.sqrt((HX-GX)**2+(HY-GY)**2)
  # corner angle
  #if(AG==0):
  if(AG<radian_epsilon):
    print("ERR406: the length AG is null at point {:s} ({:0.2f}, {:0.2f}, {:0.2f})".format(ai_error_msg_id, AX, AY, ai_router_bit_request))
    sys.exit(1)
  #if(AH==0):
  if(AH<radian_epsilon):
    print("ERR407: the length AH is null at point {:s} ({:0.2f}, {:0.2f}, {:0.2f})".format(ai_error_msg_id, AX, AY, ai_router_bit_request))
    sys.exit(1)
  #if(GH==0):
  if(GH<radian_epsilon):
    print("ERR408: the length GH is null at point {:s} ({:0.2f}, {:0.2f}, {:0.2f})".format(ai_error_msg_id, AX, AY, ai_router_bit_request))
    sys.exit(1)
  corner_angle = math.acos((AG**2+AH**2-GH**2)/(2*AH*AG))
  #print("dbg206: corner_angle:", corner_angle)
  if(corner_angle>math.pi-radian_epsilon):
    print("WARN673: Warning, the corner angle {:s} is too flat and won't be smoothed!".format(ai_error_msg_id))
    r_outline = [(AX, AY)]
  elif(corner_angle<radian_epsilon):
    print("WARN674: Warning, the corner angle {:s} is too acute and won't be smoothed!".format(ai_error_msg_id))
    r_outline = [(AX, AY)]
  else:
    # AE ( = AF = r/(tan(a/2) )
    AE = ai_router_bit_request/math.tan(corner_angle/2)
    if((AG<AE)or(AH<AE)):
      print("WARN675: Warning, the segments of {:s} are too small to smooth the corner: AG={:0.2f} AH={:0.2f} AE={:0.2f}!".format(ai_error_msg_id, AG, AH, AE))
      r_outline = [(AX, AY)]
    else:
      # coordiantes of E and F
      EX = AX+(GX-AX)*AE/AG
      EY = AY+(GY-AY)*AE/AG
      FX = AX+(HX-AX)*AE/AH
      FY = AY+(HY-AY)*AE/AH
      # AK ( = AL = AI/cos(a/2) = r*(1-sin(a/2))/(sin(a/2)*cos(a/2)) = r*(1-sin(a/2))*2/sin(a) )
      AK = ai_router_bit_request*(1-math.sin(corner_angle/2))*2/math.sin(corner_angle)
      # coordiantes of K and L
      KX = AX+(GX-AX)*AK/AG
      KY = AY+(GY-AY)*AK/AG
      LX = AX+(HX-AX)*AK/AH
      LY = AY+(HY-AY)*AK/AH
      # coordiantes of I
      IX = (KX+LX)/2
      IY = (KY+LY)/2
      r_outline = [(EX,EY), (IX,IY,FX,FY)]
  return(r_outline)

def smooth_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Generate the corner outline for a smoothed line-arc corner
  """
  (SX, SY, UX, UY, xSU, xSJ, router_bit_arc_uw, smooth_status) = sub_smooth_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id)
  r_outline = [(ai_current_point[0], ai_current_point[1])]
  if(smooth_status==1):
    # calculation of the router_bit arc : pt1, pt2, pt3
    #pt1x = SX + ai_router_bit_request*math.cos(xSU)
    #pt1y = SY + ai_router_bit_request*math.sin(xSU)
    pt1x = UX
    pt1y = UY
    pt2x = SX + ai_router_bit_request*math.cos(xSU+router_bit_arc_uw/2)
    pt2y = SY + ai_router_bit_request*math.sin(xSU+router_bit_arc_uw/2)
    pt3x = SX + ai_router_bit_request*math.cos(xSJ)
    pt3y = SY + ai_router_bit_request*math.sin(xSJ)
    r_outline = [(pt1x, pt1y), (pt2x, pt2y, pt3x, pt3y)]
  # return
  return(r_outline)
      
def smooth_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Generate the corner outline for a smoothed arc-arc corner
  """
  (SX, SY, xSI, xSJ, router_bit_arc_uw, smooth_status) = sub_smooth_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id)
  r_outline = [(ai_current_point[0], ai_current_point[1])]
  if(smooth_status==1):
    # calculation of the router_bit arc : pt1, pt2, pt3
    pt1x = SX + ai_router_bit_request*math.cos(xSI)
    pt1y = SY + ai_router_bit_request*math.sin(xSI)
    pt2x = SX + ai_router_bit_request*math.cos(xSI+router_bit_arc_uw/2)
    pt2y = SY + ai_router_bit_request*math.sin(xSI+router_bit_arc_uw/2)
    pt3x = SX + ai_router_bit_request*math.cos(xSJ)
    pt3y = SY + ai_router_bit_request*math.sin(xSJ)
    r_outline = [(pt1x, pt1y), (pt2x, pt2y, pt3x, pt3y)]
  # return
  return(r_outline)

def enlarge_corner_line_line(ai_pre_point, ai_current_point, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Generate the corner outline for a enlarged line-line corner
  """
  r_outline = []
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # to understand the notation, chech the documentation
  (AX,AY)=ai_current_point
  (GX,GY)=ai_pre_point
  (HX,HY)=ai_post_point
  # segment length
  AG=math.sqrt((GX-AX)**2+(GY-AY)**2)
  AH=math.sqrt((HX-AX)**2+(HY-AY)**2)
  GH=math.sqrt((HX-GX)**2+(HY-GY)**2)
  # corner angle
  #if(AG==0):
  if(AG<radian_epsilon):
    print("ERR506: the length AG is null at point {:s} ({:0.2f}, {:0.2f}, {:0.2f})".format(ai_error_msg_id, AX, AY, ai_router_bit_request))
    sys.exit(1)
  #if(AH==0):
  if(AH<radian_epsilon):
    print("ERR507: the length AH is null at point {:s} ({:0.2f}, {:0.2f}, {:0.2f})".format(ai_error_msg_id, AX, AY, ai_router_bit_request))
    sys.exit(1)
  #if(GH==0):
  if(GH<radian_epsilon):
    print("ERR508: the length GH is null at point {:s} ({:0.2f}, {:0.2f}, {:0.2f})".format(ai_error_msg_id, AX, AY, ai_router_bit_request))
    sys.exit(1)
  corner_angle = math.acos((AG**2+AH**2-GH**2)/(2*AH*AG))
  #print("dbg296: corner_angle:", corner_angle)
  if(corner_angle>math.pi-radian_epsilon):
    print("WARN573: Warning, the corner angle {:s} is too flat and won't be enlarged!".format(ai_error_msg_id))
    r_outline = [(AX, AY)]
  elif(corner_angle<radian_epsilon):
    print("WARN574: Warning, the corner angle {:s} is too acute and won't be enlarged!".format(ai_error_msg_id))
    r_outline = [(AX, AY)]
  elif(corner_angle>math.pi/2-radian_epsilon): # enlarge obtuse angle
    # AE ( = AF = 2*r*cos(a/2) )
    AE = 2*ai_router_bit_request*math.cos(corner_angle/2)
    if((AG<AE)or(AH<AE)):
      print("WARN575: Warning, the segments of {:s} are too small to enlarge the obtuse corner: AG={:0.2f} AH={:0.2f} AE={:0.2f}!".format(ai_error_msg_id, AG, AH, AE))
      r_outline = [(AX, AY)]
    else:
      # coordiantes of E and F
      EX = AX+(GX-AX)*AE/AG
      EY = AY+(GY-AY)*AE/AG
      FX = AX+(HX-AX)*AE/AH
      FY = AY+(HY-AY)*AE/AH
      #
      r_outline = [(EX,EY), (AX,AY,FX,FY)]
  else: # enlarge acute angle
    # AM ( = AN = r/sin(a/2) )
    AM = ai_router_bit_request/math.sin(corner_angle/2)
    #print("dbg503: AM:", AM)
    if((AG<AM)or(AH<AM)):
      print("WARN578: Warning, the segments of {:s} are too small to enlarge the acute corner: AG={:0.2f} AH={:0.2f} AM={:0.2f}!".format(ai_error_msg_id, AG, AH, AM))
      r_outline = [(AX, AY)]
    else:
      # coordiantes of M and N
      MX = AX+(GX-AX)*AM/AG
      MY = AY+(GY-AY)*AM/AG
      NX = AX+(HX-AX)*AM/AH
      NY = AY+(HY-AY)*AM/AH
      # AR ( = AS = AM/2 )
      AR = AM/2
      # coordiantes of the vector AR and AS
      ARX = (GX-AX)*AR/AG
      ARY = (GY-AY)*AR/AG
      ASX = (HX-AX)*AR/AH
      ASY = (HY-AY)*AR/AH
      # AV ( = AW = r/cos(a/2) )
      AV = ai_router_bit_request/math.cos(corner_angle/2)
      # coordiantes of the vector AV and AW
      AVX = (GX-AX)*AV/AG
      AVY = (GY-AY)*AV/AG
      AWX = (HX-AX)*AV/AH
      AWY = (HY-AY)*AV/AH
      # coordiantes of K and L
      KX = AX+ARX-ASX+(AVX+AWX)/2 
      KY = AY+ARY-ASY+(AVY+AWY)/2 
      LX = AX-ARX+ASX+(AVX+AWX)/2 
      LY = AY-ARY+ASY+(AVY+AWY)/2 
      #
      r_outline = [(MX,MY), (KX,KY), (AX,AY,LX,LY), (NX,NY)]
  return(r_outline)

def enlarge_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Generate the corner outline for a enlarged line-arc corner
  """
  ((MKX,MKY), (GX,GY), (CX,CY), (HX,HY), (NLX,NLY), enlarge_type_request_1, enlarge_type_request_2, enlarge_status) = sub_enlarge_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id)
  r_outline = [(ai_current_point[0], ai_current_point[1])]
  #print("dbg101: ai_pre_point:", ai_pre_point)
  #print("dbg103: ai_current_point:", ai_current_point)
  #print("dbg104: ai_post_middle:", ai_post_middle)
  #print("dbg105: ai_post_point:", ai_post_point)
  #print("dbg106: ai_router_bit_request:", ai_router_bit_request)
  #print("dbg201: MK: {:0.2f}  {:0.2f}".format(MKX,MKY))
  #print("dbg202: G: {:0.2f}  {:0.2f}".format(GX,GY))
  #print("dbg203: C: {:0.2f}  {:0.2f}".format(CX,CY))
  #print("dbg204: H: {:0.2f}  {:0.2f}".format(HX,HY))
  #print("dbg205: NL: {:0.2f}  {:0.2f}".format(NLX,NLY))
  #print("dbg211: enlarge_type_request_1: {:0.2f}".format(enlarge_type_request_1))
  #print("dbg212: enlarge_type_request_2: {:0.2f}".format(enlarge_type_request_2))
  #print("dbg213: enlarge_status: {:0.2f}".format(enlarge_status))
  if(enlarge_status==1):
    # corner outline construction
    r_outline = [(MKX,MKY)]
    if(enlarge_type_request_1==3):
      r_outline.append((GX,GY))
    if(enlarge_type_request_2==3):
      r_outline.append((CX,CY,HX,HY))
      r_outline.append((NLX,NLY))
    else:
      r_outline.append((CX,CY,NLX,NLY))
    if(enlarge_type_request_1==1): # (enlarge_type_request_2==1)
      r_outline = [(ai_current_point[0], ai_current_point[1])]
  # return
  #r_outline = [(ai_current_point[0], ai_current_point[1])]
  return(r_outline)

def enlarge_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Generate the corner outline for a enlarged arc-arc corner
  """
  ((MKX,MKY), (GX,GY), (CX,CY), (HX,HY), (NLX,NLY), enlarge_type_request_1, enlarge_type_request_2, enlarge_status) = sub_enlarge_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id)
  r_outline = [(ai_current_point[0], ai_current_point[1])]
  #print("dbg101: ai_pre_point:", ai_pre_point)
  #print("dbg102: ai_pre_middle:", ai_pre_middle)
  #print("dbg103: ai_current_point:", ai_current_point)
  #print("dbg104: ai_post_middle:", ai_post_middle)
  #print("dbg105: ai_post_point:", ai_post_point)
  #print("dbg106: ai_router_bit_request:", ai_router_bit_request)
  #print("dbg201: MK: {:0.2f}  {:0.2f}".format(MKX,MKY))
  #print("dbg202: G: {:0.2f}  {:0.2f}".format(GX,GY))
  #print("dbg203: C: {:0.2f}  {:0.2f}".format(CX,CY))
  #print("dbg204: H: {:0.2f}  {:0.2f}".format(HX,HY))
  #print("dbg205: NL: {:0.2f}  {:0.2f}".format(NLX,NLY))
  #print("dbg211: enlarge_type_request_1: {:0.2f}".format(enlarge_type_request_1))
  #print("dbg212: enlarge_type_request_2: {:0.2f}".format(enlarge_type_request_2))
  #print("dbg213: enlarge_status: {:0.2f}".format(enlarge_status))
  if(enlarge_status==1):
    # corner outline construction
    r_outline = [(MKX,MKY)]
    if(enlarge_type_request_1==3):
      r_outline.append((GX,GY))
    if(enlarge_type_request_2==3):
      r_outline.append((CX,CY,HX,HY))
      r_outline.append((NLX,NLY))
    else:
      r_outline.append((CX,CY,NLX,NLY))
    if(enlarge_type_request_1==1): # (enlarge_type_request_2==1)
      r_outline = [(ai_current_point[0], ai_current_point[1])]
  # return
  #print("dbg341: r_outline:", r_outline)
  return(r_outline)

def cnc_cut_corner(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id, ai_error_msg_idx):
  """ Compute the open outline of a corner defined by two segemts (lines or arcs)
      The output outline has the same format as the input format of outline_backends.outline_arc_line()
  """
  #print("dbg107: ai_error_msg_id: {:s}  ai_error_msg_idx: {:d}".format(ai_error_msg_id, ai_error_msg_idx))
  #error_msg_id = "error_msg_id: {:s}.{:d}".format(ai_error_msg_id, ai_error_msg_idx)
  error_msg_id = "{:s}.{:d}".format(ai_error_msg_id, ai_error_msg_idx)
  #print("dbg108: test error_msg_id: ", error_msg_id)
  #print("dbg741: ai_current_point:", ai_current_point)
  r_outline = []
  # ai_router_bit_request: 0:angular, 1:smoothed, 2: enlarged with obtuse angle, 3: enlarged with acute angle
  if(ai_router_bit_request==0):
    r_outline = [(ai_current_point[0], ai_current_point[1])]
  elif(ai_router_bit_request>0):
    if((ai_pre_middle==None)and(ai_post_middle==None)):
      r_outline = smooth_corner_line_line(ai_pre_point, ai_current_point, ai_post_point, ai_router_bit_request, error_msg_id)
    elif((ai_pre_middle==None)and(ai_post_middle!=None)):
      r_outline = smooth_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, error_msg_id)
    elif((ai_pre_middle!=None)and(ai_post_middle==None)):
      r_outline = reverse_outline(smooth_corner_line_arc(ai_post_point, ai_current_point, ai_pre_middle, ai_pre_point, ai_router_bit_request, error_msg_id))
    elif((ai_pre_middle!=None)and(ai_post_middle!=None)):
      r_outline = smooth_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, error_msg_id)
  elif(ai_router_bit_request<0):
    if((ai_pre_middle==None)and(ai_post_middle==None)):
      r_outline = enlarge_corner_line_line(ai_pre_point, ai_current_point, ai_post_point, abs(ai_router_bit_request), error_msg_id)
    elif((ai_pre_middle==None)and(ai_post_middle!=None)):
      r_outline = enlarge_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, abs(ai_router_bit_request), error_msg_id)
    elif((ai_pre_middle!=None)and(ai_post_middle==None)):
      r_outline = reverse_outline(enlarge_corner_line_arc(ai_post_point, ai_current_point, ai_pre_middle, ai_pre_point, abs(ai_router_bit_request), error_msg_id))
    elif((ai_pre_middle!=None)and(ai_post_middle!=None)):
      r_outline = enlarge_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, abs(ai_router_bit_request), error_msg_id)
  #print("dbg578: r_outline:", r_outline)
  return(r_outline)

def arc_middle(ai_arc_pt1, ai_arc_pt2, ai_arc_pt3, ai_new_end1, ai_new_end2, ai_error_msg_id, ai_error_msg_idx):
  """ Compute the middle point of an arc with new end points
  """
  #print("dbg107: ai_error_msg_id: {:s}  ai_error_msg_idx: {:d}".format(ai_error_msg_id, ai_error_msg_idx))
  error_msg_id = "{:s}.{:d}".format(ai_error_msg_id, ai_error_msg_idx)
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  AX = ai_arc_pt1[0]
  AY = ai_arc_pt1[1]
  BX = ai_arc_pt2[0]
  BY = ai_arc_pt2[1]
  CX = ai_arc_pt3[0]
  CY = ai_arc_pt3[1]
  DX = ai_new_end1[0]
  DY = ai_new_end1[1]
  EX = ai_new_end2[0]
  EY = ai_new_end2[1]
  # calculation of I
  (IX,IY, arc_radius, uw, u, w) = arc_center_radius_angles(ai_arc_pt1, ai_arc_pt2, ai_arc_pt3, error_msg_id)
  # check I is equidistant of A,B,C,D,E
  IA = math.sqrt((AX-IX)**2+(AY-IY)**2)
  IB = math.sqrt((BX-IX)**2+(BY-IY)**2)
  IC = math.sqrt((CX-IX)**2+(CY-IY)**2)
  ID = math.sqrt((DX-IX)**2+(DY-IY)**2)
  IE = math.sqrt((EX-IX)**2+(EY-IY)**2)
  if((abs(IA-arc_radius)>radian_epsilon)or(abs(IB-arc_radius)>radian_epsilon)or(abs(IC-arc_radius)>radian_epsilon)):
    print("ERR831: Error, in {:s}, I is not equidistant from A,B,C,D,E. IA={:0.2f} IB={:0.2f} IC={:0.2f}".format(ai_error_msg_id, IA, IB, IC))
    sys.exit(2)
  if((abs(ID-IA)>radian_epsilon)or(abs(IE-IA)>radian_epsilon)):
    print("ERR832: Error, in {:s}, I is not equidistant from A,B,C,D,E. IA={:0.2f} IB={:0.2f} IC={:0.2f} ID={:0.2f} IE={:0.2f}".format(error_msg_id, IA, IB, IC, ID, IE))
    print("dbg414: AX {:0.2f}  AY {:0.2f}".format(AX,AY))
    print("dbg424: BX {:0.2f}  BY {:0.2f}".format(BX,BY))
    print("dbg434: CX {:0.2f}  CY {:0.2f}".format(CX,CY))
    print("dbg444: DX {:0.2f}  DY {:0.2f}".format(DX,DY))
    print("dbg454: EX {:0.2f}  EY {:0.2f}".format(EX,EY))
    print("dbg464: IX {:0.2f}  IY {:0.2f}".format(IX,IY))
    sys.exit(2)
  # calculation of the angles d=(Ix, ID) and e=(Ix, IE)
  d = math.atan2(DY-IY, DX-IX)
  e = math.atan2(EY-IY, EX-IX)
  # calculation of the angles ud=(IA, ID), ue=(IA, IE)
  if(uw<0):
    ud = -1*math.fmod(u-d+4*math.pi, 2*math.pi)
    ue = -1*math.fmod(u-e+4*math.pi, 2*math.pi)
  else:
    ud = math.fmod(d-u+4*math.pi, 2*math.pi)
    ue = math.fmod(e-u+4*math.pi, 2*math.pi)
  # correction because of calculation imprecision
  if(abs(ud)>2*math.pi-radian_epsilon):
    print("WARN771: Warning in {:s}, the angle ud is corrected to zero because of presumed calculation imprecision!".format(error_msg_id))
    ud = 0
  arc_middle_status = 1
  # check if E and F below to the arc segment A,B,C
  if((abs(uw)<abs(ud)-radian_epsilon)or(abs(uw)<abs(ue)-radian_epsilon)):
    print("ERR441: Error, in {:s}, E or F are not on the arc segment A,B,C! uw={:0.2f} ud={:0.2f} ue={:0.2f}".format(error_msg_id, uw, ud, ue))
    print("dbg927: A={:0.2f} {:0.2f}  B={:0.2f} {:0.2f}  C={:0.2f} {:0.2f}  D={:0.2f} {:0.2f}  E={:0.2f} {:0.2f}".format(AX,AY,BX,BY,CX,CY,DX,DY,EX,EY))
    #sys.exit(2)
    arc_middle_status = 2
  # check the orientation of E,F compare to A,B,C
  if(abs(ud)>abs(ue)):
    print("ERR442: Error, in {:s}, E,F have not the same orientation as A,B,C! ud={:0.2f} ue={:0.2f}".format(error_msg_id, ud, ue))
    #sys.exit(2)
    arc_middle_status = 2
  # calculation of the angle de=(ID, IE)
  if(uw<0):
    de = -1*math.fmod(d-e+4*math.pi, 2*math.pi)
  else:
    de = math.fmod(e-d+4*math.pi, 2*math.pi)
  # calculation of the angle f=(Ix, IF)=(Ix, ID)+(ID, IF)
  f = d + de/2
  # calculation of F
  FX = IX+arc_radius*math.cos(f)
  FY = IY+arc_radius*math.sin(f)
  # dummy F in case of error
  if(arc_middle_status==2):
    print("ERR221: Error in {:s} during the recalculation of the arc middle point!".format(error_msg_id))
    sys.exit(2)
    #print("WARN221: Warning in {:s}, creating a dummy arc because of internal error!".format(error_msg_id))
    #lDE = math.sqrt((EX-DX)**2+(EY-DY)**2)
    #xDE = math.atan2(EY-DY, EX-DX)
    #FX = (DX+EX)/2+math.cos(xDE+math.pi/2)*lDE/4
    #FY = (DY+EY)/2+math.sin(xDE+math.pi/2)*lDE/4
  # return
  r_middle_point=(FX, FY)
  return(r_middle_point)

def general_outline_shift_xy(ai_outline, ai_x_offset, ai_x_coefficient, ai_y_offset, ai_y_coefficient):
  """ For each point of the list, add the offset and multiply by coefficient the coordinates
      ai_outline can be list of segments with the format-A or format-B except circle
  """
  # check the parameters
  if((ai_x_coefficient==0)or(ai_y_coefficient==0)):
    print("ERR439: Error, a multiplication coefficient is set to zero: {:0.2f}  {:0.2f}".format(ai_x_coefficient, ai_y_coefficient))
    sys.exit(2)
  # check if the outline must be reversed
  if((ai_x_coefficient*ai_y_coefficient)<0):
    i_outline=reverse_outline(ai_outline)
  else:
    i_outline=ai_outline
  # check the ai_outline format
  outline_type = check_outline_format(i_outline)
  #print("dbg453: outline_type:", outline_type)
  # new outline construction
  r_outline = []
  new_segment = []
  for p in i_outline:
    len_p = len(p)
    # check segment
    is_arc = False
    if(outline_type==1):
      if(len_p==2):
        is_arc = False
      elif(len_p==4):
        is_arc = True
      else:
        print("ERR237: Error, the segment has an unxepected number of items {:d}".format(len_p))
        sys.exit(2)
    elif(outline_type==2):
      if(len_p==3):
        is_arc = False
      elif(len_p==5):
        is_arc = True
      else:
        print("ERR247: Error, the segment has an unxepected number of items {:d}".format(len_p))
        sys.exit(2)
    else:
      print("ERR257: Error, the outline_type is unexpected {:d}".format(outline_type))
      sys.exit(2)
    # extract segments
    end_point = []
    end_point_router_bit = []
    middle_point = []
    if(is_arc):
      middle_point = [p[0], p[1]]
      end_point = [p[2], p[3]]
    else:
      end_point = [p[0], p[1]]
    if(outline_type==2):
      if(is_arc):
        end_point_router_bit = [p[4]]
      else:
        end_point_router_bit = [p[2]]
    # scale segments
    end_point = [ai_x_offset+ai_x_coefficient*end_point[0], ai_y_offset+ai_y_coefficient*end_point[1]]
    if(is_arc):
      middle_point = [ai_x_offset+ai_x_coefficient*middle_point[0], ai_y_offset+ai_y_coefficient*middle_point[1]]
    # reconstruct segments
    new_segment = middle_point
    new_segment.extend(end_point)
    new_segment.extend(end_point_router_bit)
    r_outline.append(tuple(new_segment))
  return(r_outline)

def general_outline_rotate(ai_outline, ai_ox, ai_oy, ai_rotation_angle):
  """ For each point of the list, apply a rotation of angle ai_rotation_angle and rotation center (ai_ox, ai_oy)
      ai_outline can be list of segments with the format-A or with the format-B except circle
  """
  # check the ai_outline format
  outline_type = check_outline_format(ai_outline)
  #print("dbg453: outline_type:", outline_type)
  # new outline construction
  r_outline = []
  new_segment = []
  for p in ai_outline:
    len_p = len(p)
    # check segment
    is_arc = False
    if(outline_type==1):
      if(len_p==2):
        is_arc = False
      elif(len_p==4):
        is_arc = True
      else:
        print("ERR237: Error, the segment has an unxepected number of items {:d}".format(len_p))
        sys.exit(2)
    elif(outline_type==2):
      if(len_p==3):
        is_arc = False
      elif(len_p==5):
        is_arc = True
      else:
        print("ERR247: Error, the segment has an unxepected number of items {:d}".format(len_p))
        sys.exit(2)
    else:
      print("ERR257: Error, the outline_type is unexpected {:d}".format(outline_type))
      sys.exit(2)
    # extract segments
    end_point = []
    end_point_router_bit = []
    middle_point = []
    if(is_arc):
      middle_point = [p[0], p[1]]
      end_point = [p[2], p[3]]
    else:
      end_point = [p[0], p[1]]
    if(outline_type==2):
      if(is_arc):
        end_point_router_bit = [p[4]]
      else:
        end_point_router_bit = [p[2]]
    # rotate points
    end_point = rotate_point(end_point, ai_ox, ai_oy, ai_rotation_angle)
    if(is_arc):
      middle_point = rotate_point(middle_point, ai_ox, ai_oy, ai_rotation_angle)
    # reconstruct segments
    new_segment = middle_point
    new_segment.extend(end_point)
    new_segment.extend(end_point_router_bit)
    r_outline.append(tuple(new_segment))
  return(r_outline)

################################################################
# ******** API function for outline creation ***********
################################################################

def outline_shift_xy(ai_outline, ai_x_offset, ai_x_coefficient, ai_y_offset, ai_y_coefficient):
  """ For each point of the list, add the offset and multiply by coefficient the coordinates
      ai_outline can be list of segments with the format-A (input of cnc_cut_outline.cnc_cut_outline()) or format-B (input of outline_backends.outline_arc_line())
  """
  outline_type = check_outline_format(ai_outline)
  if(outline_type==0): # it's a format-B circle
    if(abs(ai_x_coefficient)!=abs(ai_y_coefficient)):
      print("WARN358: Warning, circle is scaled with different scale along x and y! {:0.2f} {:0.2f}".format(ai_x_coefficient, ai_y_coefficient))
    circle_center_x = ai_outline[0]
    circle_center_y = ai_outline[1]
    circle_radius = ai_outline[2]
    r_outline = (ai_x_offset+ai_x_coefficient*circle_center_x, ai_y_offset+ai_y_coefficient*circle_center_y, circle_radius)
  else: # format-A or format-A general outline
    r_outline = general_outline_shift_xy(ai_outline, ai_x_offset, ai_x_coefficient, ai_y_offset, ai_y_coefficient)
  return(r_outline)

def outline_shift_x(ai_outline, ai_x_offset, ai_x_coefficient):
  """ For each point of the list, add the x_offset and multiply by x_coefficient to the x coordinate
      ai_outline can be list of segments with the format-A or with the format-B
  """
  r_outline =  outline_shift_xy(ai_outline, ai_x_offset, ai_x_coefficient, 0, 1)
  #print("dbg702: r_outline", r_outline)
  return(r_outline)

def outline_shift_y(ai_outline, ai_y_offset, ai_y_coefficient):
  """ For each point of the list, add the y_offset and multiply by y_coefficient to the y coordinate
      ai_outline can be list of segments with the format-A or with the format-B
  """
  r_outline =  outline_shift_xy(ai_outline, 0, 1, ai_y_offset, ai_y_coefficient)
  return(r_outline)

def outline_rotate(ai_outline, ai_ox, ai_oy, ai_rotation_angle):
  """ For each point of the list, apply a rotation of angle ai_rotation_angle and rotation center (ai_ox, ai_oy)
      ai_outline can be list of segments with the format-A or with the format-B
  """
  outline_type = check_outline_format(ai_outline)
  if(outline_type==0): # it's a format-B circle
    circle_center_x = ai_outline[0]
    circle_center_y = ai_outline[1]
    circle_radius = ai_outline[2]
    rotated_circle_center = rotate_point((circle_center_x, circle_center_y), ai_ox, ai_oy, ai_rotation_angle)
    r_outline = (rotated_circle_center[0], rotated_circle_center[1], circle_radius)
  else: # format-A or format-A general outline
    r_outline = general_outline_rotate(ai_outline, ai_ox, ai_oy, ai_rotation_angle)
  return(r_outline)

def outline_close(ai_outline):
  """ close the input outline and return it
      The output outline format is the input outline format.
      It works with the format-A or the format-B
  """
  # check the ai_outline format
  outline_type = check_outline_format(ai_outline)
  r_outline = ai_outline
  if(outline_type!=0): # general outline (not a circle)
    # check if the outline is already closed
    outline_closed = False
    #print("dbg536: ai_outline[-1]:", ai_outline[-1])
    #print("dbg537: ai_outline:", ai_outline)
    if((ai_outline[0][0]==ai_outline[-1][-outline_type-1])and(ai_outline[0][1]==ai_outline[-1][-outline_type])):
      outline_closed = True
      print("WARN421: Warning, the outline is already closed!")
    # construct the output outline
    if(not outline_closed):
      if(outline_type==1):
        r_outline.append([ai_outline[0][0], ai_outline[0][1]])
      elif(outline_type==2):
        r_outline.append([ai_outline[0][0], ai_outline[0][1], 0])
    #print("dbg758: r_outline[-1]:", r_outline[-1])
  return(r_outline)

# add this function to the API
def outline_reverse(ai_outline):
  """ reverse an outline to make the last point becomes the first point
      It handles correctly the middle point of arcs.
      it supports format-A and format-B including circle
  """
  # check the ai_outline format
  outline_type = check_outline_format(ai_outline)
  r_outline = ai_outline
  if(outline_type!=0): # general outline (not a circle)
    r_outline = reverse_outline(ai_outline)
  return(r_outline)

def cnc_cut_outline(ai_segment_list, ai_error_msg_id):
  """
  This function converts a list of segments (lines and arcs) into a list of segments (lines and arcs) compatible with a CNC cut.
  For each input segment, you must provide:
  - the end point (X,Y) for a line 
      or a middle point (X,Y) and the end point (X,Y) for an arc 
  - and the router_bit radius R.
  The start point of a line or an arc is the last point of the previous segment
  If R=0, the point is an angular corner.
  If R>0, the point is smoothed to fit the constraints of a router_bit radius R.
  If R<0, the point is enlarged to fit the constraints of a router_bit radius R.
  eg: ai_segment_list = [ [x1,y1,r1], .. [x2,y2,r2], .. [x3,y3,x4,y4,r4], .. ]
  You can use equally lists or tuples for segment description or segment_list description.
  The first element is the start point of the outline. It must be a tuple of three floats.
  If the last point of the last segment is equal to the start point, the outline is closed. Otherwise the outline is open.
  If the outline is closed, the router_bit request of the start point is used and the router_bit request of the end point of the last segment is ignore.
  From a programming point of view, ai_segment_list is a tuple of 3-tulpes and/or 5-tuples.
  The returned list of segments has the same format as the input list of segment of outline_backends.outline_arc_line()
  """
  # is the outline closed or open?
  #precision_epsilon = 1/1000.0
  outline_closed = False
  if((ai_segment_list[0][0]==ai_segment_list[-1][-3])and(ai_segment_list[0][1]==ai_segment_list[-1][-2])):
  #if((abs(ai_segment_list[0][0]-ai_segment_list[-1][-3])<precision_epsilon)and(abs(ai_segment_list[0][1]==ai_segment_list[-1][-2])<precision_epsilon)):
    outline_closed = True
  #print("dbg536: in {:s} outline_closed: {:d}".format(ai_error_msg_id, outline_closed))
  #print("dbg957: {:0.2f} = {:0.2f}".format(ai_segment_list[0][0], ai_segment_list[-1][-2]))
  #print("dbg958: {:0.2f} = {:0.2f}".format(ai_segment_list[0][1], ai_segment_list[-1][-1]))
  #print("dbg967: ", ai_segment_list[0][0], ai_segment_list[-1][-2])
  #print("dbg968: ", ai_segment_list[0][1], ai_segment_list[-1][-1])
  # number of corners and segments
  point_nb = len(ai_segment_list)
  segment_nb = point_nb-1
  # check of the outline size
  if(segment_nb<1):
    print("ERR202: Error in {:s}, the number of segments must be bigger than 1. Currently: {:d}".format(ai_error_msg_id, segment_nb))
    sys.exit(2)
  if((segment_nb<2)and(outline_closed)):
    print("ERR203: Error in {:s}, the number of segments must be bigger than 2 with a closed outline. Currently: {:d}".format(ai_error_msg_id, point_nb))
    sys.exit(2)
  # check the start point
  if(len(ai_segment_list[0])!=3):
    print("ERR564: the start point is not defined with three floats. {:d}".format(len(ai_segment_list[0])))
    sys.exit(2)
  # extract segment data
  pt_end = []
  pt_mid = []
  pt_request = []
  for pt_idx in range(point_nb):
    # check input segment and extract data
    len_segment = len(ai_segment_list[pt_idx])
    mid_elem = None
    if(len_segment==3):
      (end_pt_x, end_pt_y, end_pt_r) = ai_segment_list[pt_idx]
    elif(len_segment==5):
      (mid_pt_x, mid_pt_y, end_pt_x, end_pt_y, end_pt_r) = ai_segment_list[pt_idx]
      mid_elem = (mid_pt_x, mid_pt_y)
    else:
      print("ERR563: Error, the segment is defined with an unexpected number of float {:d}".format(len_segment))
      sys.exit(2)
    pt_end.append((end_pt_x,end_pt_y))
    pt_request.append(end_pt_r)
    pt_mid.append(mid_elem)
  # check router_bit request of first and last point
  if((pt_request[0]!=0)and(not outline_closed)):
    print("WARN946: Warning, in {:s}, the router_bit request of the start point of the open outline is not zero: {:0.2f}".format(ai_error_msg_id, pt_request[0]))
    pt_request[0]=0
  # if the outline is open, the router_bit request of the last point has no signification
  # if the outline is closed, the router_bit request of the last point is ignore. and the router_bit request of the first point is used
  if(pt_request[-1]!=0):
    print("WARN947: Warning, in {:s}, the router_bit request of the last point of the outline is not zero: {:0.2f}".format(ai_error_msg_id, pt_request[-1]))
    pt_request[-1]=0
  # build outline
  r_outline = []
  # start point
  if(outline_closed):
    r_outline.extend(cnc_cut_corner(pt_end[-2],pt_mid[-1], pt_end[0], pt_mid[1], pt_end[1], pt_request[0], ai_error_msg_id, 0))
  else:
    r_outline.append(pt_end[0])
  # middle of the outline
  for corn_idx in range(point_nb-2):
    # get the last point of the outline under construction
    #previous_point = pt_end[corn_idx]
    previous_point = (r_outline[-1][-2], r_outline[-1][-1])
    # compute a temporary middle point because it might be out of the arc
    tmp_middle_point = pt_mid[corn_idx+1]
    if(tmp_middle_point!=None):
      last_point = previous_point
      next_point = pt_end[corn_idx+1]
      tmp_middle_point = arc_middle(pt_end[corn_idx], pt_mid[corn_idx+1], pt_end[corn_idx+1], last_point, next_point, "{:s}.am1".format(ai_error_msg_id), corn_idx+1)
    # following point
    following_point = pt_end[corn_idx+2]
    following_middle_point =  pt_mid[corn_idx+2]
    if(outline_closed and (corn_idx==point_nb-3)):
      following_point = r_outline[0]
      if(following_middle_point!=None):
        following_middle_point = arc_middle(pt_end[-2], pt_mid[-1], pt_end[-1], pt_end[-2], following_point, "{:s}.am2".format(ai_error_msg_id), -2)
    # compute the corner outline
    new_corner = cnc_cut_corner(previous_point, tmp_middle_point, pt_end[corn_idx+1], following_middle_point, following_point, pt_request[corn_idx+1], ai_error_msg_id, corn_idx+1)
    #print("dbg551: previous_point", previous_point)
    #print("dbg552: tmp_middle_point", tmp_middle_point)
    #print("dbg553: pt_end[corn_idx+1]", pt_end[corn_idx+1])
    #print("dbg554: following_middle_point", following_middle_point)
    #print("dbg555: following_point", following_point)
    #print("dbg556: pt_request[corn_idx+1]", pt_request[corn_idx+1])
    #print("dbg557: new_corner", new_corner)
    # recompute the final middle point because it might be out of the arc
    if(pt_mid[corn_idx+1]!=None):
      last_point = (r_outline[-1][-2], r_outline[-1][-1])
      next_point = new_corner[0]
      new_middle_point = arc_middle(pt_end[corn_idx], pt_mid[corn_idx+1], pt_end[corn_idx+1], last_point, next_point, "{:s}.am3".format(ai_error_msg_id), corn_idx+1)
      #print("dbg632: new_middle_point:", new_middle_point)
      #print("dbg534: next_point:", next_point)
      new_corner[0] = (new_middle_point[0], new_middle_point[1], next_point[0], next_point[1])
    r_outline.extend(new_corner)
  # last segment
  if(outline_closed):
    next_point=r_outline[0]
  else:
    next_point=pt_end[-1]
  if(pt_mid[-1]!=None):
    last_point = (r_outline[-1][-2], r_outline[-1][-1])
    new_middle_point = arc_middle(pt_end[-2], pt_mid[-1], pt_end[-1], last_point, next_point, "{:s}.am4".format(ai_error_msg_id), -1)
    last_segment = (new_middle_point[0], new_middle_point[1], next_point[0], next_point[1])
  else:
    last_segment = (next_point[0], next_point[1])
  r_outline.append(last_segment)
  # function return
  return(r_outline)

def approximate_curve_tangent(ai_polyline, ai_error_msg_id):
  """
  This function gets a list of points (outline format b with only lines).
  It returns an outline format c (containing points and their tangent).
  The tangents are computed using the previous and following points.
  You can also consider this function as a convertor from outline_format_b to outline_format_c
  """
  #radian_epsilon = 1/1000.0
  # check if the input outline is closed
  outline_closed = False
  if((ai_polyline[0][0]==ai_polyline[-1][-2])and(ai_polyline[0][1]==ai_polyline[-1][-1])):
  #if((abs(ai_polyline[0][0]-ai_polyline[-1][-2])<radian_epsilon)and(abs(ai_polyline[0][1]==ai_polyline[-1][-1])<radian_epsilon)):
    outline_closed = True
  point_nb = len(ai_polyline)
  # check the outline point number
  if(point_nb<2):
    print("ERR309: Error in {:s}, the number of points must be bigger than 2. Currently: {:d}".format(ai_error_msg_id, point_nb))
    sys.exit(2)
  # check if ai_polyline is valid
  for i in range(len(ai_polyline)):
    point_len = len(ai_polyline[i])
    if(point_len!=2):
      print("ERR319: Error in {:s}, the point {:d} of ai_polyline must have exactly 2 elements. Currently: {:d}".format(ai_error_msg_id, i, point_len))
      sys.exit(2)
  # processing initialization
  r_outline = []
  pre_point = ai_polyline[0]
  post_point = ai_polyline[1]
  if(outline_closed):
    pre_point = ai_polyline[-1]
  segment_length = math.sqrt((post_point[0]-pre_point[0])**2+(post_point[1]-pre_point[1])**2)
  tangent_inclination = math.atan2((post_point[1]-pre_point[1])/segment_length, (post_point[0]-pre_point[0])/segment_length)
  if(not outline_closed):
    post2_point = ai_polyline[2]
    segment_length2 = math.sqrt((post2_point[0]-pre_point[0])**2+(post2_point[1]-pre_point[1])**2)
    tangent_inclination2 = math.atan2((post2_point[1]-pre_point[1])/segment_length, (post2_point[0]-pre_point[0])/segment_length)
    tangent_inclination2_diff = math.fmod(tangent_inclination2-tangent_inclination+5*math.pi, 2*math.pi) - math.pi
    if(abs(tangent_inclination2_diff)>math.pi/3):
      print("ERR315: Error in {:s}, the tangent_inclination is changing too fast for a curve approximation. tangent_inclination: {:0.2f}  tangent_inclination2: {:0.2f}".format(ai_error_msg_id, tangent_inclination, tangent_inclination2))
      sys.exit(2)
    tangent_inclination = math.fmod(tangent_inclination-1*tangent_inclination2_diff/2 + 5*math.pi, 2*math.pi) - math.pi
  r_outline.append((ai_polyline[0][0], ai_polyline[0][1], tangent_inclination)) # first-point
  # processing incrementation
  for i in range(point_nb-2):
    # error message
    i_error_msg_id = "{:s}.{:d}".format(ai_error_msg_id, i)
    pre_point = ai_polyline[i]
    post_point = ai_polyline[i+2]
    segment_length = math.sqrt((post_point[0]-pre_point[0])**2+(post_point[1]-pre_point[1])**2)
    tangent_inclination = math.atan2((post_point[1]-pre_point[1])/segment_length, (post_point[0]-pre_point[0])/segment_length)
    r_outline.append((ai_polyline[i+1][0], ai_polyline[i+1][1], tangent_inclination)) # point
  # processing ending
  pre_point = ai_polyline[-2]
  post_point = ai_polyline[-1]
  if(outline_closed):
    post_point = ai_polyline[0]
  segment_length = math.sqrt((post_point[0]-pre_point[0])**2+(post_point[1]-pre_point[1])**2)
  tangent_inclination = math.atan2((post_point[1]-pre_point[1])/segment_length, (post_point[0]-pre_point[0])/segment_length)
  if(not outline_closed):
    pre2_point = ai_polyline[-3]
    segment_length2 = math.sqrt((post_point[0]-pre2_point[0])**2+(post_point[1]-pre2_point[1])**2)
    tangent_inclination2 = math.atan2((post_point[1]-pre2_point[1])/segment_length, (post_point[0]-pre2_point[0])/segment_length)
    tangent_inclination2_diff = math.fmod(tangent_inclination2-tangent_inclination+5*math.pi, 2*math.pi) - math.pi
    if(abs(tangent_inclination2_diff)>math.pi/3):
      print("ERR315: Error in {:s}, the tangent_inclination is changing too fast for a curve approximation. tangent_inclination: {:0.2f}  tangent_inclination2: {:0.2f}".format(ai_error_msg_id, tangent_inclination, tangent_inclination2))
      sys.exit(2)
    tangent_inclination = math.fmod(tangent_inclination-1*tangent_inclination2_diff/2 + 5*math.pi, 2*math.pi) - math.pi
  r_outline.append((ai_polyline[-1][0], ai_polyline[-1][1], tangent_inclination)) # end-point
  # return
  return(r_outline)

def smooth_outline_c_curve(ai_polyline, ai_precision, ai_router_bit_request, ai_error_msg_id):
  """
  This function computes a serie of 2N arcs that pass through the (N+1) points defined by the N line-segments of ai_polyline.
  ai_polyline is an outline of format C, (list of list of 3 floats).
  ai_precision defined when a line should be generated instead of an arc because the tangent and the new segment are almost collinear.
  ai_router_bit_request is just used to warn if the radius_of_curvature is smaller than the router_bit. Because this function can not know on which side of the outline is the material, those warnings might be irrelevant. If you don't want this feature, just set it to 0, this disables these warnings.
  ai_error_msg_id is a string, that can help you to track bugs and erros.
  The function returns an outline of format B containing only arcs
  """
  r_outline = sub_smooth_outline_c_curve(ai_polyline, ai_precision, ai_router_bit_request, ai_error_msg_id)
  #for i in range(len(r_outline)):
  #  print("dbg339: i r_outline[i]:", i, r_outline[i])
  # return
  return(r_outline)

#def smooth_outline_b_curve(ai_polyline, ai_initial_tangent, ai_precision, ai_router_bit_request, ai_error_msg_id):
def smooth_outline_b_curve(ai_polyline, ai_precision, ai_router_bit_request, ai_error_msg_id):
  """
  This function computes a serie of 2N arcs that pass through the (N+1) points defined by the N line-segments of ai_polyline.
  ai_polyline is an outline of format B, that contains only lines (no arcs) (list of list of 2 floats).
  ai_initial_tangent is the tangent of the wished curve at the first-point of the outline ai_polyline.
  ai_precision defined when a line should be generated instead of an arc because the tangent and the new segment are almost collinear.
  ai_router_bit_request is just used to warn if the radius_of_curvature is smaller than the router_bit. Because this function can not know on which side of the outline is the material, those warnings might be irrelevant. If you don't want this feature, just set it to 0, this disables these warnings.
  ai_error_msg_id is a string, that can help you to track bugs and erros.
  The function returns an outline of format B containing only arcs
  """
  #r_outline = unstable_smooth_outline_b_curve(ai_polyline, ai_initial_tangent, ai_precision, ai_router_bit_request, ai_error_msg_id)
  outline_c = approximate_curve_tangent(ai_polyline, ai_error_msg_id)
  r_outline = smooth_outline_c_curve(outline_c, ai_precision, ai_router_bit_request, ai_error_msg_id)
  # return
  return(r_outline)

def ideal_outline(ai_outline, ai_error_msg_id):
  """ extract a format-B outline from a format-A or format-C outlines
      The returned ideal outline is probably not makable by a 3-axis CNC
      but you can use it to display it and understand the cnc_cut_outline() and smooth_outline_c_curve()
  """
  outline_type = check_outline_format(ai_outline)
  if(outline_type==2): # format-A or format-C outline
    r_outline = []
    i = 0
    for i_segment in ai_outline:
      # check the segment length
      segment_len = len(i_segment)
      if((segment_len!=3)and(segment_len!=5)):
        print("ERR868: Error in {:s}.{:d}, len(segment_len) is not 3 or 5!".format(ai_error_msg_id, i))
        sys.exit(2)
      i += 1
      # construct the ideal outline
      r_outline.append(i_segment[:-1]) # remove the third or the fifth element
  else: # format-B circle or format-B general outline
    print("WARN441: Warning in {:s}, nothing to do, the outline is already in format-B".format(ai_error_msg_id))
    r_outline = ai_outline
  return(r_outline)


################################################################
# cnc_cut_outline API testing
################################################################

################################################################
# addition import for the tests
################################################################

import importing_freecad 
importing_freecad.importing_freecad()
#
import Part
from FreeCAD import Base 
#
import Tkinter
import outline_backends
#
#import timeit
#import cProfile
import time


def make_H_shape(ai_origin_x, ai_origin_y, ai_router_bit_r, ai_height, ai_output_file):
  """ design a H-shape to test 90 degree angles with the function cnc_cut_outline()
  """
  print("dbg601: make the H-shape")
  ## yardstick
  ys_xa = 5
  ys_xb = 10
  ys_yc = 15
  ys_cd = 8
  xox = ai_origin_x
  xoy = ai_origin_y
  ## outline definition: in this example we draw a 'H'
  myh_outline=[
  [xox + 0*ys_xa + 0*ys_xb, xoy + 0*ys_yc + 0*ys_cd, 0*ai_router_bit_r],
  [xox + 1*ys_xa + 0*ys_xb, xoy + 0*ys_yc + 0*ys_cd, ai_router_bit_r],
  [xox + 1*ys_xa + 0*ys_xb, xoy + 1*ys_yc + 0*ys_cd, -4*ai_router_bit_r],
  [xox + 1*ys_xa + 1*ys_xb, xoy + 1*ys_yc + 0*ys_cd, ai_router_bit_r],
  [xox + 1*ys_xa + 1*ys_xb, xoy + 0*ys_yc + 0*ys_cd, ai_router_bit_r],
  [xox + 2*ys_xa + 1*ys_xb, xoy + 0*ys_yc + 0*ys_cd, ai_router_bit_r],
  [xox + 2*ys_xa + 1*ys_xb, xoy + 2*ys_yc + 1*ys_cd, ai_router_bit_r],
  [xox + 1*ys_xa + 1*ys_xb, xoy + 2*ys_yc + 1*ys_cd, ai_router_bit_r],
  [xox + 1*ys_xa + 1*ys_xb, xoy + 1*ys_yc + 1*ys_cd, ai_router_bit_r],
  [xox + 1*ys_xa + 0*ys_xb, xoy + 1*ys_yc + 1*ys_cd, ai_router_bit_r],
  [xox + 1*ys_xa + 0*ys_xb, xoy + 2*ys_yc + 1*ys_cd, ai_router_bit_r],
  [xox + 0*ys_xa + 0*ys_xb, xoy + 2*ys_yc + 1*ys_cd, ai_router_bit_r],
  [xox + 0*ys_xa + 0*ys_xb, xoy + 0*ys_yc + 0*ys_cd, 0*ai_router_bit_r]]
  ## construction
  myh_outline = cnc_cut_outline(myh_outline, 'h_shape')
  myh_shape = outline_backends.outline_arc_line(myh_outline, 'freecad')
  #Part.show(myh_shape) # for debug
  # preparation for the extrusion
  myh_wire = Part.Wire(myh_shape.Edges)
  myh_face = Part.Face(myh_wire)
  # extrusion
  myh_solid = myh_face.extrude(Base.Vector(0,0,ai_height)) # straight linear extrusion
  ## output
  Part.show(myh_solid) # works only with FreeCAD GUI, ignore otherwise
  if(ai_output_file!=''):
    myh_solid.exportStl(ai_output_file)
    print("output stl file: %s"%(ai_output_file))

def make_X_shape(ai_origin_x, ai_origin_y, ai_router_bit_r, ai_height, ai_output_file):
  """ design a X-shape to test not 90 degree angles with the function cnc_cut_outline()
  """
  print("dbg602: make the X-shape")
  ## yardstick
  xys_xa = 10
  xys_xb = 20
  xys_yc = 30
  xox = ai_origin_x
  xoy = ai_origin_y
  ## outline definition: in this example we draw a 'X'
  myx_outline=[
  [xox+0*xys_xa+0*xys_xb, xoy+0*xys_yc, 0*ai_router_bit_r],
  [xox+1*xys_xa+0*xys_xb, xoy+1*xys_yc, 1*ai_router_bit_r],
  [xox+1*xys_xa+1*xys_xb, xoy+2*xys_yc,-1*ai_router_bit_r],
  [xox+1*xys_xa+2*xys_xb, xoy+1*xys_yc, 1*ai_router_bit_r],
  [xox+2*xys_xa+2*xys_xb, xoy+0*xys_yc, 1*ai_router_bit_r],
  [xox+2*xys_xa+1*xys_xb, xoy+3*xys_yc, 1*ai_router_bit_r],
  [xox+2*xys_xa+2*xys_xb, xoy+6*xys_yc, 1*ai_router_bit_r],
  [xox+2*xys_xa+1*xys_xb, xoy+5*xys_yc, 1*ai_router_bit_r],
  [xox+1*xys_xa+1*xys_xb, xoy+4*xys_yc, 1*ai_router_bit_r],
  [xox+0*xys_xa+1*xys_xb, xoy+5*xys_yc, 1*ai_router_bit_r],
  [xox+0*xys_xa+0*xys_xb, xoy+6*xys_yc, 2*ai_router_bit_r],
  [xox+1*xys_xa+0*xys_xb, xoy+3*xys_yc, 1*ai_router_bit_r],
  [xox+0*xys_xa+0*xys_xb, xoy+0*xys_yc, 0*ai_router_bit_r]]
  ## construction
  myx_outline = cnc_cut_outline(myx_outline, 'x_shape')
  myx_shape = outline_backends.outline_arc_line(myx_outline, 'freecad')
  myx_wire = Part.Wire(myx_shape.Edges)
  myx_face = Part.Face(myx_wire)
  myx_solid = myx_face.extrude(Base.Vector(0,0,ai_height)) # straight linear extrusion
  ## output
  Part.show(myx_solid) # works only with FreeCAD GUI, ignore otherwise
  if(ai_output_file!=''):
    myx_solid.exportStl(ai_output_file)
    print("output stl file: %s"%(ai_output_file))

def make_M_shape(ai_origin_x, ai_origin_y, ai_router_bit_r, ai_height, ai_output_file):
  """ design a M-shape to test the three outline_shift_x, _y and _xy functions
  """
  print("dbg602: make the M-shape")
  ## yardstick
  mw = 100
  mh = 100
  mox = ai_origin_x
  moy = ai_origin_y
  ## jonction : piece of outline
  jonction_a = [
    [5, 0, 0*ai_router_bit_r],
    [5, 10, 1*ai_router_bit_r],
    [20, 10, -1*ai_router_bit_r],
    [10, 0, 0*ai_router_bit_r]]
  jonction_b = [
    [0, 30, 0*ai_router_bit_r],
    [20, 40, 1*ai_router_bit_r],
    [10, 20, 1*ai_router_bit_r],
    [0, 20, 0*ai_router_bit_r]]
  ## outline definition: in this example we draw a 'X'
  myx_outline=[]
  myx_outline.append([0*mw, 0*mh, 0*ai_router_bit_r])
  myx_outline.extend(outline_shift_x(jonction_a, 0*mw, 1))
  myx_outline.extend(outline_shift_x(jonction_a, 1*mw,-1))
  myx_outline.append([1*mw, 0*mh, 0*ai_router_bit_r])
  myx_outline.extend(outline_shift_x(jonction_b, 1*mw, -1))
  myx_outline.append([1*mw, 1*mh, 0*ai_router_bit_r])
  myx_outline.extend(outline_shift_xy(jonction_a, 1*mw, -1, 1*mh, -1))
  myx_outline.extend(outline_shift_y(jonction_a, 1*mh, -1))
  myx_outline.append([0*mw, 1*mh, 0*ai_router_bit_r])
  myx_outline.extend(outline_shift_x(jonction_b, 0*mw, 1))
  myx_outline.append([0*mw, 0*mh, 0*ai_router_bit_r])
  ## set origine
  myx_outline = outline_shift_xy(myx_outline, mox, 1, moy, 1)
  ## construction
  myx_outline = cnc_cut_outline(myx_outline, 'm_shape')
  myx_shape = outline_backends.outline_arc_line(myx_outline, 'freecad')
  myx_wire = Part.Wire(myx_shape.Edges)
  myx_face = Part.Face(myx_wire)
  myx_solid = myx_face.extrude(Base.Vector(0,0,ai_height)) # straight linear extrusion
  ## output
  Part.show(myx_solid) # works only with FreeCAD GUI, ignore otherwise
  if(ai_output_file!=''):
    myx_solid.exportStl(ai_output_file)
    print("output stl file: %s"%(ai_output_file))

def cnc_cut_outline_test1():
  """ First test to check the cnc_cut_outline API
  """
  ### check the cnc_cut_outline function with several router_bit diameter
  y_offset = 0
  for ir in [2.0, 1.5, 1.0, 0, -1.0, -2.0]:
    print("dbg603: test with router_bit radius (ir):", ir)
    make_H_shape( 0,  y_offset, ir, 2, "self_test_cnc_cut_outline_H_r%0.2f.stl"%ir)
    make_X_shape(50,  y_offset, ir, 2, "self_test_cnc_cut_outline_X_r%0.2f.stl"%ir)
    make_M_shape(150,  y_offset, ir, 2, "self_test_cnc_cut_outline_M_r%0.2f.stl"%ir)
    y_offset += 200
  r_test = 1
  return(r_test)

def cnc_cut_outline_test2(ai_sw_output_file_base, ai_sw_router_bit_radius, ai_sw_height):
  """ Second test to check the cnc_cut_outline API
  """
  ### check the cnc_cut_outline through examples
  ofb_H_shape = ""
  ofb_X_shape = ""
  ofb_M_shape = ""
  if(ai_sw_output_file_base!=""):
    ofb_H_shape = ai_sw_output_file_base + "_S_shape.stl"
    ofb_X_shape = ai_sw_output_file_base + "_X_shape.stl"
    ofb_M_shape = ai_sw_output_file_base + "_M_shape.stl"
  make_H_shape(0, 0, ai_sw_router_bit_radius, ai_sw_height, ofb_H_shape)
  make_X_shape(50, 0, ai_sw_router_bit_radius, ai_sw_height, ofb_X_shape)
  make_M_shape(150, 0, ai_sw_router_bit_radius, ai_sw_height, ofb_M_shape)
  r_test = 1
  return(r_test)

def cnc_cut_outline_test3(ai_sw_router_bit_radius):
  """ Third test to check the cnc_cut_outline API
      It displays the shapes with Tkinter
  """
  print("Run test_3  with ai_sw_router_bit_radius={:0.2f} ...".format(ai_sw_router_bit_radius))
  def outline_a(ai_router_bit_radius):
    corner_a=[
      [0,20, ai_router_bit_radius],
      [-5,15,0,10,ai_router_bit_radius],
      [-5,-5,10,0,ai_router_bit_radius],
      [15,-5,20,0,ai_router_bit_radius]]
    chichi_horizontal = [
      [40,0,ai_router_bit_radius],
      [45,5,50,0,ai_router_bit_radius],
      [60,-20,ai_router_bit_radius],
      [70,20,-ai_router_bit_radius],
      [80,-20,ai_router_bit_radius],
      [90,0,ai_router_bit_radius],
      [95,5,100,0,ai_router_bit_radius]]
    chichi_vertical = [
      [0,100,ai_router_bit_radius],
      [5,95,0,90,ai_router_bit_radius],
      [-20,80,ai_router_bit_radius],
      [20,70,-ai_router_bit_radius],
      [-20,60,ai_router_bit_radius],
      [0,50,ai_router_bit_radius],
      [5,45,0,40,ai_router_bit_radius]]
    arc_arc_horizontal = [
      [150,0,ai_router_bit_radius],
      [155, 5,160,18,ai_router_bit_radius],
      [165, 5,170, 0,ai_router_bit_radius],
      [175,15,180,20,ai_router_bit_radius],
      [185, 5,190, 0,ai_router_bit_radius],
      [195, 5,200,20,ai_router_bit_radius],
      [205,18,210, 0,ai_router_bit_radius],
      [214, -5,225,-10,ai_router_bit_radius],
      [229, 0,230,10,ai_router_bit_radius],
      [235,14,240,20,ai_router_bit_radius],
      [241,10,245,0,ai_router_bit_radius]]
    line_arc_vertical = [
      [0,200,ai_router_bit_radius],
      [10,198,20,190,ai_router_bit_radius],
      [0,190,ai_router_bit_radius],
      [10,182,30,180,ai_router_bit_radius],
      [30,170,ai_router_bit_radius],
      [0,170,ai_router_bit_radius],
      [10,167,20,160,ai_router_bit_radius],
      [30,160,ai_router_bit_radius],
      [32,155,30,150,ai_router_bit_radius],
      [20,150,ai_router_bit_radius],
      [15,145, 0,140,ai_router_bit_radius]]
    r_outline_a1 = []
    r_outline_a1.extend(outline_shift_xy(corner_a,0,1,0,1))
    r_outline_a1.extend(outline_shift_x(chichi_horizontal,0,1))
    r_outline_a1.extend(outline_shift_x(arc_arc_horizontal,0,1))
    r_outline_a1.extend(outline_shift_x(arc_arc_horizontal,500,-1))
    r_outline_a1.extend(outline_shift_x(chichi_horizontal,500,-1))
    r_outline_a1.extend(outline_shift_xy(corner_a,500,-1,0,1))
    r_outline_a1.extend(outline_shift_x(chichi_vertical,500,-1))
    r_outline_a1.extend(outline_shift_x(line_arc_vertical,500,-1))
    r_outline_a1.extend(outline_shift_xy(line_arc_vertical,500,-1,420,-1))
    r_outline_a1.extend(outline_shift_xy(chichi_vertical,500,-1,420,-1))
    r_outline_a1.extend(outline_shift_xy(corner_a,500,-1,420,-1))
    r_outline_a1.extend(outline_shift_xy(chichi_horizontal,500,-1,420,-1))
    r_outline_a1.extend(outline_shift_xy(arc_arc_horizontal,500,-1,420,-1))
    r_outline_a1.extend(outline_shift_y(arc_arc_horizontal,420,-1))
    r_outline_a1.extend(outline_shift_y(chichi_horizontal,420,-1))
    r_outline_a1.extend(outline_shift_xy(corner_a,0,1,420,-1))
    r_outline_a1.extend(outline_shift_y(chichi_vertical,420,-1))
    r_outline_a1.extend(outline_shift_y(line_arc_vertical,420,-1))
    r_outline_a1.extend(outline_shift_y(line_arc_vertical,0,1))
    r_outline_a1.extend(outline_shift_y(chichi_vertical,0,1))
    return(r_outline_a1)
  # outline_a : open, CCW (CCW has no meaning because the outline is open)
  outline_a1 = cnc_cut_outline(outline_a(0), 'cnc_cut_outline_test3_a1')
  outline_a2 = cnc_cut_outline(outline_a(ai_sw_router_bit_radius), 'cnc_cut_outline_test3_a2')
  # outline_b : closed, CCW
  outline_b1 = outline_shift_x(cnc_cut_outline(outline_close(outline_a(0)), 'cnc_cut_outline_test3_b1'), 600,1)
  outline_b2 = outline_shift_x(cnc_cut_outline(outline_close(outline_a(ai_sw_router_bit_radius)), 'cnc_cut_outline_test3_b2'), 600,1)
  # outline_c : closed, CW
  #outline_c1 = outline_shift_y(cnc_cut_outline(outline_reverse(outline_close(outline_a(0))), 'cnc_cut_outline_test3_c1'), 500,1)
  #outline_c2 = outline_shift_y(cnc_cut_outline(outline_reverse(outline_close(outline_a(ai_sw_router_bit_radius))), 'cnc_cut_outline_test3_c2'), 500,1)
  # outline_d : closed, CCW, rotate
  #outline_d1 = outline_shift_xy(cnc_cut_outline(outline_close(outline_rotate(outline_a(0),500/2,420/2,math.pi/7)), 'cnc_cut_outline_test3_d1'), 600,1,600,1)
  #outline_d2 = outline_shift_xy(cnc_cut_outline(outline_close(outline_rotate(outline_a(-1*ai_sw_router_bit_radius),500/2,420/2,math.pi/7)), 'cnc_cut_outline_test3_d2'), 600,1,600,1)
  first_curve=[
    [20,0],
    [22,10],
    [25,20],
    [32,30],
    [35,40],
    [36,50],
    [36,60]]
  radian_precision = math.pi/100
  outline_e1 = first_curve
  outline_e2 = smooth_outline_b_curve(first_curve, radian_precision, ai_sw_router_bit_radius, 'cnc_cut_outline_test3_e2')

  # display with Tkinter
  tk_root = Tkinter.Tk()
  my_canvas = outline_backends.Two_Canvas(tk_root)
  # callback function for display_backend
  def sub_canvas_graphics(ai_rotation_direction, ai_angle_position):
    # outline_c : closed, CW
    # settings for no error
    delta_x = 0.15
    delta_y = 0.15
    # settings for error generation
    #delta_x = 0.25
    #delta_y = 0.25
    outline_c1 = cnc_cut_outline(outline_shift_xy(outline_reverse(outline_close(outline_a(0))),
      -100, 1.0+delta_x*math.cos(ai_angle_position), 500, 1.0+delta_y*math.sin(ai_angle_position)), 'cnc_cut_outline_test3_c1')
    outline_c2 = cnc_cut_outline(outline_shift_xy(outline_reverse(outline_close(outline_a(ai_sw_router_bit_radius))),
      -100, 1.0+delta_x*math.cos(ai_angle_position), 500, 1.0+delta_y*math.sin(ai_angle_position)), 'cnc_cut_outline_test3_c2')
    # outline_d : closed, CCW, rotate
    outline_d1 = outline_shift_xy(cnc_cut_outline(outline_close(outline_rotate(outline_a(0),500/2,420/2,math.pi/7+ai_angle_position)), 'cnc_cut_outline_test3_d1'), 600,1,600,1)
    outline_d2 = outline_shift_xy(cnc_cut_outline(outline_close(outline_rotate(outline_a(-1*ai_sw_router_bit_radius),500/2,420/2,math.pi/7+ai_angle_position)), 'cnc_cut_outline_test3_d2'), 600,1,600,1)
    #
    r_canvas_graphics = []
    r_canvas_graphics.append(('graphic_lines', outline_backends.outline_arc_line(outline_a1, 'tkinter'), 'red', 1))
    r_canvas_graphics.append(('overlay_lines', outline_backends.outline_arc_line(outline_a2, 'tkinter'), 'green', 2))
    r_canvas_graphics.append(('graphic_lines', outline_backends.outline_arc_line(outline_b1, 'tkinter'), 'red', 1))
    r_canvas_graphics.append(('overlay_lines', outline_backends.outline_arc_line(outline_b2, 'tkinter'), 'green', 2))
    r_canvas_graphics.append(('graphic_lines', outline_backends.outline_arc_line(outline_c1, 'tkinter'), 'blue', 1))
    r_canvas_graphics.append(('overlay_lines', outline_backends.outline_arc_line(outline_c2, 'tkinter'), 'green', 2))
    r_canvas_graphics.append(('graphic_lines', outline_backends.outline_arc_line(outline_d1, 'tkinter'), 'red', 1))
    r_canvas_graphics.append(('overlay_lines', outline_backends.outline_arc_line(outline_d2, 'tkinter'), 'green', 2))
    r_canvas_graphics.append(('graphic_lines', outline_backends.outline_arc_line(outline_e1, 'tkinter'), 'red', 1))
    r_canvas_graphics.append(('overlay_lines', outline_backends.outline_arc_line(outline_e2, 'tkinter'), 'green', 2))
    return(r_canvas_graphics)
  # end of callback function
  # measurement the execution time of the callback function
  def measure_the_execution_time_of_the_sub_canvas_graphics_function(ai_repeat_nb):
    #print("dbg506: time sub_canvas_graphics:", timeit.timeit(stmt='sub_canvas_graphics(1, 0)', number=100))
    #cProfile.run('sub_canvas_graphics(1, 0)')
    time_start = time.clock()
    for i in range(ai_repeat_nb):
      tmp = sub_canvas_graphics(1, i*math.pi/200)
    time_stop = time.clock()
    print("dbg507: time sub_canvas_graphics:", time_stop-time_start)
  #measure_the_execution_time_of_the_sub_canvas_graphics_function(100)
  # end of measurement
  my_canvas.add_canvas_graphic_function(sub_canvas_graphics)
  tk_root.mainloop()
  # end of display with Tkinter
  r_test = 1
  return(r_test)

def cnc_cut_outline_test4(ai_sw_router_bit_radius):
  """ Fourth test suggests small shapes, useful to develop the cnc_cut_outline API
      It displays the shapes with Tkinter
  """
  print("Run test_4  with ai_sw_router_bit_radius={:0.2f} ...".format(ai_sw_router_bit_radius))
  def outline_t4_a(ai_router_bit_radius):
    three_arcs=[
      [0,20, 0],
      [-5,15,0,10,ai_router_bit_radius],
      [-5,-5,10,0,ai_router_bit_radius],
      [15,-5,20,0,0]]
    arc_arc_horizontal = [
      [150,0,ai_router_bit_radius],
      [155, 5,160,18,ai_router_bit_radius],
      [165, 5,170, 0,ai_router_bit_radius],
      [175,15,180,20,ai_router_bit_radius],
      [185, 5,190, 0,ai_router_bit_radius],
      [195, 5,200,20,ai_router_bit_radius],
      [205,18,210, 0,ai_router_bit_radius],
      [214, -5,225,-10,ai_router_bit_radius],
      [229, 0,230,10,ai_router_bit_radius],
      [235,14,240,20,ai_router_bit_radius],
      [241,10,245,0,ai_router_bit_radius]]
    line_arc_vertical = [
      [0,200,ai_router_bit_radius],
      [10,198,20,190,ai_router_bit_radius],
      [0,190,ai_router_bit_radius],
      [10,182,30,180,ai_router_bit_radius],
      [30,170,ai_router_bit_radius],
      [0,170,ai_router_bit_radius],
      [10,167,20,160,ai_router_bit_radius],
      [30,160,ai_router_bit_radius],
      [32,155,30,150,ai_router_bit_radius],
      [20,150,ai_router_bit_radius],
      [15,145, 0,140,ai_router_bit_radius]]
    r_outline_t4_a1=[]
    r_outline_t4_a1.append([0,220,0])
    r_outline_t4_a1.extend(line_arc_vertical)
    r_outline_t4_a1.extend(three_arcs)
    #r_outline_t4_a1.extend(outline_shift_x(arc_arc_horizontal, -100, 1))
    #r_outline_t4_a1.append([250,0,0])
    return(r_outline_t4_a1)
  # outline_a
  outline_a1 = cnc_cut_outline(outline_t4_a(0), 'cnc_cut_outline_test4_a1')
  outline_a2 = cnc_cut_outline(outline_t4_a(ai_sw_router_bit_radius), 'cnc_cut_outline_test4_a2')
  # print the outline
  #for i_segment in outline_a1:
  #  print("dbg331: outline_a1 i_segment:", len(i_segment), i_segment)
  #for i_segment in outline_a2:
  #  print("dbg332: outline_a2 i_segment:", len(i_segment), i_segment)

  # display with Tkinter
  tk_root = Tkinter.Tk()
  my_canvas = outline_backends.Two_Canvas(tk_root)
  # callback function for display_backend
  def sub_canvas_graphics_t4(ai_rotation_direction, ai_angle_position):
    r_canvas_graphics = []
    r_canvas_graphics.append(('graphic_lines', outline_backends.outline_arc_line(outline_a1, 'tkinter'), 'red', 1))
    r_canvas_graphics.append(('overlay_lines', outline_backends.outline_arc_line(outline_a2, 'tkinter'), 'green', 2))
    return(r_canvas_graphics)
  # end of callback function
  my_canvas.add_canvas_graphic_function(sub_canvas_graphics_t4)
  tk_root.mainloop()
  # end of display with Tkinter
  r_test = 1
  return(r_test)

def cnc_cut_outline_test5(ai_sw_router_bit_radius):
  """ Fifth test suggests small curves, useful to develop smooth_curve()
      It displays the shapes with Tkinter
  """
  radian_precision = math.pi/100
  print("Run test_5  with ai_sw_router_bit_radius={:0.2f} ...".format(ai_sw_router_bit_radius))
  first_curve=[
    [20,0],
    [22,10],
    [25,20],
    [32,30],
    [35,40],
    [36,50],
    [36,60]]
  # outline_a
  outline_b1 = first_curve
  #outline_b2 = smooth_outline_b_curve(first_curve, math.pi/2, radian_precision, ai_sw_router_bit_radius, 'cnc_cut_outline_test5_a2')
  outline_b2 = smooth_outline_b_curve(first_curve, radian_precision, ai_sw_router_bit_radius, 'cnc_cut_outline_test5_a2')
  # print the outline
  #for i_segment in outline_a2:
  #  print("dbg332: outline_a2 i_segment:", len(i_segment), i_segment)

  # display with Tkinter
  tk_root = Tkinter.Tk()
  my_canvas = outline_backends.Two_Canvas(tk_root)
  # callback function for display_backend
  def sub_canvas_graphics_t5(ai_rotation_direction, ai_angle_position):
    r_canvas_graphics = []
    r_canvas_graphics.append(('graphic_lines', outline_backends.outline_arc_line(outline_b1, 'tkinter'), 'green', 2))
    r_canvas_graphics.append(('overlay_lines', outline_backends.outline_arc_line(outline_b2, 'tkinter'), 'red', 1))
    return(r_canvas_graphics)
  # end of callback function
  my_canvas.add_canvas_graphic_function(sub_canvas_graphics_t5)
  tk_root.mainloop()
  # end of display with Tkinter
  r_test = 1
  return(r_test)

################################################################
# cnc_cut_outline command line interface
################################################################

def cnc_cut_outline_cli(ai_args=None):
  """ command line interface of cnc_cut_outline.py when it is used in standalone
  """
  cco_parser = argparse.ArgumentParser(description='Run the function cnc_cut_outline() to check it.')
  cco_parser.add_argument('--router_bit_radius','--rr', action='store', type=float, default=1.0, dest='sw_router_bit_radius',
    help="It defines the router_bit radius (R) of the 2.5D cnc. If sets to '0', the corners will be angular. If positive, the corner will smooth with a curve of radius R. If negative, the corner is enlarged to let the router_bit of radius R to go up to the corner. Note that you can set a value equal or bigger to your actual cnc router_bit radius.")
  cco_parser.add_argument('--height', action='store', type=float, default=1.0, dest='sw_height',
    help='It defines the height of the extrusion along the Z axis.')
  cco_parser.add_argument('--output_file_base','--ofb', action='store', default="", dest='sw_output_file_base',
    help='It defines the base name of the output file. If it is set to the empty string (which is the default value), no output files are generated')
  cco_parser.add_argument('--test1','--t1', action='store_true', default=False, dest='sw_test1',
    help='It generates a bunch of shapes, that you should observed afterward.')
  cco_parser.add_argument('--test2','--t2', action='store_true', default=False, dest='sw_test2',
    help='It generates a bunch of shapes, that you should observed afterward.')
  cco_parser.add_argument('--test3','--t3', action='store_true', default=False, dest='sw_test3',
    help='It generates a bunch of shapes, that are displayed with Tkinter.')
  cco_parser.add_argument('--test4','--t4', action='store_true', default=False, dest='sw_test4',
    help='Small shapes for development, that are displayed with Tkinter.')
  cco_parser.add_argument('--test5','--t5', action='store_true', default=False, dest='sw_test5',
    help='Small shapes to development smooth_curve, that are displayed with Tkinter.')
  effective_args = design_help.get_effective_args(ai_args)
  cco_args = cco_parser.parse_args(effective_args)
  print("dbg111: start testing cnc_cut_outline.py")
  if(cco_args.sw_test1):
    cnc_cut_outline_test1()
  if(cco_args.sw_test2):
    cnc_cut_outline_test2(cco_args.sw_output_file_base, cco_args.sw_router_bit_radius, cco_args.sw_height)
  if(cco_args.sw_test3):
    cnc_cut_outline_test3(cco_args.sw_router_bit_radius)
  if(cco_args.sw_test4):
    cnc_cut_outline_test4(cco_args.sw_router_bit_radius)
  if(cco_args.sw_test5):
    cnc_cut_outline_test5(cco_args.sw_router_bit_radius)
  print("dbg999: end of script")
  
    

################################################################
# main
################################################################

# with freecad, the script is also main :)
if __name__ == "__main__":
  #FreeCAD.Console.PrintMessage("dbg109: I'm main\n")
  #cnc_cut_outline_cli()
  #cnc_cut_outline_cli("--test1".split())
  #cnc_cut_outline_cli("--test2".split())
  #cnc_cut_outline_cli("--test1 --test2".split())
  #cnc_cut_outline_cli("--test3".split())
  cnc_cut_outline_cli("--test3 --router_bit_radius=2".split()) # --router_bit_radius=2 > no warning ; --router_bit_radius=3 > backends warnings
  #cnc_cut_outline_cli("--test4 --router_bit_radius=-3".split())
  #cnc_cut_outline_cli("--test5 --router_bit_radius=3".split())
  #make_H_shape(1.0,2.0,'')


