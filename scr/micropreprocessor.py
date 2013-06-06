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
  if(re.search(r'_src\.py$', ai_input_file_name)):
    r_output_filename = re.sub(r'_src\.py$', '.py', ai_input_file_name)
  else:
    print("ERR014: Error, the input file name convention '_src.py' is not respected!")
    sys.exit(1)
  r_input_dir = os.path.dirname(ai_input_file_name)
  if(r_input_dir==''):
    r_input_dir='.'
  return(r_output_filename, r_input_dir)

def process_include(ai_txt, ai_input_dir):
  """
  Looks for include statements and replaces them by the appropriate file
  """
  r_out_txt = ''
  txt_per_line = ai_txt.splitlines()
  line_nb = 0
  for i_line in txt_per_line:
    line_nb += 1
    #print("dbg 101: {:d} : {:s}".format(line_nb, i_line))
    if(re.search(r'include', i_line)):
      if(re.search(r'^\s*#include ".*".*$', i_line)):
        include_path = re.sub(r'^.*include\s*"', '', i_line)
        include_path = re.sub(r'".*$', '', include_path)
        include_path = ai_input_dir + '/' + include_path
        #print("dbg414: include_path:", include_path)
        if(os.path.exists(include_path)):
          print("include file {:s}".format(include_path))
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
    r_out_txt += '\n'
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
  if(not os.path.exists(input_filename)):
    print("ERR774: Error, the input file {:s} doesn't exist!".format(input_filename))
    sys.exit(1)
  ifh = open(input_filename, 'r')
  input_content = ifh.read()
  ifh.close()
  (output_filename, input_dir) = get_output_filename(input_filename)
  output_content = process_include(input_content, input_dir)
  ofh = open(output_filename, 'w')
  ofh.write(output_content)
  ofh.close()
  print("The outfile {:s} has been writen :)".format(output_filename))

##########################################################################
# main
##########################################################################

if __name__ == "__main__":
  micropreprocessor(sys.argv[1:])

