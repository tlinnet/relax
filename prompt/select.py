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

import sys

import message


class Shell:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the main class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the main class data structures
        are accessible.  For more flexibility use the main class directly.
        """

        # Load the main class into the namespace of this __init__ function.
        x = Main(relax)

        # Place references to the interactive functions within the namespace of this class.
        self.all = x.all
        self.res = x.res
        self.reverse = x.reverse

        # __repr__.
        self.__repr__ = message.main_class


class Main:
    def __init__(self, relax):
        """Class containing the functions for selecting residues."""

        self.relax = relax


    def all(self):
        """Function for selecting all residues.

        Examples
        ~~~~~~~~

        To select all residues type:

        relax> select.all()
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "select.all()"
            print text

        # Execture the functional code.
        self.relax.generic.selection.sel_all()


    def res(self, num=None, name=None, change_all=0):
        """Function for selecting specific residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        num:  The residue number.

        name:  The residue name.

        change_all:  A flag specifying if all other residues should be changed.


        Description
        ~~~~~~~~~~~

        The residue number can be either an integer for selecting a single residue or a python
        regular expression, in string form, for selecting multiple residues.  For details about
        using regular expression, see the python documentation for the module 're'.

        The residue name argument must be a string.  Regular expression is also allowed.

        The 'change_all' flag argument default is zero meaning that all residues currently either
        selected or unselected will remain that way.  Setting the argument to 1 will cause all
        residues not specified by 'num' or 'name' to become unselected.
        

        Examples
        ~~~~~~~~

        To select only glycines and alanines, assuming they have been loaded with the names GLY and
        ALA, type:

        relax> select.res(name='GLY|ALA', change_all=1)
        relax> select.res(name='[GA]L[YA]', change_all=1)

        To select residue 5 CYS in addition to the currently selected residues, type:

        relax> select.res(5)
        relax> select.res(5, 'CYS')
        relax> select.res('5')
        relax> select.res('5', 'CYS')
        relax> select.res(num='5', name='CYS')
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "select.res("
            text = text + "num=" + `num`
            text = text + ", name=" + `name`
            text = text + ", change_all=" + `change_all` + ")"
            print text

        # Residue number.
        if num != None and type(num) != int and type(num) != str:
            raise RelaxNoneIntStrError, ('residue number', num)

        # Residue name.
        if name != None and type(name) != str:
            raise RelaxNoneStrError, ('residue name', name)

        # Neither are given.
        if num == None and name == None:
            raise RelaxError, "At least one of the number or name arguments is required."

        # Change all flag.
        if type(change_all) != int or (change_all != 0 and change_all != 1):
            raise RelaxBinError, ('change_all', change_all)

        # Execture the functional code.
        self.relax.generic.selection.sel_res(num=num, name=name, change_all=change_all)


    def reverse(self):
        """Function for the reversal of the residue selection.

        Examples
        ~~~~~~~~

        To unselect all currently selected residues and select those which are unselected type:

        relax> select.reverse()
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "select.reverse()"
            print text

        # Execture the functional code.
        self.relax.generic.selection.reverse()
