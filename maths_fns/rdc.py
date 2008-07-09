###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing functions for the calculation of RDCs."""


def average_rdc_5D(vect, K, Axx, Ayy, Axy, Axz, Ayz):
    """Calculate the average RDC for an ensemble set of XH bond vectors, using the 5D notation.

    This function calculates the average RDC for a set of XH bond vectors from a structural
    ensemble, using the 5D vector form of the alignment tensor.  The formula for this ensemble
    average RDC value is::

                    _K_
                  1 \ 
        <RDC_i> = -  >  RDC_ik (theta),
                  K /__
                    k=1

    where K is the total number of structures,  k is the index over the multiple structures, RDC_ik
    is the back-calculated RDC value for spin system i and structure k, and theta is the parameter
    vector consisting of the alignment tensor parameters {Axx, Ayy, Axy, Axz, Ayz}.  The
    back-calculated RDC is given by the formula::

        RDC_ik(theta) = (x**2 - z**2)Axx + (y**2 - z**2)Ayy + 2x.y.Axy + 2x.z.Axz + 2y.z.Ayz.


    @param vect:        The XH bond vector matrix.  The first dimension corresponds to the
                        structural index, the second dimension is the coordinates of the vector.
    @type vect:         numpy matrix
    @param K:           The total number of structures.
    @type K:            int
    @param Axx:         The xx component of the alignment tensor.
    @type Axx:          float
    @param Ayy:         The yy component of the alignment tensor.
    @type Ayy:          float
    @param Axy:         The xy component of the alignment tensor.
    @type Axy:          float
    @param Axz:         The xz component of the alignment tensor.
    @type Axz:          float
    @param Ayz:         The yz component of the alignment tensor.
    @type Ayz:          float
    """

    # Initial back-calculated RDC value.
    val = 0.0

    # Loop over the structures k.
    for k in xrange(K):
        # Back-calculate the RDC.
        val = val + (vect[k, 1]**2 - vect[k, 3]**2)*Axx + (vect[k, 2]**2 - vect[k, 3]**2)*Ayy + 2*vect[k, 1]*vect[k, 2]*Axy + 2*vect[k, 1]*vect[k, 3]*Axz + 2*vect[k, 2]*vect[k, 3]*Ayz

    # Return the average RDC.
    return val / K


def average_rdc_tensor(vect, K, A):
    """Calculate the average RDC for an ensemble set of XH bond vectors, using the 3D tensor.

    This function calculates the average RDC for a set of XH bond vectors from a structural
    ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble
    average RDC value is::

                    _K_
                  1 \ 
        <RDC_i> = -  >  RDC_ik (theta),
                  K /__
                    k=1

    where K is the total number of structures,  k is the index over the multiple structures, RDC_ik
    is the back-calculated RDC value for spin system i and structure k, and theta is the parameter
    vector consisting of the alignment tensor.  The back-calculated RDC is given by the formula::

        RDC_ik(theta) = muT . A . mu,

    where mu is the unit XH bond vector, T is the transpose, and A is the alignment tensor matrix.


    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the
                        structural index, the second dimension is the coordinates of the unit
                        vector.
    @type vect:         numpy matrix
    @param K:           The total number of structures.
    @type K:            int
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    """

    # Initial back-calculated RDC value.
    val = 0.0

    # Loop over the structures k.
    for k in xrange(K):
        # Back-calculate the RDC.
        val = val + dot(vect[k], dot(A, vect[k]))

    # Return the average RDC.
    return val / K
