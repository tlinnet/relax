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

import sys


class RW:
    def __init__(self, relax):
        """Class for writing data to a file."""

        self.relax = relax


    def read(self, run=None, file='results', dir=None, format='columnar'):
        """Function for reading results from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file to read results from.

        dir:  The directory where the file is located.


        Description
        ~~~~~~~~~~~

        The name of the run can be any string.

        If no directory name is given, the results file will be searched for in a directory named
        after the run name.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", format=" + `format` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Format.
        if type(format) != str:
            raise RelaxStrError, ('format', format)

        # Execute the functional code.
        self.relax.generic.rw.read_results(run=run, file=file, directory=dir, format=format)


    def write(self, run=None, file="results", dir=None, force=0, format='columnar'):
        """Function for writing results to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file to output results to.  The default is 'results'.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the results file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the results file will be placed in a directory named after
        the run name.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "write("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force`
            text = text + ", format=" + `format` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Format.
        if type(format) != str:
            raise RelaxStrError, ('format', format)

        # Execute the functional code.
        self.relax.generic.rw.write_results(run=run, file=file, directory=dir, force=force, format=format)
