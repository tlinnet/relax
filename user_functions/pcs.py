###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""The pcs user function definitions."""

# Python module imports.
import wx

# relax module imports.
from generic_fns import align_tensor, pcs, pipes
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('pcs')
uf_class.title = "Class for handling pseudo-contact shifts."
uf_class.menu_text = "&pcs"
uf_class.gui_icon = "relax.align_tensor"


# The pcs.back_calc user function.
uf = uf_info.add_uf('pcs.back_calc')
uf.title = "Back calculate the pseudo-contact shifts."
uf.title_short = "PCS back calculation."
uf.display = True
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will back calculate the pseudo-contact shifts if the paramagnetic centre, temperature and magnetic field strength has been specified, an alignment tensor is present, and atomic positions have been loaded into the relax data store.")
uf.backend = pcs.back_calc
uf.menu_text = "&back_calc"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
uf.wizard_apply_button = False


# The pcs.calc_q_factors user function.
uf = uf_info.add_uf('pcs.calc_q_factors')
uf.title = "Calculate the PCS Q factor for the selected spins."
uf.title_short = "PCS Q factor calculation."
uf.display = True
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string for restricting to subset of all selected spins.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("For this to work, the back-calculated PCS data must first be generated by the analysis specific code.  Otherwise a warning will be given.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To calculate the PCS Q factor for only the spins '@H26', '@H27', and '@H28', type one of:")
uf.desc[-1].add_prompt("relax> pcs.calc_q_factors('@H26 & @H27 & @H28')")
uf.desc[-1].add_prompt("relax> pcs.calc_q_factors(spin_id='@H26 & @H27 & @H28')")
uf.backend = pcs.q_factors
uf.menu_text = "&calc_q_factors"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
uf.wizard_apply_button = False


# No backend!
## The pcs.copy user function.
#uf = uf_info.add_uf('pcs.copy')
#uf.title = "Copy PCS data from one data pipe to another."
#uf.title_short = "PCS copying."
#uf.add_keyarg(
#    name = "pipe_from",
#    py_type = "str",
#    desc_short = "source pipe",
#    desc = "The name of the pipe to copy the PCS data from.",
#    wiz_element_type = 'combo',
#    wiz_combo_iter = pipes.pipe_names,
#    can_be_none = True
#)
#uf.add_keyarg(
#    name = "pipe_to",
#    py_type = "str",
#    desc_short = "destination pipe",
#    desc = "The name of the pipe to copy the PCS data to.",
#    wiz_element_type = 'combo',
#    wiz_combo_iter = pipes.pipe_names,
#    can_be_none = True
#)
#uf.add_keyarg(
#    name = "align_id",
#    py_type = "str",
#    desc_short = "alignment ID string",
#    desc = "The alignment ID string.",
#    wiz_element_type = 'combo',
#    wiz_combo_iter = align_tensor.get_ids,
#    wiz_read_only = True,
#    can_be_none = True
#)
## Description.
#uf.desc.append(Desc_container())
#uf.desc[-1].add_paragraph("This function will copy PCS data from 'pipe_from' to 'pipe_to'.  If align_id is not given then all PCS data will be copied, otherwise only a specific data set will be.")
## Prompt examples.
#uf.desc.append(Desc_container("Prompt examples"))
#uf.desc[-1].add_paragraph("To copy all PCS data from pipe 'm1' to pipe 'm9', type one of:")
#uf.desc[-1].add_prompt("relax> pcs.copy('m1', 'm9')")
#uf.desc[-1].add_prompt("relax> pcs.copy(pipe_from='m1', pipe_to='m9')")
#uf.desc[-1].add_prompt("relax> pcs.copy('m1', 'm9', None)")
#uf.desc[-1].add_prompt("relax> pcs.copy(pipe_from='m1', pipe_to='m9', align_id=None)")
#uf.desc[-1].add_paragraph("To copy only the 'Th' PCS data from 'm3' to 'm6', type one of:")
#uf.desc[-1].add_prompt("relax> pcs.copy('m3', 'm6', 'Th')")
#uf.desc[-1].add_prompt("relax> pcs.copy(pipe_from='m3', pipe_to='m6', align_id='Th')")
#uf.backend = pcs.copy
#uf.menu_text = "cop&y"
#uf.gui_icon = "oxygen.actions.list-add"
#uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The pcs.corr_plot user function.
uf = uf_info.add_uf('pcs.corr_plot')
uf.title = "Generate a correlation plot of the measured vs. the back-calculated PCSs."
uf.title_short = "Correlation plot generation."
uf.add_keyarg(
    name = "format",
    default = "grace",
    py_type = "str",
    desc_short = "format",
    desc = "The format of the plot data.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["grace"],
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "file",
    default = "pcs_corr_plot.agr",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "Grace file name",
    desc = "The name of the Grace file to create.",
    wiz_filesel_wildcard = "Grace files (*.agr)|*.agr;*.AGR",
    wiz_filesel_style = wx.FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Two formats are currently supported.  If format is set to 'grace', then a Grace plot file will be created.  If the format is not set then a plain text list of the measured and back-calculated data will be created.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To create a Grace plot of the data, type:")
uf.desc[-1].add_prompt("relax> pcs.corr_plot()")
uf.desc[-1].add_paragraph("To create a plain text list of the measured and back-calculated data, type one of:")
uf.desc[-1].add_prompt("relax> pcs.corr_plot(None)")
uf.desc[-1].add_prompt("relax> pcs.corr_plot(format=None)")
uf.backend = pcs.corr_plot
uf.menu_text = "corr_&plot"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
uf.wizard_apply_button = False


# The pcs.delete user function.
uf = uf_info.add_uf('pcs.delete')
uf.title = "Delete the PCS data corresponding to the alignment ID."
uf.title_short = "PCS deletion."
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string of the data to delete.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will delete all PCS data associated with the alignment ID in the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To delete the PCS data corresponding to align_id='PH_gel', type:")
uf.desc[-1].add_prompt("relax> pcs.delete('PH_gel')")
uf.backend = pcs.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The pcs.display user function.
uf = uf_info.add_uf('pcs.display')
uf.title = "Display the PCS data corresponding to the alignment ID."
uf.title_short = "PCS data display."
uf.display = True
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "bc",
    default = False,
    py_type = "bool",
    desc_short = "back-calculation flag",
    desc = "A flag which if set will display the back-calculated rather than measured RDCs."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display all of the PCS data associated with the alignment ID in the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To display the 'phage' PCS data, type:")
uf.desc[-1].add_prompt("relax> pcs.display('phage')")
uf.backend = pcs.display
uf.menu_text = "di&splay"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The pcs.read user function.
uf = uf_info.add_uf('pcs.read')
uf.title = "Read the PCS data from file."
uf.title_short = "PCS data reading."
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the PCS data.",
    wiz_filesel_style = wx.FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin ID column",
    desc = "The spin ID string column (an alternative to the mol, res, and spin name and number columns).",
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "molecule name column",
    desc = "The molecule name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue number column",
    desc = "The residue number column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue name column",
    desc = "The residue name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin number column",
    desc = "The spin number column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin name column",
    desc = "The spin name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "data_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "data column",
    desc = "The PCS data column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "error_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "error column",
    desc = "The experimental error column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    arg_type = "free format",
    desc_short = "column separator",
    desc = "The column separator (the default is white space).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string to restrict the loading of data to certain spin subsets.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will read PCS data from a file and associate it with an alignment ID, either a new ID or a preexisting one with no PCS data.")
uf.desc[-1].add_paragraph("The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number and name, and spin number and name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will read the PCS data out of the file 'Tb.txt' where the columns are separated by the symbol ',', and store the PCSs under the ID 'Tb'.")
uf.desc[-1].add_prompt("relax> pcs.read('Tb', 'Tb.txt', sep=',')")
uf.desc[-1].add_paragraph("To read the 15N and 1H PCSs from the file 'Eu.txt', where the 15N values are in the 4th column and the 1H in the 9th, type both the following:")
uf.desc[-1].add_prompt("relax> pcs.read('Tb', 'Tb.txt', spin_id='@N', res_num_col=1, data_col=4)")
uf.desc[-1].add_prompt("relax> pcs.read('Tb', 'Tb.txt', spin_id='@H', res_num_col=1, data_col=9)")
uf.backend = pcs.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The pcs.weight user function.
uf = uf_info.add_uf('pcs.weight')
uf.title = "Set optimisation weights on the PCS data."
uf.title_short = "PCS weighting."
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string."
)
uf.add_keyarg(
    name = "weight",
    default = 1.0,
    py_type = "num",
    desc_short = "weight",
    desc = "The weighting value."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This can be used to force the PCS to contribute more or less to the chi-squared optimisation statistic.  The higher the value, the more importance the PCS will have.")
uf.backend = pcs.weight
uf.menu_text = "wei&ght"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'


# The pcs.write user function.
uf = uf_info.add_uf('pcs.write')
uf.title = "Write the PCS data to file."
uf.title_short = "PCS data writing."
uf.add_keyarg(
    name = "align_id",
    py_type = "str",
    desc_short = "alignment ID string",
    desc = "The alignment ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = align_tensor.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_style = wx.FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "bc",
    default = False,
    py_type = "bool",
    desc_short = "back-calculation flag",
    desc = "A flag which if set will write out the back-calculated rather than measured RDCs."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("If no directory name is given, the file will be placed in the current working directory.  The alignment ID is required for selecting which PCS data set will be written to file.")
uf.backend = pcs.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
