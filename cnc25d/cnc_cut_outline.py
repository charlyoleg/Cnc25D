# cnc_cut_outline.py
# a function that converts a polygon into a curve trimable with 2.5D cnc
# created by charlyoleg on 2013/05/13
# license: CC BY SA 3.0

"""
cnc_cut_outline.py provides API functions to design 2.5D parts and create cuboid assembly
"""

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

################################################################
# ******** API function for outline creation ***********
################################################################

def outline_shift_x(ai_outline, ai_x_offset, ai_x_coefficient):
  """For each point of the list, add the x_offset and multiply by x_coefficient to the x coordinate
  """
  r_outline = []
  for p in ai_outline:
    r_outline.append([ai_x_offset+ai_x_coefficient*p[0], p[1], p[2]])
  if(ai_x_coefficient<0):
    r_outline.reverse()
  #print("dbg702: r_outline", r_outline)
  return(r_outline)

def outline_shift_y(ai_outline, ai_y_offset, ai_y_coefficient):
  """For each point of the list, add the y_offset and multiply by y_coefficient to the y coordinate
  """
  r_outline = []
  for p in ai_outline:
    r_outline.append([p[0], ai_y_offset+ai_y_coefficient*p[1], p[2]])
  if(ai_y_coefficient<0):
    r_outline.reverse()
  return(r_outline)

def outline_shift_xy(ai_outline, ai_x_offset, ai_x_coefficient, ai_y_offset, ai_y_coefficient):
  """For each point of the list, add the offset and multiply by coefficient the coordinates
  """
  r_outline = []
  for p in ai_outline:
    r_outline.append([ai_x_offset+ai_x_coefficient*p[0], ai_y_offset+ai_y_coefficient*p[1], p[2]])
  if((ai_x_coefficient*ai_y_coefficient)<0):
    r_outline.reverse()
  return(r_outline)

def cnc_cut_outline(ai_corner_list, ai_error_msg_id):
  """
  This function converts a list of points into a FreeCAD closed wire shape that can be extruded afterward.
  For each input point, you must provide its (X,Y) coordinate and the router_bit radius R.
  If R=0, the point is an angular corner.
  If R>0, the point is smoothed to fit the constraints of a router_bit radius R.
  If R<0, the point is enlarged to fit the constraints of a router_bit radius R.
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  #return Part.Shape
  const_z = 0
  if(len(ai_corner_list)<3):
    print("ERR202: Error in {:s}, the number of corners must be bigger than 2. Currently: {:s}".format(ai_error_msg_id, len(ai_corner_list)))
    #sys.exit(2)
    #return(Part.Shape())
    return([])
  # array initialization
  p2p_length = [0] * len(ai_corner_list)
  corner_angle = [0] * len(ai_corner_list)
  corner_length = [0] * len(ai_corner_list)
  corner_type = [0] * len(ai_corner_list) # 0:angular, 1:smoothed, 2: enlarged with width-angle, 3: enlarged with sharp angle
  #pt_vector = [Base.Vector(0,0,0)] * len(ai_corner_list)
  pt_vector = [(0,0)] * len(ai_corner_list)
  # calculate array
  for pt_idx in range(len(ai_corner_list)):
    # tree points to define a corner
    (pre_pt_x, pre_pt_y, pre_pt_r) = ai_corner_list[pt_idx-2]
    (cur_pt_x, cur_pt_y, cur_pt_r) = ai_corner_list[pt_idx-1]
    (post_pt_x, post_pt_y, post_pt_r) = ai_corner_list[pt_idx]
    # calculate the length between two points
    l_length=math.sqrt((post_pt_x-cur_pt_x)**2+(post_pt_y-cur_pt_y)**2)
    if(l_length==0):
      print("ERR405: l_length is null at point index {:s}.{:d} ({:0.02f}, {:0.02f}) r={:0.02f}".format(ai_error_msg_id, pt_idx, cur_pt_x, cur_pt_y, cur_pt_r))
      print("dbg405: post_pt_x: %0.2f  post_pt_y: %0.2f  post_pt_r: %0.2f"%(post_pt_x, post_pt_y, post_pt_r))
      print("dbg415: pre_pt_x: %0.2f  pre_pt_y: %0.2f  pre_pt_r: %0.2f"%(pre_pt_x, pre_pt_y, pre_pt_r))
      sys.exit(1)
    #print("dbg205: l_length:", l_length)
    p2p_length[pt_idx-1] = l_length
    # calculate the angle of corners
    # first method to calculate the corner angle
    #l_angle1 = abs(math.atan((pre_pt_y-cur_pt_y)/(pre_pt_x-cur_pt_x))-math.atan((post_pt_y-cur_pt_y)/(post_pt_x-cur_pt_x)))
    #print("dbg206: l_angle1:", l_angle1)
    # second method to calculate the corner angle
    l_length_h=math.sqrt((pre_pt_x-cur_pt_x)**2+(pre_pt_y-cur_pt_y)**2)
    if(l_length_h==0):
      print("err406: l_length_h is null at point index %d (%0.2f, %0.2f) r=%0.2f"%(pt_idx, cur_pt_x, cur_pt_y, cur_pt_r))
      sys.exit(1)
    l_length_a=math.sqrt((post_pt_x-pre_pt_x)**2+(post_pt_y-pre_pt_y)**2)
    if(l_length_a==0):
      print("err407: l_length_a is null at point index %d (%0.2f, %0.2f) r=%0.2f"%(pt_idx, cur_pt_x, cur_pt_y, cur_pt_r))
      sys.exit(1)
    l_angle2 = math.acos((l_length_h**2+l_length**2-l_length_a**2)/(2*l_length_h*l_length))
    #print("dbg206: l_angle2:", l_angle2)
    corner_angle[pt_idx-1] = l_angle2
    # corner_length
    l_corner_length = 0
    l_corner_type = 0
    if(l_angle2>math.pi-radian_epsilon):
      l_corner_length = 0
      l_corner_type = 0
    elif(cur_pt_r>0):
      # smoothed corner length
      l_smoothed_corner_length = abs(cur_pt_r)/math.tan(l_angle2/2)
      #print("dbg212: l_smoothed_corner_length:", l_smoothed_corner_length)
      l_corner_length = l_smoothed_corner_length
      l_corner_type = 1
    elif(cur_pt_r<0):
      # enlarged_corner_length
      l_enlarged_corner_length = 2*abs(cur_pt_r)*math.cos(l_angle2/2)
      l_corner_type = 2
      if(l_angle2<math.pi/2-radian_epsilon):
        l_enlarged_corner_length = abs(cur_pt_r)/math.sin(l_angle2/2)
        l_corner_type = 3
      #print("dbg213: l_enlarged_corner_length:", l_enlarged_corner_length)
      l_corner_length = l_enlarged_corner_length
    corner_length[pt_idx-1] = l_corner_length
    corner_type[pt_idx-1] = l_corner_type
    # create freecad vector for each point
    #pt_vector[pt_idx-1] = Base.Vector(cur_pt_x,cur_pt_y,const_z)
    pt_vector[pt_idx-1] = (cur_pt_x,cur_pt_y)
  # check the feasibility and prepare vector list
  pre_vect = []
  post_vect = []
  cur_corner = []
  for corn_idx in range(len(corner_type)):
    pre_vect.append(pt_vector[corn_idx])
    post_vect.append(pt_vector[corn_idx])
    cur_corner.append([])
    if(((corner_length[corn_idx-1]+corner_length[corn_idx-2])>p2p_length[corn_idx-2])
      or ((corner_length[corn_idx]+corner_length[corn_idx-1])>p2p_length[corn_idx-1])):
      print("WARN301: Warning, corner {:s}.{:d} can not be smoothed or enlarged because edges are too short!".format(ai_error_msg_id, corn_idx-1))
      corner_type[corn_idx-1] = 0
      corner_length[corn_idx-1] = 0
  # build corners
  for corn_idx in range(len(corner_type)):
    #print("dbg442: corn_idx:", corn_idx)
    #l_pre_direction = pt_vector[corn_idx-2]-pt_vector[corn_idx-1]
    l_pre_direction = (pt_vector[corn_idx-2][0]-pt_vector[corn_idx-1][0], pt_vector[corn_idx-2][1]-pt_vector[corn_idx-1][1])
    #l_pre_direction_1 = l_pre_direction + Base.Vector(0,0,0) # need to duplicate the vector because the method .multiply() change the vector itself
    #l_pre_direction_2 = l_pre_direction + Base.Vector(0,0,0) 
    #l_pre_direction_3 = l_pre_direction + Base.Vector(0,0,0) 
    #l_pre_direction_4 = l_pre_direction + Base.Vector(0,0,0) 
    #l_post_direction = pt_vector[corn_idx]-pt_vector[corn_idx-1]
    l_post_direction = (pt_vector[corn_idx][0]-pt_vector[corn_idx-1][0], pt_vector[corn_idx][1]-pt_vector[corn_idx-1][1])
    #l_post_direction_1 = l_post_direction + Base.Vector(0,0,0) # need to duplicate the vector because the method .multiply() change the vector itself
    #l_post_direction_2 = l_post_direction + Base.Vector(0,0,0)
    #l_post_direction_3 = l_post_direction + Base.Vector(0,0,0)
    #l_post_direction_4 = l_post_direction + Base.Vector(0,0,0)
    #l_pre_vect = pt_vector[corn_idx-1]+l_pre_direction_1.multiply(corner_length[corn_idx-1]/p2p_length[corn_idx-2])
    m = corner_length[corn_idx-1]/p2p_length[corn_idx-2]
    l_pre_vect = (pt_vector[corn_idx-1][0]+m*l_pre_direction[0], pt_vector[corn_idx-1][1]+m*l_pre_direction[1])
    #l_post_vect = pt_vector[corn_idx-1]+l_post_direction_1.multiply(corner_length[corn_idx-1]/p2p_length[corn_idx-1])
    m = corner_length[corn_idx-1]/p2p_length[corn_idx-1]
    l_post_vect = (pt_vector[corn_idx-1][0]+m*l_post_direction[0], pt_vector[corn_idx-1][1]+m*l_post_direction[1])
    l_3rd_pt = pt_vector[corn_idx-1]
    if(corner_type[corn_idx-1]==0):
      pass
    elif(corner_type[corn_idx-1]==1):
      l_AK = abs(ai_corner_list[corn_idx-1][2])*(1-math.sin(corner_angle[corn_idx-1]/2))/math.sin(corner_angle[corn_idx-1])
      #l_3rd_pt = pt_vector[corn_idx-1] + l_pre_direction_2.multiply(l_AK/p2p_length[corn_idx-2]) + l_post_direction_2.multiply(l_AK/p2p_length[corn_idx-1])
      m1 = l_AK/p2p_length[corn_idx-2]
      m2 = l_AK/p2p_length[corn_idx-1]
      l_3rd_pt = (pt_vector[corn_idx-1][0] + m1*l_pre_direction[0] + m2*l_post_direction[0], pt_vector[corn_idx-1][1] + m1*l_pre_direction[1] + m2*l_post_direction[1])
      pre_vect[corn_idx-1] = l_pre_vect
      post_vect[corn_idx-1] = l_post_vect
      #print("dbg415: type:1, l_pre_vect:", l_pre_vect)
      #print("dbg416: type:1, l_3rd_pt:", l_3rd_pt)
      #print("dbg417: type:1, l_post_vect:", l_post_vect)
      #cur_corner[corn_idx-1] = [Part.Arc(l_pre_vect, l_3rd_pt, l_post_vect)]
      cur_corner[corn_idx-1] = [(l_3rd_pt[0], l_3rd_pt[1], l_post_vect[0], l_post_vect[1])]
      #print("dbg401: l_post_direction:", l_post_direction, l_post_direction_1, l_post_direction_2)
    elif(corner_type[corn_idx-1]==2):
      pre_vect[corn_idx-1] = l_pre_vect
      post_vect[corn_idx-1] = l_post_vect
      #print("dbg425: type:2, l_pre_vect:", l_pre_vect)
      #print("dbg426: type:2, l_3rd_pt:", l_3rd_pt)
      #print("dbg427: type:2, l_post_vect:", l_post_vect)
      #cur_corner[corn_idx-1] = [Part.Arc(l_pre_vect, l_3rd_pt, l_post_vect)]
      cur_corner[corn_idx-1] = [(l_3rd_pt[0], l_3rd_pt[1], l_post_vect[0], l_post_vect[1])]
    elif(corner_type[corn_idx-1]==3):
      l_AR = abs(ai_corner_list[corn_idx-1][2])/(2*math.sin(corner_angle[corn_idx-1]/2))
      l_AV = abs(ai_corner_list[corn_idx-1][2])/(math.cos(corner_angle[corn_idx-1]/2))
      #vec_TK_2 = l_pre_direction_2.multiply(l_AV/p2p_length[corn_idx-2]/2) + l_post_direction_2.multiply(l_AV/p2p_length[corn_idx-1]/2)
      m1 = l_AV/p2p_length[corn_idx-2]/2
      m2 = l_AV/p2p_length[corn_idx-1]/2
      vec_TK_2 = (m1*l_pre_direction[0] + m2*l_post_direction[0], m1*l_pre_direction[1] + m2*l_post_direction[1])
      #l_ppre_vect = pt_vector[corn_idx-1] + l_pre_direction_3.multiply(l_AR/p2p_length[corn_idx-2]) - l_post_direction_3.multiply(l_AR/p2p_length[corn_idx-1]) + vec_TK_2
      m1 = l_AR/p2p_length[corn_idx-2]
      m2 = l_AR/p2p_length[corn_idx-1]
      l_ppre_vect = (pt_vector[corn_idx-1][0] + m1*l_pre_direction[0] - m2*l_post_direction[0] + vec_TK_2[0], pt_vector[corn_idx-1][1] + m1*l_pre_direction[1] - m2*l_post_direction[1] + vec_TK_2[1])
      #l_ppost_vect = pt_vector[corn_idx-1] - l_pre_direction_4.multiply(l_AR/p2p_length[corn_idx-2]) + l_post_direction_4.multiply(l_AR/p2p_length[corn_idx-1]) + vec_TK_2
      m1 = l_AR/p2p_length[corn_idx-2]
      m2 = l_AR/p2p_length[corn_idx-1]
      l_ppost_vect = (pt_vector[corn_idx-1][0] - m1*l_pre_direction[0] + m2*l_post_direction[0] + vec_TK_2[0], pt_vector[corn_idx-1][1] - m1*l_pre_direction[1] + m2*l_post_direction[1] + vec_TK_2[1])
      pre_vect[corn_idx-1] = l_pre_vect
      post_vect[corn_idx-1] = l_post_vect
      #print("dbg435: type:3, l_pre_vect:", l_pre_vect)
      #print("dbg436: type:3, l_ppre_vect:", l_ppre_vect)
      #print("dbg437: type:3, l_3rd_pt:", l_3rd_pt)
      #print("dbg438: type:3, l_ppost_vect:", l_ppost_vect)
      #print("dbg439: type:3, l_post_vect:", l_post_vect)
      #cur_corner[corn_idx-1] = [Part.Line(l_pre_vect, l_ppre_vect), Part.Arc(l_ppre_vect, l_3rd_pt, l_ppost_vect), Part.Line(l_ppost_vect, l_post_vect)]
      cur_corner[corn_idx-1] = [(l_ppre_vect[0], l_ppre_vect[1]),
        (l_3rd_pt[0], l_3rd_pt[1], l_ppost_vect[0], l_ppost_vect[1]),
        (l_post_vect[0], l_post_vect[1])]
      #cur_corner[corn_idx-1] = [Part.Line(l_pre_vect, l_ppre_vect)]
      #cur_corner[corn_idx-1].append(Part.Arc(l_ppre_vect, l_3rd_pt, l_ppost_vect))
      #cur_corner[corn_idx-1].append(Part.Line(l_ppost_vect, l_post_vect))
  # build outline
  l_outline = []
  l_outline.append((post_vect[-1][0], post_vect[-1][1])) # first point of the outline
  for corn_idx in range(len(corner_type)):
    #print("dbg442: post_vect[corn_idx-1]:", post_vect[corn_idx-1])
    #print("dbg443: pre_vect[corn_idx]:", pre_vect[corn_idx])
    #l_outline.append(Part.Line(post_vect[corn_idx-1],pre_vect[corn_idx]))
    l_outline.append((pre_vect[corn_idx][0], pre_vect[corn_idx][1]))
    l_outline.extend(cur_corner[corn_idx])
  #print("dbg210: l_outline:",  l_outline)
  #r_shape = Part.Shape(l_outline)
  #r_shape = l_outline # directly return l_outline
  #print("dbg208: r_shape.Content:",  r_shape.Content)
  #print("dbg209: r_shape.Edges:",  r_shape.Edges)
  #return(r_shape)
  return(l_outline)

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
import outline_backends
#


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
  [xox + 0*ys_xa + 0*ys_xb, xoy + 2*ys_yc + 1*ys_cd, ai_router_bit_r]]
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
  [xox+1*xys_xa+0*xys_xb, xoy+3*xys_yc, 1*ai_router_bit_r]]
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
    y_offset += 100
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
  # this ensure the possible to use the script with python and freecad
  effective_args=ai_args
  if(effective_args==None):
    arg_index_offset=0
    if(sys.argv[0]=='freecad'): # check if the script is used by freecad
      arg_index_offset=1
      if(len(sys.argv)>=2):
        if(sys.argv[1]=='-c'): # check if the script is used by freecad -c
          arg_index_offset=2
    effective_args = sys.argv[arg_index_offset+1:]
  cco_args = cco_parser.parse_args(effective_args)
  print("dbg111: start testing cnc_cut_outline.py")
  if(cco_args.sw_test1):
    cnc_cut_outline_test1()
  if(cco_args.sw_test2):
    cnc_cut_outline_test2(cco_args.sw_output_file_base, cco_args.sw_router_bit_radius, cco_args.sw_height)
  print("dbg999: end of script")
  
    

################################################################
# main
################################################################

# with freecad, the script is also main :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("dbg109: I'm main\n")
  #cnc_cut_outline_cli()
  #cnc_cut_outline_cli("--test1".split())
  cnc_cut_outline_cli("--test2".split())
  #cnc_cut_outline_cli("--test1 --test2".split())
  #make_H_shape(1.0,2.0,'')


