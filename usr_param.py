# usr_param.py v0.3                  4 January 2002        Edward d'Auvergne
#
# Class containing all the user specified parameters.  Used by the program mf.
# Make sure the version numbers between the program and this class are identical.


class usr_param:
	def __init__(self):
		"Class containing parameters specified by the user"

		self.version = 0.3
		self.init_input()
		self.init_method_param()
		self.init_run_param()
		self.init_mfin_param()
		self.init_mfpar_param()
		self.init_mfmodel_param()


	def init_input(self):
		"""Specify the input data.

		To be compatible with the program Modelfree, the relaxation data should be placed in the order {R1, R2, NOE}
		and from highest field strength to lowest.

		The structure of self.input_info is as follows:  The fields of the first dimension correspond
		to each relaxation data set and is flexible in size, ie len(self.input_info) = number of data sets.
		The second dimension have the following fixed fields:
			0 - Data type (R1, R2, or NOE)
			1 - NMR frequency label
			2 - NMR proton frequency in MHz
			3 - The name of the file containing the relaxation data

		The structure of self.nmr_frq is as follows:  The length of the first dimension is equal to the number
		of field strengths.  The fields of the second are:
			0 - NMR frequency label
			1 - NMR proton frequency in MHz
			2 - R1 flag (0 or 1 depending if data is present).
			3 - R2 flag (0 or 1 depending if data is present).
			4 - NOE flag (0 or 1 depending if data is present).
		"""

		self.input_info = []
		self.input_info.append(['R1', '600', 600.0, 'r1.600.out'])
		self.input_info.append(['R2', '600', 600.0, 'r2.600.out'])
		self.input_info.append(['NOE', '600', 600.0, 'noe.600.out'])
		self.input_info.append(['R1', '500', 500.0, 'r1.500.out'])
		self.input_info.append(['R2', '500', 500.0, 'r2.500.out'])
		self.input_info.append(['NOE', '500', 500.0, 'noe.500.out'])

		self.nmr_frq = []
		self.nmr_frq.append(['600', 600.0, '1', '1', '1'])
		self.nmr_frq.append(['500', 500.0, '1', '1', '1'])


	def init_method_param(self):
		"""Model-free analysis method info.

		self.method can be set to the following:

		AIC:	Method of model-free analysis based on model selection using the Akaike Information
			Criteria.

		AICc:	Method of model-free analysis based on model selection using the Akaike Information
			Criteria corrected for finit sample size.

		BIC:	Method of model-free analysis based on model selection using the Schwartz
			Information Criteria.

		Bootstrap:	Modelfree analysis based on model selection using bootstrap methods to
				estimate the overall discrepency.

		CV:	Modelfree analysis based on model selection using cross-validation methods to
				estimate the overall discrepency.

		Farrow:	The method given by Farrow et al., 1994.

		Palmer:	The method given by Mandel et al., 1995.

		Overall:	Calculate the realized overall discrepency (real model-free parameters
				must be known).
		"""

		self.method = 'CV'

		# The following three values are only used in Palmer's method and won't affect the others.
		self.chi2_lim = 0.90      # Set the chi squared cutoff (1 - alpha critical value).
		self.ftest_lim = 0.80     # Set the F-test cutoff (1 - alpha critical value).
		self.large_chi2 = 20.0      # Set the maximum chi squared value.


	def init_run_param(self):
		"Run file parameters"

		self.pdb_file = 'Ap4Aase_new_3.pdb'
		self.pdb_path = '../../'
		self.pdb_full = self.pdb_path + self.pdb_file


	def init_mfin_param(self):
		"mfin file parameters"

		self.diff = 'isotropic'
		#self.diff = 'axial'
		self.num_sim = '200'
		self.trim = '0'               # Trim unconverged simulations.

		# tm
		self.tm = {}
		self.tm['val']   = 10
		self.tm['flag']  = '1'
		self.tm['bound'] = '2'
		self.tm['lower'] = '9.0'
		self.tm['upper'] = '13.0'
		self.tm['steps'] = '100'

		# dratio
		self.dratio = {}
		self.dratio['val']   = 1.123
		self.dratio['flag']  = '1'
		self.dratio['bound'] = '0'
		self.dratio['lower'] = '0.6'
		self.dratio['upper'] = '1.5'
		self.dratio['steps'] = '5'

		# theta
		self.theta = {}
		self.theta['val']   = 87.493
		self.theta['flag']  = '1'
		self.theta['bound'] = '0'
		self.theta['lower'] = '-90'
		self.theta['upper'] = '90'
		self.theta['steps'] = '10'

		# phi
		self.phi = {}
		self.phi['val']   = -52.470
		self.phi['flag']  = '1'
		self.phi['bound'] = '0'
		self.phi['lower'] = '-90'
		self.phi['upper'] = '90'
		self.phi['steps'] = '10'


	def init_mfpar_param(self):
		"mfpar file parameters"

		self.const = {}
		self.const['nucleus'] = 'N15'
		self.const['gamma']   = -2.710
		self.const['rxh']     = 1.020
		self.const['csa']     = -160.00

		self.vector = {}
		self.vector['atom1'] = 'N'
		self.vector['atom2'] = 'H'


	def init_mfmodel_param(self):
		"mfmodel file parameters"

		self.md1 = {}
		self.md1['tloc'] = {}
		self.md1['tloc']['start'] = '0.0'
		self.md1['tloc']['flag']  = '0'
		self.md1['tloc']['bound'] = '2'
		self.md1['tloc']['lower'] = '0.000'
		self.md1['tloc']['upper'] = '20.000'
		self.md1['tloc']['steps'] = '20'

		self.md1['theta'] = {}
		self.md1['theta']['start'] = '0.0'
		self.md1['theta']['flag']  = '0'
		self.md1['theta']['bound'] = '2'
		self.md1['theta']['lower'] = '0.000'
		self.md1['theta']['upper'] = '90.000'
		self.md1['theta']['steps'] = '20'

		self.md1['sf2'] = {}
		self.md1['sf2']['start'] = '1.0'
		self.md1['sf2']['flag']  = '0'
		self.md1['sf2']['bound'] = '2'
		self.md1['sf2']['lower'] = '0.000'
		self.md1['sf2']['upper'] = '1.000'
		self.md1['sf2']['steps'] = '20'

		self.md1['ss2'] = {}
		self.md1['ss2']['start'] = '1.0'
		self.md1['ss2']['flag']  = '0'
		self.md1['ss2']['bound'] = '2'
		self.md1['ss2']['lower'] = '0.000'
		self.md1['ss2']['upper'] = '1.000'
		self.md1['ss2']['steps'] = '20'

		self.md1['te'] = {}
		self.md1['te']['start'] = '0.0'
		self.md1['te']['flag']  = '0'
		self.md1['te']['bound'] = '2'
		self.md1['te']['lower'] = '0.000'
		self.md1['te']['upper'] = '10000.000'
		self.md1['te']['steps'] = '20'

		self.md1['rex'] = {}
		self.md1['rex']['start'] = '0.0'
		self.md1['rex']['flag']  = '0'
		self.md1['rex']['bound'] = '-1'
		self.md1['rex']['lower'] = '0.000'
		self.md1['rex']['upper'] = '20.000'
		self.md1['rex']['steps'] = '20'

		self.md2 = {}
		for param in self.md1.keys():
			self.md2[param] = {}
			for value in self.md1[param].keys():
				self.md2[param][value] = self.md1[param][value]
