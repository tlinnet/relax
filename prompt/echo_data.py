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


import help


class Echo_data:
    def __init__(self, relax):
        """Functions for printing data to standard out."""

        # Place relax in the class namespace.
        self.relax = relax

        # Help.
        self.__relax_help__ = help.relax_class_help


    def echo(self, *args):
        """Function to print the names of all data structures in self.relax.data

        With no arguments, the names of all data structures in self.relax.data are printed along
        with the data type.
        """

        self.args = args

        # Print the names of all data structures in self.relax.data if no arguments are given.
        if len(self.args) == 0:
            print dir(self.relax.data)
            return

        for struct in args:
            # Test if the data structure exists.
            try:
                getattr(self.relax.data, struct)
            except AttributeError:
                print "Data structure 'self.relax.data." + struct + "' does not exist."
                continue

            print `getattr(self.relax.data, struct)`


    def print_data(self, data, seq_flag=0):
        """Function to print data according to the argument list given."""

        if seq_flag:
            print "%-5s%-5s" % ("num", "name")
        else:
            print "%-5s%-5s%-20s%-20s" % ("num", "name", "data", "errors")

        for index in self.indecies:
            if seq_flag:
                print "%-5i%-5s" % (data[index][0], data[index][1])
            else:
                print "%-5i%-5s%-20e%-20e" % (data[index][0], data[index][1], data[index][2], data[index][3])
