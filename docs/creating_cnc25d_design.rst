========================
Creating a Cnc25D Design
========================

You can use one of the existing :doc:`Cnc25D Designs<cnc25d_designs>` or create your own *Cnc25D design* using the :doc:`Cnc25D API<cnc25d_api_overview>`. To create your own *Cnc25D design*, you can use your own *ad-hoc* way like in the :doc:`box_wood_frame_design` variant *box_wood_frame_ng.py* or use the *recommended* way using the *class bare_design* as explained in this page.


Design Script Example
=====================

*ABC* is the name of our *Cnc25D design* example.

.. code-block:: python

  import cnc25d_api
  cnc25d_api.importing_freecad()
  import Part           # to show-up 3D in FreeCAD
  import sys            # to exit on error
  import argparse       # to define the ABC_design constraint
  import math           # usually useful to calcule point coordinates

  def ABC_constraint_constructor(parser):
    """ define the ABC constraint constructor using the argparse description
    """
    parser.add_argument('--length_A', '-a', action='store', type=float, default=10.0,
      help="set the length_A of ABC. Default: 10.0")
    parser.add_argument('--length_B', '-b', action='store', type=float, default=0.0,
      help="set the length_B of ABC. If equal 0.0, set to length_A. Default: 0.0")
    parser.add_argument('--smooth_radius', '--sr', action='store', type=float, default=0.0,
      help="set the smooth-radius of the corners of ABC. Default: 0.0")
    return(parser) # return an argparse object

  def ABC_constraint_check(c):
    """ check the ABC constraint c and set the dynamic default values
    """
    # dynamic default values
    if(c['length_B']==0):
      c['length_B'] = c['length_A']
    # check the constraint
    if(c['length_B']<c['length_A']*0.1):
      print("ERR129: Error, length_B {:0.3f} is too small compare to length_A {:0.3f}".format(c['length_B'], c['length_A']))
      sys.exit(2)
    return(c) # return a dictionary

  def ABC_figures(c):
    """ construct the ABC 2D-figure-outlines at the A-format from the constraint c
        It returns a dictionary of figures with outlines in the A-format
    """
    r_figures = {}
    r_height = {}
    #
    ABC_base_figure = []
    ABC_external_outline_A = [] # the square
    ABC_external_outline_A.append((0.0,0.0, c['smooth_radius']))
    ABC_external_outline_A.append((0.0+c['length_A'], 0.0, c['smooth_radius']))
    ABC_external_outline_A.append((0.0+c['length_A'], 0.0+c['length_B'], c['smooth_radius']))
    ABC_external_outline_A.append((0.0, 0.0+c['length_B'], c['smooth_radius']))
    cnc25d_api.outline_close(ABC_external_outline_A)
    ABC_base_figure.append(ABC_external_outline_A)
    #
    r_figures['ABC_base'] = ABC_base_figure
    r_height['ABC_base'] = c['length_A']
    return((r_figures, r_height)) # return a tuple of two dictionaries

  def ABC_3d(c):
    """ construct the ABC-assembly-configuration for 3D-freecad-object from the constraint c
        It returns a dictionary of assembly-configurations
    """
    r_assembly = {}
    r_slice = {}
    #
    simple_abc_assembly = []
    simple_abc_assembly.append(('ABC_base', 0.0, 0.0, c['length_A'], c['length_B'], c['length_A'], 'i', 'xy', 0, 0, 0))
    #
    size_xyz = (c['length_A'], c['length_B'], c['length_A'])
    zero_xyz = (0.0, 0.0, 0.0)
    slice_x = [ (i+1)/12.0*size_xyz[0] for i in range(10) ]
    slice_y = [ (i+1)/12.0*size_xyz[1] for i in range(10) ]
    slice_z = [ (i+0.1)/12.0*size_xyz[2] for i in range(10) ]
    slice_xyz = (size_xyz[0], size_xyz[1], size_xyz[2], zero_xyz[0], zero_xyz[1], zero_xyz[2], slice_z, slice_y, slice_x)
    #
    r_assembly['abc_assembly_conf1'] = simple_abc_assembly
    r_slice['abc_assembly_conf1'] = slice_xyz
    return((r_assembly, r_slice)) # return a tuple of two dictionaries

  def ABC_info(c):
    """ create the text info related to the ABC from the constraint c
    """
    r_txt = """
  length_A: \t{:0.3f}
  length_B:  \t{:0.3f}
  smooth_radius: \t{:0.3f}
  """.format(c['length_A'], c['length_B'], c['smooth_radius'])
    return(r_txt) # return a string-text

  def ABC_self_test():
    """ set the self_tests for the ABC-design
    """
    r_tests = [
      ('default abc', ''),
      ('unregular abc', '--length_A 30.0 --length_B 20.0 --smooth_radius 8.0'),
      ('heigh abc', '--length_A 5.0 --length_B 5.0 --smooth_radius 2.0 --output_file_basename test_output/height_abc.dxf')]
    return(r_tests) # return a list of 2-tuples
      
  class ABC(bare_design):
    """ ABC design
    """
    def __init__(self, constraint={}):
      """ configuration of the ABC design
      """
      self.set_design_name("ABC_design")
      self.set_constraint_constructor(ABC_constraint_constructor)
      self.set_constraint_check(ABC_constraint_check)
      self.set_2d_constructor(ABC_figures)
      self.set_2d_simulation()
      self.set_3d_constructor(ABC_3d)
      self.set_info(ABC_info)
      self.set_display_figure_list()
      self.set_2d_figure_file_list()
      self.set_3d_figure_file_list()
      self.set_3d_conf_file_list()
      self.set_allinone_return_type()
      self.set_self_test(ABC_self_test())
      self.apply_constraint(constraint)


  if __name__ == "__main__":
    my_abc = ABC()
    my_abc.allinone("--length_A 50.0 --length_B 30.0 --output_file_basename test_output/abc.dxf")
    if(cnc25d_api.interpretor_is_freecad()):
      Part.show(my_abc.get_fc_obj('abc_assembly_conf1'))


Design Setup
============

set_design_name
_______________

Argument:

  - *string*: name of the design. It will be reused in many information and debug log.

This method is mandatory and must be called at the beginning of __init__() (a.k.a. design configuration).

set_constraint_constructor
__________________________

set_constraint_check
____________________

set_2d_constructor
__________________

set_2d_simulation
_________________

set_3d_constructor
__________________

set_info
________


set_display_figure_list
_______________________

set_2d_figure_file_list
_______________________

set_3d_figure_file_list
_______________________

set_3d_conf_file_list
_____________________

set_allinone_return_type
________________________

set_self_test
_____________

apply_constraint
________________

Argument:

  - *dictionary* containing all or a sub-set of the design-constraint

This let you instantiating a design and applying directly some constraint.

Alternatively, you can use *apply_external_constraint* that accepts also unknown constraint.

Design Usage
============

apply_constraint
________________

apply_external_constraint
_________________________

apply_cli
_________

outline_display
_______________

get_A_figure
____________

get_B_figure
____________

apply_2d_constructor
____________________


apply_3d_constructor
____________________


get_info
________

get_constraint
______________

get_fc_obj
__________

write_figure_svg
________________

write_figure_dxf
________________

write_figure_brep
_________________

write_assembly_brep
___________________

run_self_test
_____________

dump_constraint_file
____________________

allinone
________

Design Script Complete Template
===============================






