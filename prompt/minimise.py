from math import pi
from Numeric import Float64, array, zeros
from re import match


class Min:
    def __init__(self, relax):
        """Class containing the fixed, grid_search, and minimise functions."""

        self.relax = relax


    def fixed(self, model=None, values=None, print_flag=1):
        """Function for fixing the initial parameter values.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

        values:  An array of numbers of length equal to the number of parameters in the model.

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.


        Examples
        ~~~~~~~~

        This command will fix the parameter values of the model 'm2', which is the original
        model-free equation with parameters {S2, te}, before minimisation to the preselected values
        of this function.

        relax> fixed('m2')


        This command will do the same except the S2 and te values will be set to one and ten ps
        respectively.

        relax> fixed('m2', [1.0, 10 * 10e-12])
        relax> fixed('m2', values=[1.0, 10 * 10e-12])
        """

        # The model argument.
        if type(model) != str:
            print "The model argument " + `model` + " must be a string."
            return

        # Find the index of the model.
        if not self.relax.data.equations.has_key(model):
            print "The model '" + model + "' has not been created yet."
            return

        # User defined values.
        if values != None:
            if type(values) == list:
                if len(values) != len(self.relax.data.param_types[model]):
                    print "The argument 'values' must be an array of length equal to the number of parameters in the model."
                    print "Number of parameters = " + `len(self.relax.data.param_types[model])`
                    print "Length of 'values' = " + `len(values)`
                    return
                for i in range(len(values)):
                    if type(values[i]) != float and type(values[i]) != int:
                        print "The argument 'values' must be an array of numbers."
                        return
            else:
                print "The argument 'values' must be an array of numbers."
                return

        # The debugging flag.
        if type(print_flag) != int:
            print "The print_flag argument must be an integer."
            return

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("fixed", model)
        if fns == None:
            return
        self.fixed_setup, self.main_loop = fns

        # Setup the fixed parameter options.
        if values:
            # User supplied values.
            min_options = array(values)
        else:
            # Fixed values.
            empty = zeros(len(self.relax.data.param_types[model]), Float64)
            min_options = self.fixed_setup(min_options=empty, model=model)

        # Diagonal scaling.
        if self.relax.data.scaling.has_key(model):
            min_options = min_options / self.relax.data.scaling[model][0]

        # Main iterative loop.
        self.main_loop(model=model, min_algor="fixed", min_options=min_options, print_flag=print_flag)


    def grid_search(self, model=None, lower=None, upper=None, inc=21, print_flag=1):
        """The grid search function.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

        lower:  An array of the lower bound parameter values for the grid search.  The length of the
        array should be equal to the number of parameters in the model.

        upper:  An array of the upper bound parameter values for the grid search.  The length of the
        array should be equal to the number of parameters in the model.

        inc:  The number of increments to search over.  If a single integer is given then the number
        of increments will be equal in all dimensions.  Different numbers of increments in each
        direction can be set if 'inc' is set to an array of integers of length equal to the number
        of parameters.

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.
        """

        # The model argument.
        if type(model) != str:
            print "The model argument " + `model` + " must be a string."
            return

        # Find the index of the model.
        if not self.relax.data.equations.has_key(model):
            print "The model '" + model + "' has not been created yet."
            return

        # The lower bounds.
        if lower:
            bad_arg = 0
            if len(lower) != len(self.relax.data.param_types[model]):
                bad_arg = 1
            for i in range(len(lower)):
                if type(lower[i]) != float and type(lower[i]) != int:
                    bad_arg = 1
            if bad_arg:
                print "The argument 'lower' must be an array of numbers of length equal to the number of parameters in the model."
                return
        else:
            lower = []
            for i in range(len(self.relax.data.param_types[model])):
                lower.append(None)

        # The upper bounds.
        if upper:
            bad_arg = 0
            if len(upper) != len(self.relax.data.param_types[model]):
                bad_arg = 1
            for i in range(len(upper)):
                if type(upper[i]) != float and type(upper[i]) != int:
                    bad_arg = 1
            if bad_arg:
                print "The argument 'upper' must be an array of numbers of length equal to the number of parameters in the model."
                return
        else:
            upper = []
            for i in range(len(self.relax.data.param_types[model])):
                upper.append(None)

        # The incrementation value.
        bad_arg = 0
        if type(inc) != int and type(inc) != list:
            bad_arg = 1
        if type(inc) == list:
            if len(inc) != len(self.relax.data.param_types[model]):
                bad_arg = 1
            for i in range(len(inc)):
                if type(inc[i]) != int:
                    bad_arg = 1
        if bad_arg:
            print "The argument 'inc' must be either an integer or an array of integers of length equal to the number of parameters in the model."
            return
        elif type(inc) == int:
            inc_vector = []
            for i in range(len(self.relax.data.param_types[model])):
                inc_vector.append(inc)

        # The debugging flag.
        if type(print_flag) != int:
            print "The print_flag argument must be an integer."
            return

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("grid_search", model)
        if fns == None:
            return
        self.grid_setup, self.main_loop = fns

        # Setup the grid search options.
        min_options = self.grid_setup(model=model, inc_vector=inc_vector)

        # Set the lower and upper bounds if these are supplied.
        for i in range(len(self.relax.data.param_types[model])):
            if lower[i] != None:
                min_options[i][1] = lower[i]
            if upper[i] != None:
                min_options[i][2] = upper[i]

        # Diagonal scaling.
        if self.relax.data.scaling.has_key(model):
            for i in range(len(min_options)):
                min_options[i][1] = min_options[i][1] / self.relax.data.scaling[model][0][i]
                min_options[i][2] = min_options[i][2] / self.relax.data.scaling[model][0][i]

        # Main iterative loop.
        self.main_loop(model=model, min_algor='grid', min_options=min_options, print_flag=print_flag)


    def minimise(self, *args, **keywords):
        """Minimisation function.

        Arguments
        ~~~~~~~~~

        The arguments are all strings which specify which minimiser to use as well as the
        minimisation options.  At least one argument is required.  As this function calls the
        generic minimisation function 'generic_minimise', to see the full list of allowed arguments
        import the function and view its docstring by typing:

        relax> from minimise.generic import generic_minimise
        relax> help(generic_minimise)


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

        func_tol:  The function tolerance.  This is used to terminate minisation once the function
        value between iterations is less than the tolerance.  The default value is 1e-25.

        max_iter:  The maximum number of iterations.  The default value is 1e7.

        constraints:  A flag specifying whether the parameters should be constrained.  The default
        is to turn constraints on (constraints=1).

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.
        """

        # Minimization algorithm.
        if len(args) == 0:
            print "The minimisation algorithm has not been specified."
            return
        min_algor = args[0]

        # Minimization options.
        min_options = args[1:]

        # Test for invalid keywords.
        valid_keywords = ['model', 'func_tol', 'grad_tol', 'max_iterations', 'max_iter', 'constraints', 'print_flag']
        for key in keywords:
            valid = 0
            for valid_key in valid_keywords:
                if key == valid_key:
                    valid = 1
            if not valid:
                print "The keyword " + `key` + " is invalid."
                return

        # The model keyword.
        if keywords.has_key('model'):
            model = keywords['model']
            if type(model) != str:
                print "The model argument " + `model` + " must be a string."
                return
        else:
            print "No model has been given."
            return
        # self.res causing problems here!
        #if len(self.relax.data.params[model][self.res]) == 0:
        #    print "The minimisation of a zero parameter model is not allowed."
        #    return
        if not self.relax.data.equations.has_key(model):   # Find the index of the model.
            print "The model '" + model + "' has not been created yet."
            return

        # The function tolerance value.
        if keywords.has_key('func_tol'):
            func_tol = keywords['func_tol']
        else:
            func_tol = 1e-25

        # The gradient tolerance value.
        if keywords.has_key('grad_tol'):
            grad_tol = keywords['grad_tol']
        else:
            grad_tol = None

        # The maximum number of iterations.
        if keywords.has_key('max_iterations'):
            max_iterations = keywords['max_iterations']
        elif keywords.has_key('max_iter'):
            max_iterations = keywords['max_iter']
        else:
            max_iterations = 10000000

        # Constraint flag.
        if keywords.has_key('constraints'):
            constraints = keywords['constraints']
        else:
            constraints = 1
        if constraints == 1:
            min_algor = 'Method of Multipliers'
            min_options = args
        elif constraints != 0:
            print "The constraints flag (constraints=" + `constraints` + ") must be either 0 or 1."
            return

        # Print options.
        if keywords.has_key('print_flag'):
            print_flag = keywords['print_flag']
        else:
            print_flag = 1

        # Equation type specific function setup.
        self.main_loop = self.relax.specific_setup.setup("minimise", model)
        if self.main_loop == None:
            return

        # Main iterative loop.
        self.main_loop(model=model, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, print_flag=print_flag)
