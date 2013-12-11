# angles.py
# functions for angle converstion
# created by charlyoleg on 2013/12/10
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
angles.py contains functions to convert angles from one system to an other
"""


################################################################
# import
################################################################

import math

################################################################
# functions
################################################################

def roll_pitch_to_pan_tilt(ai_a1, ai_a2):
  """ convert a pair of roll-pitch angles to a pair of pan-tilt angles
  """
  # precision
  radian_epsilon = math.pi/1000
  #
  cos_b = math.cos(ai_a2)*math.cos(ai_a1)
  b = math.acos(cos_b)
  sin_b = math.sin(b)
  b1_sign = math.copysign(1, math.sin(ai_a1))
  if(abs(sin_b)<radian_epsilon):
    b1 = 0
  else:
    sin_A = math.sin(ai_a2)/math.sin(b)
    if(abs(sin_A)>1):
      if(abs(sin_A)<1+radian_epsilon):
        sin_A = math.copysign(1, sin_A)
      else:
        print("ERR053: Internal Error, sin_A {:0.3f}".format(sin_A))
        sys.exit(2)
    A = math.asin(sin_A)
    b1 = b1_sign*math.pi/2 - A
  b2 = math.pi/2 - b
  #
  r_pan_tilt = (b1, b2)
  return(r_pan_tilt)

def pan_tilt_to_roll_pitch(ai_b1, ai_b2):
  """ convert a pair of pan-tilt angles to a pair of roll-pitch angles
  """
  # precision
  radian_epsilon = math.pi/1000
  #
  b = math.pi/2 - ai_b2
  A = math.pi/2 - ai_b1
  sin_a = math.cos(ai_b1)*math.cos(ai_b2)
  a = math.asin(sin_a)
  cos_a = math.cos(a)
  a1_sign = math.copysign(1, math.sin(ai_b1)*math.cos(ai_b2))
  print("dbg070: ai_b1 {:0.3f}  ai_b2 {:0.3f}".format(ai_b1, ai_b2))
  if(abs(cos_a)<radian_epsilon):
    print("WARN070: Warning, a2 (tilt) is pi/2, a1 can not be calculated")
    a1 = 0
  else:
    cos_C = math.cos(ai_b1)*math.sin(ai_b2)/cos_a
    cos_c = cos_a*math.cos(b)+sin_a*math.sin(b)*cos_C
    a1 = a1_sign*math.acos(cos_c)
  a2 = a*a1_sign
  #
  r_roll_tilt = (a1, a2)
  return(r_roll_tilt)

def roll_pitch_pan_tilt_drift_angle(ai_a1, ai_a2):
  """ compute the angle (y2,y4) along the axis z3 (=x5)
      For a same z3 (=x5) orientation the roll-pitch system and the pan-tilt system provide a different y (y2 vs y4) orientation
  """
  (b1, b2) = roll_pitch_to_pan_tilt(ai_a1, ai_a2)
  cos_d = math.cos(ai_a1)*math.cos(b1)
  b3 = math.acos(cos_d)
  #
  return(b3)


