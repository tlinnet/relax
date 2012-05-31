###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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
"""The base class for all the user function classes."""

# Python module imports.
from string import split
from textwrap import wrap

# relax module imports.
import ansi
import help
from relax_string import strip_lead
from status import Status; status = Status()


def bold_text(text):
    """Convert the text to bold.

    This is for use in the help system.

    @param text:    The text to make bold.
    @type text:     str
    @return:        The bold text.
    @rtype:         str
    """

    # Init.
    new_text = ''

    # Add the bold character to all characters.
    for i in range(len(text)):
        new_text += "%s\b%s" % (text[i], text[i])

    # Return the text.
    return new_text


def build_subtitle(text, bold=True):
    """Create the formatted subtitle string.

    @param text:        The name of the subtitle.
    @type text:         str
    @keyword colour:    A flag which if true will return bold text.  Otherwise an underlined title will be returned.
    @type colour:       bool
    @return:            The formatted subtitle.
    @rtype:             str
    """

    # Bold.
    if bold:
        new = "\n%s\n\n" % bold_text(text)

    # Underline.
    else:
        new = "\n%s\n%s\n\n" % (text, "~"*len(text))

    # Return the subtitle.
    return new


def format_text(text):
    """Format the line of text by wrapping.

    @param text:    The line of text to wrap.
    @type text:     str
    @return:        The wrapped text.
    @rtype:         str
    """

    # Then wrap each line.
    new_text = ""

    # Wrap the line.
    for wrapped_line in wrap(text, status.text_width):
        new_text += wrapped_line + "\n"

    # Return the formatted text.
    return new_text
