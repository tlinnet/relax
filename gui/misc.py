###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Miscellaneous functions used throughout the GUI."""

# Python module imports.
from math import pow
from string import split
import wx


def add_border(parent, border=0, packing=wx.VERTICAL):
    """Create the main part of the frame, returning the central sizer.

    @param parent:      The parent GUI element to pack the box into.
    @type parent:       wx object
    @keyword border:    The size of the border in pixels.
    @type border:       int
    @keyword packing:   Specify if the central sizer should be vertically or horizontally packed.
    @type packing:      wx.VERTICAL or wx.HORIZONTAL
    @return:            The central sizer.
    @rtype:             wx.BoxSizer instance
    """

    # Some sizers.
    sizer_hori = wx.BoxSizer(wx.HORIZONTAL)
    sizer_vert = wx.BoxSizer(wx.VERTICAL)
    sizer_cent = wx.BoxSizer(packing)

    # Pack the sizer into the frame.
    parent.SetSizer(sizer_hori)

    # Left and right borders.
    sizer_hori.AddSpacer(border)
    sizer_hori.Add(sizer_vert, 1, wx.EXPAND|wx.ALL)
    sizer_hori.AddSpacer(border)

    # Top and bottom borders.
    sizer_vert.AddSpacer(border)
    sizer_vert.Add(sizer_cent, 1, wx.EXPAND|wx.ALL)
    sizer_vert.AddSpacer(border)

    # Return the central sizer.
    return sizer_cent


def convert_to_float(string):
    """Method to convert a string like '1.02*1e-10' to a float variable.

    @param string:  The number in string form.
    @type string:   str
    @return:        The floating point number.
    @rtype:         float
    """

    # Break the number up.
    entries = split('*')

    # The first part of the number.
    a = entries[0]
    a = float(a)

    # The second part of the number.
    b = entries[1]
    b = float(b[2:len(b)])

    # Recombine.
    result = a * pow(10, b)

    # Return the float.
    return result


def gui_to_float(string):
    """Convert the GUI obtained string to an float.

    @param string:  The number in string form.
    @type string:   str
    @return:        The float
    @rtype:         float or None
    """

    # No input.
    if string == '':
        return None

    # Convert.
    return float(string)


def gui_to_int(string):
    """Convert the GUI obtained string to an int.

    @param string:  The number in string form.
    @type string:   str
    @return:        The integer
    @rtype:         int or None
    """

    # No input.
    if string == '':
        return None

    # Convert.
    return int(string)


def int_to_gui(num):
    """Convert the int into the GUI string.

    @param num:     The number in int or None form.
    @type num:      int or None
    @return:        The GUI string.
    @rtype:         str
    """

    # No input.
    if num == None:
        num = ''

    # Convert.
    return unicode(num)


def gui_to_str(string):
    """Convert the GUI obtained string to a string.

    @param string:  The number in string form.
    @type string:   str
    @return:        The string.
    @rtype:         str
    """

    # No value.
    if string == '':
        return None

    # Convert.
    return str(string)


def str_to_gui(string):
    """Convert the string into the GUI string.

    @param num:     The number in int or None form.
    @type num:      int or None
    @return:        The GUI string.
    @rtype:         str
    """

    # No input.
    if string == None:
        string = ''

    # Convert.
    return unicode(string)
