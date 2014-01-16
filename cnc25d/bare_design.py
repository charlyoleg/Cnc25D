# bare_design.py
# a class definition that can be used to create a parametric cnc25d design.
# created by charlyoleg on 2014/01/13
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
bare_design.py contains the routines commonly used in the cnc25d designs.
The goal is discharging the design script from all the convenience stuff.
"""

################################################################
# import for bare_design
################################################################

import sys, argparse
import re # to detect .dxf or .svg
#
import outline_backends
import design_help
import design_output

################################################################
# bare_design class
################################################################

class bare_design:
  """ The bare_design class aims at being inherited by the cnc25d-design-script
  """

  def set_design_name(self, design_name):
    """ set the name of the design to complete some debug or infroamtion log
    """
    # mandatory attributes
    self.design_name = design_name
    self.parser = None
    self.f_2d_constructor = None
    self.f_info = None
    # optional attributes
    self.f_constraint_check = None # highly recommended
    self.f_3d_constructor = None
    self.f_simulation_2d = None
    self.f_return_type = None
    self.self_tests = None
    self.display_2d_figure_list = []
    self.write_2d_figure_list = []
    self.write_3d_figure_list = []
    self.write_3d_conf_list = []
    # self-generated attributes
    self.reference_constraint = None
    self.constraint = None
    self.cli_str = None
    self.A_figures = None
    self.figure_heights = None
    self.assembly_configurations = None
    self.slice3d_configurations = None

  def set_constraint_constructor(self, f_constraint_constructor):
    """ create the design constraint list
    """
    init_parser = argparse.ArgumentParser(description='Command Line Interface of {:s}'.format(self.design_name))
    self.parser = f_constraint_constructor(init_parser)
    self.reference_constraint = vars(self.parser.parse_args([]))
    self.constraint = self.reference_constraint.copy()

  def set_constraint_check(self, f_constraint_check):
    """ bind the function f_constraint_check that checks the constraint values and set the dynamic default values
    """
    self.f_constraint_check = f_constraint_check

  def set_2d_constructor(self, f_2d_constructor):
    """ bind the function f_2d_constructor that generates the 2D figures and returns them in a dictionary
    """
    self.f_2d_constructor = f_2d_constructor

  def set_2d_simulation(self, f_simulation_2d=None):
    """ bind the function f_simulation_2d that runs 2D-simulation in a Tk-window
    """
    self.f_simulation_2d = f_simulation_2d

  def set_3d_constructor(self, f_3d_constructor):
    """ bind the function f_3d_constructor that generates the 3D assembly and returns them in a dictionary
    """
    self.f_3d_constructor = f_3d_constructor

  def set_info(self, f_info):
    """ bind the function f_info that generates the design text info
    """
    self.f_info = f_info

  def set_display_figure_list(self, figure_list=[]):
    """ set the list of figures to be displayed
        If the list is empty, all 2D-figures will be display in Tk-windows
    """
    self.display_2d_figure_list = figure_list

  def set_2d_figure_file_list(self, figure_list=[]):
    """ set the list of figures to be written in SVG or DXF files
        If the list is empty, all 2D-figures will be written in files
    """
    self.write_2d_figure_list = figure_list

  def set_3d_figure_file_list(self, figure_list=[]):
    """ set the list of 2d-figures to be written in BREP files
        If the list is empty, all 2d-figures will be written in files
    """
    self.write_3d_figure_list = figure_list

  def set_3d_conf_file_list(self, assembly_conf_list=[]):
    """ set the list of 3d-assembly-configurations to be written in BREP files
        If the list is empty, all 3D-assembly-configurations will be written in files
    """
    self.write_3d_conf_list = assembly_conf_list

  def set_allinone_return_type(self, f_return_type=None):
    """ bind the function f_return_type that generate the return value of the method allinone()
    """
    self.f_return_type = f_return_type

  def set_self_test(self, self_tests):
    """ set the list of cli_string used as tests
    """
    self.self_tests = self_tests
  
  def apply_constraint(self, constraint):
    """ set the dictionary constraint to the design
    """
    rc = self.reference_constraint
    c = rc.copy()
    c.update(constraint) # apply the new constraint values
    #print("dbg100: constraint:", c)
    if(len(c.viewkeys() & rc.viewkeys()) != len(c.viewkeys() | rc.viewkeys())): # check if the dictionary c has exactly all the keys compare to self.reference_constraint
      print("ERR104: Error, constraint c has too much entries as {:s} or missing entries as {:s}".format(c.viewkeys() - rc.viewkeys(), rc.viewkeys() - c.viewkeys()))
      sys.exit(2)
    #print("dbg106: new constraint:") # some optional debug
    #for k in c.viewkeys():
    #  if(c[k] != rc[k]):
    #    print("dbg109: for k {:s}, c[k] {:s} != rc[k] {:s}".format(k, str(c[k]), str(rc[k])))
    if(self.f_constraint_check==None):
      print("WARN134: Warning, the function f_constraint_check has not been set!")
      self.constraint = c
    else:
      self.constraint = self.f_constraint_check(c)
    self.cli_str = "" # delete the cli_str when caontraint come from dictionary

  def apply_cli(self, cli_str=""):
    """ set the cli constraint to the design.
        It's an alternative to apply_constraint
    """
    effective_args = cli_str.split()
    effective_args_in_txt = "{:s} cli string: ".format(self.design_name) + ' '.join(effective_args)
    c = vars(self.parser.parse_args(effective_args))
    self.apply_constraint(c)
    self.cli_str = effective_args_in_txt # must be set after apply_constraint()

  def __init__(self):
    """ bare_design constructor
    """
    print("dbg163: create a new bare_design") # this should be never seen because the __init__ fonction is overwritten

  def get_constraint(self):
    """ return the current applied constraint in a dictionary
    """
    return(self.constraint)

  def get_info(self):
    """ generate the design info
    """
    if(self.f_info==None):
      print("ERR160: Error, the function f_info has not been set!")
      sys.exit(2)
    r_txt = "DESIGN INFO for {:s}\n{:s}\n".format(self.design_name, self.cli_str)
    r_txt += "{:s}".format(self.f_info(self.constraint))
    return(r_txt)

  def apply_2d_constructor(self):
    """ internal method that execute the f_2d_constructor function
    """
    if(self.f_2d_constructor==None):
      print("ERR169: Error, the function f_2d_constructor has not been set!")
      sys.exit(2)
    (figs, fig_heights) = self.f_2d_constructor(self.constraint) # generate all figures
    self.A_figures = figs
    self.figure_heights = fig_heights
    #print("dbg191: self.A_figures.keys():", self.A_figures.keys())

  def get_A_figure(self, figure_names=[]):
    """ generate the figures listed by figure_names and return a merge of these figures
        figure_names is a list of strings that must correspond to the design figure dictionary
        if figure_names is empty, all figures are generated and merged
    """
    self.apply_2d_constructor()
    if(figure_names==[]):
      figure_names = self.A_figures.keys()
    #print("dbg194: figure_names:", figure_names)
    r_fig = []
    for f in figure_names:
      if(not f in self.A_figures.keys()):
        print("ERR156: Error, f {:s} is not in the figure list [{:s}]".format(f, ' '.join(self.A_figures.keys())))
        sys.exit(2)
      r_fig.extend(self.A_figures[f])
    return(r_fig)
      
  def get_B_figure(self, figure_names=[]):
    """ generate the figures listed by figure_names, then merge and cnc_cut_ouline before returning the final figure
        figure_names is a list of strings that must correspond to the design figure dictionary
        if figure_names is empty, all figures are generated and merged
    """
    A_fig = self.get_A_figure(figure_names)
    r_fig = design_output.cnc_cut_figure(A_fig, "get_B_figure_{:s}".format('_'.join(figure_names)))
    return(r_fig)

  def outline_display(self):
    """ display in one or several Tk windows the design outline figures
    """
    self.get_A_figure() # create the A-figures
    print("{:s}".format(self.get_info()))
    figs = self.display_2d_figure_list
    if(len(figs)==0):
      figs = self.A_figures.keys()
    for f in figs:
      if(not f in self.A_figures.keys()):
        print("ERR232: Error, fig {:s} is not an existing 2d-figures {:s}".format(fig, ' '.join(self.A_figures.keys())))
        sys.exit(2)
      fig = self.A_figures[f]
      d_info = "display_{:s}".format(f)
      #print("dbg218: fig:", fig)
      print("{:s}".format(d_info))
      outline_backends.figure_simple_display(design_output.cnc_cut_figure(fig, d_info), design_output.ideal_figure(fig, d_info), d_info)

  def apply_3d_constructor(self):
    """ internal method that execute the f_3d_constructor function
    """
    if(self.f_3d_constructor==None):
      print("ERR214: Error, the function f_3d_constructor has not been set!")
      sys.exit(2)
    (assembly_conf, slice3d_conf) = self.f_3d_constructor(self.constraint)
    self.assembly_configurations = assembly_conf
    self.slice3d_configurations = slice3d_conf

  def complete_assembly_conf(self, partial_conf):
    """ prepare an assembly_conf and in particular generate the required outline-figures
    """
    self.apply_2d_constructor()
    #print("dbg243: partial_conf:", partial_conf)
    r_assembly_conf = []
    for i in range(len(partial_conf)):
      one_figure_conf = list(partial_conf[i])
      fig_name = one_figure_conf[0]
      fig_B = design_output.cnc_cut_figure(self.A_figures[fig_name], "complete_assembly_conf_{:s}".format(fig_name))
      one_figure_conf[0] = fig_B
      r_assembly_conf.append(one_figure_conf)
    return(r_assembly_conf)

  def get_fc_obj(self, assembly_name=""):
    """ generate on freecad-object according to the 3d-assembly-configuration
        assembly_name selects the 3d-assembly-configuration
        if assembly_name is empty, the first 3d-assembly-configuration is selected
    """
    self.apply_3d_constructor()
    if(assembly_name==""):
      assembly_name = self.assembly_configurations.keys()[0] # set the first 3d-assembly-configuration per default
    if(not assembly_name in self.assembly_configurations.keys()):
      print("ERR187: Error, the assembly_name {:s} is not in the possible 3d-assembly-configuration".format(assembly_name))
      sys.exit(2)
    #print("dbg245: self.assembly_configurations:", self.assembly_configurations)
    #print("dbg246: assembly_name:", assembly_name)
    r_fc_obj = design_output.figures_to_freecad_assembly(self.complete_assembly_conf(self.assembly_configurations[assembly_name]))
    return(r_fc_obj)

  def write_figure_svg(self, output_file_basename):
    """ write all 2d-figures in svg files
        output_file_basename contains the directory path and the file-basename
    """
    self.get_A_figure() # create the A-figures
    txt_info = self.get_info()
    figs = self.write_2d_figure_list
    if(len(figs)==0):
      figs = self.A_figures.keys()
    for f in figs:
      if(not f in self.A_figures.keys()):
        print("ERR291: Error, f {:s} is not an existing 2d-figures {:s}".format(f, ' '.join(self.A_figures.keys())))
        sys.exit(2)
      design_output.generate_output_file(design_output.cnc_cut_figure(self.A_figures[f], "generate_svg_{:s}".format(f)), "{:s}_{:s}.svg".format(output_file_basename, f), self.figure_heights[f], txt_info)

  def write_figure_dxf(self, output_file_basename):
    """ write all 2d-figures in dxf files
        output_file_basename contains the directory path and the file-basename
    """
    self.get_A_figure() # create the A-figures
    txt_info = self.get_info()
    figs = self.write_2d_figure_list
    if(len(figs)==0):
      figs = self.A_figures.keys()
    for f in figs:
      if(not f in self.A_figures.keys()):
        print("ERR306: Error, f {:s} is not an existing 2d-figures {:s}".format(f, ' '.join(self.A_figures.keys())))
        sys.exit(2)
      design_output.generate_output_file(design_output.cnc_cut_figure(self.A_figures[f], "generate_dxf_{:s}".format(f)), "{:s}_{:s}.dxf".format(output_file_basename, f), self.figure_heights[f], txt_info)

  def write_figure_brep(self, output_file_basename):
    """ write all 2d-figures in brep files
        output_file_basename contains the directory path and the file-basename
    """
    self.get_A_figure() # create the A-figures
    txt_info = self.get_info()
    figs = self.write_3d_figure_list
    if(len(figs)==0):
      figs = self.A_figures.keys()
    for f in figs:
      if(not f in self.A_figures.keys()):
        print("ERR321: Error, f {:s} is not an existing 2d-figures {:s}".format(f, ' '.join(self.A_figures.keys())))
        sys.exit(2)
      design_output.generate_output_file(design_output.cnc_cut_figure(self.A_figures[f], "generate_brep_{:s}".format(f)), "{:s}_{:s}".format(output_file_basename, f), self.figure_heights[f], txt_info)

  def write_assembly_brep(self, output_file_basename):
    """ write all 3d-assembly-configurations in brep files
        output_file_basename contains the directory path and the file-basename
    """
    self.apply_3d_constructor()
    txt_info = self.get_info()
    confs = self.write_3d_conf_list
    if(len(confs)==0):
      confs = self.assembly_configurations.keys()
    for a in confs:
      if(not a in self.assembly_configurations.keys()):
        print("ERR336: Error, a {:s} is not an existing 3d-assembly-configurations {:s}".format(f, ' '.join(self.assembly_configurations.keys())))
        sys.exit(2)
      # (ai_3d_conf, ai_output_filename, ai_brep=True, ai_stl=False, ai_slice_xyz=[])
      design_output.generate_3d_assembly_output_file(self.complete_assembly_conf(self.assembly_configurations[a]), "{:s}_{:s}".format(output_file_basename, a), True, False, self.slice3d_configurations[a]) 

  def apply_cli_with_output_options(self, cli_str=""):
    """ check the argument-output-options and then call apply_cli()
        The argument-output-options are: output_file_basename, simulate_2d, display_2d_figures, return_type
    """
    effective_args = cli_str.split()
    effective_args_in_txt = "{:s} cli_with_output_file_basename string: ".format(self.design_name) + ' '.join(effective_args)
    cwoo_parser = argparse.ArgumentParser(description='Command Line Interface of {:s} with output_file_basename'.format(self.design_name))
    cwoo_parser.add_argument('--output_file_basename','--ofb', action='store', default='', dest='sw_output_file_basename',
      help="If not  the empty_string (the default value), it outputs the (first) gear in file(s) depending on your argument file_extension: .dxf uses mozman dxfwrite, .svg uses mozman svgwrite, no-extension uses FreeCAD and you get .brep and .dxf")
    cwoo_parser.add_argument('--simulate_2d','--s2d', action='store', default='', dest='sw_simulate_2d',
      help="run a 2D-simualtion in a Tk-window")
    cwoo_parser.add_argument('--display_2d_figures','--d2f', action='store_true', default=False, dest='sw_display_2d_figures',
      help="display in Tk-window all the 2D-figures of the design")
    cwoo_parser.add_argument('--return_type', '--rt', action='store', default='', dest='sw_return_type',
      help="select the object to be returned by the function allinone. Depreciated! Use rather the appropriate methods")
    #print("dbg363: effective_args:", effective_args)
    if(('-h' in effective_args)or('--help' in effective_args)):
      cwoo_parser.print_help()
      (oo_args, remaining_args) = cwoo_parser.parse_known_args([])
      remaining_args = effective_args
    else:
      (oo_args, remaining_args) = cwoo_parser.parse_known_args(effective_args)
    #print("dbg322: remaining_args:", remaining_args)
    self.apply_cli(' '.join(remaining_args))
    self.cli_str = effective_args_in_txt # must be set after apply_constraint()
    # generate output files
    if(oo_args.sw_output_file_basename!=''):
      if(re.search('\.svg$', oo_args.sw_output_file_basename)):
        output_file_basename = re.sub('\.svg$', '', oo_args.sw_output_file_basename)
        self.write_figure_svg(output_file_basename)
      elif(re.search('\.dxf$', oo_args.sw_output_file_basename)):
        output_file_basename = re.sub('\.dxf$', '', oo_args.sw_output_file_basename)
        self.write_figure_dxf(output_file_basename)
      else:
        output_file_basename = oo_args.sw_output_file_basename
        self.write_figure_brep(output_file_basename)
        if(self.f_3d_constructor!=None):
          self.write_assembly_brep(output_file_basename)
    # run simulation
    if(oo_args.sw_simulate_2d!=''):
      if(self.f_simulation_2d==None):
        print("ERR268: Error, no simulation function is provided. Can't apply simulate_2d {:s}".format(oo_args.sw_simulate_2d))
        sys.exit(2)
      self.f_simulation_2d(oo_args.sw_simulate_2d)
    # display 2D-figures (the default action)
    if(oo_args.sw_display_2d_figures or ((oo_args.sw_output_file_basename=='')and(oo_args.sw_simulate_2d==''))):
      self.outline_display()
    # select the return value of the function allinone
    r_allinone = 1
    if(oo_args.sw_return_type!=''):
      if(self.f_return_type==None):
        print("ERR277: Error, no return_type function is provided. Can't apply return_type {:s}".format(oo_args.sw_return_type))
        sys.exit(2)
      r_allinone = self.f_return_type(oo_args.sw_return_type, self.constraint)
    return(r_allinone)

  def run_self_test(self):
    """ run the design-self-test
    """
    if(self.self_tests==None):
      print("ERR322: Error, the self_tests list has not been set!")
      sys.exit(2)
    for i in range(len(self.self_tests)):
      print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i+1, self.self_tests[i][0], self.self_tests[i][1]))
      self.apply_cli_with_output_options(self.self_tests[i][1])
    return(1)

  def dump_constraint_file(self, snippet_filename):
    """ write a file containing the complete list of parameters and their default values
    """
    if(self.parser==None):
      print("ERR331: Error, parser has not been set!")
      sys.exit(2)
    constraint_dict = vars(self.parser.parse_args([]))
    py_txt = ""
    for (k,v) in constraint_dict.iteritems():
      py_txt += "\t{:20s}\t= {:s}\n".format(k, str(v))
    print("Generate the python snippet file {:s}".format(snippet_filename))
    ofh = open(snippet_filename, 'w')
    ofh.write("# {:s} generated by cnc25d.bare_design for the design example {:s}\n\n".format(snippet_filename, self.design_name))
    ofh.write(py_txt)
    ofh.close()
    return(1)

  def allinone(self, cli_str=""):
    """ it emulates partially the previous behavior of the design functions
        partially depreciated: use it only to run the self-test or dump the constraint-file
    """
    effective_args = design_help.get_effective_args(cli_str)
    aio_parser = argparse.ArgumentParser(description='AllInOne command Line Interface of {:s}'.format(self.design_name))
    aio_parser.add_argument('--run_self_test','--rst', action='store_true', default=False, dest='sw_run_self_test',
      help="run the design self-test used usually as non-regression-test")
    aio_parser.add_argument('--dump_constraint_file', '--dcf', action='store', default='', dest='sw_dump_constraint_file',
      help="write a python file containing the list of the design constraint. The file can be used as design constraint example")
    if(('-h' in effective_args)or('--help' in effective_args)):
      aio_parser.print_help()
      (aio_args, remaining_args) = aio_parser.parse_known_args([])
      remaining_args = effective_args
    else:
      (aio_args, remaining_args) = aio_parser.parse_known_args(effective_args)
    print("dbg111: start a design")
    r_allinone = 1
    if(aio_args.sw_run_self_test):
      self.run_self_test()
    elif(aio_args.sw_dump_constraint_file!=''):
      self.dump_constraint_file(aio_args.sw_dump_constraint_file)
    else:
      r_allinone = self.apply_cli_with_output_options(' '.join(remaining_args))
    print("dbg999: end of design")
    return(r_allinone)
  
################################################################
# Tests of the bare_design class
################################################################

# import for testing bare_design
#import cnc25d_api # cannot import cnc25d_api because cnc25d_api import bare_design
import importing_freecad
importing_freecad.importing_freecad()
import cnc_outline
#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI
#
import math
import sys, argparse
#
import Part
from FreeCAD import Base
# end of import for testing bare_design

def bare_design_test1():
  """ first test of bare_design
  """

  def cube_constraint_constructor(parser):
    """ define the cube constraint constructor using the argparse description
    """
    parser.add_argument('--length', '-l', action='store', type=float, default=10.0,
      help="set the length of the cube. Default: 10.0")
    parser.add_argument('--width', '-w', action='store', type=float, default=0.0,
      help="set the width of the cube. If equal 0.0, set to length. Default: 0.0")
    parser.add_argument('--smooth_radius', '--sr', action='store', type=float, default=0.0,
      help="set the smooth-radius of the four corners of the cuve base. Default: 0.0")
    parser.add_argument('--height', '--ht', action='store', type=float, default=0.0,
      help="set the height of the cube. If equal 0.0, set to length. Default: 0.0")
    return(parser)

  def cube_constraint_check(c):
    """ check the cube constraint c and set the dynamic default values
    """
    # dynamic default values
    if(c['width']==0):
      c['width'] = c['length']
    if(c['height']==0):
      c['height'] = c['length']
    # check the constraint
    if(c['width']<c['length']*0.1):
      print("ERR129: Error, width {:0.3f} is too small compare to length {:0.3f}".format(c['width'], c['length']))
      sys.exit(2)
    if(c['width']>c['length']*10.0):
      print("ERR132: Error, width {:0.3f} is too big compare to length {:0.3f}".format(c['width'], c['length']))
      sys.exit(2)
    if(c['height']<c['length']*0.1):
      print("ERR135: Error, height {:0.3f} is too small compare to length {:0.3f}".format(c['height'], c['length']))
      sys.exit(2)
    if(c['height']>c['length']*10.0):
      print("ERR138: Error, height {:0.3f} is too big compare to length {:0.3f}".format(c['height'], c['length']))
      sys.exit(2)
    if(c['smooth_radius']>0.4*min(c['length'], c['width'])):
      print("ERR182: Error, smooth_radius {:0.3f} is too big compare to length {:0.3f} or width {:0.3f}".format(c['smooth_radius'], c['length'], c['width']))
      sys.exit(2)
    return(c)

  def cube_figures(c):
    """ construct the cube outlines at the A-format from the constraint c
        It returns a dictionary of figures with outlines in the A-format
    """
    r_figures = {}
    r_height = {}
    #
    cube_base_figure = []
    cube_external_outline_A = [] # the square
    cube_external_outline_A.append((0.0,0.0, c['smooth_radius']))
    cube_external_outline_A.append((0.0+c['length'], 0.0, c['smooth_radius']))
    cube_external_outline_A.append((0.0+c['length'], 0.0+c['width'], c['smooth_radius']))
    cube_external_outline_A.append((0.0, 0.0+c['width'], c['smooth_radius']))
    cnc_outline.outline_close(cube_external_outline_A)
    cube_base_figure.append(cube_external_outline_A)
    #
    r_figures['cube_base'] = cube_base_figure
    r_height['cube_base'] = c['height']
    return((r_figures, r_height))

  def cube_3d(c):
    """ construct the cube-assembly-configuration for 3D-freecad-object from the constraint c
        It returns a dictionary of assembly-configurations
    """
    r_assembly = {}
    r_slice = {}
    #
    simple_cube_assembly = []
    simple_cube_assembly.append(('cube_base', 0.0, 0.0, c['length'], c['width'], c['height'], 'i', 'xy', 0, 0, 0))
    #
    size_xyz = (c['length'], c['width'], c['height'])
    zero_xyz = (0.0, 0.0, 0.0)
    slice_x = [ (i+1)/12.0*size_xyz[0] for i in range(10) ]
    slice_y = [ (i+1)/12.0*size_xyz[1] for i in range(10) ]
    slice_z = [ (i+0.1)/12.0*size_xyz[2] for i in range(10) ]
    slice_xyz = (size_xyz[0], size_xyz[1], size_xyz[2], zero_xyz[0], zero_xyz[1], zero_xyz[2], slice_z, slice_y, slice_x)
    #
    r_assembly['simple_cube'] = simple_cube_assembly
    r_slice['simple_cube'] = slice_xyz
    return((r_assembly, r_slice))

  def cube_info(c):
    """ create the text info related to the cube from the constraint c
    """
    r_txt = """
 length: \t{:0.3f}
 width:  \t{:0.3f}
 height: \t{:0.3f}
 smooth_radius: \t{:0.3f}
 """.format(c['length'], c['width'], c['height'], c['smooth_radius'])
    r_txt += """
cube base area: \t{:0.3f} (mm2)
cube volume:    \t{:0.3f} (mm3)
""".format(c['length']*c['width'], c['length']*c['width']*c['height'])
    return(r_txt)

  def cube_self_test():
    """ set the self_tests for the cube design
    """
    r_tests = [
      ('default cube', ''),
      ('unregular cube', '--length 30.0 --width 20.0 --height 10.0 --smooth_radius 8.0'),
      ('heigh cube', '--length 5.0 --width 5.0 --height 30.0 --smooth_radius 2.0 --output_file_basename test_output/bd_test_test.dxf')]
    return(r_tests)
      


  class cube(bare_design):
    """ simple cube shape to test bare_design
    """
    def __init__(self, constraint={}):
      """ configure the cube design
      """
      self.set_design_name("cube design")
      self.set_constraint_constructor(cube_constraint_constructor)
      self.set_constraint_check(cube_constraint_check)
      self.set_2d_constructor(cube_figures)
      self.set_2d_simulation()
      self.set_3d_constructor(cube_3d)
      self.set_info(cube_info)
      self.set_display_figure_list()
      self.set_2d_figure_file_list()
      self.set_3d_figure_file_list()
      self.set_3d_conf_file_list()
      self.set_allinone_return_type()
      self.set_self_test(cube_self_test())
      self.apply_constraint(constraint)

  # my_cube_constraint
  mcc = {}
  mcc['length']         = 30.0
  mcc['width']          = 10.0
  mcc['height']         = 50.0
  mcc['smooth_radius']  = 4.0

  # cube object
  my_cube = cube(mcc) # create a cube
  my_cube.apply_cli("--length 50") # modify constraint via the cli
  my_cube.apply_constraint(mcc) # modify constraint via a dictionary
  # 1: display the outline
  my_cube.outline_display() # display the outline in a Tk-window
  # 2: alternative to my_cube.outline_display()
  mc_olA = my_cube.get_A_figure([]) # get the outline at the A-format
  mc_olB = my_cube.get_B_figure(['cube_base']) # get the outline at the B-format
  mc_info = my_cube.get_info() # get the text info
  mc_constraint = my_cube.get_constraint() # get the interenal dictionary
  outline_backends.figure_simple_display(mc_olB, design_output.ideal_figure(mc_olA,"cube_overlay"), mc_info) # display the outline in a Tk-window
  # 3: get the freecad-object
  mc_3d = my_cube.get_fc_obj()
  Part.show(mc_3d)
  # 4: output file
  my_cube.write_figure_svg("test_output/bdt1")
  my_cube.write_figure_dxf("test_output/bdt1")
  my_cube.write_figure_brep("test_output/bdt1")
  my_cube.write_assembly_brep("test_output/bdt1")
  # 5: run the cube self tests
  my_cube.run_self_test()
  # 6: dump constraint-file
  my_cube.dump_constraint_file("test_output/bd_constraint.py")
  # 7: backward compatibility
  my_old_cube = my_cube.allinone("--length 15.0 --width 10.0 --smooth_radius 3.0 --output_file_basename test_output/bd_allinone.dxf")
  
################################################################
# bare_desin test command line interface
################################################################

def bare_design_test_cli(ai_args=""):
  """ command line interface to run this script in standalone
  """
  bd_parser = argparse.ArgumentParser(description='CLI to test the bare_design class')
  bd_parser.add_argument('--test1','--t1', action='store_true', default=False, dest='sw_test1',
    help='Run bare_design_test1()')
  effective_args = design_help.get_effective_args(ai_args)
  bd_args = bd_parser.parse_args(effective_args)
  r_bdtc = 0
  #print("dbg111: start testing bare_design.py")
  if(bd_args.sw_test1):
    r_bdtc = bare_design_test1()
  #print("dbg999: end of script")
  return(r_bdtc)

################################################################
# main
################################################################

if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("bare_design.py says hello!\n")
  # select your script behavior
  #bare_design_test_cli()
  bare_design_test_cli("--test1")
  
