# cnc25d_api.py
# the unified interface to use the cnc25d function library
# created by charlyoleg on 2013/07/17
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
cnc25d_api.py provides a unified interface of the cnc25d function library
to be used by the design examples or external scripts
"""

################################################################
# import
################################################################

import importing_freecad
import cnc_outline
import outline_backends
import positioning
import export_2d
import design_output
import design_help
import bare_design

################################################################
# api function alias
################################################################

# from importing_freecad
importing_freecad = importing_freecad.importing_freecad

# from cnc_cut_outline
outline_shift_x = cnc_outline.outline_shift_x
outline_shift_y = cnc_outline.outline_shift_y
outline_shift_xy = cnc_outline.outline_shift_xy
outline_rotate = cnc_outline.outline_rotate
outline_close = cnc_outline.outline_close
outline_reverse = cnc_outline.outline_reverse
cnc_cut_outline = cnc_outline.cnc_cut_outline
smooth_outline_c_curve = cnc_outline.smooth_outline_c_curve
smooth_outline_b_curve = cnc_outline.smooth_outline_b_curve
ideal_outline = cnc_outline.ideal_outline

# from outline_backends
outline_arc_line = outline_backends.outline_arc_line
#outline_circle = outline_backends.outline_circle # included now in outline_arc_line()
Two_Canvas =  outline_backends.Two_Canvas
figure_simple_display = outline_backends.figure_simple_display
write_figure_in_svg = outline_backends.write_figure_in_svg
write_figure_in_dxf = outline_backends.write_figure_in_dxf
figure_to_freecad_25d_part =  outline_backends.figure_to_freecad_25d_part

# from positioning
place_plank = positioning.place_plank

# from export_2d
export_to_dxf = export_2d.export_to_dxf
export_to_svg = export_2d.export_to_svg
export_xyz_to_dxf = export_2d.export_xyz_to_dxf

# from design_help
mkdir_p = design_help.mkdir_p
interpretor_is_freecad = design_help.interpretor_is_freecad
get_effective_args = design_help.get_effective_args

# from design_output
generate_output_file_add_argument = design_output.generate_output_file_add_argument
get_output_file_suffix = design_output.get_output_file_suffix
generate_output_file = design_output.generate_output_file
freecad_object_output_file = design_output.freecad_object_output_file
generate_3d_assembly_output_file = design_output.generate_3d_assembly_output_file
rotate_and_translate_figure = design_output.rotate_and_translate_figure
flip_rotate_and_translate_figure = design_output.flip_rotate_and_translate_figure
cnc_cut_figure =  design_output.cnc_cut_figure
ideal_figure = design_output.ideal_figure
figures_to_freecad_assembly = design_output.figures_to_freecad_assembly

# from bare_design
bare_design = bare_design.bare_design

################################################################
# function combinations
################################################################

#def cnc_cut_outline_fc(*args, **kwargs):
#  """ Associate cnc_cut_outline() with outline_arc_line() in mode freecad
#  """
#  return(outline_arc_line(cnc_cut_outline(*args, **kwargs), 'freecad'))


