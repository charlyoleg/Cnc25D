==============
Cnc25D Designs
==============

Cnc25D design introduction
==========================

In addition to the Cnc25D API functions, the *Cnc25D Python package* includes also several parametric designs. The design parameters are called *constraints* and are set via a dictionary. Most of the constraints are not mandatory and if you don't set some constraints, their default values are used. Use the files provided by the *cnc25d_example_generator.py* as template to generate one of the *Cnc25D designs*. Depending on the *constraints* *output_file_basename* and *return_type*,  you can generate *.dxf*, *.svg* or *.brep* files or include the *Cnc25D Design- as *Part-object* in your FreeCAD macro. For more information about *how to use the Cnc25D designs* read the section :doc:`cnc25d_design_details`.

Cnc25D design list
==================

* :doc:`box_wood_frame_design`
* :doc:`gear_profile_function`
* :doc:`gearwheel_design`
* :doc:`gearring_design`
* :doc:`gearbar_design`
* :doc:`split_gearwheel_design`
* :doc:`epicyclic_gearing_design`
* :doc:`axle_lid_design`
* :doc:`motor_lid_design`
* :doc:`bell_design`
* :doc:`bagel_design`
* :doc:`bell_bagel_assembly`
* :doc:`crest_design`
* :doc:`cross_cube_design`

Cnc25D design overview
======================

Box_wood_frame
--------------

The :doc:`box_wood_frame_design` is a piece of furniture. Its particularity is that its top-shape and its bottom-shape are complementary. So, you can pile-up your boxes.

.. image:: images/box_wood_frame_3d.png

Gear_profile
------------

The :doc:`gear_profile_function` generates the gear-profile outline. You can also simulate this outline with a second gear-profile to make sure it works as you wish it. The gear-profile itself is not a 3D part but a simple outline. You can use this outline to create a complete 3D part.

.. image:: images/gear_profile_3d.png

Gearwheel
---------

The :doc:`gearwheel_design` is a complete gearwheel part (a.k.a. spur). You can specify the number of gear-teeth, the number of legs, the size of the axle and much more.

.. image:: images/gearwheel_3d.png

Gearring
--------

The :doc:`gearring_design` is a complete gearring part (a.k.a. annulus). You can use it to create your epicyclic gear system.

.. image:: images/gearring_3d.png

Gearbar
-------

The :doc:`gearbar_design` is a complete rack part.

.. image:: images/gearbar_3d.png

Split_gearwheel
---------------

The :doc:`split_gearwheel_design` generates several 3D parts that can be assembled to create a complete gearwheel. The split gearwheel lets you make large gearwheel by making smaller sub parts and then assembling them.

.. image:: images/split_gearwheel_3d.png


Epicyclic_gearing
-----------------

The :doc:`epicyclic_gearing_design` is a complete epicyclic gearing system. You can use it to increase the torque (and decreasing the rotation speed).

.. image:: images/epicyclic_gearing_3d.png

Axle_lid
--------

The :doc:`axle_lid_design` is a axle-lid design kit. You can use it to complete the epicyclic_gearing design.

.. image:: images/axle_lid_3d.png

Motor_lid
---------

The :doc:`motor_lid_design` is an extension of the axle-lid design kit to mount an electrical motor. You can use it to complete the epicyclic_gearing design.

.. image:: images/motor_lid_3d.png

Bell
----

The :doc:`bell_design` is the extremity of a *gimbal* system. You can complete is with a *bagel* and a *cross_cube* to get a complete *gimbal* system.

.. image:: images/bell_3d.png

Bagel
-----

The :doc:`bagel_design` is the axle-guidance of the *bell* piece.

.. image:: images/bagel_3d.png

Bell_bagel_assembly
-------------------

The :doc:`bell_bagel_assembly` is the assembly of a *bell* piece and two *bagels*.

.. image:: images/bell_bagel_assembly_3d.png

Crest
-----

The :doc:`crest_design` is an optional part for the *cross_cube* piece.

.. image:: images/crest_3d.png

Cross_cube
----------

The :doc:`cross_cube_design` is the *two-axle-join* of a *gimbal* system.

.. image:: images/cross_cube_3d.png



