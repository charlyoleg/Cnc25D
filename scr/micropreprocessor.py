#!/usr/bin/python

# -*- coding:utf-8 -*-

# micropreprocessor.py
# read a python script, process the include statement, write the output python script
# created by charlyoleg on 2013/06/06
# license: CC BY SA 3.0

"""
micropreprocessor.py reads a valid python script, which name ends with '_src.py'
it replaces each include statements looking like '#include "path/to/a/file"' by the file and warns for all lines containing the word include with an invalid syntax.
Finally, it writes the output python script with the same basename as the input script.
"""

##########################################################################
# import and global function definiton
##########################################################################

import sys, re, os

micropreprocessor_usage = """
micropreprocessor.py usage:
> micropreprocessor.py MyInputScript_src.py
"""

##########################################################################
# functions
##########################################################################

def get_output_filename(ai_input_file_name):
  """
  Deduces the output_filename from the input_filename
  """
  r_output_filename =''
  if(re.match(r'_src\.py$',ai_input_file_name)):
    r_output_filename = re.sub(r'_src\.py$', '.py', ai_input_file_name)
  else:
    print("ERR014: Error, the input file name convention '_src.py' is not respected!")
    sys.exit(1)
  return(r_output_filename)

def process_include(ai_txt):
  """
  Looks for include statements and replaces them by the appropriate file
  """
  r_out_txt = ''
  line_nb = 0
  for i_line in ai_txt:
    line_nb += 1
    if(re.match(r'include', i_line)):
      if(re.match(r'^\s*#include ".*".*$', i_line)):
        include_path = re.sub(r'^\s*#include "\(.*\(".*$', '\1', i_line)
        print("dbg414: include_path:", include_path)
        if(os.path.exists(include_path)):
          ifh = open(include_path, 'r')
          r_out_txt += ifh.read()
          ifh.close()
        else:
          print("ERR701: Error, the file {:s} doesn't exist!".format(include_path))
          sys.exit(1)
      else:
        print("WARN015: Warning, ambigous include statment ignore at line %d"%line_nb)
        r_out_txt += i_line
    else:
      r_out_txt += i_line
  return(r_out_txt)

##########################################################################
# main function
##########################################################################

def micropreprocessor(ai_args):
  """
  main function of micropreprocessor.py
  """
  if(len(ai_args) != 1):
    print("ERR233: Error, micropreprocessor takes exactly one argument. %d arguments given!"%len(ai_args))
    print(micropreprocessor_usage)
    sys.exit(1)
  input_filename = ai_args[0]
  if(!os.path.exists(input_filename)):
    print("ERR774: Error, the input file {:s} doesn't exist!".format(input_filename))
    sys.exit(1)
  ifh = open(include_path, 'r')
  input_content = ifh.read()
  ifh.close()
  output_filename = get_output_filename(input_filename)
  output_content = process_include(input_content)
  ofh = open(f_txt, 'w')
  ofh.write(output_content)
  ofh.close()
  print("The outfile {:s} has been writen :)".format(output_filename))

##########################################################################
# main
##########################################################################

if __name__ == "__main__":
  micropreprocessor(sys.argv[1:])

