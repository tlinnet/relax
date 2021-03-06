###############################################################################
#                                                                             #
# Copyright (C) 2003-2008,2013-2014 Edward d'Auvergne                         #
# Copyright (C) 2006 Chris MacRaild                                           #
# Copyright (C) 2008-2009 Sebastien Morin                                     #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Module docstring.
"""Functions for sorting and nesting the models in relaxation dispersion specific analysis."""

# Python module imports.
from datetime import date
from functools import partial
from operator import attrgetter, ne

# relax module imports.
from lib.dispersion.variables import EQ_ANALYTIC, EQ_NUMERIC, EQ_SILICO, EXP_TYPE_CPMG_MMQ, EXP_TYPE_R1RHO, EXP_TYPE_CPMG_SQ, EXP_TYPE_NOREX, EXP_TYPE_R2EFF, MODEL_DESC, MODEL_EQ, MODEL_EXP_TYPE, MODEL_NEST, MODEL_PARAMS, MODEL_PARAMS_LM63, MODEL_PARAMS_LM63_3SITE, MODEL_PARAMS_NS_MMQ_2SITE, MODEL_PARAMS_NS_MMQ_3SITE, MODEL_PARAMS_NS_MMQ_3SITE_LINEAR, MODEL_PARAMS_NS_R1RHO_2SITE, MODEL_PARAMS_NS_R1RHO_3SITE, MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR, MODEL_SITES, MODEL_YEAR, PARAMS_R20
from specific_analyses.relax_disp.data import is_r1_optimised


# Define class for describing the model.
# This class is defined to be able to make better sorting of the models.
class Model_class:
    def __init__(self, model=None):
        """Class for storing model information.

        @keyword model:     Current model
        @type model:        str
        """

        # Save the info to variables.
        self.model = model

        # model description.
        self.desc = MODEL_DESC[self.model]

        # model equation type: analytic, silico or numeric.
        self.eq =  MODEL_EQ[self.model]

        # The model experiment type.
        self.exp_type = MODEL_EXP_TYPE[self.model]

        # model parameters.
        self.params = MODEL_PARAMS[self.model]
        if is_r1_optimised(model=model) and 'r1' not in self.params:
            self.params.insert(0, 'r1')

        # model number of parameters.
        self.params_nr = len(self.params)

        # The number of chemical sites.
        self.sites = MODEL_SITES[self.model]

        # year where model was developed or published.
        self.year = MODEL_YEAR[self.model]

        # Ordered lists of models to nest from.
        nest_list = MODEL_NEST[self.model]

        # Remove the model itself from the list.
        if nest_list == None:
            self.nest_list = nest_list
        else:
            nest_list = list(filter(partial(ne, self.model), nest_list))
            self.nest_list = nest_list

        # Define the order of how exp type ranks.
        order_exp_type = [EXP_TYPE_R2EFF, EXP_TYPE_NOREX, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_MMQ, EXP_TYPE_R1RHO]

        # Save the index of current model to order of equation type.
        self.exp_type_i = order_exp_type.index(self.exp_type)

        # Define the order of how equation type ranks.
        order_eq = [EQ_NUMERIC, EQ_SILICO, EQ_ANALYTIC]

        # Save the index of current model to order of equation type.
        self.eq_i = order_eq.index(self.eq)

        # Define the order of how equation type ranks, when sorting before auto analyses.
        order_s = [EQ_SILICO, EQ_ANALYTIC, EQ_NUMERIC]

        # Save the index of current model to order of equation type.
        self.eq_s = order_s.index(self.eq)

        # Save the difference in year from now, to implemented model.
        self.year_diff = date.today().year - self.year

    # Make a readable presentation of the class object. Here a tuple.
    def __repr__(self):
        return repr((self.model, self.desc, self.exp_type, self.eq, self.sites, self.year, self.params, self.params_nr))


# Define function, to return model info.
def models_info(models=None):
    """Get model info for list of models.

    @keyword model:   The list of all models analysed.
    @type model:      list of str
    @return:          List of tuples, where each tuple contains model info.
    @rtype:           List of tuples with str.
    """

    # Define list of return.
    models_info = []

    # Loop over models.
    for model in models:
        # Append to the list, the class instance of model info.
        models_info.append(Model_class(model=model))

    # Return the list of model info.
    return models_info


# Define function, to determine which model to nest from.
def nesting_model(self_models=None, model=None):
    """Determine if the current model can use nested results from any of the previous analysed models.

    @keyword self_models:   The list of all models analysed.
    @type self_models:      list of str
    @keyword model:         The current model to analyse.
    @type model:            str
    @return:                The current model info, the possible nest model info.
    @rtype:                 class, class
    """


    # Get the list index for the current model in all models.
    model_index = self_models.index(model)

    # Define the list of models which can be tested. This is the number of models which have already been tested.
    completed_models = self_models[:model_index]

    # Get the current models information.
    model_info = models_info([model])[0]

    # Get the info of the completed models.
    completed_models_info = models_info(completed_models)

    # Sort the models according to: exp_type, equation type, chemical sites, year for model, number of parameters.
    completed_models_info = sorted(completed_models_info, key=attrgetter('exp_type_i', 'eq_i', 'sites', 'year_diff', 'params_nr'))

    # If no nest model list is specified, return None.
    if model_info.nest_list == None:
        return model_info, None

    else:
        # Loop over ordered list of possible nested models.
        for nest_model in model_info.nest_list:
            # Then loop over list of completed models, and its associated information.
            for completed_model_info in completed_models_info:
                # If the nested model is in list of completed models, then return that model.
                if nest_model == completed_model_info.model:
                    return model_info, completed_model_info

        # If nothing is found, return None.
        return model_info, None


# Define function, to determine which parameters to nest/copy over.
def nesting_param(model_params=None, nested_model_params=None):
    """Determine the conversion from the nested models params, to the current model params.

    @keyword model_params:          The list of the current model parameters.
    @type model_params:             list of str
    @keyword nested_model_params:   The list of the nested model parameters.
    @type nested_model_params:      list of str
    @return:                        A dictionary of parameter conversion for the current model params. 
    @rtype:                         dictionary
    """

    # Define dictionary.
    par_dic = {}

    # Loop over the parameters in the model parameters.
    for param in model_params:
        # The R20 parameters.
        if param in PARAMS_R20:
            # If both models have same parameter.
            if param in nested_model_params:
                par_dic[param] = param

            # If copying from a simple model to a complex model.
            elif param == 'r2a' and 'r2' in nested_model_params:
                par_dic[param] = 'r2'

            elif param == 'r2b' and 'r2' in nested_model_params:
                par_dic[param] = 'r2'

            # If copying from a complex model to a simple model.
            elif param == 'r2' and 'r2a' in nested_model_params:
                par_dic[param] = 'r2a'

        # All other parameters.
        elif param in nested_model_params:
            par_dic[param] = param

        else:
            par_dic[param] = None

    ## The LM63 3-site model parameters.
    if set(model_params) == set(MODEL_PARAMS_LM63_3SITE) and set(nested_model_params) == set(MODEL_PARAMS_LM63):
        for param in model_params:
            if param == 'phi_ex_B':
                par_dic[param] = 'phi_ex'

            elif param == 'phi_ex_C':
                par_dic[param] = 'phi_ex'

            elif param == 'kB':
                par_dic[param] = 'kex'

            elif param == 'kC':
                par_dic[param] = 'kex'

    ## The 'MODEL_PARAMS_NS_R1RHO_3SITE' model parameters from 'MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR'.
    elif set(model_params) == set(MODEL_PARAMS_NS_R1RHO_3SITE) and set(nested_model_params) == set(MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR):
        for param in model_params:
            if param == 'kex_AC':
                par_dic[param] = '0.0'

    ## The 'MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR' model parameters from R1RHO 2SITE.
    elif set(model_params) == set(MODEL_PARAMS_NS_R1RHO_3SITE_LINEAR) and set(nested_model_params) == set(MODEL_PARAMS_NS_R1RHO_2SITE):
        for param in model_params:
            if param == 'dw_AB':
                par_dic[param] = 'dw'

            elif param == 'kex_AB':
                par_dic[param] = 'kex'

            elif param == 'dw_BC':
                par_dic[param] = 'dw'

            elif param == 'kex_BC':
                par_dic[param] = 'kex'

            elif param == 'pB':
                par_dic[param] = '1 - pA'

    ## The 'MODEL_PARAMS_NS_R1RHO_3SITE' model parameters from R1RHO 2SITE.
    elif set(model_params) == set(MODEL_PARAMS_NS_R1RHO_3SITE) and set(nested_model_params) == set(MODEL_PARAMS_NS_R1RHO_2SITE):
        for param in model_params:
            if param == 'dw_AB':
                par_dic[param] = 'dw'

            elif param == 'kex_AB':
                par_dic[param] = 'kex'

            elif param == 'dw_BC':
                par_dic[param] = 'dw'

            elif param == 'kex_BC':
                par_dic[param] = 'kex'

            elif param == 'kex_AC':
                par_dic[param] = 'kex'

            elif param == 'pB':
                par_dic[param] = '1 - pA'

    ## The 'MODEL_PARAMS_NS_MMQ_3SITE' model parameters from 'MODEL_PARAMS_NS_MMQ_3SITE_LINEAR'.
    elif set(model_params) == set(MODEL_PARAMS_NS_MMQ_3SITE) and set(nested_model_params) == set(MODEL_PARAMS_NS_MMQ_3SITE_LINEAR):
        for param in model_params:
            if param == 'kex_AC':
                par_dic[param] = '0.0'

    ## The 'MODEL_PARAMS_NS_MMQ_3SITE_LINEAR' model parameters from 'MODEL_PARAMS_NS_MMQ_2'.
    elif set(model_params) == set(MODEL_PARAMS_NS_MMQ_3SITE_LINEAR) and set(nested_model_params) == set(MODEL_PARAMS_NS_MMQ_2SITE):
        for param in model_params:
            if param == 'dw_AB':
                par_dic[param] = 'dw'

            elif param == 'dwH_AB':
                par_dic[param] = 'dwH'

            elif param == 'kex_AB':
                par_dic[param] = 'kex'

            elif param == 'dw_BC':
                par_dic[param] = 'dw'

            elif param == 'dwH_BC':
                par_dic[param] = 'dwH'

            elif param == 'kex_BC':
                par_dic[param] = 'kex'

            elif param == 'pB':
                par_dic[param] = '1 - pA'

    ## The 'MODEL_PARAMS_NS_MMQ_3SITE' model parameters from 'MODEL_PARAMS_NS_MMQ_2'.
    elif set(model_params) == set(MODEL_PARAMS_NS_MMQ_3SITE) and set(nested_model_params) == set(MODEL_PARAMS_NS_MMQ_2SITE):
        for param in model_params:
            if param == 'dw_AB':
                par_dic[param] = 'dw'

            elif param == 'dwH_AB':
                par_dic[param] = 'dwH'

            elif param == 'kex_AB':
                par_dic[param] = 'kex'

            elif param == 'dw_BC':
                par_dic[param] = 'dw'

            elif param == 'dwH_BC':
                par_dic[param] = 'dwH'

            elif param == 'kex_BC':
                par_dic[param] = 'kex'

            elif param == 'kex_AC':
                par_dic[param] = 'kex'

            elif param == 'pB':
                par_dic[param] = '1 - pA'

    # Return the dictionary of conversion.
    return par_dic


# Define function, to sort models.
def sort_models(models=None):
    """Determine how to order the models for analyses.

    @keyword models:   The list of all models to be analysed.
    @type models:      list of str
    @return:           The ordered list how models should be analysed.
    @rtype:            list of str
    """

    # Get the info of the models selected for analysis.
    all_models_info = models_info(models)

    # Sort the models according to: exp_type, equation type, chemical sites, year for model, number of parameters.
    all_models_info_sorted = sorted(all_models_info, key=attrgetter('exp_type_i', 'eq_s', 'sites', 'year_diff', 'params_nr'))

    # Define list of sorted models.
    sorted_models = []

    # Loop over the models info, and extract model.
    for model_info in all_models_info_sorted:
        sorted_models.append(model_info.model)

    # Return sorted list of models.
    return sorted_models

