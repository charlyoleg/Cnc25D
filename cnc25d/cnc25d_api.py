# cnc25d_api.py
# the unified interface to use the cnc25d function library
# created by charlyoleg on 2013/07/17
# license: CC BY SA 3.0

"""
cnc25d_api.py provides a unified interface of the cnc25d function library
to be used by the design examples or external scripts
"""

################################################################
# import
################################################################

import importing_freecad
import cnc_cut_outline
import outline_backends
import positioning
import export_2d

################################################################
# api function alias
################################################################

# from importing_freecad
importing_freecad = importing_freecad.importing_freecad

# from cnc_cut_outline
outline_shift_x = cnc_cut_outline.outline_shift_x
outline_shift_y = cnc_cut_outline.outline_shift_y
outline_shift_xy = cnc_cut_outline.outline_shift_xy
cnc_cut_outline = cnc_cut_outline.cnc_cut_outline

# from outline_backends
outline_arc_line = outline_backends.outline_arc_line
outline_circle = outline_backends.outline_circle
Two_Canvas =  outline_backends.Two_Canvas

# from positioning
place_plank = positioning.place_plank

# from export_2d
export_to_dxf = export_2d.export_to_dxf
export_to_svg = export_2d.export_to_svg
export_xyz_to_dxf = export_2d.export_xyz_to_dxf


################################################################
# function combinations
################################################################

def cnc_cut_outline_fc(*args, **kwargs):
  """ Associate cnc_cut_outline() with outline_arc_line() in mode freecad
  """
  return(outline_arc_line(cnc_cut_outline(*args, **kwargs), 'freecad'))


