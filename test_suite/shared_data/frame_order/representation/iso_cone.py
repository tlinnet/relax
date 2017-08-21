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


# Create the data pipe.
pipe.create(pipe_name='frame order', pipe_type='frame order')

# Select the model.
frame_order.select_model('iso cone')

# The eigenframe.
axis_theta = 0.0
axis_phi = 0.0

# Set the average domain position translation parameters.
value.set(param='ave_pos_x', val=0.0)
value.set(param='ave_pos_y', val=0.0)
value.set(param='ave_pos_z', val=0.0)
value.set(param='ave_pos_alpha', val=0.0)
value.set(param='ave_pos_beta', val=0.0)
value.set(param='ave_pos_gamma', val=0.0)
value.set(param='axis_theta', val=axis_theta)
value.set(param='axis_phi', val=axis_phi)
value.set(param='cone_theta', val=2.0)
value.set(param='cone_sigma_max', val=0.0)

# Set the pivot.
frame_order.pivot(pivot=[1, 1, 1], fix=True)

# Create the PDB.
frame_order.pdb_model(inc=10, size=45, rep='iso_cone', force=True)
