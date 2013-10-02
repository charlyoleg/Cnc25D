# bug_dxf_arc.py
# the macro to debug the disappearing dxf arcs.
# created by charlyoleg on 2013/10/02
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
Investigating the disappearing DXF arcs
On 2013/10/02, the bug is fixed
"""

################################################################
# import
################################################################

import importing_cnc25d # give access to the cnc25d package
from cnc25d import cnc25d_api
#cnc25d_api.importing_freecad()
#print("FreeCAD.Version:", FreeCAD.Version())

import math
import sys
#
from cnc25d import cnc25d_design
#
import Part

    
################################################################
#  DXF arcs
################################################################

# precision
radian_epsilon = math.pi/1000

# parameters
iteration_nb = 10
length = 3.0
maximal_height = 0.04
height_space = 3.0*maximal_height

# internal parameters
height_incr = float(maximal_height)/iteration_nb

line_arc_figure = []
for i in range(2*iteration_nb):
  y = i*height_space
  yd = (i-iteration_nb)*height_incr
  if(yd!=0):
    one_outline = ((0, y), (length, y), (1.5*length, y+yd, 2*length, y))
  line_arc_figure.append(one_outline)
# no bug with line_arc_figure

curve_c_list = []
#curve_c_list.append(((159.98151030973634, 2.4323566793799003, 2.581103508182059), (148.21981244670462, 8.511720678292365, 2.7571797775160896), (139.54941918366882, 11.223172702078283, 2.933256046850122)))
#curve_c_list.append(((138.83335837113063, 18.03603624395383, 0.41777611697899175), (146.75054016395106, 22.49091265889753, 0.5938523863130225), (156.99124586112094, 30.88282245801178, 0.7699286556470533)))
#curve_c_list.append(((155.97981508135746, 35.641230158140374, 2.7905430184213778), (143.21116768796654, 39.14235097807352, 2.9666192877554103), (134.16650074547297, 39.991875146271866, 3.142695557089441)))
#curve_c_list.append(((132.04961360140717, 46.50698385962108, 0.6272156272183107), (138.86756508881277, 52.510585189520754, 0.8032918965523415), (147.13971064079655, 62.84827406176453, 0.979368165886374)))
curve_c_list.append(((145.16105345972858, 67.29241085339282, 2.9999825286606985), (131.94350769783776, 68.06227271427393, 3.1760587979947292), (122.91986242240063, 67.01274074426519, 3.35213506732876)))
#curve_c_list.append(((119.49466707295448, 72.94535311535454, 0.8366551374576296), (124.91541105878456, 80.23529317361815, 1.0127314067916622), (130.85746401080218, 92.06695450953949, 1.188807676125693)))
#curve_c_list.append(((127.99805724189297, 96.00259028953901, 3.2094220389000174), (114.90928328611828, 94.00754653384051, 3.385498308234048), (106.30103627652832, 91.10482800892721, 3.5615745775680807)))
#curve_c_list.append(((101.71723019438343, 96.1956604093075, 1.0460946476969504), (105.50385415484162, 104.45333383437541, 1.2221709170309811), (108.85611827975636, 117.26186725898447, 1.3982471863650119)))
#curve_c_list.append(((105.24093171976327, 120.51699585849344, 3.4188615491393364), (92.8529717988778, 115.84423947162142, 3.594937818473369), (85.03634475640621, 111.21519712013114, 3.7710140878073997)))

curve_figure = []
for i in range(len(curve_c_list)):
  curve_figure.append(cnc25d_api.smooth_outline_c_curve(curve_c_list[i], radian_epsilon, 0, "bug_dxf_arc"))

arc_outline1 = ((145.16105345972858, 67.29241085339282), (141.6992073306823, 67.71248119850708, 138.22285460617988, 67.98781635950473), (135.08404356534385, 68.0977769789459, 131.94350769783776, 68.06227271427393), (129.50007306219516, 67.9282460984374, 127.06410626967998, 67.69500429649403), (124.9839019702478, 67.40296694443323, 122.91986242240063, 67.01274074426519))
arc_outline2 = ((145, 67), (138.22285460617988, 67.98781635950473), (135.08404356534385, 68.0977769789459, 131.94350769783776, 68.06227271427393), (127, 67))
arc_outline3 = ((138, 68), (131.94350769783776, 68.06227271427393), (129.50007306219516, 67.9282460984374, 127.06410626967998, 67.69500429649403), (123, 67)) # here is the bug
arc_figure = []
arc_figure.append(arc_outline3)

#dxf_figure = line_arc_figure
#dxf_figure = curve_figure
dxf_figure = arc_figure
cnc25d_api.generate_output_file(dxf_figure, "test_output/bug_dxf_arc.dxf", 10.0, "hello")


