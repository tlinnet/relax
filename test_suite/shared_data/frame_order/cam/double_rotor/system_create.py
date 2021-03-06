###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Script for generating the double rotor geometric system."""

# Python module imports.
from numpy import array, cross, float64, radians
from numpy.linalg import norm

# relax module imports.
from lib.geometry.vectors import unit_vector_from_2point
from lib.structure.represent.rotor import rotor


# The two CoMs.
COM_N = [41.739,   6.030,  -0.764]
COM_C = [26.837, -12.379,  28.342]

# The inter-domain connection point.
PIV = array([37.254,   0.500,  16.747], float64)

# The inter-CoM vector.
inter_com = unit_vector_from_2point(COM_N, COM_C)

# The N to pivot vector.
N_piv = unit_vector_from_2point(COM_N, PIV)

# First perpendicular rotation axis.
axis1 = cross(inter_com, N_piv)
axis1 = axis1 / norm(axis1)

# Second perpendicular rotation axis.
axis2 = cross(inter_com, axis1)
axis2 = axis2 / norm(axis2)

# The 3D positions 10 Angstrom away.
pos1 = axis1 * 10.0 + COM_N 
pos2 = axis2 * 10.0 + COM_C 

# A storage data pipe.
pipe.create('system', 'N-state')

# Create the CoM central piece.
structure.add_atom(atom_name='CN', res_name='SYS', res_num=1, pos=COM_N, element='C', pdb_record='HETATM')
structure.add_atom(atom_name='CC', res_name='SYS', res_num=1, pos=COM_C, element='C', pdb_record='HETATM')
structure.connect_atom(index1=0, index2=1)

# Create a PDB representation of the rotors.
rotor(structure=cdp.structure, rotor_angle=radians(10.5), axis=axis1, axis_pt=pos1, centre=COM_N, span=2e-9, blade_length=5e-10, staggered=False)
rotor(structure=cdp.structure, rotor_angle=radians(11.5), axis=axis2, axis_pt=pos2, centre=COM_C, span=2e-9, blade_length=5e-10, staggered=False)

# Write out the system.
state.save('system', force=True)
structure.write_pdb(file='system.pdb', force=True)

# Save the state.
state.save('system', force=True)

# Printouts.
print("\n")
print("N-domain COM: %s" % COM_N)
print("C-domain COM: %s" % COM_C)
print("Axis 1:       %s" % repr(axis1))
print("Axis 2:       %s" % repr(axis2))
