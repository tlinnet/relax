###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

from copy import deepcopy
from LinearAlgebra import inverse
from math import pi
from Numeric import Float64, array, identity, matrixmultiply, ones, transpose, zeros
from re import match
from string import replace
import sys

from maths_fns.mf import Mf
from minimise.generic import generic_minimise


class Model_free:
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax


    def assemble_param_vector(self, index=None):
        """Function for assembling various pieces of data into a Numeric parameter array."""

        # Initialise.
        self.param_vector = []

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                self.param_vector.append(self.relax.data.diff[self.run].tm)

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                self.param_vector.append(self.relax.data.diff[self.run].Dper)
                self.param_vector.append(self.relax.data.diff[self.run].Dpar)
                self.param_vector.append(self.relax.data.diff[self.run].theta)
                self.param_vector.append(self.relax.data.diff[self.run].phi)

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                self.param_vector.append(self.relax.data.diff[self.run].Dx)
                self.param_vector.append(self.relax.data.diff[self.run].Dy)
                self.param_vector.append(self.relax.data.diff[self.run].Dz)
                self.param_vector.append(self.relax.data.diff[self.run].alpha)
                self.param_vector.append(self.relax.data.diff[self.run].beta)
                self.param_vector.append(self.relax.data.diff[self.run].gamma)

        # Model-free parameters (residue specific parameters).
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[i].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(self.relax.data.res[i].params[self.run])):
                    # tm.
                    if self.relax.data.res[i].params[self.run][j] == 'tm':
                        if self.relax.data.res[i].tm[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].tm[self.run])

                    # S2.
                    elif self.relax.data.res[i].params[self.run][j] == 'S2':
                        if self.relax.data.res[i].s2[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].s2[self.run])

                    # S2f.
                    elif self.relax.data.res[i].params[self.run][j] == 'S2f':
                        if self.relax.data.res[i].s2f[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].s2f[self.run])

                    # S2s.
                    elif self.relax.data.res[i].params[self.run][j] == 'S2s':
                        if self.relax.data.res[i].s2s[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].s2s[self.run])

                    # te.
                    elif self.relax.data.res[i].params[self.run][j] == 'te':
                        if self.relax.data.res[i].te[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].te[self.run])

                    # tf.
                    elif self.relax.data.res[i].params[self.run][j] == 'tf':
                        if self.relax.data.res[i].tf[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].tf[self.run])

                    # ts.
                    elif self.relax.data.res[i].params[self.run][j] == 'ts':
                        if self.relax.data.res[i].ts[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].ts[self.run])

                    # Rex.
                    elif self.relax.data.res[i].params[self.run][j] == 'Rex':
                        if self.relax.data.res[i].rex[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].rex[self.run])

                    # r.
                    elif self.relax.data.res[i].params[self.run][j] == 'r':
                        if self.relax.data.res[i].r[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].r[self.run])

                    # CSA.
                    elif self.relax.data.res[i].params[self.run][j] == 'CSA':
                        if self.relax.data.res[i].csa[self.run] == None:
                            self.param_vector.append(0.0)
                        else:
                            self.param_vector.append(self.relax.data.res[i].csa[self.run])

                    # Unknown parameter.
                    else:
                        raise RelaxError, "Unknown parameter."

        # Convert to a Numeric array.
        self.param_vector = array(self.param_vector, Float64)


    def assemble_scaling_matrix(self, index=None):
        """Function for creating the scaling matrix."""

        # Initialise.
        self.scaling_matrix = identity(len(self.param_vector), Float64)
        i = 0

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                # Test if the diffusion parameters should be scaled.
                if self.relax.data.diff[self.run].scaling:
                    # tm.
                    self.scaling_matrix[i, i] = 1e-9

                # Increment i.
                i = i + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                # Test if the diffusion parameters should be scaled.
                if self.relax.data.diff[self.run].scaling:
                    # Dper, Dpar, theta, phi
                    self.scaling_matrix[i, i] = 1e9
                    self.scaling_matrix[i+1, i+1] = 1e9
                    self.scaling_matrix[i+2, i+2] = 1.0
                    self.scaling_matrix[i+3, i+3] = 1.0

                # Increment i.
                i = i + 4

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                # Test if the diffusion parameters should be scaled.
                if self.relax.data.diff[self.run].scaling:
                    # Dx, Dy, Dz, alpha, beta, gamma.
                    self.scaling_matrix[i, i] = 1e9
                    self.scaling_matrix[i+1, i+1] = 1e9
                    self.scaling_matrix[i+2, i+2] = 1e9
                    self.scaling_matrix[i+3, i+3] = 1.0
                    self.scaling_matrix[i+4, i+4] = 1.0
                    self.scaling_matrix[i+5, i+5] = 1.0

                # Increment i.
                i = i + 6

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for j in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[j].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and j != index:
                    continue

                # Skip residues which should not be scaled.
                if not self.relax.data.res[j].scaling[self.run]:
                    i = i + len(self.relax.data.res[j].params[self.run])
                    continue

                # Loop over the model-free parameters.
                for k in xrange(len(self.relax.data.res[j].params[self.run])):
                    # tm.
                    if self.relax.data.res[j].params[self.run][k] == 'tm':
                        self.scaling_matrix[i, i] = 1e-9

                    # te, tf, and ts.
                    elif match('t', self.relax.data.res[j].params[self.run][k]):
                        self.scaling_matrix[i, i] = 1e-9

                    # Rex.
                    elif self.relax.data.res[j].params[self.run][k] == 'Rex':
                        self.scaling_matrix[i, i] = 1.0 / (2.0 * pi * self.relax.data.res[j].frq[self.run][0]) ** 2

                    # Bond length.
                    elif self.relax.data.res[j].params[self.run][k] == 'r':
                        self.scaling_matrix[i, i] = 1e-10

                    # CSA.
                    elif self.relax.data.res[j].params[self.run][k] == 'CSA':
                        self.scaling_matrix[i, i] = 1e-4

                    # Increment i.
                    i = i + 1


    def calculate(self, run, print_flag):
        """Calculation of the model-free chi-squared value."""

        # Arguments.
        self.run = run
        self.print_flag = print_flag

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Print out.
        if self.print_flag >= 1:
            if self.param_set == 'mf':
                print "Only the model-free parameters for single residues will be used."
            elif self.param_set == 'diff':
                print "Only diffusion tensor parameters will be used."
            elif self.param_set == 'all':
                print "The diffusion tensor parameters together with the model-free parameters for all residues will be used."

        # The number of calc instances and number of relaxation data sets.
        if self.param_set == 'mf':
            num_instances = len(self.relax.data.res)
            num_data_sets = 1
        elif self.param_set == 'diff':
            num_instances = 1
            num_data_sets = len(self.relax.data.res)
        elif self.param_set == 'all':
            num_instances = 1
            num_data_sets = len(self.relax.data.res)

        # Loop over the minimisation instances.
        for i in xrange(num_instances):
            # Set the index to None.
            index = None

            # Individual residue stuff.
            if self.param_set == 'mf':
                # Skip unselected residues.
                if not self.relax.data.res[i].select:
                    continue

                # Set the index to i.
                index = i

            # Create the initial parameter vector.
            self.assemble_param_vector(index=index)

            # Diagonal scaling.
            self.assemble_scaling_matrix(index=index)
            self.param_vector = matrixmultiply(inverse(self.scaling_matrix), self.param_vector)

            # Set up the relaxation data and errors.
            relax_data = []
            relax_error = []

            # Loop over the number of relaxation data sets.
            for j in xrange(num_data_sets):
                # Set the sequence index.
                if self.param_set == 'mf':
                    index = i
                else:
                    index = j

                # Make sure that the errors are strictly positive numbers.
                for k in xrange(len(self.relax.data.res[index].relax_error[self.run])):
                    if self.relax.data.res[index].relax_error[self.run][k] == 0.0:
                        raise RelaxError, "Zero error for residue '" + `self.relax.data.res[index].num[self.run]` + " " + self.relax.data.res[index].name[self.run] + "', minimisation not possible."
                    elif self.relax.data.res[index].relax_error[self.run][k] < 0.0:
                        raise RelaxError, "Negative error for residue '" + `self.relax.data.res[index].num[self.run]` + " " + self.relax.data.res[index].name[self.run] + "', minimisation not possible."

                # Set up the relaxation data and errors.
                if self.param_set == 'mf':
                    relax_data = self.relax.data.res[index].relax_data[self.run]
                    relax_error = self.relax.data.res[index].relax_error[self.run]
                else:
                    relax_data.append(self.relax.data.res[index].relax_data[self.run])
                    relax_error.append(self.relax.data.res[index].relax_error[self.run])

            # Convert to Numeric arrays.
            relax_data = array(relax_data, Float64)
            relax_error = array(relax_error, Float64)

            # Initialise the functions used in the minimisation.
            self.mf = Mf(self.relax, run=run, i=i, equation=self.relax.data.res[i].equations[run], param_types=self.relax.data.res[i].params[run], init_params=params, relax_data=relax_data, errors=relax_error, bond_length=self.relax.data.res[i].r[run], csa=self.relax.data.res[i].csa[run], diff_type=self.relax.data.diff[run].type, diff_params=[self.relax.data.diff[run].tm], scaling_matrix=scaling_matrix)

            # Chi-squared calculation.
            self.relax.data.res[i].chi2[run] = self.mf.func(params, 0)


    def create(self, run=None, model=None, equation=None, params=None, scaling=1, res_num=None):
        """Function to create a model-free model."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Check the validity of the model-free equation type.
        valid_types = ['mf_orig', 'mf_ext', 'mf_ext2']
        if not equation in valid_types:
            raise RelaxError, "The model-free equation type argument " + `equation` + " is invalid and should be one of " + `valid_types` + "."

        # Check the validity of the parameter array.
        s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in xrange(len(params)):
            # Invalid parameter flag.
            invalid_param = 0

            # S2.
            if params[i] == 'S2':
                # Does the array contain more than one instance of S2.
                if s2:
                    invalid_param = 1
                s2 = 1

                # Does the array contain S2s.
                s2s_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2s':
                        s2s_flag = 1
                if s2s_flag:
                    invalid_param = 1

            # te.
            elif params[i] == 'te':
                # Does the array contain more than one instance of te and has the extended model-free formula been selected.
                if equation == 'mf_ext' or te:
                    invalid_param = 1
                te = 1

                # Does the array contain the parameter S2.
                s2_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2':
                        s2_flag = 1
                if not s2_flag:
                    invalid_param = 1

            # S2f.
            elif params[i] == 'S2f':
                # Does the array contain more than one instance of S2f and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2f:
                    invalid_param = 1
                s2f = 1

            # S2s.
            elif params[i] == 'S2s':
                # Does the array contain more than one instance of S2s and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2s:
                    invalid_param = 1
                s2s = 1

            # tf.
            elif params[i] == 'tf':
                # Does the array contain more than one instance of tf and has the original model-free formula been selected.
                if equation == 'mf_orig' or tf:
                    invalid_param = 1
                tf = 1

                # Does the array contain the parameter S2f.
                s2f_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2f':
                        s2f_flag = 1
                if not s2f_flag:
                    invalid_param = 1

            # ts.
            elif params[i] == 'ts':
                # Does the array contain more than one instance of ts and has the original model-free formula been selected.
                if equation == 'mf_orig' or ts:
                    invalid_param = 1
                ts = 1

                # Does the array contain the parameter S2 or S2s.
                flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2' or params[j] == 'S2f':
                        flag = 1
                if not flag:
                    invalid_param = 1

            # Rex.
            elif params[i] == 'Rex':
                if rex:
                    invalid_param = 1
                rex = 1

            # Bond length.
            elif params[i] == 'r':
                if r:
                    invalid_param = 1
                r = 1

            # CSA.
            elif params[i] == 'CSA':
                if csa:
                    invalid_param = 1
                csa = 1

            # Unknown parameter.
            else:
                raise RelaxError, "The parameter " + params[i] + " is not supported."

            # The invalid parameter flag is set.
            if invalid_param:
                raise RelaxError, "The parameter array " + `params` + " contains an invalid combination of parameters."

        # Set up the model.
        self.model_setup(run, model, equation, params, scaling, res_num)


    def data_init(self, name):
        """Function for returning an initial data structure corresponding to 'name'."""

        # Empty arrays.
        list_data = [ 'models',
                      'params' ]
        if name in list_data:
            return []

        # None.
        none_data = [ 'equations',
                      'scaling',
                      's2',
                      's2f',
                      's2s',
                      'tm',
                      'te',
                      'tf',
                      'ts',
                      'rex',
                      'r',
                      'csa',
                      'chi2',
                      'iter',
                      'f_count',
                      'g_count',
                      'h_count',
                      'warning' ]
        if name in none_data:
            return None


    def data_names(self):
        """Function for returning a list of names of data structures associated with model-free.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        model: The model-free model name.

        equations:  The model-free equation type.

        params:  An array of the model-free parameter names associated with the model.

        scaling:  The scaling flag.

        s2:  S2.

        s2f:  S2f.

        s2s:  S2s.

        tm:  tm.

        te:  te.

        tf:  tf.

        ts:  ts.

        rex:  Rex.

        r:  Bond length.

        csa:  CSA value.

        chi2:  Chi-squared value.

        iter:  Iterations.

        f_count:  Function count.

        g_count:  Gradient count.

        h_count:  Hessian count.

        warning:  Minimisation warning.
        """

        names = [ 'models',
                  'equations',
                  'params',
                  'scaling',
                  's2',
                  's2f',
                  's2s',
                  'tm',
                  'te',
                  'tf',
                  'ts',
                  'rex',
                  'r',
                  'csa',
                  'chi2',
                  'iter',
                  'f_count',
                  'g_count',
                  'h_count',
                  'warning' ]

        return names


    def determine_param_set_type(self):
        """Determine the type of parameter set."""

        # If there is a local tm, fail if not all residues have a local tm parameter.
        local_tm = 0
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            if local_tm == 0 and 'tm' in self.relax.data.res[i].params[self.run]:
                local_tm = 1
            elif local_tm == 1 and not 'tm' in self.relax.data.res[i].params[self.run]:
                raise RelaxError, "All residues must either have a local tm parameter or not."

        # Check if any model-free parameters are allowed to vary.
        mf_all_fixed = 1
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Test the fixed flag.
            if not hasattr(self.relax.data.res[i], 'fixed'):
                mf_all_fixed = 0
                break
            if not self.relax.data.res[i].fixed[self.run]:
                mf_all_fixed = 0
                break

        # Find the type.
        if mf_all_fixed and (local_tm or self.relax.data.diff[self.run].fixed):
            raise RelaxError, "All parameters are fixed."
        elif local_tm == 1:
            return 'local_tm'
        elif mf_all_fixed and not self.relax.data.diff[self.run].fixed:
            return 'diff'
        elif self.relax.data.diff[self.run].fixed:
            return 'mf'
        else:
            return 'all'


    def disassemble_param_vector(self, index=None):
        """Function for disassembling the parameter vector."""

        # Initialise.
        param_index = 0

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                self.relax.data.diff[self.run].tm = self.param_vector[0]
                param_index = param_index + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                self.relax.data.diff[self.run].Dper = self.param_vector[0]
                self.relax.data.diff[self.run].Dpar = self.param_vector[1]
                self.relax.data.diff[self.run].theta = self.param_vector[2]
                self.relax.data.diff[self.run].phi = self.param_vector[3]
                param_index = param_index + 4

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                self.relax.data.diff[self.run].Dx = self.param_vector[0]
                self.relax.data.diff[self.run].Dy = self.param_vector[1]
                self.relax.data.diff[self.run].Dz = self.param_vector[2]
                self.relax.data.diff[self.run].alpha = self.param_vector[3]
                self.relax.data.diff[self.run].beta = self.param_vector[4]
                self.relax.data.diff[self.run].gamma = self.param_vector[5]
                param_index = param_index + 6

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for i in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[i].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(self.relax.data.res[i].params[self.run])):
                    # tm.
                    if self.relax.data.res[i].params[self.run][j] == 'tm':
                        self.relax.data.res[i].tm[self.run] = self.param_vector[param_index]

                    # S2.
                    elif self.relax.data.res[i].params[self.run][j] == 'S2':
                        self.relax.data.res[i].s2[self.run] = self.param_vector[param_index]

                    # S2f.
                    elif self.relax.data.res[i].params[self.run][j] == 'S2f':
                        self.relax.data.res[i].s2f[self.run] = self.param_vector[param_index]

                    # S2s.
                    elif self.relax.data.res[i].params[self.run][j] == 'S2s':
                        self.relax.data.res[i].s2s[self.run] = self.param_vector[param_index]

                    # te.
                    elif self.relax.data.res[i].params[self.run][j] == 'te':
                        self.relax.data.res[i].te[self.run] = self.param_vector[param_index]

                    # tf.
                    elif self.relax.data.res[i].params[self.run][j] == 'tf':
                        self.relax.data.res[i].tf[self.run] = self.param_vector[param_index]

                    # ts.
                    elif self.relax.data.res[i].params[self.run][j] == 'ts':
                        self.relax.data.res[i].ts[self.run] = self.param_vector[param_index]

                    # Rex.
                    elif self.relax.data.res[i].params[self.run][j] == 'Rex':
                        self.relax.data.res[i].rex[self.run] = self.param_vector[param_index]

                    # r.
                    elif self.relax.data.res[i].params[self.run][j] == 'r':
                        self.relax.data.res[i].r[self.run] = self.param_vector[param_index]

                    # CSA.
                    elif self.relax.data.res[i].params[self.run][j] == 'CSA':
                        self.relax.data.res[i].csa[self.run] = self.param_vector[param_index]

                    # Unknown parameter.
                    else:
                        raise RelaxError, "Unknown parameter."

                    # Increment the parameter index.
                    param_index = param_index + 1


    def get_data_name(self, name):
        """
        Model-free data type string matching patterns.
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Setting a parameter value may have no effect depending on which model-free model is chosen,
        for example if S2f values and S2s values are set but the run corresponds to model-free model
        'm4' then, because these data values are not parameters of the model, they will have no
        effect.

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Bond length            | r            | '^r$' or '[Bb]ond[ -_][Ll]ength'                 |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | CSA                    | csa          | '^[Cc][Ss][Aa]$'                                 |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Chemical exchange      | rex          | '^[Rr]ex$' or '[Cc]emical[ -_][Ee]xchange'       |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Order parameter S2     | s2           | '^[Ss]2$'                                        |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Order parameter S2f    | s2f          | '^[Ss]2f$'                                       |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Order parameter S2s    | s2s          | '^[Ss]2s$'                                       |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Correlation time te    | te           | '^te$'                                           |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Correlation time tf    | tf           | '^tf$'                                           |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Correlation time ts    | ts           | '^ts$'                                           |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Local tm               | tm           | '^tm$'                                           |
        |________________________|______________|__________________________________________________|

        Note that the Rex values are scaled quadratically with field strength and should be supplied
        as the value for the first given field strength.
        """

        # Bond length.
        if match('^r$', name) or match('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if match('^[Cc][Ss][Aa]$', name):
            return 'csa'

        # Rex
        if match('^[Rr]ex$', name) or match('[Cc]emical[ -_][Ee]xchange', name):
            return 'rex'

        # Order parameter S2.
        if match('^[Ss]2$', name):
            return 's2'

        # Order parameter S2f.
        if match('^[Ss]2f$', name):
            return 's2f'

        # Order parameter S2s.
        if match('^[Ss]2s$', name):
            return 's2s'

        # Correlation time te.
        if match('^te$', name):
            return 'te'

        # Correlation time tf.
        if match('^tf$', name):
            return 'tf'

        # Correlation time ts.
        if match('^ts$', name):
            return 'ts'

        # Local tm.
        if match('^tm$', name):
            return 'tm'


    def grid_search(self, run, lower, upper, inc, constraints, print_flag):
        """The grid search function."""

        # Arguments.
        self.lower = lower
        self.upper = upper
        self.inc = inc

        # Minimisation.
        self.minimise(run=run, min_algor='grid', constraints=constraints, print_flag=print_flag)


    def grid_search_setup(self, index=None):
        """The grid search setup function."""

        # The length of the parameter array.
        n = len(self.param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError, "Cannot run a grid search on a model with zero parameters."

        # Lower bounds.
        if self.lower != None:
            if len(self.lower) != n:
                raise RelaxLenError, ('lower bounds', n)

        # Upper bounds.
        if self.upper != None:
            if len(self.upper) != n:
                raise RelaxLenError, ('upper bounds', n)

        # Increment.
        if type(self.inc) == list:
            if len(self.inc) != n:
                raise RelaxLenError, ('increment', n)
            inc = self.inc
        elif type(self.inc) == int:
            temp = []
            for j in xrange(n):
                temp.append(self.inc)
            inc = temp

        # Minimisation options initialisation.
        min_options = []
        m = 0

        # Minimisation options for diffusion tensor parameters.
        if self.param_set == 'local_tm':
            # Local tm {tm}.
            min_options.append([inc[0], 1.0 * 1e-9, 10.0 * 1e-9])
            m = m + 1
        elif self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion {tm}.
            if self.relax.data.diff[self.run].type == 'iso':
                min_options.append([inc[0], 1.0 * 1e-9, 10.0 * 1e-9])
                m = m + 1

            # Axially symmetric diffusion {Dper, Dpar, theta, phi}.
            if self.relax.data.diff[self.run].type == 'axial':
                min_options.append([inc[0], 0.0, 10.0 * 1e9])
                min_options.append([inc[1], 0.0, 10.0 * 1e9])
                min_options.append([inc[2], 0.0, 2 * pi])
                min_options.append([inc[3], 0.0, 2 * pi])
                m = m + 4

            # Anisotropic diffusion {Dx, Dy, Dz, alpha, beta, gamma}.
            elif self.relax.data.diff[self.run].type == 'aniso':
                min_options.append([inc[0], 0.0, 10.0 * 1e9])
                min_options.append([inc[1], 0.0, 10.0 * 1e9])
                min_options.append([inc[2], 0.0, 10.0 * 1e9])
                min_options.append([inc[3], 0.0, 2 * pi])
                min_options.append([inc[4], 0.0, 2 * pi])
                min_options.append([inc[5], 0.0, 2 * pi])
                m = m + 6

        # Model-free parameters (residue specific parameters).
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[i].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(self.relax.data.res[i].params[self.run])):
                    # Local tm.
                    if self.param_set == 'local_tm' and j == 1:
                        continue

                    # {S2, S2f, S2s}.
                    if match('S2', self.relax.data.res[i].params[self.run][j]):
                        min_options.append([inc[m], 0.0, 1.0])

                    # {te, tf, ts}.
                    elif match('t', self.relax.data.res[i].params[self.run][j]):
                        min_options.append([inc[m], 0.0, 5000.0 * 1e-12])

                    # Rex.
                    elif self.relax.data.res[i].params[self.run][j] == 'Rex':
                        min_options.append([inc[m], 0.0, 5.0 / (2.0 * pi * self.relax.data.res[i].frq[self.run][0])**2])

                    # Bond length.
                    elif self.relax.data.res[i].params[self.run][j] == 'r':
                        min_options.append([inc[m], 1.0 * 1e-10, 1.05 * 1e-10])

                    # CSA.
                    elif self.relax.data.res[i].params[self.run][j] == 'CSA':
                        min_options.append([inc[m], -120 * 1e-6, -200 * 1e-6])

                    # Unknown option.
                    else:
                        raise RelaxError, "Unknown model-free parameter."

                    # Increment m.
                    m = m + 1

        # Set the lower and upper bounds if these are supplied.
        if self.lower != None:
            for j in xrange(n):
                if self.lower[j] != None:
                    min_options[j][1] = self.lower[j]
        if self.upper != None:
            for j in xrange(n):
                if self.upper[j] != None:
                    min_options[j][2] = self.upper[j]

        # Test if the grid is too large.
        grid_size = 1
        for i in xrange(len(min_options)):
            grid_size = grid_size * min_options[i][0]
        if type(grid_size) == long:
            raise RelaxError, "A grid search of size " + `grid_size` + " is too large."

        # Diagonal scaling of minimisation options.
        for j in xrange(len(min_options)):
            min_options[j][1] = min_options[j][1] / self.scaling_matrix[j, j]
            min_options[j][2] = min_options[j][2] / self.scaling_matrix[j, j]

        return min_options


    def default_value(self, param):
        """

        The default values are as follows:

        _______________________________________________________________________________________
        |                                       |              |                              |
        | Data type                             | Object name  | Value                        |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Bond length                           | r            | 1.02 * 1e-10                 |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | CSA                                   | csa          | -170 * 1e-6                  |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Chemical exchange relaxation          | rex          | 0.0                          |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Order parameters S2, S2f, and S2s     | s2, s2f, s2s | 0.8                          |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Correlation time te                   | te           | 100 * 1e-12                  |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Correlation time tf                   | tf           | 10 * 1e-12                   |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Correlation time ts                   | ts           | 1000 * 1e-12                 |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Local tm                              | tm           | 10 * 1e-9                    |
        |_______________________________________|______________|______________________________|
        """

        # Bond length.
        if param == 'r':
            return 1.02 * 1e-10

        # CSA.
        if param == 'CSA':
            return -170 * 1e-6

        # Rex.
        if param == 'Rex':
            return 0.0

        # {S2, S2f, S2s}.
        if match('S2', param):
            return 0.8

        # {te, tf, ts}.
        elif match('t', param):
            if param == 'tf':
                return 10.0 * 1e-12
            elif param == 'ts':
                return 1000.0 * 1e-12
            elif param == 'tm':
                return 10.0 * 1e-9
            else:
                return 100.0 * 1e-12


    def initialise_mf_data(self, data, run):
        """Function for the initialisation of model-free data structures.

        Only data structures which do not exist are created.
        """

        # Get the data names.
        data_names = self.data_names()

        # Loop over the names.
        for name in data_names:
            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                setattr(data, name, {})

            # Get the data.
            object = getattr(data, name)

            # Get the initial data structure.
            value = self.data_init(name)

            # If the data structure does not have the key 'run', add it.
            if not object.has_key(run):
                object[run] = value


    def linear_constraints(self, index=None):
        """Function for setting up the model-free linear constraint matrices A and b.

        Standard notation
        ~~~~~~~~~~~~~~~~~

        The order parameter constraints are:

            0 <= S2 <= 1
            0 <= S2f <= 1
            0 <= S2s <= 1

        By substituting the formula S2 = S2f.S2s into the above inequalities, the additional two
        inequalities can be derived:

            S2 <= S2f
            S2 <= S2s

        Correlation time constraints are:

            te >= 0
            tf >= 0
            ts >= 0

            tf <= ts

        Additional constraints used include:

            Rex >= 0
            0.9e-10 <= r <= 2e-10
            -300e-6 <= CSA <= 0


        Rearranged notation
        ~~~~~~~~~~~~~~~~~~~
        The above ineqality constraints can be rearranged into:

            S2 >= 0
            -S2 >= -1
            S2f >= 0
            -S2f >= -1
            S2s >= 0
            -S2s >= -1
            S2f - S2 >= 0
            S2s - S2 >= 0
            te >= 0
            tf >= 0
            ts >= 0
            ts - tf >= 0
            Rex >= 0
            r >= 0.9e-10
            -r >= -2e-10
            CSA >= -300e-6
            -CSA >= 0


        Matrix notation
        ~~~~~~~~~~~~~~~

        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are:

            | 1  0  0  0  0  0  0  0  0 |                  |    0    |
            |                           |                  |         |
            |-1  0  0  0  0  0  0  0  0 |                  |   -1    |
            |                           |                  |         |
            | 0  1  0  0  0  0  0  0  0 |                  |    0    |
            |                           |                  |         |
            | 0 -1  0  0  0  0  0  0  0 |                  |   -1    |
            |                           |                  |         |
            | 0  0  1  0  0  0  0  0  0 |     | S2  |      |    0    |
            |                           |     |     |      |         |
            | 0  0 -1  0  0  0  0  0  0 |     | S2f |      |   -1    |
            |                           |     |     |      |         |
            |-1  1  0  0  0  0  0  0  0 |     | S2s |      |    0    |
            |                           |     |     |      |         |
            |-1  0  1  0  0  0  0  0  0 |     | te  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  1  0  0  0  0  0 |  .  | tf  |  >=  |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  1  0  0  0  0 |     | ts  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  0  1  0  0  0 |     | Rex |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0 -1  1  0  0  0 |     |  r  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  0  0  1  0  0 |     | CSA |      |    0    |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  1  0 |                  | 0.9e-10 |
            |                           |                  |         |
            | 0  0  0  0  0  0  0 -1  0 |                  | -2e-10  |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  0  1 |                  | -300e-6 |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  0 -1 |                  |    0    |

        """

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(self.param_vector)
        zero_array = zeros(n, Float64)
        i = 0
        j = 0

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                # tm >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                # Dper >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Dpar >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Oblate diffusion, Dper >= Dpar.
                if self.relax.data.diff[self.run].axial_type == 'oblate':
                    A.append(zero_array * 0.0)
                    A[j][i-2] = 1.0
                    A[j][i-1] = -1.0
                    b.append(0.0)
                    j = j + 1

                # Prolate diffusion, Dper <= Dpar.
                if self.relax.data.diff[self.run].axial_type == 'prolate':
                    A.append(zero_array * 0.0)
                    A[j][i-2] = -1.0
                    A[j][i-1] = 1.0
                    b.append(0.0)
                    j = j + 1

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                # Dx >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Dy >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Dz >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for k in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[k].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and k != index:
                    continue

                # Save current value of i.
                old_i = i

                # Loop over the model-free parameters.
                for l in xrange(len(self.relax.data.res[k].params[self.run])):
                    # Order parameters {S2, S2f, S2s}.
                    if match('S2', self.relax.data.res[k].params[self.run][l]):
                        # 0 <= S2 <= 1.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        b.append(-1.0 / self.scaling_matrix[i, i])
                        j = j + 2

                        # S2 <= S2f and S2 <= S2s.
                        if self.relax.data.res[k].params[self.run][l] == 'S2':
                            for m in xrange(len(self.relax.data.res[k].params[self.run])):
                                if self.relax.data.res[k].params[self.run][m] == 'S2f' or self.relax.data.res[k].params[self.run][m] == 'S2s':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = -1.0
                                    A[j][old_i+m] = 1.0
                                    b.append(0.0)
                                    j = j + 1

                    # Correlation times {te, tf, ts}.
                    elif match('t[efs]', self.relax.data.res[k].params[self.run][l]):
                        # 0 <= te <= 10000 ps.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        b.append(-10e-9 / self.scaling_matrix[i, i])
                        j = j + 2

                        # tf <= ts.
                        if self.relax.data.res[k].params[self.run][l] == 'ts':
                            for m in xrange(len(self.relax.data.res[k].params[self.run])):
                                if self.relax.data.res[k].params[self.run][m] == 'tf':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = 1.0
                                    A[j][old_i+m] = -1.0
                                    b.append(0.0)
                                    j = j + 1

                    # Rex.
                    elif self.relax.data.res[k].params[self.run][l] == 'Rex':
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 1

                    # Bond length.
                    elif match('r', self.relax.data.res[k].params[self.run][l]):
                        # 0.9e-10 <= r <= 2e-10.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.9e-10 / self.scaling_matrix[i, i])
                        b.append(-2e-10 / self.scaling_matrix[i, i])
                        j = j + 2

                    # CSA.
                    elif match('CSA', self.relax.data.res[k].params[self.run][l]):
                        # -300e-6 <= CSA <= 0.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(-300e-6 / self.scaling_matrix[i, i])
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 2

                    # Local tm.
                    elif match('tm', self.relax.data.res[k].params[self.run][l]):
                        # tm >= 0.
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 1

                        # t[efs] <= tm.
                        #for m in xrange(len(self.relax.data.res[k].params[self.run])):
                        #    if match('t[efs]', self.relax.data.res[k].params[self.run][m]):
                        #        A.append(zero_array * 0.0)
                        #        A[j][i] = 1.0
                        #        A[j][old_i+m] = -1.0
                        #        b.append(0.0)
                        #        j = j + 1

                    # Increment i.
                    i = i + 1

        # Convert to Numeric data structures.
        A = array(A, Float64)
        b = array(b, Float64)

        return A, b


    def map_bounds(self, run, index):
        """The function for creating bounds for the mapping function."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Parameter array.
        params = self.relax.data.res[index].params[self.run]

        # Bounds array.
        bounds = zeros((len(params), 2), Float64)

        for i in xrange(len(params)):
            # {S2, S2f, S2s}.
            if match('S2', params[i]):
                bounds[i] = [0, 1]

            # {te, tf, ts}.
            elif match('t', params[i]):
                bounds[i] = [0, 1e-8]

            # Rex.
            elif params[i] == 'Rex':
                bounds[i] = [0, 30.0 / (2.0 * pi * self.relax.data.res[index].frq[run][0])**2]

            # Bond length.
            elif params[i] == 'r':
                bounds[i] = [1.0 * 1e-10, 1.1 * 1e-10]

            # CSA.
            elif params[i] == 'CSA':
                bounds[i] = [-100 * 1e-6, -300 * 1e-6]

        # Diagonal scaling.
        self.assemble_scaling_matrix(index=index)
        for i in xrange(len(self.bounds[0])):
            self.bounds[:, i] = matrixmultiply(inverse(self.scaling_matrix), self.bounds[:, i])
        if point != None:
            self.point = matrixmultiply(inverse(self.scaling_matrix), self.point)

        return bounds


    def map_labels(self, run, index, params, bounds, swap, inc, scaling_matrix):
        """Function for creating labels, tick locations, and tick values for an OpenDX map."""

        # Initialise.
        labels = "{"
        tick_locations = []
        tick_values = []
        n = len(params)
        axis_incs = 5.0
        loc_inc = inc / axis_incs

        # Increment over the model parameters.
        for i in xrange(n):
            # {S2, S2f, S2s}.
            if match('S2', params[swap[i]]):
                # Labels.
                labels = labels + "\"" + params[swap[i]] + "\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1.0
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1.0

            # {te, tf, and ts}.
            elif match('t', params[swap[i]]):
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (ps)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e12
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e12

            # Rex.
            elif params[swap[i]] == 'Rex':
                # Labels.
                labels = labels + "\"Rex (" + self.relax.data.res[index].frq_labels[run][0] + " MHz)\""

                # Tick values.
                vals = bounds[swap[i], 0] * (2.0 * pi * self.relax.data.res[index].frq[run][0])**2
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * (2.0 * pi * self.relax.data.res[index].frq[run][0])**2

            # Bond length.
            elif params[swap[i]] == 'r':
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (A)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-10
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-10

            # CSA.
            elif params[swap[i]] == 'CSA':
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (ppm)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-6
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-6

            if i < n - 1:
                labels = labels + " "
            else:
                labels = labels + "}"

            # Tick locations.
            string = "{"
            val = 0.0
            for j in xrange(axis_incs + 1):
                string = string + " " + `val`
                val = val + loc_inc
            string = string + " }"
            tick_locations.append(string)

            # Tick values.
            string = "{"
            for j in xrange(axis_incs + 1):
                if self.relax.data.res[index].scaling.has_key(run):
                    string = string + "\"" + "%.2f" % (vals * scaling_matrix[swap[i], swap[i]]) + "\" "
                else:
                    string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            string = string + "}"
            tick_values.append(string)

        return labels, tick_locations, tick_values


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, print_flag=0):
        """Model-free minimisation.

        Three types of parameter sets exist for which minimisation is different.  These are:
            'mf' - Model-free parameters for single residues.
            'diff' - Diffusion tensor parameters.
            'all' - All model-free and all diffusion tensor parameters.

        """

        # Arguments.
        self.run = run
        self.print_flag = print_flag

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Tests for the PDB file and unit vectors.
        if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'iso':
            # Test if the PDB file has been loaded.
            if not hasattr(self.relax.data, 'pdb'):
                raise RelaxPdbError

            # Test if unit vectors exist.
            for i in xrange(len(self.relax.data.res)):
                # Skip unselected residues.
                if not self.relax.data.res[i].select:
                    continue

                # Unit vector.
                if not hasattr(self.relax.data.res[i], 'xh_unit'):
                    raise RelaxNoVectorsError

        # Print out.
        if self.print_flag >= 1:
            if self.param_set == 'mf':
                print "Only the model-free parameters for single residues will be used."
            elif self.param_set == 'diff':
                print "Only diffusion tensor parameters will be used."
            elif self.param_set == 'all':
                print "The diffusion tensor parameters together with the model-free parameters for all residues will be used."

        # Count the total number of residues and test if the CSA and bond length values have been set.
        num_res = 0
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # CSA value.
            if not hasattr(self.relax.data.res[i], 'csa') or self.relax.data.res[i].csa[self.run] == None:
                raise RelaxNoValueError, "CSA"

            # Bond length value.
            if not hasattr(self.relax.data.res[i], 'r') or self.relax.data.res[i].r[self.run] == None:
                raise RelaxNoValueError, "bond length"

            # Increment the number of residues.
            num_res = num_res + 1

        # The number of residues, minimisation instances, and data sets for each parameter set type.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            num_instances = len(self.relax.data.res)
            num_data_sets = 1
            num_res = 1
        elif self.param_set == 'diff' or self.param_set == 'all':
            num_instances = 1
            num_data_sets = len(self.relax.data.res)

        # Loop over the minimisation instances.
        for i in xrange(num_instances):
            # Set the index to None.
            index = None

            # Individual residue stuff.
            if self.param_set == 'mf' or self.param_set == 'local_tm':
                # Skip unselected residues.
                if not self.relax.data.res[i].select:
                    continue

                # Make sure that the length of the parameter array is > 0.
                if len(self.relax.data.res[i].params[self.run]) == 0:
                    raise RelaxError, "Cannot minimise a model with zero parameters."

                # Set the index to i.
                index = i

            # Create the initial parameter vector.
            self.assemble_param_vector(index=index)

            # Diagonal scaling.
            self.assemble_scaling_matrix(index=index)
            self.param_vector = matrixmultiply(inverse(self.scaling_matrix), self.param_vector)

            # Get the grid search minimisation options.
            if match('^[Gg]rid', min_algor):
                min_options = self.grid_search_setup(index=index)

            # Scaling of values for the set function.
            if match('^[Ss]et', min_algor):
                min_options = matrixmultiply(inverse(self.scaling_matrix), min_options)

            # Linear constraints.
            if constraints:
                A, b = self.linear_constraints(index=index)

            # Print out.
            if self.print_flag >= 1:
                # Individual residue stuff.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    if self.print_flag >= 2:
                        print "\n\n"
                    string = "Fitting to residue: " + `self.relax.data.res[i].num` + " " + self.relax.data.res[i].name
                    print string
                    print len(string) * '~'

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            self.iter_count = 0
            self.f_count = 0
            self.g_count = 0
            self.h_count = 0

            # Initialise the data structures for the model-free function.
            relax_data = []
            relax_error = []
            equations = []
            param_types = []
            r = []
            csa = []
            num_frq = []
            frq = []
            num_ri = []
            remap_table = []
            noe_r1_table = []
            ri_labels = []
            num_params = []
            xh_unit_vectors = []
            if self.param_set == 'local_tm':
                mf_params = []

            # Loop over the number of data sets.
            for j in xrange(num_data_sets):
                # Set the sequence index.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    seq_index = i
                else:
                    seq_index = j

                # Skip unselected residues.
                if not self.relax.data.res[seq_index].select:
                    continue

                # Make sure that the errors are strictly positive numbers.
                for k in xrange(len(self.relax.data.res[seq_index].relax_error[self.run])):
                    if self.relax.data.res[seq_index].relax_error[self.run][k] == 0.0:
                        raise RelaxError, "Zero error for residue '" + `self.relax.data.res[seq_index].num[self.run]` + " " + self.relax.data.res[seq_index].name[self.run] + "', minimisation not possible."
                    elif self.relax.data.res[seq_index].relax_error[self.run][k] < 0.0:
                        raise RelaxError, "Negative error for residue '" + `self.relax.data.res[seq_index].num[self.run]` + " " + self.relax.data.res[seq_index].name[self.run] + "', minimisation not possible."

                # Repackage the data.
                relax_data.append(self.relax.data.res[seq_index].relax_data[self.run])
                relax_error.append(self.relax.data.res[seq_index].relax_error[self.run])
                equations.append(self.relax.data.res[seq_index].equations[self.run])
                param_types.append(self.relax.data.res[seq_index].params[self.run])
                r.append(self.relax.data.res[seq_index].r[self.run])
                csa.append(self.relax.data.res[seq_index].csa[self.run])
                num_frq.append(self.relax.data.res[seq_index].num_frq[self.run])
                frq.append(self.relax.data.res[seq_index].frq[self.run])
                num_ri.append(self.relax.data.res[seq_index].num_ri[self.run])
                remap_table.append(self.relax.data.res[seq_index].remap_table[self.run])
                noe_r1_table.append(self.relax.data.res[seq_index].noe_r1_table[self.run])
                ri_labels.append(self.relax.data.res[seq_index].ri_labels[self.run])

                # Model-free parameter values.
                if self.param_set == 'local_tm':
                    pass

                # Vectors.
                if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'iso':
                    xh_unit_vectors.append(self.relax.data.res[seq_index].xh_unit)
                else:
                    xh_unit_vectors.append(None)

                # Count the number of model-free parameters for the residue index.
                num_params.append(len(self.relax.data.res[seq_index].params[self.run]))

            # Convert to Numeric arrays.
            relax_data = array(relax_data, Float64)
            relax_error = array(relax_error, Float64)
            r = array(r, Float64)
            csa = array(csa, Float64)
            frq = array(frq, Float64)

            # Diffusion tensor type.
            if self.param_set == 'local_tm':
                diff_type = 'iso'
            else:
                diff_type = self.relax.data.diff[self.run].type

            # Package the diffusion tensor parameters.
            diff_params = None
            if self.param_set == 'mf':
                # Initialise.
                diff_params = []

                # Isotropic diffusion.
                if diff_type == 'iso':
                    diff_params.append(self.relax.data.diff[self.run].tm)

                # Axially symmetric diffusion.
                elif diff_type == 'axial':
                    diff_params.append(self.relax.data.diff[self.run].Dper)
                    diff_params.append(self.relax.data.diff[self.run].Dpar)
                    diff_params.append(self.relax.data.diff[self.run].theta)
                    diff_params.append(self.relax.data.diff[self.run].phi)

                # Anisotropic diffusion.
                elif diff_type == 'aniso':
                    diff_params.append(self.relax.data.diff[self.run].Dx)
                    diff_params.append(self.relax.data.diff[self.run].Dy)
                    diff_params.append(self.relax.data.diff[self.run].Dz)
                    diff_params.append(self.relax.data.diff[self.run].alpha)
                    diff_params.append(self.relax.data.diff[self.run].beta)
                    diff_params.append(self.relax.data.diff[self.run].gamma)

                # Convert to a Numeric array.
                diff_params = array(diff_params, Float64)


            # Initialise the function to minimise.
            ######################################

            self.mf = Mf(total_num_params=len(self.param_vector), param_set=self.param_set, diff_type=diff_type, diff_params=diff_params, scaling_matrix=self.scaling_matrix, num_res=num_res, equations=equations, param_types=param_types, relax_data=relax_data, errors=relax_error, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=self.relax.data.gx, gh=self.relax.data.gh, g_ratio=self.relax.data.g_ratio, h_bar=self.relax.data.h_bar, mu0=self.relax.data.mu0, num_params=num_params, vectors=xh_unit_vectors)


            # Setup the minimisation algorithm when constraints are present.
            ################################################################

            if constraints and not match('^[Gg]rid', min_algor):
                algor = min_options[0]
            else:
                algor = min_algor


            # Levenberg-Marquardt minimisation.
            ###################################

            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                min_options = min_options + (self.mf.lm_dri, relax_error)


            # Minimisation.
            ###############

            if constraints:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=print_flag)
            else:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=print_flag)
            if results == None:
                return
            self.param_vector, self.func, iter, fc, gc, hc, self.warning = results
            self.iter_count = self.iter_count + iter
            self.f_count = self.f_count + fc
            self.g_count = self.g_count + gc
            self.h_count = self.h_count + hc

            # Scaling.
            if self.relax.data.res[i].scaling[self.run]:
                self.param_vector = matrixmultiply(self.scaling_matrix, self.param_vector)

            # Disassemble the parameter vector.
            self.disassemble_param_vector(index=index)

            # Chi-squared statistic.
            self.relax.data.res[i].chi2[self.run] = self.func

            # Iterations.
            self.relax.data.res[i].iter[self.run] = self.iter_count

            # Function evaluations.
            self.relax.data.res[i].f_count[self.run] = self.f_count

            # Gradient evaluations.
            self.relax.data.res[i].g_count[self.run] = self.g_count

            # Hessian evaluations.
            self.relax.data.res[i].h_count[self.run] = self.h_count

            # Warning.
            self.relax.data.res[i].warning[self.run] = self.warning


    def model_setup(self, run, model, equation, params, scaling_flag, res_num):
        """Function for updating various data structures depending on the model selected."""

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # If res_num is set, then skip all other residues.
            if res_num != None and res_num != self.relax.data.res[i].num:
                continue

            # Initialise the data structures (if needed).
            self.initialise_mf_data(self.relax.data.res[i], run)

            # Model-free models, equations, and parameter types.
            self.relax.data.res[i].models[run] = model
            self.relax.data.res[i].equations[run] = equation
            self.relax.data.res[i].params[run] = params

            # Diagonal scaling.
            self.relax.data.res[i].scaling[run] = scaling_flag


    def read_results(self, file_data, run):
        """Function for printing the core of the results file."""

        # Remove the header.
        file_data = file_data[1:]

        # Loop over the file data.
        for i in xrange(len(file_data)):
            # Residue number and name.
            try:
                num = int(file_data[i][0])
            except ValueError:
                print "Warning, the residue number " + file_data[i][0] + " is not an integer."
                continue
            name = file_data[i][1]

            # Find the residue index.
            index = None
            for j in xrange(len(self.relax.data.res)):
                if self.relax.data.res[j].num == num and self.relax.data.res[j].name == name:
                    index = j
                    break
            if index == None:
                print "Warning, residue " + `num` + " " + name + " cannot be found in the sequence."
                continue

            # Test if relaxation data has been loaded.
            if not hasattr(self.relax.data.res[index], 'relax_data'):
                print "Relaxation data has not been loaded.  This is required for the frequency data for Rex values."
                break

            # Model details.
            model = file_data[i][2]
            equation = file_data[i][3]

            # Paramters.
            params = eval(file_data[i][4])
            if type(params) != list:
                print "Warning, the parameters " + file_data[i][4] + " is not an array."
                continue

            # S2.
            try:
                s2 = float(file_data[i][5])
            except ValueError:
                s2 = None

            # S2f.
            try:
                s2f = float(file_data[i][6])
            except ValueError:
                s2f = None

            # S2s.
            try:
                s2s = float(file_data[i][7])
            except ValueError:
                s2s = None

            # tm.
            try:
                tm = float(file_data[i][8])
                tm = tm * 1e-12
            except ValueError:
                tm = None

            # tf.
            try:
                tf = float(file_data[i][9])
                tf = tf * 1e-12
            except ValueError:
                tf = None

            # te and ts.
            try:
                te = float(file_data[i][10])
                te = te * 1e-12
            except ValueError:
                te = None
            if "te" in params:
                ts = None
            else:
                ts = te
                te = None

            # Rex.
            try:
                rex = float(file_data[i][11])
                rex = rex / (2.0 * pi * self.relax.data.res[i].frq[run][0])**2
            except ValueError:
                rex = None

            # Bond length.
            try:
                r = float(file_data[i][12])
                r = r * 1e-10
            except ValueError:
                r = None

            # CSA.
            try:
                csa = float(file_data[i][13])
                csa = csa * 1e-6
            except ValueError:
                csa = None

            # Chi-squared.
            try:
                chi2 = float(file_data[i][14])
            except ValueError:
                chi2 = None

            # Number of iterations.
            try:
                iter = int(file_data[i][15])
            except ValueError:
                iter = None

            # Function count.
            try:
                f_count = int(file_data[i][16])
            except ValueError:
                f_count = None

            # Gradient count.
            try:
                g_count = int(file_data[i][17])
            except ValueError:
                g_count = None

            # Hessian count.
            try:
                h_count = int(file_data[i][18])
            except ValueError:
                h_count = None

            # Warning.
            if len(file_data[i]) > 19:
                warning = file_data[i][19]
                for j in xrange(20, len(file_data[i])):
                    warning = warning + " " + file_data[i][j]
            else:
                warning = None

            # Initialise the runs data structure.
            if not hasattr(self.relax.data.res[index], 'runs'):
                self.relax.data.res[index].runs = []

            # Initialise the data structures (if needed).
            self.initialise_mf_data(self.relax.data.res[index], run)

            # Place the data into 'self.relax.data'.
            self.relax.data.res[index].models[run] = model
            self.relax.data.res[index].equations[run] = equation
            self.relax.data.res[index].params[run] = params
            self.relax.data.res[index].s2[run] = s2
            self.relax.data.res[index].s2f[run] = s2f
            self.relax.data.res[index].s2s[run] = s2s
            self.relax.data.res[index].tm[run] = tm
            self.relax.data.res[index].tf[run] = tf
            self.relax.data.res[index].te[run] = te
            self.relax.data.res[index].ts[run] = ts
            self.relax.data.res[index].rex[run] = rex
            self.relax.data.res[index].r[run] = r
            self.relax.data.res[index].csa[run] = csa
            self.relax.data.res[index].chi2[run] = chi2
            self.relax.data.res[index].iter[run] = iter
            self.relax.data.res[index].f_count[run] = f_count
            self.relax.data.res[index].g_count[run] = g_count
            self.relax.data.res[index].h_count[run] = h_count
            self.relax.data.res[index].warning[run] = warning


    def select(self, run=None, model=None, scaling=1, res_num=None):
        """Function for the selection of a preset model-free model."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run


        # Preset models.
        ################

        # Block 1.
        if model == 'm0':
            equation = 'mf_orig'
            params = []
        elif model == 'm1':
            equation = 'mf_orig'
            params = ['S2']
        elif model == 'm2':
            equation = 'mf_orig'
            params = ['S2', 'te']
        elif model == 'm3':
            equation = 'mf_orig'
            params = ['S2', 'Rex']
        elif model == 'm4':
            equation = 'mf_orig'
            params = ['S2', 'te', 'Rex']
        elif model == 'm5':
            equation = 'mf_ext'
            params = ['S2f', 'S2', 'ts']
        elif model == 'm6':
            equation = 'mf_ext'
            params = ['S2f', 'tf', 'S2', 'ts']
        elif model == 'm7':
            equation = 'mf_ext'
            params = ['S2f', 'S2', 'ts', 'Rex']
        elif model == 'm8':
            equation = 'mf_ext'
            params = ['S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm9':
            equation = 'mf_orig'
            params = ['Rex']

        # Block 2.
        elif model == 'm10':
            equation = 'mf_orig'
            params = ['CSA']
        elif model == 'm11':
            equation = 'mf_orig'
            params = ['CSA', 'S2']
        elif model == 'm12':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'te']
        elif model == 'm13':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'Rex']
        elif model == 'm14':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'te', 'Rex']
        elif model == 'm15':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'S2', 'ts']
        elif model == 'm16':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm17':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm18':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm19':
            equation = 'mf_orig'
            params = ['CSA', 'Rex']

        # Block 3.
        elif model == 'm20':
            equation = 'mf_orig'
            params = ['r']
        elif model == 'm21':
            equation = 'mf_orig'
            params = ['r', 'S2']
        elif model == 'm22':
            equation = 'mf_orig'
            params = ['r', 'S2', 'te']
        elif model == 'm23':
            equation = 'mf_orig'
            params = ['r', 'S2', 'Rex']
        elif model == 'm24':
            equation = 'mf_orig'
            params = ['r', 'S2', 'te', 'Rex']
        elif model == 'm25':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'S2', 'ts']
        elif model == 'm26':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm27':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm28':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm29':
            equation = 'mf_orig'
            params = ['r', 'Rex']

        # Block 4.
        elif model == 'm30':
            equation = 'mf_orig'
            params = ['r', 'CSA']
        elif model == 'm31':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2']
        elif model == 'm32':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'te']
        elif model == 'm33':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'Rex']
        elif model == 'm34':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'm35':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'm36':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm37':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm38':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm39':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'Rex']


        # Preset models with local correlation time.
        ############################################

        # Block 1.
        elif model == 'tm0':
            equation = 'mf_orig'
            params = ['tm']
        elif model == 'tm1':
            equation = 'mf_orig'
            params = ['tm', 'S2']
        elif model == 'tm2':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'te']
        elif model == 'tm3':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'Rex']
        elif model == 'tm4':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'te', 'Rex']
        elif model == 'tm5':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'S2', 'ts']
        elif model == 'tm6':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm7':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm8':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm9':
            equation = 'mf_orig'
            params = ['tm', 'Rex']

        # Block 2.
        elif model == 'tm10':
            equation = 'mf_orig'
            params = ['tm', 'CSA']
        elif model == 'tm11':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2']
        elif model == 'tm12':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'te']
        elif model == 'tm13':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'Rex']
        elif model == 'tm14':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm15':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm16':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm17':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm18':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm19':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'Rex']

        # Block 3.
        elif model == 'tm20':
            equation = 'mf_orig'
            params = ['tm', 'r']
        elif model == 'tm21':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2']
        elif model == 'tm22':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'te']
        elif model == 'tm23':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'Rex']
        elif model == 'tm24':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'te', 'Rex']
        elif model == 'tm25':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'S2', 'ts']
        elif model == 'tm26':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm27':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm28':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm29':
            equation = 'mf_orig'
            params = ['tm', 'r', 'Rex']

        # Block 4.
        elif model == 'tm30':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA']
        elif model == 'tm31':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2']
        elif model == 'tm32':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'te']
        elif model == 'tm33':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'Rex']
        elif model == 'tm34':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm35':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm36':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm37':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm38':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm39':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'Rex']

        # Invalid models.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(run, model, equation, params, scaling, res_num)


    def set(self, run, value, data_type, index):
        """The function for setting model-free residue specific data values."""

        # Arguments.
        self.run = run

        # Setting the model parameters prior to minimisation.
        #####################################################

        if data_type == None:
            # The values are supplied by the user:
            if value:
                # Test if the length of the value array is equal to the length of the model-free parameter array.
                if len(value) != len(self.relax.data.res[index].params[self.run]):
                    raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to the length of the model-free parameter array, " + `self.relax.data.res[index].params[self.run]` + ", for residue " + `self.relax.data.res[index].num` + " " + self.relax.data.res[index].name + "."

            # Default values.
            else:
                # Set 'value' to an empty array.
                value = []

                # Loop over the model-free parameters.
                for i in xrange(len(self.relax.data.res[index].params[self.run])):
                    value.append(self.default_value(self.relax.data.res[index].params[self.run][i]))

            # Loop over the model-free parameters.
            for i in xrange(len(self.relax.data.res[index].params[self.run])):
                # Get the object.
                object_name = self.get_data_name(self.relax.data.res[index].params[self.run][i])
                if not hasattr(self.relax.data.res[index], object_name):
                    self.initialise_mf_data(self.relax.data.res[index], self.run)
                object = getattr(self.relax.data.res[index], object_name)

                # Set the value.
                object[self.run] = float(value[i])


        # Individual data type.
        #######################

        else:
            # Get the object.
            object_name = self.get_data_name(data_type)
            if not hasattr(self.relax.data.res[index], object_name):
                self.initialise_mf_data(self.relax.data.res[index], self.run)
            object = getattr(self.relax.data.res[index], object_name)

            # Default value.
            if value == None:
                value = self.default_value(object_name)

            # Set the value.
            object[self.run] = float(value)


    def write_header(self, file, run):
        """Function for printing the header of the results file."""

        # Residue number and name.
        file.write("%-5s" % "Num")
        file.write("%-6s" % "Name")

        # Model details.
        file.write("%-6s" % "Model")
        file.write("%-10s" % "Equation")
        file.write("%-36s" % "Params")

        # Parameters.
        file.write("%-26s" % "S2")
        file.write("%-26s" % "S2f")
        file.write("%-26s" % "S2s")
        file.write("%-26s" % "tm_(ps)")
        file.write("%-26s" % "tf_(ps)")
        file.write("%-26s" % "te_or_ts_(ps)")
        file.write("%-26s" % ("Rex_(" + self.relax.data.res[0].frq_labels[run][0] + "_MHz)"))
        file.write("%-26s" % "Bond_length_(A)")
        file.write("%-26s" % "CSA_(ppm)")

        # Minimisation results.
        file.write("%-26s" % "Chi-squared")
        file.write("%-9s" % "Iter")
        file.write("%-9s" % "f")
        file.write("%-9s" % "g")
        file.write("%-9s" % "h")
        file.write("Warning")

        # End of line.
        file.write("\n")


    def write_results(self, file, run, i):
        """Function for printing the core of the results file."""

        # Reassign data structure.
        res = self.relax.data.res[i]

        # Residue number and name.
        file.write("%-5s" % res.num)
        file.write("%-6s" % res.name)

        # Test if the run exists.
        if not run in res.runs:
            file.write("\n")
            return

        # Model details.
        file.write("%-6s" % res.models[run])
        file.write("%-10s" % res.equations[run])
        file.write("%-36s" % replace(`res.params[run]`, ' ', ''))

        # S2.
        if res.s2[run] == None:
            if res.s2f[run] != None and res.s2s[run] != None:
                file.write("%-26s" % `res.s2f[run] * res.s2s[run]`)
            else:
                file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.s2[run]`)

        # S2f.
        if res.s2f[run] == None:
            if res.s2[run] != None and res.s2s[run] != None:
                if res.s2s[run] == 0.0:
                    file.write("%-26s" % "inf")
                else:
                    file.write("%-26s" % `res.s2[run] / res.s2s[run]`)
            else:
                file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.s2f[run]`)

        # S2s.
        if res.s2s[run] == None:
            if res.s2[run] != None and res.s2f[run] != None:
                if res.s2f[run] == 0.0:
                    file.write("%-26s" % "inf")
                else:
                    file.write("%-26s" % `res.s2[run] / res.s2f[run]`)
            else:
                file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.s2s[run]`)

        # tm.
        if hasattr(res, 'tm') and res.tm.has_key(run) and res.tm[run] != None:
            file.write("%-26s" % `res.tm[run] / 1e-12`)
        else:
            file.write("%-26s" % `self.relax.data.diff[run].tm / 1e-12`)

        # tf.
        if res.tf[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.tf[run] / 1e-12`)

        # te or ts.
        if res.te[run] == None and res.ts[run] == None:
            file.write("%-26s" % "N/A")
        elif res.te[run] != None:
            file.write("%-26s" % `res.te[run] / 1e-12`)
        else:
            file.write("%-26s" % `res.ts[run] / 1e-12`)

        # Rex.
        if res.rex[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.rex[run] * (2.0 * pi * res.frq[run][0])**2`)

        # Bond length.
        if res.r[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.r[run] / 1e-10`)

        # CSA.
        if res.csa[run] == None:
            file.write("%-26s" % "N/A")
        else:
            file.write("%-26s" % `res.csa[run] / 1e-6`)

        # Chi-squared.
        file.write("%-26s" % `res.chi2[run]`)

        # Iterations
        if res.iter[run] == None:
            file.write("%-9s" % "None")
        else:
            file.write("%-9i" % res.iter[run])

        # Function count.
        if res.f_count[run] == None:
            file.write("%-9s" % "None")
        else:
            file.write("%-9i" % res.f_count[run])

        # Gradient count.
        if res.g_count[run] == None:
            file.write("%-9s" % "None")
        else:
            file.write("%-9i" % res.g_count[run])

        # Hessian count.
        if res.h_count[run] == None:
            file.write("%-9s" % "None")
        else:
            file.write("%-9i" % res.h_count[run])

        # Warning
        if res.warning[run] != None:
            file.write(res.warning[run])

        # End of line.
        file.write("\n")
