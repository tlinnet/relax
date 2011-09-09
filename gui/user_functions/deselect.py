###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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

# Module docstring.
"""The deselect user function GUI elements."""

# Python module imports.
import wx

# relax module imports.
from prompt.select import boolean_doc

# GUI module imports.
from base import UF_base, UF_page
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.misc import gui_to_bool, gui_to_int, gui_to_str, str_to_gui


# The container class.
class Deselect(UF_base):
    """The container class for holding all GUI elements."""

    def all(self, event):
        """The deselect.all user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = self.create_wizard(size_x=600, size_y=300, name='deselect.all', uf_page=All_page, apply_button=False)
        wizard.run()


    def read(self, event):
        """The deselect.read user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = self.create_wizard(size_x=900, size_y=700, name='deselect.read', uf_page=Read_page)
        wizard.run()


    def reverse(self, event):
        """The deselect.reverse user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = self.create_wizard(size_x=700, size_y=400, name='deselect.reverse', uf_page=Reverse_page, apply_button=False)
        wizard.run()


    def spin(self, event):
        """The deselect.spin user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = self.create_wizard(size_x=700, size_y=500, name='deselect.spin', uf_page=Spin_page)
        wizard.run()




class All_page(UF_page):
    """The deselect.all() user function page."""

    # Some class variables.
    uf_path = ['deselect', 'all']

    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Deselect all.
        interpreter.queue('deselect.all')



class Read_page(UF_page):
    """The deselect.read() user function page."""

    # Some class variables.
    uf_path = ['deselect', 'read']
    height_desc = 200

    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The deselection file:", message="Deselection file selection", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict data loading to certain spins:")

        # The boolean operator specifying how spins should be deselected.
        self.boolean = self.combo_box(sizer, "Boolean operator:", choices=['OR', 'NOR', 'AND', 'NAND', 'XOR', 'XNOR'], tooltip=boolean_doc[2])
        self.boolean.SetValue(str_to_gui('OR'))

        # The change_all flag.
        self.change_all = self.boolean_selector(sizer, "Change all:", tooltip=self.uf._doc_args_dict['change_all'], default=False)

        # The parameter file settings.
        self.free_file_format(sizer, data_cols=False, padding=3, spacer=0)


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # Get the column numbers.
        spin_id_col =   gui_to_int(self.spin_id_col.GetValue())
        mol_name_col =  gui_to_int(self.mol_name_col.GetValue())
        res_num_col =   gui_to_int(self.res_num_col.GetValue())
        res_name_col =  gui_to_int(self.res_name_col.GetValue())
        spin_num_col =  gui_to_int(self.spin_num_col.GetValue())
        spin_name_col = gui_to_int(self.spin_name_col.GetValue())

        # The column separator.
        sep = str(self.sep.GetValue())
        if sep == 'white space':
            sep = None

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # The boolean operator and change_all flag.
        boolean = gui_to_str(self.boolean.GetValue())
        change_all = gui_to_bool(self.change_all.GetValue())

        # Deselection.
        interpreter.queue('deselect.read', file, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id, boolean=boolean, change_all=change_all)



class Reverse_page(UF_page):
    """The deselect.reverse() user function page."""

    # Some class variables.
    uf_path = ['deselect', 'reverse']

    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer)


    def on_execute(self):
        """Execute the user function."""

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Deselect all.
        interpreter.queue('deselect.reverse', spin_id=spin_id)



class Spin_page(UF_page):
    """The deselect.spin() user function page."""

    # Some class variables.
    uf_path = ['deselect', 'spin']

    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer)

        # The change_all flag.
        self.change_all = self.boolean_selector(sizer, "Change all:", tooltip=self.uf._doc_args_dict['change_all'])


    def on_execute(self):
        """Execute the user function."""

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # The change_all flag.
        change_all = gui_to_bool(self.change_all.GetValue())

        # Deselect all.
        interpreter.queue('deselect.spin', spin_id=spin_id, change_all=change_all)
