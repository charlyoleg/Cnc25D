========
Cnc 2.5D
========

Cnc25D is a Python_ Package for 2.5D part design and cuboid assembly.

.. _Python : http://www.python.org

* Cnc25D relies on FreeCAD_
* Cnc25D helps create FreeCAD_ macro
* Cnc25D helps design 3D parts entirely with Python_ script
* Cnc25D provides parametric ready-to-use design examples
* Cnc25D helps drawing shape makable by a 3-axis CNC
* Cnc25D helps positioning parts in a cuboid assembly

Have a look at the `Cnc25D release documentation`_ or the `Cnc25D daily built documentation`_ for more information.

The source code is available at https://github.com/charlyoleg/Cnc25D under the `CC BY-SA 3.0`_ license.

.. _FreeCAD : http://www.freecadweb.org
.. _`Cnc25D release documentation` : http://pythonhosted.org/Cnc25D/
.. _`Cnc25D daily built documentation` : https://cnc25d.readthedocs.org
.. _`CC BY-SA 3.0` : http://creativecommons.org/licenses/by-sa/3.0/

Why 2.5D ?
----------

3-axis CNC, laser cutter and water jet machine are getting cheaper and can be used in fablab, makerspace or hackerspace. 3-axis machine lets make 2.5D design, i.e. free xy-path at z constant. 

Installation
------------

Cnc25D is on PyPI_.

To install Cnc25D:

* First, install FreeCAD_
* Then, install the Cnc25D package with the following commands::

  > sudo pip install Cnc25D -U
  > cd directory/where/I/want/to/create/my/3D/parts
  > cnc25d_example_generator.py

* Or, clone the `Cnc25D GitHub repository`_ and run the code directly from there.


.. _PyPI : https://pypi.python.org/pypi/Cnc25D



Feedback / Contact
------------------

If you find bugs, will suggest fix or want new features report it in the `GitHub issue tracker`_ or clone the `Cnc25D GitHub repository`_.

For any other feedback, send me a message to "charlyoleg at fabfolk dot com".

.. _`Cnc25D GitHub repository` : https://github.com/charlyoleg/Cnc25D
.. _`GitHub issue tracker` : https://github.com/charlyoleg/Cnc25D/issues


