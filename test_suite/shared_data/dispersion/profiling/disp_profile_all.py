#!/usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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

# Python script for obtaining profiling statistics for multiple models between the current and an alternative version of relax.

# Python module imports.
from numpy import average, float64, std, zeros
from os import pardir, path, sep
from re import search
from shutil import copyfile
from subprocess import PIPE, Popen
import sys

# Modify the system path to add the base directory of the current relax version.
sys.path.append(path.join(pardir, pardir, pardir, pardir))

# relax module imports.
import version


# The number of iterations to run each script for the statistics.
N = 10

# The models / The current scripts. / Iterations / Multiplication factors (to scale for different nr_iter values).
models = [
    ['No Rex', 'profiling_norex.py', 100, 1],
    ['LM63', 'profiling_lm63.py', 100, 1],
    ['CR72', 'profiling_cr72.py', 100, 1],
    ['CR72 full', 'profiling_cr72_full.py', 100, 1],
    ['IT99',  'profiling_it99.py', 100, 1],
    ['TSMFK01', 'profiling_tsmfk01.py', 100, 1],
    ['B14', 'profiling_b14.py', 100, 1],
    ['B14 full', 'profiling_b14_full.py', 100, 1],
    ['NS CPMG 2-site 3D', 'profiling_ns_cpmg_2site_3D.py', 10, 10],
    ['NS CPMG 2-site 3D full', 'profiling_ns_cpmg_2site_3D_full.py', 10, 10],
    ['NS CPMG 2-site expanded', 'profiling_ns_cpmg_2site_expanded.py', 100, 1],
    ['NS CPMG 2-site star', 'profiling_ns_cpmg_2site_star.py', 10, 10],
    ['NS CPMG 2-site star full', 'profiling_ns_cpmg_2site_star_full.py', 10, 10],
    ['M61', 'profiling_m61.py', 100, 1],
    ['DPL94', 'profiling_dpl94.py', 100, 1],
    ['TP02', 'profiling_tp02.py', 100, 1],
    ['TAP03', 'profiling_tap03.py', 100, 1],
    ['MP05', 'profiling_mp05.py', 100, 1],
    ['NS R1rho 2-site', 'profiling_ns_r1rho_2site.py', 10, 10],
]

# Path to relax 3.2.2, or any other version.
if len(sys.argv) == 1:
    alt_path = '/data/relax/tags/3.2.2'
else:
    alt_path = sys.argv[1]

# The Python executable name.
python = 'python'


# First a printout of the relax version.
sys.stdout.write("\n\nCurrent relax version:  ")
sys.stdout.write(version.version_full())
sys.stdout.write("\n\n")

# Copy the current scripts to the base directory of the alternative relax version.
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]
    print("Copying: model=%s script=%s iterations=%s scale=%s"%(model, script, iter, scaling_factor))
    copyfile(script, alt_path+sep+script)

# Initialise structures for the timing statistics.
timings_new = {}
timings_alt = {}
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]
    timings_new[model] = zeros((2, N), float64)
    timings_alt[model] = zeros((2, N), float64)
timings = [timings_new, timings_alt]

# Loop over the execution iterations.
for exec_iter in range(N):
    # Printout.
    print("\n\nExecution iteration %i\n" % (exec_iter+1))

    # Loop over each model.
    for i in range(len(models)):
        model, script, iter, scaling_factor = models[i]
        # The commands to run.
        cmds = [
            "%s %s" % (python, script),
            "%s %s %s" % (python, alt_path+sep+script, alt_path),
        ]

        # Loop over the commands.
        for cmd_index in range(2):
            # Printout.
            print("$ %s" % cmds[cmd_index])

            # Execute the current script.
            pipe = Popen(cmds[cmd_index], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

            # Close the pipe.
            pipe.stdin.close()

            # Write all errors to stderr.
            err_lines = pipe.stderr.readlines()
            for line in err_lines:
                # Decode Python 3 byte arrays.
                if hasattr(line, 'decode'):
                    line = line.decode()

                # Write.
                sys.stderr.write(line)

            # Process the output.
            index = 0
            for line in pipe.stdout.readlines():
                # Decode Python 3 byte arrays.
                if hasattr(line, 'decode'):
                    line = line.decode()

                # Find the profiling stats for the target function method.
                if not search('func_', line):
                    continue

                # Printout for the record.
                print(line[:-1])

                # Split the line.
                row = line.split()

                # The timing.
                timings[cmd_index][model][index, exec_iter] = float(row[3])

                # Increment the index.
                index += 1

# Statistics.
ave_new = {}
ave_new_cluster = {}
ave_alt = {}
ave_alt_cluster = {}
sd_new = {}
sd_new_cluster = {}
sd_alt = {}
sd_alt_cluster = {}
speed_up = {}
speed_up_cluster = {}

# Loop over the models.
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]

    # The averages (scaled for different nr_iter).
    ave_new[model] = average(timings_new[model][0]) * scaling_factor
    ave_new_cluster[model] = average(timings_new[model][1]) * scaling_factor
    ave_alt[model] = average(timings_alt[model][0]) * scaling_factor
    ave_alt_cluster[model] = average(timings_alt[model][1]) * scaling_factor

    # The SD.
    sd_new[model] = std(timings_new[model][0]) * scaling_factor
    sd_new_cluster[model] = std(timings_new[model][1]) * scaling_factor
    sd_alt[model] = std(timings_alt[model][0]) * scaling_factor
    sd_alt_cluster[model] = std(timings_alt[model][1]) * scaling_factor

    # The speed up.
    speed_up[model] = ave_alt[model] / ave_new[model]
    speed_up_cluster[model] = ave_alt_cluster[model] / ave_new_cluster[model]

# Final printout.
print("\n\n100 single spins analysis:")
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]
    print("%-25s  %7.3f+/-%.3f -> %7.3f+/-%.3f, %7.3fx faster." % (model+':', ave_alt[model], sd_alt[model], ave_new[model], sd_new[model], speed_up[model]))

print("\nCluster of 100 spins analysis:")
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]
    if model == 'IT99':
        comment = "IT99: Cluster of only 1 spin analysis, since v. 3.2.2 had a bug with clustering analysis.:"
    else:
        comment = ""
    print("%-25s  %7.3f+/-%.3f -> %7.3f+/-%.3f, %7.3fx faster. %s" % (model+':', ave_alt_cluster[model], sd_alt_cluster[model], ave_new_cluster[model], sd_new_cluster[model], speed_up_cluster[model], comment) )
