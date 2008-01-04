###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
from math import pi
from re import search

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxStyleError, RelaxUnknownDataTypeError



class Molmol:
    """Class containing the Molmol specific functions for model-free analysis."""

    def classic(self, data_type, colour_start, colour_end, colour_list):
        """
        Classic style
        ~~~~~~~~~~~~~

        Creator:  Edward d'Auvergne

        Argument string:  "classic"

        Description:  The classic style draws the backbone of the protein in the Molmol 'neon'
        style.  Rather than colouring the amino acids to which the NH bond belongs, the three
        covalent bonds of the peptide bond from Ca to Ca in which the NH bond is located are
        coloured.  Deselected residues are shown as black lines.

        Supported data types:
        ____________________________________________________________________________________________
        |                |             |                                                           |
        | Data type      | String      | Description                                               |
        |________________|_____________|___________________________________________________________|
        |                |             |                                                           |
        | S2.            | 'S2'        | The standard model-free order parameter, equal to S2f.S2s |
        |                |             | for the two timescale models.  The default colour         |
        |                |             | gradient starts at 'yellow' and ends at 'red'.            |
        |                |             |                                                           |
        | S2f.           | 'S2f'       | The order parameter of the faster of two internal         |
        |                |             | motions.  Residues which are described by model-free      |
        |                |             | models m1 to m4, the single timescale models, are         |
        |                |             | illustrated as white neon bonds.  The default colour      |
        |                |             | gradient is the same as that for the S2 data type.        |
        |                |             |                                                           |
        | S2s.           | 'S2s'       | The order parameter of the slower of two internal         |
        |                |             | motions.  This functions exactly as S2f except that S2s   |
        |                |             | is plotted instead.                                       |
        |                |             |                                                           |
        | Amplitude of   | 'amp_fast'  | Model independent display of the amplite of fast motions. |
        | fast motions.  |             | For residues described by model-free models m5 to m8, the |
        |                |             | value plotted is that of S2f.  However, for residues      |
        |                |             | described by models m1 to m4, what is shown is dependent  |
        |                |             | on the timescale of the motions.  This is because these   |
        |                |             | single timescale models can, at times, be perfect         |
        |                |             | approximations to the more complex two timescale models.  |
        |                |             | Hence if te is less than 200 ps, S2 is plotted. Otherwise |
        |                |             | the peptide bond is coloured white.  The default colour   |
        |                |             | gradient  is the same as that for S2.                     |
        |                |             |                                                           |
        | Amplitude of   | 'amp_slow'  | Model independent display of the amplite of slow motions, |
        | slow motions.  |             | arbitrarily defined as motions slower than 200 ps.  For   |
        |                |             | residues described by model-free models m5 to m8, the     |
        |                |             | order parameter S2 is plotted if ts > 200 ps.  For models |
        |                |             | m1 to m4, S2 is plotted if te > 200 ps.  The default      |
        |                |             | colour gradient is the same as that for S2.               |
        |                |             |                                                           |
        | te.            | 'te'        | The correlation time, te.  The default colour gradient    |
        |                |             | starts at 'turquoise' and ends at 'blue'.                 |
        |                |             |                                                           |
        | tf.            | 'tf'        | The correlation time, tf.  The default colour gradient is |
        |                |             | the same as that of te.                                   |
        |                |             |                                                           |
        | ts.            | 'ts'        | The correlation time, ts.  The default colour gradient    |
        |                |             | starts at 'blue' and ends at 'black'.                     |
        |                |             |                                                           |
        | Timescale of   | 'time_fast' | Model independent display of the timescale of fast        |
        | fast motions   |             | motions.  For models m5 to m8, only the parameter tf is   |
        |                |             | plotted.  For models m2 and m4, the parameter te is       |
        |                |             | plotted only if it is less than 200 ps.  All other        |
        |                |             | residues are assumed to have a correlation time of zero.  |
        |                |             | The default colour gradient is the same as that of te.    |
        |                |             |                                                           |
        | Timescale of   | 'time_slow' | Model independent display of the timescale of slow        |
        | slow motions   |             | motions.  For models m5 to m8, only the parameter ts is   |
        |                |             | plotted.  For models m2 and m4, the parameter te is       |
        |                |             | plotted only if it is greater than 200 ps.  All other     |
        |                |             | residues are coloured white.  The default colour gradient |
        |                |             | is the same as that of ts.                                |
        |                |             |                                                           |
        | Chemical       | 'Rex'       | The chemical exchange, Rex.  Residues which experience no |
        | exchange       |             | chemical exchange are coloured white.  The default colour |
        |                |             | gradient starts at 'yellow' and finishes at 'red'.        |
        |________________|_____________|___________________________________________________________|
        """
        __docformat__ = "plaintext"


        # Generate the macro header.
        ############################

        self.classic_header()


        # S2.
        #####

        if data_type == 'S2':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Skip residues which don't have an S2 value.
                if not hasattr(residue, 's2') or residue.s2 == None:
                    continue

                # S2 width and colour.
                self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)


        # S2f.
        ######

        elif data_type == 'S2f':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Colour residues which don't have an S2f value white.
                if not hasattr(residue, 's2f') or residue.s2f == None:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])

                # S2f width and colour.
                else:
                    self.classic_order_param(residue, residue.s2f, colour_start, colour_end, colour_list)


        # S2s.
        ######

        elif data_type == 'S2s':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Colour residues which don't have an S2s value white.
                if not hasattr(residue, 's2s') or residue.s2s == None:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])

                # S2s width and colour.
                else:
                    self.classic_order_param(residue, residue.s2s, colour_start, colour_end, colour_list)


        # Amplitude of fast motions.
        ############################

        elif data_type == 'amp_fast':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # The model.
                if search('tm[0-9]', residue.model):
                    model = residue.model[1:]
                else:
                    model = residue.model

                # S2f width and colour (for models m5 to m8).
                if hasattr(residue, 's2f') and residue.s2f != None:
                    self.classic_order_param(residue, residue.s2f, colour_start, colour_end, colour_list)

                # S2 width and colour (for models m1 and m3).
                elif model == 'm1' or model == 'm3':
                    self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)

                # S2 width and colour (for models m2 and m4 when te <= 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te <= 200e-12:
                    self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)

                # White bonds (for models m2 and m4 when te > 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te > 200e-12:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])

                # Catch errors.
                else:
                    raise RelaxFault


        # Amplitude of slow motions.
        ############################

        elif data_type == 'amp_slow':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # The model.
                if search('tm[0-9]', residue.model):
                    model = residue.model[1:]
                else:
                    model = residue.model

                # S2 width and colour (for models m5 to m8).
                if hasattr(residue, 'ts') and residue.ts != None:
                    self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)

                # S2 width and colour (for models m2 and m4 when te > 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te > 200 * 1e-12:
                    self.classic_order_param(residue, residue.s2, colour_start, colour_end, colour_list)

                # White bonds for fast motions.
                else:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])

        # te.
        #####

        elif data_type == 'te':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Skip residues which don't have a te value.
                if not hasattr(residue, 'te') or residue.te == None:
                    continue

                # te width and colour.
                self.classic_correlation_time(residue, residue.te, colour_start, colour_end, colour_list)


        # tf.
        #####

        elif data_type == 'tf':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Skip residues which don't have a tf value.
                if not hasattr(residue, 'tf') or residue.tf == None:
                    continue

                # tf width and colour.
                self.classic_correlation_time(residue, residue.tf, colour_start, colour_end, colour_list)


        # ts.
        #####

        elif data_type == 'ts':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Skip residues which don't have a ts value.
                if not hasattr(residue, 'ts') or residue.ts == None:
                    continue

                # The default start and end colours.
                if colour_start == None:
                    colour_start = 'blue'
                if colour_end == None:
                    colour_end = 'black'

                # ts width and colour.
                self.classic_correlation_time(residue, residue.ts / 10.0, colour_start, colour_end, colour_list)


        # Timescale of fast motions.
        ############################

        elif data_type == 'time_fast':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # The model.
                if search('tm[0-9]', residue.model):
                    model = residue.model[1:]
                else:
                    model = residue.model

                # tf width and colour (for models m5 to m8).
                if hasattr(residue, 'tf') and residue.tf != None:
                    self.classic_correlation_time(residue, residue.tf, colour_start, colour_end, colour_list)

                # te width and colour (for models m2 and m4 when te <= 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te <= 200e-12:
                    self.classic_correlation_time(residue, residue.te, colour_start, colour_end, colour_list)

                # All other residues are assumed to have a fast correlation time of zero (statistically zero, not real zero!).
                # Colour these bonds white.
                else:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])


        # Timescale of slow motions.
        ############################

        elif data_type == 'time_slow':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # The model.
                if search('tm[0-9]', residue.model):
                    model = residue.model[1:]
                else:
                    model = residue.model

                # The default start and end colours.
                if colour_start == None:
                    colour_start = 'blue'
                if colour_end == None:
                    colour_end = 'black'

                # ts width and colour (for models m5 to m8).
                if hasattr(residue, 'ts') and residue.ts != None:
                    self.classic_correlation_time(residue, residue.ts / 10.0, colour_start, colour_end, colour_list)

                # te width and colour (for models m2 and m4 when te > 200 ps).
                elif (model == 'm2' or model == 'm4') and residue.te > 200e-12:
                    self.classic_correlation_time(residue, residue.te / 10.0, colour_start, colour_end, colour_list)

                # White bonds for the rest.
                else:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])


        # Rex.
        ######

        elif data_type == 'Rex':
            # Loop over the sequence.
            for residue in relax_data_store.res[self.run]:
                # Skip unselected residues.
                if not residue.select:
                    continue

                # Residues which chemical exchange.
                if hasattr(residue, 'rex') and residue.rex != None:
                    self.classic_rex(residue, residue.rex, colour_start, colour_end, colour_list)

                # White bonds for the rest.
                else:
                    self.classic_colour(res_num=residue.num, width=0.3, rgb_array=[1, 1, 1])


        # Unknown data type.
        ####################

        else:
            raise RelaxUnknownDataTypeError, data_type


    def classic_colour(self, res_num=None, width=None, rgb_array=None):
        """Colour the given peptide bond."""

        # Ca to C bond.
        self.commands.append("SelectBond 'atom1.name = \"CA\"  & atom2.name = \"C\" & res.num = " + `res_num-1` + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + `width`)
        self.commands.append("ColorBond " + `rgb_array[0]` + " " + `rgb_array[1]` + " " + `rgb_array[2]`)

        # C to N bond.
        self.commands.append("SelectBond 'atom1.name = \"C\"  & atom2.name = \"N\" & res.num = " + `res_num-1` + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + `width`)
        self.commands.append("ColorBond " + `rgb_array[0]` + " " + `rgb_array[1]` + " " + `rgb_array[2]`)

        # N to Ca bond.
        self.commands.append("SelectBond 'atom1.name = \"N\"  & atom2.name = \"CA\" & res.num = " + `res_num` + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + `width`)
        self.commands.append("ColorBond " + `rgb_array[0]` + " " + `rgb_array[1]` + " " + `rgb_array[2]`)

        # Blank line.
        self.commands.append("")


    def classic_correlation_time(self, residue, te, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for correlation times."""

        # The te value in picoseconds.
        te = te * 1e12

        # The bond width (aiming for a width range of 2 to 0 for te values of 0 to 10 ns).
        width = 2.0 - 200.0 / (te + 100.0)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (hyperbolic).
        colour_value = 1.0 / (te / 100.0 + 1.0)

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'turquoise'
        if colour_end == None:
            colour_end = 'blue'

        # Get the RGB colour array (swap the colours because of the inverted hyperbolic colour value).
        rgb_array = self.relax.colour.linear_gradient(colour_value, colour_end, colour_start, colour_list)

        # Colour the peptide bond.
        self.classic_colour(residue.num, width, rgb_array)


    def classic_header(self):
        """Create the header for the molmol macro."""

        # Hide all bonds.
        self.commands.append("SelectBond ''")
        self.commands.append("StyleBond invisible")

        # Show the backbone bonds as lines.
        self.commands.append("SelectBond 'bb'")
        self.commands.append("StyleBond line")

        # Colour the backbone black.
        self.commands.append("ColorBond 0 0 0")


    def classic_order_param(self, residue, s2, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for order parameters."""

        # The bond width (aiming for a width range of 2 to 0 for S2 values of 0.0 to 1.0).
        if s2 <= 0.0:
            width = 2.0
        else:
            width = 2.0 * (1.0 - s2**2)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (quartic).
        colour_value = s2 ** 4

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'red'
        if colour_end == None:
            colour_end = 'yellow'

        # Get the RGB colour array.
        rgb_array = self.relax.colour.linear_gradient(colour_value, colour_start, colour_end, colour_list)

        # Colour the peptide bond.
        self.classic_colour(residue.num, width, rgb_array)


    def classic_rex(self, residue, rex, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for correlation times."""

        # The Rex value at the first field strength.
        rex = rex * (2.0 * pi * relax_data_store.frq[self.run][0])**2

        # The bond width (aiming for a width range of 2 to 0 for Rex values of 0 to 25 s^-1).
        width = 2.0 - 2.0 / (rex/5.0 + 1.0)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (hyperbolic).
        colour_value = 1.0 / (rex + 1.0)

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'yellow'
        if colour_end == None:
            colour_end = 'red'

        # Get the RGB colour array (swap the colours because of the inverted hyperbolic colour value).
        rgb_array = self.relax.colour.linear_gradient(colour_value, colour_end, colour_start, colour_list)

        # Colour the peptide bond.
        self.classic_colour(residue.num, width, rgb_array)


    def macro(self, run, data_type, style, colour_start, colour_end, colour_list):
        """Create and return an array of Molmol macros of the model-free parameters."""

        # Arguments.
        self.run = run

        # Initialise.
        self.commands = []

        # The classic style.
        if style == 'classic':
            self.classic(data_type, colour_start, colour_end, colour_list)

        # Unknown style.
        else:
            raise RelaxStyleError, style

        # Return the command array.
        return self.commands
