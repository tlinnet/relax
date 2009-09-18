###############################################################################
#                                                                             #
# Copyright (C) 2006-2009 Edward d'Auvergne                                   #
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
from os import remove
from tempfile import mktemp
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_io import delete


class Align_tensor(TestCase):
    """Class for testing various aspects specific to the alignment tensors."""

    def setUp(self):
        """Function for initialising a few alignment tensors."""

        # Create a data pipe.
        self.relax.interpreter._Pipe.create('test', 'frame order')

        # Temp file name.
        self.tmpfile = mktemp()

        # Tensor name lists.
        full_list = ['0 full', '1 full', '2 full', '3 full', '4 full']
        red_list = ['0 red', '1 red', '2 red', '3 red', '4 red']

        # Error.
        error = 1.47411211147e-05

        # Tensor lists.
        self.tensors_full = [
                (0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083),
                (-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637),
                (-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515),
                (0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05),
                (-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023)
        ]
        self.tensors_red = [
                (-0.0004037026160192775, 0.00023172423501111316, -0.00020915186581478394, -0.00028817367472760139, -8.7172337025481604e-05),
                (0.0003767999506688964, -0.00021492227011444111, 0.00019620694392616774, 0.00027163215478635274, 8.147201253457049e-05),
                (0.00025970120925482461, -0.00014782823602910519, 0.00013565269563569894, 0.00018741173517420359, 5.6252903270026344e-05),
                (0.00014574884684542708, -8.3162940224598374e-05, 7.4927100277784987e-05, 0.00010508245294401461, 3.1156238348722986e-05),
                (-0.00011267453337899962, 6.412308037476237e-05, -5.7897942333203444e-05, -8.1865863377039068e-05, -2.5273427585025123e-05)
        ]

        # Set up the tensors.
        for i in range(5):
            # Load the tensor.
            self.relax.interpreter._Align_tensor.init(tensor=full_list[i], params=self.tensors_full[i], param_types=0)
            self.relax.interpreter._Align_tensor.init(tensor=red_list[i], params=self.tensors_red[i], param_types=0)

            # Errors.
            self.relax.interpreter._Align_tensor.init(tensor=full_list[i], params=(error, error, error, error, error), param_types=0, errors=True)
            self.relax.interpreter._Align_tensor.init(tensor=red_list[i], params=(error, error, error, error, error), param_types=0, errors=True)

            # Domain.
            self.relax.interpreter._Align_tensor.set_domain(tensor=full_list[i], domain='full')
            self.relax.interpreter._Align_tensor.set_domain(tensor=red_list[i], domain='red')

            # Tensor reductions.
            self.relax.interpreter._Align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])

        # Reset some values.
        cdp.align_tensors[2].Axx = 1


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset the relax data storage object.
        ds.__reset__()

        # Delete the temporary files.
        delete(self.tmpfile, fail=False)


    def test_to_and_from_xml(self):
        """Test the conversion to and from XML."""

        # Save the data pipe.
        self.relax.interpreter._Results.write(self.tmpfile, dir=None)

        # Create a new data pipe.
        self.relax.interpreter._Pipe.create('new', 'frame order')

        # Load the data.
        self.relax.interpreter._Results.read(self.tmpfile, dir=None)

        # Checks.
        self.assertEqual(len(cdp.align_tensors), 5)
        for i in range(5):
            # Full tensors.
            self.assertEqual(cdp.align_tensors[i*2].Axx, self.tensors_full[i][0])
            self.assertEqual(cdp.align_tensors[i*2].Ayy, self.tensors_full[i][1])
            self.assertEqual(cdp.align_tensors[i*2].Axy, self.tensors_full[i][2])
            self.assertEqual(cdp.align_tensors[i*2].Axz, self.tensors_full[i][3])
            self.assertEqual(cdp.align_tensors[i*2].Ayz, self.tensors_full[i][4])

            # Reduced tensors.
            self.assertEqual(cdp.align_tensors[i*2+1].Axx, self.tensors_red[i][0])
            self.assertEqual(cdp.align_tensors[i*2+1].Ayy, self.tensors_red[i][1])
            self.assertEqual(cdp.align_tensors[i*2+1].Axy, self.tensors_red[i][2])
            self.assertEqual(cdp.align_tensors[i*2+1].Axz, self.tensors_red[i][3])
            self.assertEqual(cdp.align_tensors[i*2+1].Ayz, self.tensors_red[i][4])
