###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""Variables for the relaxation dispersion specific analysis."""

# The experiment type lists.
FIXED_TIME_EXP = ['cpmg fixed', 'r1rho fixed']
"""The list of fixed relaxation time period experiments."""

VAR_TIME_EXP = ['cpmg exponential', 'r1rho exponential']
"""The list of variable relaxation time period experiments."""

CPMG_EXP = ['cpmg fixed', 'cpmg exponential']
"""The list of CPMG-type experiments."""

R1RHO_EXP = ['r1rho fixed', 'r1rho exponential']
"""The list of R1rho-type experiments."""


# The model names.
MODEL_R2EFF = 'R2eff'
"""The model for determining the R2eff/R1rho values from peak intensities."""

MODEL_NOREX = 'No Rex'
"""The model for no chemical exchange relaxation."""

MODEL_LM63 = 'LM63'
"""The CPMG 2-site fast exchange model of Luz and Meiboom (1963)."""

MODEL_CR72_RED = 'CR72 red'
"""The CPMG 2-site model for all time scales of Carver and Richards (1972), whereby the simplification R20A = R20B is assumed."""

MODEL_CR72 = 'CR72'
"""The CPMG 2-site model for all time scales of Carver and Richards (1972)."""

MODEL_IT99 = 'IT99'
"""The CPMG 2-site model for all time scales with pA >> pB of Ishima and Torchia (1999)."""

MODEL_DPL94 = 'DPL94'
"""The R1rho 2-site fast exchange model of Davis, Perlman and London (1994)."""

MODEL_M61 = 'M61'
"""The R1rho 2-site fast exchange model of Meiboom (1961)."""

MODEL_M61B = 'M61 skew'
"""The R1rho 2-site model for all time scales with pA >> pB of Meiboom (1961)."""


# The Numerical model names.
MODEL_NS_2SITE_STAR_RED = 'NS 2-site star red'
"""The numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices, whereby the simplification R20A = R20B is assumed."""

MODEL_NS_2SITE_STAR = 'NS 2-site star'
"""The numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices."""


# The model lists.
MODEL_LIST_DISP = [MODEL_NOREX, MODEL_LM63, MODEL_CR72_RED, MODEL_CR72, MODEL_IT99, MODEL_M61, MODEL_DPL94, MODEL_M61B, MODEL_NS_2SITE_STAR_RED, MODEL_NS_2SITE_STAR]
"""The list of all dispersion models (excluding the R2eff model)."""

MODEL_LIST_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_CR72_RED, MODEL_CR72, MODEL_IT99, MODEL_M61, MODEL_DPL94, MODEL_M61B, MODEL_NS_2SITE_STAR_RED, MODEL_NS_2SITE_STAR]
"""The list of the R2eff model together with all dispersion models."""

MODEL_LIST_CPMG = [MODEL_NOREX, MODEL_LM63, MODEL_CR72_RED, MODEL_CR72, MODEL_IT99, MODEL_NS_2SITE_STAR_RED, MODEL_NS_2SITE_STAR]
"""The list of all dispersion models specifically for CPMG-type experiments (excluding the R2eff model)."""

MODEL_LIST_CPMG_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_CR72_RED, MODEL_CR72, MODEL_IT99, MODEL_NS_2SITE_STAR_RED, MODEL_NS_2SITE_STAR]
"""The list of the R2eff model together with all dispersion models specifically for CPMG-type experiments."""

MODEL_LIST_R1RHO = [MODEL_NOREX, MODEL_M61, MODEL_DPL94, MODEL_M61B]
"""The list of all dispersion models specifically for R1rho-type experiments (excluding the R2eff model)."""

MODEL_LIST_R1RHO_FULL = [MODEL_R2EFF, MODEL_NOREX, MODEL_M61, MODEL_DPL94, MODEL_M61B]
"""The list of the R2eff model together with all dispersion models specifically for R1rho-type experiments."""
