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


from Queue import Queue
from os import popen3

from thread_classes import RelaxParentThread, RelaxThread


class Minimise:
    def __init__(self, relax):
        """Class containing the calc, grid_search, minimise, and set functions."""

        self.relax = relax


    def calc(self, run=None, print_flag=1):
        """Function for calculating the function value."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific calculate function setup.
        calculate = self.relax.specific_setup.setup('calculate', function_type)

        # Monte Carlo simulation calculation.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Loop over the simulations.
            for i in xrange(self.relax.data.sim_number[run]):
                if print_flag:
                    print "Simulation " + `i+1`
                calculate(run=run, print_flag=print_flag-1, sim_index=i)

        # Minimisation.
        else:
            calculate(run=run, print_flag=print_flag)


    def grid_search(self, run=None, lower=None, upper=None, inc=None, constraints=1, print_flag=1):
        """The grid search function."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific grid search function.
        grid_search = self.relax.specific_setup.setup('grid_search', function_type)

        # Monte Carlo simulation grid search.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Loop over the simulations.
            for i in xrange(self.relax.data.sim_number[run]):
                if print_flag:
                    print "Simulation " + `i+1`
                grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag-1, sim_index=i)

        # Grid search.
        else:
            grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=1, scaling=1, print_flag=1, sim_index=None):
        """Minimisation function."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific minimisation function.
        minimise = self.relax.specific_setup.setup('minimise', function_type)

        # Single Monte Carlo simulation.
        if sim_index != None:
            minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag, sim_index=sim_index)

        # Monte Carlo simulation minimisation.
        elif hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Threaded minimisation of simulations.
            if self.relax.data.thread.status:
                # Print out.
                print "Threaded minimisation of Monte Carlo simulations.\n"

                # Run the main threading loop.
                RelaxMinParentThread(self.relax, run, min_algor, min_options, func_tol, grad_tol, max_iterations, constraints, scaling, print_flag)

            # Non-threaded minimisation of simulations.
            else:
                for i in xrange(self.relax.data.sim_number[run]):
                    if print_flag:
                        print "Simulation " + `i+1`
                    minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag-1, sim_index=i)

        # Standard minimisation.
        else:
            minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag)




# Main threading loop for the minimisation of Monte Carlo simulations. 
######################################################################

class RelaxMinParentThread(RelaxParentThread):
    def __init__(self, relax, parent_run, *min_args):
        """Initialisation of the Monte Carlo simulation minimisation parent thread."""

        # Arguments.
        self.relax = relax
        self.parent_run = parent_run
        self.min_args = min_args

        # Run the RelaxParentThread __init__ function.
        RelaxParentThread.__init__(self)

        # The number of jobs.
        self.num_jobs = self.relax.data.sim_number[self.parent_run]

        # Run the main loop.
        self.run()


    def thread_object(self, i):
        """Function for returning an initialised thread object."""

        # Return the thread object.
        return RelaxMinimiseThread(self.relax, i, self.job_queue, self.results_queue, self.finished_jobs, self.job_locks, self.tag, self.parent_run, self.min_args)



# Threads for the minimisation of Monte Carlo simulations.
##########################################################

class RelaxMinimiseThread(RelaxThread):
    def __init__(self, relax, i, job_queue, results_queue, finished_jobs, job_locks, tag, parent_run, min_args):
        """Initialisation of the thread."""

        # Arguments.
        self.relax = relax
        self.tag = tag
        self.parent_run = parent_run
        self.min_args = min_args

        # Run the RelaxThread __init__ function (this is 'asserted' by the Thread class).
        RelaxThread.__init__(self, i, job_queue, results_queue, finished_jobs, job_locks)

        # Expand the minimisation arguments.
        self.min_algor, self.min_options, self.func_tol, self.grad_tol, self.max_iterations, self.constraints, self.scaling, self.print_flag = self.min_args


    def exec_thread_code(self, data):
        """Function containing the thread specific code.
        
        This code is for the minimisation of a single Monte Carlo simulation.
        """

        # Initialise the job termination flag.
        self.completion_flag = 0

        # Place the job queue data, which in this case is the simulation number, in 'self'.
        self.sim = data

        # Job termination if the job has been finished by a faster thread.
        if self.finished_jobs[self.sim] == 1:
            return

        # Place the job back into the job queue.  This is to make the threads fail safe and so that idle faster threads will pick up the jobs of the slower threads.
        self.job_queue.put(self.sim)

        # Thread run name.
        self.thread_run = '%s_sim_%s' % (self.tag, self.sim)

        # Script and log files.
        self.script_file = "%s/%s/script_sim_%s.py" % (self.swd, self.tag, self.sim)
        self.log_file = "%s/%s/sim_%s.log" % (self.swd, self.tag, self.sim)

        # Generate the script file for the minimisation of sim number 'sim'.
        self.generate_script()

        # Execute relax and run the script.
        self.exec_relax()

        # Job termination if the job has been finished by a faster thread.
        if self.finished_jobs[self.sim] == 1:
            return

        # Create a run in the parent to temporarily store the data prior to copying into the main run.
        self.relax.generic.runs.create(run=self.thread_run, run_type=self.relax.data.run_types[self.relax.data.run_names.index(self.parent_run)])

        # Read the data into the run.
        self.relax.generic.results.read(run=self.thread_run, file_data=self.results, print_flag=0)

        # Copy the results from the thread run to the parent run.
        self.relax.generic.results.copy(run1=self.thread_run, run2=self.parent_run, sim=self.sim)

        # Delete the thread run
        self.relax.generic.runs.delete(self.thread_run)

        # Set the results to the completed simulation number.
        self.results = self.sim

        # Job completed successfully.
        self.completion_flag = 1


    def generate_script(self):
        """Function for generating the script for the thread to minimise sim `sim`."""

        # Function array.
        fn = []

        # Function: Load the program state.
        fn.append("self.relax.generic.state.load(file='%s')" % self.results_file)

        # Function: Minimise.
        fn.append("self.relax.generic.minimise.minimise(run='%s', min_algor='%s', min_options=%s, func_tol=%s, grad_tol=%s, max_iterations=%s, constraints=%s, scaling=%s, print_flag=%s, sim_index=%s)" % (self.parent_run, self.min_algor, self.min_options, self.func_tol, self.grad_tol, self.max_iterations, self.constraints, self.scaling, self.print_flag, self.sim))

        # Function: Turn logging off.  This is so that the results can come back through the pipe's stdout.
        fn.append("self.relax.IO.logging_off()")

        # Generate the main text of the script file.
        text = ''
        for i in xrange(len(fn)):
            text = text + "print \"\\n" + fn[i] + "\"\n"
            text = text + fn[i] + "\n"

        # Function: Write the to stdout.
        text = text + "self.relax.generic.results.display(run='%s')\n" % (self.parent_run)

        # Cat the text into the script file.
        cmd = "cat > %s" % self.script_file
        cmd = self.remote_command(cmd=cmd, login_cmd=self.login_cmd)

        # Open a pipe.
        self.stdin, self.stdout, self.stderr = popen3(cmd, 'r')

        # Write the text to the pipe's stdin, then close it.
        self.stdin.write(text)
        self.stdin.close()

        # Stderr.
        err = self.stderr.readlines()

        # Close all pipes.
        self.stdout.close()
        self.stderr.close()

        # The file could not be copied.
        if len(err):
            raise RelaxError, "The command `%s` could not be executed." % cmd
