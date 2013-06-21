# outline_backends.py
# common interface to create lines, arcs and circles for the backends freecad, dxfwrite, svgwrite and Tkinter
# created by charlyoleg on 2013/06/21
# license: CC BY SA 3.0

"""
outline_backends.py provides a common API to create lines, arcs and circles with freecad, dxfwrite, svgwrite and Tkinter
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import importing_freecad
importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

import Part
from FreeCAD import Base
import math
import sys, argparse

################################################################
# ******** sub-functions for the API ***********
################################################################

def arc_of_circle(ai_3_points, ai_resolution):
  """ From three points (list of 6 floats) creates a polyline (list of 2*n flaots) representing the arc of circle defined by the three points
      ai_resolution sets the mamximum number of intermediate points to create
  """
  # interpretation of the three points
  ptax = ai_3_points[0]
  ptay = ai_3_points[1]
  ptbx = ai_3_points[2]
  ptby = ai_3_points[3]
  ptcx = ai_3_points[4]
  ptcy = ai_3_points[5]
  # epsilon definiton to be tolerant to calculation imprecision
  epilon = math.pi/1000 # can be used to compare radian and sine
  # check
  if((ptax==ptbx)and(ptay==ptby)):
    print("ERR807: Error, point_A and point_B are identical!")
    sys.exit(2)
  if((ptbx==ptbx)and(ptcy==ptcy)):
    print("ERR808: Error, point_B and point_C are identical!")
    sys.exit(2)
  if((ptax==ptbx)and(ptcy==ptcy)):
    print("ERR809: Error, point_A and point_C are identical!")
    sys.exit(2)
  lab = math.sqrt((ptbx-ptax)**2+(ptby-ptay)**2)
  lbc = math.sqrt((ptcx-ptbx)**2+(ptcy-ptby)**2)
  cos_ab = (ptbx-ptax)/lab
  cos_bc = (ptcx-ptbx)/lbc
  if(abs(cos_ab-cos_bc)<epilon):
    print("ERR810: Error, A, B, C are colinear. Arc can not be created!")
    sys.exit(2)
  # Calculation of M and N
  ptmx = (ptax+ptbx)/2
  ptmy = (ptay+ptby)/2
  ptnx = (ptbx+ptcx)/2
  ptny = (ptby+ptcy)/2
  
  r_polyline = ''
  return(r_polyline)

def outline_arc_line_with_freecad(ai_segments, ai_outline_closed):
  """ Generates the arcs and lines outline with the FreeCAD Part API
  """
  constant_z = 0 # FreeCAD.Part works in 3D. So we fix z=0 and just use the XY surface
  fc_vectors = [Base.Vector(ai_segments[0][0], ai_segments[0][1], constant_z)]
  segment_nb = len(ai_segments)-1
  fc_outline = []
  for i in range(segment_nb):
    segment_type = 'line'
    fc_vectors.append(Base.Vector(ai_segments[i+1][0], ai_segments[i+1][1], constant_z))
    point_start = fc_vectors[-2]
    point_end = fc_vectors[-1]
    if(len(ai_segments[i+1])==4):
      segment_type = 'arc'
      fc_vectors.append(Base.Vector(ai_segments[i+1][2], ai_segments[i+1][3], constant_z))
      point_start = fc_vectors[-3]
      point_mid = fc_vectors[-2]
      point_end = fc_vectors[-1]
    if(i==segment_nb-1):
      #print("dbg306: last segment")
      if(ai_outline_closed):
        #print("dbg307: close")
        point_end = fc_vectors[0]
    #print("dbg563: i: {:d}  segment: {:s}".format(i, segment_type))
    if(segment_type=='line'):
      fc_outline.append(Part.Line(point_start, point_end))
    elif(segment_type=='arc'):
      fc_outline.append(Part.Arc(point_start, point_mid, point_end))
  r_outline = Part.Shape(fc_outline)
  return(r_outline)

def outline_arc_line_with_svgwrite(ai_segments, ai_outline_closed):
  """ Generates the arcs and lines outline with the mozman svgwrite
  """
  
  r_outline = ''
  return(r_outline)

def outline_arc_line_with_dxfwrite(ai_segments, ai_outline_closed):
  """ Generates the arcs and lines outline with the mozman dxfwrite
  """
  
  r_outline = ''
  return(r_outline)

def outline_arc_line_with_tkinter(ai_segments, ai_outline_closed):
  """ Generates the arcs and lines outline with the tkinter
  """
  
  r_outline = ''
  return(r_outline)

################################################################
# ******** outline creation API ***************
################################################################

def outline_arc_line(ai_segments, ai_backend):
  """ Generates the arcs and lines outline according to the selected backend
      Possible backend: freecad, mozman dxfwrite, mozman svgwrite, Tkinter.
      ai_segments is a list of segments (ie line or arc)
      a segment starts from the last point of the previous segment.
      a line is defined by a list of two floats [x-end, y-end]
      an arc is defined by a list of four floats [x-mid, y-mid, x-end, y-end]
      The first element of ai_segments is the starting point, a list of two floats [x-start, y-start]
      If the last point [x-end, y-end] of the last segment is equal to [x-start, y-start] the outline is closed.
  """
  r_outline = ''
  #print("dbg204: len(ai_segments):", len(ai_segments))
  #print("dbg205: ai_backend:", ai_backend)
  # general checks on ai_segments
  if(len(ai_segments)<2):
    print("ERR402: Error, the segment list must contain at least 2 elements. Currently, len(ai_segments) = {:d}".format(len(ai_segments)))
    sys.exit(2)
  if(len(ai_segments[0])!=2):
    print("ERR403: Error, the first element of the segment list must have 2 elements. Currently, len(ai_segments[0]) = {:d}".format(len(ai_segments[0])))
    sys.exit(2)
  for i in range(len(ai_segments)):
    if((len(ai_segments[i])!=2)and(len(ai_segments[i])!=4)):
      print("ERR405: Error, the length of the segment {:d} must be 2 or 4. Currently len(ai_segments[i]) = {:d}".format(i, len(ai_segments[i])))
      sys.exit(2)
  # check if the outline is closed
  outline_closed = False
  if((ai_segments[0][0]==ai_segments[-1][-2])and(ai_segments[0][1]==ai_segments[-1][-1])):
    #print("dbg207: the outline is closed.")
    outline_closed = True
  # select backend
  if(ai_backend=='freecad'):
    r_outline = outline_arc_line_with_freecad(ai_segments, outline_closed)
  elif(ai_backend=='svgwrite'):
    r_outline = outline_arc_line_with_svgwrite(ai_segments, outline_closed)
  elif(ai_backend=='dxfwrite'):
    r_outline = outline_arc_line_with_dxfwrite(ai_segments, outline_closed)
  elif(ai_backend=='tkinter'):
    r_outline = outline_arc_line_with_tkinter(ai_segments, outline_closed)
  return(r_outline)

def outline_circle(ai_center, ai_radius, ai_backend):
  """ Generates a circle according to the selected backend.
      Possible backend: freecad, mozman dxfwrite, mozman svgwrite, Tkinter.
  """
  r_outline = 0
  return(r_outline)

################################################################
# ******** test API ***********
################################################################

def outline_arc_line_test1():
  """ test the function outline_arc_line.
  """
  l_ol1 = [
    [0,0],
    [20,0],
    [20,20],
    [0,20],
    [0,0]]

  l_ol2 = [
    [110,0],
    [120,0],
    [130,0, 130,10],
    [130,20],
    [130,30, 120,30],
    [110,30],
    [100,30, 100,20],
    [100,10],
    [100,0, 110,0]]

  l_ol3 = [
    [210,0],
    [220,0],
    [230,0, 230,10],
    [230,20],
    [230,30, 220,30],
    [210,30],
    [200,30, 200,20],
    [200,10]]
    #[200,0, 210,0]]

  l_ols = [l_ol1, l_ol2, l_ol3]
  #l_ols = [l_ol2]
  # backend freecad
  print("dbg701: test1 backend freecad")
  for i_ol in l_ols:
    r_ol = outline_arc_line(i_ol, 'freecad')
    #Part.show(r_ol)
    l_test_face = Part.Face(Part.Wire(r_ol.Edges))
    r_test_solid = l_test_face.extrude(Base.Vector(0,0,1)) # straight linear extrusion
    Part.show(r_test_solid)
  # backend svgwrite
  print("dbg702: test1 backend svgwrite")
  for i_ol in l_ols:
    r_ol = outline_arc_line(i_ol, 'svgwrite')
  # backend dxfwrite
  print("dbg703: test1 backend dxfwrite")
  for i_ol in l_ols:
    r_ol = outline_arc_line(i_ol, 'dxfwrite')
  # backend tkinter
  print("dbg704: test1 backend tkinter")
  for i_ol in l_ols:
    r_ol = outline_arc_line(i_ol, 'tkinter')

  r_test = 1
  return(r_test)

################################################################
# ******** command line interface ***********
################################################################

def outline_backends_cli():
  """ command line interface to run this script in standalone
  """
  ob_parser = argparse.ArgumentParser(description='Test the outline_backends API.')
  ob_parser.add_argument('--test1','--t1', action='store_true', default=False, dest='sw_test1',
    help='Run outline_arc_line_test1()')
  # this ensure the possible to use the script with python and freecad
  # You can not use argparse and FreeCAD together, so it's actually useless !
  # Running this script, FreeCAD will just use the argparse default values
  arg_index_offset=0
  if(sys.argv[0]=='freecad'): # check if the script is used by freecad
    arg_index_offset=1
    if(len(sys.argv)>=2):
      if(sys.argv[1]=='-c'): # check if the script is used by freecad -c
        arg_index_offset=2
  effective_args = sys.argv[arg_index_offset+1:]
  #print("dbg115: effective_args:", str(effective_args))
  #FreeCAD.Console.PrintMessage("dbg116: effective_args: %s\n"%(str(effective_args)))
  ob_args = ob_parser.parse_args(effective_args)
  r_obc = 0
  print("dbg111: start testing outline_backends")
  if(ob_args.sw_test1):
    r_obc = outline_arc_line_test1()
  print("dbg999: end of script")
  return(r_obc)

################################################################
# main
################################################################

if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("outline_backends.py says hello!\n")
  #outline_backends_cli()
  # when running with freecad:
  outline_arc_line_test1()

