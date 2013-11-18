###############
Release History
###############


0.1.9 (2013-12-01)
==================

* motor_lid
* gearlever
* gear_train  
* hexa_bone

0.1.8 (2013-11-07)
==================

* add crenels to the gearwheel
* epicyclic-gearing
* axle_lid

0.1.7 (2013-10-07)
==================

* unify the test-environment of the macro-scripts
* use python-dictionary as function-argument for designs with many parameters
* gearring (aka annulus)
* gearbar (aka rack)
* split_gearwheel

0.1.6 (2013-09-25)
==================

* Use arc primitives for generating DXF and SVG files
* finalization of gear_profile.py and gearwheel.py


0.1.5 (2013-09-18)
==================

* GPL v3 is applied to this Python package.


0.1.4 (2013-09-11)
==================

* Python package created with setuptools (instead of distribute)
* add API function smooth_outline_c_curve() approximates a curve defined by points and tangents with arcs.
* integrate circle into the format-B
* add API functions working at the *figure-level*: figure_simple_display(), figure_to_freecad_25d_part(), ..
* remove API function cnc_cut_outline_fc()
* gear_profile.py generates and simulates gear-profiles
* gearwheel.py


0.1.3 (2013-08-13)
==================

* New API function outline_arc_line() converts an outline defined by points into an outline of four possible formats: Tkinter display, svgwrite, dxfwrite or FreeCAD Part.
* API function cnc_cut_outline() supports smoothing and enlarging line-line, line-arc and arc-arc corners.
* Additional API functions such as outline_rotate(), outline_reverse()
* All Cnc25D API function are gathered in the cnc25d_api module
* Box wood frame design example generates also BRep in addition to STL and DXF.
* Box wood frame design example support router_bit radius up to 4.9 mm with all others parameters at default.


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


