==============
Box Wood Frame
==============

:date: 2013-06-03
:author: charlyoleg

1. Design purpose
=================

The Box_Wood_Frame design is a solid and cost effective piece of furniture that can be piled up.

.. image:: images/pile_up_of_pieces_of_furniture.png

The pile-up feature is useful for:

- rearranging interior
- transporting the pieces of furniture
- moving accommodation
- And also, maybe, building straw house
- it lets make big pieces of furniture out of small pieces of material
- the conception is also cut in several small problematics
- the big pieces of furniture can be easily dismount, transport and remount

The frame is made out of solid wood planks. The faces can then be closed with light plywood.


A module corresponds to one or several box of the grid.
We focus on the concatenation of box along the x axis.
N is the number of concatenated box (along the x axis).

2. Construction method
======================

The planks are fixed by crenel and glue.

.. image:: images/crenel_and_fiber_direction.png

3. Design proposal
==================

.. image:: images/design_proposal.png

Wood frame plank list:

- horizontal plank: 20x60
- vertical plank: 20x30
- diagonal: 10x30 (thiner to give space for the face plywood)

4. Box wood frame parameters
============================

A module is defined by:

- The box dimension (w*d*h): 300*300*300
- The number of aggregated box: N*1*1

N is the length of the module. It is a number of boxes.   


.. image:: images/box_wood_frame_parameters_1.png


.. image:: images/box_wood_frame_parameters_2.png


.. image:: images/box_wood_frame_parameters_3.png



5. Plank outline description
============================

Q is the number of required planks to build one module. It can depends on N, the length of the module.

5.1. plank01_xz_bottom
----------------------
Q = 2

.. image:: images/plank01_xz_bottom_outline.png

5.2. plank02_xz_top
-------------------
Q = 2

.. image:: images/plank02_xz_top_outline.png

5.3. plank03_yz_bottom
----------------------
Q = 2

.. image:: images/plank03_yz_bottom_outline.png

5.4. plank04_yz_top
-------------------
Q = 2

.. image:: images/plank04_yz_top_outline.png

5.5. plank05_z_side
-------------------
Q = 2*(3+N)

.. image:: images/plank05_z_side_outline.png

5.6. plank06_zx_middle
----------------------
Q = 2*(N-1)

.. image:: images/plank06_zx_middle_outline.png

5.7. plank07_wall_diagonal
--------------------------
Q = 4*(1+3*N)

.. image:: images/plank07_wall_diagonal_outline.png

5.8. plank08_tobo_diagonal
--------------------------
Q = 8*N

.. image:: images/plank08_tobo_diagonal_outline.png

5.9. hole_cover
---------------
Q = 8*(N+1)

The plank09_hole_cover has an aesthetic functionality.

.. image:: images/plank09_hole_cover_outline.png


6. Diagonal plank reorientation
===============================

The planks are positioned in the cuboid assembly with the plank_place() function. To position the diagonal planks with this function, the diagonal planks must first be rotated of 45 degrees and affected with virtual length and width corresponding to the assimilated straight plank.

.. image:: images/plank07_wall_diagonal_reorientation.png
.. image:: images/plank08_tobo_diagonal_reorientation.png



