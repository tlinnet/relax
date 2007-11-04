###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
import sys
from string import replace

# relax module imports.
import help
from generic_fns import residue
from generic_fns.selection import id_string_doc
from relax_errors import RelaxBinError, RelaxIntError, RelaxNoneStrError, RelaxStrError


class Residue:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the residue data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, pipe_from=None, res_from=None, pipe_to=None, res_to=None):
        """Function for copying all data associated with a residue.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The data pipe containing the residue from which the data will be copied.  This
            defaults to the current data pipe.

        res_from:  The residue identifier string of the residue to copy the data from.

        pipe_to:  The data pipe to copy the data to.  This defaults to the current data pipe.

        res_to:  The residue identifier string of the residue to copy the data to.


        Description
        ~~~~~~~~~~~

        This function will copy all the data associated with the identified residue to the new,
        non-existent residue.  The new residue must not already exist.


        Examples
        ~~~~~~~~

        To copy the residue data from residue 1 to the new residue 2, type:

        relax> residue.copy(res_from=':1', res_to=':2')


        To copy residue 1 of the molecule 'Old mol' to residue 5 of the molecule 'New mol', type:

        relax> residue.copy(res_from='#Old mol:1', res_to='#New mol:5')


        To copy the residue data of residue 1 from the data pipe 'm1' to 'm2', assuming the current
        data pipe is 'm1', type:

        relax> residue.copy(res_from=':1', pipe_to='m2')
        relax> residue.copy(pipe_from='m1', res_from=':1', pipe_to='m2', res_to=':1')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.copy("
            text = text + "pipe_from=" + `pipe_from`
            text = text + "res_from=" + `res_from`
            text = text + "pipe_to=" + `pipe_to`
            text = text + ", res_to=" + `res_to` + ")"
            print text

        # The pipe_from argument.
        if type(pipe_from) != str:
            raise RelaxStrError, ('pipe_from', pipe_from)

        # The res_from argument.
        if type(res_from) != str:
            raise RelaxStrError, ('res_from', res_from)

        # The pipe_to argument.
        if type(pipe_to) != str:
            raise RelaxStrError, ('pipe_to', pipe_to)

        # The res_to argument.
        if type(res_to) != str:
            raise RelaxStrError, ('res_to', res_to)

        # Execute the functional code.
        residue.copy(pipe_from=pipe_from, res_from=res_from, pipe_to=pipe_to, res_to=res_to)


    def create(self, res_num=None, res_name=None):
        """Function for creating a new residue.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_num:  The residue number.

        res_name:  The name of the residue.


        Description
        ~~~~~~~~~~~

        Using this function a new sequence can be generated without using the sequence user
        functions.  However if the sequence already exists, the new residue will be added to the end
        of the residue list (the residue numbers of this list need not be sequential).  The same
        residue number cannot be used more than once.  A corresponding single spin system will be
        created for this residue.  The spin system number and name or additional spin systems can be
        added later if desired.


        Examples
        ~~~~~~~~

        The following sequence of commands will generate the sequence 1 ALA, 2 GLY, 3 LYS:

        relax> residue.create(1, 'ALA')
        relax> residue.create(2, 'GLY')
        relax> residue.create(3, 'LYS')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.create("
            text = text + ", res_num=" + `res_num`
            text = text + ", res_name=" + `res_name` + ")"
            print text

        # Residue number.
        if type(res_num) != int:
            raise RelaxIntError, ('residue number', res_num)

        # Residue name.
        if type(res_name) != str:
            raise RelaxStrError, ('residue name', res_name)

        # Execute the functional code.
        residue.create(res_num=res_num, res_name=res_name)


    def delete(self, res_id=None):
        """Function for deleting residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identifier string.


        Description
        ~~~~~~~~~~~

        This function can be used to delete a single or sets of residues.  See the identification
        string documentation below for more information.  If spin system/atom ids are included a
        RelaxError will be raised.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.delete("
            text = text + "res_id=" + `res_id` + ")"
            print text

        # The residue identifier argument.
        if type(res_id) != str:
            raise RelaxStrError, ('residue identifier', res_id)

        # Execute the functional code.
        residue.delete(res_id=res_id)


    def display(self, run=None):
        """Function for displaying the sequence.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.display("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.sequence.display(run=run)


    def rename(self, res_id=None, new_name=None):
        """Function for renaming an existent residue(s).

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identification string corresponding to one or more residues.

        new_name:  The new name.


        Description
        ~~~~~~~~~~~

        This function simply allows residues to be renamed.


        Examples
        ~~~~~~~~

        The following sequence of commands will rename the sequence {1 ALA, 2 GLY, 3 LYS} to {1 XXX,
        2 XXX, 3 XXX}:

        relax> residue.rename(':1', 'XXX')
        relax> residue.rename(':2', 'XXX')
        relax> residue.rename(':3', 'XXX')

        Alternatively:

        relax> residue.rename(':1,2,3', 'XXX')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.rename("
            text = text + ", res_id=" + `res_id`
            text = text + ", new_name=" + `new_name` + ")"
            print text

        # Residue identification string.
        if type(res_id) != int:
            raise RelaxIntError, ('residue identification string', res_id)

        # New residue name.
        if type(new_name) != str:
            raise RelaxStrError, ('new residue name', new_name)

        # Execute the functional code.
        residue.create(res_num=res_num, new_name=new_name)



    # Docstring modification.
    #########################

    # Add the residue identification string description.
    copy.__doc__ = copy.__doc__ + "\n\n" + id_string_doc + "\n"
    delete.__doc__ = delete.__doc__ + "\n\n" + id_string_doc + "\n"
    rename.__doc__ = rename.__doc__ + "\n\n" + id_string_doc + "\n"
