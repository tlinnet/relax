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

import sys

class Rx_data:
    def __init__(self, relax):
        """Class containing functions for relaxation data."""

        self.relax = relax


    def data_init(self, name):
        """Function for returning an initial data structure corresponding to 'name'."""

        # Empty arrays.
        list_data = [ 'relax_data',
                      'relax_error',
                      'ri_labels',
                      'remap_table',
                      'noe_r1_table',
                      'frq_labels',
                      'frq' ]
        if name in list_data:
            return []

        # Zero.
        zero_data = [ 'num_ri', 'num_frq' ]
        if name in zero_data:
            return 0


    def data_names(self):
        """Function for returning a list of names of data structures associated with relax_data.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        relax_data:  Relaxation data.

        relax_error:  Relaxation error.

        num_ri:  Number of data points, eg 6.

        num_frq:  Number of field strengths, eg 2.

        ri_labels:  Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1',
        'R2'].

        remap_table:  A translation table to map relaxation data points to their frequencies, eg [0,
        0, 0, 1, 1, 1].

        noe_r1_table:  A translation table to direct the NOE data points to the R1 data points.
        This is used to speed up calculations by avoiding the recalculation of R1 values.  eg [None,
        None, 0, None, None, 3]

        frq_labels:  NMR frequency labels, eg ['600', '500']

        frq:  NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]
        """

        names = [ 'relax_data',
                  'relax_error',
                  'num_ri',
                  'num_frq',
                  'ri_labels',
                  'remap_table',
                  'noe_r1_table',
                  'frq_labels',
                  'frq' ]

        return names


    def initialise_relax_data(self, data, run):
        """Function for initialisation of relaxation data structures.

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


    def macro_read(self, run=None, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=1):
        """Macro for reading R1, R2, or NOE relaxation data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength in MHz, ie '600'.  This string can be anything as long as
        data collected at the same field strength have the same label.

        frq:  The spectrometer frequency in Hz.

        file_name:  The name of the file containing the relaxation data.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        data_col:  The relaxation data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).

        header_lines:  The number of lines at the top of the file to skip (the default is 1 line).


        Examples
        ~~~~~~~~

        The following commands will read the NOE relaxation data collected at 600 MHz out of a file
        called 'noe.600.out' where the residue numbers, residue names, data, errors are in the
        first, second, third, and forth columns respectively.

        relax> read.relax_data('m1', 'NOE', '600', 599.7 * 1e6, 'noe.600.out')
        relax> read.relax_data('m1', ri_label='NOE', frq_label='600', frq=600.0 * 1e6,
                               file_name='noe.600.out')


        The following commands will read the R2 data out of the file 'r2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
        respectively.  The columns are separated by commas.

        relax> read.relax_data('m1', 'R2', '800 MHz', 8.0 * 1e8, 'r2.out', 1, 2, 4, 5, ',')
        relax> read.relax_data('m1', ri_label='R2', frq_label='800 MHz', frq=8.0*1e8,
                               file_name='r2.out', num_col=1, name_col=2, data_col=4, error_col=5,
                               sep=',', header_lines=1)


        The following commands will read the R1 data out of the file 'r1.out' where the columns are
        separated by the symbol '%'

        relax> read.relax_data('m1', 'R1', '300', 300.1 * 1e6, 'r1.out', sep='%')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "read.relax_data("
            text = text + "run=" + `run`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label`
            text = text + ", frq=" + `frq`
            text = text + ", file_name=" + `file_name`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep`
            text = text + ", header_lines=" + `header_lines` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if not ri_label or type(ri_label) != str:
            raise RelaxStrError, ('relaxation label', ri_label)

        # Frequency label.
        elif type(frq_label) != str:
            raise RelaxStrError, ('frequency label', frq_label)

        # Frequency.
        elif type(frq) != float:
            raise RelaxFloatError, ('frequency', frq)

        # The file name.
        elif not file_name:
            raise RelaxNoneError, 'file name'
        elif type(file_name) != str:
            raise RelaxStrError, ('file name', file_name)

        # The number column.
        elif type(num_col) != int:
            raise RelaxIntError, ('residue number column', num_col)

        # The name column.
        elif type(name_col) != int:
            raise RelaxIntError, ('residue name column', name_col)

        # The data column.
        elif type(data_col) != int:
            raise RelaxIntError, ('data column', data_col)

        # The error column.
        elif type(error_col) != int:
            raise RelaxIntError, ('error column', error_col)

        # Column separator.
        elif sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Header lines.
        elif type(header_lines) != int:
            raise RelaxIntError, ('number of header lines', header_lines)

        # Execute the functional code.
        self.read(run=run, ri_label=ri_label, frq_label=frq_label, frq=frq, file_name=file_name, num_col=num_col, name_col=name_col, data_col=data_col, error_col=error_col, sep=sep, header_lines=header_lines)


    def read(self, run=None, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=None):
        """Function for reading R1, R2, or NOE relaxation data."""

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file_name)

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip the data.
        file_data = self.relax.file_ops.strip(file_data)

        # Test the validity of the relaxation data.
        for i in range(len(file_data)):
            try:
                int(file_data[i][num_col])
                float(file_data[i][data_col])
                float(file_data[i][error_col])
            except ValueError:
                raise RelaxError, "The relaxation data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data=" + file_data[i][data_col] + ", error=" + file_data[i][error_col] + ")."

        # Loop over the relaxation data.
        for i in range(len(file_data)):
            # Get the data.
            res_num = int(file_data[i][num_col])
            res_name = file_data[i][name_col]
            value = float(file_data[i][data_col])
            error = float(file_data[i][error_col])

            # Find the index of self.relax.data.res which corresponds to the relaxation data set i.
            index = None
            for j in range(len(self.relax.data.res)):
                if self.relax.data.res[j].num == res_num and self.relax.data.res[j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxNoResError, (res_num, res_name)

            # Initialise the relaxation data structures (if needed).
            self.initialise_relax_data(self.relax.data.res[index], run)

            # Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists, and if so, do not load or update the data.
            for j in range(self.relax.data.res[index].num_ri[run]):
               if ri_label == self.relax.data.res[index].ri_labels[run][j] and frq_label == self.relax.data.res[index].frq_labels[run][self.relax.data.res[index].remap_table[run][j]]:
                    raise RelaxError, "The relaxation data corresponding to " + `ri_label` + " and " + `frq_label` + " has already been read."

            # Relaxation data and errors.
            self.relax.data.res[index].relax_data[run].append(value)
            self.relax.data.res[index].relax_error[run].append(error)

            # Update the number of relaxation data points.
            self.relax.data.res[index].num_ri[run] = self.relax.data.res[index].num_ri[run] + 1

            # Add ri_label to the data types.
            self.relax.data.res[index].ri_labels[run].append(ri_label)

            # Find if the frequency self.frq has already been loaded.
            remap = len(self.relax.data.res[index].frq[run])
            flag = 0
            for i in range(len(self.relax.data.res[index].frq[run])):
                if frq == self.relax.data.res[index].frq[run][i]:
                    remap = i
                    flag = 1

            # Update the data structures which have a length equal to the number of field strengths.
            if not flag:
                self.relax.data.res[index].num_frq[run] = self.relax.data.res[index].num_frq[run] + 1
                self.relax.data.res[index].frq_labels[run].append(frq_label)
                self.relax.data.res[index].frq[run].append(frq)

            # Update the remap table.
            self.relax.data.res[index].remap_table[run].append(remap)

            # Update the NOE R1 translation table.
            self.relax.data.res[index].noe_r1_table[run].append(None)
            if ri_label == 'NOE':
                # If the data corresponds to 'NOE', try to find if the corresponding 'R1' data has been read.
                for i in range(self.relax.data.res[index].num_ri[run]):
                    if self.relax.data.res[index].ri_labels[run][i] == 'R1' and frq_label == self.relax.data.res[index].frq_labels[run][self.relax.data.res[index].remap_table[run][i]]:
                        self.relax.data.res[index].noe_r1_table[run][self.relax.data.res[index].num_ri[run] - 1] = i
            if ri_label == 'R1':
                # If the data corresponds to 'R1', try to find if the corresponding 'NOE' data has been read.
                for i in range(self.relax.data.res[index].num_ri[run]):
                    if self.relax.data.res[index].ri_labels[run][i] == 'NOE' and frq_label == self.relax.data.res[index].frq_labels[run][self.relax.data.res[index].remap_table[run][i]]:
                        self.relax.data.res[index].noe_r1_table[run][i] = self.relax.data.res[index].num_ri[run] - 1

        # Add the run to the runs list.
        if not run in self.relax.data.runs:
            self.relax.data.runs.append(run)


    def curvefit_input(self):
        # Loop through each time point.
        for spectra in range(len(self.usr_param.input_info)):
            print '\nProcessing data for time point ' + self.xmf.r1_data.input[i][0] + ' sec'
            for j in range(len(self.xmf.r1_data.input[i])):     # Go through the three columns of the input file.
                if j == 0:           # The time column.
                    self.xmf.r1_data.times.append(self.xmf.r1_data.input[i][0])     # Add the time to the 'times' array.
                    self.xmf.r1_data.input_data[i][0] = self.xmf.r1_data.input[i][0]
                    continue     # Go to the next column.
                file = self.xmf.r1_data.input[i][j]
                self.xmf.r1_data.input_data[i][j] = self.xmf.file_ops.extract_data(file)
                equal_size(len(self.xmf.r1_data.input_data[0][1]),len(self.xmf.r1_data.input_data[i][j]))     # Test if both are the same length.
                if j == 2:           # The duplicate spectra column.
                    diff_list = []     # List of peak intensity differences for backbone peaks.
                bb_no = 0            # Number of backbone peaks.
                indole_no = 0        # Number of tryptophane indole peaks.
                for k in range(len(self.xmf.r1_data.input_data[i][j])):     # Go through the lines of each spectra.
                    if non_residue(self.xmf.r1_data.input_data[i][j][k]):
                        continue     # Skip all non-residue lines.
                    test_res_no(self.xmf.r1_data.input_data[0][1][k][0],self.xmf.r1_data.input_data[i][j][k][0])     # Test if residue numbers match.
                    if backbone(self.xmf.r1_data.input_data[i][j][k][4]):     # Backbone peak.
                        if unresolved_peak(self.xmf.r1_data.input_data[i][j][k][5],'test/R1/unresolved'):
                            continue     # Skip unresolved peaks.
                        self.xmf.r1_data.bb_intense = create_2Dint(i, j, k, self.xmf.r1_data.input_data, self.xmf.r1_data.bb_intense, bb_no)
                        if j == 2:     # Duplicate spectra data set.
                            diff_val = float(self.xmf.r1_data.input_data[i][1][k][10]) - float(self.xmf.r1_data.input_data[i][2][k][10])
                            diff_list.append(diff_val)
                        bb_no = bb_no + 1
                    elif indole(self.xmf.r1_data.input_data[i][j][k][4]):     # Tryptophane indole peak.
                        if unresolved_peak(self.xmf.r1_data.input_data[i][j][k][5],'R1/indole_unresolved'):
                            continue     # Skip unresolved peaks.
                        self.xmf.r1_data.indole_intense = create_2Dint(i, j, k, self.xmf.r1_data.input_data, self.xmf.r1_data.indole_intense, indole_no)
                        indole_no = indole_no + 1
                if j == 2:
                    self.xmf.r1_data.diff.append(diff_list)
        self.xmf.r1_data.bb_intense.sort()
        self.xmf.r1_data.indole_intense.sort()
        sumSd = 0     # The sum of all the standard deviations.
        for set in range(len(self.xmf.r1_data.diff)):
            sd = stand_dev(self.xmf.r1_data.diff[set])
            print '\nThe standard deviation is: ' + `sd`
            sumSd = sumSd + sd
        aveSd = sumSd / len(self.xmf.r1_data.diff)
        print '\nThe average standard deviation is: ' + `aveSd`

        print '\nCreating grace files\n'
        self.xmf.grace.intensity('R1_backbone', self.xmf.r1_data.bb_intense, self.xmf.r1_data.times, aveSd)
        self.xmf.grace.intensity('R1_trp_indole', self.xmf.r1_data.indole_intense, self.xmf.r1_data.times, aveSd)
        rx_log('r1.log', self.xmf.r1_data.times, self.xmf.r1_data.bb_intense, self.xmf.r1_data.indole_intense, self.xmf.r1_data.diff, aveSd)


    def test_res_no(self, first_no, second_no):
        if first_no != second_no:
            text = 'Residues don\'t line up\n'
            print str(first_no) + ' != ' + str(second_no)
            while 1:
                pass
