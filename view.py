###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

import os


class View:
    def __init__(self, relax):
        """Class containing the functions for viewing molecules."""

        self.relax = relax


    def view(self):
        """Function for viewing the collection of molecules using VMD."""

        # Test if the PDB file has been loaded.
        if not hasattr(self.relax.data, 'molecs'):
            raise RelaxPdbError

        # Test if the environmental variable PDBVIEWER has been set.
        try:
            os.environ['PDBVIEWER']
        except KeyError:
            raise RelaxPdbviewerError

        # View the collection.
        self.relax.data.molecs.view()
