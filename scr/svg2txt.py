#!/usr/bin/env python
# -*- coding:utf-8 -*-

# svg2txt.py
# extracts text from svg files
# created by charlyoleg on 2013/07/18
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


help_msg = """
svg2txt.py extracts text from svg files.
It reads one or several svg files and writes one or several text files.
> svg2txt.py svg_file1.svg
> svg2txt.py svg_file1.svg svg_file2.svg svg_file3.svg
"""

svg2txt_xsl = """
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" indent="no" encoding="utf-8"/>
</xsl:stylesheet>
"""

from lxml import etree
import sys
import re

#def transform(xmlPath, xslPath):
def transform_svg2txt(xmlPath):
  # read xsl file
  #xslRoot = etree.fromstring(open(xslPath).read())
  #xslRoot = etree.fromstring(svg2txt_xsl)
  xslRoot = etree.XML(svg2txt_xsl)

  transform = etree.XSLT(xslRoot)

  # read xml
  #xmlRoot = etree.fromstring(open(xmlPath).read())
  xmlRoot = etree.XML(open(xmlPath, 'r').read())

  # transform xml with xslt
  transRoot = transform(xmlRoot)
  #print("dbg506: transRoot:", str(transRoot))
  #print("dbg507: transRoot.tostring:", etree.tostring(transRoot))

  # return transformation result
  #return etree.tostring(transRoot)
  return str(transRoot)

if __name__ == '__main__':
  #print("dbg101: sys.argv:", sys.argv)
  if(len(sys.argv)==1):
    print("%s"%help_msg)
    print("Nothing done!\n")
  else:
    for f_svg in sys.argv[1:]:
      print("Processing svg file: %s"%(f_svg))
      f_txt = re.sub('\.svg','', f_svg) + ".txt"
      #print(transform_svg2txt('./s0101m.mul0.xml', './tipitaka-latn.xsl'))
      txt_content = transform_svg2txt(f_svg)
      #txt_content = "abc"
      #print("dbg501: txt_content:", txt_content)
      output_file_handler = open(f_txt, 'w')
      output_file_handler.write(txt_content)
      output_file_handler.close()
      print("and outputs text file: %s"%(f_txt))


