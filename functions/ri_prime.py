from math import pi
from Numeric import Float64, zeros
from re import match


def calc_ri_prime(data, ri_prime_funcs):
	"""Function for back calculation of the transformed relaxation values R1, R2, and sigma_noe.

	The transformed relaxation equations
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  self.data.ri_prime
	Dimension:  1D, (transformed relaxation data)
	Type:  Numeric array, Float64
	Dependencies:  self.data.jw
	Required by:  self.data.ri, self.data.dri, self.data.d2ri


	Formulae
	~~~~~~~~

	Components
	~~~~~~~~~~
		      1   / mu0  \ 2  (gH.gN.h_bar)**2
		d  =  - . | ---- |  . ----------------
		      4   \ 4.pi /         <r**6>

		      (wN.csa)**2
		c  =  -----------
		           3

		J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

		J_R1_c  =  J(wN)

		J_R2_d  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

		J_R2_c  =  4J(0) + 3J(wN)

		J_sigma_noe  =  6J(wH+wN) - J(wH-wN)


	Relaxation equations
	~~~~~~~~~~~~~~~~~~~~

		R1()  =  d . J_R1_d  +  c . J_R1_c


		         d              c
		R2()  =  - . J_R2_d  +  - . J_R2_c  +  Rex
		         2              6


		sigma_noe()  =  d . J_sigma_noe

	"""

	# Calculate the components of the transformed relaxation equations.
	for i in range(data.num_ri):
		ri_prime_funcs[i](data, i, data.remap_table[i])

	# Calculate the transformed relaxation values.
	data.ri_prime = data.dip_comps * data.j_dip_comps + data.csa_comps * data.j_csa_comps + data.rex_comps


def calc_r1_prime(data, i, frq_num):
	"""Calculate the r1 components.

	R1()  =  d . J_R1_d  +  c . J_R1_c

	J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

	J_R1_c  =  J(wN)

	"""
	data.dip_comps[i] = data.dipole_const
	data.j_dip_comps[i] = data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num]
	data.j_csa_comps[i] = data.jw[frq_num, 1]


def calc_r2_prime(data, i, frq_num):
	"""Calculate the r2 components.

	         d              c
	R2()  =  - . J_R2_d  +  - . J_R2_c
	         2              6

	J_R2_d  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

	J_R2_c  =  4J(0) + 3J(wN)

	"""

	data.dip_comps[i] = data.dipole_const / 2.0
	data.j_dip_comps[i] = 4.0*data.jw[frq_num, 0] + data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 3] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num] / 6.0
	data.j_csa_comps[i] = 4.0*data.jw[frq_num, 0] + 3.0*data.jw[frq_num, 1]


def calc_r2_rex_prime(data, i, frq_num):
	"""Calculate the r2 components including chemical exchange.

	         d              c
	R2()  =  - . J_R2_d  +  - . J_R2_c  +  Rex
	         2              6

	J_R2_d  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

	J_R2_c  =  4J(0) + 3J(wN)

	"""

	data.dip_comps[i] = data.dipole_const / 2.0
	data.j_dip_comps[i] = 4.0*data.jw[frq_num, 0] + data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 3] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num] / 6.0
	data.j_csa_comps[i] = 4.0*data.jw[frq_num, 0] + 3.0*data.jw[frq_num, 1]
	data.rex_comps[i] = data.params[data.ri_indecies[0]] * (1e-8 * data.frq[frq_num])**2


def calc_sigma_noe(data, i, frq_num):
	"""Calculate the sigma_noe components.

	sigma_noe()  =  d . J_sigma_noe

	J_sigma_noe  =  6J(wH+wN) - J(wH-wN)

	"""

	data.dip_comps[i] = data.dipole_const
	data.j_dip_comps[i] = 6.0*data.jw[frq_num, 4] - data.jw[frq_num, 2]
