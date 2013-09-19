# display_backend.py
# -*- coding: utf-8 -*-

# creates and displays the two Tkinter Canvas windows used by outline_backends.py
# created by charlyoleg on 2013/07/11
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
display_backend.py creates and displays the two Tkinter Canvas windows used by outline_backends.py
"""


################################################################
# import
################################################################

import math
import sys, argparse
import Tkinter
#import tkMessageBox
import matplotlib.pyplot
import design_help # just for get_effective_args()

################################################################
# global variable
################################################################
initial_tkinter_canvas_width = 400
initial_tkinter_canvas_height = 400
tkinter_canvas_margin_x = 20
tkinter_canvas_margin_y = 20
g_fast_angle_speed = 1.0
g_step_angle_speed = float(g_fast_angle_speed)/8
g_slow_angle_speed = float(g_fast_angle_speed)/16
g_step_period = 100 # ms

################################################################
# ******** sub-functions for Two_Canvas ***********
################################################################

def find_outline_extremum(ai_outline_list):
  """ find the four extremum (min_x, min_y, max_x, max_y) of a list of outlines
  """
  # first point
  first_point_x = 0
  first_point_y = 0
  first_outline_type = ai_outline_list[0][0]
  first_outline = ai_outline_list[0][1]
  if((first_outline_type=='graphic_lines')or(first_outline_type=='overlay_lines')):
    first_point_x=first_outline[0][0]
    first_point_y=first_outline[0][1]
  elif((first_outline_type=='graphic_polygon')or(first_outline_type=='overlay_polygon')):
    first_point_x=first_outline[0]
    first_point_y=first_outline[1]
  else:
    print("ERR305: Error, the outline type is unknow: {:s}".format(first_outline_type))
    sys.exit(2)
  min_x=first_point_x
  max_x=first_point_x
  min_y=first_point_y
  max_y=first_point_y
  for outline in ai_outline_list:
    outline_type = outline[0]
    if((outline_type=='graphic_lines')or(outline_type=='overlay_lines')):
      lines = outline[1]
      for line in lines:
        #print("dbg772: line:", line)
        min_x = min(min_x, line[0], line[2])
        max_x = max(max_x, line[0], line[2])
        min_y = min(min_y, line[1], line[3])
        max_y = max(max_y, line[1], line[3])
    elif((outline_type=='graphic_polygon')or(outline_type=='overlay_polygon')):
      points = outline[1]
      for i in range(len(points)/2):
        #print("dbg773: i:", i)
        min_x = min(min_x, points[2*i])
        max_x = max(max_x, points[2*i])
        min_y = min(min_y, points[2*i+1])
        max_y = max(max_y, points[2*i+1])
  r_extremum = (min_x, min_y, max_x, max_y)
  #print("dbg653: r_extremum:", r_extremum)
  return(r_extremum)

def compute_scale_coef(ai_extremum, ai_canvas_size):
  """ compute the four scale coefficient to apply to the outlines to make it fit into a canvas
  """
  (min_x, min_y, max_x, max_y) = ai_extremum
  (canvas_width, canvas_height, margin_x, margin_y) = ai_canvas_size
  r_scale_coef = (1, 0, 1, 0)
  #print("dbg663:", max_x, min_x, max_y, min_y)
  if(((max_x-min_x)>0)and((max_y-min_y)>0)):
    lx = (canvas_width-2*margin_x)/float(max_x-min_x)
    ly = (canvas_height-2*margin_y)/float(max_y-min_y)
    lxy = min(lx, ly)
    # choose lx and ly to get (O,x,y) orthonormal direct
    lx = 1*lxy
    ly = -1*lxy
    #kx = margin_x - min_x*lx
    #ky = margin_y - min_y*ly
    kx = (canvas_width - (max_x-min_x)*lx)/2 - min_x*lx
    #ky = (canvas_height - (max_y-min_y)*ly)/2 - min_y*ly
    ky = (canvas_height - (max_y-min_y)*abs(ly))/2 - max_y*ly
    r_scale_coef = (lx, kx, ly, ky)
  return(r_scale_coef)

def scale_outline(ai_outline_list, ai_coef):
  """ apply the scale coefficient to a list of outlines
  """
  (lx, kx, ly, ky) = ai_coef
  r_outline_list = []
  for outline in ai_outline_list:
    outline_type = outline[0]
    if((outline_type=='graphic_lines')or(outline_type=='overlay_lines')):
      lines = outline[1]
      new_lines = []
      for line in lines:
        new_line = []
        for i in range(len(line)/2):
          new_line.append(line[2*i]*lx+kx)
          new_line.append(line[2*i+1]*ly+ky)
        new_lines.append(tuple(new_line))
      r_outline_list.append((outline_type, tuple(new_lines),  outline[2],  outline[3]))
    elif((outline_type=='graphic_polygon')or(outline_type=='overlay_polygon')):
      points = outline[1]
      new_points = []
      for i in range(len(points)/2):
        new_points.append(points[2*i]*lx+kx)
        new_points.append(points[2*i+1]*ly+ky)
      r_outline_list.append((outline_type, tuple(new_points),  outline[2],  outline[3], outline[4]))
  return(r_outline_list)

def compute_crop_limit(ai_selected_area, ai_canvas_size, ai_scale_coef):
  """ compute the crop four parameters according to the mouse positions, window size and current applied scale coefficient
  """
  (mouse_x1, mouse_y1, mouse_x2, mouse_y2) = ai_selected_area
  (canvas_width, canvas_height, margin_x, margin_y) = ai_canvas_size
  (lx, kx, ly, ky) = ai_scale_coef
  top_left_x = max(0, min(mouse_x1, mouse_x2))
  top_left_y = max(0, min(mouse_y1, mouse_y2))
  bottom_right_x = min(canvas_width, max(mouse_x1, mouse_x2))
  bottom_right_y = min(canvas_height, max(mouse_y1, mouse_y2))
  limit_x1=(top_left_x-kx)/float(lx)
  #limit_y1=(top_left_y-ky)/float(ly)
  limit_y2=(top_left_y-ky)/float(ly)
  limit_x2=(bottom_right_x-kx)/float(lx)
  #limit_y2=(bottom_right_y-ky)/float(ly)
  limit_y1=(bottom_right_y-ky)/float(ly)
  r_crop_limit = (limit_x1, limit_y1, limit_x2, limit_y2)
  return(r_crop_limit)

def crop_outline(ai_outline_list, ai_limit):
  """ crop a list of outlines to get a new list of outlines
  """
  (limit_x1, limit_y1, limit_x2, limit_y2) = ai_limit
  r_outline_list = []
  for outline in ai_outline_list:
    outline_type = outline[0]
    if((outline_type=='graphic_lines')or(outline_type=='overlay_lines')):
      lines = outline[1]
      new_lines = []
      for line in lines:
        include_new_line = 1
        for i in range(len(line)/2):
          if((line[2*i]<limit_x1)
              or (line[2*i]>limit_x2)
              or (line[2*i+1]<limit_y1)
              or (line[2*i+1]>limit_y2)):
            include_new_line = 0
        if(include_new_line==1):
          new_lines.append(line)
      if(len(new_lines)>0):
        r_outline_list.append((outline_type, tuple(new_lines),  outline[2],  outline[3]))
    elif((outline_type=='graphic_polygon')or(outline_type=='overlay_polygon')):
      points = outline[1]
      new_points = []
      for i in range(len(points)/2):
        if((points[2*i]>limit_x1)
            and (points[2*i]<limit_x2)
            and (points[2*i+1]>limit_y1)
            and (points[2*i+1]<limit_y2)):
          new_points.append(points[2*i])
          new_points.append(points[2*i+1])
        else:
          if(len(new_points)>1):
            r_outline_list.append((outline_type, tuple(new_points),  outline[2],  outline[3], outline[4]))
            new_points = []
      if(len(new_points)>1):
        r_outline_list.append((outline_type, tuple(new_points),  outline[2],  outline[3], outline[4]))
  return(r_outline_list)

################################################################
# ******** Two_Canvas class ***********
################################################################


class Two_Canvas():
  """ Tkinter frame work to display a gear system or other simple mechanism
      It contains:
      - a main window with a graphic overview and some button control
      - a zoom window
      - a simple input parameter window
      - a matplotlib window to display curves
  """

  def action_button_fast_backward(self):
    """ widget action
    """
    self.rotation_direction = -1
    self.angle_speed = self.rotation_direction*g_fast_angle_speed
    #self.angle_position += self.angle_speed
    self.set_label_content()

  def action_button_slow_backward(self):
    """ widget action
    """
    self.rotation_direction = -1
    self.angle_speed = self.rotation_direction*g_slow_angle_speed
    #self.angle_position += self.angle_speed
    self.set_label_content()

  def action_button_step_backward(self):
    """ widget action
    """
    self.rotation_direction = -1
    self.angle_speed = 0
    self.angle_position += self.rotation_direction*g_step_angle_speed
    self.set_label_content()

  def action_button_stop(self):
    """ widget action
    """
    #self.rotation_direction = self.rotation_direction
    self.angle_speed = 0
    #self.angle_position += 0
    self.set_label_content()

  def action_button_step_forward(self):
    """ widget action
    """
    self.rotation_direction = 1
    self.angle_speed = 0
    self.angle_position += self.rotation_direction*g_step_angle_speed
    self.set_label_content()

  def action_button_slow_forward(self):
    """ widget action
    """
    self.rotation_direction = 1
    self.angle_speed = self.rotation_direction*g_slow_angle_speed
    #self.angle_position += self.angle_speed
    self.set_label_content()

  def action_button_fast_forward(self):
    """ widget action
    """
    self.rotation_direction = 1
    self.angle_speed = self.rotation_direction*g_fast_angle_speed
    #self.angle_position += self.angle_speed
    self.set_label_content()

  def set_label_content(self):
    """ Update the angle labels
    """
    lb_rotation_direction = '+' if (self.rotation_direction==1) else '-'
    lb1 = "Angle position : {:0.3f} radian   {:0.2f} degree".format(self.angle_position, self.angle_position*180/math.pi)
    lb2 = "Angle speed    : {:0.3f} radian   {:0.2f} degree  {:s}".format(self.angle_speed, self.angle_speed*180/math.pi, lb_rotation_direction)
    #print("dbg774: lb1:", lb1)
    #print("dbg775: lb2:", lb2)
    self.label1_content.set(lb1)
    self.label2_content.set(lb2)
    #self.label3_content.set(lb3)
    #print("dbg845: self.label1_content.get:", self.label1_content.get())

  def action_button_check_event(self, event):
    """ This function is only used for debug
        It has no utility for the Two_Canvas class
    """
    print("dbg141: event:", event)
    print("dbg142: event.time:", event.time)
    print("dbg143: event.type:", event.type)
    print("dbg144: event.widget:", event.widget)
    print("dbg145: event.keysym:", event.keysym)

  def action_canvas_a_mouse_button_press(self, event):
    """ Start of the zoom area selection
    """
    self.mouse_x1 = event.x
    self.mouse_y1 = event.y
    self.mouse_x2 = self.mouse_x1
    self.mouse_y2 = self.mouse_y1
    self.canvas_a_mouse_press = 1
    #print("dbg874: mouse_x1, mouse_y1:", self.mouse_x1, self.mouse_y1)

  def action_canvas_a_mouse_button_motion(self, event):
    """ widget action
    """
    self.mouse_x2 = event.x
    self.mouse_y2 = event.y
    #self.canvas_a.create_rectangle(self.mouse_x1, self.mouse_y1, self.mouse_x2, self.mouse_y2, fill='', outline='red', width=2)

  def action_canvas_a_mouse_button_release(self, event):
    """ End of the zoom area selection
        It computes the crop_limit parameters
    """
    self.mouse_x2 = event.x
    self.mouse_y2 = event.y
    self.canvas_a_mouse_press = 0
    #print("dbg875: mouse_x2, mouse_y2:", self.mouse_x2, self.mouse_y2)
    selected_area = (self.mouse_x1, self.mouse_y1, self.mouse_x2, self.mouse_y2)
    canvas_a_size = (self.canvas_a.winfo_width(), self.canvas_a.winfo_height(), tkinter_canvas_margin_x, tkinter_canvas_margin_y)
    if(self.scale_coef_a==None):
      print("Warn763: Warning, self.scale_coef_a is not set!")
    else:
      self.crop_limit = compute_crop_limit(selected_area, canvas_a_size, self.scale_coef_a)
      #print("dbg986: self.crop_limit:", self.crop_limit)

  def action_canvas_b_mouse_button_press(self, event):
    """ Start of the length measurement in canvas_b
    """
    self.mouse_bx1 = event.x
    self.mouse_by1 = event.y
    self.mouse_bx2 = self.mouse_bx1
    self.mouse_by2 = self.mouse_by1
    self.canvas_b_mouse_press = 1
    #print("dbg877: mouse_bx1, mouse_by1:", self.mouse_bx1, self.mouse_by1)

  def action_canvas_b_mouse_button_motion(self, event):
    """ widget action in canvas_b
    """
    self.mouse_bx2 = event.x
    self.mouse_by2 = event.y

  def action_canvas_b_mouse_button_release(self, event):
    """ End of the length measurement
        It computes and display the length in the log
    """
    self.mouse_bx2 = event.x
    self.mouse_by2 = event.y
    self.canvas_b_mouse_press = 0
    #print("dbg878: mouse_bx2, mouse_by2:", self.mouse_bx2, self.mouse_by2)
    if(self.scale_coef_b==None):
      print("WARN663: Warning, scale_coef_b is not computed yet!")
    else:
      (lx, kx, ly, ky) = self.scale_coef_b
      p1x = (self.mouse_bx1-kx)/lx
      p1y = (self.mouse_by1-ky)/ly
      p2x = (self.mouse_bx2-kx)/lx
      p2y = (self.mouse_by2-ky)/ly
      length_measurement = math.sqrt((p2x-p1x)**2+(p2y-p1y)**2)
      if(length_measurement>0):
        angle_measurement = math.atan2((p2y-p1y)/length_measurement, (p2x-p1x)/length_measurement)
        self.measurement_id += 1
        print("Info: measurement {:2d} : lenght: {:0.3f}  angle: {:0.3f}".format(self.measurement_id, length_measurement, angle_measurement))
        print("P1x: {:0.2f}  P1y: {:0.2f}  P2x: {:0.2f}  P2y: {:0.2f}".format(p1x, p1y, p2x, p2y))

  def simulation_step(self):
    """ Time simulation main function
    """
    self.angle_position += self.angle_speed
    self.set_label_content()
    self.apply_canvas_graphic_function()
    #self.apply_curve_graphic_table(self.angle_position, self.angle_speed)
    self.frame_a.after(g_step_period, self.simulation_step)
  
  def draw_canvas(self, ai_canvas, ai_canvas_graphics, ai_overlay):
    """ Draw the computed outline list into a canvas
    """
    for outline in ai_canvas_graphics:
      outline_type = outline[0]
      if(outline_type=='graphic_lines'):
        lines = outline[1]
        for line in lines:
          ai_canvas.create_line(line, fill=outline[2], width=outline[3])
      elif(outline_type=='overlay_lines'):
        if(ai_overlay==1):
          lines = outline[1]
          for line in lines:
            ai_canvas.create_line(line, fill=outline[2], width=outline[3])
      elif(outline_type=='graphic_polygon'):
        ai_canvas.create_polygon(outline[1], fill=outline[2], outline=outline[3], width=outline[4])
      elif(outline_type=='overlay_polygon'):
        if(ai_overlay==1):
          ai_canvas.create_polygon(outline[1], fill=outline[2], outline=outline[3], width=outline[4])

  def apply_canvas_graphic_function(self):
    """ compute and draw the outline list for the main and the zoom window
    """
    canvas_a_width = self.canvas_a.winfo_width()
    canvas_a_height = self.canvas_a.winfo_height()
    canvas_b_width = self.canvas_b.winfo_width()
    canvas_b_height = self.canvas_b.winfo_height()
    #print("dbg104: canvas_a_width:", canvas_a_width)
    #print("dbg105: canvas_a_height:", canvas_a_height)
    #if(self.canvas_graphic_function==None):
    #  #print("ERR446: Error, the canvas_graphic_function has not been set!")
    #  #sys.exit(2)
    #  print("WARN446: Warning, the canvas_graphic_function has not been set!")
    if(self.canvas_graphic_function!=None):
      all_graphics = self.canvas_graphic_function(self.rotation_direction, self.angle_position)
      #
      self.canvas_a.delete(Tkinter.ALL)
      # uncomment if you want to scale outline depending on the angle_position
      #self.outline_extremum = find_outline_extremum(all_graphics)
      canvas_a_size = (canvas_a_width, canvas_a_height, tkinter_canvas_margin_x, tkinter_canvas_margin_y)
      self.scale_coef_a = compute_scale_coef(self.outline_extremum, canvas_a_size)
      canvas_a_graphics = scale_outline(all_graphics, self.scale_coef_a)
      self.draw_canvas(self.canvas_a, canvas_a_graphics, self.overlay)
      if(self.canvas_a_mouse_press==1):
        self.canvas_a.create_rectangle(self.mouse_x1, self.mouse_y1, self.mouse_x2, self.mouse_y2, fill='', outline='red', width=2)
      #
      if(self.crop_limit==(0,0,0,0)):
        self.crop_limit=(self.outline_extremum[0], self.outline_extremum[1], (self.outline_extremum[0]+self.outline_extremum[2])/2, (self.outline_extremum[1]+self.outline_extremum[3])/2)
      #
      self.canvas_b.delete(Tkinter.ALL)
      crop_graphics = crop_outline(all_graphics, self.crop_limit)
      #print("dbg857: len(crop_graphics):", len(crop_graphics))
      canvas_b_size = (canvas_b_width, canvas_b_height, 2, 2)
      #print("dbg768: self.crop_limit:", self.crop_limit)
      #print("dbg763: canvas_b_size:", canvas_b_size)
      self.scale_coef_b = compute_scale_coef(self.crop_limit, canvas_b_size)
      #print("dbg854: scale_coef_b:", scale_coef_b)
      canvas_b_graphics = scale_outline(crop_graphics, self.scale_coef_b)
      #print("dbg986: canvas_b_graphics:", canvas_b_graphics)
      self.draw_canvas(self.canvas_b, canvas_b_graphics, self.overlay)
      #self.canvas_b.create_line((5,5,canvas_b_width-5,canvas_b_height-5), fill='yellow', width=3)
      if(self.canvas_b_mouse_press==1):
        self.canvas_b.create_line(self.mouse_bx1, self.mouse_by1, self.mouse_bx2, self.mouse_by2, fill='red', width=2)

  def action_button_overlay(self):
    """ Toggle the overlay visibility
    """
    if(self.overlay==0):
      self.overlay=1
    else:
      self.overlay=0

  def action_button_zoom(self):
    """ Toggle the zoom window visibility
    """
    #print("dbg656: action_button_zoom")
    #print("dbg567: frame_b.winfo_exists:", self.frame_b.winfo_exists())
    #print("dbg568: frame_b.state:", self.frame_b.state())
    if(self.frame_b.state()=='withdrawn'):
      self.show_zoom_frame()
    else:
      self.hide_zoom_frame()

  def create_zoom_frame(self):
    """ Define the zoom window
    """
    #print("dbg554: create_zoom_frame")
    self.frame_b = Tkinter.Toplevel(self.frame_a)
    #self.frame_b.grid(column=0, row=0, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W) # Toplevel doesn't have grid method !
    #self.frame_b.pack(fill=Tkinter.BOTH, expand=1)
    self.frame_b.title("cnc25d display backend details")
    self.canvas_b = Tkinter.Canvas(self.frame_b, width=initial_tkinter_canvas_width, height=initial_tkinter_canvas_height)
    #self.canvas_b.grid(column=0, row=0, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
    #self.canvas_b.columnconfigure(0, weight=1)
    #self.canvas_b.rowconfigure(0, weight=1)
    self.canvas_b.pack(fill=Tkinter.BOTH, expand=1) # with Toplevel parent, it seems you need to use pack to resisze the canvas !
    self.canvas_b.bind("<ButtonPress-1>", self.action_canvas_b_mouse_button_press)
    self.canvas_b.bind("<B1-Motion>", self.action_canvas_b_mouse_button_motion)
    self.canvas_b.bind("<ButtonRelease-1>", self.action_canvas_b_mouse_button_release)
    self.frame_b.protocol("WM_DELETE_WINDOW", self.hide_zoom_frame) # change the behaviour of the window X button

  def hide_zoom_frame(self):
    """ Hide the zoom window
    """
    self.frame_b.withdraw()

  def show_zoom_frame(self):
    """ Show the zoom window
    """
    self.frame_b.update()
    self.frame_b.deiconify()

  def action_button_parameters(self):
    """ Toggle the parameter window visibility
    """
    #tkMessageBox.showinfo('lala','Yes mes')
    #print("dbg566: frame_c.winfo_exists:", self.frame_c.winfo_exists())
    #print("dbg569: frame_c.state:", self.frame_c.state())
    #print("dbg559: self.parameter_content.get():", self.parameter_content.get())
    if(self.frame_c.state()=='withdrawn'):
      if(self.parameter_content.get()==''):
        print("WARN556: Warning, no parameter information has been set!")
      else:
        self.show_parameter_frame()
    else:
      self.hide_parameter_frame()


  def create_parameter_frame(self):
    """ Define the parameter window
    """
    #print("dbg414: create_parameter_frame")
    self.frame_c = Tkinter.Toplevel(self.frame_a)
    self.frame_c.title("parameter info")
    self.parameter_message = Tkinter.Message(self.frame_c, textvariable=self.parameter_content)
    self.parameter_message.grid(sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
    self.frame_c.protocol("WM_DELETE_WINDOW", self.hide_parameter_frame) # change the behaviour of the window X button

  def hide_parameter_frame(self):
    """ Hide the parameter window
    """
    self.frame_c.withdraw()

  def show_parameter_frame(self):
    """ Show the parameter window
    """
    self.frame_c.update()
    self.frame_c.deiconify()

  #def apply_curve_graphic_table(self, ai_angle_position, ai_angle_speed):
  #  """ Compute the curve new points accordind to the angle_position and angle_speed
  #  """
  #  curve_nb = len(self.curve_graphic_table)-1
  #  if(curve_nb>0):
  #    # angle in x-axis
  #    #lx = ai_angle_position
  #    # time in x-axis
  #    lx = 0 # initial timestamp
  #    if(len(self.curve_points[0])>0):
  #      #dlx = ai_angle_speed/self.curve_graphic_table[0][2]
  #      dlx = self.curve_graphic_table[0][2]
  #      lx = self.curve_points[0][-1] + abs(dlx)
  #    self.curve_points[0].append(lx)
  #    for i in range(curve_nb):
  #      ly = self.curve_graphic_table[i+1][1](ai_angle_position, ai_angle_speed)
  #      self.curve_points[i+1].append(ly)

  def action_button_curve_graph(self, event):
    """ Launch the matplotlib window for curve display
    """
    curve_nb = len(self.curve_graphic_table)-1
    if(curve_nb<=0):
      print("WARN451: Warning, self.curve_graphic_table is not set!")
    else:
      # create curve_points
      curve_nb = len(self.curve_graphic_table)-1
      curve_points = []
      for i in range(curve_nb+1):
        curve_points.append([])
      curve_table_len = len( self.curve_graphic_table[1][1])
      for j in range(curve_nb-1):
        check_len = len( self.curve_graphic_table[j+2][1])
        if(check_len!=curve_table_len):
          print("ERR586: Error in the curve_table {:d}! Its lenght {:d} does not match the reference length {:d}".format(j, check_len, curve_table_len))
      x_increment = self.curve_graphic_table[0][2]
      abscissa_x = 0
      for i in range(curve_table_len):
        curve_points[0].append(abscissa_x)
        abscissa_x += x_increment
        for j in range(curve_nb):
          table = self.curve_graphic_table[j+1][1]
          ly = table[i]
          curve_points[j+1].append(ly)
      #matplotlib.pyplot.plot([1,2,3,4,5],[5,3,2,1,4])
      matplotlib.pyplot.figure(1)
      for i in range(curve_nb):
        matplotlib.pyplot.subplot(curve_nb,1,i+1)
        #matplotlib.pyplot.plot(self.curve_points[0], self.curve_points[i+1], self.curve_graphic_table[i+1][2])
        matplotlib.pyplot.plot(curve_points[0], curve_points[i+1], self.curve_graphic_table[i+1][2])
        matplotlib.pyplot.ylabel(self.curve_graphic_table[i+1][0])
        if(i==0):
          matplotlib.pyplot.title(self.curve_graphic_table[0][0])
        if(i==curve_nb-1):
          matplotlib.pyplot.xlabel(self.curve_graphic_table[0][1])
      matplotlib.pyplot.show()

  def quit_Two_Canvas(self):
    """ Destroy the Two_Canvas Tkinter application
    """
    self.frame_b.destroy()
    self.frame_c.destroy()
    self.frame_a.destroy()
    self.tktop.destroy()
    

  def createWidgets(self):
    """ Create the widgets of the main window with their layout and also the zoom window and parameter window
    """
    #
    #self.frame_canvas = Tkinter.Frame(self.frame_a)
    ##self.frame_canvas.pack(side=Tkinter.TOP)
    #self.frame_canvas.grid(column=0, row=0, sticky=Tkinter.W + Tkinter.N + Tkinter.E + Tkinter.S)
    #self.frame_canvas.columnconfigure(0, weight=1)
    #self.frame_canvas.rowconfigure(0, weight=1)
    #
    #self.canvas_a =  Tkinter.Canvas(self.frame_a, width=self.canvas_a_width, height=self.canvas_a_height)
    self.canvas_a =  Tkinter.Canvas(self.frame_a, width=initial_tkinter_canvas_width, height=initial_tkinter_canvas_height)
    #self.canvas_a.pack(fill=Tkinter.BOTH, expand=1)
    self.canvas_a.grid(column=0, row=0, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
    self.canvas_a.columnconfigure(0, weight=1)
    self.canvas_a.rowconfigure(0, weight=1)
    self.canvas_a.bind("<ButtonPress-1>", self.action_canvas_a_mouse_button_press)
    self.canvas_a.bind("<B1-Motion>", self.action_canvas_a_mouse_button_motion)
    self.canvas_a.bind("<ButtonRelease-1>", self.action_canvas_a_mouse_button_release)
    #
    self.frame_control = Tkinter.Frame(self.frame_a)
    #self.frame_control.pack(side=Tkinter.BOTTOM)
    self.frame_control.grid(column=0, row=1, sticky=Tkinter.W + Tkinter.S)
    #
    self.frame_button_speed = Tkinter.Frame(self.frame_control)
    self.frame_button_speed.grid(column=0, row=0)
    #
    self.button_fast_backward = Tkinter.Button(self.frame_button_speed)
    self.button_fast_backward["text"] = "<<-",
    self.button_fast_backward["command"] = self.action_button_fast_backward
    self.button_fast_backward.pack(side=Tkinter.LEFT)
    #
    self.button_slow_backward = Tkinter.Button(self.frame_button_speed)
    self.button_slow_backward["text"] = "<-",
    self.button_slow_backward["command"] = self.action_button_slow_backward
    self.button_slow_backward.pack(side=Tkinter.LEFT)
    #
    self.button_step_backward = Tkinter.Button(self.frame_button_speed)
    self.button_step_backward["text"] = "<|",
    self.button_step_backward["command"] = self.action_button_step_backward
    self.button_step_backward.pack(side=Tkinter.LEFT)
    #
    self.button_stop = Tkinter.Button(self.frame_button_speed)
    self.button_stop["foreground"]   = "red"
    self.button_stop["text"] = "||",
    self.button_stop["command"] = self.action_button_stop
    self.button_stop.pack(side=Tkinter.LEFT)
    #
    self.button_step_forward = Tkinter.Button(self.frame_button_speed)
    self.button_step_forward["text"] = "|>",
    self.button_step_forward["command"] = self.action_button_step_forward
    self.button_step_forward.pack(side=Tkinter.LEFT)
    #
    self.button_slow_forward = Tkinter.Button(self.frame_button_speed)
    self.button_slow_forward["text"] = "->",
    self.button_slow_forward["command"] = self.action_button_slow_forward
    self.button_slow_forward.pack(side=Tkinter.LEFT)
    #
    self.button_fast_forward = Tkinter.Button(self.frame_button_speed)
    self.button_fast_forward["text"] = "->>",
    self.button_fast_forward["command"] = self.action_button_fast_forward
    self.button_fast_forward.pack(side=Tkinter.LEFT)
    #
    self.frame_label = Tkinter.Frame(self.frame_control)
    self.frame_label.grid(column=0, row=1, sticky=Tkinter.W)
    #
    self.label_angle = Tkinter.Label(self.frame_label)
    self.label_angle["textvariable"] = self.label1_content
    #self.label_angle.pack(side=Tkinter.TOP)
    #self.label_angle.pack(anchor=Tkinter.NW)
    self.label_angle.grid(column=0, row=0, sticky=Tkinter.W)
    #
    self.label_angle_speed = Tkinter.Label(self.frame_label)
    self.label_angle_speed["textvariable"] = self.label2_content
    #self.label_angle_speed.pack(side=Tkinter.BOTTOM)
    #self.label_angle_speed.pack(anchor=Tkinter.SW)
    self.label_angle_speed.grid(column=0, row=1, sticky=Tkinter.W)
    #
    self.frame_button_options = Tkinter.Frame(self.frame_control)
    self.frame_button_options.grid(column=0, row=2, sticky=Tkinter.W+Tkinter.S)
    #
    self.button_zoom = Tkinter.Button(self.frame_button_options)
    self.button_zoom["text"] = "Zoom",
    self.button_zoom["command"] = self.action_button_zoom
    self.button_zoom.pack(side=Tkinter.LEFT)
    #
    self.button_overlay = Tkinter.Button(self.frame_button_options)
    self.button_overlay["text"] = "Overlay",
    self.button_overlay["command"] = self.action_button_overlay
    self.button_overlay.pack(side=Tkinter.LEFT)
    #
    self.button_parameter = Tkinter.Button(self.frame_button_options)
    self.button_parameter["text"] = "Parameters",
    self.button_parameter["command"] = self.action_button_parameters
    self.button_parameter.pack(side=Tkinter.LEFT)
    #
    self.button_graph = Tkinter.Button(self.frame_button_options)
    self.button_graph["text"] = "Graph",
    #self.button_graph["command"] = lambda a=1: self.action_button_check_event(a)
    #self.button_graph.bind("<Button-1>", lambda event: self.action_button_check_event(event))
    #self.button_graph.bind("<Button-1>", self.action_button_check_event) # the event argument is added by default
    self.button_graph.bind("<Button-1>", self.action_button_curve_graph) # the event argument is added by default
    self.button_graph.pack(side=Tkinter.LEFT)
    #
    self.button_quit = Tkinter.Button(self.frame_button_options)
    self.button_quit["text"] = "Quit",
    #self.button_quit["command"] = self.frame_a.quit
    #self.button_quit["command"] = self.tktop.destroy
    self.button_quit["command"] = self.quit_Two_Canvas
    self.button_quit.pack(side=Tkinter.LEFT)
    #
    ## second window with canvas_b
    self.create_zoom_frame()
    self.show_zoom_frame()
    #
    ## third window with parameter text
    self.create_parameter_frame()
    self.hide_parameter_frame()

  def __init__(self, winParent):
    """ Initiate the class Two_Canvas by creating the windows, initializing the class variables and starting the time simulation
    """
    self.tktop = winParent # used to destroy the app when quit
    self.frame_a = Tkinter.Frame(winParent)
    winParent.title("cnc25d display backend main")
    #self.frame_a.pack()
    #winParent.grid(sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
    winParent.columnconfigure(0, weight=1)
    winParent.rowconfigure(0, weight=1)
    self.frame_a.grid(sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
    self.frame_a.columnconfigure(0, weight=1)
    self.frame_a.rowconfigure(0, weight=1)
    #
    self.angle_speed = 0*g_slow_angle_speed
    self.rotation_direction = 1
    self.angle_position = 0
    self.outline_extremum = (0,0,0,0)
    #
    self.label1_content = Tkinter.StringVar()
    self.label2_content = Tkinter.StringVar()
    self.set_label_content()
    #
    self.parameter_content = Tkinter.StringVar()
    #
    self.overlay = 0
    self.canvas_graphic_function = None
    self.mouse_x1 = 0
    self.mouse_y1 = 0
    self.mouse_x2 = initial_tkinter_canvas_width/2
    self.mouse_y2 = initial_tkinter_canvas_height/2
    self.canvas_a_mouse_press = 0
    self.scale_coef_a = None
    self.crop_limit = (0,0,0,0)
    self.mouse_bx1 = 0
    self.mouse_by1 = 0
    self.mouse_bx2 = 0
    self.mouse_by2 = 0
    self.canvas_b_mouse_press = 0
    self.measurement_id = 0
    self.scale_coef_b = None
    #
    self.curve_graphic_table = []
    #self.curve_points = []
    #
    self.createWidgets()
    self.tktop.protocol("WM_DELETE_WINDOW", self.quit_Two_Canvas) # change the behaviour of the window X button
    # initiate the time simulation
    self.simulation_step()

  def add_canvas_graphic_function(self, ai_canvas_graphic_function):
    """ api method to add or change the canvas graphics
    """
    #print("dbg445: ai_graphic_function:", ai_graphic_function)
    self.canvas_graphic_function = ai_canvas_graphic_function
    # the next line is to compute the extremum once at initialization if you don't want to recompute it at each angle_position
    self.outline_extremum = find_outline_extremum(self.canvas_graphic_function(self.rotation_direction, self.angle_position))

  def add_parameter_info(self, ai_parameter_info):
    """ api method to add or change the parameter info
    """
    self.parameter_content.set(ai_parameter_info)
    
  def add_curve_graphic_table(self, ai_curve_graphic_table):
    """ api method to add or change the curve functions for matplotlib
    """
    self.curve_graphic_table = ai_curve_graphic_table
    #curve_nb = len(self.curve_graphic_table)-1
    #self.curve_points = []
    #for i in range(curve_nb+1):
    #  self.curve_points.append([])



#  tk_a = Tkinter.Tk()
#  tk_a.title("test1 backend tkinter")
#  canvas_a = Tkinter.Canvas(tk_a, width=win_a_w,height=win_a_h)
#  canvas_a.bind("<Configure>", gg_redraw_canvas_a)
#  canvas_a.bind("<Button-1>", gg_callback_on_click_a)
#  canvas_a.pack(fill=Tkinter.BOTH, expand=1)
#  tk_a.mainloop()

################################################################
# ******** test the Two_Canvas class ***********
################################################################

def test_canvas_graphic_1(ai_rotation_direction, ai_angle):
  """ Sub-function for test 1
      Also example of the callback function for add_canvas_graphic_function
  """
  polygon_test_1 = (
    5,5,
    35,5,
    20,35)
  lines_test_1 = (
    (0,0,20,25),
    (5,5,20,25))
  polygon_test_2 = (
    105,105,
    135,105,
    120,135)
  lines_test_2 = (
    (15,0,50,15),
    (-30,30,50,15))
  polygon_test_3 = (
    205,205,
    235,205,
    220,265)
  r_canvas_graph = []
  r_canvas_graph.append(('graphic_lines', lines_test_1, 'red', 1))
  r_canvas_graph.append(('graphic_polygon', polygon_test_1, 'green', 'red', 1))
  r_canvas_graph.append(('overlay_lines', lines_test_2, 'yellow', 2))
  r_canvas_graph.append(('overlay_polygon', polygon_test_2, 'orange', 'yellow', 2))
  r_canvas_graph.append(('graphic_polygon', polygon_test_3, 'green', 'red', 1))
  return(r_canvas_graph)

#def test1_curve1(ai_angle_position, ai_angle_speed):
#  """ test curve for matplotlib
#  """
#  r_y = math.sin(ai_angle_position)
#  return(r_y)
#
#def test1_curve2(ai_angle_position, ai_angle_speed):
#  """ test curve for matplotlib
#  """
#  r_y = math.cos(ai_angle_position)
#  return(r_y)

def two_canvas_class_test1():
  """ test the simple display of a static graphic with Two_Canvas
  """
  #
  test_parameter_info = """
Maître Corbeau, sur un arbre perché,
Tenait en son bec un fromage.
Maître Renard, par l'odeur alléché,
Lui tint à peu près ce langage :
"Hé ! bonjour, Monsieur du Corbeau.
Que vous êtes joli ! que vous me semblez beau !
Sans mentir, si votre ramage
Se rapporte à votre plumage,
Vous êtes le Phénix des hôtes de ces bois. "
  """
  #
  #lambda_function_1 = test1_curve1
  #lambda_function_1 = lambda x: test1_curve1(x)
  #lambda_function_2 = test1_curve2
  test1_curve1 = (1,2,3,4,5,6,7,8,9,10,11,12,13)
  test1_curve2 = (8,7,3,4,2,2,3,4,5,5.5,6,6.2,6.9)
  test_curve_graphic_1 = (('global_title', 'x_axis_name', 1),
    ('plot1_title', test1_curve1, 'bo'),
    ('plot2_title', test1_curve2, 'r'))
  #
  tk_root = Tkinter.Tk()
  dut = Two_Canvas(tk_root)
  #dut = Two_Canvas()
  dut.add_canvas_graphic_function(test_canvas_graphic_1)
  dut.add_parameter_info(test_parameter_info)
  dut.add_curve_graphic_table(test_curve_graphic_1)
  tk_root.mainloop()
  #dut.mainloop()
  r_test = 1
  return(r_test)

def test_canvas_graphic_2(ai_rotation_direction, ai_angle):
  """ Sub-function for test 1
      Also example of the callback function for add_canvas_graphic_function
  """
  l_angle = float(ai_angle)/100
  polygon_test_2 = (
    30*math.cos(l_angle+1.0*math.pi/2), 30*math.sin(l_angle+1.0*math.pi/2),
    35*math.cos(l_angle+1.5*math.pi/2), 35*math.sin(l_angle+1.5*math.pi/2),
    20*math.cos(l_angle+2.0*math.pi/2), 20*math.sin(l_angle+2.0*math.pi/2),
    50*math.cos(l_angle+2.5*math.pi/2), 50*math.sin(l_angle+2.5*math.pi/2),
    40*math.cos(l_angle+3.0*math.pi/2), 40*math.sin(l_angle+3.0*math.pi/2),
    30*math.cos(l_angle+3.5*math.pi/2), 30*math.sin(l_angle+3.5*math.pi/2),
    25*math.cos(l_angle+4.0*math.pi/2), 25*math.sin(l_angle+4.0*math.pi/2),
    35*math.cos(l_angle+4.5*math.pi/2), 35*math.sin(l_angle+4.5*math.pi/2))
  r_canvas_graph = []
  r_canvas_graph.append(('graphic_polygon', polygon_test_2, '', 'red', 1))
  return(r_canvas_graph)

def two_canvas_class_test2():
  """ test the simple display of a dynamic graphic with Two_Canvas
  """
  #
  test_parameter_info = """
Maître Corbeau, sur un arbre perché,
Tenait en son bec un fromage.
  """
  #
  test1_curve1 = (1,2,3,4,5,6,7,8,9,10,11,12,13)
  test1_curve2 = (8,7,3,4,2,2,3,4,5,5.5,6,6.2,6.9)
  test_curve_graphic_1 = (('global_title', 'x_axis_name', 0.001),
    ('plot1_title', test1_curve1, 'bo'),
    ('plot2_title', test1_curve2, 'r'))
  #
  tk_root = Tkinter.Tk()
  dut = Two_Canvas(tk_root)
  dut.add_canvas_graphic_function(test_canvas_graphic_2)
  dut.add_parameter_info(test_parameter_info)
  dut.add_curve_graphic_table(test_curve_graphic_1)
  tk_root.mainloop()
  #
  r_test = 1
  return(r_test)

################################################################
# ******** command line interface ***********
################################################################

def display_backends_cli(ai_args=None):
  """ command line interface to run this script in standalone
  """
  db_parser = argparse.ArgumentParser(description='Test the display_backend Two_Canvas).')
  db_parser.add_argument('--test1','--t1', action='store_true', default=False, dest='sw_test1',
    help='Run two_canvas_class_test1() with a static graphic')
  db_parser.add_argument('--test2','--t2', action='store_true', default=False, dest='sw_test2',
    help='Run two_canvas_class_test2() with a dynamic graphic')
  effective_args = design_help.get_effective_args(ai_args)
  db_args = db_parser.parse_args(effective_args)
  r_dbc = 0
  print("dbg111: start testing display_backends.py")
  if(db_args.sw_test1):
    r_dbc = two_canvas_class_test1()
  elif(db_args.sw_test2):
    r_dbc = two_canvas_class_test2()
  print("dbg999: end of script")
  return(r_dbc)

################################################################
# main
################################################################

if __name__ == "__main__":
  print("display_backend.py says hello!")
  # choose the script behavior
  #display_backends_cli()                   # get arguments from the command line
  display_backends_cli("--test1".split())   # run the test1
  #display_backends_cli("--test2".split())

