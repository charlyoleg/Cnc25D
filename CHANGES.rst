###############
Release History
###############

0.1.3 (2013-08-13)
==================

* New API function outline_arc_line() converts an outline defined by points into an outline of four possible formats: Tkinter display, svgwrite, dxfwrite or FreeCAD Part.
* API function cnc_cut_outline() supports smoothing and enlarging line-line, line-arc and arc-arc corners.
* Additional API functions such as outline_rotate(), outline_reverse()
* All Cnc25D API function are gathered in the cnc25d_api module
* Box wood frame design example generates also BRep in addition to STL and DXF.
* Box wood frame design example support router_bit radius up to 4.9 mm with all others parameters at default.
* LGPL v3 is applied to this Python package.


0.1.2 (2013-06-18)
==================

* Add the box_wood_frame design example


0.1.1 (2013-06-05)
==================

* Experimenting distribute_

.. _distribute : http://pythonhosted.org/distribute


0.1.0 (2013-06-04)
==================

* Initial release


