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
import sys

# relax module imports.
import help
from relax_errors import RelaxIntError, RelaxListError, RelaxListStrError, RelaxNoneIntError, RelaxStrError


class Model_free:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for holding the preset model functions."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def create_model(self, model=None, equation=None, params=None, res_num=None):
        """Function to create a model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model-free model.

        equation:  The model-free equation.

        params:  The array of parameter names of the model.

        res_num:  The residue number.


        Model-free equation
        ~~~~~~~~~~~~~~~~~~~

        'mf_orig' selects the original model-free equations with parameters {S2, te}.
        'mf_ext' selects the extended model-free equations with parameters {S2f, tf, S2, ts}.
        'mf_ext2' selects the extended model-free equations with parameters {S2f, tf, S2s, ts}.


        Model-free parameters
        ~~~~~~~~~~~~~~~~~~~~~

        The following parameters are accepted for the original model-free equation:

            'S2':   The square of the generalised order parameter.
            'te':   The effective correlation time.

        The following parameters are accepted for the extended model-free equation:

            'S2f':  The square of the generalised order parameter of the faster motion.
            'tf':   The effective correlation time of the faster motion.
            'S2':   The square of the generalised order parameter S2 = S2f * S2s.
            'ts':   The effective correlation time of the slower motion.

        The following parameters are accepted for the extended 2 model-free equation:

            'S2f':  The square of the generalised order parameter of the faster motion.
            'tf':   The effective correlation time of the faster motion.
            'S2s':  The square of the generalised order parameter of the slower motion.
            'ts':   The effective correlation time of the slower motion.

        The following parameters are accepted for all equations:

            'Rex':  The chemical exchange relaxation.
            'r':    The average bond length <r>.
            'CSA':  The chemical shift anisotropy.


        Residue number
        ~~~~~~~~~~~~~~

        If 'res_num' is supplied as an integer then the model will only be created for that residue,
        otherwise the model will be created for all residues.


        Examples
        ~~~~~~~~

        The following commands will create the model-free model 'm1' which is based on the original
        model-free equation and contains the single parameter 'S2'.

        relax> model_free.create_model('m1', 'mf_orig', ['S2'])
        relax> model_free.create_model(model='m1', params=['S2'], equation='mf_orig')


        The following commands will create the model-free model 'large_model' which is based on the
        extended model-free equation and contains the seven parameters 'S2f', 'tf', 'S2', 'ts',
        'Rex', 'CSA', 'r'.

        relax> model_free.create_model('large_model', 'mf_ext', ['S2f', 'tf', 'S2', 'ts', 'Rex',
                                       'CSA', 'r'])
        relax> model_free.create_model(model='large_model', params=['S2f', 'tf', 'S2', 'ts', 'Rex',
                                       'CSA', 'r'], equation='mf_ext')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "model_free.create_model("
            text = text + "model=" + `model`
            text = text + ", equation=" + `equation`
            text = text + ", params=" + `params`
            text = text + ", res_num=" + `res_num` + ")"
            print text

        # Model argument.
        if type(model) != str:
            raise RelaxStrError, ('model', model)

        # Equation.
        if type(equation) != str:
            raise RelaxStrError, ('model-free equation', equation)

        # Parameter types.
        if type(params) != list:
            raise RelaxListError, ('parameter types', params)
        for i in xrange(len(params)):
            if type(params[i]) != str:
                raise RelaxListStrError, ('parameter types', params)

        # Residue number.
        if res_num != None and type(res_num) != int:
            raise RelaxNoneIntError, ('residue number', res_num)

        # Execute the functional code.
        model_free.create_model(model=model, equation=equation, params=params, res_num=res_num)


    def delete(self):
        """Function for deleting all model-free data from the current data pipe.

        Examples
        ~~~~~~~~

        To delete all model-free data corresponding to the current data pipe 'm2', type:

        relax> model_free.delete()
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "model_free.delete()"
            print text

        # Execute the functional code.
        model_free.delete()


    def remove_tm(self, res_num=None):
        """Function for removing the local tm parameter from a model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_num:  The residue number.


        Description
        ~~~~~~~~~~~

        This function will remove the local tm parameter from the model-free parameter set.  If
        there is no local tm parameter within the set nothing will happen.

        If no residue number is given, then the function will apply to all residues.


        Examples
        ~~~~~~~~

        The following command will remove the parameter 'tm':

        relax> model_free.remove_tm()
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "model_free.remove_tm("
            text = text + "res_num=" + `res_num` + ")"
            print text

        # Residue number.
        if res_num != None and type(res_num) != int:
            raise RelaxNoneIntError, ('residue number', res_num)

        # Execute the functional code.
        model_free.remove_tm(res_num=res_num)


    def select_model(self, model=None, res_num=None):
        """Function for the selection of a preset model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the preset model.


        The preset models
        ~~~~~~~~~~~~~~~~~

        The standard preset model-free models are
            'm0' = {},
            'm1' = {S2},
            'm2' = {S2, te},
            'm3' = {S2, Rex},
            'm4' = {S2, te, Rex},
            'm5' = {S2f, S2, ts},
            'm6' = {S2f, tf, S2, ts},
            'm7' = {S2f, S2, ts, Rex},
            'm8' = {S2f, tf, S2, ts, Rex},
            'm9' = {Rex}.

        The preset model-free models with optimisation of the CSA value are
            'm10' = {CSA},
            'm11' = {CSA, S2},
            'm12' = {CSA, S2, te},
            'm13' = {CSA, S2, Rex},
            'm14' = {CSA, S2, te, Rex},
            'm15' = {CSA, S2f, S2, ts},
            'm16' = {CSA, S2f, tf, S2, ts},
            'm17' = {CSA, S2f, S2, ts, Rex},
            'm18' = {CSA, S2f, tf, S2, ts, Rex},
            'm19' = {CSA, Rex}.

        The preset model-free models with optimisation of the bond length are
            'm20' = {r},
            'm21' = {r, S2},
            'm22' = {r, S2, te},
            'm23' = {r, S2, Rex},
            'm24' = {r, S2, te, Rex},
            'm25' = {r, S2f, S2, ts},
            'm26' = {r, S2f, tf, S2, ts},
            'm27' = {r, S2f, S2, ts, Rex},
            'm28' = {r, S2f, tf, S2, ts, Rex},
            'm29' = {r, CSA, Rex}.

        The preset model-free models with both optimisation of the bond length and CSA are
            'm30' = {r, CSA},
            'm31' = {r, CSA, S2},
            'm32' = {r, CSA, S2, te},
            'm33' = {r, CSA, S2, Rex},
            'm34' = {r, CSA, S2, te, Rex},
            'm35' = {r, CSA, S2f, S2, ts},
            'm36' = {r, CSA, S2f, tf, S2, ts},
            'm37' = {r, CSA, S2f, S2, ts, Rex},
            'm38' = {r, CSA, S2f, tf, S2, ts, Rex},
            'm39' = {r, CSA, Rex}.

        Warning:  The models in the thirties range fail when using standard R1, R2, and NOE
        relaxation data.  This is due to the extreme flexibly of these models where a change in the
        parameter 'r' is compensated by a corresponding change in the parameter 'CSA' and
        vice versa.


        Additional preset model-free models, which are simply extensions of the above models with
        the addition of a local tm parameter are:
            'tm0' = {tm},
            'tm1' = {tm, S2},
            'tm2' = {tm, S2, te},
            'tm3' = {tm, S2, Rex},
            'tm4' = {tm, S2, te, Rex},
            'tm5' = {tm, S2f, S2, ts},
            'tm6' = {tm, S2f, tf, S2, ts},
            'tm7' = {tm, S2f, S2, ts, Rex},
            'tm8' = {tm, S2f, tf, S2, ts, Rex},
            'tm9' = {tm, Rex}.

        The preset model-free models with optimisation of the CSA value are
            'tm10' = {tm, CSA},
            'tm11' = {tm, CSA, S2},
            'tm12' = {tm, CSA, S2, te},
            'tm13' = {tm, CSA, S2, Rex},
            'tm14' = {tm, CSA, S2, te, Rex},
            'tm15' = {tm, CSA, S2f, S2, ts},
            'tm16' = {tm, CSA, S2f, tf, S2, ts},
            'tm17' = {tm, CSA, S2f, S2, ts, Rex},
            'tm18' = {tm, CSA, S2f, tf, S2, ts, Rex},
            'tm19' = {tm, CSA, Rex}.

        The preset model-free models with optimisation of the bond length are
            'tm20' = {tm, r},
            'tm21' = {tm, r, S2},
            'tm22' = {tm, r, S2, te},
            'tm23' = {tm, r, S2, Rex},
            'tm24' = {tm, r, S2, te, Rex},
            'tm25' = {tm, r, S2f, S2, ts},
            'tm26' = {tm, r, S2f, tf, S2, ts},
            'tm27' = {tm, r, S2f, S2, ts, Rex},
            'tm28' = {tm, r, S2f, tf, S2, ts, Rex},
            'tm29' = {tm, r, CSA, Rex}.

        The preset model-free models with both optimisation of the bond length and CSA are
            'tm30' = {tm, r, CSA},
            'tm31' = {tm, r, CSA, S2},
            'tm32' = {tm, r, CSA, S2, te},
            'tm33' = {tm, r, CSA, S2, Rex},
            'tm34' = {tm, r, CSA, S2, te, Rex},
            'tm35' = {tm, r, CSA, S2f, S2, ts},
            'tm36' = {tm, r, CSA, S2f, tf, S2, ts},
            'tm37' = {tm, r, CSA, S2f, S2, ts, Rex},
            'tm38' = {tm, r, CSA, S2f, tf, S2, ts, Rex},
            'tm39' = {tm, r, CSA, Rex}.



        Residue number
        ~~~~~~~~~~~~~~

        If 'res_num' is supplied as an integer then the model will only be selected for that
        residue, otherwise the model will be selected for all residues.



        Examples
        ~~~~~~~~

        To pick model 'm1' for all selected residues, type:

        relax> model_free.select_model('m1')
        relax> model_free.select_model(model='m1')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "model_free.select_model("
            text = text + "model=" + `model`
            text = text + ", res_num=" + `res_num` + ")"
            print text

        # Model argument.
        elif type(model) != str:
            raise RelaxStrError, ('model', model)

        # Residue number.
        if res_num != None and type(res_num) != int:
            raise RelaxNoneIntError, ('residue number', res_num)

        # Execute the functional code.
        model_free.select_model(model=model, res_num=res_num)
