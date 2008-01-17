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

# Python module imports.
from math import pi
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from specific_fns import n_state_model
from test_suite.unit_tests.n_state_model_testing_base import N_state_model_base_class


class Test_n_state_model(N_state_model_base_class, TestCase):
    """Unit tests for the functions of the 'specific_fns.n_state_model' module."""

    # Place the specific_fns.n_state_model module into the class namespace.
    n_state_model_fns = n_state_model.N_state_model()


    def test_assemble_param_vector(self):
        """Test the operation of the specific_fns.n_state_model.assemble_param_vector() method."""

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set up the N, probabilities and Euler angles.
        cdp.N = 3
        cdp.probs = [0.1, 0.3, 0.6]
        cdp.alpha = [0.0, pi/2, pi]
        cdp.beta = [pi/2, pi, 3*pi/2]
        cdp.gamma = [1.0, 3*pi/2, 2*pi]

        # Get the parameter vector.
        param_vector = self.n_state_model_fns.assemble_param_vector()

        # The correct result.
        vector_true = [0.1, 0.3, 0.0, pi/2, 1.0, pi/2, pi, 3*pi/2, pi, 3*pi/2, 2*pi]

        # Check the vector.
        self.assertEqual(len(param_vector), len(vector_true))
        for i in xrange(len(param_vector)):
            self.assertEqual(param_vector[i], vector_true[i])

