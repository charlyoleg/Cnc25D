==============================
Cnc25D API Outline Utilization
==============================

Transformations at the figure-level
===================================

The description of a 2.5D part can require several outlines. Typically one outline is the outer shape of the part, the other outlines are holes in this part. In the Cnc25D API, a list of outlines is called a *figure*. After creating such a list, you can directly display this *figure*, write it in a file or extrude it in 3D with FreeCAD.

Display a figure in a GUI
=========================

::

  cnc25d_api.figure_simple_display(graphic_figure, overlay_figure)
  return 0

*graphic_figure* is a list of format-B outlines to be displayed in *red*. *overlay_figure* is optional and could be used to display an other figure in *orange* when the overlay is active. A common practice it to set *graphic_figure* with the outlines returned by *cnc_cut_outline()* and to set *overlay_figure* with outlines returned by *ideal_outline()*. So you can see your created format-A outlines and the final format-B outlines.
Notice that you can also directly use format-A or format-C without converting them in format-B with *ideal_outline()*, but you will get a *warning* message.

If you want more control on the figure display like new *colors*, *width* or *animations*, then you should use *outline_arc_line()* and *Two_Canvas* directly.

Write a figure in a SVF file
============================

::

  cnc25d_api.write_figure_in_svg(figure, filename)
  return 0

Write a figure in a DXF file
============================

::

  cnc25d_api.write_figure_in_dxf(figure, filename)
  return 0


Extrude a figure using FreeCAD
==============================

::

  cnc25d_api.figure_to_freecad_25d_part(figure, extrusion_height)
  return FreeCAD Part Object

To create a 3D part from a *figure*, the function *figure_to_freecad_25d_part()* makes the assumption that the first outline is the *outer line* and the remaining outlines are holes.




Detailed transformations at the outline-level
=============================================

After getting a *Cnc25D format B outline* from the cnc_cut_outline() function, you probably want to use this outline in CAD_ tools. The function *cnc25d_api.outline_arc_line()* lets you transform the *Cnc25D format-B outline* into one of this four formats: *freecad*, *svgwrite*, *dxfwrite*, *tkinter*.

.. _CAD : https://en.wikipedia.org/wiki/Comparison_of_CAD_editors_for_AEC

::

  cnc25d_api.outline_arc_line(outline-B, backend) => Tkinter or svgwrite or dxfwrite or FreeCAD stuff
    with backend=['freecad', 'svgwrite', 'dxfwrite', 'tkinter']
  
freecad
-------

*outline_arc_line(outline_B, 'freecad')* returns *FreeCAD Part.Shape* object that can be used easily in the classic *FreeCAD* workflow::

  my_part_shape = cnc25d_api.outline_arc_line(my_outline_B, 'freecad')
  my_part_face = Part.Face(Part.Wire(my_part_shape.Edges))
  my_part_solid = my_part_face.extrude(Base.Vector(0,0,20))

Notice that *FreeCAD* conserve the *arc* geometrical entity during its complete workflow. So after extruding the outline, slicing the part and then projecting it again in a DXF file, you still get the *arcs* you have designed in your original outline.


svgwrite
--------

A *Cnc25D format B outline* is a 2D vectorial shape that can be transposed in a SVG_ file. *SVG file* is one of the usual input format for the 3-axis CNC tool chain. This snippet let you dump the *Cnc25D format B outline* in a *SVG* file::

  import svgwrite
  my_outline_B = [ .. ]
  object_svg = svgwrite.Drawing(filename = "my_ouline.svg")
  svg_outline = cnc25d_api.outline_arc_line(my_outline_B, 'svgwrite')
  for one_line_or_arc in svg_outline:
    object_svg.add(one_line_or_arc)
  object_svg.save()

*Cnc25D* relies on the *Python package* svgwrite_ from **mozman**. Use Inkscape_ to review the generated *SVG* file.

.. _svgwrite : http://pythonhosted.org/svgwrite/
.. _Inkscape : http://inkscape.org/

**Warning:** The SVG_ format supports the *arc* graphical object but the Python package svgwrite_ has not implemented yet the *arc* constructor. So *Cnc25D* transform each *arc* of the outline into a series of small segments. This might be an issue for certain *CNC tool chain* or for some designs.

dxfwrite
--------

A *Cnc25D format B outline* is a 2D vectorial shape that can be transposed in a DXF_ file::

  import dxfwrite
  my_outline_B = [ .. ]
  object_dxf = DXFEngine.drawing("my_outline.dxf")
  #object_dxf.add_layer("my_dxf_layer")
  dxf_outline = cnc25d_api.outline_arc_line(my_outline_B, 'dxfwrite')
  for one_line_or_arc in dxf_outline:
    object_dxf.add(one_line_or_arc)
  object_dxf.save()

*Cnc25D* relies on the *Python package* dxfwrite_ from **mozman**. Use LibreCAD_ to review the generated *DXF* file.

.. _dxfwrite : http://pythonhosted.org/svgwrite/
.. _LibreCAD : http://librecad.org

**Warning:** Like previously, the DXF_ format supports the *arc* graphical object but the Python package dxfwrite_ has not implemented yet the *arc* constructor. So *Cnc25D* transform each *arc* of the outline into a series of small segments. This might be an issue for certain *CNC tool chain* or for some designs.

tkinter
-------

During the early phase of the design, you just need to view the outline (that still might be under-construction) without using the powerful *FreeCAD* or dumping files. This is the purpose of the *Tkinter GUI*. Check the design example *cnc25d_api_example.py* generated by the binary *cnc25d_example_generator.py* or check the file *cnc25d/tests/cnc25d_api_macro.py* to see how to implement this small *graphic user interface*.

::

  cnc25d_api.Two_Canvas(Tkinter.Tk()) # object constructor


.. _DXF : http://en.wikipedia.org/wiki/AutoCAD_DXF
.. _SVG : http://www.w3.org/Graphics/SVG/


