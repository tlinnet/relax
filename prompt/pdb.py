###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2006 Edward d'Auvergne                            #
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

import help


class PDB:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class containing the PDB related functions."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def create_tensor_pdb(self, run=None, scale=1.8e-6, file='tensor.pdb', dir=None, force=0):
        """Create a PDB file to represent the diffusion tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the structure to.

        scale:  Value for scaling the diffusion rates.

        file:  The name of the PDB file.

        dir:  The directory where the file is located.

        force:  A flag which, if set to 1, will overwrite the any pre-existing file.


        Description
        ~~~~~~~~~~~

        This function creates a PDB file containing an artificial geometric structure to represent
        the diffusion tensor.  A structure must have previously been read into relax.  The diffusion
        tensor is represented by an ellipsoidal, spheroidal, or spherical geometric object with its
        origin located at the centre of mass (of the selected residues).  This diffusion tensor PDB
        file can subsequently read into any molecular viewer.

        As the Brownian rotational diffusion tensor is a measure of the rate of rotation about
        different axes - the larger the geometric object, the faster the diffusion of a molecule.
        For example the diffusion tensor of a water molecule is much larger than that of a
        macromolecule.

        The effective global correlation time experienced by an XH bond vector, not to be confused
        with the Lipari and Szabo parameter tau_e, will be approximately proportional to the
        component of the diffusion tensor parallel to it.  The approximation is not exact due to the
        multiexponential form of the correlation function of Brownian rotational diffusion.  If an
        XH bond vector is parallel to the longest axis of the tensor, it will be unaffected by
        rotations about that axis, which are the fastest rotations of the molecule, and therefore
        its effective global correlation time will be maximal.

        To set the size of the diffusion tensor within the PDB frame the unit vectors used to
        generate the geometric object are first multiplied by the diffusion tensor (which has the
        units of inverse seconds) then by the scaling factor (which has the units of second
        Angstroms and has the default value of 1.8e-6 s.Angstrom).  Therefore the rotational
        diffusion rate per Angstrom is equal the inverse of the scale value (which defaults to
        5.55e5 s^-1.Angstrom^-1).  Using the default scaling value for spherical diffusion, the
        correspondence between global correlation time, Diso diffusion rate, and the radius of the
        sphere for a number of discrete cases will be:

        _________________________________________________
        |           |               |                   |
        | tm (ns)   | Diso (s^-1)   | Radius (Angstrom) |
        |___________|_______________|___________________|
        |           |               |                   |
        | 1         | 1.67e8        | 300               |
        |           |               |                   |
        | 3         | 5.55e7        | 100               |
        |           |               |                   |
        | 10        | 1.67e7        | 30                |
        |           |               |                   |
        | 30        | 5.55e6        | 10                |
        |___________|_______________|___________________|

        
        The scaling value has been fixed to facilitate comparisons within or between publications,
        but can be changed to vary the size of the tensor geometric object if necessary.  Reporting
        the rotational diffusion rate per Angstrom within figure legends would be useful.

        To create the tensor PDB representation, a number of algorithms are utilised.  Firstly the
        centre of mass is calculated for the selected residues and is represented in the PDB by a C
        atom.  Then the axes of the diffusion are calculated, as unit vectors scaled to the
        appropriate length (multiplied by the eigenvalue Dx, Dy, Dz, Dpar, Dper, or Diso as well as
        the scale value), and a C atom placed at the position of this vector plus the centre of
        mass.  Finally a uniform distribution of vectors on a sphere is generated using spherical
        coordinates.  By incrementing the polar angle using an arccos distribution, a radial array
        of vectors representing latitude are created while incrementing the azimuthal angle evenly
        creates the longitudinal vectors.  These unit vectors, which are distributed within the PDB
        frame and are of 1 Angstrom in length, are first rotated into the diffusion frame using a
        rotation matrix (the spherical diffusion tensor is not rotated).  Then they are multiplied
        by the diffusion tensor matrix to extend the vector out to the correct length, and finally
        multiplied by the scale value so that the vectors reasonably superimpose onto the
        macromolecular structure.  The last set of algorithms place all this information into a PDB
        file.  The distribution of vectors are represented by H atoms and are all connected using
        PDB CONECT records.  Each H atom is connected to its two neighbours on the both the
        longitude and latitude.  This creates a geometric PDB object with longitudinal and
        latitudinal lines.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pdb.create_tensor_pdb("
            text = text + "run=" + `run`
            text = text + ", scale=" + `scale`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Scaling.
        if type(scale) != float and type(scale) != int:
            raise RelaxNumError, ('scaling factor', scale)

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.__relax__.generic.pdb.create_tensor_pdb(run=run, scale=scale, file=file, dir=dir, force=force)


    def read(self, run=None, file=None, dir=None, model=None, load_seq=1):
        """The pdb loading function.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the structure to.

        file:  The name of the PDB file.

        dir:  The directory where the file is located.

        model:  The PDB model number.

        load_seq:  A flag specifying whether the sequence should be loaded from the PDB file.


        Description
        ~~~~~~~~~~~

        To load a specific model from the PDB file, set the model flag to an integer i.  The
        structure beginning with the line 'MODEL i' in the PDB file will be loaded.  Otherwise all
        structures will be loaded starting from the model number 1.

        To load the sequence from the PDB file, set the 'load_seq' flag to 1.  If the sequence has
        previously been loaded, then this flag will be ignored.


        Example
        ~~~~~~~

        To load all structures from the PDB file 'test.pdb' in the directory '~/pdb' for use in the
        model-free analysis run 'm8', type:

        relax> pdb.read('m8', 'test.pdb', '~/pdb', 1)
        relax> pdb.read(run='m8', file='test.pdb', dir='pdb', model=1)


        To load the 10th model from the file 'test.pdb', use:

        relax> pdb.read('m1', 'test.pdb', model=10)
        relax> pdb.read(run='m1', file='test.pdb', model=10)

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pdb.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", model=" + `model`
            text = text + ", load_seq=" + `load_seq` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The model argument.
        if model != None and type(model) != int:
            raise RelaxIntError, ('model', model)

        # The load sequence argument.
        if type(load_seq) != int or (load_seq != 0 and load_seq != 1):
            raise RelaxBinError, ('load sequence flag', load_seq)

        # Execute the functional code.
        self.__relax__.generic.pdb.read(run=run, file=file, dir=dir, model=model, load_seq=load_seq)


    def vectors(self, run=None, heteronuc='N', proton='H', res_num=None, res_name=None):
        """Function for calculating/extracting XH vectors from the structure.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the vectors to.

        heteronuc:  The heteronucleus name as specified in the PDB file.

        proton:  The name of the proton as specified in the PDB file.

        res_num:  The residue number.

        res_name:  The name of the residue.


        Description
        ~~~~~~~~~~~

        Once the PDB structures have been loaded, the unit XH bond vectors must be calculated for
        the non-spherical diffusion models.  The vectors are calculated using the atomic coordinates
        of the atoms specified by the arguments heteronuc and proton.  If more than one model
        structure is loaded, the unit XH vectors for each model will be calculated and the final
        unit XH vector will be taken as the average.


        Example
        ~~~~~~~

        To calculate the XH vectors of the backbone amide nitrogens where in the PDB file the
        backbone nitrogen is called 'N' and the attached proton is called 'H', assuming the run
        'test', type:

        relax> pdb.vectors('test')
        relax> pdb.vectors('test', 'N')
        relax> pdb.vectors('test', 'N', 'H')
        relax> pdb.vectors('test', heteronuc='N', proton='H')

        If the attached proton is called 'HN', type:

        relax> pdb.vectors('test', proton='HN')

        If you are working with RNA, you can use the residue name identifier to calculate the
        vectors for each residue separately.  For example:

        relax> pdb.vectors('m1', 'N1', 'H1', res_name='G')
        relax> pdb.vectors('m1', 'N3', 'H3', res_name='U')

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pdb.vectors("
            text = text + "run=" + `run`
            text = text + ", heteronuc=" + `heteronuc`
            text = text + ", proton=" + `proton`
            text = text + ", res_num=" + `res_num`
            text = text + ", res_name=" + `res_name` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The heteronucleus argument.
        if type(heteronuc) != str:
            raise RelaxStrError, ('heteronucleus', heteronuc)

        # The proton argument.
        if type(proton) != str:
            raise RelaxStrError, ('proton', proton)

        # Residue number.
        if res_num != None and type(res_num) != int:
            raise RelaxNoneIntError, ('residue number', res_num)

        # Residue name.
        if res_name != None and type(res_name) != str:
            raise RelaxNoneStrError, ('residue name', res_name)

        # Execute the functional code.
        self.__relax__.generic.pdb.vectors(run=run, heteronuc=heteronuc, proton=proton, res_num=res_num, res_name=res_name)
