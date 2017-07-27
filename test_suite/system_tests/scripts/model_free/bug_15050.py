# Module docstring.
"""This system test catches bug #15050 (https://gna.org/bugs/?15050) submitted by Tiago Pais."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

# Loop over the models.
for name in ['tm4']:
    # Setup.
    pipe.create(pipe_name=name, pipe_type='mf')
    sequence.read(file='noe.500.out', dir=path, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=None, sep=None)
    relax_data.read(ri_id='R1',  ri_type='R1',  frq=500208000.0, file='r1.500.out', dir=path, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=None, data_col=3, error_col=4, sep=None)
    relax_data.read(ri_id='R2',  ri_type='R2',  frq=500208000.0, file='r2.500.out', dir=path, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=None, data_col=3, error_col=4, sep=None)
    relax_data.read(ri_id='NOE', ri_type='NOE', frq=500208000.0, file='noe.500.out', dir=path, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=None, data_col=3, error_col=4, sep=None)
    spin.name('N')
    spin.element('N')
    sequence.attach_protons()
    interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
    interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)
    value.set(val=-0.00017199999999999998, param='csa', spin_id=None)
    spin.isotope('15N', spin_id='@N')
    spin.isotope('1H', spin_id='@H')
    model_free.select_model(model=name, spin_id=None)

    # Optimisation.
    minimise.grid_search(lower=None, upper=None, inc=11, constraints=True, verbosity=1)
    minimise.execute('newton', func_tol=1e-25, max_iter=10000000, constraints=True, scaling=True, verbosity=1)
