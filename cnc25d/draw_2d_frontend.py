# draw_2d_frontend.py
# functions for design scripts
# created by charlyoleg on 2014/03/04
#
# (C) Copyright 2014 charlyoleg
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
draw_2d_frontend.py is part of the Cnc25D API.
it provides functions that generate 2d-figures to fill-up the bare_design 2d-construction function.
draw_2d_frontend and design_frontend complete the bare_design class.
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

#import importing_freecad
#importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

# Python standard library
import math
import sys
import re
#import argparse
#from datetime import datetime
#import os, errno
## cnc25d
import small_geometry
#import outline_backends
#import export_2d

################################################################
# function and class to construct figures and outlines
################################################################

def get_center(CX=0.0, CY=0.0, C=()):
  """ select between the argument CX,XY or C
  """
  OCX = CX
  OCY = CY
  if(len(C)>0):
    if((CX!=0)or(CY!=0)):
      print("ERR112: Error, CX {:0.3f} or CY {:0.3d} have been set simultaneously with C".format(CX, CY))
      sys.exit(2)
    if(len(C)!=2):
      print("ERR115: len(C) {:d} is not 2".format(len(C)))
      sys.exit(2)
    OCX = C[0]
    OCY = C[1]
  r = (OCX, OCY)
  return(r)

def c_xy(d, a, CX=0.0, CY=0.0, C=()):
  """
  Compute the Cartesian coordinates (X,Y) of the point of polar coordinate (distance d, angle a, origin-center (X,Y) or C)
  If the 2-tuple C is not empty, it is used as origin-center
  """
  # check distance
  if(d<0):
    print("ERR104: Error, the polar coordinate distance d {:0.3f} is negative".format(d))
    sys.exit(2)
  # origin-center
  (OCX, OCY) = get_center(CX, CY, C)
  # conversion polar to Cartesian coordinates
  X = OCX + d * math.cos(a)
  Y = OCY + d * math.sin(a)
  r = (X, Y)
  return(r)

def min_w_init(ai_old, ai_new):
  """ minimum with initialization
      this help function assumes that the initial value of the global_min is 0
      that's why 0 is a special case
  """
  global_min = ai_old
  if(global_min==0):
    global_min = ai_new
  global_min = min(global_min, ai_new)
  return(global_min)

def max_w_init(ai_old, ai_new):
  """ maximum with initialization
      this help function assumes that the initial value of the global_max is 0
      that's why 0 is a special case
  """
  global_max = ai_old
  if(global_max==0):
    global_max = ai_new
  global_max = max(global_max, ai_new)
  return(global_max)

class Arc_Line_Outline:
  """
  Construct a valid cnc25d format-A outline composed of lines and arcs (general case)
  """

  def __init__(self, outline_id):
    """
    Create a new outline composed of lines and arcs
    outline_id is used by the debug and error messages
    """
    self.outline_id = outline_id
    self.ol = []

  def add_StartPoint(self, CX=0.0, CY=0.0, C=(), rbr=0.0):
    """
    Create the start point. This method must be used before adding any other segments.
    rbr is the router_bit_radius to be applied on the StartPoint corner.
    """
    if(self.ol!=[]):
      print("ERR152: Error, StartPoint can not be added to the outline {:s} with {:d} segments".format(self.outline_id, len(self.ol)))
      sys.exit(2)
    (X, Y) = get_center(CX, CY, C)
    self.ol.append((X, Y, rbr))

  def add_LineTo(self, CX=0.0, CY=0.0, C=(), rbr=0.0):
    """
    Create a new line-segment from the last point to the new point.
    rbr is the router_bit_radius to be applied on the new point corner.
    """
    if(len(self.ol)<1):
      print("ERR163: Error, line-segment can not be added to the outline {:s} with {:d} segments. Add StartPoint first.".format(self.outline_id, len(self.ol)))
      sys.exit(2)
    (X, Y) = get_center(CX, CY, C)
    self.ol.append((X, Y, rbr))
    
  def add_ArcThrTo(self, CX1=0.0, CY1=0.0, CX2=0.0, CY2=0.0, C1=(), C2=(), rbr=0.0):
    """
    Create a new arc-segment from the last point, passing through CX1,CY1 to CX2,CY2.
    rbr is the router_bit_radius to be applied on the CX2,CY2 corner.
    """
    if(len(self.ol)<1):
      print("ERR174: Error, arc-segment can not be added to the outline {:s} with {:d} segments. Add StartPoint first.".format(self.outline_id, len(self.ol)))
      sys.exit(2)
    (X1, Y1) = get_center(CX1, CY1, C1)
    (X2, Y2) = get_center(CX2, CY2, C2)
    self.ol.append((X1, Y1, X2, Y2, rbr))
    
  def add_ArcThrTo_radius_angles(self, R, a1, a2, CX=0.0, CY=0.0, C=(), rbr=0.0):
    """
    Create a new arc-segment of center CX,CY, radius R, from the last point, passing through angle a1 and ending at angle a2.
    rbr is the router_bit_radius to be applied on the CX2,CY2 corner.
    """
    if(len(self.ol)<1):
      print("ERR174: Error, arc-segment can not be added to the outline {:s} with {:d} segments. Add StartPoint first.".format(self.outline_id, len(self.ol)))
      sys.exit(2)
    (X1, Y1) = c_xy(R, a1, CX, CY, C)
    (X2, Y2) = c_xy(R, a2, CX, CY, C)
    self.ol.append((X1, Y1, X2, Y2, rbr))
    
  def close_with_Line(self):
    """
    Close the outline with a line-segment
    """
    if(len(self.ol)<2):
      print("ERR157: Error, line-segment can not be added to close the outline {:s} with {:d} segments. Add at least one segment first.".format(self.outline_id, len(self.ol)))
      sys.exit(2)
    X = self.ol[0][0]
    Y = self.ol[0][1]
    self.ol.append((X, Y, 0)) # last point rbr must be 0

  def close_with_ArcThr(self, CX1=0.0, CY1=0.0, C1=()):
    """
    Close the outline with an arc-segment
    """
    if(len(self.ol)<2):
      print("ERR168: Error, arc-segment can not be added to close the outline {:s} with {:d} segments. Add at least one segment first.".format(self.outline_id, len(self.ol)))
      sys.exit(2)
    (X1, Y1) = get_center(CX1, CY1, C1)
    X2 = self.ol[0][0]
    Y2 = self.ol[0][1]
    self.ol.append((X1, Y1, X2, Y2, 0)) # last point rbr must be 0

  def check(self, figure_id=""):
    """ Check the consistence of the outline for being integrated in a figure
    """
    # length precision
    radian_epsilon = math.pi/1000
    #
    if(len(self.ol)<2):
      print("ERR179: Error, figure {:s}, outline {:s} with {:d} segments is too short. Add at leat two segment first.".format(figure_id, self.outline_id, len(self.ol)))
      sys.exit(2)
    if((self.ol[0][0]!=self.ol[-1][-3])or(self.ol[0][1]!=self.ol[-1][-2])):
      print("ERR182: Error, figure {:s}, outline {:s} is not closed: first point ({:0.3f}, {:0.3f}), last point ({:0.3f}, {:0.3f})".format(figure_id, self.outline_id, self.ol[0][0], self.ol[0][1], self.ol[-1][-3], self.ol[-1][-2]))
      sys.exit(2)
    if(self.ol[-1][-1]!=0):
      print("ERR185: Error, figure {:s}, outline {:s}, last point router_bit_radius {:0.3f} is not 0.0".format(figure_id, self.outline_id, self.ol[-1][-1]))
      sys.exit(2)
    # compute statistics on the outline
    stat = {}
    stat['pt_nb'] = 0
    stat['string_length_min'] = 0 # direct length between to consecutive points
    stat['string_length_max'] = 0
    stat['string_length_total'] = 0
    stat['segment_length_min'] = 0 # real outline length
    stat['segment_length_max'] = 0
    stat['segment_length_total'] = 0
    stat['arc_length_min'] = 0 # outline length just counting arcs
    stat['arc_length_max'] = 0
    stat['arc_length_total'] = 0
    stat['arc_radius_min'] = 0
    stat['arc_radius_max'] = 0
    stat['line_length_min'] = 0 # outline length just counting lines
    stat['line_length_max'] = 0
    stat['line_length_total'] = 0
    stat['arc_nb'] = 0
    stat['line_nb'] = 0
    stat['corner_nb'] = 0
    stat['positive_rbr_nb'] = 0
    stat['positive_rbr_max'] = 0
    stat['positive_rbr_min'] = 0
    stat['zero_rbr_nb'] = 0
    stat['negative_rbr_nb'] = 0
    stat['negative_rbr_max'] = 0
    stat['negative_rbr_min'] = 0
    # start point
    stat['x_min'] = self.ol[0][0]
    stat['x_max'] = self.ol[0][0]
    stat['y_min'] = self.ol[0][1]
    stat['y_max'] = self.ol[0][1]
    last_rbr = self.ol[0][-1]
    # segments
    for i in range(len(self.ol)-1):
      stat['corner_nb'] += 1
      # last_rbr
      if(last_rbr>0):
        stat['positive_rbr_nb'] += 1
        stat['positive_rbr_max'] = max_w_init(stat['positive_rbr_max'], last_rbr)
        stat['positive_rbr_min'] = min_w_init(stat['positive_rbr_min'], last_rbr)
      elif(last_rbr==0):
        stat['zero_rbr_nb'] += 1
      else:
        stat['negative_rbr_nb'] += 1
        stat['negative_rbr_max'] = max_w_init(stat['negative_rbr_max'], last_rbr)
        stat['negative_rbr_min'] = min_w_init(stat['negative_rbr_min'], last_rbr)
      last_rbr = self.ol[i+1][-1]
      # segment
      if(len(self.ol[i+1])==3):
        segment_line_narc = True
        stat['pt_nb'] += 1
        stat['line_nb'] += 1
        pt1_distance = math.sqrt((self.ol[i+1][0]-self.ol[i][-3])**2+(self.ol[i+1][1]-self.ol[i][-2])**2)
        pt2_distance = 0
        string_length = pt1_distance
        segment_length = pt1_distance
        stat['x_min'] = min(stat['x_min'], self.ol[i+1][0])
        stat['x_max'] = max(stat['x_max'], self.ol[i+1][0])
        stat['y_min'] = min(stat['y_min'], self.ol[i+1][1])
        stat['y_max'] = max(stat['y_max'], self.ol[i+1][1])
      elif(len(self.ol[i+1])==5):
        segment_line_narc = False
        stat['pt_nb'] += 2
        stat['arc_nb'] += 1
        pt1_distance = math.sqrt((self.ol[i+1][0]-self.ol[i][-3])**2+(self.ol[i+1][1]-self.ol[i][-2])**2)
        pt2_distance = math.sqrt((self.ol[i+1][2]-self.ol[i+1][0])**2+(self.ol[i+1][3]-self.ol[i+1][1])**2)
        string_length = pt1_distance + pt2_distance
        (IX, IY, arc_radius, uw, u, w) = small_geometry.arc_center_radius_angles((self.ol[i][-3], self.ol[i][-2]), (self.ol[i+1][0], self.ol[i+1][1]), (self.ol[i+1][2], self.ol[i+1][3]), "outline_{:s}_segment_{:d}_check".format(self.outline_id, i+1))
        segment_length = arc_radius*abs(uw)
        stat['x_min'] = min(stat['x_min'], self.ol[i+1][0], self.ol[i+1][2])
        stat['x_max'] = max(stat['x_max'], self.ol[i+1][0], self.ol[i+1][2])
        stat['y_min'] = min(stat['y_min'], self.ol[i+1][1], self.ol[i+1][3])
        stat['y_max'] = max(stat['y_max'], self.ol[i+1][1], self.ol[i+1][3])
      else:
        print("ERR244: Error, figure_id {:s}, outline {:s}, segment {:d} unexpected length {:d}".format(figure_id, self.outline_id, i+1, len(self.ol[i+1])))
        sys.exit(2)
      if(pt1_distance<radian_epsilon):
        print("ERR258: Error, figure_id {:s}, outline {:s}, segment {:d} pt1_distance {:0.3f} too small".format(figure_id, self.outline_id, i+1, pt1_distance))
        sys.exit(2)
      if((pt2_distance<radian_epsilon) and not(segment_line_narc)):
        print("ERR261: Error, figure_id {:s}, outline {:s}, segment {:d} pt2_distance {:0.3f} too small".format(figure_id, self.outline_id, i+1, pt2_distance))
        sys.exit(2)
      # string_length
      stat['string_length_min'] = min_w_init(stat['string_length_min'], string_length)
      stat['string_length_max'] = max_w_init(stat['string_length_max'], string_length)
      stat['string_length_total'] += string_length
      # segment_length
      stat['segment_length_min'] = min_w_init(stat['segment_length_min'], segment_length)
      stat['segment_length_max'] = max_w_init(stat['segment_length_max'], segment_length)
      stat['segment_length_total'] += segment_length
      # line_length
      if(segment_line_narc): # line-segment
        # line_length
        stat['line_length_min'] = min_w_init(stat['line_length_min'], segment_length)
        stat['line_length_max'] = max_w_init(stat['line_length_max'], segment_length)
        stat['line_length_total'] += segment_length
      else: # arc-segment
        # arc_length
        stat['arc_length_min'] = min_w_init(stat['arc_length_min'], segment_length)
        stat['arc_length_max'] = max_w_init(stat['arc_length_max'], segment_length)
        stat['arc_length_total'] += segment_length
        # arc_radius
        stat['arc_radius_min'] = min_w_init(stat['arc_radius_min'], arc_radius)
        stat['arc_radius_max'] = max_w_init(stat['arc_radius_max'], arc_radius)
    # return
    return(stat)

  def stat_info(self, context_msg=""):
    """ statistics information on the arc_line_outline
    """
    r_txt = "In context {:s}, Arc_Line_Outline {:s} statistics information:".format(context_msg, self.outline_id)
    ol_stat = self.check(context_msg)
    r_txt += """
pt_nb:                {:d}
string_length_min:    {:0.3f}
string_length_max:    {:0.3f}
string_length_total:  {:0.3f}
segment_length_min:   {:0.3f}
segment_length_max:   {:0.3f}
segment_length_total: {:0.3f}
""".format(ol_stat['pt_nb'], ol_stat['string_length_min'], ol_stat['string_length_max'], ol_stat['string_length_total'], ol_stat['segment_length_min'], ol_stat['segment_length_max'], ol_stat['segment_length_total'])
    r_txt += """
arc_length_min:       {:0.3f}
arc_length_max:       {:0.3f}
arc_length_total:     {:0.3f}
arc_radius_min:       {:0.3f}
arc_radius_max:       {:0.3f}
line_length_min:      {:0.3f}
line_length_max:      {:0.3f}
line_length_total:    {:0.3f}
arc_nb:               {:d}
line_nb:              {:d}
""".format(ol_stat['arc_length_min'], ol_stat['arc_length_max'], ol_stat['arc_length_total'], ol_stat['arc_radius_min'], ol_stat['arc_radius_max'], ol_stat['line_length_min'], ol_stat['line_length_max'], ol_stat['line_length_total'], ol_stat['arc_nb'], ol_stat['line_nb'])
    r_txt += """
corner_nb:            {:d}
positive_rbr_nb:      {:d}
positive_rbr_min:     {:0.3f}
positive_rbr_max:     {:0.3f}
zero_rbr_nb:          {:d}
negative_rbr_nb:      {:d}
negative_rbr_min:     {:0.3f}
negative_rbr_max:     {:0.3f}
""".format(ol_stat['corner_nb'], ol_stat['positive_rbr_nb'], ol_stat['positive_rbr_min'], ol_stat['positive_rbr_max'], ol_stat['zero_rbr_nb'], ol_stat['negative_rbr_nb'], ol_stat['negative_rbr_min'], ol_stat['negative_rbr_max'])
    r_txt += """
x_min:    {:0.3f}
x_max:    {:0.3f}
y_min:    {:0.3f}
y_max:    {:0.3f}
x_length: {:0.3f}
y_length: {:0.3f}
""".format(ol_stat['x_min'], ol_stat['x_max'], ol_stat['y_min'], ol_stat['y_max'], ol_stat['x_max']-ol_stat['x_min'], ol_stat['y_max']-ol_stat['y_min'])
    return(r_txt)
  
  def convert_to_old_format(self):
    """ convert the Arc_Line_Outline object to the old-list-format
        this function should be only used during the transistion to the new format (Arc_Line_Outline object)
    """
    r_list = self.ol
    return(r_list)

  def convert_from_old_format(self, ai_outline):
    """ convert the old-list-format to the Arc_Line_Outline object
        this function should be only used during the transistion to the new format (Arc_Line_Outline object)
    """
    if(len(ai_outline)<3):
      print("ERR378: Error, outline {:s}, convert_from_old_format failed because import list {:d} is too short".format(self.outline_id, len(ai_outline)))
      sys.exit(2)
    first_segment = ai_outline[0]
    if(len(first_segment)!=3):
      print("ERR381: Error, outline {:s}, convert_from_old_format failed because import first point length {:d} is not 3".format(self.outline_id, len(first_segment)))
      sys.exit(2)
    self.add_StartPoint(first_segment[0], first_segment[1], rbr=first_segment[2])
    for i in range(len(ai_outline)-2):
      segment = ai_outline[i+1]
      if(len(segment)==3):
        self.add_LineTo(segment[0], segment[1], rbr=segment[2])
      elif(len(segment)==5):
        self.add_ArcThrTo(segment[0], segment[1], segment[2], segment[3], rbr=segment[4])
      else:
        print("ERR390: Error, outline {:s}, convert_from_old_format failed because segment length {:d} is not 3 or 5".format(self.outline_id, len(segment)))
        sys.exit(2)
    last_segment = ai_outline[-1]
    if(last_segment[-1]!=0):
      print("ERR395: Error, outline {:s}, convert_from_old_format failed because import last_point rbr {:0.3f} is not 0.0".format(self.outline_id, last_segment[-1]))
      sys.exit(2)
    if((last_segment[-3]!=first_segment[0])or(last_segment[-2]!=first_segment[1])):
      print("ERR399: Error, outline {:s}, convert_from_old_format failed because import is not closed x {:0.3f} {:0.3f} y {:0.3f} {:0.3f}".format(self.outline_id, first_segment[0], last_segment[-3], first_segment[1], last_segment[-2]))
      sys.exit(2)
    if(len(last_segment)==3):
      self.close_with_Line()
    elif(len(last_segment)==5):
      self.close_with_ArcThr(last_segment[0], last_segment[1])
    else:
      print("ERR406: Error, outline {:s}, convert_from_old_format failed because last_segment length {:d} is not 3 or 5".format(self.outline_id, len(last_segment)))
      sys.exit(2)



class Circle_Outline:
  """
  Construct a valid cnc25d format-A circle outline
  """

  def __init__(self, outline_id, R, CX=0.0, CY=0.0, C=()):
    """
    Define a circle of radius R (must be strictly positive), and center (X,Y).
    The center is defined by the 2-tuple C if it is not empty.
    outline_id is used by the debug and error messages
    """
    # check arguments
    if(R<0):
      print("ERR151: Error, the radius R {:0.3f} is negative".format(R))
      sys.exit(2)
    (X, Y) = get_center(CX, CY, C)
    # save values
    self.outline_id = outline_id
    self.radius = R
    self.x = X
    self.y = Y

  def check(self, figure_id=""):
    """ Check the consistence of the circle for being integrated in a figure
    """
    # length precision
    radian_epsilon = math.pi/1000
    #
    if(self.radius<radian_epsilon):
      print("ERR361: Error, figure {:s}, circle {:s} with radius {:.3f} too small".format(figure_id, self.outline_id, self.radius))
      sys.exit(2)
    circumference = self.radius*2*math.pi
    #
    stat = {}
    stat['circle_radius'] = self.radius
    stat['circle_circumference'] = circumference
    stat['x_min'] = self.x - self.radius
    stat['x_max'] = self.x + self.radius
    stat['y_min'] = self.y - self.radius
    stat['y_max'] = self.y + self.radius
    # return
    return(stat)

  def stat_info(self, context_msg=""):
    """ statistics information on the circle_outline
    """
    r_txt = "In context {:s}, Circle_Outline {:s} statistics information:".format(context_msg, self.outline_id)
    ol_stat = self.check(context_msg)
    r_txt += """
circle_radius:  {:0.3f}  diameter: {:0.3f}
center: x {:0.3f}  y {:0.3f}
circle_circumference: {:0.3f}
x_min:  {:0.3f}
x_max:  {:0.3f}
y_min:  {:0.3f}
y_max:  {:0.3f}
""".format(self.radius, 2*self.radius, self.x, self.y, ol_stat['circle_circumference'], ol_stat['x_min'], ol_stat['x_max'], ol_stat['y_min'], ol_stat['y_max'])
    return(r_txt)

  def convert_to_old_format(self):
    """ convert the Circle_Outline object to the old-list-format
        this function should be only used during the transistion to the new format (Circle_Outline object)
    """
    r_list = (self.x, self.y, self.radius)
    return(r_list)

  def convert_from_old_format(self, ai_outline):
    """ convert the old-list-format to the Circle_Outline object
        this function should be only used during the transistion to the new format (Circle_Outline object)
    """
    if(len(ai_outline)!=3):
      print("ERR483: Error, outline {:s}, convert_from_old_format failed because import list {:d} is not 3".format(self.outline_id, len(ai_outline)))
      sys.exit(2)
    self.x = ai_outline[0]
    self.y = ai_outline[1]
    self.radius = ai_outline[2]

class Figure:
  """
  Construct a valid cnc25d format-A figure out of arc_line_outline and circle_outline objects
  """

  def __init__(self, figure_id):
    """
    Create a new figure. 
    figure_id is used by the debug and error messages
    """
    self.figure_id = figure_id
    self.extrudable = False # True if this figure could be extruded i.e. one big external outline containing small hole-outlines
    self.outlines = []
    self.height = 1.0 # height default value for not extrudable figure
    # statistics
    self.stat = {}
    self.stat['arc_line_outline_nb'] = 0
    self.stat['circle_outline_nb'] = 0
    # arc_line_outline
    self.stat['arc_length_min'] = 0 # outline length just counting arcs
    self.stat['arc_length_max'] = 0
    self.stat['arc_length_total'] = 0
    self.stat['arc_radius_min'] = 0
    self.stat['arc_radius_max'] = 0
    self.stat['line_length_min'] = 0 # outline length just counting lines
    self.stat['line_length_max'] = 0
    self.stat['line_length_total'] = 0
    self.stat['arc_nb'] = 0
    self.stat['line_nb'] = 0
    self.stat['corner_nb'] = 0
    self.stat['positive_rbr_nb'] = 0
    self.stat['positive_rbr_max'] = 0
    self.stat['positive_rbr_min'] = 0
    self.stat['zero_rbr_nb'] = 0
    self.stat['negative_rbr_nb'] = 0
    self.stat['negative_rbr_max'] = 0
    self.stat['negative_rbr_min'] = 0
    # circle_outline
    self.stat['circle_radius_min'] = 0
    self.stat['circle_radius_max'] = 0
    self.stat['circle_radius_total'] = 0
    # size
    self.stat['x_min'] = 0
    self.stat['x_max'] = 0
    self.stat['y_min'] = 0
    self.stat['y_max'] = 0

  def _add_outline(self, outline, hole_check=False):
    """ private function. add a arc-line-outline or a circle outline and update the figure stats
    """
    self.outlines.append(outline)
    ol_stat = outline.check(self.figure_id)
    if(hole_check):
      if((self.stat['x_min']>ol_stat['x_min'])or(self.stat['x_max']<ol_stat['x_max'])or(self.stat['y_min']>ol_stat['y_min'])or(self.stat['y_max']<ol_stat['y_max'])):
        print("ERR417: Error, figure {:s}, hole-ouline {:s} outside the boundary: x_min {:0.3f} {:0.3f}, x_max {:0.3f} {:0.3f}, y_min {:0.3f} {:0.3f}, y_max {:0.3f} {:0.3f}".format(self.figure_id, outline.outline_id, self.stat['x_min'], ol_stat['x_min'], self.stat['x_max'], ol_stat['x_max'], self.stat['y_min'], ol_stat['y_min'], self.stat['y_max'], ol_stat['y_max']))
        sys.exit(2)
    self.stat['x_min'] = min_w_init(self.stat['x_min'], ol_stat['x_min'])
    self.stat['x_max'] = max_w_init(self.stat['x_max'], ol_stat['x_max'])
    self.stat['y_min'] = min_w_init(self.stat['y_min'], ol_stat['y_min'])
    self.stat['y_max'] = max_w_init(self.stat['y_max'], ol_stat['y_max'])
    if(isinstance(outline, Circle_Outline)):
      self.stat['circle_outline_nb'] += 1
      self.stat['circle_radius_min'] = min_w_init(self.stat['circle_radius_min'], ol_stat['circle_radius'])
      self.stat['circle_radius_max'] = max_w_init(self.stat['circle_radius_max'], ol_stat['circle_radius'])
      self.stat['circle_radius_total'] += ol_stat['circle_radius']
    elif(isinstance(outline, Arc_Line_Outline)):
      self.stat['arc_line_outline_nb'] += 1
      self.stat['arc_length_min'] = min_w_init(self.stat['arc_length_min'], ol_stat['arc_length_min'])
      self.stat['arc_length_max'] = max_w_init(self.stat['arc_length_max'], ol_stat['arc_length_max'])
      self.stat['arc_length_total'] += ol_stat['arc_length_total']
      self.stat['arc_radius_min'] = min_w_init(self.stat['arc_radius_min'], ol_stat['arc_radius_min'])
      self.stat['arc_radius_max'] = max_w_init(self.stat['arc_radius_max'], ol_stat['arc_radius_max'])
      self.stat['line_length_min'] = min_w_init(self.stat['line_length_min'], ol_stat['line_length_min'])
      self.stat['line_length_max'] = max_w_init(self.stat['line_length_max'], ol_stat['line_length_max'])
      self.stat['line_length_total'] += ol_stat['line_length_total']
      self.stat['arc_nb'] += ol_stat['arc_nb']
      self.stat['line_nb'] += ol_stat['line_nb']
      self.stat['corner_nb'] += ol_stat['corner_nb']
      self.stat['positive_rbr_nb'] += ol_stat['positive_rbr_nb']
      self.stat['positive_rbr_max'] = max_w_init(self.stat['positive_rbr_max'], ol_stat['positive_rbr_max'])
      self.stat['positive_rbr_min'] = max_w_init(self.stat['positive_rbr_min'], ol_stat['positive_rbr_min'])
      self.stat['zero_rbr_nb'] += ol_stat['zero_rbr_nb']
      self.stat['negative_rbr_nb'] += ol_stat['negative_rbr_nb']
      self.stat['negative_rbr_max'] = max_w_init(self.stat['negative_rbr_max'], ol_stat['negative_rbr_max'])
      self.stat['negative_rbr_min'] = min_w_init(self.stat['negative_rbr_min'], ol_stat['negative_rbr_min'])
    else:
      print("ERR429: Error, figure {:d}, outline {:s} is an invalid object".format(self.figure_id, outline.outline_id))
      sys.exit(2)

  def add_external_outline(self, outline):
    """ add the first outline a.k.a. the external outline
    """
    self.extrudable = True
    if(len(self.outlines)!=0):
      print("ERR457: Error, figure {:s}, external_outline {:s} not added at the first position {:d}".format(self.figure_id, outline.outline_id, len(self.outlines)))
      sys.exit(2)
    self._add_outline(outline, False)
 
  def add_hole_outline(self, outline):
    """ add a hole-outline
    """
    if(len(self.outlines)==0): # check if there is already an external_outline
      print("ERR465: Error, figure {:s}, hole_outline {:s} added before external_outline".format(self.figure_id, outline.outline_id))
      sys.exit(2)
    if(not self.extrudable): # check no undefine_outline have been added
      print("ERR468: Error, figure {:s}, hole_outline {:s} added to a not extrudable figure {:d}".format(self.figure_id, outline.outline_id, len(self.outlines)))
      sys.exit(2)
    self._add_outline(outline, True)

  def add_undefine_outline(self, outline):
    """ add a undefine outline
    """
    self.extrudable = False
    self._add_outline(outline, False)

  def merge_figure(self, figure):
    """ merge a figure to the current figure
    """
    for i in range(len(figure.outlines)):
      self.add_undefine_outline(figure.outlines[i])

  def set_height(self, ai_height):
    """ set the extrude height of a figure
    """
    self.height = ai_height

  def stat_info(self, context_msg=""):
    """ statistics information on the figure
    """
    r_txt = "In context {:s}, figure {:s} statistics information:".format(context_msg, self.figure_id)
    r_txt += """
extrudable:           {:d}
arc_line_outline_nb:  {:d}
circle_outline_nb:    {:d}
""".format(self.extrudable, self.stat['arc_line_outline_nb'], self.stat['circle_outline_nb'])
    r_txt += """
arc_line_outline:
arc_length_min:     {:0.3f}
arc_length_max:     {:0.3f}
arc_length_total:   {:0.3f}
arc_radius_min:     {:0.3f}
arc_radius_max:     {:0.3f}
line_length_min:    {:0.3f}
line_length_max:    {:0.3f}
line_length_total:  {:0.3f}
arc_nb:             {:d}
line_nb:            {:d}
""".format(self.stat['arc_length_min'], self.stat['arc_length_max'], self.stat['arc_length_total'], self.stat['arc_radius_min'], self.stat['arc_radius_max'], self.stat['line_length_min'], self.stat['line_length_max'], self.stat['line_length_total'], self.stat['arc_nb'], self.stat['corner_nb'])
    r_txt += """
corner_nb:          {:d}
positive_rbr_nb:    {:d}
positive_rbr_min:   {:0.3f}
positive_rbr_max:   {:0.3f}
zero_rbr_nb:        {:d}
negative_rbr_nb:    {:d}
negative_rbr_min:   {:0.3f}
negative_rbr_max:   {:0.3f}
""".format(self.stat['corner_nb'], self.stat['positive_rbr_nb'], self.stat['positive_rbr_min'], self.stat['positive_rbr_max'], self.stat['zero_rbr_nb'], self.stat['negative_rbr_nb'], self.stat['negative_rbr_min'], self.stat['negative_rbr_max'])
    r_txt += """
circle_radius_min:    {:0.3f}
circle_radius_max:    {:0.3f}
circle_radius_total:  {:0.3f}
""".format(self.stat['circle_radius_min'], self.stat['circle_radius_max'], self.stat['circle_radius_total'])
    r_txt += """
x_min:    {:0.3f}
x_max:    {:0.3f}
y_min:    {:0.3f}
y_max:    {:0.3f}
x_length: {:0.3f}
y_length: {:0.3f}
""".format(self.stat['x_min'], self.stat['x_max'], self.stat['y_min'], self.stat['y_max'], self.stat['x_max']-self.stat['x_min'], self.stat['y_max']-self.stat['y_min'])
    r_txt += "outline_nb: {:d}\noutline_list:".format(len(self.outlines))
    for i in range(len(self.outlines)):
      r_txt += "    {:d}: {:s}".format(i, self.outlines[i].outline_id)
    return(r_txt)

  def get_outline_index(self, ai_index):
    """ return the Outline object (Arc_Line or Circle) with the corresponding index in the outline list
    """
    if(abs(ai_index)>=len(self.outlines)):
      print("ERR544: Error, figure {:s}, outline index {:d} is out of the range {:s}".format(self.figure_id, ai_index, len(self.outlines)))
      sys.exit(2)
    r_outline = self.outlines[ai_index]
    return(r_outline)

  def get_outline_id(self, ai_outline_id):
    """ return the Outline object (Arc_Line or Circle) with the corresponding outline_id
        if several outlines have the same outline_id, the last one is returned
    """
    idx = -1
    for i in range(len(self.outlines)):
      if(self.outlines[i].outline_id==ai_outline_id):
        idx = i
    if(idx==-1):
      print("ERR558: Error, figure {:s}, outline_id {:s} does not exist".format(self.figure_id, ai_outline_id))
      sys.exit(2)
    r_outline = self.get_outline_index(idx)
    return(r_outline)

  def convert_to_old_format(self):
    """ convert Figure object to the old-list-format
        this function should be only used during the transistion to the new format (Figure object)
    """
    r_list = []
    for i in range(len(self.outlines)):
      r_list.append(self.outlines[i].convert_to_old_format())
    return(r_list)

  def convert_from_old_format(self, ai_figure):
    """ convert the old-list-format to the Figure object
        this function should be only used during the transistion to the new format (Figure object)
    """
    if(len(ai_figure)<1):
      print("ERR701: Error, figure {:s}, convert_from_old_format failed because import list {:d} is 0".format(self.figure_id, len(ai_figure)))
      sys.exit(2)
    for i in range(len(ai_figure)):
      old_ol = ai_figure[i]
      if(isinstance(old_ol[0], (tuple, list))): # outline is arc-line
        ol = Arc_Line_Outline("undef_ol_arc_line_{:d}".format(i))
        ol.convert_from_old_format(old_ol)
        self.add_undefine_outline(ol)
      else: # outline is a circle
        ol = Circle_Outline("undef_ol_circle_{:d}".format(i), 1.0, 0.0, 0.0) # fictive circle of radius 1.0 and center (0.0,0.0) just for object creation
        ol.convert_from_old_format(old_ol)
        self.add_undefine_outline(ol)


class Figure_Collection:
  """
  Construct a collection of cnc25d format-A figure to be returned by the construction_2d function of the bare_design class
  """

  def __init__(self, collection_id):
    """
    Create a new figure_collection. 
    collection_id is used by the debug and error messages
    """
    self.collection_id = collection_id
    self.figures = []
    # statistics
    self.stat = {}
    self.stat['arc_radius_min'] = 0
    self.stat['arc_radius_max'] = 0
    self.stat['corner_nb'] = 0
    self.stat['positive_rbr_nb'] = 0
    self.stat['positive_rbr_max'] = 0
    self.stat['positive_rbr_min'] = 0
    self.stat['zero_rbr_nb'] = 0
    self.stat['negative_rbr_nb'] = 0
    self.stat['negative_rbr_max'] = 0
    self.stat['negative_rbr_min'] = 0
    self.stat['circle_radius_min'] = 0
    self.stat['circle_radius_max'] = 0
    self.stat['dx_min'] = 0
    self.stat['dx_max'] = 0
    self.stat['dy_min'] = 0
    self.stat['dy_max'] = 0

  def add_figure(self, ai_figure):
    """ add a figure to the collection and update the statistics
    """
    if(not isinstance(ai_figure, Figure)):
      print("ERR525: Error, figure_collection {:s}, add unexpected object {:s}".format(self.collection_id, ai_figure.figure_id))
      sys.exit(2)
    self.figures.append(ai_figure)
    # update statistics
    self.stat['arc_radius_min'] = min_w_init(self.stat['arc_radius_min'], ai_figure.stat['arc_radius_min'])
    self.stat['arc_radius_max'] = max_w_init(self.stat['arc_radius_max'], ai_figure.stat['arc_radius_max'])
    self.stat['corner_nb'] += ai_figure.stat['corner_nb']
    self.stat['positive_rbr_nb'] += ai_figure.stat['positive_rbr_nb']
    self.stat['positive_rbr_max'] = max_w_init(self.stat['positive_rbr_max'], ai_figure.stat['positive_rbr_max'])
    self.stat['positive_rbr_min'] = min_w_init(self.stat['positive_rbr_min'], ai_figure.stat['positive_rbr_min'])
    self.stat['zero_rbr_nb'] += ai_figure.stat['zero_rbr_nb']
    self.stat['negative_rbr_nb'] += ai_figure.stat['negative_rbr_nb']
    self.stat['negative_rbr_max'] = max_w_init(self.stat['negative_rbr_max'], ai_figure.stat['negative_rbr_max'])
    self.stat['negative_rbr_min'] = min_w_init(self.stat['negative_rbr_min'], ai_figure.stat['negative_rbr_min'])
    self.stat['circle_radius_max'] = max_w_init(self.stat['circle_radius_max'], ai_figure.stat['circle_radius_max'])
    self.stat['circle_radius_min'] = min_w_init(self.stat['circle_radius_min'], ai_figure.stat['circle_radius_min'])
    dx = ai_figure.stat['x_max'] - ai_figure.stat['x_min']
    dy = ai_figure.stat['y_max'] - ai_figure.stat['y_min']
    self.stat['dx_min'] = min_w_init(self.stat['dx_min'], dx)
    self.stat['dx_max'] = max_w_init(self.stat['dx_max'], dx)
    self.stat['dy_min'] = min_w_init(self.stat['dy_min'], dy)
    self.stat['dy_max'] = max_w_init(self.stat['dy_max'], dy)

  def stat_info(self, context_msg=""):
    """ statistics information on the figure_collection
    """
    r_txt = "In context {:s}, figure_collection {:s} statistics information:".format(context_msg, self.collection_id)
    r_txt += """
circle_radius_min:  {:0.3f}
circle_radius_max:  {:0.3f}
arc_radius_min:     {:0.3f}
arc_radius_max:     {:0.3f}
""".format(self.stat['circle_radius_min'], self.stat['circle_radius_max'],  self.stat['arc_radius_min'], self.stat['arc_radius_max'])
    r_txt += """
corner_nb:          {:d}
positive_rbr_nb:    {:d}
positive_rbr_min:   {:0.3f}
positive_rbr_max:   {:0.3f}
zero_rbr_nb:        {:d}
negative_rbr_nb:    {:d}
negative_rbr_min:   {:0.3f}
negative_rbr_max:   {:0.3f}
""".format(self.stat['corner_nb'], self.stat['positive_rbr_nb'], self.stat['positive_rbr_min'], self.stat['positive_rbr_max'], self.stat['zero_rbr_nb'], self.stat['negative_rbr_nb'], self.stat['negative_rbr_min'], self.stat['negative_rbr_max'])
    r_txt += """
dx_min:   {:0.3f}
dx_max:   {:0.3f}
dy_min:   {:0.3f}
dy_max:   {:0.3f}
""".format(self.stat['dx_min'], self.stat['dx_max'], self.stat['dy_min'], self.stat['dy_max'])
    r_txt += "figure_nb: {:d}\nfigure_list:".format(len(self.figures))
    for i in range(len(self.figures)):
      r_txt += "    {:d}: {:s}".format(i, self.figures[i].figure_id)
    return(r_txt)

  def get_figure_index(self, ai_index):
    """ return the Figure object with the corresponding index in the figure list
    """
    if(abs(ai_index)>=len(self.figures)):
      print("ERR583: Error, figure_collection {:s}, figure index {:d} is out of the range {:s}".format(self.collection_id, ai_index, len(self.figures)))
      sys.exit(2)
    r_figure = self.figures[ai_index]
    return(r_figure)

  def get_figure_id(self, ai_figure_id):
    """ return the Figure object with the corresponding figure_id
        if several figures have the same figure_id, the last one is returned
    """
    idx = -1
    for i in range(len(self.figures)):
      if(self.figures[i].figure_id==ai_figure_id):
        idx = i
    if(idx==-1):
      print("ERR597: Error, figure_collection {:s}, figure_id {:s} does not exist".format(self.collection_id, ai_figure_id))
      sys.exit(2)
    r_figure = self.get_figure_index(idx)
    return(r_figure)

  def convert_to_old_format(self):
    """ convert Figure_Collection object to the old-dict-format
        this function should be only used during the transistion to the new format (Figure_Collection object)
    """
    r_figures = {}
    r_height = {}
    for i in range(len(self.figures)):
      fig_id = self.figures[i].figure_id
      r_figures[fig_id] = self.figures[i].convert_to_old_format()
      r_height[fig_id] = self.figures[i].height
    r_figure_collection = (r_figures, r_height)
    return(r_figure_collection)

  def convert_from_old_format(self, ai_figure_collection):
    """ convert the old-dict-format to the Figure_Collection object
        this function should be only used during the transistion to the new format (Figure_Collection object)
    """
    (figures, height) = ai_figure_collection
    for k in figures.keys():
      fig = Figure(k)
      fig.convert_from_old_format(figures[k])
      fig.set_height(height[k])
      self.add_figure(fig)
    


################################################################
# test-functions
################################################################
#
# import for test only
import outline_backends
import design_output

def test_c_xy():
  """ test the API function c_xy()
  """
  print("\nTest c_xy()")
  (x,y) = c_xy(5.0, 1.0, 0.0, 0.0)
  print("c_xy 5.0, 1.0, 0, 0 : x {:0.3f} , y {:0.3f}".format(x,y))
  (x,y) = c_xy(3.0, -1.0, 2.0, -1.0)
  print("c_xy 3.0, -1.0, 2, -1.0 : x {:0.3f} , y {:0.3f}".format(x,y))
  (x,y) = c_xy(5.0, 1.0, C=(-2,-3))
  print("c_xy 5.0, 1.0, C=(-2,-3) : x {:0.3f} , y {:0.3f}".format(x,y))

def test_draw_2d_1():
  """ first complete test of the draw_2d
  """
  tfc = Figure_Collection("test_figure_collection")
  fig1 = Figure("first_figure")
  outer_rectangle = Arc_Line_Outline("outer_rectangle")
  outer_rectangle.add_StartPoint(-60, -40, rbr=10)
  outer_rectangle.add_LineTo(60, -40, rbr=5)
  outer_rectangle.add_LineTo(60,  40,  rbr=0)
  outer_rectangle.add_LineTo(-60,  40,  rbr=5)
  outer_rectangle.close_with_Line()
  fig1.add_external_outline(outer_rectangle) 
  inner_shape = Arc_Line_Outline("inner_shape")
  inner_shape.add_StartPoint(0, 0,  rbr=5)
  inner_shape.add_LineTo(40, 0, rbr=-5)
  inner_shape.close_with_ArcThr(20, 30)
  fig1.add_hole_outline(inner_shape)
  inner_circle = Circle_Outline("inner_circle", 15, -30, 0)
  fig1.add_hole_outline(inner_circle)
  tfc.add_figure(fig1)
  fig2 = Figure("second_figure")
  extol = Arc_Line_Outline("extol")
  extol.add_StartPoint(100, 0, rbr=0)
  extol.add_ArcThrTo_radius_angles(20, -math.pi, math.pi/2, 100, 20, rbr=0)
  extol.add_ArcThrTo(110, 40, 100, 50, rbr=0)
  extol.close_with_ArcThr(120, 40)
  fig2.add_external_outline(extol)
  tfc.add_figure(fig2)
  fig3 = Figure("all_figure")
  fig3.merge_figure(fig1)
  fig3.merge_figure(fig2)
  tfc.add_figure(fig3)
  print(tfc.stat_info())
  print(tfc.get_figure_id('first_figure').stat_info("test_figure_collection"))
  print(tfc.get_figure_id('first_figure').get_outline_id('inner_shape').stat_info("test_figure_collection.first_figure"))
  print(tfc.get_figure_id('first_figure').get_outline_id('inner_circle').stat_info("test_figure_collection.first_figure"))
  old_figure_collection = tfc.convert_to_old_format()
  #print("dbg904: old_figure_collection: ", old_figure_collection)
  tfc2 = Figure_Collection("test_figure_collection_reload")
  tfc2.convert_from_old_format(old_figure_collection)
  print(tfc2.stat_info())
  print(tfc2.get_figure_id('first_figure').stat_info("test_figure_collection_reload"))
  b_figure = design_output.cnc_cut_figure(tfc.get_figure_id('first_figure').convert_to_old_format(), "first_figure")
  outline_backends.figure_simple_display(b_figure, (), "test")


def draw_2d_frontend_self_test():
  """ check the design front-end fonctions
  """
  print("Non-regression tests of the draw_2d_frontend module")
  test_c_xy()
  test_draw_2d_1()

################################################################
# main
################################################################

if __name__ == "__main__":
  draw_2d_frontend_self_test()



