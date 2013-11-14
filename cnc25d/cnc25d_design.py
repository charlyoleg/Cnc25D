# cnc25d_design.py
# the unified interface to use the cnc25d designs
# created by charlyoleg on 2013/10/01
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
cnc25d_design.py provides a unified interface of the cnc25d designs
to be used by the design examples or external scripts
"""

################################################################
# import
################################################################

import box_wood_frame
import gear_profile
import gearwheel
import gearring
import gearbar
import split_gearwheel
import epicyclic_gearing
import axle_lid
import motor_lid

################################################################
# Cnc25d Designs
################################################################

## wood structure
box_wood_frame = box_wood_frame.box_wood_frame
#hexa_bone = hexa_bone.hexa_bone

## gear
# gear back-office
gear_profile = gear_profile.gear_profile
# standard gear
gearwheel = gearwheel.gearwheel
gearring = gearring.gearring
gearbar = gearbar.gearbar
# advanced gear
split_gearwheel = split_gearwheel.split_gearwheel
#gearlever = gearlever.gearlever
# gear system
epicyclic_gearing = epicyclic_gearing.epicyclic_gearing
axle_lid = axle_lid.axle_lid
motor_lid = motor_lid.motor_lid
#gear_train = gear_train.gear_train


