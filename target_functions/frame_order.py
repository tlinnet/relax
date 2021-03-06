###############################################################################
#                                                                             #
# Copyright (C) 2009-2015 Edward d'Auvergne                                   #
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
"""Module containing the target functions of the Frame Order theories."""

# Python module imports.
from copy import deepcopy
from math import acos, cos, pi, sin, sqrt
from numpy import add, array, dot, float32, float64, ones, outer, subtract, transpose, uint8, zeros

# relax module imports.
from extern.sobol.sobol_lib import i4_sobol_generate
from lib.alignment.alignment_tensor import to_5D, to_tensor
from lib.alignment.pcs import pcs_tensor
from lib.alignment.rdc import rdc_tensor
from lib.compat import norm
from lib.errors import RelaxError
from lib.float import isNaN
from lib.frame_order.conversions import create_rotor_axis_alpha
from lib.frame_order.double_rotor import compile_2nd_matrix_double_rotor, pcs_numeric_qr_int_double_rotor, pcs_numeric_quad_int_double_rotor
from lib.frame_order.free_rotor import compile_2nd_matrix_free_rotor
from lib.frame_order.iso_cone import compile_2nd_matrix_iso_cone, pcs_numeric_quad_int_iso_cone, pcs_numeric_qr_int_iso_cone
from lib.frame_order.iso_cone_free_rotor import compile_2nd_matrix_iso_cone_free_rotor
from lib.frame_order.iso_cone_torsionless import compile_2nd_matrix_iso_cone_torsionless, pcs_numeric_quad_int_iso_cone_torsionless, pcs_numeric_qr_int_iso_cone_torsionless
from lib.frame_order.matrix_ops import reduce_alignment_tensor
from lib.frame_order.pseudo_ellipse import compile_2nd_matrix_pseudo_ellipse, pcs_numeric_quad_int_pseudo_ellipse, pcs_numeric_qr_int_pseudo_ellipse
from lib.frame_order.pseudo_ellipse_free_rotor import compile_2nd_matrix_pseudo_ellipse_free_rotor
from lib.frame_order.pseudo_ellipse_torsionless import compile_2nd_matrix_pseudo_ellipse_torsionless, pcs_numeric_quad_int_pseudo_ellipse_torsionless, pcs_numeric_qr_int_pseudo_ellipse_torsionless
from lib.frame_order.rotor import compile_2nd_matrix_rotor, pcs_numeric_quad_int_rotor, pcs_numeric_qr_int_rotor
from lib.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID, MODEL_ROTOR
from lib.geometry.coord_transform import spherical_to_cartesian
from lib.geometry.rotations import euler_to_R_zyz, tilt_torsion_to_R, two_vect_to_R
from lib.linear_algebra.kronecker_product import kron_prod
from lib.physical_constants import pcs_constant
from target_functions.chi2 import chi2


class Frame_order:
    """Class containing the target function of the optimisation of Frame Order matrix components."""

    def __init__(self, model=None, init_params=None, full_tensors=None, full_in_ref_frame=None, rdcs=None, rdc_errors=None, rdc_weights=None, rdc_vect=None, dip_const=None, pcs=None, pcs_errors=None, pcs_weights=None, atomic_pos=None, temp=None, frq=None, paramag_centre=zeros(3), scaling_matrix=None, sobol_max_points=200, sobol_oversample=100, com=None, ave_pos_pivot=zeros(3), pivot=None, pivot_opt=False, quad_int=False):
        """Set up the target functions for the Frame Order theories.

        @keyword model:             The name of the Frame Order model.
        @type model:                str
        @keyword init_params:       The initial parameter values.
        @type init_params:          numpy float64 array
        @keyword full_tensors:      An array of the {Axx, Ayy, Axy, Axz, Ayz} values for all full alignment tensors.  The format is [Axx1, Ayy1, Axy1, Axz1, Ayz1, Axx2, Ayy2, Axy2, Axz2, Ayz2, ..., Axxn, Ayyn, Axyn, Axzn, Ayzn].
        @type full_tensors:         numpy nx5D, rank-1 float64 array
        @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
        @type full_in_ref_frame:    numpy rank-1 array
        @keyword rdcs:              The RDC lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type rdcs:                 numpy rank-2 array
        @keyword rdc_errors:        The RDC error lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_errors:           numpy rank-2 array
        @keyword rdc_weights:       The RDC weight lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_weights:          numpy rank-2 array
        @keyword rdc_vect:          The unit XH vector lists corresponding to the RDC values.  The first index must correspond to the spin systems and the second index to the x, y, z elements.
        @type rdc_vect:             numpy rank-2 array
        @keyword dip_const:         The dipolar constants for each RDC.  The indices correspond to the spin systems j.
        @type dip_const:            numpy rank-1 array
        @keyword pcs:               The PCS lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type pcs:                  numpy rank-2 array
        @keyword pcs_errors:        The PCS error lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_errors:           numpy rank-2 array
        @keyword pcs_weights:       The PCS weight lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_weights:          numpy rank-2 array
        @keyword atomic_pos:        The atomic positions of all spins for the PCS and PRE data.  The first index is the spin systems j and the second is the structure or state c.
        @type atomic_pos:           numpy rank-3 array
        @keyword temp:              The temperature of each PCS data set.
        @type temp:                 numpy rank-1 array
        @keyword frq:               The frequency of each PCS data set.
        @type frq:                  numpy rank-1 array
        @keyword paramag_centre:    The paramagnetic centre position (or positions).
        @type paramag_centre:       numpy rank-1, 3D array or rank-2, Nx3 array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 array
        @keyword sobol_max_points:  The maximum number of Sobol' points to use for the numerical PCS integration technique.
        @type sobol_max_points:     int
        @keyword sobol_oversample:  The oversampling factor Ov used for the total number of points N * Ov * 10**M, where N is the maximum number of Sobol' points and M is the number of dimensions or torsion-tilt angles for the system.
        @type sobol_oversample:     int
        @keyword com:               The centre of mass of the system.  This is used for defining the rotor model systems.
        @type com:                  numpy 3D rank-1 array
        @keyword ave_pos_pivot:     The pivot point to rotate all atoms about to the average domain position.  In most cases this will be the centre of mass of the moving domain.  This pivot is shifted by the translation vector.
        @type ave_pos_pivot:        numpy 3D rank-1 array
        @keyword pivot:             The pivot point for the ball-and-socket joint motion.  This is needed if PCS or PRE values are used.
        @type pivot:                numpy rank-1, 3D array or None
        @keyword pivot_opt:         A flag which if True will allow the pivot point of the motion to be optimised.
        @type pivot_opt:            bool
        @keyword quad_int:          A flag which if True will perform high precision numerical integration via the scipy.integrate quad(), dblquad() and tplquad() integration methods rather than the rough quasi-random numerical integration.
        @type quad_int:             bool
        """

        # Model test.
        if not model:
            raise RelaxError("The type of Frame Order model must be specified.")

        # Store the initial parameter (as a copy).
        self.params = deepcopy(init_params)

        # Store the agrs.
        self.model = model
        self.full_tensors = deepcopy(full_tensors)
        self.full_in_ref_frame = deepcopy(full_in_ref_frame)
        self.rdc = deepcopy(rdcs)
        self.rdc_weights = deepcopy(rdc_weights)
        self.rdc_vect = deepcopy(rdc_vect)
        self.dip_const = deepcopy(dip_const)
        self.pcs = deepcopy(pcs)
        self.pcs_weights = deepcopy(pcs_weights)
        self.atomic_pos = deepcopy(atomic_pos)
        self.temp = deepcopy(temp)
        self.frq = deepcopy(frq)
        self.total_num_params = len(init_params)
        self.sobol_max_points = sobol_max_points
        self.sobol_oversample = sobol_oversample
        self.com = deepcopy(com)
        self.pivot_opt = pivot_opt
        self.quad_int = quad_int

        # Tensor setup.
        self._init_tensors()

        # Scaling initialisation.
        self.scaling_matrix = scaling_matrix
        if self.scaling_matrix is not None:
            self.scaling_flag = True
        else:
            self.scaling_flag = False

        # The total number of alignments.
        self.num_align = 0
        if rdcs is not None:
            self.num_align = len(rdcs)
        elif pcs is not None:
            self.num_align = len(pcs)

        # Set the RDC and PCS flags (indicating the presence of data).
        rdc_flag = [True] * self.num_align
        pcs_flag = [True] * self.num_align
        for align_index in range(self.num_align):
            if rdcs is None or len(rdcs[align_index]) == 0:
                rdc_flag[align_index] = False
            if pcs is None or len(pcs[align_index]) == 0:
                pcs_flag[align_index] = False
        self.rdc_flag = sum(rdc_flag)
        self.pcs_flag = sum(pcs_flag)

        # Default translation vector (if not optimised).
        self._translation_vector = zeros(3, float64)

        # Some checks.
        if self.rdc_flag and (rdc_vect is None or not len(rdc_vect)):
            raise RelaxError("The rdc_vect argument " + repr(rdc_vect) + " must be supplied.")
        if self.pcs_flag and (atomic_pos is None or not len(atomic_pos)):
            raise RelaxError("The atomic_pos argument " + repr(atomic_pos) + " must be supplied.")

        # The total number of spins.
        self.num_spins = 0
        if self.pcs_flag:
            self.num_spins = len(pcs[0])

        # The total number of interatomic connections.
        self.num_interatom = 0
        if self.rdc_flag:
            self.num_interatom = len(rdcs[0])

        # Create multi-dimensional versions of certain structures for faster calculations.
        if self.pcs_flag:
            self.spin_ones_struct = ones(self.num_spins, float64)
            self.pivot = outer(self.spin_ones_struct, pivot)
            self.paramag_centre = outer(self.spin_ones_struct, paramag_centre)
            self.ave_pos_pivot = outer(self.spin_ones_struct, ave_pos_pivot)
        else:
            self.pivot = array([pivot])

        # Set up the alignment data.
        for align_index in range(self.num_align):
            to_tensor(self.A_3D[align_index], self.full_tensors[5*align_index:5*align_index+5])

        # PCS errors.
        if self.pcs_flag:
            err = False
            for i in range(len(pcs_errors)):
                for j in range(len(pcs_errors[i])):
                    if not isNaN(pcs_errors[i, j]):
                        err = True
            if err:
                self.pcs_error = pcs_errors
            else:
                # Missing errors (default to 0.1 ppm errors).
                self.pcs_error = 0.1 * 1e-6 * ones((self.num_align, self.num_spins), float64)

        # RDC errors.
        if self.rdc_flag:
            err = False
            for i in range(len(rdc_errors)):
                for j in range(len(rdc_errors[i])):
                    if not isNaN(rdc_errors[i, j]):
                        err = True
            if err:
                self.rdc_error = rdc_errors
            else:
                # Missing errors (default to 1 Hz errors).
                self.rdc_error = ones((self.num_align, self.num_interatom), float64)

        # Missing data matrices (RDC).
        if self.rdc_flag:
            self.missing_rdc = zeros((self.num_align, self.num_interatom), uint8)

        # Missing data matrices (PCS).
        if self.pcs_flag:
            self.missing_pcs = zeros((self.num_align, self.num_spins), uint8)

        # Clean up problematic data and put the weights into the errors..
        if self.rdc_flag or self.pcs_flag:
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                if self.rdc_flag:
                    for j in range(self.num_interatom):
                        if isNaN(self.rdc[align_index, j]):
                            # Set the flag.
                            self.missing_rdc[align_index, j] = 1

                            # Change the NaN to zero.
                            self.rdc[align_index, j] = 0.0

                            # Change the error to one (to avoid zero division).
                            self.rdc_error[align_index, j] = 1.0

                            # Change the weight to one.
                            rdc_weights[align_index, j] = 1.0

                    # The RDC weights.
                    if self.rdc_flag:
                        self.rdc_error[align_index, j] = self.rdc_error[align_index, j] / sqrt(rdc_weights[align_index, j])

                # Loop over the PCSs.
                if self.pcs_flag:
                    for j in range(self.num_spins):
                        if isNaN(self.pcs[align_index, j]):
                            # Set the flag.
                            self.missing_pcs[align_index, j] = 1

                            # Change the NaN to zero.
                            self.pcs[align_index, j] = 0.0

                            # Change the error to one (to avoid zero division).
                            self.pcs_error[align_index, j] = 1.0

                            # Change the weight to one.
                            pcs_weights[align_index, j] = 1.0

                    # The PCS weights.
                    if self.pcs_flag:
                        self.pcs_error[align_index, j] = self.pcs_error[align_index, j] / sqrt(pcs_weights[align_index, j])

        # The paramagnetic centre vectors and distances.
        if self.pcs_flag:
            # Initialise the data structures.
            self.paramag_unit_vect = zeros(atomic_pos.shape, float64)
            self.paramag_dist = zeros(self.num_spins, float64)
            self.pcs_const = zeros((self.num_align, self.num_spins), float64)
            self.r_pivot_atom = zeros((self.num_spins, 3), float32)
            self.r_pivot_atom_rev = zeros((self.num_spins, 3), float32)
            self.r_ln_pivot = self.pivot - self.paramag_centre

            # Set up the paramagnetic constant (without the interatomic distance and in Angstrom units).
            for align_index in range(self.num_align):
                self.pcs_const[align_index] = pcs_constant(self.temp[align_index], self.frq[align_index], 1.0) * 1e30

        # PCS function, gradient, and Hessian matrices.
        self.pcs_theta = None
        if self.pcs_flag:
            self.pcs_theta = zeros((self.num_align, self.num_spins), float64)
            self.pcs_theta_err = zeros((self.num_align, self.num_spins), float64)
            self.dpcs_theta = zeros((self.total_num_params, self.num_align, self.num_spins), float64)
            self.d2pcs_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_spins), float64)

        # RDC function, gradient, and Hessian matrices.
        self.rdc_theta = None
        if self.rdc_flag:
            self.rdc_theta = zeros((self.num_align, self.num_interatom), float64)
            self.drdc_theta = zeros((self.total_num_params, self.num_align, self.num_interatom), float64)
            self.d2rdc_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_interatom), float64)

        # The target function extension.
        ext = '_qr_int'
        if self.quad_int:
            ext = '_quad_int'

        # Non-numerical models.
        if model in [MODEL_RIGID]:
            if model == MODEL_RIGID:
                self.func = self.func_rigid

        # The Sobol' sequence data and target function aliases.
        else:
            if model == MODEL_PSEUDO_ELLIPSE:
                self.create_sobol_data(dims=['theta', 'phi', 'sigma'])
                self.func = getattr(self, 'func_pseudo_ellipse'+ext)
            elif model == MODEL_PSEUDO_ELLIPSE_TORSIONLESS:
                self.create_sobol_data(dims=['theta', 'phi'])
                self.func = getattr(self, 'func_pseudo_ellipse_torsionless'+ext)
            elif model == MODEL_PSEUDO_ELLIPSE_FREE_ROTOR:
                self.create_sobol_data(dims=['theta', 'phi', 'sigma'])
                self.func = getattr(self, 'func_pseudo_ellipse_free_rotor'+ext)
            elif model == MODEL_ISO_CONE:
                self.create_sobol_data(dims=['theta', 'phi', 'sigma'])
                self.func = getattr(self, 'func_iso_cone'+ext)
            elif model == MODEL_ISO_CONE_TORSIONLESS:
                self.create_sobol_data(dims=['theta', 'phi'])
                self.func = getattr(self, 'func_iso_cone_torsionless'+ext)
            elif model == MODEL_ISO_CONE_FREE_ROTOR:
                self.create_sobol_data(dims=['theta', 'phi', 'sigma'])
                self.func = getattr(self, 'func_iso_cone_free_rotor'+ext)
            elif model == MODEL_ROTOR:
                self.create_sobol_data(dims=['sigma'])
                self.func = getattr(self, 'func_rotor'+ext)
            elif model == MODEL_FREE_ROTOR:
                self.create_sobol_data(dims=['sigma'])
                self.func = getattr(self, 'func_free_rotor'+ext)
            elif model == MODEL_DOUBLE_ROTOR:
                self.create_sobol_data(dims=['sigma', 'sigma2'])
                self.func = getattr(self, 'func_double_rotor'+ext)


    def _init_tensors(self):
        """Set up isotropic cone optimisation against the alignment tensor data."""

        # Some checks.
        if self.full_tensors is None or not len(self.full_tensors):
            raise RelaxError("The full_tensors argument " + repr(self.full_tensors) + " must be supplied.")
        if self.full_in_ref_frame is None or not len(self.full_in_ref_frame):
            raise RelaxError("The full_in_ref_frame argument " + repr(self.full_in_ref_frame) + " must be supplied.")

        # Tensor set up.
        self.num_tensors = int(len(self.full_tensors) / 5)
        self.A_3D = zeros((self.num_tensors, 3, 3), float64)
        self.A_3D_bc = zeros((self.num_tensors, 3, 3), float64)
        self.A_5D_bc = zeros(self.num_tensors*5, float64)

        # The rotation to the Frame Order eigenframe.
        self.R_eigen = zeros((3, 3), float64)
        self.R_eigen_2 = zeros((3, 3), float64)
        self.R_ave = zeros((3, 3), float64)
        self.Ri_prime = zeros((3, 3), float64)
        self.Ri2_prime = zeros((3, 3), float64)
        self.tensor_3D = zeros((3, 3), float64)

        # The cone axis storage and molecular frame z-axis.
        self.cone_axis = zeros(3, float64)
        self.z_axis = array([0, 0, 1], float64)

        # The rotor axes.
        self.rotor_axis = zeros(3, float64)
        self.rotor_axis_2 = zeros(3, float64)

        # Initialise the Frame Order matrices.
        self.frame_order_2nd = zeros((9, 9), float64)

        # A rotation matrix for general use.
        self.R = zeros((3, 3), float64)


    def func_double_rotor_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the double rotor model.

        This function optimises the model parameters using the RDC and PCS base data.  Quasi-random, Sobol' sequence based, numerical integration is used for the PCS.


        @param params:  The vector of parameter values.  These can include {pivot_x, pivot_y, pivot_z, pivot_disp, ave_pos_x, ave_pos_y, ave_pos_z, ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_sigma_max, cone_sigma_max_2}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot2 = outer(self.spin_ones_struct, params[:3])
            param_disp = params[3]
            self._translation_vector = params[4:7]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, sigma_max, sigma_max_2 = params[7:]
        else:
            pivot2 = self.pivot
            param_disp = params[0]
            self._translation_vector = params[1:4]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, sigma_max, sigma_max_2 = params[4:]

        # Reconstruct the full eigenframe of the motion.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_double_rotor(self.frame_order_2nd, Rx2_eigen, sigma_max, sigma_max_2)

        # The average frame rotation matrix (and reduce and rotate the tensors).
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            # The 1st pivot point (sum of the 2nd pivot and the displacement along the eigenframe z-axis).
            pivot = pivot2 + param_disp * self.R_eigen[:, 2]

            # Calculate the vectors.
            self.calc_vectors(pivot=pivot, pivot2=pivot2, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_double_rotor(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, sigma_max=sigma_max, sigma_max_2=sigma_max_2, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, r_inter_pivot=self.r_inter_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, Ri2_prime=sobol_data.Ri2_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_double_rotor_quad_int(self, params):
        """SciPy quadratic integration target function for the double rotor model.

        This function optimises the model parameters using the RDC and PCS base data.  Quasi-random, Sobol' sequence based, numerical integration is used for the PCS.


        @param params:  The vector of parameter values.  These can include {pivot_x, pivot_y, pivot_z, pivot_disp, ave_pos_x, ave_pos_y, ave_pos_z, ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_sigma_max, cone_sigma_max_2}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot2 = outer(self.spin_ones_struct, params[:3])
            param_disp = params[3]
            self._translation_vector = params[4:7]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, sigma_max, sigma_max_2 = params[7:]
        else:
            pivot2 = self.pivot
            param_disp = params[0]
            self._translation_vector = params[1:4]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, sigma_max, sigma_max_2 = params[4:]

        # Reconstruct the full eigenframe of the motion.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_double_rotor(self.frame_order_2nd, Rx2_eigen, sigma_max, sigma_max_2)

        # The average frame rotation matrix (and reduce and rotate the tensors).
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            # The 1st pivot point (sum of the 2nd pivot and the displacement along the eigenframe z-axis).
            pivot = pivot2 + param_disp * self.R_eigen[:, 2]

            # Calculate the vectors.
            self.calc_vectors(pivot=pivot, pivot2=pivot2, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_double_rotor(sigma_max=sigma_max, sigma_max_2=sigma_max_2, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], r_inter_pivot=self.r_inter_pivot[j], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime, Ri2_prime=self.Ri2_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_free_rotor_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the free rotor model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, axis_alpha = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_alpha = params[3:]

        # Generate the rotor axis.
        self.cone_axis = create_rotor_axis_alpha(alpha=axis_alpha, pivot=pivot[0], point=self.com)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_free_rotor(self.frame_order_2nd, Rx2_eigen)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_rotor(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])


        # Return the chi-squared value.
        return chi2_sum


    def func_free_rotor_quad_int(self, params):
        """SciPy quadratic integration target function for the free rotor model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, axis_alpha = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_alpha = params[3:]

        # Generate the rotor axis.
        self.cone_axis = create_rotor_axis_alpha(alpha=axis_alpha, pivot=pivot[0], point=self.com)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_free_rotor(self.frame_order_2nd, Rx2_eigen)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_rotor(sigma_max=pi, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the isotropic cone model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, theta, phi, cone_theta, sigma_max} where the first 3 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, cone_theta is the cone opening half angle, and sigma_max is the torsion angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[3:]

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone(self.frame_order_2nd, Rx2_eigen, cone_theta, sigma_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_iso_cone(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, theta_max=cone_theta, sigma_max=sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_quad_int(self, params):
        """SciPy quadratic integration target function for the isotropic cone model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, s1} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and s1 is the isotropic cone order parameter.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, sigma_max = params[3:]

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone(self.frame_order_2nd, Rx2_eigen, cone_theta, sigma_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_iso_cone(theta_max=cone_theta, sigma_max=sigma_max, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_free_rotor_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the free rotor isotropic cone model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, s1} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and s1 is the isotropic cone order parameter.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, theta_max = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, theta_max = params[3:]

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone_free_rotor(self.frame_order_2nd, Rx2_eigen, theta_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_iso_cone(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, theta_max=theta_max, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_free_rotor_quad_int(self, params):
        """SciPy quadratic integration target function for the free rotor isotropic cone model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, s1} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and s1 is the isotropic cone order parameter.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, theta_max = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, theta_max = params[3:]

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone_free_rotor(self.frame_order_2nd, Rx2_eigen, theta_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_iso_cone(theta_max=theta_max, sigma_max=pi, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_torsionless_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the torsionless isotropic cone model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, cone_theta} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and cone_theta is cone opening angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[3:]

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone_torsionless(self.frame_order_2nd, Rx2_eigen, cone_theta)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_iso_cone_torsionless(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, theta_max=cone_theta, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_iso_cone_torsionless_quad_int(self, params):
        """SciPy quadratic integration target function for the torsionless isotropic cone model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {beta, gamma, theta, phi, cone_theta} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and cone_theta is cone opening angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = params[3:]

        # Generate the cone axis from the spherical angles.
        spherical_to_cartesian([1.0, axis_theta, axis_phi], self.cone_axis)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone_torsionless(self.frame_order_2nd, Rx2_eigen, cone_theta)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_iso_cone_torsionless(theta_max=cone_theta, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the pseudo-ellipse model.

        This function optimises the model parameters using the RDC and PCS base data.  Quasi-random, Sobol' sequence based, numerical integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 3 are the pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[3:]

        # Reconstruct the full eigenframe of the motion.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y, cone_sigma_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_pseudo_ellipse(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=cone_sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_quad_int(self, params):
        """SciPy quadratic integration target function for the pseudo-ellipse model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 3 are the pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params[3:]

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y, cone_sigma_max)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_pseudo_ellipse(theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=cone_sigma_max, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_free_rotor_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the free-rotor pseudo-ellipse model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the free_rotor pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]

        # Reconstruct the full eigenframe of the motion.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_pseudo_ellipse(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=pi, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_free_rotor_quad_int(self, params):
        """SciPy quadratic integration target function for the free-rotor pseudo-ellipse model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the free_rotor pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse_free_rotor(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(0.0, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_pseudo_ellipse(theta_x=cone_theta_x, theta_y=cone_theta_y, sigma_max=pi, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_torsionless_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the torsionless pseudo-ellipse model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Simple numerical integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the torsionless pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]

        # Reconstruct the full eigenframe of the motion.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse_torsionless(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_pseudo_ellipse_torsionless(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, theta_x=cone_theta_x, theta_y=cone_theta_y, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_pseudo_ellipse_torsionless_quad_int(self, params):
        """SciPy quadratic integration target function for the torsionless pseudo-ellipse model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 2 are the torsionless pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = params[3:]

        # Average position rotation.
        euler_to_R_zyz(eigen_alpha, eigen_beta, eigen_gamma, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse_torsionless(self.frame_order_2nd, Rx2_eigen, cone_theta_x, cone_theta_y)

        # Reduce and rotate the tensors.
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_pseudo_ellipse_torsionless(theta_x=cone_theta_x, theta_y=cone_theta_y, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_rigid(self, params):
        """Target function for rigid model optimisation.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        self._translation_vector = params[:3]
        ave_pos_alpha, ave_pos_beta, ave_pos_gamma = params[3:6]

        # The average frame rotation matrix (and reduce and rotate the tensors).
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma)

        # Pre-transpose matrices for faster calculations.
        RT_ave = transpose(self.R_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS.
        if self.pcs_flag:
            # Pre-calculate all the necessary vectors.
            self.calc_vectors(pivot=self.pivot, R_ave=self.R_ave, RT_ave=RT_ave)
            r_ln_atom = self.r_ln_pivot + self.r_pivot_atom
            if min(self.full_in_ref_frame) == 0:
                r_ln_atom_rev = self.r_ln_pivot + self.r_pivot_atom_rev

            # The vector length (to the inverse 5th power).
            length = 1.0 / norm(r_ln_atom, axis=1)**5
            if min(self.full_in_ref_frame) == 0:
                length_rev = 1.0 / norm(r_ln_atom, axis=1)**5

            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_ln_atom_i = r_ln_atom[j]
                            length_i = length[j]
                        else:
                            r_ln_atom_i = r_ln_atom_rev[j]
                            length_i = length_rev[j]

                        # The PCS calculation.
                        self.pcs_theta[align_index, j] = pcs_tensor(self.pcs_const[align_index, j] * length_i, r_ln_atom_i, self.A_3D[align_index])

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_rotor_qr_int(self, params):
        """Quasi-random Sobol' integration target function for the rotor model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Quasi-random, Sobol' sequence based, numerical integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi, sigma_max}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_alpha, sigma_max = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_alpha, sigma_max = params[3:]

        # Generate the rotor axis.
        self.cone_axis = create_rotor_axis_alpha(alpha=axis_alpha, pivot=pivot[0], point=self.com)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_rotor(self.frame_order_2nd, Rx2_eigen, sigma_max)

        # The average frame rotation matrix (and reduce and rotate the tensors).
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Numerical integration of the PCSs.
            pcs_numeric_qr_int_rotor(points=sobol_data.sobol_angles, max_points=self.sobol_max_points, sigma_max=sigma_max, c=self.pcs_const, full_in_ref_frame=self.full_in_ref_frame, r_pivot_atom=self.r_pivot_atom, r_pivot_atom_rev=self.r_pivot_atom_rev, r_ln_pivot=self.r_ln_pivot, A=self.A_3D, R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=sobol_data.Ri_prime, pcs_theta=self.pcs_theta, pcs_theta_err=self.pcs_theta_err, missing_pcs=self.missing_pcs)

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            for align_index in range(self.num_align):
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def func_rotor_quad_int(self, params):
        """SciPy quadratic integration target function for rotor model.

        This function optimises the isotropic cone model parameters using the RDC and PCS base data.  Scipy quadratic integration is used for the PCS.


        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma, theta, phi, sigma_max}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameters.
        if self.pivot_opt:
            pivot = outer(self.spin_ones_struct, params[:3])
            self._translation_vector = params[3:6]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_alpha, sigma_max = params[6:]
        else:
            pivot = self.pivot
            self._translation_vector = params[:3]
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_alpha, sigma_max = params[3:]

        # Generate the rotor axis.
        self.cone_axis = create_rotor_axis_alpha(alpha=axis_alpha, pivot=pivot[0], point=self.com)

        # Pre-calculate the eigenframe rotation matrix.
        two_vect_to_R(self.z_axis, self.cone_axis, self.R_eigen)

        # The Kronecker product of the eigenframe rotation.
        Rx2_eigen = kron_prod(self.R_eigen, self.R_eigen)

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_rotor(self.frame_order_2nd, Rx2_eigen, sigma_max)

        # The average frame rotation matrix (and reduce and rotate the tensors).
        self.reduce_and_rot(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, frame_order_2nd)

        # Pre-transpose matrices for faster calculations.
        RT_eigen = transpose(self.R_eigen)
        RT_ave = transpose(self.R_ave)

        # Pre-calculate all the necessary vectors.
        if self.pcs_flag:
            self.calc_vectors(pivot=pivot, R_ave=self.R_ave, RT_ave=RT_ave)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # RDCs.
        if self.rdc_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the RDCs.
                for j in range(self.num_interatom):
                    # The back calculated RDC.
                    if not self.missing_rdc[align_index, j]:
                        self.rdc_theta[align_index, j] = rdc_tensor(self.dip_const[j], self.rdc_vect[j], self.A_3D_bc[align_index])

                # Calculate and sum the single alignment chi-squared value (for the RDC).
                chi2_sum = chi2_sum + chi2(self.rdc[align_index], self.rdc_theta[align_index], self.rdc_error[align_index])

        # PCS via numerical integration.
        if self.pcs_flag:
            # Loop over each alignment.
            for align_index in range(self.num_align):
                # Loop over the PCSs.
                for j in range(self.num_spins):
                    # The back calculated PCS.
                    if not self.missing_pcs[align_index, j]:
                        # Forwards and reverse rotations.
                        if self.full_in_ref_frame[align_index]:
                            r_pivot_atom = self.r_pivot_atom[j]
                        else:
                            r_pivot_atom = self.r_pivot_atom_rev[j]

                        # The numerical integration.
                        self.pcs_theta[align_index, j] = pcs_numeric_quad_int_rotor(sigma_max=sigma_max, c=self.pcs_const[align_index, j], r_pivot_atom=r_pivot_atom, r_ln_pivot=self.r_ln_pivot[0], A=self.A_3D[align_index], R_eigen=self.R_eigen, RT_eigen=RT_eigen, Ri_prime=self.Ri_prime)

                # Calculate and sum the single alignment chi-squared value (for the PCS).
                chi2_sum = chi2_sum + chi2(self.pcs[align_index], self.pcs_theta[align_index], self.pcs_error[align_index])

        # Return the chi-squared value.
        return chi2_sum


    def calc_vectors(self, pivot=None, pivot2=None, R_ave=None, RT_ave=None):
        """Calculate the pivot to atom and lanthanide to pivot vectors for the target functions.

        @keyword pivot:     The pivot point.
        @type pivot:        numpy rank-1, 3D array
        @keyword pivot2:    The 2nd pivot point.
        @type pivot2:       numpy rank-1, 3D array
        @keyword R_ave:     The rotation matrix for rotating from the reference frame to the average position.
        @type R_ave:        numpy rank-2, 3D array
        @keyword RT_ave:    The transpose of R_ave.
        @type RT_ave:       numpy rank-2, 3D array
        """

        # The lanthanide to pivot vector.
        if self.pivot_opt:
            subtract(pivot, self.paramag_centre, self.r_ln_pivot)
        if pivot2 is not None:
            subtract(pivot2, self.paramag_centre, self.r_ln_pivot)

        # Calculate the average position pivot point to atomic positions vectors once.
        vect = self.atomic_pos - self.ave_pos_pivot

        # Rotate then translate the atomic positions, then calculate the pivot to atom vector.
        self.r_pivot_atom[:] = dot(vect, RT_ave)
        add(self.r_pivot_atom, self.ave_pos_pivot, self.r_pivot_atom)
        add(self.r_pivot_atom, self._translation_vector, self.r_pivot_atom)
        subtract(self.r_pivot_atom, pivot, self.r_pivot_atom)

        # And the reverse vectors.
        if min(self.full_in_ref_frame) == 0:
            self.r_pivot_atom_rev[:] = dot(vect, R_ave)
            add(self.r_pivot_atom_rev, self.ave_pos_pivot, self.r_pivot_atom_rev)
            add(self.r_pivot_atom_rev, self._translation_vector, self.r_pivot_atom_rev)
            subtract(self.r_pivot_atom_rev, pivot, self.r_pivot_atom_rev)

        # Calculate the inter-pivot vector for the double motion models.
        if pivot2 is not None:
            self.r_inter_pivot = pivot - pivot2


    def create_sobol_data(self, dims=None):
        """Create the Sobol' quasi-random data for numerical integration.

        This uses the external sobol_lib module to create the data.  The algorithm is that modified by Antonov and Saleev.


        @keyword dims:      The list of parameters.
        @type dims:         list of str
        """

        # Quadratic integration active, so nothing to do here!
        if self.quad_int:
            return

        # The number of dimensions.
        m = len(dims)

        # The total number of points.
        total_num = int(self.sobol_max_points * self.sobol_oversample * 10**m)

        # Reuse pre-created data if available.
        if total_num == sobol_data.total_num and self.model == sobol_data.model:
            return

        # Printout (useful to see how long this takes!).
        print("Generating the torsion-tilt angle sampling via the Sobol' sequence for numerical PCS integration.")

        # Initialise.
        sobol_data.model = self.model
        sobol_data.total_num = total_num
        sobol_data.sobol_angles = zeros((m, total_num), float32)
        sobol_data.Ri_prime = zeros((total_num, 3, 3), float32)
        sobol_data.Ri2_prime = zeros((total_num, 3, 3), float32)

        # The Sobol' points.
        points = i4_sobol_generate(m, total_num, 1000)

        # Loop over the points.
        for i in range(total_num):
            # Loop over the dimensions, converting the points to angles.
            theta = None
            phi = None
            sigma = None
            for j in range(m):
                # The tilt angle - the angle of rotation about the x-y plane rotation axis.
                if dims[j] in ['theta']:
                    theta = acos(2.0*points[j, i] - 1.0)
                    sobol_data.sobol_angles[j, i] = theta

                # The angle defining the x-y plane rotation axis.
                if dims[j] in ['phi']:
                    phi = 2.0 * pi * points[j, i]
                    sobol_data.sobol_angles[j, i] = phi

                # The 1st torsion angle - the angle of rotation about the z' axis (or y' for the double motion models).
                if dims[j] in ['sigma']:
                    sigma = 2.0 * pi * (points[j, i] - 0.5)
                    sobol_data.sobol_angles[j, i] = sigma

                # The 2nd torsion angle - the angle of rotation about the x' axis.
                if dims[j] in ['sigma2']:
                    sigma2 = 2.0 * pi * (points[j, i] - 0.5)
                    sobol_data.sobol_angles[j, i] = sigma2

            # Pre-calculate the rotation matrices for the double motion models.
            if 'sigma2' in dims:
                # The 1st rotation about the y-axis.
                c_sigma = cos(sigma)
                s_sigma = sin(sigma)
                sobol_data.Ri_prime[i, 0, 0] =  c_sigma
                sobol_data.Ri_prime[i, 0, 2] =  s_sigma
                sobol_data.Ri_prime[i, 1, 1] = 1.0
                sobol_data.Ri_prime[i, 2, 0] = -s_sigma
                sobol_data.Ri_prime[i, 2, 2] =  c_sigma

                # The 2nd rotation about the x-axis.
                c_sigma2 = cos(sigma2)
                s_sigma2 = sin(sigma2)
                sobol_data.Ri2_prime[i, 0, 0] = 1.0
                sobol_data.Ri2_prime[i, 1, 1] =  c_sigma2
                sobol_data.Ri2_prime[i, 1, 2] = -s_sigma2
                sobol_data.Ri2_prime[i, 2, 1] =  s_sigma2
                sobol_data.Ri2_prime[i, 2, 2] =  c_sigma2

            # Pre-calculate the rotation matrix for the full tilt-torsion.
            elif theta != None and phi != None and sigma != None:
                tilt_torsion_to_R(phi, theta, sigma, sobol_data.Ri_prime[i])

            # Pre-calculate the rotation matrix for the torsionless models.
            elif sigma == None:
                c_theta = cos(theta)
                s_theta = sin(theta)
                c_phi = cos(phi)
                s_phi = sin(phi)
                c_phi_c_theta = c_phi * c_theta
                s_phi_c_theta = s_phi * c_theta
                sobol_data.Ri_prime[i, 0, 0] =  c_phi_c_theta*c_phi + s_phi**2
                sobol_data.Ri_prime[i, 0, 1] =  c_phi_c_theta*s_phi - c_phi*s_phi
                sobol_data.Ri_prime[i, 0, 2] =  c_phi*s_theta
                sobol_data.Ri_prime[i, 1, 0] =  s_phi_c_theta*c_phi - c_phi*s_phi
                sobol_data.Ri_prime[i, 1, 1] =  s_phi_c_theta*s_phi + c_phi**2
                sobol_data.Ri_prime[i, 1, 2] =  s_phi*s_theta
                sobol_data.Ri_prime[i, 2, 0] = -s_theta*c_phi
                sobol_data.Ri_prime[i, 2, 1] = -s_theta*s_phi
                sobol_data.Ri_prime[i, 2, 2] =  c_theta

            # Pre-calculate the rotation matrix for the rotor models.
            else:
                c_sigma = cos(sigma)
                s_sigma = sin(sigma)
                sobol_data.Ri_prime[i, 0, 0] =  c_sigma
                sobol_data.Ri_prime[i, 0, 1] = -s_sigma
                sobol_data.Ri_prime[i, 1, 0] =  s_sigma
                sobol_data.Ri_prime[i, 1, 1] =  c_sigma
                sobol_data.Ri_prime[i, 2, 2] = 1.0

        # Printout (useful to see how long this takes!).
        print("   Oversampled to %s points." % total_num)


    def reduce_and_rot(self, ave_pos_alpha=None, ave_pos_beta=None, ave_pos_gamma=None, daeg=None):
        """Reduce and rotate the alignments tensors using the frame order matrix and Euler angles.

        @keyword ave_pos_alpha: The alpha Euler angle describing the average domain position, the tensor rotation.
        @type ave_pos_alpha:    float
        @keyword ave_pos_beta:  The beta Euler angle describing the average domain position, the tensor rotation.
        @type ave_pos_beta:     float
        @keyword ave_pos_gamma: The gamma Euler angle describing the average domain position, the tensor rotation.
        @type ave_pos_gamma:    float
        @keyword daeg:          The 2nd degree frame order matrix.
        @type daeg:             rank-2, 9D array
        """

        # Alignment tensor rotation.
        euler_to_R_zyz(ave_pos_alpha, ave_pos_beta, ave_pos_gamma, self.R_ave)

        # Back calculate the rotated tensors.
        for align_index in range(self.num_tensors):
            # Tensor indices.
            index1 = align_index*5
            index2 = align_index*5+5

            # Reduction.
            if daeg is not None:
                # Reduce the tensor.
                reduce_alignment_tensor(daeg, self.full_tensors[index1:index2], self.A_5D_bc[index1:index2])

                # Convert the reduced tensor to 3D, rank-2 form.
                to_tensor(self.tensor_3D, self.A_5D_bc[index1:index2])

            # No reduction:
            else:
                # Convert the original tensor to 3D, rank-2 form.
                to_tensor(self.tensor_3D, self.full_tensors[index1:index2])

            # Rotate the tensor (normal R.X.RT rotation).
            if self.full_in_ref_frame[align_index]:
                self.A_3D_bc[align_index] = dot(transpose(self.R_ave), dot(self.tensor_3D, self.R_ave))

            # Rotate the tensor (inverse RT.X.R rotation).
            else:
                self.A_3D_bc[align_index] = dot(self.R_ave, dot(self.tensor_3D, transpose(self.R_ave)))

            # Convert the tensor back to 5D, rank-1 form, as the back-calculated reduced tensor.
            to_5D(self.A_5D_bc[index1:index2], self.A_3D_bc[align_index])



class Sobol_data:
    """Temporary storage of the Sobol' data for speed."""

    def __init__(self):
        """Set up the object."""

        # Initialise some variables.
        self.model = None
        self.Ri_prime = None
        self.Ri2_prime = None
        self.sobol_angles = None
        self.total_num = None


# Instantiate the Sobol' data container.
sobol_data = Sobol_data()
