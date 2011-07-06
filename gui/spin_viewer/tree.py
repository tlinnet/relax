###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
"""The molecule, residue, and spin tree view GUI elements."""


# Python module imports.
import wx

# relax module imports.
from generic_fns.selection import is_mol_selected, is_res_selected, is_spin_selected
from generic_fns.mol_res_spin import get_molecule_ids, get_residue_ids, get_spin_ids, molecule_loop, residue_loop, spin_loop
from generic_fns.pipes import get_pipe

# GUI module imports.
from gui import paths
from gui.message import question
from gui.misc import gui_to_str


class Mol_res_spin_tree(wx.Window):
    """The tree view class."""

    def __init__(self, gui, parent=None, id=None):
        """Set up the tree GUI element.

        @param gui:         The gui object.
        @type gui:          wx object
        @keyword parent:    The parent GUI element that this is to be attached to.
        @type parent:       wx object
        @keyword id:        The ID number.
        @type id:           int
        """

        # Store the args.
        self.gui = gui

        # Execute the base class method.
        wx.Window.__init__(self, parent, id, style=wx.WANTS_CHARS)

        # Some default values.
        self.icon_size = 22

        # The tree.
        self.tree = wx.TreeCtrl(parent=self, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE)

        # A tracking structure for the tree IDs.
        self.tree_ids = {}

        # Resize the tree element.
        self.Bind(wx.EVT_SIZE, self._resize)

        # The tree roots.
        self.root = self.tree.AddRoot("Spin system information")
        self.tree.SetPyData(self.root, "root")

        # Build the icon list.
        icon_list = wx.ImageList(self.icon_size, self.icon_size)

        # The normal icons.
        self.icon_mol_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule, wx.BITMAP_TYPE_ANY))
        self.icon_mol_unfold_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule_unfolded, wx.BITMAP_TYPE_ANY))
        self.icon_res_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.residue, wx.BITMAP_TYPE_ANY))
        self.icon_spin_index = icon_list.Add(wx.Bitmap(paths.icon_22x22.spin, wx.BITMAP_TYPE_ANY))

        # The deselected icons.
        self.icon_mol_index_desel = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule_grey, wx.BITMAP_TYPE_ANY))
        self.icon_mol_unfold_index_desel = icon_list.Add(wx.Bitmap(paths.icon_22x22.molecule_unfolded_grey, wx.BITMAP_TYPE_ANY))
        self.icon_res_index_desel = icon_list.Add(wx.Bitmap(paths.icon_22x22.residue_grey, wx.BITMAP_TYPE_ANY))
        self.icon_spin_index_desel = icon_list.Add(wx.Bitmap(paths.icon_22x22.spin_grey, wx.BITMAP_TYPE_ANY))

        # Set the icon list.
        self.tree.SetImageList(icon_list)

        # Some weird black magic (this is essential)!!
        self.icon_list = icon_list

        # Populate the tree.
        self.update()

        # Catch mouse events.
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._selection)
        self.tree.Bind(wx.EVT_RIGHT_DOWN, self._right_click)


    def _resize(self, event):
        """Resize the tree element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The panel dimensions.
        width, height = self.GetClientSizeTuple()

        # Set the tree dimensions.
        self.tree.SetDimensions(0, 0, width, height)


    def _right_click(self, event):
        """Handle right clicks in the tree.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Obtain the position.
        pos = event.GetPosition()

        # Find the item clicked on.
        item, flags = self.tree.HitTest(pos)

        # The python data.
        self.info = self.tree.GetItemPyData(item)

        # Bring up the root menu.
        if self.info == 'root':
            self.menu_root()

        # Bring up the molecule menu.
        elif self.info['type'] == 'mol':
            self.menu_molecule()

        # Bring up the residue menu.
        elif self.info['type'] == 'res':
            self.menu_residue()

        # Bring up the spin menu.
        elif self.info['type'] == 'spin':
            self.menu_spin()


    def _selection(self, event):
        """Handle changes in selection in the tree.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Find the item clicked on.
        item = event.GetItem()

        # The python data.
        info = self.tree.GetItemPyData(item)

        # Display the container.
        self.gui.spin_viewer.container.display(info)


    def create_residue(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Call the dialog.
        self.gui.user_functions.residue.create(event, mol_name=self.info['mol_name'])


    def create_spin(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Call the dialog.
        self.gui.user_functions.spin.create(event, mol_name=self.info['mol_name'], res_num=self.info['res_num'], res_name=self.info['res_name'])


    def delete_molecule(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to delete this molecule?  This operation cannot be undone."
        if not question(msg, default=False):
            return

        # Delete the molecule.
        self.gui.user_functions.interpreter.molecule.delete(gui_to_str(self.info['id']))

        # Update.
        self.update()


    def delete_residue(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to delete this residue?  This operation cannot be undone."
        if not question(msg, default=False):
            return

        # Delete the residue.
        self.gui.user_functions.interpreter.residue.delete(gui_to_str(self.info['id']))

        # Update.
        self.update()


    def delete_spin(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to delete this spin?  This operation cannot be undone."
        if not question(msg, default=False):
            return

        # Delete the spin.
        self.gui.user_functions.interpreter.spin.delete(gui_to_str(self.info['id']))

        # Update.
        self.update()


    def deselect_molecule(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to deselect all spins of this molecule?"
        if not question(msg, default=False):
            return

        # Deselect the molecule.
        self.gui.user_functions.interpreter.deselect.spin(spin_id=gui_to_str(self.info['id']), change_all=False)

        # Update.
        self.update()


    def deselect_residue(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to deselect all spins of this residue?"
        if not question(msg, default=False):
            return

        # Deselect the residue.
        self.gui.user_functions.interpreter.deselect.spin(spin_id=gui_to_str(self.info['id']), change_all=False)

        # Update.
        self.update()


    def deselect_spin(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Deselect the spin.
        self.gui.user_functions.interpreter.deselect.spin(spin_id=gui_to_str(self.info['id']), change_all=False)

        # Update.
        self.update()


    def info(self):
        """Get the python data structure associated with the current item.

        @return:    The dictionary of data.
        @rtype:     dict
        """

        # Return the python data.
        return self.tree.GetItemPyData(item)


    def menu_molecule(self):
        """The right click molecule menu."""

        # Some ids.
        ids = []
        for i in range(3):
            ids.append(wx.NewId())

        # The menu.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[0], text="Add residue", icon=paths.icon_16x16.add))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[1], text="Delete molecule", icon=paths.icon_16x16.remove))

        # Selection or deselection.
        if self.info['select']:
            menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[2], text="Deselect"))
        else:
            menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[2], text="Select"))

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.create_residue, id=ids[0])
        self.Bind(wx.EVT_MENU, self.delete_molecule, id=ids[1])
        if self.info['select']:
            self.Bind(wx.EVT_MENU, self.deselect_molecule, id=ids[2])
        else:
            self.Bind(wx.EVT_MENU, self.select_molecule, id=ids[2])

        # Show the menu.
        self.PopupMenu(menu)
        menu.Destroy()


    def menu_residue(self):
        """The right click molecule menu."""

        # Some ids.
        ids = []
        for i in range(3):
            ids.append(wx.NewId())

        # The menu.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[0], text="Add spin", icon=paths.icon_16x16.add))
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[1], text="Delete residue", icon=paths.icon_16x16.remove))

        # Selection or deselection.
        if self.info['select']:
            menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[2], text="Deselect"))
        else:
            menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[2], text="Select"))

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.create_spin, id=ids[0])
        self.Bind(wx.EVT_MENU, self.delete_residue, id=ids[1])
        if self.info['select']:
            self.Bind(wx.EVT_MENU, self.deselect_residue, id=ids[2])
        else:
            self.Bind(wx.EVT_MENU, self.select_residue, id=ids[2])

        # Show the menu.
        self.PopupMenu(menu)
        menu.Destroy()


    def menu_root(self):
        """The right click root menu."""

        # Some ids.
        ids = []
        for i in range(1):
            ids.append(wx.NewId())

        # The menu.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[0], text="Add molecule", icon=paths.icon_16x16.add))

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.gui.user_functions.molecule.create, id=ids[0])

        # Show the menu.
        self.PopupMenu(menu)
        menu.Destroy()


    def menu_spin(self):
        """The right click spin menu."""

        # Some ids.
        ids = []
        for i in range(2):
            ids.append(wx.NewId())

        # The menu.
        menu = wx.Menu()
        menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[0], text="Delete spin", icon=paths.icon_16x16.remove))

        # Selection or deselection.
        if self.info['select']:
            menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[1], text="Deselect"))
        else:
            menu.AppendItem(self.gui.menu.build_menu_item(menu, id=ids[1], text="Select"))

        # The menu actions.
        self.Bind(wx.EVT_MENU, self.delete_spin, id=ids[0])
        if self.info['select']:
            self.Bind(wx.EVT_MENU, self.deselect_spin, id=ids[1])
        else:
            self.Bind(wx.EVT_MENU, self.select_spin, id=ids[1])

        # Show the menu.
        self.PopupMenu(menu)
        menu.Destroy()


    def prune_mol(self):
        """Remove any molecules which have been deleted."""

        # Get a list of molecule IDs from the relax data store.
        mol_ids = get_molecule_ids()

        # Find if the molecule has been removed.
        prune_list = []
        for key in self.tree_ids.keys():
            # Get the python data.
            info = self.tree.GetItemPyData(key)

            # Prune if it has been removed.
            if info['id'] not in mol_ids:
                self.tree.Delete(key)
                self.tree_ids.pop(key)


    def prune_res(self, mol_branch_id, mol_id):
        """Remove any molecules which have been deleted.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @param mol_id:          The molecule identification string.
        @type mol_id:           str
        """

        # Get a list of residue IDs from the relax data store.
        res_ids = get_residue_ids(mol_id)

        # Find if the molecule has been removed.
        prune_list = []
        for key in self.tree_ids[mol_branch_id].keys():
            # Get the python data.
            info = self.tree.GetItemPyData(key)

            # Prune if it has been removed.
            if info['id'] not in res_ids:
                self.tree.Delete(key)
                self.tree_ids[mol_branch_id].pop(key)


    def prune_spin(self, mol_branch_id, res_branch_id, res_id):
        """Remove any spins which have been deleted.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @param res_branch_id:   The residue branch ID of the wx.TreeCtrl object.
        @type res_branch_id:    TreeItemId
        @param res_id:          The residue identification string.
        @type res_id:           str
        """

        # Get a list of spin IDs from the relax data store.
        spin_ids = get_spin_ids(res_id)

        # Find if the molecule has been removed.
        prune_list = []
        for key in self.tree_ids[mol_branch_id][res_branch_id].keys():
            # Get the python data.
            info = self.tree.GetItemPyData(key)

            # Prune if it has been removed.
            if info['id'] not in spin_ids:
                self.tree.Delete(key)
                self.tree_ids[mol_branch_id][res_branch_id].pop(key)


    def select_molecule(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to select all spins of this molecule?"
        if not question(msg, default=False):
            return

        # Select the molecule.
        self.gui.user_functions.interpreter.select.spin(spin_id=gui_to_str(self.info['id']), change_all=False)

        # Update.
        self.update()


    def select_residue(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if this should be done.
        msg = "Are you sure you would like to select all spins of this residue?"
        if not question(msg, default=False):
            return

        # Select the residue.
        self.gui.user_functions.interpreter.select.spin(spin_id=gui_to_str(self.info['id']), change_all=False)

        # Update.
        self.update()


    def select_spin(self, event):
        """Wrapper method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Select the spin.
        self.gui.user_functions.interpreter.select.spin(spin_id=gui_to_str(self.info['id']), change_all=False)

        # Update.
        self.update()


    def set_bitmap_mol(self, mol_branch_id, select=True):
        """Set the molecule bitmaps.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @keyword select:        The selection flag.
        @type select:           bool
        """

        # The bitmaps for the selected state.
        if select:
            bmp = self.icon_mol_index
            bmp_unfold = self.icon_mol_unfold_index

        # The bitmaps for the deselected state.
        else:
            bmp = self.icon_mol_index_desel
            bmp_unfold = self.icon_mol_unfold_index_desel

        # Set the image.
        self.tree.SetItemImage(mol_branch_id, bmp, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(mol_branch_id, bmp_unfold, wx.TreeItemIcon_Expanded)


    def set_bitmap_res(self, res_branch_id, select=True):
        """Set the residue bitmaps.

        @param res_branch_id:   The residue branch ID of the wx.TreeCtrl object.
        @type res_branch_id:    TreeItemId
        @keyword select:        The selection flag.
        @type select:           bool
        """

        # The bitmaps for the selected state.
        if select:
            bmp = self.icon_res_index

        # The bitmaps for the deselected state.
        else:
            bmp = self.icon_res_index_desel

        # Set the image.
        self.tree.SetItemImage(res_branch_id, bmp, wx.TreeItemIcon_Normal & wx.TreeItemIcon_Expanded)


    def set_bitmap_spin(self, spin_branch_id, select=True):
        """Set the spin bitmaps.

        @param spin_branch_id:  The spin branch ID of the wx.TreeCtrl object.
        @type spin_branch_id:   TreeItemId
        @keyword select:        The selection flag.
        @type select:           bool
        """

        # The bitmaps for the selected state.
        if select:
            bmp = self.icon_spin_index

        # The bitmaps for the deselected state.
        else:
            bmp = self.icon_spin_index_desel

        # Set the image.
        self.tree.SetItemImage(spin_branch_id, bmp, wx.TreeItemIcon_Normal & wx.TreeItemIcon_Expanded)


    def update(self, pipe_name=None):
        """Update the tree view using the given data pipe."""

        # The data pipe.
        if not pipe_name:
            pipe = cdp
        else:
            pipe = get_pipe(pipe_name)

        # No data pipe, so delete everything and return.
        if not pipe:
            self.tree.DeleteChildren(self.root)
            return

        # Update the molecules.
        for mol, mol_id in molecule_loop(return_id=True):
            self.update_mol(mol, mol_id)

        # Remove any deleted molecules.
        self.prune_mol()


    def update_mol(self, mol, mol_id):
        """Update the given molecule in the tree.

        @param mol:     The molecule container.
        @type mol:      MoleculeContainer instance
        @param mol_id:  The molecule identification string.
        @type mol_id:   str
        """

        # Find the molecule, if it already exists.
        new_mol = True
        for key in self.tree_ids.keys():
            # Get the python data.
            data = self.tree.GetItemPyData(key)

            # Check the mol_id for a match and, if so, terminate to speed things up.
            if mol_id == data['id']:
                new_mol = False
                mol_branch_id = key
                break

        # A new molecule.
        if new_mol:
            # Append a molecule with name to the tree.
            mol_branch_id = self.tree.AppendItem(self.root, "Molecule: %s" % mol.name)

            # The data to store.
            data = {
                'type': 'mol',
                'mol_name': mol.name,
                'id': mol_id,
                'select': is_mol_selected(mol_id)
            }
            self.tree.SetPyData(mol_branch_id, data)

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id] = {}

            # Set the bitmap.
            self.set_bitmap_mol(mol_branch_id, select=data['select'])

        # An old molecule.
        else:
            # Check the selection state.
            select = is_mol_selected(data['id'])

            # Change of state.
            if select != data['select']:
                # Store the new state.
                data['select'] = select

                # Set the bitmap.
                self.set_bitmap_mol(mol_branch_id, select=data['select'])

        # Update the residues of this molecule.
        for res, res_id in residue_loop(mol_id, return_id=True):
            self.update_res(mol_branch_id, mol, res, res_id)

        # Start new molecules expanded.
        if new_mol:
            self.tree.Expand(mol_branch_id)

        # Remove any deleted residues.
        self.prune_res(mol_branch_id, mol_id)

        # Expand the root.
        self.tree.Expand(self.root)


    def update_res(self, mol_branch_id, mol, res, res_id):
        """Update the given residue in the tree.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @param mol:             The molecule container.
        @type mol:              MoleculeContainer instance
        @param res:             The residue container.
        @type res:              ResidueContainer instance
        @param res_id:          The residue identification string.
        @type res_id:           str
        """

        # Find the residue, if it already exists.
        new_res = True
        for key in self.tree_ids[mol_branch_id].keys():
            # Get the python data.
            data = self.tree.GetItemPyData(key)

            # Check the res_id for a match and, if so, terminate to speed things up.
            if res_id == data['id']:
                new_res = False
                res_branch_id = key
                break

        # A new residue.
        if new_res:
            # Append a residue with name and number to the tree.
            res_branch_id = self.tree.AppendItem(mol_branch_id, "Residue: %s %s" % (res.num, res.name))

            # The data to store.
            data = {
                'type': 'res',
                'mol_name': mol.name,
                'res_name': res.name,
                'res_num': res.num,
                'id': res_id,
                'select': is_res_selected(res_id)
            }
            self.tree.SetPyData(res_branch_id, data)

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id][res_branch_id] = {}

            # Set the bitmap.
            self.set_bitmap_res(res_branch_id, select=data['select'])

        # An old residue.
        else:
            # Check the selection state.
            select = is_res_selected(data['id'])

            # Change of state.
            if select != data['select']:
                # Store the new state.
                data['select'] = select

                # Set the bitmap.
                self.set_bitmap_res(res_branch_id, select=data['select'])

        # Update the spins of this residue.
        for spin, spin_id in spin_loop(res_id, return_id=True):
            self.update_spin(mol_branch_id, res_branch_id, mol, res, spin, spin_id)

        # Start new residues expanded.
        if new_res:
            self.tree.Expand(res_branch_id)

        # Remove any deleted spins.
        self.prune_spin(mol_branch_id, res_branch_id, res_id)


    def update_spin(self, mol_branch_id, res_branch_id, mol, res, spin, spin_id):
        """Update the given spin in the tree.

        @param mol_branch_id:   The molecule branch ID of the wx.TreeCtrl object.
        @type mol_branch_id:    TreeItemId
        @param res_branch_id:   The residue branch ID of the wx.TreeCtrl object.
        @type res_branch_id:    TreeItemId
        @param mol:             The molecule container.
        @type mol:              MoleculeContainer instance
        @param res:             The residue container.
        @type res:              ResidueContainer instance
        @param spin:            The spin container.
        @type spin:             SpinContainer instance
        @param spin_id:         The spin identification string.
        @type spin_id:          str
        """

        # Find the spin, if it already exists.
        new_spin = True
        for key in self.tree_ids[mol_branch_id][res_branch_id].keys():
            # Get the python data.
            data = self.tree.GetItemPyData(key)

            # Check the spin_id for a match and, if so, terminate to speed things up.
            if spin_id == data['id']:
                new_spin = False
                spin_branch_id = key
                break

        # A new spin.
        if new_spin:
            # Append a spin with name and number to the tree.
            spin_branch_id = self.tree.AppendItem(res_branch_id, "Spin: %s %s" % (spin.num, spin.name))

            # The data to store.
            data = {
                'type': 'spin',
                'mol_name': mol.name,
                'res_name': res.name,
                'res_num': res.num,
                'spin_name': spin.name,
                'spin_num': spin.num,
                'id': spin_id,
                'select': is_spin_selected(spin_id)
            }
            self.tree.SetPyData(spin_branch_id, data)

            # Add the id to the tracking structure.
            self.tree_ids[mol_branch_id][res_branch_id][spin_branch_id] = True

            # Set the bitmap.
            self.set_bitmap_spin(spin_branch_id, select=data['select'])

        # An old spin.
        else:
            # Check the selection state.
            select = is_spin_selected(data['id'])

            # Change of state.
            if select != data['select']:
                # Store the new state.
                data['select'] = select

                # Set the bitmap.
                self.set_bitmap_spin(spin_branch_id, select=data['select'])

        # Start new spins expanded.
        if new_spin:
            self.tree.Expand(spin_branch_id)
