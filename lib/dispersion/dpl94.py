###############################################################################
#                                                                             #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""The Davis, Perlman and London (1994) 2-site fast exchange R1rho U{DPL94<http://wiki.nmr-relax.com/DPL94>} model.

Description
===========

This module is for the function, gradient and Hessian of the U{DPL94<http://wiki.nmr-relax.com/DPL94>} model.


References
==========

The model is named after the reference:

    - Davis, D. G., Perlman, M. E. and London, R. E. (1994).  Direct measurements of the dissociation-rate constant for inhibitor-enzyme complexes via the T1rho and T2 (CPMG) methods.  I{J. Magn. Reson.}, Series B, B{104}, 266-275.  (U{DOI: 10.1006/jmrb.1994.1084<http://dx.doi.org/10.1006/jmrb.1994.1084>})

Equations
=========

The equation used is::

                                                                      phi_ex * kex
    R1rho = R1.cos^2(theta) + R1rho'.sin^2(theta) + sin^2(theta) * ------------------ ,
                                                                   kex^2 + omega_sl^2

where theta is the rotating frame tilt angle, and::

    phi_ex = pA * pB * delta_omega^2 ,

kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, delta_omega is the chemical shift difference between the two states, and omega_sl is the spin-lock field strength.


Links
=====

More information on the DPL94 model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/DPL94>},
    - U{relax manual<http://www.nmr-relax.com/manual/The_DPL94_2_site_fast_exchange_R1_rho_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#DPL94>}.
"""

# Python module imports.
from numpy import any, cos, isfinite, min, sin, sum
from numpy.ma import fix_invalid, masked_where


def r1rho_DPL94(r1rho_prime=None, phi_ex=None, kex=None, theta=None, R1=0.0, spin_lock_fields2=None, back_calc=None):
    """Calculate the R1rho values for the DPL94 model.

    See the module docstring for details.


    @keyword r1rho_prime:       The R1rho_prime parameter value (R1rho with no exchange).
    @type r1rho_prime:          numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword phi_ex:            The phi_ex parameter value (pA * pB * delta_omega^2).
    @type phi_ex:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword kex:               The kex parameter value (the exchange rate in rad/s).
    @type kex:                  float
    @keyword theta:             The rotating frame tilt angles for each dispersion point.
    @type theta:                numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword R1:                The R1 relaxation rate.
    @type R1:                   numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword spin_lock_fields2: The R1rho spin-lock field strengths squared (in rad^2.s^-2).
    @type spin_lock_fields2:    numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword back_calc:         The array for holding the back calculated R1rho values.  Each element corresponds to the combination of theta and spin lock field.
    @type back_calc:            numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # Flag to tell if values should be replaced if numer is zero.
    t_numer_zero = False
    t_denom_zero = False

    # The non-Rex factors.
    sin_theta2 = sin(theta)**2
    R1_R2 = R1 * cos(theta)**2 + r1rho_prime * sin_theta2

    # The numerator.
    numer = sin_theta2 * phi_ex * kex

    # Catch zeros (to avoid pointless mathematical operations).
    # This will result in no exchange, returning flat lines.
    if min(numer) == 0.0:
        t_numer_zero = True
        mask_numer_zero = masked_where(numer == 0.0, numer)

    # Denominator.
    denom = kex**2 + spin_lock_fields2

    # Catch math domain error of dividing with 0.
    # This is when denom =0.
    mask_denom_zero = denom == 0.0
    if any(mask_denom_zero):
        t_denom_zero = True
        denom[mask_denom_zero] = 1.0

    # R1rho calculation.
    back_calc[:] = R1_R2 + numer / denom

    # Replace data in array.
    # If numer is zero.
    if t_numer_zero:
        back_calc[mask_numer_zero.mask] = R1_R2[mask_numer_zero.mask]

    # If denom is zero.
    if t_denom_zero:
        back_calc[mask_denom_zero] = 1e100

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)
