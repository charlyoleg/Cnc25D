# display_backend.py
# creates and displays the two Tkinter Canvas windows used by outline_backends.py
# created by charlyoleg on 2013/07/11
# license: CC BY SA 3.0

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

################################################################
# global variable
################################################################
initial_tkinter_canvas_width = 400
initial_tkinter_canvas_height = 400
g_step_angle_speed = 1/100.0
g_slow_angle_speed = 1/1000.0
g_fast_angle_speed = 16*g_slow_angle_speed
g_step_period = 100 # ms

################################################################
# ******** Two_Canvas class ***********
################################################################


class Two_Canvas():

  def action_button_fast_backward(self):
    self.angle_speed = -1*g_fast_angle_speed
    #self.angle_position += self.angle_speed
    self.set_label_content()

  def action_button_slow_backward(self):
    self.angle_speed = -1*g_slow_angle_speed
    #self.angle_position += self.angle_speed
    self.set_label_content()

  def action_button_step_backward(self):
    self.angle_speed = 0
    self.angle_position += -1*g_step_angle_speed
    self.set_label_content()

  def action_button_stop(self):
    self.angle_speed = 0
    #self.angle_position += 0
    self.set_label_content()

  def action_button_step_forward(self):
    self.angle_speed = 0
    self.angle_position += 1*g_step_angle_speed
    self.set_label_content()

  def action_button_slow_forward(self):
    self.angle_speed = 1*g_slow_angle_speed
    #self.angle_position += self.angle_speed
    self.set_label_content()

  def action_button_fast_forward(self):
    self.angle_speed = 1*g_fast_angle_speed
    #self.angle_position += self.angle_speed
    self.set_label_content()

  def set_label_content(self):
    lb1 = "Angle position : {:0.3f} radian   {:0.2f} degree".format(self.angle_position, self.angle_position*180/math.pi)
    lb2 = "Angle speed    : {:0.3f} radian   {:0.2f} degree".format(self.angle_speed, self.angle_speed*180/math.pi)
    #print("dbg774: lb1:", lb1)
    #print("dbg775: lb2:", lb2)
    self.label1_content.set(lb1)
    self.label2_content.set(lb2)
    #print("dbg845: self.label1_content.get:", self.label1_content.get())

  def action_button_check_event(self, event):
    print("dbg141: event:", event)
    print("dbg142: event.time:", event.time)
    print("dbg143: event.type:", event.type)
    print("dbg144: event.widget:", event.widget)
    print("dbg145: event.keysym:", event.keysym)

  def simulation_step(self):
    self.angle_position += self.angle_speed
    self.set_label_content()
    self.draw_canvas_a()
    self.frame_a.after(g_step_period, self.simulation_step)
  
  def draw_canvas_a(self):
    canvas_a_width = self.canvas_a.winfo_width()
    canvas_a_height = self.canvas_a.winfo_height()
    #print("dbg104: canvas_a_width:", canvas_a_width)
    #print("dbg105: canvas_a_height:", canvas_a_height)
    self.canvas_a.delete(Tkinter.ALL)
    if(self.overlay==1):
      self.canvas_a.create_line((50,50,200,200), fill='red', width=1)
    self.canvas_a.create_line((5,5,canvas_a_width-5,canvas_a_height-5), fill='green', width=1)

  def action_button_overlay(self):
    if(self.overlay==0):
      self.overlay=1
    else:
      self.overlay=0

  def action_button_zoom(self):
    #print("dbg656: action_button_zoom")
    #print("dbg567: frame_b.winfo_exists:", self.frame_b.winfo_exists())
    #print("dbg568: frame_b.state:", self.frame_b.state())
    if(self.frame_b.state()=='withdrawn'):
      self.show_zoom_frame()
    else:
      self.hide_zoom_frame()

  def create_zoom_frame(self):
    #print("dbg554: create_zoom_frame")
    self.frame_b = Tkinter.Toplevel(self.frame_a)
    self.frame_b.title("cnc25d display backend details")
    self.canvas_b = Tkinter.Canvas(self.frame_b, width=initial_tkinter_canvas_width, height=initial_tkinter_canvas_height)
    self.canvas_b.grid(sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
    self.frame_b.protocol("WM_DELETE_WINDOW", self.hide_zoom_frame) # change the behaviour of the window X button

  def hide_zoom_frame(self):
    self.frame_b.withdraw()

  def show_zoom_frame(self):
    self.frame_b.update()
    self.frame_b.deiconify()

  def action_button_parameters(self):
    #tkMessageBox.showinfo('lala','Yes mes')
    #print("dbg566: frame_c.winfo_exists:", self.frame_c.winfo_exists())
    #print("dbg569: frame_c.state:", self.frame_c.state())
    if(self.frame_c.state()=='withdrawn'):
      self.show_parameter_frame()
    else:
      self.hide_parameter_frame()

  def set_parameter_content(self):
    lpc = "les stroumpf \n atennt\n\njop"
    self.parameter_content.set(lpc)

  def create_parameter_frame(self):
    #print("dbg414: create_parameter_frame")
    self.frame_c = Tkinter.Toplevel(self.frame_a)
    self.frame_c.title("parameter info")
    self.parameter_message = Tkinter.Message(self.frame_c, textvariable=self.parameter_content)
    self.parameter_message.grid(sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
    self.frame_c.protocol("WM_DELETE_WINDOW", self.hide_parameter_frame) # change the behaviour of the window X button

  def hide_parameter_frame(self):
    self.frame_c.withdraw()

  def show_parameter_frame(self):
    self.frame_c.update()
    self.frame_c.deiconify()

  def createWidgets(self):
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
    self.button_graph.bind("<Button-1>", self.action_button_check_event) # the event argument is added by default
    self.button_graph.pack(side=Tkinter.LEFT)
    #
    self.button_quit = Tkinter.Button(self.frame_button_options)
    self.button_quit["text"] = "Quit",
    self.button_quit["command"] = self.frame_a.quit
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
    self.angle_position = 0
    #
    self.label1_content = Tkinter.StringVar()
    self.label2_content = Tkinter.StringVar()
    self.set_label_content()
    #
    self.parameter_content = Tkinter.StringVar()
    self.set_parameter_content()
    #
    self.overlay = 0
    self.zoom_frame_exist = 0
    self.parameter_frame_exist = 0
    #
    self.createWidgets()
    # initiate the time simulation
    self.simulation_step()

  def add_graphic(self, ai_graphic):
    print("dbg445: ai_graphic:", ai_graphic)

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

def two_canvas_class_test1():
  """ test the simple display of a static graphic with Two_Canvas
  """
  test_graphic = [
    [5,5],
    [35,5],
    [20,35]]
  #
  tk_root = Tkinter.Tk()
  dut = Two_Canvas(tk_root)
  #dut = Two_Canvas()
  dut.add_graphic(test_graphic)
  tk_root.mainloop()
  #dut.mainloop()
  r_test = 1
  return(r_test)

################################################################
# ******** command line interface ***********
################################################################

def display_backends_cli():
  """ command line interface to run this script in standalone
  """
  db_parser = argparse.ArgumentParser(description='Test the display_backend Two_Canvas).')
  db_parser.add_argument('--test1','--t1', action='store_true', default=False, dest='sw_test1',
    help='Run two_canvas_class_test1()')
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
  db_args = db_parser.parse_args(effective_args)
  r_dbc = 0
  print("dbg111: start testing outline_backends")
  if(db_args.sw_test1):
    r_dbc = two_canvas_class_test1()
  print("dbg999: end of script")
  return(r_dbc)

################################################################
# main
################################################################

if __name__ == "__main__":
  print("display_backend.py says hello!\n")
  #display_backends_cli()
  # or alternatively, run directly a test
  two_canvas_class_test1()

