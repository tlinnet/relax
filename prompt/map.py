###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from Numeric import zeros
from re import match
import sys
from types import FunctionType


class Map:
    def __init__(self, relax):
        """Space mapper."""

        self.relax = relax


    def map(self, run=None, res_num=None, map_type="Iso3D", inc=20, lower=None, upper=None, swap=None, file="map", dir="dx", point=None, point_file="point", remap=None, labels=None):
        """Function for creating a map of the given space in OpenDX format.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        res_num:  Specification of the residue by number.

        map_type:  The type of map to create.  For example the default, a 3D isosurface, the type is
        "Iso3D".  See below for more details.

        inc:  The number of increments to map in each dimension.  This value controls the resolution
        of the map.

        lower:  The lower bounds of the space.  If you wish to change the lower bounds of the map
        then supply an array of length equal to the number of parameters in the model.  A lower
        bound for each parameter must be supplied.  If nothing is supplied then the defaults will
        be used.

        upper:  The upper bounds of the space.  If you wish to change the upper bounds of the map
        then supply an array of length equal to the number of parameters in the model.  A upper
        bound for each parameter must be supplied.  If nothing is supplied then the defaults will
        be used.

        swap:  An array used to swap the position of the axes.  The length of the array should be
        the same as the number of parameters in the model.  The values should be integers specifying
        which elements to interchange.  For example if swap equals [0, 1, 2] for a three parameter
        model then the axes are not interchanged whereas if swap equals [1, 0, 2] then the first and
        second dimensions are interchanged.

        file:  The file name.  All the output files are prefixed with this name.  The main file
        containing the data points will be called the value of 'file'.  The OpenDX program will be
        called 'file.net' and the OpenDX import file will be called 'file.general'.

        dir:  The directory to output files to.  Set this to 'None' if you do not want the files to
        be placed in subdirectory.  If the directory does not exist, it will be created.

        point:  An array of parameter values where a point in the map, shown as a red sphere, will
        be placed.  The length must be equal to the number of parameters.

        point_file:  The name of that the point output files will be prefixed with.

        remap:  A user supplied remapping function.  This function will receive the parameter array
        and must return an array of equal length.

        labels:  The axis labels.  If supplied this argument should be an array of strings of length
        equal to the number of parameters.


        Map type
        ~~~~~~~~

        The map type can be changed by supplying the 'map_type' keyword argument.  Here is a list of
        currently supported map types:
        _____________________________________________________________________________
        |                                           |                               |
        | Surface type                              | Pattern                       |
        |-------------------------------------------|-------------------------------|
        |                                           |                               |
        | 3D isosurface                             | '^[Ii]so3[Dd]'                |
        |-------------------------------------------|-------------------------------|

        Pattern syntax is simply regular expression syntax where square brackets [] means any
        character within the brackets, ^ means the start of the string, etc.


        Examples
        ~~~~~~~~

        The following commands will generate a map of the extended model-free space defined as run
        'm5' which consists of the parameters {S2f, S2s, ts}.  Files will be output into the
        directory 'dx' and will be prefixed by 'map'.

        relax> map('m5')
        relax> map('m5', 20, "map", "dx")
        relax> map('m5', file="map", dir="dx")
        relax> map(run='m5', inc=20, file="map", dir="dx")
        relax> map(run='m5', type="Iso3D", inc=20, swap=[0, 1, 2], file="map", dir="dx")


        The following commands will swap the S2s and ts axes of this map.

        relax> map('m5', swap=[0, 2, 1])
        relax> map(run='m5', type="Iso3D", inc=20, swap=[0, 2, 1], file="map", dir="dx")


        To map the model-free space 'm4' defined by the parameters {S2, te, Rex}, name the results
        'test', and not place the files in a subdirectory, use the following commands.

        relax> map('m4', file='test', dir=None)
        relax> map(run='m4', inc=100, file='test', dir=None)
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "map("
            text = text + "run=" + `run`
            text = text + ", res_num=" + `res_num`
            text = text + ", map_type=" + `map_type`
            text = text + ", inc=" + `inc`
            text = text + ", lower=" + `lower`
            text = text + ", upper=" + `upper`
            text = text + ", swap=" + `swap`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", point=" + `point`
            text = text + ", point_file=" + `point_file`
            text = text + ", remap=" + `remap`
            text = text + ", labels=" + `labels` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise UserArgStrError, ('run', run)

        # The residue number.
        if type(res_num) != int:
            raise UserArgIntError, ('residue number', res_num)

        # Residue index.
        index = None
        for i in range(len(self.relax.data.res)):
            if self.relax.data.res[i].num == res_num:
                index = i
                break
        if index == None:
            raise UserNoResError, res_num

        # The number of parameters.
        n = len(self.relax.data.res[index].params[run])

        # Increment.
        if type(inc) != int:
            raise UserArgIntError, ('increment', inc)
        elif inc <= 1:
            raise UserError, "The increment value needs to be greater than 1."

        # Lower bounds.
        if lower != None:
            if type(lower) != list:
                raise UserArgListError, ('lower bounds', lower)
            if len(lower) != n:
                raise UserError, "The lower bounds argument must be of length " + `n` + "."
            for i in range(n):
                if type(lower[i]) != int and type(lower[i]) != float:
                    raise UserArgListNumError, ('lower bounds', lower)

        # Upper bounds.
        if upper != None:
            if type(upper) != list:
                raise UserArgListError, ('upper bounds', upper)
            if len(upper) != n:
                raise UserError, "The upper argument must be of length " + `n` + "."
            for i in range(n):
                if type(upper[i]) != int and type(upper[i]) != float:
                    raise UserArgListNumError, ('upper bounds', upper)

        # Axes swapping.
        if swap != None:
            if type(swap) != list:
                raise UserArgListError, ('axes swapping', swap)
            if len(swap) != n:
                raise UserError, "The swap argument must be of length " + `n` + "."
            test = zeros(n)
            for i in range(n):
                if type(swap[i]) != int:
                    raise UserArgListIntError, ('axes swapping', swap)
                if swap[i] >= n:
                    raise UserError, "The integer " + `swap[i]` + " is greater than the final array element."
                elif swap[i] < 0:
                    raise UserError, "All integers of the swap argument must be positive."
                test[swap[i]] = 1
            for i in range(n):
                if test[i] != 1:
                    raise UserError, "The swap argument is invalid (possibly duplicated integer values)."

        # File name.
        if type(file) != str:
            raise UserArgStrError, ('file name', file)

        # Directory name.
        if dir == None:
            pass
        elif type(dir) != str:
            raise UserArgNoneStrError, ('directory name', dir)

        # Point.
        if point != None:
            if type(point) != list:
                raise UserArgListError, ('point', point)
            elif len(point) != n:
                raise UserError, "The point argument must be of length " + `n` + "."
            elif type(point_file) != str:
                raise UserArgStrError, ('point file name', point_file)
            for i in range(n):
                if type(point[i]) != int and type(point[i]) != float:
                    raise UserArgListNumError, ('point', point)

        # Remap function.
        if remap != None:
            if type(remap) is not FunctionType:
                raise UserArgFunctionError, ('remap function', remap)

        # Axis labels.
        if labels != None:
            if type(labels) != list:
                raise UserArgListError, ('axis labels', labels)
            elif len(labels) != n:
                raise UserError, "The axis labels argument must be of length " + `n` + "."
            for i in range(n):
                if type(labels[i]) != str:
                    raise UserArgListStrError, ('axis labels', labels)

        # Space type.
        if type(map_type) != str:
            raise UserArgStrError, ('map type', map_type)
        if match("^[Ii]so3[Dd]", map_type):
            if n != 3:
                raise UserError, "The 3D isosurface map requires a strictly 3 parameter model."
            self.relax.map.Iso3D.map_space(run=run, res_num=res_num, inc=inc, lower=lower, upper=upper, swap=swap, file=file, dir=dir, point=point, point_file=point_file, remap=remap, labels=labels)
        else:
            raise UserError, "The map type '" + map_type + "' is not supported."
