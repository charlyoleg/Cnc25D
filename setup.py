#from distutils.core import setup
from setuptools import setup
#from distribute import setup
#from distribute_setup import use_setuptools

setup(
  name='Cnc25D',
  version='0.1.2',
  author='charlyoleg',
  author_email='charlyoleg@fabfolk.com',
  packages=['cnc25d', 'cnc25d.tests'],
  scripts=['bin/cnc25d_example_generator.py'],
  url='http://pypi.python.org/pypi/Cnc25D/',
  license='LICENSE.txt',
  description='Help-functions to create 2.5D physical parts and cuboid assembly',
  long_description=open('README.rst').read(),
  install_requires=[
    #"math >= 0.6.24",
    #"sys >= 0.1.6",
    "argparse >= 1.2.1",
    "datetime >= 0.6.24",
    #"os >= 0.0.0",
    #"errno >= 0.0.0",
    #"Tkinter >= 0.0.0",
    #"tkMessageBox >= 0.0.0",
    "numpy >= 1.6.1",
    #"matplotlib >= 1.2.1",  # currently disable because of a bug in matplotlib setup.py about numpy dependency
    "svgwrite >= 1.1.2",
    "dxfwrite >= 1.2.0",
    #"timeit >= 0.0.0",
    #"cProfile >= 0.0.0",
    #"time >= 0.0.0",
  ],
)


