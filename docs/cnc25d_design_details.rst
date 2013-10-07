=====================
Cnc25D Design Details
=====================

Cnc25D design usage
===================

From the source repository
--------------------------

Using the design module
^^^^^^^^^^^^^^^^^^^^^^^

Go to the *Cnc25D source repository* and execute the *design script* with or without arguments::
  
  > cd Cnc25D
  > python cnc25D/XYZDesign.py

or::

  > python cnc25D/XYZDesign.py --param_A 50.0 --param_C 30.0

Without arguments, the default command line is used.

When you don't use argument, you can also use *freecad* instead of *python* ::

  > freecad cnc25D/XYZDesign.py

With *freecad*, you can not choose the arguments on the command line because of the conflict with the freecad argument parser. So you have to change the default command line at the end of the design script::

  if __name__ == "__main__":
    FreeCAD.Console.PrintMessage("XYZDesign.py says hello!\n")
    my_xyz = XYZDesign_cli("--param_A 6.0 --param_B 13.0 --return_type freecad_object".split()) # default command line arguments: choose here you argument to run the script with freecad
    try: # depending on xyz_c['return_type'] it might be or not a freecad_object
      Part.show(my_xyz)
      print("freecad_object returned")
    except:
      pass
      #print("return_type is not a freecad-object")
  
The argument *--return_type freecad_object* lets you visualizing the result in FreeCAD.

Using the test-macro
^^^^^^^^^^^^^^^^^^^^

Go to the *Cnc25D source repository*  and execute the *test-macro* without argument::

  > cd Cnc25D
  > python cnc25D/tests/XYZDesign_macro.py

or::

  > freecad cnc25D/tests/XYZDesign_macro.py

You can use those test-macro scripts as *FreeCAD macro* and run them from the FreeCAD GUI. Make sure the *test-macro script* returns a *freecad_object*::

  xyz_x['return_type'] = 'freecad_object'

From the installed Cnc25D package
---------------------------------

After installing the *Cnc25D Python package*, run *cnc25d_example_generator.py* to get the *Cnc25D example scripts*. These *Cnc25D example scripts* are actually a copy of the previous *test-macros*. You can execute them without argument with *python* or *freecad*::

  > cd where/I/have/generated/the/Cnc25D/example/scripts
  > python eg05_XYZDesign_example.py

or::

  > freecad eg05_XYZDesign_example.py

Like with the *test-macro script*, make sure the script returns a *freecad_object*. If not, edit your script and set the following constraint::

  xyz_x['return_type'] = 'freecad_object'

Your script can also be used as a *FreeCAD macro* and can be called from the *FreeCAD GUI*.

Cnc25D design implementation structure
======================================

Template of a Cnc25D design script::

  ################################################################
  # import
  ################################################################
  
  import cnc25d_api
  cnc25d_api.importing_freecad()
  import math
  import sys, argparse
  import Part

  ################################################################
  # XYZDesign dictionary-constraint-arguments default values
  ################################################################
  
  def XYZDesign_dictionary_init():
    """ create and initiate a XYZDesign_dictionary with the default value
    """
    r_xyzd = {}
    r_xyzd['param_A'] = 5.0
    r_xyzd['param_B'] = 10.0
    r_xyzd['param_C'] = 0.0
    r_xyzd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
    # ...
    return(r_xyzd)
  
  ################################################################
  # XYZDesign argparse
  ################################################################
  
  def XYZDesign_add_argument(ai_parser):
    """
    Add arguments relative to the XYZDesign
    This function intends to be used by the XYZDesign_cli and XYZDesign_self_test
    """
    r_parser = ai_parser
    r_parser.add_argument('--param_A','--pa', action='store', type=float, default=5.0, dest='sw_param_A',
      help="Set the param_A. Default: 5.0")
    r_parser.add_argument('--param_B','--pb', action='store', type=float, default=10.0, dest='sw_param_B',
      help="Set the param_B. Default: 10.0")
    r_parser.add_argument('--param_C','--pc', action='store', type=float, default=0.0, dest='sw_param_C',
      help="Set the param_C. If equal to 0.0, the default value is computed. Default: 0.0")
    # ...
    return(r_parser)
  
  ################################################################
  # the most important function to be used in other scripts
  ################################################################
  
  def XYZDesign(ai_constraints):
    """
    The main function of the script.
    It generates a XYZDesign according to the constraint-arguments
    """
    ### check the dictionary-arguments ai_constraints
    xyzdi = XYZDesign_dictionary_init()
    xyz_c = xyzdi.copy()
    xyz_c.update(ai_constraints)
    if(len(xyz_c.viewkeys() & xyzdi.viewkeys()) != len(xyz_c.viewkeys() | xyzdi.viewkeys())): # check if the dictionary xyz_c has exactly all the keys compare to XYZDesign_dictionary_init()
      print("ERR157: Error, xyz_c has too much entries as {:s} or missing entries as {:s}".format(xyz_c.viewkeys() - xyzdi.viewkeys(), xyzdi.viewkeys() - xyz_c.viewkeys()))
      sys.exit(2)
    ### dynamic default value
    if(ai_constraints['param_C']==0):
      xyz_c['param_C'] = xyz_c['param_B']/5
  
    ### generate the XYZDesign figure
    # ...
  
    # display with Tkinter
    if(xyz_c['tkinter_view']):
      print(XYZDesign_parameter_info)
      cnc25d_api.figure_simple_display(xyz_figure, xyz_figure_overlay, XYZDesign_parameter_info)
    # generate output file
    cnc25d_api.generate_output_file(xyz_figure, xyz_c['output_file_basename'], xyz_c['XYZDesign_height'], XYZDesign_parameter_info)
  
    #### return
    if(xyz_c['return_type']=='int_status'):
      r_xyz = 1
    elif(xyz_c['return_type']=='cnc25d_figure'):
      r_xyz = xyz_figure
    elif(xyz_c['return_type']=='freecad_object'):
      r_xyz = cnc25d_api.figure_to_freecad_25d_part(xyz_figure, xyz_c['XYZDesign_height'])
    else:
      print("ERR508: Error the return_type {:s} is unknown".format(xyz_c['return_type']))
      sys.exit(2)
    return(r_xyz)
  
  ################################################################
  # XYZDesign wrapper dance
  ################################################################

  def XYZDesign_argparse_to_dictionary(ai_xyz_args):
    """ convert a XYZDesign_argparse into a XYZDesign_dictionary
    """
    r_xyzd = {}
    r_xyzd['param_A']  = ai_xyz_args.sw_param_A
    r_xyzd['param_B']  = ai_xyz_args.sw_param_B
    r_xyzd['param_C']  = ai_xyz_args.sw_param_c
    #### return
    return(r_xyzd)
  
  def XYZDesign_argparse_wrapper(ai_xyz_args, ai_args_in_txt=""):
    """
    wrapper function of XYZDesign() to call it using the XYZDesign_parser.
    XYZDesign_parser is mostly used for debug and non-regression tests.
    """
    # view the XYZDesign with Tkinter as default action
    tkinter_view = True
    if(ai_xyz_args.sw_simulation_enable or (ai_xyz_args.sw_output_file_basename!='')):
      tkinter_view = False
    # wrapper
    xyzd = XYZDesign_argparse_to_dictionary(ai_xyz_args)
    xyzd['args_in_txt'] = ai_args_in_txt
    xyzd['tkinter_view'] = tkinter_view
    #xyzd['return_type'] = 'int_status'
    r_xyz = XYZDesign(xyzd)
    return(r_xyz)
  
  ################################################################
  # self test
  ################################################################
  
  def XYZDesign_self_test():
    """
    This is the non-regression test of XYZDesign.
    """
    test_case_switch = [
      ["Test_A"           , "--param_A 20.0"],
      ["Test B"           , "--param_B 15.0 --param_C 5.0"],
      ["Advanced Test C"  , "--param_A 10.0 --param_B 8.0 --param_C 15.0"]]
    #print("dbg741: len(test_case_switch):", len(test_case_switch))
    XYZDesign_parser = argparse.ArgumentParser(description='Command line interface for the function XYZDesign().')
    XYZDesign_parser = XYZDesign_add_argument(XYZDesign_parser)
    XYZDesign_parser = cnc25d_api.generate_output_file_add_argument(XYZDesign_parser, 1)
    for i in range(len(test_case_switch)):
      l_test_switch = test_case_switch[i][1]
      print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
      l_args = l_test_switch.split()
      #print("dbg414: l_args:", l_args)
      st_args = XYZDesign_parser.parse_args(l_args)
      r_xyzst = XYZDesign_argparse_wrapper(st_args)
    return(r_xyzst)
  
  ################################################################
  # XYZDesign command line interface
  ################################################################
  
  def XYZDesign_cli(ai_args=None):
    """ command line interface of XYZDesign.py when it is used in standalone
    """
    # XYZDesign parser
    XYZDesign_parser = argparse.ArgumentParser(description='Command line interface for the function XYZDesign().')
    XYZDesign_parser = XYZDesign_add_argument(XYZDesign_parser)
    XYZDesign_parser = cnc25d_api.generate_output_file_add_argument(XYZDesign_parser, 1)
    # switch for self_test
    XYZDesign_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets.')
    effective_args = cnc25d_api.get_effective_args(ai_args)
    effective_args_in_txt = "XYZDesign arguments: " + ' '.join(effective_args)
    xyz_args = XYZDesign_parser.parse_args(effective_args)
    print("dbg111: start making XYZDesign")
    if(xyz_args.sw_run_self_test):
      r_xyz = XYZDesign_self_test()
    else:
      r_xyz = XYZDesign_argparse_wrapper(xyz_args, effective_args_in_txt)
    print("dbg999: end of script")
    return(r_xyz)
  
  ################################################################
  # main
  ################################################################
  
  if __name__ == "__main__":
    FreeCAD.Console.PrintMessage("XYZDesign.py says hello!\n")
    my_xyz = XYZDesign_cli("--param_A 6.0 --param_B 13.0".split())
    try: # depending on xyz_c['return_type'] it might be or not a freecad_object
      Part.show(my_xyz)
      print("freecad_object returned")
    except:
      pass
      #print("return_type is not a freecad-object")
  
